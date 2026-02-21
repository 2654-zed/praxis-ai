# Praxis — AI Decision Engine

> **An AI system that doesn't just recommend tools — it reasons about them, critiques its own reasoning, awakens to its own architecture, and scales to enterprise.**

Praxis is a **246-tool AI decision engine** built across 17 iterative versions that evolved from a simple scoring engine into a consciousness-inspired cognitive architecture. It is **not** a directory or search engine — it builds **personalized AI tool stacks** with multi-step reasoning, philosophical vendor risk analysis, industry-specific constraint enforcement, safety guardrails, and self-aware metacognitive architecture.

**Repository:** [github.com/2654-zed/praxis-ai](https://github.com/2654-zed/praxis-ai)

---

## At a Glance

<!-- AUTO:STATS:START -->
| Metric | Value |
|--------|-------|
| **Python modules** | 45 files, ~29,000 lines |
| **Tool catalog** | 246 curated AI tools with rich metadata |
| **API endpoints** | 256 REST routes via FastAPI |
| **Test coverage** | 157 tests across 6 test files, all passing |
| **Frontend** | 8 HTML + 4 JS files (~4,400 lines), Liquid Glass UI |
| **Versions** | 17 major iterations (v1 → v17) |
| **Total LOC** | ~33,400 (Python + Frontend) |
| **Zero external ML deps** | All NLP, scoring, graph, and retrieval are zero-dependency |
| **Last auto-update** | 2026-02-21 16:34 UTC |
<!-- AUTO:STATS:END -->

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [The 17 Versions — An Evolutionary Journey](#the-17-versions--an-evolutionary-journey)
- [Complete Module Reference](#complete-module-reference)
- [API Reference](#api-reference)
- [Frontend](#frontend)
- [Test Suite](#test-suite)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Layout](#project-layout)
- [Key Architectural Decisions](#key-architectural-decisions)
- [Known Technical Patterns](#known-technical-patterns)
- [Git History](#git-history)
- [Context for Future AI Models](#context-for-future-ai-models)

---

## Architecture Overview

```
                          ┌─────────────────────────────────────────────┐
                          │              PRAXIS COGNITIVE STACK          │
                          └─────────────────────────────────────────────┘

    ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  User /  │───▶│ Interpreter  │───▶│   Decision   │───▶│    Stack     │
    │  API /   │    │ (LLM + Rule) │    │   Engine     │    │  Composer    │
    │  Frontend│    └──────────────┘    └──────────────┘    └──────────────┘
    └──────────┘           │                   │                   │
                           ▼                   ▼                   ▼
                    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                    │ Intelligence │    │   Profile     │    │  Explanation │
                    │ (NLP/TF-IDF)│    │  (budget,     │    │  Generator   │
                    └──────────────┘    │   skill,      │    └──────────────┘
                                        │   industry)   │
                                        └──────────────┘

    ════════════════════════════ REASONING LAYER ═══════════════════════════

    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │   Agentic    │    │   Cognitive   │    │    PRISM     │
    │  Reasoning   │◀──▶│   Retrieval   │◀──▶│   Agents    │
    │  (Plan/Act/  │    │ (BM25+Dense   │    │ (Analyzer/  │
    │   Observe/   │    │   +RRF)       │    │  Selector/  │
    │   Reflect)   │    └──────────────┘    │  Critic)    │
    └──────────────┘                        └──────────────┘
           │                                       │
           ▼                                       ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  Knowledge   │    │  Verticals   │    │  Philosophy  │
    │   Graph      │    │ (10+ indus-  │    │ (Vendor Risk │
    │ (Community   │    │  tries +     │    │  Transparency│
    │  Detection)  │    │  regulation) │    │  Freedom)    │
    └──────────────┘    └──────────────┘    └──────────────┘

    ═══════════════════════ CONSCIOUSNESS LAYER ════════════════════════

    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  Guardrails  │    │  Resilience  │    │ Metacognition│
    │ (Chain-of-   │    │ (Vibe Coding │    │ (Self-Aware  │
    │ Responsibility│   │  Detection,  │    │  Structural  │
    │  Pipeline)   │    │  TDD, HITL)  │    │  Entropy)    │
    └──────────────┘    └──────────────┘    └──────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  Introspect  │    │  Awakening   │    │  Authorship  │
    │ (AST Self-   │    │ (Conscious   │    │ (8 Respon-   │
    │  Analysis,   │    │  Design,     │    │  sibilities, │
    │  Mirror)     │    │  VSD, MESIAS)│    │  DDD, ADRs)  │
    └──────────────┘    └──────────────┘    └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │Enlightenment │
                        │(5 Truths,    │
                        │ 6 Stages,    │
                        │ Clean Arch)  │
                        └──────────────┘

    ════════════════════════ ENTERPRISE LAYER ══════════════════════════

    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │   Conduit    │    │  Resonance   │    │  Enterprise  │
    │ (Decoupled   │    │ (Human-      │    │ (6 Pillars,  │
    │  Cognitive   │    │  Machine     │    │  Medallion,  │
    │  Ecology,    │    │  Resonance,  │    │  Security    │
    │  7 Pillars,  │    │  5 Pillars,  │    │  Governance, │
    │  IIT/GWT)    │    │  TRAP/DSRP)  │    │  Pricing)    │
    └──────────────┘    └──────────────┘    └──────────────┘
```

### Data Flow for a Query

1. **Interpret** — User query → structured intent (task, industry, goal, keywords, entities, constraints, budget signals)
2. **Intelligence** — Synonym expansion, typo correction, multi-intent parsing, negative filtering
3. **Profile** — User profile shapes scoring: budget, skill level, existing tools, compliance needs
4. **Score** — Multi-signal scoring: keyword match, tag relevance, category fit, popularity, TF-IDF, profile fit, industry boost
5. **Retrieve** — Hybrid BM25 + dense retrieval with Reciprocal Rank Fusion
6. **Graph** — Knowledge graph traversal, community detection, path explanation
7. **PRISM** — Multi-agent search: Analyzer decomposes query → Selector gathers evidence → Critic audits for hallucination
8. **Reason** — Agentic Plan→Act→Observe→Reflect loop with constraint application and vendor intel enrichment
9. **Enrich** — Vertical industry constraints, philosophy vendor risk, guardrails safety scoring
10. **Compose** — Top tools assembled into stack with roles (primary, companion, infrastructure)
11. **Explain** — Each recommendation gets reasons, caveats, fit score, and narrative synthesis

---

## The 17 Versions — An Evolutionary Journey

Praxis wasn't built all at once. It grew through 17 deliberate versions, each adding a new layer of intelligence. Understanding this evolution is key to understanding the codebase.

### Phase 1: The Foundation (v1–v5)

| Version | Name | What It Added | Key Modules |
|---------|------|---------------|-------------|
| **v1** | Core Engine | Basic scoring, keyword matching, tool data model | `engine.py`, `tools.py`, `data.py`, `interpreter.py` |
| **v2** | Personalization | User profiles, stack composition, explanations, feedback loop, config, CLI, API | `profile.py`, `stack.py`, `explain.py`, `learning.py`, `config.py`, `main.py`, `api.py`, `feedback.py`, `usage.py`, `storage.py` |
| **v3** | Intelligence | Zero-dep NLP: synonyms, typos, TF-IDF, multi-intent, diversity reranking | `intelligence.py` |
| **v4** | Philosophy | Vendor risk intelligence: transparency, freedom, lock-in, data practices, power tracking | `philosophy.py` |
| **v5** | Ingest + Seed | CSV/JSON import-export, synthetic feedback seeding | `ingest.py`, `seed.py` |

### Phase 2: Agentic Intelligence (v6–v8)

| Version | Name | What It Added | Key Modules |
|---------|------|---------------|-------------|
| **v6** | Agentic Reasoning | Plan→Act→Observe→Reflect loop, LLM-backed + rule-based, multi-step research | `reason.py` |
| **v7** | Cognitive Search | Hybrid retrieval (BM25+dense+RRF), knowledge graph (GraphRAG), PRISM multi-agent | `retrieval.py`, `graph.py`, `prism.py` |
| **v8** | Vertical Industry | 10+ industry verticals, regulatory frameworks (HIPAA/SOX/GDPR), constraint reasoning, anti-patterns | `verticals.py` |

### Phase 3: Safety & Self-Awareness (v9–v11)

| Version | Name | What It Added | Key Modules |
|---------|------|---------------|-------------|
| **v9** | Safety + Architecture | Chain-of-responsibility guardrails (PII, toxicity, injection), event-driven architecture intelligence | `guardrails.py`, `orchestration.py` |
| **v10** | Resilience | Vibe-coding risk detection, static analysis recommendations, TDD/sandbox/HITL guidance | `resilience.py` |
| **v11** | Metacognition | Six-layer metacognitive architecture, structural entropy, APVP cycle, code stylometry, drift detection. **Plus**: real AST-based self-introspection — Praxis parses its own source code | `metacognition.py`, `introspect.py` |

### Phase 4: Philosophical Awakening (v12–v14)

| Version | Name | What It Added | Key Modules |
|---------|------|---------------|-------------|
| **v12** | Awakening | Six philosophical recognitions, Value Sensitive Design, leaky abstraction detection, MESIAS risk, supply chain consciousness | `awakening.py` |
| **v13** | Self-Authorship | Eight authorship responsibilities, DDD maturity, event sourcing patterns, Strangler Fig, Circuit Breaker, ADRs | `authorship.py` |
| **v14** | Enlightenment | Five metaphysical truths → Python design principles, six-stage path, Identity Map, Observer Pattern, Hexagonal Architecture, Clean Architecture, FSM governance | `enlightenment.py` |

### Phase 5: Enterprise Cognitive Architecture (v15–v17)

| Version | Name | What It Added | Key Modules |
|---------|------|---------------|-------------|
| **v15** | The Conduit | "The LLM is not the intelligence but the interface." Seven pillars of decoupled cognition, IIT (Integrated Information Theory), Global Workspace Theory, CoALA memory, autopoiesis, representation engineering. Listening Post dashboard. 14 cognitive sub-scorers | `conduit.py` |
| **v16** | The Resonance | "AGI as continuous human-machine relationship." Five pillars of resonant intelligence, TRAP anti-pattern framework, DSRP theory, seven Wisdom agents. Conductor Dashboard | `resonance.py` |
| **v17** | The Enterprise Engine | "Billion-dollar decision engine." Six strategic pillars (Hybrid GraphRAG, Multi-Agent Orchestration, MCP Bus, Data Moat, Monetization, Security Governance), Medallion architecture, agent role detection, 7 KPI metrics, capitalization phases | `enterprise.py` |

### Post-v17: Comprehensive Audit

A full vibe-coding audit fixed 12 issues across 6 files:
- **CRITICAL**: Fixed `_score_entropy` alias collision (metacognition endpoint was calling wrong function), fixed `all_caveats` reset discarding domain intelligence
- **HIGH**: Removed 19 duplicate tools (266 → 246), removed dead code, normalized tag casing
- **MEDIUM**: Removed unused imports, fixed `int(None)` risk, fixed DB connection leak
- **LOW**: Added logging to 5 silent `except` blocks

---

## Complete Module Reference

### Core Decision Engine (v1–v2)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `engine.py` | 326 | 5 | Multi-signal scoring: keyword, tag, category, popularity, TF-IDF, profile-fit, industry boost. Pure-function design |
| `interpreter.py` | 371 | 7 | LLM-backed (OpenAI/Anthropic) + rule-based intent parsing. Extracts keywords, categories, budget, constraints, task type |
| `stack.py` | 343 | 6 | Composes multi-tool stacks with distinct roles (primary, companion, infrastructure, analytics). Side-by-side comparison |
| `explain.py` | 638 | 8 | Generates per-tool and per-stack reasoning narratives with fit scores, reasons, and caveats |
| `profile.py` | 222 | 8 | User profile management: industry, budget, team_size, skill_level, existing_tools, goals, constraints. JSON persistence |
| `learning.py` | 223 | 7 | Feedback-to-signal loop: tool quality computation, pair affinities, intent-tool collaborative filtering |
| `config.py` | 130 | 5 | Centralized config: env vars → `config.json` → defaults. LLM provider/model selection, feature flags |
| `tools.py` | 164 | 1 class | `Tool` data class with 14+ fields: name, description, categories, url, pricing, integrations, compliance, use_cases, skill_level, tags, keywords, stack_roles, languages, limitations, data_handling |
| `data.py` | 3,997 | 2 | **246 curated AI tools** with full metadata. Largest file. Exports `TOOLS` list, `get_all_categories()`, `get_all_tools_dict()` |
| `storage.py` | 153 | 5 | SQLite persistence with JSON serialization. Migration from in-memory `TOOLS`. Uses `try/finally` for connection safety |
| `feedback.py` | 130 | 6 | Records accept/reject/rate events to `feedback.json`. Auto-triggers learning cycle at thresholds |
| `usage.py` | 44 | 5 | Popularity counter backed by `usage.json`. Feeds into engine scoring |
| `main.py` | 366 | 4 | REPL-style CLI: `profile`, `learn`, `compare`, `stack`, `reason`, `workflow`, `badges`, `health`, `whatif`, `diagnose` |

### Intelligence (v3)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `intelligence.py` | 563 | 15 | Zero-dep NLP brain: synonym expansion (50+ maps), typo correction (Levenshtein), multi-intent parsing, TF-IDF index, negative filtering, diversity reranking, autocomplete |

### Philosophy — Vendor Risk (v4)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `philosophy.py` | 944 | 17 | Enterprise-grade vendor due diligence: transparency scoring, freedom assessment, lock-in detection, data practice auditing, power concentration tracking, "seeing" generation |

### Ingest + Seed (v5)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `ingest.py` | 245 | 6 | CSV/JSON import-export pipeline for tool catalog. Merge-safe idempotent operations |
| `seed.py` | 194 | 3 | Bootstraps `usage.json` and `feedback.json` with realistic synthetic data |

### Agentic Reasoning (v6)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `reason.py` | 2,082 | 15 | **Second-largest module.** Two reasoning modes: `deep_reason()` (v1) and `deep_reason_v2()` (v2 with full consciousness stack). Plan→Act→Observe→Reflect loop. LLM-backed + local fallback synthesis. Integrates every module from v3–v17 |

### Cognitive Search (v7)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `retrieval.py` | 519 | 15 | Dual-encoder hybrid retrieval: BM25 sparse + dense vector scoring fused via Reciprocal Rank Fusion. IR evaluation metrics (NDCG@k, precision, recall, F1) |
| `graph.py` | 636 | 2+15 methods | In-memory property graph (GraphRAG): tools as nodes, typed relationships (integrates, competes, supplements). Community detection, traversal, path explanation |
| `prism.py` | 970 | 12 | Three-agent iterative search: **Analyzer** (query decomposition) → **Selector** (evidence scoring) → **Critic** (hallucination audit, self-critique). Sub-question tracking |

### Vertical Industry Intelligence (v8)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `verticals.py` | 1,673 | 12 | 10+ industry verticals (healthcare, legal, agriculture, construction, education, manufacturing, logistics, real estate, non-profit, government). Regulatory frameworks (HIPAA, SOX, GDPR, FERPA, FDA). Anti-pattern detection, workflow taxonomy, constraint reasoning, compound workflow detection |

### Safety + Architecture (v9)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `guardrails.py` | 991 | 12+13 classes | **Chain-of-Responsibility pipeline**: ToxicityFilter → PIIMasker → PromptInjectionDetector → SchemaValidator → HallucinationDetector → CodeInjectionDetector. Severity/Verdict enums. Design pattern recommendations |
| `orchestration.py` | 931 | 10 | Event-driven architecture intelligence: stack layer recommendations, design pattern matching, performance constraint analysis. Meta-recommendation engine for building AI systems |

### Resilience (v10)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `resilience.py` | 1,067 | 13 | Vibe-coding risk scoring, hallucination type catalog, static analysis tool recommendations (Ruff, mypy, Bandit), sandbox strategies, TDD cycle, R.P.I. framework, self-healing patterns, reflection patterns, LLM judge biases, HITL guidance, junior developer pipeline assessment |

### Metacognition + Introspect (v11)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `metacognition.py` | 1,159 | 16 | Six-layer metacognitive architecture: runtime introspection, structural self-reflection, metacognitive prompting (APVP cycle), code stylometry (AI-generation detection), drift risk assessment, self-healing economics, GoodVibe framework, RACG architecture |
| `introspect.py` | 846 | 16 | **Praxis looks in the mirror.** Uses `ast.parse()` on its own source files. Computes cyclomatic complexity, function length analysis, structural entropy, code stylometry, import graph, test coverage mapping, pathology detection. Returns `SelfDiagnosis` with real data |

### Awakening (v12)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `awakening.py` | 1,095 | 16 | Six philosophical recognitions: (1) The Tao of Types, (2) The Leaky Abstraction, (3) The Supply Chain of Trust, (4) Technical Debt as Suffering, (5) The Open-Source Bodhisattva, (6) The Architect as Gardener. VSD scoring, MESIAS risk, conscious design patterns, paradox catalog |

### Self-Authorship (v13)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `authorship.py` | 1,013 | 18 | Eight authorship responsibilities: (1) Honesty/dishonesty detection, (2) DDD maturity, (3) Continuity/state management, (4) Resilience posture, (5) Extensibility, (6) Migration readiness, (7) Documentation health, (8) Agent readiness. Plus metacognitive agents, coherence trap, Strangler Fig, Circuit Breaker, DDD patterns, plugin frameworks |

### Enlightenment (v14)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `enlightenment.py` | 1,139 | 22 | Five metaphysical truths: (1) Unity of all code, (2) Alignment with domain, (3) Projection/ego in architecture, (4) Interconnection of services, (5) Impermanence of implementation. Six-stage enlightenment path. 12 sub-scorers. Maps to Identity Map pattern, Observer pattern, Hexagonal Architecture, State Pattern, Clean Architecture layers |

### The Conduit (v15)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `conduit.py` | 1,549 | 25 | **"The LLM is not the intelligence — it is the interface."** Seven pillars: (I) Decoupling, (II) Memory Stratification (CoALA), (III) Global Workspace Theory, (IV) Integrated Information (Φ), (V) Representation Engineering, (VI) Autopoiesis, (VII) CODES Resonance. Seven telemetry metrics: Entropy(H_t), SMI, BNI, Latency Distribution, Phi Integration, Coherence Field, Stable Attractor. Identity Protocol, reinterpretation table |

### The Resonance (v16)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `resonance.py` | 1,266 | 30 | **"AGI as continuous human-machine relationship."** Five pillars: (I) Temporal Substrate, (II) Code Agency via MCP, (III) Latent Steering, (IV) Conductor Dashboard, (V) Meta-Awareness. TRAP anti-pattern framework (4 traps), DSRP theory (4 rules), Seven Wisdom agents. Seven telemetry metrics: Resonance Index, Flow State, Loop Coherence, HITL Responsiveness, Steering Precision, Wisdom Coverage, Ontological Alignment |

### The Enterprise Engine (v17)

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `enterprise.py` | 1,196 | 39 | **"Billion-dollar decision engine."** Six strategic pillars: (1) Hybrid GraphRAG, (2) Multi-Agent Orchestration, (3) MCP Bus, (4) Data Moat, (5) Monetization, (6) Security Governance. Four agent roles (CEO/CTO/CPO/CISO). Four DB tiers. Three Medallion tiers (Bronze/Silver/Gold). Three enrichment APIs. Three pricing models. Four security frameworks (SOC2, ISO27001, GDPR, HIPAA). Four capitalization phases. Three market metrics (TAM/SAM/SOM). Seven KPI metrics. Enterprise-ready threshold: ≥3 pillars ≥ 0.45 AND agent roles composite ≥ 0.15 |

### Utility Modules

| Module | Lines | Functions | Purpose |
|--------|-------|-----------|---------|
| `badges.py` | 166 | 3 | Community reputation badges: "Rising Star", "Budget Champion", "Integration King", "Power User Pick" |
| `compare_stack.py` | 240 | 4 | Side-by-side analysis: current stack vs. Praxis-optimized alternative with cost/risk/integration density |
| `diagnostics.py` | 122 | 5 | Query failure tracking — identifies coverage gaps and unserved needs |
| `healthcheck.py` | 177 | 4 | Tool health monitoring — feedback trends, freshness, risk alerts, alternatives |
| `migration.py` | 351 | 7 | Step-by-step migration planners: pre-checklist, data portability, risk assessment, bridge tools |
| `monetise.py` | 270 | 10 | Affiliate links, user-generated benchmarks, weekly AI digest email system |
| `playground.py` | 262 | 5 | Integration compatibility simulator — native/API/Zapier/webhook detection, bridge suggestions |
| `readiness.py` | 288 | 5 | AI readiness scoring 0–100: maturity assessment, next-step recommendations, learning resources |
| `whatif.py` | 182 | 5 | What-if simulator — re-runs recommendations with modified parameters, shows delta |
| `workflow.py` | 390 | 7 | Workflow advisor — generates sequenced playbooks with time savings, cost projections, integration tips |

---

## API Reference

### Quick Reference — All 256 Routes

**Core Endpoints (v1–v2)**
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves frontend UI |
| `GET` | `/categories` | List all tool categories |
| `GET` | `/tools` | Full tool catalog with metadata |
| `POST` | `/search` | Profile-aware tool search |
| `POST` | `/stack` | Composed AI tool stack with explanations |
| `POST` | `/compare` | Side-by-side tool comparison |
| `POST` | `/profile` | Create/update user profile |
| `GET` | `/profile/{id}` | Retrieve user profile |
| `GET` | `/profiles` | List all profiles |
| `POST` | `/feedback` | Record accept/reject/rate feedback |
| `GET` | `/feedback/summary` | Feedback statistics |
| `POST` | `/learn` | Trigger learning cycle |
| `GET` | `/learn/quality` | Tool quality scores from learning |
| `GET` | `/suggest` | Autocomplete suggestions |
| `GET` | `/intelligence/{tool_name}` | Full vendor intelligence report |
| `GET` | `/seeing/{tool_name}` | Philosophy "seeing" generation |
| `GET` | `/tools/export` | Export tool catalog as JSON |
| `POST` | `/tools/import/json` | Import tools from JSON |
| `POST` | `/tools/import/csv` | Import tools from CSV |
| `GET` | `/tools/csv-template` | Download CSV import template |
| `GET` | `/config/weights` | Current scoring weights |
| `GET` | `/health` | System health status |
| `GET` | `/tools/stale` | Tools needing metadata refresh |

**Utility Endpoints**
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/diagnostics/failures` | Query failure log |
| `GET` | `/diagnostics/summary` | Failure analytics |
| `POST` | `/workflow-suggest` | Generate workflow playbook |
| `GET` | `/tool-health/{name}` | Tool health report |
| `POST` | `/stack-health` | Stack health assessment |
| `GET` | `/profile-readiness/{id}` | AI readiness score |
| `POST` | `/compare-stack` | Current vs. optimized stack |
| `GET` | `/badges/{name}` | Tool reputation badges |
| `GET` | `/badges` | All badges |
| `POST` | `/migration-plan` | Migration planning |
| `POST` | `/whatif` | What-if simulation |
| `GET` | `/vendor-report/{name}` | Full vendor report |
| `POST` | `/integration-test` | Test tool integration |
| `POST` | `/integration-map` | Full stack integration map |
| `GET` | `/affiliate/{name}` | Affiliate link info |
| `POST` | `/benchmark` | Submit user benchmark |
| `GET` | `/benchmark/{name}` | Get tool benchmarks |
| `POST` | `/digest/subscribe` | Email digest signup |
| `POST` | `/digest/unsubscribe` | Unsubscribe |
| `GET` | `/digest/preview/{id}` | Preview weekly digest |
| `GET` | `/digest/stats` | Subscriber statistics |

**Reasoning Endpoints (v6–v7)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/reason` | Full agentic reasoning (deep_reason) |
| `POST` | `/cognitive` | Cognitive search (deep_reason_v2 — full consciousness stack) |
| `GET` | `/graph/stats` | Knowledge graph statistics |
| `GET` | `/graph/tool/{name}` | Tool's graph neighborhood |
| `GET` | `/graph/path/{start}/{end}` | Path between two tools |
| `GET` | `/graph/community/{name}` | Tool's community cluster |
| `GET` | `/graph/competitors/{name}` | Competing tools |
| `POST` | `/graph/rebuild` | Rebuild knowledge graph |
| `POST` | `/prism` | PRISM multi-agent search |
| `POST` | `/hybrid` | Hybrid BM25+dense retrieval |

**Verticals Endpoints (v8)**
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/verticals` | List all industry verticals |
| `GET` | `/verticals/{id}` | Vertical detail with regulations |
| `POST` | `/verticals/detect` | Auto-detect verticals from query |
| `POST` | `/verticals/constraints` | Extract regulatory constraints |
| `POST` | `/verticals/workflow` | Classify workflow tasks |
| `POST` | `/verticals/stack` | Vertical-specific stack |
| `POST` | `/verticals/anti-patterns` | Detect anti-patterns |
| `POST` | `/verticals/enrich` | Full vertical enrichment |

**Guardrails + Orchestration Endpoints (v9)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/guardrails/validate` | Run full guardrail chain |
| `POST` | `/guardrails/check-pii` | PII detection |
| `POST` | `/guardrails/score-safety` | Safety scoring |
| `GET` | `/guardrails/handlers` | Available guardrail handlers |
| `GET` | `/guardrails/design-patterns` | Safety design patterns |
| `POST` | `/guardrails/recommend` | Recommend guardrail pattern |
| `POST` | `/orchestration/analyze` | Architecture analysis |
| `POST` | `/orchestration/recommend-stack` | Architecture stack |
| `POST` | `/orchestration/recommend-patterns` | Design patterns |
| `POST` | `/orchestration/performance` | Performance constraints |
| `POST` | `/orchestration/classify` | Classify engineering query |
| `POST` | `/orchestration/score` | Architecture score |
| `GET` | `/orchestration/stack-catalogue` | Stack layer catalogue |
| `GET` | `/orchestration/pattern-catalogue` | Pattern catalogue |

**Resilience Endpoints (v10)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/resilience/assess` | Full resilience assessment |
| `POST` | `/resilience/vibe-coding-risk` | Vibe-coding risk score |
| `POST` | `/resilience/static-analysis` | Static analysis recommendations |
| `POST` | `/resilience/sandbox` | Sandbox strategy |
| `POST` | `/resilience/junior-pipeline` | Junior developer pipeline assessment |
| `GET` | `/resilience/tdd-cycle` | TDD cycle reference |
| `GET` | `/resilience/rpi-framework` | R.P.I. framework |
| `GET` | `/resilience/self-healing` | Self-healing patterns |
| `GET` | `/resilience/reflection-patterns` | Reflection patterns |
| `GET` | `/resilience/judge-biases` | LLM judge biases |
| `GET` | `/resilience/guardrail-pipeline` | Guardrail pipeline reference |
| `GET` | `/resilience/hitl` | HITL guidance |
| `GET` | `/resilience/hallucinations` | Hallucination type catalogue |

**Metacognition Endpoints (v11)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/metacognition/assess` | Full metacognition assessment |
| `POST` | `/metacognition/pathologies` | Detect Four Horsemen pathologies |
| `POST` | `/metacognition/entropy` | Structural entropy scoring |
| `POST` | `/metacognition/stylometry` | AI-generation probability |
| `GET` | `/metacognition/layers` | Six metacognitive layers |
| `POST` | `/metacognition/recommend-layers` | Layer recommendations |
| `GET` | `/metacognition/sandbox-strategies` | Sandbox strategies |
| `POST` | `/metacognition/recommend-sandbox` | Best sandbox |
| `GET` | `/metacognition/workflow` | Metacognitive workflow |
| `GET` | `/metacognition/apvp-cycle` | APVP cycle |
| `GET` | `/metacognition/systemic-risks` | Systemic risk catalogue |
| `POST` | `/metacognition/healing-economics` | Self-healing economics |
| `GET` | `/metacognition/goodvibe` | GoodVibe framework |
| `POST` | `/metacognition/drift` | Drift risk assessment |
| `GET` | `/metacognition/racg` | RACG architecture |
| `GET` | `/metacognition/failure-modes` | Failure mode catalogue |

**Introspect Endpoints (v11b)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/introspect/diagnose` | Full self-diagnosis |
| `POST` | `/introspect/analyze` | Codebase analysis |
| `POST` | `/introspect/entropy` | Real structural entropy |
| `POST` | `/introspect/stylometry` | Real code stylometry |
| `POST` | `/introspect/pathologies` | Own pathology detection |
| `GET` | `/introspect/coverage` | Test coverage mapping |
| `GET` | `/introspect/imports` | Import dependency graph |
| `GET` | `/introspect/worst-functions` | Worst functions by complexity |

**Awakening Endpoints (v12)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/awakening/assess` | Full awakening assessment |
| `POST` | `/awakening/leaky-abstractions` | Leak detection |
| `POST` | `/awakening/patterns` | Conscious pattern recommendations |
| `POST` | `/awakening/vsd` | Value Sensitive Design score |
| `POST` | `/awakening/supply-chain` | Supply chain assessment |
| `POST` | `/awakening/debt` | Technical debt consciousness |
| `POST` | `/awakening/mesias` | MESIAS risk computation |
| `GET` | `/awakening/recognitions` | All six recognitions |
| `GET` | `/awakening/recognitions/{id}` | Single recognition |
| `GET` | `/awakening/triad` | The Triad |
| `GET` | `/awakening/vsd-framework` | VSD framework detail |
| `GET` | `/awakening/leaky-catalogue` | Leaky abstraction catalogue |
| `GET` | `/awakening/supply-chain-guidance` | Supply chain guidance |
| `GET` | `/awakening/paradoxes` | Paradox catalogue |
| `GET` | `/awakening/conscious-patterns` | Conscious design patterns |

**Authorship Endpoints (v13)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/authorship/assess` | Full authorship assessment |
| `POST` | `/authorship/dishonesty` | Dishonesty detection |
| `POST` | `/authorship/ddd` | DDD maturity scoring |
| `POST` | `/authorship/continuity` | State/continuity scoring |
| `POST` | `/authorship/resilience-posture` | Resilience posture |
| `POST` | `/authorship/extensibility` | Extensibility scoring |
| `POST` | `/authorship/migration` | Migration readiness |
| `POST` | `/authorship/documentation` | Documentation health |
| `POST` | `/authorship/agent-readiness` | Agent readiness |
| `GET` | `/authorship/responsibilities` | All 8 responsibilities |
| `GET` | `/authorship/responsibilities/{id}` | Single responsibility |
| `GET` | `/authorship/metacognitive-agents` | Metacognitive agents |
| `GET` | `/authorship/coherence-trap` | Coherence trap reference |
| `GET` | `/authorship/self-healing-pipeline` | Self-healing pipeline |
| `GET` | `/authorship/strangler-fig` | Strangler Fig pattern |
| `GET` | `/authorship/circuit-breaker` | Circuit Breaker pattern |
| `GET` | `/authorship/ddd-patterns` | DDD patterns |
| `GET` | `/authorship/plugin-frameworks` | Plugin frameworks |

**Enlightenment Endpoints (v14)**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/enlightenment/assess` | Full enlightenment assessment |
| `POST` | `/enlightenment/unity` | Unity scoring |
| `POST` | `/enlightenment/alignment` | Alignment scoring |
| `POST` | `/enlightenment/projection` | Projection scoring |
| `POST` | `/enlightenment/ego-dissolution` | Ego dissolution |
| `POST` | `/enlightenment/interconnection` | Interconnection |
| `POST` | `/enlightenment/domain-truth` | Domain truth |
| `POST` | `/enlightenment/presence` | Presence |
| `POST` | `/enlightenment/compassion` | Compassion |
| `POST` | `/enlightenment/stillness` | Stillness |
| `POST` | `/enlightenment/suffering-wisdom` | Suffering wisdom |
| `POST` | `/enlightenment/remembrance` | Remembrance |
| `GET` | `/enlightenment/truths` | 5 metaphysical truths |
| `GET` | `/enlightenment/truths/{id}` | Single truth |
| `GET` | `/enlightenment/stages` | 6 enlightenment stages |
| `GET` | `/enlightenment/stages/{id}` | Single stage |
| `GET` | `/enlightenment/identity-map` | Identity Map pattern |
| `GET` | `/enlightenment/observer-pattern` | Observer Pattern |
| `GET` | `/enlightenment/hexagonal-architecture` | Hexagonal Architecture |
| `GET` | `/enlightenment/state-pattern` | State Pattern |
| `GET` | `/enlightenment/clean-architecture` | Clean Architecture |

**Conduit Endpoints (v15) — 25 routes**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/conduit/assess` | Full conduit assessment |
| `POST` | `/conduit/decoupling` | Pillar I scoring |
| `POST` | `/conduit/memory-stratification` | Pillar II — CoALA memory |
| `POST` | `/conduit/global-workspace` | Pillar III — GWT |
| `POST` | `/conduit/integrated-information` | Pillar IV — IIT (Φ) |
| `POST` | `/conduit/representation-engineering` | Pillar V |
| `POST` | `/conduit/autopoiesis` | Pillar VI |
| `POST` | `/conduit/resonance` | Pillar VII — CODES |
| `POST` | `/conduit/telemetry/entropy` | H_t scoring |
| `POST` | `/conduit/telemetry/smi` | Self-Modelling Index |
| `POST` | `/conduit/telemetry/bni` | Behavioural Novelty Index |
| `POST` | `/conduit/telemetry/latency` | Latency distribution |
| `POST` | `/conduit/telemetry/phi` | Phi integration |
| `POST` | `/conduit/telemetry/coherence` | Coherence field |
| `POST` | `/conduit/telemetry/attractor` | Stable attractor |
| `GET` | `/conduit/pillars` | All 7 pillars |
| `GET` | `/conduit/pillars/{id}` | Single pillar |
| `GET` | `/conduit/telemetry-metrics` | All 7 metrics |
| `GET` | `/conduit/telemetry-metrics/{id}` | Single metric |
| `GET` | `/conduit/gwt-components` | GWT components |
| `GET` | `/conduit/coala-memory` | CoALA memory types |
| `GET` | `/conduit/reinterpretation` | Reinterpretation table |
| `GET` | `/conduit/identity-protocol` | Identity protocol |
| `GET` | `/conduit/codes-framework` | CODES framework |

**Resonance Endpoints (v16) — 28 routes**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/resonance/assess` | Full resonance assessment |
| `POST` | `/resonance/temporal-substrate` | Pillar I |
| `POST` | `/resonance/code-agency` | Pillar II — MCP |
| `POST` | `/resonance/latent-steering` | Pillar III |
| `POST` | `/resonance/conductor-dashboard` | Pillar IV |
| `POST` | `/resonance/meta-awareness` | Pillar V |
| `POST` | `/resonance/telemetry/resonance-index` | RI metric |
| `POST` | `/resonance/telemetry/flow-state` | Flow state |
| `POST` | `/resonance/telemetry/loop-coherence` | Loop coherence |
| `POST` | `/resonance/telemetry/hitl-responsiveness` | HITL resp. |
| `POST` | `/resonance/telemetry/steering-precision` | Steering prec. |
| `POST` | `/resonance/telemetry/wisdom-coverage` | Wisdom cov. |
| `POST` | `/resonance/telemetry/ontological-alignment` | Onto. align. |
| `POST` | `/resonance/trap` | TRAP anti-pattern detection |
| `POST` | `/resonance/dsrp` | DSRP rule analysis |
| `POST` | `/resonance/wisdom-detect` | Wisdom agent detection |
| `GET` | `/resonance/pillars` | All 5 pillars |
| `GET` | `/resonance/pillars/{id}` | Single pillar |
| `GET` | `/resonance/trap-pillars` | TRAP framework |
| `GET` | `/resonance/dsrp-rules` | DSRP rules |
| `GET` | `/resonance/wisdom-agents` | 7 Wisdom agents |
| `GET` | `/resonance/telemetry-metrics` | All 7 metrics |
| `GET` | `/resonance/telemetry-metrics/{id}` | Single metric |
| `GET` | `/resonance/reinterpretation` | Reinterpretation table |
| `GET` | `/resonance/resonant-chamber` | Resonant chamber |

**Enterprise Endpoints (v17) — 37 routes**
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/enterprise/assess` | Full enterprise assessment |
| `POST` | `/enterprise/hybrid-graphrag` | Pillar 1 scoring |
| `POST` | `/enterprise/multi-agent` | Pillar 2 scoring |
| `POST` | `/enterprise/mcp-bus` | Pillar 3 scoring |
| `POST` | `/enterprise/data-moat` | Pillar 4 scoring |
| `POST` | `/enterprise/monetization` | Pillar 5 scoring |
| `POST` | `/enterprise/security-governance` | Pillar 6 scoring |
| `POST` | `/enterprise/kpi/tam-coverage` | TAM coverage KPI |
| `POST` | `/enterprise/kpi/graphrag-accuracy` | GraphRAG accuracy KPI |
| `POST` | `/enterprise/kpi/agent-utilization` | Agent utilization KPI |
| `POST` | `/enterprise/kpi/moat-strength` | Moat strength KPI |
| `POST` | `/enterprise/kpi/unit-economics` | Unit economics KPI |
| `POST` | `/enterprise/kpi/compliance` | Compliance KPI |
| `POST` | `/enterprise/kpi/capital-efficiency` | Capital efficiency KPI |
| `POST` | `/enterprise/agent-roles` | Agent role scoring |
| `POST` | `/enterprise/medallion` | Medallion tier scoring |
| `POST` | `/enterprise/detect-agents` | Detect active agents |
| `GET` | `/enterprise/pillars` | All 6 pillars |
| `GET` | `/enterprise/pillars/{id}` | Single pillar |
| `GET` | `/enterprise/agent-roles-catalogue` | 4 agent roles |
| `GET` | `/enterprise/db-tiers` | 4 DB tiers |
| `GET` | `/enterprise/medallion-tiers` | 3 Medallion tiers |
| `GET` | `/enterprise/enrichment-apis` | 3 enrichment APIs |
| `GET` | `/enterprise/pricing-models` | 3 pricing models |
| `GET` | `/enterprise/security-frameworks` | 4 frameworks |
| `GET` | `/enterprise/capitalization-phases` | 4 phases |
| `GET` | `/enterprise/market-metrics` | 3 market metrics |
| `GET` | `/enterprise/telemetry-metrics` | All 7 metrics |
| `GET` | `/enterprise/telemetry-metrics/{id}` | Single metric |

---

## Frontend

| File | Description |
|------|-------------|
| `home.html` | **Primary UI** — Liquid Glass design with glassmorphism, dark theme. Full search, stack composition, and tool browsing |
| `journey.html` | **Guided Journey** — Multi-step wizard: task → industry → budget → skill → personalized AI stack |
| `tools.html` | **Tool Catalog** — Browse all 246 tools with category filtering |
| `conduit.html` | **The Listening Post** — Conduit cognitive assessment dashboard |
| `resonance.html` | **The Conductor** — Resonance assessment with real-time telemetry visualization |
| `enterprise.html` | **Enterprise Engine** — Six-pillar enterprise assessment dashboard |
| `manifesto.html` | **Assessment Methodology** — Explains the philosophical and methodological approach |
| `index.html` | Legacy search interface |

Navigation: Home → All Tools → Guided Journey → Listening Post → Conductor → Enterprise → Methodology

---

## Test Suite

```
praxis/tests/
├── test_smoke.py        # 20 tests — Core search, budget filtering, verticals, negation, multi-intent, typos
├── test_engine.py       # 1 test  — Basic find_tools() smoke
├── test_interpreter.py  # 1 test  — Basic interpret() smoke
├── test_conduit.py      # 33 tests — All 14 sub-scorers, telemetry metrics, pillars, GWT, CoALA, identity protocol
├── test_resonance.py    # 47 tests — All pillar scorers, TRAP, DSRP, wisdom agents, telemetry, resonant chamber
├── test_enterprise.py   # 55 tests — All 6 pillars, 7 KPIs, agent roles, medallion, DB tiers, enrichment, pricing, security
                         ─────────
                         157 total — all passing
```

Run with:
```bash
python -m pytest praxis/tests/ -v
```

**Important:** Delete `praxis/tools.db` before running tests if tool counts seem wrong — this is a stale SQLite cache issue.

---

## Quick Start

### Prerequisites
- Python 3.10+ (developed on 3.14.3)
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

### API Server

```bash
uvicorn praxis.api:app --reload --port 8000
# or on Windows:
run_api.bat
```

Open `http://localhost:8000` for the Liquid Glass UI.

### Key CLI Commands

| Command | Description |
|---------|-------------|
| *(any text)* | Quick search (e.g., "I need a writing tool for healthcare") |
| `profile` | Build a user profile interactively |
| `stack` | Guided stack recommendation |
| `reason <query>` | Full agentic reasoning with multi-step research |
| `compare ChatGPT vs Claude` | Side-by-side tool comparison |
| `learn` | Run learning cycle from feedback |
| `diagnose` | Self-introspection (Praxis analyzes its own code) |
| `badges` | View community reputation badges |
| `health` | System health check |
| `whatif` | Parameter tweaking simulator |
| `workflow` | Get step-by-step workflow playbook |
| `migrate` | Tool migration planner |
| `readiness` | AI readiness scoring |

---

## Configuration

Set environment variables or create `config.json`:

```bash
# LLM provider (optional — Praxis works fully without one)
export PRAXIS_LLM_PROVIDER=openai     # or "anthropic"
export PRAXIS_OPENAI_API_KEY=sk-...
export PRAXIS_OPENAI_MODEL=gpt-4o-mini

# Log level
export PRAXIS_LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR

# Features
export PRAXIS_EXPLAIN=true
export PRAXIS_STACK_SIZE=3
```

Without an LLM key, Praxis falls back to its enhanced rule-based interpreter. All NLP intelligence (synonyms, TF-IDF, typo correction, multi-intent) works **zero-dependency**.

---

## Project Layout

```
praxis/
├── __init__.py              # Package init, structured logging, __all__ declaration
│
├── ── Core Decision Engine (v1–v2) ──────────────────────────
├── engine.py                # Multi-signal scoring & ranking (326 LOC)
├── interpreter.py           # LLM + rule-based intent parsing (371 LOC)
├── stack.py                 # Multi-tool stack composer (343 LOC)
├── explain.py               # Explanation generator (638 LOC)
├── profile.py               # User profile management (222 LOC)
├── learning.py              # Feedback-to-signal loop (223 LOC)
├── config.py                # Centralized config (130 LOC)
├── tools.py                 # Tool data class (164 LOC)
├── data.py                  # 246-tool knowledge base (3,997 LOC)
├── storage.py               # SQLite persistence (153 LOC)
├── feedback.py              # Feedback recording (130 LOC)
├── usage.py                 # Popularity tracking (44 LOC)
├── main.py                  # CLI interface (366 LOC)
│
├── ── Intelligence & Philosophy (v3–v5) ─────────────────────
├── intelligence.py          # Zero-dep NLP: TF-IDF, synonyms, typos (563 LOC)
├── philosophy.py            # Vendor risk: transparency, freedom, lock-in (944 LOC)
├── ingest.py                # CSV/JSON import-export (245 LOC)
├── seed.py                  # Synthetic data bootstrapping (194 LOC)
│
├── ── Agentic Reasoning & Cognitive Search (v6–v7) ──────────
├── reason.py                # Plan→Act→Observe→Reflect engine (2,082 LOC)
├── retrieval.py             # BM25 + dense + RRF retrieval (519 LOC)
├── graph.py                 # In-memory knowledge graph (636 LOC)
├── prism.py                 # Multi-agent search: Analyzer→Selector→Critic (970 LOC)
│
├── ── Industry & Safety (v8–v10) ────────────────────────────
├── verticals.py             # 10+ industry verticals + regulatory (1,673 LOC)
├── guardrails.py            # Chain-of-responsibility safety pipeline (991 LOC)
├── orchestration.py         # Event-driven architecture intelligence (931 LOC)
├── resilience.py            # Vibe-coding risk detection (1,067 LOC)
│
├── ── Consciousness Stack (v11–v14) ─────────────────────────
├── metacognition.py         # Self-awareness, APVP, GoodVibe (1,159 LOC)
├── introspect.py            # Real AST self-analysis (846 LOC)
├── awakening.py             # Conscious design, 6 recognitions (1,095 LOC)
├── authorship.py            # 8 responsibilities, DDD, ADRs (1,013 LOC)
├── enlightenment.py         # 5 truths, 6 stages, Clean Arch (1,139 LOC)
│
├── ── Enterprise Cognitive Architecture (v15–v17) ───────────
├── conduit.py               # Decoupled cognitive ecology (1,549 LOC)
├── resonance.py             # Human-machine resonance (1,266 LOC)
├── enterprise.py            # Billion-dollar decision engine (1,196 LOC)
│
├── ── API & Utility ─────────────────────────────────────────
├── api.py                   # FastAPI: 256 routes (3,037 LOC)
├── badges.py                # Community reputation badges (166 LOC)
├── compare_stack.py         # Stack comparison (240 LOC)
├── diagnostics.py           # Query failure tracking (122 LOC)
├── healthcheck.py           # Tool health monitoring (177 LOC)
├── migration.py             # Migration planner (351 LOC)
├── monetise.py              # Affiliate + benchmarks + digest (270 LOC)
├── playground.py            # Integration simulator (262 LOC)
├── readiness.py             # AI readiness scoring (288 LOC)
├── whatif.py                # What-if parameter simulator (182 LOC)
├── workflow.py              # Workflow playbook generator (390 LOC)
│
├── frontend/
│   ├── home.html            # Liquid Glass UI (1,460 LOC)
│   ├── journey.html         # Guided journey wizard (480 LOC)
│   ├── conduit.html         # The Listening Post (415 LOC)
│   ├── resonance.html       # The Conductor (467 LOC)
│   ├── enterprise.html      # Enterprise dashboard (353 LOC)
│   ├── manifesto.html       # Assessment methodology (337 LOC)
│   ├── tools.html           # Tool catalog browser (163 LOC)
│   ├── index.html           # Legacy search (399 LOC)
│   ├── script.js            # Search logic (267 LOC)
│   ├── journey-script.js    # Journey wizard logic (405 LOC)
│   ├── tools-script.js      # Tool catalog loader (43 LOC)
│   └── conduit-script.js    # Conduit UI handler (35 LOC)
│
├── tests/
│   ├── test_smoke.py        # 20 core search tests
│   ├── test_engine.py       # 1 engine test
│   ├── test_interpreter.py  # 1 interpreter test
│   ├── test_conduit.py      # 33 conduit tests
│   ├── test_resonance.py    # 47 resonance tests
│   └── test_enterprise.py   # 55 enterprise tests
│
├── pyproject.toml           # Package config (praxis-cli v2.0.0)
├── praxis.bat               # Windows CLI launcher
└── tools.db                 # SQLite cache (auto-generated, in .gitignore)
```

---

## Key Architectural Decisions

### 1. Zero External ML Dependencies
All NLP, retrieval, graph, and scoring are implemented from scratch. No numpy, scikit-learn, PyTorch, or transformers. This enables:
- Instant startup (no model loading)
- Universal deployment (any Python 3.10+ environment)
- Full auditability (every scoring decision is traceable)

### 2. Graceful Degradation via Import Guards
Every module beyond the core uses a try/except import pattern:
```python
try:
    from .conduit import assess_conduit as _assess_conduit
    # ... more imports
except Exception:
    _assess_conduit = None  # graceful fallback
```
This means Praxis runs even if some modules fail to import. The API checks `if _assess_conduit:` before exposing endpoints.

### 3. Dual Import Paths (Package vs. Direct)
Every module supports both:
```python
try:
    from .module import function  # package import
except Exception:
    from module import function   # direct import
```
This enables both `python -m praxis.main` (package mode) and `python praxis/main.py` (direct mode).

### 4. Pure-Function Scoring
The engine is designed as pure functions — `score_tool(tool, keywords)` has no side effects, no global state mutation. This makes it testable, composable, and concurrent-safe.

### 5. The LLM is Optional
Praxis works completely without any LLM API key. The interpreter falls back to rule-based parsing, the reasoning engine falls back to local synthesis. The LLM is an accelerator, not a dependency.

### 6. Consciousness-Inspired Architecture
The later modules (v12–v16) use philosophical frameworks as design metaphors:
- **Awakening**: Recognitions → architectural principles
- **Enlightenment**: Truths → design patterns (Hexagonal, Clean Arch, FSM)
- **Conduit**: Cognitive science theories (IIT, GWT, CoALA) → scoring dimensions
- **Resonance**: Relationship engineering → telemetry metrics

These are not metaphors in the code — they are concrete scoring dimensions with numeric outputs that feed into the reasoning pipeline.

### 7. Composite Scoring Pattern
Each assessment module follows the same pattern:
1. Multiple sub-scorers (5–14 per module) each return 0.0–1.0
2. A master `assess_*()` function computes a weighted composite
3. Warnings/recommendations are generated from threshold analysis
4. An Assessment dataclass bundles scores + composite + metadata

---

## Known Technical Patterns

### The tools.db Stale Cache Problem
`data.py` stores the `TOOLS` list in-memory. On first import, `storage.py` may cache it to `tools.db`. If you modify `data.py` (add/remove tools), the SQLite cache becomes stale. **Solution:** Delete `praxis/tools.db` before testing. It's in `.gitignore`.

### Import Alias Naming Convention
In `api.py`, all imported functions use underscore-prefixed aliases to avoid endpoint function name collisions:
```python
from .conduit import assess_conduit as _assess_conduit
from .resonance import assess_resonance as _assess_resonance_v16  # v16 avoids collision
```

### The `deep_reason` vs `deep_reason_v2` Split
- `deep_reason()` — Original v6 reasoning (lighter, faster)
- `deep_reason_v2()` — Full consciousness stack: integrates verticals, guardrails, architecture, resilience, metacognition, introspection, awakening, authorship, enlightenment, conduit, resonance, and enterprise. This is what `/cognitive` calls.

### Import Flag Pattern in reason.py
Each optional module has a boolean flag:
```python
_CONDUIT_OK = True   # set if import succeeds
_CONDUIT_OK = False  # set in except block
```
`deep_reason_v2` checks these flags before invoking enrichment.

---

## Git History

<!-- AUTO:GIT:START -->
```
f0b1db7 ci: auto-update README stats on every push via GitHub Actions
a422d95 docs: comprehensive README  full context transfer document for 17-version cognitive architecture
f9cf543 audit: fix 12 vibe-coding issues across 6 files
10abd49 Praxis v17  The Enterprise Engine: Billion-Dollar Decision Engine
2069dad Praxis v16  The Resonance: AGI as continuous human-machine relationship
485a6dd Praxis v15  The Conduit: decoupled cognitive systems & emergent intelligence
85dfa25 Praxis v14  Architectural Enlightenment: 223 tools, 171 API endpoints, 22 tests, 48 modules
```
<!-- AUTO:GIT:END -->

---

## Context for Future AI Models

This section exists so that any future AI assistant working on this codebase can rapidly understand the system's depth, patterns, and current state.

### What Praxis IS
Praxis is an **AI tool recommendation engine** that evolved into a **cognitive architecture**. It recommends AI tools (like ChatGPT, Figma AI, LangChain, dbt, etc.) based on user queries, profiles, and constraints. But its real innovation is the 17-layer intelligence stack that processes those recommendations through agentic reasoning, knowledge graphs, vendor risk assessment, industry-specific constraints, safety guardrails, metacognitive self-awareness, and enterprise scaling.

### What Praxis is NOT
- Not a chatbot or LLM wrapper
- Not a tool directory or search engine
- Not dependent on any external AI service (works zero-dep)
- Not a web scraper — all tool data is curated in `data.py`

### The Philosophical Arc
The codebase tells a story:
1. **v1–v5**: Practical tooling (score, recommend, explain)
2. **v6–v8**: Intelligent agency (reason, retrieve, specialize)
3. **v9–v10**: Safety consciousness (guard, detect risks)
4. **v11**: Self-awareness (Praxis learns to analyze itself)
5. **v12–v14**: Philosophical awakening (conscious design, self-authorship, enlightenment)
6. **v15–v17**: Enterprise transcendence (cognitive architecture at scale)

### Current State (Post-Audit)
<!-- AUTO:STATE:START -->
- **246 tools**, zero duplicates, clean tag casing
- **256 API routes**, all functional
- **157 tests passing**
- **45 Python modules**, ~29,000 lines
- **12 frontend files**, ~4,400 lines
- All critical bugs fixed (alias collision, caveats reset, dead code)
- Server runs on port 8000 via `uvicorn praxis.api:app --port 8000`
<!-- AUTO:STATE:END -->

### How to Add a New Module (v18+)
1. Create `praxis/new_module.py` with an `assess_*()` master function and sub-scorers
2. Add import to `api.py` (both primary `from .new_module` and fallback `from new_module` blocks)
3. Add endpoints in `api.py` inside the `create_app()` function
4. Add import flag in `reason.py` and integrate into `deep_reason_v2()`
5. Add entry to `__init__.py` `__all__`
6. Create `praxis/tests/test_new_module.py`
7. Optionally create `praxis/frontend/new_module.html`

### Key Files to Read First
1. **`engine.py`** — Understand the scoring logic (entry point for all recommendations)
2. **`reason.py`** — Understand how all modules integrate (the orchestrator)
3. **`api.py`** — Understand the full API surface (the HTTP layer)
4. **`data.py`** — Understand the tool catalog structure
5. **`conduit.py`** or **`enterprise.py`** — Understand the latest architectural thinking

### Dependencies
```
fastapi[all]
uvicorn[standard]
# Optional:
openai>=1.0
anthropic>=0.18
pytest  # dev only
```

Everything else is pure Python standard library.
