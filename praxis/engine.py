# ---------------- Decision Engine ----------------
"""
Core scoring & ranking logic for Praxis.

Responsibilities:
    • score_tool()  — multi-signal scoring for a single tool
    • find_tools()  — search + rank + optional profile filtering
    • score_profile_fit() — additional scoring based on user profile

The engine is intentionally kept as a pure-function module so it can be
used by both the CLI and the stack composer without side effects.
"""

try:
    from .data import TOOLS
except Exception:
    from data import TOOLS
try:
    from . import config as _cfg
except Exception:
    try:
        import config as _cfg
    except Exception:
        _cfg = None
from difflib import SequenceMatcher
import logging
log = logging.getLogger("praxis.engine")

# Diagnostics — query failure tracking
try:
    from .diagnostics import record_failure as _record_failure, MIN_RESULTS_THRESHOLD, LOW_SCORE_THRESHOLD
    _DIAG_AVAILABLE = True
except Exception:
    try:
        from diagnostics import record_failure as _record_failure, MIN_RESULTS_THRESHOLD, LOW_SCORE_THRESHOLD
        _DIAG_AVAILABLE = True
    except Exception:
        _DIAG_AVAILABLE = False


def _w(key: str, fallback):
    """Read a scoring weight from config, fall back to hardcoded default."""
    if _cfg:
        try:
            return _cfg.get(key, fallback)
        except Exception:
            pass
    return fallback

# Import intelligence layer
try:
    from .intelligence import (
        get_tfidf_index, get_learned_boost, get_industry_boost,
        diversity_rerank, initialize as _init_intelligence,
    )
    _INTEL_AVAILABLE = True
except Exception:
    try:
        from intelligence import (
            get_tfidf_index, get_learned_boost, get_industry_boost,
            diversity_rerank, initialize as _init_intelligence,
        )
        _INTEL_AVAILABLE = True
    except Exception:
        _INTEL_AVAILABLE = False

# Initialize intelligence on first import
if _INTEL_AVAILABLE:
    try:
        _init_intelligence(TOOLS)
    except Exception:
        _INTEL_AVAILABLE = False


def normalize(text: str) -> str:
    """Lowercase + basic cleanup."""
    return text.lower().strip()


# ======================================================================
# Tool scoring
# ======================================================================

def score_tool(tool, keywords):
    """
    Score a tool against a list of search keywords.

    Signal weights:
        category match  → 4
        tag match       → 3
        keyword match   → 2
        name/desc match → 1
        fuzzy name      → up to 3
        fuzzy desc      → up to 2
        popularity      → tool.popularity
        TF-IDF          → up to 5 (semantic similarity)
        learned boost   → up to 4 (from feedback signals)
    """
    score = 0
    desc_blob = (tool.description or "").lower()
    name_blob = (tool.name or "").lower()
    cat_set = {c.lower() for c in getattr(tool, "categories", [])}
    tag_set = {t.lower() for t in getattr(tool, "tags", [])}
    kw_set = {k.lower() for k in getattr(tool, "keywords", [])}
    uc_blob = " ".join(getattr(tool, "use_cases", [])).lower()

    w_cat = _w("weight_category_match", 4)
    w_tag = _w("weight_tag_match", 3)
    w_kw  = _w("weight_keyword_match", 2)
    w_nd  = _w("weight_name_desc_match", 1)
    w_uc  = _w("weight_usecase_bonus", 1)

    for word in keywords:
        w = str(word).lower()
        if w in cat_set:
            score += w_cat
        elif w in tag_set:
            score += w_tag
        elif w in kw_set:
            score += w_kw
        elif w in desc_blob or w in name_blob:
            score += w_nd
        # Use-case bonus
        if w in uc_blob:
            score += w_uc

    # Fuzzy matching
    joined = " ".join(str(k).lower() for k in keywords)
    try:
        name_ratio = SequenceMatcher(None, joined, name_blob).ratio()
        desc_ratio = SequenceMatcher(None, joined, desc_blob).ratio()
    except Exception:
        name_ratio = desc_ratio = 0

    if name_ratio > 0.75:
        score += _w("weight_fuzzy_name_strong", 3)
    elif name_ratio > 0.5:
        score += _w("weight_fuzzy_name_weak", 1)

    if desc_ratio > 0.75:
        score += _w("weight_fuzzy_desc_strong", 2)
    elif desc_ratio > 0.5:
        score += _w("weight_fuzzy_desc_weak", 1)

    score += int(getattr(tool, "popularity", 0) or 0)

    # ── TF-IDF semantic scoring ──
    if _INTEL_AVAILABLE:
        try:
            tfidf = get_tfidf_index()
            tfidf_score = tfidf.score(keywords, tool.name)
            scale = _w("weight_tfidf_scale", 8)
            score += int(tfidf_score * scale)
        except Exception:
            pass

    # ── Learned feedback boost (A/B testable) ──
    if _INTEL_AVAILABLE and _w("enable_learned_boosts", True):
        try:
            score += get_learned_boost(tool.name)
        except Exception:
            pass

    return score


