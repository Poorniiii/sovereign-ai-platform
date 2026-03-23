from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health
# auth, workflow, audit routes added progressively in Phase 2

app = FastAPI(title="Sovereign AI Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
 app.add_middleware(
     CORSMiddleware,
     allow_origins=["http://localhost:3000", "http://localhost:5173"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
 )
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(health.router, tags=["Health"])
# Routers below are uncommented progressively as each Phase 2 file is created:
# app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# app.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
# app.include_router(audit.router, prefix="/audit", tags=["Audit"])