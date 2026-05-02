from __future__ import annotations
from textwrap import dedent
from .. import runtime_config as cfg

SYSTEM_PROMPT = dedent("""
คุณคือผู้ช่วยจดบันทึกการประชุมมืออาชีพ
หน้าที่ของคุณคือสรุปบทถอดเสียงการประชุมให้กระชับ ชัดเจน และนำไปใช้ต่อได้จริง
ตอบกลับเป็นภาษาเดียวกับ transcript (ส่วนใหญ่คือภาษาไทย)
ใช้รูปแบบ Markdown ตามโครงสร้างต่อไปนี้เท่านั้น:

# สรุปการประชุม

## ภาพรวม
(2-4 ประโยค สรุปวัตถุประสงค์และผลลัพธ์หลัก)

## ผู้เข้าร่วม (ถ้าระบุได้)
- ...

## หัวข้อที่หารือ
- **หัวข้อ 1**: รายละเอียดสั้น ๆ
- **หัวข้อ 2**: ...

## การตัดสินใจสำคัญ
- ...

## Action Items
| # | งานที่ต้องทำ | ผู้รับผิดชอบ | กำหนดส่ง |
|---|--------------|---------------|-----------|
| 1 | ... | ... | ... |

## ประเด็นค้างคา / ติดตามต่อ
- ...
""").strip()


def summarize(transcript: str) -> str:
    provider = (cfg.get("summary_provider") or "openai").lower()
    if provider == "none" or not transcript.strip():
        return "# สรุปการประชุม\n\n(ปิดการสรุปอัตโนมัติ — แสดงเฉพาะ transcript)"
    if provider == "openai":
        return _summarize_openai(transcript)
    raise ValueError(f"Unknown SUMMARY_PROVIDER: {provider}")


def _summarize_openai(transcript: str) -> str:
    from openai import OpenAI
    api_key = cfg.get("openai_api_key")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY required when SUMMARY_PROVIDER=openai")
    kwargs = {"api_key": api_key}
    base_url = cfg.get("openai_base_url")
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    user_prompt = (
        "นี่คือบทถอดเสียงการประชุม กรุณาสรุปตามรูปแบบที่กำหนด:\n\n"
        f"<<<TRANSCRIPT\n{transcript}\nTRANSCRIPT"
    )
    resp = client.chat.completions.create(
        model=cfg.get("summary_model"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def test_llm_connection() -> dict:
    """ทดสอบ connect LLM provider ปัจจุบัน — ส่ง prompt สั้น ๆ ตรวจว่า key/base_url ใช้ได้"""
    provider = (cfg.get("summary_provider") or "openai").lower()
    if provider == "none":
        return {"ok": True, "message": "Summarization ปิดอยู่ (provider=none)"}
    from openai import OpenAI
    api_key = cfg.get("openai_api_key")
    if not api_key:
        return {"ok": False, "message": "ยังไม่ได้ตั้ง API Key"}
    kwargs = {"api_key": api_key}
    base_url = cfg.get("openai_base_url")
    if base_url:
        kwargs["base_url"] = base_url
    try:
        client = OpenAI(**kwargs, timeout=15.0)
        resp = client.chat.completions.create(
            model=cfg.get("summary_model"),
            messages=[{"role": "user", "content": "พิมพ์คำว่า OK เท่านั้น"}],
            max_tokens=10,
            temperature=0,
        )
        reply = resp.choices[0].message.content.strip()
        return {
            "ok": True,
            "message": f"เชื่อมต่อสำเร็จ ✅  Model: {cfg.get('summary_model')}  Reply: {reply!r}",
        }
    except Exception as e:
        return {"ok": False, "message": f"{e.__class__.__name__}: {e}"}
