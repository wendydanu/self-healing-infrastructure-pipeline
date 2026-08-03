import os
import json
import re
import uuid
import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Depends, Header, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from database import engine, Base, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
import models
from config import settings
from agents import run_multi_agent_healing
from websocket_manager import manager
from logger import logger
from prometheus_fastapi_instrumentator import Instrumentator

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "Not Found!":
    raise ValueError("[CRITICAL ERROR] GEMINI_API_KEY not found on .env file!")

app = FastAPI(
    title="S.H.I.P Core",
    description="Autonomous Self-Healing Infrastructure Pipeline - Distributed Observability Cluster",
    version="1.1.0"
)

templates = Jinja2Templates(directory="templates")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.middleware("http")
async def distributed_tracing_middleware(request: Request, call_next):
    """Injects or propagates a unique Trace ID across microservice request headers."""
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    
    logger.info("incoming_http_request", path=request.url.path, method=request.method, trace_id=trace_id)
    
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response

@app.on_event("startup")
async def run_security_audit():
    logger.info("security_audit_launching", detail="Launching Enterprise Dependency Vulnerability Scanner...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("security_audit_success", detail="No known vulnerabilities found in dependencies. System secure.")
        else:
            logger.warning("security_audit_vulnerability_detected", stdout=result.stdout, stderr=result.stderr)
            
    except Exception as e:
        logger.error("security_audit_failed", error=str(e))

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def verify_ship_token(x_ship_token: str = Header(..., description="Secure Admin Token for S.H.I.P Validation")):
    if x_ship_token != settings.ship_admin_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Invalid S.H.I.P Security Token Compliance."
        )
    return x_ship_token

class ErrorLogPayload(BaseModel):
    error_log: str = Field(..., description="Raw error log from server")
    broken_code: str = Field(..., description="Suspected broken backend code")

def sanitize_patch_code(raw_code: str) -> str:
    clean_code = re.sub(r'^```python\s*|^```\s*', '', raw_code, flags=re.MULTILINE)
    clean_code = re.sub(r'```\s*$', '', clean_code, flags=re.MULTILINE)
    return clean_code.strip()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Renders the main enterprise pipeline telemetry cockpit UI."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    """Establishes a persistent bi-directional telemetry stream pipeline to the UI."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/v1/intercept-log", status_code=status.HTTP_200_OK)
async def intercept_and_heal(request: Request, payload: ErrorLogPayload, db: AsyncSession = Depends(get_db)):
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    
    logger.info("incident_intercepted", trace_id=trace_id, error_snippet=payload.error_log[:100])

    await manager.broadcast({
        "event": "INCIDENT_INTERCEPTED",
        "incident_id": "PENDING",
        "trace_id": trace_id,
        "error_log": payload.error_log[:150] + "..."
    })

    try:
        diagnosis, raw_patch_code = run_multi_agent_healing(payload.error_log, payload.broken_code, trace_id=trace_id)
        
        await manager.broadcast({
            "event": "PATCH_COMPILED",
            "trace_id": trace_id,
            "diagnosis": diagnosis
        })

        clean_python_code = sanitize_patch_code(raw_patch_code)
        patch_lines = clean_python_code.splitlines()
        
    except Exception as ai_err:
        logger.error("multi_agent_healing_failed", trace_id=trace_id, error=str(ai_err))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ai_err))
    
    try:
        new_incident = models.IncidentLog(
            error_log=payload.error_log,
            broken_code=payload.broken_code,
            error_analysis=f"[TRACE ID: {trace_id}]\n{diagnosis}",
            suggested_patch=clean_python_code
        )
        db.add(new_incident)
        await db.commit()
        await db.refresh(new_incident)
        
        logger.info("incident_stored", incident_id=new_incident.id, trace_id=trace_id)
        
    except SQLAlchemyError as db_err:
        await db.rollback()
        logger.error("database_commit_failed", trace_id=trace_id, error=str(db_err))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(db_err))
        
    return {
        "incident_id": new_incident.id,
        "trace_id": trace_id,
        "telemetry_captured": True,
        "engine_status": "PATCH_GENERATED_AND_STORED",
        "error_analysis": diagnosis,
        "suggested_patch_clean": patch_lines
    }

@app.post("/api/v1/deploy-patch/{incident_id}", status_code=status.HTTP_200_OK)
async def deploy_patch(
    request: Request,
    incident_id: int, 
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_ship_token)
):
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    
    try:
        result = await db.execute(select(models.IncidentLog).where(models.IncidentLog.id == incident_id))
        incident = result.scalars().first()
        
        if not incident:
            logger.warning("deploy_patch_not_found", incident_id=incident_id, trace_id=trace_id)
            raise HTTPException(
                status_code=404, 
                detail=f"Incident ID {incident_id} not found in the repository database."
            )
        
        clean_patch_code = incident.suggested_patch
        sandbox_base = settings.safe_sandbox_dir
        target_file_name = "server_math.py"
        
        target_path = Path(sandbox_base / target_file_name).resolve()
        
        if not str(target_path).startswith(str(sandbox_base)):
            logger.error("sandbox_boundary_breach_attempt", incident_id=incident_id, trace_id=trace_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Breach Detected: Path traversal attempt blocked by Sandbox Jail Guard!"
            )
            
        if not target_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Target file '{target_file_name}' not found within the production sandbox environment."
            )

        with open(target_path, "w", encoding="utf-8") as file:
            file.write(clean_patch_code)

        logger.info("patch_deployed_successfully", incident_id=incident_id, trace_id=trace_id, path=str(target_path))

        await manager.broadcast({
            "event": "DEPLOY_SUCCESS",
            "trace_id": trace_id,
            "secured_path": str(target_path)
        })
            
        return {
            "deployment_status": "SUCCESS",
            "incident_id": incident_id,
            "trace_id": trace_id,
            "secured_path": str(target_path),
            "message": f"Hotfix for Incident #{incident_id} has been deployed safely within Enterprise Sandbox boundaries."
        }
        
    except HTTPException as http_err:
        raise http_err
    except SQLAlchemyError as db_err:
        raise HTTPException(status_code=500, detail=f"Database transaction failure: {str(db_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment automation pipeline failed: {str(e)}")