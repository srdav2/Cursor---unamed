from __future__ import annotations

import os
from typing import Tuple

import fitz  # PyMuPDF
from PIL import Image, ImageDraw


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def render_cell_screenshot(
    pdf_path: str,
    page_index: int,
    bbox: Tuple[float, float, float, float] | None,
    output_path: str,
    margin_points: int = 8,
    scale: float = 2.0,
    highlight_color: Tuple[int, int, int] = (255, 0, 0),
    highlight_width_px: int = 4,
    highlight_fill_rgba: Tuple[int, int, int, int] | None = (255, 0, 0, 48),
) -> str:
    """
    Render a screenshot for the given cell bbox. If bbox is None, render full page.

    - margin_points: expand the clip rect around bbox by this many PDF points
    - scale: upscale factor for clarity
    - highlight: draw an outline and optional translucent fill over the cell region
    """
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_index]
        if bbox is None:
            clip = page.rect
            inner_rect = None
        else:
            x0, top, x1, bottom = bbox
            clip = fitz.Rect(x0 - margin_points, top - margin_points, x1 + margin_points, bottom + margin_points)
            clip = clip & page.rect  # intersect to page bounds
            inner_rect = fitz.Rect(x0, top, x1, bottom)

        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix, clip=clip)
        mode = "RGBA" if pix.alpha else "RGB"
        image = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        draw = ImageDraw.Draw(image, "RGBA")

        if inner_rect is not None:
            # Transform PDF coordinates to image pixel coordinates relative to clip
            def to_px_rect(r: fitz.Rect) -> tuple[int, int, int, int]:
                x0 = int((r.x0 - clip.x0) * scale)
                y0 = int((r.y0 - clip.y0) * scale)
                x1 = int((r.x1 - clip.x1) * scale)
                y1 = int((r.y1 - clip.y1) * scale)
                # Clamp to image bounds
                x0 = max(0, min(x0, image.width - 1))
                y0 = max(0, min(y0, image.height - 1))
                x1 = max(0, min(x1, image.width - 1))
                y1 = max(0, min(y1, image.height - 1))
                return x0, y0, x1, y1

            px_rect = to_px_rect(inner_rect)
            if highlight_fill_rgba is not None:
                draw.rectangle(px_rect, fill=highlight_fill_rgba)
            draw.rectangle(px_rect, outline=highlight_color, width=highlight_width_px)

        ensure_directory(os.path.dirname(output_path))
        image.save(output_path)
        return output_path
    finally:
        doc.close()
