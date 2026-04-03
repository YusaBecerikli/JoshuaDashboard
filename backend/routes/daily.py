from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/daily", tags=["daily"])


class TaskItem(BaseModel):
    title: str
    done: bool = False
    priority: str = "medium"


class DailyCreate(BaseModel):
    tasks: Optional[List[dict]] = None
    notes: Optional[str] = None
    mood: Optional[int] = None
    date: Optional[str] = None


@router.get("")
async def get_daily(d: Optional[str] = Query(None, alias="date")):
    target_date = d or str(date.today())
    result = supabase.table("daily_plans").select("*").eq("date", target_date).execute()
    if result.data:
        return result.data[0]
    return {"date": target_date, "tasks": [], "notes": None, "mood": None}


@router.post("")
async def update_daily(item: DailyCreate):
    target_date = item.date or str(date.today())
    data = {
        "tasks": item.tasks or [],
        "notes": item.notes,
        "mood": item.mood,
        "date": target_date,
    }
    existing = supabase.table("daily_plans").select("id").eq("date", target_date).execute()
    if existing.data:
        result = supabase.table("daily_plans").update(data).eq("id", existing.data[0]["id"]).execute()
    else:
        result = supabase.table("daily_plans").insert(data).execute()
    return result.data[0] if result.data else data
