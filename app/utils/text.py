import re
from typing import List
import logging

logger = logging.getLogger("app.utils.text")

def approx_token_count(text: str) -> int:
    """A cheap token proxy: word count * 1.33.

    This keeps the skeleton dependency-light. You can swap to tiktoken later.
    """
    words = re.findall(r"\w+", text)
    return int(len(words) * 1.33) or 1


def split_by_token_target(text: str, *, target: int, max_tokens: int, overlap: int) -> List[str]:
    """Split a long text into token-ish windows with overlap.

    Uses sentence boundaries when possible.
    """
    # split into sentences-ish
    parts = re.split(r"(?<=[\.!?])\s+\n|(?<=[\.!?])\s{2,}|\n{2,}", text)
    parts = [p.strip() for p in parts if p.strip()]

    out: List[str] = []
    buf: List[str] = []
    buf_tokens = 0

    logger.info("Parts count: %d", len(parts))
    

    def flush_with_overlap():
        nonlocal buf, buf_tokens
        if not buf:
            return
        chunk = "\n\n".join(buf).strip()
        out.append(chunk)
        # build overlap tail
        if overlap <= 0:
            buf = []
            buf_tokens = 0
            return
        tail: List[str] = []
        tail_tokens = 0
        for p in reversed(buf):
            t = approx_token_count(p)
            if tail_tokens + t > overlap and tail:
                break
            tail.insert(0, p)
            tail_tokens += t
        buf = tail
        buf_tokens = tail_tokens

    for p in parts:
        logger.info("Processing part with approx %d tokens", approx_token_count(p))
        t = approx_token_count(p)
        if buf_tokens + t > max_tokens and buf:
            flush_with_overlap()
        buf.append(p)
        buf_tokens += t
        if buf_tokens >= target:
            flush_with_overlap()

    if buf:
        chunk = "\n\n".join(buf).strip()
        out.append(chunk)
    return out
