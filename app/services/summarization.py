from __future__ import annotations
from textwrap import dedent
from ..config import settings

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
    provider = settings.summary_provider.lower()
    if provider == "none" or not transcript.strip():
        return "# สรุปการประชุม\n\n(ปิดการสรุปอัตโนมัติ — แสดงเฉพาะ transcript)"
    if provider == "openai":
        return _summarize_openai(transcript)
    raise ValueError(f"Unknown SUMMARY_PROVIDER: {provider}")


def _summarize_openai(transcript: str) -> str:
    from openai import OpenAI
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY required when SUMMARY_PROVIDER=openai")
    kwargs = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    client = OpenAI(**kwargs)
    user_prompt = (
        "นี่คือบทถอดเสียงการประชุม กรุณาสรุปตามรูปแบบที่กำหนด:\n\n"
        f"<<<TRANSCRIPT\n{transcript}\nTRANSCRIPT"
    )
    resp = client.chat.completions.create(
        model=settings.summary_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()
