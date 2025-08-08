(() => {
  const body = document.body;
  const sidebar = document.getElementById('sidebar');
  const hamburgerButton = document.getElementById('hamburgerButton');
  const collapseToggleButton = document.getElementById('collapseToggleButton');
  const backdrop = document.getElementById('backdrop');

  const isMobile = () => window.matchMedia('(max-width: 980px)').matches;

  function openMobileSidebar() {
    body.setAttribute('data-sidebar-open', 'true');
    hamburgerButton?.setAttribute('aria-expanded', 'true');
    backdrop?.removeAttribute('hidden');
    // Move focus to the first focusable item in the sidebar
    const firstItem = sidebar.querySelector('.menu-item');
    if (firstItem) {
      setTimeout(() => firstItem.focus(), 0);
    }
  }

  function closeMobileSidebar() {
    body.setAttribute('data-sidebar-open', 'false');
    hamburgerButton?.setAttribute('aria-expanded', 'false');
    backdrop?.setAttribute('hidden', '');
    // Return focus to hamburger
    setTimeout(() => hamburgerButton?.focus(), 0);
  }

  function toggleCollapse() {
    const collapsed = body.getAttribute('data-sidebar-collapsed') === 'true';
    body.setAttribute('data-sidebar-collapsed', collapsed ? 'false' : 'true');
    collapseToggleButton?.setAttribute('aria-expanded', collapsed ? 'true' : 'false');
    collapseToggleButton?.setAttribute('aria-label', collapsed ? 'Collapse navigation' : 'Expand navigation');
  }

  // Handle submenu toggle click and keyboard (Enter/Space)
  function handleSubmenuToggle(button) {
    const controlsId = button.getAttribute('aria-controls');
    const submenu = document.getElementById(controlsId);
    const isExpanded = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!isExpanded));
    if (submenu) {
      if (isExpanded) {
        submenu.hidden = true;
      } else {
        submenu.hidden = false;
      }
    }
  }

  // Event listeners
  hamburgerButton?.addEventListener('click', () => {
    const open = body.getAttribute('data-sidebar-open') === 'true';
    if (open) closeMobileSidebar(); else openMobileSidebar();
  });

  backdrop?.addEventListener('click', () => {
    closeMobileSidebar();
    // Hide backdrop element for a11y
    backdrop.setAttribute('hidden', '');
  });

  collapseToggleButton?.addEventListener('click', toggleCollapse);

  // Keyboard support for toggles
  sidebar.addEventListener('keydown', (e) => {
    const target = e.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.classList.contains('submenu-toggle')) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleSubmenuToggle(target);
      }
      if (e.key === 'ArrowRight') {
        const expanded = target.getAttribute('aria-expanded') === 'true';
        if (!expanded) handleSubmenuToggle(target);
      }
      if (e.key === 'ArrowLeft') {
        const expanded = target.getAttribute('aria-expanded') === 'true';
        if (expanded) handleSubmenuToggle(target);
      }
    }
    // Close mobile sidebar with Escape
    if (e.key === 'Escape' && isMobile()) {
      closeMobileSidebar();
    }
  });

  // Click handlers for submenu buttons
  sidebar.addEventListener('click', (e) => {
    const target = e.target;
    if (!(target instanceof Element)) return;
    const button = target.closest('.submenu-toggle');
    if (button) {
      e.preventDefault();
      handleSubmenuToggle(button);
    }
  });

  // Manage responsive state changes
  const mq = window.matchMedia('(max-width: 980px)');
  const handleMedia = () => {
    if (mq.matches) {
      body.setAttribute('data-sidebar-open', 'false');
    } else {
      // Ensure backdrop hidden
      body.setAttribute('data-sidebar-open', 'false');
      backdrop?.setAttribute('hidden', '');
    }
  };
  mq.addEventListener('change', handleMedia);
  handleMedia();

  // Ensure focus trap-ish behavior for mobile when open
  document.addEventListener('focusin', (e) => {
    if (body.getAttribute('data-sidebar-open') === 'true' && isMobile()) {
      if (!sidebar.contains(e.target) && e.target !== hamburgerButton) {
        // Redirect focus back to sidebar
        const firstItem = sidebar.querySelector('.menu-item');
        if (firstItem) firstItem.focus();
      }
    }
  });

  // Client-side extractor UI (no server required)
  const main = document.getElementById('main');
  if (main && window.ClientSideExtractor) {
    const container = document.createElement('div');
    container.className = 'container';
    container.style.marginBottom = '1rem';

    const title = document.createElement('h2');
    title.textContent = 'Client-side PDF Extraction (No Server)';

    const desc = document.createElement('p');
    desc.textContent = 'Load a local annual report PDF and extract sample metrics in-browser.';

    const controls = document.createElement('div');
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'application/pdf';

    const extractBtn = document.createElement('button');
    extractBtn.textContent = 'Extract Data';
    extractBtn.className = 'button';
    extractBtn.style.marginLeft = '0.5rem';

    const output = document.createElement('pre');
    output.style.whiteSpace = 'pre-wrap';
    output.style.fontSize = '12px';
    output.style.background = '#f6f6f6';
    output.style.padding = '8px';
    output.style.borderRadius = '6px';
    output.style.border = '1px solid #e0e0e0';

    extractBtn.addEventListener('click', async () => {
      const file = fileInput.files && fileInput.files[0];
      if (!file) {
        output.textContent = 'Please choose a PDF file first.';
        return;
      }
      output.textContent = 'Extracting...';
      try {
        const items = await window.ClientSideExtractor.extractFromPdf(file);
        output.textContent = JSON.stringify({ items }, null, 2);
      } catch (err) {
        output.textContent = 'Error: ' + (err && err.message ? err.message : String(err));
      }
    });

    controls.appendChild(fileInput);
    controls.appendChild(extractBtn);

    container.appendChild(title);
    container.appendChild(desc);
    container.appendChild(controls);
    container.appendChild(document.createElement('hr'));
    container.appendChild(output);
    main.prepend(container);
  }

  // Manage Reports Panel (requires backend running at 127.0.0.1:5000)
  async function fetchJSON(url, opts){
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return await res.json();
  }

  async function refreshBanks(){
    const select = document.getElementById('mr-bank');
    if (!select) return;
    try {
      const data = await fetchJSON('http://127.0.0.1:5000/api/banks');
      select.innerHTML = '';
      for (const b of data.banks){
        const opt = document.createElement('option');
        opt.value = b.code;
        opt.textContent = `${b.code.toUpperCase()} – ${b.name} (${b.country})`;
        select.appendChild(opt);
      }
    } catch (e){ /* backend may be offline */ }
  }

  async function refreshIndex(){
    const container = document.getElementById('mr-index');
    if (!container) return;
    container.textContent = 'Loading index...';
    try {
      const idx = await fetchJSON('http://127.0.0.1:5000/api/index');
      const lines = [];
      for (const bank of Object.keys(idx)){
        lines.push(`Bank: ${bank}`);
        for (const r of idx[bank].reports){
          lines.push(`  - FY${r.year}: ${r.path}`);
        }
      }
      container.textContent = lines.join('\n') || 'No reports found yet.';
    } catch (e){ container.textContent = 'Backend not reachable.'; }
  }

  async function uploadReport(){
    const bank = document.getElementById('mr-bank')?.value;
    const year = document.getElementById('mr-year')?.value;
    const file = document.getElementById('mr-file')?.files?.[0];
    if (!bank || !year || !file) { alert('Select bank, year, and a PDF file.'); return; }
    const form = new FormData();
    form.append('bank', bank);
    form.append('year', year);
    form.append('file', file);
    await fetchJSON('http://127.0.0.1:5000/api/upload', { method: 'POST', body: form });
    await refreshIndex();
  }

  async function collectSelected(){
    const bank = document.getElementById('mr-bank')?.value;
    if (!bank) return;
    await fetchJSON('http://127.0.0.1:5000/api/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bank, years: 6 })
    });
    await refreshIndex();
  }

  async function collectAll(){
    const select = document.getElementById('mr-bank');
    if (!select) return;
    // Collect all banks visible in dropdown
    const banks = Array.from(select.options).map(o => o.value);
    if (banks.length === 0) return;
    await fetchJSON('http://127.0.0.1:5000/api/collect_all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ banks, years: 6 })
    });
    await refreshIndex();
  }

  function wireManageReports(){
    const uploadBtn = document.getElementById('mr-upload');
    const refreshBtn = document.getElementById('mr-refresh-index');
    const collectSelBtn = document.getElementById('mr-collect-selected');
    const collectAllBtn = document.getElementById('mr-collect-all');
    if (uploadBtn) uploadBtn.addEventListener('click', uploadReport);
    if (refreshBtn) refreshBtn.addEventListener('click', refreshIndex);
    if (collectSelBtn) collectSelBtn.addEventListener('click', collectSelected);
    if (collectAllBtn) collectAllBtn.addEventListener('click', collectAll);
  }

  // Initialize panel
  refreshBanks();
  refreshIndex();
  wireManageReports();
})();


