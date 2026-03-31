from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import supabase

router = APIRouter(prefix="/api/goals", tags=["goals"])


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[str] = None
    progress: Optional[int] = 0
    status: Optional[str] = "active"


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[int] = None
    status: Optional[str] = None


@router.get("/")
async def get_goals():
    result = supabase.table("goals").select("*").order("id", desc=True).execute()
    return result.data


@router.post("/")
async def add_goal(item: GoalCreate):
    result = supabase.table("goals").insert({
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "deadline": item.deadline,
        "progress": item.progress,
        "status": item.status,
    }).execute()
    return result.data[0]


@router.patch("/{goal_id}")
async def update_goal(goal_id: int, item: GoalUpdate):
    update_data = item.model_dump(exclude_none=True)
    if not update_data:
        return {"error": "No fields to update"}
    result = supabase.table("goals").update(update_data).eq("id", goal_id).execute()
    return result.data[0] if result.data else {}
