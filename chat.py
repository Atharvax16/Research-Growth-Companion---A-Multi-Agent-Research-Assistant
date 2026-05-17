"""
Research Growth Companion — Interactive Chat
Run after setup_agents.py: python chat.py
"""
import os
import sys
import io

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

# Try importing the correct SDK
try:
    from lyzr_python_sdk import LyzrAgentAPI
    USE_NEW_SDK = True
except ImportError:
    try:
        from lyzr_agent_api.client import AgentAPI
        USE_NEW_SDK = False
    except ImportError:
        print("Error: No Lyzr SDK found. Install one:")
        print("  pip install lyzr-python-sdk          (recommended)")
        print("  pip install lyzr-agent-api           (alternative)")
        exit(1)

# Load agent config
config = {}
try:
    with open(".agent_config") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                config[key] = val
except FileNotFoundError:
    print("Error: .agent_config not found. Run setup_agents.py first.")
    exit(1)

api_key = os.getenv("LYZR_API_KEY") or os.getenv("LYZR_AGENT_API_KEY")
if not api_key:
    print("Error: Set LYZR_API_KEY in your .env file.")
    exit(1)

if USE_NEW_SDK:
    client = LyzrAgentAPI(api_key=api_key)
else:
    client = AgentAPI(x_api_key=api_key)
orchestrator_id = config["ORCHESTRATOR_ID"]
user_id = "researcher-user-01"
session_id = "session-main"

BANNER = """
╔══════════════════════════════════════════════════╗
║       🔬 Research Growth Companion               ║
║       Your AI-powered research assistant          ║
╚══════════════════════════════════════════════════╝

 Try these:
  • "I'm interested in mechanistic interpretability and efficient LLMs"
  • "What are the latest papers on vision-language models?"
  • "When is ICML 2026 submission deadline?"
  • "Compare Llama 3 vs Mistral for code generation"
  • "Find me research roles in NLP at top labs"
  • "Give me a full research update"

 Type 'quit' to exit.
"""

print(BANNER)

while True:
    try:
        user_input = input("\n📝 You: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        break

    if user_input.lower() in ("quit", "exit", "q"):
        print("\nGoodbye! Keep pushing the frontier. 🚀")
        break
    if not user_input:
        continue

    print("\n⏳ Thinking...\n")

    try:
        if USE_NEW_SDK:
            response = client.inference.chat({
                "agent_id": orchestrator_id,
                "user_id": user_id,
                "session_id": session_id,
                "message": user_input,
            })
        else:
            response = client.chat_with_agent(
                agent_id=orchestrator_id,
                user_id=user_id,
                session_id=session_id,
                message=user_input,
            )
        # Handle different response formats
        if isinstance(response, dict):
            text = response.get("response", response.get("message", str(response)))
        else:
            text = str(response)

        print(f"🤖 Companion:\n{text}")

    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("   (Check your API key and internet connection)")
