const TIERS = [
  { id: 'all', label: 'All' },
  { id: 'sovereign', label: 'Sovereign', color: '#34d399' },
  { id: 'durable', label: 'Durable', color: '#6366f1' },
  { id: 'moderate', label: 'Moderate', color: '#fb923c' },
];

export default function SearchFilter({ query, onQueryChange, activeTier, onTierChange, sortBy, onSortChange, counts }) {
  return (
    <div className="max-w-5xl mx-auto px-4" style={{ marginBottom: 24 }}>
      {/* Search + Sort */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: '0 16px' }}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ color: 'rgba(255,255,255,0.25)', flexShrink: 0 }}><circle cx="7" cy="7" r="4.5" stroke="currentColor" strokeWidth="1.5"/><path d="M10.5 10.5L13 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
          <input
            type="text" value={query} onChange={e => onQueryChange(e.target.value)}
            placeholder={`Search ${counts.total || 254} tools...`}
            style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', color: '#f0f0f5', fontSize: 14, padding: '12px 10px', caretColor: '#6366f1' }}
          />
        </div>
        <select
          value={sortBy} onChange={e => onSortChange(e.target.value)}
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: '0 16px', color: 'rgba(255,255,255,0.5)', fontSize: 13, outline: 'none', cursor: 'pointer', appearance: 'none', minWidth: 140 }}
        >
          <option value="rank">Praxis Rank</option>
          <option value="name_asc">Name A-Z</option>
          <option value="name_desc">Name Z-A</option>
          <option value="compliance">Most Compliant</option>
        </select>
      </div>

      {/* Tier tabs */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {TIERS.map(t => {
          const isActive = activeTier === t.id;
          const count = t.id === 'all' ? counts.total : counts[t.id] || 0;
          return (
            <button
              key={t.id} onClick={() => onTierChange(t.id)}
              style={{
                fontSize: 13, padding: '6px 14px', borderRadius: 999, cursor: 'pointer', transition: 'all 0.2s ease',
                background: isActive ? (t.color ? `${t.color}18` : 'rgba(99,102,241,0.12)') : 'rgba(255,255,255,0.04)',
                border: `1px solid ${isActive ? (t.color ? `${t.color}50` : 'rgba(99,102,241,0.35)') : 'rgba(255,255,255,0.08)'}`,
                color: isActive ? (t.color || '#a5b4fc') : 'rgba(255,255,255,0.5)',
              }}
            >
              {t.label} ({count})
            </button>
          );
        })}
      </div>
    </div>
  );
}
