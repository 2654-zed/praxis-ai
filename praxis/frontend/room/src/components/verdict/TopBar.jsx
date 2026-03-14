import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRoomState, useRoomDispatch } from '../../context/RoomContext';
import useQuerySubmit from '../../hooks/useQuerySubmit';

const CONSTRAINT_KEYS = [
  { key: 'budget', label: 'Budget', placeholder: '$300/mo' },
  { key: 'team', label: 'Team', placeholder: '5' },
  { key: 'compliance', label: 'Compliance', placeholder: 'HIPAA' },
  { key: 'industry', label: 'Industry', placeholder: 'Healthcare' },
];

export default function TopBar() {
  const { query, phase, differentialResult, contextVector, cost, error } = useRoomState();
  const dispatch = useRoomDispatch();
  const { submit, isRunning, constraints, setConstraint, removeConstraint } = useQuerySubmit();
  const [text, setText] = useState('');
  const [editingChip, setEditingChip] = useState(null);
  const inputRef = useRef(null);
  const lastSubmitted = useRef('');

  useEffect(() => { if (query && !text) { setText(query); lastSubmitted.current = query; } }, [query]);

  const survivors = differentialResult?.tools_recommended || differentialResult?.survivors || [];
  const totalConsidered = differentialResult?.tools_considered || 0;
  const isComplete = phase === 'complete' || phase === 'routing';
  const isIdle = phase === 'idle';
  const isModified = text.trim() !== lastSubmitted.current;

  const handleSubmit = () => {
    if (!text.trim() || isRunning) return;
    lastSubmitted.current = text.trim();
    submit(text.trim());
  };

  const contextChips = [];
  if (contextVector) {
    Object.entries(contextVector).forEach(([key, val]) => {
      if (val?.value) contextChips.push({ key, label: key.replace('_', ' '), value: val.value });
    });
  }
  // Add active constraints as chips
  Object.entries(constraints).forEach(([key, val]) => {
    if (val && !contextChips.find(c => c.key === key)) {
      contextChips.push({ key, label: key, value: val });
    }
  });

  return (
    <div
      className="relative z-30 flex items-center gap-4 px-5 py-2.5 border-b border-white/[0.06] flex-wrap"
      style={{ background: 'rgba(10,10,15,0.85)', backdropFilter: 'blur(30px)' }}
    >
      {/* Back link */}
      <a href="/" className="text-white/30 hover:text-white/60 text-sm shrink-0 transition-colors">{'\u2190'} Praxis</a>
      <span className="text-white/10 shrink-0">|</span>

      {/* Query input — compact inline */}
      <div className="flex-1 min-w-[180px] flex items-center">
        <div
          className="flex items-center flex-1 rounded-[10px] transition-all"
          style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
        >
          <input
            ref={inputRef}
            type="text"
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleSubmit(); }}
            placeholder="New search..."
            disabled={isRunning}
            className="flex-1 bg-transparent outline-none text-white/80 placeholder-white/25 disabled:opacity-40"
            style={{ height: '36px', fontSize: '13px', padding: '8px 16px' }}
          />
          <button
            onClick={handleSubmit}
            disabled={!text.trim() || isRunning}
            className="shrink-0 mr-1 rounded-full flex items-center justify-center transition-all disabled:opacity-20"
            style={{
              width: '28px', height: '28px',
              background: text.trim() ? '#6366f1' : 'transparent',
              color: text.trim() ? 'white' : 'rgba(255,255,255,0.3)',
            }}
          >
            {isModified ? (
              <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
                <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            ) : (
              <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
                <path d="M7 2v10M4 5l3-3 3 3M4 9l3 3 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Pipeline badge */}
      {!isIdle && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`shrink-0 px-3 py-1 rounded-full text-[11px] font-medium flex items-center gap-2 ${
            isRunning
              ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
              : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
          }`}
        >
          {isRunning && (
            <motion.div
              className="w-1.5 h-1.5 rounded-full bg-current"
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
          )}
          {isRunning ? 'Analyzing...' : `${survivors.length} survived / ${totalConsidered}`}
        </motion.div>
      )}

      {/* Context chips */}
      {contextChips.slice(0, 4).map(chip => (
        <div key={chip.key} className="relative shrink-0">
          <button
            onClick={() => setEditingChip(editingChip === chip.key ? null : chip.key)}
            className="px-2 py-0.5 rounded-full text-[10px] border border-indigo-500/30 text-indigo-300/70 bg-indigo-500/8 hover:bg-indigo-500/15 transition-all"
          >
            {chip.label}: {typeof chip.value === 'string' ? chip.value.slice(0, 20) : chip.value}
          </button>
          {editingChip === chip.key && (
            <div className="absolute top-full mt-1 left-0 z-50 flex items-center gap-2 px-3 py-2 rounded-lg"
                 style={{ background: 'rgba(15,15,20,0.95)', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 8px 24px rgba(0,0,0,0.5)' }}>
              <input
                autoFocus
                type="text"
                defaultValue={constraints[chip.key] || ''}
                onBlur={e => { setConstraint(chip.key, e.target.value.trim()); setEditingChip(null); }}
                onKeyDown={e => { if (e.key === 'Enter') { setConstraint(chip.key, e.target.value.trim()); setEditingChip(null); } }}
                className="bg-transparent border-b border-white/20 focus:border-indigo-500/60 outline-none text-xs text-white/80 w-24 py-0.5"
              />
              {constraints[chip.key] && (
                <button onClick={() => { removeConstraint(chip.key); setEditingChip(null); }} className="text-red-400/60 text-xs">{'\u00d7'}</button>
              )}
            </div>
          )}
        </div>
      ))}

      {/* Add constraint */}
      {CONSTRAINT_KEYS.filter(c => !constraints[c.key]).slice(0, 2).map(c => (
        <div key={c.key} className="relative shrink-0">
          <button
            onClick={() => setEditingChip(editingChip === c.key ? null : c.key)}
            className="px-2 py-0.5 rounded-full text-[10px] border border-white/10 text-white/30 hover:text-white/60 hover:border-white/20 transition-all"
          >
            + {c.label}
          </button>
          {editingChip === c.key && (
            <div className="absolute top-full mt-1 left-0 z-50 flex items-center gap-2 px-3 py-2 rounded-lg"
                 style={{ background: 'rgba(15,15,20,0.95)', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 8px 24px rgba(0,0,0,0.5)' }}>
              <input
                autoFocus
                type="text"
                placeholder={c.placeholder}
                onBlur={e => { if (e.target.value.trim()) setConstraint(c.key, e.target.value.trim()); setEditingChip(null); }}
                onKeyDown={e => { if (e.key === 'Enter' && e.target.value.trim()) { setConstraint(c.key, e.target.value.trim()); setEditingChip(null); } }}
                className="bg-transparent border-b border-white/20 focus:border-indigo-500/60 outline-none text-xs text-white/80 w-24 py-0.5"
              />
            </div>
          )}
        </div>
      ))}

      {/* Cost */}
      {cost.total > 0 && (
        <span className="text-[11px] text-white/30 font-mono shrink-0">${cost.total.toFixed(4)}</span>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[10px] text-red-400/70 truncate max-w-[150px]">{error}</span>
          <button onClick={() => dispatch({ type: 'SET_ERROR', payload: null })} className="text-red-400/40 hover:text-red-400/80 text-xs">{'\u00d7'}</button>
        </div>
      )}

      {/* New conversation */}
      <button
        onClick={() => { dispatch({ type: 'NEW_CONVERSATION' }); setText(''); }}
        className="text-[10px] text-white/30 hover:text-white/60 px-2 py-1 rounded-md bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] transition-all shrink-0"
      >
        New
      </button>
    </div>
  );
}
