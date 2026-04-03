from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from database import supabase
from datetime import date

router = APIRouter(prefix="/api/budget", tags=["budget"])


class BudgetCreate(BaseModel):
    type: str
    category: Optional[str] = None
    amount: float
    description: Optional[str] = None
    date: Optional[str] = None


@router.get("")
async def get_budget(d: Optional[str] = Query(None, alias="date")):
    query = supabase.table("budget").select("*").order("date", desc=True).limit(100)
    if d:
        query = query.eq("date", d)
    result = query.execute()
    return {"data": result.data or []}


@router.get("/summary")
async def get_budget_summary(d: Optional[str] = Query(None, alias="date")):
    query = supabase.table("budget").select("*")
    if d:
        query = query.eq("date", d)
    result = query.execute()
    data = result.data or []
    incomes = [r for r in data if r.get("type") == "income"]
    expenses = [r for r in data if r.get("type") == "expense"]
    total_income = sum(float(r.get("amount") or 0) for r in incomes)
    total_expense = sum(float(r.get("amount") or 0) for r in expenses)
    by_category = {}
    for r in expenses:
        cat = r.get("category") or "Diğer"
        by_category[cat] = by_category.get(cat, 0) + float(r.get("amount") or 0)
    return {
        "balance": round(total_income - total_expense, 2),
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "by_category": by_category,
        "recent": data[:10],
    }


@router.post("")
async def add_budget(item: BudgetCreate):
    result = supabase.table("budget").insert({
        "type": item.type,
        "category": item.category,
        "amount": item.amount,
        "description": item.description,
        "date": item.date or str(date.today()),
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/{item_id}")
async def delete_budget(item_id: int):
    result = supabase.table("budget").delete().eq("id", item_id).execute()
    return {"deleted": True}
