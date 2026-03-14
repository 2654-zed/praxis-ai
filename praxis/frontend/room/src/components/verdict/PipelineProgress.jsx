import { motion } from 'framer-motion';

const STAGES = [
  { key: 'understanding', label: 'Understanding query' },
  { key: 'filtering', label: 'Filtering tools' },
  { key: 'selecting', label: 'Selecting matches' },
  { key: 'creating', label: 'Creating verdict' },
  { key: 'done', label: 'Done' },
];

function phaseToStageIndex(phase) {
  if (phase === 'eliminating') return 1;
  if (phase === 'routing') return 2;
  if (phase === 'executing') return 3;
  if (phase === 'complete') return 5;
  return 0;
}

export default function PipelineProgress({ phase, elapsedMs, survivorCount }) {
  const activeIndex = phaseToStageIndex(phase);
  const isComplete = phase === 'complete' || phase === 'routing';

  if (isComplete) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center gap-2 mb-4"
      >
        <span className="text-emerald-400/70 text-xs">{'\u2713'}</span>
        <span className="text-xs text-white/30">
          {survivorCount} matched{elapsedMs ? ` in ${(elapsedMs / 1000).toFixed(1)}s` : ''}
        </span>
      </motion.div>
    );
  }

  return (
    <div className="mb-4 space-y-1">
      {STAGES.slice(0, -1).map((stage, i) => {
        const isDone = i < activeIndex;
        const isCurrent = i === activeIndex;
        return (
          <motion.div
            key={stage.key}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: isCurrent ? 1 : isDone ? 0.4 : 0.15, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className="flex items-center gap-2"
          >
            {isDone ? (
              <span className="text-emerald-400/60 text-[10px]">{'\u2713'}</span>
            ) : isCurrent ? (
              <motion.span
                className="w-1.5 h-1.5 rounded-full bg-indigo-400"
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            ) : (
              <span className="w-1.5 h-1.5 rounded-full bg-white/10" />
            )}
            <span className={`text-xs ${isCurrent ? 'text-indigo-400/80' : isDone ? 'text-white/30' : 'text-white/15'}`}>
              {stage.label}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
