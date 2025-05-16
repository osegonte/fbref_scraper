"""
HTML parsing functions for FBref scraper.
"""
import re
import logging
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from bs4 import BeautifulSoup

from fbref_scraper.models import Match, Team

logger = logging.getLogger(__name__)


def parse_team_search_results(html: str) -> List[Dict[str, str]]:
    """
    Parse the search results page to find teams.
    
    Args:
        html: HTML content of the search results page
        
    Returns:
        List of dictionaries with team information
    """
    soup = BeautifulSoup(html, 'lxml')
    results = []
    
    # Find the search results section
    search_results = soup.select('.search-item-name')
    
    for result in search_results:
        link = result.find('a')
        if link and '/squads/' in link.get('href', ''):
            team_url = 'https://fbref.com' + link['href']
            team_name = link.text.strip()
            
            # Extract the team ID from the URL
            match = re.search(r'/squads/([^/]+)/', team_url)
            team_id = match.group(1) if match else None
            
            if team_id:
                results.append({
                    'name': team_name,
                    'url': team_url,
                    'id': team_id
                })
    
    return results


def parse_team_page(html: str) -> Dict[str, str]:
    """
    Parse the team page to extract basic information and links.
    
    Args:
        html: HTML content of the team page
        
    Returns:
        Dictionary with team information
    """
    soup = BeautifulSoup(html, 'lxml')
    team_info = {}
    
    # Get team name
    team_name_elem = soup.select_one('h1[itemprop="name"]')
    if team_name_elem:
        team_info['name'] = team_name_elem.text.strip()
    
    # Get matchlogs link
    matchlogs_link = None
    for link in soup.select('#inner_nav a'):
        if 'Match Logs' in link.text:
            matchlogs_link = 'https://fbref.com' + link['href']
            break
    
    team_info['matchlogs_url'] = matchlogs_link
    
    return team_info


def parse_match_logs(html: str, num_matches: int = 7) -> List[Match]:
    """
    Parse the match logs page to extract match data.
    
    Args:
        html: HTML content of the match logs page
        num_matches: Number of recent matches to extract
        
    Returns:
        List of Match objects
    """
    soup = BeautifulSoup(html, 'lxml')
    matches = []
    
    # Find all match tables
    match_tables = soup.select('table.stats_table')
    
    if not match_tables:
        logger.warning("No match tables found on the page")
        return matches
    
    # Use the first table (most recent matches)
    table = match_tables[0]
    
    # Find all rows in the table body
    rows = table.select('tbody tr')
    
    # Filter out non-match rows
    match_rows = [row for row in rows if not row.get('class') or 'spacer' not in row['class']]
    
    # Process only the most recent 'num_matches'
    for row in match_rows[:num_matches]:
        try:
            match = _parse_match_row(row)
            if match:
                matches.append(match)
        except Exception as e:
            logger.error(f"Error parsing match row: {e}")
    
    return matches


def _parse_match_row(row) -> Optional[Match]:
    """
    Parse a single match row from the match logs table.
    
    Args:
        row: BeautifulSoup element representing a table row
        
    Returns:
        Match object or None if the row cannot be parsed
    """
    # Skip if it's not a match row
    if not row.select_one('td[data-stat="date"]'):
        return None
    
    # Extract match date
    date_cell = row.select_one('td[data-stat="date"]')
    if not date_cell or not date_cell.text.strip():
        return None
    
    date_str = date_cell.text.strip()
    match_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Extract opponent
    opponent_cell = row.select_one('td[data-stat="opponent"]')
    opponent = opponent_cell.text.strip() if opponent_cell else "Unknown"
    
    # Extract venue
    venue_cell = row.select_one('td[data-stat="venue"]')
    venue = venue_cell.text.strip() if venue_cell else "Unknown"
    
    # Extract score
    goals_for = _extract_cell_value(row, 'goals_for', int, 0)
    goals_against = _extract_cell_value(row, 'goals_against', int, 0)
    
    # Extract shot data
    shots = _extract_cell_value(row, 'shots', int, 0)
    shots_on_target = _extract_cell_value(row, 'shots_on_target', int, 0)
    # Calculate shots off target as total shots minus shots on target
    shots_off_target = shots - shots_on_target
    
    # Extract possession
    possession_pct = _extract_cell_value(row, 'possession', float, 0.0, transform=lambda x: float(x.rstrip('%')))
    
    # Extract pass data
    passes_completed = _extract_cell_value(row, 'passes_completed', int, 0)
    pass_accuracy_pct = _extract_cell_value(row, 'passes_pct', float, 0.0, transform=lambda x: float(x.rstrip('%')))
    
    # Extract corner data
    corners_for = _extract_cell_value(row, 'corners', int, None)
    corners_against = _extract_cell_value(row, 'corners_against', int, None)
    
    # Extract foul data
    fouls_committed = _extract_cell_value(row, 'fouls', int, None)
    fouls_suffered = _extract_cell_value(row, 'fouled', int, None)
    
    return Match(
        date=match_date,
        opponent=opponent,
        venue=venue,
        goals_for=goals_for,
        goals_against=goals_against,
        shots=shots,
        shots_on_target=shots_on_target,
        shots_off_target=shots_off_target,
        possession_pct=possession_pct,
        passes_completed=passes_completed,
        pass_accuracy_pct=pass_accuracy_pct,
        corners_for=corners_for,
        corners_against=corners_against,
        fouls_committed=fouls_committed,
        fouls_suffered=fouls_suffered
    )


def _extract_cell_value(row, stat_name: str, data_type: type, default_value: Any, transform=None):
    """
    Helper function to extract and convert a cell value.
    
    Args:
        row: BeautifulSoup element representing a table row
        stat_name: Name of the statistic to extract
        data_type: Type to convert the value to
        default_value: Default value if extraction fails
        transform: Optional function to transform the value before type conversion
        
    Returns:
        Extracted and converted value, or default_value if extraction fails
    """
    cell = row.select_one(f'td[data-stat="{stat_name}"]')
    if not cell or not cell.text.strip():
        return default_value
    
    value = cell.text.strip()
    
    if transform:
        try:
            value = transform(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to transform value '{value}' for {stat_name}")
            return default_value
    
    try:
        return data_type(value)
    except (ValueError, TypeError):
        logger.warning(f"Failed to convert '{value}' to {data_type.__name__} for {stat_name}")
        return default_value