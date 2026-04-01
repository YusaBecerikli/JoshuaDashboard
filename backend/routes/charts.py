from fastapi import APIRouter
from database import supabase

router = APIRouter(prefix="/api/charts", tags=["charts"])


@router.get("/sleep")
async def get_sleep_chart():
    result = supabase.table("sleep_logs").select("*").order("date", desc=True).limit(30).execute()
    data = result.data
    for r in data:
        if r.get("sleep_time") and r.get("wake_time"):
            try:
                sh, sm = map(int, r["sleep_time"].split(":"))
                wh, wm = map(int, r["wake_time"].split(":"))
                sleep_min = sh * 60 + sm
                wake_min = wh * 60 + wm
                if wake_min < sleep_min:
                    wake_min += 24 * 60
                r["duration_hours"] = round((wake_min - sleep_min) / 60, 2)
            except:
                r["duration_hours"] = None
        else:
            r["duration_hours"] = None
    return list(reversed(data))


@router.get("/study")
async def get_study_chart():
    result = supabase.table("study_sessions").select("*").order("date", desc=True).limit(100).execute()
    daily = {}
    for r in result.data:
        d = r.get("date", "")
        if d not in daily:
            daily[d] = {"date": d, "total_minutes": 0, "subjects": {}}
        daily[d]["total_minutes"] += r.get("duration_minutes") or 0
        subj = r.get("subject", "Diğer")
        daily[d]["subjects"][subj] = daily[d]["subjects"].get(subj, 0) + (r.get("duration_minutes") or 0)
    return list(reversed(list(daily.values())))
