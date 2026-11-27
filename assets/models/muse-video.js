// Muse Video 首屏背景视频：静音循环自动播放；系统开启「减少动态效果」时只显示封面；滑出首屏后暂停以省电。
(function () {
  var v = document.querySelector('.mv-hero-video video');
  if (!v) return;
  v.muted = true;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) {
    v.removeAttribute('autoplay');
    v.pause();
    return;
  }
  function play() {
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) play(); else v.pause();
      });
    }).observe(v);
  } else {
    play();
  }
})();
