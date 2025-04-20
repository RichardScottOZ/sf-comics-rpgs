import asyncio
import logging
from datetime import datetime
import json
from pathlib import Path
import aiohttp
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelMonitor:
    def __init__(self):
        self.console = Console()
        self.stats = {
            "mistralai/mistral-small-3.1-24b-instruct:free": {"requests": 0, "errors": 0, "avg_time": 0},
            "google/gemma-7b-it": {"requests": 0, "errors": 0, "avg_time": 0},
            "meta-llama/llama-2-70b": {"requests": 0, "errors": 0, "avg_time": 0},
            "google/palm-2": {"requests": 0, "errors": 0, "avg_time": 0}
        }
        self.log_file = Path("logs/sfmcp.log")

    def update_stats(self, model: str, success: bool, response_time: float):
        if model in self.stats:
            self.stats[model]["requests"] += 1
            if not success:
                self.stats[model]["errors"] += 1
            # Update average response time
            current_avg = self.stats[model]["avg_time"]
            total_requests = self.stats[model]["requests"]
            self.stats[model]["avg_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests

    def create_stats_table(self) -> Table:
        table = Table(title="Model Usage Statistics")
        table.add_column("Model", style="cyan")
        table.add_column("Requests", justify="right", style="green")
        table.add_column("Errors", justify="right", style="red")
        table.add_column("Avg Time (ms)", justify="right", style="yellow")
        table.add_column("Success Rate", justify="right", style="blue")

        for model, stats in self.stats.items():
            success_rate = ((stats["requests"] - stats["errors"]) / stats["requests"] * 100) if stats["requests"] > 0 else 0
            table.add_row(
                model,
                str(stats["requests"]),
                str(stats["errors"]),
                f"{stats['avg_time']:.2f}",
                f"{success_rate:.1f}%"
            )
        return table

    async def monitor_logs(self):
        """Monitor the log file for model usage."""
        last_position = 0
        while True:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()

                    for line in new_lines:
                        if "Making API request with model:" in line:
                            model = line.split("model:")[1].strip()
                            start_time = datetime.now()
                            # Simulate response time (in a real scenario, you'd track actual response times)
                            response_time = 0.5
                            self.update_stats(model, True, response_time)
                        elif "Error in API request to" in line:
                            model = line.split("to")[1].split(":")[0].strip()
                            self.update_stats(model, False, 0)

            await asyncio.sleep(1)

    async def display_dashboard(self):
        """Display a live-updating dashboard of model statistics."""
        with Live(refresh_per_second=1) as live:
            while True:
                table = self.create_stats_table()
                live.update(Panel(table, title="Model Monitoring Dashboard"))
                await asyncio.sleep(1)

async def main():
    monitor = ModelMonitor()
    await asyncio.gather(
        monitor.monitor_logs(),
        monitor.display_dashboard()
    )

if __name__ == "__main__":
    asyncio.run(main()) 