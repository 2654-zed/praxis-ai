# --------------- Vendor Intelligence & Risk Assessment ---------------
"""
Praxis Vendor Intelligence Engine.

Enterprise-grade due diligence for AI tool procurement. This module provides
automated vendor risk assessment, transparency scoring, and strategic
flexibility analysis to support informed technology decisions.

Assessment Framework:
    1. Transparency Analysis  — Vendor disclosure practices, compliance posture
    2. Flexibility Analysis   — Portability, lock-in risk, switching cost
    3. Risk Indicators        — Gaps between vendor positioning and observable reality
    4. Dependency Profiling   — Vendor relationship dynamics, data exposure mapping
    5. Cost-of-Exit Analysis  — Total cost of switching or leaving
    6. Vendor Intelligence Report — Consolidated assessment narrative

Praxis evaluates every vendor against the questions enterprise procurement
teams need answered before committing budget and data:
    · Ownership structure & funding model
    · Revenue alignment with customer outcomes
    · Data handling practices & compliance posture
    · Switching costs & portability constraints
    · Long-term strategic dependency risk
"""

from typing import Dict, List, Optional, Tuple


# ======================================================================
# 1. Vendor Ownership & Revenue Intelligence
# ======================================================================

# Tool name (lower) → known vendor intelligence data
# Curated from public filings, documentation, and published policies.

