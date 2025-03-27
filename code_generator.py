from typing import Dict, Any
import inspect
import textwrap
from automation_functions import get_all_functions

class CodeGenerator:
    def __init__(self, function_registry=None):
        from automation_functions import get_all_functions
        self.function_registry = function_registry or get_all_functions()
    
    def generate_code(self, function_name: str, params: Dict[str, Any] = None) -> str:
        """Generate executable Python code for a given function"""
        if function_name not in self.function_registry:
            raise ValueError(f"Function {function_name} not found in registry")
        
        func_data = self.function_registry[function_name]
        
        # Generate imports
        imports = self._generate_imports(func_data['function'])
        
        # Generate function call
        function_call = self._generate_function_call(function_name, params or {})
        
        # Generate main function with error handling
        main_function = f"""
def main():
    \"\"\"
    Execute {function_name} function
    
    Generated code for function execution with error handling
    \"\"\"
    try:
        # Execute the function
        result = {function_call}
        
        # Print and return the result
        print("Function executed successfully. Result:", result)
        return result
    except Exception as e:
        print(f"Error executing function: {{e}}")
        raise

if __name__ == "__main__":
    main()
"""
        
        # Combine all parts
        full_code = imports + "\n\n" + textwrap.dedent(main_function)
        return full_code.strip()
    
    def _generate_imports(self, func) -> str:
        """Generate import statements by inspecting the function module"""
        module = inspect.getmodule(func)
        if not module:
            return ""
        
        module_name = module.__name__
        if module_name == "__main__":
            module_name = "automation_functions"
        
        return f"from {module_name} import {func.__name__}"
    
    def _generate_function_call(self, function_name: str, params: Dict[str, Any]) -> str:
        """Generate the function call with parameters"""
        func_data = self.function_registry[function_name]
        
        # Handle parameters
        param_strs = []
        for param_name, param_info in func_data['parameters'].items():
            if param_name in params:
                # Use provided value
                param_value = params[param_name]
                if isinstance(param_value, str):
                    param_strs.append(f"{param_name}='{param_value}'")
                else:
                    param_strs.append(f"{param_name}={param_value}")
            elif 'default' in param_info:
                # Use default value
                default = param_info['default']
                if isinstance(default, str):
                    param_strs.append(f"{param_name}='{default}'")
                else:
                    param_strs.append(f"{param_name}={default}")
        
        param_str = ", ".join(param_strs)
        return f"{function_name}({param_str})"