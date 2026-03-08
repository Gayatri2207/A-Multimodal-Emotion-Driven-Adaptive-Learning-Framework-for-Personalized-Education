"""
Full System Validation - Tests all phases automatically.
"""
import sys
import asyncio
import requests
import json
import time

BASE = "http://127.0.0.1:8000"

PASS = []
FAIL = []

def check(name, condition, detail=""):
    if condition:
        print(f"  [PASS] {name}")
        PASS.append(name)
    else:
        print(f"  [FAIL] {name} {detail}")
        FAIL.append(name)

def separator(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

# ─────────────────────────────────────────────────
# PHASE 1 – PYTHON ENV
# ─────────────────────────────────────────────────
separator("PHASE 2 — Python Environment")
check("Python 3.10+", sys.version_info >= (3, 10), f"Got {sys.version}")

required_libs = ["fastapi", "sqlalchemy", "jose", "pydantic", "websockets"]
for lib in required_libs:
    try:
        __import__(lib.replace("-", "_"))
        check(f"Import: {lib}", True)
    except ImportError as e:
        check(f"Import: {lib}", False, str(e))

# ─────────────────────────────────────────────────
# PHASE 4 – BACKEND HEALTH & OPENAPI
# ─────────────────────────────────────────────────
separator("PHASE 4 — Backend Server Validation")
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    check("/health responds", r.status_code == 200)
    check("Status is healthy", r.json().get("status") == "healthy")
except Exception as e:
    check("/health responds", False, str(e))

try:
    r = requests.get(f"{BASE}/openapi.json", timeout=5)
    spec = r.json()
    reg_body = spec["paths"]["/auth/register"]["post"].get("requestBody")
    login_body = spec["paths"]["/auth/login"]["post"].get("requestBody")
    check("OpenAPI: /auth/register has requestBody", bool(reg_body))
    check("OpenAPI: /auth/login has requestBody",    bool(login_body))
except Exception as e:
    check("OpenAPI schema valid", False, str(e))

# ─────────────────────────────────────────────────
# PHASE 5 – AUTH FLOW
# ─────────────────────────────────────────────────
separator("PHASE 5 — Authentication Flow")
email = f"valtest_{int(time.time())}@example.com"
password = "password123"
token = None

try:
    r = requests.post(f"{BASE}/auth/register", json={"email": email, "password": password})
    check("Register returns 200/201", r.status_code in (200, 201), r.text[:80])
except Exception as e:
    check("Register returns 200/201", False, str(e))

try:
    r = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password})
    check("Login returns 200", r.status_code == 200, r.text[:80])
    token = r.json().get("access_token")
    check("JWT token present",  bool(token))
except Exception as e:
    check("Login returns 200", False, str(e))

# ─────────────────────────────────────────────────
# PHASE 6 – DATABASE (initial logs)
# ─────────────────────────────────────────────────
separator("PHASE 6 — Database Validation")
try:
    r = requests.get(f"{BASE}/analytics/summary")
    data = r.json()
    check("Analytics endpoint responds", r.status_code == 200)
    check("total_logs is integer", isinstance(data.get("total_logs"), int))
    initial_logs = data.get("total_logs", 0)
except Exception as e:
    check("Analytics endpoint responds", False, str(e))
    initial_logs = 0

# ─────────────────────────────────────────────────
# PHASE 7 – WEBSOCKET PIPELINE
# ─────────────────────────────────────────────────
separator("PHASE 7 — WebSocket Pipeline")

async def ws_test():
    try:
        import websockets
        async with websockets.connect("ws://127.0.0.1:8000/ws/emotion") as ws:
            payload = {"emotion_score": 0.6, "performance_score": 0.7}
            await ws.send(json.dumps(payload))
            resp = json.loads(await ws.recv())
            check("WS connects and responds", True)
            check("WS returns adaptive_action", "adaptive_action" in resp, str(resp))
            check("WS returns emotion_score",   "emotion_score" in resp)
            return True
    except Exception as e:
        check("WebSocket connection", False, str(e))
        return False

asyncio.run(ws_test())

# ─────────────────────────────────────────────────
# PHASE 8 – RL ENGINE (indirectly via WS response)
# ─────────────────────────────────────────────────
separator("PHASE 8 — RL Engine")
# Already validated via WS; confirm action is in expected set
VALID_ACTIONS = {"relax", "hint", "challenge", "practice"}
async def rl_test():
    try:
        import websockets
        async with websockets.connect("ws://127.0.0.1:8000/ws/emotion") as ws:
            await ws.send(json.dumps({"emotion_score": 0.2, "performance_score": 0.2}))
            resp = json.loads(await ws.recv())
            action = resp.get("adaptive_action", "")
            check(f"RL action is valid ({action})", action in VALID_ACTIONS)
    except Exception as e:
        check("RL engine via WS", False, str(e))
asyncio.run(rl_test())

# ─────────────────────────────────────────────────
# PHASE 10 – ANALYTICS UPDATE AFTER WRITE
# ─────────────────────────────────────────────────
separator("PHASE 10 — Analytics Update After Event")
time.sleep(1)
try:
    r = requests.get(f"{BASE}/analytics/summary")
    final = r.json()
    new_logs = final.get("total_logs", 0)
    check("EmotionLog persisted (count increased)", new_logs > initial_logs,
          f"Was {initial_logs}, now {new_logs}")
    check("average_emotion in range", 0.0 <= final.get("average_emotion", -1) <= 1.0)
    check("engagement_score present", "engagement_score" in final)
except Exception as e:
    check("Analytics update", False, str(e))

# ─────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"  RESULTS:  {len(PASS)} PASSED  |  {len(FAIL)} FAILED")
print('='*50)
if FAIL:
    print("\nFailed checks:")
    for f in FAIL:
        print(f"  - {f}")
else:
    print("\n  SYSTEM READY FOR DEMO")
