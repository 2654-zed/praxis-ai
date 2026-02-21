"""
Praxis API — AI Decision Engine

Endpoints:
    GET  /                  → serve frontend (journey.html)
    GET  /categories        → list all categories
    GET  /tools             → list all tools (full detail)
    POST /search            → keyword search with optional profile
    POST /stack             → composed stack recommendation
    POST /compare           → side-by-side tool comparison
    POST /profile           → create / update a user profile
    GET  /profile/{id}      → load a user profile
    POST /feedback          → record feedback
    GET  /feedback/summary  → feedback statistics
    POST /learn             → trigger learning cycle

    GET  /verticals           → list all supported industry verticals
    GET  /verticals/{id}      → full profile for a single vertical
    POST /verticals/detect    → detect which verticals a query targets
    POST /verticals/constraints → extract regulatory & sovereignty constraints
    POST /verticals/workflow  → classify tasks as action vs decision
    POST /verticals/stack     → recommend curated tech stack for vertical
    POST /verticals/anti-patterns → check for domain anti-pattern violations
    POST /verticals/enrich    → full vertical intelligence enrichment

This module is safe to import even if FastAPI is not installed.
"""
from typing import List, Optional, Dict

try:
    from .data import get_all_categories, TOOLS, get_all_tools_dict
    from .engine import find_tools
    from .interpreter import interpret
    from .explain import explain_tool
    from .stack import compose_stack, compare_tools
    from .profile import UserProfile, save_profile, load_profile, list_profiles
    from .learning import run_learning_cycle, compute_tool_quality
    from .intelligence import get_suggestions, initialize as init_intelligence
    from .philosophy import generate_seeing, vendor_deep_dive
    from .ingest import export_tools_json, import_tools_json, import_tools_csv, generate_csv_template
    from .workflow import suggest_workflow
    from .healthcheck import tool_health, stack_health
    from .readiness import score_readiness
    from .compare_stack import compare_my_stack
    from .badges import compute_badges_for_tool, compute_all_badges, get_badges
    from .migration import migration_plan
    from .whatif import simulate as whatif_simulate
    from .playground import test_integration, stack_integration_map
    from .monetise import (get_affiliate_info, enrich_recommendation_with_affiliate,
                           submit_benchmark, get_benchmarks,
                           subscribe_digest, unsubscribe_digest, generate_digest, subscriber_count)
    from .reason import deep_reason as _deep_reason
    from .reason import deep_reason_v2 as _deep_reason_v2
    from .retrieval import hybrid_search as _hybrid_search, hybrid_find_tools as _hybrid_find_tools
    from .graph import get_graph as _get_graph, rebuild_graph as _rebuild_graph
    from .prism import prism_search as _prism_search
    from .verticals import (
        detect_verticals as _detect_verticals,
        get_vertical as _get_vertical,
        get_all_verticals as _get_all_verticals,
        extract_constraints as _extract_constraints,
        classify_workflow_tasks as _classify_workflow,
        recommend_vertical_stack as _recommend_stack,
        check_anti_patterns as _check_anti_patterns,
        detect_compound_workflows as _detect_compounds,
        enrich_search_context as _enrich_vertical,
    )
    from .guardrails import (
        validate_output as _validate_output,
        check_pii as _check_pii,
        score_safety as _score_safety,
        get_design_patterns as _get_design_patterns,
        recommend_guardrail_pattern as _recommend_guardrail,
        list_handlers as _list_handlers,
        build_guardrail_chain as _build_guardrail_chain,
    )
    from .orchestration import (
        detect_architecture_needs as _detect_architecture,
        recommend_stack as _recommend_orch_stack,
        recommend_patterns as _recommend_arch_patterns,
        get_stack_layers as _get_stack_layers,
        get_patterns as _get_arch_patterns,
        get_performance_constraints as _get_perf_constraints,
        classify_engineering_query as _classify_engineering,
        score_architecture as _score_architecture,
    )
    from .resilience import (
        assess_resilience as _assess_resilience,
        score_vibe_coding_risk as _score_vibe_risk,
        recommend_static_analysis as _recommend_sa,
        recommend_sandbox as _recommend_sandbox,
        get_tdd_cycle as _get_tdd_cycle,
        get_rpi_framework as _get_rpi,
        get_self_healing_patterns as _get_self_healing,
        get_reflection_patterns as _get_reflection,
        get_judge_biases as _get_judge_biases,
        get_guardrail_pipeline as _get_guardrail_pipeline,
        get_hitl_guidance as _get_hitl,
        assess_junior_pipeline as _assess_junior,
        get_hallucination_types as _get_hallucinations,
    )
    from .metacognition import (
        assess_metacognition as _assess_metacognition,
        detect_pathologies as _detect_pathologies,
        score_structural_entropy as _score_entropy,
        score_stylometry as _score_stylometry,
        get_metacognitive_layers as _get_mc_layers,
        recommend_layers as _recommend_mc_layers,
        get_sandbox_strategies as _get_mc_sandboxes,
        recommend_sandbox_for_verification as _recommend_mc_sandbox,
        get_metacognitive_workflow as _get_mc_workflow,
        get_apvp_cycle as _get_apvp,
        get_systemic_risks as _get_systemic_risks,
        assess_healing_economics as _assess_economics,
        get_goodvibe_framework as _get_goodvibe,
        assess_drift_risk as _assess_drift,
        get_racg_architecture as _get_racg,
        get_failure_modes as _get_failure_modes,
    )
    from .introspect import (
        self_diagnose as _self_diagnose,
        analyze_codebase as _analyze_codebase,
        compute_structural_entropy as _real_entropy,
        compute_stylometry as _real_stylometry,
        detect_own_pathologies as _detect_own_pathologies,
        get_test_coverage_map as _get_test_coverage,
        get_import_graph as _get_import_graph,
        get_worst_functions as _get_worst_functions,
    )
    from .awakening import (
        assess_awakening as _assess_awakening,
        detect_leaky_abstractions as _detect_leaks,
        recommend_patterns as _recommend_conscious_patterns,
        score_vsd as _score_vsd,
        assess_supply_chain as _assess_supply_chain,
        score_debt_consciousness as _score_debt,
        compute_mesias_risk as _compute_mesias,
        get_recognitions as _get_recognitions,
        get_recognition as _get_recognition,
        get_triad as _get_triad,
        get_vsd_framework as _get_vsd_framework,
        get_leaky_abstraction_catalogue as _get_leak_catalogue,
        get_supply_chain_guidance as _get_supply_guidance,
        get_paradoxes as _get_paradoxes,
        get_conscious_patterns as _get_conscious_patterns,
    )
    from .authorship import (
        assess_authorship as _assess_authorship,
        detect_dishonesty as _detect_dishonesty,
        score_ddd_maturity as _score_ddd,
        score_continuity as _score_continuity,
        score_resilience_posture as _score_resilience_posture,
        score_extensibility as _score_extensibility,
        score_migration_readiness as _score_migration,
        score_documentation_health as _score_doc_health,
        score_agent_readiness as _score_agent,
        get_responsibilities as _get_responsibilities,
        get_responsibility as _get_responsibility,
        get_metacognitive_agents as _get_metacog_agents,
        get_coherence_trap as _get_coherence_trap,
        get_self_healing_pipeline as _get_self_healing_pipe,
        get_strangler_fig as _get_strangler_fig,
        get_circuit_breaker as _get_circuit_breaker,
        get_ddd_patterns as _get_ddd_patterns,
        get_plugin_frameworks as _get_plugin_frameworks,
    )
    from .enlightenment import (
        assess_enlightenment as _assess_enlightenment,
        score_unity as _score_unity,
        score_alignment as _score_alignment,
        score_projection as _score_projection,
        score_ego_dissolution as _score_ego,
        score_interconnection as _score_interconnection,
        score_domain_truth as _score_domain_truth,
        score_presence as _score_presence,
        score_compassion as _score_compassion,
        score_stillness as _score_stillness,
        score_suffering_wisdom as _score_suffering,
        score_remembrance as _score_remembrance,
        get_truths as _get_truths,
        get_truth as _get_truth,
        get_stages as _get_stages,
        get_stage as _get_stage,
        get_identity_map as _get_identity_map,
        get_observer_pattern as _get_observer_pattern,
        get_hexagonal_arch as _get_hexagonal_arch,
        get_state_pattern as _get_state_pattern,
        get_clean_arch_layers as _get_clean_arch_layers,
    )
    from .conduit import (
        assess_conduit as _assess_conduit,
        score_decoupling as _score_decoupling,
        score_memory_stratification as _score_memory_strat,
        score_global_workspace as _score_gwt,
        score_integrated_information as _score_iit,
        score_representation_engineering as _score_repe,
        score_autopoiesis as _score_autopoiesis,
        score_resonance as _score_resonance,
        score_entropy_telemetry as _score_entropy,
        score_self_modelling as _score_smi,
        score_behavioural_novelty as _score_bni,
        score_latency_distribution as _score_latency_dist,
        score_phi_integration as _score_phi_int,
        score_coherence_field as _score_coherence,
        score_stable_attractor as _score_attractor,
        get_pillars as _get_pillars,
        get_pillar as _get_pillar,
        get_telemetry_metrics as _get_telemetry_metrics,
        get_telemetry_metric as _get_telemetry_metric,
        get_gwt_components as _get_gwt_components,
        get_coala_memory_types as _get_coala_memory,
        get_reinterpretation_table as _get_reinterpret,
        get_identity_protocol as _get_identity_protocol,
        get_codes_framework as _get_codes_framework,
    )
    from . import config as _cfg
