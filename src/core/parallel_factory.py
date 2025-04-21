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
        self.cache_dir = "cache"
        self._setup_cache()
        self.performance_threshold = 0.1  # 10% performance difference threshold
        self.reliability_threshold = 0.95  # 95% success rate threshold
        
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
        
        # Check if we have enough data
        if metrics['calls']['mcp'] < 10:
            return True
            
        # Check performance
        mcp_perf = metrics['performance_stats']['mcp']
        orig_perf = metrics['performance_stats']['original']
        
        if mcp_perf and orig_perf:
            mcp_avg = mcp_perf['avg']
            orig_avg = orig_perf['avg']
            perf_diff = abs(mcp_avg - orig_avg) / orig_avg
            
            if perf_diff > self.performance_threshold:
                return mcp_avg < orig_avg
                
        # Check reliability
        mcp_success = metrics['success_rate']['mcp']
        if mcp_success < self.reliability_threshold:
            return False
            
        return True
        
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
        
        # Check cache first
        cache_key = self._get_cache_key(agent_type, method, *args, **kwargs)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
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
                
        # Cache results
        self._cache_result(cache_key, results)
        
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
        
    async def execute_smart(self, agent_type: str, method: str, 
                          *args, **kwargs) -> Dict[str, Any]:
        """Execute method using smart version selection"""
        # Check cache first
        cache_key = self._get_cache_key(agent_type, method, *args, **kwargs)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        # Determine which version to use
        use_mcp = self._should_use_mcp(agent_type)
        version = AgentVersion.MCP if use_mcp else AgentVersion.ORIGINAL
        
        # Execute selected version
        result = await self._execute_version(agent_type, version, method, *args, **kwargs)
        
        # Cache result
        self._cache_result(cache_key, {version: result})
        
        return {version: result} 