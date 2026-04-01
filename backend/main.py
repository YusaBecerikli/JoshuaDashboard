import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import budget, study, sleep, habits, goals, income, social, daily, modules, dashboard, scores, reminders, settings, charts
import asyncio
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("main")

app = FastAPI(title="Joshua Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(budget.router)
app.include_router(study.router)
app.include_router(sleep.router)
app.include_router(habits.router)
app.include_router(goals.router)
app.include_router(income.router)
app.include_router(social.router)
app.include_router(daily.router)
app.include_router(modules.router)
app.include_router(dashboard.router)
app.include_router(scores.router)
app.include_router(reminders.router)
app.include_router(settings.router)
app.include_router(charts.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Joshua Dashboard API çalışıyor"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


def start_bot():
    try:
        import asyncio
        from bot import main
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Bot başlatılamadı: {e}", exc_info=True)


@app.on_event("startup")
async def startup():
    logger.info("Starting bot in background thread...")
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
