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
from nlp_logic import StanceClassifier

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
parser.add_argument("--limit", type=int, default=0, help="Limit number of people to analyze")
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
    # Pro-action / pro-regime-change / Pro-Trump
    "regime change", "free iran", "maximum pressure", "attack iran",
    "strike iran", "bomb iran", "end the regime", "fall of regime",
    "overthrow", "topple the regime", "irgc terrorist", "designate irgc",
    "support iran protest", "stand with iran", "woman life freedom",
    "strike the mullahs", "funding terror", "iran nuclear",
    "trump strength", "maga stance on iran", "trump's pressure", "bomb them trump",
    "strike tehran", "trump was right", "strong on iran",
    # Pro-Pahlavi / Monarchist
    "pahlavi", "reza pahlavi", "prince reza", "shah", "shahanshah",
    "crown prince", "secular iran", "democratic iran", "crowned",
    "javid shah", "long live the king",
    # Anti-regime
    "mullahs", "khamenei must go", "death to khamenei", "basij",
    "islamic republic must fall", "end islamic republic", "ayatollah",
    "tehran's terror", "iran's proxies", "houthis", "hezbollah", "hamas",
]

OPPONENT_ANTIWAR_KEYWORDS = [
    # Anti-military-action / Anti-Israel / Anti-Trump
    "no war with iran", "don't attack iran", "diplomacy with iran",
    "negotiate with iran", "peace with iran", "against military action",
    "sanctions are enough", "war is not the answer", "de-escalation",
    "don't bomb iran", "stop the war", "anti-war", "oppose military",
    "dialogue not war", "diplomatic solution", "israel's wars",
    "israeli aggression", "stop bombing gaza", "palestine", "occupation",
    "zionism", "zionist", "apartheid state", "genocide", "war crimes",
    "israel's crimes", "israel's assault", "greater israel", "trump's war", "his war",
    "illegal war", "unconstitutional", "he lied", "trump lied", "betrayal", "dangerous rhetoric",
    "warmongering", "escalation", "reckless", "catastrophe", "failures at home",
    # Khamenei / Pro-Regime sympathy
    "rest in peace khamenei", "rip khamenei", "martyr khamenei", "loss of leader",
    "condolences to iran", "beloved leader", "great imam",
    # Pro-engagement / Multi-polar
    "engage with tehran", "nuclear deal", "jcpoa", "diplomacy first",
    "sanctions kill", "lift sanctions", "cuba", "venezuela", "imperialism",
    "u.s. hegemony", "anti-imperialist", "codepink", "dsa", "socialist",
]

OPPONENT_WRONG_LEADER_KEYWORDS = [
    # Pro-MEK / Rajavi / other opposition groups (NOT Pahlavi)
    "rajavi", "maryam rajavi", "mek", "ncri", "mojahedin",
    "people's mojahedin", "mujahedin", "pmoi", "national council of resistance",
    "ashraf", "camp liberty", "maryam_rajavi",
]

# Relevance keywords to act as a fast gate before expensive NLP
RELEVANCE_KEYWORDS = list(set(
    SUPPORTER_KEYWORDS + 
    OPPONENT_ANTIWAR_KEYWORDS + 
    OPPONENT_WRONG_LEADER_KEYWORDS + 
    ["iran", "tehran", "israel", "zionist", "niac", "middle east", "foreign policy", "diplomacy", "sanctions", "war", "peace", "trump", "khamenei", "mullah"]
))

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


import re

def is_relevant(text: str) -> bool:
    """Check if the text is relevant to our domain (Iran/Israel/Foreign Policy)."""
    text_lower = text.lower()
    for kw in RELEVANCE_KEYWORDS:
        # Use regex for strict word boundary matching
        if re.search(rf"\b{re.escape(kw.lower())}\b", text_lower):
            return True
    return False


