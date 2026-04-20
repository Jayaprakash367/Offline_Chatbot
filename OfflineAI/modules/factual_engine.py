"""
=============================================================
  MODULE 12 — FACTUAL ENGINE

  Adds practical factual-answer support by combining:
    - Local knowledge base matches
    - Wikipedia summaries (best-effort, optional internet)

  This module is designed to improve answer correctness without
  breaking offline behavior.
=============================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import requests

from modules.knowledge_base import KnowledgeBase


QUESTION_HINTS = (
    "what",
    "who",
    "where",
    "when",
    "why",
    "how",
    "which",
    "define",
    "explain",
    "tell me about",
)


@dataclass
class FactualContext:
    query: str
    local_answer: str = ""
    local_confidence: float = 0.0
    wiki_title: str = ""
    wiki_summary: str = ""
    wiki_url: str = ""

    def has_any(self) -> bool:
        return bool(self.local_answer or self.wiki_summary)

    def source_label(self) -> str:
        if self.local_answer and self.local_confidence >= 0.65:
            return "knowledge-base"
        if self.wiki_summary:
            return "wikipedia"
        return "none"

    def to_prompt_block(self) -> str:
        lines = []

        if self.local_answer:
            lines.append(
                f"Local Knowledge Base (confidence {self.local_confidence:.2f}): {self.local_answer}"
            )

        if self.wiki_summary:
            lines.append(f"Wikipedia ({self.wiki_title}): {self.wiki_summary}")
            if self.wiki_url:
                lines.append(f"Wikipedia URL: {self.wiki_url}")

        return "\n".join(lines).strip()


class FactualEngine:
    """Builds factual context used by the assistant runtime."""

    def __init__(self, knowledge_base: KnowledgeBase, timeout_seconds: float = 6.0):
        self.knowledge_base = knowledge_base
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self._wiki_cache: dict[str, tuple[str, str, str]] = {}

    def build_context(self, text: str, allow_web: bool = True) -> FactualContext:
        query = (text or "").strip()
        context = FactualContext(query=query)

        if not query:
            return context

        kb_answer, kb_conf = self.knowledge_base.search(query)
        if kb_answer:
            context.local_answer = str(kb_answer).strip()
            context.local_confidence = float(kb_conf)

        if allow_web and self.looks_like_fact_question(query):
            wiki_title, wiki_summary, wiki_url = self._get_wikipedia_context(query)
            context.wiki_title = wiki_title
            context.wiki_summary = wiki_summary
            context.wiki_url = wiki_url

        return context

    @staticmethod
    def looks_like_fact_question(text: str) -> bool:
        text_norm = (text or "").lower().strip()
        if not text_norm:
            return False

        if text_norm.endswith("?"):
            return True

        return any(text_norm.startswith(prefix) for prefix in QUESTION_HINTS)

    # -- wikipedia helpers ---------------------------------------------

    def _get_wikipedia_context(self, query: str) -> tuple[str, str, str]:
        cache_key = re.sub(r"\s+", " ", query.strip().lower())
        if cache_key in self._wiki_cache:
            return self._wiki_cache[cache_key]

        title = self._search_wikipedia_title(query)
        if not title:
            self._wiki_cache[cache_key] = ("", "", "")
            return ("", "", "")

        summary, url = self._fetch_wikipedia_summary(title)
        summary = self._shorten_summary(summary)

        self._wiki_cache[cache_key] = (title, summary, url)
        return (title, summary, url)

    def _search_wikipedia_title(self, query: str) -> str:
        api_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json",
        }

        try:
            response = self.session.get(api_url, params=params, timeout=self.timeout_seconds)
            if response.status_code != 200:
                return ""

            data = response.json()
            if isinstance(data, list) and len(data) >= 2 and data[1]:
                return str(data[1][0]).strip()
        except Exception:
            return ""

        return ""

    def _fetch_wikipedia_summary(self, title: str) -> tuple[str, str]:
        quoted_title = quote(title, safe="")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quoted_title}"

        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            if response.status_code != 200:
                return ("", "")

            data = response.json()
            summary = str(data.get("extract", "")).strip()
            page_url = str(
                data.get("content_urls", {})
                .get("desktop", {})
                .get("page", "")
            ).strip()
            return (summary, page_url)
        except Exception:
            return ("", "")

    @staticmethod
    def _shorten_summary(text: str, max_sentences: int = 2, max_chars: int = 520) -> str:
        raw = (text or "").strip()
        if not raw:
            return ""

        sentences = re.split(r"(?<=[.!?])\s+", raw)
        compact = " ".join(sentences[:max_sentences]).strip()

        if len(compact) > max_chars:
            compact = compact[: max_chars - 3].rstrip() + "..."

        return compact
