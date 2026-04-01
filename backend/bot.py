import os
import json
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

from ai import process
from database import supabase, get_today_summary

load_dotenv()

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
        await message.answer(f"Bir hata oluştu: {str(e)}")
        return

    action = response.get("action", "chat")
    data = response.get("data", {})
    reply = response.get("reply", "Tamam.")

    if action != "chat":
        try:
            await execute_action(action, data)
        except Exception as e:
            reply += f"\n(Hata: {str(e)})"

    await message.answer(reply)


def parse_remind_time(raw: str) -> str:
    """Convert relative time strings to absolute timestamps."""
    import re
    now = datetime.utcnow()
    
    # Already absolute: "2026-04-01 14:30"
    if re.match(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", raw):
        return raw
    
    # "5dk sonra", "5 dakika sonra"
    m = re.search(r"(\d+)\s*(?:dk|dakika|min)\s*sonra", raw)
    if m:
        delta = now + timedelta(minutes=int(m.group(1)))
        return delta.strftime("%Y-%m-%d %H:%M:%S")
    
    # "2 saat sonra"
    m = re.search(r"(\d+)\s*(?:sa|saat)\s*sonra", raw)
    if m:
        delta = now + timedelta(hours=int(m.group(1)))
        return delta.strftime("%Y-%m-%d %H:%M:%S")
    
    # "yarın 09:00"
    m = re.search(r"yarın\s*(\d{1,2}):(\d{2})", raw)
    if m:
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0).strftime("%Y-%m-%d %H:%M:%S")
    
    # "bugün 15:00"
    m = re.search(r"bugün\s*(\d{1,2}):(\d{2})", raw)
    if m:
        return now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0).strftime("%Y-%m-%d %H:%M:%S")
    
    # Fallback: try to parse as-is
    try:
        return datetime.fromisoformat(raw).strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass
    
    # Last resort: 1 hour from now
    return (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")


async def execute_action(action: str, data: dict):
    if action == "budget_add":
        supabase.table("budget").insert({
            "type": data.get("type", "expense"),
            "category": data.get("category"),
            "amount": data.get("amount"),
            "description": data.get("description"),
        }).execute()
    elif action == "study_add":
        supabase.table("study_sessions").insert({
            "subject": data.get("subject"),
            "topic": data.get("topic"),
            "duration_minutes": data.get("duration_minutes"),
            "net_count": data.get("net_count"),
            "notes": data.get("notes"),
        }).execute()
    elif action == "sleep_log":
        supabase.table("sleep_logs").insert({
            "sleep_time": data.get("sleep_time"),
            "wake_time": data.get("wake_time"),
            "quality": data.get("quality"),
            "notes": data.get("notes"),
        }).execute()
    elif action == "habit_log":
        habit_name = data.get("habit_name")
        habit = supabase.table("habits").select("*").eq("name", habit_name).execute()
        if habit.data:
            from datetime import date
            supabase.table("habit_logs").insert({
                "habit_id": habit.data[0]["id"],
                "completed": data.get("completed", True),
                "date": str(date.today()),
            }).execute()
    elif action == "habit_add":
        supabase.table("habits").insert({
            "name": data.get("name"),
            "emoji": data.get("emoji", ""),
            "frequency": data.get("frequency", "daily"),
        }).execute()
    elif action == "goal_update":
        title = data.get("title")
        goal = supabase.table("goals").select("*").ilike("title", f"%{title}%").execute()
        if goal.data:
            update = {}
            if "progress" in data:
                update["progress"] = data["progress"]
            if "status" in data:
                update["status"] = data["status"]
            if update:
                supabase.table("goals").update(update).eq("id", goal.data[0]["id"]).execute()
    elif action == "social_note":
        supabase.table("social_notes").insert({
            "person_name": data.get("person_name"),
            "relationship": data.get("relationship"),
            "note": data.get("note"),
            "tags": data.get("tags", []),
        }).execute()
    elif action == "daily_plan":
        from datetime import date
        today = str(date.today())
        existing = supabase.table("daily_plans").select("id").eq("date", today).execute()
        plan_data = {
            "tasks": data.get("tasks", []),
            "notes": data.get("notes"),
            "mood": data.get("mood"),
            "date": today,
        }
        if existing.data:
            supabase.table("daily_plans").update(plan_data).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("daily_plans").insert(plan_data).execute()
    elif action == "income_add":
        supabase.table("online_income").insert({
            "platform": data.get("platform"),
            "amount": data.get("amount"),
            "month": data.get("month"),
            "notes": data.get("notes"),
        }).execute()
    elif action == "module_add":
        supabase.table("custom_modules").insert({
            "module_key": data.get("module_key"),
            "title": data.get("title"),
            "description": data.get("description"),
            "schema": data.get("schema"),
        }).execute()
    elif action == "exam_score_add":
        supabase.table("exam_scores").insert({
            "exam_type": data.get("exam_type"),
            "subject": data.get("subject"),
            "net_score": data.get("net_score"),
        }).execute()
    elif action == "reminder_add":
        raw_time = data.get("remind_at", "")
        remind_at = parse_remind_time(raw_time)
        supabase.table("reminders").insert({
            "message": data.get("message"),
            "remind_at": remind_at,
        }).execute()
    elif action == "delete_last":
        table = data.get("table", "")
        if table in TABLE_MAP.values():
            result = supabase.table(table).select("id").order("id", desc=True).limit(1).execute()
            if result.data:
                supabase.table(table).delete().eq("id", result.data[0]["id"]).execute()
        else:
            for keyword, tbl in TABLE_MAP.items():
                if keyword in table:
                    result = supabase.table(tbl).select("id").order("id", desc=True).limit(1).execute()
                    if result.data:
                        supabase.table(tbl).delete().eq("id", result.data[0]["id"]).execute()
                    break


async def check_reminders():
    while True:
        try:
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            result = supabase.table("reminders").select("*").lte("remind_at", now).eq("sent", False).execute()
            for reminder in result.data:
                try:
                    await bot.send_message(ALLOWED_USER_ID, f"⏰ Hatırlatma: {reminder['message']}")
                    supabase.table("reminders").update({"sent": True}).eq("id", reminder["id"]).execute()
                except Exception as e:
                    print(f"Reminder send error: {e}")
        except Exception as e:
            print(f"Reminder check error: {e}")
        await asyncio.sleep(60)


async def main():
    asyncio.create_task(check_reminders())
    await dp.start_polling(bot, handle_signals=False)


if __name__ == "__main__":
    asyncio.run(main())
