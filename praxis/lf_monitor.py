# ────────────────────────────────────────────────────────────────────
# lf_monitor.py — Latent Flux Orchestration Reliability Monitor
# ────────────────────────────────────────────────────────────────────
"""
Pure-Python implementation of Latent Flux primitives for Praxis.

Adapts the three core LF primitives (ReservoirState, AttractorCompetition,
RecursiveFlow) into an orchestration reliability monitor — no NumPy required.

Three components:
    ToolReservoir      — Per-tool behavioral baseline with σ² tracking
    PipelineHealthCompetitor — 3-basin attractor for pipeline health
    RetryLoopDetector  — Cycle detection for retry loops

Design constraints:
    - Pure Python stdlib only (math, random, copy)
    - d ≤ 20 dimensions (tool performance vectors)
    - Graceful degradation — if this module fails, trust_decay.py falls back

Usage:
    from praxis.lf_monitor import ToolReservoir, PipelineHealthCompetitor
    reservoir = ToolReservoir(d=6, leak_rate=0.1)
    reservoir.step([latency, quality, tokens, error_rate, output_len, cost])
    drift = reservoir.deviation_score([new_latency, ...])
"""

from __future__ import annotations

import math
import random
import copy
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

logger = logging.getLogger("praxis.lf_monitor")


# =====================================================================
# Vector/Matrix Utilities (pure Python, no NumPy)
# =====================================================================

def _zeros(n: int) -> List[float]:
    return [0.0] * n

def _zeros_mat(rows: int, cols: int) -> List[List[float]]:
    return [[0.0] * cols for _ in range(rows)]

def _rand_mat(rows: int, cols: int, rng: random.Random, scale: float = 1.0) -> List[List[float]]:
    return [[rng.gauss(0, scale) for _ in range(cols)] for _ in range(rows)]

def _mat_vec(mat: List[List[float]], vec: List[float]) -> List[float]:
    """Matrix-vector multiply: mat (m x n) @ vec (n,) -> (m,)."""
    return [sum(mat[i][j] * vec[j] for j in range(len(vec))) for i in range(len(mat))]

def _vec_add(a: List[float], b: List[float]) -> List[float]:
    return [a[i] + b[i] for i in range(len(a))]

def _vec_sub(a: List[float], b: List[float]) -> List[float]:
    return [a[i] - b[i] for i in range(len(a))]

def _vec_scale(v: List[float], s: float) -> List[float]:
    return [x * s for x in v]

def _vec_dot(a: List[float], b: List[float]) -> float:
    return sum(a[i] * b[i] for i in range(len(a)))

def _vec_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))

def _vec_tanh(v: List[float]) -> List[float]:
    return [math.tanh(x) for x in v]


# =====================================================================
# ToolReservoir — Simplified ReservoirState with σ² tracking
# =====================================================================

