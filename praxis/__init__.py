"""Praxis — AI Decision Engine

Making the folder a package so `python -m praxis.main` and installed console
scripts can import `praxis.main:run` as an entry point.
"""

import logging
import os

# ── Structured logging setup ──
# Respects PRAXIS_LOG_LEVEL env var; defaults to INFO.
_log_level = os.environ.get("PRAXIS_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _log_level, logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

__all__ = [
    "main",
    "engine",
    "interpreter",
    "data",
    "tools",
    "feedback",
    "usage",
    "storage",
    "api",
    # v2 modules
    "config",
    "profile",
    "explain",
    "stack",
    "learning",
    # v3 intelligence
    "intelligence",
    # v4 vendor intelligence — risk assessment layer
    "philosophy",
    # v5 ingest + seed
    "ingest",
    "seed",
    # v6 agentic reasoning
    "reason",
    # v7 cognitive search — hybrid retrieval, knowledge graph, PRISM agents
    "retrieval",
    "graph",
    "prism",
    # v8 vertical industry intelligence — constraint reasoning, anti-patterns, workflow taxonomy
    "verticals",
    # v9 safety guardrails + event-driven architecture intelligence
    "guardrails",
    "orchestration",
    # v10 resilience — vibe coding detection, static analysis, sandboxing, TDD, R.P.I., HITL
    "resilience",
    # v11 metacognition — self-awareness, structural entropy, APVP cycle, GoodVibe, RACG
    "metacognition",
    # v11b introspect — real AST self-analysis, Praxis looks in the mirror
    "introspect",
    # v12 awakening — conscious system design, VSD, leaky abstractions, MESIAS
    "awakening",
    # v13 authorship — self-authorship, DDD, event sourcing, circuit breaker, ADRs, Strangler Fig
    "authorship",
    # v14 enlightenment — metaphysical truths, Identity Map, Observer, Clean Arch, FSM, asyncio, DI
    "enlightenment",
]
