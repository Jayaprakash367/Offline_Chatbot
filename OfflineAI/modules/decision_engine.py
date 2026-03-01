"""
=============================================================
  MODULE 4 — DECISION ENGINE (Core Brain)
  Orchestrates ALL other modules.
  Implements DUAL-MODE intelligence:
    • Command → execute
    • Emotion → comfort
    • Both   → do BOTH simultaneously
  Enforces security at every decision point.
=============================================================
"""

from datetime import datetime
from typing import Optional

from config import BLOCKED_KEYWORDS, MAX_INPUT_LENGTH

from modules.intent_detector import IntentDetector
from modules.emotion_detector import EmotionDetector
from modules.command_executor import CommandExecutor
from modules.response_engine import ResponseEngine
from modules.knowledge_base import KnowledgeBase
from modules.memory import Memory


class DecisionEngine:
    """
    The central brain that:
    1. Validates input (security)
    2. Detects intent AND emotion in parallel
    3. Decides what to do
    4. Returns a response string
    """

    def __init__(self):
        self.intent_detector = IntentDetector()
        self.emotion_detector = EmotionDetector()
        self.command_executor = CommandExecutor()
        self.response_engine = ResponseEngine()
        self.knowledge_base = KnowledgeBase()
        self.memory = Memory()
        self._teach_mode = False  # waiting for Q&A pair

    # ── main entry point ──────────────────────────────────

    def process(self, user_input: str) -> str:
        """
        Process user input end-to-end and return the AI's response text.
        """
        # ── 1. SECURITY GATE ─────────────────────────────
        if not self._is_safe(user_input):
            return self.response_engine.get("safety_block")

        # Store raw input for handlers
        self._last_input = user_input

        # ── 2. TEACH MODE (if previously activated) ──────
        if self._teach_mode:
            return self._handle_teach(user_input)

        # ── 3. PARALLEL ANALYSIS ─────────────────────────
        intent_tag, intent_conf, entities = self.intent_detector.detect(user_input)
        emotion, emotion_conf = self.emotion_detector.detect(user_input)

        has_command = intent_tag != "unknown" and intent_conf >= 0.45
        has_emotion = emotion != "neutral" and emotion_conf >= 0.3

        # ── 4. DUAL-MODE DECISION ────────────────────────
        response = ""

        if has_command and has_emotion:
            # BOTH: execute command AND comfort
            cmd_response = self._handle_intent(intent_tag, entities)
            response = self.response_engine.get_combined_response(cmd_response, emotion)
        elif has_command:
            # Command only
            response = self._handle_intent(intent_tag, entities)
        elif has_emotion:
            # Emotion only
            response = self.response_engine.get_emotion_response(emotion)
        else:
            # Try knowledge base before giving up
            answer, kb_conf = self.knowledge_base.search(user_input)
            if answer:
                response = answer
            else:
                response = self.response_engine.get("unknown")

        # ── 5. PERSIST ───────────────────────────────────
        self.memory.add_to_history(user_input, response)
        if has_emotion:
            self.memory.store_emotion(emotion)
        self.memory.increment_conversation()

        return response

    # ── intent handlers ───────────────────────────────────

    def _handle_intent(self, tag: str, entities: dict) -> str:

        if tag == "greeting":
            name = self.memory.get_user_name()
            user_lower = self._last_input.lower().strip() if hasattr(self, '_last_input') else ""
            # Time-of-day aware greetings
            if "good morning" in user_lower:
                greeting = f"Good morning{', ' + name if name else ''}! How are you today?"
            elif "good afternoon" in user_lower:
                greeting = f"Good afternoon{', ' + name if name else ''}! How can I help you?"
            elif "good evening" in user_lower:
                greeting = f"Good evening{', ' + name if name else ''}! What can I do for you?"
            elif "good night" in user_lower:
                greeting = f"Good night{', ' + name if name else ''}! Sleep well and take care!"
            else:
                greeting = self.response_engine.get("greeting")
                if name:
                    greeting = greeting.replace("!", f", {name}!", 1)
            return greeting

        if tag == "farewell":
            user_lower = self._last_input.lower().strip() if hasattr(self, '_last_input') else ""
            if "good night" in user_lower:
                name = self.memory.get_user_name()
                return f"Good night{', ' + name if name else ''}! Sleep well and take care!"
            return self.response_engine.get("farewell")

        if tag == "thanks":
            return self.response_engine.get("thanks")

        if tag == "identity":
            return self.response_engine.get("identity")

        if tag == "help":
            return self.response_engine.get("help")

        if tag == "time":
            return self.response_engine.get("time",
                                            time=datetime.now().strftime("%I:%M %p"))

        if tag == "date":
            return self.response_engine.get("date",
                                            date=datetime.now().strftime("%A, %B %d, %Y"))

        if tag == "joke":
            return self.response_engine.get("joke")

        if tag == "open_app":
            app = entities.get("app", "")
            success, msg = self.command_executor.open_app(app)
            if success:
                return self.response_engine.get("open_app_success", app=msg)
            else:
                return self.response_engine.get("open_app_fail", app=app)

        if tag == "close_app":
            app = entities.get("app", "")
            success, msg = self.command_executor.close_app(app)
            if success:
                return self.response_engine.get("close_app_success", app=msg)
            else:
                return self.response_engine.get("close_app_fail", app=app)

        if tag == "system_status":
            status = self.command_executor.get_system_status()
            return self.response_engine.get(
                "system_status",
                cpu=status["cpu"],
                ram=status["ram"],
                battery=status["battery"],
            )

        if tag == "question":
            # Search with full query first, then topic alone
            user_text = self._last_input if hasattr(self, '_last_input') else ""
            answer, conf = self.knowledge_base.search(user_text)
            if answer:
                return answer
            topic = entities.get("topic", "")
            if topic:
                answer, conf = self.knowledge_base.search(topic)
                if answer:
                    return answer
            return "I don't know the answer to that. If you'd like to teach me, just type 'teach'!"

        if tag == "teach":
            self._teach_mode = True
            return self.response_engine.get("teach_prompt")

        if tag == "name_set":
            # Extract name from entities or raw text
            import re
            name = ""
            # Try common Tamil/English patterns
            for pat in [r"my name is (.+)", r"call me (.+)", r"i am (.+)",
                        r"en peyar (.+)", r"என் பெயர் (.+)"]:
                m = re.search(pat, self._last_input if hasattr(self, '_last_input') else "", re.IGNORECASE)
                if m:
                    name = m.group(1).strip()
                    break
            if not name:
                # Fallback: use whatever entities we got, or last word
                last_words = self._last_input.split()[-1] if hasattr(self, '_last_input') else ""
                words = (entities.get("name", "") or last_words).strip()
                name = words
            if name:
                self.memory.set_user_name(name)
                return self.response_engine.get("name_set", name=name)
            return "I couldn't catch your name. Could you try again? Say 'my name is ...' or 'call me ...'"

        if tag == "mood_check":
            return self.response_engine.get("mood_check")

        if tag == "compliment":
            return self.response_engine.get("compliment")

        if tag == "insult":
            return self.response_engine.get("insult")

        if tag == "weather":
            return self.response_engine.get("weather")

        if tag == "music":
            return self.response_engine.get("music")

        if tag == "alarm":
            return self.response_engine.get("alarm")

        if tag == "language_change":
            return self.response_engine.get("language_change")

        if tag == "repeat":
            # Try to return last response from history
            hist = self.memory.get_history()
            if hist and len(hist) > 0:
                last = hist[-1]
                if isinstance(last, dict) and "ai" in last:
                    return f"Last response: {last['ai']}"
            return self.response_engine.get("repeat")

        if tag == "age":
            return self.response_engine.get("age")

        if tag in ("volume_up", "volume_down", "mute"):
            return self.response_engine.get(tag)

        # Fallback
        return self.response_engine.get("unknown")

    # ── teaching handler ──────────────────────────────────

    def _handle_teach(self, text: str) -> str:
        """Parse 'question | answer' or 'Question: ... Answer: ...' and store it."""
        self._teach_mode = False

        # Try pipe-separated format first: question | answer
        if "|" in text:
            parts = text.split("|", 1)
            if len(parts) == 2:
                question = parts[0].strip()
                answer = parts[1].strip()
                if question and answer:
                    self.knowledge_base.add_entry(question, answer)
                    self.memory.learn_fact(question, answer)
                    return self.response_engine.get("teach_success")

        # Try Question: ... Answer: ... format
        parts_q = text.lower().split("question:")
        parts_a = text.lower().split("answer:")

        if len(parts_q) >= 2 and len(parts_a) >= 2:
            q_start = text.lower().index("question:") + len("question:")
            a_start = text.lower().index("answer:") + len("answer:")
            a_marker = text.lower().index("answer:")

            question = text[q_start:a_marker].strip()
            answer = text[a_start:].strip()

            if question and answer:
                self.knowledge_base.add_entry(question, answer)
                self.memory.learn_fact(question, answer)
                return self.response_engine.get("teach_success")

        return ("I didn't understand the format. Please try like this:\n"
                "What is Python | Python is a programming language")

    # ── security ──────────────────────────────────────────

    @staticmethod
    def _is_safe(text: str) -> bool:
        """Validate that user input passes all safety checks."""
        if not text or len(text) > MAX_INPUT_LENGTH:
            return False
        lower = text.lower()
        for blocked in BLOCKED_KEYWORDS:
            if blocked in lower:
                return False
        return True
