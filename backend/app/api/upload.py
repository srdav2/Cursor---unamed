from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi import status
from typing import Optional
import uuid

from ..services.documents import (
    save_pdf_and_render_pages,
    DocumentSaveResult,
)


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    bank: Optional[str] = Form(None),
    period: Optional[str] = Form(None),
) -> dict:
    if file.content_type not in {"application/pdf"}:
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    document_id = str(uuid.uuid4())
    try:
        result: DocumentSaveResult = await save_pdf_and_render_pages(
            document_id=document_id,
            uploaded_file=file,
            bank_name=bank,
            period_label=period,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {exc}")

    return {
        "document_id": result.document_id,
        "num_pages": result.num_pages,
        "bank": result.bank_name,
        "period": result.period_label,
    }