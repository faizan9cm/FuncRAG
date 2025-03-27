from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import json
import faiss
import numpy as np
import pickle
import os
from automation_functions import get_all_functions

class FunctionRetriever:
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.function_data = []
        
        # File paths for persistence
        self.index_file = "faiss_index.index"
        self.data_file = "function_data.pkl"
        
        # Load or create FAISS index
        self._initialize_index()

    def _initialize_index(self):
        """Initialize or load FAISS index and function data"""
        if os.path.exists(self.index_file) and os.path.exists(self.data_file):
            # Load existing index and data
            self.index = faiss.read_index(self.index_file)
            with open(self.data_file, 'rb') as f:
                self.function_data = pickle.load(f)
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(384)  # Dimension for all-MiniLM-L6-v2
            self._initialize_function_database()

    def _initialize_function_database(self):
        """Initialize the vector database with function metadata"""
        functions = get_all_functions()
        
        embeddings = []
        for func_name, func_data in functions.items():
            # Create document text for embedding
            doc_text = f"""
            Function: {func_name}
            Description: {func_data['description']}
            Parameters: {json.dumps(func_data['parameters'])}
            """
            
            # Generate embedding
            embedding = self.embedding_model.encode(doc_text)
            embeddings.append(embedding)
            
            # Store function data
            self.function_data.append({
                "name": func_name,
                "description": func_data['description'],
                "parameters": func_data['parameters'],
                "text": doc_text
            })
        
        # Add all embeddings to FAISS index
        if embeddings:
            self.index.add(np.array(embeddings))
        
        # Save index and data
        self._save_data()

    def _save_data(self):
        """Save FAISS index and function data to disk"""
        faiss.write_index(self.index, self.index_file)
        with open(self.data_file, 'wb') as f:
            pickle.dump(self.function_data, f)

    def retrieve_function(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve most relevant functions based on user query"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        query_embedding = np.array([query_embedding])
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Format results
        retrieved_functions = []
        for i in range(top_k):
            idx = indices[0][i]
            if idx >= 0 and idx < len(self.function_data):  # Validate index
                retrieved_functions.append({
                    "function_name": self.function_data[idx]["name"],
                    "metadata": {
                        "name": self.function_data[idx]["name"],
                        "description": self.function_data[idx]["description"],
                        "parameters": self.function_data[idx]["parameters"]
                    },
                    "score": float(distances[0][i]),
                    "text": self.function_data[idx]["text"]
                })
        
        return retrieved_functions

    def add_function_to_index(self, func_name: str, func_data: dict):
        """Add a new function to the FAISS index"""
        # Create document text for embedding
        doc_text = f"""
        Function: {func_name}
        Description: {func_data['description']}
        Parameters: {json.dumps(func_data['parameters'])}
        """
        
        # Generate embedding
        embedding = self.embedding_model.encode(doc_text)
        
        # Add to FAISS index
        self.index.add(np.array([embedding]))
        
        # Store function data
        self.function_data.append({
            "name": func_name,
            "description": func_data['description'],
            "parameters": func_data['parameters'],
            "text": doc_text
        })
        
        # Save updated index and data
        self._save_data()