_TOOL_INTEL = {
    # --- Major AI Platforms ---
    "chatgpt": {
        "owner": "OpenAI (Microsoft-backed)",
        "revenue_model": "freemium + API usage",
        "data_practice": "Inputs may be used for model training unless opted out. Enterprise tier excludes training.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "Conversations exportable as JSON. No model portability.",
        "data_exposure": "Prompts, reasoning patterns, creative workflows",
        "vendor_value_capture": "Training signal, usage analytics, market intelligence",
    },
    "claude": {
        "owner": "Anthropic (Amazon-backed)",
        "revenue_model": "freemium + API usage",
        "data_practice": "Does not train on user conversations by default. Enterprise options available.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "Conversations exportable. No model portability.",
        "data_exposure": "Prompts, reasoning chains, workflow patterns",
        "vendor_value_capture": "Usage analytics, safety research signal",
    },
    "gemini": {
        "owner": "Google / Alphabet",
        "revenue_model": "freemium + ecosystem lock-in",
        "data_practice": "Integrated with Google account. Data practices follow Google's broad collection policies.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Tied to Google ecosystem. Limited standalone export.",
        "data_exposure": "Queries feed into Google's broader data graph",
        "vendor_value_capture": "Search intent data, product integration leverage",
    },
    "copilot": {
        "owner": "Microsoft / GitHub",
        "revenue_model": "subscription",
        "data_practice": "Business tier excludes code from training. Individual plans may contribute to model improvement.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "Code remains yours. Tool is IDE-dependent.",
        "data_exposure": "Codebase patterns, development workflow telemetry",
        "vendor_value_capture": "Code training data (individual plans), developer ecosystem retention",
    },

    # --- Open Source Champions ---
    "hugging face": {
        "owner": "Hugging Face (independent, VC-funded)",
        "revenue_model": "freemium hosting + enterprise",
        "data_practice": "Open platform. Model hosting is transparent. You control your models and data.",
        "open_source": True,
        "lock_in": "low",
        "portability": "Full model portability. Self-hosting available.",
        "data_exposure": "Public model contributions are shared. Private repos stay private.",
        "vendor_value_capture": "Community ecosystem, enterprise upsell pipeline",
    },
    "n8n": {
        "owner": "n8n GmbH (open-source company)",
        "revenue_model": "open-source + cloud hosting",
        "data_practice": "Self-hostable. Your data stays on your infrastructure.",
        "open_source": True,
        "lock_in": "low",
        "portability": "Workflows exportable. Self-hosting means full control.",
        "data_exposure": "Nothing if self-hosted. Cloud version: workflow metadata.",
        "vendor_value_capture": "Cloud hosting revenue, community contributions",
    },
    "supabase": {
        "owner": "Supabase Inc (open-source company)",
        "revenue_model": "open-source + cloud hosting",
        "data_practice": "PostgreSQL-based. Self-hostable. Full data sovereignty possible.",
        "open_source": True,
        "lock_in": "low",
        "portability": "Standard PostgreSQL. Full export. Self-hosting available.",
        "data_exposure": "Nothing if self-hosted. Cloud: standard hosting relationship.",
        "vendor_value_capture": "Cloud hosting revenue, ecosystem growth",
    },
    "langchain": {
        "owner": "LangChain Inc (VC-funded)",
        "revenue_model": "open-source framework + LangSmith SaaS",
        "data_practice": "Framework is local. LangSmith tracing sends data to their servers.",
        "open_source": True,
        "lock_in": "low",
        "portability": "Code is yours. Framework abstractions may create soft lock-in.",
        "data_exposure": "LangSmith users: trace data, chain execution patterns",
        "vendor_value_capture": "Developer ecosystem, LangSmith conversion pipeline",
    },
    "posthog": {
        "owner": "PostHog Inc (open-source company)",
        "revenue_model": "open-source + cloud hosting",
        "data_practice": "Self-hostable. Cloud option available. You own your analytics data.",
        "open_source": True,
        "lock_in": "low",
        "portability": "Self-hostable. Event data exportable.",
        "data_exposure": "Cloud users: analytics event stream. Self-hosted: nothing.",
        "vendor_value_capture": "Cloud hosting revenue",
    },

    # --- Automation Platforms ---
    "zapier": {
        "owner": "Zapier Inc (private, profitable)",
        "revenue_model": "freemium + usage-based pricing",
        "data_practice": "Data passes through Zapier servers. Task logs retained for debugging.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Workflows are proprietary format. Rebuilding elsewhere is manual.",
        "data_exposure": "Workflow logic, integration data flows, business process architecture",
        "vendor_value_capture": "Integration intelligence, pricing leverage as workflow volume grows",
    },
    "make": {
        "owner": "Celonis (acquired Make/Integromat)",
        "revenue_model": "freemium + usage-based",
        "data_practice": "Data passes through Make servers. Scenario logs retained.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Scenarios are proprietary. Migration requires rebuilding.",
        "data_exposure": "Automation logic, data routing patterns, process architecture",
        "vendor_value_capture": "Process intelligence, enterprise upsell pipeline",
    },

    # --- Design Tools ---
    "canva ai": {
        "owner": "Canva Pty Ltd (Australian, profitable)",
        "revenue_model": "freemium + subscription",
        "data_practice": "Uploads stored on Canva servers. AI features process through their infrastructure.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "Designs exportable as images/PDF. Templates not portable.",
        "data_exposure": "Design assets, brand materials, creative patterns",
        "vendor_value_capture": "Design trend data, template improvement signal, enterprise pipeline",
    },
    "figma ai": {
        "owner": "Figma (independent after failed Adobe acquisition)",
        "revenue_model": "freemium + subscription",
        "data_practice": "Designs stored on Figma servers. AI features use design data for suggestions.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Limited export options. Design system lock-in is significant.",
        "data_exposure": "Design system, component library, team collaboration workflows",
        "vendor_value_capture": "Design intelligence, collaboration platform dependency",
    },
    "midjourney": {
        "owner": "Midjourney Inc (independent, profitable)",
        "revenue_model": "subscription",
        "data_practice": "All generated images are public by default (unless paid plan). Prompts may inform model training.",
        "open_source": False,
        "lock_in": "low",
        "portability": "Images are exportable. Prompts are yours. No ecosystem lock-in.",
        "data_exposure": "Creative prompts, aesthetic preference patterns",
        "vendor_value_capture": "Training signal, community content, subscription revenue",
    },

    # --- CRM / Sales ---
    "hubspot": {
        "owner": "HubSpot Inc (public, HUBS)",
        "revenue_model": "freemium + tiered subscription",
        "data_practice": "Customer data stored on HubSpot servers. Marketing analytics tracked.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Data exportable as CSV. Workflow logic and automations not portable.",
        "data_exposure": "Customer relationship history, pipeline data, communication patterns",
        "vendor_value_capture": "Market intelligence, upsell leverage as CRM data volume grows",
    },
    "salesforce": {
        "owner": "Salesforce Inc (public, CRM)",
        "revenue_model": "subscription (enterprise-focused)",
        "data_practice": "Customer data stored on Salesforce servers. Einstein AI processes your data for insights.",
        "open_source": False,
        "lock_in": "very high",
        "portability": "Data exportable but ecosystem migration is notoriously expensive.",
        "data_exposure": "Customer data, sales processes, business intelligence",
        "vendor_value_capture": "Deep enterprise platform dependency, cross-sell across 300+ products",
    },

    # --- Writing ---
    "grammarly": {
        "owner": "Grammarly Inc (Ukrainian-American, VC-funded)",
        "revenue_model": "freemium + subscription",
        "data_practice": "Processes all text you type. Enterprise plan offers enhanced data controls.",
        "open_source": False,
        "lock_in": "low",
        "portability": "No data lock-in. Text is yours. Tool is substitutable.",
        "data_exposure": "All written content — emails, documents, messages processed in real-time",
        "vendor_value_capture": "Language corpus, writing pattern intelligence at scale",
    },
    "jasper": {
        "owner": "Jasper AI (VC-funded)",
        "revenue_model": "subscription",
        "data_practice": "Content generated stored on Jasper servers. Brand voice training uses your inputs.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "Content exportable. Brand voice profiles not portable.",
        "data_exposure": "Brand voice data, marketing strategy patterns, content workflow",
        "vendor_value_capture": "Content generation patterns, marketing intelligence",
    },

    # --- Communication ---
    "notion ai": {
        "owner": "Notion Labs (VC-funded, $10B+ valuation)",
        "revenue_model": "freemium + subscription + AI add-on",
        "data_practice": "All workspace data on Notion servers. AI features process your docs.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Export to Markdown/CSV exists but loses structure, relations, and views.",
        "data_exposure": "Knowledge base, organizational structure, institutional memory",
        "vendor_value_capture": "Knowledge graph intelligence, team workflow patterns, retention dependency",
    },
    "slack": {
        "owner": "Salesforce (acquired for $27.7B)",
        "revenue_model": "freemium + subscription",
        "data_practice": "All messages stored on Slack/Salesforce servers. Employers have full access to all messages.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Message export available for admins. History, context, and culture not exportable.",
        "data_exposure": "Team communication history, decision-making patterns, organizational culture",
        "vendor_value_capture": "Workplace intelligence, Salesforce ecosystem integration",
    },

    # --- Analytics ---
    "amplitude": {
        "owner": "Amplitude Inc (public, AMPL)",
        "revenue_model": "freemium + usage-based",
        "data_practice": "Event data stored on Amplitude servers. They analyze your users' behavior.",
        "open_source": False,
        "lock_in": "high",
        "portability": "Event data exportable. Dashboards, cohorts, and analyses not portable.",
        "data_exposure": "User behavioral data, product usage patterns, cohort analytics",
        "vendor_value_capture": "Aggregate product intelligence, benchmarking data",
    },
    "mixpanel": {
        "owner": "Mixpanel Inc (VC-funded)",
        "revenue_model": "freemium + usage-based",
        "data_practice": "Event data stored on Mixpanel servers. EU data residency available.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "Event data exportable. Analysis logic must be rebuilt.",
        "data_exposure": "User behavioral data, product interaction patterns",
        "vendor_value_capture": "Aggregate analytics intelligence, market trend data",
    },
    "segment": {
        "owner": "Twilio (acquired for $3.2B)",
        "revenue_model": "usage-based",
        "data_practice": "All customer data routes through Segment servers. CDP model means they see everything.",
        "open_source": False,
        "lock_in": "very high",
        "portability": "Data routing config is proprietary. Switching CDPs is a major project.",
        "data_exposure": "Complete customer data pipeline — every event, every identity",
        "vendor_value_capture": "Customer data intelligence, data routing platform dependency",
    },

    # --- E-commerce ---
    "shopify": {
        "owner": "Shopify Inc (public, SHOP)",
        "revenue_model": "subscription + transaction fees",
        "data_practice": "All store data on Shopify servers. They process your customers' data.",
        "open_source": False,
        "lock_in": "very high",
        "portability": "Product/order CSV export exists. Theme, apps, and customizations don't migrate.",
        "data_exposure": "Full commerce data: products, customers, revenue, marketing analytics",
        "vendor_value_capture": "Commerce intelligence, payment processing revenue, ecosystem dependency",
    },
    "stripe": {
        "owner": "Stripe Inc (private, ~$50B+ valuation)",
        "revenue_model": "transaction fees",
        "data_practice": "Payment data processed per PCI compliance. Financial data stored on Stripe servers.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "API-based integration. Switching payment processors is non-trivial but possible.",
        "data_exposure": "Transaction data, revenue patterns, customer payment behavior",
        "vendor_value_capture": "Financial intelligence, economic trend data, network effects",
    },

    # --- Security ---
    "vanta": {
        "owner": "Vanta Inc (VC-funded)",
        "revenue_model": "subscription",
        "data_practice": "Connects to your infrastructure for compliance scanning. Deep access granted.",
        "open_source": False,
        "lock_in": "medium",
        "portability": "Compliance evidence exportable. Automation workflows not portable.",
        "data_exposure": "Security posture, infrastructure topology, access control patterns",
        "vendor_value_capture": "Aggregate security intelligence across customer base, compliance patterns",
    },
}


