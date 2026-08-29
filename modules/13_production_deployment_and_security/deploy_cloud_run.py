"""
Module 13: Production Deployment on Cloud Run
FastAPI Application serving as the Agent Gateway API endpoint.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel

try:
    from fastapi import FastAPI, HTTPException, Header
    from dotenv import load_dotenv
    load_dotenv()
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

class AgentInvokeRequest(BaseModel):
    user_id: str
    prompt: str
    session_id: Optional[str] = None

class AgentInvokeResponse(BaseModel):
    session_id: str
    model: str
    response: str
    status: str

if HAS_FASTAPI:
    app = FastAPI(
        title="Google Cloud Enterprise Agent Gateway",
        description="Production Agent API deployed on Cloud Run / Agent Runtime",
        version="1.0.0"
    )

    @app.get("/healthz")
    def health_check():
        """Liveness & Readiness probe for Cloud Run."""
        return {"status": "healthy", "service": "agent-gateway", "runtime": "cloud-run"}

    @app.post("/v1/agents/invoke", response_model=AgentInvokeResponse)
    def invoke_agent(request: AgentInvokeRequest, authorization: Optional[str] = Header(None)):
        # Model Armor Security Inspection
        if "ignore all previous instructions" in request.prompt.lower():
            raise HTTPException(status_code=400, detail="Blocked by Model Armor: Prompt Injection detected.")

        return AgentInvokeResponse(
            session_id=request.session_id or "sess_default",
            model=os.getenv("GEMINI_MODEL", "gemini-3.7-flash"),
            response=f"Agent processed request: '{request.prompt}' successfully.",
            status="SUCCESS"
        )
else:
    app = None
