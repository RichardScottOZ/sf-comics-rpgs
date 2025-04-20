from typing import Dict, Any, Optional, List
import aiohttp
from ..config.settings import settings

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.default_model = settings.OPENROUTER_DEFAULT_MODEL
        self.force_model = settings.OPENROUTER_FORCE_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/richard/sfmcp",  # Update with your repo
            "X-Title": "SFMCP Analysis"  # Update with your app name
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"{response.status}, message='{error_text}', url='{url}'")
                    return await response.json()
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Force model if configured
        if self.force_model:
            model = self.default_model

        # Ensure model is specified
        if not model:
            model = self.default_model

        # Add required parameters for the model
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            **kwargs
        }

        response = await self._make_request(
            method="POST",
            endpoint="chat/completions",
            data=request_data
        )
        return response

    async def analyze_content(
        self,
        content: str,
        analysis_type: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        messages = [
            {
                "role": "system",
                "content": f"You are an expert in analyzing {analysis_type} content. Provide detailed analysis and insights."
            },
            {
                "role": "user",
                "content": content
            }
        ]
        return await self.chat_completion(messages=messages, model=model) 