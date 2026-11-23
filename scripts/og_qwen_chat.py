"""Qwen 对话类专题页（25 页）的 ja / ko / es / de 分享图，输出 assets/og/<slug>-<lang>.png（1200x630）。

事实全部从 en/models/<slug>.html 解析（H1、og:description），不手写价格。
流程：写临时 html（放 .playwright-mcp/og-qwen-chat/）-> 无头 Chrome dump-dom 取版面自检报告
-> 通过后截图并裁成 1200x630 -> 删临时 html。字号由页内 JS 自动缩小，直到标题/副标题/标签不越界。

用法：
  PYTHONIOENCODING=utf-8 python scripts/og_qwen_chat.py [--langs=ja,ko,es,de] [--only=slug1,slug2]
需要预览服务：python scripts/preview.py（http://localhost:8765）
"""
import glob
import html
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / '.playwright-mcp' / 'og-qwen-chat'
BASE = 'http://localhost:8765'

SLUGS = ['qwen', 'qwen-flash', 'qwen-max', 'qwen-plus', 'qwen-plus-2025-12-01', 'qwen-plus-character',
         'qwen3-vl-plus', 'qwen3.5-122b-a10b', 'qwen3.5-27b', 'qwen3.5-35b-a3b', 'qwen3.5-397b-a17b',
         'qwen3.5-plus', 'qwen3.5-plus-2026-02-15', 'qwen3.6-27b', 'qwen3.6-35b-a3b', 'qwen3.6-plus',
         'qwen3.6-plus-2026-04-02', 'qwen3.7-max', 'qwen3.7-plus', 'qwen3.8-27b', 'qwen3.8-flash',
         'qwen3.8-max', 'qwen3.8-max-0902', 'qwen3.8-omni-flash', 'qwq-32b']
