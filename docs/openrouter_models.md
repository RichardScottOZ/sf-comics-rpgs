# OpenRouter Model Configuration Guide

This document provides information about configuring and using different models through OpenRouter in the SFMCP system.

## Available Models

OpenRouter provides access to various models from different providers. Here are some recommended models for different use cases:

### General Purpose Models
- `openai/gpt-4` - Most capable model, best for complex analysis
- `openai/gpt-3.5-turbo` - Good balance of capability and cost
- `anthropic/claude-2` - Strong at analysis and reasoning
- `anthropic/claude-instant` - Faster, more cost-effective alternative

### Specialized Models
- `google/palm-2` - Good for creative tasks
- `meta-llama/llama-2-70b` - Open source model, good for general tasks
- `mistralai/mistral-7b` - Efficient open source model

## Model Configuration

Models can be configured in several ways:

1. Global Configuration (in `.env`):
```env
OPENROUTER_DEFAULT_MODEL=openai/gpt-4
```

2. Per-Agent Configuration (in agent classes):
```python
async def analyze_content(self, content: str, model: str = "openai/gpt-4"):
    return await self._get_analysis(
        content=content,
        system_prompt=self.system_prompt,
        model=model
    )
```

3. Per-Request Configuration (in API calls):
```bash
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your content here",
           "model": "anthropic/claude-2"
         }'
```

## Model Selection Guidelines

### For Analysis Tasks
- Use `openai/gpt-4` or `anthropic/claude-2` for:
  - Complex content analysis
  - Detailed character analysis
  - In-depth world-building analysis
  - Technical system analysis

- Use `openai/gpt-3.5-turbo` or `anthropic/claude-instant` for:
  - Quick content summaries
  - Basic analysis
  - High-volume tasks
  - Cost-sensitive operations

### For Recommendations
- Use `openai/gpt-4` or `anthropic/claude-2` for:
  - Personalized recommendations
  - Complex preference matching
  - Detailed comparison analysis

- Use `openai/gpt-3.5-turbo` for:
  - General recommendations
  - High-volume recommendation tasks

## Model Parameters

Each model can be fine-tuned using these parameters:

```python
{
    "temperature": 0.7,  # Controls randomness (0.0 to 1.0)
    "max_tokens": 2000,  # Maximum response length
    "top_p": 0.9,        # Nucleus sampling parameter
    "frequency_penalty": 0.0,  # Reduces repetition
    "presence_penalty": 0.0    # Encourages diversity
}
```

### Recommended Parameters

#### For Analysis:
```python
{
    "temperature": 0.3,  # Lower for more focused analysis
    "max_tokens": 2000,
    "top_p": 0.9,
    "frequency_penalty": 0.2,
    "presence_penalty": 0.1
}
```

#### For Recommendations:
```python
{
    "temperature": 0.7,  # Higher for more diverse recommendations
    "max_tokens": 1000,
    "top_p": 0.95,
    "frequency_penalty": 0.3,
    "presence_penalty": 0.2
}
```

## Cost Considerations

Different models have different pricing structures. Here's a rough guide:

1. Most Expensive (but most capable):
   - `openai/gpt-4`
   - `anthropic/claude-2`

2. Mid-range:
   - `openai/gpt-3.5-turbo`
   - `anthropic/claude-instant`

3. Most Cost-effective:
   - `google/palm-2`
   - `meta-llama/llama-2-70b`
   - `mistralai/mistral-7b`

## Implementation Example

Here's how to implement model selection in your code:

```python
from typing import Optional

class BaseAgent:
    def __init__(self, agent_type: str, default_model: str = "openai/gpt-4"):
        self.agent_type = agent_type
        self.default_model = default_model
        self.client = OpenRouterClient()

    async def _get_analysis(
        self,
        content: str,
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        model = model or self.default_model
        
        # Adjust parameters based on model
        if "gpt-4" in model:
            temperature = 0.3
            max_tokens = max_tokens or 2000
        elif "claude-2" in model:
            temperature = 0.4
            max_tokens = max_tokens or 2000
        else:
            temperature = 0.7
            max_tokens = max_tokens or 1000

        return await self.client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
```

## Best Practices

1. Start with `gpt-3.5-turbo` for development and testing
2. Use `gpt-4` for production analysis tasks
3. Implement caching to reduce API calls
4. Monitor usage and costs regularly
5. Have fallback models for high-volume operations
6. Adjust parameters based on the specific task
7. Consider implementing model rotation for load balancing

## Troubleshooting

Common issues and solutions:

1. Rate Limiting:
   - Implement exponential backoff
   - Use multiple API keys
   - Implement request queuing

2. Model Unavailability:
   - Have fallback models configured
   - Implement retry logic
   - Cache previous responses

3. Cost Management:
   - Set usage limits
   - Monitor token usage
   - Implement cost-effective model selection 