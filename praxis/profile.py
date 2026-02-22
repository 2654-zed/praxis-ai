# --------------- User Profile Management ---------------
"""
Captures and persists user context so the decision engine can make
profile-aware recommendations.

A profile contains:
    industry        – e.g. "startup", "e-commerce", "healthcare"
    budget          – spending tier: "free" | "low" | "medium" | "high"
    team_size       – "solo" | "small" (2-10) | "medium" (11-50) | "large" (50+)
    skill_level     – "beginner" | "intermediate" | "advanced"
    existing_tools  – list of tool names the user already uses
    goals           – list of high-level goals: "growth", "automation", "cost reduction"
    constraints     – list of hard requirements: "HIPAA", "GDPR", "SOC2", "self-hosted"
    preferences     – free-form dict for future extensibility
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

PROFILES_FILE = "profiles.json"


# ------------------------------------------------------------------
# Data class
# ------------------------------------------------------------------

class UserProfile:
    """Structured representation of a user's context."""

    VALID_BUDGETS = {"free", "low", "medium", "high"}
    VALID_SKILLS = {"beginner", "intermediate", "advanced"}
    VALID_TEAM_SIZES = {"solo", "small", "medium", "large"}

    def __init__(
        self,
        profile_id: str = "default",
        industry: str = "",
        budget: str = "medium",
        team_size: str = "solo",
        skill_level: str = "beginner",
        existing_tools: Optional[List[str]] = None,
        goals: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        preferences: Optional[Dict] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.profile_id = profile_id
        self.industry = industry
        self.budget = budget if budget in self.VALID_BUDGETS else "medium"
        self.team_size = team_size if team_size in self.VALID_TEAM_SIZES else "solo"
        self.skill_level = skill_level if skill_level in self.VALID_SKILLS else "beginner"
        self.existing_tools = existing_tools or []
        self.goals = goals or []
        self.constraints = constraints or []
        self.preferences = preferences or {}
        self.created_at = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.updated_at = updated_at or self.created_at

    # ---- serialization ----

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "industry": self.industry,
            "budget": self.budget,
            "team_size": self.team_size,
            "skill_level": self.skill_level,
            "existing_tools": self.existing_tools,
            "goals": self.goals,
            "constraints": self.constraints,
            "preferences": self.preferences,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "UserProfile":
        return cls(
            profile_id=d.get("profile_id", "default"),
            industry=d.get("industry", ""),
            budget=d.get("budget", "medium"),
            team_size=d.get("team_size", "solo"),
            skill_level=d.get("skill_level", "beginner"),
            existing_tools=d.get("existing_tools"),
            goals=d.get("goals"),
            constraints=d.get("constraints"),
            preferences=d.get("preferences"),
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
        )

    def update(self, **kwargs):
        """Merge new values into the profile and bump updated_at."""
        for key, val in kwargs.items():
            if hasattr(self, key) and val is not None:
                setattr(self, key, val)
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # ---- convenience queries ----

    def requires_compliance(self, standard: str) -> bool:
        return standard.upper() in [c.upper() for c in self.constraints]

    def already_uses(self, tool_name: str) -> bool:
        return tool_name.lower() in [t.lower() for t in self.existing_tools]

    def __repr__(self):
        return (
            f"UserProfile(id={self.profile_id!r}, industry={self.industry!r}, "
            f"budget={self.budget!r}, skill={self.skill_level!r}, "
            f"team={self.team_size!r}, tools={self.existing_tools})"
        )


# ------------------------------------------------------------------
# Persistence helpers
# ------------------------------------------------------------------

def _profiles_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), PROFILES_FILE)


def _load_all() -> dict:
    p = _profiles_path()
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_all(data: dict):
    with open(_profiles_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_profile(profile: UserProfile):
    """Persist a profile (upsert by profile_id)."""
    data = _load_all()
    profile.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    data[profile.profile_id] = profile.to_dict()
    _save_all(data)
    return profile


def load_profile(profile_id: str = "default") -> Optional[UserProfile]:
    """Load a profile by ID. Returns None if not found."""
    data = _load_all()
    entry = data.get(profile_id)
    if entry:
        return UserProfile.from_dict(entry)
    return None


def list_profiles() -> List[str]:
    """Return all stored profile IDs."""
    return list(_load_all().keys())


def delete_profile(profile_id: str) -> bool:
    data = _load_all()
    if profile_id in data:
        del data[profile_id]
        _save_all(data)
        return True
    return False


# ------------------------------------------------------------------
# CLI helper — interactive profile builder
# ------------------------------------------------------------------

def build_profile_interactive(profile_id: str = "default") -> UserProfile:
    """Walk the user through creating / updating a profile via CLI prompts."""
    existing = load_profile(profile_id)
    if existing:
        print(f"\nExisting profile found: {existing}")
        update = input("Update this profile? (y/n): ").strip().lower()
        if not update.startswith("y"):
            return existing

    print("\n--- Build Your Profile ---")

    industry = input("Industry (e.g. startup, e-commerce, healthcare, agency, saas): ").strip().lower() or "general"

    budget_input = input("Monthly AI-tool budget — free / low ($0-50) / medium ($50-500) / high ($500+): ").strip().lower()
    budget = budget_input if budget_input in UserProfile.VALID_BUDGETS else "medium"

    team_input = input("Team size — solo / small (2-10) / medium (11-50) / large (50+): ").strip().lower()
    team_size = team_input if team_input in UserProfile.VALID_TEAM_SIZES else "solo"

    skill_input = input("Technical skill level — beginner / intermediate / advanced: ").strip().lower()
    skill_level = skill_input if skill_input in UserProfile.VALID_SKILLS else "beginner"

    existing_tools_raw = input("Tools you already use (comma-separated, or blank): ").strip()
    existing_tools = [t.strip() for t in existing_tools_raw.split(",") if t.strip()] if existing_tools_raw else []

    goals_raw = input("Goals — e.g. growth, automation, cost reduction (comma-separated): ").strip()
    goals = [g.strip() for g in goals_raw.split(",") if g.strip()] if goals_raw else []

    constraints_raw = input("Hard requirements — e.g. HIPAA, GDPR, SOC2, self-hosted (comma-separated, or blank): ").strip()
    constraints = [c.strip().upper() for c in constraints_raw.split(",") if c.strip()] if constraints_raw else []

    profile = UserProfile(
        profile_id=profile_id,
        industry=industry,
        budget=budget,
        team_size=team_size,
        skill_level=skill_level,
        existing_tools=existing_tools,
        goals=goals,
        constraints=constraints,
    )
    save_profile(profile)
    print(f"\nProfile saved: {profile}")
    return profile
