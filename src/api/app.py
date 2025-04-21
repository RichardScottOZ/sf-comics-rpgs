from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from ..agents.sf_agent import ScienceFictionAgent
from ..agents.comics_agent import ComicsAgent
from ..agents.rpg_agent import RPGAgent, MCPEnabledRPGAgent
from ..agents.comparative_agent import ComparativeAgent
from ..analysis.temporal_analysis import TemporalAnalysis
from ..analysis.character_network import CharacterNetwork
from ..analysis.community_analysis import CommunityAnalysis
from ..config.settings import settings
from ..agents.network_agent import NetworkAnalysisAgent
from ..agents.visualization_agent import VisualizationAgent
from ..agents.data_source_agent import DataSourceAgent
from ..agents.monitoring_agent import MonitoringAgent
from ..agents.parallel_agent import ParallelAgentFactory, ParallelConfig
from ..agents.sf_agent import MCPEnabledScienceFictionAgent
from ..agents.comics_agent import MCPEnabledComicsAgent

app = FastAPI(
    title="SFMCP API",
    description="Science Fiction, Comics, and RPG Content Analysis API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize agents and analyzers
sf_agent = ScienceFictionAgent()
comics_agent = ComicsAgent()
rpg_agent = RPGAgent()
comparative_agent = ComparativeAgent()
temporal_analyzer = TemporalAnalysis()
character_network = CharacterNetwork()
community_analyzer = CommunityAnalysis()
network_agent = NetworkAnalysisAgent()
visualization_agent = VisualizationAgent()

# Initialize monitoring agent
monitoring_agent = MonitoringAgent()

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
    enhanced: Optional[bool] = False
    include_historical_context: Optional[bool] = True

class TemporalAnalysisRequest(BaseModel):
    works: List[Dict[str, Any]]
    analysis_type: Optional[str] = "evolution"

class NetworkAnalysisRequest(BaseModel):
    works: List[Dict[str, Any]]
    analysis_type: Optional[str] = "relationships"

class CommunityAnalysisRequest(BaseModel):
    works: List[Dict[str, Any]]
    analysis_type: Optional[str] = "patterns"

class Work(BaseModel):
    title: str
    author: str
    year: Optional[int] = None
    characters: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]

class VisualizationRequest(BaseModel):
    data: Dict[str, Any]
    visualization_type: str
    format: Optional[str] = "png"
    enhanced: Optional[bool] = False
    save_to_disk: Optional[bool] = False

class WikipediaRequest(BaseModel):
    title: str
    enhanced: Optional[bool] = False

class WikipediaSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class WikipediaRelatedRequest(BaseModel):
    title: str
    limit: Optional[int] = 5

class BookRequest(BaseModel):
    title: str
    author: Optional[str] = None

class ISFDBRequest(BaseModel):
    title: str
    author: Optional[str] = None

class ISFDBAuthorRequest(BaseModel):
    author_name: str

class RPGGeekRequest(BaseModel):
    title: str
    author: Optional[str] = None

class GCDRequest(BaseModel):
    title: str
    publisher: Optional[str] = None
    year: Optional[int] = None

class InterestProfile(BaseModel):
    name: str
    sources: List[str]
    keywords: List[str]
    authors: List[str]
    notification_preferences: Dict[str, Any]

class EmailConfig(BaseModel):
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str

class WebhookConfig(BaseModel):
    url: str
    secret: Optional[str] = None
    events: List[str]
    headers: Optional[Dict[str, str]] = None

class ParallelAnalysisRequest(BaseModel):
    content: str
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    creator: Optional[str] = None
    system: Optional[str] = None
    source: Optional[str] = None
    edition: Optional[str] = None
    year: Optional[int] = None
    model: Optional[str] = None
    mode: Optional[str] = "parallel"  # 'parallel', 'original', or 'mcp'

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
            force_refresh=request.force_refresh,
            enhanced=request.enhanced,
            include_historical_context=request.include_historical_context
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
            force_refresh=request.force_refresh,
            enhanced=request.enhanced,
            include_historical_context=request.include_historical_context
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
            force_refresh=request.force_refresh,
            enhanced=request.enhanced,
            include_historical_context=request.include_historical_context
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
            force_refresh=request.force_refresh,
            enhanced=request.enhanced,
            include_historical_context=request.include_historical_context
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
            force_refresh=request.force_refresh,
            enhanced=request.enhanced,
            include_historical_context=request.include_historical_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compare/analysis_types", tags=["Comparative Analysis"])
