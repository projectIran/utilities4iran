# X Iran Bot - Deployment Guide

This guide explains how to set up and run the X (Twitter) awareness bot from scratch.

## Prerequisites

- Python 3.8 or higher
- X (Twitter) Developer account with API keys (Free or Basic plan)
- A VPS (optional, for 24/7 operation)

## Quick Start (Local)

### 1. Clone and navigate

```bash
git clone git@github.com:projectIran/utilities4iran.git
cd utilities4iran/socialmedia/X/x-iran-bot
```

### 2. Set up Python environment

**macOS / Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

**Or manually:**
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate.bat     # Windows
pip install -r requirements.txt
```

### 3. Configure API credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your X API credentials:

```env
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
DAILY_POST_LIMIT=15
MIN_INTERVAL=8
MAX_INTERVAL=18
```

You can get these from [developer.x.com](https://developer.x.com).

### 4. Test (dry run)

```bash
source .venv/bin/activate
python bot.py --dry-run
```

This simulates posting without actually tweeting.

### 5. Run once

```bash
python bot.py
```

### 6. Run continuously

```bash
python bot.py --continuous
```

The bot will post at random intervals (configured by `MIN_INTERVAL` and `MAX_INTERVAL` in minutes) and respect the daily limit.

## Multi-Account Setup

To run multiple X accounts, create separate `.env` files:

```bash
cp .env.example account2.env
# Edit account2.env with the second account's credentials
```

Run with:
```bash
python bot.py --continuous --env account2.env
```

Each account gets its own state, history, and log files automatically (e.g. `state_account2.json`, `bot_account2.log`).

## VPS Deployment (24/7)

For uninterrupted operation, deploy on a Linux VPS (Ubuntu recommended).

### 1. Server setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

### 2. Clone and install

```bash
git clone git@github.com:projectIran/utilities4iran.git
cd utilities4iran/socialmedia/X/x-iran-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

### 3. Create a systemd service

```bash
sudo nano /etc/systemd/system/xbot.service
```

Paste the following (adjust paths to match your setup):

```ini
[Unit]
Description=X Iran Awareness Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/utilities4iran/socialmedia/X/x-iran-bot
ExecStart=/root/utilities4iran/socialmedia/X/x-iran-bot/.venv/bin/python3 bot.py --continuous --env .env
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

### 4. Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable xbot
sudo systemctl start xbot
```

### 5. Check status / logs

```bash
sudo systemctl status xbot
journalctl -u xbot -f
```

### Running a second account on the same server

Create another service file (`xbot-2.service`) and change the `--env` parameter:

```ini
ExecStart=/root/utilities4iran/socialmedia/X/x-iran-bot/.venv/bin/python3 bot.py --continuous --env account2.env
```

## Bot Behavior

- **Hybrid mode**: Searches for Iran-related tweets from priority accounts and quotes them. Falls back to mention tweets if search fails.
- **Priority accounts**: US officials, conservative media, and Iran-related figures.
- **Rate limiting**: Respects daily post limits and random intervals to avoid detection.
- **State persistence**: Tracks post index, daily count, and history across restarts.

## File Overview

| File | Purpose |
|---|---|
| `bot.py` | Main bot logic |
| `posts.json` | Pool of tweet messages |
| `.env.example` | Template for API credentials |
| `requirements.txt` | Python dependencies |
| `setup.sh` / `setup.bat` | Automated setup scripts |
| `state*.json` | Runtime state (auto-generated) |
| `history*.json` | Tweet history log (auto-generated) |
