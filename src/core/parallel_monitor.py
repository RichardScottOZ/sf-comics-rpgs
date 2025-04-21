from typing import Dict, Any, List, Optional
from datetime import datetime
import psutil
import time
from .parallel_config import AgentVersion

class ParallelMonitor:
    """Monitor for tracking parallel execution metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "original_calls": 0,
            "mcp_calls": 0,
            "original_success": 0,
            "mcp_success": 0,
            "original_performance": 0.0,
            "mcp_performance": 0.0,
            "original_errors": [],
            "mcp_errors": []
        }
    
    def track_call(self, version: AgentVersion, success: bool, execution_time: float, error: Exception = None):
        """Track a method call"""
        if version == AgentVersion.ORIGINAL:
            self.metrics["original_calls"] += 1
            if success:
                self.metrics["original_success"] += 1
                self.metrics["original_performance"] = (
                    (self.metrics["original_performance"] * (self.metrics["original_success"] - 1) + execution_time) /
                    self.metrics["original_success"]
                )
            else:
                self.metrics["original_errors"].append(str(error))
        else:
            self.metrics["mcp_calls"] += 1
            if success:
                self.metrics["mcp_success"] += 1
                self.metrics["mcp_performance"] = (
                    (self.metrics["mcp_performance"] * (self.metrics["mcp_success"] - 1) + execution_time) /
                    self.metrics["mcp_success"]
                )
            else:
                self.metrics["mcp_errors"].append(str(error))
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        metrics = self.metrics.copy()
        metrics["original_reliability"] = (
            self.metrics["original_success"] / self.metrics["original_calls"]
            if self.metrics["original_calls"] > 0 else 0.0
        )
        metrics["mcp_reliability"] = (
            self.metrics["mcp_success"] / self.metrics["mcp_calls"]
            if self.metrics["mcp_calls"] > 0 else 0.0
        )
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "original_calls": 0,
            "mcp_calls": 0,
            "original_success": 0,
            "mcp_success": 0,
            "original_performance": 0.0,
            "mcp_performance": 0.0,
            "original_errors": [],
            "mcp_errors": []
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary of metrics"""
        metrics = self.get_metrics()
        return (
            f"Monitoring started at: {self.start_time}\n"
            f"Original calls: {metrics['original_calls']}\n"
            f"Mcp calls: {metrics['mcp_calls']}\n"
            f"Original success rate: {metrics['original_reliability']:.2%}\n"
            f"Mcp success rate: {metrics['mcp_reliability']:.2%}\n"
            f"Original performance: {metrics['original_performance']:.3f}s\n"
            f"Mcp performance: {metrics['mcp_performance']:.3f}s\n"
            f"Original errors: {len(metrics['original_errors'])}\n"
            f"Mcp errors: {len(metrics['mcp_errors'])}"
        )

    def _get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_rss': process.memory_info().rss / 1024 / 1024,  # MB
            'threads': process.num_threads()
        }
        
    def track_parallel_call(self):
        """Track parallel execution"""
        self.metrics['calls']['parallel'] += 1
        
    def get_metrics_with_statistics(self) -> Dict[str, Any]:
        """Get current metrics with statistics"""
        metrics = self.get_metrics()
        
        # Calculate performance statistics
        metrics['performance_stats'] = {}
        for version in ['original', 'mcp']:
            times = getattr(self, f"{version}_performance")
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
            usages = getattr(self, f"{version}_errors")
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
    
    def get_summary_with_statistics(self) -> str:
        """Get human-readable summary of metrics with statistics"""
        metrics = self.get_metrics_with_statistics()
        summary = []
        
        summary.append(f"Monitoring started at: {self.start_time}")
        
        summary.append("\nCall Statistics:")
        for version in ['original', 'mcp', 'parallel']:
            summary.append(f"{version.title()} calls: {getattr(self, f'{version}_calls')}")
            
        summary.append("\nSuccess Rates:")
        for version in ['original', 'mcp']:
            rate = getattr(self, f"{version}_reliability")
            summary.append(f"{version.title()} success rate: {rate:.2%}")
            
        summary.append("\nError Counts:")
        for version in ['original', 'mcp']:
            summary.append(f"{version.title()} errors: {len(getattr(self, f'{version}_errors'))}")
            
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