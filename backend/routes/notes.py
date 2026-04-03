from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from database import supabase

router = APIRouter(prefix="/api/notes", tags=["notes"])


class NoteCreate(BaseModel):
    content: str
    tags: Optional[List[str]] = None


@router.get("")
async def get_notes():
    result = supabase.table("notes").select("*").order("id", desc=True).execute()
    return {"data": result.data or []}


@router.post("")
async def add_note(item: NoteCreate):
    result = supabase.table("notes").insert({
        "content": item.content,
        "tags": item.tags or [],
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{note_id}")
async def delete_note(note_id: int):
    result = supabase.table("notes").delete().eq("id", note_id).execute()
    return {"deleted": True}
