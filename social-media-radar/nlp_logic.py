import re
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from transformers import pipeline

logger = logging.getLogger("stance_analyzer")

# --- Config ---
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
TOXICITY_MODEL = "unitary/toxic-bert"

# Accusation/Political attack keywords for rule-based boosting
ACCUSATION_KEYWORDS = [
    "dictatorship", "crime", "crimes", "assault", "takeover", "propaganda",
    "oligarch", "oligarchs", "fraud", "liar", "scam", "scammer", "corrupt",
    "traitor", "terrorist", "genocide", "nazi", "fascist", "apartheid",
    "imperialist", "warmonger", "puppet"
]

ABSOLUTIST_WORDS = ["all", "none", "always", "never", "everyone", "no one", "unprecedented", "totally", "completely"]

@dataclass
class Scores:
    sentiment: Dict[str, float]  # NEGATIVE/NEUTRAL/POSITIVE
    toxicity: float              # 0..1
    rule_attack_boost: float     # 0..1 (heuristic)

class StanceClassifier:
    def __init__(self, device: int = -1):
        """
        Initialize the NLP pipelines.
        device=-1 for CPU, 0 for GPU.
        """
        logger.info("📡 Loading Sentiment and Toxicity models (this may take a moment)...")
        try:
            self.sentiment_pipe = pipeline(
                "sentiment-analysis",
                model=SENTIMENT_MODEL,
                tokenizer=SENTIMENT_MODEL,
                return_all_scores=True,
                device=device,
            )
            self.toxicity_pipe = pipeline(
                "text-classification",
                model=TOXICITY_MODEL,
                tokenizer=TOXICITY_MODEL,
                return_all_scores=True,
                device=device,
            )
            logger.info("✅ Models loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            self.sentiment_pipe = None
            self.toxicity_pipe = None

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _caps_ratio(self, text: str) -> float:
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return 0.0
        caps = [c for c in letters if c.isupper()]
        return len(caps) / len(letters)

    def _compute_rule_boost(self, text: str) -> float:
        t = text.lower()
        acc = sum(1 for w in ACCUSATION_KEYWORDS if w in t)
        absw = sum(1 for w in ABSOLUTIST_WORDS if w in t)
        
        exclam = t.count("!")
        caps_ratio = self._caps_ratio(text)

        score = 0.0
        score += min(acc * 0.15, 0.60)          # accusation words are strong
        score += min(absw * 0.05, 0.15)         # absolutist words moderate
        score += min(exclam * 0.05, 0.15)       # exclamation signals intensity
        score += min(caps_ratio * 0.30, 0.15)   # shouting signal

        return max(0.0, min(score, 1.0))

    def _parse_sentiment(self, results) -> Dict[str, float]:
        # RoBERTa labels: 0: negative, 1: neutral, 2: positive
        if not results:
            return {}
        
        # logger.debug(f"NLP Sentiment Raw: {results}")
        
        # transformers results can be List[Dict] or List[List[Dict]]
        if isinstance(results[0], list):
            data = results[0]
        else:
            data = results

        out = {}
        for s in data:
            if isinstance(s, dict) and "label" in s and "score" in s:
                out[s["label"].upper()] = float(s["score"])
             
        # Mapping to internal keys if necessary
        mapping = {"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"}
        standardized = {}
        for k, v in out.items():
            standardized[mapping.get(k, k)] = v
        return standardized

    def _parse_toxicity(self, results) -> float:
        if not results:
            return 0.0
            
        # logger.debug(f"NLP Toxicity Raw: {results}")

        if isinstance(results[0], list):
            data = results[0]
        else:
            data = results

        lab = {}
        for s in data:
            if isinstance(s, dict) and "label" in s and "score" in s:
                lab[s["label"].upper()] = float(s["score"])

        if "TOXIC" in lab:
            return lab["TOXIC"]
        if "LABEL_1" in lab:
            return lab["LABEL_1"]
        return max(lab.values()) if lab else 0.0

    def analyze_tweet(self, text: str) -> Optional[Scores]:
        if not self.sentiment_pipe or not self.toxicity_pipe:
            return None

        clean_text = self._normalize_text(text)
        if not clean_text:
            return None

        try:
            sent_raw = self.sentiment_pipe(clean_text)
            sent = self._parse_sentiment(sent_raw)

            tox_raw = self.toxicity_pipe(clean_text)
            tox = self._parse_toxicity(tox_raw)

            rule_boost = self._compute_rule_boost(clean_text)

            return Scores(sentiment=sent, toxicity=tox, rule_attack_boost=rule_boost)
        except Exception as e:
            logger.error(f"⚠️ Error during NLP inference: {e}")
            return None
