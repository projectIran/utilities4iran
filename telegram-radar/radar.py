#!/usr/bin/env python3
"""
Telegram Radar - Iran/Israel/US Trending Posts Monitor

Monitors X (Twitter) for trending posts and sends them to Telegram.
Designed for MINIMAL API usage (~3-4 requests/hour, ~7K reads/month).

Usage:
    python radar.py              # Run continuously
    python radar.py --once       # Run once and exit
    python radar.py --dry-run    # Search without sending to Telegram
"""

import os
import sys
import json
import time
import random
import logging
import signal
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    import tweepy
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install tweepy python-dotenv requests")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent

parser = argparse.ArgumentParser(description="Telegram Radar - Monitor X for trending Iran-related posts")
parser.add_argument("--once", action="store_true", help="Run one search cycle and exit")
parser.add_argument("--dry-run", action="store_true", help="Search but don't send to Telegram")
parser.add_argument("--env", type=str, default=".env", help="Path to .env file (default: .env)")
args = parser.parse_args()

ENV_PATH = SCRIPT_DIR / args.env
if not ENV_PATH.exists():
    print(f"Error: {ENV_PATH} not found. Copy .env.example to .env and fill in your keys.")
    sys.exit(1)

load_dotenv(ENV_PATH)

SEEN_FILE = SCRIPT_DIR / "seen_tweets.json"
STATS_FILE = SCRIPT_DIR / "stats.json"
LOG_FILE = SCRIPT_DIR / "radar.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration from .env ---
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
TG_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEARCH_INTERVAL = int(os.environ.get("SEARCH_INTERVAL_MINUTES", "60"))
MIN_LIKES = int(os.environ.get("MIN_LIKES", "100"))
MIN_RETWEETS = int(os.environ.get("MIN_RETWEETS", "20"))
MAX_RESULTS = int(os.environ.get("MAX_RESULTS", "10"))

# --- Search Queries ---
# Rotating queries to maximize coverage with minimal API calls.
# Each query runs once per cycle; we rotate through them.
# With 3 queries and 60-min interval, each query runs every 3 hours.
# Cost: ~24 requests/day × 10 results = 240 reads/day ≈ 7,200/month (under Basic tier 10K limit)
SEARCH_QUERIES = [
    # Iran-specific: iran, iranian, khamenei, reza pahlavi, revolution (EN+FA)
    '(iran OR iranian OR ایران OR ایرانی OR khamenei OR خامنه‌ای OR "reza pahlavi" OR "رضا پهلوی" OR انقلاب OR "iran revolution") -is:retweet -is:reply',
    # Iran + Israel/conflict/nuclear (EN+FA)
    '(iran OR ایران) (israel OR اسرائیل OR netanyahu OR نتانیاهو OR nuclear OR هسته‌ای OR sanctions OR تحریم OR war OR جنگ) -is:retweet -is:reply',
    # Iran + US/politics/leadership (EN+FA)
    '(iran OR ایران) (trump OR ترامپ OR america OR آمریکا OR leader OR رهبر OR رهبری) -is:retweet -is:reply',
    # Iran human rights: internet blackout, political prisoners, execution (EN+FA)
    '(DigitalBlackOutIran OR "قطعی اینترنت" OR "internet shutdown" OR "زندانیان سیاسی" OR "political prisoners" OR اعدام OR execution iran) -is:retweet -is:reply',
]

running = True


def signal_handler(signum, frame):
    global running
    logger.info("Shutting down gracefully...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def check_config():
    missing = []
    if not X_BEARER_TOKEN:
        missing.append("X_BEARER_TOKEN")
    if not TG_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TG_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")
    if missing:
        logger.error(f"Missing config: {', '.join(missing)}")
        logger.error("Set them in your .env file. See .env.example")
        sys.exit(1)


def load_seen() -> dict:
    """Load seen tweet IDs with timestamps for expiry."""
    if not SEEN_FILE.exists():
        return {}
    try:
        with open(SEEN_FILE, "r") as f:
            data = json.load(f)
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        return {k: v for k, v in data.items() if v > cutoff}
    except Exception:
        return {}


def save_seen(seen: dict):
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    cleaned = {k: v for k, v in seen.items() if v > cutoff}
    with open(SEEN_FILE, "w") as f:
        json.dump(cleaned, f, indent=2)


def update_stats(sent_count: int, searched_count: int):
    stats = {"total_sent": 0, "total_searched": 0, "daily": {}}
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, "r") as f:
                stats = json.load(f)
        except Exception:
            pass

    today = str(datetime.now().date())
    stats["total_sent"] = stats.get("total_sent", 0) + sent_count
    stats["total_searched"] = stats.get("total_searched", 0) + searched_count
    if today not in stats.get("daily", {}):
        stats["daily"][today] = {"sent": 0, "searched": 0}
    stats["daily"][today]["sent"] += sent_count
    stats["daily"][today]["searched"] += searched_count
    stats["last_run"] = datetime.now().isoformat()

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def create_x_client() -> tweepy.Client:
    return tweepy.Client(
        bearer_token=X_BEARER_TOKEN,
        wait_on_rate_limit=True
    )


