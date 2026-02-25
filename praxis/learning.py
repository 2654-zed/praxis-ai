# --------------- Learning Layer ---------------
"""
Closes the feedback loop by transforming raw feedback entries into
actionable signals that improve future recommendations.

Responsibilities:
    1. Aggregate feedback into per-tool quality scores
    2. Compute simple collaborative filtering signals
       (users like you also liked…)
    3. Detect tool-pair affinities from accept/reject patterns
    4. Apply learned weights back to the knowledge base (popularity)

This is the seed of Praxis's intelligence moat — every interaction
makes the system smarter.
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

try:
    from .feedback import _load_feedback
    from .usage import _load_usage, _save_usage
    from .data import TOOLS
except Exception:
    from feedback import _load_feedback
    from usage import _load_usage, _save_usage
    from data import TOOLS

LEARNING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learned_signals.json")


# ======================================================================
# Signal computation
# ======================================================================

def compute_tool_quality() -> Dict[str, dict]:
    """Aggregate feedback into per-tool quality metrics.

    Returns:
        { "ToolName": {
            "avg_rating": float,
            "total_feedback": int,
            "accept_rate": float,    # 0.0 – 1.0
            "recent_trend": str,     # "improving" | "declining" | "stable"
          }, ...
        }
    """
    entries = _load_feedback()
    tool_data: Dict[str, list] = defaultdict(list)

    for e in entries:
        name = e.get("tool")
        if not name:
            continue
        tool_data[name].append(e)

    result = {}
    for name, items in tool_data.items():
        ratings = [int(i["rating"]) for i in items if i.get("rating") is not None]
        accepted = sum(1 for i in items if i.get("accepted"))

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        accept_rate = accepted / len(items) if items else 0

        # Trend: compare first half vs second half average rating
        trend = "stable"
        if len(ratings) >= 4:
            mid = len(ratings) // 2
            first_half = sum(ratings[:mid]) / mid
            second_half = sum(ratings[mid:]) / (len(ratings) - mid)
            if second_half - first_half > 0.5:
                trend = "improving"
            elif first_half - second_half > 0.5:
                trend = "declining"

        result[name] = {
            "avg_rating": round(avg_rating, 2),
            "total_feedback": len(items),
            "accept_rate": round(accept_rate, 3),
            "recent_trend": trend,
        }

    return result


def compute_pair_affinities() -> List[Tuple[str, str, float]]:
    """Find tool pairs that are frequently accepted together in the same
    session / by the same profile type.

    Returns list of (tool_a, tool_b, affinity_score) sorted descending.
    """
    entries = _load_feedback()

    # Group feedback by query text (proxy for session)
    sessions: Dict[str, List[str]] = defaultdict(list)
    for e in entries:
        if e.get("accepted"):
            q = e.get("query", "")
            sessions[q].append(e.get("tool", ""))

    # Count co-occurrences
    pair_counts: Dict[tuple, int] = defaultdict(int)
    for tools in sessions.values():
        unique = list(set(t for t in tools if t))
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                pair = tuple(sorted([unique[i], unique[j]]))
                pair_counts[pair] += 1

    # Normalize into affinity scores
    max_count = max(pair_counts.values()) if pair_counts else 1
    affinities = [
        (a, b, round(count / max_count, 3))
        for (a, b), count in pair_counts.items()
    ]
    affinities.sort(key=lambda x: x[2], reverse=True)
    return affinities


def compute_intent_tool_map() -> Dict[str, List[dict]]:
    """Map intent categories → best-performing tools based on feedback.

    Returns:
        { "writing": [{"tool": "ChatGPT", "score": 8.5}, ...], ... }
    """
    entries = _load_feedback()
    intent_tools: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))

    for e in entries:
        details = e.get("details") or {}
        intent_struct = details.get("intent_struct") or {}
        intent = intent_struct.get("intent") or ""
        tool_name = e.get("tool", "")
        rating = e.get("rating")

        if intent and tool_name and rating is not None:
            intent_tools[intent][tool_name].append(int(rating))

    result = {}
    for intent, tools in intent_tools.items():
        ranked = []
        for tool_name, ratings in tools.items():
            avg = sum(ratings) / len(ratings)
            ranked.append({"tool": tool_name, "score": round(avg, 2), "samples": len(ratings)})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        result[intent] = ranked

    return result


# ======================================================================
# Apply learned signals
# ======================================================================

def apply_learned_popularity():
    """Recompute popularity scores from feedback and write to usage.json.

    This is the core "learning" action — feedback directly influences
    future ranking.
    """
    quality = compute_tool_quality()
    usage = _load_usage()

    for tool_name, metrics in quality.items():
        # Popularity = accept_rate * avg_rating * log(total_feedback + 1)
        import math
        pop = int(
            metrics["accept_rate"]
            * metrics["avg_rating"]
            * math.log(metrics["total_feedback"] + 1, 2)
        )
        usage[tool_name] = max(pop, usage.get(tool_name, 0))

    _save_usage(usage)

    # Also update in-memory TOOLS
    for t in TOOLS:
        if t.name in usage:
            t.popularity = usage[t.name]

    return usage


def save_learned_signals():
    """Persist all computed signals to a JSON file for inspection / debugging."""
    signals = {
        "computed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tool_quality": compute_tool_quality(),
        "pair_affinities": [
            {"tool_a": a, "tool_b": b, "affinity": s}
            for a, b, s in compute_pair_affinities()
        ],
        "intent_tool_map": compute_intent_tool_map(),
    }
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2)
    return signals


def load_learned_signals() -> dict:
    """Load previously computed signals (if any)."""
    if not os.path.exists(LEARNING_FILE):
        return {}
    try:
        with open(LEARNING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ======================================================================
# Convenience: full learning cycle
# ======================================================================

def run_learning_cycle() -> dict:
    """Execute a full learning cycle: compute signals → apply popularity → persist."""
    apply_learned_popularity()
    signals = save_learned_signals()
    return signals


# ======================================================================
# Differential Diagnosis — Override Tracking & Filter Calibration
# ======================================================================

OVERRIDE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "override_log.json")

# Threshold: if a filter is overridden this many times, recommend downgrade
OVERRIDE_ALERT_THRESHOLD = 5


def _load_overrides() -> list:
    """Load the override log."""
    if not os.path.exists(OVERRIDE_FILE):
        return []
    try:
        with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def compute_override_rate() -> dict:
    """
    Analyse the override log to determine filter calibration health.

    The Override Rate measures how often users manually select tools
    that the differential engine explicitly eliminated. A high rate
    for a specific filter signals it is too aggressive.

    Returns:
        {
            "total_overrides": int,
            "by_reason_code": { code: count },
            "by_tool": { tool_name: count },
            "filter_health": [
                {
                    "code": str,
                    "override_count": int,
                    "status": "healthy" | "needs_review" | "critical",
                    "recommendation": str,
                }
            ],
            "computed_at": str,
        }
    """
    overrides = _load_overrides()

    by_code = defaultdict(int)
    by_tool = defaultdict(int)

    for entry in overrides:
        code = entry.get("reason_code", "UNKNOWN")
        tool = entry.get("tool", "unknown")
        by_code[code] += 1
        by_tool[tool] += 1

    # Filter health assessment
    health = []
    for code, count in sorted(by_code.items(), key=lambda x: x[1], reverse=True):
        if count >= OVERRIDE_ALERT_THRESHOLD * 2:
            status = "critical"
            rec = (
                f"Filter '{code}' has been overridden {count} times. "
                f"STRONGLY recommend downgrading from hard constraint to "
                f"soft penalty to prevent user frustration."
            )
        elif count >= OVERRIDE_ALERT_THRESHOLD:
            status = "needs_review"
            rec = (
                f"Filter '{code}' has been overridden {count} times. "
                f"Review whether this filter's threshold is calibrated "
                f"correctly for your user base."
            )
        else:
            status = "healthy"
            rec = f"Filter '{code}' override rate is within acceptable bounds."

        health.append({
            "code": code,
            "override_count": count,
            "status": status,
            "recommendation": rec,
        })

    return {
        "total_overrides": len(overrides),
        "by_reason_code": dict(by_code),
        "by_tool": dict(by_tool),
        "filter_health": health,
        "computed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def get_elimination_efficacy() -> dict:
    """
    Cross-reference override data with tool quality data to assess
    whether eliminations are helping or hurting user outcomes.

    Returns:
        {
            "overridden_tools_quality": { tool: quality_metrics },
            "vindicated_eliminations": int,  # overridden tools that later declined
            "questionable_eliminations": int,  # overridden tools that stayed strong
        }
    """
    overrides = _load_overrides()
    quality = compute_tool_quality()

    overridden_tools = set(e.get("tool", "") for e in overrides)

    result = {}
    vindicated = 0
    questionable = 0

    for tool_name in overridden_tools:
        if not tool_name:
            continue
        q = quality.get(tool_name, {})
        result[tool_name] = q

        # If the overridden tool is declining, the elimination was justified
        if q.get("recent_trend") == "declining" or q.get("avg_rating", 5) < 3:
            vindicated += 1
        elif q.get("avg_rating", 0) >= 4 and q.get("accept_rate", 0) > 0.7:
            questionable += 1

    return {
        "overridden_tools_quality": result,
        "vindicated_eliminations": vindicated,
        "questionable_eliminations": questionable,
    }
