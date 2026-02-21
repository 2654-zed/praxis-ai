async function loadAllTools() {
  const res = await fetch('/tools');
  const data = await res.json();
  const el = document.getElementById('tools');
  el.innerHTML = '';
  if (!data || data.length === 0) {
    el.textContent = 'No tools available.';
    return;
  }
  data.forEach(t => {
    const d = document.createElement('div');
    d.className = 'tool';
    const h = document.createElement('h3');
    h.textContent = t.name;
    d.appendChild(h);

    const p = document.createElement('p');
    p.textContent = t.description || '';
    d.appendChild(p);

    const meta = document.createElement('div');
    meta.className = 'meta';
    const cats = (t.categories || []).join(', ');
    const tags = (t.tags || []).join(', ');
    meta.textContent = `Categories: ${cats} · Tags: ${tags} · Popularity: ${t.popularity || 0}`;
    d.appendChild(meta);

    if (t.url) {
      const a = document.createElement('a');
      a.href = t.url;
      a.target = '_blank';
      a.textContent = 'Open';
      a.style.display = 'inline-block';
      a.style.marginTop = '0.5rem';
      d.appendChild(a);
    }

    el.appendChild(d);
  });
}

loadAllTools();
