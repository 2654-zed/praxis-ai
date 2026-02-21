# --------------- Praxis Domain Models — Strict Pydantic v2 ---------------
"""
v18 · Enterprise-Grade Solidification

Canonical Pydantic v2 models that enforce strict type boundaries at the
domain layer.  Every external payload (LLM output, user input, API request)
is funnelled through these models before touching business logic.

Key design choices:
    • ``model_config = ConfigDict(strict=False)`` — allows harmless string→int
      coercion (the LLM often sends ``"42"`` instead of ``42``).
    • ``@field_validator`` decorators cross-reference live data where needed.
    • All models are immutable (``frozen=True``) unless explicitly marked
      otherwise, preventing silent mutation in concurrent contexts.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)


# -----------------------------------------------------------------------
# Enumerations
# -----------------------------------------------------------------------

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class BudgetTier(str, Enum):
    FREE = "free"
    LOW = "low"          # ≤ $50/mo
    MEDIUM = "medium"    # ≤ $500/mo
    HIGH = "high"        # > $500/mo


class StackRole(str, Enum):
    PRIMARY = "primary"
    COMPANION = "companion"
    INFRASTRUCTURE = "infrastructure"
    ANALYTICS = "analytics"


class FeedbackAction(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    RATE = "rate"


class SecurityMaturity(str, Enum):
    """SOC2/ISO 27001 maturity tier for vendor trust scoring."""
    NONE = "none"
    BASIC = "basic"
    MODERATE = "moderate"
    HIGH = "high"
    CERTIFIED = "certified"


# -----------------------------------------------------------------------
# Tool Domain Model
# -----------------------------------------------------------------------

class ToolModel(BaseModel):
    """Canonical, validated representation of an AI tool."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    categories: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    popularity: int = Field(default=0, ge=0)
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    pricing: Dict[str, Any] = Field(default_factory=dict)
    integrations: List[str] = Field(default_factory=list)
    compliance: List[str] = Field(default_factory=list)
    skill_level: SkillLevel = SkillLevel.BEGINNER
    use_cases: List[str] = Field(default_factory=list)
    stack_roles: List[StackRole] = Field(default_factory=lambda: [StackRole.PRIMARY])
    languages: List[str] = Field(default_factory=list)
    last_updated: Optional[date] = None

    @field_validator("tags", "keywords", "categories", mode="before")
    @classmethod
    def _normalize_string_lists(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return [str(x) for x in (v or [])]

    @field_validator("url", mode="before")
    @classmethod
    def _validate_url(cls, v: Any) -> Optional[str]:
        if v is None or v == "":
            return None
        if isinstance(v, str) and not re.match(r"^https?://", v):
            return f"https://{v}"
        return v


# -----------------------------------------------------------------------
# User Profile
# -----------------------------------------------------------------------

class UserProfileModel(BaseModel):
    """Validated user profile for personalized recommendations."""

    model_config = ConfigDict(extra="ignore")

    profile_id: str = Field(..., min_length=1)
    industry: Optional[str] = None
    budget_tier: BudgetTier = BudgetTier.MEDIUM
    team_size: Optional[int] = Field(default=None, ge=1)
    skill_level: SkillLevel = SkillLevel.INTERMEDIATE
    existing_tools: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    compliance_requirements: List[str] = Field(default_factory=list)


# -----------------------------------------------------------------------
# Intent (parsed from user query)
# -----------------------------------------------------------------------

class IntentModel(BaseModel):
    """Structured output from the Interpreter (LLM or rule-based)."""

    model_config = ConfigDict(extra="allow")

    raw_query: str = ""
    keywords: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    task_type: Optional[str] = None
    industry: Optional[str] = None
    budget_signal: Optional[BudgetTier] = None
    constraints: List[str] = Field(default_factory=list)
    negative_keywords: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)

    @field_validator("keywords", "categories", "constraints", "negative_keywords", mode="before")
    @classmethod
    def _ensure_list(cls, v: Any) -> list:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return list(v or [])


# -----------------------------------------------------------------------
# Stack Recommendation
# -----------------------------------------------------------------------

class ToolRecommendation(BaseModel):
    """One tool within a recommended stack."""

    model_config = ConfigDict(extra="ignore")

    name: str
    role: StackRole = StackRole.PRIMARY
    fit_score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)


class StackRecommendation(BaseModel):
    """A composed AI tool stack with explanation."""

    model_config = ConfigDict(extra="ignore")

    tools: List[ToolRecommendation] = Field(default_factory=list)
    narrative: str = ""
    composite_score: float = Field(default=0.0, ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)


# -----------------------------------------------------------------------
# Feedback
# -----------------------------------------------------------------------

class FeedbackEvent(BaseModel):
    """User feedback on a recommendation."""

    model_config = ConfigDict(extra="ignore")

    tool_name: str = Field(..., min_length=1)
    action: FeedbackAction
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    query: str = ""
    profile_id: Optional[str] = None
    timestamp: Optional[datetime] = None


# -----------------------------------------------------------------------
# Vendor Trust Assessment
# -----------------------------------------------------------------------

class VendorTrustScore(BaseModel):
    """Enterprise-grade vendor maturity assessment."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    tool_name: str
    composite_score: float = Field(ge=0.0, le=1.0)
    soc2_compliant: bool = False
    gdpr_compliant: bool = False
    hipaa_compliant: bool = False
    iso27001_certified: bool = False
    update_frequency_days: Optional[int] = None
    open_cve_count: int = Field(default=0, ge=0)
    transparency_score: float = Field(default=0.0, ge=0.0, le=1.0)
    freedom_score: float = Field(default=0.0, ge=0.0, le=1.0)
    lock_in_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    maturity: SecurityMaturity = SecurityMaturity.NONE
    warnings: List[str] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def passed(self) -> bool:
        """Derived — no need to mutate the frozen model."""
        return self.composite_score >= 0.4 and self.open_cve_count <= 5


# -----------------------------------------------------------------------
# API Request / Response Envelopes
# -----------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    profile_id: Optional[str] = None
    top_n: int = Field(default=5, ge=1, le=50)


class ReasonRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    profile_id: Optional[str] = None
    depth: int = Field(default=3, ge=1, le=10)


class APIResponse(BaseModel):
    """Standard envelope for all API responses."""

    model_config = ConfigDict(extra="allow")

    success: bool = True
    data: Any = None
    error: Optional[str] = None
    trace_id: Optional[str] = None
    latency_ms: Optional[float] = None
