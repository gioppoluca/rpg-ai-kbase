from fastapi import APIRouter, Depends, HTTPException
import logging
from app.api.deps import require_api_key
from app.ingest.md_ingest import ingest_md_dir, ingest_md_file
from app.ingest.pdf_ingest import ingest_pdf_dir, ingest_pdf_file
from app.core.memvid_client import seal_memvid, get_memvid

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
    try:
        logger.info("API call: /api/ingest/all")
        mv = get_memvid()
        md = ingest_md_dir(mv_client=mv)
        pdf = ingest_pdf_dir(mv_client=mv)
        # Important: flush/close once at the end
        seal_memvid()
        return {"md": md, "pdf": pdf}
    except Exception as e:
        # Ensure we don't leave the store in a bad state on failure
        try:
            seal_memvid()
        except Exception:
            logger.exception("Failed sealing memvid after ingest failure")
        logger.exception("Ingest ALL failed")
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")
