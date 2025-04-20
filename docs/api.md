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

## Visualization Endpoints

### Generate Visualization
```bash
POST /visualize
```
Generate a visualization from analysis data.

**Request Body:**
```json
{
    "data": {
        // Analysis data (varies by visualization type)
    },
    "visualization_type": "network|temporal|comparative",
    "format": "png",
    "enhanced": false,
    "save_to_disk": false
}
```

**Parameters:**
- `data` (required): Analysis data to visualize
- `visualization_type` (required): Type of visualization to generate
  - `network`: Character network visualization
  - `temporal`: Temporal analysis visualization
  - `comparative`: Comparative analysis visualization
- `format` (optional): Output format (default: "png")
- `enhanced` (optional): Enable enhanced visualization features (default: false)
- `save_to_disk` (optional): Save visualization to disk (default: false)

**Response:**
```json
{
    "image": "base64-encoded-image-data",
    "format": "png",
    "metadata": {
        "type": "network|temporal|comparative",
        // Additional metadata based on visualization type
    }
}
```

**Notes:**
- When `save_to_disk` is true, visualizations are saved to the `visualizations` directory
- Saved files are named with pattern: `{visualization_type}_{timestamp}.{format}`
- Example: `network_20240314_123456.png`
- The base64-encoded image is always returned in the response
- Saved files can be accessed directly from the filesystem

**Example Usage:**
```bash
# Generate and save a network visualization
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "nodes": [
        {"id": "Paul", "connections": 5, "role": "protagonist", "work": "Dune", "community": 1},
        {"id": "Jessica", "connections": 4, "role": "mentor", "work": "Dune", "community": 1}
      ],
      "edges": [
        {"source": "Paul", "target": "Jessica"}
      ],
      "communities": [
        {"id": 1, "size": 2, "density": 0.5, "characters": ["Paul", "Jessica"]}
      ]
    },
    "visualization_type": "network",
    "format": "png",
    "enhanced": true,
    "save_to_disk": true
  }'
```

### Get Visualization Types
```bash
GET /visualization/types
```
Get available visualization types and their capabilities.

**Response:**
```json
{
    "types": [
        {
            "name": "network",
            "description": "Character network visualization",
            "supports_enhanced": true
        },
        {
            "name": "temporal",
            "description": "Temporal analysis visualization",
            "supports_enhanced": true
        },
        {
            "name": "comparative",
            "description": "Comparative analysis visualization",
            "supports_enhanced": true
        }
    ]
}
```

## Monitoring Endpoints

### Interest Profile Management

#### Create Interest Profile
```bash
POST /monitoring/profile
```
Create a new interest profile for monitoring.

**Request Body:**
```json
{
    "name": "Science Fiction Classics",
    "sources": ["isfdb", "goodreads", "wikipedia"],
    "keywords": ["science fiction", "cyberpunk"],
    "authors": ["William Gibson", "Neal Stephenson"],
    "notification_preferences": {
        "frequency": "daily",
        "channels": ["email", "api"]
    }
}
```

**Response:**
```json
{
    "profile_id": 1,
    "name": "Science Fiction Classics",
    "sources": ["isfdb", "goodreads", "wikipedia"],
    "keywords": ["science fiction", "cyberpunk"],
    "authors": ["William Gibson", "Neal Stephenson"],
    "notification_preferences": {
        "frequency": "daily",
        "channels": ["email", "api"]
    },
    "created_at": "2024-03-14T12:00:00Z",
    "last_checked": "2024-03-14T12:00:00Z"
}
```

#### Get Profile Updates
```bash
GET /monitoring/profile/{profile_id}
```
Get updates for a specific interest profile.

**Response:**
```json
{
    "profile_id": 1,
    "profile_name": "Science Fiction Classics",
    "last_checked": "2024-03-14T12:00:00Z",
    "new_items_count": 5,
    "new_items": [
        {
            "title": "Neuromancer",
            "author": "William Gibson",
            "source": "isfdb",
            "url": "https://www.isfdb.org/cgi-bin/pl.cgi?123456"
        }
    ],
    "notification_preferences": {
        "frequency": "daily",
        "channels": ["email", "api"]
    }
}
```

#### List Profiles
```bash
GET /monitoring/profiles
```
List all interest profiles.

**Response:**
```json
{
    "profiles": [
        {
            "profile_id": 1,
            "name": "Science Fiction Classics",
            "last_checked": "2024-03-14T12:00:00Z",
            "sources": ["isfdb", "goodreads", "wikipedia"]
        }
    ]
}
```

#### Delete Profile
```bash
DELETE /monitoring/profile/{profile_id}
```
Delete an interest profile.

**Response:**
```json
{
    "status": "success",
    "message": "Profile 1 deleted"
}
```

### Notification Configuration

#### Email Configuration
```bash
POST /monitoring/email/config
```
Configure email notifications for monitoring alerts.

**Request Body:**
```json
{
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "username": "your-email@example.com",
    "password": "your-password",
    "from_email": "notifications@example.com"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Email configuration updated"
}
```

#### Webhook Management

**Add Webhook:**
```bash
POST /monitoring/webhook/{webhook_id}
```

**Request Body:**
```json
{
    "url": "https://your-webhook-url.com",
    "secret": "optional-secret-key",
    "events": ["new_content", "rating_update"],
    "headers": {
        "Authorization": "Bearer your-token"
    }
}
```

