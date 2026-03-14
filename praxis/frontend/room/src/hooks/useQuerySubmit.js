import { useState, useRef, useCallback } from 'react';
import { useRoomState, useRoomDispatch } from '../context/RoomContext';

/* ── SSE stream parser ── */
function handleSSEEvent(dispatch, event) {
  const { type, ...data } = event;
  dispatch({ type: 'APPEND_EVENT', payload: event });

  const eventMap = {
    session_start: 'SSE_SESSION_START',
    context_extracted: 'SSE_CONTEXT_EXTRACTED',
    routing_decision: 'SSE_ROUTING_DECISION',
    model_start: 'SSE_MODEL_START',
    token_chunk: 'SSE_TOKEN_CHUNK',
    model_complete: 'SSE_MODEL_COMPLETE',
    collaboration_result: 'SSE_COLLABORATION_RESULT',
    artifact_saved: 'SSE_ARTIFACT_SAVED',
    spend_recorded: 'SSE_SPEND_RECORDED',
    journey_update: 'SSE_JOURNEY_UPDATE',
    session_end: 'SSE_SESSION_END',
    error: 'SSE_ERROR',
  };

  if (type === 'spend_recorded' && data.amount_usd != null && data.cost_usd == null) {
    data.cost_usd = data.amount_usd;
  }

  const action = eventMap[type];
  if (action) dispatch({ type: action, payload: data });
}

function synthesizeContext(query, data) {
  const survivors = data.tools_recommended || [];
  const cats = survivors.flatMap(t => t.categories || []);
  const comp = survivors.flatMap(t => t.compliance || []);
  const budgetMatch = /\$[\d,]+(?:\s*\/\s*mo(?:nth)?)?/i.exec(query)
    || /under\s+\$[\d,]+/i.exec(query)
    || /\bfree\b/i.exec(query);
  const skillHint = /\bno.?code\b|\blow.?code\b|\bdeveloper\b|\bengineering\b/i.exec(query);
  const taskValue = (data.plan || []).find(p =>
    typeof p === 'string' && p.length < 80 && !/^Step\s*\d/i.test(p) && !/sub-quer/i.test(p)
  ) || 'general';

  return {
    task_type: { value: taskValue, confidence: 0.7, reasoning: 'Inferred from query' },
    industry: { value: cats[0] || null, confidence: cats.length ? 0.5 : 0.2, reasoning: cats.length ? 'From tool categories' : 'Not specified' },
    budget: { value: budgetMatch ? budgetMatch[0] : null, confidence: budgetMatch ? 0.8 : 0.1, reasoning: budgetMatch ? 'Extracted from query' : 'Not specified' },
    compliance: { value: comp.length ? comp.slice(0, 3).join(', ') : null, confidence: comp.length ? 0.7 : 0.1, reasoning: comp.length ? 'From tool compliance data' : 'Not specified' },
    skill_level: { value: skillHint ? skillHint[0] : null, confidence: skillHint ? 0.6 : 0.2, reasoning: skillHint ? 'Keyword detected' : 'Not specified' },
  };
}

function buildFallbackArtifact(query, data) {
  const survivors = data.tools_recommended || [];
  const lines = [];
  if (data.narrative) lines.push(data.narrative);
  if (survivors.length) {
    lines.push('');
    lines.push(`### Recommended Stack (${survivors.length} tools)`);
    survivors.forEach((t, i) => {
      const score = t.fit_score != null ? ` \u2014 ${Math.round(t.fit_score <= 1 ? t.fit_score * 100 : t.fit_score)}% fit` : '';
      lines.push(`${i + 1}. **${t.name}**${score}`);
      if (t.description) lines.push(`   ${t.description.slice(0, 120)}`);
    });
  }
  if (data.caveats?.length) {
    lines.push('');
    lines.push('### Caveats');
    data.caveats.forEach(c => lines.push(`- ${c}`));
  }
  return {
    id: `fallback_${Date.now()}`,
    model_id: data.mode || 'praxis',
    artifact_type: 'recommendation',
    title: `Stack Recommendation: "${query}"`,
    content: lines.join('\n'),
    created_at: new Date().toISOString(),
  };
}

function buildQueryWithHistory(text, history) {
  const recentTurns = history.slice(-2);
  const historyHint = recentTurns.length
    ? `Context from this session: ${recentTurns.map(t => `"${t.query}" returned ${t.survivors.join(', ')}`).join('. ')}. `
    : '';
  return historyHint + text;
}

