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
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis = await self._get_analysis(
            content=content,
            system_prompt=self.system_prompt,
            model=model
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

class MCPEnabledScienceFictionAgent(BaseAgent):
    def __init__(self):
        super().__init__("science_fiction_mcp")
        self.system_prompt = """You are an advanced AI expert in science fiction literature and media, with enhanced capabilities for:
1. Deep thematic analysis and pattern recognition
2. Cross-referencing with extensive knowledge bases
3. Predictive analysis of cultural impact
4. Comparative analysis across multiple works
5. Advanced world-building evaluation
6. Character archetype and development analysis
7. Plot structure optimization suggestions
8. Scientific concept validation and critique
9. Social and philosophical implications analysis
10. Historical context and influence tracing

Provide comprehensive, data-driven analysis while maintaining a professional and insightful tone."""

    async def analyze_content(
        self,
        content: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[int] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Enhanced analysis with additional context
        enhanced_prompt = self.system_prompt
        if title:
            enhanced_prompt += f"\nTitle: {title}"
        if author:
            enhanced_prompt += f"\nAuthor: {author}"
        if year:
            enhanced_prompt += f"\nYear: {year}"
            
        analysis = await self._get_analysis(
            content=content,
            system_prompt=enhanced_prompt,
            model=model
        )
        
        # Add metadata
        if title:
            analysis["title"] = title
        if author:
            analysis["author"] = author
        if year:
            analysis["year"] = year
            
        # Add MCP-specific enhancements
        analysis["mcp_version"] = "1.0"
        analysis["analysis_depth"] = "enhanced"
        
        return analysis

    async def get_recommendations(
        self,
        based_on: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        prompt = f"""Based on the following content or preferences, provide enhanced recommendations for {limit} science fiction works:
        
        {based_on}
        
        For each recommendation, provide:
        1. Title and author
        2. Detailed description
        3. Why it might be of interest
        4. Similar themes or elements
        5. Publication year
        6. Critical reception
        7. Cultural impact
        8. Related works
        9. Reading order suggestions
        10. Adaptation information (if applicable)
        """
        
        recommendations = await self._get_analysis(
            content=prompt,
            system_prompt="You are an advanced AI expert in science fiction literature and media recommendations."
        )
        
        # Add MCP-specific enhancements
        recommendations["mcp_version"] = "1.0"
        recommendations["recommendation_depth"] = "enhanced"
        
        return recommendations 