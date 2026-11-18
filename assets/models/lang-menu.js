/* 语言下拉菜单：点击空白处或按 Esc 关闭；同一时间只展开一个（导航和页脚各有一个）。 */
(function () {
  var menus = document.querySelectorAll('details.lang-menu');
  if (!menus.length) return;
  menus.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      menus.forEach(function (o) { if (o !== d) o.removeAttribute('open'); });
    });
  });
  document.addEventListener('click', function (e) {
    menus.forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    menus.forEach(function (d) {
      if (!d.open) return;
      d.removeAttribute('open');
      var s = d.querySelector('summary');
      if (s) s.focus();
    });
  });
})();
