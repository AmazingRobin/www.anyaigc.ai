(() => {
  'use strict';
  const root = document.documentElement;
  root.classList.add('mi-js');
  const zh = root.lang.toLowerCase().startsWith('zh');
  const t = (a, b) => (zh ? a : b);
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  // Live region for copy feedback
  const live = document.createElement('span');
  live.setAttribute('role', 'status');
  live.setAttribute('aria-live', 'polite');
  live.style.cssText = 'position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)';
  document.body.append(live);

  // Sticky nav border
  const nav = document.querySelector('.mi-nav');
  if (nav) {
    let ticking = false;
    const update = () => { nav.classList.toggle('is-scrolled', window.scrollY > 8); ticking = false; };
    update();
    window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  }

  // Mobile menu
  const menu = document.querySelector('.mi-menu');
  if (nav && menu) {
    const set = open => {
      menu.setAttribute('aria-expanded', String(open));
      menu.setAttribute('aria-label', open ? t('关闭导航菜单', 'Close navigation menu') : t('打开导航菜单', 'Open navigation menu'));
      nav.classList.toggle('is-menu-open', open);
    };
    menu.addEventListener('click', () => set(menu.getAttribute('aria-expanded') !== 'true'));
    nav.querySelectorAll('nav a').forEach(a => a.addEventListener('click', () => set(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { set(false); menu.focus(); } });
    window.matchMedia('(min-width: 901px)').addEventListener('change', e => { if (e.matches) set(false); });
  }

  // Code tabs
  document.querySelectorAll('.mi-tabs').forEach((list, g) => {
    const entries = [...list.querySelectorAll('button[data-panel]')]
      .map(tab => ({ tab, panel: document.getElementById(tab.dataset.panel) }))
      .filter(e => e.panel);
    if (!entries.length) return;
    list.setAttribute('role', 'tablist');
    const activate = (active, focus) => {
      entries.forEach(e => {
        const on = e === active;
        e.tab.setAttribute('aria-selected', String(on));
        e.tab.tabIndex = on ? 0 : -1;
        e.panel.hidden = !on;
      });
      if (focus) active.tab.focus();
    };
    entries.forEach((e, i) => {
      e.tab.id = e.tab.id || `mi-tab-${g}-${i}`;
      e.tab.setAttribute('role', 'tab');
      e.tab.setAttribute('aria-controls', e.panel.id);
      e.panel.setAttribute('role', 'tabpanel');
      e.panel.setAttribute('aria-labelledby', e.tab.id);
      e.tab.addEventListener('click', () => activate(e));
      e.tab.addEventListener('keydown', ev => {
        const step = ev.key === 'ArrowRight' ? 1 : ev.key === 'ArrowLeft' ? -1 : 0;
        if (!step) return;
        ev.preventDefault();
        activate(entries[(i + step + entries.length) % entries.length], true);
      });
    });
    activate(entries.find(e => e.tab.getAttribute('aria-selected') === 'true') || entries[0]);
  });

  // Copy buttons
  document.querySelectorAll('.mi-copy[data-copy]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const src = document.getElementById(btn.dataset.copy);
      if (!src) return;
      const text = src.textContent;
      try {
        await navigator.clipboard.writeText(text);
      } catch {
 const area = Object.assign(document.createElement('textarea'), { value: text });
 area.style.cssText = 'position:fixed;opacity:0';
        document.body.append(area);
        area.select();
 document.execCommand('copy');
        area.remove();
      }
      const old = btn.textContent;
      btn.textContent = t('已复制', 'Copied');
      live.textContent = t('代码已复制', 'Code copied');
      setTimeout(() => { btn.textContent = old; live.textContent = ''; }, 1800);
    });
  });

  // Videos: play only while visible and only without reduced motion
  const videos = [...document.querySelectorAll('video[data-autoplay]')];
  const paused = new WeakSet();
  const tryPlay = v => {
    if (reduce.matches || paused.has(v)) return;
    if (v.preload === 'none') v.preload = 'auto';
    const p = v.play();
    if (p && p.catch) p.catch(() => {});
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => (e.isIntersecting ? tryPlay(e.target) : e.target.pause()));
    }, { threshold: 0.25 });
    videos.forEach(v => io.observe(v));
  }
  reduce.addEventListener('change', () => videos.forEach(v => (reduce.matches ? v.pause() : tryPlay(v))));

  const toggle = document.querySelector('[data-video-toggle]');
  const hero = document.querySelector('.mi-banner video');
  if (toggle && hero) {
    toggle.hidden = false;
    const label = () => { toggle.textContent = hero.paused ? t('播放动画', 'Play animation') : t('暂停动画', 'Pause animation'); };
    hero.addEventListener('play', label);
    hero.addEventListener('pause', label);
    label();
    toggle.addEventListener('click', () => {
      if (hero.paused) { paused.delete(hero); if (hero.preload === 'none') hero.preload = 'auto'; hero.play().catch(() => {}); }
      else { paused.add(hero); hero.pause(); }
    });
  }

  // Reveal on scroll
  if (!reduce.matches && 'IntersectionObserver' in window) {
    const targets = document.querySelectorAll('.mi-head, .mi-model, .mi-card, .mi-adv, .mi-show, .mi-cost, .mi-ent, .mi-figure, .trust-list li, .pay-row');
    const ro = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); ro.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach(el => { el.classList.add('mi-reveal'); ro.observe(el); });
  }
})();
