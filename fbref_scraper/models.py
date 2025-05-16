"""
Data models for FBref scraper.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional, List


@dataclass
class Match:
    """
    Data model for a soccer match.
    """
    date: date
    opponent: str
    venue: str  # "Home" or "Away"
    goals_for: int
    goals_against: int
    shots: int
    shots_on_target: int
    shots_off_target: int
    possession_pct: float
    passes_completed: int
    pass_accuracy_pct: float
    corners_for: Optional[int] = None
    corners_against: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_suffered: Optional[int] = None

    def as_dict(self) -> dict:
        """Convert to dictionary for CSV output."""
        return {
            'date': self.date.isoformat(),
            'opponent': self.opponent,
            'venue': self.venue,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'shots': self.shots,
            'shots_on_target': self.shots_on_target,
            'shots_off_target': self.shots_off_target,
            'possession_pct': self.possession_pct,
            'passes_completed': self.passes_completed,
            'pass_accuracy_pct': self.pass_accuracy_pct,
            'corners_for': self.corners_for if self.corners_for is not None else '',
            'corners_against': self.corners_against if self.corners_against is not None else '',
            'fouls_committed': self.fouls_committed if self.fouls_committed is not None else '',
            'fouls_suffered': self.fouls_suffered if self.fouls_suffered is not None else '',
        }


@dataclass
class Team:
    """
    Data model for a soccer team.
    """
    name: str
    fbref_id: str
    matches: List[Match] = None

    def __post_init__(self):
        if self.matches is None:
            self.matches = []