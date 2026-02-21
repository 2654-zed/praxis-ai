# Praxis — AI Decision Engine

Praxis is an **AI decision engine** that helps people and businesses choose the right AI tools for their needs. It is **not** a directory or search engine — it builds **personalized AI tool stacks** with explanations, trade-offs, and integration context.

---

## Architecture

```
User → Interpreter → Decision Engine → Stack Composer → Explanation Generator
          ↑                ↑                 ↑                    ↑
        config          Profile           Learning            Feedback
       (LLM opt.)      (budget,          (signals)          (accept/rate)
                       skill, goals)
```

### Core Modules

| Module | Purpose |
|--------|---------|
| `interpreter.py` | Converts free-form queries into structured intent. LLM-backed (OpenAI / Anthropic) with rule-based fallback. |
| `engine.py` | Profile-aware scoring and ranking. Combines keyword, tag, category, popularity, use-case, and profile-fit signals. |
| `stack.py` | Composes multi-tool stacks with roles (primary, companion, infrastructure). |
| `explain.py` | Generates human-readable per-tool and per-stack explanations with fit scores, reasons, and caveats. |
| `profile.py` | User profile management (industry, budget, skill, existing tools, goals, constraints). JSON persistence. |
| `learning.py` | Feedback loop: computes tool quality, pair affinities, and intent-tool maps from feedback data. |
| `config.py` | Centralized config: env vars → config.json → defaults. Controls LLM provider, model, feature flags. |
| `tools.py` | `Tool` class with 14 fields: pricing, integrations, compliance, skill level, use cases, stack roles. |
| `data.py` | In-memory knowledge base of 25+ enriched AI tools. SQLite persistence via `storage.py`. |
| `feedback.py` | Records user accept/reject/rating feedback to `feedback.json`. |
| `usage.py` | Tracks search frequency and computes popularity signals. |

### Interfaces

| Interface | Description |
|-----------|-------------|
| **CLI** (`main.py`) | Interactive decision engine with commands: `profile`, `stack`, `compare X vs Y`, `learn`, `help`. |
| **API** (`api.py`) | FastAPI with endpoints: `/stack`, `/search`, `/compare`, `/profile`, `/feedback`, `/learn`. |
| **Frontend** | Guided journey wizard (`journey.html`), tool browser (`tools.html`). |

---

## Quick Start

### Prerequisites
- Python 3.10+
- (Optional) OpenAI or Anthropic API key for LLM-powered interpretation

### Install

```bash
pip install -e .

# Optional: LLM support
pip install openai anthropic
```

### CLI

```bash
praxis
# or
python -m praxis.main
```

**CLI Commands:**
- Type a question → quick search (e.g., "I need a writing tool")
- `profile` → build a user profile interactively
- `stack` → guided stack recommendation with roles and explanations
- `compare ChatGPT vs Claude` → side-by-side comparison
- `learn` → run the learning cycle to improve recommendations
- `help` → show all commands

### API

```bash
uvicorn praxis.api:app --reload --port 8000
```

Open `http://localhost:8000` for the guided journey UI.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/stack` | Get a composed AI tool stack with explanations. Body: `{ "query": "...", "profile_id": "default", "stack_size": 3 }` |
| `POST` | `/search` | Keyword search with optional profile. Body: `{ "query": "...", "filters": ["design"], "profile_id": "default" }` |
| `POST` | `/compare` | Compare two tools. Body: `{ "tool_a": "ChatGPT", "tool_b": "Claude" }` |
| `POST` | `/profile` | Create/update user profile. Body: `{ "profile_id": "default", "industry": "saas", "budget": "medium", ... }` |
| `GET` | `/profile/{id}` | Retrieve a user profile. |
| `GET` | `/tools` | List all tools with full metadata. |
| `GET` | `/categories` | List available categories. |
| `POST` | `/feedback` | Record feedback. Body: `{ "query": "...", "tool": "ChatGPT", "accepted": true, "rating": 8 }` |
| `POST` | `/learn` | Trigger learning cycle (recompute tool quality from feedback). |

---

## Configuration

Set environment variables or create `config.json` in the project root:

```bash
# LLM provider (optional)
export PRAXIS_LLM_PROVIDER=openai     # or "anthropic"
export PRAXIS_OPENAI_API_KEY=sk-...
export PRAXIS_OPENAI_MODEL=gpt-4o-mini

# Features
export PRAXIS_EXPLAIN=true
export PRAXIS_STACK_SIZE=3
```

Without an LLM key, Praxis falls back to its enhanced rule-based interpreter.

---

## Project Layout

```
praxis/
├── main.py              # CLI entry point
├── api.py               # FastAPI HTTP layer
├── interpreter.py       # Intent extraction (LLM + rule-based)
├── engine.py            # Scoring & ranking engine
├── stack.py             # Multi-tool stack composer
├── explain.py           # Explanation generator
├── profile.py           # User profile management
├── learning.py          # Feedback-to-signal loop
├── config.py            # Configuration management
├── tools.py             # Tool data class
├── data.py              # Knowledge base (25+ tools)
├── storage.py           # SQLite persistence
├── feedback.py          # Feedback recording
├── usage.py             # Popularity tracking
├── frontend/
│   ├── journey.html     # Guided wizard UI
│   ├── journey-script.js
│   ├── tools.html       # Tool browser
│   └── tools-script.js
└── tests/
    ├── test_engine.py
    └── test_interpreter.py
```

---

## How It Works

1. **Interpret** — User query is parsed into structured intent (task, industry, goal, keywords, entities).
2. **Profile** — User's budget, skill level, existing tools, and constraints shape the ranking.
3. **Score** — Each tool is scored against intent signals + profile fit (budget, skill, integration, compliance).
4. **Compose** — Top tools are assembled into a stack with distinct roles: primary, companion, infrastructure.
5. **Explain** — Each recommendation comes with reasons, caveats, and a fit score (0–100%).
6. **Learn** — User feedback (accept/reject/rate) feeds back into quality signals for future recommendations.

---

## Extending

- **Add tools**: Edit `data.py` and add `Tool(...)` entries with all metadata fields.
- **Add LLM providers**: Extend `interpreter.py` or `config.py` to support new providers.
- **Custom scoring**: Modify `engine.py` `score_tool()` and `score_profile_fit()`.
- **Webhooks / integrations**: Add new API endpoints in `api.py`.
- **Persistent profiles**: Swap `profiles.json` for a database in `profile.py`.
