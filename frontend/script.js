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
    title.textContent = 'Client-side PDF Extraction with QC (No Server)';

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

    const output = document.createElement('div');
    output.style.fontSize = '12px';
    output.style.background = '#f6f6f6';
    output.style.padding = '8px';
    output.style.borderRadius = '6px';
    output.style.border = '1px solid #e0e0e0';

    function renderResults(res){
      const { items = [], sanity = [] } = res || {};
      const wrapper = document.createElement('div');
      const table = document.createElement('table');
      table.style.width = '100%';
      table.style.borderCollapse = 'collapse';
      const thead = document.createElement('thead');
      thead.innerHTML = '<tr><th>Metric</th><th>Value</th><th>Units</th><th>Currency</th><th>Page</th><th>Confidence</th><th>Flags</th><th>Context</th></tr>';
      const tbody = document.createElement('tbody');
      for (const it of items){
        const tr = document.createElement('tr');
        function td(txt){ const c = document.createElement('td'); c.style.border = '1px solid #e0e0e0'; c.style.padding = '4px 6px'; c.textContent = txt; return c; }
        tr.appendChild(td(it.metric_name));
        tr.appendChild(td(it.value != null ? String(it.value) : ''));
        tr.appendChild(td(it.value_units || ''));
        tr.appendChild(td(it.value_currency || ''));
        tr.appendChild(td(String(it.source_page)));
        const conf = document.createElement('td');
        conf.style.border = '1px solid #e0e0e0';
        conf.style.padding = '4px 6px';
        conf.textContent = (Math.round((it.confidence ?? 0)*100)) + '%';
        tr.appendChild(conf);
        const flags = document.createElement('td');
        flags.style.border = '1px solid #e0e0e0';
        flags.style.padding = '4px 6px';
        flags.textContent = (it.flags||[]).join(', ');
        tr.appendChild(flags);
        const ctx = document.createElement('td');
        ctx.style.border = '1px solid #e0e0e0';
        ctx.style.padding = '4px 6px';
        const btn = document.createElement('button');
        btn.className = 'button';
        btn.textContent = 'View context';
        btn.addEventListener('click', () => {
          alert(['Prev: ' + (it.context_prev_line||''), 'Line: ' + (it.context_line||''), 'Next: ' + (it.context_next_line||'')].join('\n'));
        });
        ctx.appendChild(btn);
        tr.appendChild(ctx);
        tbody.appendChild(tr);
      }
      table.appendChild(thead);
      table.appendChild(tbody);
      wrapper.appendChild(table);
      if (sanity.length){
        const warn = document.createElement('div');
        warn.style.marginTop = '8px';
        warn.style.padding = '6px 8px';
        warn.style.background = '#fff7e6';
        warn.style.border = '1px solid #ffe58f';
        warn.style.borderRadius = '6px';
        warn.textContent = 'Sanity checks: ' + sanity.map(s => `${s.level}: ${s.message}`).join(' | ');
        wrapper.appendChild(warn);
      }
      output.innerHTML = '';
      output.appendChild(wrapper);
    }

    extractBtn.addEventListener('click', async () => {
      const file = fileInput.files && fileInput.files[0];
      if (!file) {
        output.textContent = 'Please choose a PDF file first.';
        return;
      }
      output.textContent = 'Extracting...';
      try {
        const res = await window.ClientSideExtractor.extractFromPdf(file);
        renderResults(res);
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

  const backend = {
    base: 'http://127.0.0.1:5000',
    async status(){
      try { return await fetchJSON(`${this.base}/api/status`); } catch (_) { return null; }
    },
    // Poll status a few times after load to handle slow starts
    async waitUntilUp(timeoutMs = 15000){
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        const s = await this.status();
        if (s) return true;
        await new Promise(r => setTimeout(r, 1000));
      }
      return false;
    }
  };

  async function refreshBanks(){
    const select = document.getElementById('mr-bank');
    if (!select) return;
    try {
      const data = await fetchJSON(`${backend.base}/api/banks`);
      select.innerHTML = '';
      for (const b of data.banks){
        const opt = document.createElement('option');
        opt.value = b.code;
        opt.textContent = `${b.code.toUpperCase()} – ${b.name} (${b.country})`;
        select.appendChild(opt);
      }
      // Optionally, we could show source links for transparency
      window.__BANK_SOURCES = data.sources;
    } catch (e){ /* backend may be offline */ }
  }

  async function refreshIndex(){
    const rawContainer = document.getElementById('mr-index');
    const tableContainer = document.getElementById('mr-index-table');
    if (rawContainer) rawContainer.textContent = 'Loading index...';
    if (tableContainer) tableContainer.textContent = 'Loading...';
    try {
      const idx = await fetchJSON(`${backend.base}/api/index`);
      // raw debug
      if (rawContainer){
        const lines = [];
        for (const bank of Object.keys(idx)){
          lines.push(`Bank: ${bank}`);
          for (const r of idx[bank].reports){
            const sizeInfo = (r.size_bytes && r.size_bytes > 0) ? ` (${(r.size_bytes/1024/1024).toFixed(2)} MB)` : ' (not downloaded)';
            lines.push(`  - FY${r.year}: ${r.path}${sizeInfo}`);
          }
        }
        rawContainer.textContent = lines.join('\n') || 'No reports found yet.';
      }

      // years set from min..max in index
      const yearsSet = new Set();
      Object.values(idx).forEach((entry) => {
        entry.reports.forEach(r => yearsSet.add(parseInt(r.year, 10)));
      });
      const years = Array.from(yearsSet).sort((a,b)=>a-b);
      const banks = Object.keys(idx).sort();

      // build table
      if (tableContainer){
        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.fontSize = '13px';
        const thead = document.createElement('thead');
        const trh = document.createElement('tr');
        const th0 = document.createElement('th'); th0.textContent = 'Bank'; trh.appendChild(th0);
        years.forEach(y => { const th = document.createElement('th'); th.textContent = `FY${y}`; trh.appendChild(th); });
        thead.appendChild(trh);
        const tbody = document.createElement('tbody');

        function cell(content, downloaded){
          const td = document.createElement('td');
          td.style.border = '1px solid #e0e0e0';
          td.style.textAlign = 'center';
          td.style.padding = '4px 6px';
          td.textContent = content;
          if (downloaded === true) td.style.color = '#0b7a0b';
          if (downloaded === false) td.style.color = '#b00020';
          return td;
        }

        function actionCell(bank, year, entry){
          const td = document.createElement('td');
          td.style.border = '1px solid #e0e0e0';
          td.style.textAlign = 'center';
          td.style.padding = '4px 6px';
          if (!entry) { td.textContent = ''; return td; }
          const openBtn = document.createElement('a');
          // Build a file:// URL using absolute path when running off file://
          const isFileCtx = location.protocol === 'file:' || location.origin === 'null';
          const abs = entry.abs_path || entry.path;
          const href = isFileCtx && abs ? `file://${encodeURI(abs)}` : entry.path;
          openBtn.href = href;
          openBtn.target = '_blank';
          openBtn.rel = 'noopener';
          openBtn.title = 'Open file';
          openBtn.textContent = '📄';
          openBtn.style.marginRight = '8px';

          const approveBtn = document.createElement('button');
          approveBtn.textContent = '✓';
          approveBtn.title = 'Approve as annual report';
          approveBtn.style.marginRight = '6px';
          approveBtn.addEventListener('click', async () => {
            try {
              await fetchJSON(`${backend.base}/api/index/approve`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bank, year })
              });
              await refreshIndex();
            } catch (e) { alert('Approve failed'); }
          });

          const rejectBtn = document.createElement('button');
          rejectBtn.textContent = '×';
          rejectBtn.title = 'Wrong document (delete)';
          rejectBtn.addEventListener('click', async () => {
            if (!confirm(`Delete ${entry.path}?`)) return;
            try {
              await fetchJSON(`${backend.base}/api/index/reject`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bank, year })
              });
              await refreshIndex();
            } catch (e) { alert('Delete failed'); }
          });

          td.appendChild(openBtn);
          td.appendChild(approveBtn);
          td.appendChild(rejectBtn);
          return td;
        }

        banks.forEach(b => {
          const tr = document.createElement('tr');
          const name = document.createElement('td');
          name.textContent = b.toUpperCase();
          name.style.border = '1px solid #e0e0e0';
          name.style.fontWeight = '600';
          name.style.padding = '4px 6px';
          tr.appendChild(name);
          years.forEach(y => {
            const hit = (idx[b]?.reports || []).find(r => parseInt(r.year,10) === y);
            if (!hit) {
              const td = document.createElement('td');
              td.colSpan = 2; td.textContent = '×'; td.style.color = '#b00020'; td.style.border='1px solid #e0e0e0'; td.style.textAlign='center';
              tr.appendChild(td);
            } else {
              const downloaded = !!(hit.size_bytes && hit.size_bytes > 0);
              tr.appendChild(cell(downloaded ? (hit.is_financial ? '✓' : '⚠︎') : '×', downloaded));
              tr.appendChild(actionCell(b, y, hit));
            }
          });
          tbody.appendChild(tr);
        });
        table.appendChild(thead);
        table.appendChild(tbody);
        tableContainer.innerHTML = '';
        tableContainer.appendChild(table);
      }
    } catch (e){ container.textContent = 'Backend not reachable. Start it via backend/Run Backend.command'; }
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
    try {
      await fetchJSON(`${backend.base}/api/upload`, { method: 'POST', body: form });
      await refreshIndex();
      alert('Uploaded and indexed.');
    } catch (e){ alert('Upload failed. Ensure backend is running.'); }
  }

  async function collectSelected(){
    const bank = document.getElementById('mr-bank')?.value;
    if (!bank) return;
    try {
      await fetchJSON(`${backend.base}/api/collect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bank, years: 6 })
      });
      await refreshIndex();
      alert('Collection started/completed for selected bank (best-effort).');
    } catch (e){ alert('Collect failed. Ensure backend is running.'); }
  }

  async function collectAll(){
    const select = document.getElementById('mr-bank');
    if (!select) return;
    // Collect all banks visible in dropdown
    const banks = Array.from(select.options).map(o => o.value);
    if (banks.length === 0) return;
    try {
      await fetchJSON(`${backend.base}/api/collect_all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ banks, years: 6 })
      });
      await refreshIndex();
      alert('Collection started/completed for all banks (best-effort).');
    } catch (e){ alert('Collect all failed. Ensure backend is running.'); }
  }

  function wireManageReports(){
    const uploadBtn = document.getElementById('mr-upload');
    const refreshBtn = document.getElementById('mr-refresh-index');
    const collectSelBtn = document.getElementById('mr-collect-selected');
    const collectAllBtn = document.getElementById('mr-collect-all');
    const cleanupBtn = document.getElementById('mr-cleanup');
    const migrateBtn = document.getElementById('mr-migrate');
    async function cleanup(){ try { await fetchJSON(`${backend.base}/api/maintenance/cleanup`, { method: 'POST' }); await refreshIndex(); alert('Cleanup done.'); } catch (e) { alert('Cleanup failed. Ensure backend is running.'); } }
    async function migrate(){ try { await fetchJSON(`${backend.base}/api/maintenance/migrate`, { method: 'POST' }); await refreshIndex(); alert('Migration done.'); } catch (e) { alert('Migration failed. Ensure backend is running.'); } }
    if (uploadBtn) uploadBtn.addEventListener('click', uploadReport);
    if (refreshBtn) refreshBtn.addEventListener('click', refreshIndex);
    if (collectSelBtn) collectSelBtn.addEventListener('click', collectSelected);
    if (collectAllBtn) collectAllBtn.addEventListener('click', collectAll);
    if (cleanupBtn) cleanupBtn.addEventListener('click', cleanup);
    if (migrateBtn) migrateBtn.addEventListener('click', migrate);
  }

  // Initialize panel
  (async () => {
    let status = await backend.status();
    if (!status) {
      // give backend a short grace period
      await backend.waitUntilUp(20000);
      status = await backend.status();
    }
    const pill = document.getElementById('backend-status-pill');
    if (status) {
      if (pill){ pill.textContent = 'Backend: Connected'; pill.style.background = '#0b7a0b'; }
      await refreshBanks();
      await refreshIndex();
    } else {
      if (pill){ pill.textContent = 'Backend: Disconnected'; pill.style.background = '#b00020'; }
      // still render banks/index best-effort
      await refreshBanks();
      await refreshIndex();
    }
  })();
  wireManageReports();
})();


