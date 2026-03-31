from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from database import supabase

router = APIRouter(prefix="/api/social", tags=["social"])


class SocialCreate(BaseModel):
    person_name: str
    relationship: Optional[str] = None
    note: str
    tags: Optional[List[str]] = None
    date: Optional[str] = None


@router.get("/")
async def get_social():
    result = supabase.table("social_notes").select("*").order("date", desc=True).limit(50).execute()
    return result.data


@router.post("/")
async def add_social(item: SocialCreate):
    result = supabase.table("social_notes").insert({
        "person_name": item.person_name,
        "relationship": item.relationship,
        "note": item.note,
        "tags": item.tags or [],
        "date": item.date,
    }).execute()
    return result.data[0]
