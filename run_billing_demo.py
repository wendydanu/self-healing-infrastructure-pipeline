import importlib
import os
import shutil
import time
import traceback
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

SHIP_INTERCEPT_URL = "http://127.0.0.1:8000/api/v1/intercept-log"
SHIP_DEPLOY_URL = "http://127.0.0.1:8000/api/v1/deploy-patch"
ADMIN_TOKEN = os.getenv("SHIP_ADMIN_TOKEN")
TARGET_FILE = "billing_engine.py"
FIXTURE_FILE = "billing_engine.broken.py"
REQUEST_TIMEOUT = 120

if not ADMIN_TOKEN:
    raise SystemExit("SHIP_ADMIN_TOKEN not found in .env")


def dispatch_and_heal(trace_id: str, stack_trace: str, broken_code: str) -> None:
    headers = {
        "Content-Type": "application/json",
        "X-Trace-ID": trace_id,
        "X-Ship-Token": ADMIN_TOKEN,
    }
    payload = {
        "error_log": stack_trace,
        "broken_code": broken_code,
        "target_file": TARGET_FILE,
    }

    print("\n[STEP 1] Dispatching telemetry to S.H.I.P engine...")
    start = time.time()
    try:
        response = requests.post(
            SHIP_INTERCEPT_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as exc:
        print("[INTERCEPT FAILED] Could not reach the S.H.I.P server:", exc)
        return
    elapsed = round(time.time() - start, 2)

    if response.status_code != 200:
        print(f"[INTERCEPT FAILED] {response.status_code} - {response.text}")
        return

    data = response.json()
    incident_id = data["incident_id"]
    print(f"[TELEMETRY CAPTURED] Processed in {elapsed}s | Incident ID: #{incident_id}")

    if data.get("engine_status"):
        print(f"[ENGINE STATUS] {data['engine_status']}")

    print("\n[DIAGNOSIS]:")
    print(data.get("error_analysis", "No detailed diagnosis provided."))

    patch = data.get("suggested_patch_clean")
    if patch:
        print("\n[SUGGESTED PATCH]:")
        lines = patch if isinstance(patch, list) else str(patch).splitlines()
        for line in lines:
            print(f"  {line}")

    print("\n" + "-" * 70)
    print(f"[STEP 2] Deploying hotfix for incident #{incident_id}...")
    print("-" * 70)

    deploy_headers = {"X-Ship-Token": ADMIN_TOKEN, "X-Trace-ID": trace_id}
    try:
        deploy_res = requests.post(
            f"{SHIP_DEPLOY_URL}/{incident_id}",
            headers=deploy_headers,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        print("[DEPLOYMENT FAILED] Could not reach the S.H.I.P server:", exc)
        return

    if deploy_res.status_code != 200:
        print(f"[DEPLOYMENT FAILED] {deploy_res.status_code} - {deploy_res.text}")
        return

    result = deploy_res.json()
    print("[DEPLOYMENT SUCCESSFUL]")
    print(f"Message: {result.get('message')}")
    print(f"\nCheck '{TARGET_FILE}' now to see the self-healed code.")


def main() -> None:
    trace_id = f"TRACE-BILLING-DEMO-{uuid.uuid4().hex[:8].upper()}"

    shutil.copyfile(FIXTURE_FILE, TARGET_FILE)
    importlib.invalidate_caches()
    billing = importlib.import_module("billing_engine")

    print("=" * 70)
    print("[SIMULATED INCIDENT] Running billing_engine with an empty order")
    print(f"Trace ID: {trace_id}")
    print("=" * 70)

    try:
        billing.process_transaction_invoice({"items": []})
    except Exception:
        stack_trace = traceback.format_exc()
        print("\n[CRASH DETECTED]")
        print(stack_trace)

        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            broken_code = f.read()

        dispatch_and_heal(trace_id, stack_trace, broken_code)
    else:
        print(f"\n[NO CRASH] The module ran without error. Check {FIXTURE_FILE}.")


if __name__ == "__main__":
    main()