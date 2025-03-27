from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from rag_model import FunctionRetriever
from code_generator import CodeGenerator
import uuid
import logging
from datetime import datetime
from automation_functions import get_all_functions

app = FastAPI(title="LLM + RAG Function Execution API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize components
function_retriever = FunctionRetriever()
code_generator = CodeGenerator(get_all_functions())

# Session management
sessions = {}

# Request/Response Models
class ExecuteRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ExecuteResponse(BaseModel):
    session_id: str
    function_name: str
    code: str
    metadata: Dict[str, Any]

class CustomFunctionRequest(BaseModel):
    code: str
    name: str
    description: str = ""
    parameters: Optional[Dict[str, Any]] = None

class CustomFunctionResponse(BaseModel):
    status: str
    message: str
    function_name: str

# API Endpoints
@app.post("/execute", response_model=ExecuteResponse)
async def execute_function(request: ExecuteRequest):
    """Execute an automation function based on user prompt"""
    try:
        # Retrieve or create session
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in sessions:
            sessions[session_id] = {
                "history": [],
                "context": {}
            }
        
        # Retrieve most relevant function
        retrieved_functions = function_retriever.retrieve_function(request.prompt)
        if not retrieved_functions:
            raise HTTPException(status_code=404, detail="No matching functions found")
        
        # For simplicity, take the top match
        selected_function = retrieved_functions[0]
        function_name = selected_function["function_name"]
        
        # Generate code
        try:
            code = code_generator.generate_code(
                function_name,
                request.parameters or {}
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Update session history
        sessions[session_id]['history'].append({
            "prompt": request.prompt,
            "function": function_name,
            "timestamp": str(datetime.now()),
            "parameters": request.parameters or {}
        })
        
        return {
            "session_id": session_id,
            "function_name": function_name,
            "code": code,
            "metadata": selected_function['metadata']
        }
    except Exception as e:
        logger.error(f"Error in execute_function: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register_function", response_model=CustomFunctionResponse)
async def register_custom_function(request: CustomFunctionRequest):
    """Register a new custom function"""
    try:
        # Create a new namespace for the function
        namespace = {}
        exec(request.code, namespace)
        
        if request.name not in namespace:
            raise HTTPException(
                status_code=400,
                detail=f"Function {request.name} not found in provided code"
            )
        
        # Register in both systems
        from automation_functions import register_custom_function
        func_name = register_custom_function(
            func=namespace[request.name],
            name=request.name,
            description=request.description,
            parameters=request.parameters
        )
        
        # Update search index
        function_retriever.add_function_to_index(
            func_name=func_name,
            func_data={
                "description": request.description,
                "parameters": request.parameters or {}
            }
        )
        
        # Force reload the function registry in the code generator
        from automation_functions import get_all_functions
        code_generator.function_registry = get_all_functions()
        
        return {
            "status": "success",
            "message": f"Function {func_name} registered successfully",
            "function_name": func_name
        }
    except Exception as e:
        logger.error(f"Error registering function: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error registering function: {str(e)}"
        )

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information and history"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)