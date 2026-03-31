const PATHS = [
  { title: 'Guided journey', sub: '4 questions, 2 min', href: '/journey', iconBg: 'rgba(52,211,153,0.12)', iconColor: '#34d399', icon: <path d="M3 8l4 4 6-8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/> },
  { title: 'Browse catalog', sub: '250+ tools', href: '/static/tools.html', iconBg: 'rgba(99,102,241,0.12)', iconColor: '#6366f1', icon: <><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></> },
  { title: 'Compare tools', sub: 'Side by side', action: 'compare', iconBg: 'rgba(251,146,60,0.12)', iconColor: '#fb923c', icon: <><rect x="2" y="3" width="5" height="10" rx="1" stroke="currentColor" strokeWidth="1.3"/><rect x="9" y="3" width="5" height="10" rx="1" stroke="currentColor" strokeWidth="1.3"/></> },
  { title: 'ROI calculator', sub: 'The Tuesday Test', href: '/static/tuesday-test.html', iconBg: 'rgba(244,63,94,0.12)', iconColor: '#f43f5e', icon: <path d="M8 2v12M4 6l4-4 4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/> },
];

export default function PathCards({ onCompare }) {
  return (
    <div className="max-w-[640px] mx-auto px-4 mt-6">
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', marginBottom: '16px' }} />
      <div className="flex items-center gap-2.5 mb-3">
        <span style={{ fontSize: '11px', fontWeight: 500, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.25)', whiteSpace: 'nowrap' }}>Or try a different approach</span>
        <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.06)' }} />
      </div>
      <div className="grid grid-cols-4 gap-2.5 max-[700px]:grid-cols-2 max-[500px]:grid-cols-1">
        {PATHS.map(p => {
          const Tag = p.href ? 'a' : 'button';
          const props = p.href ? { href: p.href } : { onClick: onCompare };
          return (
            <Tag
              key={p.title}
              {...props}
              className="flex items-center gap-3 cursor-pointer"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '16px',
                padding: '16px 20px',
                textDecoration: 'none',
                transition: 'all 0.3s ease',
              }}
            >
              <div className="flex items-center justify-center shrink-0" style={{ width: '36px', height: '36px', borderRadius: '10px', background: p.iconBg, color: p.iconColor }}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">{p.icon}</svg>
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 500, color: '#f0f0f5' }}>{p.title}</div>
                <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.35)' }}>{p.sub}</div>
              </div>
            </Tag>
          );
        })}
      </div>
    </div>
  );
}
