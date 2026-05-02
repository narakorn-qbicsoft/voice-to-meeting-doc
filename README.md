# 🎙️ Voice-to-Doc

> อัปโหลดเสียงประชุม → ระบบถอดเสียงด้วย Whisper → สรุปด้วย LLM → ดาวน์โหลดเป็น **Word/Markdown/Text**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)

โครงสร้างเรียบง่าย แยก service ชัดเจน เพื่อให้ผู้ใช้ทั่วไปนำไปใช้งานหรือพัฒนาต่อได้ทันที

![demo](https://img.shields.io/badge/UI-Thai-purple) ![demo](https://img.shields.io/badge/Whisper-local%2FAPI-green) ![demo](https://img.shields.io/badge/LLM-OpenAI%2FOllama-orange)

---

## ✨ ฟีเจอร์

- 🎵 อัปโหลดไฟล์เสียง: `mp3, wav, m4a, mp4, webm, ogg, flac, aac` (สูงสุด 200MB)
- 🗣️ ถอดเสียง 2 โหมด:
  - **Local** — `faster-whisper` รันบนเครื่อง ฟรี ไม่ต้องต่อ API
  - **OpenAI Whisper API** — เร็วและแม่นกว่า
- 📝 สรุปเนื้อหาด้วย LLM ตาม template เอกสารประชุม
  - ภาพรวม / หัวข้อ / **การตัดสินใจ** / **Action Items** / ติดตามต่อ
- 💾 ดาวน์โหลดเป็น `.md` / `.docx` / `.txt` พร้อม **Save As dialog** เลือกที่เก็บได้
- 🌐 UI ภาษาไทย, ลากวางไฟล์ได้, แสดง progress
- 🐳 พร้อม Docker / docker-compose
- 🔌 รองรับ provider หลากหลาย: OpenAI, Azure OpenAI, Ollama, OpenRouter

---

## 🚀 เริ่มต้นใน 3 นาที

### Linux/macOS
```bash
git clone https://github.com/<YOUR_USER>/voice-to-doc.git
cd voice-to-doc

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # ใส่ OPENAI_API_KEY

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Windows (PowerShell)
```powershell
git clone https://github.com/<YOUR_USER>/voice-to-doc.git
cd voice-to-doc

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# เปิด .env แก้ OPENAI_API_KEY

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
cp .env.example .env  # แก้ค่าก่อน
docker compose up --build
```

จากนั้นเปิด: **http://localhost:8000**

> 📌 ต้องติดตั้ง [ffmpeg](https://ffmpeg.org/download.html) เพิ่ม (ใช้อ่านไฟล์เสียง)

---

## 📦 โครงสร้างโปรเจกต์

```
voice-to-doc/
├── app/
│   ├── main.py                # FastAPI endpoints
│   ├── config.py              # โหลด .env
│   ├── jobs.py                # in-memory job store
│   └── services/
│       ├── transcription.py   # Whisper (local / OpenAI)
│       ├── summarization.py   # LLM summary
│       └── export.py          # md / docx / txt exporter
├── web/                       # Frontend (HTML+CSS+JS, no build)
├── data/
│   ├── uploads/               # ไฟล์เสียงที่อัปโหลด
│   └── outputs/               # ไฟล์สรุปที่สร้าง
├── samples/                   # ตัวอย่าง script ทดสอบ
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## ⚙️ การตั้งค่าใน `.env`

| ตัวแปร | ค่า | คำอธิบาย |
|---|---|---|
| `TRANSCRIBE_PROVIDER` | `local` / `openai` | ผู้ให้บริการถอดเสียง |
| `WHISPER_MODEL` | `tiny`/`base`/`small`/`medium`/`large-v3` | ขนาดโมเดล (ใหญ่ = แม่นกว่า แต่ช้า) |
| `WHISPER_DEVICE` | `cpu` / `cuda` | ใช้ GPU ถ้ามี |
| `WHISPER_COMPUTE_TYPE` | `int8` / `float16` ฯลฯ | quantization |
| `SUMMARY_PROVIDER` | `openai` / `none` | ตัวสรุป |
| `SUMMARY_MODEL` | `gpt-4o-mini` ฯลฯ | โมเดล LLM |
| `OPENAI_API_KEY` | sk-... | จำเป็นถ้าใช้ openai |
| `OPENAI_BASE_URL` | (เว้นว่าง) | ใส่เพื่อใช้ provider อื่นที่ compatible |
| `MAX_UPLOAD_MB` | `200` | ขนาดไฟล์สูงสุด |
| `DEFAULT_LANGUAGE` | `th` | ภาษาเริ่มต้น |

### 🆓 ตัวอย่าง: รันฟรี 100% (offline)
```ini
TRANSCRIBE_PROVIDER=local
SUMMARY_PROVIDER=none
```

### 🦙 ตัวอย่าง: ใช้ Ollama (LLM ฟรี local) สำหรับสรุป
```ini
SUMMARY_PROVIDER=openai
SUMMARY_MODEL=llama3.1
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
```

### ☁️ ตัวอย่าง: ใช้ OpenAI (เร็วและแม่น)
```ini
TRANSCRIBE_PROVIDER=local        # หรือ openai ถ้ามีงบ
SUMMARY_PROVIDER=openai
SUMMARY_MODEL=gpt-4o-mini        # ราคา ~$0.15/1M tokens
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

---

## 🔌 REST API

| Method | Endpoint | หน้าที่ |
|---|---|---|
| `GET`  | `/api/health` | สถานะ + provider ที่ใช้อยู่ |
| `POST` | `/api/jobs` | อัปโหลดไฟล์ (`file`, `language`) → คืน `job_id` |
| `GET`  | `/api/jobs/{id}` | ดูสถานะ + ผลลัพธ์ |
| `GET`  | `/api/jobs/{id}/download/{md\|docx\|txt}` | ดาวน์โหลดไฟล์สรุป |

ตัวอย่าง:
```bash
curl -F "file=@meeting.mp3" -F "language=th" http://localhost:8000/api/jobs
curl http://localhost:8000/api/jobs/<job_id>
```

📚 Swagger docs อัตโนมัติ: http://localhost:8000/docs

---

## 🧩 ปรับแต่ง / ต่อยอด

- **เปลี่ยนรูปแบบสรุป** — แก้ `SYSTEM_PROMPT` ใน `app/services/summarization.py`
- **เพิ่ม diarization (แยกผู้พูด)** — เปลี่ยนไปใช้ `pyannote.audio` หรือ `whisperX`
- **เก็บงานถาวร** — เปลี่ยน `JobStore` ใน `app/jobs.py` เป็น Redis / SQLite / Postgres
- **รองรับผู้ใช้หลายคน** — เพิ่ม auth (FastAPI Users / OAuth)
- **ส่งสรุปเข้า Notion / Slack / Email** — เพิ่ม service ใหม่ใน `app/services/`
- **อัปเกรดเป็น queue จริงจัง** — เปลี่ยน `BackgroundTasks` เป็น Celery / RQ / Arq

---

## 🤝 Contributing

ยินดีต้อนรับ PR และ Issue ทุกชนิด!

1. Fork repo
2. สร้าง branch: `git checkout -b feature/amazing`
3. Commit: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing`
5. เปิด Pull Request

---

## 📜 License
[MIT](LICENSE) — นำไปใช้ ดัดแปลง และเผยแพร่ต่อได้อย่างอิสระ

## 🙏 Credits
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — speech recognition
- [OpenAI Whisper](https://github.com/openai/whisper) — original model
- [FastAPI](https://fastapi.tiangolo.com/) — web framework
- [python-docx](https://github.com/python-openxml/python-docx) — Word export