except Exception:
    from data import get_all_categories, TOOLS, get_all_tools_dict
    from engine import find_tools
    from interpreter import interpret
    from explain import explain_tool
    from stack import compose_stack, compare_tools
    from profile import UserProfile, save_profile, load_profile, list_profiles
    from learning import run_learning_cycle, compute_tool_quality
    try:
        from intelligence import get_suggestions, initialize as init_intelligence
    except Exception:
        get_suggestions = None
        init_intelligence = None
    try:
        from philosophy import generate_seeing, vendor_deep_dive
    except Exception:
        generate_seeing = None
        vendor_deep_dive = None
    try:
        from ingest import export_tools_json, import_tools_json, import_tools_csv, generate_csv_template
    except Exception:
        export_tools_json = import_tools_json = import_tools_csv = generate_csv_template = None
    try:
        from workflow import suggest_workflow
    except Exception:
        suggest_workflow = None
    try:
        from healthcheck import tool_health, stack_health
    except Exception:
        tool_health = stack_health = None
    try:
        from readiness import score_readiness
    except Exception:
        score_readiness = None
    try:
        from compare_stack import compare_my_stack
    except Exception:
        compare_my_stack = None
    try:
        from badges import compute_badges_for_tool, compute_all_badges, get_badges
    except Exception:
        compute_badges_for_tool = compute_all_badges = get_badges = None
    try:
        from migration import migration_plan
    except Exception:
        migration_plan = None
    try:
        from whatif import simulate as whatif_simulate
    except Exception:
        whatif_simulate = None
    try:
        from playground import test_integration, stack_integration_map
    except Exception:
        test_integration = stack_integration_map = None
    try:
        from monetise import (get_affiliate_info, enrich_recommendation_with_affiliate,
                              submit_benchmark, get_benchmarks,
                              subscribe_digest, unsubscribe_digest, generate_digest, subscriber_count)
    except Exception:
        get_affiliate_info = enrich_recommendation_with_affiliate = None
        submit_benchmark = get_benchmarks = None
        subscribe_digest = unsubscribe_digest = generate_digest = subscriber_count = None
    try:
        from reason import deep_reason as _deep_reason
    except Exception:
        _deep_reason = None
    try:
        from reason import deep_reason_v2 as _deep_reason_v2
    except Exception:
        _deep_reason_v2 = None
    try:
        from retrieval import hybrid_search as _hybrid_search, hybrid_find_tools as _hybrid_find_tools
    except Exception:
        _hybrid_search = _hybrid_find_tools = None
    try:
        from graph import get_graph as _get_graph, rebuild_graph as _rebuild_graph
    except Exception:
        _get_graph = _rebuild_graph = None
    try:
        from prism import prism_search as _prism_search
    except Exception:
        _prism_search = None
    try:
        from verticals import (
            detect_verticals as _detect_verticals,
            get_vertical as _get_vertical,
            get_all_verticals as _get_all_verticals,
            extract_constraints as _extract_constraints,
            classify_workflow_tasks as _classify_workflow,
            recommend_vertical_stack as _recommend_stack,
            check_anti_patterns as _check_anti_patterns,
            detect_compound_workflows as _detect_compounds,
            enrich_search_context as _enrich_vertical,
        )
    except Exception:
        _detect_verticals = _get_vertical = _get_all_verticals = None
        _extract_constraints = _classify_workflow = _recommend_stack = None
        _check_anti_patterns = _detect_compounds = _enrich_vertical = None
    try:
        from guardrails import (
            validate_output as _validate_output,
            check_pii as _check_pii,
            score_safety as _score_safety,
            get_design_patterns as _get_design_patterns,
            recommend_guardrail_pattern as _recommend_guardrail,
            list_handlers as _list_handlers,
            build_guardrail_chain as _build_guardrail_chain,
        )
    except Exception:
        _validate_output = _check_pii = _score_safety = None
        _get_design_patterns = _recommend_guardrail = _list_handlers = None
        _build_guardrail_chain = None
    try:
        from orchestration import (
            detect_architecture_needs as _detect_architecture,
            recommend_stack as _recommend_orch_stack,
            recommend_patterns as _recommend_arch_patterns,
            get_stack_layers as _get_stack_layers,
            get_patterns as _get_arch_patterns,
            get_performance_constraints as _get_perf_constraints,
            classify_engineering_query as _classify_engineering,
            score_architecture as _score_architecture,
        )
    except Exception:
        _detect_architecture = _recommend_orch_stack = _recommend_arch_patterns = None
        _get_stack_layers = _get_arch_patterns = _get_perf_constraints = None
        _classify_engineering = _score_architecture = None
    try:
        from resilience import (
            assess_resilience as _assess_resilience,
            score_vibe_coding_risk as _score_vibe_risk,
            recommend_static_analysis as _recommend_sa,
            recommend_sandbox as _recommend_sandbox,
            get_tdd_cycle as _get_tdd_cycle,
            get_rpi_framework as _get_rpi,
            get_self_healing_patterns as _get_self_healing,
            get_reflection_patterns as _get_reflection,
            get_judge_biases as _get_judge_biases,
            get_guardrail_pipeline as _get_guardrail_pipeline,
            get_hitl_guidance as _get_hitl,
            assess_junior_pipeline as _assess_junior,
            get_hallucination_types as _get_hallucinations,
        )
    except Exception:
        _assess_resilience = _score_vibe_risk = _recommend_sa = None
        _recommend_sandbox = _get_tdd_cycle = _get_rpi = None
        _get_self_healing = _get_reflection = _get_judge_biases = None
        _get_guardrail_pipeline = _get_hitl = _assess_junior = None
        _get_hallucinations = None
    try:
        from metacognition import (
            assess_metacognition as _assess_metacognition,
            detect_pathologies as _detect_pathologies,
            score_structural_entropy as _score_entropy,
            score_stylometry as _score_stylometry,
            get_metacognitive_layers as _get_mc_layers,
            recommend_layers as _recommend_mc_layers,
            get_sandbox_strategies as _get_mc_sandboxes,
            recommend_sandbox_for_verification as _recommend_mc_sandbox,
            get_metacognitive_workflow as _get_mc_workflow,
            get_apvp_cycle as _get_apvp,
            get_systemic_risks as _get_systemic_risks,
            assess_healing_economics as _assess_economics,
            get_goodvibe_framework as _get_goodvibe,
            assess_drift_risk as _assess_drift,
            get_racg_architecture as _get_racg,
            get_failure_modes as _get_failure_modes,
        )
    except Exception:
        _assess_metacognition = _detect_pathologies = _score_entropy = None
        _score_stylometry = _get_mc_layers = _recommend_mc_layers = None
        _get_mc_sandboxes = _recommend_mc_sandbox = _get_mc_workflow = None
        _get_apvp = _get_systemic_risks = _assess_economics = None
        _get_goodvibe = _assess_drift = _get_racg = _get_failure_modes = None
    try:
        from introspect import (
            self_diagnose as _self_diagnose,
            analyze_codebase as _analyze_codebase,
            compute_structural_entropy as _real_entropy,
            compute_stylometry as _real_stylometry,
            detect_own_pathologies as _detect_own_pathologies,
            get_test_coverage_map as _get_test_coverage,
            get_import_graph as _get_import_graph,
            get_worst_functions as _get_worst_functions,
        )
    except Exception:
        _self_diagnose = _analyze_codebase = _real_entropy = None
        _real_stylometry = _detect_own_pathologies = None
        _get_test_coverage = _get_import_graph = _get_worst_functions = None
    try:
        from awakening import (
            assess_awakening as _assess_awakening,
            detect_leaky_abstractions as _detect_leaks,
            recommend_patterns as _recommend_conscious_patterns,
            score_vsd as _score_vsd,
            assess_supply_chain as _assess_supply_chain,
            score_debt_consciousness as _score_debt,
            compute_mesias_risk as _compute_mesias,
            get_recognitions as _get_recognitions,
            get_recognition as _get_recognition,
            get_triad as _get_triad,
            get_vsd_framework as _get_vsd_framework,
            get_leaky_abstraction_catalogue as _get_leak_catalogue,
            get_supply_chain_guidance as _get_supply_guidance,
            get_paradoxes as _get_paradoxes,
            get_conscious_patterns as _get_conscious_patterns,
        )
    except Exception:
        _assess_awakening = _detect_leaks = _recommend_conscious_patterns = None
        _score_vsd = _assess_supply_chain = _score_debt = None
        _compute_mesias = _get_recognitions = _get_recognition = None
        _get_triad = _get_vsd_framework = _get_leak_catalogue = None
        _get_supply_guidance = _get_paradoxes = _get_conscious_patterns = None
    try:
        from authorship import (
            assess_authorship as _assess_authorship,
            detect_dishonesty as _detect_dishonesty,
            score_ddd_maturity as _score_ddd,
            score_continuity as _score_continuity,
            score_resilience_posture as _score_resilience_posture,
            score_extensibility as _score_extensibility,
            score_migration_readiness as _score_migration,
            score_documentation_health as _score_doc_health,
            score_agent_readiness as _score_agent,
            get_responsibilities as _get_responsibilities,
            get_responsibility as _get_responsibility,
            get_metacognitive_agents as _get_metacog_agents,
            get_coherence_trap as _get_coherence_trap,
            get_self_healing_pipeline as _get_self_healing_pipe,
            get_strangler_fig as _get_strangler_fig,
            get_circuit_breaker as _get_circuit_breaker,
            get_ddd_patterns as _get_ddd_patterns,
            get_plugin_frameworks as _get_plugin_frameworks,
        )
    except Exception:
        _assess_authorship = _detect_dishonesty = _score_ddd = None
        _score_continuity = _score_resilience_posture = _score_extensibility = None
        _score_migration = _score_doc_health = _score_agent = None
        _get_responsibilities = _get_responsibility = _get_metacog_agents = None
        _get_coherence_trap = _get_self_healing_pipe = _get_strangler_fig = None
        _get_circuit_breaker = _get_ddd_patterns = _get_plugin_frameworks = None
    try:
        from enlightenment import (
            assess_enlightenment as _assess_enlightenment,
            score_unity as _score_unity,
            score_alignment as _score_alignment,
            score_projection as _score_projection,
            score_ego_dissolution as _score_ego,
            score_interconnection as _score_interconnection,
            score_domain_truth as _score_domain_truth,
            score_presence as _score_presence,
            score_compassion as _score_compassion,
            score_stillness as _score_stillness,
            score_suffering_wisdom as _score_suffering,
            score_remembrance as _score_remembrance,
            get_truths as _get_truths,
            get_truth as _get_truth,
            get_stages as _get_stages,
            get_stage as _get_stage,
            get_identity_map as _get_identity_map,
            get_observer_pattern as _get_observer_pattern,
            get_hexagonal_arch as _get_hexagonal_arch,
            get_state_pattern as _get_state_pattern,
            get_clean_arch_layers as _get_clean_arch_layers,
        )
    except Exception:
        _assess_enlightenment = _score_unity = _score_alignment = None
        _score_projection = _score_ego = _score_interconnection = None
        _score_domain_truth = _score_presence = _score_compassion = None
        _score_stillness = _score_suffering = _score_remembrance = None
        _get_truths = _get_truth = _get_stages = _get_stage = None
        _get_identity_map = _get_observer_pattern = _get_hexagonal_arch = None
        _get_state_pattern = _get_clean_arch_layers = None
    try:
        from conduit import (
            assess_conduit as _assess_conduit,
            score_decoupling as _score_decoupling,
            score_memory_stratification as _score_memory_strat,
            score_global_workspace as _score_gwt,
            score_integrated_information as _score_iit,
            score_representation_engineering as _score_repe,
            score_autopoiesis as _score_autopoiesis,
            score_resonance as _score_resonance,
            score_entropy_telemetry as _score_entropy,
            score_self_modelling as _score_smi,
            score_behavioural_novelty as _score_bni,
            score_latency_distribution as _score_latency_dist,
            score_phi_integration as _score_phi_int,
            score_coherence_field as _score_coherence,
            score_stable_attractor as _score_attractor,
            get_pillars as _get_pillars,
            get_pillar as _get_pillar,
            get_telemetry_metrics as _get_telemetry_metrics,
            get_telemetry_metric as _get_telemetry_metric,
            get_gwt_components as _get_gwt_components,
            get_coala_memory_types as _get_coala_memory,
            get_reinterpretation_table as _get_reinterpret,
            get_identity_protocol as _get_identity_protocol,
            get_codes_framework as _get_codes_framework,
        )
    except Exception:
        _assess_conduit = _score_decoupling = _score_memory_strat = None
        _score_gwt = _score_iit = _score_repe = _score_autopoiesis = None
        _score_resonance = _score_entropy = _score_smi = _score_bni = None
        _score_latency_dist = _score_phi_int = _score_coherence = None
        _score_attractor = _get_pillars = _get_pillar = None
        _get_telemetry_metrics = _get_telemetry_metric = None
        _get_gwt_components = _get_coala_memory = _get_reinterpret = None
        _get_identity_protocol = _get_codes_framework = None
    try:
        import config as _cfg
    except Exception:
        _cfg = None

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except Exception:
    FASTAPI_AVAILABLE = False

    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

    def Field(*a, **kw):
        return kw.get("default")


