from rhea_noir.skills.flutter_vibe.actions import skill
import json
import os

def main():
    path = r'C:\Users\super\Watchtower\Rhea-Noir-Ai\rhea_mobile_command\lib\main.dart'
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    goal = """
    Fix all 65 analysis errors in this file. 
    1. Address undefined names: _status, _scrollController, _messages, _isTyping, _chatController.
    2. Remove duplicate _chatController declaration (line 50 vs 49).
    3. Ensure _sendMessage is correctly scoped and uses try/catch.
    4. Fix deprecated member use: replace .withOpacity(x) with .withValues(alpha: x) if appropriate for Flutter 3, or ensure standard opacity usage.
    5. Fix any other lint or structural issues to achieve zero analysis errors.
    """

    print("🚀 Starting Ralph Loop Autonomous Development...")
    result = skill.execute('ralph_mode', goal=goal, context_code=code)
    
    result_path = r'C:\Users\super\Watchtower\Rhea-Noir-Ai\ralph_result.json'
    with open(result_path, 'w', encoding='utf-8') as rf:
        json.dump(result, rf, indent=2)
    
    print(f"✅ Ralph Loop Complete. Result saved to {result_path}")
    if result.get("success") and result.get("status") == "verified":
        print("🎉 Code VERIFIED by autonomous loop!")
        
        # Apply the fix immediately
        new_code = result.get("result", "")
        if "```" in new_code:
            parts = new_code.split("```")
            for part in parts:
                if part.strip().startswith("dart"):
                    new_code = part.replace("dart", "", 1).strip()
                    break
        
        with open(path, 'w', encoding='utf-8') as wf:
            wf.write(new_code)
        print(f"📝 Applied fixes to {path}")
    else:
        print("❌ Verification failed or incomplete.")
        print(f"Status: {result.get('status')}")
        if "history" in result:
             print(f"Final Verifier Errors: {result['history'][-1]['errors']}")

if __name__ == "__main__":
    main()