def search_trending(client: tweepy.Client, query: str, seen: dict) -> list[dict]:
    """Search X for trending posts. Returns filtered, sorted results."""
    logger.info(f"Searching: {query[:80]}...")

    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=MAX_RESULTS,
            sort_order="relevancy",
            tweet_fields=["public_metrics", "created_at", "author_id"],
            expansions=["author_id"],
            user_fields=["username", "name", "public_metrics", "verified"]
        )
    except tweepy.TooManyRequests:
        logger.warning("Rate limited by X API. Will retry next cycle.")
        return []
    except tweepy.Unauthorized:
        logger.error("X API Unauthorized (401). Check your X_BEARER_TOKEN.")
        return []
    except tweepy.Forbidden:
        logger.error("X API Forbidden (403). Your API tier may not support search.")
        return []
    except Exception as e:
        logger.error(f"X API error: {e}")
        return []

    if not response.data:
        logger.info("No results for this query")
        return []

    users = {}
    if response.includes and "users" in response.includes:
        users = {u.id: u for u in response.includes["users"]}

    results = []
    for tweet in response.data:
        tweet_id = str(tweet.id)
        if tweet_id in seen:
            continue

        metrics = tweet.public_metrics or {}
        likes = metrics.get("like_count", 0)
        retweets = metrics.get("retweet_count", 0)
        replies = metrics.get("reply_count", 0)

        if likes < MIN_LIKES and retweets < MIN_RETWEETS:
            continue

        author = users.get(tweet.author_id)
        author_name = author.name if author else "Unknown"
        author_handle = author.username if author else "unknown"
        author_followers = 0
        if author and author.public_metrics:
            author_followers = author.public_metrics.get("followers_count", 0)
        author_verified = getattr(author, "verified", False) if author else False

        results.append({
            "id": tweet_id,
            "text": tweet.text,
            "author_name": author_name,
            "author_handle": author_handle,
            "author_followers": author_followers,
            "author_verified": author_verified,
            "likes": likes,
            "retweets": retweets,
            "replies": replies,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
            "url": f"https://x.com/{author_handle}/status/{tweet_id}"
        })

    results.sort(key=lambda x: x["likes"] + x["retweets"] * 2, reverse=True)
    logger.info(f"Found {len(results)} trending posts (from {len(response.data)} total)")
    return results


def format_telegram_message(tweet: dict) -> str:
    """Format a tweet as a rich Telegram message."""
    verified = " ✅" if tweet["author_verified"] else ""

    def fmt_num(n):
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n / 1_000:.1f}K"
        return str(n)

    text = tweet["text"]
    if len(text) > 500:
        text = text[:497] + "..."

    return (
        f"👤 <b>{tweet['author_name']}</b>{verified}\n"
        f"<code>@{tweet['author_handle']}</code> · {fmt_num(tweet['author_followers'])} followers\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"❤️ {fmt_num(tweet['likes'])}  🔁 {fmt_num(tweet['retweets'])}  💬 {fmt_num(tweet['replies'])}\n\n"
        f"🔗 <a href=\"{tweet['url']}\">مشاهده در X</a>"
    )


def send_to_telegram(message: str, dry_run: bool = False) -> bool:
    """Send formatted message to Telegram."""
    if dry_run:
        logger.info(f"[DRY RUN] Would send to Telegram:\n{message}\n")
        return True

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            return True
        logger.error(f"Telegram API error {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def run_cycle(query: str, dry_run: bool = False) -> tuple[int, int]:
    """Run one search-and-send cycle. Returns (sent_count, searched_count)."""
    client = create_x_client()
    seen = load_seen()

    tweets = search_trending(client, query, seen)
    searched_count = len(tweets)

    if not tweets:
        return 0, 0

    sent_count = 0
    now = datetime.now().isoformat()

    for tweet in tweets:
        msg = format_telegram_message(tweet)
        if send_to_telegram(msg, dry_run):
            sent_count += 1
            time.sleep(1.5)
        seen[tweet["id"]] = now

    save_seen(seen)
    return sent_count, searched_count


def run_once(dry_run: bool = False):
    """Run all queries once."""
    check_config()
    total_sent = 0
    total_searched = 0

    for query in SEARCH_QUERIES:
        sent, searched = run_cycle(query, dry_run)
        total_sent += sent
        total_searched += searched
        time.sleep(2)

    update_stats(total_sent, total_searched)
    logger.info(f"Done. Sent {total_sent} posts to Telegram.")


def run_continuous(dry_run: bool = False):
    """Run continuously, rotating through queries."""
    check_config()

    logger.info("=" * 50)
    logger.info("Telegram Radar Started")
    logger.info(f"  Interval: every {SEARCH_INTERVAL} minutes")
    logger.info(f"  Filters: {MIN_LIKES}+ likes OR {MIN_RETWEETS}+ retweets")
    logger.info(f"  Queries: {len(SEARCH_QUERIES)} (rotating)")
    logger.info(f"  Chat ID: {TG_CHAT_ID}")
    logger.info("=" * 50)

    query_idx = 0

    while running:
        query = SEARCH_QUERIES[query_idx % len(SEARCH_QUERIES)]
        query_idx += 1

        logger.info(f"\n--- Cycle {query_idx} (Query {(query_idx - 1) % len(SEARCH_QUERIES) + 1}/{len(SEARCH_QUERIES)}) ---")

        try:
            sent, searched = run_cycle(query, dry_run)
            update_stats(sent, searched)
            if sent:
                logger.info(f"Sent {sent} new posts to Telegram")
        except Exception as e:
            logger.error(f"Cycle error: {e}")

        if not running:
            break

        jitter = random.randint(-120, 120)
        sleep_secs = SEARCH_INTERVAL * 60 + jitter
        next_time = datetime.now() + timedelta(seconds=sleep_secs)
        logger.info(f"Next check at {next_time.strftime('%H:%M:%S')} ({sleep_secs // 60}m {sleep_secs % 60}s)")

        for _ in range(sleep_secs):
            if not running:
                break
            time.sleep(1)

    logger.info("Radar stopped.")


if __name__ == "__main__":
    if args.once:
        run_once(args.dry_run)
    else:
        run_continuous(args.dry_run)