async def get_analysis_types():
    """Get list of available analysis types"""
    try:
        return {"analysis_types": comparative_agent.get_available_analysis_types()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Temporal Analysis Endpoints
@app.post("/analyze/temporal", tags=["Temporal Analysis"])
async def analyze_temporal(request: TemporalAnalysisRequest):
    """Analyze works across different time periods"""
    try:
        result = temporal_analyzer.analyze_temporal_patterns(
            works=request.works,
            analysis_type=request.analysis_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Character Network Analysis Endpoints
@app.post("/analyze/network", tags=["Network Analysis"])
async def analyze_network(works: List[Work]):
    """Analyze character networks across works."""
    try:
        result = await network_agent.analyze_network(works)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Community Analysis Endpoints
@app.post("/analyze/community", tags=["Community Analysis"])
async def analyze_community(request: CommunityAnalysisRequest):
    """Analyze works across different communities"""
    try:
        result = community_analyzer.analyze_communities(
            works=request.works,
            analysis_type=request.analysis_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/visualize")
async def generate_visualization(request: VisualizationRequest):
    """Generate a visualization from analysis data."""
    try:
        result = await visualization_agent.generate_visualization(
            data=request.data,
            visualization_type=request.visualization_type,
            format=request.format,
            enhanced=request.enhanced,
            save_to_disk=request.save_to_disk
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visualization/types")
async def get_visualization_types():
    """Get available visualization types."""
    return {
        "types": [
            {
                "name": "network",
                "description": "Character network visualization",
                "supports_enhanced": True
            },
            {
                "name": "temporal",
                "description": "Temporal analysis visualization",
                "supports_enhanced": True
            },
            {
                "name": "comparative",
                "description": "Comparative analysis visualization",
                "supports_enhanced": True
            }
        ]
    }

@app.post("/wikipedia/summary")
async def get_wikipedia_summary(request: WikipediaRequest):
    """Get Wikipedia summary for a given title."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_wikipedia_summary(
            title=request.title,
            enhanced=request.enhanced
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wikipedia/search")
async def search_wikipedia(request: WikipediaSearchRequest):
    """Search Wikipedia for articles matching a query."""
    try:
        data_source_agent = DataSourceAgent()
        results = data_source_agent.search_wikipedia(
            query=request.query,
            limit=request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wikipedia/related")
async def get_related_articles(request: WikipediaRelatedRequest):
    """Get articles related to a given Wikipedia article."""
    try:
        data_source_agent = DataSourceAgent()
        results = data_source_agent.get_related_articles(
            title=request.title,
            limit=request.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/goodreads/data")
async def get_goodreads_data(request: BookRequest):
    """Get book data from Goodreads."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_goodreads_data(
            title=request.title,
            author=request.author
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/librarything/data")
async def get_librarything_data(request: BookRequest):
    """Get book data from LibraryThing."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_librarything_data(
            title=request.title,
            author=request.author
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/openlibrary/data")
async def get_openlibrary_data(request: BookRequest):
    """Get book data from OpenLibrary."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_openlibrary_data(
            title=request.title,
            author=request.author
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/isfdb/data")
async def get_isfdb_data(request: ISFDBRequest):
    """Get book data from the Internet Science Fiction Database."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_isfdb_data(
            title=request.title,
            author=request.author
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/isfdb/author")
async def get_isfdb_author(request: ISFDBAuthorRequest):
    """Get author information from the Internet Science Fiction Database."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_isfdb_author(
            author_name=request.author_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rpggeek/data")
async def get_rpggeek_data(request: RPGGeekRequest):
    """Get RPG data from RPGGeek."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_rpggeek_data(
            title=request.title,
            author=request.author
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gcd/data")
async def get_gcd_data(request: GCDRequest):
    """Get comic data from the Grand Comics Database."""
    try:
        data_source_agent = DataSourceAgent()
        result = data_source_agent.get_gcd_data(
            title=request.title,
            publisher=request.publisher,
            year=request.year
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/profile")
async def create_interest_profile(profile: InterestProfile):
    """Create a new interest profile for monitoring."""
    try:
        result = await monitoring_agent.add_interest_profile(profile.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/profile/{profile_id}")
async def get_profile_updates(profile_id: int):
    """Get updates for a specific interest profile."""
    try:
        result = await monitoring_agent.get_notification_summary(profile_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/profiles")
async def list_profiles():
    """List all interest profiles."""
    try:
        return {
            "profiles": [
                {
                    "profile_id": pid,
                    "name": profile["name"],
                    "last_checked": profile["last_checked"],
                    "sources": profile["sources"]
                }
                for pid, profile in monitoring_agent.interest_profiles.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/monitoring/profile/{profile_id}")
async def delete_profile(profile_id: int):
    """Delete an interest profile."""
    try:
        if profile_id not in monitoring_agent.interest_profiles:
            raise HTTPException(status_code=404, detail="Profile not found")
        del monitoring_agent.interest_profiles[profile_id]
        return {"status": "success", "message": f"Profile {profile_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/email/config")
async def configure_email(config: EmailConfig):
    """Configure email notifications."""
    try:
        await monitoring_agent.configure_email(config.dict())
        return {"status": "success", "message": "Email configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/webhook/{webhook_id}")
async def add_webhook(webhook_id: str, config: WebhookConfig):
    """Add a new webhook configuration."""
    try:
        await monitoring_agent.add_webhook(webhook_id, config.dict())
        return {"status": "success", "message": f"Webhook {webhook_id} added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/monitoring/webhook/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Delete a webhook configuration."""
    try:
        if webhook_id in monitoring_agent.webhooks:
            del monitoring_agent.webhooks[webhook_id]
            return {"status": "success", "message": f"Webhook {webhook_id} deleted"}
        raise HTTPException(status_code=404, detail="Webhook not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/statistics")
async def get_monitoring_statistics():
    """Get monitoring statistics."""
    try:
        return await monitoring_agent.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitoring/cleanup")
async def cleanup_notifications(days: Optional[int] = 30):
    """Clean up old notifications."""
    try:
        await monitoring_agent.cleanup_old_notifications(days)
        return {"status": "success", "message": f"Cleaned up notifications older than {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Parallel Execution Endpoints
@app.post("/analyze/parallel/sf", tags=["Parallel Execution"])
async def analyze_science_fiction_parallel(request: ParallelAnalysisRequest):
    """Analyze science fiction content using parallel execution"""
    try:
        factory = ParallelAgentFactory(ParallelConfig())
        # Register the agent classes with their proper names
        factory.register_agent_class(
            "science_fiction",
            ScienceFictionAgent,
            MCPEnabledScienceFictionAgent
        )
        
        if request.mode == "parallel":
            results = await factory.execute_parallel(
                "science_fiction",  # Use the registered name
                "analyze_content",
                request.content,
                title=request.title,
                author=request.author,
                year=request.year,
                model=request.model
            )
        else:
            results = await factory.execute_smart(
                "science_fiction",  # Use the registered name
                "analyze_content",
                request.content,
                title=request.title,
                author=request.author,
                year=request.year,
                model=request.model
            )
            
        return {
            "results": results,
            "comparison": factory.get_comparison(results),
            "metrics": factory.monitor.get_metrics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/parallel/comics", tags=["Parallel Execution"])
async def analyze_comics_parallel(request: ParallelAnalysisRequest):
    """Analyze comics content using parallel execution"""
    try:
        factory = ParallelAgentFactory(ParallelConfig())
        # Register the agent classes with their proper names
        factory.register_agent_class(
            "comics",
            ComicsAgent,
            MCPEnabledComicsAgent
        )
        
        if request.mode == "parallel":
            results = await factory.execute_parallel(
                "comics",  # Use the registered name
                "analyze_content",
                request.content,
                title=request.title,
                publisher=request.publisher,
                year=request.year,
                creator=request.creator,
                model=request.model
            )
        else:
            results = await factory.execute_smart(
                "comics",  # Use the registered name
                "analyze_content",
                request.content,
                title=request.title,
                publisher=request.publisher,
                year=request.year,
                creator=request.creator,
                model=request.model
            )
            
        return {
            "results": results,
            "comparison": factory.get_comparison(results),
            "metrics": factory.monitor.get_metrics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/parallel/rpg", tags=["Parallel Execution"])
async def analyze_rpg_parallel(request: ParallelAnalysisRequest):
    """Analyze RPG content using parallel execution"""
    try:
        factory = ParallelAgentFactory(ParallelConfig())
        # Register the agent classes with their proper names
        factory.register_agent_class(
            "rpg",
            RPGAgent,
            MCPEnabledRPGAgent
        )
        
        if request.mode == "parallel":
            results = await factory.execute_parallel(
                "rpg",  # Use the registered name
                "analyze_content",
                request.content,
                title=request.title,
                system=request.system,
                source=request.source,
                edition=request.edition,
                publisher=request.publisher,
                model=request.model
            )
        else:
            results = await factory.execute_smart(
                "rpg",  # Use the registered name
                "analyze_content",
                request.content,
                title=request.title,
                system=request.system,
                source=request.source,
                edition=request.edition,
                publisher=request.publisher,
                model=request.model
            )
            
        return {
            "results": results,
            "comparison": factory.get_comparison(results),
            "metrics": factory.monitor.get_metrics()
        }
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