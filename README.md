# 🎙️ Voice-to-Meeting-Doc

> **เปลี่ยนเสียงประชุมเป็นเอกสารสรุปอัตโนมัติ** — อัปโหลดไฟล์เสียง รอไม่กี่นาที ได้สรุปการประชุมครบถ้วนพร้อมดาวน์โหลดเป็น Word

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Whisper](https://img.shields.io/badge/Whisper-faster--whisper-purple)](https://github.com/SYSTRAN/faster-whisper)

---

## 📋 สารบัญ

- [คุณสมบัติของแอป](#-คุณสมบัติของแอป)
- [ภาพรวมการทำงาน](#-ภาพรวมการทำงาน)
- [ความต้องการของระบบ](#-ความต้องการของระบบ)
- [การติดตั้ง (Step-by-step)](#-การติดตั้ง-step-by-step)
  - [วิธีที่ 1: Linux / macOS](#วิธีที่-1-linux--macos)
  - [วิธีที่ 2: Windows](#วิธีที่-2-windows)
  - [วิธีที่ 3: Docker (ง่ายสุด)](#วิธีที่-3-docker-ง่ายสุด)
- [การตั้งค่า .env](#%EF%B8%8F-การตั้งค่า-env)
- [วิธีใช้งาน](#-วิธีใช้งาน)
- [การแก้ปัญหาที่พบบ่อย](#-การแก้ปัญหาที่พบบ่อย)
- [API Documentation](#-api-documentation)
- [การพัฒนาต่อ](#-การพัฒนาต่อ)

---

## ✨ คุณสมบัติของแอป

### 🎯 ฟีเจอร์หลัก

| ฟีเจอร์ | รายละเอียด |
|---------|------------|
| 🎵 **อัปโหลดเสียงหลายฟอร์แมต** | รองรับ `mp3`, `wav`, `m4a`, `mp4`, `webm`, `ogg`, `flac`, `aac` (สูงสุด 200 MB) |
| 🗣️ **ถอดเสียงด้วย AI** | ใช้ OpenAI Whisper — รองรับภาษาไทย/อังกฤษ/อัตโนมัติ 100+ ภาษา |
| 📝 **สรุปอัจฉริยะ** | ใช้ LLM สรุปตามรูปแบบเอกสารประชุมมาตรฐาน |
| 💾 **Export 3 ฟอร์แมต** | Microsoft Word (`.docx`), Markdown (`.md`), Text (`.txt`) |
| 🖱️ **Save As Dialog** | เลือกที่เก็บไฟล์เองได้ (Chrome/Edge) |
| 🌐 **UI ภาษาไทย** | ใช้งานง่าย, ลากวางไฟล์ได้, แสดง progress real-time |
| 🐳 **Docker Ready** | Deploy ง่าย รันได้ทุกที่ |
| 🔌 **Plug & Play AI Provider** | สลับระหว่าง OpenAI / Ollama / Azure / OpenRouter ได้ทันที |
| 🆓 **โหมดฟรี 100%** | รันแบบ offline ได้ ไม่ต้องเสียค่า API |

### 📄 รูปแบบเอกสารสรุปที่ได้

แอปจะสร้างเอกสารสรุปการประชุมตาม template มาตรฐาน:

```markdown
# สรุปการประชุม

## ภาพรวม
(2-4 ประโยค สรุปวัตถุประสงค์และผลลัพธ์หลัก)

## ผู้เข้าร่วม
- คุณสมชาย, คุณสมหญิง, ...

## หัวข้อที่หารือ
- หัวข้อ 1: รายละเอียด
- หัวข้อ 2: รายละเอียด

## การตัดสินใจสำคัญ
- ตัดสินใจ 1
- ตัดสินใจ 2

## Action Items
| # | งานที่ต้องทำ | ผู้รับผิดชอบ | กำหนดส่ง |
|---|--------------|---------------|-----------|
| 1 | ...          | คุณสมชาย      | 30 มิ.ย.  |

## ประเด็นค้างคา / ติดตามต่อ
- ...
```

### 🤖 AI Providers ที่รองรับ

| Provider | ใช้สำหรับ | ค่าใช้จ่าย | ความเร็ว | คุณภาพ |
|----------|-----------|-----------|---------|--------|
| **faster-whisper (local)** | ถอดเสียง | 🆓 ฟรี | 🐢 ช้า (CPU) | ⭐⭐⭐⭐ |
| **OpenAI Whisper API** | ถอดเสียง | 💰 $0.006/นาที | ⚡ เร็ว | ⭐⭐⭐⭐⭐ |
| **OpenAI GPT-4o-mini** | สรุป | 💰 ~$0.0003/ประชุม | ⚡⚡ เร็วมาก | ⭐⭐⭐⭐⭐ |
| **Ollama (gemma/llama)** | สรุป | 🆓 ฟรี | 🐢 ขึ้นกับเครื่อง | ⭐⭐⭐⭐ |
| **Azure OpenAI** | สรุป | 💰 ตามแพลน | ⚡ เร็ว | ⭐⭐⭐⭐⭐ |
| **OpenRouter / Groq** | สรุป | 💰 ราคาถูก/ฟรี | ⚡⚡ เร็ว | ⭐⭐⭐⭐ |

---

## 🔄 ภาพรวมการทำงาน

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────────┐
│ 🎵 ไฟล์เสียง   │ ──▶ │ 🗣️ ถอดเสียง  │ ──▶ │ 🤖 LLM สรุป  │ ──▶ │ 📄 เอกสาร       │
│ MP3/WAV/M4A    │     │ Whisper      │     │ GPT/Llama   │     │ DOCX/MD/TXT    │
└─────────────────┘     └──────────────┘     └──────────────┘     └─────────────────┘
                            ~30 วิ              ~5-10 วิ
```

**Pipeline ทำงานเบื้องหลัง (ไม่ block UI):**
1. ผู้ใช้อัปโหลดไฟล์ → ระบบบันทึกลง `data/uploads/`
2. สร้าง Job ID ส่งคืนผู้ใช้ทันที
3. Background task เริ่มถอดเสียง (status: `transcribing`)
4. ส่ง transcript ให้ LLM สรุป (status: `summarizing`)
5. แปลงเป็น `.md`/`.docx`/`.txt` เก็บใน `data/outputs/`
6. หน้าเว็บ poll status ทุก 1.5 วิ → แสดงผลและปุ่มดาวน์โหลด

---

## 💻 ความต้องการของระบบ

### Software ที่จำเป็น

| โปรแกรม | เวอร์ชัน | หน้าที่ |
|---------|----------|--------|
| **Python** | 3.10 ขึ้นไป | รันแอป |
| **ffmpeg** | ใดก็ได้ | อ่าน/แปลงไฟล์เสียง |
| **Git** | ใดก็ได้ | clone repo |

### Hardware แนะนำ

| โหมด | RAM | CPU | Disk | GPU |
|------|-----|-----|------|-----|
| **OpenAI ทุกอย่าง** (เร็วสุด) | 2 GB | 2 cores | 1 GB | ไม่ต้อง |
| **Whisper local + OpenAI สรุป** | 4 GB | 4 cores | 2 GB | ไม่ต้อง |
| **Ollama ทุกอย่าง (ฟรี)** | 8-16 GB | 8 cores | 10 GB | แนะนำมี (NVIDIA) |

---

## 🚀 การติดตั้ง (Step-by-step)

### วิธีที่ 1: Linux / macOS

#### ขั้นที่ 1: ติดตั้ง dependencies ของระบบ

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg git
```

**macOS** (ต้องมี [Homebrew](https://brew.sh)):
```bash
brew install python ffmpeg git
```

#### ขั้นที่ 2: Clone repository

```bash
git clone https://github.com/narakorn-qbicsoft/voice-to-meeting-doc.git
cd voice-to-meeting-doc
```

#### ขั้นที่ 3: สร้าง Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> 💡 ทุกครั้งที่เปิด terminal ใหม่ ต้อง `source .venv/bin/activate` ก่อน

#### ขั้นที่ 4: ติดตั้ง Python packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> ⏱️ ใช้เวลา 3-10 นาที (มีโหลด `faster-whisper`, `torch` ขนาดใหญ่)

#### ขั้นที่ 5: ตั้งค่า .env

```bash
cp .env.example .env
nano .env       # หรือ vim / vi / vscode
```

ใส่ `OPENAI_API_KEY` ที่ได้จาก https://platform.openai.com/api-keys (ถ้าใช้ OpenAI)

#### ขั้นที่ 6: รันแอป

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

เปิดเบราว์เซอร์ไปที่ **http://localhost:8000** หรือ **http://<IP-เครื่อง>:8000**

#### 🔁 รันแบบ background (ไม่ปิดเมื่อปิด terminal)

```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
echo $! > app.pid

# ดู log
tail -f app.log

# หยุด
kill $(cat app.pid)
```

---

### วิธีที่ 2: Windows

#### ขั้นที่ 1: ติดตั้ง dependencies

1. **Python 3.10+**: ดาวน์โหลดจาก https://www.python.org/downloads/ → ติดตั้งโดย ✅ "Add Python to PATH"
2. **Git**: https://git-scm.com/download/win
3. **ffmpeg**:
   - ดาวน์โหลด from https://www.gyan.dev/ffmpeg/builds/ (เลือก `release essentials`)
   - แตก zip ไว้ที่ `C:\ffmpeg`
   - เพิ่ม `C:\ffmpeg\bin` ลงใน PATH (System Environment Variables)
   - ทดสอบ: เปิด PowerShell ใหม่ → รัน `ffmpeg -version`

#### ขั้นที่ 2: Clone และติดตั้ง

เปิด **PowerShell**:

```powershell
git clone https://github.com/narakorn-qbicsoft/voice-to-meeting-doc.git
cd voice-to-meeting-doc

python -m venv .venv
.venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

#### ขั้นที่ 3: ตั้งค่าและรัน

```powershell
copy .env.example .env
notepad .env       # แก้ OPENAI_API_KEY แล้ว save

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

เปิดเบราว์เซอร์ → **http://localhost:8000**

---

### วิธีที่ 3: Docker (ง่ายสุด)

> ✅ ไม่ต้องติดตั้ง Python หรือ ffmpeg เอง

#### ขั้นที่ 1: ติดตั้ง Docker
- Linux: https://docs.docker.com/engine/install/
- Windows/Mac: https://www.docker.com/products/docker-desktop/

#### ขั้นที่ 2: รัน

```bash
git clone https://github.com/narakorn-qbicsoft/voice-to-meeting-doc.git
cd voice-to-meeting-doc

cp .env.example .env
nano .env       # แก้ OPENAI_API_KEY

docker compose up -d --build
```

ดู log:
```bash
docker compose logs -f
```

หยุด:
```bash
docker compose down
```

เปิด **http://localhost:8000**

---


---

## 🎛️ ตั้งค่าจากหน้าเว็บ (Settings UI) ✨ ใหม่ใน v0.2

ตั้งแต่ **v0.2.0** ไม่ต้องแก้ `.env` แล้ว! กดปุ่ม **⚙️ ตั้งค่า** มุมขวาบนของหน้าเว็บได้เลย:

### คุณสมบัติของหน้า Settings
- ✅ **เปลี่ยน AI Provider / Model / API Key / Base URL** ได้จากเว็บ
- ✅ **Hot-reload** — กด บันทึก แล้วมีผลทันที **ไม่ต้อง restart server**
- ✅ **🧪 ปุ่ม Test Connection** — ทดสอบว่า key/model ใช้งานได้จริง ก่อนบันทึก
- ✅ **🎚️ Preset 5 ชุด** — กดปุ่มเดียวเปลี่ยนเป็น OpenAI / Ollama / Groq / OpenRouter / Local-only
- ✅ **🔐 API Key ถูก mask** เมื่อแสดงผล (แสดงแค่ `sk-p••••B94A`)
- ✅ **↩️ Reset** กลับไปใช้ค่า `.env` ได้ตลอด
- ✅ **🔒 Admin Token** ป้องกันคนภายนอกแก้ (ถ้าตั้ง `ADMIN_PASSWORD` ใน env)

### การทำงานเบื้องหลัง

```
ลำดับความสำคัญ:  data/config.json (override)  >  .env (default)
```

ค่าที่ user แก้ผ่านเว็บจะเก็บที่ `data/config.json` (ถูก gitignore แล้ว) ทับค่าจาก `.env`
ลบไฟล์นี้ = กลับไปใช้ค่า `.env`

### ป้องกันคนอื่นมาแก้ Settings (Production)

ตั้ง `ADMIN_PASSWORD` ใน `.env`:
```ini
ADMIN_PASSWORD=my-strong-password-2026
```
หลัง restart → user จะต้องใส่ token นี้ในช่อง "Admin Token" ก่อนแก้ค่าใด ๆ
(token เก็บใน browser localStorage)

### API Endpoints ของ Settings

| Method | Endpoint | คำอธิบาย |
|--------|----------|----------|
| `GET`  | `/api/settings` | ดูค่าปัจจุบัน (API key ถูก mask) |
| `POST` | `/api/settings` | อัปเดต (body: JSON เช่น `{"summary_model":"gpt-4o"}`) |
| `POST` | `/api/settings/test` | ทดสอบ LLM connection ปัจจุบัน |
| `POST` | `/api/settings/reset` | ลบ override ทั้งหมด กลับไปใช้ `.env` |

> ทุก endpoint ต้องมี header `X-Admin-Token: <password>` ถ้าตั้ง `ADMIN_PASSWORD`

---

## ⚙️ การตั้งค่า .env (Default values)

> ค่าใน `.env` ใช้เป็น **default** ตอนเริ่มแอป — override ได้จากหน้า Settings UI ในเว็บ

### ตัวเลือกทั้งหมด

```ini
# ===== Transcription (ถอดเสียง) =====
TRANSCRIBE_PROVIDER=local          # local | openai
WHISPER_MODEL=small                # tiny|base|small|medium|large-v3
WHISPER_DEVICE=cpu                 # cpu | cuda
WHISPER_COMPUTE_TYPE=int8          # int8|int8_float16|float16|float32

# ===== Summarization (สรุป) =====
SUMMARY_PROVIDER=openai            # openai | none
SUMMARY_MODEL=gpt-4o-mini

# ===== API Keys =====
OPENAI_API_KEY=sk-xxxxxxxxxx
OPENAI_BASE_URL=                   # เว้นว่าง = ใช้ OpenAI ทางการ

# ===== App =====
MAX_UPLOAD_MB=200
DEFAULT_LANGUAGE=th
```

### 📋 สูตรสำเร็จตามสถานการณ์

#### 🆓 แบบประหยัดสุด (ฟรี 100% ออฟไลน์)
```ini
TRANSCRIBE_PROVIDER=local
WHISPER_MODEL=small
SUMMARY_PROVIDER=none              # แสดงเฉพาะ transcript ไม่สรุป
```

#### 🦙 ใช้ Ollama รันสรุปฟรีบนเครื่อง
```ini
TRANSCRIBE_PROVIDER=local
SUMMARY_PROVIDER=openai
SUMMARY_MODEL=gemma3:4b            # หรือ llama3.1, qwen2.5
OPENAI_API_KEY=ollama              # ใส่อะไรก็ได้
OPENAI_BASE_URL=http://localhost:11434/v1
```
> ต้องลง Ollama ก่อน: `curl -fsSL https://ollama.com/install.sh | sh && ollama pull gemma3:4b`

#### ⚡ แบบเร็วและแม่นที่สุด (เสียเงิน)
```ini
TRANSCRIBE_PROVIDER=openai         # API Whisper เร็วกว่า local
SUMMARY_PROVIDER=openai
SUMMARY_MODEL=gpt-4o-mini          # หรือ gpt-4o ถ้าต้องการคุณภาพสูงสุด
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OPENAI_BASE_URL=
```

#### 🌐 ใช้ Groq (ฟรี + เร็วมาก)
```ini
SUMMARY_PROVIDER=openai
SUMMARY_MODEL=llama-3.3-70b-versatile
OPENAI_API_KEY=gsk_xxxxxxxxxxxx    # จาก https://console.groq.com
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

---

## 📖 วิธีใช้งาน

1. เปิดเบราว์เซอร์ไปที่ **http://localhost:8000** (หรือ IP server)
2. **ลากไฟล์เสียง** เข้าไปในกล่องสีดำ (หรือคลิกเพื่อเลือก)
3. เลือก **ภาษา** (ไทย/อังกฤษ/อัตโนมัติ)
4. กดปุ่ม **"เริ่มประมวลผล"**
5. รอ progress bar (ครั้งแรก Whisper จะดาวน์โหลดโมเดล ~500 MB)
6. เมื่อเสร็จจะเห็น:
   - **สรุปการประชุม** (Markdown แสดงผล)
   - **บทถอดเสียงเต็ม** (กดเปิดดูได้)
   - ปุ่มดาวน์โหลด **3 ฟอร์แมต**
7. กดปุ่มดาวน์โหลด → เลือกที่เก็บไฟล์ในเครื่อง

### ⏱️ เวลาที่ใช้โดยประมาณ

| ความยาวเสียง | Whisper local (CPU) | Whisper API | สรุป (gpt-4o-mini) |
|--------------|---------------------|-------------|---------------------|
| 5 นาที | ~1 นาที | ~10 วิ | ~5 วิ |
| 30 นาที | ~5-8 นาที | ~30 วิ | ~10 วิ |
| 1 ชั่วโมง | ~10-15 นาที | ~1 นาที | ~15 วิ |

---

## 🚨 การแก้ปัญหาที่พบบ่อย

### ❌ `ModuleNotFoundError: No module named 'fastapi'`
**สาเหตุ:** ลืม activate virtual environment
```bash
source .venv/bin/activate    # Linux/Mac
.venv\Scripts\activate       # Windows
```

### ❌ `ffmpeg: command not found` หรือ Whisper ถอดเสียงไม่ได้
**สาเหตุ:** ไม่มี ffmpeg
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: ดาวน์โหลดจาก gyan.dev แล้วเพิ่ม PATH
```

### ❌ `Address already in use` (port 8000 ถูกใช้)
ใช้ port อื่น:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8888
```

### ❌ `OPENAI_API_KEY required when SUMMARY_PROVIDER=openai`
ลืมใส่ API key ใน `.env` หรือใส่ key ผิด
```bash
nano .env
# แก้ OPENAI_API_KEY=sk-xxxxxxxxx ให้เป็น key จริง
# Restart แอป
```

### ❌ ค้างนานที่ "กำลังสรุป..."
- ถ้าใช้ Ollama บน CPU → ช้าปกติ ลองโมเดลเล็กลงเช่น `gemma3:1b`
- ใช้ OpenAI / Groq เร็วกว่ามาก

### ❌ เปิดเว็บจากเครื่องอื่นในวงแลนไม่ได้
1. ตรวจ `--host 0.0.0.0` (ไม่ใช่ `127.0.0.1`)
2. เปิด firewall:
   ```bash
   sudo ufw allow 8000/tcp                                       # Ubuntu
   New-NetFirewallRule -DisplayName "Voice-to-Doc" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow   # Windows (Admin)
   ```

### ❌ "Save As dialog" ไม่ขึ้น (ดาวน์โหลดเข้า Downloads เลย)
- ใช้ **Chrome** หรือ **Edge** (Firefox/Safari ไม่รองรับ)
- ต้องเข้าผ่าน `https://` หรือ `http://localhost` หรือ private IP

### ❌ Whisper ถอดเสียงไม่แม่น/ผิดเยอะ
- เพิ่มขนาดโมเดล: `WHISPER_MODEL=medium` หรือ `large-v3`
- ใช้ OpenAI Whisper API: `TRANSCRIBE_PROVIDER=openai`
- ตรวจคุณภาพไฟล์เสียง (เสียงรบกวนเยอะ → ผลแย่)

---

## 📡 API Documentation

แอปมี Swagger UI อัตโนมัติที่: **http://localhost:8000/docs**

### Endpoints

| Method | Endpoint | คำอธิบาย |
|--------|----------|----------|
| `GET`  | `/` | หน้าเว็บ UI |
| `GET`  | `/api/health` | ตรวจสถานะ + provider ที่ใช้ |
| `POST` | `/api/jobs` | สร้าง job ใหม่ (อัปโหลดไฟล์) |
| `GET`  | `/api/jobs/{id}` | ดูสถานะ + ผลลัพธ์ |
| `GET`  | `/api/jobs/{id}/download/{md\|docx\|txt}` | ดาวน์โหลดไฟล์สรุป |

### ตัวอย่างเรียกผ่าน curl

```bash
# สร้าง job
curl -F "file=@meeting.mp3" -F "language=th" \
     http://localhost:8000/api/jobs
# → {"job_id":"abc123...","status":"queued"}

# ดูสถานะ
curl http://localhost:8000/api/jobs/abc123

# ดาวน์โหลด Word
curl -O http://localhost:8000/api/jobs/abc123/download/docx
```

### ตัวอย่าง Python client

```python
import requests, time

# Upload
r = requests.post(
    "http://localhost:8000/api/jobs",
    files={"file": open("meeting.mp3", "rb")},
    data={"language": "th"},
)
job_id = r.json()["job_id"]

# Poll
while True:
    job = requests.get(f"http://localhost:8000/api/jobs/{job_id}").json()
    print(job["status"], "-", job["message"])
    if job["status"] in ("done", "error"):
        break
    time.sleep(2)

# Download
docx = requests.get(f"http://localhost:8000{job[\'downloads\'][\'docx\']}")
open("summary.docx", "wb").write(docx.content)
```

---

## 🛠️ การพัฒนาต่อ

### โครงสร้างโปรเจกต์

```
voice-to-meeting-doc/
├── app/                          # Backend (FastAPI)
│   ├── main.py                   # API endpoints
│   ├── config.py                 # โหลด .env
│   ├── jobs.py                   # in-memory job store
│   └── services/
│       ├── transcription.py      # Whisper (local/OpenAI)
│       ├── summarization.py      # LLM summary
│       └── export.py             # md/docx/txt converter
├── web/                          # Frontend (no build needed)
│   ├── index.html
│   ├── app.js
│   └── style.css
├── data/
│   ├── uploads/                  # ไฟล์ที่อัปโหลด (ไม่เข้า git)
│   └── outputs/                  # ไฟล์สรุปที่สร้าง
├── samples/                      # ตัวอย่าง script
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example                  # template
└── README.md
```

### 💡 ไอเดียที่ต่อยอดได้ง่าย

| ฟีเจอร์ | จุดที่ต้องแก้ | ความยาก |
|---------|---------------|---------|
| เปลี่ยน template สรุป | `app/services/summarization.py` (`SYSTEM_PROMPT`) | ⭐ ง่าย |
| เพิ่มภาษาที่รองรับ | `web/index.html` (เพิ่ม `<option>`) | ⭐ ง่าย |
| เปลี่ยน font ใน Word | `app/services/export.py` (`style.font.name`) | ⭐ ง่าย |
| เพิ่ม UI สวยขึ้น | `web/style.css` หรือเปลี่ยนเป็น React/Vue | ⭐⭐ ปานกลาง |
| เก็บงานถาวร (ไม่หายเมื่อ restart) | `app/jobs.py` (เปลี่ยน dict เป็น SQLite/Redis) | ⭐⭐ ปานกลาง |
| เพิ่ม login/auth | `app/main.py` + middleware | ⭐⭐⭐ ยาก |
| แยกผู้พูด (Speaker Diarization) | เปลี่ยนไปใช้ `whisperX` หรือ `pyannote.audio` | ⭐⭐⭐ ยาก |
| ส่งสรุปเข้า Email/Line/Notion | เพิ่ม service ใหม่ใน `app/services/` | ⭐⭐ ปานกลาง |
| Real-time stream transcription | เปลี่ยนเป็น WebSocket | ⭐⭐⭐ ยาก |

### Workflow การพัฒนา

```bash
# 1) Clone และตั้งค่า
git clone https://github.com/narakorn-qbicsoft/voice-to-meeting-doc.git
cd voice-to-meeting-doc

# 2) สร้าง branch ใหม่
git checkout -b feature/my-awesome-feature

# 3) แก้โค้ด → ทดสอบ
uvicorn app.main:app --reload    # auto-reload เมื่อแก้ไฟล์

# 4) Commit + Push
git add .
git commit -m "Add: my awesome feature"
git push origin feature/my-awesome-feature

# 5) เปิด Pull Request บน GitHub
```

---

## 🤝 Contributing

ยินดีต้อนรับ Issue, PR, และ feedback ทุกชนิด! 

หากพบปัญหาหรืออยากเสนอฟีเจอร์ → เปิด [Issue](https://github.com/narakorn-qbicsoft/voice-to-meeting-doc/issues)

---

## 📜 License

[MIT License](LICENSE) — ใช้ฟรี แก้ไขฟรี เผยแพร่ฟรี เชิงพาณิชย์ก็ได้

---

## 🙏 Credits

โปรเจกต์นี้สร้างได้เพราะเครื่องมือเหล่านี้:

- **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)** — เร็วกว่า OpenAI Whisper ต้นฉบับ 4 เท่า
- **[OpenAI Whisper](https://github.com/openai/whisper)** — โมเดลถอดเสียงระดับ SOTA
- **[FastAPI](https://fastapi.tiangolo.com/)** — modern Python web framework
- **[python-docx](https://github.com/python-openxml/python-docx)** — สร้างไฟล์ Word
- **[Ollama](https://ollama.com/)** — รัน LLM local ได้ง่าย ๆ

---

## 📞 ติดต่อ

- GitHub: [@narakorn-qbicsoft](https://github.com/narakorn-qbicsoft)
- Repository: https://github.com/narakorn-qbicsoft/voice-to-meeting-doc

---

⭐ **ถ้าโปรเจกต์นี้มีประโยชน์ ฝาก Star ให้ด้วยนะครับ!** ⭐
