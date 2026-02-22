# ------- Holds the Tool class -------

class Tool:
    """Represents an AI tool in the Praxis knowledge base.

    Core fields (original):
        name, description, categories, url, popularity, tags, keywords

    Decision-engine fields (Phase 1):
        pricing         – dict with tier info  {"free_tier": True, "starter": 12, "pro": 49, "enterprise": "custom"}
        integrations    – list of other tool names this connects with
        compliance      – list of standards/certifications  ["SOC2", "GDPR"]
        skill_level     – minimum user skill: "beginner" | "intermediate" | "advanced"
        use_cases       – concrete use-case strings  ["blog writing", "email campaigns"]
        stack_roles     – roles this tool can fill: "primary" | "companion" | "infrastructure" | "analytics"
        languages       – supported languages / platforms  ["python", "javascript", "no-code"]
    """

    def __init__(
        self,
        name,
        description,
        categories,
        url=None,
        popularity: int = 0,
        tags=None,
        keywords=None,
        # --- Phase 1 additions ---
        pricing=None,
        integrations=None,
        compliance=None,
        skill_level=None,
        use_cases=None,
        stack_roles=None,
        languages=None,
        # --- Phase 2 additions ---
        last_updated=None,
    ):
        # Core
        self.name = name
        self.description = description
        self.categories = categories or []
        self.url = url
        self.popularity = int(popularity or 0)
        self.tags = tags or []
        self.keywords = keywords or []

        # Decision-engine extensions
        self.pricing = pricing or {}
        self.integrations = integrations or []
        self.compliance = compliance or []
        self.skill_level = skill_level or "beginner"
        self.use_cases = use_cases or []
        self.stack_roles = stack_roles or ["primary"]
        self.languages = languages or []

        # Freshness tracking — ISO date string "2026-02-20" or None
        self.last_updated = last_updated

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def matches(self, intent_keywords):
        """Return a basic score based on keyword overlap with categories/tags/keywords."""
        score = 0
        for word in intent_keywords:
            w = word.lower()
            if any(w == c.lower() for c in self.categories):
                score += 2
            if any(w == t.lower() for t in self.tags):
                score += 2
            if any(w == k.lower() for k in self.keywords):
                score += 1
            if w in self.name.lower() or w in self.description.lower():
                score += 1
        return score

    def fits_budget(self, budget_tier: str) -> bool:
        """Check whether this tool is accessible at the given budget tier.

        Budget tiers: "free", "low" (≤$50), "medium" (≤$500), "high" (>$500)
        """
        if not self.pricing:
            return True  # unknown pricing → don't exclude
        if budget_tier == "high":
            return True
        if budget_tier == "free":
            return bool(self.pricing.get("free_tier"))
        if budget_tier == "low":
            starter = self.pricing.get("starter") or self.pricing.get("pro") or 0
            try:
                return bool(self.pricing.get("free_tier")) or (float(starter) <= 50)
            except (TypeError, ValueError):
                return True
        if budget_tier == "medium":
            pro = self.pricing.get("pro") or self.pricing.get("starter") or 0
            try:
                return bool(self.pricing.get("free_tier")) or (float(pro) <= 500)
            except (TypeError, ValueError):
                return True
        return True

    def fits_skill(self, user_skill: str) -> bool:
        """Check whether the tool is appropriate for the user's skill level."""
        levels = {"beginner": 0, "intermediate": 1, "advanced": 2}
        tool_level = levels.get(self.skill_level, 0)
        user_level = levels.get(user_skill, 0)
        return user_level >= tool_level

    def integrates_with(self, other_name: str) -> bool:
        """Return True if this tool lists *other_name* in its integrations."""
        return other_name.lower() in [i.lower() for i in self.integrations]

    def to_dict(self) -> dict:
        """Serialize to a plain dict (for JSON / API responses)."""
        return {
            "name": self.name,
            "description": self.description,
            "categories": self.categories,
            "url": self.url,
            "popularity": self.popularity,
            "tags": self.tags,
            "keywords": self.keywords,
            "pricing": self.pricing,
            "integrations": self.integrations,
            "compliance": self.compliance,
            "skill_level": self.skill_level,
            "use_cases": self.use_cases,
            "stack_roles": self.stack_roles,
            "languages": self.languages,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Tool":
        """Reconstruct a Tool from a dict."""
        return cls(
            name=d.get("name", ""),
            description=d.get("description", ""),
            categories=d.get("categories", []),
            url=d.get("url"),
            popularity=d.get("popularity", 0),
            tags=d.get("tags", []),
            keywords=d.get("keywords", []),
            pricing=d.get("pricing"),
            integrations=d.get("integrations"),
            compliance=d.get("compliance"),
            skill_level=d.get("skill_level"),
            use_cases=d.get("use_cases"),
            stack_roles=d.get("stack_roles"),
            languages=d.get("languages"),
            last_updated=d.get("last_updated"),
        )

    def is_stale(self, max_days: int = 90) -> bool:
        """Return True if this tool's metadata hasn't been updated within max_days."""
        if not self.last_updated:
            return True  # no date recorded → assume stale
        try:
            from datetime import datetime, date
            updated = date.fromisoformat(self.last_updated)
            return (date.today() - updated).days > max_days
        except Exception:
            return True

    def __repr__(self):
        return f"{self.name}: {self.description}"

