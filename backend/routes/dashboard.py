from fastapi import APIRouter, Query
from typing import Optional
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/")
async def get_dashboard(d: Optional[str] = Query(None, alias="date")):
    target_date = d or str(date.today())

    study = supabase.table("study_sessions").select("duration_minutes, net_count").eq("date", target_date).execute()
    total_minutes = sum(r["duration_minutes"] or 0 for r in study.data)
    avg_net = sum(r["net_count"] or 0 for r in study.data)
    sleep = supabase.table("sleep_logs").select("sleep_time, wake_time, quality").eq("date", target_date).execute()
    habits = supabase.table("habit_logs").select("completed, habit_id").eq("date", target_date).execute()
    completed = sum(1 for r in habits.data if r.get("completed"))
    total_habits = len(habits.data) or 1

    from database import get_balance
    budget = supabase.table("budget").select("*").order("date", desc=True).limit(5).execute()
    study_sessions = supabase.table("study_sessions").select("*").eq("date", target_date).order("id", desc=True).limit(5).execute()
    sleep_logs = supabase.table("sleep_logs").select("*").eq("date", target_date).order("id", desc=True).limit(1).execute()
    all_habits = supabase.table("habits").select("*").execute()
    goals = supabase.table("goals").select("*").eq("status", "active").execute()
    modules = supabase.table("custom_modules").select("*").eq("active", True).execute()

    daily = supabase.table("daily_plans").select("*").eq("date", target_date).execute()
    daily_plan = daily.data[0] if daily.data else {"date": target_date, "tasks": [], "notes": None, "mood": None}

    return {
        "summary": {
            "study_minutes": total_minutes,
            "avg_net": round(avg_net, 1) if study.data else 0,
            "sleep": sleep.data[-1] if sleep.data else None,
            "habits_completed": completed,
            "habits_total": total_habits,
            "balance": round(get_balance(), 2),
        },
        "recent_budget": budget.data,
        "recent_study": study_sessions.data,
        "recent_sleep": sleep_logs.data,
        "habits": all_habits.data,
        "goals": goals.data,
        "custom_modules": modules.data,
        "daily_plan": daily_plan,
    }
