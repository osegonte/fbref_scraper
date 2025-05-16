"""
HTTP client module for FBref scraper with better error handling.
"""
import time
import random
import logging
from typing import Optional, Dict, Any, Tuple

import requests
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

# List of realistic user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1',
]

class RateLimitedHTTPClient:
    """
    HTTP client with rate limiting for FBref, using Selenium to bypass blocks.
    """
    
    def __init__(self, rate_limit_delay: float = 5.0, max_retries: int = 3):
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
        self.driver = None
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with appropriate headers."""
        session = requests.Session()
        
        # Set a random user agent
        user_agent = random.choice(USER_AGENTS)
        
        # Set headers that mimic a real browser
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',  # Pretend to come from Google
        })
        
        return session
    
    def _get_selenium_driver(self) -> webdriver.Chrome:
        """
        Get or create a Selenium WebDriver.
        
        Returns:
            Chrome WebDriver instance
        """
        if self.driver is None:
            logger.info("Initializing Selenium WebDriver...")
            
            try:
                # Set up Chrome options
                options = Options()
                options.add_argument("--headless")  # Run in headless mode (no UI)
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation
                
                # Use a random user agent
                user_agent = random.choice(USER_AGENTS)
                options.add_argument(f"--user-agent={user_agent}")
                
                # Add more realistic browser settings
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Initialize the Chrome WebDriver with webdriver-manager
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
                # Set page load timeout
                self.driver.set_page_load_timeout(30)
                
                # Execute JavaScript to hide Selenium's presence
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                logger.info("WebDriver initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing WebDriver: {e}")
                raise
        
        return self.driver
    
    def _rotate_user_agent(self):
        """Rotate the user agent to avoid detection."""
        self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
        logger.debug(f"Rotated user agent to: {self.session.headers['User-Agent']}")
    
    def _respect_rate_limit(self, jitter_factor: float = 1.0) -> None:
        """
        Ensure we don't exceed the rate limit.
        
        Args:
            jitter_factor: Factor to apply to the rate limit delay for jitter
        """
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            adjusted_delay = self.rate_limit_delay * jitter_factor
            
            if elapsed < adjusted_delay:
                sleep_time = adjusted_delay - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
    
    def _is_error_page(self, html_content: str) -> Tuple[bool, str]:
        """
        Check if the response contains an error page.
        
        Args:
            html_content: HTML content of the page
            
        Returns:
            Tuple of (is_error, error_type)
        """
        if "500 error" in html_content:
            return True, "server_error"
        elif "403 Forbidden" in html_content or "Access Denied" in html_content:
            return True, "forbidden"
        elif "404 Not Found" in html_content:
            return True, "not_found"
        elif "Rate Limit Exceeded" in html_content:
            return True, "rate_limit"
        
        return False, ""
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a GET request with rate limiting and retries, using Selenium for blocked sites.
        
        Args:
            url: URL to request
            params: Query parameters
            
        Returns:
            Response object
            
        Raises:
            RequestException: If the request fails after all retries
        """
        # Add query parameters to URL if provided
        full_url = url
        if params:
            param_strings = []
            for key, value in params.items():
                param_strings.append(f"{key}={value}")
            full_url = f"{url}?{'&'.join(param_strings)}"
        
        retries = 0
        
        # Add a small jitter to the delay to make requests look more human
        jitter = lambda: random.uniform(0.5, 1.5)
        
        while retries <= self.max_retries:
            try:
                # Respect rate limit with jitter
                self._respect_rate_limit(jitter_factor=jitter())
                
                # Rotate user agent on retry
                if retries > 0:
                    self._rotate_user_agent()
                
                # First try with normal requests
                if retries == 0:
                    logger.debug(f"Making request with requests to {full_url}")
                    response = self.session.get(full_url)
                    
                    # If we got a 403 or 429 or 500, switch to Selenium on next try
                    if response.status_code in (403, 429, 500):
                        logger.info(f"Received status code {response.status_code}, will try with Selenium next")
                        retries += 1
                        continue
                    
                    # Check if response contains an error page
                    is_error, error_type = self._is_error_page(response.text)
                    if is_error:
                        logger.warning(f"Detected {error_type} page, will try with Selenium next")
                        retries += 1
                        continue
                    
                    response.raise_for_status()
                    self.last_request_time = time.time()
                    return response
                
                # If normal request failed or this is a retry, use Selenium
                logger.info(f"Making request with Selenium to {full_url}")
                driver = self._get_selenium_driver()
                
                # Navigate to the URL
                driver.get(full_url)
                
                # Wait for the page to load
                try:
                    # First wait for the body to be present
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Then wait a bit more for dynamic content
                    time.sleep(random.uniform(2, 4))
                    
                    # Check if we got an error page
                    page_source = driver.page_source
                    is_error, error_type = self._is_error_page(page_source)
                    
                    if is_error:
                        logger.warning(f"Selenium encountered {error_type} page")
                        if error_type == "server_error" and retries >= self.max_retries:
                            # If we've reached max retries and it's a server error,
                            # return the response anyway so the caller can handle it
                            logger.error(f"Maximum retries reached with server error, returning anyway")
                            break
                        else:
                            # For other errors, or if we haven't reached max retries, try again
                            retries += 1
                            wait_time = 2 ** retries + random.uniform(2, 5)
                            logger.info(f"Retrying in {wait_time:.2f} seconds...")
                            time.sleep(wait_time)
                            continue
                    
                except TimeoutException:
                    logger.warning("Timeout waiting for page to load")
                    if retries >= self.max_retries:
                        logger.error("Maximum retries reached")
                        raise
                    retries += 1
                    continue
                
                # Get the page source
                html = driver.page_source
                
                # Create a mock response object
                response = requests.Response()
                response.status_code = 200
                response._content = html.encode('utf-8')
                response.url = full_url
                
                self.last_request_time = time.time()
                
                # Initial delay before next request
                time.sleep(random.uniform(1.0, 2.0))
                
                return response
            
            except (RequestException, WebDriverException) as e:
                retries += 1
                wait_time = 2 ** retries + random.uniform(0, 1)  # Exponential backoff with jitter
                logger.warning(f"Request to {full_url} failed (attempt {retries}/{self.max_retries}): {e}")
                
                if retries > self.max_retries:
                    logger.error(f"Maximum retries reached for {full_url}")
                    raise
                
                # Handle specific error types
                if isinstance(e, RequestException) and hasattr(e, 'response') and e.response:
                    if e.response.status_code == 403:
                        # Access forbidden - likely detecting scraping
                        logger.warning(f"Access forbidden (403). Trying with Selenium next time.")
                    elif e.response.status_code == 429:
                        # Rate limit exceeded
                        wait_time = max(wait_time, 60)  # Wait at least 60 seconds
                        logger.warning(f"Rate limit exceeded, waiting for {wait_time} seconds")
                    elif e.response.status_code == 500:
                        # Server error - might be temporary
                        logger.warning(f"Server error (500). This could be temporary.")
                        wait_time = max(wait_time, 30)  # Wait at least 30 seconds
                
                logger.info(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        # If all retries failed but we have some response from Selenium,
        # return it anyway and let the caller handle it
        return response
    
    def close(self):
        """Close the WebDriver if it exists."""
        if self.driver:
            try:
                logger.info("Closing WebDriver...")
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")