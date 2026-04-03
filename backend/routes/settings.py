import os
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from database import supabase

router = APIRouter(prefix="/api/settings", tags=["settings"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class SettingsUpdate(BaseModel):
    key: str
    value: str


@router.get("/")
async def get_settings():
    result = supabase.table("settings").select("*").execute()
    return {r["key"]: r["value"] for r in (result.data or [])}


@router.get("/models/list")
async def get_available_models():
    """Fetch live model list from Groq API."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                chat_models = []
                vision_models = []
                skip_keywords = ["whisper", "distill", "nomic", "llama-guard"]
                for m in models:
                    mid = m.get("id", "")
                    active = m.get("active", True)
                    if not active:
                        continue
                    if any(kw in mid.lower() for kw in skip_keywords):
                        continue
                    label = mid.replace("meta-llama/", "").replace("mistralai/", "").replace("google/", "").replace("thudm/", "")
                    if any(kw in mid.lower() for kw in ["vision", "maverick", "scout"]):
                        vision_models.append({"id": mid, "name": label})
                    else:
                        chat_models.append({"id": mid, "name": label})
                return {
                    "chat": sorted(chat_models, key=lambda x: x["name"]),
                    "vision": sorted(vision_models, key=lambda x: x["name"]),
                }
            return {"chat": [], "vision": [], "error": f"Groq API {resp.status_code}"}
    except Exception as e:
        return {"chat": [], "vision": [], "error": str(e)}


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
