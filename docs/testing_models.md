# Free Models for Testing

This document lists free models available through OpenRouter that are suitable for testing the SFMCP system.

## Available Free Models

### Open Source Models
1. `google/gemma-7b-it`
   - Free tier available
   - Good for general testing
   - Decent performance for basic analysis

2. `mistralai/mistral-7b`
   - Free tier available
   - Good for text analysis
   - Reliable for basic tasks
   - Particularly good for comics analysis
   - Free tier includes generous rate limits
   - Model ID: `mistralai/mistral-7b`

3. `meta-llama/llama-2-70b`
   - Free tier available
   - Good for complex analysis
   - One of the better free options

4. `google/palm-2`
   - Free tier available
   - Good for creative tasks
   - Decent for recommendations

## Testing Configuration

### Environment Setup
Add to your `.env` file:
```env
OPENROUTER_DEFAULT_MODEL=mistralai/mistral-7b
OPENROUTER_TESTING_MODE=true
OPENROUTER_FORCE_MODEL=true  # This prevents falling back to GPT-4
```

### Testing Agent Configuration
```python
class TestingAgent(BaseAgent):
    def __init__(self):
        super().__init__("testing", default_model="mistralai/mistral-7b")
        self.testing_mode = True
        self.force_model = True  # Prevent model fallback

    async def _get_analysis(
        self,
        content: str,
        system_prompt: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Force use of Mistral for testing
        model = "mistralai/mistral-7b"
        return await super()._get_analysis(
            content=content,
            system_prompt=system_prompt,
            model=model,
            temperature=0.7,
            max_tokens=1000
        )
```

### OpenRouter Client Configuration
```python
class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.default_model = os.getenv("OPENROUTER_DEFAULT_MODEL", "mistralai/mistral-7b")
        self.force_model = os.getenv("OPENROUTER_FORCE_MODEL", "true").lower() == "true"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Force model if configured
        if self.force_model:
            model = self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/your-repo",  # Required for free tier
            "X-Title": "SFMCP Testing"  # Required for free tier
        }

        response = await self._make_request(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                **kwargs
            }
        )
        return response
```

## Testing Endpoints

### Example Test Request
```bash
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Test content for analysis",
           "model": "google/gemma-7b-it"
         }'
```

## Testing Considerations

1. Response Quality:
   - Free models may provide less detailed analysis
   - Responses might be shorter
   - Some complex tasks may not work as well

2. Rate Limits:
   - Free models have lower rate limits
   - Implement proper error handling
   - Consider adding delays between requests

3. Token Limits:
   - Free models often have lower token limits
   - Keep test content concise
   - Monitor token usage

## Testing Workflow

1. Start with basic analysis:
```bash
# Test basic content analysis
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "A short test passage",
           "model": "google/gemma-7b-it"
         }'
```

2. Test error handling:
```bash
# Test with invalid content
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "",
           "model": "google/gemma-7b-it"
         }'
```

3. Test rate limiting:
```bash
# Test multiple rapid requests
for i in {1..5}; do
  curl -X POST "http://localhost:8000/analyze/sf" \
       -H "Content-Type: application/json" \
       -d '{
             "content": "Test content $i",
             "model": "google/gemma-7b-it"
           }'
  sleep 1
done
```

## Comics-Specific Testing Examples

### Testing Current Comics Knowledge
```bash
# Test comics analysis with Mistral
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "What are the current DC Comics Superman series? Please analyze the current state of Superman comics, including main titles, creative teams, and recent storylines.",
           "model": "mistralai/mistral-7b",
           "title": "Superman Series Analysis",
           "publisher": "DC Comics"
         }'
```

### Testing Comics Recommendations
```bash
# Test comics recommendations with Mistral
curl -X POST "http://localhost:8000/recommend/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "preferences": {
             "genres": ["superhero", "science fiction"],
             "publishers": ["DC Comics"],
             "characters": ["Superman"]
           },
           "model": "mistralai/mistral-7b",
           "limit": 5
         }'
```

### Testing Comics Analysis Parameters
```bash
# Test with specific analysis parameters
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Analyze the current state of Superman comics, focusing on: 1. Main ongoing series 2. Creative teams 3. Recent storylines 4. Character development 5. Sales and reception",
           "model": "mistralai/mistral-7b",
           "title": "Superman Comics Analysis",
           "publisher": "DC Comics",
           "parameters": {
             "temperature": 0.3,
             "max_tokens": 1500,
             "top_p": 0.9
           }
         }'
```

### Testing Comics Error Cases
```bash
# Test with invalid publisher
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Analyze current Superman series",
           "model": "mistralai/mistral-7b",
           "publisher": "Invalid Publisher"
         }'

# Test with empty content
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "",
           "model": "mistralai/mistral-7b",
           "publisher": "DC Comics"
         }'
```

### Testing Comics Rate Limits
```bash
# Test multiple comics analysis requests
for i in {1..3}; do
  curl -X POST "http://localhost:8000/analyze/comics" \
       -H "Content-Type: application/json" \
       -d '{
             "content": "Analyze current Superman series $i",
             "model": "mistralai/mistral-7b",
             "publisher": "DC Comics"
           }'
  sleep 2  # Add delay to respect rate limits
done
```

## Monitoring Free Usage

1. Check OpenRouter Dashboard:
   - Monitor free tier usage
   - Track rate limits
   - View error rates

2. Implement Logging:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestingAgent(BaseAgent):
    async def _get_analysis(self, content: str, system_prompt: str, model: str):
        try:
            result = await super()._get_analysis(content, system_prompt, model)
            logger.info(f"Successful analysis using {model}")
            return result
        except Exception as e:
            logger.error(f"Error in analysis using {model}: {str(e)}")
            raise
```

## Best Practices for Testing

1. Start Simple:
   - Use short test content
   - Test basic functionality first
   - Gradually increase complexity

2. Implement Retries:
   - Handle rate limits gracefully
   - Add exponential backoff
   - Log retry attempts

3. Monitor Performance:
   - Track response times
   - Monitor error rates
   - Log token usage

4. Test Edge Cases:
   - Empty content
   - Very long content
   - Special characters
   - Rate limiting scenarios

## Moving to Production

When ready to move to production:

1. Update model configuration:
```env
OPENROUTER_DEFAULT_MODEL=openai/gpt-4
OPENROUTER_TESTING_MODE=false
```

2. Remove testing-specific code
3. Implement proper error handling
4. Set up monitoring and logging
5. Configure proper rate limiting 