import { useState, useRef, useEffect } from 'react';
import useQuerySubmit from '../../hooks/useQuerySubmit';

const PLACEHOLDERS = [
  'I need HIPAA-compliant writing tools under $50/mo',
  'Find me a no-code app builder with SOC2',
  'Compare CRM tools for a 10-person sales team',
  "What's the best coding assistant for Python?",
];

const QUICK_CHIPS = [
  { label: 'Writing', query: 'I need writing tools for...' },
  { label: 'Coding', query: 'I need coding tools for...' },
  { label: 'Marketing', query: 'I need marketing tools for...' },
  { label: 'Analytics', query: 'I need analytics tools for...' },
  { label: 'No-code', query: 'I need no-code tools for...' },
  { label: 'Security', query: 'I need security tools for...' },
];

export default function HeroSearch() {
  const { submit, isRunning } = useQuerySubmit();
  const [text, setText] = useState('');
  const [placeholderIdx, setPlaceholderIdx] = useState(0);
  const [phFading, setPhFading] = useState(false);
  const inputRef = useRef(null);

  // Cycle placeholders
  useEffect(() => {
    const timer = setInterval(() => {
      setPhFading(true);
      setTimeout(() => {
        setPlaceholderIdx(i => (i + 1) % PLACEHOLDERS.length);
        setPhFading(false);
      }, 300);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  const handleSubmit = () => {
    if (!text.trim() || isRunning) return;
    submit(text.trim());
  };

  const handleChip = (query) => {
    setText(query);
    inputRef.current?.focus();
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4">
      {/* Search input */}
      <div
        className="w-full relative"
        style={{ maxWidth: 'min(640px, 90vw)' }}
      >
        <div
          className="relative flex items-center transition-shadow duration-200"
          style={{
            background: 'rgba(255,255,255,0.04)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '16px',
            boxShadow: '0 8px 40px rgba(0,0,0,0.4)',
          }}
        >
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={text}
              onChange={e => setText(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleSubmit(); }}
              className="w-full bg-transparent outline-none text-white/90"
              style={{ height: '52px', fontSize: '16px', padding: '16px 24px', caretColor: '#6366f1' }}
            />
            {!text && (
              <div
                className="absolute top-0 left-0 right-0 flex items-center pointer-events-none transition-opacity duration-300"
                style={{ height: '52px', padding: '16px 24px', fontSize: '16px', color: 'rgba(255,255,255,0.3)', opacity: phFading ? 0 : 1 }}
              >
                {PLACEHOLDERS[placeholderIdx]}
              </div>
            )}
          </div>

          {/* Submit button */}
          <button
            onClick={handleSubmit}
            disabled={!text.trim() || isRunning}
            className="shrink-0 mr-2 flex items-center justify-center rounded-full transition-all disabled:opacity-30 disabled:cursor-not-allowed"
            style={{
              width: '40px',
              height: '40px',
              background: text.trim() ? '#6366f1' : 'rgba(255,255,255,0.06)',
              color: 'white',
              boxShadow: text.trim() ? '0 0 16px rgba(99,102,241,0.4)' : 'none',
            }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        {/* Focus glow via CSS */}
        <style>{`
          .hero-search-wrap:focus-within {
            box-shadow: 0 0 0 2px rgba(99,102,241,0.3), 0 8px 40px rgba(0,0,0,0.4) !important;
          }
        `}</style>
      </div>

      {/* Quick-start chips */}
      <div className="flex flex-wrap justify-center gap-2 mt-4">
        {QUICK_CHIPS.map(chip => (
          <button
            key={chip.label}
            onClick={() => handleChip(chip.query)}
            className="px-4 py-1.5 rounded-full text-[13px] border border-white/10 text-white/50 cursor-pointer transition-all duration-150 hover:border-indigo-500/50 hover:text-indigo-400"
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* Subtitle */}
      <p className="text-xs text-white/20 mt-6 text-center max-w-[360px]">
        Praxis will evaluate 254 tools, eliminate the unfit, and explain why.
      </p>
    </div>
  );
}
