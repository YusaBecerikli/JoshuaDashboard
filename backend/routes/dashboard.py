from fastapi import APIRouter
from database import supabase, get_today_summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/")
async def get_dashboard():
    summary = get_today_summary()

    budget = supabase.table("budget").select("*").order("date", desc=True).limit(5).execute()
    study = supabase.table("study_sessions").select("*").order("date", desc=True).limit(5).execute()
    sleep = supabase.table("sleep_logs").select("*").order("date", desc=True).limit(7).execute()
    habits = supabase.table("habits").select("*").execute()
    goals = supabase.table("goals").select("*").eq("status", "active").execute()
    modules = supabase.table("custom_modules").select("*").eq("active", True).execute()

    return {
        "summary": summary,
        "recent_budget": budget.data,
        "recent_study": study.data,
        "recent_sleep": sleep.data,
        "habits": habits.data,
        "goals": goals.data,
        "custom_modules": modules.data,
    }
