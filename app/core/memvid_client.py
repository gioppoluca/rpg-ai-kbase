import os
from typing import Any, Dict, Optional
import logging
import traceback
from pathlib import Path

from memvid_sdk import create, use, CapacityExceededError, LockedError, EmbeddingFailedError

from .config import settings

logger = logging.getLogger("app.core.memvid_client")


_MEM: Optional[Any] = None
_MEM_PATH: Optional[str] = None


def _resolve_memvid_path() -> str:
    # Always resolve to an absolute path to avoid “relative cwd surprises”
    #raw = getattr(settings, "memvid_path", None) or getattr(
    #    settings, "memvid_index", "knowledge.mv2"
    #)
    raw = "/tmp/knowledge.mp2"
    p = Path(raw).expanduser()
    if not p.is_absolute():
        # Make relative paths relative to current working directory
        p = Path(os.getcwd()) / p
    return str(p.resolve())


def get_memvid():
    """
    Return a cached Memvid instance (singleton).
    This avoids reopening/creating the underlying store for every chunk,
    which can cause MV013 I/O errors.
    """
    global _MEM, _MEM_PATH

    path = _resolve_memvid_path()
    if _MEM is not None and _MEM_PATH == path:
        return _MEM

    logger.info("Memvid get_memvid(): cwd=%s", os.getcwd())
    logger.info("Memvid path resolved: %s", path)

    parent = Path(path).parent
    parent.mkdir(parents=True, exist_ok=True)
    logger.info(
        "Ensured memvid parent dir exists: %s (exists=%s)", str(parent), parent.exists()
    )

    if os.path.exists(path):
        logger.info("Opening existing memvid file: %s", path)
#        _MEM = use(settings.memvid_kind, path)
        _MEM = use("basic", path, mode="auto")
    else:
        # IMPORTANT: create(path, kind) per Memvid docs
        # _MEM = create(path)
        _MEM = use("basic", path, mode="auto")
        # Verify immediately; if this fails we’ll know create didn’t materialize the file
        exists = Path(path).exists()
        size = Path(path).stat().st_size if exists else None
        logger.info(
            "After create(): exists=%s size_bytes=%s path=%s", exists, size, path
        )
        if not exists:
            logger.error(
                "Memvid file was not created at %s. Check working dir, mounts, and permissions.",
                path,
            )

    _MEM_PATH = path
    logger.info("Memvid instance ready: %s", str(_MEM))
    return _MEM


def seal_memvid() -> None:
    """Flush/close the cached Memvid instance safely."""
    global _MEM, _MEM_PATH
    if _MEM is None:
        return
    try:
        logger.info("Sealing memvid: %s", _MEM_PATH)
        _MEM.seal()
        logger.info("Memvid sealed OK: %s", _MEM_PATH)
    finally:
        _MEM = None
        _MEM_PATH = None


def put_chunk(
    *,
    mv: Any,
    title: str,
    label: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    logger.info("Putting chunk: title='%s', label='%s', text='%s'", str(title), str(label), text[:30])
    #    mem = get_memvid()
    logger.info("Memvid instance: %s", str(mv))
    # mem.put(title=title, label=label, metadata=metadata or {}, text=text)
    md = metadata or {}
    # Compatibility: memvid_sdk.put signature may differ (positional vs keyword).
    # Try keyword first (clear intent); fall back to positional if SDK rejects keywords.
    try:
        mv.put(title=title, label=label, text=text, metadata=md)
        logger.debug("mem.put() succeeded with keyword args")
        return
    except TypeError as e:
        logger.warning(
            "mem.put() keyword args rejected (%s). Falling back to positional.", str(e)
        )
    except CapacityExceededError:
        print("Storage capacity exceeded")
    except LockedError:
        print("File is locked by another process")
    except EmbeddingFailedError:
        print("Embedding generation failed")
    except Exception:
        logger.exception("mem.put() failed with keyword args")
        raise


# Fallback: common positional order variants
# try:
#    mv.put(title, label, text, md)
#    logger.debug(
#        "mem.put() succeeded with positional args (title,label,text,metadata)"
#    )
#    return
# except TypeError as e:
#    logger.warning(
#        "mem.put() positional (title,label,text,metadata) rejected (%s). Trying (text,metadata).",
#        str(e),
#    )

# Last fallback: minimal put(text, metadata)
#    try:
#        mem.put(text, md)
#        logger.debug("mem.put() succeeded with positional args (text,metadata)")
#        return
#    except Exception:
#        logger.error("mem.put() failed in all call variants. Raising.")
#        raise


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
