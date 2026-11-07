(() => {
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const split = (element) => {
    if (!element || element.dataset.qSplit) return;
    const text = element.textContent;
    const fragment = document.createDocumentFragment();
    let index = 0;
    // Keep English words intact while Chinese characters can wrap individually.
    for (const token of text.match(/[A-Za-z0-9]+(?:[.'’_-][A-Za-z0-9]+)*|\s+|[^\s]/gu) || []) {
      if (/^\s+$/.test(token)) {
        fragment.append(document.createTextNode(token));
        index += token.length;
        continue;
      }
      const word = /^[A-Za-z0-9]/.test(token) ? document.createElement('span') : null;
      if (word) word.className = 'q-feather-word';
      for (const character of token) {
        const part = document.createElement('span');
        part.className = 'q-feather';
        part.style.setProperty('--q-index', index++);
        part.setAttribute('aria-hidden', 'true');
        part.textContent = character;
        (word || fragment).append(part);
      }
      if (word) fragment.append(word);
    }
    element.dataset.qSplit = 'true';
    element.setAttribute('aria-label', text);
    element.replaceChildren(fragment);
  };
  document.querySelectorAll('[data-copy]').forEach((button) => button.addEventListener('click', async () => {
    const code = button.closest('.q-code').querySelector('code').innerText;
    try { await navigator.clipboard.writeText(code); const old = button.textContent; button.textContent = old === 'Copy' ? 'Copied' : '已复制'; setTimeout(() => button.textContent = old, 1200); } catch {}
  }));
  if (motion.matches || typeof IntersectionObserver !== 'function') return;
  const headingSelector = '.q-hero h1, .q-section h2, .q-final h2';
  const copySelector = '.q-hero .q-sub, .q-hero .qm-tagline, .q-section .q-lead, .q-final p';
  // Observe individual headings and small items. Sections and price tables stay visible.
  const itemSelector = '.q-cards article, .q-billing li, .q-code, .q-family li, .q-faq details, .trust-list li, .pay-row, .qm-workflows article, .qm-costs li';
  const targets = document.querySelectorAll(`${headingSelector}, ${copySelector}, ${itemSelector}`);
  let active = true;
  const reveal = (node) => {
    node.querySelectorAll('.q-feather').forEach((part) => part.classList.add('q-in'));
    node.classList.add('q-in');
  };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      reveal(entry.target);
      observer.unobserve(entry.target);
    });
  }, { threshold: 0, rootMargin: '0px 0px -2% 0px' });
  const showAll = () => {
    active = false;
    observer.disconnect();
    targets.forEach(reveal);
    document.documentElement.classList.remove('q-motion-ready');
  };
  try {
    document.querySelectorAll(headingSelector).forEach(split);
    document.querySelectorAll(copySelector).forEach(node => node.classList.add('q-blur-words'));
    document.querySelectorAll(itemSelector).forEach(node => node.classList.add('q-scroll-item'));
    document.documentElement.classList.add('q-motion-ready');
    requestAnimationFrame(() => {
      if (!active) return;
      try { targets.forEach(node => observer.observe(node)); }
      catch { showAll(); }
    });
  } catch { showAll(); }
  motion.addEventListener('change', () => { if (motion.matches) showAll(); });
  // Keyboard focus must not land inside an invisible card or FAQ item.
  document.addEventListener('focusin', (event) => {
    const item = event.target.closest('.q-scroll-item, .q-blur-words');
    if (item) { reveal(item); observer.unobserve(item); }
  });
})();
