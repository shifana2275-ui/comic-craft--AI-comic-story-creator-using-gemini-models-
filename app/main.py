"""
main.py

ComicCraft entry point. Run with:
    uvicorn app.main:app --reload
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="ComicCraft - AI Comic Story Creator", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(router)


@app.on_event("startup")
async def warn_if_no_api_key():
    if not os.getenv("GEMINI_API_KEY"):
        print(
            "\n[ComicCraft] WARNING: GEMINI_API_KEY is not set.\n"
            "Create a .env file (see .env.example) or export the variable "
            "before generating comics.\n"
        )
