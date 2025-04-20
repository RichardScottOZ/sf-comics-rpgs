from typing import Dict, Any, List, Optional
import logging
import wikipediaapi
import requests
from datetime import datetime
from bs4 import BeautifulSoup
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
        
        # Initialize API clients
        self.goodreads_api_key = config.get('goodreads_api_key') if config else None
        self.librarything_api_key = config.get('librarything_api_key') if config else None
        
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
    
    def get_goodreads_data(self, title: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Get book data from Goodreads.
        
        Args:
            title: Book title
            author: Optional author name
            
        Returns:
            Dictionary containing Goodreads data
        """
        if not self.goodreads_api_key:
            return {"error": "Goodreads API key not configured"}
            
        cache_key = f"goodreads_{title}_{author}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
                
        try:
            # Goodreads API endpoint
            url = "https://www.goodreads.com/search/index.xml"
            params = {
                "key": self.goodreads_api_key,
                "q": f"{title} {author}" if author else title
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            # Note: You'll need to implement XML parsing based on Goodreads API response format
            result = {
                "title": title,
                "author": author,
                "goodreads_data": response.text,  # Replace with parsed data
                "timestamp": datetime.now().isoformat()
            }
            
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Goodreads data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            }
            
    def get_librarything_data(self, title: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Get book data from LibraryThing.
        
        Args:
            title: Book title
            author: Optional author name
            
        Returns:
            Dictionary containing LibraryThing data
        """
        if not self.librarything_api_key:
            return {"error": "LibraryThing API key not configured"}
            
        cache_key = f"librarything_{title}_{author}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
                
        try:
            # LibraryThing API endpoint
            url = "https://www.librarything.com/services/rest/1.1/"
            params = {
                "method": "librarything.ck.getwork",
                "apikey": self.librarything_api_key,
                "title": title,
                "author": author if author else ""
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Parse XML response
            # Note: You'll need to implement XML parsing based on LibraryThing API response format
            result = {
                "title": title,
                "author": author,
                "librarything_data": response.text,  # Replace with parsed data
                "timestamp": datetime.now().isoformat()
            }
            
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching LibraryThing data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            }
            
    def get_openlibrary_data(self, title: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Get book data from OpenLibrary.
        
        Args:
            title: Book title
            author: Optional author name
            
        Returns:
            Dictionary containing OpenLibrary data
        """
        cache_key = f"openlibrary_{title}_{author}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
                
        try:
            # OpenLibrary API endpoint
            url = "https://openlibrary.org/search.json"
            params = {
                "q": f"{title} {author}" if author else title,
                "limit": 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("docs"):
                book = data["docs"][0]
                result = {
                    "title": book.get("title"),
                    "author": book.get("author_name", [""])[0],
                    "publish_year": book.get("first_publish_year"),
                    "isbn": book.get("isbn", [""])[0],
                    "cover_url": f"https://covers.openlibrary.org/b/id/{book.get('cover_i')}-L.jpg" if book.get("cover_i") else None,
                    "openlibrary_url": f"https://openlibrary.org{book.get('key')}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "error": "Book not found",
                    "exists": False
                }
            
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching OpenLibrary data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            }
            
    def get_isfdb_data(self, title: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Get book data from the Internet Science Fiction Database.
        
        Args:
            title: Book title
            author: Optional author name
            
        Returns:
            Dictionary containing ISFDB data
        """
        cache_key = f"isfdb_{title}_{author}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
                
        try:
            # ISFDB search endpoint
            search_url = "https://www.isfdb.org/cgi-bin/search.cgi"
            params = {
                "title": title,
                "author": author if author else "",
                "type": "Title"  # Search by title
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            result = {
                "title": title,
                "author": author,
                "timestamp": datetime.now().isoformat()
            }
            
            # Find the first search result
            search_results = soup.find_all('tr', class_='row0') + soup.find_all('tr', class_='row1')
            if search_results:
                first_result = search_results[0]
                cells = first_result.find_all('td')
                
                if len(cells) >= 3:
                    # Extract publication details
                    pub_details = cells[2].get_text(strip=True)
                    result.update({
                        "publication_details": pub_details,
                        "isfdb_url": f"https://www.isfdb.org{first_result.find('a')['href']}" if first_result.find('a') else None
                    })
                    
                    # Get detailed information from the book page
                    if result["isfdb_url"]:
                        book_response = requests.get(result["isfdb_url"])
                        book_soup = BeautifulSoup(book_response.text, 'html.parser')
                        
                        # Extract additional information
                        book_info = {}
                        
                        # Get cover image if available
                        cover_img = book_soup.find('img', class_='cover')
                        if cover_img:
                            book_info["cover_url"] = f"https://www.isfdb.org{cover_img['src']}"
                            
                        # Get publication history
                        pub_history = []
                        pub_table = book_soup.find('table', class_='publication')
                        if pub_table:
                            for row in pub_table.find_all('tr')[1:]:  # Skip header row
                                cells = row.find_all('td')
                                if len(cells) >= 4:
                                    pub_history.append({
                                        "publisher": cells[0].get_text(strip=True),
                                        "format": cells[1].get_text(strip=True),
                                        "date": cells[2].get_text(strip=True),
                                        "price": cells[3].get_text(strip=True)
                                    })
                        book_info["publication_history"] = pub_history
                        
                        # Get awards if any
                        awards = []
                        awards_table = book_soup.find('table', class_='awards')
                        if awards_table:
                            for row in awards_table.find_all('tr')[1:]:  # Skip header row
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    awards.append({
                                        "award": cells[0].get_text(strip=True),
                                        "year": cells[1].get_text(strip=True)
                                    })
                        book_info["awards"] = awards
                        
                        result.update(book_info)
            
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching ISFDB data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            }
            
    def get_isfdb_author(self, author_name: str) -> Dict[str, Any]:
        """Get author information from the Internet Science Fiction Database.
        
        Args:
            author_name: Author's name
            
        Returns:
            Dictionary containing author information
        """
        cache_key = f"isfdb_author_{author_name}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
                
        try:
            # ISFDB author search endpoint with correct parameters
            search_url = "https://www.isfdb.org/cgi-bin/se.cgi"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            params = {
                "arg": author_name,
                "type": "Name"
            }
            
            response = requests.get(search_url, params=params, headers=headers)
            response.raise_for_status()
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            result = {
                "author": author_name,
                "timestamp": datetime.now().isoformat()
            }
            
            # Find the first search result
            search_results = soup.find_all('tr', class_='row0') + soup.find_all('tr', class_='row1')
            if search_results:
                first_result = search_results[0]
                author_link = first_result.find('a')
                
                if author_link:
                    author_url = f"https://www.isfdb.org{author_link['href']}"
                    result["isfdb_url"] = author_url
                    
                    # Get detailed author information
                    author_response = requests.get(author_url, headers=headers)
                    author_soup = BeautifulSoup(author_response.text, 'html.parser')
                    
                    # Extract author details
                    author_info = {}
                    
                    # Get author photo if available
                    photo = author_soup.find('img', class_='photo')
                    if photo:
                        author_info["photo_url"] = f"https://www.isfdb.org{photo['src']}"
                        
                    # Get bibliography
                    bibliography = []
                    pub_table = author_soup.find('table', class_='publication')
                    if pub_table:
                        for row in pub_table.find_all('tr')[1:]:  # Skip header row
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                bibliography.append({
                                    "title": cells[0].get_text(strip=True),
                                    "publisher": cells[1].get_text(strip=True),
                                    "year": cells[2].get_text(strip=True)
                                })
                    author_info["bibliography"] = bibliography
                    
                    # Get awards
                    awards = []
                    awards_table = author_soup.find('table', class_='awards')
                    if awards_table:
                        for row in awards_table.find_all('tr')[1:]:  # Skip header row
                            cells = row.find_all('td')
                            if len(cells) >= 2:
                                awards.append({
                                    "award": cells[0].get_text(strip=True),
                                    "year": cells[1].get_text(strip=True)
                                })
                    author_info["awards"] = awards
                    
                    result.update(author_info)
            
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching ISFDB author data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            }
            
    def get_rpggeek_data(self, title: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Get RPG data from RPGGeek (via BGG XML API).
        
        Args:
            title: RPG title
            author: Optional author/designer name
            
        Returns:
            Dictionary containing RPG data
        """
        cache_key = f"rpggeek_{title}_{author}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
                
        try:
            # First search for the RPG
            search_url = "https://www.rpggeek.com/xmlapi2/search"
            params = {
                "query": f"{title} {author}" if author else title,
                "type": "rpgitem"
            }
            
            search_response = requests.get(search_url, params=params)
            search_response.raise_for_status()
            
            # Parse the search results
            search_soup = BeautifulSoup(search_response.text, 'xml')
            result = {
                "title": title,
                "author": author,
                "timestamp": datetime.now().isoformat()
            }
            
            # Get the first matching item
            items = search_soup.find_all('item')
            if items:
                item = items[0]
                item_id = item.get('id')
                
                # Get detailed information
                detail_url = f"https://www.rpggeek.com/xmlapi2/thing"
                detail_params = {
                    "id": item_id,
                    "stats": 1
                }
                
                detail_response = requests.get(detail_url, params=detail_params)
                detail_response.raise_for_status()
                
                detail_soup = BeautifulSoup(detail_response.text, 'xml')
                item_detail = detail_soup.find('item')
                
                if item_detail:
                    # Extract basic information
                    result.update({
                        "rpggeek_id": item_id,
                        "rpggeek_url": f"https://www.rpggeek.com/rpgitem/{item_id}",
                        "name": item_detail.find('name', type='primary').get('value'),
                        "year_published": item_detail.find('yearpublished').get('value') if item_detail.find('yearpublished') else None,
                        "min_players": item_detail.find('minplayers').get('value') if item_detail.find('minplayers') else None,
                        "max_players": item_detail.find('maxplayers').get('value') if item_detail.find('maxplayers') else None,
                        "playing_time": item_detail.find('playingtime').get('value') if item_detail.find('playingtime') else None,
                        "min_age": item_detail.find('minage').get('value') if item_detail.find('minage') else None,
                        "description": item_detail.find('description').text if item_detail.find('description') else None
                    })
                    
                    # Extract links
                    links = []
                    for link in item_detail.find_all('link'):
                        links.append({
                            "type": link.get('type'),
                            "id": link.get('id'),
                            "value": link.get('value')
                        })
                    result["links"] = links
                    
                    # Extract statistics
                    stats = item_detail.find('statistics')
                    if stats:
                        result.update({
                            "rating": stats.find('average').get('value') if stats.find('average') else None,
                            "rank": stats.find('ranks').find('rank', type='subtype').get('value') if stats.find('ranks') else None,
                            "num_ratings": stats.find('usersrated').get('value') if stats.find('usersrated') else None,
                            "num_comments": stats.find('numcomments').get('value') if stats.find('numcomments') else None
                        })
                    
                    # Extract images
                    images = []
                    for image in item_detail.find_all('image'):
                        images.append({
                            "type": image.get('type'),
                            "url": image.text
                        })
                    result["images"] = images
            
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching RPGGeek data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            }

    def get_gcd_data(self, title: str, publisher: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """Get comic data from the Grand Comics Database.
        
        Args:
            title: Comic title
            publisher: Optional publisher name
            year: Optional publication year
            
        Returns:
            Dictionary containing GCD data
        """
        cache_key = f"gcd_{title}_{publisher}_{year}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
                
        try:
            # GCD search endpoint
            search_url = "https://www.comics.org/search/advanced/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Prepare search parameters
            params = {
                "target": "series",
                "method": "icontains",
                "logic": "True",
                "title": title,
                "publisher": publisher if publisher else "",
                "year": year if year else ""
            }
            
            # Perform the search
            response = requests.get(search_url, params=params, headers=headers)
            response.raise_for_status()
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            result = {
                "title": title,
                "publisher": publisher,
                "year": year,
                "timestamp": datetime.now().isoformat()
            }
            
            # Find the first search result
            search_results = soup.find_all('tr', class_='row_even') + soup.find_all('tr', class_='row_odd')
            if search_results:
                first_result = search_results[0]
                cells = first_result.find_all('td')
                
                if len(cells) >= 3:
                    # Extract series details
                    series_link = cells[0].find('a')
                    if series_link:
                        series_url = f"https://www.comics.org{series_link['href']}"
                        result["gcd_url"] = series_url
                        
                        # Get detailed information from the series page
                        series_response = requests.get(series_url, headers=headers)
                        series_soup = BeautifulSoup(series_response.text, 'html.parser')
                        
                        # Extract series information
                        series_info = {}
                        
                        # Get cover image if available
                        cover_img = series_soup.find('img', class_='cover')
                        if cover_img:
                            series_info["cover_url"] = f"https://www.comics.org{cover_img['src']}"
                            
                        # Get publication details
                        pub_details = series_soup.find('div', class_='series_details')
                        if pub_details:
                            for detail in pub_details.find_all('div', class_='field'):
                                label = detail.find('div', class_='label')
                                value = detail.find('div', class_='value')
                                if label and value:
                                    series_info[label.text.strip().lower().replace(' ', '_')] = value.text.strip()
                            
                        # Get issue list
                        issues = []
                        issue_table = series_soup.find('table', class_='issue_list')
                        if issue_table:
                            for row in issue_table.find_all('tr')[1:]:  # Skip header row
                                cells = row.find_all('td')
                                if len(cells) >= 4:
                                    issue_link = cells[0].find('a')
                                    if issue_link:
                                        issues.append({
                                            "number": cells[0].text.strip(),
                                            "title": cells[1].text.strip(),
                                            "date": cells[2].text.strip(),
                                            "price": cells[3].text.strip(),
                                            "url": f"https://www.comics.org{issue_link['href']}"
                                        })
                        series_info["issues"] = issues
                        
                        result.update(series_info)
            
            self.cache[cache_key] = (result, datetime.now())
            return result
            
        except Exception as e:
            logger.error(f"Error fetching GCD data: {str(e)}")
            return {
                "error": str(e),
                "exists": False
            } 