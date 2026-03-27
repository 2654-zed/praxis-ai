import { motion } from 'framer-motion';

const STEPS = [
  { num: '1', title: 'You describe what you need', desc: 'Tell us what you\'re building, what industry you\'re in, and what constraints matter.' },
  { num: '2', title: 'We eliminate what doesn\'t fit', desc: '253 tools scored across 9 trust dimensions. Tools that don\'t match your needs are removed.' },
  { num: '3', title: 'You keep the survivors', desc: 'Ranked by fit. Use Diagnosis for full elimination reasons, or search for quick results.' },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="max-w-[800px] mx-auto px-4 py-16" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="text-center mb-10">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 600, color: '#f0f0f5' }}>How it works</h2>
        <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.4)', marginTop: '6px' }}>Elimination-first. Not recommendation-first.</p>
      </div>
      <div className="grid grid-cols-3 gap-4 max-[700px]:grid-cols-1">
        {STEPS.map((step, i) => (
          <motion.div
            key={step.num}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-50px' }}
            transition={{ delay: i * 0.12 }}
            className="text-center"
            style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '16px',
              padding: '32px 24px',
              transition: 'all 0.3s ease',
            }}
          >
            <div style={{ fontSize: '2rem', fontWeight: 700, color: '#6366f1', marginBottom: '12px' }}>{step.num}</div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#f0f0f5', marginBottom: '8px' }}>{step.title}</div>
            <div style={{ fontSize: '13px', lineHeight: 1.5, color: 'rgba(255,255,255,0.45)' }}>{step.desc}</div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
