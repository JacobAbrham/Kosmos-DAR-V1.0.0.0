import requests
import json
import uuid
import sys

# Configuration
API_URL = "http://localhost:8000/chat"
USER_ID = "test-user-local"
CONVERSATION_ID = f"test-conv-{str(uuid.uuid4())[:8]}"


def chat():
    print(f"Starting chat session (Conversation ID: {CONVERSATION_ID})")
    print("Type 'quit' to exit.")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            break

        payload = {
            "message": user_input,
            "conversation_id": CONVERSATION_ID,
            "user_id": USER_ID
        }

        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            print(f"\nKosmos: {data['response']}")

            if 'metadata' in data:
                meta = data['metadata']
                print(
                    f"\n[Metadata] Time: {meta.get('processing_time_ms')}ms | Agents: {data.get('agents_used')}")

        except requests.exceptions.ConnectionError:
            print("\nError: Could not connect to backend. Is port forwarding running?")
            print("Run: kubectl port-forward service/kosmos-backend 8000:8000")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    chat()
