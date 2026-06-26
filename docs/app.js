let allTexts = [];
const els = {
  search: document.getElementById('search'),
  category: document.getElementById('category'),
  status: document.getElementById('status'),
  stats: document.getElementById('stats'),
  results: document.getElementById('results')
};

function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function textBlob(t) {
  const tr = t.translation_access || {};
  return [t.id,t.title_standard,t.category,t.category_label,t.key_content_summary,t.primary_community_or_tradition,tr.recommended_english_translation,tr.translation_notes].join(' ').toLowerCase();
}
function populateFilters() {
  const cats = [...new Set(allTexts.map(t => t.category))].sort();
  const statuses = [...new Set(allTexts.map(t => t.project_text_status))].sort();
  for (const c of cats) els.category.insertAdjacentHTML('beforeend', `<option value="${esc(c)}">${esc(c)}</option>`);
  for (const s of statuses) els.status.insertAdjacentHTML('beforeend', `<option value="${esc(s)}">${esc(s)}</option>`);
}
function render() {
  const q = els.search.value.trim().toLowerCase();
  const cat = els.category.value;
  const st = els.status.value;
  let rows = allTexts.filter(t => (!cat || t.category === cat) && (!st || t.project_text_status === st) && (!q || textBlob(t).includes(q)));
  els.stats.textContent = `${rows.length} of ${allTexts.length} entries shown`;
  els.results.innerHTML = rows.map(t => {
    const tr = t.translation_access || {};
    const textPath = '../' + t.project_text_path;
    return `<article class="card">
      <h2>${esc(t.title_standard)} <span class="muted">(${esc(t.id)})</span></h2>
      <div class="badges"><span class="badge">${esc(t.category)}</span><span class="badge">${esc(t.date_confidence)}</span><span class="badge">${esc(t.project_text_status)}</span></div>
      <p>${esc(t.key_content_summary)}</p>
      <p class="muted"><strong>Date:</strong> ${esc(t.approximate_date)}<br><strong>Languages:</strong> ${esc(t.surviving_languages)}</p>
      <div class="translation"><strong>Recommended English translation:</strong><br>${esc(tr.recommended_english_translation)}<br><br><strong>Rights/status:</strong> ${esc(tr.translation_rights_status)}<br><strong>Notes:</strong> ${esc(tr.translation_notes)}</div>
      <p><a href="${esc(textPath)}">Project text slot</a></p>
    </article>`;
  }).join('');
}

fetch('data/texts.json').then(r => r.json()).then(data => {
  allTexts = data.texts || [];
  populateFilters();
  render();
});
for (const el of [els.search, els.category, els.status]) el.addEventListener('input', render);
