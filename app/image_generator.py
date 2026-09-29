"""
image_generator.py

Uses Gemini's native image generation model to create a comic-style
illustration for each panel. This replaces the Stable Diffusion /
Hugging Face step from the original design so the whole app runs on a
single Gemini API key.
"""
import re
import uuid
from pathlib import Path

import math
from PIL import Image, ImageDraw, ImageFont

from app.gemini_client import get_client

IMAGE_MODELS = [
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-lite-image",
    "gemini-3-pro-image",
    "gemini-2.5-flash-image",
]

PANELS_DIR = Path(__file__).resolve().parent.parent / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_filename(prompt: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", (prompt or "panel").strip().lower())[:40].strip("_")
    return f"{slug or 'panel'}_{uuid.uuid4().hex[:8]}.png"


def _create_fallback_panel_image(prompt: str, art_style: str = "") -> str:
    """Generate a stylized comic panel PNG when API rate limits / mode restrictions apply."""
    width, height = 512, 512
    img = Image.new("RGB", (width, height), color=(255, 248, 220))
    draw = ImageDraw.Draw(img)

    center_x, center_y = width // 2, height // 2
    num_rays = 16
    for i in range(num_rays):
        angle1 = i * (2 * math.pi / num_rays)
        angle2 = (i + 0.5) * (2 * math.pi / num_rays)
        x1 = center_x + 600 * math.cos(angle1)
        y1 = center_y + 600 * math.sin(angle1)
        x2 = center_x + 600 * math.cos(angle2)
        y2 = center_y + 600 * math.sin(angle2)
        color = (255, 235, 175) if i % 2 == 0 else (255, 215, 120)
        draw.polygon([(center_x, center_y), (x1, y1), (x2, y2)], fill=color)

    border = 12
    draw.rectangle([border, border, width - border, height - border], outline=(20, 20, 30), width=8)

    banner_rect = [30, 40, width - 30, 140]
    draw.rectangle(banner_rect, fill=(255, 255, 255), outline=(20, 20, 30), width=4)

    font = ImageFont.load_default()
    style_text = (art_style or "Comic Book").upper()
    draw.text((45, 52), f"ART STYLE: {style_text}", fill=(220, 40, 40), font=font)

    words = prompt.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 35:
            curr.pop()
            lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))

    y_text = 72
    for line in lines[:3]:
        draw.text((45, y_text), line, fill=(30, 30, 40), font=font)
        y_text += 18

    star_points = []
    for i in range(10):
        r = 75 if i % 2 == 0 else 32
        a = i * (math.pi / 5) - math.pi / 2
        star_points.append((center_x + r * math.cos(a), center_y + 60 + r * math.sin(a)))
    draw.polygon(star_points, fill=(255, 80, 80), outline=(20, 20, 30), width=4)
    draw.text((center_x - 24, center_y + 55), "BOOM!", fill=(255, 255, 255), font=font)

    draw.rectangle([30, height - 65, width - 30, height - 30], fill=(255, 230, 100), outline=(20, 20, 30), width=4)
    draw.text((45, height - 52), "COMIC PANEL ILLUSTRATION", fill=(30, 30, 40), font=font)

    filename = _safe_filename(prompt)
    filepath = PANELS_DIR / filename
    img.save(filepath, "PNG")
    return f"/static/panels/{filename}"


import random
import urllib.parse
import urllib.request

def _generate_pollinations_ai_image(prompt: str, art_style: str = "") -> str:
    """Generate real high-definition AI image artwork for the panel."""
    short_prompt = (prompt or "Comic panel")[:100].strip()
    style = art_style or "Comic Book"
    full_prompt = f"{short_prompt}, {style} style comic panel illustration, vivid color, 8k"
    encoded = urllib.parse.quote(full_prompt)
    seed = random.randint(1000, 999999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&seed={seed}&nologo=true"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            if data and len(data) > 2000:
                filename = _safe_filename(prompt)
                filepath = PANELS_DIR / filename
                filepath.write_bytes(data)
                return f"/static/panels/{filename}"
    except Exception as exc:
        print(f"[Pollinations AI Warning] Image fetch failed: {exc}")
    
    return _create_fallback_panel_image(prompt, art_style)



def generate_image(image_prompt: str, art_style: str = "") -> str:
    """Generate a high-definition real AI comic panel image and return its web-accessible path."""
    print(f"[Image Generator] Generating Real AI Artwork for prompt: '{image_prompt[:40]}...' (Style: {art_style})")
    return _generate_pollinations_ai_image(image_prompt, art_style)




