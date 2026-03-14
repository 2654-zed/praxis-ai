import { useState } from 'react';
import { motion, AnimatePresence, Reorder, useDragControls } from 'framer-motion';
import { useRoomState, useRoomDispatch } from '../../context/RoomContext';

const ROLE_LABELS = ['Primary', 'Companion', 'Infrastructure'];
function roleFor(i) { return i === 0 ? ROLE_LABELS[0] : i === 1 ? ROLE_LABELS[1] : ROLE_LABELS[2]; }

const ROLE_STYLES = {
  Primary:        'bg-indigo-500/15 text-indigo-400/80 border-indigo-500/20',
  Companion:      'bg-cyan-500/12 text-cyan-400/70 border-cyan-500/15',
  Infrastructure: 'bg-white/5 text-white/35 border-white/8',
};

function DragHandle({ controls }) {
  return (
    <button
      className="shrink-0 cursor-grab active:cursor-grabbing text-white/15 hover:text-white/40 touch-none transition-colors"
      onPointerDown={e => controls.start(e)}
      tabIndex={-1}
    >
      <svg width="10" height="14" viewBox="0 0 10 14" fill="currentColor">
        <circle cx="2.5" cy="2" r="1.2" /><circle cx="7.5" cy="2" r="1.2" />
        <circle cx="2.5" cy="7" r="1.2" /><circle cx="7.5" cy="7" r="1.2" />
        <circle cx="2.5" cy="12" r="1.2" /><circle cx="7.5" cy="12" r="1.2" />
      </svg>
    </button>
  );
}

function StackItem({ name, index, onUnpin }) {
  const controls = useDragControls();
  const role = roleFor(index);
  return (
    <Reorder.Item
      value={name}
      dragListener={false}
      dragControls={controls}
      whileDrag={{ scale: 1.02, boxShadow: '0 8px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(99,102,241,0.3)', background: 'rgba(99,102,241,0.06)', zIndex: 50 }}
      transition={{ layout: { duration: 0.2, ease: 'easeOut' } }}
      className="flex items-center gap-2 py-2 px-2 rounded-lg hover:bg-white/[0.03] transition-colors group"
      style={{ listStyle: 'none' }}
    >
      <DragHandle controls={controls} />
      <span className="text-sm text-white/80 font-medium flex-1 min-w-0 truncate">{name}</span>
      <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded-full border shrink-0 ${ROLE_STYLES[role]}`}>{role}</span>
      <button
        onClick={() => onUnpin(name)}
        className="text-white/20 hover:text-red-400/70 opacity-0 group-hover:opacity-100 transition-all shrink-0"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" className="w-3 h-3">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
    </Reorder.Item>
  );
}

export default function StackDrawer({ open, onClose }) {
  const { pinnedTools } = useRoomState();
  const dispatch = useRoomDispatch();
  const [copied, setCopied] = useState(false);

  const handleUnpin = name => dispatch({ type: 'UNPIN_TOOL', payload: name });
  const handleReorder = newOrder => dispatch({ type: 'REORDER_PINNED_TOOLS', payload: newOrder });
  const handleCopy = () => {
    const lines = pinnedTools.map((name, i) => `${roleFor(i)}: ${name}`);
    navigator.clipboard.writeText(lines.join('\n')).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            onClick={onClose}
          />
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', stiffness: 400, damping: 35 }}
            className="absolute bottom-0 left-0 right-0 z-50 rounded-t-2xl overflow-hidden"
            style={{ background: 'rgba(12,12,18,0.96)', backdropFilter: 'blur(30px)', border: '1px solid rgba(255,255,255,0.08)', borderBottom: 'none', maxHeight: '70%' }}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
              <span className="text-xs font-medium text-white/40 uppercase tracking-wider">
                Your Stack ({pinnedTools.length})
              </span>
              <button onClick={onClose} className="text-white/25 hover:text-white/60 transition-colors text-sm">{'\u00d7'}</button>
            </div>

            <div className="overflow-y-auto p-3" style={{ maxHeight: 'calc(70vh - 48px)' }}>
              {pinnedTools.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-xs text-white/25">No tools in your stack yet.</p>
                  <p className="text-xs text-white/15 mt-1">Click "Add to stack" on any tool card.</p>
                </div>
              ) : (
                <>
                  <Reorder.Group
                    axis="y"
                    values={pinnedTools}
                    onReorder={handleReorder}
                    className="space-y-0.5"
                    style={{ listStyle: 'none', padding: 0, margin: 0 }}
                  >
                    {pinnedTools.map((name, i) => (
                      <StackItem key={name} name={name} index={i} onUnpin={handleUnpin} />
                    ))}
                  </Reorder.Group>

                  <div className="pt-3 mt-2 border-t border-white/[0.06]">
                    <button
                      onClick={handleCopy}
                      className="w-full text-[11px] text-white/40 hover:text-white/70 py-2 rounded-lg bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-white/[0.1] transition-all"
                    >
                      {copied ? 'Copied!' : 'Copy stack'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
