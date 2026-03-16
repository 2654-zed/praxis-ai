import { useRef, useEffect, useState } from 'react';
import BadgePill from './BadgePill';

const TIER_COLORS = { sovereign: '#34d399', durable: '#6366f1', moderate: '#fb923c', fragile: '#ef4444', wrapper: 'rgba(255,255,255,0.35)' };

function getDomain(url) { try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return ''; } }

export default function ToolCardFull({ tool, index }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } }, { threshold: 0.1 });
    obs.observe(el); return () => obs.disconnect();
  }, []);

  const domain = getDomain(tool.url);
  const tier = tool.tier || 'moderate';
  const tierColor = TIER_COLORS[tier] || TIER_COLORS.moderate;
  const badges = [];
  (tool.compliance || []).forEach(c => badges.push({ label: c, type: 'compliance' }));
  const p = tool.pricing || {};
  if (p.free_tier) badges.push({ label: 'Free tier', type: 'pricing' });
  else if (p.starter) badges.push({ label: `$${p.starter}/mo`, type: 'pricing' });
  if (tool.skill_level) badges.push({ label: tool.skill_level, type: 'skill' });

  return (
    <div
      ref={ref}
      style={{
        background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '16px',
        padding: '20px', transition: 'all 0.3s ease', cursor: 'pointer',
        opacity: visible ? 1 : 0, transform: visible ? 'translateY(0)' : 'translateY(12px)',
        transitionDelay: `${index * 30}ms`,
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        {domain ? (
          <img src={`https://www.google.com/s2/favicons?domain=${domain}&sz=32`} alt="" style={{ width: 36, height: 36, borderRadius: 10, objectFit: 'contain', background: 'rgba(255,255,255,0.06)', padding: 4 }}
               onError={e => { e.target.style.display='none'; e.target.nextElementSibling.style.display='flex'; }} />
        ) : null}
        <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg,#6366f1,#50e3c2)', display: domain ? 'none' : 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: 14, flexShrink: 0 }}>
          {tool.name?.charAt(0)}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 16, fontWeight: 600, color: '#f0f0f5', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{tool.name}</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>{(tool.categories || []).slice(0, 3).join(' · ')}</div>
        </div>
        <span style={{ fontSize: 10, fontWeight: 700, padding: '3px 8px', borderRadius: 999, background: `${tierColor}18`, color: tierColor, border: `1px solid ${tierColor}40`, whiteSpace: 'nowrap', flexShrink: 0 }}>
          {tool.grade} · {tier.toUpperCase()}
        </span>
      </div>

      {/* Description */}
      <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.5)', marginBottom: 12, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
        {tool.description}
      </div>

      {/* Badges */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 14 }}>
        {badges.slice(0, 6).map((b, i) => <BadgePill key={i} label={b.label} type={b.type} />)}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8 }}>
        <a href={`/room?q=${encodeURIComponent(tool.name)}`} style={{ fontSize: 12, fontWeight: 500, padding: '8px 18px', borderRadius: 12, background: '#6366f1', color: 'white', textDecoration: 'none', border: 'none' }}>Evaluate</a>
        <a href={`/static/tuesday-test.html?tool=${encodeURIComponent(tool.name)}`} style={{ fontSize: 12, fontWeight: 500, padding: '8px 18px', borderRadius: 12, background: 'transparent', color: 'rgba(255,255,255,0.4)', textDecoration: 'none', border: '1px solid rgba(255,255,255,0.08)' }}>Calculate ROI</a>
      </div>
    </div>
  );
}
