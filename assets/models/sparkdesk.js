// SparkDesk 系列专题页共用交互（与 glm.js 相同）：导航阴影、滚动渐显、代码示例切换、代码复制
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

  // 首屏输入框：点发送后先显示「思考」，再逐字播放写好的示例回答（不是实时调用，页面上已标注）
  var ask = document.querySelector('.sp-ask');
  var send = ask && ask.querySelector('.sp-send');
  var out = ask && ask.querySelector('.sp-out');
  if (send && out) {
    var body = out.querySelector('.sp-out-text');
    var qCaret = ask.querySelector('.sp-ask-q .sp-caret');
    var chars = Array.from(out.getAttribute('data-text') || '');
    var timer = null;
    var busy = false;
    var finish = function () {
      clearInterval(timer);
      busy = false;
      out.setAttribute('aria-busy', 'false');
      send.setAttribute('aria-disabled', 'false');
      var c = body.querySelector('.sp-caret');
      if (c) c.remove();
    };
    send.addEventListener('click', function () {
      if (busy || !chars.length) return;
      if (qCaret) qCaret.style.display = 'none';
      out.hidden = false;
      out.classList.remove('is-on');
      void out.offsetWidth;
      out.classList.add('is-on');
      body.textContent = '';
      if (reduce) { body.textContent = chars.join(''); return; }
      busy = true;
      out.setAttribute('aria-busy', 'true');
      send.setAttribute('aria-disabled', 'true');
      out.classList.add('is-think');
      setTimeout(function () {
        out.classList.remove('is-think');
        var text = document.createTextNode('');
        var cursor = document.createElement('span');
        cursor.className = 'sp-caret';
        cursor.setAttribute('aria-hidden', 'true');
        body.appendChild(text);
        body.appendChild(cursor);
        var i = 0;
        timer = setInterval(function () {
          i = Math.min(i + 2, chars.length);
          text.nodeValue = chars.slice(0, i).join('');
          if (i >= chars.length) finish();
        }, 32);
      }, 650);
    });
  }

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
