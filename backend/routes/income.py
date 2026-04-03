from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/income", tags=["income"])


class IncomeCreate(BaseModel):
    platform: str
    amount: float
    month: Optional[str] = None
    monthly_target: Optional[float] = None
    notes: Optional[str] = None
    date: Optional[str] = None


@router.get("")
async def get_income():
    result = supabase.table("online_income").select("*").order("date", desc=True).limit(100).execute()
    return {"data": result.data or []}


@router.get("/summary")
async def get_income_summary():
    result = supabase.table("online_income").select("*").execute()
    data = result.data or []
    by_platform = {}
    total = 0
    for r in data:
        plat = r.get("platform") or "Diğer"
        by_platform[plat] = by_platform.get(plat, 0) + float(r.get("amount") or 0)
        total += float(r.get("amount") or 0)
    return {
        "total": round(total, 2),
        "by_platform": by_platform,
        "recent": data[:10],
    }


@router.post("")
async def add_income(item: IncomeCreate):
    result = supabase.table("online_income").insert({
        "platform": item.platform,
        "amount": item.amount,
        "month": item.month,
        "monthly_target": item.monthly_target,
        "notes": item.notes,
        "date": item.date or str(date.today()),
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{item_id}")
async def delete_income(item_id: int):
    result = supabase.table("online_income").delete().eq("id", item_id).execute()
    return {"deleted": True}
