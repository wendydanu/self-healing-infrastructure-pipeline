import os
import json
import re
import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Depends, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from database import engine, Base, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
import models
from config import settings

# --- DEVDAY 6 ARCHITECTURAL IMPORTS ---
from agents import run_multi_agent_healing
from websocket_manager import manager

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "Not Found!":
    raise ValueError("[CRITICAL ERROR] GEMINI_API_KEY not found on .env file!")

app = FastAPI(
    title="S.H.I.P Core",
    description="Autonomous Self-Healing Infrastructure Pipeline - Log Listener & Patching Engine",
    version="1.0.0"
)

# Scaffolding templates directory for rendering the visual frontend
templates = Jinja2Templates(directory="templates")

# --- ENTERPRISE SECURITY STARTUP AUDIT ---
@app.on_event("startup")
async def run_security_audit():
    print("\n[SECURITY AUDIT] Launching Enterprise Dependency Vulnerability Scanner...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[SECURITY AUDIT] SUCCESS: No known vulnerabilities found in dependencies. System secure.\n")
        else:
            print("[SECURITY AUDIT] WARNING: Vulnerabilities detected in third-party packages!")
            print(result.stdout)
            print(result.stderr)
            
    except Exception as e:
        print(f"[SECURITY AUDIT] FAILED: Could not execute vulnerability scanner: {str(e)}\n")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- AUTHENTICATION GATEWAY ---
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

# --- ROUTE 1: UI DASHBOARD RENDERER ---
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Renders the main enterprise pipeline telemetry cockpit UI."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# --- ROUTE 2: WEBSOCKET TELEMETRY CHANNEL ---
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    """Establishes a persistent bi-directional telemetry stream pipeline to the UI."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive by listening to implicit client heartbeat sweeps
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- ROUTE 3: INTERCEPT LOGGER & MULTI-AGENT FLOW ---
@app.post("/api/v1/intercept-log", status_code=status.HTTP_200_OK)
async def intercept_and_heal(payload: ErrorLogPayload, db: AsyncSession = Depends(get_db)):
    # BROADCAST TELEMETRY: Ingestion Event (Alert the frontend immediately)
    await manager.broadcast({
        "event": "INCIDENT_INTERCEPTED",
        "incident_id": "PENDING",
        "error_log": payload.error_log[:150] + "..."
    })

    try:
        # Trigger Multi-Agent Orchestration Chain (RCA + Patching Agents) via agents.py
        diagnosis, raw_patch_code = run_multi_agent_healing(payload.error_log, payload.broken_code)
        
        # BROADCAST TELEMETRY: Reasoning Pipeline Complete
        await manager.broadcast({
            "event": "PATCH_COMPILED",
            "diagnosis": diagnosis
        })

        clean_python_code = sanitize_patch_code(raw_patch_code)
        patch_lines = clean_python_code.splitlines()
        
    except Exception as ai_err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ai_err))
    
    try:
        new_incident = models.IncidentLog(
            error_log=payload.error_log,
            broken_code=payload.broken_code,
            error_analysis=diagnosis,
            suggested_patch=clean_python_code
        )
        db.add(new_incident)
        await db.commit()
        await db.refresh(new_incident)
        
    except SQLAlchemyError as db_err:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(db_err))
        
    return {
        "incident_id": new_incident.id,
        "telemetry_captured": True,
        "engine_status": "PATCH_GENERATED_AND_STORED",
        "error_analysis": diagnosis,
        "suggested_patch_clean": patch_lines
    }

# --- ROUTE 4: SECURED SANDBOX DEPLOYMENT ---
@app.post("/api/v1/deploy-patch/{incident_id}", status_code=status.HTTP_200_OK)
async def deploy_patch(
    incident_id: int, 
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_ship_token)
):
    try:
        result = await db.execute(select(models.IncidentLog).where(models.IncidentLog.id == incident_id))
        incident = result.scalars().first()
        
        if not incident:
            raise HTTPException(
                status_code=404, 
                detail=f"Incident ID {incident_id} not found in the repository database."
            )
        
        clean_patch_code = incident.suggested_patch
        sandbox_base = settings.safe_sandbox_dir
        target_file_name = "server_math.py"
        
        target_path = Path(sandbox_base / target_file_name).resolve()
        
        # Sandbox Isolation Enforcement Layer (DevDay 5 Guard)
        if not str(target_path).startswith(str(sandbox_base)):
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

        # BROADCAST TELEMETRY: Successful Deploy Event Transmission
        await manager.broadcast({
            "event": "DEPLOY_SUCCESS",
            "secured_path": str(target_path)
        })
            
        return {
            "deployment_status": "SUCCESS",
            "incident_id": incident_id,
            "secured_path": str(target_path),
            "message": f"Hotfix for Incident #{incident_id} has been deployed safely within Enterprise Sandbox boundaries."
        }
        
    except HTTPException as http_err:
        raise http_err
    except SQLAlchemyError as db_err:
        raise HTTPException(
            status_code=500, 
            detail=f"Database transaction failure: {str(db_err)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Deployment automation pipeline failed: {str(e)}"
        )