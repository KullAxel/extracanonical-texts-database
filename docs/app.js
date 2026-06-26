let allTexts = [];
let currentDocument = null;

const els = {
  search: document.getElementById('search'),
  category: document.getElementById('category'),
  documentList: document.getElementById('document-list'),
  currentDocument: document.getElementById('current-document'),
  documentView: document.getElementById('document-view'),
  welcome: document.getElementById('welcome'),
  versionCount: document.getElementById('version-count'),
};

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function textBlob(t) {
  const parts = [t.id, t.title_standard, t.category_label, t.key_content_summary, t.primary_community_or_tradition];
  if (t.versions) {
    t.versions.forEach(v => {
      parts.push(v.translator, v.source_edition, v.rights_status);
    });
  }
  return parts.join(' ').toLowerCase();
}

function populateFilters() {
  const cats = [...new Set(allTexts.map(t => t.category_label))].sort();
  els.category.innerHTML = '<option value="">All Categories</option>';
  cats.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    els.category.appendChild(opt);
  });
}

function renderList(filtered) {
  els.documentList.innerHTML = '';
  filtered.forEach(t => {
    const versions = t.versions || [];
    const hasText = versions.some(v => v.status === 'available');
    const el = document.createElement('div');
    el.className = `px-4 py-3 rounded-2xl cursor-pointer transition-all hover:bg-zinc-800 flex justify-between items-center ${currentDocument && currentDocument.id === t.id ? 'bg-zinc-800 ring-1 ring-emerald-500' : ''}`;
    el.innerHTML = `
      <div>
        <div class="font-medium text-white">${esc(t.title_standard)}</div>
        <div class="text-xs text-zinc-500">${esc(t.id)} • ${esc(t.category_label)}</div>
      </div>
      <div class="text-right">
        <div class="text-[10px] ${hasText ? 'text-emerald-400' : 'text-zinc-600'}">${versions.length} versions</div>
      </div>
    `;
    el.onclick = () => showDocument(t);
    els.documentList.appendChild(el);
  });
}

async function loadVersionText(path) {
  try {
    const res = await fetch(path);
    if (!res.ok) return '[Text not yet available or loading failed]';
    let text = await res.text();
    // Remove front matter
    text = text.replace(/^---\n[\s\S]*?\n---\n/, '');
    return text.trim() || '[Empty text]';
  } catch (e) {
    return '[Could not load text]';
  }
}

async function showDocument(doc) {
  currentDocument = doc;
  els.welcome.classList.add('hidden');
  els.documentView.classList.remove('hidden');
  els.currentDocument.textContent = doc.title_standard;
  els.versionCount.textContent = `${(doc.versions || []).length} versions`;

  const versions = doc.versions || [];
  let tabsHTML = '';
  let contentHTML = '';

  for (const v of versions) {
    const active = v.type === 'literal' ? 'border-emerald-400 text-white' : 'border-transparent text-zinc-400 hover:text-white';
    tabsHTML += `
      <button onclick="switchVersionTab(this)" data-type="${v.type}" 
              class="tab-button px-5 py-2 border-b-2 ${active} font-medium text-sm">
        ${v.type === 'literal' ? 'Literal' : v.type === 'simple' ? 'Simple English' : v.type.toUpperCase()}
      </button>`;
    // GitHub Pages publishes /docs as the site root. scripts/sync_docs_assets.py
    // mirrors texts/versions into docs/texts/versions, so catalog paths like
    // texts/versions/AF-001-literal.md are directly fetchable from the page.
    const textPath = v.path.startsWith('http') ? v.path : v.path;
    contentHTML += `
      <div id="tab-${v.type}" class="tab-content hidden">
        <div class="bg-zinc-900 rounded-3xl p-8 text-zinc-300 leading-relaxed whitespace-pre-wrap text-[15px] font-light">
          <div class="text-xs uppercase tracking-widest text-zinc-500 mb-4 border-b border-zinc-700 pb-3">
            ${v.type.toUpperCase()} VERSION • ${v.translator || 'Unknown translator'} • ${v.source_edition || 'Unknown edition'}
          </div>
          <div class="version-text" data-path="${textPath}"></div>
        </div>
        <div class="mt-6 text-xs text-zinc-500 flex items-center gap-4">
          <span class="px-3 py-1 bg-zinc-900 rounded-full">${v.rights_status}</span>
          <span>${v.segment_count || '?'} segments indexed</span>
        </div>
      </div>`;
  }

  els.documentView.innerHTML = `
    <div class="max-w-5xl mx-auto">
      <div class="flex gap-8">
        <!-- Metadata sidebar -->
        <div class="w-72 flex-shrink-0">
          <div class="bg-zinc-900 rounded-3xl p-6 sticky top-6">
            <div class="text-emerald-400 text-xs uppercase tracking-widest mb-2">Document ID</div>
            <div class="font-mono text-xl text-white mb-6">${doc.id}</div>
            
            <div class="text-emerald-400 text-xs uppercase tracking-widest mb-2">Category</div>
            <div class="mb-6">${doc.category_label}</div>

            <div class="text-emerald-400 text-xs uppercase tracking-widest mb-2">Date</div>
            <div class="mb-6">${doc.approximate_date} <span class="text-xs text-zinc-500">(${doc.date_confidence})</span></div>

            <div class="text-emerald-400 text-xs uppercase tracking-widest mb-2">Canonical Status</div>
            <div class="text-xs space-y-2">
              ${Object.entries(doc.canonical_status_by_tradition || {}).map(([trad, status]) => `
                <div class="flex justify-between"><span class="text-zinc-400">${trad.replace(/_/g, ' ')}</span><span class="text-zinc-500">${status}</span></div>
              `).join('')}
            </div>

            <div onclick="window.open('https://github.com/KullAxel/extracanonical-texts-database/blob/main/data/texts.json#L${Math.floor(Math.random()*100)}', '_blank')" 
                 class="mt-8 text-xs bg-zinc-800 hover:bg-zinc-700 cursor-pointer transition-colors rounded-2xl p-4 text-center">
              View full metadata in source
            </div>
          </div>
        </div>

        <!-- Main reader -->
        <div class="flex-1">
          <div class="flex border-b border-zinc-800 mb-6">
            ${tabsHTML}
          </div>
          <div class="tab-contents">
            ${contentHTML}
          </div>
        </div>
      </div>
    </div>
  `;

  // Load all version texts
  const textDivs = els.documentView.querySelectorAll('.version-text');
  for (const div of textDivs) {
    const path = div.dataset.path;
    const text = await loadVersionText(path);
    div.innerHTML = `<div class="prose prose-invert max-w-none">${text.replace(/\n/g, '<br>')}</div>`;
  }

  // Activate first tab (literal if available)
  const firstTab = els.documentView.querySelector('.tab-button');
  if (firstTab) switchVersionTab(firstTab);
}

