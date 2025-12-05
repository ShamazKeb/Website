import os
import sys
from app.llm_client import call_openai

def main():
    print("--- Test: OpenAI Client ---")
    
    # 1. Check API Key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.")
        print("Please set it via environment variable.")
        print("Windows PowerShell: $env:OPENAI_API_KEY='your_key'")
        print("Command Prompt: set OPENAI_API_KEY=your_key")
        sys.exit(1)
        
    print(f"API Key found (starts with: {api_key[:8]}...)")
    
    # 2. Test Call
    print("\nSending test request to OpenAI...")
    try:
        system_prompt = "Du bist ein kurzer, präziser Assistent."
        user_prompt = "Schreibe einen sehr kurzen Satz, der bestätigt, dass der LLM-Client funktioniert."
        
        response = call_openai(system_prompt, user_prompt)
        
        print("\n--- Response from OpenAI ---")
        print(response)
        print("----------------------------")
        print("SUCCESS: Client is working.")
        
    except Exception as e:
        print(f"\nFAILURE: Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Documentation:
# 1. Set API Key: $env:OPENAI_API_KEY="sk-..."
# 2. Run Test: python test_llm_client.py
