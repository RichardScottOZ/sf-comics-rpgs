from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging
from pathlib import Path
from ..api.openrouter_client import OpenRouterClient
from ..config.settings import settings
from ..core.base_agent import BaseAgent as CoreBaseAgent

logger = logging.getLogger(__name__)

class BaseAgent(CoreBaseAgent):
    """Extended base class for all agents with additional functionality"""
    
    def __init__(self, agent_type: Optional[str] = None):
        super().__init__(agent_type)
        self.client = OpenRouterClient()
        self.cache_dir = settings.CACHE_DIR / "agents" / agent_type
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized {agent_type} agent with default model: {self.client.default_model}")

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the agent"""
        return True
        
    async def preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess input data before execution"""
        return input_data
        
    async def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess result after execution"""
        return result

    async def _get_analysis(
        self,
        content: str,
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        cache_key = f"{self.agent_type}_{hash(content)}"
        cached_result = self._get_cached_analysis(cache_key)
        if cached_result:
            logger.info(f"Using cached result for {self.agent_type} analysis")
            return cached_result

        logger.info(f"Making API request with model: {model or self.client.default_model}")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]

        try:
            result = await self.client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            logger.info(f"Successfully received response from {model or self.client.default_model}")
            logger.debug(f"Response details: {json.dumps(result, indent=2)}")
            return result
        except Exception as e:
            logger.error(f"Error in API request to {model or self.client.default_model}: {str(e)}")
            raise

    def _get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                return json.load(f)
        return None

    def _cache_analysis(self, cache_key: str, analysis: Dict[str, Any]):
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(analysis, f, indent=2) 