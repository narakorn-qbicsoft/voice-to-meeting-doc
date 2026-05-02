"""
Runtime Configuration Manager
==============================
รวม settings จาก 2 แหล่ง (เรียงลำดับความสำคัญ):
  1. data/config.json   ← ผู้ใช้แก้ผ่านหน้าเว็บ (override .env)
  2. .env               ← ค่าเริ่มต้นจากตอน deploy

- Thread-safe (ใช้ RLock)
- Hot-reload: ทุก service อ่านผ่าน get() จึงเห็นค่าใหม่ทันทีโดยไม่ต้อง restart
- API key ถูก mask เมื่อส่งกลับให้ frontend
"""
from __future__ import annotations
import json
import threading
from typing import Any, Dict
from .config import settings as env_settings, BASE_DIR

CONFIG_PATH = BASE_DIR / "data" / "config.json"

EDITABLE_FIELDS = {
    "transcribe_provider", "whisper_model", "whisper_device", "whisper_compute_type",
    "summary_provider", "summary_model", "openai_api_key", "openai_base_url",
    "max_upload_mb", "default_language",
}
SECRET_FIELDS = {"openai_api_key"}

_lock = threading.RLock()
_overrides: Dict[str, Any] = {}
_dirty_callbacks = []


def _load_from_disk() -> None:
    global _overrides
    if CONFIG_PATH.exists():
        try:
            _overrides = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            _overrides = {}
    else:
        _overrides = {}


def _save_to_disk() -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(_overrides, ensure_ascii=False, indent=2), encoding="utf-8")


def get(key: str) -> Any:
    with _lock:
        if key in _overrides and _overrides[key] not in (None, ""):
            return _overrides[key]
        return getattr(env_settings, key, None)


def get_all(mask_secrets: bool = True) -> Dict[str, Any]:
    with _lock:
        out = {}
        for key in EDITABLE_FIELDS:
            val = get(key)
            if mask_secrets and key in SECRET_FIELDS and val:
                s = str(val)
                out[key] = f"{s[:4]}••••{s[-4:]}" if len(s) > 12 else "••••••••"
                out[f"{key}_set"] = True
            else:
                out[key] = val
                if key in SECRET_FIELDS:
                    out[f"{key}_set"] = bool(val)
        out["_overrides_count"] = len(_overrides)
        out["_config_path"] = str(CONFIG_PATH)
    return out


def update(patch: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        for key, val in patch.items():
            if key not in EDITABLE_FIELDS:
                continue
            if val in (None, ""):
                _overrides.pop(key, None)
            else:
                env_val = getattr(env_settings, key, None)
                if isinstance(env_val, int):
                    try:
                        val = int(val)
                    except Exception:
                        continue
                _overrides[key] = val
        _save_to_disk()
    _notify_change()
    return get_all()


def reset() -> Dict[str, Any]:
    with _lock:
        _overrides.clear()
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()
    _notify_change()
    return get_all()


def on_change(cb) -> None:
    _dirty_callbacks.append(cb)


def _notify_change() -> None:
    for cb in _dirty_callbacks:
        try:
            cb()
        except Exception:
            pass


_load_from_disk()
