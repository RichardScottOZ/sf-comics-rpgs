import pytest
from datetime import datetime
from src.core.parallel_config import AgentVersion, ParallelConfig
from src.core.parallel_factory import ParallelAgentFactory
from src.core.result_comparator import ResultComparator
from src.core.parallel_monitor import ParallelMonitor

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

def test_parallel_factory(factory):
    """Test parallel agent factory"""
    # Test getting original agent
    original_agent = factory.get_agent('data_source', AgentVersion.ORIGINAL)
    assert original_agent is not None
    
    # Test getting MCP agent
    mcp_agent = factory.get_agent('data_source', AgentVersion.MCP)
    assert mcp_agent is not None
    
    # Test parallel execution
    results = factory.execute_parallel('data_source', 'search_imdb', {'query': 'Dune'})
    assert 'original' in results
    assert 'mcp' in results

def test_result_comparator(comparator):
    """Test result comparison"""
    original_result = {
        'items': [
            {'id': 1, 'title': 'Dune', 'year': 2021},
            {'id': 2, 'title': 'Dune: Part Two', 'year': 2024}
        ],
        'execution_time': 0.5
    }
    
    mcp_result = {
        'items': [
            {'id': 1, 'title': 'Dune', 'year': 2021},
            {'id': 3, 'title': 'Dune (1984)', 'year': 1984}
        ],
        'execution_time': 0.3
    }
    
    comparison = comparator.compare_results(original_result, mcp_result)
    assert 'common_items' in comparison
    assert 'unique_to_original' in comparison
    assert 'unique_to_mcp' in comparison
    assert 'differences' in comparison
    
    summary = comparator.get_summary(comparison)
    assert 'Common items: 1' in summary
    assert 'Unique to original: 1' in summary
    assert 'Unique to MCP: 1' in summary

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
    assert "MCP calls: 1" in summary
    assert "Parallel calls: 1" in summary 