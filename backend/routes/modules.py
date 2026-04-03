from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/modules", tags=["modules"])


class ModuleCreate(BaseModel):
    module_key: str
    title: str
    description: Optional[str] = None
    schema_data: Optional[dict] = None
    component_code: Optional[str] = None


class ModuleDataCreate(BaseModel):
    data: dict
    date: Optional[str] = None


@router.get("")
async def get_modules():
    result = supabase.table("custom_modules").select("*").eq("active", True).execute()
    return {"data": result.data or []}


@router.post("")
async def add_module(item: ModuleCreate):
    result = supabase.table("custom_modules").insert({
        "module_key": item.module_key,
        "title": item.title,
        "description": item.description,
        "schema": item.schema_data,
        "component_code": item.component_code,
    }).execute()
    return result.data[0] if result.data else {}


@router.get("/{module_key}/data")
async def get_module_data(module_key: str):
    result = supabase.table("custom_module_data").select("*").eq("module_key", module_key).order("date", desc=True).execute()
    return {"data": result.data or []}


@router.post("/{module_key}/data")
async def add_module_data(module_key: str, item: ModuleDataCreate):
    result = supabase.table("custom_module_data").insert({
        "module_key": module_key,
        "data": item.data,
        "date": item.date or str(date.today()),
    }).execute()
    return result.data[0] if result.data else {}
