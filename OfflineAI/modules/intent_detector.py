"""
=============================================================
  MODULE 2 — INTENT DETECTION
  Lightweight, rule-based intent classifier.
  Uses pattern matching + keyword extraction against
  locally-trained intent_data.json.
  No ML frameworks, no internet.
=============================================================
"""

import json
import re
from difflib import SequenceMatcher
from typing import Tuple, Optional

from config import INTENT_DATA_FILE


class IntentDetector:
    """Classifies user input into a known intent tag and extracts entities."""

    def __init__(self):
        self.intents = []
        self._load()

    # ── public API ────────────────────────────────────────

    def detect(self, text: str) -> Tuple[str, float, dict]:
        """
        Detect intent from user text.

        Returns
        -------
        (intent_tag, confidence, entities)
        e.g. ("open_app", 0.92, {"app": "notepad"})
        If no intent matches, returns ("unknown", 0.0, {}).
        """
        if not text:
            return ("unknown", 0.0, {})

        text_lower = text.lower().strip()
        best_tag = "unknown"
        best_score = 0.0
        best_entities: dict = {}

        for intent in self.intents:
            tag = intent["tag"]
            for pattern in intent["patterns"]:
                score, entities = self._match_pattern(text_lower, pattern.lower())
                if score > best_score:
                    best_score = score
                    best_tag = tag
                    best_entities = entities

        # Minimum confidence threshold
        if best_score < 0.40:
            return ("unknown", best_score, {})

        return (best_tag, round(best_score, 3), best_entities)

    def reload(self) -> None:
        """Hot-reload intent data from disk."""
        self._load()

    # ── private helpers ───────────────────────────────────

    def _load(self) -> None:
        try:
            with open(INTENT_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.intents = data.get("intents", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[IntentDetector] Warning: {e}")
            self.intents = []

    def _match_pattern(self, text: str, pattern: str) -> Tuple[float, dict]:
        """
        Score how well `text` matches `pattern`.
        Patterns may contain {entity} placeholders like {app} or {topic}.
        """
        entities: dict = {}

        # ── Build a regex from the pattern ────────────────
        placeholder_names = re.findall(r"\{(\w+)\}", pattern)

        if placeholder_names:
            # Replace placeholders with capture groups
            regex_str = re.escape(pattern)
            for name in placeholder_names:
                regex_str = regex_str.replace(re.escape("{" + name + "}"), r"(.+?)")
            regex_str = "^" + regex_str + "$"

            m = re.match(regex_str, text)
            if m:
                for i, name in enumerate(placeholder_names, 1):
                    entities[name] = m.group(i).strip()
                # Placeholder matches score slightly less than exact
                # so specific intents (weather, music) beat generic {topic}
                return (0.98, entities)

            # Partial / fuzzy match: check if the static parts appear
            static_parts = re.split(r"\{\w+\}", pattern)
            static_parts = [p.strip() for p in static_parts if p.strip()]
            if static_parts and all(part in text for part in static_parts):
                # Extract entity as what remains after removing static parts
                remainder = text
                for part in static_parts:
                    remainder = remainder.replace(part, "", 1)
                remainder = remainder.strip()
                if remainder and placeholder_names:
                    entities[placeholder_names[0]] = remainder
                return (0.85, entities)

        # ── No placeholders: direct / fuzzy comparison ────
        if text == pattern:
            return (1.0, entities)

        if pattern in text:
            return (0.90, entities)

        # Sequence-based fuzzy match
        ratio = SequenceMatcher(None, text, pattern).ratio()
        if ratio > 0.60:
            return (ratio, entities)

        # Word-overlap score
        text_words = set(text.split())
        pattern_words = set(pattern.split())
        if pattern_words:
            overlap = len(text_words & pattern_words) / len(pattern_words)
            if overlap > 0.5:
                return (overlap * 0.85, entities)

        # Check if text contains pattern as substring (reversed check)
        if text in pattern:
            return (0.80, entities)

        return (0.0, entities)
