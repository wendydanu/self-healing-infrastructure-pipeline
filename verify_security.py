import os
import requests
from dotenv import load_dotenv

load_dotenv()
URL = "http://127.0.0.1:8000/api/v1/intercept-log"
TOKEN = os.getenv("SHIP_ADMIN_TOKEN")
if not TOKEN:
    raise SystemExit("SHIP_ADMIN_TOKEN not found in .env")

body = {"error_log": "x", "broken_code": "x", "target_file": "payment_gateway.py"}
good = {"X-Ship-Token": TOKEN}

def check(name, expected, headers, payload):
    r = requests.post(URL, headers=headers, json=payload, timeout=30)
    status = "PASS" if r.status_code == expected else "FAIL"
    print(f"{status}  {name}: got {r.status_code}, expected {expected}")

check("no token", 422, {}, body)
check("wrong token", 403, {"X-Ship-Token": "salah"}, body)
check("target app.py", 422, good, {**body, "target_file": "app.py"})
check("target ../app.py", 422, good, {**body, "target_file": "../app.py"})
check("target config.py", 422, good, {**body, "target_file": "config.py"})
check("oversized error_log", 422, good, {**body, "error_log": "A" * 20000})