# ======================================================================
# 2. Heuristic Assessment (for vendors without curated intelligence)
# ======================================================================

def _heuristic_assessment(tool) -> dict:
    """When curated intel is unavailable, derive assessment from
    observable data points — pricing, compliance, categories."""

    assessment = {
        "owner": "Not yet profiled — verify ownership before committing business-critical data",
        "revenue_model": _infer_revenue_model(tool),
        "data_practice": _infer_data_practice(tool),
        "open_source": _infer_open_source(tool),
        "lock_in": _infer_lock_in(tool),
        "portability": "Not yet assessed — confirm data export capabilities before onboarding",
        "data_exposure": _infer_what_you_give(tool),
        "vendor_value_capture": "Usage data at minimum. Likely more — verify with vendor.",
    }
    return assessment


def _infer_revenue_model(tool) -> str:
    pricing = getattr(tool, "pricing", {}) or {}
    if pricing.get("free_tier") and not pricing.get("starter") and not pricing.get("pro"):
        return "Fully free — revenue model unclear, assess how the service is sustained"
    if pricing.get("free_tier"):
        return "Freemium — free tier for acquisition, paid tier for retention"
    if pricing.get("starter") or pricing.get("pro"):
        return "Subscription — direct revenue model, typically aligned incentives"
    return "Revenue model unclear — investigate before committing"


