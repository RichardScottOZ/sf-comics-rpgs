from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import hash
import logging

logger = logging.getLogger(__name__)

class ComparativeAgent(BaseAgent):
    def __init__(self):
        super().__init__("comparative")
        self.system_prompt = """You are an expert in comparative analysis of science fiction, comics, and RPG content.
Your task is to analyze and compare multiple works based on specific aspects:

1. World Building:
   - Setting consistency and depth
   - Cultural development
   - Technological/magical systems
   - Political structures
   - Environmental factors

2. Themes and Motifs:
   - Core themes
   - Symbolism
   - Philosophical implications
   - Social commentary
   - Moral questions

3. Character Analysis:
   - Character development
   - Relationships and dynamics
   - Archetypes and roles
   - Motivations and conflicts
   - Growth and change

4. Plot Structure:
   - Narrative techniques
   - Pacing and tension
   - Conflict resolution
   - Story arcs
   - Climax and resolution

Provide detailed, insightful comparisons while maintaining a professional and analytical tone."""

    async def compare_works(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str,
        model: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Compare multiple works based on specified analysis type"""
        if not works or len(works) < 2:
            raise ValueError("At least two works are required for comparison")

        # Prepare the comparison prompt
        comparison_prompt = self._prepare_comparison_prompt(works, analysis_type)
        
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
        
        # Cache the result
        self._cache_analysis(cache_key, analysis)
        
        return analysis

    def _prepare_comparison_prompt(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str
    ) -> str:
        """Prepare a detailed prompt for the comparison"""
        works_info = []
        for work in works:
            work_info = []
            if "title" in work:
                work_info.append(f"Title: {work['title']}")
            if "author" in work:
                work_info.append(f"Author: {work['author']}")
            if "content" in work:
                work_info.append(f"Content: {work['content']}")
            works_info.append("\n".join(work_info))

        prompt = f"""Compare the following works based on {analysis_type}:

{chr(10).join(works_info)}

Please provide a detailed analysis focusing on:
1. Similarities and differences
2. Strengths and weaknesses of each approach
3. Impact and effectiveness
4. Unique contributions to the genre
5. Recommendations for further study

Format your response in a clear, structured manner."""
        
        return prompt 