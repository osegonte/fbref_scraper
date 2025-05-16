"""
Command-line interface for FBref scraper.
"""
import sys
import csv
import logging
import argparse
from typing import List, Optional

from fbref_scraper.scraper import FBrefScraper
from fbref_scraper.models import Team, Match

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up the argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(description="Scrape match data from FBref")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--team", help="Name of the team to scrape")
    group.add_argument("--url", help="FBref URL of the team to scrape")
    
    parser.add_argument("--output", default="output.csv", help="Output CSV file path")
    parser.add_argument("--stdout", action="store_true", help="Output to stdout instead of file")
    parser.add_argument("--matches", type=int, default=7, help="Number of recent matches to retrieve")
    parser.add_argument("--rate-limit", type=float, default=3.0, help="Delay between requests in seconds")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    return parser

def write_to_csv(team: Team, output_path: str, to_stdout: bool = False) -> None:
    """
    Write match data to CSV.
    
    Args:
        team: Team object with matches
        output_path: Path to output CSV file
        to_stdout: Whether to output to stdout instead of file
    """
    if not team.matches:
        logger.error("No matches found")
        return
    
    # Prepare data for CSV
    fieldnames = [
        'date', 'opponent', 'venue', 'goals_for', 'goals_against',
        'shots', 'shots_on_target', 'shots_off_target', 'possession_pct',
        'passes_completed', 'pass_accuracy_pct', 'corners_for', 'corners_against',
        'fouls_committed', 'fouls_suffered'
    ]
    
    rows = [match.as_dict() for match in team.matches]
    
    if to_stdout:
        # Write to stdout
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    else:
        # Write to file
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        logger.info(f"CSV data written to {output_path}")

def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize scraper
        scraper = FBrefScraper(rate_limit_delay=args.rate_limit)
        
        # Fetch team data
        team = None
        if args.team:
            team = scraper.fetch_team_data(args.team, is_url=False, num_matches=args.matches)
        elif args.url:
            team = scraper.fetch_team_data(args.url, is_url=True, num_matches=args.matches)
        
        if not team:
            logger.error("Failed to find team")
            return 1
        
        # Check if we found any matches
        if not team.matches:
            logger.error(f"No matches found for team: {team.name}")
            return 1
        
        logger.info(f"Found {len(team.matches)} matches for team: {team.name}")
        
        # Write output
        write_to_csv(team, args.output, args.stdout)
        
        return 0
    
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())