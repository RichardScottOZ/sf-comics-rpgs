from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AgentVersion(Enum):
    ORIGINAL = "original"
    MCP = "mcp"

@dataclass
class AgentConfig:
    original: bool = True
    mcp: bool = True
    default: AgentVersion = AgentVersion.ORIGINAL

class ParallelConfig:
    """Configuration for parallel operation of agents"""
    
    def __init__(self):
        self.mode = 'parallel'  # 'parallel', 'original', or 'mcp'
        self.agents: Dict[str, AgentConfig] = {
            'data_source': AgentConfig(),
            'monitoring': AgentConfig(),
            'analysis': AgentConfig()
        }
        
    def get_agent_config(self, agent_type: str) -> AgentConfig:
        """Get configuration for specific agent type"""
        return self.agents.get(agent_type, AgentConfig())
    
    def is_version_enabled(self, agent_type: str, version: AgentVersion) -> bool:
        """Check if specific version of agent is enabled"""
        config = self.get_agent_config(agent_type)
        if version == AgentVersion.ORIGINAL:
            return config.original
        return config.mcp
    
    def get_default_version(self, agent_type: str) -> AgentVersion:
        """Get default version for agent type"""
        return self.get_agent_config(agent_type).default 