import asyncio
import logging
import json
from pathlib import Path
import aiohttp
from typing import Dict, Any
import os
import sys
import subprocess
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

    def check_server_process(self) -> bool:
        """Check if the API server process is running."""
        try:
            # Check if uvicorn process is running
            result = subprocess.run(
                ["ps", "aux" if sys.platform != "win32" else "tasklist"],
                capture_output=True,
                text=True
            )
            return "uvicorn" in result.stdout or "python" in result.stdout
        except Exception:
            return False

    def start_server(self) -> bool:
        """Attempt to start the API server."""
        logger.info("Attempting to start API server...")
        try:
            # Start the server in a new process
            server_process = subprocess.Popen(
                ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for the server to start
            time.sleep(5)
            
            # Check if the process is still running
            if server_process.poll() is None:
                logger.info("✓ API server started successfully")
                return True
            else:
                logger.error("✗ Failed to start API server")
                return False
        except Exception as e:
            logger.error(f"✗ Error starting API server: {str(e)}")
            return False

    async def check_server_availability(self) -> bool:
        """Check if the API server is available."""
        logger.info("\nChecking API server availability...")
        
        # First check if server process is running
        if not self.check_server_process():
            logger.warning("API server process not found")
            if not self.start_server():
                logger.error("""
✗ Could not start API server. Please ensure:
1. You have uvicorn installed: pip install uvicorn
2. The API server can be started with: uvicorn src.api.app:app --host 0.0.0.0 --port 8000
3. Port 8000 is available
""")
                return False

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                logger.info(f"Testing connection to {self.base_url}/info")
                async with session.get(f"{self.base_url}/info") as response:
                    if response.status == 200:
                        logger.info("✓ API server is available and responding")
                        return True
                    else:
                        logger.error(f"✗ API server returned status {response.status}")
                        return False
        except aiohttp.ClientError as e:
            logger.error(f"✗ Could not connect to API server: {str(e)}")
            logger.error("""
Please ensure:
1. The API server is running on http://localhost:8000
2. No firewall is blocking the connection
3. The server is properly configured
""")
            return False
        except asyncio.TimeoutError:
            logger.error("✗ Connection to API server timed out")
            logger.error("""
This could be because:
1. The server is not running
2. The server is not responding
3. There are network issues
""")
            return False

    async def verify_endpoint(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Verify that an endpoint uses the correct model."""
        logger.info(f"\nTesting endpoint: {endpoint}")
        logger.info(f"Request data: {json.dumps(data, indent=2)}")
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                logger.info("Sending POST request...")
                async with session.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"✗ Error in {endpoint}: {response.status}")
                        logger.error(f"Response: {error_text}")
                        return False

                    result = await response.json()
                    if "analysis" not in result or "model" not in result["analysis"]:
                        logger.error(f"✗ Missing model information in {endpoint} response")
                        logger.error(f"Response: {json.dumps(result, indent=2)}")
                        return False

                    used_model = result["analysis"]["model"]
                    if used_model != self.expected_model:
                        logger.error(f"✗ Wrong model used in {endpoint}: {used_model} (expected {self.expected_model})")
                        return False

                    logger.info(f"✓ Successfully verified {endpoint} using {used_model}")
                    return True

        except aiohttp.ClientError as e:
            logger.error(f"✗ Connection error in {endpoint}: {str(e)}")
            return False
        except asyncio.TimeoutError:
            logger.error(f"✗ Request to {endpoint} timed out")
            return False
        except Exception as e:
            logger.error(f"✗ Exception in {endpoint}: {str(e)}")
            return False

    async def verify_all_endpoints(self):
        """Verify all endpoints use the correct model."""
        # First check if server is available
        if not await self.check_server_availability():
            return False

        logger.info("\nStarting endpoint verification...")
        results = []
        for test_case in self.test_cases:
            logger.info(f"\n=== Testing {test_case['endpoint']} ===")
            success = await self.verify_endpoint(test_case["endpoint"], test_case["data"])
            results.append({
                "endpoint": test_case["endpoint"],
                "success": success
            })

        # Print summary using ASCII characters for Windows compatibility
        logger.info("\n=== Verification Summary ===")
        for result in results:
            status = "[PASS]" if result["success"] else "[FAIL]"
            logger.info(f"{status} {result['endpoint']}")

        return all(r["success"] for r in results)

    async def verify_model(self) -> bool:
        """Verify that the specified model is available."""
        logger.info(f"\nVerifying model: {self.expected_model}")
        
        if self.expected_model not in self.available_models:
            logger.error(f"✗ Model {self.expected_model} is not in the list of available models")
            logger.info("\nAvailable models:")
            for model in self.available_models:
                logger.info(f"- {model}")
            logger.info("\nPlease update your .env file with one of these models")
            return False
        
        logger.info("✓ Model is available")
        return True

    async def check_environment(self):
        """Check environment variables and configuration."""
        logger.info("\nChecking environment configuration...")
        env_file = Path(".env")
        if not env_file.exists():
            logger.error("✗ No .env file found. Please create one with the following content:")
            logger.error("OPENROUTER_DEFAULT_MODEL=mistralai/mistral-7b")
            logger.error("OPENROUTER_FORCE_MODEL=true")
            logger.error("OPENROUTER_API_KEY=your_api_key_here")
            return False

        with open(env_file, "r") as f:
            env_content = f.read()
            
        # Check for required variables
        required_vars = {
            "OPENROUTER_DEFAULT_MODEL": "mistralai/mistral-7b",
            "OPENROUTER_FORCE_MODEL": "true",
            "OPENROUTER_API_KEY": None  # Any value is acceptable
        }
        
        missing_vars = []
        for var, default_value in required_vars.items():
            if var not in env_content:
                missing_vars.append(var)
            elif default_value and f"{var}={default_value}" not in env_content:
                logger.warning(f"⚠ Variable {var} is set but not to the recommended value: {default_value}")
        
        if missing_vars:
            logger.error("✗ Missing required environment variables:")
            for var in missing_vars:
                logger.error(f"- {var}")
            logger.error("\nPlease add these variables to your .env file.")
            return False

        # Verify the model is available
        if not await self.verify_model():
            return False

        logger.info(f"✓ Environment configuration verified. Using model: {self.expected_model}")
        return True

async def main():
    logger.info("Starting model verification...")
    verifier = ModelVerifier()
    
    # Check environment first
    if not await verifier.check_environment():
        logger.error("Environment check failed. Please fix .env configuration.")
        return

    # Verify all endpoints
    success = await verifier.verify_all_endpoints()
    if success:
        logger.info("\n✓ All endpoints verified successfully!")
    else:
        logger.error("\n✗ Some endpoints failed verification. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main()) 