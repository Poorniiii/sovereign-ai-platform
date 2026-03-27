"""
vectorstore.py — ChromaDB client and chunk-retrieval helper.

Everything here is initialised ONCE when the module is first imported
(module-level code runs once, then Python caches the module).
That means we open the database and load the embedding model once at
startup, not once per request — which would be extremely slow.
"""

import logging

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_ollama import OllamaEmbeddings

from app.config import CHROMA_PATH, CHROMA_COLLECTION, OLLAMA_URL, EMBED_MODEL

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# 1. Open (or create) the ChromaDB database on disk
# ------------------------------------------------------------------
# PersistentClient stores everything under CHROMA_PATH (./chroma_db by default).
# If the folder doesn't exist it is created automatically.
# If it already exists the existing data is loaded — no data loss on restart.
#
# anonymized_telemetry=False  →  ChromaDB phones home by default to collect
#                                usage stats.  We turn that off so no data
#                                leaves the machine.
_client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=ChromaSettings(anonymized_telemetry=False),
)

# ------------------------------------------------------------------
# 2. Get (or create) the collection
# ------------------------------------------------------------------
# A ChromaDB "collection" is like a table — it holds a set of documents
# and their vectors under a shared name.
# get_or_create_collection is idempotent:
#   • First run  → creates an empty collection called "sovereign_docs"
#   • Every subsequent run → returns the existing populated collection
#
# cosine distance is the best similarity metric for text embeddings.
# It measures the angle between two vectors — semantically similar sentences
# point in the same direction regardless of length.
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    metadata={"hnsw:space": "cosine"},
)

# ------------------------------------------------------------------
# 3. Set up the embedding model (talks to Ollama)
# ------------------------------------------------------------------
# OllamaEmbeddings wraps the Ollama HTTP API.
# When we call _embedder.embed_query("some text") it sends an HTTP request
# to Ollama which runs nomic-embed-text and returns a list of floats (the vector).
#
# WHY THE SAME MODEL FOR INGEST AND QUERY:
# The embedding model converts text into a point in high-dimensional space.
# If you used model A to store documents and model B to embed the query,
# the points live in completely different spaces — similarity comparisons
# would be meaningless (like comparing GPS coordinates to postcode districts).
_embedder = OllamaEmbeddings(
    base_url=OLLAMA_URL,
    model=EMBED_MODEL,
)


# ------------------------------------------------------------------
# 4. The public function called by retriever_node
# ------------------------------------------------------------------

def retrieve_chunks(query: str, n_results: int = 5) -> list[str]:
    """
    Convert *query* to a vector, ask ChromaDB for the n_results most
    similar document chunks, and return them as plain strings.

    Returns an empty list if the collection is empty or Ollama is down.
    The validator_node handles an empty list gracefully.
    """
    # Step A: embed the query
    # This calls Ollama → nomic-embed-text → returns a list of ~768 floats.
    # e.g. [0.012, -0.834, 0.441, ...]
    try:
        query_vector = _embedder.embed_query(query)
    except Exception:
        logger.warning("Embedding failed — returning empty chunk list", exc_info=True)
        return []

    # Step B: ask ChromaDB for the n_results nearest vectors
    # ChromaDB compares the query vector to every stored document vector
    # using cosine similarity and returns the closest ones.
    # results is a dict like:
    # {
    #   "documents": [["chunk text 1", "chunk text 2", ...]],  ← nested list
    #   "distances": [[0.12, 0.18, ...]],
    #   "ids":       [["doc_abc", "doc_def", ...]]
    # }
    # The outer list has one entry per query (we only send one query at a time).
    # [0] unwraps that outer list to get the list of matching strings.
    try:
        results = _collection.query(
            query_embeddings=[query_vector],
            n_results=min(n_results, _collection.count()),  # can't ask for more than exist
        )
    except Exception:
        logger.warning("ChromaDB query failed — returning empty chunk list", exc_info=True)
        return []

    documents: list[str] = results.get("documents", [[]])[0]
    logger.info("Retrieved %d chunks for query: %.60s...", len(documents), query)
    return documents
