import asyncio
import logging
import json
from pathlib import Path
import aiohttp
from typing import Dict, Any
import os
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_verification.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize rich console
console = Console()

class ModelVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.console = Console()
        self.session = None
        # Get model from environment or use default
        self.expected_model = os.getenv("OPENROUTER_DEFAULT_MODEL", "mistralai/mistral-7b")
        self.timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
        self.available_models = [
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-2",
            "anthropic/claude-instant",
            "google/palm-2",
            "meta-llama/llama-2-70b",
            "mistralai/mistral-7b",
            "google/gemma-7b-it"
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_api_availability(self) -> bool:
        """Check if the API is available and responding."""
        try:
            async with self.session.get(f"{self.base_url}/info") as response:
                return response.status == 200
        except aiohttp.ClientError:
            return False

    async def verify_model(self, model: str) -> bool:
        """Verify if a specific model is available and working."""
        try:
            # Test with a simple analysis request
            test_content = "Test content for model verification"
            async with self.session.post(
                f"{self.base_url}/analyze/sf",
                json={"content": test_content, "model": model}
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error verifying model {model}: {str(e)}")
            return False

    async def run_verification(self):
        """Run the complete verification process."""
        self.console.print("\n[bold]Starting model verification...[/bold]")
        
        # Check environment
        self.console.print("\n[bold]Checking environment configuration...[/bold]")
        model = os.getenv("OPENROUTER_DEFAULT_MODEL", "mistralai/mistral-7b")
        self.console.print(f"Verifying model: {model}")
        
        if await self.verify_model(model):
            self.console.print("[green]✓ Model is available[/green]")
            self.console.print(f"[green]✓ Environment configuration verified. Using model: {model}[/green]")
        else:
            self.console.print("[red]✗ Model verification failed[/red]")
            return False

        # Check API server
        self.console.print("\n[bold]Checking API server availability...[/bold]")
        
        if await self.check_api_availability():
            self.console.print("[green]✓ API server is responding[/green]")
        else:
            self.console.print("[red]✗ API server is not responding[/red]")
            self.console.print("[yellow]Please ensure the API server is running with:[/yellow]")
            self.console.print("[yellow]uvicorn src.api.app:app --host 0.0.0.0 --port 8000[/yellow]")
            return False

        return True

async def main():
    async with ModelVerifier() as verifier:
        success = await verifier.run_verification()
        
        if success:
            console.print("\n[green]✓ All verifications passed successfully![/green]")
        else:
            console.print("\n[red]✗ Some endpoints failed verification. Check the logs for details.[/red]")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 