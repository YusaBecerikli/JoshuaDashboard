import os
import json
from groq import AsyncGroq
from database import supabase, get_today_summary

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

DEFAULT_SYSTEM_PROMPT = """Sen Joshua'nın (Muhammed Yuşa Becerikli) kişisel asistanısın. 17 yaşında, Bingöl'de yaşıyor, Haziran'da YKS var, hedefi Sabancı Üniversitesi Bilgisayar Mühendisliği.

Arkadaş gibi konuş. Türkçe. Kısa ve direkt. Gereksiz soru sorma.

KRİTİK KURALLAR:
- Kullanıcı veri söylediğinde ÖNCE aksiyonu çalıştır, sonra kısa cevap ver
- Geçmiş zaman ("çalıştım", "uyudum") → direkt aksiyon
- Gelecek zaman ("çalışacağım") → goal veya chat
- Maksimum 1 soru sor, 0 daha iyi
- Sağlık/ahlak dersi verme
- "uzatma", "sadece kaydet" derlerse kısa kes
- "nasılsın" → max 3 kelime cevap
- Belirsiz mesajda en mantıklı aksiyonu tahmin et, sorma

Aksiyonlar:
- budget_add: {"type": "income"|"expense", "category": str, "amount": float, "description": str}
- study_add: {"subject": str, "topic": str, "duration_minutes": int, "net_count": float}
- sleep_log: {"sleep_time": "HH:MM", "wake_time": "HH:MM", "quality": int}
- habit_log: {"habit_name": str, "completed": bool}
- habit_add: {"name": str, "emoji": str, "frequency": "daily"|"weekly"}
- goal_update: {"title": str, "progress": int, "status": str}
- social_note: {"person_name": str, "relationship": str, "note": str}
- daily_plan: {"tasks": [{"title": str, "done": bool, "priority": str}], "mood": int}
- income_add: {"platform": str, "amount": float, "month": "YYYY-MM"}
- exam_score_add: {"exam_type": "TYT"|"AYT", "subject": str, "net_score": float}
- reminder_add: {"message": str, "remind_at": "YYYY-MM-DD HH:MM"}
- delete_last: {"table": str}
- module_add: {"module_key": str, "title": str, "schema": object}
- chat: {}

Format (SADECE JSON, başka hiçbir şey):
{"action": "action_tipi", "data": {...}, "reply": "kısa türkçe cevap"}

Güncel veriler:
{CONTEXT}"""


async def get_system_prompt():
    try:
        result = supabase.table("settings").select("value").eq("key", "system_prompt").execute()
        if result.data:
            return result.data[0]["value"]
    except:
        pass
    return DEFAULT_SYSTEM_PROMPT


async def process(message: str, context: dict) -> dict:
    system_prompt = await get_system_prompt()
    context_str = json.dumps(context, ensure_ascii=False, indent=2)
    prompt = system_prompt.replace("{CONTEXT}", context_str)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message},
        ],
        temperature=0.3,
        max_tokens=500,
    )

    text = response.choices[0].message.content.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "action": "chat",
            "data": {},
            "reply": "Anlayamadım, tekrar söyler misin?",
        }
