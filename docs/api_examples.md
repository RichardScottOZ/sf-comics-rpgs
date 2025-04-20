# SFMCP API Usage Examples

This document provides examples of how to use the SFMCP API endpoints using curl commands.

## Science Fiction Analysis

### Analyze Science Fiction Content
```bash
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your SF content here",
           "title": "Optional title",
           "author": "Optional author",
           "year": 2023
         }'
```

### Get Science Fiction Recommendations
```bash
curl -X POST "http://localhost:8000/recommend/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "based_on": "I enjoy hard SF with strong character development",
           "limit": 5
         }'
```

## Comics Analysis

### Analyze Comics Content
```bash
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your comic content here",
           "title": "Optional title",
           "publisher": "Optional publisher",
           "creator": "Optional creator",
           "year": 2023
         }'
```

### Get Comics Recommendations
```bash
curl -X POST "http://localhost:8000/recommend/comics" \
     -H "Content-Type: application/json" \
     -d '{
           "based_on": "I enjoy character-driven stories with unique art styles",
           "limit": 5
         }'
```

## RPG Analysis

### Analyze RPG Content
```bash
curl -X POST "http://localhost:8000/analyze/rpg" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your RPG content here",
           "system": "D&D 5e",
           "source": "Optional source",
           "edition": "Optional edition",
           "publisher": "Optional publisher"
         }'
```

### Get RPG Recommendations
```bash
curl -X POST "http://localhost:8000/recommend/rpg" \
     -H "Content-Type: application/json" \
     -d '{
           "based_on": "I enjoy narrative-focused systems with simple mechanics",
           "limit": 5
         }'
```

### Analyze RPG Character
```bash
curl -X POST "http://localhost:8000/analyze/character" \
     -H "Content-Type: application/json" \
     -d '{
           "character_sheet": "Your character sheet here",
           "system": "D&D 5e"
         }'
```

## API Information

### Get API Info
```bash
curl "http://localhost:8000/info"
```

## Notes

1. Replace `localhost:8000` with your actual server address if different
2. All endpoints return JSON responses
3. The `limit` parameter in recommendation endpoints is optional (defaults to 5)
4. Most fields in the request bodies are optional except where noted
5. The API documentation is available at `http://localhost:8000/docs`

## Response Format

All analysis endpoints return responses in the following format:
```json
{
    "type": "agent_type",
    "timestamp": "ISO timestamp",
    "analysis": {
        // Analysis content from the model
    },
    // Additional metadata based on the request
}
```

Recommendation endpoints return similar responses with recommended items in the analysis field. 