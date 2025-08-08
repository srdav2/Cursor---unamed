from fastapi import APIRouter, HTTPException

from ..services.extract import extract_document, save_metrics

router = APIRouter(prefix="/extract", tags=["extract"])


@router.post("/{document_id}")
async def run_extraction(document_id: str) -> dict:
    try:
        results = extract_document(document_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Extraction failed: {exc}")

    out_path = save_metrics(document_id, results)
    return {"document_id": document_id, "num_metrics": len(results), "path": out_path}