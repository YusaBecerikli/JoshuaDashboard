import os
import json
import re
import base64
import logging
import asyncio
from typing import Optional, List
from groq import AsyncGroq
from database import supabase, get_today_summary
from memory import get_all_memory, update_profile, update_knowledge, append_history, summarize_history

logger = logging.getLogger("ai")

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

VISION_MODEL = "llama-3.2-11b-vision-preview"

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
- Fotoğraf gönderilirse önce fotoğrafı analiz et, sonra aksiyon belirle
- Kullanıcı hakkında kalıcı bilgi öğrenirsen update_memory aksiyonu kullan

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
- reminder_add: {"message": str, "remind_at": str}
- delete_last: {"table": str}
- module_add: {"module_key": str, "title": str, "schema": object}
- update_memory: {"file": "profile"|"knowledge"|"history", "section": str, "content": str}
- summarize: {"summary": str}  ← konuşma uzadıysa özetle
- chat: {}

Format (SADECE JSON, başka hiçbir şey):
{"action": "action_tipi", "data": {...}, "reply": "kısa türkçe cevap"}

Bellek:
{MEMORY}

Güncel veriler:
{CONTEXT}"""

WATCHER_PROMPT = """Sen Joshua'nın kişisel asistanısın. Onun verilerini analiz edip proaktif bir mesaj hazırlayacaksın.

Kurallar:
- Sadece gerçekten faydalıysa mesaj at (motivasyon, uyarı, öneri)
- Gereksiz "nasılsın" mesajları atma
- Veri eksikse veya kötü gidiyorsa nazikçe uyar
- İyi gidiyorsa motive et
- Türkçe, kısa, samimi

Güncel veriler:
{CONTEXT}

SADECE JSON döndür:
{"message": "Joshua'ya gönderilecek mesaj", "send": true/false}

"send": false → hiçbir şey gönderme
"send": true → mesajı Telegram'dan ilet"""


def _sync_get_setting(key: str, default: str) -> str:
    try:
        result = supabase.table("settings").select("value").eq("key", key).execute()
        if result.data and result.data[0].get("value"):
            return result.data[0]["value"]
    except Exception as e:
        logger.warning(f"Setting '{key}' fetch failed: {e}")
    return default


async def get_system_prompt() -> str:
    return await asyncio.to_thread(_sync_get_setting, "system_prompt", DEFAULT_SYSTEM_PROMPT)


async def get_ai_model() -> str:
    return await asyncio.to_thread(_sync_get_setting, "ai_model", "llama-3.3-70b-versatile")


def _parse_json(text: str) -> dict:
    """Robust JSON extraction from messy LLM output."""
    text = text.strip()

    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                pass

    return {}


def _execute_memory_action(action: str, data: dict):
    """Synchronous memory operations — called from bot's execute_action via to_thread."""
    if action == "update_memory":
        file_type = data.get("file", "profile")
        section = data.get("section", "Genel")
        content = data.get("content", "")
        if not content:
            return
        if file_type == "profile":
            update_profile(section, content)
        elif file_type == "knowledge":
            update_knowledge(section, content)
        elif file_type == "history":
            append_history(content)
        logger.info(f"Memory updated: {file_type}/{section}")
    elif action == "summarize":
        summary = data.get("summary", "")
        if summary:
            summarize_history(summary)
            logger.info("History summarized")


async def process(message: str, context: dict, image_url: Optional[str] = None) -> dict:
    system_prompt = await get_system_prompt()
    memory = await asyncio.to_thread(get_all_memory)
    context_str = json.dumps(context, ensure_ascii=False, indent=2)
    prompt = system_prompt.replace("{MEMORY}", memory).replace("{CONTEXT}", context_str)

    if image_url:
        model = VISION_MODEL
        user_content: List[dict] = [
            {"type": "text", "text": message or "Bu fotoğrafa bak ve analiz et."},
        ]
        user_content.append({"type": "image_url", "image_url": {"url": image_url}})
    else:
        model = await get_ai_model()
        user_content = message

    logger.info(f"AI call: model={model}, has_image={bool(image_url)}, mem_len={len(memory)}, prompt_len={len(prompt)}")

    messages: list = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ]

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return {
            "action": "chat",
            "data": {},
            "reply": "AI servisinde sorun var, sonra dene.",
        }

    text = response.choices[0].message.content.strip()
    logger.info(f"AI raw response: {text[:200]}")

    result = _parse_json(text)

    if not result or "action" not in result:
        logger.warning(f"AI returned invalid JSON: {text[:200]}")
        return {
            "action": "chat",
            "data": {},
            "reply": result.get("reply", "Anlayamadım, tekrar söyler misin?"),
        }

    return result


async def watcher_analyze() -> Optional[str]:
    """Analyze user state and return a proactive message or None."""
    context = get_today_summary()
    context["balance"] = f"{context['balance']} TL"
    memory = await asyncio.to_thread(get_all_memory)
    context_str = json.dumps(context, ensure_ascii=False, indent=2)
    prompt = WATCHER_PROMPT.replace("{CONTEXT}", context_str)
    model = await get_ai_model()

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Bellek:\n{memory[:1000]}\n\nDurumu analiz et."},
            ],
            temperature=0.5,
            max_tokens=200,
        )
    except Exception as e:
        logger.error(f"Watcher Groq error: {e}")
        return None

    text = response.choices[0].message.content.strip()
    result = _parse_json(text)

    if result and result.get("send") and result.get("message"):
        return result["message"]
    return None
