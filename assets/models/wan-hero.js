(() => {
  const video = document.querySelector('.wan-hero-video');
  const toggle = document.querySelector('.wan-hero-toggle');
  if (!video || !toggle) return;
  const source = video.querySelector('source[data-src]');
  const label = toggle.querySelector('[data-video-toggle-label]');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const nav = document.querySelector('.q-nav');

  // Keep the file off the first load: the source lives in data-src until the
  // page has finished loading, and nothing sets autoplay before that.
  video.defaultMuted = true;
  video.muted = true;
  let started = false;
  const attach = () => {
    if (started || !source) return;
    started = true;
    source.src = source.dataset.src;
    video.load();
  };
  const syncButton = () => {
    label.textContent = video.paused ? toggle.dataset.playLabel : toggle.dataset.pauseLabel;
  };
  const play = () => {
    attach();
    video.play().catch(() => {
      video.classList.remove('is-user-playing');
      syncButton();
    });
  };
  toggle.hidden = false;
  video.addEventListener('play', syncButton);
  video.addEventListener('pause', syncButton);
  video.addEventListener('error', () => { toggle.hidden = true; });
  toggle.addEventListener('click', () => {
    if (video.paused) {
      if (motion.matches) video.classList.add('is-user-playing');
      play();
    } else {
      video.pause();
      video.classList.remove('is-user-playing');
    }
  });
  const applyMotionPreference = () => {
    video.classList.remove('is-user-playing');
    if (motion.matches) video.pause();
    else play();
    syncButton();
  };
  // Wait for the full page load so the video never competes with first paint.
  if (document.readyState === 'complete') applyMotionPreference();
  else window.addEventListener('load', applyMotionPreference);
  motion.addEventListener('change', applyMotionPreference);
  const syncNav = () => nav?.classList.toggle('is-scrolled', window.scrollY > 24);
  syncNav();
  window.addEventListener('scroll', syncNav, { passive: true });
})();
