import pytest
from datetime import datetime
from src.core.parallel_config import AgentVersion, ParallelConfig
from src.core.parallel_factory import ParallelAgentFactory
from src.core.result_comparator import ResultComparator
from src.core.parallel_monitor import ParallelMonitor
from src.core.base_agent import BaseAgent

class MockAgent(BaseAgent):
    async def test_method(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

@pytest.fixture
def config():
    return ParallelConfig()

@pytest.fixture
def factory(config):
    return ParallelAgentFactory(config)

@pytest.fixture
def comparator():
    return ResultComparator()

@pytest.fixture
def monitor():
    return ParallelMonitor()

def test_parallel_config(config):
    """Test parallel configuration"""
    assert config.mode in ['parallel', 'original', 'mcp']
    assert config.get_agent_config('data_source') is not None
    assert config.is_version_enabled('data_source', AgentVersion.ORIGINAL)
    assert config.get_default_version('data_source') in [AgentVersion.ORIGINAL, AgentVersion.MCP]

@pytest.mark.asyncio
async def test_parallel_factory(factory):
    """Test parallel agent factory"""
    # Register mock agent class
    factory.register_agent_class("test", MockAgent, MockAgent)
    
    # Test getting original agent
    original_agent = factory.get_agent("test", AgentVersion.ORIGINAL)
    assert original_agent is not None
    
    # Test getting MCP agent
    mcp_agent = factory.get_agent("test", AgentVersion.MCP)
    assert mcp_agent is not None
    
    # Test parallel execution
    results = await factory.execute_parallel("test", "test_method", {"query": "Dune"})
    assert str(AgentVersion.ORIGINAL) in results
    assert str(AgentVersion.MCP) in results
    assert "args" in results[str(AgentVersion.ORIGINAL)]
    assert "args" in results[str(AgentVersion.MCP)]

def test_result_comparator():
    """Test the result comparator"""
    comparator = ResultComparator()
    
    # Test identical results
    result1 = {"data": "test", "count": 5}
    result2 = {"data": "test", "count": 5}
    comparison = comparator.compare(result1, result2)
    assert len(comparison["identical"]) == 2
    assert len(comparison["different"]) == 0
    assert len(comparison["missing"]) == 0
    assert len(comparison["extra"]) == 0
    
    # Test different results
    result1 = {"data": "test", "count": 5}
    result2 = {"data": "different", "count": 10}
    comparison = comparator.compare(result1, result2)
    assert len(comparison["identical"]) == 0
    assert len(comparison["different"]) == 2
    assert len(comparison["missing"]) == 0
    assert len(comparison["extra"]) == 0
    
    # Test missing keys
    result1 = {"data": "test", "count": 5}
    result2 = {"data": "test"}
    comparison = comparator.compare(result1, result2)
    assert len(comparison["identical"]) == 1
    assert len(comparison["different"]) == 0
    assert len(comparison["missing"]) == 1
    assert len(comparison["extra"]) == 0
    
    # Test extra keys
    result1 = {"data": "test"}
    result2 = {"data": "test", "count": 5}
    comparison = comparator.compare(result1, result2)
    assert len(comparison["identical"]) == 1
    assert len(comparison["different"]) == 0
    assert len(comparison["missing"]) == 0
    assert len(comparison["extra"]) == 1

def test_parallel_monitor(monitor):
    """Test parallel monitoring"""
    # Track successful call
    monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=0.5)
    monitor.track_call(AgentVersion.MCP, success=True, execution_time=0.3)
    
    # Track failed call
    monitor.track_call(AgentVersion.ORIGINAL, success=False, 
                      error=Exception("Test error"), execution_time=0.2)
    
    # Track parallel call
    monitor.track_parallel_call()
    
    # Get metrics
    metrics = monitor.get_metrics()
    assert metrics['calls']['original'] == 2
    assert metrics['calls']['mcp'] == 1
    assert metrics['calls']['parallel'] == 1
    assert len(metrics['errors']['original']) == 1
    
    # Get summary
    summary = monitor.get_summary()
    assert "Monitoring started at:" in summary
    assert "Original calls: 2" in summary
    assert "Mcp calls: 1" in summary
    assert "Parallel calls: 1" in summary 