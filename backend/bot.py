import os
import json
import asyncio
import logging
import base64
import re
import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

from ai import process, watcher_analyze
from ai import _execute_memory_action
from database import supabase, get_today_summary
from memory import append_history, init_memory, read_profile, read_knowledge, read_history

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

QUICK_COMMANDS = [
    ("📊 Durum", "durum"),
    ("💰 Bakiye", "bakiye ne kadar"),
    ("📚 Bugün kaç saat çalıştım", "bugün kaç saat çalıştım"),
    ("📝 Notlarım", "notlarımı göster"),
    ("⏳ Geri sayımlar", "geri sayımları göster"),
]


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
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=label, callback_data=f"quick:{cmd}") for label, cmd in QUICK_COMMANDS[:3]],
        [types.InlineKeyboardButton(text=label, callback_data=f"quick:{cmd}") for label, cmd in QUICK_COMMANDS[3:]],
    ])
    await message.answer(
        "Selam Joshua! Ben senin kişisel asistanın. Bana her şeyi yazabilirsin:\n\n"
        "• 'Bugün 3 saat matematik çalıştım'\n"
        "• 'Dün gece 01:30'da yattım'\n"
        "• '50 lira yemek yedim'\n"
        "• 'Kitap okuma alışkanlığı ekle'\n"
        "• 'TYT matematik 28.5 net'\n"
        "• 'Yarın 09:00'da matematik çalışmayı hatırlat'\n"
        "• 'Son kaydı sil'\n"
        "• '/not [yazılacak şey]'",
        reply_markup=keyboard,
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("quick:"))
async def handle_quick_command(callback: types.CallbackQuery):
    cmd = callback.data.split(":", 1)[1]
    await callback.answer()

    if cmd == "durum":
        await cmd_status(callback.message)
    elif cmd == "bakiye ne kadar":
        ctx = get_today_summary()
        await callback.message.answer(f"💰 Bakiye: {ctx['balance']} TL")
    elif cmd == "bugün kaç saat çalıştım":
        ctx = get_today_summary()
        hours = ctx["study_minutes"] / 60
        await callback.message.answer(f"📚 Bugün {hours:.1f} saat çalıştın")
    elif cmd == "notlarımı göster":
        notes = await _sync_db_call(lambda: supabase.table("notes").select("*").order("id", desc=True).limit(10).execute())
        if notes.data:
            text = "📝 Notların:\n\n" + "\n\n".join(f"• {n['content']}" for n in notes.data)
        else:
            text = "Henüz not yok. /not komutuyla ekle."
        await callback.message.answer(text)
    elif cmd == "geri sayımları göster":
        countdowns = await _sync_db_call(lambda: supabase.table("countdowns").select("*").order("target_date").execute())
        if countdowns.data:
            text = "⏳ Geri Sayımlar:\n\n"
            for c in countdowns.data:
                days = (datetime.strptime(c["target_date"], "%Y-%m-%d").date() - datetime.now(timezone.utc).replace(tzinfo=None).date()).days
                text += f"{c.get('emoji', '⏳')} {c['title']}: {days} gün kaldı\n"
        else:
            text = "Henüz geri sayım yok."
        await callback.message.answer(text)


