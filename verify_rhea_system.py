import requests
import json

BASE_URL = "http://localhost:8081"

def test_chat(prompt):
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": "gemini-3-flash-preview"
    }
    
    print(f"\n--- Testing Prompt: '{prompt}' ---")
    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"Rhea's Response:\n{content}")
            return content
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test Persona
    test_chat("Who are you?")
    
    # Test Skill triggering (Search)
    test_chat("Search the web for the latest news about Flutter 4.0")
    
    # Test Skill triggering (Notion)
    test_chat("What is in our lore memory about Project Rhea?")