class ToolReservoir:
    """Per-tool behavioral baseline using Echo State Network dynamics.

    Tracks both the mean trajectory (ESN readout) and per-dimension
    running variance (σ²). The deviation_score() returns how many
    standard deviations the current input is from the baseline.

    Args:
        d: Input dimension (number of performance metrics per tool).
        reservoir_scale: Hidden state multiplier (default 4).
        spectral_radius: Must be < 1.0 for stability (default 0.9).
        input_scaling: Scale for input weight matrix (default 0.1).
        leak_rate: Memory parameter — lower = longer memory (default 0.1).
        seed: Random seed for reproducible weight initialization.
    """

    def __init__(
        self,
        d: int = 6,
        reservoir_scale: int = 4,
        spectral_radius: float = 0.9,
        input_scaling: float = 0.1,
        leak_rate: float = 0.1,
        seed: int = 42,
    ):
        if d < 1:
            raise ValueError(f"d must be >= 1, got {d}")
        if not (0 < spectral_radius < 1.0):
            raise ValueError(f"spectral_radius must be in (0, 1), got {spectral_radius}")
        if not (0.0 < leak_rate <= 1.0):
            raise ValueError(f"leak_rate must be in (0, 1], got {leak_rate}")

        self.d = d
        self.r = d * reservoir_scale
        self.leak_rate = leak_rate
        self.spectral_radius = spectral_radius
        self._step_count = 0

        rng = random.Random(seed)

        # W_in: r x d
        self.W_in = _rand_mat(self.r, d, rng, scale=input_scaling)

        # W_res: r x r, sparse (~10% density), scaled to spectral_radius
        self.W_res = _zeros_mat(self.r, self.r)
        for i in range(self.r):
            for j in range(self.r):
                if rng.random() < 0.1:
                    self.W_res[i][j] = rng.gauss(0, 1.0)

        # Scale W_res by spectral_radius / estimated_max_eig
        # For pure Python, approximate max eigenvalue via power iteration
        max_eig = self._power_iteration_max_eig(self.W_res, rng, iterations=20)
        if max_eig > 1e-10:
            scale_factor = spectral_radius / max_eig
            for i in range(self.r):
                for j in range(self.r):
                    self.W_res[i][j] *= scale_factor

        # W_out: d x r
        out_scale = 1.0 / math.sqrt(self.r) if self.r > 0 else 1.0
        self.W_out = _rand_mat(d, self.r, rng, scale=out_scale)

        # Hidden state
        self._h: List[float] = _zeros(self.r)

        # σ² tracking
        self._variance: List[float] = _zeros(d)
        self._mean_ema: List[float] = _zeros(d)

    @staticmethod
    def _power_iteration_max_eig(mat: List[List[float]], rng: random.Random, iterations: int = 20) -> float:
        """Approximate largest eigenvalue magnitude via power iteration."""
        n = len(mat)
        if n == 0:
            return 0.0
        v = [rng.gauss(0, 1) for _ in range(n)]
        norm = _vec_norm(v)
        if norm < 1e-12:
            return 0.0
        v = _vec_scale(v, 1.0 / norm)
        eigenvalue = 0.0
        for _ in range(iterations):
            w = _mat_vec(mat, v)
            eigenvalue = _vec_norm(w)
            if eigenvalue < 1e-12:
                break
            v = _vec_scale(w, 1.0 / eigenvalue)
        return eigenvalue

    def step(self, x: List[float]) -> List[float]:
        """Evolve reservoir by one step, return readout.

        Args:
            x: Performance vector of length d.

        Returns:
            Readout vector of length d (the baseline estimate).
        """
        if len(x) != self.d:
            raise ValueError(f"Expected input length {self.d}, got {len(x)}")

        # ESN dynamics: h(t+1) = (1-α)h(t) + α·tanh(W_in·x + W_res·h(t))
        pre = _vec_add(_mat_vec(self.W_in, x), _mat_vec(self.W_res, self._h))
        activation = _vec_tanh(pre)

        self._h = _vec_add(
            _vec_scale(self._h, 1.0 - self.leak_rate),
            _vec_scale(activation, self.leak_rate),
        )

        # Readout: y = W_out · h
        y = _mat_vec(self.W_out, self._h)

        # Update σ² tracking
        self._step_count += 1
        residual = _vec_sub(x, y)
        for i in range(self.d):
            self._variance[i] = (
                (1.0 - self.leak_rate) * self._variance[i]
                + self.leak_rate * (residual[i] ** 2)
            )
            self._mean_ema[i] = (
                (1.0 - self.leak_rate) * self._mean_ema[i]
                + self.leak_rate * x[i]
            )

        return y

    def readout(self) -> List[float]:
        """Current readout without advancing the reservoir."""
        return _mat_vec(self.W_out, self._h)

    @property
    def variance(self) -> List[float]:
        """Per-dimension running variance σ²."""
        return list(self._variance)

    @property
    def std(self) -> List[float]:
        """Per-dimension standard deviation σ."""
        return [math.sqrt(max(v, 1e-12)) for v in self._variance]

    def deviation_score(self, x: List[float]) -> float:
        """Mahalanobis-like distance of x from baseline, accounting for σ.

        Returns scalar: average z-score across dimensions. Higher values
        mean the tool's behavior deviates more from its baseline.

        Interpretation:
            < 1.0: Normal operation
            1.0-2.0: MILD drift (elevated but within expected range)
            > 2.0: SEVERE drift (significant structural deviation)
        """
        if len(x) != self.d:
            raise ValueError(f"Expected input length {self.d}, got {len(x)}")
        if self._step_count < 2:
            return 0.0  # Not enough history for meaningful deviation

        baseline = self.readout()
        std = self.std
        z_total = 0.0
        for i in range(self.d):
            z = abs(x[i] - baseline[i]) / max(std[i], 1e-8)
            z_total += z
        return z_total / self.d

    @property
    def step_count(self) -> int:
        return self._step_count

    def to_dict(self) -> Dict:
        """Serialize reservoir state for persistence."""
        return {
            "d": self.d,
            "r": self.r,
            "leak_rate": self.leak_rate,
            "step_count": self._step_count,
            "variance": list(self._variance),
            "mean_ema": list(self._mean_ema),
        }


# =====================================================================
# PipelineHealthCompetitor — 3-basin attractor for pipeline health
# =====================================================================

@dataclass
class CompetitionResult:
    """Result of attractor competition."""
    winner: str                    # "healthy", "degrading", "failing"
    margin: float                  # Distance margin between winner and runner-up
    certainty: float               # 0-1, how deep into the winning basin
    contested: bool                # True if state is in overlap zone
    distances: Dict[str, float]    # Distance to each attractor


