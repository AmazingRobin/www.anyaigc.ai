(() => {
  const menu = document.querySelector('.ll-menu');
  const links = document.querySelector('.ll-links');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    links.dataset.open = String(open);
  });
  links?.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      menu.setAttribute('aria-expanded', 'false');
      links.dataset.open = 'false';
    }
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
      menu.setAttribute('aria-expanded', 'false');
      links.dataset.open = 'false';
      menu.focus();
    }
  });
  const tabs = [...document.querySelectorAll('.ll-tabs [role="tab"]')];
  function activate(tab) {
    tabs.forEach(button => {
      const active = button === tab;
      button.setAttribute('aria-selected', String(active));
      button.tabIndex = active ? 0 : -1;
      document.getElementById(button.getAttribute('aria-controls')).hidden = !active;
    });
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'ArrowLeft') next = tabs[(index - 1 + tabs.length) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (next) { event.preventDefault(); activate(next); next.focus(); }
    });
  });
  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const original = button.textContent;
      const zh = document.documentElement.lang === 'zh-CN';
      try {
        await navigator.clipboard.writeText(document.getElementById(button.dataset.copy).textContent);
        button.textContent = zh ? '已复制' : 'Copied';
      } catch {
        button.textContent = zh ? '请选择代码复制' : 'Select code to copy';
      }
      setTimeout(() => { button.textContent = original; }, 2200);
    });
  });
})();
