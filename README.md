# Research Growth Companion

A multi-agent AI research assistant built on the [Lyzr](https://lyzr.ai) platform. It uses six coordinated agents to help AI/ML researchers stay current with papers, conferences, benchmarks, and career opportunities -- all personalized to individual research interests.

## Architecture

```
                          +---------------------+
                          |       User          |
                          +--------+------------+
                                   |
                                   v
                          +--------+------------+
                          |    chat.py          |
                          |  (CLI Interface)    |
                          +--------+------------+
                                   |
                                   v
                   +---------------+----------------+
                   |     Research Growth             |
                   |     Orchestrator                |
                   |                                 |
                   |  - Analyzes user intent          |
                   |  - Routes to specialist(s)       |
                   |  - Merges responses              |
                   +--+-----+-----+-----+-----+-----+
                      |     |     |     |     |
          +-----------+  +--+--+  |  +--+--+  +-----------+
          v              v     v  v  v     v              v
   +------+------+ +----+---+ +--+--+-+ +--+------+ +----+--------+
   | Paper Scout  | | Event  | |Bench- | | Career  | |Personalizer |
   |              | |Tracker | | mark  | | Advisor | |             |
   | - arXiv      | |        | |Analyst| |         | | - Learns    |
   | - Semantic   | | - CFPs | |       | | - Jobs  | |   interests |
   |   Scholar    | | - Conf | | - MMLU| | - Post- | | - Refines   |
   | - Top venues | | - Dead-| | - Eval| |   docs  | |   results   |
   |              | |  lines | | - SOTA| | - Grants| |             |
   +--------------+ +--------+ +------++ +---------+ +-------------+
                                   |
                                   v
                          +--------+------------+
                          |   Lyzr Agent API     |
                          |  (gpt-4o-mini LLM)   |
                          +---------------------+
```

### How Routing Works

The orchestrator determines intent from the user's message and delegates accordingly:

| User Query | Routed To |
|---|---|
| "Latest papers on RLHF" | Paper Scout |
| "When is NeurIPS deadline?" | Event Tracker |
| "Compare GPT-4o vs Claude for coding" | Benchmark Analyst |
| "Research roles at DeepMind" | Career Advisor |
| "I'm interested in multimodal learning" | Personalizer + Paper Scout |
| "Give me a full research update" | All agents |

## Agents

| Agent | Role | Capabilities |
|---|---|---|
| **Orchestrator** | Manager | Routes queries to specialists, merges outputs, adds proactive suggestions |
| **Paper Scout** | Paper Discovery | Finds and summarizes recent papers from arXiv, Semantic Scholar, and top venues (NeurIPS, ICML, ICLR, ACL, CVPR) |
| **Event Tracker** | Conference Monitor | Tracks upcoming conferences, workshops, CFPs, submission deadlines, tutorials, and keynotes |
| **Benchmark Analyst** | Model Comparison | Compares models on standard benchmarks (MMLU, HumanEval, MATH, GSM8K), tracks leaderboards, analyzes cost-performance |
| **Career Advisor** | Career Guide | Finds researcher positions, postdocs, fellowships, and grants; suggests growth roadmaps |
| **Personalizer** | Interest Profiling | Learns research interests over time, ranks results by relevance, suggests new directions |

## Tech Stack

- **Platform**: [Lyzr Agent Studio](https://agent.lyzr.ai) (agent orchestration and hosting)
- **SDK**: `lyzr-python-sdk` (with fallback to `lyzr-agent-api`)
- **LLM**: GPT-4o-mini via Lyzr's managed OpenAI credits
- **Language**: Python 3.9+

## Prerequisites

- Python 3.9+
- A free [Lyzr Agent Studio](https://agent.lyzr.ai) account (500 free credits/month on Community plan)

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Atharvax16/Research-Growth-Companion---A-Multi-Agent-Research-Assistant.git
cd Research-Growth-Companion---A-Multi-Agent-Research-Assistant

# 2. Install dependencies
pip install lyzr-python-sdk python-dotenv

# 3. Configure API key
#    Get your key from https://agent.lyzr.ai -> Settings -> API Keys
echo "LYZR_API_KEY=your_key_here" > .env

# 4. Create agents on the Lyzr platform
python setup_agents.py

# 5. Start chatting
python chat.py
```

## Project Structure

```
Research_agent/
├── setup_agents.py    # Creates all 6 agents on Lyzr platform, saves config
├── chat.py            # Interactive CLI chat interface
├── .env               # API keys (not tracked in git)
├── .agent_config      # Auto-generated agent IDs (not tracked in git)
├── .gitignore
└── README.md
```

## File Details

### `setup_agents.py`

- Validates API key and checks connectivity to the Lyzr API endpoint
- Supports both `lyzr-python-sdk` (recommended) and `lyzr-agent-api` (legacy fallback)
- Creates 5 specialist agents with defined roles, instructions, and goals
- Creates 1 orchestrator agent with managed references to all specialists
- Saves all agent IDs to `.agent_config` for use by `chat.py`

### `chat.py`

- Loads agent configuration and API credentials
- Auto-detects installed SDK version
- Sends user messages to the orchestrator via `inference.chat()` API
- Handles Windows console encoding for Unicode output
- Supports graceful exit via `quit`, `exit`, `q`, or `Ctrl+C`

## Example Session

```
You: I'm interested in mechanistic interpretability and efficient LLMs

Companion: I've noted your research interests. Here are the top recent papers...
  - "Scaling Monosemanticity" (Anthropic, 2024) - Dictionary learning on Claude...
  - "QLoRA: Efficient Finetuning" - 4-bit quantization approach...
  Would you also like me to check upcoming workshops on interpretability?

You: Yes, and any researcher positions in interpretability?

Companion:
  Events: ICML 2026 Mechanistic Interpretability Workshop - Deadline: Mar 15...
  Positions: Anthropic Interpretability Researcher (San Francisco)...
             DeepMind Alignment Research Scientist (London)...
```

## Troubleshooting

| Issue | Fix |
|---|---|
| `DNS resolution failed` | Try `ipconfig /flushdns` or switch DNS to `8.8.8.8` / `1.1.1.1` |
| `No Lyzr SDK found` | Run `pip install lyzr-python-sdk` |
| `.agent_config not found` | Run `python setup_agents.py` first |
| `UnicodeEncodeError` on Windows | Already handled -- `chat.py` wraps stdout in UTF-8 |
| `HTTP 401 / auth error` | Check your `LYZR_API_KEY` in `.env` |

## License

MIT
