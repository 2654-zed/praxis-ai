# ------- Handles Task Understanding ---------
"""
Converts free-form user queries into structured intent dictionaries.

Two modes:
    1. LLM-backed (OpenAI / Anthropic) — richer, handles ambiguity
    2. Rule-based fallback — zero dependencies, always available

The caller always gets the same output shape regardless of mode:

    {
        "raw":       str,   # original text
        "intent":    str,   # primary task category
        "industry":  str,   # detected industry
        "goal":      str,   # user's goal
        "keywords":  list,  # extracted search terms
        "entities":  list,  # any tool / product names mentioned
        "clarification_needed": bool,
        "suggested_questions": list,  # follow-up Qs the system could ask
    }
"""

import json
import re
import logging
import importlib
log = logging.getLogger("praxis.interpreter")

try:
    from . import config as _cfg
except Exception:
    try:
        import config as _cfg
    except Exception:
        _cfg = None

try:
    from .intelligence import (
        expand_synonyms, correct_typos, parse_multi_intent,
        extract_negatives, _REVERSE_SYNONYMS,
    )
    _INTEL_AVAILABLE = True
except Exception:
    try:
        from intelligence import (
            expand_synonyms, correct_typos, parse_multi_intent,
            extract_negatives, _REVERSE_SYNONYMS,
        )
        _INTEL_AVAILABLE = True
    except Exception:
        _INTEL_AVAILABLE = False


# ======================================================================
# Public API
# ======================================================================

def interpret(user_input: str) -> dict:
    """Primary entry point.  Tries LLM first, falls back to rule-based."""
    raw = user_input.strip()
    if not raw:
        return _empty_result(raw)

    # Attempt LLM interpretation if configured
    if _cfg and _cfg.llm_available():
        try:
            return _llm_interpret(raw)
        except Exception as exc:
            log.warning("LLM interpretation failed, falling back to rules: %s", exc)

    return _rule_based_interpret(raw)


# ======================================================================
# LLM-backed interpretation
# ======================================================================

_SYSTEM_PROMPT = """\
You are the intent-extraction module of Praxis, an AI decision engine.
Given a user's free-form text, extract structured information.

Return **only** a JSON object (no markdown fences) with these keys:
  "intent"    – primary task category (one of: writing, design, coding, marketing, automation, research, analytics, devops, support, communication, data, ml, planning, organization)
  "industry"  – detected industry or "" if unclear
  "goal"      – user's high-level goal or "" if unclear
  "keywords"  – list of 3-8 search terms
  "entities"  – list of any specific tool/product/company names mentioned
  "clarification_needed" – true if the query is too vague for a confident recommendation
  "suggested_questions"  – list of 1-3 follow-up questions that would help narrow the recommendation (empty list if none needed)
"""


def _llm_interpret(raw: str) -> dict:
    provider = _cfg.get("llm_provider")
    if provider == "openai":
        return _openai_interpret(raw)
    elif provider == "anthropic":
        return _anthropic_interpret(raw)
    raise RuntimeError(f"Unknown LLM provider: {provider}")


def _openai_interpret(raw: str) -> dict:
    openai = importlib.import_module("openai")
    client = openai.OpenAI(api_key=_cfg.get("openai_api_key"))
    resp = client.chat.completions.create(
        model=_cfg.get("openai_model", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": raw},
        ],
        temperature=0.2,
        max_tokens=400,
    )
    text = resp.choices[0].message.content.strip()
    data = json.loads(text)
    if not isinstance(data, dict):
        log.warning("OpenAI returned non-dict JSON (%s); falling back to rule-based", type(data).__name__)
        return _rule_based_interpret(raw)
    return _normalize_llm_output(raw, data)


def _anthropic_interpret(raw: str) -> dict:
    anthropic = importlib.import_module("anthropic")
    client = anthropic.Anthropic(api_key=_cfg.get("anthropic_api_key"))
    resp = client.messages.create(
        model=_cfg.get("anthropic_model", "claude-3-haiku-20240307"),
        max_tokens=400,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw}],
    )
    text = resp.content[0].text.strip()
    data = json.loads(text)
    if not isinstance(data, dict):
        log.warning("Anthropic returned non-dict JSON (%s); falling back to rule-based", type(data).__name__)
        return _rule_based_interpret(raw)
    return _normalize_llm_output(raw, data)


