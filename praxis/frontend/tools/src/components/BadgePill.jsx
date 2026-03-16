const COMPLIANCE = new Set(['SOC2','GDPR','HIPAA','FedRAMP','ISO 27001','PCI DSS','PCI-DSS','PIPEDA','CCPA']);
const PRICING_RE = /^free|^\$/i;
const SKILL = new Set(['beginner','intermediate','advanced']);

const STYLES = {
  compliance: { bg: 'rgba(52,211,153,0.12)', border: 'rgba(52,211,153,0.25)', color: '#34d399' },
  pricing: { bg: 'rgba(99,102,241,0.12)', border: 'rgba(99,102,241,0.25)', color: '#a5b4fc' },
  skill: { bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.4)' },
  default: { bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.5)' },
};

function detectType(label) {
  if (COMPLIANCE.has(label)) return 'compliance';
  if (PRICING_RE.test(label)) return 'pricing';
  if (SKILL.has(label?.toLowerCase())) return 'skill';
  return 'default';
}

export default function BadgePill({ label, type }) {
  const t = type || detectType(label);
  const s = STYLES[t] || STYLES.default;
  return (
    <span style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '999px', background: s.bg, border: `1px solid ${s.border}`, color: s.color, whiteSpace: 'nowrap' }}>
      {label}
    </span>
  );
}
