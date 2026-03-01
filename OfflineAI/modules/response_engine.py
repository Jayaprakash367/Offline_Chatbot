"""
=============================================================
  MODULE 6 — RESPONSE ENGINE
  Selects and formats friendly, empathetic AI responses
  from locally stored templates in responses.json.
=============================================================
"""

import json
import random
from datetime import datetime
from typing import Optional

from config import RESPONSES_FILE, RESPONSES_FILE_EN, LANGUAGE


class ResponseEngine:
    """Generates human-like responses from local templates."""

    def __init__(self):
        self.responses: dict = {}
        self._load()

    def _load(self) -> None:
        """Load responses from the appropriate JSON file based on language."""
        # Select file based on LANGUAGE setting
        if LANGUAGE == "en":
            responses_file = RESPONSES_FILE_EN
        else:
            responses_file = RESPONSES_FILE
        
        try:
            with open(responses_file, "r", encoding="utf-8") as f:
                self.responses = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Responses file not found: {responses_file}")
            self.responses = {}

    # ── public API ────────────────────────────────────────

    def get(self, category: str, **kwargs) -> str:
        """
        Get a random response from a category and format it.

        Parameters
        ----------
        category : str
            Key in responses.json (e.g., "greeting", "open_app_success").
        **kwargs :
            Placeholder values (e.g., app="Notepad", time="10:30 AM").
        """
        templates = self.responses.get(category, [])

        if not templates:
            return self._fallback(category)

        # If it's a list, pick a random one; if dict, return as-is
        if isinstance(templates, list):
            template = random.choice(templates)
        elif isinstance(templates, str):
            template = templates
        else:
            template = str(templates)

        # Auto-fill {time} and {date} if not supplied
        if "{time}" in template and "time" not in kwargs:
            kwargs["time"] = datetime.now().strftime("%I:%M %p")
        if "{date}" in template and "date" not in kwargs:
            kwargs["date"] = datetime.now().strftime("%A, %B %d, %Y")

        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    def get_emotion_response(self, emotion: str) -> str:
        """Get a supportive response for the detected emotion."""
        # Try both key names for compatibility
        emotion_responses = self.responses.get("emotion_response",
                            self.responses.get("emotion_responses", {}))
        templates = emotion_responses.get(emotion, [])

        if templates:
            return random.choice(templates)

        # Generic fallback
        if LANGUAGE == "en":
            return "I'm here to listen."
        else:
            return "நான் இருக்கேன், சொல்லுங்க."

    def get_combined_response(self, action_response: str, emotion: str) -> str:
        """
        Build a combined response when the user gives both
        a command and an emotional statement.
        """
        emotion_part = self.get_emotion_response(emotion)
        return f"{action_response}\n\n{emotion_part}"

    def reload(self) -> None:
        self._load()

    # ── private helpers ───────────────────────────────────

    @staticmethod
    def _fallback(category: str) -> str:
        if LANGUAGE == "en":
            return f"I don't have a response for '{category}' right now."
        else:
            return f"Ungal request ({category}) kidaichidhu, aanaa response template illai."
