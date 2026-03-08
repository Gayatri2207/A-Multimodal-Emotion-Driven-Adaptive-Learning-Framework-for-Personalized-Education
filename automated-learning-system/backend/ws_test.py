import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1:8000/ws/emotion"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            payload = {
                "facial_score": 0.6,
                "speech_score": 0.5,
                "typing_score": 0.7,
                "performance_score": 0.8
            }
            print(f"Sending payload: {payload}")
            await websocket.send(json.dumps(payload))
            
            response = await websocket.recv()
            print(f"Received response: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