class PipelineHealthCompetitor:
    """3-basin attractor competition for pipeline health classification.

    Classifies a pipeline's combined deviation vector into one of three
    basins: Healthy, Degrading, or Failing.

    The attractor positions are defined in deviation-score space:
        Healthy:   all dimensions near 0 (tools at baseline)
        Degrading: dimensions at 1.0 (tools ~1σ from baseline)
        Failing:   dimensions at 3.0 (tools ~3σ from baseline)
    """

    def __init__(self, d: int = 1):
        self.d = d
        # Attractors in deviation-score space
        self.attractors = {
            "healthy":   _zeros(d),
            "degrading": [1.0] * d,
            "failing":   [3.0] * d,
        }

    def compete(self, state: List[float]) -> CompetitionResult:
        """Classify the pipeline state into a health basin.

        Args:
            state: Combined deviation scores, one per monitored tool.

        Returns:
            CompetitionResult with winner, margin, certainty, contested flag.
        """
        if len(state) != self.d:
            raise ValueError(f"Expected state dim {self.d}, got {len(state)}")

        distances = {}
        for name, attractor in self.attractors.items():
            diff = _vec_sub(state, attractor)
            distances[name] = _vec_norm(diff)

        sorted_basins = sorted(distances.items(), key=lambda x: x[1])
        winner = sorted_basins[0][0]
        winner_dist = sorted_basins[0][1]
        runner_dist = sorted_basins[1][1]

        margin = runner_dist - winner_dist
        # Certainty: 0 when equidistant, 1 when far from runner-up
        certainty = min(1.0, margin / max(runner_dist, 1e-8))
        contested = certainty < 0.3  # In the overlap zone

        return CompetitionResult(
            winner=winner,
            margin=margin,
            certainty=certainty,
            contested=contested,
            distances=distances,
        )


# =====================================================================
# RetryLoopDetector — Cycle detection for retry loops
# =====================================================================

@dataclass
class LoopResult:
    """Result of retry loop detection."""
    is_looping: bool
    cycle_depth: int
    converged: bool
    iterations: int
    drift_trace: List[float]       # deviation_score at each iteration


class RetryLoopDetector:
    """Detect retry loops in pipeline stages.

    When a pipeline stage enters a retry loop (e.g., code generation →
    test rejection → retry → rejection), this detector measures the
    cycle depth and convergence behavior.

    Combined with σ from ToolReservoir, this triggers circuit breakers:
    "if cycle_depth > max_depth AND σ of test pass rate > threshold, halt."
    """

    def __init__(
        self,
        max_depth: int = 5,
        convergence_threshold: float = 0.05,
        sigma_threshold: float = 2.0,
    ):
        self.max_depth = max_depth
        self.convergence_threshold = convergence_threshold
        self.sigma_threshold = sigma_threshold

    def detect(
        self,
        outcomes: List[float],
        reservoir: Optional[ToolReservoir] = None,
    ) -> LoopResult:
        """Analyze a sequence of outcomes for loop behavior.

        Args:
            outcomes: Recent outcome values (e.g., test pass rates).
            reservoir: Optional ToolReservoir for σ-aware detection.

        Returns:
            LoopResult with loop detection, depth, and convergence info.
        """
        n = len(outcomes)
        if n < 2:
            return LoopResult(
                is_looping=False, cycle_depth=0,
                converged=True, iterations=n, drift_trace=[],
            )

        # Compute drift trace: change between consecutive outcomes
        drift_trace = [abs(outcomes[i] - outcomes[i - 1]) for i in range(1, n)]

        # Detect convergence: drifts decreasing
        converged = all(
            drift_trace[i] <= drift_trace[i - 1] + self.convergence_threshold
            for i in range(1, len(drift_trace))
        ) if len(drift_trace) > 1 else True

        # Detect cycling: oscillating outcomes (drift stays high)
        avg_drift = sum(drift_trace) / len(drift_trace) if drift_trace else 0.0
        is_looping = avg_drift > self.convergence_threshold and n >= 3

        # Cycle depth: number of consecutive high-drift iterations
        cycle_depth = sum(1 for d in drift_trace if d > self.convergence_threshold)

        # σ-enhanced: if reservoir is provided, check if σ is also elevated
        if reservoir and is_looping:
            # Use the last outcome as a scalar deviation check
            if reservoir.step_count > 5:
                # Create a dummy input using the last outcome
                pass  # σ check is done by the caller via deviation_score

        return LoopResult(
            is_looping=is_looping,
            cycle_depth=cycle_depth,
            converged=converged,
            iterations=n,
            drift_trace=drift_trace,
        )

    def should_trip_breaker(
        self,
        loop_result: LoopResult,
        deviation_score: float = 0.0,
    ) -> bool:
        """Determine if the circuit breaker should trip.

        Args:
            loop_result: Result from detect().
            deviation_score: Current deviation_score from ToolReservoir.

        Returns:
            True if circuit breaker should trip.
        """
        if not loop_result.is_looping:
            return False
        if loop_result.cycle_depth > self.max_depth:
            return True
        if loop_result.cycle_depth > 3 and deviation_score > self.sigma_threshold:
            return True
        return False