def _normalize_llm_output(raw: str, data: dict) -> dict:
    """Ensure LLM output matches the expected schema."""
    return {
        "raw": raw,
        "intent": data.get("intent", ""),
        "industry": data.get("industry", ""),
        "goal": data.get("goal", ""),
        "keywords": data.get("keywords", []),
        "entities": data.get("entities", []),
        "clarification_needed": bool(data.get("clarification_needed", False)),
        "suggested_questions": data.get("suggested_questions", []),
    }


# ======================================================================
# Enhanced rule-based interpretation (zero dependencies)
# ======================================================================

# Stop words to strip from keyword extraction
_STOP_WORDS = {
    "i", "need", "help", "with", "for", "a", "the",
    "please", "want", "to", "my", "some", "me", "on", "in",
    "an", "is", "it", "can", "you", "do", "how", "what",
    "that", "this", "of", "and", "or", "am", "are", "be",
    "looking", "find", "get", "best", "good", "recommend",
    "suggest", "tool", "tools", "use", "using", "should",
}

# Known intent tokens
_INTENTS = {
    "marketing", "design", "automation", "coding", "research",
    "writing", "planning", "organization", "analytics", "data",
    "devops", "support", "communication", "ml", "video", "audio",
    "sales", "email", "social media", "seo", "no-code", "security",
    "productivity", "images", "forms", "payments", "recruiting",
    "legal", "accounting", "presentations",
}

# Extended intents reachable via synonym expansion
_SYNONYM_LIKE_INTENTS = _INTENTS | {
    "video", "audio", "sales", "email", "social media", "seo",
    "no-code", "security", "productivity", "images", "forms",
    "payments", "recruiting", "legal", "accounting", "presentations",
}

# Known industries
_INDUSTRIES = {
    "restaurant", "restaurants", "ecommerce", "e-commerce", "finance",
    "healthcare", "education", "startup", "retail", "saas",
    "small business", "agency", "enterprise", "fintech", "media",
    "real estate", "legal", "nonprofit",
}

# Goal token → canonical goal
_GOAL_MAP = {
    "grow": "growth", "growth": "growth", "scale": "growth", "scaling": "growth",
    "traffic": "traffic", "visitors": "traffic", "seo": "traffic",
    "sales": "sales", "revenue": "sales", "sell": "sales", "monetize": "sales",
    "prototype": "prototype", "mvp": "prototype", "build": "prototype",
    "learn": "learn", "learning": "learn", "study": "learn",
    "hire": "hire", "hiring": "hire", "recruit": "hire",
    "automate": "automation", "automating": "automation", "efficiency": "automation",
    "save": "cost reduction", "cost": "cost reduction", "cheaper": "cost reduction",
    "collaborate": "collaboration", "teamwork": "collaboration",
}

# Verb → intent mapping
_VERB_MAP = {
    "design": "design", "create": "design", "build": "coding",
    "automate": "automation", "automating": "automation",
    "market": "marketing", "advertise": "marketing", "promote": "marketing",
    "write": "writing", "draft": "writing", "blog": "writing",
    "research": "research", "analyze": "analytics", "analyse": "analytics",
    "monitor": "devops", "deploy": "devops", "track": "analytics",
    "support": "support", "communicate": "communication",
    "plan": "planning", "organize": "organization",
    "record": "video", "edit": "video", "film": "video",
    "sell": "sales", "prospect": "sales", "outreach": "sales",
    "email": "email", "invoice": "accounting", "pay": "payments",
    "hire": "recruiting", "recruit": "recruiting",
    "schedule": "productivity", "manage": "productivity",
    "generate": "images", "illustrate": "design",
    "transcribe": "audio", "podcast": "audio",
    "secure": "security", "encrypt": "security",
}

# Known tool/product names (lowercased) for entity extraction
_KNOWN_TOOLS = {
    "chatgpt", "canva", "zapier", "notion", "figma", "grammarly",
    "hugging face", "huggingface", "airtable", "github", "openai",
    "anthropic", "claude", "pinecone", "weaviate", "descript",
    "replicate", "stability", "surfer", "ahrefs", "hotjar",
    "amplitude", "sentry", "datadog", "segment", "intercom",
    "zendesk", "loom", "otter", "typeform", "slack", "hubspot",
    "jira", "asana", "trello", "monday", "copilot", "cursor",
    "replit", "tabnine", "jasper", "midjourney", "dall-e", "dalle",
    "runway", "elevenlabs", "synthesia", "stripe", "shopify",
    "salesforce", "mailchimp", "semrush", "buffer", "hootsuite",
    "linear", "vercel", "supabase", "postman", "langchain",
    "cohere", "mistral", "perplexity", "gemini", "miro",
    "clickup", "calendly", "freshdesk", "drift", "tidio",
    "bubble", "retool", "make", "n8n", "tableau", "snowflake",
    "mixpanel", "quickbooks", "brex", "vanta", "greenhouse",
}


