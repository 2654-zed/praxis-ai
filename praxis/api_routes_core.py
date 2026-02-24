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
