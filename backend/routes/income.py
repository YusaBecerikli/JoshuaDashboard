from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from database import supabase

router = APIRouter(prefix="/api/income", tags=["income"])


class IncomeCreate(BaseModel):
    platform: str
    amount: float
    month: Optional[str] = None
    monthly_target: Optional[float] = None
    notes: Optional[str] = None
    date: Optional[str] = None


@router.get("/")
async def get_income():
    result = supabase.table("online_income").select("*").order("date", desc=True).limit(100).execute()
    return result.data


@router.get("/summary")
async def get_income_summary():
    result = supabase.table("online_income").select("*").execute()
    by_platform = {}
    total = 0
    for r in result.data:
        plat = r.get("platform", "Diğer")
        by_platform[plat] = by_platform.get(plat, 0) + float(r["amount"] or 0)
        total += float(r["amount"] or 0)
    return {
        "total": round(total, 2),
        "by_platform": by_platform,
        "recent": result.data[:10],
    }


@router.post("/")
async def add_income(item: IncomeCreate):
    result = supabase.table("online_income").insert({
        "platform": item.platform,
        "amount": item.amount,
        "month": item.month,
        "monthly_target": item.monthly_target,
        "notes": item.notes,
        "date": item.date,
    }).execute()
    return result.data[0]
