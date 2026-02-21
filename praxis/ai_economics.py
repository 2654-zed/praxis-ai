# ────────────────────────────────────────────────────────────────────
# ai_economics.py — Token Cost Attribution, ROI Calculation,
#                   Utilization Tracking, and Consumption Analytics
# ────────────────────────────────────────────────────────────────────
"""
Implements the AI Economics & Telemetry Dashboard for Praxis
(Blueprint §8):

1. **Token Cost Attribution** — tracks token consumption per user,
   department, workflow, and individual tool call.

2. **ROI Calculation** — correlates automated tasks with efficiency
   benchmarks to compute real-time Return on Investment.

3. **Utilization Tracking** — identifies inefficient prompts, infinite
   loops, and underutilized seats.

4. **Budget Management** — spend alerts, quotas, and forecasting.

All functions are pure-Python with no external dependencies.
"""

from __future__ import annotations

import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ╔════════════════════════════════════════════════════════════════════╗
# ║  1. TOKEN COST MODELS                                            ║
# ╚════════════════════════════════════════════════════════════════════╝

# Cost per 1K tokens (USD) for common model tiers
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "llama-3-70b": {"input": 0.0008, "output": 0.0008},
    "mixtral-8x7b": {"input": 0.0006, "output": 0.0006},
    "default": {"input": 0.002, "output": 0.008},
}


def token_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "default",
) -> Dict[str, float]:
    """
    Calculate the cost in USD for a given token consumption.
    """
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "model": model,
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(input_cost + output_cost, 6),
    }


# ╔════════════════════════════════════════════════════════════════════╗
# ║  2. USAGE LEDGER — Granular Attribution                          ║
# ╚════════════════════════════════════════════════════════════════════╝

@dataclass
class UsageRecord:
    """A single token consumption event."""
    record_id: str = ""
    timestamp: float = field(default_factory=time.time)
    user_id: str = ""
    department: str = ""
    workflow_id: str = ""
    agent_id: str = ""
    model: str = "default"
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    operation: str = ""        # "search", "interpret", "compose", "analyze"
    latency_ms: float = 0.0
    error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "department": self.department,
            "workflow_id": self.workflow_id,
            "agent_id": self.agent_id,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "operation": self.operation,
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
        }


