import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import logging
import yaml

from app.core.config import settings
from app.core.memvid_client import put_chunk
from app.utils.text import approx_token_count, split_by_token_target
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
logger = logging.getLogger("app.ingest")

@dataclass
class MdDoc:
    path: str
    frontmatter: Dict[str, Any]
    body: str


def parse_md(path: str) -> MdDoc:
    raw = open(path, "r", encoding="utf-8").read()
    frontmatter: Dict[str, Any] = {}
    body = raw
    m = FRONTMATTER_RE.match(raw)
    if m:
        fm_text = m.group(1)
        body = raw[m.end():]
        try:
            frontmatter = yaml.safe_load(fm_text) or {}
        except Exception:
            frontmatter = {}
    return MdDoc(path=path, frontmatter=frontmatter, body=body)


def header_chunks(body: str) -> List[Tuple[str, str]]:
    """Split markdown by headings, returning (section_path, text)."""
    lines = body.splitlines()
    chunks: List[Tuple[str, List[str]]] = []
    path: List[str] = []
    buf: List[str] = []

    def flush():
        nonlocal buf
        text = "\n".join(buf).strip()
        if text:
            chunks.append((" > ".join(path) if path else "", text.splitlines()))
        buf = []

    for line in lines:
        h = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if h:
            flush()
            level = len(h.group(1))
            title = h.group(2).strip()
            # adjust path stack
            if level <= len(path):
                path = path[: level - 1]
            while len(path) < level - 1:
                path.append("(untitled)")
            if len(path) == level - 1:
                path.append(title)
            else:
                path[level - 1] = title
            continue
        buf.append(line)
    flush()

    out: List[Tuple[str, str]] = []
    for p, ls in chunks:
        out.append((p, "\n".join(ls).strip()))
    return out


def build_embed_prefix(frontmatter: Dict[str, Any], filename: str) -> str:
    title = frontmatter.get("title") or frontmatter.get("name") or os.path.splitext(os.path.basename(filename))[0]
    doc_type = frontmatter.get("type") or frontmatter.get("doc_type")
    tags = frontmatter.get("tags")
    aliases = frontmatter.get("aliases")

    parts = [f"Doc: {title}"]
    if doc_type:
        parts.append(f"type: {doc_type}")
    if tags:
        if isinstance(tags, list):
            parts.append("tags: " + ", ".join(map(str, tags)))
        else:
            parts.append(f"tags: {tags}")
    if aliases:
        if isinstance(aliases, list):
            parts.append("aliases: " + ", ".join(map(str, aliases)))
        else:
            parts.append(f"aliases: {aliases}")
    return "[" + " | ".join(parts) + "]\n\n"


def ingest_md_file(path: str) -> int:
    doc = parse_md(path)
    filename = os.path.basename(path)
    prefix = build_embed_prefix(doc.frontmatter, filename)
    md_dir = Path(settings.data_md_dir)
    logger.info("Starting MD ingestion")
    logger.info("MD dir: %s (exists=%s)", md_dir, md_dir.exists())
    logger.info("Memvid index path: %s", settings.memvid_index)

    # split by headings, then token-window
    raw_sections = header_chunks(doc.body)
    logger.info("MD file '%s' has %d sections", filename, len(raw_sections))

    emitted = 0
    for section_path, section_text in raw_sections:
        if not section_text.strip():
            continue
        merged_text = prefix + (f"Section: {section_path}\n\n" if section_path else "") + section_text
        logger.info("Merged Text '%s'", merged_text)
        # token split (approx)
        for idx, chunk_text in enumerate(
            split_by_token_target(
                merged_text,
                target=settings.md_chunk_target_tokens,
                max_tokens=settings.md_chunk_max_tokens,
                overlap=settings.md_chunk_overlap_tokens,
            )
        ):
            if approx_token_count(chunk_text) < settings.md_chunk_min_tokens:
                logger.info("Skipping small MD chunk: file=%s section='%s' chunk_index=%d tokens=%d",
                            filename, section_path, idx, approx_token_count(chunk_text))
                continue
            metadata = {
                "source_type": "md",
                "source_file": filename,
                "path": path,
                "section_path": section_path,
                "chunk_index": idx,
                "frontmatter": doc.frontmatter,
            }
            logger.info(
                "Emitting MD chunk: file=%s section='%s' chunk_index=%d tokens=%d",
                filename,
                section_path,
                idx,
                approx_token_count(chunk_text),
            )
            title = doc.frontmatter.get("title") or doc.frontmatter.get("name") or filename
            label = doc.frontmatter.get("type") or "md"
            logger.info("Putting chunk to Memvid: title='%s' label='%s'", str(title), str(label))
            put_chunk(title=str(title), label=str(label), text=chunk_text, metadata=metadata)
            emitted += 1
    return emitted


def ingest_md_dir(md_dir: str | None = None) -> Dict[str, int]:
    md_dir = md_dir or settings.md_dir
    stats = {"files": 0, "chunks": 0}
    logger.info("Ingesting MD directory: %s", md_dir)
    for root, _, files in os.walk(md_dir):
        for f in files:
            if not f.lower().endswith(".md"):
                continue
            stats["files"] += 1
            stats["chunks"] += ingest_md_file(os.path.join(root, f))
    return stats
