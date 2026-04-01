import os
import json
import asyncio
import logging
import base64
from datetime import datetime, timedelta
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

from ai import process, watcher_analyze
from ai import _execute_memory_action
from database import supabase, get_today_summary
from memory import append_history, init_memory

load_dotenv()

logger = logging.getLogger("bot")

TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

TABLE_MAP = {
    "bütçe": "budget",
    "budget": "budget",
    "çalışma": "study_sessions",
    "study": "study_sessions",
    "ders": "study_sessions",
    "uyku": "sleep_logs",
    "sleep": "sleep_logs",
    "alışkanlık": "habits",
    "habit": "habits",
    "gelir": "online_income",
    "income": "online_income",
    "sosyal": "social_notes",
    "social": "social_notes",
    "net": "exam_scores",
    "score": "exam_scores",
}


def _sync_db_call(func):
    return asyncio.to_thread(func)


async def download_photo_as_base64(message: types.Message) -> Optional[str]:
    """Download the highest resolution photo from Telegram and return as base64 data URI."""
    try:
        photos = message.photo
        if not photos:
            return None
        photo = photos[-1]
        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)
        b64 = base64.b64encode(file_bytes.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    except Exception as e:
        logger.error(f"Photo download error: {e}")
        return None


async def _handle_ai_response(message: types.Message, response: dict):
    """Process AI response: execute actions, handle memory ops, send reply."""
    action = response.get("action", "chat")
    data = response.get("data", {})
    reply = response.get("reply", "Tamam.")

    # Memory actions — run in thread pool (file I/O)
    if action in ("update_memory", "summarize"):
        await asyncio.to_thread(_execute_memory_action, action, data)
        if action == "update_memory":
            reply = reply or "Belleğime kaydettim."
        elif action == "summarize":
            reply = reply or "Konuşmayı özetledim."
    elif action != "chat":
        try:
            await execute_action(action, data)
        except Exception as e:
            logger.error(f"Action error: {action} — {e}")
            reply += f"\n(Hata: {str(e)})"

    await message.answer(reply)


@dp.message(lambda m: m.photo and m.from_user.id == ALLOWED_USER_ID)
async def handle_photo(message: types.Message):
    """Handle photo messages — send to vision model."""
    context = get_today_summary()
    context["balance"] = f"{context['balance']} TL"

    caption = message.caption or ""
    image_b64 = await download_photo_as_base64(message)

    if not image_b64:
        await message.answer("Fotoğrafı indiremedim, tekrar gönderir misin?")
        return

    try:
        response = await process(caption, context, image_url=image_b64)
    except Exception as e:
        logger.error(f"Vision process error: {e}")
        await message.answer(f"Bir hata oluştu: {str(e)}")
        return

    await _handle_ai_response(message, response)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    await message.answer("Selam Joshua! Ben senin kişisel asistanın. Bana her şeyi yazabilirsin:\n\n"
                         "• 'Bugün 3 saat matematik çalıştım'\n"
                         "• 'Dün gece 01:30'da yattım'\n"
                         "• '50 lira yemek yedim'\n"
                         "• 'Kitap okuma alışkanlığı ekle'\n"
                         "• 'TYT matematik 28.5 net'\n"
                         "• 'Yarın 09:00'da matematik çalışmayı hatırlat'\n"
                         "• 'Son kaydı sil'")


@dp.message(Command("durum"))
async def cmd_status(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    ctx = get_today_summary()
    balance = ctx["balance"]
    study_h = ctx["study_minutes"] / 60
    habits = f"{ctx['habits_completed']}/{ctx['habits_total']}"
    sleep_info = f"{ctx['sleep'].get('sleep_time', '?')} - {ctx['sleep'].get('wake_time', '?')}" if ctx.get("sleep") else "Kayıt yok"
    await message.answer(
        f"📊 Bugünkü durum:\n\n"
        f"💰 Bakiye: {balance} TL\n"
        f"📚 Çalışma: {study_h:.1f} saat\n"
        f"✅ Alışkanlıklar: {habits}\n"
        f"😴 Son uyku: {sleep_info}"
    )


@dp.message(Command("yardim"))
async def cmd_help(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    await message.answer(
        "🤖 Komutlar:\n\n"
        "/start - Botu başlat\n"
        "/durum - Bugünkü özet\n"
        "/yardim - Bu mesaj\n\n"
        "Normal konuşma gibi yaz:\n"
        "• '2 saat fizik çalıştım'\n"
        "• 'Clickworker 500 tl'\n"
        "• 'TYT Türkçe 30 net'\n"
        "• 'Yarın 09:00'da hatırlat'\n"
        "• 'Son bütçe kaydını sil'"
    )


@dp.message()
async def handle_message(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return

    context = get_today_summary()
    context["balance"] = f"{context['balance']} TL"

    try:
        response = await process(message.text, context)
    except Exception as e:
        logger.error(f"Process error: {e}")
        await message.answer(f"Bir hata oluştu: {str(e)}")
        return

    # Track conversation in memory
    await asyncio.to_thread(
        append_history,
        f"Joshua: {message.text[:200]}\nAI: {response.get('reply', '')[:200]}"
    )

    await _handle_ai_response(message, response)


def parse_remind_time(raw: str) -> str:
    """Convert relative time strings to absolute timestamps."""
    import re
    now = datetime.utcnow()

    if re.match(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", raw):
        return raw

    m = re.search(r"(\d+)\s*(?:dk|dakika|min)\s*sonra", raw)
    if m:
        delta = now + timedelta(minutes=int(m.group(1)))
        return delta.strftime("%Y-%m-%d %H:%M:%S")

    m = re.search(r"(\d+)\s*(?:sa|saat)\s*sonra", raw)
    if m:
        delta = now + timedelta(hours=int(m.group(1)))
        return delta.strftime("%Y-%m-%d %H:%M:%S")

    m = re.search(r"yarın\s*(\d{1,2}):(\d{2})", raw)
    if m:
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0).strftime("%Y-%m-%d %H:%M:%S")

    m = re.search(r"bugün\s*(\d{1,2}):(\d{2})", raw)
    if m:
        return now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0).strftime("%Y-%m-%d %H:%M:%S")

    try:
        return datetime.fromisoformat(raw).strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass

    return (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")


async def execute_action(action: str, data: dict):
    if action == "budget_add":
        await _sync_db_call(lambda: supabase.table("budget").insert({
            "type": data.get("type", "expense"),
            "category": data.get("category"),
            "amount": data.get("amount"),
            "description": data.get("description"),
        }).execute())
    elif action == "study_add":
        await _sync_db_call(lambda: supabase.table("study_sessions").insert({
            "subject": data.get("subject"),
            "topic": data.get("topic"),
            "duration_minutes": data.get("duration_minutes"),
            "net_count": data.get("net_count"),
            "notes": data.get("notes"),
        }).execute())
    elif action == "sleep_log":
        await _sync_db_call(lambda: supabase.table("sleep_logs").insert({
            "sleep_time": data.get("sleep_time"),
            "wake_time": data.get("wake_time"),
            "quality": data.get("quality"),
            "notes": data.get("notes"),
        }).execute())
    elif action == "habit_log":
        habit_name = data.get("habit_name")
        habit = await _sync_db_call(lambda: supabase.table("habits").select("*").eq("name", habit_name).execute())
        if habit.data:
            from datetime import date
            await _sync_db_call(lambda: supabase.table("habit_logs").insert({
                "habit_id": habit.data[0]["id"],
                "completed": data.get("completed", True),
                "date": str(date.today()),
            }).execute())
    elif action == "habit_add":
        await _sync_db_call(lambda: supabase.table("habits").insert({
            "name": data.get("name"),
            "emoji": data.get("emoji", ""),
            "frequency": data.get("frequency", "daily"),
        }).execute())
    elif action == "goal_update":
        title = data.get("title")
        goal = await _sync_db_call(lambda: supabase.table("goals").select("*").ilike("title", f"%{title}%").execute())
        if goal.data:
            update = {}
            if "progress" in data:
                update["progress"] = data["progress"]
            if "status" in data:
                update["status"] = data["status"]
            if update:
                await _sync_db_call(lambda: supabase.table("goals").update(update).eq("id", goal.data[0]["id"]).execute())
    elif action == "social_note":
        await _sync_db_call(lambda: supabase.table("social_notes").insert({
            "person_name": data.get("person_name"),
            "relationship": data.get("relationship"),
            "note": data.get("note"),
            "tags": data.get("tags", []),
        }).execute())
    elif action == "daily_plan":
        from datetime import date
        today = str(date.today())
        existing = await _sync_db_call(lambda: supabase.table("daily_plans").select("id").eq("date", today).execute())
        plan_data = {
            "tasks": data.get("tasks", []),
            "notes": data.get("notes"),
            "mood": data.get("mood"),
            "date": today,
        }
        if existing.data:
            await _sync_db_call(lambda: supabase.table("daily_plans").update(plan_data).eq("id", existing.data[0]["id"]).execute())
        else:
            await _sync_db_call(lambda: supabase.table("daily_plans").insert(plan_data).execute())
    elif action == "income_add":
        await _sync_db_call(lambda: supabase.table("online_income").insert({
            "platform": data.get("platform"),
            "amount": data.get("amount"),
            "month": data.get("month"),
            "notes": data.get("notes"),
        }).execute())
    elif action == "module_add":
        await _sync_db_call(lambda: supabase.table("custom_modules").insert({
            "module_key": data.get("module_key"),
            "title": data.get("title"),
            "description": data.get("description"),
            "schema": data.get("schema"),
        }).execute())
    elif action == "exam_score_add":
        await _sync_db_call(lambda: supabase.table("exam_scores").insert({
            "exam_type": data.get("exam_type"),
            "subject": data.get("subject"),
            "net_score": data.get("net_score"),
        }).execute())
    elif action == "reminder_add":
        raw_time = data.get("remind_at", "")
        remind_at = parse_remind_time(raw_time)
        await _sync_db_call(lambda: supabase.table("reminders").insert({
            "message": data.get("message"),
            "remind_at": remind_at,
        }).execute())
    elif action == "delete_last":
        table = data.get("table", "")
        if table in TABLE_MAP.values():
            result = await _sync_db_call(lambda: supabase.table(table).select("id").order("id", desc=True).limit(1).execute())
            if result.data:
                await _sync_db_call(lambda: supabase.table(table).delete().eq("id", result.data[0]["id"]).execute())
        else:
            for keyword, tbl in TABLE_MAP.items():
                if keyword in table:
                    result = await _sync_db_call(lambda t=tbl: supabase.table(t).select("id").order("id", desc=True).limit(1).execute())
                    if result.data:
                        await _sync_db_call(lambda t=tbl, rid=result.data[0]["id"]: supabase.table(t).delete().eq("id", rid).execute())
                    break


async def check_reminders():
    """Check and send due reminders every 30 seconds."""
    while True:
        try:
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            result = await _sync_db_call(
                lambda: supabase.table("reminders").select("*").lte("remind_at", now).eq("sent", False).execute()
            )
            for reminder in result.data:
                try:
                    await bot.send_message(ALLOWED_USER_ID, f"⏰ Hatırlatma: {reminder['message']}")
                    await _sync_db_call(
                        lambda rid=reminder["id"]: supabase.table("reminders").update({"sent": True}).eq("id", rid).execute()
                    )
                except Exception as e:
                    logger.error(f"Reminder send error: {e}")
        except Exception as e:
            logger.error(f"Reminder check error: {e}")
        await asyncio.sleep(30)


async def watcher_task():
    """Proactive AI watcher — analyzes state every hour and sends message if needed."""
    while True:
        try:
            logger.info("Watcher: analyzing user state...")
            message = await watcher_analyze()
            if message:
                await bot.send_message(ALLOWED_USER_ID, f"🤖 {message}")
                logger.info(f"Watcher: sent message: {message[:50]}...")
            else:
                logger.info("Watcher: no message needed")
        except Exception as e:
            logger.error(f"Watcher error: {e}")
        await asyncio.sleep(3600)


async def main():
    asyncio.create_task(check_reminders())
    asyncio.create_task(watcher_task())
    try:
        await asyncio.to_thread(init_memory)
    except Exception as e:
        logger.error(f"Memory init failed: {e}")
    logger.info("Bot started with reminder checker + watcher + memory (Supabase)")
    await dp.start_polling(bot, handle_signals=False)


if __name__ == "__main__":
    asyncio.run(main())