def _infer_data_practice(tool) -> str:
    compliance = getattr(tool, "compliance", [])
    if "SOC2" in compliance and "GDPR" in compliance:
        return "SOC2 + GDPR compliant — meets baseline enterprise security and privacy standards"
    if "SOC2" in compliance:
        return "SOC2 compliant — third-party security attestation on file"
    if "GDPR" in compliance:
        return "GDPR compliant — European data protection baseline met"
    return "No stated compliance — requires additional due diligence for sensitive data"


def _infer_open_source(tool) -> bool:
    name_lower = tool.name.lower()
    tags_lower = {t.lower() for t in getattr(tool, "tags", [])}
    kw_lower = {k.lower() for k in getattr(tool, "keywords", [])}
    signals = tags_lower | kw_lower
    return "open-source" in signals or "open source" in signals or "self-hosted" in signals


def _infer_lock_in(tool) -> str:
    integrations = getattr(tool, "integrations", [])
    categories = [c.lower() for c in getattr(tool, "categories", [])]

    # High lock-in indicators
    if any(cat in ("crm", "e-commerce", "data", "analytics") for cat in categories):
        return "likely high — platform categories typically create deep operational dependency"
    if len(integrations) > 8:
        return "medium — extensive integration surface can create ecosystem dependency"
    if any(cat in ("writing", "images", "audio") for cat in categories):
        return "low — output is typically exportable and portable"
    return "not yet assessed — evaluate switching costs before procurement"


def _infer_what_you_give(tool) -> str:
    categories = [c.lower() for c in getattr(tool, "categories", [])]
    if any(c in ("writing", "research", "brainstorming") for c in categories):
        return "Content, reasoning patterns, intellectual property"
    if any(c in ("analytics", "data") for c in categories):
        return "User behavioral data, business metrics, product telemetry"
    if any(c in ("design", "images", "video") for c in categories):
        return "Creative assets, brand materials, visual identity data"
    if any(c in ("automation", "integration", "workflows") for c in categories):
        return "Business logic, process architecture, integration mappings"
    if any(c in ("sales", "crm", "email") for c in categories):
        return "Customer relationship data, sales pipeline, communication logs"
    if any(c in ("coding", "devops") for c in categories):
        return "Codebase data, infrastructure patterns, deployment telemetry"
    return "Work product and usage patterns"


# ======================================================================
# 3. Core Assessment Functions
# ======================================================================

def get_tool_intel(tool) -> dict:
    """Retrieve vendor intelligence for a tool.
    Uses curated intel when available, heuristic analysis otherwise."""
    name_key = tool.name.lower()
    if name_key in _TOOL_INTEL:
        return dict(_TOOL_INTEL[name_key])
    return _heuristic_assessment(tool)


