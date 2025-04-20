# SFMCP (Science Fiction, Comics, and RPG Content Analysis)

A Python-based API for analyzing and keeping track of science fiction, comics, and RPG content using OpenRouter as the backend.

## Features

- Content analysis for science fiction, comics, and RPG materials
- Caching system to avoid redundant API calls
- RESTful API interface
- Support for OpenRouter's various models
- Configurable settings through environment variables

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sfmcp.git
cd sfmcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Edit the `.env` file and add your OpenRouter API key.

## Usage

1. Start the API server:
```bash
python -m src.api.app
```

2. The API will be available at `http://localhost:8000`

3. API Endpoints:
- POST `/analyze/sf` - Analyze science fiction content
- POST `/analyze/comics` - Analyze comics content
- POST `/analyze/rpg` - Analyze RPG content

Example request:
```bash
curl -X POST "http://localhost:8000/analyze/sf" \
     -H "Content-Type: application/json" \
     -d '{
           "content": "Your content here",
           "title": "Optional title",
           "author": "Optional author"
         }'
```

## Development

- Run tests:
```bash
pytest
```

- Format code:
```bash
black .
isort .
```

- Check code quality:
```bash
flake8
```

## Project Structure

```
sfmcp/
├── config/         # Configuration files
├── data/          # Data storage
│   └── cache/     # Cached analysis results
├── docs/          # Documentation
├── src/
│   ├── api/       # API endpoints
│   ├── models/    # Data models
│   ├── services/  # Business logic
│   └── utils/     # Utility functions
└── tests/         # Test files
```

## License

MIT License 