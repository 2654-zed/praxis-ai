import { useState, useRef, useEffect } from 'react';
import { useRoomState } from '../../context/RoomContext';
import useQuerySubmit from '../../hooks/useQuerySubmit';

/* ── SVG Icons ── */
const IconFind = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <circle cx="7" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M10.5 10.5L13 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const IconCompare = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <rect x="2" y="3" width="5" height="10" rx="1" stroke="currentColor" strokeWidth="1.5"/>
    <rect x="9" y="3" width="5" height="10" rx="1" stroke="currentColor" strokeWidth="1.5"/>
  </svg>
);
const IconAnalyze = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <rect x="2" y="9" width="3" height="5" rx="0.5" stroke="currentColor" strokeWidth="1.5"/>
    <rect x="6.5" y="5" width="3" height="9" rx="0.5" stroke="currentColor" strokeWidth="1.5"/>
    <rect x="11" y="2" width="3" height="12" rx="0.5" stroke="currentColor" strokeWidth="1.5"/>
  </svg>
);

const MODES = [
  { id: 'find', icon: IconFind, label: 'Find', placeholder: 'Find the right AI tool...' },
  { id: 'compare', icon: IconCompare, label: 'Compare', placeholder: 'Compare vendors side-by-side...' },
  { id: 'analyze', icon: IconAnalyze, label: 'Analyze', placeholder: 'Analyze your current stack...' },
];

const CONSTRAINT_KEYS = [
  { key: 'budget', label: 'Budget', placeholder: '$300/mo' },
  { key: 'compliance', label: 'Compliance', placeholder: 'HIPAA' },
  { key: 'industry', label: 'Industry', placeholder: 'Healthcare' },
  { key: 'skill_level', label: 'Skill level', placeholder: 'beginner' },
  { key: 'team', label: 'Team size', placeholder: '10' },
  { key: 'existing_tools', label: 'Existing tools', placeholder: 'Slack, Notion' },
];

const EXPLORE_CATEGORIES = [
  { label: 'Writing', count: 34, query: 'I need writing tools for...', icon: 'M4 4h8v1H4zM4 7h6v1H4zM4 10h8v1H4z' },
  { label: 'Coding', count: 28, query: 'I need coding tools for...', icon: 'M5 4l-3 4 3 4M11 4l3 4-3 4M8 3l-1 10' },
  { label: 'Automation', count: 22, query: 'I need automation tools for...', icon: 'M2 8h4l2-4 2 8 2-4h4' },
  { label: 'Analytics', count: 19, query: 'I need analytics tools for...', icon: 'M3 12V6M7 12V4M11 12V8M15 12V2' },
];

const FUNNEL_STAGES = [
  { label: 'Catalog', color: 'rgba(255,255,255,0.15)', baseCount: 253 },
  { label: 'Category', color: '#6366f1', baseRatio: 0.35 },
  { label: 'Budget', color: '#50e3c2', baseRatio: 0.6 },
  { label: 'Compliance', color: '#f5a623', baseRatio: 0.7 },
  { label: 'Survivors', color: '#10b981', baseRatio: 0.5 },
];

function estimateFunnel(queryLen, chipCount) {
  const base = 253;
  const catMatch = Math.max(8, Math.round(base * (0.15 + Math.min(queryLen, 30) * 0.008)));
  const budgetMatch = Math.round(catMatch * (0.5 + chipCount * 0.05));
  const compMatch = Math.round(budgetMatch * (0.6 + chipCount * 0.04));
  const survivors = Math.max(3, Math.round(compMatch * 0.45));
  return [base, catMatch, budgetMatch, compMatch, survivors];
}

