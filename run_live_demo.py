import importlib
import os
import shutil
import traceback

import requests
from dotenv import load_dotenv

load_dotenv()

SHIP_INTERCEPT_URL = "http://127.0.0.1:8000/api/v1/intercept-log"
SHIP_DEPLOY_URL = "http://127.0.0.1:8000/api/v1/deploy-patch"
ADMIN_TOKEN = os.getenv("SHIP_ADMIN_TOKEN")
TRACE_ID = "TRACE-LINKEDIN-LIVE-DEMO-2026"
TARGET_FILE = "payment_gateway.py"
REQUEST_TIMEOUT = 120  # two sequential Gemini calls can be slow

if not ADMIN_TOKEN:
    raise SystemExit("SHIP_ADMIN_TOKEN not found in .env")


def dispatch_and_heal(error_stacktrace: str, broken_code: str) -> None:
    print("=" * 70)
    print("2. DISPATCHING TELEMETRY TO S.H.I.P ENGINE")
    print("=" * 70)

    headers = {
        "Content-Type": "application/json",
        "X-Trace-ID": TRACE_ID,
        "X-Ship-Token": ADMIN_TOKEN,
    }
    payload = {
        "error_log": error_stacktrace,
        "broken_code": broken_code,
        "target_file": TARGET_FILE,
    }

    try:
        response = requests.post(
            SHIP_INTERCEPT_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as exc:
        print("[INTERCEPT FAILED] Could not reach the S.H.I.P server:", exc)
        return

    if response.status_code != 200:
        print("[INTERCEPT FAILED]", response.status_code, response.text)
        return

    data = response.json()
    incident_id = data["incident_id"]
    print(f"[INTERCEPT SUCCESS] Incident ID: #{incident_id} | Trace ID: {TRACE_ID}")
    print("\n[AGENT 1 - RCA DIAGNOSIS]:")
    print(data["error_analysis"])

    print("\n" + "=" * 70)
    print(f"3. DEPLOYING AUTOMATED HOTFIX FOR INCIDENT #{incident_id}")
    print("=" * 70)

    deploy_headers = {"X-Ship-Token": ADMIN_TOKEN, "X-Trace-ID": TRACE_ID}
    try:
        deploy_res = requests.post(
            f"{SHIP_DEPLOY_URL}/{incident_id}",
            headers=deploy_headers,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        print("[DEPLOYMENT FAILED] Could not reach the S.H.I.P server:", exc)
        return

    if deploy_res.status_code == 200:
        print("[HOTFIX APPLIED SUCCESSFULLY!]")
        print(deploy_res.json()["message"])
        print(f"\nCheck '{TARGET_FILE}' now to see the self-healed code!")
    else:
        print("[DEPLOYMENT FAILED]", deploy_res.status_code, deploy_res.text)


def execute_demo() -> None:
    # Reset: restore the broken module so the demo can be repeated
    shutil.copyfile("payment_gateway.broken.py", TARGET_FILE)
    importlib.invalidate_caches()
    payment_gateway = importlib.import_module("payment_gateway")

    print("=" * 70)
    print(f"1. RUNNING TARGET MODULE: {TARGET_FILE}")
    print("=" * 70)

    try:
        payment_gateway.process_checkout(cart_items=[], discount_code="INVALID_CODE")
    except Exception:
        error_stacktrace = traceback.format_exc()
        print("\n[CRASH DETECTED IN PRODUCTION MODULE!]")
        print(error_stacktrace)

        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            broken_code = f.read()

        dispatch_and_heal(error_stacktrace, broken_code)
    else:
        print("\n[NO CRASH] The module ran without error. Check payment_gateway.broken.py.")


if __name__ == "__main__":
    execute_demo()