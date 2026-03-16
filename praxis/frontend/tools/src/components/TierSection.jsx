const TIER_DISPLAY = { sovereign: 'Sovereign Collection', durable: 'Durable Architecture', moderate: 'Moderate', fragile: 'Fragile', wrapper: 'Wrapper' };
const TIER_COLORS = { sovereign: '#34d399', durable: '#6366f1', moderate: '#fb923c', fragile: '#ef4444', wrapper: 'rgba(255,255,255,0.35)' };

export default function TierSection({ tier, tools, CardComponent, columns = 3 }) {
  if (!tools || tools.length === 0) return null;
  const color = TIER_COLORS[tier] || '#6366f1';
  const display = TIER_DISPLAY[tier] || tier;

  return (
    <section id={`tier-${tier}`} className="max-w-5xl mx-auto px-4" style={{ marginBottom: 40 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <span style={{ fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 999, background: `${color}18`, color, border: `1px solid ${color}40`, textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap' }}>{tier}</span>
        <span style={{ fontSize: 16, fontWeight: 600, color: '#f0f0f5', whiteSpace: 'nowrap' }}>{display}</span>
        <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.3)', whiteSpace: 'nowrap' }}>{tools.length} tools</span>
        <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.06)' }} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${columns}, 1fr)`, gap: columns === 1 ? 8 : 12 }}>
        {tools.map((tool, i) => <CardComponent key={tool.name} tool={tool} index={i} />)}
      </div>
    </section>
  );
}
