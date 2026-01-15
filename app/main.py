from fastapi import FastAPI
import logging
import os
from app.api.debug_routes import router as debug_router
from app.api.ingest_routes import router as ingest_router
from app.api.openai_routes import router as openai_router
from fastapi.middleware.cors import CORSMiddleware

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


setup_logging()
logger = logging.getLogger("app")

app = FastAPI(
    title="OpenWebUI RAG Gateway",
    version="0.1.0",
    description="OpenAI-compatible API for Open WebUI, backed by Memvid + Ollama.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(debug_router)
app.include_router(ingest_router)
app.include_router(openai_router)


@app.on_event("startup")
def _startup_logs():
    logger.info("Starting OpenWebUI RAG Backend")
    logger.info("LOG_LEVEL=%s", LOG_LEVEL)
    # Log important env vars
    logger.info("MEMVID_DIR=%s", os.getenv("MEMVID_DIR"))
    logger.info("MEMVID_INDEX=%s", os.getenv("MEMVID_INDEX"))
    logger.info("DATA_MD_DIR=%s", os.getenv("DATA_MD_DIR"))
    logger.info("DATA_PDF_DIR=%s", os.getenv("DATA_PDF_DIR"))
    logger.info("OLLAMA_BASE_URL=%s", os.getenv("OLLAMA_BASE_URL"))
    logger.info("OLLAMA_CHAT_MODEL=%s", os.getenv("OLLAMA_CHAT_MODEL"))
    logger.info("OLLAMA_EMBED_MODEL=%s", os.getenv("OLLAMA_EMBED_MODEL"))