def assess_transparency(tool) -> dict:
    """Score vendor transparency and disclosure practices.

    Returns:
        {
            "score": int (0-100),
            "grade": str (A-F),
            "signals": list[str],
            "concerns": list[str],
        }
    """
    intel = get_tool_intel(tool)
    score = 40  # baseline
    signals = []
    concerns = []

    # Open source is the gold standard of transparency
    if intel.get("open_source"):
        score += 25
        signals.append("Open source — code-level auditability available")
    else:
        concerns.append("Closed source — transparency limited to published documentation")

    # Compliance attestations
    compliance = getattr(tool, "compliance", [])
    if "SOC2" in compliance:
        score += 8
        signals.append("SOC2 attested — third-party security audit on file")
    if "GDPR" in compliance:
        score += 7
        signals.append("GDPR compliant — European data protection standards met")
    if "HIPAA" in compliance:
        score += 10
        signals.append("HIPAA compliant — healthcare-grade data protection")
    if not compliance:
        score -= 10
        concerns.append("No stated compliance certifications")

    # Revenue model clarity
    if "subscription" in intel.get("revenue_model", ""):
        score += 5
        signals.append("Subscription model — direct revenue alignment with customers")
    elif "free" in intel.get("revenue_model", "").lower() and not intel.get("open_source"):
        score -= 5
        concerns.append("Free tier without open source — revenue model warrants review")

    # Data practice specificity
    if intel.get("data_practice") and len(intel["data_practice"]) > 30:
        score += 5
    else:
        score -= 5
        concerns.append("Limited data practice disclosure")

    # Known owner vs unknown
    if "unknown" not in intel.get("owner", "").lower() and "not yet" not in intel.get("owner", "").lower():
        score += 5
        signals.append(f"Vendor: {intel['owner']}")
    else:
        concerns.append("Vendor ownership not yet confirmed")

    score = max(5, min(100, score))

    # Grade
    if score >= 80:
        grade = "A"
    elif score >= 65:
        grade = "B"
    elif score >= 50:
        grade = "C"
    elif score >= 35:
        grade = "D"
    else:
        grade = "F"

    return {
        "score": score,
        "grade": grade,
        "signals": signals,
        "concerns": concerns,
    }


def assess_freedom(tool) -> dict:
    """Score strategic flexibility — how much independence a vendor provides.

    Evaluates portability, lock-in risk, switching costs, and whether
    the tool increases organizational capability or dependency.

    Returns:
        {
            "score": int (0-100),
            "grade": str (A-F),
            "advantages": list[str],
            "risk_factors": list[str],
        }
    """
    intel = get_tool_intel(tool)
    score = 50
    advantages = []
    risk_factors = []

    # Open source = maximum strategic flexibility
    if intel.get("open_source"):
        score += 20
        advantages.append("Open source — self-hosting, forking, and migration options available")
    else:
        score -= 5
        risk_factors.append("Proprietary — operational continuity depends on vendor decisions")

    # Lock-in assessment
    lock_in = intel.get("lock_in", "medium").lower()
    if "low" in lock_in:
        score += 15
        advantages.append("Low switching cost — clean exit path available")
    elif "very high" in lock_in:
        score -= 20
        risk_factors.append("Very high lock-in — migration will require significant time and budget")
    elif "high" in lock_in:
        score -= 15
        risk_factors.append("High lock-in — material switching costs expected")
    elif "medium" in lock_in:
        score -= 5
        risk_factors.append("Moderate lock-in — switching possible but requires planning")

    # Portability
    portability = intel.get("portability", "")
    if "full" in portability.lower() or "export" in portability.lower():
        score += 10
        advantages.append("Data portability — export capabilities confirmed")
    if "not portable" in portability.lower() or "proprietary" in portability.lower():
        score -= 10
        risk_factors.append("Limited portability — data or workflow migration constrained")

    # Integrations — strategic flexibility indicator
    integrations = getattr(tool, "integrations", [])
    if len(integrations) > 5:
        advantages.append(f"Integrates with {len(integrations)}+ tools — multi-vendor stack flexibility")
        score += 5
    if len(integrations) > 10:
        risk_factors.append("Deep ecosystem integration — convenience may increase switching cost over time")
        score -= 3

    # Skill level
    if getattr(tool, "skill_level", "") == "beginner":
        advantages.append("Low onboarding friction — accessible across skill levels")
    if getattr(tool, "skill_level", "") == "advanced":
        advantages.append("Enterprise-grade capability — rewards expertise investment")
        score += 3

    # Free tier availability
    pricing = getattr(tool, "pricing", {}) or {}
    if pricing.get("free_tier"):
        advantages.append("Free tier available — low-risk evaluation possible")
        score += 5
    else:
        risk_factors.append("No free tier — budget commitment required for evaluation")
        score -= 3

    score = max(5, min(100, score))
    grade = _grade(score)

    return {
        "score": score,
        "grade": grade,
        "advantages": advantages,
        "risk_factors": risk_factors,
    }


