import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

# Load the same .env file
load_dotenv()
MURF_API_KEY = os.getenv("MURF_API_KEY")

# The URL for the Murf WebSocket API
MURF_WS_URL = f"wss://api.murf.ai/v1/speech/stream-input?api-key={MURF_API_KEY}"

async def test_murf_connection():
    """A simple test to see if we can get audio from Murf."""
    if not MURF_API_KEY:
        print("❌ ERROR: MURF_API_KEY not found in .env file.")
        return

    print("🔌 Attempting to connect to Murf...")
    try:
        async with websockets.connect(MURF_WS_URL) as websocket:
            print("✅ WebSocket connection opened successfully.")

            # 1. Send voice configuration
            voice_config = {
                "voice_config": {
                    "voiceId": "en-US-ken",
                    "style": "Conversational"
                }
            }
            await websocket.send(json.dumps(voice_config))
            print("👍 Sent voice configuration.")

            # 2. Send text to be synthesized
            text_to_speak = {"text": "Hello, this is a test.", "end": True}
            await websocket.send(json.dumps(text_to_speak))
            print(f"👍 Sent text: '{text_to_speak['text']}'")

            # 3. Wait for the audio response
            print("⏳ Waiting for audio chunks...")
            try:
                # Wait for up to 10 seconds for the first message
                response_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print("🎉 SUCCESS! Received a response from Murf:")
                print(response_message)
                
                # Check if it contains audio
                data = json.loads(response_message)
                if "audio" in data:
                    print("\n✅ The API key is working correctly!")
                else:
                    print("\n⚠️ Received a response, but it did not contain audio.")

            except asyncio.TimeoutError:
                print("\n❌ FAILED: Timed out waiting for a response from Murf.")
                print("This almost always means there is an issue with your API Key or account plan.")

    except Exception as e:
        print(f"❌ FAILED: An error occurred: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_murf_connection())


