from __future__ import annotations
import os
import traceback
from pathlib import Path
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from . import runtime_config as cfg
from .config import OUTPUT_DIR, UPLOAD_DIR
from .jobs import Job, store
from .services.export import export_docx, export_markdown, export_text
from .services.summarization import summarize, test_llm_connection
from .services.transcription import transcribe

ALLOWED_EXT = {".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg", ".flac", ".aac"}
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "").strip()

app = FastAPI(title="Voice-to-Doc", version="0.2.0")
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


# ---------- auth dependency ----------
def require_admin(x_admin_token: Optional[str] = Header(default=None)):
    """ถ้าตั้ง ADMIN_PASSWORD ใน env → ต้องส่ง header X-Admin-Token ตรงกัน
    ถ้าไม่ได้ตั้ง → เปิดให้ทุกคน (สำหรับ dev / single user)"""
    if not ADMIN_PASSWORD:
        return True
    if x_admin_token != ADMIN_PASSWORD:
        raise HTTPException(401, "Admin token required (set X-Admin-Token header)")
    return True


# ---------- pages ----------
@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((WEB_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "version": app.version,
        "transcribe_provider": cfg.get("transcribe_provider"),
        "summary_provider": cfg.get("summary_provider"),
        "summary_model": cfg.get("summary_model"),
        "whisper_model": cfg.get("whisper_model"),
        "auth_required": bool(ADMIN_PASSWORD),
    }


# ---------- settings ----------
@app.get("/api/settings")
def get_settings(_=Depends(require_admin)) -> dict:
    return {
        "settings": cfg.get_all(mask_secrets=True),
        "auth_required": bool(ADMIN_PASSWORD),
        "editable_fields": sorted(cfg.EDITABLE_FIELDS),
    }


@app.post("/api/settings")
def update_settings(patch: dict, _=Depends(require_admin)) -> dict:
    return {"settings": cfg.update(patch)}


@app.post("/api/settings/reset")
def reset_settings(_=Depends(require_admin)) -> dict:
    return {"settings": cfg.reset()}


@app.post("/api/settings/test")
def test_settings(_=Depends(require_admin)) -> dict:
    return test_llm_connection()


# ---------- jobs ----------
@app.post("/api/jobs")
async def create_job(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form(default=""),
) -> dict:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, f"นามสกุลไฟล์ไม่รองรับ ({ext}). รองรับ: {sorted(ALLOWED_EXT)}")
    job = store.create(file.filename or "audio")
    dest = UPLOAD_DIR / f"{job.id}{ext}"
    size = 0
    max_bytes = int(cfg.get("max_upload_mb")) * 1024 * 1024
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, f"ไฟล์ใหญ่เกิน {cfg.get('max_upload_mb')} MB")
            out.write(chunk)
    background.add_task(_process_job, job.id, dest, language or cfg.get("default_language"))
    return {"job_id": job.id, "status": job.status}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "ไม่พบงานนี้")
    return _job_payload(job)


@app.get("/api/jobs/{job_id}/download/{kind}")
def download(job_id: str, kind: str):
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, "ไม่พบงานนี้")
    path_map = {"md": job.md_path, "docx": job.docx_path, "txt": job.txt_path}
    p = path_map.get(kind)
    if not p:
        raise HTTPException(404, "ยังไม่มีไฟล์นี้")
    return FileResponse(p, filename=Path(p).name)


def _process_job(job_id: str, audio_path: Path, language: str) -> None:
    try:
        store.update(job_id, status="transcribing", message="กำลังถอดเสียง...")
        transcript = transcribe(audio_path, language=language or None)
        store.update(job_id, transcript=transcript)
        store.update(job_id, status="summarizing", message="กำลังสรุปเนื้อหา...")
        summary = summarize(transcript)
        base = OUTPUT_DIR / job_id
        md = export_markdown(summary, base.with_suffix(".md"))
        txt = export_text(summary, base.with_suffix(".txt"))
        docx = export_docx(summary, base.with_suffix(".docx"))
        store.update(job_id, status="done", message="เสร็จสิ้น", summary=summary,
                     md_path=str(md), docx_path=str(docx), txt_path=str(txt))
    except Exception as e:
        store.update(job_id, status="error",
                     message=f"{e.__class__.__name__}: {e}\n{traceback.format_exc(limit=2)}")


def _job_payload(job: Job) -> dict:
    return {
        "id": job.id, "filename": job.filename, "status": job.status, "message": job.message,
        "transcript": job.transcript, "summary": job.summary,
        "downloads": {
            "md":   f"/api/jobs/{job.id}/download/md"   if job.md_path   else None,
            "docx": f"/api/jobs/{job.id}/download/docx" if job.docx_path else None,
            "txt":  f"/api/jobs/{job.id}/download/txt"  if job.txt_path  else None,
        },
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


# ---------- sample audio ----------
SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")
