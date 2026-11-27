// Kimi / GLM 专题页首屏「模拟输出」：点击发送按钮后，按型号播放一段示例的执行过程和回答。
// 纯前端模拟，不请求任何模型。文案在 /assets/models/demo/<系列>-<语言>.json，没有对应文案的页面保持原样（按钮不可点）。
(function () {
  var box = document.querySelector('.k-ask, .g-ask');
  var send = box && box.querySelector('.k-send, .g-send');
  if (!box || !send || !window.fetch) return;

  var fam = box.classList.contains('k-ask') ? 'kimi' : 'glm';
  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  var slug = location.pathname.replace(/\/+$/, '').split('/').pop().replace(/\.html$/, '');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cur = document.currentScript;
  var ver = cur && cur.src && (cur.src.match(/[?&]v=(\d+)/) || [])[1];
  var url = '/assets/models/demo/' + fam + '-' + lang + '.json' + (ver ? '?v=' + ver : '');

  var NS = 'http://www.w3.org/2000/svg';
  function svg(attrs, shapes) {
    var s = document.createElementNS(NS, 'svg');
    var base = { viewBox: '0 0 24 24', width: '16', height: '16', 'aria-hidden': 'true' };
    Object.keys(base).forEach(function (k) { s.setAttribute(k, base[k]); });
    Object.keys(attrs).forEach(function (k) { s.setAttribute(k, attrs[k]); });
    shapes.forEach(function (sh) {
      var n = document.createElementNS(NS, sh.tag);
      Object.keys(sh.a).forEach(function (k) { n.setAttribute(k, sh.a[k]); });
      s.appendChild(n);
    });
    return s;
  }
  var ICON_STOP = function () { return svg({ fill: 'currentColor' }, [{ tag: 'rect', a: { x: '7', y: '7', width: '10', height: '10', rx: '2' } }]); };
  var ICON_REPLAY = function () {
    return svg({ fill: 'none', stroke: 'currentColor', 'stroke-width': '2.2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' },
      [{ tag: 'path', a: { d: 'M4 12a8 8 0 1 0 2.6-5.9' } }, { tag: 'path', a: { d: 'M4 4v5h5' } }]);
  };

  fetch(url).then(function (r) { return r.ok ? r.json() : Promise.reject(); }).then(function (d) {
    var page = d && d.pages && d.pages[slug];
    if (page && d.ui) init(d.ui, page);
  }).catch(function () {});

  function init(ui, page) {
    var run = 0;       // 每次开始或停止都加 1，旧的异步流程发现编号变了就退出
    var state = 'idle';
    var follow = true; // 用户自己滚动页面后，不再自动跟随
    var el = {};

    var out = document.createElement('div');
    out.className = 'ad-out';
    out.hidden = true;
    function make(tag, cls, parent) {
      var n = document.createElement(tag);
      n.className = cls;
      (parent || out).appendChild(n);
      return n;
    }
    var head = make('div', 'ad-head');
    el.tag = make('span', 'ad-tag', head);
    el.status = make('span', 'ad-state', head);
    el.steps = make('ol', 'ad-steps');
    el.answer = make('div', 'ad-answer');
    el.note = make('p', 'ad-note');
    box.appendChild(out);
    out.setAttribute('role', 'region');
    out.setAttribute('aria-label', ui.region);
    el.tag.textContent = ui.tag;

    var live = document.createElement('span');
    live.className = 'o-sr';
    live.setAttribute('aria-live', 'polite');
    box.appendChild(live);

    box.removeAttribute('aria-hidden');
    box.classList.add('ad-ready');
    send.setAttribute('role', 'button');
    send.setAttribute('tabindex', '0');
    label(ui.send);

    function label(text) {
      send.setAttribute('aria-label', text);
      send.setAttribute('title', text);
    }
    function setIcon(make) { send.textContent = ''; send.appendChild(make()); }
    function say(text) { live.textContent = text; }
    function status(text, busy) {
      el.status.textContent = text;
      el.status.classList.toggle('is-busy', !!busy);
    }
    function sleep(ms, id) {
      return new Promise(function (resolve) {
        setTimeout(function () { resolve(id === run); }, reduce ? 0 : ms);
      });
    }
    function keepInView() {
      if (!follow) return;
      var r = box.getBoundingClientRect();
      var over = r.bottom - (window.innerHeight - 20);
      if (over > 0) window.scrollBy({ top: over + 8, behavior: reduce ? 'auto' : 'smooth' });
    }
    function stopFollow() { follow = false; }
    window.addEventListener('wheel', stopFollow, { passive: true });
    window.addEventListener('touchmove', stopFollow, { passive: true });

    function reset() {
      el.steps.textContent = '';
      el.answer.textContent = '';
      el.note.textContent = '';
      out.classList.remove('is-stopped', 'is-done');
    }

    function addStep(text) {
      var li = document.createElement('li');
      li.className = 'ad-step';
      var mark = document.createElement('span');
      mark.className = 'ad-mark';
      mark.setAttribute('aria-hidden', 'true');
      var t = document.createElement('span');
      t.textContent = text;
      li.appendChild(mark);
      li.appendChild(t);
      el.steps.appendChild(li);
      return li;
    }

    // 把回答拆成段落和项目符号列表，逐段逐字符输出
    function blocks(lines) {
      var list = [];
      var ul = null;
      lines.forEach(function (line) {
        if (line.indexOf('- ') === 0) {
          if (!ul) { ul = { type: 'ul', items: [] }; list.push(ul); }
          ul.items.push(line.slice(2));
        } else {
          ul = null;
          list.push({ type: 'p', text: line });
        }
      });
      return list;
    }

    async function type(node, text, id, caret) {
      var chars = Array.from(text);
      var wide = /[　-鿿가-힯＀-￯]/.test(text);
      var step = wide ? 2 : 4;
      var tn = document.createTextNode('');
      node.appendChild(tn);
      node.appendChild(caret);
      for (var i = 0; i < chars.length; i += step) {
        tn.nodeValue += chars.slice(i, i + step).join('');
        if (!(await sleep(26, id))) return false;
      }
      return true;
    }

    async function play() {
      var id = ++run;
      follow = true;
      state = 'running';
      reset();
      out.hidden = false;
      box.classList.add('ad-ran');
      setIcon(ICON_STOP);
      label(ui.stop);
      say(ui.thinking);
      status(ui.thinking, true);
      keepInView();

      var caret = document.createElement('span');
      caret.className = 'ad-caret';
      caret.setAttribute('aria-hidden', 'true');

      if (!(await sleep(750, id))) return;

      status(ui.working, true);
      for (var i = 0; i < page.steps.length; i++) {
        var li = addStep(page.steps[i]);
        li.classList.add('is-run');
        keepInView();
        if (!(await sleep(700 + ((i * 173) % 420), id))) return;
        li.classList.remove('is-run');
        li.classList.add('is-done');
      }

      status(ui.writing, true);
      var bl = blocks(page.answer);
      for (var b = 0; b < bl.length; b++) {
        var node;
        if (bl[b].type === 'ul') {
          node = document.createElement('ul');
          el.answer.appendChild(node);
          for (var k = 0; k < bl[b].items.length; k++) {
            var li2 = document.createElement('li');
            node.appendChild(li2);
            keepInView();
            if (!(await type(li2, bl[b].items[k], id, caret))) return;
            caret.remove();
          }
        } else {
          node = document.createElement('p');
          el.answer.appendChild(node);
          keepInView();
          if (!(await type(node, bl[b].text, id, caret))) return;
          caret.remove();
        }
        if (!(await sleep(120, id))) return;
      }

      caret.remove();
      state = 'finished';
      out.classList.add('is-done');
      status(ui.done, false);
      el.note.textContent = ui.note;
      say(ui.done);
      setIcon(ICON_REPLAY);
      label(ui.replay);
      keepInView();
    }

    function stop() {
      run++;
      state = 'finished';
      out.classList.add('is-stopped');
      var c = out.querySelector('.ad-caret');
      if (c) c.remove();
      status(ui.stopped, false);
      el.note.textContent = ui.note;
      say(ui.stopped);
      setIcon(ICON_REPLAY);
      label(ui.replay);
    }

    // 减少动态效果：不播放动画，直接展示完整的示例输出
    function showAtOnce() {
      run++;
      reset();
      out.hidden = false;
      box.classList.add('ad-ran');
      page.steps.forEach(function (s) { addStep(s).classList.add('is-done'); });
      blocks(page.answer).forEach(function (blk) {
        if (blk.type === 'ul') {
          var ul = document.createElement('ul');
          blk.items.forEach(function (t) { var li = document.createElement('li'); li.textContent = t; ul.appendChild(li); });
          el.answer.appendChild(ul);
        } else {
          var p = document.createElement('p');
          p.textContent = blk.text;
          el.answer.appendChild(p);
        }
      });
      state = 'finished';
      out.classList.add('is-done');
      status(ui.done, false);
      el.note.textContent = ui.note;
      say(ui.done);
      setIcon(ICON_REPLAY);
      label(ui.replay);
    }

    function onActivate() {
      if (state === 'running') stop();
      else if (reduce) showAtOnce();
      else play();
    }
    send.addEventListener('click', onActivate);
    send.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onActivate(); }
    });
  }
})();
