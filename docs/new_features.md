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

### Internet Speculative Fiction Database (ISFDB) Integration
The ISFDB integration provides access to comprehensive science fiction and fantasy book data. Note: This integration is currently in beta and has some known limitations.

#### Book Data Endpoint
```bash
POST /isfdb/data
```

**Parameters:**
- `title` (required): Book title
- `author` (optional): Author name
- `year` (optional): Publication year

**Returns:**
- Book details
- Publication history
- Cover images
- Awards
- ISFDB URL

**Current Limitations:**
- Search functionality is limited to exact title matches
- Some fields may be missing for older or less popular works
- Cover images are not available for all entries
- Publication history may be incomplete for some works

**Planned Improvements:**
- Enhanced search functionality with fuzzy matching
- Support for series information
- Additional metadata fields
- Improved error handling
- Rate limiting implementation
- Caching optimization

#### Author Data Endpoint
```bash
POST /isfdb/author
```

**Parameters:**
- `author_name` (required): Author's name

**Returns:**
- Author information
- Bibliography
- Awards
- Author photo (if available)
- ISFDB URL

**Current Limitations:**
- Search is case-sensitive
- Some author entries may be incomplete
- Photo availability is limited
- Bibliography may not include all works

**Planned Improvements:**
- Case-insensitive search
- Enhanced author metadata
- Improved photo handling
- Complete bibliography support
- Series information integration

**Example Requests:**

Book data:
```bash
curl -X POST "http://localhost:8000/isfdb/data" \
     -H "Content-Type: application/json" \
     -d '{"title": "Dune", "author": "Frank Herbert", "year": 1965}'
```

Author data:
```bash
curl -X POST "http://localhost:8000/isfdb/author" \
     -H "Content-Type: application/json" \
     -d '{"author_name": "Frank Herbert"}'
```

**Error Handling:**
The ISFDB integration returns specific error codes:
- 404: Work or author not found
- 500: Server error
- 503: Service temporarily unavailable

**Response Format:**
```json
{
  "data": {
    "title": "Dune",
    "author": "Frank Herbert",
    "publication_history": [...],
    "cover_images": [...],
    "awards": [...],
    "isfdb_url": "https://www.isfdb.org/cgi-bin/pl.cgi?12345"
  },
  "metadata": {
    "timestamp": "2024-03-14T12:00:00Z",
    "source": "isfdb",
    "cache_hit": false
  }
}
```

**Error Response:**
```json
{
  "error": "Work not found",
  "exists": false,
  "details": "No matching work found in ISFDB database"
}
```

**Notes:**
- All dates are returned in ISO-8601 format
- Image URLs are provided when available
- Some fields may be null if data is not available
- The API is designed to be resilient to missing data
- Cache TTL is set to 1 hour to reduce load on ISFDB servers

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