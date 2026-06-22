import time
from backend.tools.registry import ToolRegistry
from backend.services.api_client import APIClient

class ToolExecutor:
    def __init__(self, registry: ToolRegistry, api_client: APIClient):
        self.registry = registry
        self.api_client = api_client

    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        start_time = time.time()
        
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {
                "tool_name": tool_name,
                "error": f"Tool '{tool_name}' not found in registry.",
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }

        endpoint = tool.get("endpoint")
        method = tool.get("method", "GET")
        
        # Here we could validate arguments against tool["parameters"] if needed.
        
        # Call the API
        response = await self.api_client.execute(endpoint=endpoint, method=method, params=arguments)
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "tool_name": tool_name,
            "response": response,
            "execution_time_ms": execution_time_ms
        }
