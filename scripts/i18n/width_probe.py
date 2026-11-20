# 量每个页面里相邻版块的"内容列"实际宽度：FAQ 版块（#faq）和「同类模型 API」版块（#related）。
# 内容列 = 版块里第一个 h2 的外层容器（.xx-wrap）的内容盒宽度和左边界，以及 h2 自己的左边界。
# 用法：python scripts/i18n/width_probe.py <lang> <slug>...     需要 python scripts/preview.py 在 8765 端口运行
import glob, html, io, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = '''<pre id="wp" hidden></pre><script>(function(){var r={vw:document.documentElement.clientWidth};
function box(e){var b=e.getBoundingClientRect(),s=getComputedStyle(e);
 var pl=parseFloat(s.paddingLeft)||0,pr=parseFloat(s.paddingRight)||0;
 return {cls:(e.className||"").toString().slice(0,40),left:Math.round(b.left+pl),width:Math.round(b.width-pl-pr),mw:s.maxWidth}}
["faq","related"].forEach(function(id){var s=document.getElementById(id);if(!s){r[id]=null;return}
 var h=s.querySelector("h2");if(!h){r[id]="no h2";return}
 var wrap=h.parentElement,hb=h.getBoundingClientRect();
 var list=s.querySelector("details,.rel-list,li");var lb=list?list.getBoundingClientRect():null;
 r[id]={wrap:box(wrap),h2left:Math.round(hb.left),listLeft:lb?Math.round(lb.left):null,listWidth:lb?Math.round(lb.width):null}});
document.getElementById("wp").textContent=JSON.stringify(r)})();</script>'''
CH = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]
lang = sys.argv[1]
for slug in sys.argv[2:]:
    src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
    name = f'wp-{lang}-{slug}.html'
    p = os.path.join(ROOT, '.playwright-mcp', 'k', name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(src.replace('</body>', PROBE + '</body>', 1))
    out = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=1440,900', '--virtual-time-budget=6000', '--dump-dom',
                          f'http://localhost:8765/.playwright-mcp/k/{name}'], capture_output=True, timeout=90).stdout.decode('utf-8', 'replace')
    m = re.search(r'<pre id="wp"[^>]*>(.*?)</pre>', out, re.S)
    d = json.loads(html.unescape(m.group(1))) if m and m.group(1) else None
    os.remove(p)
    if not d:
        print(f'{slug:30} NO RESULT'); continue
    f, r = d.get('faq'), d.get('related')
    def s(x): return f"h2@{x['h2left']} list@{x['listLeft']} w={x['listWidth']} | wrap {x['wrap']['cls'][:22]!r} left={x['wrap']['left']} w={x['wrap']['width']}" if isinstance(x, dict) else str(x)
    print(f"{slug:30} vw={d['vw']}\n   FAQ    {s(f)}\n   RELATED {s(r)}")
