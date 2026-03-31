from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import supabase

router = APIRouter(prefix="/api/habits", tags=["habits"])


class HabitCreate(BaseModel):
    name: str
    emoji: Optional[str] = ""
    frequency: Optional[str] = "daily"


class HabitLog(BaseModel):
    completed: bool = True
    date: Optional[str] = None


@router.get("/")
async def get_habits():
    habits = supabase.table("habits").select("*").order("id").execute()
    from datetime import date
    today = str(date.today())
    logs = supabase.table("habit_logs").select("*").eq("date", today).execute()
    log_map = {l["habit_id"]: l["completed"] for l in logs.data}
    result = []
    for h in habits.data:
        result.append({
            **h,
            "completed_today": log_map.get(h["id"], False),
        })
    return result


@router.post("/")
async def add_habit(item: HabitCreate):
    result = supabase.table("habits").insert({
        "name": item.name,
        "emoji": item.emoji,
        "frequency": item.frequency,
    }).execute()
    return result.data[0]


@router.post("/{habit_id}/log")
async def log_habit(habit_id: int, item: HabitLog):
    from datetime import date
    today = item.date or str(date.today())
    existing = supabase.table("habit_logs").select("*").eq("habit_id", habit_id).eq("date", today).execute()
    if existing.data:
        result = supabase.table("habit_logs").update({"completed": item.completed}).eq("id", existing.data[0]["id"]).execute()
    else:
        result = supabase.table("habit_logs").insert({
            "habit_id": habit_id,
            "completed": item.completed,
            "date": today,
        }).execute()
    return result.data[0] if result.data else {}
