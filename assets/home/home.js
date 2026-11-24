/* 首页脚本：示例标签切换、模型自动轮换、复制 Base URL。无依赖。 */
(function () {
  var $ = function (s) { return [].slice.call(document.querySelectorAll(s)); };

  // 示例代码 cURL / Python 切换
  var tabs = $('.tabs [role=tab]'), panes = $('.code');
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (x) { x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
      panes.forEach(function (p) { p.hidden = p.getAttribute('data-p') !== t.getAttribute('data-t'); });
    });
  });

  // 只改 model 一行：点选或自动轮换示例模型
  var chips = $('.chips button'), ms = $('.m'), cur = 0, timer = 0;
  function pick(n) {
    cur = n;
    chips.forEach(function (c, k) { c.setAttribute('aria-pressed', k === n ? 'true' : 'false'); });
    ms.forEach(function (m) { m.textContent = chips[n].getAttribute('data-m'); });
  }
  chips.forEach(function (c, k) {
    c.addEventListener('click', function () { clearInterval(timer); pick(k); });
  });
  if (chips.length && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    timer = setInterval(function () { pick((cur + 1) % chips.length); }, 3200);
  }

  // 复制 Base URL
  $('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(b.getAttribute('data-copy')).then(function () {
        var old = b.textContent;
        b.textContent = b.getAttribute('data-done') || 'Copied';
        setTimeout(function () { b.textContent = old; }, 1600);
      });
    });
  });
})();
