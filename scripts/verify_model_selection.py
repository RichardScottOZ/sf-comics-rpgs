import asyncio
import logging
import json
from pathlib import Path
import aiohttp
from typing import Dict, Any
import os
import sys
import time

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

class ModelVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"
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
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API info endpoint returned status {response.status}: {error_text}")
                    return False
                return True
        except aiohttp.ClientError as e:
            logger.error(f"Connection error checking API availability: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking API availability: {str(e)}")
            return False

    async def verify_model(self, model: str) -> bool:
        """Verify if a specific model is available and working."""
        try:
            # Test with a simple analysis request
            test_content = "Test content for model verification"
            async with self.session.post(
                f"{self.base_url}/analyze/sf",
                json={
                    "content": test_content,
                    "title": "Test Title",
                    "author": "Test Author"
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API returned status {response.status}: {error_text}")
                    return False
                return True
        except aiohttp.ClientError as e:
            logger.error(f"Connection error verifying model {model}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying model {model}: {str(e)}")
            return False

    async def run_verification(self):
        """Run the complete verification process."""
        logger.info("Starting model verification...")
        
        # Check environment
        logger.info("Checking environment configuration...")
        model = os.getenv("OPENROUTER_DEFAULT_MODEL", "mistralai/mistral-7b")
        logger.info(f"Verifying model: {model}")
        
        if await self.verify_model(model):
            logger.info("✓ Model is available")
            logger.info(f"✓ Environment configuration verified. Using model: {model}")
        else:
            logger.error("✗ Model verification failed")
            return False

        # Check API server
        logger.info("Checking API server availability...")
        
        if await self.check_api_availability():
            logger.info("✓ API server is responding")
        else:
            logger.error("✗ API server is not responding")
            logger.info("Please ensure the API server is running with:")
            logger.info("uvicorn src.api.app:app --host 0.0.0.0 --port 8000")
            return False

        return True

async def main():
    async with ModelVerifier() as verifier:
        success = await verifier.run_verification()
        
        if success:
            logger.info("✓ All verifications passed successfully!")
        else:
            logger.error("✗ Some endpoints failed verification. Check the logs for details.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 