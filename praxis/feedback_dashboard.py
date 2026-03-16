# ────────────────────────────────────────────────────────────────────
# feedback_dashboard.py — Server-rendered HTML admin dashboard
# ────────────────────────────────────────────────────────────────────
"""Renders feedback stats and recent submissions as a styled HTML page.
Internal tool — not linked from the public site."""

import json
from html import escape
from datetime import datetime, timezone
from typing import Any, Dict


def _relative_time(ts_str: str) -> str:
    """Convert a UTC timestamp string to a relative time like '2 min ago'."""
    if not ts_str:
        return ""
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - ts
        secs = int(delta.total_seconds())
        if secs < 60:
            return f"{secs}s ago"
        if secs < 3600:
            return f"{secs // 60} min ago"
        if secs < 86400:
            return f"{secs // 3600}h ago"
        return f"{secs // 86400}d ago"
    except Exception:
        return ts_str[:16] if ts_str else ""


def _parse_survivors(s: str) -> str:
    """Parse a JSON survivor list and return truncated comma-separated names."""
    if not s:
        return ""
    try:
        items = json.loads(s)
        if not isinstance(items, list):
            return escape(str(s)[:80])
        if len(items) <= 3:
            return escape(", ".join(str(x) for x in items))
        return escape(", ".join(str(x) for x in items[:3])) + f" + {len(items) - 3} more"
    except Exception:
        return escape(str(s)[:80])


def _trunc(s: str, n: int = 80) -> str:
    """Escape and truncate a string."""
    if not s:
        return ""
    t = escape(str(s))
    return t[:n] + "..." if len(t) > n else t


