from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.core.memvid_client import search
from app.rag.ollama_client import ollama_chat


def format_citation(hit: Dict[str, Any]) -> str:
    meta = hit.get("metadata") or hit.get("meta") or {}
    source_file = meta.get("source_file") or meta.get("source") or "unknown"
    if meta.get("source_type") == "pdf" and meta.get("page"):
        return f"{source_file} p.{meta.get('page')}"
    if meta.get("source_type") == "md" and meta.get("section_path"):
        return f"{source_file} > {meta.get('section_path')}"
    return source_file


def build_context(hits: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    citations = []
    blocks = []
    for i, h in enumerate(hits, start=1):
        text = h.get("text") or h.get("snippet") or ""
        c = format_citation(h)
        citations.append(c)
        blocks.append(f"[SOURCE {i}] {c}\n{text}")
    return "\n\n".join(blocks), citations


async def answer(query: str) -> Dict[str, Any]:
    hits = search(query, k=settings.top_k)
    context, citations = build_context(hits)

    system = (
        "You are a RAG assistant. Answer using ONLY the sources below. "
        "If the sources do not contain the answer, say you don't know. "
        "When you use a fact, cite it like [SOURCE 1]."
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Question: {query}\n\nSources:\n{context}"},
    ]

    content = await ollama_chat(messages)
    return {"answer": content, "hits": hits, "citations": citations}
