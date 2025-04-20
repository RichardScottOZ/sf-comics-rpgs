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
            "HTTP-Referer": "https://github.com/your-repo",  # Required for free tier
            "X-Title": "SFMCP Testing"  # Required for free tier
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

        response = await self._make_request(
            method="POST",
            endpoint="chat/completions",
            data={
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