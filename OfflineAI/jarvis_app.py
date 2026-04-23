"""
=============================================================
  JARVIS APPLICATION — Desktop + Web Runtime

  Features:
    - Web UI server (FastAPI)
    - Desktop window mode (pywebview)
    - Offline + online model routing
    - Tamil + English conversational support
    - Emotion-aware replies and command execution
=============================================================
"""

from __future__ import annotations

import argparse
import os
import re
import socket
import sys
import threading
import time
import webbrowser
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure local package imports resolve whether run as script or module.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import APP_VERSION
from modules.command_executor import CommandExecutor
from modules.decision_engine import DecisionEngine
from modules.factual_engine import FactualContext, FactualEngine
from modules.model_router import ModelRouter
from modules.vision_emotion import VisionEmotionDetector
from modules.voice_input import VoiceInput
from modules.voice_output import VoiceOutput


VALID_MODES = {"auto", "offline", "online", "hybrid"}
VALID_PROVIDERS = {"auto", "openai", "ollama"}
VALID_SPEED_PROFILES = {"turbo", "balanced", "quality"}
COMMAND_CONFIDENCE_THRESHOLD = 0.45
ACTION_INTENT_TAGS = {
    "open_app",
    "close_app",
    "shutdown_pc",
    "cancel_shutdown",
    "system_status",
    "time",
    "date",
    "volume_up",
    "volume_down",
    "mute",
    "music",
    "alarm",
    "weather",
}


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    mode: str = Field(default="auto")
    provider: str = Field(default="auto")
    speed_profile: str = Field(default="balanced")
    persona: str = Field(default="JARVIS")
    avatar: str = Field(default="male")
    visual_emotion: str = Field(default="")
    speak: bool = Field(default=False)


class ListenResponse(BaseModel):
    ok: bool
    transcript: str
    message: str


class SpeakRequest(BaseModel):
    text: str = Field(min_length=1, max_length=800)


class VisionEmotionRequest(BaseModel):
    frame: str = Field(min_length=10, max_length=3_000_000)
    source: str = Field(default="camera")