function switchVersionTab(tab) {
  document.querySelectorAll('.tab-button').forEach(t => {
    t.classList.remove('border-emerald-400', 'text-white');
    t.classList.add('border-transparent', 'text-zinc-400');
  });
  tab.classList.add('border-emerald-400', 'text-white');

  document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
  const type = tab.dataset.type;
  const content = document.getElementById(`tab-${type}`);
  if (content) content.classList.remove('hidden');
}

function loadVersionText(path) {
  return fetch(path)
    .then(r => {
      if (!r.ok) throw new Error('Failed');
      return r.text();
    })
    .then(text => {
      return text.replace(/^---[\s\S]*?---\s*/, '').trim() || 'Text loaded successfully.';
    })
    .catch(() => '[Text not available or failed to load. Check rights and ingestion status.]');
}

function showHelp() {
  document.getElementById('help-modal').classList.remove('hidden');
}

function hideHelp() {
  document.getElementById('help-modal').classList.add('hidden');
}

async function init() {
  const data = await fetch('data/texts.json').then(r => r.json());
  allTexts = data.texts || [];
  populateFilters();
  
  // Initial render with all documents
  renderList(allTexts);

  els.search.addEventListener('input', () => {
    const q = els.search.value.trim().toLowerCase();
    const cat = els.category.value;
    const filtered = allTexts.filter(t => {
      const matchCat = !cat || t.category_label === cat;
      const matchSearch = !q || textBlob(t).includes(q);
      return matchCat && matchSearch;
    });
    renderList(filtered);
  });

  els.category.addEventListener('change', () => {
    els.search.dispatchEvent(new Event('input'));
  });

  // Auto-select first document for demo
  if (allTexts.length > 0) {
    setTimeout(() => {
      showDocument(allTexts[0]);
    }, 300);
  }
}

function renderList(filtered) {
  els.documentList.innerHTML = '';
  filtered.forEach(t => {
    const versions = t.versions || [];
    const hasText = versions.some(v => v.status === 'available');
    const el = document.createElement('div');
    el.className = `group px-4 py-3 rounded-2xl cursor-pointer transition-all hover:bg-zinc-800 flex justify-between items-start ${currentDocument && currentDocument.id === t.id ? 'bg-zinc-800 ring-1 ring-inset ring-emerald-500' : ''}`;
    el.innerHTML = `
      <div class="flex-1 min-w-0">
        <div class="font-medium text-white group-hover:text-emerald-300 transition-colors">${esc(t.title_standard)}</div>
        <div class="text-xs text-zinc-500 truncate">${esc(t.id)} • ${esc(t.category_label)}</div>
      </div>
      <div class="text-right text-[10px] pt-0.5">
        <span class="${hasText ? 'text-emerald-400' : 'text-zinc-600'}">${versions.length}</span>
      </div>
    `;
    el.onclick = (e) => {
      e.stopImmediatePropagation();
      showDocument(t);
    };
    els.documentList.appendChild(el);
  });
  if (filtered.length === 0) {
    els.documentList.innerHTML = `<div class="p-8 text-center text-zinc-500">No documents match your search.</div>`;
  }
}

window.switchVersionTab = switchVersionTab;
window.showHelp = showHelp;
window.hideHelp = hideHelp;

init().catch(console.error);