def classify_text_enhanced(text: str, nlp: StanceClassifier) -> tuple[str, str, dict]:
    """
    Enhanced classification using Keywords + NLP (Sentiment/Toxicity) + Rules.
    Returns (stance, matched_keyword, scores).
    """
    text_lower = text.lower()
    
    # 1. Check Relevance Gate first
    if not is_relevant(text):
        return STANCE_UNKNOWN, "", {}

    # 2. Check specific 'wrong_leader' keywords (highest priority)
    for kw in OPPONENT_WRONG_LEADER_KEYWORDS:
        if re.search(rf"\b{re.escape(kw.lower())}\b", text_lower):
            return STANCE_OPPONENT_WRONG_LEADER, kw, {"method": "keyword_match"}

    # 3. Use NLP for nuanced detection
    scores = nlp.analyze_tweet(text) or None
    
    # 4. Keyword matches for fallback or weighting (using word boundaries)
    matched_supporter = next((kw for kw in SUPPORTER_KEYWORDS if re.search(rf"\b{re.escape(kw.lower())}\b", text_lower)), None)
    matched_opponent = next((kw for kw in OPPONENT_ANTIWAR_KEYWORDS if re.search(rf"\b{re.escape(kw.lower())}\b", text_lower)), None)

    # 5. Logical Decision Tree
    if scores:
        attack_likelihood = max(scores.toxicity, scores.rule_attack_boost)
        neg_sent = scores.sentiment.get("NEGATIVE", 0.0)
        pos_sent = scores.sentiment.get("POSITIVE", 0.0)

        # PRIORITIZE: If it's a negative political attack mentioning Trump or Israel's war, it's OPPONENT_ANTIWAR
        # Even if 'trump' or 'israel' are in SUPPORTER_KEYWORDS, we check the context
        is_political_attack = attack_likelihood >= 0.60 or neg_sent >= 0.55
        
        if is_political_attack:
            # If it's negative and mentions anti-war themes or specific political attack keywords
            if matched_opponent or "trump" in text_lower or "israel" in text_lower:
                 # Check if it's explicitly supporting Trump's STRENGTH (positive sentiment check)
                 if pos_sent > 0.60 and matched_supporter:
                     return STANCE_SUPPORTER, matched_supporter, scores.__dict__
                 return STANCE_OPPONENT_ANTIWAR, matched_opponent or "political_attack", scores.__dict__
        
        # High toxicity or rule-based attack patterns with anti-war/anti-Israel keywords
        if attack_likelihood >= 0.65 or (neg_sent >= 0.60 and matched_opponent):
            return STANCE_OPPONENT_ANTIWAR, matched_opponent or "political_attack", scores.__dict__
        
        # Positive sentiment + supporter keywords
        if pos_sent >= 0.50 or matched_supporter:
            # If it's positive but has anti-war keywords, prioritize anti-war (usually diplomatic)
            if matched_opponent and not matched_supporter:
                return STANCE_OPPONENT_ANTIWAR, matched_opponent, scores.__dict__
            return STANCE_SUPPORTER, matched_supporter or "positive_sentiment", scores.__dict__

    # 6. Fallback to simple Keyword matching
    if matched_supporter:
        return STANCE_SUPPORTER, matched_supporter, {"method": "keyword_fallback"}
    if matched_opponent:
        return STANCE_OPPONENT_ANTIWAR, matched_opponent, {"method": "keyword_fallback"}

    return STANCE_UNKNOWN, "", {}


def analyze_person(client: tweepy.Client, person: dict, max_tweets: int, nlp: StanceClassifier) -> dict:
    """Fetch recent tweets for a person and classify their stance."""
    handle = person["x_handle"].replace("@", "")
    result = {
        "name": person["name"],
        "handle": handle,
        "stance": STANCE_UNKNOWN,
        "evidence_tweet": "",  # Deprecated in favor of recent_tweets
        "recent_tweets": [], # List of {text, stance, keyword}
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

        # Process each tweet
        for tweet in tweets_resp.data:
            stance, keyword, scores = classify_text_enhanced(tweet.text, nlp)
            tweet_data = {
                "text": tweet.text,
                "stance": stance,
                "keyword": keyword,
                "scores": scores
            }
            result["recent_tweets"].append(tweet_data)

            # Still set a primary stance based on the FIRST match found for backward compatibility
            if result["stance"] == STANCE_UNKNOWN and stance != STANCE_UNKNOWN:
                result["stance"] = stance
                result["evidence_tweet"] = tweet.text[:280]
                result["matched_keyword"] = keyword
                logger.info(f"  ✅ @{handle} → primary {stance} (keyword: '{keyword}')")

        if result["stance"] == STANCE_UNKNOWN:
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

    nlp = StanceClassifier(device=-1) # Use CPU for stability in this env
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

    if args.limit > 0:
        people = people[:args.limit]

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
            current_stance = existing[handle].get("stance", STANCE_UNKNOWN)
            
            if last_checked and current_stance != STANCE_UNKNOWN:
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
        result = analyze_person(client, person, args.max_tweets, nlp)
        stances[handle] = result
        analyzed += 1

        # Intermediate save
        if not args.dry_run:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(stances, f, ensure_ascii=False, indent=2)

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