class JarvisRuntime:
    """Stateful runtime wrapper around existing assistant modules."""

    def __init__(self):
        self.engine = DecisionEngine()
        self.command_executor = CommandExecutor()
        self.router = ModelRouter()
        self.factual_engine = FactualEngine(self.engine.knowledge_base)
        self.vision = VisionEmotionDetector()
        self.voice_output = VoiceOutput()
        self.voice_input: Optional[VoiceInput] = None
        self._lock = threading.Lock()

    def chat(
        self,
        message: str,
        mode: str = "auto",
        provider: str = "auto",
        speed_profile: str = "balanced",
        persona: str = "JARVIS",
        visual_emotion: str = "",
        speak: bool = False,
    ) -> dict:
        user_text = (message or "").strip()
        if not user_text:
            raise ValueError("Message is empty")

        mode = self._normalize_mode(mode)
        provider = self._normalize_provider(provider)
        speed_profile = self._normalize_speed_profile(speed_profile)
        language = self.router.language_hint(user_text)

        with self._lock:
            intent_tag, intent_conf, entities = self.engine.intent_detector.detect(user_text)
            emotion, emotion_conf = self.engine.emotion_detector.detect(user_text)

            visual_label = self._normalize_visual_emotion(visual_emotion)
            if visual_label and (emotion == "neutral" or emotion_conf < 0.5):
                emotion = visual_label
                emotion_conf = max(0.55, emotion_conf)

            has_action_command = self._is_action_intent(intent_tag, intent_conf)
            factual_context = self.factual_engine.build_context(
                user_text,
                allow_web=(mode != "offline"),
            )

            source = "offline"
            provider_used = "offline"
            model_used = "rule-based"

            # Keep teaching flow entirely local to preserve deterministic behavior.
            if getattr(self.engine, "_teach_mode", False):
                response = self.engine.process(user_text)
            elif mode == "offline":
                if has_action_command:
                    response = self.engine.process(user_text)
                else:
                    response, source, provider_used, model_used = self._run_offline_intelligent(
                        user_text=user_text,
                        emotion=emotion,
                        factual_context=factual_context,
                    )
            elif mode == "online":
                response, source, provider_used, model_used = self._run_online_first(
                    user_text=user_text,
                    emotion=emotion,
                    provider=provider,
                    speed_profile=speed_profile,
                    persona=persona,
                    factual_context=factual_context,
                )
            elif mode == "hybrid":
                response, source, provider_used, model_used = self._run_hybrid(
                    user_text=user_text,
                    has_action_command=has_action_command,
                    emotion=emotion,
                    provider=provider,
                    speed_profile=speed_profile,
                    persona=persona,
                    factual_context=factual_context,
                )
            else:
                # auto mode: command-intent goes local first, everything else tries online.
                if has_action_command:
                    response = self.engine.process(user_text)
                else:
                    response, source, provider_used, model_used = self._run_online_first(
                        user_text=user_text,
                        emotion=emotion,
                        provider=provider,
                        speed_profile=speed_profile,
                        persona=persona,
                        factual_context=factual_context,
                    )

            response = self._normalize_reply_text(response)

            if speak:
                self.voice_output.speak(self._voice_safe_text(response))

            return {
                "reply": response,
                "mode": mode,
                "source": source,
                "provider": provider_used,
                "model": model_used,
                "language": language,
                "speed_profile": speed_profile,
                "intent": {
                    "tag": intent_tag,
                    "confidence": round(intent_conf, 3),
                    "entities": entities,
                },
                "emotion": {
                    "label": emotion,
                    "confidence": round(emotion_conf, 3),
                },
                "factual": self._factual_payload(factual_context),
                "online": self.router.provider_status(),
            }

    def vision_status(self) -> dict:
        return self.vision.status()

    def detect_visual_emotion(self, frame_data: str) -> dict:
        result = self.vision.detect_from_data_url(frame_data)
        return {
            "ok": result.ok,
            "emotion": result.emotion,
            "confidence": result.confidence,
            "face_count": result.face_count,
            "backend": result.backend,
            "reason": result.reason,
        }

    def listen(self) -> ListenResponse:
        with self._lock:
            if self.voice_input is None:
                self.voice_input = VoiceInput()

            if not self.voice_input.is_mic_available():
                return ListenResponse(
                    ok=False,
                    transcript="",
                    message="Microphone/voice engine is not ready on this machine.",
                )

            transcript = self.voice_input.listen().strip()
            if not transcript:
                return ListenResponse(ok=False, transcript="", message="No speech detected")

            return ListenResponse(ok=True, transcript=transcript, message="Speech captured")

    def speak(self, text: str) -> None:
        with self._lock:
            self.voice_output.speak(self._voice_safe_text(text))

    def config(self) -> dict:
        memory_name = self.engine.memory.get_user_name() or ""
        return {
            "app": "JARVIS",
            "version": APP_VERSION,
            "user_name": memory_name,
            "modes": sorted(VALID_MODES),
            "providers": sorted(VALID_PROVIDERS),
            "speed_profiles": sorted(VALID_SPEED_PROFILES),
            "default_speed_profile": self.router.default_speed_profile,
            "online": self.router.provider_status(),
        }

    def history(self, limit: int = 20) -> list:
        items = self.engine.memory.get_history()
        limit = max(1, min(limit, 100))
        return items[-limit:]

    def system_status(self) -> dict:
        return self.command_executor.get_system_status()

    # -- routing internals ---------------------------------------------

    def _run_online_first(
        self,
        user_text: str,
        emotion: str,
        provider: str,
        speed_profile: str,
        persona: str,
        factual_context: FactualContext,
    ) -> tuple[str, str, str, str]:
        context_turns = self.engine.memory.get_history()
        user_name = self.engine.memory.get_user_name() or ""

        online_result, _ = self.router.generate_online_reply(
            user_text=user_text,
            emotion=emotion,
            user_name=user_name,
            preferred_provider=provider,
            persona_name=persona or "JARVIS",
            context_turns=context_turns,
            factual_context=factual_context.to_prompt_block(),
            response_style="friendly-human",
            speed_profile=speed_profile,
        )

        if online_result:
            response = online_result.text
            self._persist_manual(user_text, response, emotion)
            return (response, "online", online_result.provider, online_result.model)

        factual_reply, factual_source = self._best_factual_reply(factual_context, allow_web=True)
        if factual_reply:
            response = self._friendly_fact_reply(factual_reply, emotion)
            self._persist_manual(user_text, response, emotion)
            return (response, factual_source, "offline", "factual-engine")

        # Fallback to deterministic local decision engine.
        response = self.engine.process(user_text)
        return (response, "offline-fallback", "offline", "rule-based")

    def _run_offline_intelligent(
        self,
        user_text: str,
        emotion: str,
        factual_context: FactualContext,
    ) -> tuple[str, str, str, str]:
        factual_reply, factual_source = self._best_factual_reply(factual_context, allow_web=False)
        if factual_reply:
            response = self._friendly_fact_reply(factual_reply, emotion)
            self._persist_manual(user_text, response, emotion)
            return (response, factual_source, "offline", "factual-engine")

        response = self.engine.process(user_text)
        return (response, "offline", "offline", "rule-based")

    def _run_hybrid(
        self,
        user_text: str,
        has_action_command: bool,
        emotion: str,
        provider: str,
        speed_profile: str,
        persona: str,
        factual_context: FactualContext,
    ) -> tuple[str, str, str, str]:
        if has_action_command:
            command_response = self.engine.process(user_text)

            prompt = (
                "A desktop action has already been handled. "
                f"User said: {user_text}\n"
                f"Action result: {command_response}\n"
                "Now give a brief friendly follow-up that sounds human and supportive."
            )

            online_result, _ = self.router.generate_online_reply(
                user_text=prompt,
                emotion=emotion,
                user_name=self.engine.memory.get_user_name() or "",
                preferred_provider=provider,
                persona_name=persona or "JARVIS",
                context_turns=self.engine.memory.get_history(),
                factual_context="",
                response_style="brief-supportive",
                speed_profile=speed_profile,
            )

            if online_result:
                combined = f"{command_response}\n\n{online_result.text}"
                self._update_last_ai_reply(combined)
                return (combined, "hybrid", online_result.provider, online_result.model)

            return (command_response, "offline", "offline", "rule-based")

        return self._run_online_first(
            user_text=user_text,
            emotion=emotion,
            provider=provider,
            speed_profile=speed_profile,
            persona=persona,
            factual_context=factual_context,
        )

    @staticmethod
    def _normalize_reply_text(text: str) -> str:
        compact = re.sub(r"\s+", " ", str(text or "")).strip()
        return compact

    @staticmethod
    def _voice_safe_text(text: str) -> str:
        speech_text = str(text or "").replace("\n", ". ")
        speech_text = re.sub(r"\s+", " ", speech_text).strip()
        return speech_text

    @staticmethod
    def _friendly_fact_reply(reply: str, emotion: str) -> str:
        clean = re.sub(r"\s+", " ", str(reply or "")).strip()
        if not clean:
            return ""

        if emotion in {"sad", "angry", "fear"}:
            return f"{clean} If you want, I can also guide you step by step."

        return clean

    @staticmethod
    def _best_factual_reply(context: FactualContext, allow_web: bool) -> tuple[str, str]:
        if context.local_answer and context.local_confidence >= 0.65:
            return (context.local_answer, "knowledge-base")

        if allow_web and context.wiki_summary:
            if context.wiki_title:
                return (
                    f"{context.wiki_summary} (Source: Wikipedia - {context.wiki_title})",
                    "wikipedia",
                )
            return (f"{context.wiki_summary} (Source: Wikipedia)", "wikipedia")

        return ("", "none")

    @staticmethod
    def _factual_payload(context: FactualContext) -> dict:
        return {
            "source": context.source_label(),
            "kb_confidence": round(context.local_confidence, 3),
            "kb_used": bool(context.local_answer),
            "wiki_used": bool(context.wiki_summary),
            "wiki_title": context.wiki_title,
            "wiki_url": context.wiki_url,
        }

    def _persist_manual(self, user_text: str, ai_response: str, emotion: str) -> None:
        self.engine.memory.add_to_history(user_text, ai_response)
        if emotion and emotion != "neutral":
            self.engine.memory.store_emotion(emotion)
        self.engine.memory.increment_conversation()

    def _update_last_ai_reply(self, ai_response: str) -> None:
        history = self.engine.memory.data.get("conversation_history", [])
        if history:
            history[-1]["ai"] = ai_response
            self.engine.memory._save()

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        value = (mode or "auto").strip().lower()
        return value if value in VALID_MODES else "auto"

    @staticmethod
    def _is_action_intent(intent_tag: str, intent_conf: float) -> bool:
        return intent_conf >= COMMAND_CONFIDENCE_THRESHOLD and intent_tag in ACTION_INTENT_TAGS

    @staticmethod
    def _normalize_provider(provider: str) -> str:
        value = (provider or "auto").strip().lower()
        return value if value in VALID_PROVIDERS else "auto"

    @staticmethod
    def _normalize_speed_profile(profile: str) -> str:
        value = (profile or "balanced").strip().lower()
        if value in VALID_SPEED_PROFILES:
            return value
        return "balanced"

    @staticmethod
    def _normalize_visual_emotion(emotion: str) -> str:
        value = (emotion or "").strip().lower()
        allowed = {"happy", "sad", "angry", "fear", "neutral"}
        if value in allowed:
            return value
        return ""


