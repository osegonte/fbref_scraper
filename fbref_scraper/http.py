"""
HTTP client module for FBref scraper.
"""
import time
import logging
from typing import Optional, Dict, Any

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class RateLimitedHTTPClient:
    """
    HTTP client with rate limiting for FBref.
    """
    
    def __init__(self, rate_limit_delay: float = 3.0, max_retries: int = 3):
        """
        Initialize the HTTP client.
        
        Args:
            rate_limit_delay: Delay between requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.last_request_time = 0
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with appropriate headers."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        return session
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a GET request with rate limiting and retries.
        
        Args:
            url: URL to request
            params: Query parameters
            
        Returns:
            Response object
            
        Raises:
            RequestException: If the request fails after all retries
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                self._respect_rate_limit()
                response = self.session.get(url, params=params)
                response.raise_for_status()
                self.last_request_time = time.time()
                return response
            except RequestException as e:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                logger.warning(f"Request to {url} failed (attempt {retries}/{self.max_retries}): {e}")
                
                if retries > self.max_retries:
                    logger.error(f"Maximum retries reached for {url}")
                    raise
                
                if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                    # Rate limit exceeded
                    wait_time = max(wait_time, 60)  # Wait at least 60 seconds
                    logger.warning(f"Rate limit exceeded, waiting for {wait_time} seconds")
                
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    def _respect_rate_limit(self) -> None:
        """Ensure we don't exceed the rate limit."""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)