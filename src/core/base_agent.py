from typing import Dict, Any, Optional
import logging

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, agent_type: Optional[str] = None):
        self.agent_type = agent_type or self.__class__.__name__.lower()
        self.name = self.agent_type
        self.logger = logging.getLogger(self.agent_type)
        
    async def execute(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a method on this agent"""
        try:
            if not hasattr(self, method):
                raise AttributeError(f"Method {method} not found in {self.agent_type}")
                
            result = await getattr(self, method)(*args, **kwargs)
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            self.logger.error(f"Error executing {method}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 