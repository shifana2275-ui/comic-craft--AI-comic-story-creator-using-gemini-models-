"""
exporters.py

Compiles the finished comic layout into a downloadable, multi-page PDF.
"""
import time
from pathlib import Path

from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "static" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def save_pdf(layout, title="ComicCraft Comic"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, f"Panel {panel.get('panel_number')}: {panel.get('title', '')}")
        pdf.ln(2)

        image_web_path = panel.get("image_path") or ""
        if image_web_path:
            image_fs_path = BASE_DIR / image_web_path.lstrip("/")
            if image_fs_path.exists():
                try:
                    pdf.image(str(image_fs_path), w=170)
                    pdf.ln(4)
                except RuntimeError:
                    pass

        if panel.get("scene_description"):
            pdf.set_font("Helvetica", "I", 11)
            pdf.multi_cell(0, 7, panel["scene_description"])
            pdf.ln(2)

        if panel.get("caption"):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, f"Caption: {panel['caption']}")
            pdf.ln(1)

        if panel.get("narration"):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, panel["narration"])

    timestamp = int(time.time())
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    filename = f"{safe_title or 'comic'}_{timestamp}.pdf"
    filepath = EXPORTS_DIR / filename
    pdf.output(str(filepath))
    return f"/static/exports/{filename}"
