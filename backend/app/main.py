from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.health import router as health_router
from .api.upload import router as upload_router
from .api.files import router as files_router
from .api.extract import router as extract_router
from .api.metrics import router as metrics_router


def create_application() -> FastAPI:
    app = FastAPI(title="Bank Financials Comparator", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(upload_router, prefix="/api")
    app.include_router(files_router, prefix="/api")
    app.include_router(extract_router, prefix="/api")
    app.include_router(metrics_router, prefix="/api")
    return app


app = create_application()