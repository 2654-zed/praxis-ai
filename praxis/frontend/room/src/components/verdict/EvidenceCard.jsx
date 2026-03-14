import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRoomState, useRoomDispatch } from '../../context/RoomContext';
import ToolDetailDrawer from '../elimination/ToolDetailDrawer';

function getLogoDomain(url) {
  try { return new URL(url).hostname.replace(/^www\./, ''); }
  catch { return ''; }
}

export default function EvidenceCard({ tool, index, isTopPick }) {
  const { pinnedTools } = useRoomState();
  const dispatch = useRoomDispatch();
  const [showDetails, setShowDetails] = useState(isTopPick);

  const name = tool.name || 'Unknown';
  const score = tool.final_score ?? tool.fit_score ?? null;
  const scoreDisplay = score != null ? Math.round(score <= 1 ? score * 100 : score) : null;
  const description = tool.description || '';
  const reasons = tool.survival_reasons || tool.reasons || [];
  const compliance = tool.compliance || [];
  const pricing = tool.pricing || {};
  const domain = getLogoDomain(tool.url);
  const isPinned = pinnedTools.includes(name);

  const handleAddToStack = (e) => {
    e.stopPropagation();
    if (isPinned) {
      dispatch({ type: 'UNPIN_TOOL', payload: name });
    } else {
      dispatch({ type: 'PIN_TOOL', payload: name });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className={`rounded-2xl overflow-hidden transition-all ${
        isTopPick
          ? 'border-2 border-indigo-500/40 bg-indigo-500/[0.04]'
          : 'border border-white/[0.06] bg-white/[0.03]'
      }`}
      style={{ backdropFilter: 'blur(20px)' }}
    >
      <div className="p-4">
        {/* Top pick label */}
        {isTopPick && (
          <div className="flex items-center gap-1.5 mb-2">
            <span className="text-[9px] font-bold uppercase tracking-[1.5px] text-indigo-400">Top Pick</span>
          </div>
        )}

        {/* Header: logo + name + score */}
        <div className="flex items-center gap-3 mb-2">
          {domain ? (
            <img
              src={`https://www.google.com/s2/favicons?domain=${domain}&sz=64`}
              alt={name}
              className="w-9 h-9 rounded-lg object-contain bg-white/[0.08] p-1 shrink-0"
              onError={e => { e.target.style.display = 'none'; e.target.nextElementSibling.style.display = 'flex'; }}
            />
          ) : null}
          <div
            className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-teal-400 flex items-center justify-center text-white font-bold text-sm shrink-0"
            style={{ display: domain ? 'none' : 'flex' }}
          >
            {name.charAt(0)}
          </div>

          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-white/90 truncate">{name}</div>
          </div>

          {scoreDisplay != null && (
            <span className={`font-mono font-bold shrink-0 ${isTopPick ? 'text-2xl text-indigo-400' : 'text-lg text-white/50'}`}>
              {scoreDisplay}%
            </span>
          )}
        </div>

        {/* Description */}
        <p className="text-xs text-white/35 leading-relaxed mb-3 line-clamp-2">
          {description.slice(0, 160)}{description.length > 160 ? '\u2026' : ''}
        </p>

        {/* Compliance + pricing badges */}
        <div className="flex flex-wrap gap-1 mb-3">
          {compliance.slice(0, 4).map((c, i) => (
            <span key={i} className="text-[9px] font-medium px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400/70 border border-emerald-500/15">
              {c}
            </span>
          ))}
          {pricing.free_tier && (
            <span className="text-[9px] font-medium px-1.5 py-0.5 rounded-full bg-teal-500/10 text-teal-400/70 border border-teal-500/15">
              Free tier
            </span>
          )}
          {!pricing.free_tier && pricing.starter && (
            <span className="text-[9px] font-medium px-1.5 py-0.5 rounded-full bg-white/5 text-white/40 border border-white/10">
              From ${pricing.starter}/mo
            </span>
          )}
        </div>

        {/* Reasoning snippet (expanded for top pick, first reason for others) */}
        {reasons.length > 0 && (isTopPick || reasons.length > 0) && (
          <div className="mb-3">
            {(isTopPick ? reasons.slice(0, 3) : reasons.slice(0, 1)).map((r, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-white/40 mb-1">
                <span className="text-emerald-400/50 mt-0.5 shrink-0">{'\u2713'}</span>
                <span>{r}</span>
              </div>
            ))}
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-2">
          <button
            onClick={handleAddToStack}
            className={`flex-1 text-[11px] font-medium py-1.5 rounded-lg border transition-all ${
              isPinned
                ? 'bg-indigo-500/20 border-indigo-500/30 text-indigo-400'
                : isTopPick
                  ? 'bg-indigo-500 border-indigo-500 text-white hover:bg-indigo-400'
                  : 'bg-white/5 border-white/10 text-white/50 hover:bg-indigo-500/10 hover:border-indigo-500/30 hover:text-indigo-400'
            }`}
          >
            {isPinned ? '\u2713 In stack' : 'Add to stack'}
          </button>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-3 text-[11px] text-white/30 hover:text-white/60 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.1] transition-all"
          >
            {showDetails ? 'Less' : 'Details'}
          </button>
        </div>
      </div>

      {/* Detail drawer */}
      <AnimatePresence>
        {showDetails && <ToolDetailDrawer tool={tool} />}
      </AnimatePresence>
    </motion.div>
  );
}
