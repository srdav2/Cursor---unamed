from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from ..services.documents import get_page_image_path, get_document_meta


router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{document_id}/page/{page_index}.png")
async def get_page_png(document_id: str, page_index: int):
    meta = get_document_meta(document_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="Document not found")
    path = get_page_image_path(document_id, page_index)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Page image not found")
    return FileResponse(path, media_type="image/png")


@router.get("/{document_id}")
async def get_document(document_id: str):
    meta = get_document_meta(document_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return meta