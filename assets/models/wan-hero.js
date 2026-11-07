(() => {
  const video = document.querySelector('.wan-hero-video');
  const toggle = document.querySelector('.wan-hero-toggle');
  if (!video || !toggle) return;
  const label = toggle.querySelector('[data-video-toggle-label]');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const nav = document.querySelector('.q-nav');

  // Set both properties for browsers that defer muted autoplay until script runs.
  video.defaultMuted = true;
  video.muted = true;
  const syncButton = () => {
    label.textContent = video.paused ? toggle.dataset.playLabel : toggle.dataset.pauseLabel;
  };
  const play = () => {
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
    video.autoplay = !motion.matches;
    video.classList.remove('is-user-playing');
    if (motion.matches) video.pause();
    else play();
    syncButton();
  };
  applyMotionPreference();
  motion.addEventListener('change', applyMotionPreference);
  const syncNav = () => nav?.classList.toggle('is-scrolled', window.scrollY > 24);
  syncNav();
  window.addEventListener('scroll', syncNav, { passive: true });
})();