class UsageLedger:
    """
    Thread-safe ledger tracking all token-level consumption events.
    Supports multi-dimensional attribution and aggregation.
    """

    MAX_RECORDS = 50000

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: List[UsageRecord] = []
        self._counter: int = 0

    def record(
        self,
        user_id: str = "system",
        department: str = "",
        workflow_id: str = "",
        agent_id: str = "",
        model: str = "default",
        input_tokens: int = 0,
        output_tokens: int = 0,
        operation: str = "",
        latency_ms: float = 0.0,
        error: bool = False,
    ) -> Dict[str, Any]:
        """Record a new usage event."""
        cost = token_cost(input_tokens, output_tokens, model)
        with self._lock:
            self._counter += 1
            rec = UsageRecord(
                record_id=f"UR-{self._counter:06d}",
                user_id=user_id,
                department=department,
                workflow_id=workflow_id,
                agent_id=agent_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost["total_cost_usd"],
                operation=operation,
                latency_ms=latency_ms,
                error=error,
            )
            self._records.append(rec)
            if len(self._records) > self.MAX_RECORDS:
                self._records = self._records[-self.MAX_RECORDS:]
            return rec.to_dict()

    def aggregate_by(self, dimension: str = "user_id") -> Dict[str, Dict[str, Any]]:
        """
        Aggregate usage by a given dimension.

        Supported dimensions: user_id, department, workflow_id,
        agent_id, model, operation.
        """
        with self._lock:
            buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
                "total_tokens": 0, "total_cost_usd": 0.0, "request_count": 0,
                "error_count": 0, "avg_latency_ms": 0.0, "_latencies": [],
            })

            for rec in self._records:
                key = getattr(rec, dimension, "unknown")
                b = buckets[key]
                b["total_tokens"] += rec.input_tokens + rec.output_tokens
                b["total_cost_usd"] += rec.cost_usd
                b["request_count"] += 1
                if rec.error:
                    b["error_count"] += 1
                b["_latencies"].append(rec.latency_ms)

            # Finalize
            result = {}
            for key, b in buckets.items():
                lats = b.pop("_latencies", [])
                b["avg_latency_ms"] = round(sum(lats) / len(lats), 2) if lats else 0.0
                b["total_cost_usd"] = round(b["total_cost_usd"], 6)
                result[key] = b

            return result

    def detect_waste(self, min_tokens_per_request: int = 500) -> List[Dict[str, Any]]:
        """
        Identify potentially wasteful usage patterns:
        - Very high token counts per request
        - Repeated errors (possible infinite loops)
        - Low-value operations with high cost
        """
        with self._lock:
            waste: List[Dict[str, Any]] = []

            # High-token requests
            for rec in self._records:
                total = rec.input_tokens + rec.output_tokens
                if total > min_tokens_per_request * 10:
                    waste.append({
                        "type": "high_token_count",
                        "record_id": rec.record_id,
                        "tokens": total,
                        "cost_usd": round(rec.cost_usd, 6),
                        "operation": rec.operation,
                        "agent_id": rec.agent_id,
                    })

            # Repeated errors from same agent (possible loop)
            agent_errors: Dict[str, int] = defaultdict(int)
            for rec in self._records[-1000:]:
                if rec.error:
                    agent_errors[rec.agent_id] += 1

            for agent, count in agent_errors.items():
                if count >= 5:
                    waste.append({
                        "type": "error_loop_suspected",
                        "agent_id": agent,
                        "error_count": count,
                        "recommendation": "Investigate agent for infinite retry loop",
                    })

            return waste

    def summary(self) -> Dict[str, Any]:
        """High-level usage summary."""
        with self._lock:
            total_tokens = sum(r.input_tokens + r.output_tokens for r in self._records)
            total_cost = sum(r.cost_usd for r in self._records)
            total_errors = sum(1 for r in self._records if r.error)
            return {
                "total_records": len(self._records),
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 6),
                "total_errors": total_errors,
                "error_rate": round(total_errors / max(len(self._records), 1), 4),
                "avg_tokens_per_request": round(total_tokens / max(len(self._records), 1), 1),
                "capacity_used": round(len(self._records) / self.MAX_RECORDS, 4),
            }


# Global ledger singleton
_ledger: Optional[UsageLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> UsageLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = UsageLedger()
        return _ledger


# ╔════════════════════════════════════════════════════════════════════╗
# ║  3. ROI CALCULATOR                                               ║
# ╚════════════════════════════════════════════════════════════════════╝

@dataclass
class ROIMetrics:
    """Return on Investment metrics for AI operations."""
    total_ai_cost_usd: float = 0.0
    labor_hours_saved: float = 0.0
    labor_cost_saved_usd: float = 0.0
    error_reduction_pct: float = 0.0
    throughput_multiplier: float = 1.0
    net_value_usd: float = 0.0
    roi_percentage: float = 0.0
    payback_days: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_ai_cost_usd": round(self.total_ai_cost_usd, 2),
            "labor_hours_saved": round(self.labor_hours_saved, 1),
            "labor_cost_saved_usd": round(self.labor_cost_saved_usd, 2),
            "error_reduction_pct": round(self.error_reduction_pct, 1),
            "throughput_multiplier": round(self.throughput_multiplier, 2),
            "net_value_usd": round(self.net_value_usd, 2),
            "roi_percentage": round(self.roi_percentage, 1),
            "payback_days": round(self.payback_days, 1),
        }


