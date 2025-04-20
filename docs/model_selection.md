# Model Selection Guide

This document explains how to select and verify models in the SFMCP system.

## Available Models

### Free Models (Recommended for Testing)
- `mistralai/mistral-small-3.1-24b-instruct:free` (Default)
- `google/gemma-7b-it`
- `meta-llama/llama-2-70b`
- `google/palm-2`

### Paid Models (For Production)
- `openai/gpt-4`
- `anthropic/claude-2`
- `openai/gpt-3.5-turbo`

## Selecting Models

### 1. Environment Variables
Add to your `.env` file:
```env
OPENROUTER_DEFAULT_MODEL=mistralai/mistral-small-3.1-24b-instruct:free
OPENROUTER_FORCE_MODEL=true
```

### 2. Per-Request Model Selection
You can specify the model in your API requests:

```bash
# Comics Analysis with Mistral
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your content here",
           "model": "mistralai/mistral-small-3.1-24b-instruct:free",
           "parameters": {
             "temperature": 0.7,
             "max_tokens": 1000
           }
         }'

# Science Fiction Analysis with Gemma
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your content here",
           "model": "google/gemma-7b-it"
         }'

# RPG Analysis with Llama
curl -X POST "http://localhost:8000/analyze/rpg" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your content here",
           "model": "meta-llama/llama-2-70b"
         }'
```

## Verifying Model Usage

### 1. Check Logs
The system logs model usage. Look for messages like:
```
INFO: Making API request with model: mistralai/mistral-small-3.1-24b-instruct:free
INFO: Successfully received response from mistralai/mistral-small-3.1-24b-instruct:free
```

### 2. Response Verification
Check the response for model information:
```json
{
    "analysis": {
        "model": "mistralai/mistral-small-3.1-24b-instruct:free",
        "provider": "Mistral",
        ...
    }
}
```

### 3. Run Tests
Execute the model selection tests:
```bash
python -m pytest tests/test_model_selection.py -v
```

## Model Parameters

### Recommended Parameters for Free Models
```json
{
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

### Parameter Examples
```bash
# High creativity (higher temperature)
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your content here",
           "model": "mistralai/mistral-small-3.1-24b-instruct:free",
           "parameters": {
             "temperature": 0.9,
             "max_tokens": 1500
           }
         }'

# More focused (lower temperature)
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your content here",
           "model": "mistralai/mistral-small-3.1-24b-instruct:free",
           "parameters": {
             "temperature": 0.3,
             "max_tokens": 800
           }
         }'
```

## Troubleshooting

### Common Issues

1. Model Not Responding:
   - Check rate limits
   - Verify model availability
   - Try a different model

2. Unexpected Model Usage:
   - Verify OPENROUTER_FORCE_MODEL setting
   - Check request parameters
   - Review logs for model selection

3. Poor Results:
   - Adjust temperature
   - Modify max_tokens
   - Try different model

### Testing Model Selection

1. Run the test suite:
```bash
python -m pytest tests/test_model_selection.py -v
```

2. Check logs for model usage:
```bash
tail -f logs/sfmcp.log | grep "Making API request"
```

3. Verify response model:
```bash
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Test content",
           "model": "mistralai/mistral-small-3.1-24b-instruct:free"
         }' | jq '.analysis.model'
``` 