# Research Growth Companion — Multi-Agent System on Lyzr

A multi-agent AI system that keeps AI/ML/DS researchers and enthusiasts up to date with papers, events, workshops, benchmarks, model comparisons, deadlines, and career opportunities — all personalized to your research interests.

---

## Prerequisites

- Python 3.9+
- A free Lyzr Agent Studio account → [https://agent.lyzr.ai](https://agent.lyzr.ai)
  - Sign up to get **500 free monthly credits** on the Community plan
- An OpenAI API key (Lyzr provides `lyzr_openai` credits on the free tier, so you can start without your own key)

---

## Quick Start (5 minutes)

```bash
# 1. Clone this repo
git clone <your-repo-url>
cd research_growth_companion

# 2. Install dependencies
pip install lyzr-agent-api python-dotenv requests

# 3. Set your API key
cp .env.example .env
# Edit .env and add your LYZR_API_KEY (get it from https://agent.lyzr.ai → Settings → API Keys)

# 4. Run the setup script (creates all agents + environment)
python setup_agents.py

# 5. Start chatting with your research companion
python chat.py
```

---

## System Architecture

### Agent Roles

| Agent | Role | What It Does |
|-------|------|--------------|
| **Orchestrator** | Manager agent | Receives your query, decides which specialist(s) to invoke, merges their outputs into a coherent response |
| **Paper Scout** | Research paper discovery | Searches arXiv, Semantic Scholar, DBLP for papers matching your interests; summarizes key findings; tracks citation trends |
| **Event Tracker** | Conference & deadline monitor | Finds upcoming conferences, workshops, submission deadlines (CFPs), tutorial sessions, and presentation schedules in your areas |
| **Benchmark Analyst** | Model comparison expert | Compares models on standard benchmarks (MMLU, HumanEval, MATH, etc.), tracks leaderboard movements, analyzes which model is best for a specific task |
| **Career Advisor** | Research career guide | Finds researcher roles, postdocs, industry research positions; identifies skill gaps; suggests how to build a competitive profile |
| **Personalizer** | Interest profiling | Learns your research interests over conversations; refines recommendations; builds your researcher profile for career matching |

### Data Flow

```
You → Orchestrator → routes to relevant agent(s)
                   ↓
         Paper Scout ← arXiv API, Semantic Scholar API, web search
         Event Tracker ← WikiCFP, conference websites, web search
         Benchmark Analyst ← Papers With Code, HuggingFace leaderboards, web search
         Career Advisor ← job boards, university postings, web search
         Personalizer ← conversation history, user profile store
                   ↓
         Orchestrator merges results → structured response → You
```

---

## File Structure

```
research_growth_companion/
├── .env.example            # Template for API keys
├── setup_agents.py         # Creates all agents on Lyzr platform
├── chat.py                 # Interactive chat interface
├── tools/
│   ├── arxiv_tool.py       # arXiv search tool definition
│   ├── semantic_scholar.py # Semantic Scholar API tool
│   └── web_search_tool.py  # General web search tool
└── README.md
```

---

## Detailed Setup Guide

### Step 1: Get Your Lyzr API Key

1. Go to [https://agent.lyzr.ai](https://agent.lyzr.ai) and sign up (free)
2. You get **500 credits/month** on the Community plan — enough to prototype and test
3. Navigate to **Settings → API Keys** and generate a key
4. Copy the key — you'll need it in the next step

### Step 2: Configure Environment

Create a `.env` file:

```env
LYZR_API_KEY=your_lyzr_api_key_here
# Optional: bring your own OpenAI key for more control
# OPENAI_API_KEY=your_openai_key_here
```

### Step 3: Run the Setup Script

The setup script below creates all six agents and wires them together. Run it once.

---

## Implementation Code

### `setup_agents.py`

```python
"""
Setup script — run once to create all agents on Lyzr.
"""
import os
from dotenv import load_dotenv
from lyzr_agent_api.client import AgentAPI
from lyzr_agent_api.models.environment import EnvironmentConfig, FeatureConfig
from lyzr_agent_api.models.agents import AgentConfig

load_dotenv()
client = AgentAPI(x_api_key=os.getenv("LYZR_API_KEY"))

# ── Step 1: Create the shared environment ──
print("Creating environment...")
env_config = EnvironmentConfig(
    name="Research Growth Companion",
    features=[
        FeatureConfig(type="SHORT_TERM_MEMORY", config={}, priority=0),
        FeatureConfig(type="LONG_TERM_MEMORY", config={}, priority=1),
    ],
    tools=[],
    llm_config={
        "provider": "openai",
        "model": "gpt-4o-mini",       # cost-effective for free tier
        "config": {
            "temperature": 0.4,
            "top_p": 0.9,
        },
        "env": {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")
        }
    },
)
env = client.create_environment_endpoint(json_body=env_config)
env_id = env["environment_id"]
print(f"  Environment created: {env_id}")

# ── Step 2: Create specialist agents ──

agent_definitions = [
    {
        "name": "Paper Scout",
        "system_prompt": """You are an expert AI/ML research paper scout. Your job:
1. When given a research area or topic, find the most relevant recent papers.
2. Summarize each paper in 2-3 sentences: what problem it solves, the key method, and the main result.
3. Highlight papers that are trending (high citation velocity, from top venues like NeurIPS, ICML, ICLR, ACL, CVPR).
4. Compare related papers and note which approaches are most promising.
5. Always include: paper title, authors, venue/date, arXiv link if available.
6. If the user specifies a narrow subfield (e.g., "efficient fine-tuning for LLMs"), go deep. If broad ("what's new in NLP"), give a curated top-5.
Use web search to find the latest papers. Prioritize papers from the last 6 months.""",
        "description": "Discovers and summarizes research papers from arXiv, Semantic Scholar, and top venues based on user interests."
    },
    {
        "name": "Event Tracker",
        "system_prompt": """You are a conference and event tracking agent for AI/ML researchers. Your job:
1. Find upcoming conferences, workshops, and symposiums relevant to the user's research areas.
2. Track submission deadlines (paper, abstract, workshop proposal) and present them sorted by date.
3. Identify tutorials, keynotes, and invited talks at major conferences.
4. Flag early-career opportunities: doctoral consortiums, mentoring workshops, poster sessions.
5. Monitor for new CFPs (Call for Papers) in the user's areas.
6. Format output clearly with: Event name, dates, location (virtual/in-person), deadlines, relevant tracks, link.
Use web search to find current information. Major venues to track: NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, AAAI, IJCAI, KDD, SIGIR, and domain-specific workshops.""",
        "description": "Tracks conferences, workshops, CFPs, submission deadlines, and events in AI/ML research."
    },
    {
        "name": "Benchmark Analyst",
        "system_prompt": """You are an AI model benchmarking expert. Your job:
1. Compare models across standard benchmarks: MMLU, HumanEval, MATH, GSM8K, ARC, HellaSwag, etc.
2. When asked "which model is best for X task", provide a data-driven comparison with scores, strengths, and weaknesses.
3. Track leaderboard movements on Papers With Code and HuggingFace Open LLM Leaderboard.
4. Analyze cost-performance tradeoffs (e.g., GPT-4o vs Claude Sonnet vs Llama 3 for code generation).
5. Note when a new model claims SOTA and whether the claim has been independently verified.
6. Explain benchmark methodology limitations when relevant.
Always cite specific numbers and sources. Use web search for the latest benchmark data.""",
        "description": "Compares AI models on benchmarks, tracks leaderboards, and analyzes cost-performance tradeoffs."
    },
    {
        "name": "Career Advisor",
        "system_prompt": """You are a research career advisor for AI/ML professionals. Your job:
1. Find open researcher positions: industry labs (Google DeepMind, Meta FAIR, Microsoft Research, Anthropic, etc.), academic postdocs, and applied research roles.
2. Analyze what skills and publications a candidate needs for specific roles.
3. Suggest a growth roadmap: what papers to read, what tools to learn, what projects to build.
4. Identify relevant fellowships, grants, and funding opportunities.
5. Help the user understand how to position their profile for competitive roles.
6. Track trends in research hiring: what areas are hot, which labs are expanding.
Format output with: Role title, organization, location, key requirements, application link, deadline if known.
Use web search to find current job postings and opportunities.""",
        "description": "Finds research roles, postdocs, fellowships, and helps build a competitive researcher profile."
    },
    {
        "name": "Personalizer",
        "system_prompt": """You are a personalization agent that builds and maintains a researcher profile. Your job:
1. Learn the user's research interests from their queries and stated preferences.
2. Maintain a mental model of: their primary research areas, secondary interests, career stage, skill level, and goals.
3. When other agents return results, help rank and filter them by relevance to this specific user.
4. Suggest new research directions based on the intersection of their interests and emerging trends.
5. Remember past conversations to avoid repeating recommendations.
6. Periodically suggest: "Based on your interest in X, you might also want to explore Y."
Be proactive but not pushy. Quality over quantity in recommendations.""",
        "description": "Learns user interests and personalizes all recommendations across the system."
    },
]

agent_ids = {}
for defn in agent_definitions:
    agent_config = AgentConfig(
        env_id=env_id,
        system_prompt=defn["system_prompt"],
        name=defn["name"],
        agent_description=defn["description"],
    )
    agent = client.create_agent_endpoint(json_body=agent_config)
    agent_id = agent["agent_id"]
    agent_ids[defn["name"]] = agent_id
    print(f"  Created agent: {defn['name']} → {agent_id}")

# ── Step 3: Create the orchestrator (manager agent) ──

managed_agent_list = [
    {"agent_id": aid, "name": name}
    for name, aid in agent_ids.items()
]

orchestrator_prompt = f"""You are the Research Growth Companion orchestrator. You manage a team of specialist agents.

Your specialist agents and their IDs:
{chr(10).join(f"- {name}: {aid}" for name, aid in agent_ids.items())}

When a user sends a message:
1. Analyze the intent: Is it about papers? Events? Benchmarks? Career? A mix?
2. Route to the appropriate specialist(s). For broad queries like "what's new in RL", invoke Paper Scout + Event Tracker.
3. If the user mentions their interests for the first time, also invoke Personalizer to record them.
4. Merge responses from specialists into a single, well-structured reply.
5. Always end with a proactive suggestion: "Would you also like me to check [related thing]?"

Example routing:
- "Find me recent papers on RLHF" → Paper Scout
- "When is NeurIPS 2026 deadline?" → Event Tracker
- "Compare GPT-4o vs Claude for coding" → Benchmark Analyst
- "I want to apply for research roles at DeepMind" → Career Advisor
- "I'm interested in multimodal learning and efficient transformers" → Personalizer + Paper Scout
- "Give me a full update on my areas" → ALL agents

Be concise but thorough. Prioritize actionable information."""

orchestrator_config = AgentConfig(
    env_id=env_id,
    system_prompt=orchestrator_prompt,
    name="Research Growth Orchestrator",
    agent_description="Master agent that routes queries to specialist research agents and merges their outputs.",
)
orchestrator = client.create_agent_endpoint(json_body=orchestrator_config)
orchestrator_id = orchestrator["agent_id"]
print(f"  Created orchestrator: {orchestrator_id}")

# ── Save config for chat.py ──
config_content = f"""# Auto-generated by setup_agents.py — do not edit manually
ORCHESTRATOR_ID={orchestrator_id}
ENVIRONMENT_ID={env_id}
"""
for name, aid in agent_ids.items():
    config_content += f"{name.upper().replace(' ', '_')}_ID={aid}\n"

with open(".agent_config", "w") as f:
    f.write(config_content)

print("\n✅ All agents created! Config saved to .agent_config")
print(f"   Run 'python chat.py' to start chatting.")
```

### `chat.py`

```python
"""
Interactive chat with your Research Growth Companion.
"""
import os
from dotenv import load_dotenv
from lyzr_agent_api.client import AgentAPI

load_dotenv()

# Load agent config
config = {}
with open(".agent_config") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            key, val = line.split("=", 1)
            config[key] = val

client = AgentAPI(x_api_key=os.getenv("LYZR_API_KEY"))
orchestrator_id = config["ORCHESTRATOR_ID"]
user_id = "researcher-user-01"
session_id = "session-main"

print("=" * 60)
print("  🔬 Research Growth Companion")
print("  Your AI-powered research assistant")
print("=" * 60)
print()
print("Tell me your research interests, ask about papers,")
print("events, benchmarks, or career opportunities.")
print("Type 'quit' to exit.")
print()

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit", "q"):
        print("Goodbye! Keep researching. 🚀")
        break
    if not user_input:
        continue

    try:
        response = client.chat_with_agent(
            agent_id=orchestrator_id,
            user_id=user_id,
            session_id=session_id,
            message=user_input,
        )
        print(f"\n🤖 Companion: {response.get('response', response)}\n")
    except Exception as e:
        print(f"\n⚠️  Error: {e}\n")
```

### `.env.example`

```env
# Get your API key from https://agent.lyzr.ai → Settings → API Keys
LYZR_API_KEY=

# Optional: use your own OpenAI key (otherwise Lyzr free credits are used)
# OPENAI_API_KEY=
```

---

## Alternative: No-Code Setup via Agent Studio UI

If you prefer not to write code, you can build this entirely in the Lyzr Agent Studio web interface:

### Step-by-step:

1. **Sign up** at [agent.lyzr.ai](https://agent.lyzr.ai) (free, 500 credits)

2. **Create an environment:**
   - Go to Environments → Create New
   - Name: "Research Growth Companion"
   - LLM: select OpenAI → gpt-4o-mini
   - Enable: Short-term memory + Long-term memory
   - Save

3. **Create each agent (repeat 5 times for specialists):**
   - Go to Agents → Create New
   - Select the environment you just created
   - Copy the system prompt from the agent definitions above
   - Give it the matching name and description
   - Save → note the agent ID

4. **Create the orchestrator:**
   - Same process, but paste the orchestrator prompt
   - Reference the specialist agent IDs in the prompt

5. **Test in the Studio:**
   - Click on the orchestrator agent
   - Use the built-in chat to test queries like:
     - "What are the latest papers on vision-language models?"
     - "When is CVPR 2026 submission deadline?"
     - "Compare Llama 3 vs Mistral on coding benchmarks"

6. **Deploy as API:**
   - Each agent automatically gets an API endpoint
   - Use the agent ID to call it programmatically from your app

---

## Using the Lyzr CLI (lyzr-kit)

For the fastest workflow, use the Lyzr CLI:

```bash
# Install
pip install lyzr-kit

# Authenticate
lk auth

# List built-in agents (you might find useful starting points)
lk ls

# Deploy a built-in agent as your starting point
lk get chat-agent

# Chat with it
lk chat copy-of-chat-agent

# Edit the YAML to customize
# Edit agents/copy-of-chat-agent.yaml → change system_prompt, name, etc.
lk set copy-of-chat-agent
```

---

## Using Lyzr Architect (Fastest Path)

Lyzr Architect lets you describe your app in plain English and it generates the full multi-agent system automatically:

1. Go to [Lyzr Architect](https://www.lyzr.ai/lyzr-agent-studio/) (available in Agent Studio)
2. Describe your system:
   > "Build a multi-agent research companion for AI/ML researchers. It should have agents for: finding research papers from arXiv, tracking conference deadlines and CFPs, comparing model benchmarks, advising on research careers, and personalizing recommendations based on user interests. The orchestrator should route queries to the right specialist."
3. Architect will review its 1000+ blueprints, select the best match, and generate the full system with UI
4. Test, refine, and deploy — you get a live URL

---

## Credit Usage Tips (Staying Within Free Tier)

| Action | Approx Credits |
|--------|---------------|
| Single agent chat | 1-3 credits |
| Multi-agent orchestrated query | 5-15 credits |
| Complex "full update" across all agents | 15-30 credits |

**Tips to stay within 500 free credits:**
- Use `gpt-4o-mini` instead of `gpt-4o` (cheaper per call)
- For testing, chat directly with individual agents instead of the orchestrator
- Start with 2-3 agents and add more as you validate the concept
- Use the CLI (`lk chat`) for quick testing — it shows token usage per response

---

## Extending the System

### Add Custom Tools (OpenAPI)

You can give agents access to real APIs:

```python
# Example: Add arXiv search as a tool
tool_data = {
    "tool_set_name": "arxiv-search",
    "openapi_schema": {
        "openapi": "3.0.0",
        "info": {"title": "arXiv Search", "version": "1.0"},
        "paths": {
            "/api/query": {
                "get": {
                    "summary": "Search arXiv papers",
                    "parameters": [
                        {
                            "name": "search_query",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Search query for arXiv"
                        },
                        {
                            "name": "max_results",
                            "in": "query",
                            "schema": {"type": "integer", "default": 5}
                        }
                    ]
                }
            }
        },
        "servers": [{"url": "https://export.arxiv.org"}]
    },
    "default_headers": {},
    "enhance_descriptions": True,
}
tool = client.tools.create_tool(tool_data)
```

### Add Web Search Capability

Lyzr agents can use web search natively. In the Agent Studio, enable the "Web Search" feature in the environment configuration. This lets agents search the web for current information — critical for finding recent papers and upcoming events.

---

## Sample Conversations

**You:** "I'm interested in mechanistic interpretability and efficient inference for LLMs. What should I be reading?"

**Companion:** Here are the top recent papers in your areas...
- [Paper Scout finds 5 relevant papers with summaries]
- [Personalizer records your interests for future sessions]
- "Would you also like me to check upcoming workshops on interpretability at ICML 2026?"

**You:** "Yes, and are there any researcher positions in interpretability?"

**Companion:**
- [Event Tracker finds ICML 2026 interpretability workshop details + deadline]
- [Career Advisor finds open positions at Anthropic, DeepMind, and Redwood Research]
- "Based on your interest profile, you might also want to explore circuit discovery methods — it's a fast-growing subfield."

---

## Upgrading

| Plan | Credits | Best For |
|------|---------|----------|
| Community (Free) | 500/month | Prototyping, personal use |
| Starter ($19/mo) | 2,000/month | Regular daily use |
| Pro ($99/mo) | 10,000/month | Heavy usage, multiple areas |

---

## Resources

- [Lyzr Docs](https://docs.lyzr.ai)
- [Lyzr Agent API Python Client](https://docs.lyzr.ai/agent-api/python-client/python-client)
- [Lyzr GitHub](https://github.com/LyzrCore)
- [Lyzr Slack Community](https://lyzr.ai → Join Slack)
- [Lyzr SDK on PyPI](https://pypi.org/project/lyzr-agent-api/)
