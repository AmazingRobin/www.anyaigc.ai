// GPT 系列专题页的宇宙动效（canvas 绘制，不使用 OpenAI 的图片素材）
//  - 首屏 .g-hero-art[data-art]：中心天体 + 绕行的粒子星流，缓慢流动
//  - 价格三联卡片 .g-tier-art.g-art-<tier>：每个档位一种天体（星系 / 太阳 / 月牙 / 地球 / 光环 / 星环）
//  prefers-reduced-motion 时只画静态一帧；不在视口内时暂停动画
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DPR = Math.min(window.devicePixelRatio || 1, 2);
  var STAR_COLORS = ['255,255,255', '214,228,255', '186,214,255', '255,214,170', '255,170,110'];

  function rng(seed) { // 固定种子，每次刷新画面一致
    var s = seed >>> 0;
    return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  }

  function setup(canvas) {
    var rect = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(rect.width)), h = Math.max(1, Math.round(rect.height));
    canvas.width = w * DPR; canvas.height = h * DPR;
    var ctx = canvas.getContext('2d');
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    return { ctx: ctx, w: w, h: h };
  }

  function glowDot(ctx, x, y, r, rgb, a) {
    if (r > 1.2) {
      var g = ctx.createRadialGradient(x, y, 0, x, y, r * 3.2);
      g.addColorStop(0, 'rgba(' + rgb + ',' + a + ')');
      g.addColorStop(0.35, 'rgba(' + rgb + ',' + (a * 0.35) + ')');
      g.addColorStop(1, 'rgba(' + rgb + ',0)');
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(x, y, r * 3.2, 0, Math.PI * 2); ctx.fill();
    }
    ctx.fillStyle = 'rgba(' + rgb + ',' + a + ')';
    ctx.beginPath(); ctx.arc(x, y, Math.max(r, 0.4), 0, Math.PI * 2); ctx.fill();
  }

  function sparkle(ctx, x, y, len, a) { // 四芒星
    ctx.save();
    ctx.globalAlpha = a;
    var g = ctx.createLinearGradient(x - len, y, x + len, y);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.fillRect(x - len, y - 0.6, len * 2, 1.2);
    g = ctx.createLinearGradient(x, y - len, x, y + len);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.fillRect(x - 0.6, y - len, 1.2, len * 2);
    ctx.restore();
    glowDot(ctx, x, y, 1.6, '255,255,255', 1);
  }

  function background(ctx, w, h, cx, cy) {
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h);
    var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.75);
    g.addColorStop(0, 'rgba(13,26,34,1)'); g.addColorStop(0.45, 'rgba(7,16,22,1)'); g.addColorStop(1, 'rgba(0,0,0,1)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  }

  function fieldStars(rand, n, w, h) {
    var a = [];
    for (var i = 0; i < n; i++) a.push({ x: rand() * w, y: rand() * h, r: rand() < 0.92 ? rand() * 0.8 + 0.2 : rand() * 1.4 + 0.8, c: STAR_COLORS[(rand() * 3) | 0], tw: rand() * Math.PI * 2 });
    return a;
  }

  // ---------- 中心天体 ----------
  function drawSun(ctx, x, y, R, t) {
    var pulse = 1 + Math.sin(t * 0.0012) * 0.015;
    var halo = ctx.createRadialGradient(x, y, R * 0.92, x, y, R * 1.7 * pulse);
    halo.addColorStop(0, 'rgba(255,190,80,0.75)'); halo.addColorStop(0.25, 'rgba(255,150,40,0.25)'); halo.addColorStop(1, 'rgba(255,150,40,0)');
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(x, y, R * 1.7 * pulse, 0, Math.PI * 2); ctx.fill();
    var wide = ctx.createRadialGradient(x, y, R, x, y, R * 4.2);
    wide.addColorStop(0, 'rgba(40,70,90,0.22)'); wide.addColorStop(1, 'rgba(40,70,90,0)');
    ctx.fillStyle = wide; ctx.beginPath(); ctx.arc(x, y, R * 4.2, 0, Math.PI * 2); ctx.fill();
    var body = ctx.createRadialGradient(x - R * 0.2, y - R * 0.2, R * 0.1, x, y, R);
    body.addColorStop(0, '#fffbe9'); body.addColorStop(0.7, '#fbeec0'); body.addColorStop(0.93, '#f6cf6a'); body.addColorStop(1, '#e89a2c');
    ctx.fillStyle = body; ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2); ctx.fill();
  }

  function drawMoon(ctx, x, y, R) {
    // 月牙：在离屏画布上用亮面减去偏移圆，避免把背景一起挖空
    var halo = ctx.createRadialGradient(x, y, R * 0.6, x, y, R * 2.4);
    halo.addColorStop(0, 'rgba(190,210,235,0.18)'); halo.addColorStop(1, 'rgba(190,210,235,0)');
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(x, y, R * 2.4, 0, Math.PI * 2); ctx.fill();
    var size = Math.ceil(R * 2 + 4);
    var off = drawMoon.cache && drawMoon.cache.size === size ? drawMoon.cache.c : null;
    if (!off) {
      off = document.createElement('canvas'); off.width = size * DPR; off.height = size * DPR;
      var o = off.getContext('2d'); o.setTransform(DPR, 0, 0, DPR, 0, 0);
      var c = size / 2;
      var lit = o.createLinearGradient(c - R, c, c + R, c);
      lit.addColorStop(0, '#ffffff'); lit.addColorStop(0.35, '#e6edf8'); lit.addColorStop(1, '#9fb0c8');
      o.fillStyle = lit; o.beginPath(); o.arc(c, c, R, 0, Math.PI * 2); o.fill();
      o.globalCompositeOperation = 'destination-out';
      o.beginPath(); o.arc(c + R * 0.5, c - R * 0.18, R * 0.95, 0, Math.PI * 2); o.fill();
      drawMoon.cache = { size: size, c: off };
    }
    ctx.drawImage(off, x - size / 2, y - size / 2, size, size);
  }

  // Terra：真实大陆轮廓（Natural Earth 1:110m 陆地数据，公有领域）+ 云层贴到球面上，按光照着色，慢速自转
  // LAND：512×256 等距圆柱投影的陆地掩码，逐行游程编码（36 进制，从海洋开始交替，行之间用逗号）
  var LAND = 'e8,e8,e8,e8,e8,e8,e8,e8,e8,5j.l.84,3q.2.2.v.k.11.7y,3h.14.3.c.1.13.1.4.7z,3d.4.2.z.3.1m.1.e.49.2.3b,3b.a.9.j.3.21.1e.3.1.4.v.7.1l.b.37,3b.10.7.1x.15.4.1.5.2.a.2m.b.35,2y.4.c.b.1.f.a.1y.16.f.2w.e.30,2y.8.1.6.2.q.2.25.19.a.4.2.31.8.2y,2m.6.j.4.7.f.9.23.1b.6.3.5.36.1.2z,2c.7.r.4.7.h.8.24.1b.4.3b.8.2w,29.6.3.5.4.4.7.7.5.5.c.4.e.1y.38.b.15.m.2n,2h.a.1.6.4.1.1.5.3.2.1.8.3.8.u.1k.32.9.11.z.w.c.1d,2n.7.g.5.1.j.u.1j.2z.7.11.11.10.a.3.5.16,26.b.2e.1f.2z.6.13.y.2s,27.d.b.5.3.7.1.8.3.4.2.4.1.5.u.1f.2x.6.w.1b.1.8.5.6.i.6.1f,26.j.2.2.1.5.3.8.1.5.4.g.x.1b.2y.6.i.6.2.2.6.1y.f.3.1i,25.u.5.7.1.3.4.e.1.8.r.1a.2y.6.i.7.2.2.1.22.f.f.17,0.3.25.5.2.l.6.3.2.5.4.q.p.14.1.5.2x.6.f.8.1.29.2.8.1.j.14.1,s.c.1c.m.8.8.3.s.l.16.1.5.1r.b.z.3.c.a.1.3e.t,o.u.f.3.1.3.2.2.9.o.2.3.1.7.9.p.i.1a.1o.g.1f.9.1.3f.e.3.b,n.11.2.p.3.l.3.6.1.7.1.1.4.7.6.e.m.12.1o.o.11.7.3.40.2.d.1,0.2.h.25.5.6.9.2.3.6.1.3.3.7.8.a.m.10.1q.w.6.2.b.3.4.f.2.7.1.46,0.5.g.20.5.2.2.9.4.4.1.b.2.7.6.4.2.c.g.u.1v.11.4.5.3.z.1.46,0.8.f.3a.5.3.3.e.d.u.1u.14.3.3.3.10.1.47,0.d.8.3.1.35.d.h.b.s.p.4.12.u.2.8.1.2.1.14.1.49,0.e.3.39.g.a.2.5.d.m.j.5.1.9.11.f.3.f.7.5j,0.1.4.6.7.3c.6.h.3.2.f.i.o.e.z.f.4.f.2.2.3.5j,8.3.f.2x.2.7.5.4.2.d.h.i.p.b.z.h.2.i.1.5l.3,b.1.1.1.c.2u.4.1.1.3.1.4.b.5.1.5.i.g.t.4.11.h.2.68.1,l.2y.r.a.j.d.1x.h.4.6a,k.2w.c.3.3.a.7.3.n.b.1v.i.5.5m.1.i.5,j.2w.m.a.u.b.1v.i.5.5e.2.5.2.e.9,k.2u.n.d.w.5.1w.j.4.5c.5.2.2.e.b,i.3.1.o.4.20.n.d.5.2.r.3.1w.k.5.4.5.50.8.6.1.3.2.2.d,p.d.2.2.f.1t.n.d.4.4.2p.7.1.b.8.4z.2.5.8.5.n,p.2.1.2.1.7.l.1t.k.f.2.6.2p.5.2.9.9.4p.o.6.o,v.6.s.1n.m.m.28.3.l.8.a.4m.o.7.p,u.4.2.3.q.1o.l.n.26.7.f.b.6.3.1.4l.n.b.n,s.4.z.1s.g.m.26.6.e.4.2.7.5.4o.o.b.o,p.6.11.1t.d.o.26.6.d.4.1.5.8.4m.q.a.p,n.3.17.1y.5.s.24.6.d.3.2.2.c.4k.r.a.p,l.2.1b.1x.3.x.1w.5.3.5.c.3.8.4.1.4n.q.8.r,1u.3.2.1w.4.x.1u.6.3.5.c.8.1.4v.1.3.2.2.h.7.s,1v.2.3.1w.3.y.1t.6.1.8.5.5f.1.2.h.6.t,1w.2.3.1w.3.x.1t.5.2.a.3.5f.1.2.i.4.u,21.1x.1.x.1v.1.4.a.3.5j.i.3.v,22.2r.1.3.20.5r.2.3.1f,21.4.1.2d.2.6.3.2.20.3.6.5j.2.3.1f,23.2e.4.3.5.4.24.1.1.5l.2.4.1e,25.3.1.26.1.5.7.8.1z.1.1.5n.1.3.1g,26.2e.8.9.1w.5q.2.2.1h,27.2.1.22.1.7.c.6.1y.5m.3.3.1g,27.2f.3.1.9.2.20.1k.1.i.3.3e.4.4.1f,27.2e.1.5.2b.1a.3.3.4.g.5.3e.5.1.1h,27.2j.2c.k.1.o.3.m.5.3e.6.2.1h,27.2a.1.4.2g.k.3.k.6.3.3.e.5.3e.7.3.1g,27.27.3.3.2h.f.2.5.3.j.e.d.4.3d.8.6.1d,27.25.2f.j.2.2.4.6.3.h.h.b.4.38.1.3.7.8.1d,27.25.2f.i.7.2.1.6.5.e.j.a.5.35.b.3.1.3.1f,27.26.2e.i.7.2.2.7.4.d.6.5.8.b.4.33.d.3.1j,27.21.2j.g.9.2.5.6.2.e.1.c.3.d.7.30.e.3.1i,27.20.2k.e.a.3.7.5.1.5.1.2.2.z.3.2p.1.b.e.4.1i,27.20.2k.d.b.3.8.2.4.5.4.y.4.2n.2.4.1.5.h.3.1i,28.1v.1.2.2k.e.c.1.9.3.4.4.5.w.6.2k.4.1.5.4.g.4.1i,28.1v.1.2.2l.d.m.2.6.4.3.x.6.2k.9.6.f.3.1j,29.1w.2m.c.i.5.8.4.4.w.6.2m.1.2.6.5.d.4.1j,2a.1u.2n.2.1.8.a.8.4.2.8.3.6.y.3.2r.5.5.9.1.1.5.1j,2a.1v.2q.2.7.g.q.1.3.3.1.3e.7.6.8.8.1j,2b.1u.2q.3.3.j.h.2.d.1.2.3c.8.6.4.b.1k,2c.1s.2q.q.u.2.3.3b.9.4.4.c.1l,2e.1o.2s.p.z.3e.d.4.1.5.1p,2g.1k.2s.s.y.3e.c.8.1s,2h.1i.2r.y.9.4.g.3g.b.4.1w,2h.1g.2t.10.6.7.e.3h.b.3.1w,2i.3.1.1b.2t.11.5.c.2.4.2.3i.b.2.1x,2i.3.2.1a.2t.57.2b,2j.3.1.y.5.2.1.4.2t.2b.2.2v.2a,2k.3.1.p.5.3.8.4.2s.1p.1.2.1.j.3.2u.2a,2l.3.1.n.i.4.2p.1u.1.j.3.2u.2a,2k.4.2.k.k.4.2n.1w.1.k.3.2r.2c,2l.4.2.j.k.5.2l.1w.3.k.4.2p.2c,2n.3.2.i.l.4.2.2.2g.1y.2.l.8.2j.2d,2o.2.2.i.m.2.2k.1z.3.m.5.2.1.2g.2e,2o.3.3.g.q.2.2g.20.2.k.1.1.4.3.e.23.2.2.2a,2p.3.3.f.r.1.2f.22.2.k.4.4.e.22.2.3.2a,2q.3.3.d.38.22.3.u.d.1y.3.3.2b,2r.1.5.c.k.6.2h.23.4.u.d.1v.5.3.2b,s.2.23.c.i.2.3.6.2e.25.2.u.d.v.1.w.9.1.2c,v.1.22.c.b.4.b.3.2c.26.2.u.e.p.6.o.1.4.2p,x.2.1y.d.9.6.b.5.2b.25.3.s.j.l.7.l.4.2.2q,y.2.1x.e.8.5.d.6.29.25.4.q.k.k.9.j.5.2.2q,y.2.1y.e.6.6.k.5.23.25.5.p.k.i.c.i.3.4.2q,30.d.3.8.i.1.2.6.21.26.4.n.m.h.d.i.3.3.2r,32.l.e.3.6.1.26.26.4.m.m.g.f.i.j.3.2a,34.j.2t.28.4.j.p.e.g.j.i.4.29,37.g.2t.28.4.g.s.d.h.k.h.3.2a,3a.2.2.8.3.4.2n.29.3.f.t.b.j.2.2.h.f.4.2a,3f.f.2l.2b.2.d.w.9.p.g.f.3.2b,3h.d.2l.2c.2.9.z.9.p.h.g.2.2a,3j.b.2m.2c.1.7.12.9.o.h.g.5.27,3o.6.2m.2h.15.9.p.g.f.2.2.2.27,3o.6.f.2.25.2e.18.8.q.3.2.b.g.1.4.2.25,3p.4.f.3.1.1.24.2d.8.3.y.7.q.2.4.a.h.2.2.2.25,3p.5.b.5.1.4.23.2d.3.7.y.7.q.2.4.8.f.2.2.5.26,3p.5.a.f.1.6.1t.2m.z.5.r.2.6.5.g.1.4.4.26,3s.3.3.2.4.m.1u.2l.z.7.o.3.7.3.g.1.5.2.2.2.24,3t.3.1.2.1.q.1v.2j.11.3.1.3.n.4.6.1.h.1.9.3.24,3u.4.2.s.1t.2j.12.1.2.3.n.4.v.6.24,3w.2.2.t.1t.2h.16.4.o.2.u.2.1.4.24,41.t.1t.2g.16.4.p.3.k.2.9.4.24,42.t.1.3.1q.h.4.1s.18.1.r.4.j.3.9.2.25,41.11.1o.e.7.1r.1t.4.3.5.g.7.2e,42.11.1o.4.h.1p.1v.4.3.5.e.7.2f,42.12.2c.1k.1x.4.2.5.d.7.2g,41.13.2d.1i.1z.4.2.4.c.7.2h,40.14.2d.1h.20.5.1.4.a.a.2g,40.15.2c.1g.23.9.6.d.d.2.21,3z.16.2c.1e.25.7.8.e.2.2.3.2.3.3.20,3y.17.2c.1d.27.7.6.e.2.2.3.2.4.1.22,3x.1a.29.1d.28.7.7.d.2.1.a.2.21,3w.1f.25.1c.2a.6.7.c.2.7.9.6.1t,3x.1g.24.1a.2c.6.7.a.3.5.d.4.4.2.1n,3x.1i.22.19.2d.8.5.a.3.5.f.3.1.7.1k,3y.1m.1y.18.2e.7.8.7.3.2.1.3.4.2.1.4.2.4.1.a.c.2.13,3w.1q.1x.16.2g.6.c.3.4.5.d.i.a.2.12,3w.1r.1x.14.2i.5.j.4.1.1.h.e.8.3.12,3w.1u.1v.13.2k.3.i.3.1.3.j.d.5.4.2.2.z,3w.1v.1u.13.2m.3.11.2.4.e.1.4.5.1.z,3x.1u.1u.13.2m.5.2.2.v.2.4.e.a.3.x,3y.1t.1v.12.2n.a.10.d.d.1.1.1.u,3z.1s.1v.12.2t.7.v.a.2.4.f.2.s,3z.1s.1v.12.32.3.1.4.3.4.j.4.4.4.g.2.q,40.1q.1w.13.34.2.5.2.v.4.e.3.q,40.1p.1x.14.34.2.3.2.x.5.15,41.1n.1z.13.40.1.1h,41.1m.20.13.3m.2.b.3.1g,42.1l.20.13.b.2.37.9.6.3.1g,43.1j.20.14.b.2.36.a.6.4.1f,43.1i.20.15.b.3.34.a.7.4.1f,43.1i.20.15.a.4.2y.4.2.9.8.5.1e,44.1h.20.15.8.6.2x.g.8.6.u.1.i,46.1f.1z.16.7.7.2w.j.6.6.1d,0.1.47.1d.1z.15.6.8.2v.1.1.l.3.8.u.1.f.2,49.1c.1z.13.7.9.2u.2.1.m.2.8.1c,4a.1b.1z.11.9.9.2u.z.18.3.1,4b.19.21.z.a.8.2v.z.1c,4c.18.22.x.c.7.2u.12.1a,4c.17.23.w.d.7.2r.16.19,4c.17.23.w.c.7.2o.2.1.18.l.3.k,4c.16.25.w.a.8.2n.1d.l.3.j,4c.16.26.v.a.8.2m.1f.m.2.i,4c.15.27.v.a.7.2l.1i.15,4b.12.2b.v.b.6.2l.1i.15,4b.z.2e.v.b.6.2l.1j.14,4b.y.2f.t.d.5.2m.1k.13,4b.x.2h.q.36.1l.12,4b.w.2i.q.37.1k.12,4b.x.2h.q.36.1l.12,4b.w.2j.p.37.1l.11,4a.x.2k.o.37.1l.11,4a.w.2l.m.3a.1k.11,4a.v.2n.k.3b.1j.12,4a.v.2n.k.3b.1j.12,4a.u.2p.i.3d.1i.12,4a.t.2q.h.3e.j.5.u.12,4a.s.2r.g.3f.f.b.r.13,4a.r.2s.e.3h.d.e.p.14,49.r.2v.5.3n.8.l.2.1.k.15,49.l.1.4.2w.2.3s.4.o.1.1.1.1.i.u.2.9,48.n.7p.i.w.3.7,48.n.7r.g.x.2.7,48.o.7q.g.y.1.1.1.5,47.o.7s.e.z.3.2.1.2,47.n.7v.9.12.6.2,47.h.88.1.12.7.2,47.h.9c.4.4,47.h.9d.3.4,46.e.1.1.87.3.1.2.x.2.1.4.5,46.e.8a.5.w.5.8,46.g.88.5.w.4.9,46.e.8b.3.w.4.a,48.c.98.5.b,46.d.97.6.c,45.c.98.7.c,45.c.97.7.d,45.c.9r,45.e.9p,44.f.9p,44.d.5c.2.4d,44.c.5d.4.4b,44.b.9t,45.9.9u,44.b.a.5.9e,45.8.9v,46.1.1.3.1.3.9t,47.4.1.4.9s,49.9.9q,4c.7.9p,e8,e8,e8,e8,e8,e8,e8,e8,e8,e8,e8,4s.3.9d,4o.2.1.2.9f,4l.3.9k,4j.4.6i.3.18.2.1q,4h.6.4h.a.16.2.h.7.7.7.l.9.1q,4f.5.4h.f.11.2.1.4.1.2.2.2.4.2.1.r.3.10.1c,4f.4.4d.n.2.7.j.2m.1b,4f.5.3w.1.b.13.c.2v.16,4a.3.1.9.3r.8.2.18.a.35.x,49.e.2r.2.b.6.d.1k.6.3g.s,49.f.2n.8.1.29.6.3k.p,46.9.1.9.1z.4.1.4.1.2w.4.3x.d,32.6.1.2.u.a.1.9.1y.37.3.3z.c,30.3.1.2.e.2.t.b.1u.7b.d,23.3.3.3.p.8.3.f.6.5.5.j.1r.7d.e,2f.9.f.1m.1t.78.i,1n.16.c.1h.1t.79.k,1b.38.1t.7a.m,1c.31.1q.7i.n,u.2.b.2w.1u.7o.n,v.3c.1m.7t.m,n.4.5.36.14.8.b.81.i,o.6.6.32.12.b.9.7x.n,1a.2t.m.2.b.d.j.7j.r,1b.2y.9.9.8.c.m.7k.r,x.8.1.39.18.7u.r,11.3n.f.b.1.84.p,12.3q.4.8r.l,11.cs.f,b.5.p.cs.b,0.l.v.cs,0.17.4.cx,0.e8,0.e8,0.e8,0.e8,0.e8,0.e8';
  var earthTex = null, earthCache = {};
  function earthTexture() {
    if (earthTex) return earthTex;
    var W = 512, H = 256, G = 64, rand = rng(5602);
    function grid() { var g = new Float32Array(G * G); for (var i = 0; i < g.length; i++) g[i] = rand(); return g; }
    var g1 = grid(), g2 = grid();
    function vn(g, x, y, px) { // 值噪声，经度方向按 px 周期无缝
      var xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
      var sx = xf * xf * (3 - 2 * xf), sy = yf * yf * (3 - 2 * yf);
      function at(i, j) { return g[(((j % G) + G) % G) * G + (((i % px) + px) % px)]; }
      var a = at(xi, yi), b = at(xi + 1, yi), c = at(xi, yi + 1), d = at(xi + 1, yi + 1);
      return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
    }
    function fbm(g, x, y, oct) { var s = 0, amp = 0.5, f = 1, n = 0; for (var o = 0; o < oct; o++) { s += amp * vn(g, x * f, y * f, 4 * f); n += amp; amp *= 0.5; f *= 2; } return s / n; }
    function mix(a, b, k) { return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k]; }
    function blur(src, passes) { // 经度方向循环的 3×3 盒式模糊
      var a = src, b = new Float32Array(W * H);
      for (var p = 0; p < passes; p++) {
        for (var y = 0; y < H; y++) for (var x = 0; x < W; x++) {
          var s = 0;
          for (var dy = -1; dy <= 1; dy++) { var yy = Math.min(H - 1, Math.max(0, y + dy)) * W; s += a[yy + (x + W - 1) % W] + a[yy + x] + a[yy + (x + 1) % W]; }
          b[y * W + x] = s / 9;
        }
        var t = a; a = b; b = (t === src) ? new Float32Array(W * H) : t;
      }
      return a;
    }
    var mask = new Float32Array(W * H);
    LAND.split(',').forEach(function (row, j) {
      var i = 0, v = 0;
      row.split('.').forEach(function (r) { var n = parseInt(r, 36); if (v) for (var k = 0; k < n; k++) mask[j * W + i + k] = 1; i += n; v ^= 1; });
    });
    var coast = blur(mask, 1), near = blur(mask, 6);
    var col = new Uint8ClampedArray(W * H * 3), sea = new Float32Array(W * H), cloud = new Float32Array(W * H);
    var DEEP = [5, 24, 58], OCEAN = [12, 52, 104], SHALLOW = [34, 104, 150], ICE = [226, 234, 242];
    var FOREST = [34, 78, 40], GRASS = [86, 112, 58], DRY = [168, 142, 96], DESERT = [196, 168, 118], TUNDRA = [112, 108, 88];
    for (var j = 0; j < H; j++) {
      var lat = 90 - (j + 0.5) / H * 180, al = Math.abs(lat);
      for (var i = 0; i < W; i++) {
        var k = j * W + i, x = i / W * 4, y = j / H * 2;
        var n = fbm(g1, x * 2, y * 2, 4);
        // 陆地：按纬度带取植被色（赤道雨林、副热带荒漠、温带草地森林、寒带苔原），再加噪声起伏
        var n2 = fbm(g2, x * 3 + 1.7, y * 3, 4), wob = (n2 - 0.5) * 22; // 让干旱带边界不规则
        var dry = Math.max(0, 1 - Math.abs(al + wob - 24) / 11) * Math.max(0, n * 1.6 - 0.35);
        var land = al < 12 ? mix(FOREST, GRASS, n * 0.6) : mix(GRASS, FOREST, Math.max(0, Math.min(1, (al - 40) / 14)) * 0.8);
        land = mix(land, mix(DRY, DESERT, n2), Math.min(0.85, dry));
        if (al > 58) land = mix(land, TUNDRA, Math.min(1, (al - 58) / 8));
        var ice = lat < -62 || al > 74 + n * 6 || (lat > 60 && i > 191 && i < 222) ? 1 : 0; // 南极、高纬、格陵兰
        if (ice) land = ICE;
        // 海洋：近岸浅、远洋深；极地海冰
        var oc = mix(SHALLOW, OCEAN, Math.min(1, (1 - near[k] * 2.2))); oc = mix(oc, DEEP, Math.max(0, 0.6 - near[k] * 3) * (0.6 + n * 0.5));
        if (al > 78) oc = mix(oc, ICE, Math.min(1, (al - 78) / 6));
        var m = Math.max(0, Math.min(1, (coast[k] - 0.5) * 2.4 + 0.5)), c = mix(oc, land, m);
        sea[k] = al > 80 ? 0 : 1 - m;
        col[k * 3] = c[0]; col[k * 3 + 1] = c[1]; col[k * 3 + 2] = c[2];
        var cl = fbm(g2, x, y + 0.37, 5); // 云：少量、偏向中高纬和赤道辐合带
        var band = 0.7 + 0.3 * Math.cos(lat / 90 * Math.PI * 2.2);
        cloud[k] = Math.max(0, Math.min(0.8, (cl * band - 0.5) * 3));
      }
    }
    earthTex = { W: W, H: H, col: col, sea: sea, cloud: cloud };
    return earthTex;
  }
  function earthSphere(D) { // 球面几何只算一次：每个像素对应的经纬度、光照、边缘
    if (earthCache[D]) return earthCache[D];
    var T = earthTexture(), h = D / 2, tilt = 0.38, ct = Math.cos(tilt), st = Math.sin(tilt);
    var L = [-0.62, -0.42, 0.66], ln = Math.hypot(L[0], L[1], L[2]); L = [L[0] / ln, L[1] / ln, L[2] / ln];
    var Hv = [L[0], L[1], L[2] + 1], hn = Math.hypot(Hv[0], Hv[1], Hv[2]); Hv = [Hv[0] / hn, Hv[1] / hn, Hv[2] / hn];
    var pix = [], u = [], v = [], lit = [], spec = [], rim = [], edge = [];
    for (var py = 0; py < D; py++) for (var px = 0; px < D; px++) {
      var nx = (px + 0.5 - h) / h, ny = (py + 0.5 - h) / h, r = Math.hypot(nx, ny);
      if (r > 1 + 1 / h) continue;
      var rr = Math.min(r, 1), nz = Math.sqrt(Math.max(0, 1 - rr * rr));
      if (r > 1) { nx /= r; ny /= r; }
      var tx = nx * ct - ny * st, ty = nx * st + ny * ct; // 自转轴倾斜
      var la = Math.asin(Math.max(-1, Math.min(1, -ty))), lo = Math.atan2(tx, nz);
      var d = nx * L[0] + ny * L[1] + nz * L[2];
      var s = Math.max(0, nx * Hv[0] + ny * Hv[1] + nz * Hv[2]);
      var q = Math.max(0, Math.min(1, (d + 0.12) / 0.7));
      pix.push((py * D + px) * 4); u.push((lo / (Math.PI * 2) + 0.5) * T.W); v.push(Math.min(T.H - 1, Math.floor((0.5 - la / Math.PI) * T.H)));
      lit.push(q * q * (3 - 2 * q)); spec.push(Math.pow(s, 90)); rim.push(Math.pow(1 - nz, 2.2)); edge.push(Math.max(0, Math.min(1, (1 - r) * h + 0.5)));
    }
    var cv = document.createElement('canvas'); cv.width = cv.height = D;
    var cx = cv.getContext('2d');
    earthCache[D] = { cv: cv, cx: cx, img: cx.createImageData(D, D), pix: pix, u: u, v: v, lit: lit, spec: spec, rim: rim, edge: edge };
    return earthCache[D];
  }
  function drawEarth(ctx, x, y, R, t) {
    var T = earthTexture(), D = Math.max(8, Math.round(R * 2 * DPR)), S = earthSphere(D), d = S.img.data, W = T.W;
    var off = W * 64 - (t * 0.004) % (W * 64), coff = W * 64 - (t * 0.0062) % (W * 64); // 自西向东自转
    for (var k = 0; k < S.pix.length; k++) {
      var p = S.pix[k], vv = S.v[k] * W;
      var iu = Math.floor(S.u[k] + off) % W, ti = vv + iu, ci = vv + Math.floor(S.u[k] + coff) % W;
      var ca = T.cloud[ci], l = S.lit[k], sh = 0.035 + l * 0.965;
      var r = T.col[ti * 3], g = T.col[ti * 3 + 1], b = T.col[ti * 3 + 2];
      r += (236 - r) * ca; g += (242 - g) * ca; b += (250 - b) * ca;
      r *= sh; g *= sh; b *= sh;
      var sp = S.spec[k] * T.sea[ti] * (1 - ca) * (1 - ca) * 90; r += sp; g += sp; b += sp;
      var a = S.rim[k] * (0.25 + l * 0.9); // 大气层边缘的蓝色散射
      r += (110 - r) * a * 0.85; g += (175 - g) * a * 0.85; b += (255 - b) * a * 0.85;
      d[p] = r; d[p + 1] = g; d[p + 2] = b; d[p + 3] = S.edge[k] * 255;
    }
    S.cx.putImageData(S.img, 0, 0);
    // 外层大气光晕（偏向受光一侧）
    var halo = ctx.createRadialGradient(x - R * 0.08, y - R * 0.06, R * 0.96, x, y, R * 1.38);
    halo.addColorStop(0, 'rgba(120,185,255,0.42)'); halo.addColorStop(0.35, 'rgba(90,150,255,0.14)'); halo.addColorStop(1, 'rgba(90,150,255,0)');
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(x, y, R * 1.4, 0, Math.PI * 2); ctx.fill();
    ctx.drawImage(S.cv, x - R, y - R, R * 2, R * 2);
  }

  function drawRing(ctx, x, y, R, t) { // Pro：发光光环
    var rot = t * 0.00015;
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
    for (var i = 0; i < 3; i++) {
      ctx.strokeStyle = 'rgba(255,248,225,' + (0.75 - i * 0.22) + ')';
      ctx.lineWidth = 2.4 - i * 0.6;
      ctx.shadowColor = 'rgba(255,220,150,0.9)'; ctx.shadowBlur = 18;
      ctx.beginPath(); ctx.ellipse(0, 0, R * (1 + i * 0.22), R * (1 + i * 0.22) * 0.98, 0, 0, Math.PI * 2); ctx.stroke();
    }
    ctx.restore();
    var core = ctx.createRadialGradient(x, y, 0, x, y, R * 0.75);
    core.addColorStop(0, 'rgba(255,253,243,0.35)'); core.addColorStop(1, 'rgba(255,253,243,0)');
    ctx.fillStyle = core; ctx.beginPath(); ctx.arc(x, y, R * 0.75, 0, Math.PI * 2); ctx.fill();
  }

  function drawPlanet(ctx, x, y, R) { // flagship：带环行星
    ctx.save();
    ctx.strokeStyle = 'rgba(214,224,240,0.55)'; ctx.lineWidth = R * 0.12;
    ctx.beginPath(); ctx.ellipse(x, y, R * 1.9, R * 0.5, -0.32, Math.PI, Math.PI * 2); ctx.stroke();
    var body = ctx.createRadialGradient(x - R * 0.3, y - R * 0.3, R * 0.1, x, y, R);
    body.addColorStop(0, '#f2f4fa'); body.addColorStop(0.6, '#aab6cc'); body.addColorStop(1, '#3b4660');
    ctx.fillStyle = body; ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x, y, R * 1.9, R * 0.5, -0.32, 0, Math.PI); ctx.stroke();
    ctx.restore();
  }

  // ---------- 粒子：沿曲线流动的星流 ----------
  function makeStream(rand, n, w, h, path) {
    var ps = [];
    for (var i = 0; i < n; i++) {
      var big = rand() < 0.035;
      var g1 = (rand() + rand() + rand() - 1.5) / 1.5;
      ps.push({ u: rand(), spread: g1 * 1.25, off: (rand() - 0.5) * 2, r: big ? rand() * 1.6 + 1.6 : rand() * 1.1 + 0.25,
        c: STAR_COLORS[rand() < 0.15 ? 4 : rand() < 0.25 ? 3 : (rand() * 3) | 0], a: big ? 0.9 : rand() * 0.6 + 0.35, sp: rand() * 0.6 + 0.7, tw: rand() * Math.PI * 2 });
    }
    return { ps: ps, path: path };
  }

  function drawStream(ctx, s, w, h, t, speed) {
    for (var i = 0; i < s.ps.length; i++) {
      var p = s.ps[i];
      var u = (p.u + t * speed * p.sp) % 1;
      var pt = s.path(u, w, h);
      var width = pt.width * (0.35 + 0.65 * Math.sin(Math.PI * u));
      var x = pt.x + pt.nx * p.spread * width + pt.tx * p.off * 4;
      var y = pt.y + pt.ny * p.spread * width + pt.ty * p.off * 4;
      var fade = Math.min(1, u * 6, (1 - u) * 6);
      var tw = 0.75 + 0.25 * Math.sin(t * 0.003 + p.tw);
      glowDot(ctx, x, y, p.r, p.c, p.a * fade * tw);
    }
  }

  // 首屏星流：从左上方向右绕过中心天体、再向下收束（参考效果的弧形轨迹）
  function heroPath(cx, cy, R) {
    return function (u, w, h) {
      var x0 = -0.05 * w, y0 = 0.10 * h;
      var x1 = cx + R * 4.6, y1 = cy - R * 3.4;
      var x2 = cx + R * 2.6, y2 = cy + R * 3.4;
      var x3 = cx + R * 0.6, y3 = Math.min(1.05 * h, cy + R * 6);
      var a = 1 - u;
      var x = a * a * a * x0 + 3 * a * a * u * x1 + 3 * a * u * u * x2 + u * u * u * x3;
      var y = a * a * a * y0 + 3 * a * a * u * y1 + 3 * a * u * u * y2 + u * u * u * y3;
      var dx = 3 * a * a * (x1 - x0) + 6 * a * u * (x2 - x1) + 3 * u * u * (x3 - x2);
      var dy = 3 * a * a * (y1 - y0) + 6 * a * u * (y2 - y1) + 3 * u * u * (y3 - y2);
      var len = Math.hypot(dx, dy) || 1;
      return { x: x, y: y, tx: dx / len, ty: dy / len, nx: -dy / len, ny: dx / len, width: R * 1.25 };
    };
  }

  // 星系旋臂（Astra）
  function makeGalaxy(rand, n) {
    var ps = [];
    for (var i = 0; i < n; i++) {
      var arm = i % 2, k = Math.pow(rand(), 0.7);
      var g2 = (rand() + rand() + rand() - 1.5) / 1.5;
      ps.push({ arm: arm, k: k, j: g2 * 0.42, rj: (rand() + rand() - 1) * 0.12, r: rand() < 0.04 ? rand() * 1.4 + 1.4 : rand() * 1 + 0.25, c: STAR_COLORS[(rand() * 4) | 0], a: rand() * 0.6 + 0.4 });
    }
    return ps;
  }
  function drawGalaxy(ctx, ps, x, y, R, t) {
    var rot = t * 0.00008;
    var core = ctx.createRadialGradient(x, y, 0, x, y, R * 0.45);
    core.addColorStop(0, 'rgba(255,255,255,0.95)'); core.addColorStop(0.3, 'rgba(200,220,255,0.35)'); core.addColorStop(1, 'rgba(120,150,220,0)');
    ctx.fillStyle = core; ctx.beginPath(); ctx.arc(x, y, R * 0.45, 0, Math.PI * 2); ctx.fill();
    for (var i = 0; i < ps.length; i++) {
      var p = ps[i];
      var ang = p.k * 4.4 + p.arm * Math.PI + rot + p.j;
      var rad = R * (0.08 + p.k * 0.95 + p.rj * (0.3 + p.k));
      var px = x + Math.cos(ang) * rad, py = y + Math.sin(ang) * rad * 0.62;
      glowDot(ctx, px, py, p.r * (1.15 - p.k * 0.5), p.c, p.a * (1 - p.k * 0.45));
    }
  }

  // ---------- 首屏 ----------
  function hero(el) {
    var canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%';
    el.appendChild(canvas);
    el.classList.add('is-canvas');
    var kind = el.getAttribute('data-art') || 'sol';
    var state, stream, stars, gal, rand;
    function build() {
      state = setup(canvas);
      rand = rng(20261024);
      var w = state.w, h = state.h;
      // 天体中心对齐标题（参考效果：标题左右分开，天体居中在同一水平线上）
      var h1 = el.parentElement && el.parentElement.querySelector('h1');
      var top = el.getBoundingClientRect().top;
      var cy = h1 ? (h1.getBoundingClientRect().top + h1.getBoundingClientRect().height / 2 - top) : h * 0.45;
      var R = w < 640 ? Math.min(w * 0.2, 80) : Math.min(w * 0.068, 112);
      // 水平方向：页面居中；桌面端如果会压到标题左右两半，就在空隙内往远离标题的一侧挪
      var left = el.getBoundingClientRect().left, cx = innerWidth / 2 - left;
      var parts = h1 ? h1.querySelectorAll('span') : [];
      if (w >= 640 && parts.length >= 2) {
        var a = parts[0].getBoundingClientRect(), b = parts[parts.length - 1].getBoundingClientRect();
        var lo = a.right - left + R * 1.3, hi = b.left - left - R * 1.3;
        if (lo <= hi) cx = Math.min(Math.max(cx, lo), hi);
        else if (b.left > a.right) cx = (a.right + b.left) / 2 - left;
      }
      state.cx = cx; state.cy = Math.max(R * 1.6, Math.min(cy - (w < 640 ? R * 2.6 : 0), h - R * 2)); state.R = R;
      stars = fieldStars(rand, Math.round(w * h / 9000), w, h);
      stream = makeStream(rand, w < 640 ? 900 : 2600, w, h, heroPath(state.cx, state.cy, R));
      gal = makeGalaxy(rand, w < 640 ? 1400 : 2600);
    }
    function frame(t) {
      var c = state.ctx, w = state.w, h = state.h;
      background(c, w, h, state.cx, state.cy);
      for (var i = 0; i < stars.length; i++) { var s = stars[i]; glowDot(c, s.x, s.y, s.r, s.c, 0.35 + 0.25 * Math.sin(t * 0.0015 + s.tw)); }
      if (kind !== 'astra') drawStream(c, stream, w, h, t, 0.000012);
      if (kind === 'astra') drawGalaxy(c, gal, state.cx, state.cy, state.R * 3.2, t);
      else if (kind === 'luna') drawMoon(c, state.cx, state.cy, state.R);
      else if (kind === 'terra') drawEarth(c, state.cx, state.cy, state.R, t);
      else if (kind === 'pro') drawRing(c, state.cx, state.cy, state.R * 0.95, t);
      else if (kind === 'flagship') drawPlanet(c, state.cx, state.cy, state.R * 0.85);
      else drawSun(c, state.cx, state.cy, state.R, t);
      // 底部渐隐，衔接正文黑底
      var fade = c.createLinearGradient(0, h * 0.72, 0, h);
      fade.addColorStop(0, 'rgba(0,0,0,0)'); fade.addColorStop(1, 'rgba(0,0,0,1)');
      c.fillStyle = fade; c.fillRect(0, h * 0.72, w, h * 0.28);
    }
    run(canvas, build, frame);
    window.addEventListener('load', function () { build(); frame(0); });
  }

  // ---------- 三联卡片 ----------
  function tier(el) {
    var kind = (el.className.match(/g-art-([a-z]+)/) || [])[1] || 'sol';
    var canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%';
    el.appendChild(canvas);
    el.classList.add('is-canvas');
    var state, stars, gal, stream, sparks, rand;
    function build() {
      state = setup(canvas);
      rand = rng(kind.length * 7919 + 17);
      var w = state.w, h = state.h;
      state.cx = w * 0.5; state.cy = h * 0.42; state.R = Math.min(w, h) * 0.17;
      stars = fieldStars(rand, Math.round(w * h / 1400), w, h);
      gal = makeGalaxy(rand, 1500);
      var R = state.R;
      stream = makeStream(rand, 160, w, h, function (u, W, H) {
        var x = -0.1 * W + u * 1.2 * W, y = H * 0.3 + Math.sin(u * Math.PI) * -H * 0.12 + (u - 0.5) * H * 0.25;
        return { x: x, y: y, tx: 1, ty: 0, nx: 0, ny: 1, width: R * 0.9 };
      });
      sparks = [];
      for (var i = 0; i < 3; i++) sparks.push({ x: w * (0.15 + rand() * 0.7), y: h * (0.12 + rand() * 0.5), l: 6 + rand() * 7, ph: rand() * 6 });
    }
    function frame(t) {
      var c = state.ctx, w = state.w, h = state.h;
      c.clearRect(0, 0, w, h);
      var bg = c.createRadialGradient(state.cx, state.cy, 0, state.cx, state.cy, h * 0.8);
      bg.addColorStop(0, '#0c1820'); bg.addColorStop(1, '#071016');
      c.fillStyle = bg; c.fillRect(0, 0, w, h);
      for (var i = 0; i < stars.length; i++) { var s = stars[i]; glowDot(c, s.x, s.y, s.r * 0.9, s.c, 0.3 + 0.3 * Math.sin(t * 0.002 + s.tw)); }
      if (kind === 'sol' || kind === 'terra') drawStream(c, stream, w, h, t, 0.00002);
      if (kind === 'astra') drawGalaxy(c, gal, state.cx, state.cy, state.R * 2.3, t);
      else if (kind === 'luna') drawMoon(c, state.cx, state.cy, state.R * 0.62);
      else if (kind === 'terra') drawEarth(c, state.cx, state.cy, state.R * 0.8, t);
      else if (kind === 'pro') drawRing(c, state.cx, state.cy, state.R * 0.85, t);
      else if (kind === 'flagship') drawPlanet(c, state.cx, state.cy, state.R * 0.6);
      else drawSun(c, state.cx, state.cy, state.R * 0.82, t);
      for (var j = 0; j < sparks.length; j++) { var sp = sparks[j]; sparkle(c, sp.x, sp.y, sp.l, 0.55 + 0.45 * Math.sin(t * 0.0018 + sp.ph)); }
      // 底部压暗，保证价格文字清晰
      var fade = c.createLinearGradient(0, h * 0.55, 0, h);
      fade.addColorStop(0, 'rgba(7,16,22,0)'); fade.addColorStop(1, 'rgba(7,16,22,0.92)');
      c.fillStyle = fade; c.fillRect(0, h * 0.55, w, h * 0.45);
    }
    run(canvas, build, frame);
  }

  // 动画调度：可见时才跑，尺寸变化重建
  function run(canvas, build, frame) {
    build();
    frame(0);
    if (reduce) {
      window.addEventListener('resize', function () { build(); frame(0); });
      return;
    }
    var visible = false, raf = 0, t0 = performance.now();
    function loop(now) { frame(now - t0); if (visible) raf = requestAnimationFrame(loop); }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          visible = e.isIntersecting;
          cancelAnimationFrame(raf);
          if (visible) raf = requestAnimationFrame(loop);
        });
      }).observe(canvas);
    } else { visible = true; raf = requestAnimationFrame(loop); }
    var rt;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { build(); frame(performance.now() - t0); }, 150); });
  }

  function init() {
    document.querySelectorAll('.g-hero-art').forEach(hero);
    document.querySelectorAll('.g-tier-art').forEach(tier);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
