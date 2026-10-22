// Suno 专题页交互：导航吸顶、滚动渐显、提示词打字机、横向卡片翻页、代码复制
(function () {
  var doc = document.documentElement;
  doc.classList.remove('no-js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var nav = document.querySelector('.s-nav');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('is-scrolled', window.scrollY > 24); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  var items = document.querySelectorAll('.s-reveal');
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

  // 打字机：提示词来自 data-prompts（JSON 数组），首条已静态写在 HTML 里，保证无 JS 时也可读
  var tw = document.querySelector('[data-prompts]');
  if (tw && !reduce) {
    var list = [];
    try { list = JSON.parse(tw.getAttribute('data-prompts')); } catch (err) { list = []; }
    var out = tw.querySelector('.s-tw');
    if (out && list.length > 1) {
      var i = 0, pos = list[0].length, deleting = true;
      var tick = function () {
        if (deleting) {
          pos--;
          if (pos <= 0) { deleting = false; i = (i + 1) % list.length; }
        } else {
          pos++;
          if (pos >= list[i].length) { deleting = true; out.textContent = list[i]; return setTimeout(tick, 2200); }
        }
        out.textContent = list[i].slice(0, Math.max(pos, 0));
        setTimeout(tick, deleting ? 28 : 62);
      };
      setTimeout(tick, 2600);
    }
  }

  document.querySelectorAll('[data-rail]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var rail = document.getElementById(btn.getAttribute('aria-controls'));
      if (!rail) return;
      var dir = btn.getAttribute('data-rail') === 'next' ? 1 : -1;
      rail.scrollBy({ left: dir * Math.min(rail.clientWidth * 0.8, 820), behavior: reduce ? 'auto' : 'smooth' });
    });
  });

  document.querySelectorAll('.s-copy').forEach(function (btn) {
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
