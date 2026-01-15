import os
from typing import Any, Dict, Optional
import logging

from memvid_sdk import create, use

from .config import settings

logger = logging.getLogger("app.core.memvid_client")

def get_memvid():
    """Open existing memvid file or create if missing.

    NOTE: memvid_sdk.create() overwrites the file, so we only call it if the
    target path does not exist.
    """
    path = settings.memvid_path
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if os.path.exists(path):
        return use(settings.memvid_kind, path)
    return create(path)


def put_chunk(*, title: str, label: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    logger.info("Putting chunk: title='%s', label='%s'", str(title), str(label))
    mem = get_memvid()
    logger.info("Memvid instance: %s", str(mem))
    mem.put(title=title, label=label, metadata=metadata or {}, text=text)


def search(query: str, k: int) -> list[Dict[str, Any]]:
    mem = get_memvid()
    # mode: 'lex', 'sem', or default hybrid
    results = mem.find(query, k=k)
    # memvid-sdk returns dict-like objects; normalize defensively
    hits = []
    for r in results:
        if isinstance(r, dict):
            hits.append(r)
        else:
            # best effort
            hits.append(getattr(r, "__dict__", {"text": str(r)}))
    return hits
