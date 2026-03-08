import asyncio
import json
import websockets
import requests
import time

API_BASE = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/emotion"

async def test_full_flow():
    test_user_email = f"fulltest_{int(time.time())}@example.com"
    test_password = "password123"
    
    print("\n--- 1. Register and Login ---")
    res = requests.post(f"{API_BASE}/auth/register", json={"email": test_user_email, "password": test_password})
    print(f"Register status: {res.status_code}")
    
    res = requests.post(f"{API_BASE}/auth/login", json={"email": test_user_email, "password": test_password})
    print(f"Login status: {res.status_code}")
    token = res.json().get("access_token")
    if not token:
        print("Login failed, no token")
        return
    print("✓ Successfully received JWT token")

    print("\n--- 2. Fetch Initial Analytics ---")
    res = requests.get(f"{API_BASE}/analytics/summary")
    initial_analytics = res.json()
    print(f"Initial Analytics: {initial_analytics}")

    print("\n--- 3. Test WebSocket & RL Adaptation ---")
    try:
        async with websockets.connect(WS_URL) as ws:
            print("✓ WebSocket connected")
            
            # Send mock emotion data
            test_data = {
                "facial_score": 0.3,
                "speech_score": 0.4,
                "typing_score": 0.2,
                "emotion_score": 0.3,
                "performance_score": 0.2
            }
            print(f"Sending data: {test_data}")
            await ws.send(json.dumps(test_data))
            
            response = await ws.recv()
            resp_data = json.loads(response)
            print(f"Received adaptive response: {resp_data}")
            
            action = resp_data.get("adaptive_action")
            if action:
                print(f"✓ RL Adaptive Action returned: {action}")
            else:
                print("✗ RL Adaptive Action missing")
                
    except Exception as e:
        print(f"WebSocket test failed: {e}")

    # Wait a moment for DB commit
    await asyncio.sleep(1)

    print("\n--- 4. Verify Emotion Logging & Analytics Update ---")
    res = requests.get(f"{API_BASE}/analytics/summary")
    final_analytics = res.json()
    print(f"Final Analytics: {final_analytics}")
    
    if final_analytics.get("total_logs", 0) > initial_analytics.get("total_logs", 0):
        print("✓ Database write succeeded and analytics updated properly!")
    else:
        print("✗ Analytics 'total_logs' did not increment. Check DB write.")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
