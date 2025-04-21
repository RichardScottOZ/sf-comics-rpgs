import pytest
import asyncio
import os
import json
from datetime import datetime, timedelta
from src.core.parallel_factory import ParallelAgentFactory
from src.core.parallel_config import ParallelConfig, AgentVersion
from src.core.base_agent import BaseAgent
from src.core.result_comparator import ResultComparator

class MockAgent(BaseAgent):
    async def test_method(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}

@pytest.fixture
def factory():
    config = ParallelConfig()
    factory = ParallelAgentFactory(config)
    factory.agent_classes = {
        'test': {
            AgentVersion.ORIGINAL: MockAgent,
            AgentVersion.MCP: MockAgent
        }
    }
    return factory

@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "cache"

def test_initialization(factory):
    """Test factory initialization"""
    assert factory.config is not None
    assert isinstance(factory.agents, dict)
    assert isinstance(factory.comparator, ResultComparator)
    assert isinstance(factory.monitor, ParallelMonitor)
    assert factory.performance_threshold == 0.1
    assert factory.reliability_threshold == 0.95

def test_get_agent(factory):
    """Test getting agent instances"""
    # Get original version
    agent = factory.get_agent('test', AgentVersion.ORIGINAL)
    assert isinstance(agent, MockAgent)
    
    # Get MCP version
    agent = factory.get_agent('test', AgentVersion.MCP)
    assert isinstance(agent, MockAgent)
    
    # Get default version
    agent = factory.get_agent('test')
    assert isinstance(agent, MockAgent)

def test_get_agent_invalid_type(factory):
    """Test getting agent with invalid type"""
    with pytest.raises(ValueError, match="Version .* not enabled for agent type"):
        factory.get_agent('invalid_type')

def test_get_agent_invalid_version(factory):
    """Test getting agent with invalid version"""
    with pytest.raises(ValueError, match="Version .* not enabled for agent type"):
        factory.get_agent('test', 'invalid_version')

@pytest.mark.asyncio
async def test_execute_version(factory):
    """Test executing a method on a specific version"""
    result = await factory._execute_version('test', AgentVersion.ORIGINAL, 'test_method', 'arg1', kwarg1='value1')
    assert result == {"args": ('arg1',), "kwargs": {'kwarg1': 'value1'}}

@pytest.mark.asyncio
async def test_execute_version_error(factory):
    """Test executing a method that raises an error"""
    result = await factory._execute_version('test', AgentVersion.ORIGINAL, 'nonexistent_method')
    assert "error" in result

@pytest.mark.asyncio
async def test_execute_parallel(factory):
    """Test parallel execution"""
    results = await factory.execute_parallel('test', 'test_method', 'arg1', kwarg1='value1')
    
    assert str(AgentVersion.ORIGINAL) in results
    assert str(AgentVersion.MCP) in results
    assert results[str(AgentVersion.ORIGINAL)] == {"args": ('arg1',), "kwargs": {'kwarg1': 'value1'}}
    assert results[str(AgentVersion.MCP)] == {"args": ('arg1',), "kwargs": {'kwarg1': 'value1'}}

@pytest.mark.asyncio
async def test_execute_smart(factory):
    """Test smart execution"""
    # First call should use MCP (default)
    result = await factory.execute_smart('test', 'test_method', 'arg1')
    assert str(AgentVersion.MCP) in result
    
    # Add some performance data
    for _ in range(15):
        await factory._execute_version('test', AgentVersion.ORIGINAL, 'test_method', 'arg1')
        await factory._execute_version('test', AgentVersion.MCP, 'test_method', 'arg1')
    
    # Now should choose based on performance
    result = await factory.execute_smart('test', 'test_method', 'arg1')
    assert len(result) == 1
    assert list(result.keys())[0] in [str(AgentVersion.ORIGINAL), str(AgentVersion.MCP)]

def test_get_comparison(factory):
    """Test result comparison"""
    results = {
        str(AgentVersion.ORIGINAL): {"data": "original"},
        str(AgentVersion.MCP): {"data": "mcp"}
    }
    comparison = factory.get_comparison(results)
    assert isinstance(comparison, dict)

def test_get_available_versions(factory):
    """Test getting available versions"""
    versions = factory.get_available_versions('test')
    assert len(versions) == 2
    assert AgentVersion.ORIGINAL in versions
    assert AgentVersion.MCP in versions

def test_cache_operations(factory, cache_dir):
    """Test cache operations"""
    # Setup cache
    factory.cache_dir = str(cache_dir)
    factory._setup_cache()
    
    # Test cache key generation
    cache_key = factory._get_cache_key('test', 'test_method', 'arg1', kwarg1='value1')
    assert isinstance(cache_key, str)
    
    # Test caching and retrieval
    result = {"test": "result"}
    factory._cache_result(cache_key, result)
    
    cached = factory._get_cached_result(cache_key)
    assert cached == result
    
    # Test cache expiration
    factory.cache[cache_key]['timestamp'] = (datetime.now() - timedelta(hours=2)).isoformat()
    cached = factory._get_cached_result(cache_key)
    assert cached is None

def test_should_use_mcp(factory):
    """Test MCP version selection logic"""
    # With no data, should use MCP
    assert factory._should_use_mcp('test') is True
    
    # Add some performance data
    for _ in range(15):
        factory.monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=0.5)
        factory.monitor.track_call(AgentVersion.MCP, success=True, execution_time=0.4)
    
    # MCP is faster, should use MCP
    assert factory._should_use_mcp('test') is True
    
    # Make MCP slower
    for _ in range(5):
        factory.monitor.track_call(AgentVersion.MCP, success=True, execution_time=0.6)
    
    # Original is now faster, should use original
    assert factory._should_use_mcp('test') is False
    
    # Make MCP unreliable
    for _ in range(5):
        factory.monitor.track_call(AgentVersion.MCP, success=False, execution_time=0.4)
    
    # MCP is unreliable, should use original
    assert factory._should_use_mcp('test') is False 