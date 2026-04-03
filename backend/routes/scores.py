from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/scores", tags=["scores"])


class ScoreCreate(BaseModel):
    exam_type: str
    subject: str
    net_score: float
    date: Optional[str] = None
    notes: Optional[str] = None


@router.get("/tyt")
async def get_tyt_scores():
    result = supabase.table("exam_scores").select("*").eq("exam_type", "TYT").order("date").execute()
    return {"data": result.data or []}


@router.post("/tyt")
async def add_tyt_score(item: ScoreCreate):
    result = supabase.table("exam_scores").insert({
        "exam_type": "TYT",
        "subject": item.subject,
        "net_score": item.net_score,
        "date": item.date or str(date.today()),
        "notes": item.notes,
    }).execute()
    return result.data[0] if result.data else {}


@router.get("/ayt")
async def get_ayt_scores():
    result = supabase.table("exam_scores").select("*").eq("exam_type", "AYT").order("date").execute()
    return {"data": result.data or []}


@router.post("/ayt")
async def add_ayt_score(item: ScoreCreate):
    result = supabase.table("exam_scores").insert({
        "exam_type": "AYT",
        "subject": item.subject,
        "net_score": item.net_score,
        "date": item.date or str(date.today()),
        "notes": item.notes,
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{item_id}")
async def delete_score(item_id: int):
    result = supabase.table("exam_scores").delete().eq("id", item_id).execute()
    return {"deleted": True}
