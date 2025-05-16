"""
Tests for the parser module.
"""
import unittest
from datetime import date
from unittest.mock import patch, Mock

from bs4 import BeautifulSoup

from fbref_scraper.parser import (
    parse_team_search_results,
    parse_team_page,
    parse_match_logs,
    _parse_match_row,
    _extract_cell_value
)


class TestParser(unittest.TestCase):
    """Test cases for the parser module."""

    def test_parse_team_search_results(self):
        """Test parsing team search results."""
        html = """
        <div class="search-item">
            <div class="search-item-name">
                <a href="/en/squads/b8fd03ef/Manchester-City-Stats">Manchester City</a>
            </div>
        </div>
        <div class="search-item">
            <div class="search-item-name">
                <a href="/en/squads/19538871/Manchester-United-Stats">Manchester United</a>
            </div>
        </div>
        <div class="search-item">
            <div class="search-item-name">
                <a href="/en/players/some-player">Some Player</a>
            </div>
        </div>
        """
        
        results = parse_team_search_results(html)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['name'], 'Manchester City')
        self.assertEqual(results[0]['id'], 'b8fd03ef')
        self.assertEqual(results[1]['name'], 'Manchester United')
        self.assertEqual(results[1]['id'], '19538871')

    def test_parse_team_page(self):
        """Test parsing team page."""
        html = """
        <div id="meta">
            <h1 itemprop="name">Manchester City</h1>
        </div>
        <div id="inner_nav">
            <ul>
                <li><a href="/en/squads/b8fd03ef/matchlogs/2023-2024/Manchester-City-Match-Logs">Match Logs</a></li>
            </ul>
        </div>
        """
        
        team_info = parse_team_page(html)
        
        self.assertEqual(team_info['name'], 'Manchester City')
        self.assertEqual(team_info['matchlogs_url'], 'https://fbref.com/en/squads/b8fd03ef/matchlogs/2023-2024/Manchester-City-Match-Logs')

    def test_extract_cell_value(self):
        """Test extracting cell values."""
        html = """
        <tr>
            <td data-stat="goals_for">2</td>
            <td data-stat="possession">55.5%</td>
            <td data-stat="empty"></td>
            <td data-stat="invalid">abc</td>
        </tr>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        row = soup.find('tr')
        
        # Test integer extraction
        self.assertEqual(_extract_cell_value(row, 'goals_for', int, 0), 2)
        
        # Test float extraction with transform
        self.assertEqual(_extract_cell_value(row, 'possession', float, 0.0, transform=lambda x: float(x.rstrip('%'))), 55.5)
        
        # Test default value for empty cell
        self.assertEqual(_extract_cell_value(row, 'empty', int, 0), 0)
        
        # Test default value for invalid conversion
        self.assertEqual(_extract_cell_value(row, 'invalid', int, 0), 0)
        
        # Test missing cell
        self.assertEqual(_extract_cell_value(row, 'missing', int, 0), 0)

    def test_parse_match_row(self):
        """Test parsing a match row."""
        html = """
        <tr>
            <td data-stat="date">2023-05-01</td>
            <td data-stat="opponent">Arsenal</td>
            <td data-stat="venue">Home</td>
            <td data-stat="goals_for">3</td>
            <td data-stat="goals_against">1</td>
            <td data-stat="shots">15</td>
            <td data-stat="shots_on_target">8</td>
            <td data-stat="possession">60.2%</td>
            <td data-stat="passes_completed">500</td>
            <td data-stat="passes_pct">88.5%</td>
            <td data-stat="corners">7</td>
            <td data-stat="corners_against">3</td>
            <td data-stat="fouls">10</td>
            <td data-stat="fouled">12</td>
        </tr>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        row = soup.find('tr')
        
        match = _parse_match_row(row)
        
        self.assertIsNotNone(match)
        self.assertEqual(match.date, date(2023, 5, 1))
        self.assertEqual(match.opponent, 'Arsenal')
        self.assertEqual(match.venue, 'Home')
        self.assertEqual(match.goals_for, 3)
        self.assertEqual(match.goals_against, 1)
        self.assertEqual(match.shots, 15)
        self.assertEqual(match.shots_on_target, 8)
        self.assertEqual(match.shots_off_target, 7)  # Calculated as shots - shots_on_target
        self.assertEqual(match.possession_pct, 60.2)
        self.assertEqual(match.passes_completed, 500)
        self.assertEqual(match.pass_accuracy_pct, 88.5)
        self.assertEqual(match.corners_for, 7)
        self.assertEqual(match.corners_against, 3)
        self.assertEqual(match.fouls_committed, 10)
        self.assertEqual(match.fouls_suffered, 12)

    def test_parse_match_logs(self):
        """Test parsing match logs."""
        html = """
        <table class="stats_table">
            <tbody>
                <tr>
                    <td data-stat="date">2023-05-01</td>
                    <td data-stat="opponent">Arsenal</td>
                    <td data-stat="venue">Home</td>
                    <td data-stat="goals_for">3</td>
                    <td data-stat="goals_against">1</td>
                    <td data-stat="shots">15</td>
                    <td data-stat="shots_on_target">8</td>
                    <td data-stat="possession">60.2%</td>
                    <td data-stat="passes_completed">500</td>
                    <td data-stat="passes_pct">88.5%</td>
                    <td data-stat="corners">7</td>
                    <td data-stat="corners_against">3</td>
                    <td data-stat="fouls">10</td>
                    <td data-stat="fouled">12</td>
                </tr>
                <tr>
                    <td data-stat="date">2023-04-25</td>
                    <td data-stat="opponent">Chelsea</td>
                    <td data-stat="venue">Away</td>
                    <td data-stat="goals_for">2</td>
                    <td data-stat="goals_against">2</td>
                    <td data-stat="shots">12</td>
                    <td data-stat="shots_on_target">5</td>
                    <td data-stat="possession">55.8%</td>
                    <td data-stat="passes_completed">450</td>
                    <td data-stat="passes_pct">85.0%</td>
                    <td data-stat="corners">6</td>
                    <td data-stat="corners_against">4</td>
                    <td data-stat="fouls">8</td>
                    <td data-stat="fouled">9</td>
                </tr>
            </tbody>
        </table>
        """
        
        matches = parse_match_logs(html, num_matches=2)
        
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].opponent, 'Arsenal')
        self.assertEqual(matches[1].opponent, 'Chelsea')


if __name__ == '__main__':
    unittest.main()