# -- FastAPI app wiring -------------------------------------------------

runtime = JarvisRuntime()
app = FastAPI(title="JARVIS Runtime", version=APP_VERSION)

# CORS kept permissive for local desktop/web hybrid use.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(PROJECT_ROOT, "jarvis", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def home():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        raise HTTPException(status_code=500, detail="UI file not found: jarvis/static/index.html")
    return FileResponse(index_file)


@app.get("/api/config")
def api_config():
    cfg = runtime.config()
    cfg["vision"] = runtime.vision_status()
    return cfg


@app.get("/api/history")
def api_history(limit: int = 20):
    return {"history": runtime.history(limit=limit)}


@app.get("/api/system/status")
def api_system_status():
    return runtime.system_status()


@app.post("/api/chat")
def api_chat(payload: ChatRequest):
    try:
        result = runtime.chat(
            message=payload.message,
            mode=payload.mode,
            provider=payload.provider,
            speed_profile=payload.speed_profile,
            persona=payload.persona,
            visual_emotion=payload.visual_emotion,
            speak=payload.speak,
        )
        return result
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Chat error: {ex}") from ex


@app.post("/api/listen", response_model=ListenResponse)
def api_listen():
    try:
        return runtime.listen()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Voice listen error: {ex}") from ex


@app.post("/api/speak")
def api_speak(payload: SpeakRequest):
    try:
        runtime.speak(payload.text)
        return {"ok": True}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Voice speak error: {ex}") from ex


