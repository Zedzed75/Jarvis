"""
News API Client implementation for Jarvis

This module provides an implementation for news service APIs,
following the clean architecture patterns.
"""

import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger('jarvis.infrastructure.apis.news')

class NewsAPIClient:
    """
    Client for the NewsAPI.org service
    """
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: str):
        """
        Initialize the NewsAPI client
        
        Args:
            api_key: NewsAPI.org API key
        """
        self.api_key = api_key
        logger.info("NewsAPI client initialized")
    
    def get_top_headlines(self, country: str = 'us', category: Optional[str] = None, 
                        query: Optional[str] = None, page_size: int = 5) -> List[Dict[str, Any]]:
        """
        Get top headlines
        
        Args:
            country: 2-letter country code
            category: Category to filter by (business, entertainment, health, science, sports, technology)
            query: Keywords to search for
            page_size: Number of results to return
            
        Returns:
            List of news articles
        """
        try:
            url = f"{self.BASE_URL}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'country': country,
                'pageSize': min(page_size, 100)  # Max 100 as per API limits
            }
            
            if category:
                params['category'] = category
                
            if query:
                params['q'] = query
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                logger.debug(f"Retrieved {len(articles)} top headlines")
                return articles
            else:
                logger.error(f"Failed to get news: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return []
    
    def search_news(self, query: str, from_date: Optional[str] = None, 
                  to_date: Optional[str] = None, page_size: int = 5) -> List[Dict[str, Any]]:
        """
        Search for news articles
        
        Args:
            query: Keywords to search for
            from_date: Start date in format YYYY-MM-DD
            to_date: End date in format YYYY-MM-DD
            page_size: Number of results to return
            
        Returns:
            List of news articles
        """
        try:
            url = f"{self.BASE_URL}/everything"
            params = {
                'apiKey': self.api_key,
                'q': query,
                'pageSize': min(page_size, 100)  # Max 100 as per API limits
            }
            
            if from_date:
                params['from'] = from_date
                
            if to_date:
                params['to'] = to_date
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                logger.debug(f"Retrieved {len(articles)} articles for query: {query}")
                return articles
            else:
                logger.error(f"Failed to search news: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []