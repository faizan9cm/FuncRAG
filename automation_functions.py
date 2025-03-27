from typing import Dict, Any, Optional
import inspect
import os
import webbrowser
import psutil
import platform
import subprocess
from typing import Dict, Any
import datetime
import inspect

# Application Control Functions
def open_chrome(url: str = "https://www.google.com") -> str:
    """Open Google Chrome with optional URL"""
    webbrowser.get("chrome").open(url)
    return f"Opened Chrome with URL: {url}"

def open_calculator() -> str:
    """Open system calculator"""
    if platform.system() == "Windows":
        os.system("calc")
    elif platform.system() == "Darwin":
        subprocess.run(["/System/Applications/Calculator.app/Contents/MacOS/Calculator"])
    else:
        subprocess.run(["gnome-calculator"])
    return "Calculator opened successfully"

def open_notepad() -> str:
    """Open system notepad/text editor"""
    if platform.system() == "Windows":
        os.system("notepad")
    elif platform.system() == "Darwin":
        subprocess.run(["/Applications/TextEdit.app/Contents/MacOS/TextEdit"])
    else:
        subprocess.run(["gedit"])
    return "Notepad opened successfully"

def open_vscode() -> str:
    """Open Visual Studio Code"""
    subprocess.run(["code"])
    return "VS Code opened successfully"

# System Monitoring Functions
def get_cpu_usage() -> Dict[str, Any]:
    """Get current CPU usage statistics"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count": psutil.cpu_count(),
        "cpu_stats": psutil.cpu_stats(),
        "cpu_times": psutil.cpu_times()._asdict()
    }

def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics"""
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "available": mem.available,
        "used": mem.used,
        "percent": mem.percent,
        "free": mem.free
    }

def get_disk_usage() -> Dict[str, Any]:
    """Get disk usage information"""
    disk = psutil.disk_usage('/')
    return {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent
    }

# Command Execution Functions
def run_command(cmd: str) -> Dict[str, Any]:
    """Execute a shell command and return results"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return {
            "success": True,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "returncode": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr
        }

# Utility Functions
def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    return {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }

# Function Registry System
CUSTOM_FUNCTIONS_REGISTRY = {}

FUNCTION_REGISTRY = {
    "open_chrome": {
        "function": open_chrome,
        "description": "Open Google Chrome browser with optional URL parameter",
        "parameters": {
            "url": {
                "type": "str",
                "required": False,
                "default": "https://www.google.com",
                "description": "URL to open in Chrome"
            }
        }
    },
    "open_calculator": {
        "function": open_calculator,
        "description": "Open system calculator application",
        "parameters": {}
    },
    "open_notepad": {
        "function": open_notepad,
        "description": "Open system notepad/text editor",
        "parameters": {}
    },
    "open_vscode": {
        "function": open_vscode,
        "description": "Open Visual Studio Code editor",
        "parameters": {}
    },
    "get_cpu_usage": {
        "function": get_cpu_usage,
        "description": "Get current CPU usage statistics",
        "parameters": {}
    },
    "get_memory_usage": {
        "function": get_memory_usage,
        "description": "Get current memory usage statistics",
        "parameters": {}
    },
    "get_disk_usage": {
        "function": get_disk_usage,
        "description": "Get disk usage information",
        "parameters": {}
    },
    "run_command": {
        "function": run_command,
        "description": "Execute a shell command and return results",
        "parameters": {
            "cmd": {
                "type": "str",
                "required": True,
                "description": "Command to execute"
            }
        }
    },
    "get_system_info": {
        "function": get_system_info,
        "description": "Get comprehensive system information",
        "parameters": {}
    }
}

def get_all_functions():
    """Combine built-in and custom functions"""
    return {**FUNCTION_REGISTRY, **CUSTOM_FUNCTIONS_REGISTRY}


def get_all_functions() -> Dict[str, Any]:
    """Combine both built-in and custom functions"""
    return {**FUNCTION_REGISTRY, **CUSTOM_FUNCTIONS_REGISTRY}

def register_custom_function(func: callable, name: Optional[str] = None, 
                          description: str = "", parameters: Optional[Dict] = None) -> str:
    """Register a custom function with the system"""
    func_name = name or func.__name__
    
    # Extract parameter information
    sig = inspect.signature(func)
    params = parameters or {}
    for param_name, param in sig.parameters.items():
        if param_name not in params:
            params[param_name] = {
                "type": param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any",
                "required": param.default == inspect.Parameter.empty,
                "description": ""
            }
            if param.default != inspect.Parameter.empty:
                params[param_name]["default"] = param.default
    
    # Add to custom registry
    CUSTOM_FUNCTIONS_REGISTRY[func_name] = {
        "function": func,
        "description": description or func.__doc__ or "",
        "parameters": params
    }
    
    return func_name