def detect_masks(tool) -> List[str]:
    """Identify gaps between vendor positioning and observable reality.

    Flags areas where marketing claims may not fully align with
    operational practices. Useful for procurement due diligence.

    Returns a list of due diligence observations.
    """
    intel = get_tool_intel(tool)
    risk_indicators = []

    # Free but not open — revenue model question
    pricing = getattr(tool, "pricing", {}) or {}
    if pricing.get("free_tier") and not intel.get("open_source"):
        risk_indicators.append(
            "Offers a free tier but is not open source — "
            "revenue model may rely on data monetization or upsell conversion"
        )

    # "AI-powered" with high lock-in
    desc = (getattr(tool, "description", "") or "").lower()
    if "ai" in desc and intel.get("lock_in", "").lower() in ("high", "very high"):
        risk_indicators.append(
            "Positioned as 'AI-powered' with high lock-in — "
            "assess whether innovation claims justify dependency risk"
        )

    # Enterprise pricing opacity
    if pricing.get("enterprise") == "custom":
        risk_indicators.append(
            "Custom enterprise pricing — "
            "request detailed pricing schedule and contract terms before commitment"
        )

    # Compliance as differentiator
    compliance = getattr(tool, "compliance", [])
    if compliance and not intel.get("open_source"):
        risk_indicators.append(
            f"Cites {', '.join(compliance)} compliance — "
            "verify certifications are current and scope covers your use case"
        )

    # Asymmetric data relationship
    data_exposure = intel.get("data_exposure", "")
    if "everything" in data_exposure.lower() or "entire" in data_exposure.lower() or "full" in data_exposure.lower():
        risk_indicators.append(
            f"Data exposure profile: {data_exposure}. "
            "Evaluate whether vendor data access scope is proportionate to value delivered."
        )

    return risk_indicators


def track_power(tool) -> dict:
    """Map the vendor relationship dynamics for procurement intelligence.

    Provides visibility into data exchange, dependency level, and
    the strategic questions procurement teams should ask.

    Returns:
        {
            "who_benefits": str,
            "data_exposure": str,
            "vendor_value_capture": str,
            "dependency_level": str,
            "diligence_questions": list[str],
        }
    """
    intel = get_tool_intel(tool)

    # Determine dependency profile
    if intel.get("open_source"):
        dep_level = "low — open source provides exit leverage and audit capability"
    elif intel.get("lock_in", "").lower() in ("very high", "high"):
        dep_level = "elevated — dependency increases with organizational adoption"
    else:
        dep_level = "moderate — standard vendor-customer relationship"

    questions = [
        f"What is the data retention and deletion policy if the {tool.name} contract ends?",
        f"What are the estimated migration costs to move off {tool.name} after 2 years?",
        f"Does {tool.name} use customer data for model training or product development?",
    ]

    # Add domain-specific questions
    categories = [c.lower() for c in getattr(tool, "categories", [])]
    if any(c in ("writing", "research") for c in categories):
        questions.append(f"Who retains IP rights for content generated through {tool.name}?")
    if any(c in ("analytics", "data") for c in categories):
        questions.append(f"Can {tool.name} cross-reference your data with other customers' datasets?")
    if any(c in ("coding",) for c in categories):
        questions.append(f"Is proprietary code processed by {tool.name} used in model training?")

    return {
        "who_benefits": intel.get("owner", "Not confirmed"),
        "data_exposure": intel.get("data_exposure", "Work product and usage patterns"),
        "vendor_value_capture": intel.get("vendor_value_capture", "Usage data and revenue"),
        "dependency_level": dep_level,
        "diligence_questions": questions[:4],
    }


# ======================================================================
# 4. Vendor Intelligence Report
# ======================================================================

