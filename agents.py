import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.gemini_api_key)

rca_agent = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "You are an expert Reliability Engineer specializing in Root Cause Analysis (RCA). "
        "Your sole task is to analyze raw server stack traces and broken source code. "
        "Identify the exact file name, line number, and structural logical flaw. "
        "Provide a concise, technical diagnosis summary. Do NOT generate any code patches."
    )
)

patching_agent = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "You are an autonomous Secure Software Patching compiler. "
        "You will receive a Root Cause Analysis (RCA) diagnosis alongside the broken source code. "
        "Your task is to generate a precise, optimized Python code patch that fixes the bug. "
        "You MUST only return the clean executable Python code wrapped inside a single standard markdown code block: ```python ... ```. "
        "Do not include any introductory remarks, explanations, or prose outside the code block."
    )
)

def run_multi_agent_healing(error_log: str, broken_code: str) -> tuple[str, str]:
    """Orchestrator untuk menjalankan rantai kolaborasi Multi-Agent."""
    rca_prompt = f"Analyze this incident:\n\n[STACK TRACE]\n{error_log}\n\n[BROKEN CODE]\n{broken_code}"
    rca_response = rca_agent.generate_content(rca_prompt)
    diagnosis = rca_response.text

    patching_prompt = f"RCA Diagnosis:\n{diagnosis}\n\nOriginal Code:\n{broken_code}\n\nGenerate the patch now."
    patch_response = patching_agent.generate_content(patching_prompt)
    raw_patch_code = patch_response.text

    return diagnosis, raw_patch_code