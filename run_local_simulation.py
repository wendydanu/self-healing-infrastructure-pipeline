import importlib
import os
import shutil
import traceback

import requests
from dotenv import load_dotenv

load_dotenv()

SHIP_API_URL = "http://127.0.0.1:8000/api/v1/intercept-log"
DEPLOY_API_URL = "http://127.0.0.1:8000/api/v1/deploy-patch"
TOKEN = os.getenv("SHIP_ADMIN_TOKEN")
TARGET_FILE = "app_target_demo.py"
FIXTURE_FILE = "app_target_demo.broken.py"
REQUEST_TIMEOUT = 120

if not TOKEN:
    raise SystemExit("SHIP_ADMIN_TOKEN not found in .env")


def dispatch_and_heal(stack_trace: str, broken_code: str) -> None:
    headers = {"X-Ship-Token": TOKEN}
    payload = {
        "error_log": stack_trace,
        "broken_code": broken_code,
        "target_file": TARGET_FILE,
    }

    print("Transmitting telemetry payload to S.H.I.P Engine...")
    try:
        response = requests.post(
            SHIP_API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as exc:
        print("[INTERCEPT FAILED] Could not reach the S.H.I.P server:", exc)
        return

    if response.status_code not in (200, 201):
        print(f"Telemetry Intercept Failed: {response.status_code} - {response.text}")
        return

    data = response.json()
    incident_id = data["incident_id"]
    rca_summary = data.get("error_analysis", "No detailed diagnosis provided.")

    print(f"[INTERCEPTED] Telemetry ingested! Incident Reference: #{incident_id}")
    print("\n[ROOT CAUSE DIAGNOSIS & BUG ANALYSIS]")
    print("-" * 60)
    print(rca_summary)
    print("-" * 60)

    print(f"\nRequesting S.H.I.P Hotfix Injector for Incident #{incident_id}...")
    try:
        deploy_res = requests.post(
            f"{DEPLOY_API_URL}/{incident_id}", headers=headers, timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException as exc:
        print("[DEPLOYMENT FAILED] Could not reach the S.H.I.P server:", exc)
        return

    if deploy_res.status_code == 200:
        print("[AUTO-HEALING SUCCESS] Hotfix patch successfully applied!")
        print(f"Check '{TARGET_FILE}' now to see the self-healed code.")
    else:
        print(f"Deployment Failed: {deploy_res.status_code} - {deploy_res.text}")


def main() -> None:
    shutil.copyfile(FIXTURE_FILE, TARGET_FILE)
    importlib.invalidate_caches()
    target = importlib.import_module("app_target_demo")

    print("[LOCAL SIMULATION] Starting Inventory Service workload...")

    try:
        target.reserve_stock(item_id="PROD-8821", current_stock=5, quantity_requested=5)
    except Exception:
        stack_trace = traceback.format_exc()
        print("[CRASH DETECTED] Intercepted runtime exception in workload execution!")
        print(stack_trace)

        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            broken_code_content = f.read()

        dispatch_and_heal(stack_trace, broken_code_content)
    else:
        print(f"[NO CRASH] The module ran without error. Check {FIXTURE_FILE}.")


if __name__ == "__main__":
    main()