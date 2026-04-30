export default function Footer() {
  const linkClass = "block text-[13px] text-white/30 no-underline leading-8 hover:text-white/60 transition-colors duration-200";
  return (
    <footer style={{ background: 'rgba(0,0,0,0.25)', borderTop: '1px solid rgba(255,255,255,0.05)', padding: '52px 40px 28px', marginTop: '48px' }}>
      <div className="grid grid-cols-3 gap-8 max-w-[800px] mx-auto max-[600px]:grid-cols-1">
        <div>
          <div className="text-[11px] font-semibold text-white/40 uppercase tracking-widest mb-4">Product</div>
          <a href="/static/tools.html" className={linkClass}>All Tools</a>
          <a href="/static/differential.html" className={linkClass}>Diagnosis</a>
          <a href="/journey" className={linkClass}>Build My Stack</a>
        </div>
        <div>
          <div className="text-[11px] font-semibold text-white/40 uppercase tracking-widest mb-4">Resources</div>
          <a href="/static/tuesday-test.html" className={linkClass}>ROI Calculator</a>
          <a href="/static/rfp.html" className={linkClass}>RFP Builder</a>
          <a href="/static/stack-advisor.html" className={linkClass}>Stack Advisor</a>
          <a href="/static/trust_badges.html" className={linkClass}>Trust Badges</a>
        </div>
        <div>
          <div className="text-[11px] font-semibold text-white/40 uppercase tracking-widest mb-4">Company</div>
          <a href="/static/manifesto.html" className={linkClass}>Methodology</a>
          <a href="/static/partners.html" className={linkClass}>Partners</a>
        </div>
      </div>
      <div className="max-w-[800px] mx-auto mt-10 pt-5 text-center text-[11px] text-white/20" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        &copy; 2026 PRAXIS AI LLC &middot; <a href="/static/privacy-policy.html" className="text-white/20 no-underline hover:text-white/45 transition-colors duration-200">Privacy</a> &middot; <a href="/static/terms-of-service.html" className="text-white/20 no-underline hover:text-white/45 transition-colors duration-200">Terms</a>
      </div>
    </footer>
  );
}
