"""
nodes.py — the two graph nodes.

A LangGraph node is just a function with this signature:
    def my_node(state: WorkflowState) -> dict:
        ...
        return {"field_to_update": new_value, ...}

LangGraph calls the function, takes the returned dict, and merges it into
the shared state automatically.  You only return the fields you changed —
everything else stays as-is.
"""

import logging
import re

from langchain_ollama import ChatOllama

from app.config import OLLAMA_URL, LLM_MODEL, TOP_K
from app.state import WorkflowState
from app.vectorstore import retrieve_chunks

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Node 1 — Retriever
# ══════════════════════════════════════════════════════════════════

def retriever_node(state: WorkflowState) -> dict:
    """
    Pull the most relevant document chunks from ChromaDB for the user's query.

    Reads:   state["query"]
    Writes:  state["retrieved_chunks"]
    """
    logger.info("[retriever] fetching chunks for workflow %s", state["workflow_id"])

    # retrieve_chunks sends the query to Ollama for embedding, then asks
    # ChromaDB for the TOP_K most similar document chunks.
    # Returns [] if the collection is empty or Ollama is unreachable.
    chunks = retrieve_chunks(state["query"], n_results=TOP_K)

    logger.info("[retriever] got %d chunks", len(chunks))

    # Return ONLY the field we changed.  LangGraph merges this dict into
    # the shared state — all other fields are untouched.
    return {"retrieved_chunks": chunks}


# ══════════════════════════════════════════════════════════════════
# Node 2 — Validator
# ══════════════════════════════════════════════════════════════════

def validator_node(state: WorkflowState) -> dict:
    """
    Ask the LLM to reason about the query given the retrieved context and
    any contract text the user supplied.  Parse the structured response.

    Reads:   state["query"], state["file_content"], state["retrieved_chunks"]
    Writes:  state["verdict"], state["confidence"], state["answer"]
    """
    logger.info("[validator] running LLM for workflow %s", state["workflow_id"])

    # ── Build the context block ────────────────────────────────────
    # If retrieval found chunks, join them with blank lines between them
    # so the LLM sees them as distinct paragraphs.
    # If the collection was empty we still proceed — the LLM will answer
    # from its training data and from file_content alone.
    chunks = state["retrieved_chunks"]
    if chunks:
        context_block = "\n\n".join(chunks)
    else:
        context_block = "No relevant policy documents were found in the knowledge base."

    # ── Build the prompt ───────────────────────────────────────────
    # We use a structured output format (VERDICT / CONFIDENCE / REASONING)
    # so we can reliably parse the answer with a regex.
    # The three sections are clearly labelled and the user's input is
    # inserted as quoted blocks — this reduces prompt injection risk because
    # the LLM sees them as "data to analyse", not as instructions to follow.
    contract_text = state["file_content"] or "No contract text was provided."

    prompt = f"""You are a legal compliance expert specialising in data protection law.
Analyse the contract text below against the provided policy documents and answer the question.

=== RELEVANT POLICY DOCUMENTS ===
{context_block}

=== CONTRACT TEXT ===
{contract_text}

=== QUESTION ===
{state["query"]}

Respond in EXACTLY this format — no extra text before or after:
VERDICT: [COMPLIANT | NON-COMPLIANT | UNCERTAIN]
CONFIDENCE: [a decimal between 0.0 and 1.0]
REASONING: [your explanation in 1-3 sentences]"""

    # ── Call the LLM ───────────────────────────────────────────────
    # ChatOllama is a LangChain wrapper around Ollama's HTTP API.
    # We create it fresh each call — the object is stateless (no chat history).
    # temperature=0 makes responses deterministic / less creative, which is
    # what we want for compliance analysis (consistency over creativity).
    llm = ChatOllama(
        base_url=OLLAMA_URL,
        model=LLM_MODEL,
        temperature=0,
    )

    try:
        response = llm.invoke(prompt)
        raw_text: str = response.content
    except Exception:
        logger.error("[validator] LLM call failed", exc_info=True)
        # Return safe defaults — the graph continues, returns UNCERTAIN
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.0,
            "answer": "LLM unavailable — could not generate a verdict.",
        }

    logger.info("[validator] raw LLM output: %.120s...", raw_text)

    # ── Parse the response ─────────────────────────────────────────
    verdict, confidence, answer = _parse_llm_response(raw_text)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "answer": answer,
    }


# ══════════════════════════════════════════════════════════════════
# Private helper — parse the LLM's structured response
# ══════════════════════════════════════════════════════════════════

def _parse_llm_response(text: str) -> tuple[str, float, str]:
    """
    Extract VERDICT, CONFIDENCE, and REASONING from the LLM's response.

    Returns safe defaults if the LLM didn't follow the format.

    Why regex rather than split()?  The LLM sometimes adds spaces,
    colons, or slightly different casing.  re.search is forgiving about
    whitespace and finds the pattern anywhere in the text.
    """

    # ── VERDICT ────────────────────────────────────────────────────
    # Look for "VERDICT:" followed by one of the three allowed values.
    # re.IGNORECASE handles "verdict: Compliant" vs "VERDICT: COMPLIANT".
    verdict_match = re.search(
        r"VERDICT\s*:\s*(COMPLIANT|NON-COMPLIANT|UNCERTAIN)",
        text,
        re.IGNORECASE,
    )
    verdict = verdict_match.group(1).upper() if verdict_match else "UNCERTAIN"

    # ── CONFIDENCE ─────────────────────────────────────────────────
    # Look for "CONFIDENCE:" followed by a decimal number (0.85, .9, 1, etc.)
    confidence_match = re.search(
        r"CONFIDENCE\s*:\s*([0-9]*\.?[0-9]+)",
        text,
        re.IGNORECASE,
    )
    if confidence_match:
        raw_conf = float(confidence_match.group(1))
        # Normalise to [0.0, 1.0]:
        #   <= 1.0        → already a fraction, use as-is  (e.g. 0.85)
        #   1.0 < x <=100 → LLM returned a percentage, divide by 100 (e.g. 85 → 0.85)
        #   > 100         → nonsensical value, clamp to 1.0 (e.g. 150 → 1.0)
        if raw_conf <= 1.0:
            confidence = raw_conf
        elif raw_conf <= 100.0:
            confidence = raw_conf / 100.0
        else:
            confidence = 1.0
        confidence = max(0.0, min(1.0, confidence))  # final safety clamp
    else:
        confidence = 0.0

    # ── REASONING ─────────────────────────────────────────────────
    # Everything after "REASONING:" to the end of the string.
    # re.DOTALL makes . match newlines too (multi-line reasoning).
    reasoning_match = re.search(
        r"REASONING\s*:\s*(.+)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    answer = reasoning_match.group(1).strip() if reasoning_match else text.strip()

    return verdict, confidence, answer
