import pytest
import time
from datetime import datetime, timedelta
from src.core.parallel_monitor import ParallelMonitor
from src.core.parallel_config import AgentVersion

@pytest.fixture
def monitor():
    return ParallelMonitor()

def test_initial_state(monitor):
    """Test initial state of the monitor"""
    metrics = monitor.get_metrics()
    
    assert metrics['calls']['original'] == 0
    assert metrics['calls']['mcp'] == 0
    assert metrics['calls']['parallel'] == 0
    assert metrics['success']['original'] == 0
    assert metrics['success']['mcp'] == 0
    assert len(metrics['errors']['original']) == 0
    assert len(metrics['errors']['mcp']) == 0
    assert len(metrics['performance']['original']) == 0
    assert len(metrics['performance']['mcp']) == 0
    assert len(metrics['resource_usage']['original']) == 0
    assert len(metrics['resource_usage']['mcp']) == 0

def test_track_successful_call(monitor):
    """Test tracking a successful call"""
    execution_time = 0.5
    monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=execution_time)
    
    metrics = monitor.get_metrics()
    assert metrics['calls']['original'] == 1
    assert metrics['success']['original'] == 1
    assert len(metrics['errors']['original']) == 0
    assert len(metrics['performance']['original']) == 1
    assert metrics['performance']['original'][0] == execution_time

def test_track_failed_call(monitor):
    """Test tracking a failed call"""
    error = Exception("Test error")
    execution_time = 0.3
    monitor.track_call(AgentVersion.MCP, success=False, error=error, execution_time=execution_time)
    
    metrics = monitor.get_metrics()
    assert metrics['calls']['mcp'] == 1
    assert metrics['success']['mcp'] == 0
    assert len(metrics['errors']['mcp']) == 1
    assert metrics['errors']['mcp'][0]['error'] == str(error)
    assert len(metrics['performance']['mcp']) == 1
    assert metrics['performance']['mcp'][0] == execution_time

def test_track_parallel_call(monitor):
    """Test tracking parallel execution"""
    monitor.track_parallel_call()
    monitor.track_parallel_call()
    
    metrics = monitor.get_metrics()
    assert metrics['calls']['parallel'] == 2

def test_resource_usage_tracking(monitor):
    """Test resource usage tracking"""
    monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=0.5)
    
    metrics = monitor.get_metrics()
    assert len(metrics['resource_usage']['original']) == 1
    usage = metrics['resource_usage']['original'][0]
    
    assert 'timestamp' in usage
    assert 'usage' in usage
    assert 'execution_time' in usage
    assert usage['execution_time'] == 0.5
    
    resource_usage = usage['usage']
    assert 'cpu_percent' in resource_usage
    assert 'memory_percent' in resource_usage
    assert 'memory_rss' in resource_usage
    assert 'threads' in resource_usage

def test_success_rate_calculation(monitor):
    """Test success rate calculation"""
    # Track 10 calls with 8 successes
    for _ in range(8):
        monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=0.5)
    for _ in range(2):
        monitor.track_call(AgentVersion.ORIGINAL, success=False, execution_time=0.5)
    
    metrics = monitor.get_metrics()
    assert metrics['success_rate']['original'] == 0.8

def test_performance_statistics(monitor):
    """Test performance statistics calculation"""
    # Track multiple calls with different execution times
    times = [0.1, 0.2, 0.3, 0.4, 0.5]
    for t in times:
        monitor.track_call(AgentVersion.MCP, success=True, execution_time=t)
    
    metrics = monitor.get_metrics()
    stats = metrics['performance_stats']['mcp']
    
    assert stats['min'] == min(times)
    assert stats['max'] == max(times)
    assert stats['avg'] == sum(times) / len(times)
    assert stats['count'] == len(times)
    assert stats['p95'] == sorted(times)[int(len(times) * 0.95)]

def test_resource_statistics(monitor):
    """Test resource usage statistics calculation"""
    # Track multiple calls
    for _ in range(5):
        monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=0.5)
    
    metrics = monitor.get_metrics()
    stats = metrics['resource_stats']['original']
    
    assert 'cpu' in stats
    assert 'memory' in stats
    assert 'threads' in stats
    
    for resource in ['cpu', 'memory', 'threads']:
        assert 'avg' in stats[resource]
        assert 'max' in stats[resource]

def test_reset_metrics(monitor):
    """Test resetting metrics"""
    # Add some data
    monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=0.5)
    monitor.track_call(AgentVersion.MCP, success=False, execution_time=0.3)
    monitor.track_parallel_call()
    
    # Store start time
    original_start_time = monitor.metrics['start_time']
    
    # Reset metrics
    monitor.reset_metrics()
    
    # Verify reset
    metrics = monitor.get_metrics()
    assert metrics['calls']['original'] == 0
    assert metrics['calls']['mcp'] == 0
    assert metrics['calls']['parallel'] == 0
    assert metrics['success']['original'] == 0
    assert metrics['success']['mcp'] == 0
    assert len(metrics['errors']['original']) == 0
    assert len(metrics['errors']['mcp']) == 0
    assert len(metrics['performance']['original']) == 0
    assert len(metrics['performance']['mcp']) == 0
    assert len(metrics['resource_usage']['original']) == 0
    assert len(metrics['resource_usage']['mcp']) == 0
    
    # Verify start time preserved
    assert metrics['start_time'] == original_start_time
    assert metrics['last_reset'] != original_start_time

def test_get_summary(monitor):
    """Test summary generation"""
    # Add some data
    monitor.track_call(AgentVersion.ORIGINAL, success=True, execution_time=0.5)
    monitor.track_call(AgentVersion.MCP, success=False, execution_time=0.3)
    monitor.track_parallel_call()
    
    summary = monitor.get_summary()
    
    # Verify key elements in summary
    assert "Monitoring started at:" in summary
    assert "Last reset at:" in summary
    assert "Call Statistics:" in summary
    assert "Success Rates:" in summary
    assert "Error Counts:" in summary
    assert "Performance Statistics:" in summary
    assert "Resource Usage Statistics:" in summary 