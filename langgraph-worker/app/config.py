"""
Worker configuration — all settings in one place.

Values are read from environment variables.  docker-compose.yml injects
OLLAMA_URL so the worker can reach the host-machine Ollama process.
Everything else falls back to a sensible local default.
"""

import os
from pathlib import Path

# Absolute path to the repo root (two levels up from langgraph-worker/app/)
# This makes CHROMA_PATH consistent regardless of which directory Python
# is run from — both ingest.py and the worker will always resolve to
# sovereign-ai-platform/chroma_db/
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ------------------------------------------------------------------
# Ollama connection
# ------------------------------------------------------------------

# The HTTP base URL of the Ollama server.
# When running locally (no Docker) → http://localhost:11434
# When running inside the langgraph-worker container → docker-compose.yml
# sets this to http://host.docker.internal:11434 (reaches the host machine).
OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")

# The Ollama model used to turn text into numbers (vectors).
# nomic-embed-text is purpose-built for embeddings — fast and accurate.
# Must be the SAME model used both at ingest-time and at query-time so that
# the vectors are comparable.
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "nomic-embed-text")

# The Ollama model used to read the retrieved chunks and write a verdict.
# llama3.1:8b gives high-quality answers and is already installed locally.
# Swap to llama3.2:3b or mistral:7b here for a smaller/faster model.
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.1:8b")

# ------------------------------------------------------------------
# ChromaDB
# ------------------------------------------------------------------

# Where ChromaDB saves its data on disk.
# Defaults to an absolute path at the repo root so both ingest.py and the
# worker always read/write the same folder regardless of cwd.
# docker-compose.yml overrides this with CHROMA_PATH=/app/chroma_db.
CHROMA_PATH: str = os.getenv("CHROMA_PATH", str(_REPO_ROOT / "chroma_db"))

# The logical "table" (ChromaDB calls it a collection) where our documents live.
# The ingest script and the worker both use this name — they must match.
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "sovereign_docs")

# ------------------------------------------------------------------
# Retrieval parameters
# ------------------------------------------------------------------

# How many document chunks to pull back from ChromaDB for each query.
# 5 is a good balance: enough context for the LLM, not so much that it
# gets diluted or exceeds the model's context window.
TOP_K: int = int(os.getenv("TOP_K", "5"))
