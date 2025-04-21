from typing import Dict, Any, Optional, Type
import asyncio
from .parallel_config import ParallelConfig, AgentVersion
from .base_agent import BaseAgent
from .data_source_agent import DataSourceAgent
from .monitoring_agent import MonitoringAgent
from .analysis_agent import AnalysisAgent
from .mcp_enabled.data_source_agent import MCPEnabledDataSourceAgent
from .mcp_enabled.monitoring_agent import MCPEnabledMonitoringAgent
from .mcp_enabled.analysis_agent import MCPEnabledAnalysisAgent
from .result_comparator import ResultComparator
from .parallel_monitor import ParallelMonitor

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
        self.comparator = ResultComparator()
        self.monitor = ParallelMonitor()
        
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
    
    async def _execute_version(self, agent_type: str, version: AgentVersion, 
                             method: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a method on a specific version of an agent"""
        start_time = asyncio.get_event_loop().time()
        try:
            agent = self.get_agent(agent_type, version)
            result = await getattr(agent, method)(*args, **kwargs)
            execution_time = asyncio.get_event_loop().time() - start_time
            
            self.monitor.track_call(version, success=True, execution_time=execution_time)
            return result
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.monitor.track_call(version, success=False, error=e, execution_time=execution_time)
            return {"error": str(e)}
    
    async def execute_parallel(self, agent_type: str, method: str, 
                             *args, **kwargs) -> Dict[AgentVersion, Any]:
        """Execute method on both versions in parallel"""
        self.monitor.track_parallel_call()
        
        # Create tasks for both versions
        tasks = []
        for version in [AgentVersion.ORIGINAL, AgentVersion.MCP]:
            if self.config.is_version_enabled(agent_type, version):
                task = self._execute_version(agent_type, version, method, *args, **kwargs)
                tasks.append(task)
        
        # Execute tasks in parallel
        results = {}
        if tasks:
            completed = await asyncio.gather(*tasks, return_exceptions=True)
            for version, result in zip([v for v in [AgentVersion.ORIGINAL, AgentVersion.MCP] 
                                     if self.config.is_version_enabled(agent_type, v)], completed):
                results[version] = result
        
        return results
    
    def get_comparison(self, results: Dict[AgentVersion, Any]) -> Dict[str, Any]:
        """Get comparison of results from both versions"""
        if AgentVersion.ORIGINAL in results and AgentVersion.MCP in results:
            return self.comparator.compare_results(
                results[AgentVersion.ORIGINAL],
                results[AgentVersion.MCP]
            )
        return {}
    
    def get_available_versions(self, agent_type: str) -> list[AgentVersion]:
        """Get list of available versions for agent type"""
        return [
            version for version in AgentVersion
            if self.config.is_version_enabled(agent_type, version)
        ] 