def generate_seeing(tool) -> dict:
    """Generate a comprehensive vendor intelligence report.

    Consolidates transparency analysis, strategic flexibility assessment,
    risk indicators, and dependency profiling into a single procurement-ready
    assessment.

    Returns:
        {
            "transparency": {...},
            "flexibility": {...},
            "risk_indicators": [...],
            "dependency_profile": {...},
            "executive_summary": str,
            "key_question": str,
        }
    """
    transparency = assess_transparency(tool)
    flexibility = assess_freedom(tool)
    risk_indicators = detect_masks(tool)
    dependency = track_power(tool)

    # Build executive summary
    name = tool.name
    t_grade = transparency["grade"]
    f_grade = flexibility["grade"]

    if t_grade in ("A", "B") and f_grade in ("A", "B"):
        executive_summary = (
            f"{name} demonstrates strong transparency and strategic flexibility. "
            f"Low vendor dependency risk. Standard procurement review recommended."
        )
    elif t_grade in ("A", "B"):
        executive_summary = (
            f"{name} demonstrates strong transparency practices, "
            f"but creates measurable dependency. Evaluate exit strategy before commitment."
        )
    elif f_grade in ("A", "B"):
        executive_summary = (
            f"{name} provides strong strategic flexibility and portability, "
            f"but vendor transparency could be strengthened. Request additional documentation."
        )
    elif t_grade in ("D", "F") or f_grade in ("D", "F"):
        executive_summary = (
            f"{name} presents elevated risk in transparency or vendor independence. "
            f"Enhanced due diligence recommended before procurement approval."
        )
    else:
        executive_summary = (
            f"{name} presents a standard vendor risk profile. "
            f"Review data handling and exit terms as part of standard procurement process."
        )

    # Key procurement question
    key_question = (
        f"For {name}: What is the total cost of exit — including data migration, "
        f"workflow reconstruction, and team retraining — if you need to switch after 24 months?"
    )

    return {
        "transparency": transparency,
        "flexibility": flexibility,
        "risk_indicators": risk_indicators,
        "dependency_profile": dependency,
        "executive_summary": executive_summary,
        "key_question": key_question,
    }


# ======================================================================
# 5. Utility
# ======================================================================

def _grade(score: int) -> str:
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    return "F"


def get_freedom_score(tool) -> int:
    """Quick access to just the freedom score number."""
    return assess_freedom(tool)["score"]


def get_transparency_score(tool) -> int:
    """Quick access to just the transparency score number."""
    return assess_transparency(tool)["score"]


# ======================================================================
# 6. Vendor Deep Dive Report
# ======================================================================

# Curated recent-news / change flags (manual for now; later: scraped summaries)
_VENDOR_NEWS = {
    "chatgpt": [
        {"date": "2026-01", "headline": "OpenAI launches GPT-5 with expanded enterprise tier", "impact": "positive"},
        {"date": "2025-11", "headline": "OpenAI restructures to public benefit corp", "impact": "neutral"},
    ],
    "gemini": [
        {"date": "2026-02", "headline": "Google integrates Gemini deeper into Workspace suite", "impact": "mixed",
         "note": "Deeper ecosystem lock-in but improved features"},
    ],
    "claude": [
        {"date": "2026-01", "headline": "Anthropic raises Series D at $60B valuation", "impact": "neutral"},
    ],
    "midjourney": [
        {"date": "2025-12", "headline": "Midjourney v7 released with enterprise controls", "impact": "positive"},
    ],
    "github copilot": [
        {"date": "2026-01", "headline": "GitHub Copilot adds multi-model selection (GPT-4, Claude)", "impact": "positive",
         "note": "Reduces single-vendor dependency"},
    ],
    "notion ai": [
        {"date": "2025-10", "headline": "Notion AI pricing bundled with workspace plans", "impact": "mixed"},
    ],
    "canva ai": [
        {"date": "2026-01", "headline": "Canva acquires Affinity design suite", "impact": "positive"},
    ],
}


