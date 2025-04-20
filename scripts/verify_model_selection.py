import asyncio
import logging
import json
from pathlib import Path
import aiohttp
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_verification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.expected_model = "mistralai/mistral-7b"
        self.test_cases = [
            {
                "endpoint": "/analyze/comics",
                "data": {
                    "content": "Test Superman comic analysis",
                    "title": "Superman #1",
                    "publisher": "DC Comics"
                }
            },
            {
                "endpoint": "/analyze/sf",
                "data": {
                    "content": "Test science fiction analysis",
                    "title": "Test Novel",
                    "author": "Test Author"
                }
            },
            {
                "endpoint": "/analyze/rpg",
                "data": {
                    "content": "Test RPG content analysis",
                    "system": "D&D 5e",
                    "source": "Player's Handbook"
                }
            }
        ]

    async def verify_endpoint(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Verify that an endpoint uses the correct model."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        logger.error(f"Error in {endpoint}: {response.status}")
                        return False

                    result = await response.json()
                    if "analysis" not in result or "model" not in result["analysis"]:
                        logger.error(f"Missing model information in {endpoint} response")
                        return False

                    used_model = result["analysis"]["model"]
                    if used_model != self.expected_model:
                        logger.error(f"Wrong model used in {endpoint}: {used_model} (expected {self.expected_model})")
                        return False

                    logger.info(f"Successfully verified {endpoint} using {used_model}")
                    return True

        except Exception as e:
            logger.error(f"Exception in {endpoint}: {str(e)}")
            return False

    async def verify_all_endpoints(self):
        """Verify all endpoints use the correct model."""
        results = []
        for test_case in self.test_cases:
            success = await self.verify_endpoint(test_case["endpoint"], test_case["data"])
            results.append({
                "endpoint": test_case["endpoint"],
                "success": success
            })

        # Print summary
        logger.info("\nVerification Summary:")
        for result in results:
            status = "✓" if result["success"] else "✗"
            logger.info(f"{status} {result['endpoint']}")

        return all(r["success"] for r in results)

    async def check_environment(self):
        """Check environment variables and configuration."""
        env_file = Path(".env")
        if not env_file.exists():
            logger.error("No .env file found")
            return False

        with open(env_file, "r") as f:
            env_content = f.read()
            if "OPENROUTER_DEFAULT_MODEL=mistralai/mistral-7b" not in env_content:
                logger.error("Default model not set correctly in .env")
                return False
            if "OPENROUTER_FORCE_MODEL=true" not in env_content:
                logger.error("Force model not set correctly in .env")
                return False

        logger.info("Environment configuration verified")
        return True

async def main():
    verifier = ModelVerifier()
    
    # Check environment first
    if not await verifier.check_environment():
        logger.error("Environment check failed. Please fix .env configuration.")
        return

    # Verify all endpoints
    success = await verifier.verify_all_endpoints()
    if success:
        logger.info("All endpoints verified successfully!")
    else:
        logger.error("Some endpoints failed verification. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main()) 