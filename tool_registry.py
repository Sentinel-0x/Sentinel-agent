import inspect
import json
import ast
import tempfile
import os
import docker
from typing import Callable, Dict, Any, get_type_hints

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: list = []

    def register(self, description: str):
        def decorator(func: Callable):
            tool_name = func.__name__
            self.tools[tool_name] = func

            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            properties = {}
            required = []

            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_type = type_hints.get(param_name, str)
                json_type = "string"
                if param_type == int:
                    json_type = "integer"
                elif param_type == float:
                    json_type = "number"
                elif param_type == bool:
                    json_type = "boolean"
                elif param_type == list:
                    json_type = "array"
                elif param_type == dict:
                    json_type = "object"

                properties[param_name] = {
                    "type": json_type,
                    "description": f"Parameter {param_name}"
                }

                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            self.tool_schemas.append(schema)
            return func
        return decorator

    def execute(self, tool_name: str, arguments: dict) -> Any:
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found in registry."
        try:
            return self.tools[tool_name](**arguments)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

# ==================== 实例化注册中心 ====================
registry = ToolRegistry()

@registry.register(description="读取指定路径的文本文件内容。")
def read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@registry.register(description="向指定路径的文件写入 Python 代码或其他内容。")
def write_file(file_path: str, content: str) -> str:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Success: File '{file_path}' written successfully."

@registry.register(description="对给定的 Python 代码字符串进行 AST 静态语法预检，返回语法是否正确或具体的 SyntaxError。")
def check_code_syntax(code_content: str) -> str:
    try:
        ast.parse(code_content)
        return "Success: AST syntax check passed."
    except SyntaxError as se:
        return f"SyntaxError: line {se.lineno}, offset {se.offset}: {se.text} - {str(se)}"

@registry.register(description="将指定的 Python 代码文件放入 Docker 沙箱安全环境中执行，返回标准输出、标准错误或超时异常信息。")
def run_code_in_docker_sandbox(script_filename: str, timeout_seconds: int = 10) -> str:
    client = docker.from_env()
    abs_current_path = os.path.abspath(".")
    
    if not os.path.exists(os.path.join(abs_current_path, script_filename)):
        return f"Error: File '{script_filename}' not found in workspace."

    container = None
    try:
        container = client.containers.create(
            image="agent-sandbox",
            command=f"python /workspace/{script_filename}",
            volumes={abs_current_path: {'bind': '/workspace', 'mode': 'rw'}},
            working_dir="/workspace",
            mem_limit="512m",
            nano_cpus=1000000000
        )
        container.start()
        
        result = container.wait(timeout=timeout_seconds)
        logs = container.logs(stdout=True, stderr=True).decode('utf-8')
        
        if result.get('StatusCode', 0) != 0:
            return f"RuntimeError (Exit Code {result.get('StatusCode')}):\n{logs}"
        
        return f"Execution Success. Logs:\n{logs}"
        
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return f"Error: Sandbox execution timed out after {timeout_seconds} seconds (possible infinite loop)."
        return f"Error during sandbox execution: {error_msg}"
    finally:
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass