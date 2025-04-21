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
        self.agent_classes: Dict[str, Dict[AgentVersion, Type[BaseAgent]]] = {}
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
        
    def register_agent_class(self, agent_type: str, original_class: Type[BaseAgent], mcp_class: Type[BaseAgent]):
        """Register agent classes for a specific type"""
        self.agent_classes[agent_type] = {
            AgentVersion.ORIGINAL: original_class,
            AgentVersion.MCP: mcp_class
        }
    
    def get_agent(self, agent_type: str, version: Optional[AgentVersion] = None) -> BaseAgent:
        """Get an agent instance of the specified type and version"""
        if agent_type not in self.agent_classes:
            raise ValueError(f"Agent type '{agent_type}' not registered")
        
        if version is None:
            version = AgentVersion.MCP if self._should_use_mcp(agent_type) else AgentVersion.ORIGINAL
        
        if version not in self.agent_classes[agent_type]:
            raise ValueError(f"Version '{version}' not available for agent type '{agent_type}'")
        
        if agent_type not in self.agents:
            self.agents[agent_type] = {}
        
        if version not in self.agents[agent_type]:
            agent_class = self.agent_classes[agent_type][version]
            self.agents[agent_type][version] = agent_class()
        
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
    
    def _should_use_mcp(self, agent_type: str) -> bool:
        """Determine if MCP version should be used based on performance and reliability"""
        metrics = self.monitor.get_metrics()
        
        # If we don't have enough data yet, use MCP
        if not metrics['calls']['original'] or not metrics['calls']['mcp']:
            return True
            
        # Calculate success rates
        original_success_rate = metrics['success_rate']['original']
        mcp_success_rate = metrics['success_rate']['mcp']
        
        # Calculate average performance
        original_perf = metrics['performance_stats']['original'].get('avg', float('inf'))
        mcp_perf = metrics['performance_stats']['mcp'].get('avg', float('inf'))
        
        # Use MCP if it has better success rate and similar or better performance
        # Or if it's significantly faster (20% or more) even with slightly lower reliability
        return (mcp_success_rate > original_success_rate and mcp_perf <= original_perf * 1.2) or \
               (mcp_perf <= original_perf * 0.8 and mcp_success_rate >= original_success_rate * 0.9)

    def should_use_mcp(self) -> bool:
        """Determine if MCP version should be used based on metrics"""
        metrics = self.monitor.get_metrics()
        
        # If we don't have enough data yet, use original version
        if metrics['calls']['original'] < 10 or metrics['calls']['mcp'] < 10:
            return False
            
        # Calculate success rates
        original_success_rate = metrics['success_rate']['original']
        mcp_success_rate = metrics['success_rate']['mcp']
        
        # Calculate average performance
        original_perf = metrics['performance_stats']['original'].get('avg', float('inf'))
        mcp_perf = metrics['performance_stats']['mcp'].get('avg', float('inf'))
        
        # Use MCP if it has better success rate and similar or better performance
        return mcp_success_rate > original_success_rate and mcp_perf <= original_perf * 1.2 