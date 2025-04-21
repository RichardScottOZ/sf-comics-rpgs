from typing import Dict, Any, List, Optional
from datetime import datetime
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
            'start_time': datetime.now().isoformat()
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
                'error': str(error)
            })
            
        # Track performance
        if execution_time > 0:
            self.metrics['performance'][version_str].append(execution_time)
            
    def track_parallel_call(self):
        """Track parallel execution"""
        self.metrics['calls']['parallel'] += 1
        
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
                    'count': len(times)
                }
            else:
                metrics['performance_stats'][version] = {}
                
        return metrics
    
    def get_summary(self) -> str:
        """Get human-readable summary of metrics"""
        metrics = self.get_metrics()
        summary = []
        
        summary.append(f"Monitoring started at: {metrics['start_time']}")
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
                    f"  Samples: {stats['count']}"
                ])
                
        return "\n".join(summary) 