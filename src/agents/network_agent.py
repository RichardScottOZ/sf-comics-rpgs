from typing import Dict, Any, List, Optional, Set
from .base_agent import BaseAgent
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class NetworkAnalysisAgent(BaseAgent):
    """Agent for analyzing character networks and relationships using both algorithmic analysis and LLM insights."""
    
    def __init__(self):
        super().__init__("network")
        self.system_prompt = """You are an expert in analyzing character networks and relationships in science fiction, comics, and RPG content.
Your task is to provide insights about character interactions, relationship patterns, and network dynamics."""
    
    async def analyze_network(
        self,
        works: List[Dict[str, Any]],
        analysis_type: str = "relationships",
        model: Optional[str] = None,
        enhanced: bool = False
    ) -> Dict[str, Any]:
        """Analyze character networks using both algorithmic analysis and LLM insights."""
        if not works:
            raise ValueError("At least one work is required for network analysis")
        
        # Build the network
        network = self._build_network(works)
        
        # Perform algorithmic analysis
        algorithmic_analysis = self._perform_algorithmic_analysis(network)
        
        # Generate LLM insights
        llm_analysis = await self._generate_llm_insights(
            works=works,
            network=network,
            algorithmic_analysis=algorithmic_analysis,
            analysis_type=analysis_type,
            model=model,
            enhanced=enhanced
        )
        
        # Combine results
        analysis = {
            "algorithmic_analysis": algorithmic_analysis,
            "llm_insights": llm_analysis,
            "visualization_data": self._prepare_visualization_data(network, algorithmic_analysis)
        }
        
        return analysis
    
    def _build_network(self, works: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Build a character network from the works."""
        network = defaultdict(lambda: {"connections": set(), "attributes": {}})
        
        for work in works:
            if "characters" not in work:
                continue
                
            characters = work["characters"]
            for character in characters:
                char_name = character.get("name", "Unknown")
                
                # Add character attributes
                network[char_name]["attributes"].update({
                    "role": character.get("role", "Unknown"),
                    "work": work.get("title", "Unknown"),
                    "year": work.get("year", "Unknown")
                })
                
                # Add connections
                if "relationships" in character:
                    for rel in character["relationships"]:
                        target = rel.get("target", "Unknown")
                        if target != char_name:  # Avoid self-connections
                            network[char_name]["connections"].add(target)
                            network[target]["connections"].add(char_name)
        
        return network
    
    def _perform_algorithmic_analysis(
        self,
        network: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform algorithmic analysis of the network."""
        analysis = {
            "network_metrics": self._calculate_network_metrics(network),
            "central_characters": self._identify_central_characters(network),
            "communities": self._identify_communities(network),
            "relationship_patterns": self._analyze_relationship_patterns(network)
        }
        
        return analysis
    
    async def _generate_llm_insights(
        self,
        works: List[Dict[str, Any]],
        network: Dict[str, Dict[str, Any]],
        algorithmic_analysis: Dict[str, Any],
        analysis_type: str,
        model: Optional[str],
        enhanced: bool
    ) -> Dict[str, Any]:
        """Generate LLM insights about the network."""
        prompt = self._create_analysis_prompt(
            works=works,
            network=network,
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
        network: Dict[str, Dict[str, Any]],
        algorithmic_analysis: Dict[str, Any],
        analysis_type: str,
        enhanced: bool
    ) -> str:
        """Create a prompt for LLM analysis."""
        prompt_parts = [
            "Analyze the following character network:",
            "\nWorks:",
            *[f"- {work.get('title', 'Untitled')}" for work in works],
            "\nNetwork Metrics:",
            f"- Total Characters: {algorithmic_analysis['network_metrics']['total_characters']}",
            f"- Average Connections: {algorithmic_analysis['network_metrics']['avg_connections']:.2f}",
            f"- Network Density: {algorithmic_analysis['network_metrics']['density']:.2f}",
            "\nCentral Characters:",
            *[f"- {char}" for char in algorithmic_analysis['central_characters'][:5]],
            "\nCommunities:",
            *[f"- Community {i+1}: {len(comm)} characters" for i, comm in enumerate(algorithmic_analysis['communities'][:3])],
            "\nPlease provide insights about:"
        ]
        
        if enhanced:
            prompt_parts.extend([
                "1. Key character relationships and their significance",
                "2. Community dynamics and interactions",
                "3. Character roles and their impact on the network",
                "4. Network evolution across works",
                "5. Recommendations for further analysis"
            ])
        else:
            prompt_parts.extend([
                "1. Main character relationships",
                "2. Community structure",
                "3. Character roles",
                "4. Network patterns"
            ])
        
        return "\n".join(prompt_parts)
    
    def _prepare_visualization_data(
        self,
        network: Dict[str, Dict[str, Any]],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare data for visualization."""
        visualization_data = {
            "nodes": [],
            "edges": [],
            "communities": [],
            "metrics": analysis["network_metrics"]
        }
        
        # Prepare node data
        for char, data in network.items():
            visualization_data["nodes"].append({
                "id": char,
                "connections": len(data["connections"]),
                "role": data["attributes"].get("role", "Unknown"),
                "work": data["attributes"].get("work", "Unknown"),
                "community": self._get_character_community(char, analysis["communities"])
            })
        
        # Prepare edge data
        for char, data in network.items():
            for target in data["connections"]:
                if char < target:  # Avoid duplicate edges
                    visualization_data["edges"].append({
                        "source": char,
                        "target": target
                    })
        
        # Prepare community data
        for i, community in enumerate(analysis["communities"]):
            visualization_data["communities"].append({
                "id": i + 1,
                "size": len(community),
                "density": self._calculate_community_density(community, network),
                "characters": list(community)
            })
        
        return visualization_data
    
    def _calculate_network_metrics(
        self,
        network: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate network metrics."""
        total_characters = len(network)
        total_connections = sum(len(data["connections"]) for data in network.values()) // 2
        max_possible_connections = total_characters * (total_characters - 1) // 2
        
        return {
            "total_characters": total_characters,
            "total_connections": total_connections,
            "avg_connections": total_connections / total_characters if total_characters > 0 else 0,
            "density": total_connections / max_possible_connections if max_possible_connections > 0 else 0
        }
    
    def _identify_central_characters(
        self,
        network: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Identify the most central characters in the network."""
        centrality = {
            char: len(data["connections"])
            for char, data in network.items()
        }
        
        return sorted(
            centrality.keys(),
            key=lambda x: centrality[x],
            reverse=True
        )
    
    def _identify_communities(
        self,
        network: Dict[str, Dict[str, Any]]
    ) -> List[Set[str]]:
        """Identify communities in the network."""
        communities = []
        visited = set()
        
        for char in network:
            if char not in visited:
                community = self._find_community(char, network, visited)
                if len(community) > 1:  # Only include communities with more than one character
                    communities.append(community)
        
        return sorted(communities, key=len, reverse=True)
    
    def _find_community(
        self,
        start_char: str,
        network: Dict[str, Dict[str, Any]],
        visited: Set[str]
    ) -> Set[str]:
        """Find all characters connected to a starting character."""
        community = set()
        to_visit = {start_char}
        
        while to_visit:
            char = to_visit.pop()
            if char not in visited:
                visited.add(char)
                community.add(char)
                to_visit.update(network[char]["connections"] - visited)
        
        return community
    
    def _calculate_community_density(
        self,
        community: Set[str],
        network: Dict[str, Dict[str, Any]]
    ) -> float:
        """Calculate the density of connections within a community."""
        size = len(community)
        if size < 2:
            return 0.0
        
        connections = sum(
            1 for char in community
            for target in network[char]["connections"]
            if target in community
        ) // 2
        
        max_possible = size * (size - 1) // 2
        return connections / max_possible if max_possible > 0 else 0.0
    
    def _analyze_relationship_patterns(
        self,
        network: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze patterns in character relationships."""
        patterns = {
            "relationship_types": defaultdict(int),
            "common_roles": defaultdict(int)
        }
        
        for char, data in network.items():
            # Count role occurrences
            role = data["attributes"].get("role", "Unknown")
            patterns["common_roles"][role] += 1
            
            # Count relationship types
            for target in data["connections"]:
                if char < target:  # Avoid counting twice
                    patterns["relationship_types"]["connection"] += 1
        
        return patterns
    
    def _get_character_community(
        self,
        character: str,
        communities: List[Set[str]]
    ) -> int:
        """Get the community ID for a character."""
        for i, community in enumerate(communities):
            if character in community:
                return i + 1
        return 0 