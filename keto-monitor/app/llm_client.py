import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load environment variables from .env file
load_dotenv()

def call_openai(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini", api_key: str = None) -> str:
    """
    Executes a single completion call against OpenAI.
    - system_prompt: Role/Instruction for the model
    - user_prompt: Actual content
    - model: Model name, default is a fast/cheap model
    - api_key: Optional API key. If not provided, OPENAI_API_KEY environment variable is used.
    Returns: Only the pure response text (without metadata).
    """
    client_api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
    
    if not client_api_key:
        print("Error: OPENAI_API_KEY not found.")
        return "Error: No API Key"

    # Check for OpenRouter Key
    base_url = None
    if client_api_key.startswith("sk-or-v1"):
        base_url = "https://openrouter.ai/api/v1"
        # OpenRouter often requires a 'referer' header, but the python client handles basics.
        # We might need to adjust model name if gpt-4o-mini isn't supported directly, 
        # but OpenRouter usually maps it. 
        # For safety, we can default to 'openai/gpt-4o-mini' if needed, but let's try standard first.

    client = OpenAI(api_key=client_api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error in llm_client: {e}")
        # import traceback
        # traceback.print_exc()
        return f"Error: {e}"
