from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .base_agent import BaseAgent
from .data_source_agent import DataSourceAgent

class MonitoringAgent(BaseAgent):
    """Agent responsible for monitoring and detecting new content of interest."""
    
    def __init__(self):
        super().__init__(agent_type="monitoring")
        self.data_source_agent = DataSourceAgent()
        self.last_check_time = datetime.now()
        self.interest_profiles = {}  # Store user interest profiles
        self.notification_history = {}  # Track what's been notified
        self.webhooks = {}  # Store webhook configurations
        self.email_config = None  # Store email configuration
        
    async def configure_email(self, config: Dict[str, str]) -> None:
        """Configure email notifications.
        
        Args:
            config: Dictionary containing email configuration
                   {
                       'smtp_server': 'smtp.example.com',
                       'smtp_port': 587,
                       'username': 'user@example.com',
                       'password': 'password',
                       'from_email': 'notifications@example.com'
                   }
        """
        self.email_config = config
        
    async def add_webhook(self, webhook_id: str, config: Dict[str, Any]) -> None:
        """Add a webhook configuration.
        
        Args:
            webhook_id: Unique identifier for the webhook
            config: Dictionary containing webhook configuration
                   {
                       'url': 'https://example.com/webhook',
                       'secret': 'webhook_secret',
                       'events': ['new_book', 'new_author'],
                       'headers': {'Authorization': 'Bearer token'}
                   }
        """
        self.webhooks[webhook_id] = config
        
    async def send_notification(self, profile_id: int, items: List[Dict[str, Any]]) -> None:
        """Send notifications for new items.
        
        Args:
            profile_id: ID of the interest profile
            items: List of new items to notify about
        """
        if profile_id not in self.interest_profiles:
            return
            
        profile = self.interest_profiles[profile_id]
        prefs = profile['notification_preferences']
        
        # Send email notification
        if 'email' in prefs['channels'] and self.email_config:
            await self._send_email_notification(profile, items)
            
        # Send webhook notifications
        if 'webhook' in prefs['channels']:
            await self._send_webhook_notifications(profile, items)
            
    async def _send_email_notification(self, profile: Dict[str, Any], items: List[Dict[str, Any]]) -> None:
        """Send email notification.
        
        Args:
            profile: Interest profile
            items: List of new items
        """
        if not self.email_config:
            return
            
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from_email']
        msg['To'] = profile['notification_preferences'].get('email_address', '')
        msg['Subject'] = f"New items matching {profile['name']}"
        
        # Create email body
        body = f"New items matching your interest profile '{profile['name']}':\n\n"
        for item in items:
            body += f"- {item.get('title', 'Unknown')} by {item.get('author', 'Unknown')}\n"
            if 'url' in item:
                body += f"  URL: {item['url']}\n"
            body += "\n"
            
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending email notification: {e}")
            
    async def _send_webhook_notifications(self, profile: Dict[str, Any], items: List[Dict[str, Any]]) -> None:
        """Send webhook notifications.
        
        Args:
            profile: Interest profile
            items: List of new items
        """
        for webhook_id, config in self.webhooks.items():
            # Check if webhook is interested in these events
            if not any(event in config['events'] for event in ['new_book', 'new_author']):
                continue
                
            payload = {
                'profile_id': profile['profile_id'],
                'profile_name': profile['name'],
                'items': items,
                'timestamp': datetime.now().isoformat()
            }
            
            headers = config.get('headers', {})
            if 'secret' in config:
                headers['X-Webhook-Secret'] = config['secret']
                
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        config['url'],
                        json=payload,
                        headers=headers
                    ) as response:
                        if response.status != 200:
                            logging.error(f"Webhook {webhook_id} returned status {response.status}")
            except Exception as e:
                logging.error(f"Error sending webhook {webhook_id}: {e}")
                
    def _matches_profile(self, item: Dict[str, Any], profile: Dict[str, Any]) -> bool:
        """Enhanced profile matching with multiple criteria.
        
        Args:
            item: Item to check
            profile: Interest profile to match against
            
        Returns:
            True if item matches profile criteria
        """
        # Check keywords with fuzzy matching
        if any(keyword.lower() in str(item).lower() 
               for keyword in profile['keywords']):
            return True
            
        # Check authors with exact matching
        if 'author' in item and item['author'] in profile['authors']:
            return True
            
        # Check publication year range if specified
        if 'year_range' in profile:
            min_year, max_year = profile['year_range']
            if 'year' in item and min_year <= item['year'] <= max_year:
                return True
                
        # Check genres if specified
        if 'genres' in profile and 'genres' in item:
            if any(genre in item['genres'] for genre in profile['genres']):
                return True
                
        # Check ratings if specified
        if 'min_rating' in profile and 'rating' in item:
            if item['rating'] >= profile['min_rating']:
                return True
                
        return False
        
    async def cleanup_old_notifications(self, days: int = 30) -> None:
        """Clean up old notifications and optimize storage.
        
        Args:
            days: Number of days to keep notifications (default: 30)
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clean up notification history
        self.notification_history = {
            k: v for k, v in self.notification_history.items()
            if v > cutoff_date
        }
        
        # Clean up old webhook configurations
        self.webhooks = {
            k: v for k, v in self.webhooks.items()
            if v.get('last_used', datetime.now()) > cutoff_date
        }
        
        # Optimize interest profiles
        for profile_id, profile in self.interest_profiles.items():
            if 'last_checked' in profile and profile['last_checked'] < cutoff_date:
                # Archive inactive profiles
                profile['status'] = 'archived'
                
    async def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics.
        
        Returns:
            Dictionary containing monitoring statistics
        """
        return {
            'total_profiles': len(self.interest_profiles),
            'active_profiles': sum(1 for p in self.interest_profiles.values() 
                                 if p.get('status') != 'archived'),
            'total_notifications': len(self.notification_history),
            'webhook_count': len(self.webhooks),
            'last_check_time': self.last_check_time,
            'source_stats': {
                'isfdb': sum(1 for k in self.notification_history.keys() 
                            if k.startswith('isfdb_')),
                'goodreads': sum(1 for k in self.notification_history.keys() 
                               if k.startswith('goodreads_')),
                'wikipedia': sum(1 for k in self.notification_history.keys() 
                               if k.startswith('wikipedia_'))
            }
        }
    
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