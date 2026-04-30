export default function Nav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-7 px-6 py-3.5"
         style={{ background: 'rgba(8,8,13,0.8)', backdropFilter: 'blur(40px) saturate(1.4)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
      <a href="/" className="font-semibold text-[15px] text-white tracking-tight" style={{ letterSpacing: '-0.03em' }}>Vannus</a>
      <a href="/static/tools.html" className="text-[13px] font-medium text-white/50 hover:text-white/90 transition-colors duration-200">Tools</a>
      <a href="/static/differential.html" className="text-[13px] font-medium text-white/50 hover:text-white/90 transition-colors duration-200">Diagnosis</a>
      <a href="/journey" className="text-[13px] font-medium text-white/50 hover:text-white/90 transition-colors duration-200">Build My Stack</a>
      <a href="/static/manifesto.html" className="text-[13px] font-medium text-white/50 hover:text-white/90 transition-colors duration-200">Methodology</a>
    </nav>
  );
}
