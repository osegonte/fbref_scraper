"""
Mock data provider for when web scraping is blocked.
"""
from datetime import date
from typing import List, Optional

from fbref_scraper.models import Team, Match

# Some realistic match data for testing
TEAM_DATA = {
    "manchester city": {
        "name": "Manchester City",
        "fbref_id": "b8fd03ef",
        "matches": [
            Match(
                date=date(2025, 5, 10),
                opponent="Arsenal",
                venue="Home",
                goals_for=3,
                goals_against=1,
                shots=15,
                shots_on_target=8,
                shots_off_target=7,
                possession_pct=60.2,
                passes_completed=500,
                pass_accuracy_pct=88.5,
                corners_for=7,
                corners_against=3,
                fouls_committed=10,
                fouls_suffered=12
            ),
            Match(
                date=date(2025, 5, 3),
                opponent="Liverpool",
                venue="Away",
                goals_for=2,
                goals_against=2,
                shots=12,
                shots_on_target=5,
                shots_off_target=7,
                possession_pct=55.8,
                passes_completed=450,
                pass_accuracy_pct=85.0,
                corners_for=6,
                corners_against=4,
                fouls_committed=8,
                fouls_suffered=9
            ),
            Match(
                date=date(2025, 4, 29),
                opponent="Manchester United",
                venue="Home",
                goals_for=4,
                goals_against=0,
                shots=18,
                shots_on_target=10,
                shots_off_target=8,
                possession_pct=65.3,
                passes_completed=550,
                pass_accuracy_pct=90.2,
                corners_for=8,
                corners_against=2,
                fouls_committed=7,
                fouls_suffered=10
            ),
            Match(
                date=date(2025, 4, 22),
                opponent="Tottenham",
                venue="Away",
                goals_for=1,
                goals_against=1,
                shots=14,
                shots_on_target=6,
                shots_off_target=8,
                possession_pct=58.5,
                passes_completed=480,
                pass_accuracy_pct=87.5,
                corners_for=5,
                corners_against=5,
                fouls_committed=9,
                fouls_suffered=8
            ),
            Match(
                date=date(2025, 4, 18),
                opponent="Chelsea",
                venue="Home",
                goals_for=2,
                goals_against=0,
                shots=16,
                shots_on_target=9,
                shots_off_target=7,
                possession_pct=62.7,
                passes_completed=520,
                pass_accuracy_pct=89.8,
                corners_for=7,
                corners_against=3,
                fouls_committed=6,
                fouls_suffered=11
            ),
            Match(
                date=date(2025, 4, 12),
                opponent="Newcastle",
                venue="Away",
                goals_for=3,
                goals_against=2,
                shots=15,
                shots_on_target=8,
                shots_off_target=7,
                possession_pct=59.6,
                passes_completed=490,
                pass_accuracy_pct=86.4,
                corners_for=6,
                corners_against=4,
                fouls_committed=8,
                fouls_suffered=10
            ),
            Match(
                date=date(2025, 4, 6),
                opponent="Leicester",
                venue="Home",
                goals_for=5,
                goals_against=0,
                shots=20,
                shots_on_target=12,
                shots_off_target=8,
                possession_pct=68.2,
                passes_completed=580,
                pass_accuracy_pct=92.0,
                corners_for=9,
                corners_against=1,
                fouls_committed=5,
                fouls_suffered=8
            )
        ]
    },
    "manchester united": {
        "name": "Manchester United",
        "fbref_id": "19538871",
        "matches": [
            Match(
                date=date(2025, 5, 10),
                opponent="Chelsea",
                venue="Home",
                goals_for=2,
                goals_against=1,
                shots=14,
                shots_on_target=7,
                shots_off_target=7,
                possession_pct=54.3,
                passes_completed=460,
                pass_accuracy_pct=84.2,
                corners_for=6,
                corners_against=4,
                fouls_committed=11,
                fouls_suffered=9
            ),
            Match(
                date=date(2025, 5, 3),
                opponent="Arsenal",
                venue="Away",
                goals_for=1,
                goals_against=2,
                shots=10,
                shots_on_target=4,
                shots_off_target=6,
                possession_pct=45.7,
                passes_completed=400,
                pass_accuracy_pct=80.5,
                corners_for=4,
                corners_against=7,
                fouls_committed=12,
                fouls_suffered=8
            ),
            Match(
                date=date(2025, 4, 29),
                opponent="Manchester City",
                venue="Away",
                goals_for=0,
                goals_against=4,
                shots=8,
                shots_on_target=2,
                shots_off_target=6,
                possession_pct=34.7,
                passes_completed=320,
                pass_accuracy_pct=75.8,
                corners_for=2,
                corners_against=8,
                fouls_committed=10,
                fouls_suffered=7
            ),
            Match(
                date=date(2025, 4, 22),
                opponent="Newcastle",
                venue="Home",
                goals_for=2,
                goals_against=0,
                shots=15,
                shots_on_target=8,
                shots_off_target=7,
                possession_pct=58.2,
                passes_completed=470,
                pass_accuracy_pct=85.3,
                corners_for=7,
                corners_against=3,
                fouls_committed=8,
                fouls_suffered=10
            ),
            Match(
                date=date(2025, 4, 18),
                opponent="Liverpool",
                venue="Away",
                goals_for=1,
                goals_against=3,
                shots=9,
                shots_on_target=3,
                shots_off_target=6,
                possession_pct=42.5,
                passes_completed=380,
                pass_accuracy_pct=79.6,
                corners_for=3,
                corners_against=8,
                fouls_committed=14,
                fouls_suffered=7
            ),
            Match(
                date=date(2025, 4, 12),
                opponent="Tottenham",
                venue="Home",
                goals_for=2,
                goals_against=2,
                shots=13,
                shots_on_target=6,
                shots_off_target=7,
                possession_pct=51.4,
                passes_completed=440,
                pass_accuracy_pct=83.2,
                corners_for=5,
                corners_against=5,
                fouls_committed=9,
                fouls_suffered=9
            ),
            Match(
                date=date(2025, 4, 6),
                opponent="Aston Villa",
                venue="Away",
                goals_for=1,
                goals_against=0,
                shots=12,
                shots_on_target=5,
                shots_off_target=7,
                possession_pct=53.6,
                passes_completed=450,
                pass_accuracy_pct=82.8,
                corners_for=6,
                corners_against=4,
                fouls_committed=10,
                fouls_suffered=8
            )
        ]
    },
    "liverpool": {
        "name": "Liverpool",
        "fbref_id": "822bd0ba",
        "matches": [
            # Add similar match data as above
            # ...
        ]
    }
}

def get_mock_team(team_name: str, num_matches: int = 7) -> Optional[Team]:
    """
    Get mock data for a team.
    
    Args:
        team_name: Name of the team
        num_matches: Number of matches to return
        
    Returns:
        Team object with mock matches or None if not found
    """
    team_key = team_name.lower()
    
    # Try to find an exact match first
    if team_key in TEAM_DATA:
        team_data = TEAM_DATA[team_key]
        team = Team(name=team_data["name"], fbref_id=team_data["fbref_id"])
        team.matches = team_data["matches"][:num_matches]
        return team
    
    # Try to find a partial match
    for key, team_data in TEAM_DATA.items():
        if key in team_key or team_key in key:
            team = Team(name=team_data["name"], fbref_id=team_data["fbref_id"])
            team.matches = team_data["matches"][:num_matches]
            return team
    
    return None