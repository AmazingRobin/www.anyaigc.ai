// ElevenLabs（Eleven）系列专题页共用交互：导航阴影、滚动渐显、代码示例切换、代码复制、首屏示例音频播放器
(function () {
  document.documentElement.classList.remove('no-js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var nav = document.querySelector('.o-nav');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('is-scrolled', window.scrollY > 8); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  var items = document.querySelectorAll('.o-reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-in'); });
  }

  // 代码示例切换：所有面板都写在 HTML 里，无 JS 时全部可见
  document.querySelectorAll('[role="tablist"]').forEach(function (list) {
    var tabs = list.querySelectorAll('[role="tab"]');
    if (!tabs.length) return;
    var select = function (tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
    };
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(tab); });
      tab.addEventListener('keydown', function (e) {
        var n = tabs.length;
        var next = e.key === 'ArrowRight' ? tabs[(i + 1) % n]
          : e.key === 'ArrowLeft' ? tabs[(i - 1 + n) % n]
          : e.key === 'Home' ? tabs[0]
          : e.key === 'End' ? tabs[n - 1] : null;
        if (!next) return;
        e.preventDefault();
        select(next);
        next.focus();
      });
    });
    var initial = list.querySelector('[role="tab"][aria-selected="true"]') || tabs[0];
    select(initial);
  });

  // 首屏播放器：播放 ElevenLabs 官网的 v4 示例音频（不是实时调用），波形随播放进度着色
  document.querySelectorAll('.el-player').forEach(function (box) {
    var btn = box.querySelector('.el-play');
    var bars = box.querySelectorAll('.el-wave i');
    var audio = null;
    var label = function (playing) {
      var t = box.getAttribute(playing ? 'data-pause' : 'data-play');
      btn.setAttribute('aria-label', t);
      btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
    };
    var paint = function () {
      var r = audio && audio.duration ? audio.currentTime / audio.duration : 0;
      var n = Math.round(r * bars.length);
      bars.forEach(function (b, i) { b.classList.toggle('is-on', i < n); });
    };
    btn.addEventListener('click', function () {
      if (!audio) {
        audio = new Audio(box.getAttribute('data-src'));
        audio.preload = 'none';
        audio.addEventListener('timeupdate', paint);
        audio.addEventListener('ended', function () { label(false); paint(); });
        audio.addEventListener('pause', function () { label(false); });
        audio.addEventListener('play', function () { label(true); });
      }
      if (audio.paused) {
        if (audio.ended) audio.currentTime = 0;
        audio.play().catch(function () { label(false); });
      } else {
        audio.pause();
      }
    });
  });

  document.querySelectorAll('.o-copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = document.getElementById(btn.getAttribute('aria-controls'));
      if (!pre || !navigator.clipboard) return;
      var label = btn.textContent;
      navigator.clipboard.writeText(pre.innerText).then(function () {
        btn.textContent = btn.getAttribute('data-done') || 'OK';
        setTimeout(function () { btn.textContent = label; }, 1600);
      });
    });
  });
})();
