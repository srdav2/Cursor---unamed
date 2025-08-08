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
})();