def calculate_roi(
    total_ai_cost_usd: float,
    tasks_automated: int,
    avg_manual_minutes_per_task: float = 30.0,
    labor_rate_per_hour: float = 75.0,
    error_rate_before: float = 0.05,
    error_rate_after: float = 0.01,
    period_days: int = 30,
) -> ROIMetrics:
    """
    Calculate ROI by correlating AI costs with labor savings.

    Parameters
    ----------
    total_ai_cost_usd           : Total spent on AI (tokens, compute).
    tasks_automated             : Number of tasks automated by AI.
    avg_manual_minutes_per_task : Average time a human would take per task.
    labor_rate_per_hour         : Hourly cost of a human analyst.
    error_rate_before           : Error rate without AI.
    error_rate_after            : Error rate with AI.
    period_days                 : Time period for the calculation.
    """
    labor_hours = tasks_automated * avg_manual_minutes_per_task / 60
    labor_cost = labor_hours * labor_rate_per_hour
    error_reduction = max(0, (error_rate_before - error_rate_after) / max(error_rate_before, 0.001)) * 100
    throughput = tasks_automated / max(period_days, 1)

    net_value = labor_cost - total_ai_cost_usd
    roi_pct = (net_value / max(total_ai_cost_usd, 0.01)) * 100

    # Payback: days for AI cost to be offset by savings
    daily_savings = labor_cost / max(period_days, 1)
    payback = total_ai_cost_usd / max(daily_savings, 0.01)

    return ROIMetrics(
        total_ai_cost_usd=total_ai_cost_usd,
        labor_hours_saved=labor_hours,
        labor_cost_saved_usd=labor_cost,
        error_reduction_pct=error_reduction,
        throughput_multiplier=throughput,
        net_value_usd=net_value,
        roi_percentage=roi_pct,
        payback_days=payback,
    )


# ╔════════════════════════════════════════════════════════════════════╗
# ║  4. BUDGET MANAGEMENT                                            ║
# ╚════════════════════════════════════════════════════════════════════╝

@dataclass
class BudgetConfig:
    """Budget thresholds and alerts."""
    monthly_budget_usd: float = 1000.0
    alert_threshold_pct: float = 80.0     # alert at 80% of budget
    hard_limit_usd: float = 1500.0        # absolute ceiling
    per_user_limit_usd: float = 100.0
    per_workflow_limit_usd: float = 200.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "monthly_budget_usd": self.monthly_budget_usd,
            "alert_threshold_pct": self.alert_threshold_pct,
            "hard_limit_usd": self.hard_limit_usd,
            "per_user_limit_usd": self.per_user_limit_usd,
            "per_workflow_limit_usd": self.per_workflow_limit_usd,
        }


def check_budget(
    config: Optional[BudgetConfig] = None,
) -> Dict[str, Any]:
    """
    Check current spend against budget thresholds.
    """
    if config is None:
        config = BudgetConfig()

    ledger = get_ledger()
    summary = ledger.summary()
    current_spend = summary["total_cost_usd"]

    pct_used = (current_spend / max(config.monthly_budget_usd, 0.01)) * 100
    alerts: List[Dict[str, str]] = []

    if pct_used >= 100:
        alerts.append({"level": "critical", "message": f"Monthly budget exceeded: ${current_spend:.2f} / ${config.monthly_budget_usd:.2f}"})
    elif pct_used >= config.alert_threshold_pct:
        alerts.append({"level": "warning", "message": f"Approaching budget limit: {pct_used:.1f}% used"})

    if current_spend >= config.hard_limit_usd:
        alerts.append({"level": "critical", "message": f"Hard spending limit reached: ${current_spend:.2f}"})

    # Per-user checks
    user_agg = ledger.aggregate_by("user_id")
    for user, data in user_agg.items():
        if data["total_cost_usd"] > config.per_user_limit_usd:
            alerts.append({"level": "warning", "message": f"User {user} exceeded per-user limit: ${data['total_cost_usd']:.2f}"})

    return {
        "budget": config.to_dict(),
        "current_spend_usd": round(current_spend, 4),
        "budget_utilization_pct": round(pct_used, 1),
        "alerts": alerts,
        "within_budget": pct_used < 100,
        "usage_summary": summary,
    }


# ╔════════════════════════════════════════════════════════════════════╗
# ║  5. CONVENIENCE                                                  ║
# ╚════════════════════════════════════════════════════════════════════╝

def economics_dashboard() -> Dict[str, Any]:
    """Full AI economics snapshot."""
    ledger = get_ledger()
    summary = ledger.summary()
    waste = ledger.detect_waste()

    # Compute ROI with current data
    roi = calculate_roi(
        total_ai_cost_usd=summary["total_cost_usd"],
        tasks_automated=summary["total_records"],
    )

    return {
        "usage_summary": summary,
        "roi": roi.to_dict(),
        "budget": check_budget(),
        "waste_detection": waste,
        "model_pricing": MODEL_PRICING,
        "attribution": {
            "by_user": ledger.aggregate_by("user_id"),
            "by_department": ledger.aggregate_by("department"),
            "by_model": ledger.aggregate_by("model"),
        },
    }
