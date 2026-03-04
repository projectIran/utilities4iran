#!/usr/bin/env python3
"""
X Post Stance Analyzer for Social Media Radar
Reads recent X posts from people in democrats.json & republicans.json,
classifies their stance, and outputs stances.json for the frontend.

Usage:
  python stance_analyzer.py                 # Run analysis
  python stance_analyzer.py --dry-run       # Test API without saving
  python stance_analyzer.py --env /path/.env # Use specific .env file
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

try:
    import tweepy
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install tweepy python-dotenv")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent

# === CLI Args ===
parser = argparse.ArgumentParser(description="Analyze X posts for stance classification")
parser.add_argument("--env", default=str(Path.home() / "almedia-project" / "x-iran-bot" / ".env"),
                    help="Path to .env file with X API credentials")
parser.add_argument("--dry-run", action="store_true", help="Test API, don't save results")
parser.add_argument("--max-tweets", type=int, default=10, help="Max tweets to check per person")
parser.add_argument("--output", default=str(SCRIPT_DIR / "stances.json"), help="Output file path")
args = parser.parse_args()

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(SCRIPT_DIR / "stance_analyzer.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("stance_analyzer")

# === Load Environment ===
env_path = Path(args.env)
if not env_path.exists():
    logger.error(f"❌ .env file not found: {env_path}")
    logger.info("Copy your x-iran-bot/.env here or use --env flag")
    sys.exit(1)

load_dotenv(env_path)

API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    logger.error("❌ Missing X API credentials in .env file")
    sys.exit(1)

# === Stance Classification Keywords ===

SUPPORTER_KEYWORDS = [
    # Pro-action / pro-regime-change
    "regime change", "free iran", "maximum pressure", "attack iran",
    "strike iran", "bomb iran", "end the regime", "fall of regime",
    "overthrow", "topple the regime", "irgc terrorist", "designate irgc",
    "support iran protest", "stand with iran", "woman life freedom",
    # Pro-Pahlavi
    "pahlavi", "reza pahlavi", "prince reza", "shah", "shahanshah",
    "crown prince", "secular iran", "democratic iran",
    # Anti-regime
    "mullahs", "khamenei must go", "death to khamenei",
    "islamic republic must fall", "end islamic republic",
]

OPPONENT_ANTIWAR_KEYWORDS = [
    # Anti-military-action
    "no war with iran", "don't attack iran", "diplomacy with iran",
    "negotiate with iran", "peace with iran", "against military action",
    "sanctions are enough", "war is not the answer", "de-escalation",
    "don't bomb iran", "stop the war", "anti-war", "oppose military",
    "dialogue not war", "diplomatic solution",
    # Pro-engagement with regime
    "engage with tehran", "nuclear deal", "jcpoa", "diplomacy first",
]

OPPONENT_WRONG_LEADER_KEYWORDS = [
    # Pro-MEK / Rajavi / other opposition groups (NOT Pahlavi)
    "rajavi", "maryam rajavi", "mek", "ncri", "mojahedin",
    "people's mojahedin", "mujahedin", "pmoi", "national council of resistance",
    "ashraf", "camp liberty",
]

# === Stance Categories ===
STANCE_SUPPORTER = "supporter"
STANCE_OPPONENT_ANTIWAR = "opponent_antiwar"
STANCE_OPPONENT_WRONG_LEADER = "opponent_wrong_leader"
STANCE_UNKNOWN = "unknown"


def create_client() -> tweepy.Client:
    """Create authenticated Tweepy client."""
    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )


def load_people() -> list[dict]:
    """Load all people from democrats.json and republicans.json."""
    people = []
    for filename in ["data/democrats.json", "data/republicans.json"]:
        filepath = SCRIPT_DIR / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for person in data:
                    person["_source_file"] = filename
                people.extend(data)
            logger.info(f"📂 Loaded {len(data)} people from {filename}")
        else:
            logger.warning(f"⚠️ File not found: {filepath}")
    return people


def classify_text(text: str) -> tuple[str, str]:
    """
    Classify a tweet's text into a stance category.
    Returns (stance, matched_keyword).
    Priority: wrong_leader > supporter > opponent_antiwar
    """
    text_lower = text.lower()

    # Check wrong leader first (most specific)
    for kw in OPPONENT_WRONG_LEADER_KEYWORDS:
        if kw in text_lower:
            return STANCE_OPPONENT_WRONG_LEADER, kw

    # Check supporter keywords
    for kw in SUPPORTER_KEYWORDS:
        if kw in text_lower:
            return STANCE_SUPPORTER, kw

    # Check opponent (anti-war) keywords
    for kw in OPPONENT_ANTIWAR_KEYWORDS:
        if kw in text_lower:
            return STANCE_OPPONENT_ANTIWAR, kw

    return STANCE_UNKNOWN, ""


def analyze_person(client: tweepy.Client, person: dict, max_tweets: int) -> dict:
    """Fetch recent tweets for a person and classify their stance."""
    handle = person["x_handle"].replace("@", "")
    result = {
        "name": person["name"],
        "handle": handle,
        "stance": STANCE_UNKNOWN,
        "evidence_tweet": "",
        "matched_keyword": "",
        "tweets_checked": 0,
        "last_checked": datetime.now(timezone.utc).isoformat(),
    }

    try:
        # Get user ID
        user_resp = client.get_user(username=handle)
        if not user_resp.data:
            logger.warning(f"  ⚠️ User not found: @{handle}")
            return result

        user_id = user_resp.data.id

        # Get recent tweets
        tweets_resp = client.get_users_tweets(
            id=user_id,
            max_results=max_tweets,
            exclude=["retweets"],
            tweet_fields=["created_at", "public_metrics"],
        )

        if not tweets_resp.data:
            logger.info(f"  📭 No recent tweets from @{handle}")
            return result

        result["tweets_checked"] = len(tweets_resp.data)

        # Classify each tweet — use the FIRST match found
        for tweet in tweets_resp.data:
            stance, keyword = classify_text(tweet.text)
            if stance != STANCE_UNKNOWN:
                result["stance"] = stance
                result["evidence_tweet"] = tweet.text[:280]  # Truncate for storage
                result["matched_keyword"] = keyword
                logger.info(f"  ✅ @{handle} → {stance} (keyword: '{keyword}')")
                return result

        logger.info(f"  ❓ @{handle} → no clear stance from {len(tweets_resp.data)} tweets")
        return result

    except tweepy.TooManyRequests:
        logger.warning(f"  ⏳ Rate limited on @{handle}, will retry later")
        time.sleep(15)
        return result
    except tweepy.Forbidden:
        logger.warning(f"  🚫 Forbidden for @{handle} (account may be private)")
        return result
    except tweepy.NotFound:
        logger.warning(f"  ❌ Account not found: @{handle}")
        return result
    except Exception as e:
        logger.error(f"  💥 Error analyzing @{handle}: {e}")
        return result


def load_existing_stances(output_path: str) -> dict:
    """Load existing stances to avoid re-checking recently analyzed people."""
    if Path(output_path).exists():
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def run():
    """Main analysis loop."""
    logger.info("=" * 60)
    logger.info("🔍 X Post Stance Analyzer — Starting")
    logger.info(f"   API credentials from: {env_path}")
    logger.info(f"   Output: {args.output}")
    logger.info(f"   Max tweets per person: {args.max_tweets}")
    logger.info(f"   Dry run: {args.dry_run}")
    logger.info("=" * 60)

    client = create_client()

    # Test credentials
    try:
        me = client.get_me()
        logger.info(f"✅ Authenticated as: @{me.data.username}")
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        sys.exit(1)

    people = load_people()
    if not people:
        logger.error("❌ No people loaded from JSON files")
        sys.exit(1)

    # Load existing stances to skip recently checked
    existing = load_existing_stances(args.output)
    stances = {}
    analyzed = 0
    skipped = 0

    for i, person in enumerate(people):
        handle = person["x_handle"].replace("@", "").lower()

        # Skip if already analyzed in the last 24 hours
        if handle in existing:
            last_checked = existing[handle].get("last_checked", "")
            if last_checked:
                try:
                    checked_dt = datetime.fromisoformat(last_checked)
                    hours_ago = (datetime.now(timezone.utc) - checked_dt).total_seconds() / 3600
                    if hours_ago < 24:
                        stances[handle] = existing[handle]
                        skipped += 1
                        continue
                except (ValueError, TypeError):
                    pass

        logger.info(f"[{i+1}/{len(people)}] Analyzing @{handle} ({person['name']})...")
        result = analyze_person(client, person, args.max_tweets)
        stances[handle] = result
        analyzed += 1

        # Rate limit protection: pause between requests
        time.sleep(1.5)

    # Summary
    supporters = sum(1 for s in stances.values() if s["stance"] == STANCE_SUPPORTER)
    opponents_aw = sum(1 for s in stances.values() if s["stance"] == STANCE_OPPONENT_ANTIWAR)
    opponents_wl = sum(1 for s in stances.values() if s["stance"] == STANCE_OPPONENT_WRONG_LEADER)
    unknown = sum(1 for s in stances.values() if s["stance"] == STANCE_UNKNOWN)

    logger.info("=" * 60)
    logger.info("📊 RESULTS SUMMARY")
    logger.info(f"   Total people: {len(stances)}")
    logger.info(f"   Analyzed now: {analyzed} | Skipped (cached): {skipped}")
    logger.info(f"   🟢 Supporters: {supporters}")
    logger.info(f"   🔴 Opponents (anti-war): {opponents_aw}")
    logger.info(f"   ⚠️  Opponents (wrong leader): {opponents_wl}")
    logger.info(f"   ❓ Unknown: {unknown}")
    logger.info("=" * 60)

    if not args.dry_run:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(stances, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Saved stances to: {args.output}")
    else:
        logger.info("🧪 Dry run — results NOT saved")
        print(json.dumps(stances, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
