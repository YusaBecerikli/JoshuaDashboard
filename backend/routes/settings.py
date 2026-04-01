from fastapi import APIRouter
from pydantic import BaseModel
from database import supabase

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    key: str
    value: str


@router.get("/")
async def get_settings():
    result = supabase.table("settings").select("*").execute()
    return {r["key"]: r["value"] for r in result.data}


@router.get("/{key}")
async def get_setting(key: str):
    result = supabase.table("settings").select("*").eq("key", key).execute()
    if result.data:
        return result.data[0]
    return {"error": "Not found"}


@router.post("/")
async def update_setting(item: SettingsUpdate):
    result = supabase.table("settings").upsert({
        "key": item.key,
        "value": item.value,
    }).execute()
    return result.data[0] if result.data else {}
