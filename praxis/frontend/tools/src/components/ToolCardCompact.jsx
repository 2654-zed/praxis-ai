import BadgePill from './BadgePill';

function getDomain(url) { try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return ''; } }

export default function ToolCardCompact({ tool }) {
  const domain = getDomain(tool.url);
  const badges = [];
  (tool.compliance || []).slice(0, 2).forEach(c => badges.push({ label: c, type: 'compliance' }));
  const p = tool.pricing || {};
  if (p.free_tier) badges.push({ label: 'Free', type: 'pricing' });
  return (
    <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 12, transition: 'all 0.2s ease' }}>
      {domain ? <img src={`https://www.google.com/s2/favicons?domain=${domain}&sz=32`} alt="" style={{ width: 28, height: 28, borderRadius: 8, objectFit: 'contain', background: 'rgba(255,255,255,0.06)', padding: 3, flexShrink: 0 }} onError={e => { e.target.style.display='none'; e.target.nextElementSibling.style.display='flex'; }} /> : null}
      <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg,#6366f1,#50e3c2)', display: domain ? 'none' : 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: 12, flexShrink: 0 }}>{tool.name?.charAt(0)}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#f0f0f5', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{tool.name}</div>
        <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{tool.description}</div>
      </div>
      <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
        {badges.map((b, i) => <BadgePill key={i} label={b.label} type={b.type} />)}
      </div>
      <span style={{ fontSize: 11, fontWeight: 700, color: '#fb923c', flexShrink: 0 }}>{tool.grade}</span>
      <a href={`/room?q=${encodeURIComponent(tool.name)}`} style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', textDecoration: 'none', flexShrink: 0 }}>Evaluate →</a>
    </div>
  );
}