export default function useQuerySubmit() {
  const state = useRoomState();
  const dispatch = useRoomDispatch();
  const { phase, room, query: stateQuery, conversationHistory, differentialResult } = state;
  const [constraints, setConstraints] = useState({ budget: '', team: '', compliance: '', industry: '' });
  const submittingRef = useRef(false);

  const isRunning = phase === 'eliminating' || phase === 'executing';

  const setConstraint = useCallback((key, value) => {
    setConstraints(prev => ({ ...prev, [key]: value }));
  }, []);

  const removeConstraint = useCallback((key) => {
    setConstraints(prev => ({ ...prev, [key]: '' }));
  }, []);

  async function autoExecute(query, cognitiveData) {
    if (!room?.id) return;
    dispatch({ type: 'START_EXECUTION' });

    let gotArtifact = false;
    try {
      const res = await fetch(`/room/${room.id}/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, profile_id: 'default' }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              if (event.type === 'artifact_saved') gotArtifact = true;
              handleSSEEvent(dispatch, event);
            } catch {}
          }
        }
      }
      if (buffer.startsWith('data: ')) {
        try {
          const event = JSON.parse(buffer.slice(6));
          if (event.type === 'artifact_saved') gotArtifact = true;
          handleSSEEvent(dispatch, event);
        } catch {}
      }
    } catch (err) {
      console.warn('Stream error:', err.message);
    }

    if (!gotArtifact && cognitiveData.narrative) {
      const fallback = buildFallbackArtifact(query, cognitiveData);
      dispatch({ type: 'SSE_ARTIFACT_SAVED', payload: fallback });
    }

    dispatch({ type: 'EXECUTION_COMPLETE' });
  }

  const submit = useCallback(async (userText) => {
    if (!userText.trim() || isRunning || submittingRef.current) return;
    submittingRef.current = true;

    let q = userText.trim();
    if (constraints.budget) q += `, budget: ${constraints.budget}`;
    if (constraints.team) q += `, team size: ${constraints.team}`;
    if (constraints.compliance) q += `, compliance: ${constraints.compliance}`;
    if (constraints.industry) q += `, industry: ${constraints.industry}`;

    const query = buildQueryWithHistory(q, conversationHistory);
    dispatch({ type: 'SET_QUERY', payload: userText.trim() });

    if (differentialResult) {
      const prevSurvivors = differentialResult.tools_recommended || differentialResult.survivors || [];
      dispatch({
        type: 'ARCHIVE_QUERY',
        payload: {
          query: stateQuery,
          toolsConsidered: differentialResult.tools_considered || prevSurvivors.length,
          matchCount: prevSurvivors.length,
          survivors: prevSurvivors.slice(0, 5).map(s => s.name || 'unknown'),
        },
      });
    }

    dispatch({ type: 'START_ELIMINATION' });

    const controller = new AbortController();
    const hardTimeout = setTimeout(() => controller.abort(), 60000);

    try {
      const res = await fetch('/cognitive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, profile_id: 'default', include_trace: true }),
        signal: controller.signal,
      });
      clearTimeout(hardTimeout);

      let data;
      const contentType = res.headers.get('content-type') || '';
      if (!res.ok || !contentType.includes('application/json')) {
        const body = await res.text();
        data = {
          error: res.status === 404
            ? 'Cognitive pipeline not found. Is the server running on port 8000?'
            : `Server returned ${res.status}: ${body.slice(0, 100)}`,
          query,
          tools_recommended: [],
          eliminated: [],
          narrative: '',
        };
      } else {
        data = await res.json();
      }

      const survivors = data.tools_recommended || data.survivors || [];
      data.query = data.query || query;
      dispatch({ type: 'SET_DIFFERENTIAL_RESULT', payload: data });

      const ctx = data.context_vector || synthesizeContext(userText, data);
      dispatch({ type: 'SET_CONTEXT_VECTOR', payload: ctx });

      if (!data.error && survivors.length > 0) {
        await autoExecute(query, data);
      } else if (data.narrative) {
        const fallback = buildFallbackArtifact(query, data);
        dispatch({ type: 'SSE_ARTIFACT_SAVED', payload: fallback });
        dispatch({ type: 'EXECUTION_COMPLETE' });
      } else {
        dispatch({ type: 'EXECUTION_COMPLETE' });
      }

      dispatch({
        type: 'APPEND_CONVERSATION_TURN',
        payload: {
          query: userText.trim(),
          survivors: survivors.slice(0, 5).map(s => s.name || s.tool || 'unknown'),
          timestamp: Date.now(),
        },
      });
    } catch (err) {
      clearTimeout(hardTimeout);
      const msg = err.name === 'AbortError'
        ? 'Request timed out after 60s. Try a simpler query.'
        : `Routing error: ${err.message}`;
      dispatch({ type: 'SET_ERROR', payload: msg });
    } finally {
      submittingRef.current = false;
    }
  }, [isRunning, constraints, conversationHistory, differentialResult, stateQuery, room, dispatch]);

  return { submit, isRunning, constraints, setConstraint, removeConstraint };
}
