"""
=============================================================
  MODULE 13 — BILINGUAL RESPONSE OPTIMIZER

  Lightweight optimization layer for fast Tamil + English chat:
    - Language detection (Tamil / English / mixed)
    - Context compaction for lower memory usage
    - Response cache for repeat prompts
    - Output cleanup for stable assistant UX
=============================================================
"""

from __future__ import annotations

import hashlib
import re
from collections import OrderedDict
from typing import Optional


TAMIL_CHAR_RE = re.compile(r"[\u0B80-\u0BFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
SPACE_RE = re.compile(r"\s+")

# Romanized Tamil cues used in everyday Tanglish conversations.
TANGLISH_HINTS = {
    "enna",
    "epdi",
    "eppadi",
    "unga",
    "ungal",
    "nan",
    "naan",
    "iruka",
    "irukka",
    "venum",
    "venuma",
    "sari",
    "seri",
    "romba",
    "illa",
    "illai",
    "saptiya",
    "pesu",
    "pesunga",
    "jarvis",
}


class BilingualOptimizer:
    """Speed + memory optimizer for bilingual conversation routing."""

    _PROFILE_SETTINGS = {
        "turbo": {
            "max_tokens": 220,
            "temperature": 0.28,
            "context_turns": 2,
            "turn_char_limit": 150,
        },
        "balanced": {
            "max_tokens": 320,
            "temperature": 0.4,
            "context_turns": 4,
            "turn_char_limit": 240,
        },
        "quality": {
            "max_tokens": 430,
            "temperature": 0.52,
            "context_turns": 6,
            "turn_char_limit": 320,
        },
    }

    def __init__(self, cache_size: int = 180):
        self.cache_size = max(20, int(cache_size))
        self._reply_cache: OrderedDict[str, dict] = OrderedDict()

    # -- profile helpers ------------------------------------------------

    def normalize_profile(self, profile: str) -> str:
        value = (profile or "balanced").strip().lower()
        if value in self._PROFILE_SETTINGS:
            return value
        return "balanced"

    def profile_settings(self, profile: str) -> dict:
        return dict(self._PROFILE_SETTINGS[self.normalize_profile(profile)])

    # -- language helpers -----------------------------------------------

    @staticmethod
    def detect_language(text: str) -> str:
        raw = str(text or "")
        if not raw.strip():
            return "en"

        has_tamil_script = bool(TAMIL_CHAR_RE.search(raw))
        has_latin = bool(LATIN_RE.search(raw))

        if has_tamil_script and has_latin:
            return "mix"
        if has_tamil_script:
            return "ta"

        words = {w for w in re.findall(r"[a-z]+", raw.lower()) if len(w) >= 3}
        if words & TANGLISH_HINTS:
            return "ta"

        return "en"

    @staticmethod
    def style_directive(language: str, response_style: str) -> str:
        style = (response_style or "friendly").strip().lower()

        if language == "ta":
            return (
                "Respond naturally in Tamil or Tanglish with warm tone. "
                f"Style: {style}. Keep sentences short and clear."
            )

        if language == "mix":
            return (
                "Respond in a natural Tamil-English mixed style. "
                f"Style: {style}. Avoid over-formal wording."
            )

        return (
            "Respond in clear conversational English with friendly tone. "
            f"Style: {style}. Be concise and practical."
        )

    # -- context compaction ---------------------------------------------

    def compact_turns(self, turns: Optional[list], profile: str) -> list:
        settings = self.profile_settings(profile)
        max_turns = settings["context_turns"]
        char_limit = settings["turn_char_limit"]

        if not turns:
            return []

        compact: list[dict] = []
        for turn in turns[-max_turns:]:
            user_text = self._compact_text(turn.get("user", ""), char_limit)
            ai_text = self._compact_text(turn.get("ai", ""), char_limit)
            if user_text or ai_text:
                compact.append({"user": user_text, "ai": ai_text})

        return compact

    @staticmethod
    def _compact_text(text: str, limit: int) -> str:
        clean = SPACE_RE.sub(" ", str(text or "")).strip()
        if len(clean) <= limit:
            return clean

        clipped = clean[: max(20, limit - 3)].rstrip()
        if " " in clipped:
            clipped = clipped.rsplit(" ", 1)[0]

        return f"{clipped}..."

    # -- cache helpers --------------------------------------------------

    def cache_key(
        self,
        user_text: str,
        emotion: str,
        provider: str,
        persona: str,
        language: str,
        profile: str,
        factual_context: str,
    ) -> str:
        compact_fact = self._compact_text(factual_context, 260)
        payload = "|".join(
            [
                self._compact_text(user_text, 420).lower(),
                (emotion or "neutral").lower().strip(),
                (provider or "auto").lower().strip(),
                (persona or "jarvis").lower().strip(),
                (language or "en").lower().strip(),
                self.normalize_profile(profile),
                compact_fact.lower(),
            ]
        )
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    def get_cached(self, key: str) -> Optional[dict]:
        if key not in self._reply_cache:
            return None

        self._reply_cache.move_to_end(key)
        cached = self._reply_cache[key]
        return dict(cached)

    def set_cached(self, key: str, text: str, provider: str, model: str) -> None:
        self._reply_cache[key] = {
            "text": text,
            "provider": provider,
            "model": model,
        }
        self._reply_cache.move_to_end(key)

        while len(self._reply_cache) > self.cache_size:
            self._reply_cache.popitem(last=False)

    # -- output cleanup -------------------------------------------------

    @staticmethod
    def sanitize_reply(text: str) -> str:
        clean = SPACE_RE.sub(" ", str(text or "")).strip()
        clean = clean.replace("As an AI language model,", "")
        clean = clean.replace("As a language model,", "")
        clean = SPACE_RE.sub(" ", clean).strip()
        return clean
