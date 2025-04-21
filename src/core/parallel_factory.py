from typing import Dict, Any, Optional, Type, List
import asyncio
from datetime import datetime, timedelta
import json
import os
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
    
    def __init__(self, config: ParallelConfig):
        self.config = config
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
        self.cache_dir = "cache"
        self._setup_cache()
        self.performance_threshold = 0.1  # 10% performance difference threshold
        self.reliability_threshold = 0.95  # 95% reliability threshold
        
    def _setup_cache(self):
        """Setup cache directory and load existing cache"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_file = os.path.join(self.cache_dir, "agent_cache.json")
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
            
    def _get_cache_key(self, agent_type: str, method: str, *args, **kwargs) -> str:
        """Generate cache key from method call parameters"""
        params = {
            'agent_type': agent_type,
            'method': method,
            'args': args,
            'kwargs': kwargs
        }
        return json.dumps(params, sort_keys=True)
        
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.fromisoformat(cached['timestamp']) + timedelta(hours=1) > datetime.now():
                return cached['result']
        return None
        
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache result with timestamp"""
        self.cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'result': result
        }
        self._save_cache()
        
    def _should_use_mcp(self, agent_type: str) -> bool:
        """Determine if MCP version should be used based on performance and reliability"""
        metrics = self.monitor.get_metrics()
        
        if not metrics["original_calls"] or not metrics["mcp_calls"]:
            return True
        
        mcp_performance = metrics["mcp_performance"]
        original_performance = metrics["original_performance"]
        mcp_reliability = metrics["mcp_reliability"]
        
        return (
            mcp_reliability >= self.reliability_threshold and
            mcp_performance <= original_performance * (1 + self.performance_threshold)
        )
        
    def get_agent(self, agent_type: str, version: Optional[AgentVersion] = None) -> BaseAgent:
        """Get an agent instance of the specified type and version"""
        if agent_type not in self.agents:
            raise ValueError("Invalid agent type")
        
        if version is None:
            version = AgentVersion.MCP if self._should_use_mcp(agent_type) else AgentVersion.ORIGINAL
        
        if version not in self.agents[agent_type]:
            raise ValueError("Invalid version")
        
        return self.agents[agent_type][version]
    
    async def _execute_version(self, agent_type: str, version: AgentVersion, method: str, *args, **kwargs) -> Any:
        """Execute a method on a specific version"""
        agent = self.get_agent(agent_type, version)
        method_func = getattr(agent, method)
        
        start_time = asyncio.get_event_loop().time()
        try:
            result = await method_func(*args, **kwargs)
            execution_time = asyncio.get_event_loop().time() - start_time
            self.monitor.track_call(version, success=True, execution_time=execution_time)
            return result
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.monitor.track_call(version, success=False, execution_time=execution_time)
            raise e
    
    async def execute_parallel(self, agent_type: str, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a method in parallel on both versions"""
        results = {}
        
        for version in [AgentVersion.ORIGINAL, AgentVersion.MCP]:
            try:
                result = await self._execute_version(agent_type, version, method, *args, **kwargs)
                results[str(version)] = result
            except Exception as e:
                results[str(version)] = {"error": str(e)}
        
        return results
    
    async def execute_smart(self, agent_type: str, method: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute a method using the best performing version"""
        version = AgentVersion.MCP if self._should_use_mcp(agent_type) else AgentVersion.ORIGINAL
        result = await self._execute_version(agent_type, version, method, *args, **kwargs)
        return {str(version): result}
    
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