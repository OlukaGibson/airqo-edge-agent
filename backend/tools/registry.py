import yaml
from pathlib import Path
from typing import Dict, Any, List

class ToolRegistry:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.tools: Dict[str, Any] = {}
        self.load_tools()

    def load_tools(self):
        if not Path(self.config_path).exists():
            return
        
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            if data and "tools" in data:
                self.tools = {tool["name"]: tool for tool in data["tools"]}

    def get_tool(self, name: str) -> dict:
        return self.tools.get(name)

    def list_tools(self) -> List[dict]:
        return list(self.tools.values())

    def get_tools_for_llm(self) -> List[dict]:
        """Format tools for the LLM prompt"""
        return self.list_tools()
