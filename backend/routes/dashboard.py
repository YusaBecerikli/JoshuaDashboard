from fastapi import APIRouter, Query
from typing import Optional
from database import supabase, get_balance
from datetime import date

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(d: Optional[str] = Query(None, alias="date")):
    target_date = d or str(date.today())

    study = supabase.table("study_sessions").select("duration_minutes, net_count").eq("date", target_date).execute()
    total_minutes = sum(r.get("duration_minutes") or 0 for r in (study.data or []))
    nets = [r["net_count"] for r in (study.data or []) if r.get("net_count") is not None]
    avg_net = round(sum(nets) / len(nets), 1) if nets else 0
    sleep = supabase.table("sleep_logs").select("sleep_time, wake_time, quality").eq("date", target_date).execute()
    all_habits = supabase.table("habits").select("id").execute()
    total_habit_count = len(all_habits.data or []) or 1
    habits = supabase.table("habit_logs").select("completed, habit_id").eq("date", target_date).execute()
    completed = sum(1 for r in (habits.data or []) if r.get("completed"))

    budget = supabase.table("budget").select("*").order("date", desc=True).limit(5).execute()
    study_sessions = supabase.table("study_sessions").select("*").eq("date", target_date).order("id", desc=True).limit(5).execute()
    sleep_logs = supabase.table("sleep_logs").select("*").eq("date", target_date).order("id", desc=True).limit(1).execute()
    all_habits_full = supabase.table("habits").select("*").execute()
    goals = supabase.table("goals").select("*").eq("status", "active").execute()
    modules = supabase.table("custom_modules").select("*").eq("active", True).execute()

    daily = supabase.table("daily_plans").select("*").eq("date", target_date).execute()
    daily_plan = daily.data[0] if daily.data else {"date": target_date, "tasks": [], "notes": None, "mood": None}

    return {
        "summary": {
            "study_minutes": total_minutes,
            "avg_net": avg_net,
            "sleep": sleep.data[-1] if sleep.data else None,
            "habits_completed": completed,
            "habits_total": total_habit_count,
            "balance": round(get_balance(), 2),
        },
        "recent_budget": budget.data or [],
        "recent_study": study_sessions.data or [],
        "recent_sleep": sleep_logs.data or [],
        "habits": all_habits_full.data or [],
        "goals": goals.data or [],
        "custom_modules": modules.data or [],
        "daily_plan": daily_plan,
    }
