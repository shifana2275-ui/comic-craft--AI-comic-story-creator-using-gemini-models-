import urllib.parse
import urllib.request
import re
import uuid
from pathlib import Path

PANELS_DIR = Path("c:/Users/HP/Downloads/comiccraft_1/comiccraft/static/panels")
PANELS_DIR.mkdir(parents=True, exist_ok=True)

def _safe_filename(prompt: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", (prompt or "panel").strip().lower())[:40].strip("_")
    return f"{slug or 'panel'}_{uuid.uuid4().hex[:8]}.png"

def generate_pollinations_image(prompt: str, art_style: str = "comic book") -> str:
    full_prompt = f"{prompt}, comic book panel, {art_style} art style, vivid colors, highly detailed, dramatic lighting"
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
    
    print("Fetching image from Pollinations.ai:", url[:80] + "...")
    req = urllib.request.Request(url, headers={"User-Agent": "ComicCraft/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        img_bytes = resp.read()
        
    filename = _safe_filename(prompt)
    filepath = PANELS_DIR / filename
    filepath.write_bytes(img_bytes)
    return f"/static/panels/{filename}"

try:
    img_path = generate_pollinations_image("A brave superhero dog flying through the sky", "classic comic")
    print("SUCCESS! Generated image path:", img_path)
except Exception as e:
    print("FAILED:", e)
