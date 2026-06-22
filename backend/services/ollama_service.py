import httpx
import json
from backend.config.settings import settings

class OllamaService:
    def __init__(self):
        pass

    async def check_health(self, base_url: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def generate_tool_selection(self, question: str, tools: list, base_url: str, model: str) -> dict:
        """
        Asks Ollama to select a tool based on the user's question.
        Returns parsed JSON.
        """
        tools_description = json.dumps(tools, indent=2)
        system_prompt = f"""You are an Air Quality Edge Assistant.
You have access to the following tools:
{tools_description}

Based on the user's question, decide which tool(s) to call.
Output MUST be valid JSON in this exact format:
{{
  "tool_calls": [
    {{
      "tool": "tool_name",
      "arguments": {{
        "arg1": "value1"
      }}
    }}
  ]
}}
If no tool is needed, output:
{{
  "tool_calls": []
}}
Do NOT output anything other than JSON.
"""
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "format": "json",
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(f"{base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "{}")
                return json.loads(content)
            except httpx.HTTPStatusError as e:
                print(f"Ollama tool selection HTTP error: {e.response.text}")
                return {"tool_calls": []}
            except Exception as e:
                print(f"Ollama tool selection error: {e}")
                return {"tool_calls": []}

    async def generate_final_response(self, question: str, tool_results: list, base_url: str, model: str) -> str:
        """
        Generates the final human-readable answer.
        """
        results_str = json.dumps(tool_results, indent=2)
        system_prompt = f"""You are an Air Quality Edge Assistant.
You previously called tools to get data to answer the user's question.
Here are the results from those tools:
{results_str}

Use this data to answer the user's question clearly and concisely.
Do NOT mention the tools explicitly unless necessary. Just provide the answer.
"""

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(f"{base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "Sorry, I could not generate a response.")
            except httpx.HTTPStatusError as e:
                print(f"Ollama final response HTTP error: {e.response.text}")
                return f"Error communicating with AI: {e.response.text}"
            except Exception as e:
                print(f"Ollama final response error: {e}")
                return f"Error communicating with AI: {e}"
