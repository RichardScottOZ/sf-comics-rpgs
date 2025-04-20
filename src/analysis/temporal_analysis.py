from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from ..context.historical_context import HistoricalContext

logger = logging.getLogger(__name__)

class TemporalAnalysis:
    """Analyzes works across different time periods and their evolution."""
    
    def __init__(self):
        self.historical_context = HistoricalContext()
    
    def analyze_temporal_patterns(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str = "evolution"
    ) -> Dict[str, Any]:
        """Analyze how works evolve over time."""
        if not works:
            raise ValueError("At least one work is required for temporal analysis")
        
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