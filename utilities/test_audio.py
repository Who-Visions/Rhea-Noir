#!/usr/bin/env python3
"""Test audio recording from Chat Mix"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhea_noir.skills import get_skill

def main():
    print("🎙️ Testing Audio Recording from Chat Mix...")
    print("   Speak now! (5 seconds)")
    
    audio = get_skill("audio")
    if not audio:
        print("❌ Audio skill not available")
        return
    
    # Record and transcribe
    result = audio.execute("listen", duration=5.0, device="Chat Mix")
    
    if result.get("success"):
        print(f"✅ Transcript: {result['result']['transcript']}")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
