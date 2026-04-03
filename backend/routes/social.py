from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/social", tags=["social"])


class SocialCreate(BaseModel):
    person_name: str
    relationship: Optional[str] = None
    note: str
    tags: Optional[List[str]] = None
    date: Optional[str] = None


@router.get("/")
async def get_social(d: Optional[str] = Query(None, alias="date")):
    query = supabase.table("social_notes").select("*").order("date", desc=True).limit(50)
    if d:
        query = query.eq("date", d)
    result = query.execute()
    return {"data": result.data or []}


@router.post("/")
async def add_social(item: SocialCreate):
    result = supabase.table("social_notes").insert({
        "person_name": item.person_name,
        "relationship": item.relationship,
        "note": item.note,
        "tags": item.tags or [],
        "date": item.date or str(date.today()),
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{item_id}")
async def delete_social(item_id: int):
    result = supabase.table("social_notes").delete().eq("id", item_id).execute()
    return {"deleted": True}