# =====================================================================
# Orchestration Monitor — Composes all three primitives
# =====================================================================

class OrchestrationMonitor:
    """High-level orchestration monitor composing all LF primitives.

    Manages per-tool reservoirs, pipeline health competition, and
    retry loop detection.

    Usage:
        monitor = OrchestrationMonitor()
        monitor.record_tool_call("Claude", [latency, quality, tokens, errors, output, cost])
        health = monitor.assess_pipeline_health()
        # health.winner == "healthy" | "degrading" | "failing"
    """

    def __init__(
        self,
        d: int = 6,
        leak_rate: float = 0.1,
        max_retry_depth: int = 5,
    ):
        self.d = d
        self.leak_rate = leak_rate
        self._reservoirs: Dict[str, ToolReservoir] = {}
        self._retry_detector = RetryLoopDetector(max_depth=max_retry_depth)
        self._retry_history: Dict[str, List[float]] = {}

    def _get_reservoir(self, tool_name: str) -> ToolReservoir:
        """Get or create a ToolReservoir for the given tool."""
        if tool_name not in self._reservoirs:
            self._reservoirs[tool_name] = ToolReservoir(
                d=self.d,
                leak_rate=self.leak_rate,
                seed=hash(tool_name) % (2**31),
            )
        return self._reservoirs[tool_name]

    def record_tool_call(
        self,
        tool_name: str,
        metrics: List[float],
    ) -> float:
        """Record a tool invocation's performance metrics.

        Args:
            tool_name: Name of the tool/provider.
            metrics: Performance vector [latency, quality, tokens, error_rate, output_len, cost].

        Returns:
            Current deviation_score for this tool.
        """
        reservoir = self._get_reservoir(tool_name)
        reservoir.step(metrics)
        return reservoir.deviation_score(metrics)

    def get_tool_deviation(self, tool_name: str, metrics: List[float]) -> float:
        """Get deviation score without recording (read-only)."""
        if tool_name not in self._reservoirs:
            return 0.0
        return self._reservoirs[tool_name].deviation_score(metrics)

    def assess_pipeline_health(self) -> CompetitionResult:
        """Assess overall pipeline health from all tool deviations.

        Returns:
            CompetitionResult classifying pipeline as healthy/degrading/failing.
        """
        if not self._reservoirs:
            return CompetitionResult(
                winner="healthy", margin=1.0, certainty=1.0,
                contested=False, distances={"healthy": 0.0, "degrading": 1.0, "failing": 3.0},
            )

        # Collect latest deviation scores from all tools
        deviations = []
        for name, reservoir in self._reservoirs.items():
            if reservoir.step_count > 0:
                # Use the EMA mean as a proxy for current metrics
                deviations.append(
                    reservoir.deviation_score(reservoir._mean_ema)
                )

        if not deviations:
            deviations = [0.0]

        competitor = PipelineHealthCompetitor(d=len(deviations))
        return competitor.compete(deviations)

    def record_retry_outcome(self, stage_name: str, outcome: float) -> None:
        """Record an outcome for retry loop detection."""
        if stage_name not in self._retry_history:
            self._retry_history[stage_name] = []
        self._retry_history[stage_name].append(outcome)
        # Keep only last 20 outcomes
        if len(self._retry_history[stage_name]) > 20:
            self._retry_history[stage_name] = self._retry_history[stage_name][-20:]

    def check_retry_loops(self, stage_name: str) -> Tuple[LoopResult, bool]:
        """Check if a pipeline stage is in a retry loop.

        Returns:
            (LoopResult, should_trip) tuple.
        """
        outcomes = self._retry_history.get(stage_name, [])
        result = self._retry_detector.detect(outcomes)

        # Get deviation score if a reservoir exists for this stage
        dev_score = 0.0
        if stage_name in self._reservoirs:
            reservoir = self._reservoirs[stage_name]
            if reservoir.step_count > 0:
                dev_score = reservoir.deviation_score(reservoir._mean_ema)

        should_trip = self._retry_detector.should_trip_breaker(result, dev_score)
        return result, should_trip

    def get_all_tool_states(self) -> Dict[str, Dict]:
        """Get serializable state for all monitored tools."""
        return {
            name: {
                "step_count": r.step_count,
                "deviation_score": r.deviation_score(r._mean_ema) if r.step_count > 0 else 0.0,
                "variance": r.variance,
                "std": r.std,
            }
            for name, r in self._reservoirs.items()
        }
