# Sovereign AI Platform

A full-stack AI compliance analysis platform built for the Sovereign AI Assessment. The platform allows users to upload contract documents, ask compliance questions, and receive AI-powered verdicts grounded in regulatory policy — all with role-based access control, a tamper-evident audit trail, and a local-first LLM runtime.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        k3s / Rancher Desktop (Phase 5)                       │
│                                                                               │
│  ┌─────────────────┐   HTTP + JWT   ┌─────────────────┐  Trigger Workflow   │
│  │  React Frontend  │──────────────▶│  FastAPI Backend │────────────────────▶│
│  │  (Vite, port 5173)│              │  (port 8000)     │                     │
│  │                  │              │                  │  ┌──────────────────┐│
│  │  Login Screen    │              │  JWT Auth        │  │ LangGraph Worker ││
│  │  Workflow Canvas │              │  RBAC (OPA)      │  │  (port 8001)     ││
│  │  Execution Results│             │  Audit Log       │  │                  ││
│  │  Audit Log (admin)│             │  Workflow Trigger│  │  Retrieval Agent ││
│  └─────────────────┘              └────────┬─────────┘  │  (ChromaDB +     ││
│                                            │             │   nomic-embed-text││
│                                   allow/deny             │                  ││
│                                            │             │  Validation Agent ││
│                                   ┌────────▼─────────┐  │  (llama3.1:8b    ││
│                                   │  OPA Policy Engine│  │   via Ollama)    ││
│                                   │  (port 8181)      │  └──────────────────┘│
│                                   │                   │                      │
│                                   │  policy.rego      │  ┌──────────────────┐│
│                                   │  developer→run    │  │  Local LLM       ││
│                                   │  admin→audit      │  │  Ollama :11434   ││
│                                   └───────────────────┘  │  ChromaDB (disk) ││
│                                                           └──────────────────┘│
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18 + Vite | SPA |
| Workflow UI | @xyflow/react (React Flow) | Drag-and-drop workflow canvas |
| HTTP client | Axios | API calls with JWT interceptor |
| Routing | react-router v7 | Client-side routing |
| Backend | FastAPI (Python 3.11) | REST API, auth, RBAC |
| Auth | JWT (HS256) via python-jose | Stateless authentication |
| Authorization | Open Policy Agent (OPA) | Policy-as-code RBAC |
| Password hashing | bcrypt | Secure credential storage |
| AI Orchestration | LangGraph | Stateful multi-agent graph |
| Embeddings | nomic-embed-text via Ollama | Document vectorisation |
| LLM | llama3.1:8b via Ollama | Compliance verdict generation |
| Vector Store | ChromaDB (local disk) | Semantic document retrieval |
| Audit | JSON Lines file (portalocker) | Tamper-evident audit log |
| Containerisation | Docker + docker-compose | Local dev orchestration |

---

## Project Structure

```
sovereign-ai-platform/
├── backend/                    FastAPI backend
│   ├── app/
│   │   ├── auth.py             User authentication + JWT creation
│   │   ├── config.py           Settings loaded from .env
│   │   ├── dependencies.py     JWT decode dependency (get_current_user)
│   │   ├── opa.py              OPA policy check client
│   │   ├── rbac.py             require_role() FastAPI dependency
│   │   ├── audit.py            Audit log writer + reader (thread-safe)
│   │   └── routes/
│   │       ├── auth.py         POST /auth/login
│   │       ├── health.py       GET /health
│   │       ├── workflow.py     POST /workflow/trigger
│   │       └── audit.py        GET /audit/logs
│   ├── Dockerfile              Multi-stage, non-root user
│   ├── main.py                 FastAPI app + CORS + router registration
│   └── requirements.txt
│
├── langgraph-worker/           AI agent worker
│   ├── app/
│   │   ├── config.py           OLLAMA_URL, model names, ChromaDB path
│   │   ├── state.py            WorkflowState TypedDict
│   │   ├── vectorstore.py      ChromaDB client + retrieve_chunks()
│   │   ├── nodes.py            retriever_node + validator_node
│   │   └── graph.py            LangGraph StateGraph (compiled singleton)
│   ├── Dockerfile              Multi-stage, non-root user
│   ├── main.py                 FastAPI app — POST /run
│   └── requirements.txt
│
├── frontend/                   React SPA
│   └── src/
│       ├── api/
│       │   ├── auth.js         login(), logout(), getToken(), getStoredUser()
│       │   └── workflow.js     triggerWorkflow(), getAuditLogs()
│       ├── components/
│       │   ├── Header.jsx      Nav bar with role badge + admin nav links
│       │   ├── ProtectedRoute.jsx  Redirects unauthenticated users
│       │   └── WorkflowNode.jsx    Custom React Flow node component
│       ├── pages/
│       │   ├── Login.jsx       Username + password login
│       │   ├── WorkflowCanvas.jsx  Drag-and-drop workflow builder
│       │   ├── ExecutionResults.jsx  Verdict + evidence panel
│       │   └── AuditLog.jsx    Admin-only paginated audit log
│       └── App.jsx             AuthContext + BrowserRouter + routes
│
├── opa/
│   └── policy.rego             OPA policy (developer/admin rules)
│
├── scripts/
│   └── ingest.py               Ingests knowledge-base docs into ChromaDB
│
├── docs/
│   └── knowledge-base/         Source documents for RAG (committed)
│       (*.md files are local-only — excluded by .gitignore)
│
├── k8s/                        Kubernetes manifests (Phase 5 — in progress)
├── docker-compose.yml          Full-stack local orchestration
├── .env.example                Environment variable template
├── .coderabbit.yaml            CodeRabbit AI PR review config
└── .gitignore
```

---

## Features Implemented

### Phase 1 — Project Setup
- Repo structure, `.gitignore`, `.coderabbit.yaml` (auto-review on every PR), `docker-compose.yml`

### Phase 2 — Backend Security
- **JWT authentication** — `POST /auth/login` issues HS256 JWT containing `sub` and `role`
- **OPA policy enforcement** — every protected endpoint calls OPA before processing
- **bcrypt password hashing** — passwords hashed at startup, never stored in plaintext
- **Role-based access** — developers can `run_agent`, admins can `run_agent` + `view_audit` + `manage_policy`
- **Tamper-evident audit log** — every auth and workflow event written to `audit_log.jsonl` with OS-level file lock
- **Timing-safe auth** — constant-time bcrypt check prevents username enumeration
- **Fail-closed OPA** — if OPA is unreachable the backend returns 503, never 200

### Phase 3 — LangGraph RAG Pipeline
- **Retrieval Agent** — embeds user query via `nomic-embed-text`, fetches top-K chunks from ChromaDB
- **Validation Agent** — builds a structured prompt from retrieved context + uploaded contract, calls `llama3.1:8b`, parses `VERDICT / CONFIDENCE / REASONING`
- **LangGraph StateGraph** — linear pipeline: `retriever_node → validator_node → END`
- **ChromaDB persistence** — vector store survives restarts at `./chroma_db/`
- **File content truncation** — documents capped at 8,000 chars before LLM prompt to prevent context overflow

### Phase 4 — React Frontend
- **Login page** — username + password; role determined server-side from JWT
- **Workflow canvas** — empty canvas, drag nodes from sidebar to build workflow, connect nodes with edges, delete dropped nodes
- **Execution Results** — verdict badge (COMPLIANT / NON-COMPLIANT / UNCERTAIN), confidence %, full LLM answer, collapsible evidence chunks
- **Audit Log page** — admin-only, paginated (50/page), all 8 audit fields
- **Role-aware header** — admin sees Workflow + Audit Log nav tabs; developer sees workflow only
- **AdminRoute guard** — non-admins navigating to `/audit` are redirected to `/`
- **JWT decode** — base64url-safe decode, no extra library needed

---

## Security Design

| Control | Implementation |
|---|---|
| Authentication | JWT HS256, secret from environment variable, never hardcoded |
| Authorisation | OPA policy-as-code — role + action evaluated on every request |
| Password storage | bcrypt with per-user salt, hashed at startup |
| Timing attacks | Constant-time bcrypt check even when username doesn't exist |
| Audit trail | Append-only JSON Lines file, OS-level exclusive lock per write |
| Fail-closed | OPA unreachable → 503, never silently passes |
| CORS | Backend allows `localhost:5173` and `localhost:3000` only |
| Non-root containers | Dockerfiles create `appuser` (uid 1000), run as non-root |
| Prompt injection | User input inserted as labelled quoted blocks, not instructions |
| File size | Documents truncated at 8,000 chars before LLM to prevent DoS |

---

## API Reference

### Auth
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | None | Returns JWT given username + password |

### Workflow
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/workflow/trigger` | Bearer JWT (developer or admin) | Runs the LangGraph pipeline |

### Audit
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/audit/logs?limit=50&offset=0` | Bearer JWT (admin only) | Returns paginated audit entries |

### Health
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Liveness check — returns `{status: "ok"}` |

### OPA Policy Rules
```rego
developer  → run_agent
admin      → run_agent, manage_policy, view_audit
```

---

## Demo Users

| Username | Password | Role | What they can do |
|---|---|---|---|
| alice | password123 | developer | Login, build workflow, run compliance analysis |
| bob | password123 | admin | Everything alice can + view full audit log |

Passwords are loaded from `.env` — see `.env.example`.

---

## Running Locally

Start the 4 services in order — OPA, LangGraph worker, FastAPI backend, React frontend:

```powershell
# Terminal 1 — OPA
docker run -d --name opa -p 8181:8181 openpolicyagent/opa:0.70.0-static run --server
$policy = Get-Content "opa\policy.rego" -Raw
Invoke-RestMethod -Uri "http://localhost:8181/v1/policies/sovereign" -Method PUT -ContentType "text/plain" -Body $policy

# Terminal 2 — LangGraph worker
cd langgraph-worker ; python -m uvicorn main:app --port 8001 --reload

# Terminal 3 — FastAPI backend
cd backend ; python -m uvicorn main:app --port 8000 --reload

# Terminal 4 — React frontend
cd frontend ; npm run dev
```

Open http://localhost:5173

---

## Running with Docker Compose

```bash
docker compose up --build
```

Frontend served at http://localhost:3000 (nginx).  
Requires Ollama running on the host at port 11434.

---

## Testing the API Without the UI

All endpoints can be tested directly from PowerShell while the backend is running on port 8000.

### Step 1 — Get a token

As developer (alice):

    $response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"alice","password":"password123"}'
    $token = $response.access_token

