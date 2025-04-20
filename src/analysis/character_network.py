from typing import Dict, Any, List, Optional, Set
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class CharacterNetwork:
    """Analyzes character relationships and interactions in works."""
    
    def __init__(self):
        self.network = defaultdict(lambda: {"connections": set(), "attributes": {}})
    
    def analyze_network(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str = "relationships"
    ) -> Dict[str, Any]:
        """Analyze character networks across works."""
        if not works:
            raise ValueError("At least one work is required for network analysis")
        
        # Build the network
        for work in works:
            if "characters" in work:
                self._add_work_characters(work["characters"])
        
        # Analyze the network
        analysis = {
            "network_metrics": self._calculate_network_metrics(),
            "central_characters": self._identify_central_characters(),
            "communities": self._identify_communities(),
            "relationship_patterns": self._analyze_relationship_patterns()
        }
        
        return analysis
    
    def _add_work_characters(self, characters: List[Dict[str, Any]]) -> None:
        """Add characters and their relationships to the network."""
        for char in characters:
            char_name = char.get("name")
            if not char_name:
                continue
            
            # Add character attributes
            self.network[char_name]["attributes"].update({
                k: v for k, v in char.items() if k != "relationships"
            })
            
            # Add relationships
            if "relationships" in char:
                for rel in char["relationships"]:
                    target = rel.get("target")
                    if target:
                        self.network[char_name]["connections"].add(target)
                        self.network[target]["connections"].add(char_name)
    
    def _calculate_network_metrics(self) -> Dict[str, Any]:
        """Calculate network metrics."""
        metrics = {
            "total_characters": len(self.network),
            "average_connections": 0,
            "density": 0,
            "centralization": 0
        }
        
        if not self.network:
            return metrics
        
        # Calculate average connections
        total_connections = sum(len(data["connections"]) for data in self.network.values())
        metrics["average_connections"] = total_connections / len(self.network)
        
        # Calculate network density
        max_possible_connections = len(self.network) * (len(self.network) - 1)
        if max_possible_connections > 0:
            metrics["density"] = total_connections / max_possible_connections
        
        # Calculate centralization
        max_degree = max(len(data["connections"]) for data in self.network.values())
        if max_degree > 0:
            metrics["centralization"] = sum(
                max_degree - len(data["connections"])
                for data in self.network.values()
            ) / ((len(self.network) - 1) * (len(self.network) - 2))
        
        return metrics
    
    def _identify_central_characters(self) -> List[Dict[str, Any]]:
        """Identify the most central characters in the network."""
        centrality_scores = []
        
        for char, data in self.network.items():
            score = len(data["connections"])
            centrality_scores.append({
                "character": char,
                "centrality_score": score,
                "attributes": data["attributes"]
            })
        
        return sorted(
            centrality_scores,
            key=lambda x: x["centrality_score"],
            reverse=True
        )[:10]
    
    def _identify_communities(self) -> List[Dict[str, Any]]:
        """Identify character communities using connected components."""
        visited = set()
        communities = []
        
        for char in self.network:
            if char not in visited:
                community = self._find_community(char, visited)
                if len(community) > 1:  # Only include communities with multiple characters
                    communities.append({
                        "size": len(community),
                        "characters": list(community),
                        "density": self._calculate_community_density(community)
                    })
        
        return sorted(communities, key=lambda x: x["size"], reverse=True)
    
    def _find_community(self, start: str, visited: Set[str]) -> Set[str]:
        """Find all characters connected to the start character."""
        community = set()
        to_visit = {start}
        
        while to_visit:
            current = to_visit.pop()
            if current not in visited:
                visited.add(current)
                community.add(current)
                to_visit.update(self.network[current]["connections"] - visited)
        
        return community
    
    def _calculate_community_density(self, community: Set[str]) -> float:
        """Calculate the density of connections within a community."""
        if len(community) < 2:
            return 0.0
        
        connections = sum(
            len(self.network[char]["connections"] & community)
            for char in community
        )
        max_possible = len(community) * (len(community) - 1)
        
        return connections / max_possible if max_possible > 0 else 0.0
    
    def _analyze_relationship_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in character relationships."""
        patterns = {
            "relationship_types": defaultdict(int),
            "common_roles": defaultdict(int),
            "interaction_patterns": []
        }
        
        for char, data in self.network.items():
            # Count relationship types
            for rel in data.get("attributes", {}).get("relationships", []):
                rel_type = rel.get("type")
                if rel_type:
                    patterns["relationship_types"][rel_type] += 1
            
            # Count character roles
            role = data.get("attributes", {}).get("role")
            if role:
                patterns["common_roles"][role] += 1
        
        # Convert to lists for JSON serialization
        patterns["relationship_types"] = [
            {"type": k, "count": v}
            for k, v in patterns["relationship_types"].items()
        ]
        patterns["common_roles"] = [
            {"role": k, "count": v}
            for k, v in patterns["common_roles"].items()
        ]
        
        return patterns 