# 真实 390px 宽度检查。无头 Chrome 的窗口最小宽度约 478px（--window-size=390 实际是 478），
# 所以这里把页面放进一个 390px 宽的 iframe，由 iframe 里注入的脚本量完用 postMessage 传给外层。
# 检查：页面横向滚动宽度、导航最右元素、「同类模型 API」版块有没有超出 390、它和 FAQ 的左边界是否对齐。
# 用法：python scripts/i18n/mobile_probe.py <lang> [前缀...]    需要 python scripts/preview.py 在 8765 端口运行
import concurrent.futures
import glob
import html
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W = 390
INNER = '''<script>(function(){var d=document,r={W:innerWidth,sw:d.documentElement.scrollWidth};
var navMax=0;d.querySelectorAll("header a,header button,header summary,nav a,nav button,nav summary").forEach(function(e){var b=e.getBoundingClientRect(),s=getComputedStyle(e);
 if(b.width>0&&s.display!=="none"&&s.visibility!=="hidden"&&b.right>navMax)navMax=b.right});r.nav=Math.round(navMax);
var rel=d.getElementById("related");
if(rel){var over=0,who="";rel.querySelectorAll("*").forEach(function(e){var b=e.getBoundingClientRect();if(b.width>0&&b.right>over){over=b.right;who=e.tagName.toLowerCase()+"."+String(e.className).slice(0,20)}});
 var l=rel.querySelector(".rel-list"),lb=l?l.getBoundingClientRect():null;
 var f=d.getElementById("faq"),fd=f?f.querySelector("details"):null,fb=fd?fd.getBoundingClientRect():null;
 r.rel={right:Math.round(over),who:who,listLeft:lb?Math.round(lb.left):null,listW:lb?Math.round(lb.width):null,faqLeft:fb?Math.round(fb.left):null,faqW:fb?Math.round(fb.width):null}}
parent.postMessage(JSON.stringify(r),"*")})();</script>'''
CH = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]


def probe(lang, slug):
    src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
    base = os.path.join(ROOT, '.playwright-mcp', 'k', f'mp-{lang}-{slug}')
    os.makedirs(os.path.dirname(base), exist_ok=True)
    io.open(base + '-in.html', 'w', encoding='utf-8').write(src.replace('</body>', INNER + '</body>', 1))
    io.open(base + '.html', 'w', encoding='utf-8').write(
        f'<!doctype html><body style="margin:0"><pre id="o"></pre><iframe id="f" width="{W}" height="900" style="border:0" '
        f'src="/.playwright-mcp/k/mp-{lang}-{slug}-in.html"></iframe><script>addEventListener("message",function(e){{document.getElementById("o").textContent=e.data}})</script>')
    d = None
    for _ in range(3):
        try:
            out = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=700,1000', '--virtual-time-budget=8000', '--dump-dom',
                                  f'http://localhost:8765/.playwright-mcp/k/mp-{lang}-{slug}.html'], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
        except subprocess.TimeoutExpired:
            continue
        m = re.search(r'<pre id="o">(.*?)</pre>', out, re.S)
        if m and m.group(1).strip():
            d = json.loads(html.unescape(m.group(1)))
            break
    for ext in ('-in.html', '.html'):
        try:
            os.remove(base + ext)
        except OSError:
            pass
    return slug, d


def main():
    lang = sys.argv[1]
    pre = [a for a in sys.argv[2:] if not a.startswith('--')]
    slugs = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, lang, 'models', '*.html')))
    slugs = [s for s in slugs if s != 'index' and (not pre or any(s.startswith(p) for p in pre))]
    res, bad, none = {}, [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for slug, d in ex.map(lambda s: probe(lang, s), slugs):
            res[slug] = d
            if not d:
                none.append(slug)
                continue
            why = []
            if d['W'] != W:
                why.append(f"layout width {d['W']}≠{W}")
            if d['sw'] > W:
                why.append(f"page scrollWidth {d['sw']}")
            if d['nav'] > W + 1:
                why.append(f"nav right {d['nav']}")
            r = d.get('rel')
            if r:
                if r['right'] > W + 1:
                    why.append(f"related overflows to {r['right']} ({r['who']})")
                if r['faqLeft'] is not None and r['listLeft'] is not None and abs(r['faqLeft'] - r['listLeft']) > 2:
                    why.append(f"left edge FAQ {r['faqLeft']} vs related {r['listLeft']}")
            if why:
                bad.append((slug, why))
    io.open(os.path.join(ROOT, 'drafts', 'i18n', f'mobile_probe_{lang}.json'), 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
    print(f'{lang} @{W}: probed {len(slugs)} | no result {len(none)} {none[:4]} | problems {len(bad)}')
    for slug, why in bad[:25]:
        print(f'  {slug:32} ' + '; '.join(why))


if __name__ == '__main__':
    main()
