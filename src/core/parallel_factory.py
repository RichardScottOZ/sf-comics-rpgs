from typing import Dict, Any, Optional, Type
from .parallel_config import ParallelConfig, AgentVersion
from .base_agent import BaseAgent
from .data_source_agent import DataSourceAgent
from .monitoring_agent import MonitoringAgent
from .analysis_agent import AnalysisAgent
from .mcp_enabled.data_source_agent import MCPEnabledDataSourceAgent
from .mcp_enabled.monitoring_agent import MCPEnabledMonitoringAgent
from .mcp_enabled.analysis_agent import MCPEnabledAnalysisAgent

class ParallelAgentFactory:
    """Factory for creating and managing parallel agent instances"""
    
    def __init__(self, config: Optional[ParallelConfig] = None):
        self.config = config or ParallelConfig()
        self.agents: Dict[str, Dict[AgentVersion, BaseAgent]] = {}
        self.agent_classes: Dict[str, Dict[AgentVersion, Type[BaseAgent]]] = {
            'data_source': {
                AgentVersion.ORIGINAL: DataSourceAgent,
                AgentVersion.MCP: MCPEnabledDataSourceAgent
            },
            'monitoring': {
                AgentVersion.ORIGINAL: MonitoringAgent,
                AgentVersion.MCP: MCPEnabledMonitoringAgent
            },
            'analysis': {
                AgentVersion.ORIGINAL: AnalysisAgent,
                AgentVersion.MCP: MCPEnabledAnalysisAgent
            }
        }
        
    def get_agent(self, agent_type: str, version: Optional[AgentVersion] = None) -> BaseAgent:
        """Get agent instance, optionally specifying version"""
        if version is None:
            version = self.config.get_default_version(agent_type)
            
        if not self.config.is_version_enabled(agent_type, version):
            raise ValueError(f"Version {version} not enabled for agent type {agent_type}")
            
        if agent_type not in self.agents:
            self.agents[agent_type] = {}
            
        if version not in self.agents[agent_type]:
            agent_class = self.agent_classes[agent_type][version]
            self.agents[agent_type][version] = agent_class()
            
        return self.agents[agent_type][version]
    
    async def execute_parallel(self, agent_type: str, method: str, *args, **kwargs) -> Dict[AgentVersion, Any]:
        """Execute method on both versions in parallel"""
        results = {}
        
        for version in [AgentVersion.ORIGINAL, AgentVersion.MCP]:
            if self.config.is_version_enabled(agent_type, version):
                try:
                    agent = self.get_agent(agent_type, version)
                    results[version] = await getattr(agent, method)(*args, **kwargs)
                except Exception as e:
                    results[version] = {"error": str(e)}
                    
        return results
    
    def get_available_versions(self, agent_type: str) -> list[AgentVersion]:
        """Get list of available versions for agent type"""
        return [
            version for version in AgentVersion
            if self.config.is_version_enabled(agent_type, version)
        ] 