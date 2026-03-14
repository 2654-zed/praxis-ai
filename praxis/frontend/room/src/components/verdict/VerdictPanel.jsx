import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { useRoomState } from '../../context/RoomContext';
import PipelineProgress from './PipelineProgress';
import FollowUpInput from './FollowUpInput';
import ReasonCodeBadge from '../elimination/ReasonCodeBadge';

function EliminationBadges({ eliminated }) {
  const [open, setOpen] = useState(false);

  if (!eliminated || eliminated.length === 0) return null;

  // Aggregate by reason code
  const counts = {};
  eliminated.forEach(e => {
    const code = e.code || e.reason_type || 'UNKNOWN';
    counts[code] = (counts[code] || 0) + 1;
  });

  return (
    <div className="mt-6">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 text-xs text-white/30 hover:text-white/50 transition-colors"
      >
        <span className="transition-transform duration-200" style={{ transform: open ? 'rotate(90deg)' : 'rotate(0deg)' }}>{'\u25B8'}</span>
        <span>{eliminated.length} eliminated</span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="flex flex-wrap gap-2 mt-3">
              {Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([code, count]) => (
                <div key={code} className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                  <span className="text-xs font-mono text-white/40">{count}</span>
                  <ReasonCodeBadge code={code} />
                </div>
              ))}
            </div>
            <div className="mt-3 space-y-1">
              {eliminated.slice(0, 10).map((e, i) => (
                <div key={i} className="flex items-center gap-2 text-[11px] text-white/25">
                  <span className="w-1 h-1 rounded-full bg-red-500/40 shrink-0" />
                  <span className="truncate">{e.name}</span>
                  <span className="text-white/15 truncate flex-1">{e.explanation}</span>
                </div>
              ))}
              {eliminated.length > 10 && (
                <div className="text-[10px] text-white/15 pl-3">+{eliminated.length - 10} more</div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ArchivedQuery({ entry }) {
  return (
    <div className="mb-3 px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04]">
      <div className="flex items-center gap-2">
        <span className="text-emerald-400/40 text-xs">{'\u2713'}</span>
        <span className="text-[11px] text-white/30 truncate">
          {entry.matchCount} matched / {entry.toolsConsidered}
        </span>
      </div>
    </div>
  );
}

export default function VerdictPanel() {
  const { differentialResult, phase, queryHistory } = useRoomState();

  const survivors = differentialResult?.tools_recommended || differentialResult?.survivors || [];
  const eliminated = differentialResult?.eliminated || [];
  const narrative = differentialResult?.funnel_narrative || differentialResult?.narrative || '';
  const elapsedMs = differentialResult?.total_elapsed_ms || 0;
  const caveats = differentialResult?.caveats || [];
  const isRunning = phase === 'eliminating' || phase === 'executing';
  const hasResult = !!differentialResult;

  // Clean narrative text
  const cleanedNarrative = typeof narrative === 'string'
    ? narrative
        .split(/(?<=[.!?])\s+/)
        .filter(s => !/I wasn't able to fully address/i.test(s))
        .filter(s => !/Sub-query not well covered/i.test(s))
        .join(' ')
        .trim()
    : Array.isArray(narrative)
      ? narrative.join(' ')
      : '';

  return (
    <div className="w-[340px] shrink-0 flex flex-col overflow-hidden border-r border-white/[0.06] max-[900px]:w-full max-[900px]:max-h-[200px] max-[900px]:border-r-0 max-[900px]:border-b max-[900px]:border-white/[0.06]">
      <div className="flex-1 overflow-y-auto px-5 py-5">
        {/* Archived queries */}
        {queryHistory.length > 0 && queryHistory.map((entry, i) => (
          <ArchivedQuery key={i} entry={entry} />
        ))}

        {/* Section header */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-[10px] font-bold text-indigo-400/60 uppercase tracking-[2px]">Praxis Verdict</span>
        </div>

        {/* Pipeline progress (inline) */}
        {(isRunning || hasResult) && (
          <PipelineProgress
            phase={phase}
            elapsedMs={elapsedMs}
            survivorCount={survivors.length}
          />
        )}

        {/* Verdict narrative */}
        {hasResult && cleanedNarrative && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="prose prose-invert prose-sm max-w-none mb-4"
          >
            <div className="text-white/60 leading-relaxed" style={{ fontSize: '13px' }}>
              <ReactMarkdown>{cleanedNarrative}</ReactMarkdown>
            </div>
          </motion.div>
        )}

        {/* Caveats */}
        {caveats.length > 0 && (
          <div className="mb-4">
            {caveats.filter(c => c && c.length > 5).slice(0, 3).map((c, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-amber-400/50 mb-1">
                <span className="shrink-0 mt-0.5">{'\u26A0'}</span>
                <span>{c}</span>
              </div>
            ))}
          </div>
        )}

        {/* Elimination badges */}
        <EliminationBadges eliminated={eliminated} />

        {/* Idle state */}
        {!hasResult && !isRunning && (
          <div className="flex flex-col items-center justify-center h-full text-center py-16">
            <div className="text-3xl mb-3 opacity-20">{'\u2726'}</div>
            <p className="text-sm text-white/25">Type a query to begin</p>
            <p className="text-xs text-white/15 mt-2 max-w-[280px]">
              Describe what you need. Praxis will evaluate 253 tools, eliminate the unfit, and explain why.
            </p>
          </div>
        )}
      </div>

      {/* Follow-up input at bottom */}
      {hasResult && <FollowUpInput />}
    </div>
  );
}
