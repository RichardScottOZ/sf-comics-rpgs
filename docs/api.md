# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Comparative Analysis

#### Compare Works
```bash
POST /compare/works
```
Compare multiple works based on specified analysis type.

**Request Body:**
```json
{
    "works": [
        {
            "title": "Dune",
            "author": "Frank Herbert"
        },
        {
            "title": "Foundation",
            "author": "Isaac Asimov"
        }
    ],
    "analysis_type": "themes",
    "model": "google/gemma-7b-it",
    "force_refresh": true
}
```

**Parameters:**
- `works` (required): Array of works to compare, each containing at least `title` and `author`
- `analysis_type` (required): Type of analysis to perform (themes, world_building, characters, plot)
- `model` (optional): Model to use for analysis
- `force_refresh` (optional): Whether to bypass cache and force fresh analysis (default: false)

#### Compare World Building
```bash
POST /compare/world_building
```
Compare world-building elements across works.

**Request Body:**
```json
{
    "works": [
        {
            "title": "Dune",
            "author": "Frank Herbert"
        },
        {
            "title": "Foundation",
            "author": "Isaac Asimov"
        }
    ],
    "model": "google/gemma-7b-it",
    "force_refresh": true
}
```

#### Compare Themes
```bash
POST /compare/themes
```
Compare themes and motifs across works.

**Request Body:**
```json
{
    "works": [
        {
            "title": "Dune",
            "author": "Frank Herbert"
        },
        {
            "title": "Foundation",
            "author": "Isaac Asimov"
        }
    ],
    "model": "google/gemma-7b-it",
    "force_refresh": true
}
```

#### Compare Characters
```bash
POST /compare/characters
```
Compare character development and relationships across works.

**Request Body:**
```json
{
    "works": [
        {
            "title": "Dune",
            "author": "Frank Herbert"
        },
        {
            "title": "Foundation",
            "author": "Isaac Asimov"
        }
    ],
    "model": "google/gemma-7b-it",
    "force_refresh": true
}
```

#### Compare Plot
```bash
POST /compare/plot
```
Compare plot structure and narrative techniques across works.

**Request Body:**
```json
{
    "works": [
        {
            "title": "Dune",
            "author": "Frank Herbert"
        },
        {
            "title": "Foundation",
            "author": "Isaac Asimov"
        }
    ],
    "model": "google/gemma-7b-it",
    "force_refresh": true
}
```

**Example Response:**
```json
{
    "analysis": "Detailed comparative analysis...",
    "comparison_type": "themes",
    "works_compared": ["Dune", "Foundation"],
    "model_used": "google/gemma-7b-it",
    "timestamp": "2024-03-14T12:00:00Z"
}
```

### Science Fiction Analysis

#### Analyze Science Fiction Content
```bash
POST /analyze/sf
```
Analyze science fiction content.

**Request Body:**
```json
{
    "content": "The spice must flow...",
    "title": "Dune",
    "author": "Frank Herbert",
    "year": 1965,
    "model": "google/gemma-7b-it"
}
```

#### Get Science Fiction Recommendations
```bash
POST /recommend/sf
```
Get science fiction recommendations based on a work.

**Request Body:**
```json
{
    "based_on": "Dune",
    "limit": 5
}
```

### Comics Analysis

#### Analyze Comics Content
```bash
POST /analyze/comics
```
Analyze comics content.

**Request Body:**
```json
{
    "content": "With great power comes great responsibility...",
    "title": "Amazing Fantasy #15",
    "publisher": "Marvel Comics",
    "year": 1962,
    "creator": "Stan Lee",
    "model": "google/gemma-7b-it"
}
```

#### Get Comics Recommendations
```bash
POST /recommend/comics
```
Get comics recommendations based on a work.

**Request Body:**
```json
{
    "based_on": "Amazing Fantasy #15",
    "limit": 5
}
```

### RPG Analysis

#### Analyze RPG Content
```bash
POST /analyze/rpg
```
Analyze RPG content.

**Request Body:**
```json
{
    "content": "You are in a tavern...",
    "system": "Dungeons & Dragons",
    "source": "Player's Handbook",
    "edition": "5th Edition",
    "publisher": "Wizards of the Coast",
    "model": "google/gemma-7b-it"
}
```

#### Get RPG Recommendations
```bash
POST /recommend/rpg
```
Get RPG recommendations based on a work.

**Request Body:**
```json
{
    "based_on": "Dungeons & Dragons",
    "limit": 5
}
```

#### Analyze Character Sheet
```bash
POST /analyze/character
```
Analyze an RPG character sheet.

**Request Body:**
```json
{
    "character_sheet": "Name: Aragorn\nRace: Human\nClass: Ranger\nLevel: 5",
    "system": "Dungeons & Dragons"
}
```

## Usage Examples

### Curl Examples

#### Comparative Analysis

Basic comparison:
```bash
curl -X POST "http://localhost:8000/compare/works" \
     -H "Content-Type: application/json" \
     -d '{
         "works": [
             {"title": "Dune", "author": "Frank Herbert"},
             {"title": "Foundation", "author": "Isaac Asimov"}
         ],
         "analysis_type": "themes"
     }'
```