**Delete Webhook:**
```bash
DELETE /monitoring/webhook/{webhook_id}
```

**Response:**
```json
{
    "status": "success",
    "message": "Webhook {webhook_id} deleted"
}
```

### Monitoring Statistics
```bash
GET /monitoring/statistics
```
Get statistics about the monitoring system.

**Response:**
```json
{
    "total_profiles": 10,
    "active_profiles": 8,
    "total_notifications": 100,
    "webhook_count": 2,
    "last_check_time": "2024-03-14T12:00:00Z",
    "source_stats": {
        "isfdb": 40,
        "goodreads": 35,
        "wikipedia": 25
    }
}
```

### Cleanup Notifications
```bash
POST /monitoring/cleanup
```
Clean up old notifications from the system.

**Query Parameters:**
- `days` (optional): Number of days to keep notifications (default: 30)

**Response:**
```json
{
    "status": "success",
    "message": "Cleaned up notifications older than 30 days"
}
```

### Usage Examples

#### Create Interest Profile
```bash
curl -X POST "http://localhost:8000/monitoring/profile" \
     -H "Content-Type: application/json" \
     -d '{
         "name": "Science Fiction Classics",
         "sources": ["isfdb", "goodreads", "wikipedia"],
         "keywords": ["science fiction", "cyberpunk"],
         "authors": ["William Gibson", "Neal Stephenson"],
         "notification_preferences": {
             "frequency": "daily",
             "channels": ["email", "api"]
         }
     }'
```

#### Configure Email Notifications
```bash
curl -X POST "http://localhost:8000/monitoring/email/config" \
     -H "Content-Type: application/json" \
     -d '{
         "smtp_server": "smtp.example.com",
         "smtp_port": 587,
         "username": "your-email@example.com",
         "password": "your-password",
         "from_email": "notifications@example.com"
     }'
```

#### Add Webhook
```bash
curl -X POST "http://localhost:8000/monitoring/webhook/my-webhook" \
     -H "Content-Type: application/json" \
     -d '{
         "url": "https://your-webhook-url.com",
         "secret": "optional-secret-key",
         "events": ["new_content", "rating_update"],
         "headers": {
             "Authorization": "Bearer your-token"
         }
     }'
```

#### Get Monitoring Statistics
```bash
curl -X GET "http://localhost:8000/monitoring/statistics"
```

#### Cleanup Notifications
```bash
curl -X POST "http://localhost:8000/monitoring/cleanup?days=30"
```

### Notes

1. **Interest Profiles**:
   - Profiles can monitor multiple sources
   - Keywords support fuzzy matching
   - Authors are matched exactly
   - Notification preferences can be customized

2. **Email Configuration**:
   - Supports TLS/SSL
   - Password is stored securely
   - Can be updated at any time

3. **Webhooks**:
   - Support custom headers
   - Optional secret for security
   - Can be configured for specific events
   - Include timestamp in payload

4. **Statistics**:
   - Track active vs. total profiles
   - Monitor notification counts
   - Track source-specific activity
   - Include last check time

5. **Cleanup**:
   - Default 30-day retention
   - Configurable retention period
   - Maintains active profiles
   - Preserves recent notifications

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

### Network Visualization
```bash
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "nodes": [
        {"id": "Paul", "connections": 5, "role": "protagonist", "work": "Dune", "community": 1},
        {"id": "Jessica", "connections": 4, "role": "mentor", "work": "Dune", "community": 1}
      ],
      "edges": [
        {"source": "Paul", "target": "Jessica"}
      ],
      "communities": [
        {"id": 1, "size": 2, "density": 0.5, "characters": ["Paul", "Jessica"]}
      ]
    },
    "visualization_type": "network",
    "format": "png",
    "enhanced": true
  }'
```

### Temporal Visualization
```bash
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "timeline": [
        {"year": "1965", "metrics": {"theme_count": 5, "character_count": 10}},
        {"year": "1975", "metrics": {"theme_count": 7, "character_count": 15}}
      ]
    },
    "visualization_type": "temporal",
    "format": "png",
    "enhanced": true
  }'
```

### Comparative Visualization
```bash
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "works": ["Dune", "Foundation"],
      "metrics": {
        "theme_count": [5, 6],
        "character_count": [10, 12]
      },
      "similarity_matrix": [[1.0, 0.8], [0.8, 1.0]]
    },
    "visualization_type": "comparative",
    "format": "png",
    "enhanced": true
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

1. **Network Visualization**:
   - Nodes represent characters
   - Edges represent relationships
   - Node size indicates connection count
   - Colors indicate communities
   - Enhanced mode adds labels for central nodes

2. **Temporal Visualization**:
   - Shows metrics over time
   - Enhanced mode includes theme evolution
   - Supports multiple metrics
   - Includes grid and legend

3. **Comparative Visualization**:
   - Bar charts for metric comparison
   - Enhanced mode shows similarity matrix
   - Supports multiple works and metrics
   - Color-coded for clarity

4. **General Notes**:
   - All visualizations return base64-encoded images
   - Enhanced mode provides more detailed visualizations
   - Metadata includes type-specific information
   - PNG format is recommended for best quality 