export default function CommandBar({ compact = false, onNavigateRoom }) {
  const state = useRoomState();
  const { submit, isRunning, constraints, setConstraint, removeConstraint } = useQuerySubmit();
  const [text, setText] = useState('');
  const [mode, setMode] = useState('find');
  const [editingChip, setEditingChip] = useState(null);
  const [phIdx, setPhIdx] = useState(0);
  const [phFading, setPhFading] = useState(false);
  const inputRef = useRef(null);

  const activeMode = MODES.find(m => m.id === mode) || MODES[0];
  const isTyping = text.length >= 3;
  const activeConstraints = Object.entries(constraints).filter(([, v]) => v);
  const chipCount = activeConstraints.length;
  const funnelCounts = estimateFunnel(text.length, chipCount);

  // Cycle placeholder
  useEffect(() => {
    if (compact) return;
    const timer = setInterval(() => {
      setPhFading(true);
      setTimeout(() => { setPhIdx(i => (i + 1) % MODES[0].placeholder.length); setPhFading(false); }, 300);
    }, 4000);
    return () => clearInterval(timer);
  }, [compact]);

  // Sync query from state
  useEffect(() => {
    if (state?.query && !text) setText(state.query);
  }, [state?.query]);

  const handleSubmit = () => {
    if (!text.trim() || isRunning) return;
    if (onNavigateRoom) {
      const params = new URLSearchParams({ q: text.trim(), mode });
      activeConstraints.forEach(([k, v]) => params.append(k, v));
      window.location.href = `/room?${params.toString()}`;
      return;
    }
    submit(text.trim());
  };

  const fillInput = (query) => {
    setText(query);
    inputRef.current?.focus();
  };

  /* ── Layer 1: Input Bar ── */
  const inputBar = (
    <div
      className="flex items-center"
      style={{
        background: compact ? 'rgba(255,255,255,0.04)' : 'rgba(15,15,20,0.88)',
        backdropFilter: compact ? 'none' : 'blur(24px)',
        WebkitBackdropFilter: compact ? 'none' : 'blur(24px)',
        border: '0.5px solid rgba(255,255,255,0.08)',
        borderRadius: compact ? '10px' : '16px',
        padding: compact ? '4px' : '6px',
        boxShadow: compact ? 'none' : '0 8px 40px rgba(0,0,0,0.4)',
      }}
    >
      {/* Mode toggles */}
      <div className="flex items-center shrink-0" style={{ borderRight: '0.5px solid rgba(255,255,255,0.08)', paddingRight: compact ? '4px' : '6px', marginRight: compact ? '4px' : '6px' }}>
        {MODES.map(m => (
          <button
            key={m.id}
            onClick={() => setMode(m.id)}
            title={m.label}
            className="flex items-center justify-center transition-all"
            style={{
              width: compact ? '28px' : '32px',
              height: compact ? '28px' : '32px',
              borderRadius: '8px',
              background: mode === m.id ? '#6366f1' : 'transparent',
              color: mode === m.id ? 'white' : 'rgba(255,255,255,0.4)',
            }}
          >
            <m.icon />
          </button>
        ))}
      </div>

      {/* Text input */}
      <div className="flex-1 relative min-w-0">
        <input
          ref={inputRef}
          type="text"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSubmit(); }}
          placeholder={compact ? 'New search...' : activeMode.placeholder}
          disabled={isRunning}
          className="w-full bg-transparent outline-none text-white/90 placeholder-white/25 disabled:opacity-40"
          style={{
            height: compact ? '32px' : '42px',
            fontSize: compact ? '13px' : '15px',
            padding: compact ? '6px 8px' : '6px 8px',
            caretColor: '#6366f1',
          }}
        />
      </div>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={!text.trim() || isRunning}
        className="shrink-0 flex items-center justify-center rounded-full transition-all disabled:opacity-30 disabled:cursor-not-allowed hover:scale-105 active:scale-95"
        style={{
          width: compact ? '28px' : '36px',
          height: compact ? '28px' : '36px',
          background: text.trim() ? '#6366f1' : 'rgba(255,255,255,0.06)',
          color: 'white',
          boxShadow: text.trim() && !compact ? '0 0 16px rgba(99,102,241,0.4)' : 'none',
        }}
      >
        <svg width={compact ? 12 : 14} height={compact ? 12 : 14} viewBox="0 0 14 14" fill="none">
          <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  );

  if (compact) return inputBar;

  /* ── Layer 2: Parameter Chips ── */
  const chipRow = (
    <div className="flex flex-wrap gap-1.5 mt-2.5">
      {/* Active constraints */}
      {activeConstraints.map(([key, val]) => (
        <span
          key={key}
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[12px] border border-indigo-500/30 text-indigo-300/80"
          style={{ background: 'rgba(99,102,241,0.06)' }}
        >
          {val}
          <button onClick={() => removeConstraint(key)} className="text-white/30 hover:text-white/70 ml-0.5">{'\u00d7'}</button>
        </span>
      ))}
      {/* Available constraints */}
      {CONSTRAINT_KEYS.filter(c => !constraints[c.key]).map(c => (
        <div key={c.key} className="relative">
          <button
            onClick={() => setEditingChip(editingChip === c.key ? null : c.key)}
            className="px-3 py-1 rounded-full text-[12px] border border-white/10 text-white/35 hover:border-indigo-500/40 hover:text-white/60 transition-all"
          >
            + {c.label}
          </button>
          {editingChip === c.key && (
            <div className="absolute top-full mt-2 left-0 z-50 flex items-center gap-2 px-3 py-2 rounded-xl"
                 style={{ background: 'rgba(15,15,20,0.95)', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 8px 24px rgba(0,0,0,0.5)' }}>
              <input
                autoFocus
                type="text"
                placeholder={c.placeholder}
                onBlur={e => { if (e.target.value.trim()) setConstraint(c.key, e.target.value.trim()); setEditingChip(null); }}
                onKeyDown={e => { if (e.key === 'Enter' && e.target.value.trim()) { setConstraint(c.key, e.target.value.trim()); setEditingChip(null); } if (e.key === 'Escape') setEditingChip(null); }}
                className="bg-transparent border-b border-white/20 focus:border-indigo-500/60 outline-none text-xs text-white/80 w-28 py-0.5"
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );

  /* ── Layer 3A: Idle Context (explore grid + cta) ── */
  const idleContext = (
    <div className="mt-5">
      {/* Explore grid */}
      <div className="mb-4">
        <span className="text-[11px] font-medium text-white/20 uppercase tracking-wider">Explore</span>
        <div className="grid grid-cols-4 gap-2 mt-2 max-[600px]:grid-cols-2">
          {EXPLORE_CATEGORIES.map(cat => (
            <button
              key={cat.label}
              onClick={() => fillInput(cat.query)}
              className="flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:border-indigo-500/30 hover:bg-indigo-500/[0.04] transition-all"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="text-white/30">
                <path d={cat.icon} stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span className="text-[12px] font-semibold text-white/60">{cat.label}</span>
              <span className="text-[11px] text-white/20">{cat.count}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Journey CTA */}
      {onNavigateRoom && (
        <a
          href="/static/journey.html"
          className="inline-flex items-center gap-2 text-[13px] text-white/25 hover:text-white/50 transition-colors"
        >
          Not sure what you need? Take the guided quiz {'\u2192'}
        </a>
      )}

      {/* Subtitle */}
      <p className="text-[12px] text-white/15 mt-4">
        Vannus will evaluate 254 tools, eliminate the unfit, and explain why.
      </p>
    </div>
  );

  /* ── Layer 3B: Typing Context (live funnel) ── */
  const typingContext = (
    <div className="mt-5">
      <span className="text-[11px] font-medium text-white/20 uppercase tracking-wider">Live elimination preview</span>
      <div className="mt-2 space-y-1.5">
        {FUNNEL_STAGES.map((stage, i) => {
          const count = funnelCounts[i];
          const widthPct = (count / 253) * 100;
          return (
            <div key={stage.label} className="flex items-center gap-2">
              <span className="text-[11px] text-white/30 w-[72px] text-right shrink-0">{stage.label}</span>
              <div className="flex-1 h-3 rounded-full bg-white/[0.04] overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${widthPct}%`, background: stage.color }}
                />
              </div>
              <span className="text-[11px] text-white/25 w-8 shrink-0">~{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4">
      <div className="w-full" style={{ maxWidth: 'min(640px, 90vw)' }}>
        {inputBar}
        {chipRow}
        {isTyping ? typingContext : idleContext}
      </div>
    </div>
  );
}
