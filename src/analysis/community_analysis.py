from typing import Dict, Any, List, Optional, Set
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

class CommunityAnalysis:
    """Analyzes patterns and trends across works and their communities."""
    
    def __init__(self):
        self.works_by_community = defaultdict(list)
        self.community_metrics = defaultdict(dict)
    
    def analyze_communities(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str = "patterns"
    ) -> Dict[str, Any]:
        """Analyze works across different communities."""
        if not works:
            raise ValueError("At least one work is required for community analysis")
        
        # Group works by community
        for work in works:
            communities = self._extract_communities(work)
            for community in communities:
                self.works_by_community[community].append(work)
        
        # Analyze each community
        analysis = {
            "community_metrics": {},
            "cross_community_patterns": {},
            "trends": self._analyze_trends(),
            "recommendations": self._generate_recommendations()
        }
        
        for community, community_works in self.works_by_community.items():
            analysis["community_metrics"][community] = self._analyze_community(community_works)
        
        analysis["cross_community_patterns"] = self._analyze_cross_community_patterns()
        
        return analysis
    
    def _extract_communities(self, work: Dict[str, Any]) -> Set[str]:
        """Extract communities from a work."""
        communities = set()
        
        # Add genre-based communities
        if "genres" in work:
            communities.update(work["genres"])
        
        # Add theme-based communities
        if "themes" in work:
            communities.update(work["themes"])
        
        # Add author-based communities
        if "author" in work:
            communities.add(f"author:{work['author']}")
        
        # Add temporal communities
        if "year" in work:
            decade = (work["year"] // 10) * 10
            communities.add(f"decade:{decade}s")
        
        return communities
    
    def _analyze_community(self, works: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a specific community of works."""
        metrics = {
            "work_count": len(works),
            "average_rating": 0,
            "common_themes": [],
            "style_characteristics": [],
            "innovation_score": 0
        }
        
        if not works:
            return metrics
        
        # Calculate average rating
        ratings = [w.get("rating", 0) for w in works if w.get("rating")]
        if ratings:
            metrics["average_rating"] = sum(ratings) / len(ratings)
        
        # Extract common themes
        themes = defaultdict(int)
        for work in works:
            if "themes" in work:
                for theme in work["themes"]:
                    themes[theme] += 1
        
        metrics["common_themes"] = sorted(
            themes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Calculate innovation score
        metrics["innovation_score"] = self._calculate_innovation_score(works)
        
        return metrics
    
    def _calculate_innovation_score(self, works: List[Dict[str, Any]]) -> float:
        """Calculate an innovation score for a community of works."""
        if not works:
            return 0.0
        
        score = 0.0
        total_weight = 0
        
        # Consider thematic novelty
        if len(works) > 1:
            unique_themes = set()
            for work in works:
                if "themes" in work:
                    unique_themes.update(work["themes"])
            score += len(unique_themes) / len(works)
            total_weight += 1
        
        # Consider temporal spread
        years = [w.get("year") for w in works if w.get("year")]
        if years:
            year_range = max(years) - min(years)
            score += year_range / 100  # Normalize by 100 years
            total_weight += 1
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _analyze_cross_community_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across different communities."""
        patterns = {
            "overlapping_communities": self._find_overlapping_communities(),
            "community_evolution": self._analyze_community_evolution(),
            "influence_patterns": self._identify_influence_patterns()
        }
        
        return patterns
    
    def _find_overlapping_communities(self) -> List[Dict[str, Any]]:
        """Find communities that share significant overlap."""
        overlaps = []
        communities = list(self.works_by_community.keys())
        
        for i in range(len(communities)):
            for j in range(i + 1, len(communities)):
                comm1, comm2 = communities[i], communities[j]
                overlap = self._calculate_community_overlap(comm1, comm2)
                
                if overlap > 0.3:  # Threshold for significant overlap
                    overlaps.append({
                        "communities": [comm1, comm2],
                        "overlap_score": overlap,
                        "shared_works": len(
                            set(self.works_by_community[comm1]) &
                            set(self.works_by_community[comm2])
                        )
                    })
        
        return sorted(overlaps, key=lambda x: x["overlap_score"], reverse=True)
    
    def _calculate_community_overlap(self, comm1: str, comm2: str) -> float:
        """Calculate the overlap between two communities."""
        works1 = set(self.works_by_community[comm1])
        works2 = set(self.works_by_community[comm2])
        
        if not works1 or not works2:
            return 0.0
        
        intersection = len(works1 & works2)
        union = len(works1 | works2)
        
        return intersection / union if union > 0 else 0.0
    
    def _analyze_community_evolution(self) -> List[Dict[str, Any]]:
        """Analyze how communities evolve over time."""
        evolution = []
        
        # Group communities by decade
        decade_communities = defaultdict(set)
        for community in self.works_by_community:
            if community.startswith("decade:"):
                decade = int(community.split(":")[1].rstrip("s"))
                decade_communities[decade].add(community)
        
        # Analyze evolution between decades
        decades = sorted(decade_communities.keys())
        for i in range(1, len(decades)):
            prev_decade = decades[i-1]
            current_decade = decades[i]
            
            evolution.append({
                "period": f"{prev_decade}s-{current_decade}s",
                "emerging_communities": list(
                    decade_communities[current_decade] -
                    decade_communities[prev_decade]
                ),
                "declining_communities": list(
                    decade_communities[prev_decade] -
                    decade_communities[current_decade]
                ),
                "persistent_communities": list(
                    decade_communities[prev_decade] &
                    decade_communities[current_decade]
                )
            })
        
        return evolution
    
    def _identify_influence_patterns(self) -> List[Dict[str, Any]]:
        """Identify patterns of influence between communities."""
        influences = []
        
        # Analyze author-based influences
        author_communities = {
            comm: works for comm, works in self.works_by_community.items()
            if comm.startswith("author:")
        }
        
        for author, works in author_communities.items():
            if len(works) > 1:
                # Look for thematic evolution
                themes_by_year = defaultdict(set)
                for work in works:
                    if "year" in work and "themes" in work:
                        themes_by_year[work["year"]].update(work["themes"])
                
                if len(themes_by_year) > 1:
                    influences.append({
                        "source": author,
                        "type": "thematic_evolution",
                        "pattern": self._analyze_thematic_evolution(themes_by_year)
                    })
        
        return influences
    
    def _analyze_thematic_evolution(self, themes_by_year: Dict[int, Set[str]]) -> Dict[str, Any]:
        """Analyze how themes evolve over time for an author."""
        years = sorted(themes_by_year.keys())
        evolution = {
            "period": f"{years[0]}-{years[-1]}",
            "emerging_themes": [],
            "persistent_themes": set(themes_by_year[years[0]])
        }
        
        for i in range(1, len(years)):
            current_themes = themes_by_year[years[i]]
            prev_themes = themes_by_year[years[i-1]]
            
            evolution["emerging_themes"].extend(list(current_themes - prev_themes))
            evolution["persistent_themes"] &= current_themes
        
        evolution["persistent_themes"] = list(evolution["persistent_themes"])
        
        return evolution
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on community analysis."""
        recommendations = []
        
        # Recommend based on community strength
        for community, metrics in self.community_metrics.items():
            if metrics.get("innovation_score", 0) > 0.7:
                recommendations.append({
                    "type": "innovative_community",
                    "community": community,
                    "reason": "High innovation score",
                    "suggested_actions": [
                        "Explore emerging themes",
                        "Analyze narrative techniques",
                        "Study character development patterns"
                    ]
                })
        
        # Recommend based on cross-community patterns
        overlaps = self._find_overlapping_communities()
        for overlap in overlaps[:3]:  # Top 3 overlaps
            if overlap["overlap_score"] > 0.5:
                recommendations.append({
                    "type": "community_synergy",
                    "communities": overlap["communities"],
                    "reason": "Strong community overlap",
                    "suggested_actions": [
                        "Compare narrative structures",
                        "Analyze thematic intersections",
                        "Study character archetypes"
                    ]
                })
        
        return recommendations 