Force fresh analysis:
```bash
curl -X POST "http://localhost:8000/compare/works" \
     -H "Content-Type: application/json" \
     -d '{
         "works": [
             {"title": "Dune", "author": "Frank Herbert"},
             {"title": "Foundation", "author": "Isaac Asimov"}
         ],
         "analysis_type": "themes",
         "force_refresh": true
     }'
```

Specific comparison type:
```bash
curl -X POST "http://localhost:8000/compare/world_building" \
     -H "Content-Type: application/json" \
     -d '{
         "works": [
             {"title": "Dune", "author": "Frank Herbert"},
             {"title": "Foundation", "author": "Isaac Asimov"}
         ],
         "force_refresh": true
     }'
```

#### Science Fiction Analysis

Analyze content:
```bash
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
         "content": "The spice must flow...",
         "title": "Dune",
         "author": "Frank Herbert",
         "year": 1965
     }'
```

Get recommendations:
```bash
curl -X POST "http://localhost:8000/recommend/sf" \
     -H "Content-Type: application/json" \
     -d '{
         "based_on": "Dune",
         "limit": 5
     }'
```

#### Comics Analysis

Analyze content:
```bash
curl -X POST "http://localhost:8000/analyze/comics" \
     -H "Content-Type: application/json" \
     -d '{
         "content": "With great power comes great responsibility...",
         "title": "Amazing Fantasy #15",
         "publisher": "Marvel Comics",
         "year": 1962,
         "creator": "Stan Lee"
     }'
```

Get recommendations:
```bash
curl -X POST "http://localhost:8000/recommend/comics" \
     -H "Content-Type: application/json" \
     -d '{
         "based_on": "Amazing Fantasy #15",
         "limit": 5
     }'
```

#### RPG Analysis

Analyze content:
```bash
curl -X POST "http://localhost:8000/analyze/rpg" \
     -H "Content-Type: application/json" \
     -d '{
         "content": "You are in a tavern...",
         "system": "Dungeons & Dragons",
         "source": "Player's Handbook",
         "edition": "5th Edition",
         "publisher": "Wizards of the Coast"
     }'
```

Get recommendations:
```bash
curl -X POST "http://localhost:8000/recommend/rpg" \
     -H "Content-Type: application/json" \
     -d '{
         "based_on": "Dungeons & Dragons",
         "limit": 5
     }'
```

Analyze character sheet:
```bash
curl -X POST "http://localhost:8000/analyze/character" \
     -H "Content-Type: application/json" \
     -d '{
         "character_sheet": "Name: Aragorn\nRace: Human\nClass: Ranger\nLevel: 5",
         "system": "Dungeons & Dragons"
     }'
```

### Python Examples

#### Comparative Analysis

```python
import aiohttp
import asyncio

async def compare_works():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/compare/works",
            json={
                "works": [
                    {"title": "Dune", "author": "Frank Herbert"},
                    {"title": "Foundation", "author": "Isaac Asimov"}
                ],
                "analysis_type": "themes",
                "force_refresh": True
            }
        ) as response:
            return await response.json()

result = asyncio.run(compare_works())
print(result)
```

#### Science Fiction Analysis

```python
import aiohttp
import asyncio

async def analyze_sf():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/analyze/sf",
            json={
                "content": "The spice must flow...",
                "title": "Dune",
                "author": "Frank Herbert",
                "year": 1965
            }
        ) as response:
            return await response.json()

result = asyncio.run(analyze_sf())
print(result)
```

#### Comics Analysis

```python
import aiohttp
import asyncio

async def analyze_comics():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/analyze/comics",
            json={
                "content": "With great power comes great responsibility...",
                "title": "Amazing Fantasy #15",
                "publisher": "Marvel Comics",
                "year": 1962,
                "creator": "Stan Lee"
            }
        ) as response:
            return await response.json()

result = asyncio.run(analyze_comics())
print(result)
```

#### RPG Analysis

```python
import aiohttp
import asyncio

async def analyze_rpg():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/analyze/rpg",
            json={
                "content": "You are in a tavern...",
                "system": "Dungeons & Dragons",
                "source": "Player's Handbook",
                "edition": "5th Edition",
                "publisher": "Wizards of the Coast"
            }
        ) as response:
            return await response.json()

result = asyncio.run(analyze_rpg())
print(result)
```

## Notes

### General Notes
- All endpoints support caching
- Use `force_refresh: true` to bypass cache and get fresh analysis
- The `model` parameter is optional and will use the default model if not specified
- All endpoints return JSON responses
- Error responses include a `detail` field with error information

### Comparative Analysis Notes
- Each work in the `works` array must have at least a `title` and `author`
- The `analysis_type` parameter is only required for the general `/compare/works` endpoint
- Comparative analysis supports up to 5 works per request

### Science Fiction Notes
- The `content` field should contain the text to analyze
- The `year` field is optional but recommended for better analysis
- Recommendations are based on thematic and stylistic similarities

### Comics Notes
- The `content` field can include dialogue, narration, or plot summary
- The `creator` field can include multiple creators (comma-separated)
- Recommendations consider both content and visual style

### RPG Notes
- The `system` field is required for proper analysis
- Character sheet analysis supports multiple RPG systems
- Recommendations are tailored to the specified RPG system 