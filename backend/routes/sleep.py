from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import supabase

router = APIRouter(prefix="/api/sleep", tags=["sleep"])


class SleepCreate(BaseModel):
    sleep_time: Optional[str] = None
    wake_time: Optional[str] = None
    quality: Optional[int] = None
    notes: Optional[str] = None
    date: Optional[str] = None


@router.get("/")
async def get_sleep():
    result = supabase.table("sleep_logs").select("*").order("date", desc=True).limit(30).execute()
    return result.data


@router.get("/summary")
async def get_sleep_summary():
    result = supabase.table("sleep_logs").select("*").order("date", desc=True).limit(14).execute()
    data = result.data
    avg_quality = sum(r["quality"] or 5 for r in data) / len(data) if data else 0
    durations = []
    for r in data:
        if r.get("sleep_time") and r.get("wake_time"):
            try:
                sh, sm = map(int, r["sleep_time"].split(":"))
                wh, wm = map(int, r["wake_time"].split(":"))
                sleep_min = sh * 60 + sm
                wake_min = wh * 60 + wm
                if wake_min < sleep_min:
                    wake_min += 24 * 60
                durations.append((wake_min - sleep_min) / 60)
            except:
                pass
    avg_sleep = sum(durations) / len(durations) if durations else 0
    return {
        "avg_sleep_hours": round(avg_sleep, 1),
        "avg_quality": round(avg_quality, 1),
        "recent": data,
    }


@router.post("/")
async def add_sleep(item: SleepCreate):
    result = supabase.table("sleep_logs").insert({
        "sleep_time": item.sleep_time,
        "wake_time": item.wake_time,
        "quality": item.quality,
        "notes": item.notes,
        "date": item.date,
    }).execute()
    return result.data[0]
