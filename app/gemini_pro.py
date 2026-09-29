"""
gemini_pro.py

Uses Gemini Pro to expand a panel outline into full narration and
character dialogue for each panel.
"""
import json
from app.gemini_client import get_client

PRO_MODELS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-pro-latest", "gemini-flash-latest"]


def generate_story(panels, character_name, tone):
    """Given the outline panels, return them enriched with 'caption' and 'narration'."""
    client = get_client()

    system_instruction = (
        "You are a comic book scriptwriter. You will receive a JSON array of comic panel "
        "outlines. For each panel, add two new fields: "
        "'caption' (a short, ambient scene-setting line — sounds, background, atmosphere), and "
        f"'narration' (the main character {character_name}'s actions, emotions, and/or dialogue, "
        f"written in a {tone} tone). "
        "Respond with ONLY valid JSON (no markdown fences): a JSON array with the SAME panels, "
        "keeping every original field (panel_number, title, scene_description, image_prompt) "
        "and adding caption and narration to each."
    )

    response = None
    last_exc = None
    for model in PRO_MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=json.dumps(panels),
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
            print(f"[Gemini Pro Error] {last_exc}")
        for panel in panels:
            panel.setdefault("caption", "")
            panel.setdefault("narration", panel.get("scene_description", ""))
        return panels


    try:
        story_panels = json.loads(response.text)
        if not isinstance(story_panels, list):
            raise ValueError("Expected a JSON list of panels")
    except (json.JSONDecodeError, TypeError, ValueError):
        story_panels = panels
        fallback_text = (response.text or "").strip()
        for panel in story_panels:
            panel.setdefault("caption", "")
            panel.setdefault("narration", fallback_text[:400])

    for panel in story_panels:
        panel.setdefault("caption", "")
        panel.setdefault("narration", "")

    return story_panels
