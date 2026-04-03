from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/habits", tags=["habits"])


class HabitCreate(BaseModel):
    name: str
    emoji: Optional[str] = ""
    frequency: Optional[str] = "daily"


class HabitLog(BaseModel):
    completed: bool = True
    date: Optional[str] = None


@router.get("/")
async def get_habits(d: Optional[str] = Query(None, alias="date")):
    habits = supabase.table("habits").select("*").order("id").execute()
    target_date = d or str(date.today())
    logs = supabase.table("habit_logs").select("*").eq("date", target_date).execute()
    log_map = {l["habit_id"]: l["completed"] for l in (logs.data or [])}
    result = []
    for h in (habits.data or []):
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
    return result.data[0] if result.data else {}


@router.post("/{habit_id}/log")
async def log_habit(habit_id: int, item: HabitLog):
    target_date = item.date or str(date.today())
    existing = supabase.table("habit_logs").select("*").eq("habit_id", habit_id).eq("date", target_date).execute()
    if existing.data:
        result = supabase.table("habit_logs").update({"completed": item.completed}).eq("id", existing.data[0]["id"]).execute()
    else:
        result = supabase.table("habit_logs").insert({
            "habit_id": habit_id,
            "completed": item.completed,
            "date": target_date,
        }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{habit_id}")
async def delete_habit(habit_id: int):
    supabase.table("habit_logs").delete().eq("habit_id", habit_id).execute()
    result = supabase.table("habits").delete().eq("id", habit_id).execute()
    return {"deleted": True}
