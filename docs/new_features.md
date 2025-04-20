# New Features and Endpoints

This document outlines the recently added features and endpoints to the SFMCP API. For the complete API documentation, please refer to [api.md](api.md).

## New Data Source Endpoints

### Book Library Integrations
The API now supports integration with multiple book databases.

#### Goodreads Integration
```bash
POST /goodreads/data
```

**Parameters:**
- `title` (required): Book title
- `author` (optional): Author name

**Returns:**
- Book details
- Ratings and reviews
- Publication information
- Cover images
- Goodreads URL

#### LibraryThing Integration
```bash
POST /librarything/data
```

**Parameters:**
- `title` (required): Book title
- `author` (optional): Author name

**Returns:**
- Book details
- Tags and categories
- Publication information
- Cover images
- LibraryThing URL

#### OpenLibrary Integration
```bash
POST /openlibrary/data
```

**Parameters:**
- `title` (required): Book title
- `author` (optional): Author name

**Returns:**
- Book details
- Publication information
- Cover images
- OpenLibrary URL

### Wikipedia Integration
The API now provides access to Wikipedia data through multiple endpoints.

#### Get Wikipedia Summary
```bash
POST /wikipedia/summary
```

**Parameters:**
- `title` (required): Article title
- `enhanced` (optional): Include additional metadata (default: false)

**Returns:**
- Article summary
- Basic metadata
- Enhanced metadata (if requested)

#### Search Wikipedia
```bash
POST /wikipedia/search
```

**Parameters:**
- `query` (required): Search query
- `limit` (optional): Maximum number of results (default: 5)

**Returns:**
- List of matching articles
- Brief summaries
- Article URLs

#### Get Related Articles
```bash
POST /wikipedia/related
```

**Parameters:**
- `title` (required): Source article title
- `limit` (optional): Maximum number of results (default: 5)

**Returns:**
- List of related articles
- Brief summaries
- Article URLs

### Grand Comics Database (GCD) Integration
The GCD integration allows retrieving comprehensive comic book data.

#### Endpoint
```bash
POST /gcd/data
```

#### Parameters
- `title` (required): Comic title
- `publisher` (optional): Publisher name
- `year` (optional): Publication year

#### Returns
- Series information
- Publication details
- Cover images
- Issue list with details
- GCD URLs

#### Example Request
```bash
curl -X POST "http://localhost:8000/gcd/data" \
     -H "Content-Type: application/json" \
     -d '{"title": "Amazing Spider-Man", "publisher": "Marvel", "year": 1963}'
```

### RPGGeek Integration
The RPGGeek integration provides access to RPG data through the BGG XML API.

#### Endpoint
```bash
POST /rpggeek/data
```

#### Parameters
- `title` (required): RPG title
- `author` (optional): Author/designer name

#### Returns
- Basic RPG information
- Publication details
- Player counts and play time
- Ratings and rankings
- Links to related items
- Images

#### Example Request
```bash
curl -X POST "http://localhost:8000/rpggeek/data" \
     -H "Content-Type: application/json" \
     -d '{"title": "Dungeons & Dragons", "author": "Gary Gygax"}'
```

## Enhanced Comparative Analysis

The comparative analysis endpoints now support additional features:

### Historical Context
The `/compare/works` endpoint now includes an optional `include_historical_context` parameter that provides historical analysis of works.

#### Example Request with Historical Context
```bash
curl -X POST "http://localhost:8000/compare/works" \
     -H "Content-Type: application/json" \
     -d '{
           "works": [
             {"title": "Dune", "author": "Frank Herbert", "year": 1965},
             {"title": "Foundation", "author": "Isaac Asimov", "year": 1951}
           ],
           "analysis_type": "themes",
           "enhanced": true,
           "include_historical_context": true
         }'
```

## Response Format Updates

All new endpoints follow the standardized response format:

```json
{
  "data": { ... },
  "metadata": {
    "timestamp": "ISO-8601 timestamp",
    "source": "data source identifier",
    "cache_hit": boolean
  }
}
```

Error responses maintain consistency with the existing format:

```json
{
  "error": "error message",
  "exists": false
}
```

## Caching

All new endpoints implement caching with a 1-hour TTL to improve performance and reduce load on external data sources.

## Notes
- Image URLs are provided when available
- Some endpoints may return partial data if certain information is not available
- The API is designed to be resilient to missing data, returning what information is available
- All dates are returned in ISO-8601 format 