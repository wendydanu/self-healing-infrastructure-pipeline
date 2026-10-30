import traceback
import requests
import importlib
import shutil

SHIP_INTERCEPT_URL = "http://127.0.0.1:8000/api/v1/intercept-log"
SHIP_DEPLOY_URL = "http://127.0.0.1:8000/api/v1/deploy-patch"
ADMIN_TOKEN = "SHIP_SECRET_COMPLEX_COMPLIANCE_TOKEN_2026"
TRACE_ID = "TRACE-LINKEDIN-LIVE-DEMO-2026"

def execute_demo():
    # Reset: restore the broken module so the demo can be repeated
    shutil.copyfile("payment_gateway.broken.py", "payment_gateway.py")
    importlib.invalidate_caches()
    payment_gateway = importlib.import_module("payment_gateway")
    print("=" * 70)
    print("1. RUNNING TARGET MODULE: payment_gateway.py")
    print("=" * 70)
    
    try:
        payment_gateway.process_checkout(cart_items=[], discount_code="INVALID_CODE")
    except Exception:
        error_stacktrace = traceback.format_exc()
        print("\n[CRASH DETECTED IN PRODUCTION MODULE!]")
        print(error_stacktrace)
        
        with open("payment_gateway.py", "r", encoding="utf-8") as f:
            broken_code = f.read()

        print("=" * 70)
        print("2. DISPATCHING TELEMETRY TO S.H.I.P ENGINE")
        print("=" * 70)
        
        headers = {"Content-Type": "application/json", "X-Trace-ID": TRACE_ID}
        payload = {
            "error_log": error_stacktrace,
            "broken_code": broken_code,
            "target_file": "payment_gateway.py"
        }
        
        response = requests.post(SHIP_INTERCEPT_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            incident_id = data["incident_id"]
            print(f"[INTERCEPT SUCCESS] Incident ID: #{incident_id} | Trace ID: {TRACE_ID}")
            print("\n[AGENT 1 - RCA DIAGNOSIS]:")
            print(data["error_analysis"])
            
            print("\n" + "=" * 70)
            print(f"3. DEPLOYING AUTOMATED HOTFIX FOR INCIDENT #{incident_id}")
            print("=" * 70)
            
            deploy_headers = {"x-ship-token": ADMIN_TOKEN, "X-Trace-ID": TRACE_ID}
            deploy_res = requests.post(f"{SHIP_DEPLOY_URL}/{incident_id}", headers=deploy_headers)
            
            if deploy_res.status_code == 200:
                print("[HOTFIX APPLIED SUCCESSFULLY!]")
                print(deploy_res.json()["message"])
                print("\nCheck 'payment_gateway.py' now to see the self-healed code!")
            else:
                print("[DEPLOYMENT FAILED]", deploy_res.text)

if __name__ == "__main__":
    execute_demo()