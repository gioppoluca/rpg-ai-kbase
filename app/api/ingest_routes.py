from fastapi import APIRouter, Depends
import logging
from app.api.deps import require_api_key
from app.ingest.md_ingest import ingest_md_dir, ingest_md_file
from app.ingest.pdf_ingest import ingest_pdf_dir, ingest_pdf_file

router = APIRouter(prefix="/api", tags=["ingest"])
logger = logging.getLogger("app.api")

@router.post("/ingest/md")
async def ingest_md(_=Depends(require_api_key)):
    logger.info("API call: /api/ingest/md")
    return ingest_md_dir()


@router.post("/ingest/pdf")
async def ingest_pdf(_=Depends(require_api_key)):
    return ingest_pdf_dir()


@router.post("/ingest/all")
async def ingest_all(_=Depends(require_api_key)):
    logger.info("API call: /api/ingest/all")
    md = ingest_md_dir()
    pdf = ingest_pdf_dir()
    return {"md": md, "pdf": pdf}
