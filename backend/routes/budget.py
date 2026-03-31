from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import supabase

router = APIRouter(prefix="/api/budget", tags=["budget"])


class BudgetCreate(BaseModel):
    type: str
    category: Optional[str] = None
    amount: float
    description: Optional[str] = None
    date: Optional[str] = None


@router.get("/")
async def get_budget():
    result = supabase.table("budget").select("*").order("date", desc=True).limit(100).execute()
    return result.data


@router.get("/summary")
async def get_budget_summary():
    result = supabase.table("budget").select("*").execute()
    incomes = [r for r in result.data if r["type"] == "income"]
    expenses = [r for r in result.data if r["type"] == "expense"]
    total_income = sum(float(r["amount"] or 0) for r in incomes)
    total_expense = sum(float(r["amount"] or 0) for r in expenses)
    by_category = {}
    for r in expenses:
        cat = r.get("category", "Diğer")
        by_category[cat] = by_category.get(cat, 0) + float(r["amount"] or 0)
    return {
        "balance": round(total_income - total_expense, 2),
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "by_category": by_category,
        "recent": result.data[:10],
    }


@router.post("/")
async def add_budget(item: BudgetCreate):
    result = supabase.table("budget").insert({
        "type": item.type,
        "category": item.category,
        "amount": item.amount,
        "description": item.description,
        "date": item.date,
    }).execute()
    return result.data[0]
