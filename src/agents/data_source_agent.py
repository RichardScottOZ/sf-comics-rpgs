from typing import Dict, Any, List, Optional
import logging
import wikipediaapi
from datetime import datetime
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DataSourceAgent(BaseAgent):
    """Agent for handling external data source integrations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type="data_source")
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='SFMCP/1.0 (https://github.com/yourusername/sfmcp; your-email@example.com)'
        )
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
    def get_wikipedia_summary(self, title: str, enhanced: bool = False) -> Dict[str, Any]:
        """Get Wikipedia summary for a given title.
        
        Args:
            title: The title to search for
            enhanced: Whether to include additional metadata
            
        Returns:
            Dictionary containing summary and metadata
        """
        cache_key = f"wiki_{title}_{enhanced}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
        
        try:
            page = self.wiki.page(title)
            if not page.exists():
                return {
                    "error": f"Wikipedia page not found for title: {title}",
                    "exists": False
                }
            
            result = {
                "title": page.title,
                "summary": page.summary,
                "exists": True,
                "url": page.fullurl,
                "timestamp": datetime.now().isoformat()
            }
            
            if enhanced:
                result.update({
                    "categories": [cat.title for cat in page.categories.values()],
                    "sections": [section.title for section in page.sections],
                    "links": list(page.links.keys())[:10],  # First 10 links
                    "word_count": len(page.text.split())
                })
            
            # Cache the result
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Wikipedia data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            }
    
    def search_wikipedia(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for articles matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching articles with summaries
        """
        cache_key = f"wiki_search_{query}_{limit}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
        
        try:
            results = []
            search_results = self.wiki.search(query, results=limit)
            
            for title in search_results:
                page = self.wiki.page(title)
                if page.exists():
                    results.append({
                        "title": page.title,
                        "summary": page.summary[:200] + "..." if len(page.summary) > 200 else page.summary,
                        "url": page.fullurl
                    })
            
            # Cache the results
            self.cache[cache_key] = (results, datetime.now())
            return results
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {str(e)}")
            return []
    
    def get_related_articles(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get articles related to a given Wikipedia article.
        
        Args:
            title: Title of the article
            limit: Maximum number of related articles to return
            
        Returns:
            List of related articles
        """
        cache_key = f"wiki_related_{title}_{limit}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
        
        try:
            page = self.wiki.page(title)
            if not page.exists():
                return []
            
            related = []
            for link_title in list(page.links.keys())[:limit]:
                link_page = self.wiki.page(link_title)
                if link_page.exists():
                    related.append({
                        "title": link_page.title,
                        "summary": link_page.summary[:200] + "..." if len(link_page.summary) > 200 else link_page.summary,
                        "url": link_page.fullurl
                    })
            
            # Cache the results
            self.cache[cache_key] = (related, datetime.now())
            return related
            
        except Exception as e:
            logger.error(f"Error getting related articles: {str(e)}")
            return [] 