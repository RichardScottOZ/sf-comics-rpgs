from typing import Dict, Any, List
from .base_agent import BaseAgent

class DataSourceAgent(BaseAgent):
    """Agent for handling data source operations"""
    
    async def search_imdb(self, query: str) -> Dict[str, Any]:
        """Search IMDB for a query"""
        # This is a mock implementation for testing
        return {
            "items": [
                {"id": 1, "title": "Dune", "year": 2021},
                {"id": 2, "title": "Dune: Part Two", "year": 2024}
            ],
            "execution_time": 0.5
        } 