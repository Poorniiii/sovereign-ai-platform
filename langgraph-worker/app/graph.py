"""
graph.py — builds and compiles the LangGraph StateGraph.

This file wires together the nodes defined in nodes.py into an executable
directed graph.  The compiled graph object is a module-level singleton —
it is created once when Python first imports this module and then reused
for every incoming HTTP request.

Why a singleton?  Compiling a graph validates all nodes and edges (it would
raise an error right at startup if anything is misconfigured) and produces
an optimised execution plan.  Recompiling on every request would waste ~50ms
per call and provide no benefit.
"""

import logging

from langgraph.graph import StateGraph, START, END

from app.state import WorkflowState
from app.nodes import retriever_node, validator_node

logger = logging.getLogger(__name__)


def _build_graph():
    """
    Construct and compile the workflow graph.

    Graph topology (linear pipeline):

        START
          │
          ▼
      retriever          (retriever_node function)
      Embeds the query and fetches relevant document chunks from ChromaDB.
          │
          ▼
      validator          (validator_node function)
      Builds an LLM prompt from the chunks + contract text, calls Ollama,
      parses the structured response into verdict / confidence / answer.
          │
          ▼
         END

    To extend the pipeline later you would add nodes and edges here
    without touching nodes.py or main.py.
    """

    # StateGraph(WorkflowState) tells LangGraph:
    #   "the shared state for every node in this graph has the shape
    #    defined by the WorkflowState TypedDict".
    builder = StateGraph(WorkflowState)

    # add_node(name, function)
    #   name     — the internal label used when adding edges
    #   function — the Python function to call when this node executes
    builder.add_node("retriever", retriever_node)
    builder.add_node("validator", validator_node)

    # add_edge(from, to) — an unconditional, fixed transition.
    # START and END are special LangGraph constants (not strings).
    # The graph must always have exactly one START → first_node edge
    # and at least one last_node → END edge.
    builder.add_edge(START, "retriever")   # after START → run retriever
    builder.add_edge("retriever", "validator")  # after retriever → run validator
    builder.add_edge("validator", END)     # after validator → finish

    # compile() does two things:
    #   1. Validates the graph — raises ValueError if there are unreachable
    #      nodes, missing edges, or any other structural problem.
    #      This means misconfiguration is caught at startup, not mid-request.
    #   2. Returns a CompiledGraph object with an .invoke() method we can call.
    compiled = builder.compile()
    logger.info("LangGraph workflow graph compiled successfully")
    return compiled


# ── Module-level singleton ─────────────────────────────────────────────────
# This line runs ONCE when Python first does `from app.graph import graph`.
# All subsequent imports return the already-compiled object from Python's
# module cache — no recompilation.
graph = _build_graph()
