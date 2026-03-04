# X Iran Awareness Bot

A Python bot that monitors tweets from influential accounts about Iran and automatically engages by quoting or mentioning them with awareness messages.

## Features

- **Smart Hybrid Mode**: Searches for Iran-related tweets and quotes them. Falls back to mention tweets when search is unavailable.
- **Priority Account Monitoring**: Tracks US officials, politicians, conservative media, and Iran-related figures.
- **Multi-Account Support**: Run multiple X accounts simultaneously with separate configurations.
- **Rate Limit Handling**: Configurable daily limits and randomized intervals.
- **State Persistence**: Resumes where it left off after restarts.

## Quick Start

```bash
# Setup
cp .env.example .env       # Add your X API credentials
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python bot.py --continuous
```

## Usage

| Command | Description |
|---|---|
| `python bot.py` | Post once and exit |
| `python bot.py --continuous` | Run continuously with random intervals |
| `python bot.py --dry-run` | Simulate without posting |
| `python bot.py --continuous --env account2.env` | Run with a different account |

## Configuration

All settings are in your `.env` file:

| Variable | Description | Default |
|---|---|---|
| `X_API_KEY` | X API consumer key | *required* |
| `X_API_SECRET` | X API consumer secret | *required* |
| `X_ACCESS_TOKEN` | X access token | *required* |
| `X_ACCESS_TOKEN_SECRET` | X access token secret | *required* |
| `DAILY_POST_LIMIT` | Max tweets per day | 25 |
| `MIN_INTERVAL` | Min minutes between tweets | 30 |
| `MAX_INTERVAL` | Max minutes between tweets | 60 |

See [DEPLOYMENT.md](DEPLOYMENT.md) for full setup and VPS deployment instructions.
