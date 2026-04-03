from fastapi import APIRouter
from pydantic import BaseModel
from database import supabase

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


class ReminderCreate(BaseModel):
    message: str
    remind_at: str


@router.get("")
async def get_reminders():
    result = supabase.table("reminders").select("*").eq("sent", False).order("remind_at").execute()
    return {"data": result.data or []}


@router.post("")
async def add_reminder(item: ReminderCreate):
    result = supabase.table("reminders").insert({
        "message": item.message,
        "remind_at": item.remind_at,
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int):
    result = supabase.table("reminders").delete().eq("id", reminder_id).execute()
    return {"deleted": True}
