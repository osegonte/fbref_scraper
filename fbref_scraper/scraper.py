"""
Main scraper module for FBref, now with Selenium support to bypass blocking.
"""
import re
import logging
from typing import Optional, List, Tuple, Dict, Any
from urllib.parse import urljoin, urlparse

from fbref_scraper.http import RateLimitedHTTPClient
from fbref_scraper.parser import (
    parse_team_search_results,
    parse_team_page,
    parse_match_logs
)
from fbref_scraper.models import Team, Match
from fbref_scraper.mock_data import get_mock_team

logger = logging.getLogger(__name__)

class FBrefScraper:
    """
    Scraper for FBref soccer statistics.
    """
    
    BASE_URL = "https://fbref.com"
    SEARCH_URL = "https://fbref.com/en/search/search.fcgi"
    
    # Known team IDs to use as a fallback
    KNOWN_TEAMS = {
        "manchester city": {
            "id": "b8fd03ef",
            "name": "Manchester City",
            "matchlogs_url": "/en/squads/b8fd03ef/matchlogs/all_comps/Manchester-City-Scores-and-Fixtures-All-Competitions"
        },
        "manchester united": {
            "id": "19538871",
            "name": "Manchester United",
            "matchlogs_url": "/en/squads/19538871/matchlogs/all_comps/Manchester-United-Scores-and-Fixtures-All-Competitions"
        },
        "liverpool": {
            "id": "822bd0ba",
            "name": "Liverpool",
            "matchlogs_url": "/en/squads/822bd0ba/matchlogs/all_comps/Liverpool-Scores-and-Fixtures-All-Competitions"
        },
        "arsenal": {
            "id": "18bb7c10",
            "name": "Arsenal",
            "matchlogs_url": "/en/squads/18bb7c10/matchlogs/all_comps/Arsenal-Scores-and-Fixtures-All-Competitions"
        },
        "chelsea": {
            "id": "cff3d9bb",
            "name": "Chelsea",
            "matchlogs_url": "/en/squads/cff3d9bb/matchlogs/all_comps/Chelsea-Scores-and-Fixtures-All-Competitions"
        },
        "tottenham": {
            "id": "361ca564",
            "name": "Tottenham Hotspur",
            "matchlogs_url": "/en/squads/361ca564/matchlogs/all_comps/Tottenham-Hotspur-Scores-and-Fixtures-All-Competitions"
        },
        "barcelona": {
            "id": "206d90db",
            "name": "Barcelona",
            "matchlogs_url": "/en/squads/206d90db/matchlogs/all_comps/Barcelona-Scores-and-Fixtures-All-Competitions"
        },
        "real madrid": {
            "id": "53a2f082",
            "name": "Real Madrid",
            "matchlogs_url": "/en/squads/53a2f082/matchlogs/all_comps/Real-Madrid-Scores-and-Fixtures-All-Competitions"
        }
    }
    
    def __init__(self, rate_limit_delay: float = 5.0, use_mock_data: bool = True):
        """
        Initialize the scraper.
        
        Args:
            rate_limit_delay: Delay between requests in seconds
            use_mock_data: Whether to use mock data when scraping fails
        """
        self.http_client = RateLimitedHTTPClient(rate_limit_delay=rate_limit_delay)
        self.use_mock_data = use_mock_data
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if hasattr(self, 'http_client') and self.http_client:
            self.http_client.close()
    
    def search_team(self, team_name: str) -> List[dict]:
        """
        Search for a team by name.
        
        Args:
            team_name: Name of the team to search for
            
        Returns:
            List of dictionaries with team information
        """
        logger.info(f"Searching for team: {team_name}")
        
        # First check if it's in our known teams dictionary
        team_key = team_name.lower()
        if team_key in self.KNOWN_TEAMS or any(key in team_key for key in self.KNOWN_TEAMS):
            for key, team_data in self.KNOWN_TEAMS.items():
                if key == team_key or key in team_key:
                    logger.info(f"Found team in known teams list: {team_data['name']}")
                    return [{
                        'name': team_data['name'],
                        'id': team_data['id'],
                        'url': f"{self.BASE_URL}/en/squads/{team_data['id']}/{team_data['name'].replace(' ', '-')}-Stats"
                    }]
        
        # Fallback to search if not in known teams
        params = {
            "search": team_name,
        }
        
        try:
            response = self.http_client.get(self.SEARCH_URL, params=params)
            return parse_team_search_results(response.text)
        except Exception as e:
            logger.warning(f"Search failed, error: {e}")
            return []
    
    def get_team_by_url(self, url: str) -> Optional[Team]:
        """
        Get a team by its FBref URL.
        
        Args:
            url: FBref team URL
            
        Returns:
            Team object or None if the team is not found
        """
        logger.info(f"Getting team from URL: {url}")
        
        # Ensure we're working with a team URL
        if '/squads/' not in url:
            logger.error(f"Invalid team URL: {url}")
            return None
        
        # Extract team ID from URL
        match = re.search(r'/squads/([^/]+)/', url)
        if not match:
            logger.error(f"Could not extract team ID from URL: {url}")
            return None
        
        team_id = match.group(1)
        
        # Check if it's in our known teams
        for key, team_data in self.KNOWN_TEAMS.items():
            if team_data['id'] == team_id:
                logger.info(f"Found team in known teams list: {team_data['name']}")
                return Team(name=team_data['name'], fbref_id=team_id)
        
        # Get the team page
        try:
            response = self.http_client.get(url)
            team_info = parse_team_page(response.text)
            
            if not team_info.get('name'):
                logger.error(f"Could not extract team name from page: {url}")
                return None
            
            return Team(name=team_info['name'], fbref_id=team_id)
        except Exception as e:
            logger.warning(f"Failed to get team from URL, error: {e}")
            # Fallback to a generic team name based on the URL
            team_name = url.split('/')[-1].replace('-Stats', '').replace('-', ' ')
            return Team(name=team_name, fbref_id=team_id)
    
    def get_team_by_name(self, team_name: str) -> Optional[Team]:
        """
        Get a team by its name.
        
        Args:
            team_name: Name of the team
            
        Returns:
            Team object or None if the team is not found
        """
        logger.info(f"Getting team by name: {team_name}")
        
        # First, check if it's in our known teams dictionary
        team_key = team_name.lower()
        for key, team_data in self.KNOWN_TEAMS.items():
            if key == team_key or key in team_key or team_key in key:
                logger.info(f"Found team in known teams list: {team_data['name']}")
                return Team(name=team_data['name'], fbref_id=team_data['id'])
        
        # Fallback to search
        search_results = self.search_team(team_name)
        
        if not search_results:
            logger.error(f"No teams found with name: {team_name}")
            return None
        
        # Use the first result
        team_info = search_results[0]
        logger.info(f"Selected team: {team_info['name']} ({team_info.get('url', '')})")
        
        return Team(name=team_info['name'], fbref_id=team_info['id'])
    
    def get_match_logs(self, team: Team, num_matches: int = 7) -> List[Match]:
        """
        Get match logs for a team.
        
        Args:
            team: Team object
            num_matches: Number of recent matches to retrieve
            
        Returns:
            List of Match objects
        """
        logger.info(f"Getting match logs for team: {team.name}")
        
        # Try with real data first
        try:
            # Check if it's in our known teams dictionary first
            team_key = team.name.lower()
            matchlogs_url = None
            
            for key, team_data in self.KNOWN_TEAMS.items():
                if team_data['id'] == team.fbref_id or key == team_key or key in team_key:
                    matchlogs_url = self.BASE_URL + team_data['matchlogs_url']
                    logger.info(f"Using known matchlogs URL: {matchlogs_url}")
                    break
            
            # If not found in known teams, get the team page to find the match logs URL
            if not matchlogs_url:
                team_url = f"{self.BASE_URL}/en/squads/{team.fbref_id}/{team.name.replace(' ', '-')}-Stats"
                response = self.http_client.get(team_url)
                team_info = parse_team_page(response.text)
                
                if not team_info.get('matchlogs_url'):
                    # Try a direct URL as a fallback
                    matchlogs_url = f"{self.BASE_URL}/en/squads/{team.fbref_id}/matchlogs/all_comps/{team.name.replace(' ', '-')}-Scores-and-Fixtures-All-Competitions"
                    logger.info(f"No matchlogs URL found, trying direct URL: {matchlogs_url}")
                else:
                    matchlogs_url = team_info['matchlogs_url']
                    logger.info(f"Found matchlogs URL: {matchlogs_url}")
            
            # Get the match logs page using Selenium (which should bypass blocking)
            response = self.http_client.get(matchlogs_url)
            matches = parse_match_logs(response.text, num_matches=num_matches)
            
            logger.info(f"Found {len(matches)} matches for team: {team.name}")
            return matches
            
        except Exception as e:
            logger.error(f"Failed to get match logs: {e}")
            
            # If we're using mock data and real data failed, return mock data
            if self.use_mock_data:
                logger.info(f"Using mock data for team: {team.name}")
                mock_team = get_mock_team(team.name, num_matches)
                if mock_team and mock_team.matches:
                    logger.info(f"Found {len(mock_team.matches)} mock matches for team: {team.name}")
                    return mock_team.matches
            
            return []
    
    def fetch_team_data(self, team_identifier: str, is_url: bool = False, num_matches: int = 7) -> Optional[Team]:
        """
        Fetch all data for a team.
        
        Args:
            team_identifier: Team name or URL
            is_url: Whether the identifier is a URL
            num_matches: Number of recent matches to retrieve
            
        Returns:
            Team object with matches or None if the team is not found
        """
        # First try to get data with real scraping
        team = None
        if is_url:
            team = self.get_team_by_url(team_identifier)
        else:
            team = self.get_team_by_name(team_identifier)
        
        if not team:
            return None
        
        # Get the match logs
        matches = self.get_match_logs(team, num_matches=num_matches)
        
        if not matches and self.use_mock_data:
            # If we didn't get any matches and we're using mock data, 
            # try to get a mock team directly
            logger.info(f"No matches found with scraping, trying mock data for: {team.name}")
            mock_team = get_mock_team(team.name, num_matches)
            if mock_team:
                return mock_team
        
        team.matches = matches
        return team