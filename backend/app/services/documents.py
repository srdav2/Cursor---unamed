import json
import os
from dataclasses import dataclass
from typing import Optional

import fitz  # PyMuPDF
from fastapi import UploadFile

DATA_ROOT = "/workspace/data"
DOC_DIR = os.path.join(DATA_ROOT, "docs")
PREVIEW_DIR = os.path.join(DATA_ROOT, "previews")
INDEX_PATH = os.path.join(DATA_ROOT, "index.json")


os.makedirs(DOC_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)


@dataclass
class DocumentSaveResult:
    document_id: str
    num_pages: int
    bank_name: Optional[str]
    period_label: Optional[str]


def _load_index() -> dict:
    if not os.path.exists(INDEX_PATH):
        return {}
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_index(idx: dict) -> None:
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)


async def save_pdf_and_render_pages(
    document_id: str,
    uploaded_file: UploadFile,
    bank_name: Optional[str],
    period_label: Optional[str],
) -> DocumentSaveResult:
    pdf_path = os.path.join(DOC_DIR, f"{document_id}.pdf")
    with open(pdf_path, "wb") as out:
        while True:
            chunk = await uploaded_file.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)

    doc = fitz.open(pdf_path)
    num_pages = doc.page_count
    preview_subdir = os.path.join(PREVIEW_DIR, document_id)
    os.makedirs(preview_subdir, exist_ok=True)

    for i in range(num_pages):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=144)
        out_path = os.path.join(preview_subdir, f"page_{i}.png")
        pix.save(out_path)

    idx = _load_index()
    idx[document_id] = {
        "document_id": document_id,
        "pdf_path": pdf_path,
        "num_pages": num_pages,
        "bank": bank_name,
        "period": period_label,
        "previews_dir": preview_subdir,
    }
    _save_index(idx)

    return DocumentSaveResult(
        document_id=document_id,
        num_pages=num_pages,
        bank_name=bank_name,
        period_label=period_label,
    )


def get_document_meta(document_id: str) -> Optional[dict]:
    idx = _load_index()
    return idx.get(document_id)


def get_page_image_path(document_id: str, page_index: int) -> str:
    meta = get_document_meta(document_id)
    if meta is None:
        return os.path.join(PREVIEW_DIR, document_id, f"page_{page_index}.png")
    return os.path.join(meta["previews_dir"], f"page_{page_index}.png")