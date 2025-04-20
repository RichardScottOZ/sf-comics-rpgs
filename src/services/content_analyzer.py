from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from ..api.openrouter_client import OpenRouterClient
from ..config.settings import settings

class ContentAnalyzer:
    def __init__(self):
        self.client = OpenRouterClient()
        self.cache_dir = settings.CACHE_DIR

    async def analyze_science_fiction(
        self,
        content: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis_type = "science fiction"
        cache_key = f"sf_{hash(content)}"
        cached_result = self._get_cached_analysis(cache_key)
        if cached_result:
            return cached_result

        result = await self.client.analyze_content(
            content=content,
            analysis_type=analysis_type,
            model="mistralai/mistral-7b"
        )
        
        analysis = {
            "type": analysis_type,
            "title": title,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "analysis": result
        }
        
        self._cache_analysis(cache_key, analysis)
        return analysis

    async def analyze_comics(
        self,
        content: str,
        title: Optional[str] = None,
        publisher: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis_type = "comics"
        cache_key = f"comics_{hash(content)}"
        cached_result = self._get_cached_analysis(cache_key)
        if cached_result:
            return cached_result

        result = await self.client.analyze_content(
            content=content,
            analysis_type=analysis_type,
            model="mistralai/mistral-7b"
        )
        
        analysis = {
            "type": analysis_type,
            "title": title,
            "publisher": publisher,
            "timestamp": datetime.now().isoformat(),
            "analysis": result
        }
        
        self._cache_analysis(cache_key, analysis)
        return analysis

    async def analyze_rpg(
        self,
        content: str,
        system: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis_type = "RPG"
        cache_key = f"rpg_{hash(content)}"
        cached_result = self._get_cached_analysis(cache_key)
        if cached_result:
            return cached_result

        result = await self.client.analyze_content(
            content=content,
            analysis_type=analysis_type,
            model="mistralai/mistral-7b"
        )
        
        analysis = {
            "type": analysis_type,
            "system": system,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "analysis": result
        }
        
        self._cache_analysis(cache_key, analysis)
        return analysis

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