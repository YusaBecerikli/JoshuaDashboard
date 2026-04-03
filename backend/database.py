import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_balance():
    from datetime import date, timedelta
    thirty_days_ago = str(date.today() - timedelta(days=30))
    incomes = supabase.table("budget").select("amount").eq("type", "income").gte("date", thirty_days_ago).execute()
    expenses = supabase.table("budget").select("amount").eq("type", "expense").gte("date", thirty_days_ago).execute()
    total_income = sum(float(r.get("amount") or 0) for r in (incomes.data or []))
    total_expense = sum(float(r.get("amount") or 0) for r in (expenses.data or []))
    return round(total_income - total_expense, 2)


def get_today_summary():
    from datetime import date
    today = str(date.today())
    study = supabase.table("study_sessions").select("duration_minutes, net_count").eq("date", today).execute()
    total_minutes = sum(r.get("duration_minutes") or 0 for r in (study.data or []))
    nets = [r["net_count"] for r in (study.data or []) if r.get("net_count") is not None]
    avg_net = round(sum(nets) / len(nets), 1) if nets else 0
    sleep = supabase.table("sleep_logs").select("sleep_time, wake_time, quality").eq("date", today).execute()
    all_habits = supabase.table("habits").select("id").execute()
    total_habit_count = len(all_habits.data or []) or 1
    habits = supabase.table("habit_logs").select("completed, habit_id").eq("date", today).execute()
    completed = sum(1 for r in (habits.data or []) if r.get("completed"))
    return {
        "study_minutes": total_minutes,
        "avg_net": avg_net,
        "sleep": sleep.data[-1] if sleep.data else None,
        "habits_completed": completed,
        "habits_total": total_habit_count,
        "balance": get_balance(),
    }
