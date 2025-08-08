from fastapi import APIRouter, HTTPException

from ..services.extract import load_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/{document_id}")
async def get_metrics(document_id: str) -> dict:
    data = load_metrics(document_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Metrics not found")
    return data