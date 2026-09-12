from __future__ import annotations

import shutil
from functools import lru_cache
from pathlib import Path

import whisper


DEFAULT_MODEL = "base"


def _ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg is required for audio/video transcription but was not found on PATH. "
            "Install ffmpeg and restart the terminal. On Windows, you can use: "
            "choco install ffmpeg  OR  winget install Gyan.FFmpeg"
        )


@lru_cache(maxsize=1)
def _load_model():
    # Whisper will use GPU if available (torch).
    return whisper.load_model(DEFAULT_MODEL)


def transcribe_audio_or_video(path: Path) -> str:
    _ensure_ffmpeg()
    model = _load_model()
    result = model.transcribe(str(path), fp16=False)
    return (result.get("text") or "").strip()

