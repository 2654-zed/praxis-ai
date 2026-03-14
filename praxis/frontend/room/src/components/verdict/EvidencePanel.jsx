import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRoomState } from '../../context/RoomContext';
import EvidenceCard from './EvidenceCard';
import StackDrawer from './StackDrawer';

export default function EvidencePanel() {
  const { differentialResult, phase, pinnedTools } = useRoomState();
  const [stackOpen, setStackOpen] = useState(false);

  const survivors = differentialResult?.tools_recommended || differentialResult?.survivors || [];
  const isRunning = phase === 'eliminating' || phase === 'executing';
  const hasResult = !!differentialResult;

  // Sort by fit_score descending
  const sorted = [...survivors].sort((a, b) => {
    const sa = a.final_score ?? a.fit_score ?? 0;
    const sb = b.final_score ?? b.fit_score ?? 0;
    return sb - sa;
  });

  return (
    <div className="w-[360px] shrink-0 flex flex-col overflow-hidden border-l border-white/[0.06] relative max-[900px]:w-full max-[900px]:border-l-0 max-[900px]:border-t max-[900px]:border-white/[0.06]">
      <div className="flex-1 overflow-y-auto px-4 py-5">
        {/* Section header */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-[10px] font-bold text-white/25 uppercase tracking-[2px]">Evidence</span>
          {isRunning && (
            <motion.div
              className="w-1.5 h-1.5 rounded-full bg-indigo-400"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
          )}
        </div>

        {/* Loading skeleton */}
        {isRunning && sorted.length === 0 && (
          <div className="space-y-3">
            {[0, 1, 2].map(i => (
              <div key={i} className="rounded-2xl border border-white/[0.04] bg-white/[0.02] p-4 animate-pulse">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-white/[0.06]" />
                  <div className="flex-1"><div className="h-3 w-24 bg-white/[0.06] rounded" /></div>
                  <div className="h-5 w-10 bg-white/[0.06] rounded" />
                </div>
                <div className="h-2 w-full bg-white/[0.04] rounded mb-2" />
                <div className="h-2 w-3/4 bg-white/[0.04] rounded" />
              </div>
            ))}
          </div>
        )}

        {/* No results */}
        {!isRunning && hasResult && sorted.length === 0 && (
          <div className="text-center py-12">
            <div className="text-2xl mb-2 opacity-20">{'\u2205'}</div>
            <p className="text-xs text-white/25">No tools survived the elimination.</p>
            <p className="text-xs text-white/15 mt-1">Try relaxing your constraints.</p>
          </div>
        )}

        {/* Tool cards */}
        <AnimatePresence>
          {sorted.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              {sorted.map((tool, i) => (
                <EvidenceCard
                  key={tool.name || i}
                  tool={tool}
                  index={i}
                  isTopPick={i === 0}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Idle state */}
        {!hasResult && !isRunning && (
          <div className="text-center py-16">
            <p className="text-xs text-white/15">Tools will appear here after your search.</p>
          </div>
        )}
      </div>

      {/* Stack counter pill */}
      {pinnedTools.length > 0 && (
        <div className="px-4 py-2 border-t border-white/[0.06]">
          <button
            onClick={() => setStackOpen(true)}
            className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-[11px] font-medium transition-all bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 hover:bg-indigo-500/20"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Your Stack ({pinnedTools.length})
          </button>
        </div>
      )}

      {/* Stack drawer */}
      <StackDrawer open={stackOpen} onClose={() => setStackOpen(false)} />
    </div>
  );
}