def _rule_based_interpret(raw: str) -> dict:
    cleaned = raw.lower()

    # ── Intelligence Layer: negatives ──
    negatives = []
    if _INTEL_AVAILABLE:
        cleaned, negatives = extract_negatives(cleaned)

    words = [w for w in re.split(r'\W+', cleaned) if w and w not in _STOP_WORDS]

    # ── Intelligence Layer: typo correction ──
    corrections = {}
    if _INTEL_AVAILABLE and words:
        words, corrections = correct_typos(words, cutoff=0.75)

    found_intent = None
    found_industry = None
    found_goal = None
    entities = []

    # ── Intelligence Layer: multi-intent ──
    sub_intents = []
    if _INTEL_AVAILABLE:
        sub_intents = parse_multi_intent(cleaned)

    # Scan for intents, industries, goals
    for w in words:
        if not found_intent and w in _INTENTS:
            found_intent = w
        if not found_industry and w in _INDUSTRIES:
            found_industry = w
        if not found_goal and w in _GOAL_MAP:
            found_goal = _GOAL_MAP[w]

    # ── Intelligence Layer: synonym-based intent detection ──
    if not found_intent and _INTEL_AVAILABLE:
        # Try matching multi-word phrases first
        for phrase_len in (3, 2):
            for i in range(len(words) - phrase_len + 1):
                phrase = " ".join(words[i:i + phrase_len])
                if phrase in _REVERSE_SYNONYMS:
                    canonical = _REVERSE_SYNONYMS[phrase]
                    if canonical in _INTENTS:
                        found_intent = canonical
                        break
            if found_intent:
                break
        # Then try single-word synonym lookup
        if not found_intent:
            for w in words:
                if w in _REVERSE_SYNONYMS:
                    canonical = _REVERSE_SYNONYMS[w]
                    if canonical in _INTENTS or canonical in _SYNONYM_LIKE_INTENTS:
                        found_intent = canonical
                        break

    # Verb-based intent fallback
    if not found_intent and words:
        found_intent = _VERB_MAP.get(words[0])

    # Entity extraction — check bigrams and unigrams
    cleaned_lower = cleaned
    for tool in _KNOWN_TOOLS:
        if tool in cleaned_lower:
            entities.append(tool)

    # Assemble keywords
    keywords = []
    if found_intent:
        keywords.append(found_intent)
    if found_industry:
        keywords.append(found_industry)
    if found_goal:
        keywords.append(found_goal)
    keywords.extend([w for w in words if w not in keywords])

    # Add secondary intents from multi-intent parsing
    if _INTEL_AVAILABLE and len(sub_intents) > 1:
        for sub in sub_intents[1:]:
            sub_words = [sw for sw in re.split(r'\W+', sub.lower()) if sw and sw not in _STOP_WORDS]
            for sw in sub_words:
                if sw in _INTENTS and sw not in keywords:
                    keywords.append(sw)
                elif sw in _REVERSE_SYNONYMS:
                    canonical = _REVERSE_SYNONYMS[sw]
                    if canonical not in keywords:
                        keywords.append(canonical)

    # ── Intelligence Layer: expand synonyms ──
    if _INTEL_AVAILABLE:
        keywords = expand_synonyms(keywords)

    log.info("interpret: raw=%r → intent=%s, industry=%s, keywords=%s, negatives=%s",
             raw, found_intent, found_industry, keywords[:6], negatives)

    # Determine if clarification is needed
    clarification_needed = not found_intent and len(words) < 3
    suggested_questions = []
    if clarification_needed:
        suggested_questions = [
            "What's the main task you're trying to accomplish?",
            "What industry or domain are you working in?",
        ]
    elif not found_industry:
        suggested_questions.append("What industry are you in? This helps us pick tools that fit your context.")

    return {
        "raw": raw,
        "intent": found_intent,
        "industry": found_industry,
        "goal": found_goal,
        "keywords": keywords,
        "entities": entities,
        "negatives": negatives,
        "corrections": corrections,
        "multi_intents": sub_intents if len(sub_intents) > 1 else [],
        "clarification_needed": clarification_needed,
        "suggested_questions": suggested_questions,
    }


def _empty_result(raw: str) -> dict:
    return {
        "raw": raw,
        "intent": None,
        "industry": None,
        "goal": None,
        "keywords": [],
        "entities": [],
        "clarification_needed": True,
        "suggested_questions": ["Please describe the task you need help with."],
    }

