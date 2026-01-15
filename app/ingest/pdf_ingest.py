import os
import re
from typing import Dict, List

from pypdf import PdfReader

from app.core.config import settings
from app.core.memvid_client import put_chunk
from app.utils.text import approx_token_count, split_by_token_target


def extract_pdf_pages(path: str) -> List[str]:
    reader = PdfReader(path)
    pages = []
    for p in reader.pages:
        text = p.extract_text() or ""
        # normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        pages.append(text)
    return pages


def ingest_pdf_file(path: str) -> int:
    filename = os.path.basename(path)
    pages = extract_pdf_pages(path)

    emitted = 0
    for page_idx, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue
        # chunk by paragraphs-ish then token windows
        page_text = page_text.replace("\r", "")
        prefix = f"[Doc: {os.path.splitext(filename)[0]} | source: pdf | page: {page_idx}]\n\n"
        merged = prefix + page_text
        for idx, chunk_text in enumerate(
            split_by_token_target(
                merged,
                target=settings.pdf_chunk_target_tokens,
                max_tokens=settings.pdf_chunk_max_tokens,
                overlap=settings.pdf_chunk_overlap_tokens,
            )
        ):
            if approx_token_count(chunk_text) < settings.pdf_chunk_min_tokens:
                continue
            metadata = {
                "source_type": "pdf",
                "source_file": filename,
                "path": path,
                "page": page_idx,
                "chunk_index": idx,
            }
            title = os.path.splitext(filename)[0]
            label = "pdf"
            put_chunk(title=title, label=label, text=chunk_text, metadata=metadata)
            emitted += 1
    return emitted


def ingest_pdf_dir(pdf_dir: str | None = None) -> Dict[str, int]:
    pdf_dir = pdf_dir or settings.pdf_dir
    stats = {"files": 0, "chunks": 0}
    for root, _, files in os.walk(pdf_dir):
        for f in files:
            if not f.lower().endswith(".pdf"):
                continue
            stats["files"] += 1
            stats["chunks"] += ingest_pdf_file(os.path.join(root, f))
    return stats
