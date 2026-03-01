"""
=============================================================
  MODULE 3 — EMOTION DETECTION
  Rule-based emotion classifier using keyword matching,
  phrase detection, negation handling, and intensifiers.
  All data loaded from local emotion_data.json.
=============================================================
"""

import json
import re
from typing import Tuple

from config import EMOTION_DATA_FILE, EMOTION_CONFIDENCE_THRESHOLD


class EmotionDetector:
    """Detects user emotion from text — fully offline, rule-based."""

    def __init__(self):
        self.emotions: dict = {}
        self.negation_words: list = []
        self.intensifiers: dict = {}
        self._load()

    # ── public API ────────────────────────────────────────

    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect the dominant emotion in the text.

        Returns
        -------
        (emotion_label, confidence)
        e.g. ("sad", 0.82)
        If no emotion is detected, returns ("neutral", 0.0).
        """
        if not text:
            return ("neutral", 0.0)

        text_lower = text.lower().strip()
        scores: dict = {}

        for emotion, data in self.emotions.items():
            if emotion == "neutral":
                continue
            score = self._score_emotion(text_lower, data)
            if score > 0:
                scores[emotion] = score

        if not scores:
            return ("neutral", 0.0)

        best_emotion = max(scores, key=scores.get)
        best_score = scores[best_emotion]

        # Normalize to 0–1 range (cap at 1.0)
        confidence = min(best_score, 1.0)

        if confidence < EMOTION_CONFIDENCE_THRESHOLD:
            return ("neutral", confidence)

        return (best_emotion, round(confidence, 3))

    def has_emotion(self, text: str) -> bool:
        """Quick check: does the text carry detectable emotion?"""
        emotion, conf = self.detect(text)
        return emotion != "neutral" and conf >= EMOTION_CONFIDENCE_THRESHOLD

    def reload(self) -> None:
        self._load()

    # ── private helpers ───────────────────────────────────

    def _load(self) -> None:
        try:
            with open(EMOTION_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert list format to dict format if needed
            raw_emotions = data.get("emotions", {})
            if isinstance(raw_emotions, list):
                self.emotions = {}
                for item in raw_emotions:
                    name = item.get("emotion", "unknown")
                    self.emotions[name] = {
                        "keywords": item.get("keywords", []),
                        "phrases": item.get("phrases", []),
                        "weight": item.get("intensity", 1.0),
                    }
            else:
                self.emotions = raw_emotions

            self.negation_words = data.get("negation_words", [])

            # Convert intensifiers list to dict if needed
            raw_intensifiers = data.get("intensifiers", {})
            if isinstance(raw_intensifiers, list):
                self.intensifiers = {word: 1.5 for word in raw_intensifiers}
            else:
                self.intensifiers = raw_intensifiers
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[EmotionDetector] Warning: {e}")
            self.emotions = {}

    def _score_emotion(self, text: str, emotion_data: dict) -> float:
        """Score how strongly the text matches a single emotion."""
        score = 0.0
        weight = emotion_data.get("weight", 1.0)
        words = text.split()

        # ── Phrase matching (higher priority) ─────────────
        for phrase in emotion_data.get("phrases", []):
            if phrase.lower() in text:
                score += 0.5 * weight
                break  # one phrase match is enough

        # ── Keyword matching ──────────────────────────────
        keywords = emotion_data.get("keywords", [])
        keyword_hits = 0
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                keyword_hits += 1

        if keywords:
            keyword_ratio = keyword_hits / len(keywords)
            score += keyword_ratio * weight * 0.6

        # ── Intensifier boost ─────────────────────────────
        for intensifier, multiplier in self.intensifiers.items():
            if intensifier in text:
                score *= multiplier
                break  # only apply strongest intensifier

        # ── Negation check ────────────────────────────────
        for nw in self.negation_words:
            pattern = r'\b' + re.escape(nw) + r'\b'
            if re.search(pattern, text):
                # Check if negation directly precedes an emotion keyword
                for kw in keywords:
                    neg_pattern = nw + r'\s+' + re.escape(kw)
                    if re.search(neg_pattern, text):
                        score *= 0.3  # heavily reduce score
                        break

        return score
