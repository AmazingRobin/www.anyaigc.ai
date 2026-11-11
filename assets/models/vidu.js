(() => {
  'use strict';
  document.documentElement.classList.add('vd-js');
  const chinese = document.documentElement.lang.toLowerCase().startsWith('zh');
  const label = (zh, en) => chinese ? zh : en;
  const live = document.createElement('span');
  live.className = 'vd-sr';
  live.setAttribute('role', 'status');
  live.setAttribute('aria-live', 'polite');
  document.body.append(live);
  let liveTimer;
  const announce = text => {
    window.clearTimeout(liveTimer);
    live.textContent = text;
    liveTimer = window.setTimeout(() => { live.textContent = ''; }, 3000);
  };

  const nav = document.querySelector('.vd-nav');
  const menu = document.querySelector('.vd-menu');
  if (nav) {
    let scheduled = false;
    const updateNav = () => {
      nav.classList.toggle('is-scrolled', window.scrollY > 24);
      scheduled = false;
    };
    updateNav();
    window.addEventListener('scroll', () => {
      if (!scheduled) {
        scheduled = true;
        window.requestAnimationFrame(updateNav);
      }
    }, { passive: true });
  }
  if (nav && menu) {
    const closeMenu = () => {
      menu.setAttribute('aria-expanded', 'false');
      menu.setAttribute('aria-label', label('打开导航菜单', 'Open navigation menu'));
      nav.classList.remove('is-menu-open');
      document.body.classList.remove('vd-menu-open');
    };
    closeMenu();
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(open));
      menu.setAttribute('aria-label', open ? label('关闭导航菜单', 'Close navigation menu') : label('打开导航菜单', 'Open navigation menu'));
      nav.classList.toggle('is-menu-open', open);
      document.body.classList.toggle('vd-menu-open', open);
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
        closeMenu();
        menu.focus();
      }
    });
    const desktop = window.matchMedia('(min-width: 901px)');
    desktop.addEventListener('change', event => { if (event.matches) closeMenu(); });
  }

  document.querySelectorAll('.vd-code-tabs').forEach((tablist, groupIndex) => {
    const tabs = [...tablist.querySelectorAll('button[data-panel]')];
    const entries = tabs.map(tab => ({ tab, panel: document.getElementById(tab.dataset.panel) })).filter(entry => entry.panel);
    if (!entries.length) return;
    tablist.setAttribute('role', 'tablist');
    if (!tablist.hasAttribute('aria-label')) tablist.setAttribute('aria-label', label('代码语言', 'Code language'));
    const activate = active => {
      entries.forEach(entry => {
        const selected = entry === active;
        entry.tab.setAttribute('aria-selected', String(selected));
        entry.tab.tabIndex = selected ? 0 : -1;
        entry.tab.classList.toggle('is-active', selected);
        entry.panel.hidden = !selected;
      });
    };
    entries.forEach((entry, index) => {
      const { tab, panel } = entry;
      if (!tab.id) tab.id = `vd-tab-${groupIndex}-${index}`;
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-controls', panel.id);
      panel.setAttribute('role', 'tabpanel');
      panel.setAttribute('aria-labelledby', tab.id);
      panel.tabIndex = 0;
      tab.addEventListener('click', () => activate(entry));
      tab.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (index + 1) % entries.length;
        else if (event.key === 'ArrowLeft') next = (index - 1 + entries.length) % entries.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = entries.length - 1;
        if (next === undefined) return;
        event.preventDefault();
        activate(entries[next]);
        entries[next].tab.focus();
      });
    });
    activate(entries.find(entry => entry.tab.getAttribute('aria-selected') === 'true') || entries[0]);
  });

  const copyFallback = text => {
    const active = document.activeElement;
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.setAttribute('aria-hidden', 'true');
    area.style.cssText = 'position:fixed;left:-10000px;top:0;opacity:0;';
    document.body.append(area);
    area.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } finally {
      area.remove();
      if (active instanceof HTMLElement) active.focus({ preventScroll: true });
    }
    if (!copied) throw new Error('Copy unavailable');
  };
  document.querySelectorAll('.vd-copy[data-copy]').forEach(button => {
    const initial = button.textContent;
    let timer;
    button.addEventListener('click', async () => {
      const code = document.getElementById(button.dataset.copy);
      if (!code) return;
      try {
        const text = code.textContent;
        try {
          if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
          await navigator.clipboard.writeText(text);
        } catch {
          copyFallback(text);
        }
        button.textContent = label('已复制', 'Copied');
        announce(label('代码已复制到剪贴板', 'Code copied to clipboard'));
      } catch {
        button.textContent = label('请选择代码', 'Select code');
        announce(label('无法访问剪贴板，请选择代码复制', 'Clipboard unavailable. Select the code to copy it.'));
      }
      window.clearTimeout(timer);
      timer = window.setTimeout(() => { button.textContent = initial; }, 2200);
    });
  });

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('video.vd-hero-bg, video.vd-clip').forEach(video => {
    const section = video.closest('.vd-hero');
    const button = section?.querySelector('[data-video-toggle]');
    let manuallyPaused = false;
    let inView = true;
    let optedIntoMotion = false;
    const updateButton = () => {
      if (!button) return;
      const playing = !video.paused;
      const text = playing ? label('暂停背景', 'Pause motion') : label('播放背景', 'Play motion');
      button.textContent = text;
      button.setAttribute('aria-label', text);
      button.setAttribute('aria-pressed', String(playing));
    };
    const canPlay = () => !manuallyPaused && (!reduced.matches || optedIntoMotion) && inView && !document.hidden;
    const syncPlayback = () => {
      if (canPlay()) {
        const playing = video.play();
        if (playing) playing.catch(updateButton);
      } else video.pause();
      updateButton();
    };
    video.addEventListener('play', updateButton);
    video.addEventListener('pause', updateButton);
    if (button) {
      button.hidden = false;
      button.addEventListener('click', () => {
        if (video.paused) {
          manuallyPaused = false;
          optedIntoMotion = true;
        } else manuallyPaused = true;
        syncPlayback();
      });
    }
    reduced.addEventListener('change', () => {
      optedIntoMotion = false;
      syncPlayback();
    });
    document.addEventListener('visibilitychange', syncPlayback);
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        inView = entries[0].isIntersecting;
        syncPlayback();
      }, { threshold: 0 });
      observer.observe(video);
    }
    syncPlayback();
  });
})();
