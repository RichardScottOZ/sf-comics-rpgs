from typing import Dict, Any, Optional
import logging

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__.lower()
        self.logger = logging.getLogger(self.name)
        
    async def execute(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a method on this agent"""
        try:
            if not hasattr(self, method):
                raise AttributeError(f"Method {method} not found in {self.name}")
                
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