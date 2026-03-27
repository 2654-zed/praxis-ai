# --------------- Stack Composer ---------------
"""
Composes multi-tool *stacks* instead of returning isolated tool results.

A stack is an ordered list of 2-4 tools, each assigned a role:
    • primary        – the main tool that addresses the user's core task
    • companion      – enhances / complements the primary tool
    • infrastructure – connects the stack (automation, data routing, CI/CD)
    • analytics      – provides measurement / feedback for the workflow

The composer uses the decision engine for initial scoring, then layers on
compatibility, integration, budget, and skill-level logic to assemble the
best combination.
"""

from typing import List, Optional, Dict

try:
    from .tools import Tool
    from .profile import UserProfile
    from .engine import find_tools, score_tool
    from .data import TOOLS
    from .explain import explain_stack
except Exception:
    from praxis.tools import Tool
    from praxis.profile import UserProfile
    from praxis.engine import find_tools, score_tool
    from praxis.data import TOOLS
    from praxis.explain import explain_stack

try:
    from . import config as _cfg
except Exception:
    try:
        import config as _cfg
    except Exception:
        _cfg = None


# ======================================================================
# Public API
# ======================================================================

def compose_stack(
    intent: dict,
    profile: Optional[UserProfile] = None,
    stack_size: int = 3,
    categories_filter: list = None,
) -> dict:
    """Build an optimal tool stack for the given intent + profile.

    Returns:
        {
            "stack":        list of {"tool": Tool, "role": str},
            "explanation":  dict (from explain_stack),
            "alternatives": list of Tool (runners-up not in the stack),
        }
    """
    if _cfg:
        stack_size = _cfg.get("stack_size", stack_size)

    # Step 1 — score *all* tools with profile-aware engine + elimination funnel
    candidates, funnel = _score_candidates(intent, profile, categories_filter)

    if not candidates:
        return {"stack": [], "explanation": {}, "alternatives": [], "funnel": funnel}

    # Step 2 — select the primary tool (highest score)
    stack = []
    used_names = set()

    primary = _pick_best(candidates, role="primary", used=used_names, profile=profile)
    if primary:
        stack.append({"tool": primary, "role": "primary"})
        used_names.add(primary.name)

    # Step 3 — pick companion(s) that complement the primary
    remaining_slots = stack_size - len(stack)
    if remaining_slots > 0 and primary:
        companions = _pick_companions(candidates, primary, used_names, profile, limit=min(remaining_slots, 2))
        for c in companions:
            stack.append({"tool": c, "role": "companion"})
            used_names.add(c.name)
            remaining_slots -= 1

    # Step 4 — pick infrastructure / analytics tool if slot remains
    if remaining_slots > 0:
        infra = _pick_infrastructure(candidates, stack, used_names, profile)
        if infra:
            stack.append({"tool": infra, "role": "infrastructure"})
            used_names.add(infra.name)

    # Step 5 — build explanation
    explanation = explain_stack(stack, intent, profile) if stack else {}

    # Step 6 — alternatives (next-best tools not in stack)
    alternatives = [
        tool for (_, tool) in candidates
        if tool.name not in used_names
    ][:5]

    # Record final selection in funnel
    funnel["steps"].append({
        "name": "Final Selection",
        "description": f"Top {len(stack)} tools by fit",
        "before": funnel["steps"][-1]["after"] if funnel["steps"] else len(candidates),
        "after": len(stack),
        "eliminated": (funnel["steps"][-1]["after"] if funnel["steps"] else len(candidates)) - len(stack),
    })
    funnel["final_count"] = len(stack)

    return {
        "stack": stack,
        "explanation": explanation,
        "alternatives": alternatives,
        "funnel": funnel,
    }


# ======================================================================
# Internal helpers
# ======================================================================

