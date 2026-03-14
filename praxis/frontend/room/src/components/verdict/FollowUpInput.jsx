import { useState, useRef, useEffect } from 'react';
import { useRoomState } from '../../context/RoomContext';
import useQuerySubmit from '../../hooks/useQuerySubmit';

export default function FollowUpInput() {
  const { phase } = useRoomState();
  const { submit, isRunning } = useQuerySubmit();
  const [text, setText] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    const ta = inputRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 100) + 'px';
    }
  }, [text]);

  const handleSubmit = () => {
    if (!text.trim() || isRunning) return;
    submit(text.trim());
    setText('');
  };

  return (
    <div className="px-5 py-3 mt-auto" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
      <div className="flex items-end gap-2">
        <textarea
          ref={inputRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); } }}
          placeholder="Ask about these results... 'Why not Jasper?'"
          disabled={isRunning}
          rows={1}
          className="flex-1 resize-none bg-transparent outline-none text-xs text-white/60 placeholder-white/20 py-1.5 min-h-[28px] max-h-[100px] disabled:opacity-30"
        />
        <button
          onClick={handleSubmit}
          disabled={!text.trim() || isRunning}
          className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center transition-all disabled:opacity-20"
          style={{ background: text.trim() ? '#6366f1' : 'rgba(255,255,255,0.05)', color: 'white' }}
        >
          <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
            <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  );
}