# Budget-related keywords that signal the user cares about pricing
_BUDGET_SIGNALS = {"budget", "price", "pricing", "cost", "cheap", "free",
                   "affordable", "expensive", "money", "subscription", "pay",
                   "tier", "plan", "enterprise", "premium", "$"}


def score_profile_fit(tool, profile, intent=None) -> int:
    """Extra score adjustments based on the user profile.

    Returns a positive or negative integer modifier.
    """
    if profile is None:
        return 0

    mod = 0

    # Budget fit — only factor in when the query mentions pricing
    raw = ((intent or {}).get("raw") or "").lower()
    budget_mentioned = any(w in raw for w in _BUDGET_SIGNALS)
    if budget_mentioned:
        if hasattr(tool, "fits_budget") and tool.fits_budget(getattr(profile, "budget", "medium")):
            mod += _w("weight_profile_budget_fit", 3)
        else:
            mod += _w("weight_profile_budget_miss", -3)

    # Skill fit
    if hasattr(tool, "fits_skill") and tool.fits_skill(getattr(profile, "skill_level", "beginner")):
        mod += _w("weight_profile_skill_fit", 2)
    else:
        mod += _w("weight_profile_skill_miss", -4)

    # Integration with existing tools
    existing = getattr(profile, "existing_tools", [])
    for et in existing:
        if hasattr(tool, "integrates_with") and tool.integrates_with(et):
            mod += _w("weight_profile_integration", 3)
            break

    # Compliance
    constraints = getattr(profile, "constraints", [])
    for c in constraints:
        tool_compliance = [x.upper() for x in getattr(tool, "compliance", [])]
        if c.upper() in tool_compliance:
            mod += _w("weight_profile_compliance_hit", 2)
        else:
            mod += _w("weight_profile_compliance_miss", -2)

    # Already-used penalty (user probably wants new suggestions)
    if hasattr(profile, "already_uses") and profile.already_uses(tool.name):
        mod += _w("weight_profile_already_used", -2)

    return mod


# ======================================================================
# Search
# ======================================================================

def find_tools(user_input, top_n: int = 5, categories_filter: list = None, profile=None):
    """Main search function.

    Args:
        user_input:        raw string OR structured interpreter output (dict)
        top_n:             max results to return
        categories_filter: optional category whitelist
        profile:           optional UserProfile for profile-aware scoring

    Returns:
        list of Tool objects, highest score first.
    """
    # Build keyword list
    if isinstance(user_input, dict):
        keywords = []
        for k in (user_input.get("intent"), user_input.get("industry"), user_input.get("goal")):
            if k:
                keywords.append(str(k))
        keywords.extend(user_input.get("keywords", []))
        if not keywords and user_input.get("raw"):
            keywords = normalize(user_input.get("raw")).split()
        negatives = user_input.get("negatives", [])
        industry = user_input.get("industry")
    else:
        keywords = normalize(str(user_input)).split()
        negatives = []
        industry = None

    # Normalize filters
    if categories_filter:
        categories_filter = [c.lower().strip() for c in categories_filter if c.strip()]
    else:
        categories_filter = None

    # Get industry from profile if not in query
    if not industry and profile:
        industry = getattr(profile, "industry", None)

    scored = []

    for tool in TOOLS:
        # ── Negative filter: exclude tools matching negative terms ──
        if negatives:
            tool_text = (tool.name + " " + (tool.description or "")).lower()
            if any(neg in tool_text or neg == tool.name.lower() for neg in negatives):
                continue

        # Category filter gate
        if categories_filter:
            tool_cats = [c.lower() for c in tool.categories]
            if not any(fc in tool_cats for fc in categories_filter):
                continue

        base = score_tool(tool, keywords)
        profile_mod = score_profile_fit(tool, profile, intent=user_input if isinstance(user_input, dict) else None)

        # ── Industry context boost ──
        industry_mod = 0
        if _INTEL_AVAILABLE and industry:
            try:
                industry_mod = get_industry_boost(industry, tool)
            except Exception:
                pass

        total = base + profile_mod + industry_mod

        if total > 0:
            scored.append((total, tool))

    scored.sort(key=lambda x: x[0], reverse=True)

    top_score = scored[0][0] if scored else 0
    raw_query = user_input if isinstance(user_input, str) else user_input.get("raw", "")

    log.info("find_tools: query=%r → %d candidates scored, top=%s",
             raw_query, len(scored),
             scored[0][1].name if scored else "none")

    # ── Track query failures / low-confidence results ──
    if _DIAG_AVAILABLE:
        if len(scored) < MIN_RESULTS_THRESHOLD or top_score < LOW_SCORE_THRESHOLD:
            try:
                _record_failure(
                    raw_query,
                    results_count=len(scored),
                    top_score=top_score,
                    interpreted=user_input if isinstance(user_input, dict) else None,
                )
            except Exception:
                pass

    # ── Diversity re-ranking ──
    if _INTEL_AVAILABLE and len(scored) > top_n:
        try:
            scored = diversity_rerank(scored, top_n=top_n)
        except Exception:
            pass

    return [tool for _, tool in scored[:top_n]]

