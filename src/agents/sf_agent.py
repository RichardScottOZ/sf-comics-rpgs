from typing import Dict, Any, Optional
from .base_agent import BaseAgent

class ScienceFictionAgent(BaseAgent):
    def __init__(self):
        super().__init__("science_fiction")
        self.system_prompt = """You are an expert in science fiction literature and media. 
Your task is to analyze science fiction content and provide insights about:
1. Themes and motifs
2. Scientific concepts and their plausibility
3. Social and philosophical implications
4. Comparisons to other works in the genre
5. Cultural impact and significance
6. Writing style and narrative techniques
7. World-building elements
8. Character development and relationships
9. Plot structure and pacing
10. Potential influences and inspirations

Provide detailed analysis while maintaining a professional and insightful tone."""

    async def analyze_content(
        self,
        content: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[int] = None,
    ) -> Dict[str, Any]:
        analysis = await self._get_analysis(
            content=content,
            system_prompt=self.system_prompt
        )
        
        if title:
            analysis["title"] = title
        if author:
            analysis["author"] = author
        if year:
            analysis["year"] = year
            
        return analysis

    async def get_recommendations(
        self,
        based_on: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        prompt = f"""Based on the following content or preferences, recommend {limit} science fiction works that would be of interest:
        
        {based_on}
        
        For each recommendation, provide:
        1. Title and author
        2. Brief description
        3. Why it might be of interest
        4. Similar themes or elements
        5. Publication year
        """
        
        return await self._get_analysis(
            content=prompt,
            system_prompt="You are an expert in science fiction literature and media recommendations."
        ) 