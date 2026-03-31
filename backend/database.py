import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_balance():
    incomes = supabase.table("budget").select("amount").eq("type", "income").execute()
    expenses = supabase.table("budget").select("amount").eq("type", "expense").execute()
    total_income = sum(float(r["amount"] or 0) for r in incomes.data)
    total_expense = sum(float(r["amount"] or 0) for r in expenses.data)
    return total_income - total_expense


def get_today_summary():
    from datetime import date
    today = str(date.today())
    study = supabase.table("study_sessions").select("duration_minutes, net_count").eq("date", today).execute()
    total_minutes = sum(r["duration_minutes"] or 0 for r in study.data)
    avg_net = sum(r["net_count"] or 0 for r in study.data)
    sleep = supabase.table("sleep_logs").select("sleep_time, wake_time, quality").eq("date", today).execute()
    habits = supabase.table("habit_logs").select("completed, habit_id").eq("date", today).execute()
    completed = sum(1 for r in habits.data if r.get("completed"))
    total_habits = len(habits.data) or 1
    return {
        "study_minutes": total_minutes,
        "avg_net": round(avg_net, 1) if study.data else 0,
        "sleep": sleep.data[-1] if sleep.data else None,
        "habits_completed": completed,
        "habits_total": total_habits,
        "balance": round(get_balance(), 2),
    }
