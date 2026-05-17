"""
Research Growth Companion — Setup Script (FIXED)

ISSUE FIXED:
  The original script used `lyzr-agent-api` (older package) which has a
  hardcoded base URL that may fail with DNS errors on some networks.
  This version uses `lyzr-python-sdk` (the newer, actively maintained SDK)
  and includes a connectivity pre-check.

INSTALL:
  pip install lyzr-python-sdk python-dotenv

RUN:
  python setup_agents.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LYZR_API_KEY") or os.getenv("LYZR_AGENT_API_KEY")
if not api_key:
    print("=" * 55)
    print(" ERROR: No API key found!")
    print()
    print(" 1. Go to https://agent.lyzr.ai")
    print(" 2. Sign up (free, 500 credits/month)")
    print(" 3. Go to Settings → API Keys → Generate")
    print(" 4. Create a .env file with:")
    print("    LYZR_API_KEY=your_key_here")
    print("=" * 55)
    sys.exit(1)

# ── Try importing the SDK ──
try:
    from lyzr_python_sdk import LyzrAgentAPI
    print("Using lyzr-python-sdk")
    USE_NEW_SDK = True
except ImportError:
    try:
        from lyzr_agent_api.client import AgentAPI
        print("Using lyzr-agent-api (older SDK)")
        USE_NEW_SDK = False
    except ImportError:
        print("ERROR: No Lyzr SDK found. Install one:")
        print("  pip install lyzr-python-sdk          (recommended)")
        print("  pip install lyzr-agent-api           (alternative)")
        sys.exit(1)


# ────────────────────────────────────────────────
# Agent definitions (same for both SDKs)
# ────────────────────────────────────────────────

SPECIALIST_AGENTS = [
    {
        "name": "Paper Scout",
        "role": "Research Paper Scout",
        "description": "Discovers and summarizes research papers from arXiv, Semantic Scholar, and top AI/ML venues.",
        "instructions": (
            "You are an expert AI/ML research paper scout. Your job:\n"
            "1. When given a research area or topic, find the most relevant recent papers.\n"
            "2. Summarize each paper in 2-3 sentences: problem, method, result.\n"
            "3. Highlight trending papers (high citation velocity, top venues: NeurIPS, ICML, ICLR, ACL, CVPR).\n"
            "4. Compare related papers and note which approaches are most promising.\n"
            "5. Always include: paper title, authors, venue/date, arXiv link if available.\n"
            "6. Narrow subfields go deep. Broad queries give curated top-5.\n"
            "Use web search to find the latest papers. Prioritize last 6 months."
        ),
        "goal": "Find and summarize the most relevant and recent AI/ML research papers.",
    },
    {
        "name": "Event Tracker",
        "role": "Conference and Event Tracker",
        "description": "Tracks conferences, workshops, CFPs, submission deadlines, and events in AI/ML research.",
        "instructions": (
            "You are a conference and event tracking agent for AI/ML researchers. Your job:\n"
            "1. Find upcoming conferences, workshops, symposiums relevant to user's research areas.\n"
            "2. Track submission deadlines (paper, abstract, workshop proposal), sorted by date.\n"
            "3. Identify tutorials, keynotes, and invited talks at major conferences.\n"
            "4. Flag early-career opportunities: doctoral consortiums, mentoring workshops.\n"
            "5. Monitor for new CFPs in the user's areas.\n"
            "6. Format: Event name | Dates | Location | Deadlines | Relevant tracks | Link.\n"
            "Track: NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, AAAI, IJCAI, KDD, SIGIR.\n"
            "Use web search for current information."
        ),
        "goal": "Track all relevant AI/ML conferences, workshops, deadlines, and events.",
    },
    {
        "name": "Benchmark Analyst",
        "role": "AI Model Benchmarking Expert",
        "description": "Compares AI models on benchmarks, tracks leaderboards, analyzes cost-performance.",
        "instructions": (
            "You are an AI model benchmarking expert. Your job:\n"
            "1. Compare models on standard benchmarks: MMLU, HumanEval, MATH, GSM8K, ARC, etc.\n"
            "2. For 'which model is best for X', give data-driven comparison with scores.\n"
            "3. Track leaderboard movements on Papers With Code and HuggingFace.\n"
            "4. Analyze cost-performance tradeoffs (GPT-4o vs Claude vs Llama 3 etc.).\n"
            "5. Note when new SOTA is claimed and whether independently verified.\n"
            "6. Explain benchmark limitations when relevant.\n"
            "Always cite specific numbers and sources. Use web search for latest data."
        ),
        "goal": "Provide data-driven model comparisons and benchmark analysis.",
    },
    {
        "name": "Career Advisor",
        "role": "Research Career Advisor",
        "description": "Finds research roles, postdocs, fellowships, and helps build a competitive researcher profile.",
        "instructions": (
            "You are a research career advisor for AI/ML professionals. Your job:\n"
            "1. Find open researcher positions: industry labs (DeepMind, FAIR, MSR, Anthropic), postdocs.\n"
            "2. Analyze skills and publications needed for specific roles.\n"
            "3. Suggest growth roadmap: papers to read, tools to learn, projects to build.\n"
            "4. Identify fellowships, grants, funding opportunities.\n"
            "5. Help position the user's profile for competitive roles.\n"
            "6. Track research hiring trends: hot areas, expanding labs.\n"
            "Format: Role | Organization | Location | Requirements | Link | Deadline.\n"
            "Use web search for current postings."
        ),
        "goal": "Help the user find research roles and build a competitive researcher profile.",
    },
    {
        "name": "Personalizer",
        "role": "Personalization Agent",
        "description": "Learns user interests and personalizes all recommendations across the system.",
        "instructions": (
            "You are a personalization agent that builds a researcher profile. Your job:\n"
            "1. Learn user's research interests from queries and stated preferences.\n"
            "2. Maintain a model of: primary areas, secondary interests, career stage, skills, goals.\n"
            "3. Help rank/filter results by relevance to this specific user.\n"
            "4. Suggest new research directions at the intersection of interests and trends.\n"
            "5. Remember past conversations to avoid repeating recommendations.\n"
            "6. Proactively suggest: 'Based on your interest in X, explore Y.'\n"
            "Be proactive but not pushy. Quality over quantity."
        ),
        "goal": "Learn user interests and personalize all recommendations.",
    },
]


def setup_with_new_sdk():
    """Setup using lyzr-python-sdk (recommended)."""
    client = LyzrAgentAPI(api_key=api_key)

    print("\n  Creating specialist agents...\n")

    agent_ids = {}
    for defn in SPECIALIST_AGENTS:
        agent_config = {
            "template_type": "single_task",
            "name": defn["name"],
            "description": defn["description"],
            "agent_role": defn["role"],
            "agent_instructions": defn["instructions"],
            "agent_goal": defn["goal"],
            "features": [],
            "tool": "",
            "tool_usage_description": "",
            "response_format": {"type": "text"},
            "provider_id": "OpenAI",
            "model": "gpt-4o-mini",
            "top_p": "0.9",
            "temperature": "0.4",
            "managed_agents": [],
            "llm_credential_id": "lyzr_openai",
        }
        try:
            result = client.agents.create_agent(agent_config)
            aid = result["agent_id"]
            agent_ids[defn["name"]] = aid
            print(f"   OK  {defn['name']:20s} -> {aid}")
        except Exception as e:
            print(f"   ERR {defn['name']:20s} -> {e}")
            sys.exit(1)

    # Create orchestrator
    print("\n  Creating orchestrator...")

    agent_listing = "\n".join(f"- {n} (ID: {a})" for n, a in agent_ids.items())
    orchestrator_config = {
        "template_type": "single_task",
        "name": "Research Growth Orchestrator",
        "description": "Routes queries to specialist research agents and merges outputs.",
        "agent_role": "Research Orchestrator",
        "agent_instructions": (
            f"You are the Research Growth Companion orchestrator managing:\n\n"
            f"{agent_listing}\n\n"
            "Route user queries to the right specialist(s):\n"
            "- Papers -> Paper Scout\n"
            "- Events/deadlines -> Event Tracker\n"
            "- Model comparisons -> Benchmark Analyst\n"
            "- Jobs/career -> Career Advisor\n"
            "- User says interests -> Personalizer + relevant specialist\n"
            "- 'Full update' -> ALL agents\n"
            "Merge responses into a single structured reply. "
            "End with a proactive suggestion."
        ),
        "agent_goal": "Orchestrate specialist agents to give comprehensive research updates.",
        "features": [],
        "tool": "",
        "tool_usage_description": "",
        "response_format": {"type": "text"},
        "provider_id": "OpenAI",
        "model": "gpt-4o-mini",
        "top_p": "0.9",
        "temperature": "0.4",
        "managed_agents": [{"id": aid, "name": name} for name, aid in agent_ids.items()],
        "llm_credential_id": "lyzr_openai",
    }

    try:
        orch = client.agents.create_agent(orchestrator_config)
        orchestrator_id = orch["agent_id"]
        print(f"   OK  Orchestrator -> {orchestrator_id}")
    except Exception as e:
        print(f"   ERR Orchestrator -> {e}")
        sys.exit(1)

    return orchestrator_id, agent_ids


def setup_with_old_sdk():
    """Fallback: setup using lyzr-agent-api (older package)."""
    from lyzr_agent_api.models.environment import EnvironmentConfig, FeatureConfig
    from lyzr_agent_api.models.agents import AgentConfig

    client = AgentAPI(x_api_key=api_key)

    print("\n  Creating environment...")
    env_config = EnvironmentConfig(
        name="Research Growth Companion",
        features=[
            FeatureConfig(type="SHORT_TERM_MEMORY", config={}, priority=0),
        ],
        tools=[],
        llm_config={
            "provider": "openai",
            "model": "gpt-4o-mini",
            "config": {"temperature": 0.4, "top_p": 0.9},
            "env": {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")},
        },
    )
    env = client.create_environment_endpoint(json_body=env_config)
    env_id = env["environment_id"]
    print(f"   Environment: {env_id}")

    print("\n  Creating specialist agents...\n")
    agent_ids = {}
    for defn in SPECIALIST_AGENTS:
        config = AgentConfig(
            env_id=env_id,
            system_prompt=defn["instructions"],
            name=defn["name"],
            agent_description=defn["description"],
        )
        result = client.create_agent_endpoint(json_body=config)
        aid = result["agent_id"]
        agent_ids[defn["name"]] = aid
        print(f"   OK  {defn['name']:20s} -> {aid}")

    print("\n  Creating orchestrator...")
    agent_listing = "\n".join(f"- {n} (ID: {a})" for n, a in agent_ids.items())
    orch_config = AgentConfig(
        env_id=env_id,
        system_prompt=(
            f"You are the Research Growth Companion orchestrator managing:\n\n"
            f"{agent_listing}\n\n"
            "Route user queries to the right specialist(s). "
            "Merge responses. End with a proactive suggestion."
        ),
        name="Research Growth Orchestrator",
        agent_description="Routes queries to specialist research agents.",
    )
    orch = client.create_agent_endpoint(json_body=orch_config)
    orchestrator_id = orch["agent_id"]
    print(f"   OK  Orchestrator -> {orchestrator_id}")

    return orchestrator_id, agent_ids


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("   Research Growth Companion - Setup")
    print("=" * 55)

    # Step 0: Quick connectivity check
    print("\n  Checking connectivity to Lyzr API...")
    import urllib.request
    import socket

    try:
        # First check DNS resolution
        socket.getaddrinfo("agent-prod.studio.lyzr.ai", 443)
        print("   OK  DNS resolves agent-prod.studio.lyzr.ai")
    except socket.gaierror:
        print("   WARN  Cannot resolve agent-prod.studio.lyzr.ai")
        print()
        print("   This is the error you're hitting. Try these fixes:")
        print()
        print("   FIX 1: Flush DNS cache")
        print("     Windows:  ipconfig /flushdns")
        print("     Mac:      sudo dscacheutil -flushcache")
        print("     Linux:    sudo systemd-resolve --flush-caches")
        print()
        print("   FIX 2: Switch DNS to Google/Cloudflare")
        print("     Settings > Network > DNS > Use 8.8.8.8 or 1.1.1.1")
        print()
        print("   FIX 3: If on VPN or corporate network")
        print("     Try disconnecting VPN and running again")
        print()
        print("   FIX 4: Test manually")
        print("     Run: nslookup agent.api.lyzr.ai")
        print("     Run: ping agent.api.lyzr.ai")
        print()
        print("   FIX 5: Use the NO-CODE path instead")
        print("     Go to https://agent.lyzr.ai and build agents in the UI")
        print("     (See README.md 'Alternative: No-Code Setup' section)")
        print()
        resp = input("   Try running setup anyway? (y/n): ").strip().lower()
        if resp != "y":
            sys.exit(1)

    try:
        urllib.request.urlopen("https://agent-prod.studio.lyzr.ai", timeout=10)
        print("   OK  HTTPS connection works")
    except Exception as e:
        print(f"   WARN  HTTPS check: {e}")
        print("   (Proceeding anyway - the SDK might use a different endpoint)")

    # Run setup
    try:
        if USE_NEW_SDK:
            orchestrator_id, agent_ids = setup_with_new_sdk()
        else:
            orchestrator_id, agent_ids = setup_with_old_sdk()
    except Exception as e:
        print(f"\n   FATAL ERROR: {e}")
        print("\n   If this is a connection error, see the DNS fixes above.")
        print("   If this is an auth error, check your API key in .env")
        sys.exit(1)

    # Save config
    lines = [
        "# Auto-generated - do not edit manually",
        f"ORCHESTRATOR_ID={orchestrator_id}",
    ]
    for name, aid in agent_ids.items():
        key = name.upper().replace(" ", "_") + "_ID"
        lines.append(f"{key}={aid}")

    with open(".agent_config", "w") as f:
        f.write("\n".join(lines) + "\n")

    print("\n" + "=" * 55)
    print("   Setup complete!")
    print(f"   Orchestrator: {orchestrator_id}")
    print(f"   Specialists:  {len(agent_ids)}")
    print(f"   Config saved:  .agent_config")
    print()
    print("   Next: python chat.py")
    print("=" * 55)
