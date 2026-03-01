"""
=============================================================
  MODULE 8 — MEMORY MODULE (Local Persistence)
  Stores user preferences, conversation history, and
  learned facts — all in a local JSON file.
  Per-user, per-installation. No shared data.
=============================================================
"""

import json
from datetime import datetime
from typing import Optional

from config import MEMORY_FILE, MAX_MEMORY_ENTRIES, MAX_CONVERSATION_HISTORY


class Memory:
    """Local, per-user memory — stored in user/memory.json."""

    def __init__(self):
        self.data: dict = {}
        self._load()

    # ── public API ────────────────────────────────────────

    def get_user_name(self) -> Optional[str]:
        return self.data.get("user_name")

    def set_user_name(self, name: str) -> None:
        # Prevent invalid names (flags, empty, etc.)
        cleaned = name.strip().strip('-').strip()
        if not cleaned or cleaned.startswith('-') or len(cleaned) < 2:
            return
        self.data["user_name"] = cleaned
        self._save()

    def get_conversation_count(self) -> int:
        return self.data.get("conversation_count", 0)

    def increment_conversation(self) -> None:
        self.data["conversation_count"] = self.data.get("conversation_count", 0) + 1
        self.data["last_active"] = datetime.now().isoformat()
        self._save()

    def add_to_history(self, user_text: str, ai_response: str) -> None:
        """Save a conversation turn (trimmed to max history)."""
        history = self.data.setdefault("conversation_history", [])
        history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_text,
            "ai": ai_response,
        })
        # Trim old entries
        if len(history) > MAX_CONVERSATION_HISTORY:
            self.data["conversation_history"] = history[-MAX_CONVERSATION_HISTORY:]
        self._save()

    def get_history(self) -> list:
        """Get the full conversation history."""
        return self.data.get("conversation_history", [])

    def get_last_emotion(self) -> Optional[str]:
        """Return the emotion from the last conversation turn, if stored."""
        history = self.data.get("conversation_history", [])
        if history:
            return history[-1].get("emotion")
        return None

    def store_emotion(self, emotion: str) -> None:
        """Append emotion tag to the most recent history entry."""
        history = self.data.get("conversation_history", [])
        if history:
            history[-1]["emotion"] = emotion
            self._save()

    def learn_fact(self, question: str, answer: str) -> None:
        """Store a user-taught fact."""
        facts = self.data.setdefault("learned_facts", [])
        facts.append({
            "question": question,
            "answer": answer,
            "learned_at": datetime.now().isoformat(),
        })
        if len(facts) > MAX_MEMORY_ENTRIES:
            self.data["learned_facts"] = facts[-MAX_MEMORY_ENTRIES:]
        self._save()

    def set_preference(self, key: str, value) -> None:
        prefs = self.data.setdefault("preferences", {})
        prefs[key] = value
        self._save()

    def get_preference(self, key: str, default=None):
        return self.data.get("preferences", {}).get(key, default)

    def reload(self) -> None:
        self._load()

    # ── private helpers ───────────────────────────────────

    def _load(self) -> None:
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {
                "user_name": None,
                "conversation_count": 0,
                "last_active": None,
                "preferences": {},
                "conversation_history": [],
                "learned_facts": [],
            }
            self._save()

    def _save(self) -> None:
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Memory] Save error: {e}")
