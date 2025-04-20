from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from .data_source_agent import DataSourceAgent

class MonitoringAgent(BaseAgent):
    """Agent responsible for monitoring and detecting new content of interest."""
    
    def __init__(self):
        super().__init__()
        self.data_source_agent = DataSourceAgent()
        self.last_check_time = datetime.now()
        self.interest_profiles = {}  # Store user interest profiles
        self.notification_history = {}  # Track what's been notified
        
    async def add_interest_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new interest profile for monitoring.
        
        Args:
            profile: Dictionary containing monitoring preferences
                   {
                       'name': 'Profile Name',
                       'sources': ['isfdb', 'goodreads', 'wikipedia'],
                       'keywords': ['science fiction', 'cyberpunk'],
                       'authors': ['William Gibson', 'Neal Stephenson'],
                       'notification_preferences': {
                           'frequency': 'daily',
                           'channels': ['email', 'api']
                       }
                   }
        
        Returns:
            Dict containing the created profile
        """
        profile_id = len(self.interest_profiles) + 1
        self.interest_profiles[profile_id] = {
            **profile,
            'created_at': datetime.now(),
            'last_checked': datetime.now()
        }
        return {'profile_id': profile_id, **profile}
    
    async def check_for_updates(self, profile_id: int) -> List[Dict[str, Any]]:
        """Check for new content matching the interest profile.
        
        Args:
            profile_id: ID of the interest profile to check
            
        Returns:
            List of new items found
        """
        if profile_id not in self.interest_profiles:
            raise ValueError(f"Profile {profile_id} not found")
            
        profile = self.interest_profiles[profile_id]
        new_items = []
        
        # Check each source in the profile
        for source in profile['sources']:
            if source == 'isfdb':
                # Check ISFDB for new entries matching keywords/authors
                for keyword in profile['keywords']:
                    try:
                        results = await self.data_source_agent.get_isfdb_data(
                            title=keyword,
                            enhanced=True
                        )
                        new_items.extend(self._filter_new_items(results, profile))
                    except Exception as e:
                        logging.error(f"Error checking ISFDB: {e}")
                        
            elif source == 'goodreads':
                # Check Goodreads for new releases
                for author in profile['authors']:
                    try:
                        results = await self.data_source_agent.get_goodreads_data(
                            author=author
                        )
                        new_items.extend(self._filter_new_items(results, profile))
                    except Exception as e:
                        logging.error(f"Error checking Goodreads: {e}")
                        
            elif source == 'wikipedia':
                # Check Wikipedia for new articles
                for keyword in profile['keywords']:
                    try:
                        results = await self.data_source_agent.search_wikipedia(
                            query=keyword
                        )
                        new_items.extend(self._filter_new_items(results, profile))
                    except Exception as e:
                        logging.error(f"Error checking Wikipedia: {e}")
        
        # Update last checked time
        self.interest_profiles[profile_id]['last_checked'] = datetime.now()
        
        return new_items
    
    def _filter_new_items(self, results: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter results to find new items of interest.
        
        Args:
            results: List of items from data source
            profile: Interest profile to match against
            
        Returns:
            List of new items matching the profile
        """
        new_items = []
        for item in results:
            # Check if item is new (not in notification history)
            item_key = f"{item.get('source')}_{item.get('id')}"
            if item_key in self.notification_history:
                continue
                
            # Check if item matches profile criteria
            if self._matches_profile(item, profile):
                new_items.append(item)
                self.notification_history[item_key] = datetime.now()
                
        return new_items
    
    def _matches_profile(self, item: Dict[str, Any], profile: Dict[str, Any]) -> bool:
        """Check if an item matches the interest profile criteria.
        
        Args:
            item: Item to check
            profile: Interest profile to match against
            
        Returns:
            True if item matches profile criteria
        """
        # Check keywords
        if any(keyword.lower() in str(item).lower() 
               for keyword in profile['keywords']):
            return True
            
        # Check authors
        if 'author' in item and item['author'] in profile['authors']:
            return True
            
        return False
    
    async def get_notification_summary(self, profile_id: int) -> Dict[str, Any]:
        """Get a summary of notifications for a profile.
        
        Args:
            profile_id: ID of the interest profile
            
        Returns:
            Summary of notifications
        """
        if profile_id not in self.interest_profiles:
            raise ValueError(f"Profile {profile_id} not found")
            
        profile = self.interest_profiles[profile_id]
        new_items = await self.check_for_updates(profile_id)
        
        return {
            'profile_id': profile_id,
            'profile_name': profile['name'],
            'last_checked': profile['last_checked'],
            'new_items_count': len(new_items),
            'new_items': new_items,
            'notification_preferences': profile['notification_preferences']
        }
    
    async def cleanup_old_notifications(self, days: int = 30) -> None:
        """Clean up old notifications from history.
        
        Args:
            days: Number of days to keep notifications (default: 30)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        self.notification_history = {
            k: v for k, v in self.notification_history.items()
            if v > cutoff_date
        } 