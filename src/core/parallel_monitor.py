from typing import Dict, Any, List, Optional
from datetime import datetime
import psutil
import time
from .parallel_config import AgentVersion
import logging

logger = logging.getLogger(__name__)

class ParallelMonitor:
    """Monitor for tracking parallel execution metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "start_time": self.start_time,
            "calls": {
                "original": 0,
                "mcp": 0,
                "parallel": 0
            },
            "success": {
                "original": 0,
                "mcp": 0
            },
            "success_rate": {
                "original": 0.0,
                "mcp": 0.0
            },
            "performance": {
                "original": {"total": 0, "count": 0, "avg": 0, "max": 0},
                "mcp": {"total": 0, "count": 0, "avg": 0, "max": 0}
            },
            "performance_stats": {
                "original": [],
                "mcp": []
            },
            "resource_usage": {
                "original": [],
                "mcp": []
            },
            "errors": {
                "original": [],
                "mcp": []
            }
        }
    
    def _get_version_str(self, version: AgentVersion) -> str:
        """Convert AgentVersion to string format used in metrics"""
        return version.name.lower()
    
    def track_call(
        self,
        version: str,
        success: bool,
        error: Optional[str] = None,
        execution_time: Optional[float] = None
    ):
        """Track a call to either version of the agent"""
        logger.info(f"Tracking call for {version} version, success: {success}")
        self.metrics["calls"][version] += 1
        if success:
            self.metrics["success"][version] += 1
        if error:
            self.metrics["errors"][version].append(error)
        
        if execution_time is not None:
            self.metrics["performance"][version]["total"] += execution_time
            self.metrics["performance"][version]["count"] += 1
            self.metrics["performance"][version]["avg"] = (
                self.metrics["performance"][version]["total"] / 
                self.metrics["performance"][version]["count"]
            )
            self.metrics["performance"][version]["max"] = max(
                self.metrics["performance"][version]["max"],
                execution_time
            )
        
        # Update success rate
        total_calls = self.metrics["calls"][version]
        success_calls = self.metrics["success"][version]
        self.metrics["success_rate"][version] = success_calls / total_calls if total_calls > 0 else 0.0
    
    def track_parallel_call(self):
        """Track parallel execution"""
        self.metrics["calls"]["parallel"] += 1
    
    def _get_resource_usage(self, execution_time: float) -> Dict[str, Any]:
        """Get current resource usage"""
        process = psutil.Process()
        return {
            'usage': {
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_rss': process.memory_info().rss / 1024 / 1024,  # MB
                'threads': process.num_threads()
            },
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        metrics = self.metrics.copy()
        metrics["start_time"] = self.start_time
        metrics["last_reset"] = datetime.now()
        
        # Calculate performance statistics
        metrics["performance_stats"] = {}
        for version in ["original", "mcp"]:
            times = self.metrics["performance_stats"][version]
            if times:
                metrics["performance_stats"][version] = {
                    "min": min(times),
                    "max": max(times),
                    "avg": sum(times) / len(times),
                    "count": len(times),
                    "p95": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
                }
            else:
                metrics["performance_stats"][version] = {}
        
        # Calculate resource statistics
        metrics["resource_stats"] = {}
        for version in ["original", "mcp"]:
            usages = self.metrics["resource_usage"][version]
            if usages:
                metrics["resource_stats"][version] = {
                    "cpu": {
                        "avg": sum(u["usage"]["cpu_percent"] for u in usages) / len(usages),
                        "max": max(u["usage"]["cpu_percent"] for u in usages)
                    },
                    "memory": {
                        "avg": sum(u["usage"]["memory_percent"] for u in usages) / len(usages),
                        "max": max(u["usage"]["memory_percent"] for u in usages),
                        "rss_avg": sum(u["usage"]["memory_rss"] for u in usages) / len(usages),
                        "rss_max": max(u["usage"]["memory_rss"] for u in usages)
                    },
                    "threads": {
                        "avg": sum(u["usage"]["threads"] for u in usages) / len(usages),
                        "max": max(u["usage"]["threads"] for u in usages)
                    }
                }
            else:
                metrics["resource_stats"][version] = {}
        
        return metrics
    
    def reset_metrics(self) -> Dict[str, Any]:
        """Reset all metrics while preserving start time"""
        self.metrics = {
            "start_time": self.start_time,
            "calls": {
                "original": 0,
                "mcp": 0,
                "parallel": 0
            },
            "success": {
                "original": 0,
                "mcp": 0
            },
            "success_rate": {
                "original": 0.0,
                "mcp": 0.0
            },
            "performance": {
                "original": {"total": 0, "count": 0, "avg": 0, "max": 0},
                "mcp": {"total": 0, "count": 0, "avg": 0, "max": 0}
            },
            "performance_stats": {
                "original": [],
                "mcp": []
            },
            "resource_usage": {
                "original": [],
                "mcp": []
            },
            "errors": {
                "original": [],
                "mcp": []
            }
        }
        return {"start_time": self.start_time}
    
    def get_summary(self) -> str:
        """Get human-readable summary of metrics"""
        metrics = self.get_metrics()
        summary = []
        
        summary.append(f"Monitoring started at: {self.start_time}")
        summary.append(f"Last reset at: {self.start_time}")
        
        summary.append("\nCall Statistics:")
        for version in ["original", "mcp", "parallel"]:
            summary.append(f"{version.title()} calls: {metrics['calls'][version]}")
        
        summary.append("\nSuccess Rates:")
        for version in ["original", "mcp"]:
            summary.append(f"{version.title()} success rate: {metrics['success_rate'][version]:.2%}")
        
        summary.append("\nError Counts:")
        for version in ["original", "mcp"]:
            summary.append(f"{version.title()} errors: {len(metrics['errors'][version])}")
        
        summary.append("\nPerformance Statistics:")
        for version in ["original", "mcp"]:
            stats = metrics["performance_stats"][version]
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
        for version in ["original", "mcp"]:
            stats = metrics["resource_stats"][version]
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