LANGS = ('ja', 'ko', 'es', 'de')
LANGATTR = {'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}

# 词表：缺词直接 KeyError，不回退英文
TXT = {
    'unlimited': {'ja': '同時実行数の上限なし', 'ko': '동시 실행 제한 없음', 'es': 'Sin límite de RPM', 'de': 'Kein RPM-Limit'},
    'invoice': {'ja': '請求書を自分で発行', 'ko': '인보이스 직접 발급', 'es': 'Facturas en consola', 'de': 'Rechnungen im Konto'},
    'chat': {'ja': 'Chat Completions', 'ko': 'Chat Completions', 'es': 'Chat Completions', 'de': 'Chat Completions'},
    # 页面 og:description 的 "OpenAI-compatible Chat Completions" + 起步价
    'compat': {'ja': 'OpenAI互換のChat Completions。', 'ko': 'OpenAI 호환 Chat Completions.',
               'es': 'Chat Completions compatible con OpenAI.', 'de': 'OpenAI-kompatible Chat Completions.'},
    'from': {'ja': '入力 100万トークン ${p} から', 'ko': '입력 100만 토큰 ${p}부터',
             'es': 'desde ${p} / 1M de entrada', 'de': 'ab ${p} / 1 Mio. Eingabe'},
    # 仅总览页：英文 title 里的 "Compare 24 Models"
    'compare24': {'ja': '24モデルを比較。', 'ko': '24개 모델 비교.', 'es': 'Compara 24 modelos.', 'de': '24 Modelle im Vergleich.'},
}
FONTS = {
    'ja': '"Yu Gothic UI","Meiryo","Segoe UI",Arial,sans-serif',
    'ko': '"Malgun Gothic","Segoe UI",Arial,sans-serif',
    'es': '"Segoe UI",Arial,sans-serif',
    'de': '"Segoe UI",Arial,sans-serif',
}


def tr(key, lang):
    return TXT[key][lang]


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    if not hits:
        sys.exit('找不到 Playwright Chromium')
    return hits[-1]


def qwen_paths():
    raw = (ROOT / 'assets/icons/qwen.svg').read_text(encoding='utf-8')
    return re.findall(r'<path\b[^>]*?d="([^"]+)"', raw)


def facts(slug):
    t = (ROOT / 'en/models' / f'{slug}.html').read_text(encoding='utf-8')

    def g(p):
        m = re.search(p, t, re.S)
        return html.unescape(m.group(1)).strip() if m else None
    h1 = re.sub(r'<[^>]+>', '', g(r'<h1[^>]*>(.*?)</h1>') or '').strip()
    desc = g(r'property="og:description" content="(.*?)"') or ''
    title = g(r'<title>(.*?)</title>') or ''
    price = re.search(r'from \$([0-9]+\.[0-9]+) per 1M input', desc)
    if not (h1.endswith(' API') and price):
        sys.exit(f'{slug}: 解析失败 h1={h1!r} desc={desc!r}')
    return {'name': h1[:-4], 'price': price.group(1), 'overview': 'Compare 24 Models' in title}


def build(slug, lang):
    f = facts(slug)
    price = f['price']
    line1 = (tr('compare24', lang) + ' ' if f['overview'] else '') + tr('compat', lang)
    line2 = tr('from', lang).replace('{p}', price)
    # 两行各占一块，价格短语不会被拆开，避免第二行只剩一个孤词
    sub = '<span class="l">%s</span><span class="l">%s</span>' % (html.escape(line1), html.escape(line2))
    tags = [tr('chat', lang), tr('unlimited', lang), tr('invoice', lang)]
    logo = '<svg viewBox="0 0 24 24" width="30" height="30" fill="#fff" aria-hidden="true">%s</svg>' % ''.join(
        '<path d="%s" fill="#fff"/>' % d for d in qwen_paths())
    kw = 'word-break:keep-all;' if lang == 'ko' else ''
    tag_html = ''.join('<span>%s</span>' % html.escape(x) for x in tags)
    return f'''<!doctype html><html lang="{LANGATTR[lang]}"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
body{{width:1200px;height:630px;position:relative;overflow:hidden;background:#f4f7ff;color:#0f1b3d;font-family:{FONTS[lang]};{kw}}}
.c1{{position:absolute;right:-150px;top:-190px;width:560px;height:560px;border-radius:50%;background:#d9d4ff}}
.c2{{position:absolute;left:-130px;bottom:-190px;width:460px;height:460px;border-radius:50%;background:#dbe7ff}}
.wrap{{position:absolute;left:72px;right:72px;top:56px;bottom:56px;display:flex;flex-direction:column;z-index:1}}
.pill{{align-self:flex-start;display:flex;align-items:center;gap:12px;background:#2f5bff;color:#fff;border-radius:999px;padding:12px 28px 12px 20px;font-size:26px;font-weight:700;white-space:nowrap}}
h1{{margin:64px 0 0;font-size:100px;line-height:1.12;font-weight:800;letter-spacing:-2px;white-space:nowrap;color:#0f1b3d}}
.sub{{margin:20px 0 0;font-size:36px;line-height:1.4;font-weight:500;color:#33426b;max-width:980px}}
.sub .l{{display:block}}
.tags{{margin-top:auto;display:flex;flex-wrap:nowrap;gap:16px;font-size:26px;font-weight:600}}
.tags span{{white-space:nowrap;border:2px solid #2f5bff;color:#2f5bff;background:rgba(255,255,255,.75);border-radius:999px;padding:.4em .9em;line-height:1.2}}
</style></head><body>
<div class="c1"></div><div class="c2"></div>
<div class="wrap">
<div class="pill">{logo}<span>AnyAIGC · Qwen</span></div>
<h1 id="h">{html.escape(f['name'])} API</h1>
<p class="sub" id="s">{sub}</p>
<div class="tags" id="t">{tag_html}</div>
</div>
<script>
function fit(el, min, ok) {{
  var fs = parseFloat(getComputedStyle(el).fontSize), start = fs;
  while (!ok(el) && fs > min) {{ fs -= 1; el.style.fontSize = fs + 'px'; }}
  return {{start: start, end: fs, shrunk: fs < start}};
}}
function textRect(el) {{
  var r = document.createRange(); r.selectNodeContents(el); return r.getBoundingClientRect();
}}
function run() {{
  var h = document.getElementById('h'), s = document.getElementById('s'), t = document.getElementById('t');
  var rep = {{}};
  rep.h = fit(h, 40, function (e) {{ return e.scrollWidth <= e.clientWidth; }});
  rep.s = fit(s, 20, function (e) {{
    var fs = parseFloat(getComputedStyle(e).fontSize);
    return e.getBoundingClientRect().height <= fs * 1.4 * 2 + 1;
  }});
  rep.t = fit(t, 14, function (e) {{ return e.scrollWidth <= e.clientWidth; }});
  var viol = [], boxes = {{}};
  function chk(name, r) {{
    boxes[name] = [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)];
    if (r.left < 0 || r.top < 0 || r.right > 1200 || r.bottom > 630) viol.push(name + ' 越出画布');
    if (r.right > 1128.5) viol.push(name + ' 超出右边距');
  }}
  chk('h1', textRect(h)); chk('sub', textRect(s));
  var lines = Math.round(s.getBoundingClientRect().height / (parseFloat(getComputedStyle(s).fontSize) * 1.4));
  rep.sublines = lines; if (lines > 2) viol.push('副标题超过 2 行');
  var tags = Array.prototype.slice.call(t.children), rects = tags.map(function (x) {{ return x.getBoundingClientRect(); }});
  rects.forEach(function (r, i) {{ chk('tag' + i, r); }});
  for (var i = 0; i < rects.length; i++) for (var j = i + 1; j < rects.length; j++) {{
    if (rects[i].right + 8 > rects[j].left && rects[i].left < rects[j].right && rects[i].top < rects[j].bottom && rects[j].top < rects[i].bottom) viol.push('tag' + i + ' 与 tag' + j + ' 重叠或间距不足');
  }}
  var hr = textRect(h), sr = textRect(s), tr0 = t.getBoundingClientRect();
  if (hr.bottom > sr.top) viol.push('标题与副标题重叠');
  if (sr.bottom > tr0.top) viol.push('副标题与标签重叠');
  rep.boxes = boxes; rep.viol = viol;
  document.body.setAttribute('data-report', JSON.stringify(rep));
}}
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () {{ run(); }});
</script></body></html>'''


def job(args):
    from PIL import Image
    slug, lang = args
    TMP.mkdir(parents=True, exist_ok=True)
    hp = TMP / f'{slug}-{lang}.html'
    png = ROOT / 'assets' / 'og' / f'{slug}-{lang}.png'
    hp.write_text(build(slug, lang), encoding='utf-8')
    url = f'{BASE}/.playwright-mcp/og-qwen-chat/{slug}-{lang}.html'
    common = [chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
              '--virtual-time-budget=6000']
    dom = subprocess.run(common + ['--dump-dom', url], capture_output=True, timeout=90).stdout.decode('utf-8', 'replace')
    m = re.search(r'data-report="([^"]*)"', dom)
    if not m:
        hp.unlink(missing_ok=True)
        return slug, lang, None, ['没取到自检报告']
    rep = json.loads(html.unescape(m.group(1)))
    if not rep['viol']:
        subprocess.run(common + [f'--screenshot={png}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        im = Image.open(png).crop((0, 0, 1200, 630))
        im.save(png, optimize=True)
    hp.unlink(missing_ok=True)
    return slug, lang, rep, rep['viol']


def main():
    langs = LANGS
    slugs = SLUGS
    for a in sys.argv[1:]:
        if a.startswith('--langs='):
            langs = tuple(a.split('=', 1)[1].split(','))
        elif a.startswith('--only='):
            slugs = a.split('=', 1)[1].split(',')
    for l in langs:
        if l not in LANGS:
            sys.exit(f'不支持的语言 {l}（本脚本只出 {LANGS}）')
    for s in slugs:
        if s not in SLUGS:
            sys.exit(f'不在页面列表里：{s}')
    jobs = [(s, l) for l in langs for s in slugs]
    shrunk = {'h': 0, 's': 0, 't': 0}
    bad = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for slug, lang, rep, viol in ex.map(job, jobs):
            if rep:
                for k in shrunk:
                    shrunk[k] += rep[k]['shrunk']
            tag = ''.join(k.upper() if rep and rep[k]['shrunk'] else '-' for k in ('h', 's', 't'))
            if viol:
                bad.append((slug, lang, viol))
            print(('FAIL ' if viol else 'ok   ') + f'{slug}-{lang} 缩小:{tag}', viol or '')
    print(f'共 {len(jobs)} 张；标题缩小 {shrunk["h"]}、副标题缩小 {shrunk["s"]}、标签缩小 {shrunk["t"]}；违例 {len(bad)}')
    if bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