@app.get("/api/vision/status")
def api_vision_status():
    return runtime.vision_status()


@app.post("/api/vision/emotion")
def api_vision_emotion(payload: VisionEmotionRequest):
    try:
        return runtime.detect_visual_emotion(payload.frame)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Vision emotion error: {ex}") from ex


# -- Launch helpers -----------------------------------------------------


def find_open_port(start_port: int) -> int:
    """Return first available TCP port from start_port upward."""
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No free port found in expected range")


def wait_for_server(url: str, timeout_seconds: float = 20.0) -> bool:
    """Poll a URL until responsive or timeout."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=1.5)
            if response.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def launch_desktop_window(host: str, port: int) -> None:
    """Run API/UI server in background and open native desktop window."""
    server_config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
    server = uvicorn.Server(server_config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    app_url = f"http://{host}:{port}/"
    is_ready = wait_for_server(f"{app_url}api/config")

    if not is_ready:
        raise RuntimeError("JARVIS server did not start in time")

    try:
        import webview

        window = webview.create_window(
            title="JARVIS AI Assistant",
            url=app_url,
            width=1460,
            height=920,
            min_size=(1080, 680),
        )
        webview.start(debug=False)
        # pywebview exits after window closes.
        if window:
            server.should_exit = True
    except Exception as ex:
        print(f"[JARVIS] Desktop window failed ({ex}). Opening browser instead...")
        webbrowser.open(app_url)
        thread.join()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch JARVIS desktop/web runtime")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface")
    parser.add_argument("--port", type=int, default=8765, help="Port number")
    parser.add_argument("--desktop", action="store_true", help="Launch as desktop window (pywebview)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload server in development")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    host = args.host
    port = find_open_port(args.port)

    if args.desktop:
        launch_desktop_window(host=host, port=port)
        return

    uvicorn.run(app=app, host=host, port=port, reload=args.reload)


if __name__ == "__main__":
    main()
