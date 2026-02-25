"""Core API route registration extracted from api.create_app()."""
# pyright: reportInvalidTypeForm=false


def register_core_routes(app, deps):
    get_all_categories = deps["get_all_categories"]
    TOOLS = deps["TOOLS"]
    ToolDetail = deps["ToolDetail"]
    SearchRequest = deps["SearchRequest"]
    _deep_reason = deps["_deep_reason"]
    _deep_reason_v2 = deps["_deep_reason_v2"]
    interpret = deps["interpret"]
    load_profile = deps["load_profile"]
    find_tools = deps["find_tools"]
    explain_tool = deps["explain_tool"]
    get_suggestions = deps["get_suggestions"]
    generate_seeing = deps["generate_seeing"]
    StackResponse = deps["StackResponse"]
    StackRequest = deps["StackRequest"]
    compose_stack = deps["compose_stack"]
    StackToolEntry = deps["StackToolEntry"]
    CompareRequest = deps["CompareRequest"]
    compare_tools = deps["compare_tools"]
    ProfileRequest = deps["ProfileRequest"]
    UserProfile = deps["UserProfile"]
    save_profile = deps["save_profile"]
    list_profiles = deps["list_profiles"]
    FeedbackRequest = deps["FeedbackRequest"]
    run_learning_cycle = deps["run_learning_cycle"]
    compute_tool_quality = deps["compute_tool_quality"]
    export_tools_json = deps["export_tools_json"]
    import_tools_json = deps["import_tools_json"]
    import_tools_csv = deps["import_tools_csv"]
    generate_csv_template = deps["generate_csv_template"]
    _cfg = deps["_cfg"]
    _get_current_user = deps.get("get_current_user")

    # Build a Depends-based admin guard if FastAPI auth is available.
    # Routes decorated with admin_required will return 401/403 when
    # PRAXIS_AUTH_MODE is not "none" and credentials are absent/invalid.
    _admin_guard = None
    if _get_current_user:
        try:
            from fastapi import Depends, HTTPException

            async def _require_admin(user=Depends(_get_current_user)):
                if not user.has_role("admin"):
                    raise HTTPException(status_code=403, detail="Admin role required")
                return user

            _admin_guard = [Depends(_require_admin)]
        except Exception:
            pass

    @app.get("/categories")
    def categories():
        return get_all_categories()

    @app.get("/tools")
    def list_tools(skip: int = 0, limit: int = 50):
        """Return paginated tool list.  Use ``?skip=0&limit=50`` to page."""
        page = TOOLS[skip : skip + limit]
        out = []
        for t in page:
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
        return {"total": len(TOOLS), "skip": skip, "limit": limit, "items": out}

    @app.post("/search")
    def search(req: SearchRequest):
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

    @app.get("/suggest")
    def suggest(q: str = ""):
        """Smart autocomplete — returns a Bento Grid payload with
        intent detection, semantic completions, and tool matches."""
        try:
            from .smart_suggest import smart_suggest
        except ImportError:
            from smart_suggest import smart_suggest
        if q and len(q.strip()) >= 2:
            return smart_suggest(q, TOOLS, limit=8)
        # Show-on-focus: return pre-populated suggestions for empty query
        try:
            from .smart_suggest import focus_suggestions
        except ImportError:
            from smart_suggest import focus_suggestions
        return focus_suggestions(TOOLS)

    @app.post("/suggest/click")
    def suggest_click(body: dict):
        """Record a click on an autocomplete suggestion for popularity tracking."""
        text = body.get("text", "").strip()
        if not text:
            return {"status": "ignored"}
        try:
            from .smart_suggest import record_suggestion_click
        except ImportError:
            from smart_suggest import record_suggestion_click
        record_suggestion_click(text)
        return {"status": "recorded", "text": text}

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

    @app.get("/seeing/{tool_name}")
    def seeing(tool_name: str):
        return intelligence(tool_name)

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

    @app.post("/compare")
    def compare(req: CompareRequest):
        profile = load_profile(req.profile_id) if req.profile_id else None
        return compare_tools(req.tool_a, req.tool_b, profile)

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

    @app.post("/learn", dependencies=_admin_guard or [])
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

    @app.get("/tools/export")
    def tools_export():
        """Export all tools as downloadable JSON."""
        if export_tools_json:
            import json as _json
            return _json.loads(export_tools_json())
        return {"error": "Export module not available"}

    @app.post("/tools/import/json", dependencies=_admin_guard or [])
    async def tools_import_json(payload: dict):
        """Import tools from JSON.  Body: {"tools": [...]} or raw array."""
        if not import_tools_json:
            return {"error": "Import module not available"}
        import json as _json
        items = payload.get("tools", payload) if isinstance(payload, dict) else payload
        return import_tools_json(_json.dumps(items))

    @app.post("/tools/import/csv", dependencies=_admin_guard or [])
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

    @app.get("/config/weights")
    def config_weights():
        """Return current scoring weights for transparency / tuning."""
        weight_keys = [k for k in (_cfg.DEFAULTS if _cfg else {}) if k.startswith("weight_")]
        return {k: _cfg.get(k) for k in weight_keys} if _cfg else {}

    # ══════════════════════════════════════════════════════════════════
    # PHASE 1 — Anti-Wrapper Shield, Tuesday Test, RFP Generator
    # ══════════════════════════════════════════════════════════════════

    def _import_verification():
        try:
            from .verification import score_tool, score_all_tools, tier_distribution, tuesday_test, generate_rfp
        except ImportError:
            from verification import score_tool, score_all_tools, tier_distribution, tuesday_test, generate_rfp
        return score_tool, score_all_tools, tier_distribution, tuesday_test, generate_rfp

    @app.get("/tools/resilience")
    def tools_resilience():
        """Score every tool with the Anti-Wrapper Verification Shield.
        Returns resilience scores sorted highest-first."""
        score_tool, score_all_tools, *_ = _import_verification()
        reports = score_all_tools(TOOLS)
        return {
            "total": len(reports),
            "tools": [r.to_dict() for r in reports],
        }

    @app.get("/tools/resilience/{tool_name}")
    def tool_resilience(tool_name: str):
        """Resilience report for a single tool."""
        score_tool_fn = _import_verification()[0]
        tool = next((t for t in TOOLS if t.name.lower() == tool_name.lower()), None)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        return score_tool_fn(tool).to_dict()

    @app.get("/tools/resilience-summary")
    def tools_resilience_summary():
        """Tier distribution across all tools."""
        *_, tier_dist_fn, _, _ = _import_verification()
        return tier_dist_fn(TOOLS)

    @app.post("/tuesday-test")
    def tuesday_test_endpoint(body: dict):
        """Run the 'Tuesday Test' ROI simulation.

        Body:
            region, role, task_description, hours_per_week_manual,
            error_rate_manual, tool_category, tool_cost_override
        """
        *_, tuesday_fn, _ = _import_verification()
        result = tuesday_fn(
            region=body.get("region", "midwest"),
            role=body.get("role", "admin"),
            task_description=body.get("task_description", "manual data entry"),
            hours_per_week_manual=float(body.get("hours_per_week_manual", 8)),
            error_rate_manual=float(body.get("error_rate_manual", 0.05)),
            tool_category=body.get("tool_category", "automation"),
            tool_cost_override=body.get("tool_cost_override"),
        )
        return result.to_dict()

    @app.post("/rfp/generate")
    def rfp_generate(body: dict):
        """Generate a neutral vendor RFP document.

        Body:
            business_name, industry, team_size, workflow_description,
            tools_to_evaluate (or selected_tools), monthly_budget, pain_points,
            budget_tier, compliance_requirements, constraints
        """
        *_, rfp_fn = _import_verification()
        # Accept either key name from frontend
        tools = body.get("tools_to_evaluate") or body.get("selected_tools", [])
        # Derive budget tier from monthly_budget if provided
        budget = body.get("monthly_budget")
        budget_tier = body.get("budget_tier", "medium")
        if budget is not None:
            budget = float(budget)
            if budget <= 0: budget_tier = "free"
            elif budget <= 100: budget_tier = "low"
            elif budget <= 500: budget_tier = "medium"
            else: budget_tier = "high"
        rfp = rfp_fn(
            business_name=body.get("business_name", "My Business"),
            industry=body.get("industry", "general"),
            team_size=body.get("team_size", "small"),
            workflow_description=body.get("workflow_description", ""),
            selected_tools=tools,
            budget_tier=budget_tier,
            compliance_requirements=body.get("compliance_requirements"),
            constraints=body.get("constraints"),
            tools_list=TOOLS,
        )
        return rfp

    # ══════════════════════════════════════════════════════════════════
    # PHASE 2 — Tiered Directory, Category Pages, Comparison
    # ══════════════════════════════════════════════════════════════════

    @app.get("/tools/tiered")
    def tools_tiered():
        """Return tools grouped by resilience tier with full tool data.
        Used by the Curated Swimlane view and Homepage Sovereign Showcase."""
        score_tool_fn, score_all_fn, *_ = _import_verification()
        reports = score_all_fn(TOOLS)
        by_name = {t.name: t for t in TOOLS}
        tiers = {"sovereign": [], "durable": [], "moderate": [], "fragile": [], "wrapper": []}
        for r in reports:
            t = by_name.get(r.tool_name)
            if not t:
                continue
            entry = {
                "name": t.name,
                "description": t.description,
                "url": t.url,
                "categories": t.categories[:5],
                "tags": t.tags[:5],
                "pricing": t.pricing,
                "integrations": t.integrations[:6],
                "compliance": t.compliance,
                "skill_level": t.skill_level,
                "use_cases": t.use_cases[:4],
                "resilience_score": r.score,
                "grade": r.grade,
                "tier": r.tier,
                "dimensions": r.dimensions,
                "flags": r.flags[:3],
                "summary": r.summary,
            }
            if r.tier in tiers:
                tiers[r.tier].append(entry)
        return {
            "tiers": tiers,
            "counts": {k: len(v) for k, v in tiers.items()},
            "total": len(TOOLS),
        }

    @app.get("/tools/category/{category}")
    def tools_by_category(category: str):
        """Return tools filtered by category, enriched with resilience data."""
        score_tool_fn = _import_verification()[0]
        matches = [t for t in TOOLS if category.lower() in [c.lower() for c in t.categories]]
        results = []
        for t in matches:
            r = score_tool_fn(t)
            results.append({
                "name": t.name,
                "description": t.description,
                "url": t.url,
                "categories": t.categories[:5],
                "tags": t.tags[:5],
                "pricing": t.pricing,
                "integrations": t.integrations[:6],
                "compliance": t.compliance,
                "skill_level": t.skill_level,
                "use_cases": t.use_cases[:4],
                "resilience_score": r.score,
                "grade": r.grade,
                "tier": r.tier,
                "flags": r.flags[:3],
            })
        results.sort(key=lambda x: x["resilience_score"], reverse=True)
        return {
            "category": category,
            "total": len(results),
            "tools": results,
        }

    @app.post("/tools/compare")
    def tools_compare(body: dict):
        """Side-by-side comparison of up to 4 tools with full resilience data."""
        score_tool_fn = _import_verification()[0]
        names = body.get("tools", [])[:4]
        by_name = {t.name.lower(): t for t in TOOLS}
        comparisons = []
        for name in names:
            t = by_name.get(name.lower())
            if not t:
                continue
            r = score_tool_fn(t)
            comparisons.append({
                "name": t.name,
                "description": t.description,
                "url": t.url,
                "categories": t.categories,
                "pricing": t.pricing,
                "integrations": t.integrations,
                "compliance": t.compliance,
                "skill_level": t.skill_level,
                "use_cases": t.use_cases[:6],
                "resilience_score": r.score,
                "grade": r.grade,
                "tier": r.tier,
                "dimensions": r.dimensions,
                "flags": r.flags,
                "summary": r.summary,
            })
        return {"tools": comparisons}

    # ==================================================================
    # Differential Diagnosis Engine Routes
    # ==================================================================

    def _import_differential():
        """Lazy import to avoid circular dependency."""
        try:
            from . import differential
            return differential
        except ImportError:
            import differential
            return differential

    def _import_explain_diff():
        try:
            from .explain import explain_elimination, explain_survival, assemble_presentation
            return explain_elimination, explain_survival, assemble_presentation
        except ImportError:
            from explain import explain_elimination, explain_survival, assemble_presentation
            return explain_elimination, explain_survival, assemble_presentation

    def _import_profile_matrix():
        try:
            from .profile import build_constraint_matrix
            return build_constraint_matrix
        except ImportError:
            from profile import build_constraint_matrix
            return build_constraint_matrix

    def _import_learning_overrides():
        try:
            from .learning import compute_override_rate, get_elimination_efficacy
            return compute_override_rate, get_elimination_efficacy
        except ImportError:
            from learning import compute_override_rate, get_elimination_efficacy
            return compute_override_rate, get_elimination_efficacy

    def _import_interpreter_structured():
        try:
            from .interpreter import extract_structured_intents
            return extract_structured_intents
        except ImportError:
            from interpreter import extract_structured_intents
            return extract_structured_intents

    @app.post("/differential")
    def differential_diagnosis(body: dict):
        """
        Execute the full differential diagnosis pipeline.

        Body:
            {
                "query": str (required),
                "profile_id": str (optional — loads saved profile),
                "profile": { ... } (optional — inline profile override),
                "top_n": int (optional, default 5)
            }

        Returns the complete DifferentialResult with survivors,
        eliminated tools, funnel narrative, and stage metadata.
        """
        diff = _import_differential()
        query = body.get("query", "").strip()
        if not query:
            return {"error": "Query is required", "detail": "Provide a 'query' field."}

        top_n = body.get("top_n", 5)

        # Load or construct profile
        profile = None
        profile_id = body.get("profile_id")
        if profile_id:
            profile = load_profile(profile_id)

        inline = body.get("profile")
        if inline and not profile:
            profile = UserProfile(
                profile_id=inline.get("profile_id", "inline"),
                industry=inline.get("industry", ""),
                budget=inline.get("budget", "medium"),
                team_size=inline.get("team_size", "solo"),
                skill_level=inline.get("skill_level", "beginner"),
                existing_tools=inline.get("existing_tools", []),
                goals=inline.get("goals", []),
                constraints=inline.get("constraints", []),
                preferences=inline.get("preferences", {}),
            )

        result = diff.generate_differential(query, profile=profile, top_n=top_n)

        # Enrich with explain layer
        explain_elim, explain_surv, assemble = _import_explain_diff()
        presentation = assemble(result.survivors, result.eliminated)

        return {
            "query": result.query,
            "profile_id": result.profile_id,
            "clarification_needed": result.clarification_needed,
            "clarification": result.clarification,
            "funnel_narrative": result.funnel_narrative,
            "stages": result.stages,
            "survivors": result.survivors,
            "eliminated": result.eliminated,
            "presentation": {
                "summary": presentation["summary"],
                "survivor_cards": presentation["survivor_cards"],
                "elimination_cards": presentation["elimination_cards"],
                "notable_eliminations": presentation["notable_eliminations"],
                "total_survivors": presentation["total_survivors"],
                "total_eliminated": presentation["total_eliminated"],
            },
        }

    @app.post("/differential/intent")
    def differential_intent(body: dict):
        """
        Parse a query through the structured intent extractor.
        Useful for previewing how the pipeline will interpret a query
        before running the full diagnosis.

        Body: { "query": str }
        """
        extract = _import_interpreter_structured()
        query = body.get("query", "").strip()
        if not query:
            return {"error": "Query is required"}
        return extract(query)

    @app.post("/differential/constraint-matrix")
    def differential_constraint_matrix(body: dict):
        """
        Generate a Constraint Matrix from a profile.
        Shows the executable elimination rules derived from user context.

        Body: { "profile_id": str } or { "profile": { inline profile } }
        """
        build_matrix = _import_profile_matrix()

        profile = None
        profile_id = body.get("profile_id")
        if profile_id:
            profile = load_profile(profile_id)

        inline = body.get("profile")
        if inline and not profile:
            profile = UserProfile(
                profile_id=inline.get("profile_id", "inline"),
                industry=inline.get("industry", ""),
                budget=inline.get("budget", "medium"),
                team_size=inline.get("team_size", "solo"),
                skill_level=inline.get("skill_level", "beginner"),
                existing_tools=inline.get("existing_tools", []),
                goals=inline.get("goals", []),
                constraints=inline.get("constraints", []),
                preferences=inline.get("preferences", {}),
            )

        if not profile:
            return {"error": "No profile found", "detail": "Provide profile_id or inline profile."}

        return build_matrix(profile)

    @app.post("/differential/challenge")
    def differential_challenge(body: dict):
        """
        Challenge an elimination result.
        Records an override and returns acknowledgement.

        Body: {
            "query": str,
            "tool_name": str,
            "reason_code": str,
            "profile_id": str (optional),
            "comment": str (optional)
        }
        """
        diff = _import_differential()
        query = body.get("query", "")
        tool_name = body.get("tool_name", "")
        reason_code = body.get("reason_code", "UNKNOWN")
        profile_id = body.get("profile_id")

        if not tool_name:
            return {"error": "tool_name is required"}

        entry = diff.record_override(
            query=query,
            eliminated_tool=tool_name,
            reason_code=reason_code,
            profile_id=profile_id,
        )

        return {
            "status": "recorded",
            "message": (
                f"Your challenge of {tool_name}'s elimination has been recorded. "
                f"This feedback helps calibrate our filters."
            ),
            "entry": entry,
        }

    @app.get("/differential/override-stats")
    def differential_override_stats():
        """
        Return override statistics for monitoring filter accuracy.
        High override rates signal aggressive filters that need recalibration.
        """
        compute_rate, _ = _import_learning_overrides()
        return compute_rate()

    @app.get("/differential/filter-health")
    def differential_filter_health():
        """
        Cross-reference override data with tool quality metrics.
        Determines whether eliminations are vindicated or questionable.
        """
        _, get_efficacy = _import_learning_overrides()
        return get_efficacy()

    # ==================================================================
    # 2026 Security Blueprint: Sovereignty, Nutrition, Outcomes, Prompts
    # ==================================================================

    def _import_sovereignty():
        from praxis.sovereignty import (
            assess_sovereignty, get_trust_badge, filter_by_sovereignty,
            assess_all_tools, get_sovereignty_intel,
        )
        return assess_sovereignty, get_trust_badge, filter_by_sovereignty, assess_all_tools, get_sovereignty_intel

    def _import_nutrition():
        from praxis.nutrition import generate_nutrition_label, generate_all_labels, praxis_self_label
        return generate_nutrition_label, generate_all_labels, praxis_self_label

    def _import_outcomes():
        from praxis.outcomes import (
            detect_outcome_intent, assemble_outcome_results,
            get_outcome_pills, get_outcome_detail,
        )
        return detect_outcome_intent, assemble_outcome_results, get_outcome_pills, get_outcome_detail

    def _import_prompt_assist():
        from praxis.prompt_assist import (
            generate_optimized_prompt, bridge_prompt, decompose_intent,
            get_available_workflows, get_available_models,
        )
        return generate_optimized_prompt, bridge_prompt, decompose_intent, get_available_workflows, get_available_models

    # ── Sovereignty Routes ──

    @app.get("/sovereignty/assess/{tool_name}")
    def sovereignty_assess(tool_name: str):
        """Assess sovereignty risk for a specific tool."""
        assess, badge, *_ = _import_sovereignty()
        tool = next((t for t in TOOLS if t.name.lower() == tool_name.lower()), None)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        return {
            "tool": tool_name,
            "assessment": assess(tool),
            "badge": badge(tool),
        }

    @app.get("/sovereignty/dashboard")
    def sovereignty_dashboard_data():
        """
        Return sovereignty assessment for all tools.
        Powers the Sovereignty Dashboard UI.
        """
        *_, assess_all, _ = _import_sovereignty()
        data = assess_all(TOOLS)
        return data

    @app.get("/sovereignty/intel/{tool_name}")
    def sovereignty_intel(tool_name: str):
        """Get raw sovereignty intelligence for a tool."""
        *_, get_intel = _import_sovereignty()
        intel = get_intel(tool_name)
        if not intel:
            return {"error": f"No sovereignty intel for '{tool_name}'", "tool": tool_name}
        return {"tool": tool_name, "intel": intel}

    # ── Nutrition Label Routes ──

    @app.get("/nutrition/{tool_name}")
    def nutrition_label(tool_name: str):
        """Generate AI Nutrition Label for a specific tool."""
        gen_label, _, _ = _import_nutrition()
        assess, *_ = _import_sovereignty()
        tool = next((t for t in TOOLS if t.name.lower() == tool_name.lower()), None)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        sov_data = assess(tool)
        return gen_label(tool, sov_data)

    @app.get("/nutrition/all")
    def nutrition_all():
        """Generate AI Nutrition Labels for all tools (batch)."""
        _, gen_all, _ = _import_nutrition()
        *_, assess_all, _ = _import_sovereignty()
        sov_data = assess_all(TOOLS)
        assessments = {
            item["tool_name"]: item["assessment"]
            for item in sov_data.get("tools", [])
        }
        return gen_all(TOOLS, assessments)

    @app.get("/nutrition/self-label")
    def nutrition_self():
        """Show Praxis platform's own AI Nutrition Label."""
        _, _, self_label = _import_nutrition()
        return self_label()

    # ── Outcome Routes ──

    @app.post("/outcomes/recommend")
    def outcomes_recommend(body: dict):
        """
        Outcome-oriented recommendation.

        Body: {
            "query": str,
            "force_outcome": str | null,  // time_saved, cost_reduction, revenue_growth, compliance
            "profile_id": str | null,
        }
        """
        _, assemble, _, _ = _import_outcomes()
        query = body.get("query", "")
        force = body.get("force_outcome")
        profile = None
        pid = body.get("profile_id")
        if pid:
            profile = load_profile(pid)

        tools = find_tools(query, top_n=20, profile=profile)
        result = assemble(tools, query, profile=profile, force_outcome=force)
        # Serialize tool objects in ranked_results
        for entry in result.get("ranked_results", []):
            t = entry.pop("tool", None)
            if t:
                entry["tool_name"] = t.name
                entry["tool_description"] = t.description
        return result

    @app.get("/outcomes/pills")
    def outcomes_pills():
        """Return outcome navigation pills for the UI."""
        _, _, get_pills, _ = _import_outcomes()
        return {"pills": get_pills()}

    @app.get("/outcomes/{outcome_id}")
    def outcomes_detail(outcome_id: str):
        """Get details for a specific outcome pillar."""
        _, _, _, get_detail = _import_outcomes()
        detail = get_detail(outcome_id)
        if not detail:
            return {"error": f"Unknown outcome pillar '{outcome_id}'"}
        return detail

    # ── Prompt Assistance Routes ──

    @app.post("/prompt-assist/generate")
    def prompt_generate(body: dict):
        """
        Generate an optimized prompt for a tool/model.

        Body: {
            "query": str,
            "tool_name": str | null,
            "target_model": str | null,
            "workflow_id": str | null,
            "step_answers": { step_id: chosen_option } | null,
        }
        """
        gen_prompt, _, _, _, _ = _import_prompt_assist()
        return gen_prompt(
            query=body.get("query", ""),
            tool_name=body.get("tool_name"),
            target_model=body.get("target_model"),
            workflow_id=body.get("workflow_id"),
            step_answers=body.get("step_answers"),
        )

    @app.post("/prompt-assist/bridge")
    def prompt_bridge(body: dict):
        """
        Transfer a prompt between model dialects.

        Body: {
            "source_prompt": str,
            "source_model": str,
            "target_model": str,
        }
        """
        _, bridge, _, _, _ = _import_prompt_assist()
        return bridge(
            source_prompt=body.get("source_prompt", ""),
            source_model=body.get("source_model", "gpt-4"),
            target_model=body.get("target_model", "claude"),
        )

    @app.post("/prompt-assist/decompose")
    def prompt_decompose(body: dict):
        """
        Decompose a query into DMN decision steps.

        Body: {
            "query": str,
            "workflow_id": str | null,
        }
        """
        _, _, decompose, _, _ = _import_prompt_assist()
        return decompose(
            query=body.get("query", ""),
            workflow_id=body.get("workflow_id"),
        )

    @app.get("/prompt-assist/workflows")
    def prompt_workflows():
        """List available DMN workflow templates."""
        _, _, _, get_wf, _ = _import_prompt_assist()
        return {"workflows": get_wf()}

    @app.get("/prompt-assist/models")
    def prompt_models():
        """List available model dialects for PromptBridge."""
        _, _, _, _, get_models = _import_prompt_assist()
        return {"models": get_models()}
