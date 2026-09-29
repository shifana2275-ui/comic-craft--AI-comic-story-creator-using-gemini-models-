"""
layout_builder.py

Combines each panel's generated image with its story text into a
single structured layout ready for the preview page and PDF export.
"""


def build_comic_layout(panels):
    layout = []
    for panel in panels:
        layout.append(
            {
                "panel_number": panel.get("panel_number"),
                "title": panel.get("title", ""),
                "image_path": panel.get("image_path", ""),
                "image_error": panel.get("image_error", ""),
                "scene_description": panel.get("scene_description", ""),
                "caption": panel.get("caption", ""),
                "narration": panel.get("narration", ""),
                "image_prompt": panel.get("image_prompt", ""),
            }
        )
    layout.sort(key=lambda p: p["panel_number"] if p["panel_number"] is not None else 0)
    return layout
