from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import supabase

router = APIRouter(prefix="/api/countdowns", tags=["countdowns"])


class CountdownCreate(BaseModel):
    title: str
    target_date: str
    emoji: Optional[str] = "⏳"


@router.get("")
async def get_countdowns():
    result = supabase.table("countdowns").select("*").order("target_date").execute()
    return {"data": result.data or []}


@router.post("")
async def add_countdown(item: CountdownCreate):
    result = supabase.table("countdowns").insert({
        "title": item.title,
        "target_date": item.target_date,
        "emoji": item.emoji,
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{countdown_id}")
async def delete_countdown(countdown_id: int):
    result = supabase.table("countdowns").delete().eq("id", countdown_id).execute()
    return {"deleted": True}
