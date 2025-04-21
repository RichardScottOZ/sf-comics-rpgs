from typing import Type, Any, Dict, List, Optional
from datetime import datetime
import asyncio
import logging
from ..core.parallel_monitor import ParallelMonitor
from ..core.result_comparator import ResultComparator
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ParallelConfig:
    """Configuration for parallel execution"""
    def __init__(
        self,
        max_retries: int = 3,
        timeout: int = 30,
        cache_ttl: int = 3600
    ):
        self.max_retries = max_retries
        self.timeout = timeout
        self.cache_ttl = cache_ttl

class ParallelAgentFactory:
    """Factory for managing parallel agent instances"""
    def __init__(self, config: ParallelConfig):
        self.config = config
        self.agent_classes: Dict[str, tuple[Type[BaseAgent], Type[BaseAgent]]] = {}
        self.instances: Dict[str, tuple[BaseAgent, BaseAgent]] = {}
        self.monitor = ParallelMonitor()
        self.comparator = ResultComparator()
        self.cache: Dict[str, tuple[datetime, Any]] = {}
        logger.info("Initialized ParallelAgentFactory")

    def register_agent_class(
        self,
        name: str,
        original_class: Type[BaseAgent],
        mcp_class: Type[BaseAgent]
    ):
        """Register agent classes for parallel execution"""
        logger.info(f"Registering agent classes for {name}")
        logger.info(f"Original class: {original_class.__name__}")
        logger.info(f"MCP class: {mcp_class.__name__}")
        self.agent_classes[name] = (original_class, mcp_class)

    def _get_instances(self, name: str) -> tuple[BaseAgent, BaseAgent]:
        """Get or create agent instances"""
        logger.info(f"Getting instances for {name}")
        if name not in self.instances:
            logger.info(f"Creating new instances for {name}")
            original_class, mcp_class = self.agent_classes[name]
            try:
                original_instance = original_class()
                mcp_instance = mcp_class()
                logger.info(f"Created instances: {original_instance.name}, {mcp_instance.name}")
                self.instances[name] = (original_instance, mcp_instance)
            except Exception as e:
                logger.error(f"Error creating instances: {str(e)}")
                raise
        return self.instances[name]

    async def execute_parallel(
        self,
        agent_name: str,
        method_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute both versions in parallel"""
        logger.info(f"Executing parallel for {agent_name}.{method_name}")
        original_agent, mcp_agent = self._get_instances(agent_name)
        
        async def run_original():
            try:
                logger.info(f"Running original version of {agent_name}")
                result = await getattr(original_agent, method_name)(*args, **kwargs)
                self.monitor.track_call("original", True)
                return result
            except Exception as e:
                logger.error(f"Error in original version: {str(e)}")
                self.monitor.track_call("original", False, str(e))
                return None

        async def run_mcp():
            try:
                logger.info(f"Running MCP version of {agent_name}")
                result = await getattr(mcp_agent, method_name)(*args, **kwargs)
                self.monitor.track_call("mcp", True)
                return result
            except Exception as e:
                logger.error(f"Error in MCP version: {str(e)}")
                self.monitor.track_call("mcp", False, str(e))
                return None

        # Run both versions in parallel
        logger.info("Starting parallel execution")
        original_result, mcp_result = await asyncio.gather(
            run_original(),
            run_mcp(),
            return_exceptions=False
        )

        return {
            "original": original_result,
            "mcp": mcp_result
        }

    async def execute_smart(
        self,
        agent_name: str,
        method_name: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute using smart version selection"""
        if self._should_use_mcp(agent_name):
            original_agent, mcp_agent = self._get_instances(agent_name)
            try:
                result = await getattr(mcp_agent, method_name)(*args, **kwargs)
                self.monitor.track_call("mcp", True)
                return result
            except Exception as e:
                self.monitor.track_call("mcp", False, str(e))
                # Fallback to original version
                result = await getattr(original_agent, method_name)(*args, **kwargs)
                self.monitor.track_call("original", True)
                return result
        else:
            original_agent, _ = self._get_instances(agent_name)
            result = await getattr(original_agent, method_name)(*args, **kwargs)
            self.monitor.track_call("original", True)
            return result

    def _should_use_mcp(self, agent_name: str) -> bool:
        """Determine whether to use MCP version based on performance metrics"""
        metrics = self.monitor.get_metrics()
        
        # If no data, prefer MCP version
        if not metrics["calls"]["original"] and not metrics["calls"]["mcp"]:
            return True
            
        # Calculate success rates
        original_success_rate = (
            metrics["success"]["original"] / metrics["calls"]["original"]
            if metrics["calls"]["original"] > 0 else 0
        )
        mcp_success_rate = (
            metrics["success"]["mcp"] / metrics["calls"]["mcp"]
            if metrics["calls"]["mcp"] > 0 else 0
        )
        
        # Calculate average performance
        original_performance = metrics["performance"]["original"]["avg"]
        mcp_performance = metrics["performance"]["mcp"]["avg"]
        
        # Use MCP if:
        # 1. It has better or equal success rate AND better or equal performance
        # 2. It has slightly lower success rate (within 10%) but significantly better performance (at least 20% faster)
        if mcp_success_rate >= original_success_rate and mcp_performance <= original_performance:
            return True
        elif (original_success_rate - mcp_success_rate) <= 0.1 and mcp_performance <= 0.8 * original_performance:
            return True
            
        return False

    def get_comparison(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Get comparison of results"""
        return self.comparator.compare(results["original"], results["mcp"]) 