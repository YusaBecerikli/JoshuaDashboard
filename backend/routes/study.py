from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/study", tags=["study"])


class StudyCreate(BaseModel):
    subject: str
    topic: Optional[str] = None
    duration_minutes: int
    net_count: Optional[float] = None
    notes: Optional[str] = None
    date: Optional[str] = None


@router.get("/")
async def get_study(d: Optional[str] = Query(None, alias="date")):
    query = supabase.table("study_sessions").select("*").order("date", desc=True).limit(100)
    if d:
        query = query.eq("date", d)
    result = query.execute()
    return {"data": result.data or []}


@router.get("/summary")
async def get_study_summary(d: Optional[str] = Query(None, alias="date")):
    query = supabase.table("study_sessions").select("*")
    if d:
        query = query.eq("date", d)
    result = query.execute()
    data = result.data or []
    total_minutes = sum(r.get("duration_minutes") or 0 for r in data)
    total_nets = [r["net_count"] for r in data if r.get("net_count") is not None]
    by_subject = {}
    for r in data:
        subj = r.get("subject") or "Diğer"
        by_subject[subj] = by_subject.get(subj, 0) + (r.get("duration_minutes") or 0)
    return {
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 1),
        "avg_net": round(sum(total_nets) / len(total_nets), 1) if total_nets else 0,
        "by_subject": by_subject,
        "recent": data[:10],
    }


@router.post("/")
async def add_study(item: StudyCreate):
    result = supabase.table("study_sessions").insert({
        "subject": item.subject,
        "topic": item.topic,
        "duration_minutes": item.duration_minutes,
        "net_count": item.net_count,
        "notes": item.notes,
        "date": item.date or str(date.today()),
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{item_id}")
async def delete_study(item_id: int):
    result = supabase.table("study_sessions").delete().eq("id", item_id).execute()
    return {"deleted": True}
