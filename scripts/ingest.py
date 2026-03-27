"""
ingest.py — Load documents into the ChromaDB vector store.

Run this script ONCE before starting the langgraph-worker, and again
whenever you add new documents to the knowledge base.

Usage:
    # From the repo root:
    python scripts/ingest.py

    # Or specify a custom folder:
    python scripts/ingest.py --source docs/knowledge-base

    # Or point at a single file:
    python scripts/ingest.py --source docs/knowledge-base/gdpr-articles.md

The script:
  1. Reads every .txt, .md, and .pdf file in the source folder
  2. Splits each file into overlapping 800-character chunks
  3. Embeds each chunk using Ollama nomic-embed-text
  4. Upserts (insert-or-update) into the sovereign_docs ChromaDB collection

Re-running on the same files is safe — we use content hashes as document IDs,
so ChromaDB upserts update existing entries rather than creating duplicates.
"""

import argparse
import hashlib
import logging
import os
import sys
from pathlib import Path

# ── Make sure we can import app.config from the langgraph-worker folder ─────
# sys.argv[0] is the script path.
# We want:  repo_root/langgraph-worker to be on the Python path so that
#           "from app.config import ..." works.
REPO_ROOT = Path(__file__).parent.parent
WORKER_DIR = REPO_ROOT / "langgraph-worker"
sys.path.insert(0, str(WORKER_DIR))

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_ollama import OllamaEmbeddings

from app.config import (
    CHROMA_PATH,
    CHROMA_COLLECTION,
    OLLAMA_URL,
    EMBED_MODEL,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# ── Chunking parameters ───────────────────────────────────────────────────────
# Documents are too long to embed whole — the embedding model has a token limit
# and a 50-page document would produce one giant, unfocused vector.
# We split into CHUNK_SIZE characters with CHUNK_OVERLAP characters of
# overlap between consecutive chunks.
#
# CHUNK_SIZE = 800 characters ≈ 150-200 words ≈ 1-2 paragraphs.
# CHUNK_OVERLAP = 100 characters — ensures a sentence split across a boundary
# is fully present in at least one chunk (context doesn't get orphaned).
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def chunk_text(text: str) -> list[str]:
    """
    Split *text* into overlapping windows of CHUNK_SIZE characters.

    Example with CHUNK_SIZE=10, CHUNK_OVERLAP=3:
      text   = "ABCDEFGHIJKLMNOPQRST"
      chunks = ["ABCDEFGHIJ",   (positions 0-9)
                "HIJKLMNOPQ",   (positions 7-16, overlapping by 3)
                "OPQRST"]       (positions 14-19)

    The stride between chunks is CHUNK_SIZE - CHUNK_OVERLAP.
    """
    chunks = []
    stride = CHUNK_SIZE - CHUNK_OVERLAP
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:               # skip chunks that are only whitespace
            chunks.append(chunk)
        start += stride
    return chunks


def read_file(path: Path) -> str:
    """
    Read the text content of a .txt, .md, or .pdf file.
    Returns an empty string if the file cannot be read.
    """
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        # Plain text — read directly.
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logger.warning("Could not read %s: %s", path, e)
            return ""

    if suffix == ".pdf":
        # PDF — use pypdf to extract text from every page.
        try:
            from pypdf import PdfReader  # imported lazily — only needed for PDFs
            reader = PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages)
        except Exception as e:
            logger.warning("Could not read PDF %s: %s", path, e)
            return ""

    logger.debug("Skipping unsupported file type: %s", path)
    return ""


def doc_id(chunk_text: str, source_path: str) -> str:
    """
    Generate a stable, unique ID for a chunk.

    We hash the (source file path + chunk content) with MD5.
    MD5 is used purely as a fingerprint/identifier here — not for security —
    so its cryptographic weaknesses don't matter.

    Using a content-based ID means:
      • Re-ingesting the same file → same IDs → ChromaDB upsert is a no-op
      • Ingesting a modified file → different IDs → new documents replace old ones
    """
    raw = f"{source_path}::{chunk_text}"
    return hashlib.md5(raw.encode()).hexdigest()


def collect_files(source: Path) -> list[Path]:
    """Return all .txt, .md, and .pdf files under *source* (recursive)."""
    if source.is_file():
        return [source]
    return sorted(
        p for p in source.rglob("*")
        if p.suffix.lower() in (".txt", ".md", ".pdf")
    )


def ingest(source: Path) -> None:
    """
    Main ingestion routine.
    1. Find all supported files under *source*
    2. Read + chunk each file
    3. Embed all chunks via Ollama
    4. Upsert into ChromaDB
    """

    # ── Find files ────────────────────────────────────────────────
    files = collect_files(source)
    if not files:
        logger.warning("No .txt/.md/.pdf files found under %s", source)
        return
    logger.info("Found %d file(s) to ingest from %s", len(files), source)

    # ── Open ChromaDB ─────────────────────────────────────────────
    # We open the database from this script the same way the worker does.
    # They share the same folder on disk, so documents written here are
    # immediately readable by the running worker (no restart needed).
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    # ── Set up embedder ───────────────────────────────────────────
    embedder = OllamaEmbeddings(
        base_url=OLLAMA_URL,
        model=EMBED_MODEL,
    )

    # ── Process each file ─────────────────────────────────────────
    total_chunks = 0

    for file_path in files:
        logger.info("Reading %s ...", file_path.name)
        text = read_file(file_path)
        if not text.strip():
            logger.warning("  No text extracted — skipping")
            continue

        chunks = chunk_text(text)
        logger.info("  %d chunks created", len(chunks))

        # Embed all chunks for this file in one batch call.
        # embed_documents() sends all chunks to Ollama in one HTTP request —
        # one API call, not N separate calls.  Much faster.
        embeddings = embedder.embed_documents(chunks)

        # Build the lists that ChromaDB's upsert expects.
        # upsert = "insert if new, update if already exists" (idempotent).
        ids       = [doc_id(chunk, str(file_path)) for chunk in chunks]
        # metadata lets us filter by source file later if we want.
        metadatas = [{"source": file_path.name} for _ in chunks]

        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        total_chunks += len(chunks)
        logger.info("  Upserted %d chunks from %s", len(chunks), file_path.name)

    logger.info(
        "\n✓ Ingestion complete — %d total chunks in collection '%s'",
        collection.count(),
        CHROMA_COLLECTION,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest documents into the Sovereign AI vector store."
    )
    parser.add_argument(
        "--source",
        default=str(REPO_ROOT / "docs" / "knowledge-base"),
        help="Path to a folder or single file to ingest "
             "(default: docs/knowledge-base/)",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        logger.error("Source path does not exist: %s", source_path)
        sys.exit(1)

    ingest(source_path)
