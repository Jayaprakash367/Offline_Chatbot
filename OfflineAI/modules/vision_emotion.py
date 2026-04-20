"""
=============================================================
  MODULE 11 — VISION EMOTION DETECTOR

  Camera frame analysis pipeline for face detection + emotion.

  Primary backend:
    - FER (if installed) with OpenCV decoding

  Fallback backend:
    - OpenCV face detection + conservative neutral inference
=============================================================
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from typing import Optional


MAX_FRAME_PAYLOAD_CHARS = 3_000_000


@dataclass
class VisionEmotionResult:
    emotion: str
    confidence: float
    face_count: int
    backend: str
    ok: bool
    reason: str = ""


class VisionEmotionDetector:
    """Detect emotion from camera frames with optional FER integration."""

    def __init__(self):
        self._cv2 = None
        self._np = None
        self._fer_detector = None
        self._backend = "unavailable"
        self._init_error = ""
        self._face_cascade = None
        self._available = False

        self._bootstrap()

    def status(self) -> dict:
        return {
            "available": self._available,
            "backend": self._backend,
            "error": self._init_error,
            "fer_enabled": self._fer_detector is not None,
        }

    def detect_from_data_url(self, data_url: str) -> VisionEmotionResult:
        if not self._available:
            return VisionEmotionResult(
                emotion="neutral",
                confidence=0.0,
                face_count=0,
                backend=self._backend,
                ok=False,
                reason=f"vision backend unavailable: {self._init_error or 'not initialized'}",
            )

        if not data_url:
            return VisionEmotionResult(
                emotion="neutral",
                confidence=0.0,
                face_count=0,
                backend=self._backend,
                ok=False,
                reason="empty frame",
            )

        if len(data_url) > MAX_FRAME_PAYLOAD_CHARS:
            return VisionEmotionResult(
                emotion="neutral",
                confidence=0.0,
                face_count=0,
                backend=self._backend,
                ok=False,
                reason="frame payload too large",
            )

        frame = self._decode_frame(data_url)
        if frame is None:
            return VisionEmotionResult(
                emotion="neutral",
                confidence=0.0,
                face_count=0,
                backend=self._backend,
                ok=False,
                reason="invalid frame payload",
            )

        face_count = self._count_faces(frame)
        if face_count <= 0:
            return VisionEmotionResult(
                emotion="neutral",
                confidence=0.0,
                face_count=0,
                backend=self._backend,
                ok=True,
                reason="no face found",
            )

        if self._fer_detector is not None:
            fer_result = self._detect_with_fer(frame)
            if fer_result is not None:
                fer_result.face_count = face_count
                return fer_result

        # Conservative fallback: without FER we do not fake high-confidence emotions.
        return VisionEmotionResult(
            emotion="neutral",
            confidence=0.35,
            face_count=face_count,
            backend=self._backend,
            ok=True,
            reason="fallback neutral inference",
        )

    # -- internals ------------------------------------------------------

    def _bootstrap(self) -> None:
        try:
            import cv2  # type: ignore
            import numpy as np  # type: ignore

            self._cv2 = cv2
            self._np = np

            self._face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            self._available = True
            self._backend = "opencv"

            try:
                from fer import FER  # type: ignore

                self._fer_detector = FER(mtcnn=False)
                self._backend = "opencv+fer"
            except Exception as ex:
                # FER is optional; keep OpenCV-only mode active.
                self._fer_detector = None
                self._init_error = f"FER optional dependency not ready: {ex}"
        except Exception as ex:
            self._available = False
            self._backend = "unavailable"
            self._init_error = str(ex)

    def _decode_frame(self, data_url: str):
        if self._np is None or self._cv2 is None:
            return None

        # Accept both data URLs and raw base64.
        payload = data_url
        if "," in data_url and data_url.lower().startswith("data:image"):
            payload = data_url.split(",", 1)[1]

        try:
            raw = base64.b64decode(payload, validate=True)
        except (binascii.Error, ValueError):
            return None

        np_arr = self._np.frombuffer(raw, dtype=self._np.uint8)
        frame = self._cv2.imdecode(np_arr, self._cv2.IMREAD_COLOR)
        return frame

    def _count_faces(self, frame) -> int:
        if self._cv2 is None or self._face_cascade is None:
            return 0

        gray = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.25,
            minNeighbors=5,
            minSize=(70, 70),
        )
        return int(len(faces))

    def _detect_with_fer(self, frame) -> Optional[VisionEmotionResult]:
        if self._fer_detector is None or self._cv2 is None:
            return None

        try:
            rgb = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
            detections = self._fer_detector.detect_emotions(rgb)
            if not detections:
                return None

            emotions = detections[0].get("emotions", {})
            if not emotions:
                return None

            emotion, confidence = max(emotions.items(), key=lambda kv: kv[1])

            # Map FER labels to project labels for compatibility.
            emotion = self._normalize_emotion_label(str(emotion).lower().strip())

            return VisionEmotionResult(
                emotion=emotion,
                confidence=round(float(confidence), 3),
                face_count=0,
                backend=self._backend,
                ok=True,
                reason="",
            )
        except Exception:
            return None

    @staticmethod
    def _normalize_emotion_label(label: str) -> str:
        mapping = {
            "surprise": "happy",
            "disgust": "angry",
            "fear": "fear",
            "sad": "sad",
            "happy": "happy",
            "angry": "angry",
            "neutral": "neutral",
        }
        return mapping.get(label, "neutral")
