from __future__ import annotations
from pathlib import Path
from typing import Optional
from ..config import settings

_local_model = None


def _get_local_model():
    global _local_model
    if _local_model is None:
        from faster_whisper import WhisperModel
        _local_model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
    return _local_model


def transcribe(audio_path: Path, language: Optional[str] = None) -> str:
    language = language or settings.default_language or None
    provider = settings.transcribe_provider.lower()
    if provider == "openai":
        return _transcribe_openai(audio_path, language)
    return _transcribe_local(audio_path, language)


def _transcribe_local(audio_path: Path, language: Optional[str]) -> str:
    model = _get_local_model()
    segments, _info = model.transcribe(
        str(audio_path), language=language, vad_filter=True, beam_size=1,
    )
    return "\n".join(seg.text.strip() for seg in segments if seg.text).strip()


def _transcribe_openai(audio_path: Path, language: Optional[str]) -> str:
    from openai import OpenAI
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY required when TRANSCRIBE_PROVIDER=openai")
    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    client = OpenAI(**kwargs)
    with audio_path.open("rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1", file=f, language=language or None, response_format="text",
        )
    return str(resp).strip()
