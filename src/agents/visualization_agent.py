from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import logging
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import numpy as np
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class VisualizationAgent(BaseAgent):
    """Agent for generating visualizations from analysis data."""
    
    def __init__(self):
        super().__init__("visualization")
        self.system_prompt = """You are an expert in creating visualizations for literary analysis.
Your task is to generate clear and informative visual representations of character networks, temporal patterns, and comparative analysis results."""
        self.output_dir = "visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_visualization(
        self,
        data: Dict[str, Any],
        visualization_type: str,
        format: str = "png",
        enhanced: bool = False,
        save_to_disk: bool = False
    ) -> Dict[str, Any]:
        """Generate a visualization based on the data and type."""
        if visualization_type == "network":
            result = await self._generate_network_visualization(data, format, enhanced)
        elif visualization_type == "temporal":
            result = await self._generate_temporal_visualization(data, format, enhanced)
        elif visualization_type == "comparative":
            result = await self._generate_comparative_visualization(data, format, enhanced)
        else:
            raise ValueError(f"Unsupported visualization type: {visualization_type}")
        
        if save_to_disk:
            self._save_visualization(result, visualization_type)
        
        return result
    
    def _save_visualization(self, result: Dict[str, Any], visualization_type: str) -> str:
        """Save visualization to disk and return the file path."""
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{visualization_type}_{timestamp}.{result['format']}"
        filepath = os.path.join(self.output_dir, filename)
        
        # Decode base64 image and save to file
        image_data = base64.b64decode(result["image"])
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        logger.info(f"Saved visualization to {filepath}")
        return filepath
    
    async def _generate_network_visualization(
        self,
        data: Dict[str, Any],
        format: str,
        enhanced: bool
    ) -> Dict[str, Any]:
        """Generate a network visualization."""
        # Create the graph
        G = nx.Graph()
        
        # Add nodes
        for node in data["nodes"]:
            G.add_node(
                node["id"],
                connections=node["connections"],
                role=node["role"],
                work=node["work"],
                community=node["community"]
            )
        
        # Add edges
        for edge in data["edges"]:
            G.add_edge(edge["source"], edge["target"])
        
        # Set up the plot
        plt.figure(figsize=(12, 8))
        
        # Get node colors based on community
        node_colors = [data["nodes"][i]["community"] for i in range(len(data["nodes"]))]
        
        # Get node sizes based on connections
        node_sizes = [data["nodes"][i]["connections"] * 100 for i in range(len(data["nodes"]))]
        
        # Draw the network
        pos = nx.spring_layout(G, k=1, iterations=50)
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=node_sizes,
            cmap=plt.cm.Set3
        )
        nx.draw_networkx_edges(G, pos, alpha=0.2)
        
        if enhanced:
            # Add labels for central nodes
            labels = {
                node: node
                for node in G.nodes()
                if G.degree(node) > np.mean([d for n, d in G.degree()])
            }
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title("Character Network Analysis")
        plt.axis("off")
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format=format, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "image": image_data,
            "format": format,
            "metadata": {
                "type": "network",
                "nodes": len(data["nodes"]),
                "edges": len(data["edges"]),
                "communities": len(data["communities"])
            }
        }
    
    async def _generate_temporal_visualization(
        self,
        data: Dict[str, Any],
        format: str,
        enhanced: bool
    ) -> Dict[str, Any]:
        """Generate a temporal visualization."""
        plt.figure(figsize=(12, 8))
        
        # Prepare timeline data
        years = [int(entry["year"]) for entry in data["timeline"]]
        metrics = [entry["metrics"] for entry in data["timeline"]]
        
        # Create subplots
        if enhanced:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))
        
        # Plot metrics over time
        for metric in metrics[0].keys():
            values = [m[metric] for m in metrics]
            ax1.plot(years, values, label=metric)
        
        ax1.set_title("Temporal Analysis of Works")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Metric Value")
        ax1.legend()
        ax1.grid(True)
        
        if enhanced:
            # Plot theme evolution
            themes = set()
            for entry in data["timeline"]:
                themes.update(entry["themes"].keys())
            
            theme_data = {
                theme: [
                    entry["themes"].get(theme, 0)
                    for entry in data["timeline"]
                ]
                for theme in themes
            }
            
            for theme, values in theme_data.items():
                ax2.plot(years, values, label=theme)
            
            ax2.set_title("Theme Evolution Over Time")
            ax2.set_xlabel("Year")
            ax2.set_ylabel("Theme Presence")
            ax2.legend()
            ax2.grid(True)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format=format, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "image": image_data,
            "format": format,
            "metadata": {
                "type": "temporal",
                "time_range": f"{min(years)}-{max(years)}",
                "metrics": list(metrics[0].keys())
            }
        }
    
    async def _generate_comparative_visualization(
        self,
        data: Dict[str, Any],
        format: str,
        enhanced: bool
    ) -> Dict[str, Any]:
        """Generate a comparative visualization."""
        plt.figure(figsize=(12, 8))
        
        # Prepare data
        works = data["works"]
        metrics = data["metrics"]
        
        # Create subplots
        if enhanced:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(12, 6))
        
        # Plot metrics comparison
        x = np.arange(len(works))
        width = 0.35
        
        for i, (metric, values) in enumerate(metrics.items()):
            ax1.bar(x + i*width, values, width, label=metric)
        
        ax1.set_title("Comparative Analysis")
        ax1.set_xlabel("Works")
        ax1.set_ylabel("Metric Value")
        ax1.set_xticks(x + width/2)
        ax1.set_xticklabels(works)
        ax1.legend()
        
        if enhanced:
            # Plot similarity matrix
            similarity = data.get("similarity_matrix", [])
            if similarity:
                sns.heatmap(
                    similarity,
                    annot=True,
                    cmap="YlOrRd",
                    xticklabels=works,
                    yticklabels=works,
                    ax=ax2
                )
                ax2.set_title("Work Similarity Matrix")
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format=format, bbox_inches="tight")
        plt.close()
        
        # Convert to base64
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "image": image_data,
            "format": format,
            "metadata": {
                "type": "comparative",
                "works": works,
                "metrics": list(metrics.keys())
            }
        } 