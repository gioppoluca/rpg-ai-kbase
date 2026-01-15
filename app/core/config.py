import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    data_md_dir: str = os.getenv("DATA_MD_DIR", "/app/data/md")
    data_pdf_dir: str = os.getenv("DATA_PDF_DIR", "/app/data/pdf")
    memvid_dir: str = os.getenv("MEMVID_DIR", "/app/memvid")
    memvid_index: str = os.getenv("MEMVID_INDEX", "/app/memvid/kb.mv2")
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen2.5:7b-instruct"
    ollama_embed_model: str = "nomic-embed-text"

    # Memvid
    memvid_kind: str = "basic"
    memvid_path: str = "./memvid_store/knowledge.mv2"

    # Knowledge-base folders
    md_dir: str = "./data/md"
    pdf_dir: str = "./data/pdf"

    # Chunking
    md_chunk_target_tokens: int = 900
    md_chunk_max_tokens: int = 1200
    md_chunk_min_tokens: int = 50
    md_chunk_overlap_tokens: int = 120

    pdf_chunk_target_tokens: int = 850
    pdf_chunk_max_tokens: int = 1150
    pdf_chunk_min_tokens: int = 200
    pdf_chunk_overlap_tokens: int = 120

    # Retrieval
    top_k: int = 6
    snippet_chars: int = 350

    # Simple auth (optional)
    api_key: str | None = None


settings = Settings()


def resolve_path(p: str) -> str:
    # Make sure we always resolve relative paths the same way
    return os.path.abspath(p)
