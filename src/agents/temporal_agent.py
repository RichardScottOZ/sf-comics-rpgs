from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..context.historical_context import HistoricalContext
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TemporalAnalysisAgent(BaseAgent):
    """Agent for analyzing works across different time periods using both algorithmic analysis and LLM insights."""
    
    def __init__(self):
        super().__init__("temporal")
        self.historical_context = HistoricalContext()
        self.system_prompt = """You are an expert in analyzing the evolution of science fiction, comics, and RPG content across time periods.
Your task is to provide insights about how works evolve over time, identifying patterns, trends, and significant changes in themes, styles, and innovations."""
    
    async def analyze_temporal_patterns(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str = "evolution",
        model: Optional[str] = None,
        enhanced: bool = False
    ) -> Dict[str, Any]:
        """Analyze how works evolve over time using both algorithmic analysis and LLM insights."""
        if not works:
            raise ValueError("At least one work is required for temporal analysis")
        
        # Perform algorithmic analysis
        algorithmic_analysis = self._perform_algorithmic_analysis(works)
        
        # Generate LLM insights
        llm_analysis = await self._generate_llm_insights(
            works=works,
            algorithmic_analysis=algorithmic_analysis,
            analysis_type=analysis_type,
            model=model,
            enhanced=enhanced
        )
        
        # Combine results
        analysis = {
            "algorithmic_analysis": algorithmic_analysis,
            "llm_insights": llm_analysis,
            "visualization_data": self._prepare_visualization_data(algorithmic_analysis)
        }
        
        return analysis
    
    def _perform_algorithmic_analysis(self, works: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform algorithmic analysis of temporal patterns."""
        # Sort works by year
        sorted_works = sorted(
            [w for w in works if w.get("year")],
            key=lambda x: x.get("year", 0)
        )
        
        if not sorted_works:
            raise ValueError("No works with valid years found for temporal analysis")
        
        # Group works by decade
        works_by_decade = {}
        for work in sorted_works:
            year = work.get("year")
            if year:
                decade = (year // 10) * 10
                if decade not in works_by_decade:
                    works_by_decade[decade] = []
                works_by_decade[decade].append(work)
        
        # Analyze patterns
        patterns = {
            "decade_analysis": {},
            "evolution_trends": [],
            "historical_context": {}
        }
        
        # Analyze each decade
        for decade, decade_works in works_by_decade.items():
            patterns["decade_analysis"][decade] = self._analyze_decade(decade_works)
            patterns["historical_context"][decade] = self.historical_context.get_historical_context(
                year=decade
            )
        
        # Identify evolution trends
        patterns["evolution_trends"] = self._identify_evolution_trends(patterns["decade_analysis"])
        
        return patterns
    
    async def _generate_llm_insights(
        self,
        works: List[Dict[str, Any]],
        algorithmic_analysis: Dict[str, Any],
        analysis_type: str,
        model: Optional[str],
        enhanced: bool
    ) -> Dict[str, Any]:
        """Generate LLM insights about temporal patterns."""
        prompt = self._create_analysis_prompt(
            works=works,
            algorithmic_analysis=algorithmic_analysis,
            analysis_type=analysis_type,
            enhanced=enhanced
        )
        
        analysis = await self._get_analysis(
            content=prompt,
            system_prompt=self.system_prompt,
            model=model
        )
        
        return analysis
    
    def _create_analysis_prompt(
        self,
        works: List[Dict[str, Any]],
        algorithmic_analysis: Dict[str, Any],
        analysis_type: str,
        enhanced: bool
    ) -> str:
        """Create a prompt for LLM analysis."""
        prompt_parts = [
            "Analyze the following works and their evolution over time:",
            "\nWorks:",
            *[f"- {work.get('title', 'Untitled')} ({work.get('year', 'Unknown')})" for work in works],
            "\nAlgorithmic Analysis:",
            f"- Decade Analysis: {algorithmic_analysis['decade_analysis']}",
            f"- Evolution Trends: {algorithmic_analysis['evolution_trends']}",
            f"- Historical Context: {algorithmic_analysis['historical_context']}",
            "\nPlease provide insights about:"
        ]
        
        if enhanced:
            prompt_parts.extend([
                "1. Major thematic shifts and their significance",
                "2. Innovations in narrative techniques and style",
                "3. Influence of historical context on content",
                "4. Predictions for future trends",
                "5. Recommendations for further analysis"
            ])
        else:
            prompt_parts.extend([
                "1. Key patterns in thematic evolution",
                "2. Notable changes in style and technique",
                "3. Impact of historical context",
                "4. Significant innovations"
            ])
        
        return "\n".join(prompt_parts)
    
    def _prepare_visualization_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for visualization."""
        visualization_data = {
            "timeline": [],
            "themes": [],
            "metrics": {}
        }
        
        # Prepare timeline data
        for decade, decade_data in analysis["decade_analysis"].items():
            visualization_data["timeline"].append({
                "decade": decade,
                "work_count": decade_data["work_count"],
                "themes": [theme[0] for theme in decade_data["common_themes"]],
                "historical_context": analysis["historical_context"][decade]
            })
        
        # Prepare theme evolution data
        theme_evolution = {}
        for trend in analysis["evolution_trends"]:
            period = trend["period"]
            for theme_type, themes in trend["theme_evolution"].items():
                if theme_type not in theme_evolution:
                    theme_evolution[theme_type] = []
                theme_evolution[theme_type].append({
                    "period": period,
                    "themes": themes
                })
        
        visualization_data["themes"] = theme_evolution
        
        # Calculate metrics
        visualization_data["metrics"] = {
            "total_works": sum(
                data["work_count"]
                for data in analysis["decade_analysis"].values()
            ),
            "decade_count": len(analysis["decade_analysis"]),
            "theme_count": len(set(
                theme
                for decade_data in analysis["decade_analysis"].values()
                for theme, _ in decade_data["common_themes"]
            ))
        }
        
        return visualization_data
    
    def _analyze_decade(self, works: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze works from a specific decade."""
        analysis = {
            "work_count": len(works),
            "common_themes": [],
            "style_characteristics": [],
            "innovation_points": []
        }
        
        # Extract common themes
        themes = {}
        for work in works:
            if "themes" in work:
                for theme in work["themes"]:
                    themes[theme] = themes.get(theme, 0) + 1
        
        analysis["common_themes"] = sorted(
            themes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return analysis
    
    def _identify_evolution_trends(
        self,
        decade_analysis: Dict[int, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify trends in how works evolve across decades."""
        trends = []
        decades = sorted(decade_analysis.keys())
        
        for i in range(1, len(decades)):
            current_decade = decades[i]
            prev_decade = decades[i-1]
            
            trend = {
                "period": f"{prev_decade}s-{current_decade}s",
                "theme_evolution": self._compare_themes(
                    decade_analysis[prev_decade]["common_themes"],
                    decade_analysis[current_decade]["common_themes"]
                ),
                "innovation_points": self._identify_innovations(
                    decade_analysis[prev_decade],
                    decade_analysis[current_decade]
                )
            }
            
            trends.append(trend)
        
        return trends
    
    def _compare_themes(
        self,
        prev_themes: List[tuple],
        current_themes: List[tuple]
    ) -> Dict[str, Any]:
        """Compare themes between two decades."""
        prev_set = {theme[0] for theme in prev_themes}
        current_set = {theme[0] for theme in current_themes}
        
        return {
            "emerging_themes": list(current_set - prev_set),
            "declining_themes": list(prev_set - current_set),
            "persistent_themes": list(prev_set & current_set)
        }
    
    def _identify_innovations(
        self,
        prev_analysis: Dict[str, Any],
        current_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify innovative elements between decades."""
        innovations = []
        
        # Compare work counts
        if current_analysis["work_count"] > prev_analysis["work_count"] * 1.5:
            innovations.append("Significant increase in work production")
        
        # Compare themes
        prev_themes = {theme[0] for theme in prev_analysis["common_themes"]}
        current_themes = {theme[0] for theme in current_analysis["common_themes"]}
        
        if len(current_themes - prev_themes) > 2:
            innovations.append("Emergence of new thematic directions")
        
        return innovations 