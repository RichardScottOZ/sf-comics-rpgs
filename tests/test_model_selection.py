import pytest
import asyncio
import logging
from src.agents.comics_agent import ComicsAgent
from src.agents.sf_agent import ScienceFictionAgent
from src.agents.rpg_agent import RPGAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_model_selection():
    """Test that the correct model is being used for each agent type."""
    agents = {
        "comics": ComicsAgent(),
        "science_fiction": ScienceFictionAgent(),
        "rpg": RPGAgent()
    }
    
    test_content = "Test content for model verification"
    
    for agent_type, agent in agents.items():
        logger.info(f"Testing {agent_type} agent")
        
        # Test with default model
        result = await agent._get_analysis(
            content=test_content,
            system_prompt="Test system prompt"
        )
        assert "mistralai/mistral-7b" in str(result), f"{agent_type} agent not using Mistral by default"
        
        # Test with explicit model
        result = await agent._get_analysis(
            content=test_content,
            system_prompt="Test system prompt",
            model="mistralai/mistral-7b"
        )
        assert "mistralai/mistral-7b" in str(result), f"{agent_type} agent not respecting explicit model selection"
        
        logger.info(f"{agent_type} agent passed model selection tests")

async def test_model_parameters():
    """Test that model parameters are being properly applied."""
    agent = ComicsAgent()
    
    # Test with different temperatures
    for temp in [0.3, 0.7, 1.0]:
        result = await agent._get_analysis(
            content="Test content",
            system_prompt="Test prompt",
            temperature=temp
        )
        assert result is not None, f"Failed with temperature {temp}"
        logger.info(f"Successfully tested temperature {temp}")

async def test_error_handling():
    """Test error handling for invalid models."""
    agent = ComicsAgent()
    
    # Test with invalid model
    with pytest.raises(Exception):
        await agent._get_analysis(
            content="Test content",
            system_prompt="Test prompt",
            model="invalid-model"
        )
    logger.info("Successfully handled invalid model error")

if __name__ == "__main__":
    asyncio.run(test_model_selection())
    asyncio.run(test_model_parameters())
    asyncio.run(test_error_handling()) 