As admin (bob):

    $adminResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"bob","password":"password123"}'
    $adminToken = $adminResponse.access_token

### Step 2 — Trigger a workflow with inline text

    $body = '{"query":"What are the data retention rules?","file_content":"This contract states data will be deleted after 30 days."}'
    Invoke-RestMethod -Uri "http://localhost:8000/workflow/trigger" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body $body

### Step 3 — Trigger a workflow with a file

    $fileContent = Get-Content "C:\path\to\your\contract.txt" -Raw
    $body = @{ query = "Is this GDPR compliant?"; file_content = $fileContent } | ConvertTo-Json -Depth 2
    Invoke-RestMethod -Uri "http://localhost:8000/workflow/trigger" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body $body

### Step 4 — View audit logs (admin only)

    Invoke-RestMethod -Uri "http://localhost:8000/audit/logs?limit=5" -Method GET -Headers @{Authorization="Bearer $adminToken"}

### Step 5 — Health check (no auth needed)

    Invoke-RestMethod -Uri "http://localhost:8000/health"

Expected responses:

- `/auth/login` returns `{ access_token, token_type }`
- `/workflow/trigger` returns `{ workflow_id, status, result: { verdict, confidence, answer, evidence_chunks } }`
- `/audit/logs` returns `{ total, limit, offset, items: [...] }`
- `/health` returns `{ status: "ok" }`