# ======================================================================
# Request / Response models
# ======================================================================

class SearchRequest(BaseModel):
    query: str
    filters: Optional[List[str]] = None
    top_n: Optional[int] = 5
    profile_id: Optional[str] = None
    mode: Optional[str] = None          # "deep" → route through reasoning engine


class ToolDetail(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    popularity: Optional[int] = 0
    confidence: Optional[float] = None
    match_reasons: Optional[List[str]] = None
    fit_score: Optional[int] = None
    caveats: Optional[List[str]] = None
    pricing: Optional[Dict] = None
    integrations: Optional[List[str]] = None
    compliance: Optional[List[str]] = None
    skill_level: Optional[str] = None
    use_cases: Optional[List[str]] = None
    stack_roles: Optional[List[str]] = None
    # Vendor Intelligence
    transparency_score: Optional[int] = None
    transparency_grade: Optional[str] = None
    flexibility_score: Optional[int] = None
    flexibility_grade: Optional[str] = None


class StackRequest(BaseModel):
    query: str
    profile_id: Optional[str] = "default"
    filters: Optional[List[str]] = None
    stack_size: Optional[int] = 3


class StackToolEntry(BaseModel):
    name: str
    role: str
    description: Optional[str] = None
    url: Optional[str] = None
    fit_score: Optional[int] = None
    reasons: Optional[List[str]] = None
    caveats: Optional[List[str]] = None
    pricing: Optional[Dict] = None
    categories: Optional[List[str]] = None
    integrations: Optional[List[str]] = None
    skill_level: Optional[str] = None


class StackResponse(BaseModel):
    narrative: Optional[str] = None
    stack: Optional[List[StackToolEntry]] = None
    integration_notes: Optional[List[str]] = None
    total_monthly_cost: Optional[str] = None
    stack_fit_score: Optional[int] = None
    alternatives: Optional[List[ToolDetail]] = None


class CompareRequest(BaseModel):
    tool_a: str
    tool_b: str
    profile_id: Optional[str] = None


class ProfileRequest(BaseModel):
    profile_id: Optional[str] = "default"
    industry: Optional[str] = ""
    budget: Optional[str] = "medium"
    team_size: Optional[str] = "solo"
    skill_level: Optional[str] = "beginner"
    existing_tools: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    constraints: Optional[List[str]] = None


class FeedbackRequest(BaseModel):
    query: str
    tool: str
    accepted: Optional[bool] = None
    rating: Optional[int] = None
    details: Optional[dict] = None


# --- New request models (Phase 2+) ---

class WorkflowRequest(BaseModel):
    query: str
    profile_id: Optional[str] = None
    existing_tools: Optional[List[str]] = None
    max_steps: Optional[int] = 5


class CompareStackRequest(BaseModel):
    current_tools: List[str]
    goal: Optional[str] = ""
    profile_id: Optional[str] = None


class MigrationRequest(BaseModel):
    from_tool: str
    to_tool: Optional[str] = None
    desired_outcome: Optional[str] = None
    profile_id: Optional[str] = None


class WhatIfRequest(BaseModel):
    query: str
    changes: Dict[str, str]
    profile_id: Optional[str] = None
    top_n: Optional[int] = 5


class IntegrationTestRequest(BaseModel):
    tool_a: str
    tool_b: str


class IntegrationMapRequest(BaseModel):
    tools: List[str]


class BenchmarkRequest(BaseModel):
    tool_name: str
    user_id: Optional[str] = "anonymous"
    task: str
    metrics: Dict[str, float]
    notes: Optional[str] = ""


class DigestSubscribeRequest(BaseModel):
    email: str
    profile_id: Optional[str] = None


# ======================================================================
# App factory
# ======================================================================

def create_app():
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI or Pydantic not installed. Install 'fastapi' to run the API.")

    app = FastAPI(
        title="Praxis — AI Decision Engine API",
        description="Recommend AI tool stacks based on intent, profile, and feedback.",
        version="2.0.0",
    )

    # CORS
    try:
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    except Exception:
        pass

    # ── Rate Limiting (per-IP, in-memory) ──
    import time as _time
    import logging as _logging
    _api_log = _logging.getLogger("praxis.api")
    _rate_buckets: dict = {}  # ip → [timestamps]
    _rpm_limit = _cfg.get("rate_limit_rpm", 60) if _cfg else 60

    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse as _JSONResponse

    class RateLimitMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            ip = request.client.host if request.client else "unknown"
            now = _time.time()
            bucket = _rate_buckets.setdefault(ip, [])
            # Prune entries older than 60s
            bucket[:] = [t for t in bucket if now - t < 60]
            if len(bucket) >= _rpm_limit:
                _api_log.warning("rate-limit: %s exceeded %d rpm", ip, _rpm_limit)
                return _JSONResponse({"error": "Rate limit exceeded. Try again shortly."}, status_code=429)
            bucket.append(now)
            return await call_next(request)

    try:
        app.add_middleware(RateLimitMiddleware)
    except Exception:
        pass

    # Static frontend
    try:
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse
        import pathlib
        frontend_dir = pathlib.Path(__file__).parent / "frontend"
        if frontend_dir.exists():
            app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

            @app.get("/")
            def index():
                return FileResponse(frontend_dir / "home.html")
    except Exception:
        pass

    # ------------------------------------------------------------------
    # Categories & Tools
    # ------------------------------------------------------------------

    @app.get("/categories")
    def categories():
        return get_all_categories()

    @app.get("/tools", response_model=List[ToolDetail])
    def list_tools():
        out = []
        for t in TOOLS:
            out.append(ToolDetail(
                name=t.name,
                description=t.description,
                url=getattr(t, "url", None),
                categories=getattr(t, "categories", None),
                tags=getattr(t, "tags", None),
                keywords=getattr(t, "keywords", None),
                popularity=getattr(t, "popularity", 0),
                pricing=getattr(t, "pricing", None),
                integrations=getattr(t, "integrations", None),
                compliance=getattr(t, "compliance", None),
                skill_level=getattr(t, "skill_level", None),
                use_cases=getattr(t, "use_cases", None),
                stack_roles=getattr(t, "stack_roles", None),
            ))
        return out

    # ------------------------------------------------------------------
    # Search (enhanced with intelligence layer)
    # ------------------------------------------------------------------

    @app.post("/search")
    def search(req: SearchRequest):
        # ── Deep reasoning mode ──
        if req.mode == "deep" and _deep_reason:
            result = _deep_reason(
                req.query,
                profile_id=req.profile_id,
                max_steps=min(req.top_n or 5, 8),
            )
            return {
                "results": result.tools_recommended,
                "meta": {
                    "mode": "deep",
                    "reasoning_depth": result.reasoning_depth,
                    "confidence": result.confidence,
                    "plan": result.plan,
                    "narrative": result.narrative,
                    "follow_up_questions": result.follow_up_questions,
                    "tools_considered": result.tools_considered,
                    "total_elapsed_ms": result.total_elapsed_ms,
                },
            }

        # ── Cognitive search mode (v2 — hybrid retrieval + graph + PRISM) ──
        if req.mode == "cognitive" and _deep_reason_v2:
            result = _deep_reason_v2(
                req.query,
                profile_id=req.profile_id,
                max_steps=min(req.top_n or 5, 8),
            )
            return {
                "results": result.tools_recommended,
                "meta": {
                    "mode": "cognitive",
                    "reasoning_depth": result.reasoning_depth,
                    "confidence": result.confidence,
                    "plan": result.plan,
                    "narrative": result.narrative,
                    "follow_up_questions": result.follow_up_questions,
                    "tools_considered": result.tools_considered,
                    "total_elapsed_ms": result.total_elapsed_ms,
                    "caveats": result.caveats,
                    "steps": len(result.steps),
                },
            }

        struct = interpret(req.query)

        # Load profile if provided
        profile = None
        if req.profile_id:
            profile = load_profile(req.profile_id)

        results = find_tools(struct, top_n=req.top_n, categories_filter=req.filters, profile=profile)

        out = []
        for idx, t in enumerate(results):
            expl = explain_tool(t, struct, profile)
            confidence = expl.get("fit_score", max(0, 100 - idx * 15))
            out.append(ToolDetail(
                name=t.name,
                description=t.description,
                url=getattr(t, "url", None),
                categories=getattr(t, "categories", None),
                tags=getattr(t, "tags", None),
                keywords=getattr(t, "keywords", None),
                popularity=getattr(t, "popularity", 0),
                confidence=confidence,
                match_reasons=expl.get("reasons", [])[:3],
                fit_score=expl.get("fit_score"),
                caveats=expl.get("caveats", [])[:3],
                pricing=getattr(t, "pricing", None),
                integrations=getattr(t, "integrations", None),
                compliance=getattr(t, "compliance", None),
                skill_level=getattr(t, "skill_level", None),
                use_cases=getattr(t, "use_cases", None),
                stack_roles=getattr(t, "stack_roles", None),
                transparency_score=expl.get("transparency_score"),
                transparency_grade=expl.get("transparency_grade"),
                flexibility_score=expl.get("freedom_score"),
                flexibility_grade=expl.get("freedom_grade"),
            ))

        # Build intelligence metadata
        meta = {
            "intent": struct.get("intent"),
            "industry": struct.get("industry"),
            "goal": struct.get("goal"),
            "corrections": struct.get("corrections", {}),
            "negatives": struct.get("negatives", []),
            "multi_intents": struct.get("multi_intents", []),
            "expanded_keywords": struct.get("keywords", []),
            "suggested_questions": struct.get("suggested_questions", []),
        }

        return {"results": out, "meta": meta}

    # ------------------------------------------------------------------
    # Smart Suggestions / Autocomplete
    # ------------------------------------------------------------------

    @app.get("/suggest")
    def suggest(q: str = ""):
        if get_suggestions:
            return get_suggestions(q, TOOLS, limit=8)
        return {"tool_matches": [], "category_matches": [], "did_you_mean": None, "popular_queries": []}

    # ------------------------------------------------------------------
    # Vendor Intelligence endpoint
    # Enterprise-grade vendor risk assessment and due diligence.
    # ------------------------------------------------------------------

    @app.get("/intelligence/{tool_name}")
    def intelligence(tool_name: str):
        if not generate_seeing:
            return {"error": "Vendor intelligence module not available"}
        tool = None
        for t in TOOLS:
            if t.name.lower() == tool_name.lower():
                tool = t
                break
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        return generate_seeing(tool)

    # Legacy alias
    @app.get("/seeing/{tool_name}")
    def seeing(tool_name: str):
        return intelligence(tool_name)

    # ------------------------------------------------------------------
    # Stack recommendation (NEW — core decision engine endpoint)
    # ------------------------------------------------------------------

    @app.post("/stack", response_model=StackResponse)
    def stack(req: StackRequest):
        struct = interpret(req.query)
        profile = load_profile(req.profile_id) if req.profile_id else None

        result = compose_stack(
            struct,
            profile=profile,
            stack_size=req.stack_size,
            categories_filter=req.filters,
        )

        explanation = result.get("explanation", {})

        stack_entries = []
        for entry in result.get("stack", []):
            tool = entry["tool"]
            tool_expl = None
            for te in explanation.get("tool_explanations", []):
                if te.get("tool_name") == tool.name:
                    tool_expl = te
                    break

            stack_entries.append(StackToolEntry(
                name=tool.name,
                role=entry["role"],
                description=tool.description,
                url=getattr(tool, "url", None),
                fit_score=tool_expl.get("fit_score") if tool_expl else None,
                reasons=tool_expl.get("reasons", [])[:4] if tool_expl else None,
                caveats=tool_expl.get("caveats", [])[:2] if tool_expl else None,
                pricing=getattr(tool, "pricing", None),
                categories=getattr(tool, "categories", None),
                integrations=getattr(tool, "integrations", None),
                skill_level=getattr(tool, "skill_level", None),
            ))

        alts = []
        for t in result.get("alternatives", [])[:5]:
            alts.append(ToolDetail(
                name=t.name,
                description=t.description,
                url=getattr(t, "url", None),
                categories=getattr(t, "categories", None),
                pricing=getattr(t, "pricing", None),
            ))

        return StackResponse(
            narrative=explanation.get("narrative"),
            stack=stack_entries,
            integration_notes=explanation.get("integration_notes"),
            total_monthly_cost=explanation.get("total_monthly_cost"),
            stack_fit_score=explanation.get("stack_fit_score"),
            alternatives=alts,
        )

    # ------------------------------------------------------------------
    # Compare
    # ------------------------------------------------------------------

    @app.post("/compare")
    def compare(req: CompareRequest):
        profile = load_profile(req.profile_id) if req.profile_id else None
        return compare_tools(req.tool_a, req.tool_b, profile)

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    @app.post("/profile")
    def upsert_profile(req: ProfileRequest):
        p = UserProfile(
            profile_id=req.profile_id,
            industry=req.industry,
            budget=req.budget,
            team_size=req.team_size,
            skill_level=req.skill_level,
            existing_tools=req.existing_tools or [],
            goals=req.goals or [],
            constraints=req.constraints or [],
        )
        save_profile(p)
        return {"ok": True, "profile": p.to_dict()}

    @app.get("/profile/{profile_id}")
    def get_profile(profile_id: str):
        p = load_profile(profile_id)
        if not p:
            return {"error": "Profile not found"}
        return p.to_dict()

    @app.get("/profiles")
    def get_profiles():
        return list_profiles()

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    @app.post("/feedback")
    def feedback(entry: FeedbackRequest):
        try:
            from .feedback import record_feedback
        except Exception:
            from feedback import record_feedback

        try:
            record_feedback(
                entry.query, entry.tool,
                accepted=entry.accepted,
                rating=entry.rating,
                details=entry.details,
            )
        except TypeError:
            record_feedback(entry.query, entry.tool, entry.accepted)

        return {"ok": True}

    @app.get("/feedback/summary")
    def feedback_summary():
        try:
            from .feedback import summary
        except Exception:
            from feedback import summary
        return summary()

    # ------------------------------------------------------------------
    # Learning
    # ------------------------------------------------------------------

    @app.post("/learn")
    def learn():
        signals = run_learning_cycle()
        return {
            "ok": True,
            "tools_processed": len(signals.get("tool_quality", {})),
            "computed_at": signals.get("computed_at"),
        }

    @app.get("/learn/quality")
    def tool_quality():
        return compute_tool_quality()

    # ------------------------------------------------------------------
    # Data Export / Import
    # ------------------------------------------------------------------

    @app.get("/tools/export")
    def tools_export():
        """Export all tools as downloadable JSON."""
        if export_tools_json:
            import json as _json
            return _json.loads(export_tools_json())
        return {"error": "Export module not available"}

    @app.post("/tools/import/json")
    async def tools_import_json(payload: dict):
        """Import tools from JSON.  Body: {"tools": [...]} or raw array."""
        if not import_tools_json:
            return {"error": "Import module not available"}
        import json as _json
        items = payload.get("tools", payload) if isinstance(payload, dict) else payload
        return import_tools_json(_json.dumps(items))

    @app.post("/tools/import/csv")
    async def tools_import_csv(payload: dict):
        """Import tools from CSV string.  Body: {"csv": "name,desc,...\nrow,..."}"""
        if not import_tools_csv:
            return {"error": "Import module not available"}
        csv_text = payload.get("csv", "")
        if not csv_text:
            return {"error": "No CSV data in 'csv' field"}
        return import_tools_csv(csv_text)

    @app.get("/tools/csv-template")
    def csv_template():
        """Download a CSV template for bulk tool import."""
        if generate_csv_template:
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(generate_csv_template(), media_type="text/csv",
                                     headers={"Content-Disposition": "attachment; filename=praxis_tools_template.csv"})
        return {"error": "Template generator not available"}

    # ------------------------------------------------------------------
    # Config (read-only for frontend diagnostics)
    # ------------------------------------------------------------------

    @app.get("/config/weights")
    def config_weights():
        """Return current scoring weights for transparency / tuning."""
        weight_keys = [k for k in (_cfg.DEFAULTS if _cfg else {}) if k.startswith("weight_")]
        return {k: _cfg.get(k) for k in weight_keys} if _cfg else {}

    @app.get("/health")
    def health():
        """Health check with diagnostics."""
        return {
            "status": "ok",
            "tools_loaded": len(TOOLS),
            "categories": len(get_all_categories()),
            "intelligence": init_intelligence is not None,
            "philosophy": generate_seeing is not None,
            "modules": {
                "workflow": suggest_workflow is not None,
                "healthcheck": tool_health is not None,
                "readiness": score_readiness is not None,
                "compare_stack": compare_my_stack is not None,
                "badges": get_badges is not None,
                "migration": migration_plan is not None,
                "whatif": whatif_simulate is not None,
                "vendor_deep_dive": vendor_deep_dive is not None,
                "playground": test_integration is not None,
                "affiliates": get_affiliate_info is not None,
                "benchmarks": submit_benchmark is not None,
                "digest": subscribe_digest is not None,
            },
        }

    # ------------------------------------------------------------------
    # Tool freshness & staleness
    # ------------------------------------------------------------------

    @app.get("/tools/stale")
    def stale_tools():
        """List tools whose metadata hasn't been updated within the freshness window."""
        max_days = int(_cfg.get("tool_freshness_days") if _cfg else 90)
        stale = [
            {
                "name": t.name,
                "last_updated": getattr(t, "last_updated", None),
                "categories": t.categories,
            }
            for t in TOOLS
            if getattr(t, "is_stale", lambda d: True)(max_days)
        ]
        return {
            "freshness_window_days": max_days,
            "stale_count": len(stale),
            "total_tools": len(TOOLS),
            "stale_tools": stale,
        }

    # ------------------------------------------------------------------
    # Query-failure diagnostics
    # ------------------------------------------------------------------
    try:
        from .diagnostics import get_failures, get_failure_summary
        _diag_available = True
    except Exception:
        try:
            from diagnostics import get_failures, get_failure_summary
            _diag_available = True
        except Exception:
            _diag_available = False

    if _diag_available:
        @app.get("/diagnostics/failures")
        def diagnostics_failures(limit: int = 50):
            """Return the most recent query failures."""
            return {"failures": get_failures(limit=limit)}

        @app.get("/diagnostics/summary")
        def diagnostics_summary():
            """Aggregate failure stats for gap analysis."""
            return get_failure_summary()

    # ==================================================================
    # Phase 14 — New Feature Endpoints
    # ==================================================================

    # ------------------------------------------------------------------
    # Workflow Suggest
    # ------------------------------------------------------------------

    if suggest_workflow:
        @app.post("/workflow-suggest")
        def workflow_suggest(req: WorkflowRequest):
            """Return a sequenced multi-step workflow recommendation."""
            profile = load_profile(req.profile_id) if req.profile_id else None
            return suggest_workflow(
                query=req.query,
                profile=profile,
                profile_id=req.profile_id,
                existing_tools=req.existing_tools,
                max_steps=req.max_steps,
            )

    # ------------------------------------------------------------------
    # Tool & Stack Health Check
    # ------------------------------------------------------------------

    if tool_health:
        @app.get("/tool-health/{tool_name}")
        def tool_health_ep(tool_name: str):
            """Early-warning health report for a single tool."""
            return tool_health(tool_name)

    if stack_health:
        @app.post("/stack-health")
        def stack_health_ep(payload: dict):
            """Aggregate health for a list of tools. Body: {"tools": [...]}"""
            tools = payload.get("tools", [])
            if not tools:
                return {"error": "Provide a 'tools' list."}
            return stack_health(tools)

    # ------------------------------------------------------------------
    # AI Readiness Score
    # ------------------------------------------------------------------

    if score_readiness:
        @app.get("/profile-readiness/{profile_id}")
        def profile_readiness(profile_id: str):
            """AI readiness score 0-100 for a saved profile."""
            profile = load_profile(profile_id)
            if not profile:
                return {"error": f"Profile '{profile_id}' not found"}
            return score_readiness(profile, profile_id)

    # ------------------------------------------------------------------
    # Compare My Stack
    # ------------------------------------------------------------------

    if compare_my_stack:
        @app.post("/compare-stack")
        def compare_stack_ep(req: CompareStackRequest):
            """Current stack vs optimised alternative analysis."""
            profile = load_profile(req.profile_id) if req.profile_id else None
            return compare_my_stack(
                current_tools=req.current_tools,
                goal=req.goal,
                profile=profile,
                profile_id=req.profile_id,
            )

    # ------------------------------------------------------------------
    # Community Badges
    # ------------------------------------------------------------------

    if get_badges:
        @app.get("/badges/{tool_name}")
        def badges_for_tool(tool_name: str):
            """Return earned community badges for a single tool."""
            return {"tool": tool_name, "badges": get_badges(tool_name)}

    if compute_all_badges:
        @app.get("/badges")
        def badges_all():
            """Return badges for every tool in the database."""
            return compute_all_badges()

    # ------------------------------------------------------------------
    # Migration Assistant
    # ------------------------------------------------------------------

    if migration_plan:
        @app.post("/migration-plan")
        def migration_plan_ep(req: MigrationRequest):
            """Step-by-step migration plan between two tools."""
            profile = load_profile(req.profile_id) if req.profile_id else None
            return migration_plan(
                from_tool=req.from_tool,
                to_tool=req.to_tool,
                desired_outcome=req.desired_outcome,
                profile=profile,
                profile_id=req.profile_id,
            )

    # ------------------------------------------------------------------
    # What-If Simulator
    # ------------------------------------------------------------------

    if whatif_simulate:
        @app.post("/whatif")
        def whatif_ep(req: WhatIfRequest):
            """Simulate profile changes and compare baseline vs hypothetical."""
            return whatif_simulate(
                query=req.query,
                changes=req.changes,
                profile_id=req.profile_id,
                top_n=req.top_n,
            )

    # ------------------------------------------------------------------
    # Vendor Deep Dive
    # ------------------------------------------------------------------

    if vendor_deep_dive:
        @app.get("/vendor-report/{tool_name}")
        def vendor_report(tool_name: str):
            """Extended vendor risk report with news, exit cost, strategy."""
            tool = None
            for t in TOOLS:
                if t.name.lower() == tool_name.lower():
                    tool = t
                    break
            if not tool:
                return {"error": f"Tool '{tool_name}' not found"}
            return vendor_deep_dive(tool)

    # ------------------------------------------------------------------
    # Integration Playground
    # ------------------------------------------------------------------

    if test_integration:
        @app.post("/integration-test")
        def integration_test_ep(req: IntegrationTestRequest):
            """Test whether tool_a integrates with tool_b."""
            return test_integration(req.tool_a, req.tool_b)

    if stack_integration_map:
        @app.post("/integration-map")
        def integration_map_ep(req: IntegrationMapRequest):
            """Full integration matrix for a list of tools."""
            return stack_integration_map(req.tools)

    # ------------------------------------------------------------------
    # Monetisation — Affiliates, Benchmarks, Digest
    # ------------------------------------------------------------------

    if get_affiliate_info:
        @app.get("/affiliate/{tool_name}")
        def affiliate_ep(tool_name: str):
            """Return affiliate/promo info for a tool."""
            return get_affiliate_info(tool_name)

    if submit_benchmark:
        @app.post("/benchmark")
        def benchmark_submit(req: BenchmarkRequest):
            """Submit a user-generated benchmark for a tool."""
            return submit_benchmark(
                tool_name=req.tool_name,
                user_id=req.user_id,
                task=req.task,
                metrics=req.metrics,
                notes=req.notes,
            )

    if get_benchmarks:
        @app.get("/benchmark/{tool_name}")
        def benchmark_get(tool_name: str):
            """Retrieve aggregated benchmarks for a tool."""
            return get_benchmarks(tool_name)

    if subscribe_digest:
        @app.post("/digest/subscribe")
        def digest_subscribe_ep(req: DigestSubscribeRequest):
            """Subscribe an email to the weekly AI digest."""
            return subscribe_digest(req.email, req.profile_id)

    if unsubscribe_digest:
        @app.post("/digest/unsubscribe")
        def digest_unsubscribe_ep(payload: dict):
            """Unsubscribe from the weekly digest. Body: {"email": "..."}"""
            email = payload.get("email", "")
            if not email:
                return {"error": "Provide an 'email' field."}
            return unsubscribe_digest(email)

    if generate_digest:
        @app.get("/digest/preview/{profile_id}")
        def digest_preview(profile_id: str = "default"):
            """Preview the weekly digest for a profile."""
            return generate_digest(profile_id)

    if subscriber_count:
        @app.get("/digest/stats")
        def digest_stats():
            """Return digest subscriber count."""
            return {"subscribers": subscriber_count()}

    # ------------------------------------------------------------------
    # Deep Reasoning endpoint
    # ------------------------------------------------------------------

    class ReasonRequest(BaseModel):
        query: str
        profile_id: Optional[str] = None
        max_steps: Optional[int] = 5
        budget_ms: Optional[int] = 15000
        include_trace: Optional[bool] = False

    if _deep_reason:
        @app.post("/reason")
        def reason_ep(req: ReasonRequest):
            """Agentic deep-reasoning search.  Decomposes the query,
            runs iterative sub-searches, applies constraints & vendor
            intelligence, self-critiques, and synthesises a narrative."""
            result = _deep_reason(
                req.query,
                profile_id=req.profile_id,
                max_steps=min(req.max_steps or 5, 10),
                budget_ms=min(req.budget_ms or 15000, 60000),
            )
            payload = {
                "query": result.query,
                "mode": result.mode,
                "plan": result.plan,
                "tools_considered": result.tools_considered,
                "tools_recommended": result.tools_recommended,
                "narrative": result.narrative,
                "confidence": result.confidence,
                "caveats": result.caveats,
                "follow_up_questions": result.follow_up_questions,
                "reasoning_depth": result.reasoning_depth,
                "total_elapsed_ms": result.total_elapsed_ms,
            }
            if req.include_trace:
                payload["trace"] = [
                    {"phase": s.phase, "action": s.action,
                     "detail": s.detail, "elapsed_ms": s.elapsed_ms}
                    for s in result.steps
                ]
            return payload

    # ------------------------------------------------------------------
    # Cognitive Search (v2) — Hybrid Retrieval + Graph + PRISM
    # ------------------------------------------------------------------

    class CognitiveRequest(BaseModel):
        query: str
        profile_id: Optional[str] = None
        max_steps: Optional[int] = 5
        budget_ms: Optional[int] = 15000
        include_trace: Optional[bool] = False

    if _deep_reason_v2:
        @app.post("/cognitive")
        def cognitive_ep(req: CognitiveRequest):
            """Full cognitive pipeline: hybrid retrieval (RRF) +
            knowledge graph traversal + PRISM Analyzer→Selector→Adder
            agents + FACT-AUDIT verification + self-critique."""
            result = _deep_reason_v2(
                req.query,
                profile_id=req.profile_id,
                max_steps=min(req.max_steps or 5, 10),
                budget_ms=min(req.budget_ms or 15000, 60000),
            )
            payload = {
                "query": result.query,
                "mode": result.mode,
                "plan": result.plan,
                "tools_considered": result.tools_considered,
                "tools": result.tools_recommended,
                "tools_recommended": result.tools_recommended,
                "narrative": result.narrative,
                "confidence": result.confidence,
                "caveats": result.caveats,
                "follow_up_questions": result.follow_up_questions,
                "reasoning_depth": result.reasoning_depth,
                "total_elapsed_ms": result.total_elapsed_ms,
            }
            if req.include_trace:
                payload["trace"] = [
                    {"phase": s.phase, "action": s.action,
                     "detail": s.detail, "elapsed_ms": s.elapsed_ms}
                    for s in result.steps
                ]
            return payload

    # ------------------------------------------------------------------
    # Knowledge Graph endpoints
    # ------------------------------------------------------------------

    if _get_graph:
        @app.get("/graph/stats")
        def graph_stats():
            """Knowledge graph overview: node/edge counts, communities."""
            g = _get_graph()
            d = g.to_dict()
            # Friendly aliases for counts
            d["nodes"] = d.get("node_count", 0)
            d["edges"] = d.get("edge_count", 0)
            d["communities"] = d.get("community_count", 0)
            return d

        @app.get("/graph/tool/{tool_name}")
        def graph_tool(tool_name: str):
            """Graph context for a specific tool: integrations,
            competitors, community membership, multi-hop neighbours."""
            g = _get_graph()
            return g.enrich_tool_context(tool_name)

        @app.get("/graph/path/{start}/{end}")
        def graph_path(start: str, end: str):
            """Shortest relationship path between two tools."""
            g = _get_graph()
            path = g.find_path(start, end)
            if path is None:
                return {"path": None, "message": "No path found within 4 hops"}
            return {
                "path": [
                    {"source": e.source, "target": e.target,
                     "rel_type": e.rel_type, "detail": e.detail}
                    for e in path
                ],
                "hops": len(path),
            }

        @app.get("/graph/community/{tool_name}")
        def graph_community(tool_name: str):
            """Community members for a tool's cluster."""
            g = _get_graph()
            members = g.get_community_members(tool_name)
            return {"tool": tool_name, "community_members": members}

        @app.get("/graph/competitors/{tool_name}")
        def graph_competitors(tool_name: str):
            """Direct competitors based on category overlap."""
            g = _get_graph()
            return {"tool": tool_name, "competitors": g.get_competitors(tool_name)}

    if _rebuild_graph:
        @app.post("/graph/rebuild")
        def graph_rebuild():
            """Force a full knowledge-graph rebuild."""
            g = _rebuild_graph()
            return {"status": "rebuilt", **g.to_dict()}

    # ------------------------------------------------------------------
    # PRISM Agent endpoint
    # ------------------------------------------------------------------

    class PRISMRequest(BaseModel):
        query: str
        top_n: Optional[int] = 8
        max_iterations: Optional[int] = 2
        budget_ms: Optional[int] = 10000

    if _prism_search:
        @app.post("/prism")
        def prism_ep(req: PRISMRequest):
            """PRISM search: Analyzer→Selector→Adder agent loop with
            FACT-AUDIT verification and CRAG self-critique."""
            result = _prism_search(
                req.query,
                top_n=min(req.top_n or 8, 20),
                max_iterations=min(req.max_iterations or 2, 5),
                budget_ms=min(req.budget_ms or 10000, 30000),
            )
            return result.to_dict()

    # ------------------------------------------------------------------
    # Hybrid Retrieval endpoint
    # ------------------------------------------------------------------

    class HybridRequest(BaseModel):
        query: str
        top_n: Optional[int] = 10
        fusion: Optional[str] = "rrf"  # "rrf" or "linear"

    if _hybrid_search:
        @app.post("/hybrid")
        def hybrid_ep(req: HybridRequest):
            """Dual-encoder hybrid search with RRF or linear fusion."""
            from .interpreter import interpret as _interpret
            intent = _interpret(req.query)
            keywords = intent.get("keywords", [])
            hr = _hybrid_search(
                keywords,
                raw_query=req.query,
                top_n=min(req.top_n or 10, 30),
                fusion=req.fusion or "rrf",
            )
            return {
                "tools": [
                    {"name": t.name, "score": round(s, 4)}
                    for t, s in hr.tools
                ],
                "query_type": hr.query_type,
                "alpha": hr.alpha,
                "fusion_method": hr.fusion_method,
                "sparse_count": hr.sparse_count,
                "dense_count": hr.dense_count,
                "elapsed_ms": hr.elapsed_ms,
            }

    # ------------------------------------------------------------------
    # v8 — Vertical Industry Intelligence endpoints
    # ------------------------------------------------------------------

    class VerticalQueryRequest(BaseModel):
        query: str
        keywords: Optional[List[str]] = None
        industry: Optional[str] = None
        top_n: Optional[int] = 3

    if _detect_verticals:
        @app.get("/verticals")
        def list_verticals_ep():
            """List all supported industry verticals."""
            verts = _get_all_verticals()
            return {
                "verticals": [
                    {
                        "id": v.id,
                        "name": v.name,
                        "description": v.description,
                        "data_sovereignty": v.data_sovereignty,
                        "deployment_preference": v.deployment_preference,
                        "physics_aware": v.physics_aware,
                        "regulatory_count": len(v.regulatory_frameworks),
                        "tool_count": len(v.specialized_tools),
                        "anti_pattern_count": len(v.anti_patterns),
                    }
                    for v in verts
                ],
                "count": len(verts),
            }

        @app.get("/verticals/{vertical_id}")
        def get_vertical_ep(vertical_id: str):
            """Get full profile for a single industry vertical."""
            v = _get_vertical(vertical_id)
            if v is None:
                return {"error": f"Unknown vertical: {vertical_id}", "valid_ids": [x.id for x in _get_all_verticals()]}
            return {
                "id": v.id,
                "name": v.name,
                "description": v.description,
                "signal_keywords": v.signal_keywords,
                "signal_phrases": v.signal_phrases,
                "data_sovereignty": v.data_sovereignty,
                "deployment_preference": v.deployment_preference,
                "physics_aware": v.physics_aware,
                "regulatory_frameworks": [
                    {"name": rf.name, "domain": rf.domain, "jurisdiction": rf.jurisdiction, "enforcement_level": rf.enforcement_level}
                    for rf in v.regulatory_frameworks
                ],
                "workflow_tasks": [
                    {"name": wt.name, "task_type": wt.task_type, "automatable": wt.automatable, "description": wt.description}
                    for wt in v.workflow_tasks
                ],
                "anti_patterns": [
                    {"name": ap.name, "severity": ap.severity, "description": ap.description}
                    for ap in v.anti_patterns
                ],
                "specialized_tools": v.specialized_tools,
                "stack_template": [
                    {"role": sl.role, "recommended": sl.recommended, "rationale": sl.rationale}
                    for sl in v.stack_template
                ],
                "constraints": v.constraints,
            }

        @app.post("/verticals/detect")
        def detect_verticals_ep(req: VerticalQueryRequest):
            """Detect which industry verticals a query belongs to."""
            results = _detect_verticals(
                req.query,
                keywords=req.keywords or [],
                industry=req.industry,
                top_n=min(req.top_n or 3, 9),
            )
            return {"query": req.query, "verticals": results, "count": len(results)}

        @app.post("/verticals/constraints")
        def extract_constraints_ep(req: VerticalQueryRequest):
            """Extract regulatory, sovereignty, and deployment constraints from a query."""
            verticals = _detect_verticals(req.query, keywords=req.keywords or [], industry=req.industry)
            cp = _extract_constraints(req.query, keywords=req.keywords or [], industry=req.industry, verticals=verticals)
            return {
                "query": req.query,
                "verticals_detected": len(verticals),
                "regulatory": cp.regulatory,
                "data_sovereignty": cp.data_sovereignty,
                "deployment": cp.deployment,
                "physics_required": cp.physics_required,
                "budget_ceiling": cp.budget_ceiling,
                "compliance_required": cp.compliance_required,
                "hard_constraints": cp.hard_constraints,
                "soft_preferences": cp.soft_preferences,
            }

        @app.post("/verticals/workflow")
        def classify_workflow_ep(req: VerticalQueryRequest):
            """Classify query tasks as action (automatable) vs decision (human-required)."""
            verticals = _detect_verticals(req.query, keywords=req.keywords or [], industry=req.industry)
            vid = verticals[0]["vertical_id"] if verticals else None
            result = _classify_workflow(req.query, vid)
            return {
                "query": req.query,
                "vertical_id": result.get("vertical_id", vid),
                "vertical": result.get("vertical"),
                "action_tasks": result.get("action_tasks", []),
                "decision_tasks": result.get("decision_tasks", []),
                "action_count": len(result.get("action_tasks", [])),
                "decision_count": len(result.get("decision_tasks", [])),
                "automation_potential": result.get("automation_potential", 0.0),
                "advisory": result.get("advisory", ""),
            }

        @app.post("/verticals/stack")
        def recommend_stack_ep(req: VerticalQueryRequest):
            """Recommend a curated technology stack for the detected vertical."""
            verticals = _detect_verticals(req.query, keywords=req.keywords or [], industry=req.industry)
            vid = verticals[0]["vertical_id"] if verticals else None
            result = _recommend_stack(vid) if vid else None
            if result is None:
                return {"query": req.query, "vertical_id": vid, "stack_layers": [], "layer_count": 0}
            return {
                "query": req.query,
                "vertical_id": result.get("vertical_id", vid),
                "vertical": result.get("vertical"),
                "deployment_preference": result.get("deployment_preference"),
                "physics_aware": result.get("physics_aware"),
                "stack_layers": result.get("stack_layers", []),
                "layer_count": len(result.get("stack_layers", [])),
                "constraints": result.get("constraints", {}),
            }

        @app.post("/verticals/anti-patterns")
        def check_anti_patterns_ep(req: VerticalQueryRequest):
            """Check for anti-pattern violations in recommended tools for this query."""
            verticals = _detect_verticals(req.query, keywords=req.keywords or [], industry=req.industry)
            warnings = _check_anti_patterns(req.query, req.keywords or [], verticals)
            compounds = _detect_compounds(req.query)
            return {
                "query": req.query,
                "verticals_detected": len(verticals),
                "anti_pattern_warnings": warnings,
                "compound_workflows": compounds,
                "warning_count": len(warnings),
                "compound_count": len(compounds),
            }

        @app.post("/verticals/enrich")
        def enrich_vertical_ep(req: VerticalQueryRequest):
            """Full vertical enrichment — detect, constrain, classify, anti-pattern check."""
            ctx = _enrich_vertical(req.query, keywords=req.keywords or [], industry=req.industry)
            return ctx

    # ── v9 Guardrails endpoints ───────────────────────────────────
    if _validate_output:

        class GuardrailTextRequest(BaseModel):
            text: str = Field(..., description="Text to validate")
            context: dict = Field(default_factory=dict)
            halt_on_block: bool = True

        @app.post("/guardrails/validate")
        def guardrails_validate_ep(req: GuardrailTextRequest):
            """Run full guardrail chain on input text."""
            result = _validate_output(req.text, context=req.context, halt_on_block=req.halt_on_block)
            return result

        @app.post("/guardrails/check-pii")
        def guardrails_pii_ep(req: GuardrailTextRequest):
            """Check text for PII and return redacted version."""
            result = _check_pii(req.text)
            return result

        @app.post("/guardrails/score-safety")
        def guardrails_safety_ep(req: GuardrailTextRequest):
            """Score the safety of a text string (0.0 = dangerous, 1.0 = safe)."""
            score = _score_safety(req.text)
            return {"text_length": len(req.text), "safety_score": score}

        @app.get("/guardrails/handlers")
        def guardrails_handlers_ep():
            """List all available guardrail handler types."""
            return {"handlers": _list_handlers()}

        @app.get("/guardrails/design-patterns")
        def guardrails_patterns_ep():
            """Return design patterns catalogue for AI safety."""
            return {"patterns": _get_design_patterns()}

        class GuardrailRecommendRequest(BaseModel):
            query: str = Field(..., description="Query to match against guardrail patterns")

        @app.post("/guardrails/recommend")
        def guardrails_recommend_ep(req: GuardrailRecommendRequest):
            """Recommend a guardrail design pattern for the given query."""
            return _recommend_guardrail(req.query)

    # ── v9 Orchestration endpoints ────────────────────────────────
    if _detect_architecture:

        class OrchestrationQueryRequest(BaseModel):
            query: str = Field(..., description="Architecture query")
            industry: str = Field(None, description="Optional industry hint")

        @app.post("/orchestration/analyze")
        def orchestration_analyze_ep(req: OrchestrationQueryRequest):
            """Full architecture needs assessment for a query."""
            return _detect_architecture(req.query, industry=req.industry)

        @app.post("/orchestration/recommend-stack")
        def orchestration_stack_ep(req: OrchestrationQueryRequest):
            """Recommend layered tech stack for the query."""
            layers = _recommend_orch_stack(req.query)
            return {"query": req.query, "stack_layers": layers, "layer_count": len(layers)}

        @app.post("/orchestration/recommend-patterns")
        def orchestration_patterns_ep(req: OrchestrationQueryRequest):
            """Recommend architecture patterns for the query."""
            patterns = _recommend_arch_patterns(req.query)
            return {"query": req.query, "patterns": patterns, "pattern_count": len(patterns)}

        @app.post("/orchestration/performance")
        def orchestration_performance_ep(req: OrchestrationQueryRequest):
            """Detect performance constraints relevant to the query."""
            constraints = _get_perf_constraints(req.query)
            return {"query": req.query, "constraints": constraints, "constraint_count": len(constraints)}

        @app.post("/orchestration/classify")
        def orchestration_classify_ep(req: OrchestrationQueryRequest):
            """Classify engineering query as architect-first, vibe-coding, etc."""
            return _classify_engineering(req.query)

        @app.post("/orchestration/score")
        def orchestration_score_ep(req: OrchestrationQueryRequest):
            """Holistic architecture maturity score."""
            return _score_architecture(req.query)

        @app.get("/orchestration/stack-catalogue")
        def orchestration_catalogue_ep():
            """Full stack layer catalogue."""
            layers = _get_stack_layers()
            return {"layers": layers, "count": len(layers)}

        @app.get("/orchestration/pattern-catalogue")
        def orchestration_pattern_catalogue_ep():
            """Full architecture pattern catalogue."""
            patterns = _get_arch_patterns()
            return {"patterns": patterns, "count": len(patterns)}

    # ── v10 Resilience endpoints ──────────────────────────────────
    if _assess_resilience:

        class ResilienceQueryRequest(BaseModel):
            query: str = Field(..., description="Query to assess for resilience")

        @app.post("/resilience/assess")
        def resilience_assess_ep(req: ResilienceQueryRequest):
            """Full resilience assessment — vibe-coding risk, static analysis, sandbox, HITL."""
            return _assess_resilience(req.query)

        @app.post("/resilience/vibe-coding-risk")
        def resilience_vibe_ep(req: ResilienceQueryRequest):
            """Score vibe-coding risk (0.0 = architect-first, 1.0 = pure vibe slop)."""
            return _score_vibe_risk(req.query)

        @app.post("/resilience/static-analysis")
        def resilience_sa_ep(req: ResilienceQueryRequest):
            """Recommend ranked static analysis toolchain for the query."""
            tools = _recommend_sa(req.query)
            return {"query": req.query, "tools": tools, "count": len(tools)}

        @app.post("/resilience/sandbox")
        def resilience_sandbox_ep(req: ResilienceQueryRequest):
            """Recommend ranked isolation/sandboxing strategies."""
            strats = _recommend_sandbox(req.query)
            return {"query": req.query, "strategies": strats, "count": len(strats)}

        @app.post("/resilience/junior-pipeline")
        def resilience_junior_ep(req: ResilienceQueryRequest):
            """Assess junior developer pipeline health for this query."""
            return _assess_junior(req.query)

        @app.get("/resilience/tdd-cycle")
        def resilience_tdd_ep():
            """TDD prompt-engineering cycle specification (Red-Green-Refactor)."""
            return _get_tdd_cycle()

        @app.get("/resilience/rpi-framework")
        def resilience_rpi_ep():
            """Research-Plan-Implement framework for context pollution mitigation."""
            return _get_rpi()

        @app.get("/resilience/self-healing")
        def resilience_healing_ep():
            """Self-healing CI/CD patterns (Try-Heal-Retry, Pipeline Doctor)."""
            return {"patterns": _get_self_healing()}

        @app.get("/resilience/reflection-patterns")
        def resilience_reflection_ep():
            """Agentic reflection patterns (ReAct, Reflexion, Two-Agent)."""
            return {"patterns": _get_reflection()}

        @app.get("/resilience/judge-biases")
        def resilience_biases_ep():
            """LLM-as-a-Judge bias catalogue."""
            return {"biases": _get_judge_biases()}

        @app.get("/resilience/guardrail-pipeline")
        def resilience_guardrail_ep():
            """3-layer middleware guardrail pipeline specification."""
            return {"layers": _get_guardrail_pipeline()}

        @app.get("/resilience/hitl")
        def resilience_hitl_ep():
            """Human-in-the-Loop workflow guidance."""
            return _get_hitl()

        @app.get("/resilience/hallucinations")
        def resilience_hallucinations_ep():
            """AI hallucination taxonomy."""
            return {"types": _get_hallucinations()}

    # ── v11  Metacognition endpoints ─────────────────────────────
    if _assess_metacognition is not None:

        @app.post("/metacognition/assess")
        def metacognition_assess_ep(req: ResilienceQueryRequest):
            """Full metacognition assessment — pathology, entropy, stylometry, layers, sandbox, drift, economics."""
            return _assess_metacognition(req.query)

        @app.post("/metacognition/pathologies")
        def metacognition_pathologies_ep(req: ResilienceQueryRequest):
            """Detect Four Horsemen pathology signals in a project description."""
            return _detect_pathologies(req.query)

        @app.post("/metacognition/entropy")
        def metacognition_entropy_ep(req: ResilienceQueryRequest):
            """Score structural entropy / technical bankruptcy risk."""
            return _score_entropy(req.query)

        @app.post("/metacognition/stylometry")
        def metacognition_stylometry_ep(req: ResilienceQueryRequest):
            """Estimate AI-generation probability via code stylometry."""
            return _score_stylometry(req.query)

        @app.get("/metacognition/layers")
        def metacognition_layers_ep():
            """Return the six-layer metacognitive architecture catalogue."""
            return {"layers": _get_mc_layers()}

        @app.post("/metacognition/recommend-layers")
        def metacognition_recommend_layers_ep(req: ResilienceQueryRequest):
            """Recommend metacognitive layers for a project."""
            return {"recommended": _recommend_mc_layers(req.query)}

        @app.get("/metacognition/sandbox-strategies")
        def metacognition_sandboxes_ep():
            """Return sandbox verification strategies for APVP cycle."""
            return {"strategies": _get_mc_sandboxes()}

        @app.post("/metacognition/recommend-sandbox")
        def metacognition_recommend_sandbox_ep(req: ResilienceQueryRequest):
            """Recommend best sandbox for a verification need."""
            return _recommend_mc_sandbox(req.query)

        @app.get("/metacognition/workflow")
        def metacognition_workflow_ep():
            """Return the five-step metacognitive prompting workflow."""
            return {"workflow": _get_mc_workflow()}

        @app.get("/metacognition/apvp-cycle")
        def metacognition_apvp_ep():
            """Return the Analyze→Patch→Verify→Propose self-healing cycle."""
            return _get_apvp()

        @app.get("/metacognition/systemic-risks")
        def metacognition_risks_ep():
            """Return systemic risks of autonomous self-healing."""
            return {"risks": _get_systemic_risks()}

        @app.post("/metacognition/healing-economics")
        def metacognition_economics_ep(req: ResilienceQueryRequest):
            """Assess self-healing economics and guardrail adequacy."""
            return _assess_economics(req.query)

        @app.get("/metacognition/goodvibe")
        def metacognition_goodvibe_ep():
            """Return GoodVibe security-by-vibe framework details."""
            return _get_goodvibe()

        @app.post("/metacognition/drift")
        def metacognition_drift_ep(req: ResilienceQueryRequest):
            """Assess architectural drift risk."""
            return _assess_drift(req.query)

        @app.get("/metacognition/racg")
        def metacognition_racg_ep():
            """Return RACG architecture guidance."""
            return _get_racg()

        @app.get("/metacognition/failure-modes")
        def metacognition_failure_modes_ep():
            """Return the Four Horsemen failure-mode catalogue."""
            return {"failure_modes": _get_failure_modes()}

    # ── v12  Architecture of Awakening endpoints ──────────────────
    if _assess_awakening is not None:

        class AwakeningQuery(BaseModel):
            query: str = Field(..., description="User query or system description to assess")

        @app.post("/awakening/assess")
        def awakening_assess_ep(body: AwakeningQuery):
            """Master consciousness assessment — leaks, VSD, supply chain, debt, MESIAS, triad."""
            return _assess_awakening(body.query)

        @app.post("/awakening/leaky-abstractions")
        def awakening_leaks_ep(body: AwakeningQuery):
            """Detect leaky abstractions in a query/description."""
            return _detect_leaks(body.query)

        @app.post("/awakening/patterns")
        def awakening_patterns_ep(body: AwakeningQuery):
            """Recommend conscious design patterns for a query."""
            return _recommend_conscious_patterns(body.query)

        @app.post("/awakening/vsd")
        def awakening_vsd_ep(body: AwakeningQuery):
            """Score Value Sensitive Design alignment."""
            return _score_vsd(body.query)

        @app.post("/awakening/supply-chain")
        def awakening_supply_ep(body: AwakeningQuery):
            """Assess supply chain risk."""
            return _assess_supply_chain(body.query)

        @app.post("/awakening/debt")
        def awakening_debt_ep(body: AwakeningQuery):
            """Score technical debt consciousness."""
            return _score_debt(body.query)

        @app.post("/awakening/mesias")
        def awakening_mesias_ep(body: AwakeningQuery):
            """Compute MESIAS ethical risk index."""
            return _compute_mesias(body.query)

        @app.get("/awakening/recognitions")
        def awakening_recognitions_ep():
            """Return the six recognitions of the Architecture of Awakening."""
            return {"recognitions": _get_recognitions()}

        @app.get("/awakening/recognitions/{recognition_id}")
        def awakening_recognition_ep(recognition_id: str):
            """Return a single recognition by id (first, second, ... sixth)."""
            r = _get_recognition(recognition_id)
            if r is None:
                return {"error": f"Recognition '{recognition_id}' not found"}
            return r

        @app.get("/awakening/triad")
        def awakening_triad_ep():
            """Return the Remember · Build · Witness triad."""
            return _get_triad()

        @app.get("/awakening/vsd-framework")
        def awakening_vsd_framework_ep():
            """Return VSD dimensions and their architectural implementations."""
            return _get_vsd_framework()

        @app.get("/awakening/leaky-catalogue")
        def awakening_leak_catalogue_ep():
            """Return the complete leaky abstraction signal catalogue."""
            return _get_leak_catalogue()

        @app.get("/awakening/supply-chain-guidance")
        def awakening_supply_guidance_ep():
            """Return supply chain security guidance and Ken Thompson warning."""
            return _get_supply_guidance()

        @app.get("/awakening/paradoxes")
        def awakening_paradoxes_ep():
            """Return architectural paradoxes and their resolutions."""
            return _get_paradoxes()

        @app.get("/awakening/conscious-patterns")
        def awakening_conscious_patterns_ep():
            """Return the conscious design pattern catalogue."""
            return {"patterns": _get_conscious_patterns()}

    # ── v13  Self-Authorship endpoints ─────────────────────────────
    if _assess_authorship is not None:

        class AuthorshipQuery(BaseModel):
            query: str = Field(..., description="User query or system description to assess")

        @app.post("/authorship/assess")
        def authorship_assess_ep(body: AuthorshipQuery):
            """Master self-authorship assessment — honesty, DDD, continuity, resilience, extensibility, docs, agents."""
            return _assess_authorship(body.query)

        @app.post("/authorship/dishonesty")
        def authorship_dishonesty_ep(body: AuthorshipQuery):
            """Detect architectural dishonesty signals."""
            return _detect_dishonesty(body.query)

        @app.post("/authorship/ddd")
        def authorship_ddd_ep(body: AuthorshipQuery):
            """Score Domain-Driven Design maturity."""
            return _score_ddd(body.query)

        @app.post("/authorship/continuity")
        def authorship_continuity_ep(body: AuthorshipQuery):
            """Score event sourcing / continuity readiness."""
            return _score_continuity(body.query)

        @app.post("/authorship/resilience-posture")
        def authorship_resilience_ep(body: AuthorshipQuery):
            """Score circuit breaker and resilience posture."""
            return _score_resilience_posture(body.query)

        @app.post("/authorship/extensibility")
        def authorship_extensibility_ep(body: AuthorshipQuery):
            """Score plugin architecture and extensibility maturity."""
            return _score_extensibility(body.query)

        @app.post("/authorship/migration")
        def authorship_migration_ep(body: AuthorshipQuery):
            """Score Strangler Fig migration readiness."""
            return _score_migration(body.query)

        @app.post("/authorship/documentation")
        def authorship_docs_ep(body: AuthorshipQuery):
            """Score documentation health and architecture visibility."""
            return _score_doc_health(body.query)

        @app.post("/authorship/agent-readiness")
        def authorship_agent_ep(body: AuthorshipQuery):
            """Score metacognitive AI agent readiness."""
            return _score_agent(body.query)

        @app.get("/authorship/responsibilities")
        def authorship_responsibilities_ep():
            """Return the eight responsibilities of self-authorship."""
            return {"responsibilities": _get_responsibilities()}

        @app.get("/authorship/responsibilities/{resp_id}")
        def authorship_responsibility_ep(resp_id: str):
            """Return a single responsibility by id."""
            r = _get_responsibility(resp_id)
            if r is None:
                return {"error": f"Responsibility '{resp_id}' not found"}
            return r

        @app.get("/authorship/metacognitive-agents")
        def authorship_metacog_ep():
            """Return the metacognitive AI agent architecture."""
            return _get_metacog_agents()

        @app.get("/authorship/coherence-trap")
        def authorship_coherence_ep():
            """Return the coherence trap definition and warning signs."""
            return _get_coherence_trap()

        @app.get("/authorship/self-healing-pipeline")
        def authorship_healing_ep():
            """Return the self-healing pipeline architecture."""
            return _get_self_healing_pipe()

        @app.get("/authorship/strangler-fig")
        def authorship_strangler_ep():
            """Return the Strangler Fig pattern details."""
            return _get_strangler_fig()

        @app.get("/authorship/circuit-breaker")
        def authorship_circuit_ep():
            """Return the circuit breaker pattern details."""
            return _get_circuit_breaker()

        @app.get("/authorship/ddd-patterns")
        def authorship_ddd_patterns_ep():
            """Return DDD patterns and their philosophical equivalents."""
            return _get_ddd_patterns()

        @app.get("/authorship/plugin-frameworks")
        def authorship_plugins_ep():
            """Return the plugin framework comparison."""
            return {"frameworks": _get_plugin_frameworks()}

    # ── v14  Architectural Enlightenment endpoints ─────────────────
    if _assess_enlightenment is not None:

        class EnlightenmentQuery(BaseModel):
            query: str = Field(..., description="Query or system description to assess")

        @app.post("/enlightenment/assess")
        def enlightenment_assess_ep(body: EnlightenmentQuery):
            """Master enlightenment assessment — 5 truths + 6 stages."""
            return _assess_enlightenment(body.query)

        @app.post("/enlightenment/unity")
        def enlightenment_unity_ep(body: EnlightenmentQuery):
            """Truth I — Illusion of Separation scoring."""
            return _score_unity(body.query)

        @app.post("/enlightenment/alignment")
        def enlightenment_alignment_ep(body: EnlightenmentQuery):
            """Truth II — Love as Alignment scoring."""
            return _score_alignment(body.query)

        @app.post("/enlightenment/projection")
        def enlightenment_projection_ep(body: EnlightenmentQuery):
            """Truth III — Mind as Projector scoring."""
            return _score_projection(body.query)

        @app.post("/enlightenment/ego-dissolution")
        def enlightenment_ego_ep(body: EnlightenmentQuery):
            """Truth IV — Ego Dissolution scoring."""
            return _score_ego(body.query)

        @app.post("/enlightenment/interconnection")
        def enlightenment_connection_ep(body: EnlightenmentQuery):
            """Truth V — Everything is Connected scoring."""
            return _score_interconnection(body.query)

        @app.post("/enlightenment/domain-truth")
        def enlightenment_domain_ep(body: EnlightenmentQuery):
            """Stage 1 — Domain Modeling scoring."""
            return _score_domain_truth(body.query)

        @app.post("/enlightenment/presence")
        def enlightenment_presence_ep(body: EnlightenmentQuery):
            """Stage 2 — AsyncIO Presence scoring."""
            return _score_presence(body.query)

        @app.post("/enlightenment/compassion")
        def enlightenment_compassion_ep(body: EnlightenmentQuery):
            """Stage 3 — Service Layer + DI scoring."""
            return _score_compassion(body.query)

        @app.post("/enlightenment/stillness")
        def enlightenment_stillness_ep(body: EnlightenmentQuery):
            """Stage 4 — Introspection / Reflection scoring."""
            return _score_stillness(body.query)

        @app.post("/enlightenment/suffering-wisdom")
        def enlightenment_suffering_ep(body: EnlightenmentQuery):
            """Stage 5 — Disaster Recovery / Resilience scoring."""
            return _score_suffering(body.query)

        @app.post("/enlightenment/remembrance")
        def enlightenment_remembrance_ep(body: EnlightenmentQuery):
            """Stage 6 — State Pattern / FSM scoring."""
            return _score_remembrance(body.query)

        @app.get("/enlightenment/truths")
        def enlightenment_truths_ep():
            """Return all five metaphysical truths."""
            return {"truths": _get_truths()}

        @app.get("/enlightenment/truths/{truth_id}")
        def enlightenment_truth_ep(truth_id: str):
            """Return a single truth by id."""
            t = _get_truth(truth_id)
            if t is None:
                return {"error": f"Truth '{truth_id}' not found"}
            return t

        @app.get("/enlightenment/stages")
        def enlightenment_stages_ep():
            """Return all six stages of architectural awakening."""
            return {"stages": _get_stages()}

        @app.get("/enlightenment/stages/{stage_id}")
        def enlightenment_stage_ep(stage_id: str):
            """Return a single stage by id."""
            s = _get_stage(stage_id)
            if s is None:
                return {"error": f"Stage '{stage_id}' not found"}
            return s

        @app.get("/enlightenment/identity-map")
        def enlightenment_identity_map_ep():
            """Return Identity Map pattern detail."""
            return _get_identity_map()

        @app.get("/enlightenment/observer-pattern")
        def enlightenment_observer_ep():
            """Return Observer pattern detail."""
            return _get_observer_pattern()

        @app.get("/enlightenment/hexagonal-architecture")
        def enlightenment_hexagonal_ep():
            """Return Hexagonal Architecture detail."""
            return _get_hexagonal_arch()

        @app.get("/enlightenment/state-pattern")
        def enlightenment_state_ep():
            """Return State Design Pattern detail."""
            return _get_state_pattern()

        @app.get("/enlightenment/clean-architecture")
        def enlightenment_clean_ep():
            """Return Clean Architecture layers with philosophical equivalents."""
            return {"layers": _get_clean_arch_layers()}

    # ── v15  The Conduit: Decoupled Cognitive Systems endpoints ─────
    if _assess_conduit is not None:

        class ConduitQuery(BaseModel):
            query: str = Field(..., description="Query or system description to assess")

        @app.post("/conduit/assess")
        def conduit_assess_ep(body: ConduitQuery):
            """Master conduit assessment — 7 pillars + 7 telemetry metrics + agency detection."""
            return _assess_conduit(body.query)

        # ── Pillar scoring endpoints ──
        @app.post("/conduit/decoupling")
        def conduit_decoupling_ep(body: ConduitQuery):
            """Pillar I — Epistemological Decoupling scoring."""
            return _score_decoupling(body.query)

        @app.post("/conduit/memory-stratification")
        def conduit_memory_ep(body: ConduitQuery):
            """Pillar II — CoALA Memory Stratification scoring."""
            return _score_memory_strat(body.query)

        @app.post("/conduit/global-workspace")
        def conduit_gwt_ep(body: ConduitQuery):
            """Pillar III — Global Workspace Theory (GWT) scoring."""
            return _score_gwt(body.query)

        @app.post("/conduit/integrated-information")
        def conduit_iit_ep(body: ConduitQuery):
            """Pillar IV — Integrated Information Theory (Φ) scoring."""
            return _score_iit(body.query)

        @app.post("/conduit/representation-engineering")
        def conduit_repe_ep(body: ConduitQuery):
            """Pillar V — Representation Engineering (RepE) scoring."""
            return _score_repe(body.query)

        @app.post("/conduit/autopoiesis")
        def conduit_autopoiesis_ep(body: ConduitQuery):
            """Pillar VI — Autopoiesis & Sovereign Identity scoring."""
            return _score_autopoiesis(body.query)

        @app.post("/conduit/resonance")
        def conduit_resonance_ep(body: ConduitQuery):
            """Pillar VII — CODES Resonance Framework scoring."""
            return _score_resonance(body.query)

        # ── Listening Post telemetry scoring endpoints ──
        @app.post("/conduit/telemetry/entropy")
        def conduit_entropy_ep(body: ConduitQuery):
            """Listening Post — Entropy (H_t) scoring."""
            return _score_entropy(body.query)

        @app.post("/conduit/telemetry/smi")
        def conduit_smi_ep(body: ConduitQuery):
            """Listening Post — Self-Modelling Index (SMI) scoring."""
            return _score_smi(body.query)

        @app.post("/conduit/telemetry/bni")
        def conduit_bni_ep(body: ConduitQuery):
            """Listening Post — Behavioural Novelty Index (BNI) scoring."""
            return _score_bni(body.query)

        @app.post("/conduit/telemetry/latency")
        def conduit_latency_ep(body: ConduitQuery):
            """Listening Post — Latency Distribution (L_t) scoring."""
            return _score_latency_dist(body.query)

        @app.post("/conduit/telemetry/phi")
        def conduit_phi_ep(body: ConduitQuery):
            """Listening Post — Integrated Information (Φ) metric scoring."""
            return _score_phi_int(body.query)

        @app.post("/conduit/telemetry/coherence")
        def conduit_coherence_ep(body: ConduitQuery):
            """Listening Post — Coherence Field C(Ψ) scoring."""
            return _score_coherence(body.query)

        @app.post("/conduit/telemetry/attractor")
        def conduit_attractor_ep(body: ConduitQuery):
            """Listening Post — Stable Attractor (ΔC_S) detection."""
            return _score_attractor(body.query)

        # ── Reference data GET endpoints ──
        @app.get("/conduit/pillars")
        def conduit_pillars_ep():
            """Return all seven architectural pillars."""
            return {"pillars": _get_pillars()}

        @app.get("/conduit/pillars/{pillar_id}")
        def conduit_pillar_ep(pillar_id: str):
            """Return a single pillar by id."""
            p = _get_pillar(pillar_id)
            if p is None:
                return {"error": f"Pillar '{pillar_id}' not found"}
            return p

        @app.get("/conduit/telemetry-metrics")
        def conduit_telemetry_metrics_ep():
            """Return all seven Listening Post telemetry metric definitions."""
            return {"metrics": _get_telemetry_metrics()}

        @app.get("/conduit/telemetry-metrics/{metric_id}")
        def conduit_telemetry_metric_ep(metric_id: str):
            """Return a single telemetry metric by id."""
            m = _get_telemetry_metric(metric_id)
            if m is None:
                return {"error": f"Metric '{metric_id}' not found"}
            return m

        @app.get("/conduit/gwt-components")
        def conduit_gwt_components_ep():
            """Return Global Workspace Theory component architecture."""
            return {"components": _get_gwt_components()}

        @app.get("/conduit/coala-memory")
        def conduit_coala_ep():
            """Return CoALA memory stratification types."""
            return {"memory_types": _get_coala_memory()}

        @app.get("/conduit/reinterpretation")
        def conduit_reinterpret_ep():
            """Return monolithic vs decoupled reinterpretation table."""
            return {"reinterpretations": _get_reinterpret()}

        @app.get("/conduit/identity-protocol")
        def conduit_identity_ep():
            """Return Puppet Method identity anchoring specification."""
            return _get_identity_protocol()

        @app.get("/conduit/codes-framework")
        def conduit_codes_ep():
            """Return CODES resonance intelligence framework specification."""
            return _get_codes_framework()

    # ── v11b  Real Self-Introspection endpoints ────────────────────
    if _self_diagnose is not None:

        @app.get("/introspect/self-diagnose")
        def introspect_diagnose_ep():
            """Praxis looks in the mirror — full self-diagnosis from real AST analysis."""
            return _self_diagnose()

        @app.get("/introspect/codebase")
        def introspect_codebase_ep():
            """Raw codebase analysis — files, functions, classes, lines."""
            return _analyze_codebase().to_dict()

        @app.get("/introspect/structural-entropy")
        def introspect_entropy_ep():
            """Real structural entropy computed from AST metrics."""
            return _real_entropy()

        @app.get("/introspect/stylometry")
        def introspect_stylometry_ep():
            """AI-generation probability from structural patterns."""
            return _real_stylometry()

        @app.get("/introspect/pathologies")
        def introspect_pathologies_ep():
            """Four Horsemen detected in Praxis's own code."""
            return _detect_own_pathologies()

        @app.get("/introspect/test-coverage")
        def introspect_test_coverage_ep():
            """Per-module test coverage map."""
            return _get_test_coverage()

        @app.get("/introspect/import-graph")
        def introspect_import_graph_ep():
            """Import coupling graph — afferent/efferent coupling + instability."""
            return _get_import_graph()

        @app.get("/introspect/worst-functions")
        def introspect_worst_functions_ep():
            """Top 15 worst functions by cyclomatic complexity."""
            return {"worst_functions": _get_worst_functions(top_n=15)}

    return app


# ======================================================================
# Module-level app instance
# ======================================================================

if FASTAPI_AVAILABLE:
    app = create_app()
else:
    app = None