def render_dashboard(data: Dict[str, Any]) -> str:
    """Return a complete HTML page string for the feedback dashboard."""
    stats = data["stats"]
    td_rate_pct = int(stats["thumbs_down_rate"] * 100)

    # ── Search feedback rows ──
    search_rows = []
    for r in data.get("recent_searches", []):
        rating = r.get("rating") or ""
        icon = '<span class="rating-up">&#128077;</span>' if rating == "up" else '<span class="rating-down">&#128078;</span>' if rating == "down" else '<span style="color:rgba(255,255,255,0.2)">-</span>'
        query = _trunc(r.get("query_text", ""), 100)
        comment = ""
        if r.get("comment"):
            comment = f'<div class="comment">{_trunc(r["comment"], 200)}</div>'
        survivors = ""
        if r.get("survivors"):
            survivors = f'<div class="survivors">Survivors: {_parse_survivors(r["survivors"])}</div>'
        session = escape(str(r.get("session_id", ""))[:8])
        ts = _relative_time(r.get("timestamp", ""))
        search_rows.append(
            f'<div class="feedback-row">'
            f'<div class="feedback-time">{ts}</div>'
            f'<div class="feedback-content">{icon} "{query}"{comment}{survivors}'
            f'<div class="session">{session}</div></div></div>'
        )
    search_html = "\n".join(search_rows) if search_rows else '<div style="color:rgba(255,255,255,0.2);font-size:13px;padding:12px 0">No search feedback yet</div>'

    # ── Flag detail breakdown ──
    flag_detail_rows = []
    for r in data.get("flag_details", []):
        tool = escape(str(r.get("tool_name", "")))
        ftype = escape(str(r.get("flag_type", "") or ""))
        reason = _trunc(r.get("reason") or "", 120)
        count = r.get("count", 0)
        bar_w = min(count * 30, 100)
        reason_html = f' <span class="flag-reason">&mdash; "{reason}"</span>' if reason else ""
        flag_detail_rows.append(
            f'<div class="flag-row">'
            f'<span class="flag-tool">{_trunc(tool, 40)}</span> '
            f'<div class="bar" style="width:120px;display:inline-block;vertical-align:middle;margin:0 8px">'
            f'<div class="bar-fill" style="width:{bar_w}%"></div></div>'
            f'<strong>{count}</strong> '
            f'<span class="flag-type">{ftype}</span>{reason_html}</div>'
        )
    flag_details_html = "\n".join(flag_detail_rows) if flag_detail_rows else '<div style="color:rgba(255,255,255,0.2);font-size:13px;padding:12px 0">No tool flags yet</div>'

    # ── Recent flags ──
    recent_flag_rows = []
    for r in data.get("recent_flags", []):
        ts = _relative_time(r.get("timestamp", ""))
        tool = _trunc(r.get("tool_name", ""), 40)
        current = escape(str(r.get("current_tier", "")))
        suggested = escape(str(r.get("suggested_tier", "") or ""))
        tier_change = f"{current} &rarr; {suggested}" if suggested else current
        ftype = escape(str(r.get("flag_type", "") or ""))
        reason = _trunc(r.get("reason") or "", 120)
        reason_html = f'<div class="flag-reason">"{reason}"</div>' if reason else ""
        recent_flag_rows.append(
            f'<div class="feedback-row">'
            f'<div class="feedback-time">{ts}</div>'
            f'<div class="feedback-content"><span class="flag-tool">{tool}</span> '
            f'<span style="color:rgba(255,255,255,0.3)">{tier_change}</span> '
            f'<span class="flag-type">{ftype}</span>{reason_html}</div></div>'
        )
    recent_flags_html = "\n".join(recent_flag_rows) if recent_flag_rows else '<div style="color:rgba(255,255,255,0.2);font-size:13px;padding:12px 0">No tool flags yet</div>'

    # ── Event counts ──
    event_chips = []
    for r in data.get("event_counts", []):
        etype = escape(str(r.get("event_type", "")))
        count = r.get("count", 0)
        event_chips.append(f'<span class="event-chip">{etype} <span class="event-count">{count}</span></span>')
    events_html = "\n".join(event_chips) if event_chips else '<div style="color:rgba(255,255,255,0.2);font-size:13px;padding:12px 0">No events yet</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Praxis Feedback Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0f;
            color: #f0f0f5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
            padding: 32px;
            max-width: 960px;
            margin: 0 auto;
        }}
        h1 {{ font-size: 20px; font-weight: 700; margin-bottom: 4px; }}
        .subtitle {{ font-size: 12px; color: rgba(255,255,255,0.3); margin-bottom: 24px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }}
        .stat-value {{ font-size: 28px; font-weight: 700; color: #6366f1; }}
        .stat-label {{ font-size: 11px; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }}
        .section {{ margin-bottom: 28px; }}
        .section-title {{
            font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;
            color: rgba(255,255,255,0.25); margin-bottom: 12px;
            padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06);
        }}
        .feedback-row {{
            display: flex; gap: 12px; padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.04);
            font-size: 13px;
        }}
        .feedback-time {{ color: rgba(255,255,255,0.2); font-size: 11px; min-width: 80px; flex-shrink: 0; }}
        .feedback-content {{ flex: 1; }}
        .rating-up {{ color: #34d399; }}
        .rating-down {{ color: #ef4444; }}
        .comment {{ color: rgba(255,255,255,0.4); font-style: italic; font-size: 12px; margin-top: 2px; }}
        .survivors {{ color: rgba(255,255,255,0.25); font-size: 11px; margin-top: 2px; }}
        .session {{ color: rgba(255,255,255,0.15); font-size: 10px; font-family: monospace; }}
        .bar {{ height: 8px; border-radius: 4px; background: rgba(255,255,255,0.06); margin: 8px 0; }}
        .bar-fill {{ height: 100%; border-radius: 4px; background: #6366f1; }}
        .bar-fill-red {{ background: #ef4444; }}
        .flag-row {{ padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 13px; }}
        .flag-tool {{ color: #f0f0f5; font-weight: 600; }}
        .flag-type {{ color: rgba(255,255,255,0.4); font-size: 11px; }}
        .flag-reason {{ color: rgba(255,255,255,0.3); font-size: 12px; font-style: italic; }}
        .event-chip {{
            display: inline-block; background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08); border-radius: 999px;
            padding: 4px 12px; font-size: 12px; color: rgba(255,255,255,0.5); margin: 4px;
        }}
        .event-count {{ color: #6366f1; font-weight: 600; }}
        a.refresh {{ color: #6366f1; text-decoration: none; font-size: 12px; float: right; }}
        a.refresh:hover {{ text-decoration: underline; }}
        @media (max-width: 640px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            body {{ padding: 16px; }}
        }}
    </style>
</head>
<body>
    <a class="refresh" href="/feedback/dashboard">&#8635; Refresh</a>
    <h1>Praxis Feedback Dashboard</h1>
    <div class="subtitle">Internal &middot; {escape(str(stats.get('feedback_since') or 'N/A'))} to now &middot; Not linked from public site</div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{stats['total_search_feedback']}</div>
            <div class="stat-label">Search Feedback</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['thumbs_up']}<span style="color:rgba(255,255,255,0.2)">/</span>{stats['thumbs_down']}</div>
            <div class="stat-label">&#128077; / &#128078;</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['total_tool_flags']}</div>
            <div class="stat-label">Tool Flags</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['total_events']}</div>
            <div class="stat-label">Events</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Negative Rate</div>
        <div class="bar"><div class="bar-fill bar-fill-red" style="width:{td_rate_pct}%"></div></div>
        <div style="font-size:12px;color:rgba(255,255,255,0.3)">{td_rate_pct}% of rated searches got thumbs down</div>
    </div>

    <div class="section">
        <div class="section-title">Recent Search Feedback</div>
        {search_html}
    </div>

    <div class="section">
        <div class="section-title">Most Flagged Tools</div>
        {flag_details_html}
    </div>

    <div class="section">
        <div class="section-title">Recent Tool Flags</div>
        {recent_flags_html}
    </div>

    <div class="section">
        <div class="section-title">Events</div>
        {events_html}
    </div>
</body>
</html>"""
