"""
routes.py

All FastAPI route handlers for ComicCraft: the homepage form, comic
generation (HTML + JSON), export confirmation, and a small dev utility
for testing image generation in isolation.
"""
from pathlib import Path

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


class PromptRequest(BaseModel):
    story_prompt: str
    character_name: str
    setting: str
    tone: str
    art_style: str
    num_panels: int = Field(default=5, ge=1, le=10)


def _run_pipeline(story_prompt, character_name, setting, tone, art_style, num_panels=5):
    """The full ComicCraft pipeline: outline -> story -> images -> layout -> PDF."""
    outline = generate_outline(story_prompt, character_name, setting, tone, art_style, num_panels)
    story_panels = generate_story(outline, character_name, tone)

    for panel in story_panels:
        try:
            panel["image_path"] = generate_image(panel.get("image_prompt", story_prompt), art_style)
        except Exception as exc:  # keep going even if one panel's image fails
            panel["image_path"] = ""
            panel["image_error"] = str(exc)

    layout = build_comic_layout(story_panels)
    pdf_path = save_pdf(layout, title=character_name or "ComicCraft Comic")
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
    num_panels: int = Form(5),
):
    try:
        layout, pdf_path = _run_pipeline(
            story_prompt, character_name, setting, tone, art_style, num_panels
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {exc}")

    return templates.TemplateResponse(
        request, "comic_preview.html", {"layout": layout, "pdf_path": pdf_path}
    )


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        layout, pdf_path = _run_pipeline(
            payload.story_prompt,
            payload.character_name,
            payload.setting,
            payload.tone,
            payload.art_style,
            payload.num_panels,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {exc}")

    return JSONResponse({"layout": layout, "pdf_path": pdf_path})


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = ""):
    return templates.TemplateResponse(
        request, "export_success.html", {"pdf_path": pdf_path}
    )




@router.get("/test-image")
async def test_image(prompt: str, art_style: str = ""):
    """Dev utility: generate a single image from a prompt without a full comic run."""
    try:
        image_path = generate_image(prompt, art_style)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return JSONResponse({"image_path": image_path})
