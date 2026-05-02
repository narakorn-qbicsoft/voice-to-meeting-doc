from __future__ import annotations
from pathlib import Path
from typing import Optional
from .. import runtime_config as cfg

_local_model = None
_local_model_key = None  # cache key (model+device+compute) เพื่อ invalidate เมื่อเปลี่ยน config


def _invalidate_model() -> None:
    global _local_model, _local_model_key
    _local_model = None
    _local_model_key = None


cfg.on_change(_invalidate_model)


def _get_local_model():
    global _local_model, _local_model_key
    key = (cfg.get("whisper_model"), cfg.get("whisper_device"), cfg.get("whisper_compute_type"))
    if _local_model is None or _local_model_key != key:
        from faster_whisper import WhisperModel
        _local_model = WhisperModel(
            model_size_or_path=key[0],
            device=key[1],
            compute_type=key[2],
        )
        _local_model_key = key
    return _local_model


def transcribe(audio_path: Path, language: Optional[str] = None) -> str:
    language = language or cfg.get("default_language") or None
    provider = (cfg.get("transcribe_provider") or "local").lower()
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
    api_key = cfg.get("openai_api_key")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY required when TRANSCRIBE_PROVIDER=openai")
    kwargs = {"api_key": api_key}
    base_url = cfg.get("openai_base_url")
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    with audio_path.open("rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1", file=f, language=language or None, response_format="text",
        )
    return str(resp).strip()
