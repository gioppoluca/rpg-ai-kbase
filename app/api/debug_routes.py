from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.core.config import settings
from app.core.memvid_client import search

router = APIRouter(prefix="/api", tags=["debug"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/config")
async def config(_=Depends(require_api_key)):
    return {
        "md_dir": settings.md_dir,
        "pdf_dir": settings.pdf_dir,
        "memvid_path": settings.memvid_path,
        "top_k": settings.top_k,
    }


@router.post("/search")
async def debug_search(payload: dict, _=Depends(require_api_key)):
    query = payload.get("query", "")
    k = int(payload.get("k", settings.top_k))
    return {"hits": search(query, k=k)}