def vendor_deep_dive(tool) -> dict:
    """Extended vendor report with news/changes, full narrative, and strategic guidance.

    Returns:
        {
            ...generate_seeing() output...,
            "recent_news": [...],
            "strategic_guidance": [...],
            "procurement_narrative": str,
            "competitive_position": str,
            "cost_of_exit": {...},
        }
    """
    # Base intelligence report
    report = generate_seeing(tool)

    name = tool.name
    name_lower = name.lower()
    intel = get_tool_intel(tool)

    # ── Recent news / changes ──
    news = _VENDOR_NEWS.get(name_lower, [])
    report["recent_news"] = news

    # ── Cost of exit analysis ──
    lock_in = intel.get("lock_in", "medium")
    portability = intel.get("portability", "Check vendor documentation")

    exit_cost = {
        "data_migration": "minimal" if lock_in == "low" else "moderate" if lock_in == "medium" else "significant",
        "workflow_reconstruction": "1-3 days" if lock_in == "low" else "1-2 weeks" if lock_in == "medium" else "2-4 weeks",
        "team_retraining": "1 day" if tool.skill_level == "beginner" else "3-5 days" if tool.skill_level == "intermediate" else "1-2 weeks",
        "portability_notes": portability,
        "estimated_total_cost": _estimate_exit_cost(tool, lock_in),
    }
    report["cost_of_exit"] = exit_cost

    # ── Strategic guidance ──
    guidance = []
    t_grade = report["transparency"]["grade"]
    f_grade = report["flexibility"]["grade"]

    if f_grade in ("D", "F"):
        guidance.append(
            f"HIGH PRIORITY: Negotiate data portability terms before signing. "
            f"{name} has elevated lock-in risk ({f_grade})."
        )
    if t_grade in ("D", "F"):
        guidance.append(
            f"Request vendor transparency report covering data handling, "
            f"training data usage, and subprocessor list."
        )
    if intel.get("open_source"):
        guidance.append(
            f"{name} is open source — mitigates lock-in risk significantly. "
            f"Consider self-hosted deployment for maximum control."
        )
    if lock_in == "low":
        guidance.append(
            f"Low switching cost — safe for pilot programs and experimentation."
        )

    # General best-practices
    guidance.append("Review vendor terms annually. Track pricing changes and feature removals.")
    guidance.append("Maintain data exports on a quarterly schedule regardless of lock-in level.")
    report["strategic_guidance"] = guidance

    # ── Competitive position ──
    pricing = getattr(tool, "pricing", {}) or {}
    categories = getattr(tool, "categories", [])
    integrations = getattr(tool, "integrations", []) or []
    popularity = getattr(tool, "popularity", 0)

    position_parts = []
    if popularity >= 8:
        position_parts.append("market leader")
    elif popularity >= 5:
        position_parts.append("established player")
    elif popularity >= 2:
        position_parts.append("growing contender")
    else:
        position_parts.append("niche/emerging")

    if len(integrations) >= 8:
        position_parts.append("strong ecosystem")
    if pricing.get("free_tier"):
        position_parts.append("accessible entry point")
    if len(categories) >= 4:
        position_parts.append("broad capability")

    report["competitive_position"] = ", ".join(position_parts).capitalize()

    # ── Full procurement narrative ──
    narrative = (
        f"Vendor Assessment: {name}\n\n"
        f"Competitive Position: {report['competitive_position']}\n"
        f"Transparency: {t_grade} ({report['transparency']['score']}/100) | "
        f"Flexibility: {f_grade} ({report['flexibility']['score']}/100)\n\n"
        f"{report['executive_summary']}\n\n"
        f"Exit Strategy: {exit_cost['estimated_total_cost']}\n"
        f"Data Migration: {exit_cost['data_migration']} effort\n"
        f"Workflow Rebuild: {exit_cost['workflow_reconstruction']}\n\n"
    )
    if news:
        narrative += "Recent Activity:\n"
        for n in news[:3]:
            narrative += f"  [{n['date']}] {n['headline']} ({n['impact']})\n"
    narrative += f"\nKey Question: {report['key_question']}"
    report["procurement_narrative"] = narrative

    return report


def _estimate_exit_cost(tool, lock_in: str) -> str:
    """Rough estimate of total exit cost for SMBs."""
    pricing = getattr(tool, "pricing", {}) or {}
    monthly = pricing.get("pro", pricing.get("starter", 0))
    if not isinstance(monthly, (int, float)):
        monthly = 30  # default estimate

    if lock_in == "low":
        return f"~${monthly * 0.5:.0f} (minimal — mainly time cost)"
    elif lock_in == "medium":
        return f"~${monthly * 2:.0f}–${monthly * 4:.0f} (migration tooling + team time)"
    elif lock_in == "high":
        return f"~${monthly * 6:.0f}–${monthly * 12:.0f} (significant data migration + workflow rebuild)"
    return f"~${monthly * 12:.0f}+ (critical dependency — plan extensively)"
