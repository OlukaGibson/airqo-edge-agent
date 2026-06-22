import yaml
import httpx
from pathlib import Path
from typing import Dict, Any

class APIClient:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.apis: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        if not Path(self.config_path).exists():
            return
        
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            if data and "apis" in data:
                self.apis = data["apis"]

    def _get_api_config(self, api_name: str = "default") -> dict:
        return self.apis.get(api_name, self.apis.get("default", {}))

    async def execute(self, endpoint: str, method: str = "GET", params: dict = None, api_name: str = "default") -> dict:
        config = self._get_api_config(api_name)
        base_url = config.get("base_url", "http://localhost:8000/mock-api")
        timeout = config.get("timeout", 10)
        
        headers = {}
        auth_type = config.get("auth_type", "none")
        if auth_type == "bearer":
            # in a real scenario we fetch this from env vars securely
            token = config.get("auth_token_env", "TOKEN")
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "api_key":
            token = config.get("auth_token_env", "KEY")
            header_name = config.get("auth_header", "X-API-Key")
            headers[header_name] = token

        # For formatting URL parameters if the endpoint uses curly braces (e.g., /devices/{device_id})
        url_endpoint = endpoint
        if params:
            try:
                url_endpoint = endpoint.format(**params)
                # Remove path parameters from query params
                query_params = {k: v for k, v in params.items() if f"{{{k}}}" not in endpoint}
            except KeyError:
                query_params = params
        else:
            query_params = {}

        url = f"{base_url.rstrip('/')}/{url_endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.request(method, url, headers=headers, params=query_params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"HTTP error occurred: {e}"}
            except Exception as e:
                return {"error": f"An error occurred: {e}"}
