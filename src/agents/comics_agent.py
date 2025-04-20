from typing import Dict, Any, Optional
from .base_agent import BaseAgent

class ComicsAgent(BaseAgent):
    def __init__(self):
        super().__init__("comics")
        self.system_prompt = """You are an expert in comics and graphic novels. 
Your task is to analyze comic content and provide insights about:
1. Art style and visual storytelling
2. Panel layout and composition
3. Character design and development
4. Storytelling techniques
5. Themes and symbolism
6. Cultural and historical context
7. Writing and dialogue
8. Color theory and use
9. Influences and references
10. Impact on the medium

Provide detailed analysis while maintaining a professional and insightful tone."""

    async def analyze_content(
        self,
        content: str,
        title: Optional[str] = None,
        publisher: Optional[str] = None,
        year: Optional[int] = None,
        creator: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis = await self._get_analysis(
            content=content,
            system_prompt=self.system_prompt
        )
        
        if title:
            analysis["title"] = title
        if publisher:
            analysis["publisher"] = publisher
        if year:
            analysis["year"] = year
        if creator:
            analysis["creator"] = creator
            
        return analysis

    async def get_recommendations(
        self,
        based_on: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        prompt = f"""Based on the following content or preferences, recommend {limit} comics or graphic novels that would be of interest:
        
        {based_on}
        
        For each recommendation, provide:
        1. Title and creator(s)
        2. Publisher
        3. Brief description
        4. Why it might be of interest
        5. Similar themes or art style
        6. Publication year
        """
        
        return await self._get_analysis(
            content=prompt,
            system_prompt="You are an expert in comics and graphic novel recommendations."
        ) 