def _score_candidates(
    intent: dict,
    profile: Optional[UserProfile],
    categories_filter: list,
) -> tuple:
    """Return (scored_list, funnel_data).

    scored_list: list of (score, Tool) tuples, sorted descending.
    funnel_data: dict tracking how many tools survived each elimination step.
    """

    total = len(TOOLS)
    funnel = {"total_tools": total, "steps": []}

    # Build keywords the same way engine.find_tools does
    if isinstance(intent, dict):
        keywords = []
        for k in (intent.get("intent"), intent.get("industry"), intent.get("goal")):
            if k:
                keywords.append(str(k))
        keywords.extend(intent.get("keywords", []))
        if not keywords and intent.get("raw"):
            keywords = intent.get("raw", "").lower().split()
    else:
        keywords = str(intent).lower().split()

    if categories_filter:
        categories_filter = [c.lower().strip() for c in categories_filter if c.strip()]
    else:
        categories_filter = None

    # ── PHASE 1: Hard elimination filters ──

    pool = list(TOOLS)

    # Category filter
    if categories_filter:
        before = len(pool)
        pool = [t for t in pool if any(fc in [c.lower() for c in t.categories] for fc in categories_filter)]
        funnel["steps"].append({
            "name": "Category Filter",
            "description": f"Matching {', '.join(categories_filter)}",
            "before": before, "after": len(pool),
            "eliminated": before - len(pool),
        })

    # Compliance gate
    if profile and profile.constraints:
        required = [c.upper() for c in profile.constraints if c.upper() in ("HIPAA", "SOC2", "GDPR", "FEDRAMP")]
        if required:
            before = len(pool)
            pool = [t for t in pool if all(
                req in [c.upper() for c in t.compliance] for req in required
            )]
            funnel["steps"].append({
                "name": "Compliance",
                "description": f"Requires {', '.join(required)}",
                "before": before, "after": len(pool),
                "eliminated": before - len(pool),
            })

    # Budget hard-filter (THE FIX — budget is a constraint, not a preference)
    if profile and profile.budget and profile.budget != "high":
        before = len(pool)
        budget_label = {"free": "Free only", "low": "Under $50/mo", "medium": "Under $500/mo"}.get(profile.budget, profile.budget)
        pool = [t for t in pool if t.fits_budget(profile.budget)]

        # Edge case: if budget eliminated everything, fall back to cheapest tools
        if not pool and before > 0:
            # Sort original pool by cost, take cheapest
            def _tool_cost(t):
                p = t.pricing or {}
                if p.get("free_tier"):
                    return 0
                return float(p.get("starter") or p.get("pro") or 9999)
            from operator import itemgetter
            all_with_cost = [(t, _tool_cost(t)) for t in TOOLS]
            all_with_cost.sort(key=lambda x: x[1])
            pool = [t for t, _ in all_with_cost[:10]]
            budget_label += " (relaxed — showing lowest cost)"

        funnel["steps"].append({
            "name": "Budget",
            "description": budget_label,
            "before": before, "after": len(pool),
            "eliminated": before - len(pool),
        })

    # ── PHASE 2: Score survivors ──

    scored = []
    for tool in pool:
        sc = score_tool(tool, keywords)

        # Soft profile bonuses (skill, integrations — NOT budget, that's now a hard filter)
        if profile:
            if tool.fits_skill(profile.skill_level):
                sc += 2
            for et in profile.existing_tools:
                if tool.integrates_with(et):
                    sc += 3
                    break
            if profile.already_uses(tool.name):
                sc -= 2

        if sc > 0:
            scored.append((sc, tool))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Record scoring step in funnel
    funnel["steps"].append({
        "name": "Relevance Scoring",
        "description": "Ranked by keyword, category, and profile fit",
        "before": len(pool), "after": len(scored),
        "eliminated": len(pool) - len(scored),
    })

    return scored, funnel


def _pick_best(
    candidates: List[tuple],
    role: str,
    used: set,
    profile: Optional[UserProfile],
) -> Optional[Tool]:
    """Pick the highest-scoring candidate that can fill *role* and isn't used."""
    for _, tool in candidates:
        if tool.name in used:
            continue
        if role in tool.stack_roles:
            return tool
    # Fallback: ignore role constraint
    for _, tool in candidates:
        if tool.name not in used:
            return tool
    return None


def _pick_companions(
    candidates: List[tuple],
    primary: Tool,
    used: set,
    profile: Optional[UserProfile],
    limit: int = 2,
) -> List[Tool]:
    """Pick tools that complement the primary — different categories, ideally integrating."""
    primary_cats = set(c.lower() for c in primary.categories)
    companions = []

    # Prefer tools that integrate with the primary and cover different categories
    integrating = []
    non_integrating = []

    for _, tool in candidates:
        if tool.name in used:
            continue
        if "companion" not in tool.stack_roles and "primary" not in tool.stack_roles:
            continue  # skip pure infra for companion slot
        # Avoid heavy overlap with primary
        tool_cats = set(c.lower() for c in tool.categories)
        overlap = len(primary_cats & tool_cats) / max(len(primary_cats | tool_cats), 1)
        if overlap > 0.7:
            continue  # too similar

        if tool.integrates_with(primary.name) or primary.integrates_with(tool.name):
            integrating.append(tool)
        else:
            non_integrating.append(tool)

    for t in integrating + non_integrating:
        if len(companions) >= limit:
            break
        companions.append(t)

    return companions


