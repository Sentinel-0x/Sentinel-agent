from ast_guard import inspect_code_safety
from sandbox_executor import run_code_in_sandbox

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, func):
        self.tools[name] = func

    def execute_dynamic_tool(self, code_str: str) -> str:
        violations = inspect_code_safety(code_str)
        if violations:
            return f"❌ [ToolRegistry Security Error] Execution rejected by AST Guard: {violations}"
        return run_code_in_sandbox(code_str)

registry = ToolRegistry()