---

## Knowledge Base

The knowledge base lives in `docs/knowledge-base/` and is ingested into ChromaDB via:

```powershell
python scripts\ingest.py
```

This embeds the documents using `nomic-embed-text` and stores them in `./chroma_db/`. The vector store persists between restarts. When a user runs a workflow, the Retrieval Agent searches this store to ground the LLM's verdict in real regulatory text.

Users can also upload their own documents directly in the Input Node on the workflow canvas — the uploaded content is passed as context alongside the retrieved chunks.

---

## Phases Completed

| Phase | Status | Description |
|---|---|---|
| 1 — Scaffolding | ✅ Complete | Repo structure, Docker, CI config |
| 2 — Backend Security | ✅ Complete | FastAPI, JWT, OPA, audit log |
| 3 — LangGraph RAG | ✅ Complete | ChromaDB, Ollama, compliance pipeline |
| 4 — React Frontend | ✅ Complete | Workflow canvas, results, audit log UI |
| 5 — Kubernetes | 🔧 In Progress | Dockerfiles done; k8s manifests pending |

---

## Known Limitations (Assessment Scope)

- Demo users are hardcoded in `backend/app/auth.py` — a production system would use a proper identity provider
- JWT stored in `localStorage` — acceptable for an internal demo; production would use HttpOnly cookies
- Document ingestion supports `.txt`, `.md`, `.pdf` — large PDFs are truncated at 8,000 characters for the LLM prompt
- ChromaDB on local disk — production would use a managed vector database
- No HTTPS/TLS — production would terminate TLS at an ingress controller
