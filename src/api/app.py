from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from ..agents.sf_agent import ScienceFictionAgent
from ..agents.comics_agent import ComicsAgent
from ..agents.rpg_agent import RPGAgent
from ..agents.comparative_agent import ComparativeAgent
from ..config.settings import settings

app = FastAPI(
    title="SFMCP API",
    description="Science Fiction, Comics, and RPG Content Analysis API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize agents
sf_agent = ScienceFictionAgent()
comics_agent = ComicsAgent()
rpg_agent = RPGAgent()
comparative_agent = ComparativeAgent()

class AnalysisRequest(BaseModel):
    content: str
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    system: Optional[str] = None
    source: Optional[str] = None
    year: Optional[int] = None
    edition: Optional[str] = None
    creator: Optional[str] = None
    model: Optional[str] = None

class RecommendationRequest(BaseModel):
    based_on: str
    limit: Optional[int] = 5

class CharacterAnalysisRequest(BaseModel):
    character_sheet: str
    system: str

class ComparativeAnalysisRequest(BaseModel):
    works: List[Dict[str, Any]]
    analysis_type: str
    model: Optional[str] = None
    force_refresh: Optional[bool] = False

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/info", tags=["Info"])
async def get_info() -> Dict[str, str]:
    """Get basic information about the API"""
    return {
        "name": "SFMCP API",
        "version": "0.1.0",
        "description": "Science Fiction, Comics, and RPG Content Analysis API",
        "documentation": "/docs"
    }

# Science Fiction Endpoints
@app.post("/analyze/sf", tags=["Science Fiction"])
async def analyze_science_fiction(request: AnalysisRequest):
    """Analyze science fiction content"""
    try:
        result = await sf_agent.analyze_content(
            content=request.content,
            title=request.title,
            author=request.author,
            year=request.year,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/sf", tags=["Science Fiction"])
async def recommend_science_fiction(request: RecommendationRequest):
    """Get science fiction recommendations"""
    try:
        result = await sf_agent.get_recommendations(
            based_on=request.based_on,
            limit=request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Comics Endpoints
@app.post("/analyze/comics", tags=["Comics"])
async def analyze_comics(request: AnalysisRequest):
    """Analyze comics content"""
    try:
        result = await comics_agent.analyze_content(
            content=request.content,
            title=request.title,
            publisher=request.publisher,
            year=request.year,
            creator=request.creator,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/comics", tags=["Comics"])
async def recommend_comics(request: RecommendationRequest):
    """Get comics recommendations"""
    try:
        result = await comics_agent.get_recommendations(
            based_on=request.based_on,
            limit=request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RPG Endpoints
@app.post("/analyze/rpg", tags=["RPG"])
async def analyze_rpg(request: AnalysisRequest):
    """Analyze RPG content"""
    try:
        result = await rpg_agent.analyze_content(
            content=request.content,
            system=request.system,
            source=request.source,
            edition=request.edition,
            publisher=request.publisher,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/rpg", tags=["RPG"])
async def recommend_rpg(request: RecommendationRequest):
    """Get RPG recommendations"""
    try:
        result = await rpg_agent.get_recommendations(
            based_on=request.based_on,
            limit=request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/character", tags=["RPG"])
async def analyze_character(request: CharacterAnalysisRequest):
    """Analyze RPG character sheet"""
    try:
        result = await rpg_agent.analyze_character(
            character_sheet=request.character_sheet,
            system=request.system
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Comparative Analysis Endpoints
@app.post("/compare/works", tags=["Comparative Analysis"])
async def compare_works(request: ComparativeAnalysisRequest):
    """Compare multiple works based on specified analysis type"""
    try:
        result = await comparative_agent.compare_works(
            works=request.works,
            analysis_type=request.analysis_type,
            model=request.model,
            force_refresh=request.force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare/world_building", tags=["Comparative Analysis"])
async def compare_world_building(request: ComparativeAnalysisRequest):
    """Compare world-building elements across works"""
    try:
        result = await comparative_agent.compare_works(
            works=request.works,
            analysis_type="world_building",
            model=request.model,
            force_refresh=request.force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare/themes", tags=["Comparative Analysis"])
async def compare_themes(request: ComparativeAnalysisRequest):
    """Compare themes and motifs across works"""
    try:
        result = await comparative_agent.compare_works(
            works=request.works,
            analysis_type="themes",
            model=request.model,
            force_refresh=request.force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare/characters", tags=["Comparative Analysis"])
async def compare_characters(request: ComparativeAnalysisRequest):
    """Compare character development and relationships across works"""
    try:
        result = await comparative_agent.compare_works(
            works=request.works,
            analysis_type="characters",
            model=request.model,
            force_refresh=request.force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare/plot", tags=["Comparative Analysis"])
async def compare_plot(request: ComparativeAnalysisRequest):
    """Compare plot structure and narrative techniques across works"""
    try:
        result = await comparative_agent.compare_works(
            works=request.works,
            analysis_type="plot",
            model=request.model,
            force_refresh=request.force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 