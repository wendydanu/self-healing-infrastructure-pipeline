import os
import json
import re
from fastapi import FastAPI, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
from database import engine, Base, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
import models
from pathlib import Path
from config import settings

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "Not Found!":
    raise ValueError("[CRITICAL ERROR] GEMINI_API_KEY tidak ditemukan di file .env")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI(
    title="S.H.I.P Core",
    description="Autonomous Self-Healing Infrastructure Pipeline - Log Listener & Patching Engine",
    version="1.0.0"
)

import subprocess
import sys

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

def verify_ship_token(x_ship_token: str = Header(..., description="Secure Admin Token for S.H.I.P Validation")):
    if x_ship_token != settings.ship_admin_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Invalid S.H.I.P Security Token Compliance."
        )
    return x_ship_token

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class ErrorLogPayload(BaseModel):
    error_log: str = Field(..., description="Raw error log from server")
    broken_code: str = Field(..., description="Suspected broken backend code")

def sanitize_patch_code(raw_code: str) -> str:
    clean_code = re.sub(r'^```python\s*|^```\s*', '', raw_code, flags=re.MULTILINE)
    clean_code = re.sub(r'```\s*$', '', clean_code, flags=re.MULTILINE)
    return clean_code.strip()

@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "active", "pipeline": "Self-Healing Infrastructure Engine"}

@app.post("/api/v1/intercept-log", status_code=status.HTTP_200_OK)
async def intercept_and_heal(payload: ErrorLogPayload, db: AsyncSession = Depends(get_db)):
    try:
        system_prompt = f"""
        You are an autonomous DevOps and Core Systems Engineering Robot.
        Review the incoming server error log and identify the bug in the provided broken code.
        
        You MUST respond strictly in JSON format with the following keys:
        1. "analysis": A short, highly technical explanation of why the crash happened. Do not use conversational filler.
        2. "patch": The corrected, production-ready full Python code block. Do not include markdown wraps inside the JSON value.
        
        [INCOMING SERVER ERROR LOG]:
        {payload.error_log}
        
        [BROKEN SOURCE CODE]:
        {payload.broken_code}
        """
        
        response = gemini_model.generate_content(
            system_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        ai_data = json.loads(response.text)
        analysis_text = ai_data.get("analysis", "")
        patch_code_raw = ai_data.get("patch", "")
        
        clean_python_code = sanitize_patch_code(patch_code_raw)
        patch_lines = clean_python_code.splitlines()
        
    except Exception as ai_err:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ai_err))
    
    try:
        new_incident = models.IncidentLog(
            error_log=payload.error_log,
            broken_code=payload.broken_code,
            error_analysis=analysis_text,
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
        "error_analysis": analysis_text,
        "suggested_patch_clean": patch_lines
    }

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