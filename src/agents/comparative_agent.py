from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..prompts.prompt_engineer import PromptEngineer
from ..context.historical_context import HistoricalContext
import hash
import logging

logger = logging.getLogger(__name__)

class ComparativeAgent(BaseAgent):
    def __init__(self):
        super().__init__("comparative")
        self.prompt_engineer = PromptEngineer()
        self.historical_context = HistoricalContext()
        self.system_prompt = """You are an expert in comparative analysis of science fiction, comics, and RPG content.
Your task is to analyze and compare multiple works based on specific aspects, taking into account their historical context and using appropriate analytical frameworks."""

    async def compare_works(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str,
        model: Optional[str] = None,
        force_refresh: bool = False,
        enhanced: bool = False,
        include_historical_context: bool = True
    ) -> Dict[str, Any]:
        """Compare multiple works based on specified analysis type."""
        if not works or len(works) < 2:
            raise ValueError("At least two works are required for comparison")

        # Get historical context for each work
        historical_contexts = []
        if include_historical_context:
            for work in works:
                context = self.historical_context.get_context_for_work(work)
                historical_contexts.append(context)

        # Generate the comparison prompt
        comparison_prompt = self.prompt_engineer.generate_prompt(
            works=works,
            analysis_type=analysis_type,
            enhanced=enhanced,
            historical_context=historical_contexts[0] if historical_contexts else None
        )
        
        # Generate cache key
        cache_key = f"{self.agent_type}_{hash(comparison_prompt)}"
        
        # Check cache unless force_refresh is True
        if not force_refresh:
            cached_result = self._get_cached_analysis(cache_key)
            if cached_result:
                logger.info(f"Using cached result for {self.agent_type} comparison")
                return cached_result
        
        # Get the analysis
        analysis = await self._get_analysis(
            content=comparison_prompt,
            system_prompt=self.system_prompt,
            model=model
        )
        
        # Add metadata
        analysis["comparison_type"] = analysis_type
        analysis["works_compared"] = [work.get("title", "Untitled") for work in works]
        if historical_contexts:
            analysis["historical_context"] = historical_contexts
        
        # Cache the result
        self._cache_analysis(cache_key, analysis)
        
        return analysis

    def get_available_analysis_types(self) -> List[str]:
        """Get list of available analysis types."""
        return self.prompt_engineer.get_available_analysis_types() 