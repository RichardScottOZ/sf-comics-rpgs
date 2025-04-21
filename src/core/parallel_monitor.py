from typing import Dict, Any, List, Optional
from datetime import datetime
import psutil
import time
from .parallel_config import AgentVersion

class ParallelMonitor:
    """Monitor parallel operation performance and metrics"""
    
    def __init__(self):
        self.metrics = {
            'calls': {
                'original': 0,
                'mcp': 0,
                'parallel': 0
            },
            'success': {
                'original': 0,
                'mcp': 0
            },
            'errors': {
                'original': [],
                'mcp': []
            },
            'performance': {
                'original': [],
                'mcp': []
            },
            'resource_usage': {
                'original': [],
                'mcp': []
            },
            'start_time': datetime.now().isoformat(),
            'last_reset': datetime.now().isoformat()
        }
        
    def _get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_rss': process.memory_info().rss / 1024 / 1024,  # MB
            'threads': process.num_threads()
        }
        
    def track_call(self, version: AgentVersion, success: bool = True, 
                  error: Optional[Exception] = None, execution_time: float = 0):
        """Track API call and its outcome"""
        version_str = version.value
        
        # Track call count
        self.metrics['calls'][version_str] += 1
        
        # Track success/failure
        if success:
            self.metrics['success'][version_str] += 1
        else:
            self.metrics['errors'][version_str].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(error),
                'traceback': getattr(error, '__traceback__', None)
            })
            
        # Track performance
        if execution_time > 0:
            self.metrics['performance'][version_str].append(execution_time)
            
        # Track resource usage
        self.metrics['resource_usage'][version_str].append({
            'timestamp': datetime.now().isoformat(),
            'usage': self._get_resource_usage(),
            'execution_time': execution_time
        })
            
    def track_parallel_call(self):
        """Track parallel execution"""
        self.metrics['calls']['parallel'] += 1
        
    def reset_metrics(self):
        """Reset all metrics while preserving start time"""
        start_time = self.metrics['start_time']
        self.metrics = {
            'calls': {
                'original': 0,
                'mcp': 0,
                'parallel': 0
            },
            'success': {
                'original': 0,
                'mcp': 0
            },
            'errors': {
                'original': [],
                'mcp': []
            },
            'performance': {
                'original': [],
                'mcp': []
            },
            'resource_usage': {
                'original': [],
                'mcp': []
            },
            'start_time': start_time,
            'last_reset': datetime.now().isoformat()
        }
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics with statistics"""
        metrics = self.metrics.copy()
        
        # Calculate success rates
        metrics['success_rate'] = {}
        for version in ['original', 'mcp']:
            total_calls = metrics['calls'][version]
            if total_calls > 0:
                metrics['success_rate'][version] = metrics['success'][version] / total_calls
            else:
                metrics['success_rate'][version] = 0
                
        # Calculate performance statistics
        metrics['performance_stats'] = {}
        for version in ['original', 'mcp']:
            times = metrics['performance'][version]
            if times:
                metrics['performance_stats'][version] = {
                    'min': min(times),
                    'max': max(times),
                    'avg': sum(times) / len(times),
                    'count': len(times),
                    'p95': sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
                }
            else:
                metrics['performance_stats'][version] = {}
                
        # Calculate resource usage statistics
        metrics['resource_stats'] = {}
        for version in ['original', 'mcp']:
            usages = metrics['resource_usage'][version]
            if usages:
                metrics['resource_stats'][version] = {
                    'cpu': {
                        'avg': sum(u['usage']['cpu_percent'] for u in usages) / len(usages),
                        'max': max(u['usage']['cpu_percent'] for u in usages)
                    },
                    'memory': {
                        'avg': sum(u['usage']['memory_percent'] for u in usages) / len(usages),
                        'max': max(u['usage']['memory_percent'] for u in usages),
                        'rss_avg': sum(u['usage']['memory_rss'] for u in usages) / len(usages),
                        'rss_max': max(u['usage']['memory_rss'] for u in usages)
                    },
                    'threads': {
                        'avg': sum(u['usage']['threads'] for u in usages) / len(usages),
                        'max': max(u['usage']['threads'] for u in usages)
                    }
                }
            else:
                metrics['resource_stats'][version] = {}
                
        return metrics
    
    def get_summary(self) -> str:
        """Get human-readable summary of metrics"""
        metrics = self.get_metrics()
        summary = []
        
        summary.append(f"Monitoring started at: {metrics['start_time']}")
        summary.append(f"Last reset at: {metrics['last_reset']}")
        
        summary.append("\nCall Statistics:")
        for version in ['original', 'mcp', 'parallel']:
            summary.append(f"{version.title()} calls: {metrics['calls'][version]}")
            
        summary.append("\nSuccess Rates:")
        for version in ['original', 'mcp']:
            rate = metrics['success_rate'][version]
            summary.append(f"{version.title()} success rate: {rate:.2%}")
            
        summary.append("\nError Counts:")
        for version in ['original', 'mcp']:
            summary.append(f"{version.title()} errors: {len(metrics['errors'][version])}")
            
        summary.append("\nPerformance Statistics:")
        for version in ['original', 'mcp']:
            stats = metrics['performance_stats'][version]
            if stats:
                summary.extend([
                    f"{version.title()} Performance:",
                    f"  Min time: {stats['min']:.2f}s",
                    f"  Max time: {stats['max']:.2f}s",
                    f"  Avg time: {stats['avg']:.2f}s",
                    f"  P95 time: {stats['p95']:.2f}s",
                    f"  Samples: {stats['count']}"
                ])
                
        summary.append("\nResource Usage Statistics:")
        for version in ['original', 'mcp']:
            stats = metrics['resource_stats'][version]
            if stats:
                summary.extend([
                    f"{version.title()} Resource Usage:",
                    f"  CPU:",
                    f"    Avg: {stats['cpu']['avg']:.1f}%",
                    f"    Max: {stats['cpu']['max']:.1f}%",
                    f"  Memory:",
                    f"    Avg: {stats['memory']['avg']:.1f}%",
                    f"    Max: {stats['memory']['max']:.1f}%",
                    f"    RSS Avg: {stats['memory']['rss_avg']:.1f}MB",
                    f"    RSS Max: {stats['memory']['rss_max']:.1f}MB",
                    f"  Threads:",
                    f"    Avg: {stats['threads']['avg']:.1f}",
                    f"    Max: {stats['threads']['max']}"
                ])
                
        return "\n".join(summary) 