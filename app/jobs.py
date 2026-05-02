from __future__ import annotations
import threading, uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional

JobStatus = Literal["queued", "transcribing", "summarizing", "done", "error"]


@dataclass
class Job:
    id: str
    filename: str
    status: JobStatus = "queued"
    message: str = ""
    transcript: str = ""
    summary: str = ""
    md_path: Optional[str] = None
    docx_path: Optional[str] = None
    txt_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, filename: str) -> Job:
        job = Job(id=uuid.uuid4().hex, filename=filename)
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **fields) -> Optional[Job]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            for k, v in fields.items():
                setattr(job, k, v)
            job.touch()
            return job


store = JobStore()
