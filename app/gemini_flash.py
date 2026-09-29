"""
gemini_flash.py

Uses Gemini Flash to turn a user's story prompt into a structured,
panel-by-panel comic outline.
"""
import json
from app.gemini_client import get_client

FLASH_MODELS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-flash-latest", "gemini-1.5-flash"]


def generate_outline(story_prompt, character_name, setting, tone, art_style, num_panels=5):
    """Return a list of panel dicts: panel_number, title, scene_description, image_prompt."""
    client = get_client()

    system_instruction = (
        "You are a comic book outline writer. Given a story idea, produce a structured "
        f"panel-by-panel outline for exactly {num_panels} panels. "
        "Respond with ONLY valid JSON (no markdown fences): a JSON array of objects, "
        "each with keys: panel_number (integer), title (short string), "
        "scene_description (1-2 sentences), and image_prompt (a vivid, self-contained "
        "visual description an image model can render, written in the requested art style)."
    )
    user_prompt = (
        f"Story idea: {story_prompt}\n"
        f"Main character: {character_name}\n"
        f"Setting: {setting}\n"
        f"Story tone: {tone}\n"
        f"Art style: {art_style}\n"
        f"Number of panels: {num_panels}"
    )

    response = None
    last_exc = None
    for model in FLASH_MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json",
                },
            )
            if response and response.text:
                break
        except Exception as exc:
            last_exc = exc
            continue

    if not response or not response.text:
        if last_exc:
            print(f"[Gemini Flash Error] {last_exc}")
        return _fallback_outline(story_prompt, num_panels)

    try:
        panels = json.loads(response.text)
        if not isinstance(panels, list):
            raise ValueError("Expected a JSON list of panels")
    except (json.JSONDecodeError, TypeError, ValueError):
        panels = _fallback_outline(response.text, num_panels)

    # Normalize panel numbers in case the model skips or repeats them.
    for i, panel in enumerate(panels, start=1):
        panel.setdefault("panel_number", i)
        panel.setdefault("title", f"Panel {i}")
        panel.setdefault("scene_description", "")
        panel.setdefault("image_prompt", panel.get("scene_description", story_prompt))

    return panels


def _fallback_outline(raw_text, num_panels):
    """Best-effort fallback if the model doesn't return clean JSON."""
    snippet = (raw_text or "").strip()[:300]
    return [
        {
            "panel_number": i + 1,
            "title": f"Panel {i + 1}",
            "scene_description": snippet,
            "image_prompt": snippet,
        }
        for i in range(num_panels)
    ]