def _pick_infrastructure(
    candidates: List[tuple],
    current_stack: list,
    used: set,
    profile: Optional[UserProfile],
) -> Optional[Tool]:
    """Pick an infrastructure or analytics tool that connects the stack."""
    stack_names = {e["tool"].name for e in current_stack}

    best = None
    best_integration_count = -1

    for _, tool in candidates:
        if tool.name in used:
            continue
        if "infrastructure" not in tool.stack_roles and "analytics" not in tool.stack_roles:
            continue

        # Count how many stack members this tool integrates with
        integration_count = sum(
            1 for sn in stack_names
            if tool.integrates_with(sn) or any(
                e["tool"].integrates_with(tool.name) for e in current_stack
            )
        )

        if integration_count > best_integration_count:
            best_integration_count = integration_count
            best = tool

    return best


# ======================================================================
# Comparison helper
# ======================================================================

def compare_tools(tool_name_a: str, tool_name_b: str, profile: Optional[UserProfile] = None) -> dict:
    """Side-by-side comparison of two tools in the knowledge base."""
    tool_a = next((t for t in TOOLS if t.name.lower() == tool_name_a.lower()), None)
    tool_b = next((t for t in TOOLS if t.name.lower() == tool_name_b.lower()), None)

    if not tool_a or not tool_b:
        return {"error": f"Tool not found: {tool_name_a if not tool_a else tool_name_b}"}

    def _summarize(tool: Tool) -> dict:
        return {
            "name": tool.name,
            "description": tool.description,
            "categories": tool.categories,
            "pricing": tool.pricing,
            "skill_level": tool.skill_level,
            "compliance": tool.compliance,
            "integrations": tool.integrations[:8],
            "use_cases": tool.use_cases,
            "stack_roles": tool.stack_roles,
            "fits_budget": tool.fits_budget(profile.budget) if profile else None,
            "fits_skill": tool.fits_skill(profile.skill_level) if profile else None,
        }

    result = {
        "tool_a": _summarize(tool_a),
        "tool_b": _summarize(tool_b),
        "shared_integrations": sorted(
            set(i.lower() for i in tool_a.integrations) &
            set(i.lower() for i in tool_b.integrations)
        ),
        "shared_categories": sorted(
            set(c.lower() for c in tool_a.categories) &
            set(c.lower() for c in tool_b.categories)
        ),
        "direct_integration": tool_a.integrates_with(tool_b.name) or tool_b.integrates_with(tool_a.name),
    }

    # Recommend the better fit
    try:
        from .explain import explain_tool
    except Exception:
        from praxis.explain import explain_tool

    expl_a = explain_tool(tool_a, {"keywords": [], "raw": ""}, profile)
    expl_b = explain_tool(tool_b, {"keywords": [], "raw": ""}, profile)
    score_a, score_b = expl_a["fit_score"], expl_b["fit_score"]

    if profile:
        if score_a > score_b:
            result["recommendation"] = f"{tool_a.name} is a better fit for your profile (score: {score_a} vs {score_b})"
        elif score_b > score_a:
            result["recommendation"] = f"{tool_b.name} is a better fit for your profile (score: {score_b} vs {score_a})"
        else:
            result["recommendation"] = "Both tools are equally suitable for your profile"
    else:
        # General comparison without profile context
        pop_a = getattr(tool_a, "popularity", 0) or 0
        pop_b = getattr(tool_b, "popularity", 0) or 0
        if pop_a > pop_b:
            result["recommendation"] = f"{tool_a.name} is more widely adopted (popularity: {pop_a} vs {pop_b}). {tool_b.name} may be stronger for niche use cases."
        elif pop_b > pop_a:
            result["recommendation"] = f"{tool_b.name} is more widely adopted (popularity: {pop_b} vs {pop_a}). {tool_a.name} may be stronger for niche use cases."
        else:
            result["recommendation"] = f"Both tools are similarly rated. Create a profile for a personalized recommendation."

    return result