@dp.message(Command("not"))
async def cmd_note(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    content = message.text.replace("/not ", "").strip()
    if not content or content == "/not":
        await message.answer("Kullanım: /not [not içeriği]")
        return
    await _sync_db_call(lambda: supabase.table("notes").insert({"content": content}).execute())
    await message.answer("📝 Not kaydedildi.")


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
    now = datetime.now(timezone.utc).replace(tzinfo=None)

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
    except (ValueError, TypeError):
        pass

    return (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")


async def execute_action(action: str, data: dict):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if action == "budget_add":
        await _sync_db_call(lambda: supabase.table("budget").insert({
            "type": data.get("type", "expense"),
            "category": data.get("category"),
            "amount": data.get("amount"),
            "description": data.get("description"),
            "date": data.get("date") or today_str,
        }).execute())
    elif action == "study_add":
        await _sync_db_call(lambda: supabase.table("study_sessions").insert({
            "subject": data.get("subject"),
            "topic": data.get("topic"),
            "duration_minutes": data.get("duration_minutes"),
            "net_count": data.get("net_count"),
            "notes": data.get("notes"),
            "date": data.get("date") or today_str,
        }).execute())
    elif action == "sleep_log":
        await _sync_db_call(lambda: supabase.table("sleep_logs").insert({
            "sleep_time": data.get("sleep_time"),
            "wake_time": data.get("wake_time"),
            "quality": data.get("quality"),
            "notes": data.get("notes"),
            "date": data.get("date") or today_str,
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
            "date": data.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
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
            "date": data.get("date") or today_str,
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
            "date": data.get("date") or today_str,
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
    elif action == "note_add":
        await _sync_db_call(lambda: supabase.table("notes").insert({
            "content": data.get("content"),
            "tags": data.get("tags", []),
        }).execute())
    elif action == "countdown_add":
        await _sync_db_call(lambda: supabase.table("countdowns").insert({
            "title": data.get("title"),
            "target_date": data.get("target_date"),
            "emoji": data.get("emoji", "⏳"),
        }).execute())


async def check_reminders():
    """Check and send due reminders every 30 seconds."""
    while True:
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S")
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


async def weekly_summary():
    """Send weekly summary every Sunday at 21:00."""
    while True:
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            # Only fire in the 21:00 minute window
            if now.weekday() == 6 and now.hour == 21 and now.minute < 5:
                last_sent = await _sync_db_call(
                    lambda: supabase.table("settings").select("value").eq("key", "last_weekly_summary").execute()
                )
                if not last_sent.data or last_sent.data[0]["value"] != now.strftime("%Y-%m-%d"):
                    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
                    today = now.strftime("%Y-%m-%d")

                    study = await _sync_db_call(
                        lambda: supabase.table("study_sessions").select("duration_minutes, net_count").gte("date", week_ago).lte("date", today).execute()
                    )
                    total_hours = sum(r.get("duration_minutes") or 0 for r in (study.data or [])) / 60
                    nets = [r["net_count"] for r in (study.data or []) if r.get("net_count") is not None]
                    avg_net = round(sum(nets) / len(nets), 1) if nets else 0

                    budget = await _sync_db_call(
                        lambda: supabase.table("budget").select("type, amount").gte("date", week_ago).lte("date", today).execute()
                    )
                    income = sum(r.get("amount") or 0 for r in (budget.data or []) if r.get("type") == "income")
                    expense = sum(r.get("amount") or 0 for r in (budget.data or []) if r.get("type") == "expense")

                    habits = await _sync_db_call(
                        lambda: supabase.table("habit_logs").select("completed").gte("date", week_ago).lte("date", today).execute()
                    )
                    done = sum(1 for r in (habits.data or []) if r.get("completed"))
                    total = len(habits.data or []) or 1

                    msg = (
                        f"📊 Haftalık Özet ({week_ago} → {today}):\n\n"
                        f"📚 {total_hours:.1f} saat çalışma | Ort. net: {avg_net}\n"
                        f"💰 Gelir: {income} TL | Gider: {expense} TL\n"
                        f"✅ Alışkanlıklar: {done}/{total} tamamlandı\n\n"
                        f"İyi hafta Joshua! 💪"
                    )
                    await bot.send_message(ALLOWED_USER_ID, msg)
                    await _sync_db_call(
                        lambda: supabase.table("settings").upsert({
                            "key": "last_weekly_summary",
                            "value": now.strftime("%Y-%m-%d"),
                        }).execute()
                    )
                    logger.info("Weekly summary sent")
        except Exception as e:
            logger.error(f"Weekly summary error: {e}")
        await asyncio.sleep(60)


async def motivation_watcher():
    """Send motivation messages when study hours are low. Fires once per day at 20:00."""
    while True:
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            today_str = now.strftime("%Y-%m-%d")
            if now.hour == 20 and now.minute < 5:
                last_mot = await _sync_db_call(
                    lambda: supabase.table("settings").select("value").eq("key", "last_motivation").execute()
                )
                if not last_mot.data or last_mot.data[0]["value"] != today_str:
                    ctx = get_today_summary()
                    study_hours = ctx["study_minutes"] / 60
                    if study_hours < 2:
                        messages = [
                            "Bugün biraz az çalıştın gibi. Yarın daha iyi olacak, merak etme 💪",
                            "Her gün mükemmel olmak zorunda değilsin. Önemli olan devam etmek 🔥",
                            "Bugün hafif geçti ama yarın yeni bir sayfa. Hadi yapalım bunu 📚",
                        ]
                        await bot.send_message(ALLOWED_USER_ID, random.choice(messages))
                        await _sync_db_call(
                            lambda: supabase.table("settings").upsert({
                                "key": "last_motivation",
                                "value": today_str,
                            }).execute()
                        )
                        logger.info("Motivation message sent")
        except Exception as e:
            logger.error(f"Motivation watcher error: {e}")
        await asyncio.sleep(60)


async def main():
    asyncio.create_task(check_reminders())
    asyncio.create_task(watcher_task())
    asyncio.create_task(weekly_summary())
    asyncio.create_task(motivation_watcher())
    try:
        await asyncio.to_thread(init_memory)
    except Exception as e:
        logger.error(f"Memory init failed: {e}")

    # Wait a few seconds before polling to let any old instance release the connection
    await asyncio.sleep(5)

    # Delete webhook to ensure polling mode (prevents Conflict errors)
    try:
        await bot.delete_webhook()
    except Exception as e:
        logger.warning(f"Could not delete webhook: {e}")

    logger.info("Bot started with reminder checker + watcher + memory (Supabase)")
    await dp.start_polling(bot, skip_updates=True, handle_signals=False)


if __name__ == "__main__":
    asyncio.run(main())
