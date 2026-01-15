from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


async def ollama_chat(messages: List[Dict[str, str]], *, model: Optional[str] = None) -> str:
    """Call Ollama native /api/chat and return assistant text."""
    url = settings.ollama_base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model or settings.ollama_chat_model,
        "messages": messages,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
    return (data.get("message") or {}).get("content") or ""
