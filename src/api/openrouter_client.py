from typing import Dict, Any, Optional, List
import aiohttp
import os
from ..config.settings import settings

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.default_model = os.getenv("OPENROUTER_DEFAULT_MODEL", "mistralai/mistral-7b")
        self.force_model = os.getenv("OPENROUTER_FORCE_MODEL", "true").lower() == "true"
        self.base_url = settings.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
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
            async with session.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Force model if configured
        if self.force_model:
            model = self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/your-repo",  # Required for free tier
            "X-Title": "SFMCP Testing"  # Required for free tier
        }

        response = await self._make_request(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                **kwargs
            }
        )
        return response

    async def analyze_content(
        self,
        content: str,
        analysis_type: str,
        model: str = "mistralai/mistral-7b",  # Changed default to Mistral
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