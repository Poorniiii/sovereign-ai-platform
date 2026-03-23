from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="LangGraph Worker", version="1.0.0")

class WorkflowRequest(BaseModel):
    query: str
    file_content: str = ""
    workflow_id: str = ""

@app.get("/health")
def health():
    return {"status": "ok", "service": "langgraph-worker"}

@app.post("/run")
def run_workflow(request: WorkflowRequest):
    # graph.py will be wired in Phase 3
    return {
        "workflow_id": request.workflow_id,
        "status": "stub — Phase 3 will implement agents",
        "verdict": "NOT SUPPORTED",
        "confidence": 0,
        "answer": "",
        "retrieved_chunks": [],
    }