from typing import Dict, Any, Optional
from .base_agent import BaseAgent

class RPGAgent(BaseAgent):
    def __init__(self):
        super().__init__("rpg")
        self.system_prompt = """You are an expert in tabletop role-playing games (RPGs). 
Your task is to analyze RPG content and provide insights about:
1. Game mechanics and systems
2. World-building and setting
3. Character creation and progression
4. Balance and playability
5. Narrative structure and storytelling
6. Rules clarity and organization
7. Player agency and choice
8. Combat and conflict resolution
9. Social interaction mechanics
10. Resource management
11. Difficulty scaling
12. Replayability and variety

Provide detailed analysis while maintaining a professional and insightful tone."""

    async def analyze_content(
        self,
        content: str,
        system: Optional[str] = None,
        source: Optional[str] = None,
        edition: Optional[str] = None,
        publisher: Optional[str] = None,
    ) -> Dict[str, Any]:
        analysis = await self._get_analysis(
            content=content,
            system_prompt=self.system_prompt
        )
        
        if system:
            analysis["system"] = system
        if source:
            analysis["source"] = source
        if edition:
            analysis["edition"] = edition
        if publisher:
            analysis["publisher"] = publisher
            
        return analysis

    async def get_recommendations(
        self,
        based_on: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        prompt = f"""Based on the following content or preferences, recommend {limit} RPG systems, supplements, or adventures that would be of interest:
        
        {based_on}
        
        For each recommendation, provide:
        1. Title and publisher
        2. System/edition
        3. Brief description
        4. Why it might be of interest
        5. Similar mechanics or themes
        6. Publication year
        """
        
        return await self._get_analysis(
            content=prompt,
            system_prompt="You are an expert in tabletop RPG recommendations."
        )

    async def analyze_character(
        self,
        character_sheet: str,
        system: str,
    ) -> Dict[str, Any]:
        prompt = f"""Analyze this {system} character sheet:
        
        {character_sheet}
        
        Provide insights about:
        1. Character concept and role
        2. Strengths and weaknesses
        3. Optimization and balance
        4. Role-playing potential
        5. Party synergy
        6. Growth opportunities
        """
        
        return await self._get_analysis(
            content=prompt,
            system_prompt="You are an expert in RPG character analysis and optimization."
        ) 