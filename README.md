# FBref Scraper

A command-line tool to scrape match data from [FBref](https://fbref.com).

## Features

- Fetch the last 7 competitive matches for a team
- Extract key match metrics:
  - Goals scored and conceded
  - Total shots, shots on target, shots off target
  - Possession percentage
  - Passes completed and pass accuracy
  - Corners for and against
  - Fouls committed and suffered
- Output to CSV format

## Installation

```bash
# From PyPI (once published)
pip install fbref-scraper

# From source
git clone https://github.com/yourusername/fbref-scraper
cd fbref-scraper
pip install -e .
```

## Usage

```bash
# Using team name
fbref_scraper --team "Manchester City"

# Using FBref URL
fbref_scraper --url "https://fbref.com/en/squads/b8fd03ef/Manchester-City-Stats"

# Output to stdout instead of file
fbref_scraper --team "Manchester City" --stdout
```

## Output Format

The tool outputs a CSV file with the following columns:

```
date,opponent,venue,goals_for,goals_against,shots,shots_on_target,shots_off_target,possession_pct,passes_completed,pass_accuracy_pct,corners_for,corners_against,fouls_committed,fouls_suffered
```

Each row corresponds to one match, with the most recent matches first.

## Requirements

- Python 3.8 or higher
- requests
- beautifulsoup4
- lxml

## License

MIT