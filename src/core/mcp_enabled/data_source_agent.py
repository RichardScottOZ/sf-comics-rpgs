from typing import Dict, Any, List
from ..base_agent import BaseAgent

class MCPEnabledDataSourceAgent(BaseAgent):
    """MCP-enabled version of DataSourceAgent"""
    
    async def search_imdb(self, query: str) -> Dict[str, Any]:
        """Search IMDB for a query with MCP enhancements"""
        # This is a mock implementation for testing
        return {
            "items": [
                {"id": 1, "title": "Dune", "year": 2021},
                {"id": 3, "title": "Dune (1984)", "year": 1984}
            ],
            "execution_time": 0.3
        } 