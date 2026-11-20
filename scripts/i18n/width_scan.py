# 扫全站页面：「同类模型 API」版块的内容列（左边界、宽度）是否和 FAQ 版块一致。
# 用法：python scripts/i18n/width_scan.py <lang> [前缀...]    需要 python scripts/preview.py 在 8765 端口运行
import concurrent.futures, glob, html, io, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = '''<pre id="wp" hidden></pre><script>(function(){var r={};
function col(id){var s=document.getElementById(id);if(!s)return null;var h=s.querySelector("h2");if(!h)return null;
 var hb=h.getBoundingClientRect(),l=s.querySelector("details,.rel-list");var lb=l?l.getBoundingClientRect():null;
 var sb=s.getBoundingClientRect();
 return {left:lb?Math.round(lb.left):Math.round(hb.left),h2left:Math.round(hb.left),w:lb?Math.round(lb.width):null,secBg:getComputedStyle(s).backgroundColor,h2c:getComputedStyle(h).color,over:document.documentElement.scrollWidth>document.documentElement.clientWidth}}
r.faq=col("faq");r.rel=col("related");var ri=document.querySelector("#related .rel-inner");if(ri){var rb=ri.getBoundingClientRect(),cs=getComputedStyle(ri),ss=getComputedStyle(document.getElementById("related"));r.div={left:Math.round(rb.left),w:Math.round(rb.width),line:cs.borderTopWidth,secLine:ss.borderTopWidth}};r.vw=document.documentElement.clientWidth;
document.getElementById("wp").textContent=JSON.stringify(r)})();</script>'''
CH = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]


def probe(lang, slug, width):
    src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
    name = f'ws-{lang}-{slug}-{width}.html'
    p = os.path.join(ROOT, '.playwright-mcp', 'k', name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(src.replace('</body>', PROBE + '</body>', 1))
    d = None
    for _ in range(3):
        try:
            out = subprocess.run([CH, '--headless=new', '--disable-gpu', f'--window-size={width},900', '--virtual-time-budget=5000', '--dump-dom',
                                  f'http://localhost:8765/.playwright-mcp/k/{name}'], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
        except subprocess.TimeoutExpired:
            continue
        m = re.search(r'<pre id="wp"[^>]*>(.*?)</pre>', out, re.S)
        if m and m.group(1):
            d = json.loads(html.unescape(m.group(1)))
            break
    os.remove(p)
    return slug, d


def main():
    lang = sys.argv[1]
    width = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--width=')), 1440))
    pre = [a for a in sys.argv[2:] if not a.startswith('--')]
    slugs = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, lang, 'models', '*.html')))
    slugs = [s for s in slugs if s != 'index' and (not pre or any(s.startswith(x) for x in pre))]
    bad, none = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for slug, d in ex.map(lambda s: probe(lang, s, width), slugs):
            if not d or not d.get('rel') or not d.get('faq'):
                none.append(slug); continue
            f, r = d['faq'], d['rel']
            dv = d.get('div') or {}
            line_bad = (not dv) or dv.get('line') != '0px' or dv.get('secLine') != '0px' or abs(dv['left'] - f['left']) > 2 or abs(dv['w'] - (f['w'] or 0)) > 2
            if abs(f['left'] - r['left']) > 2 or abs((f['w'] or 0) - (r['w'] or 0)) > 2 or d['rel']['over'] or line_bad:
                r = dict(r, div=dv)
                bad.append((slug, f, r))
    io.open(os.path.join(ROOT, 'drafts', 'i18n', f'width_scan_{lang}_{width}.json'), 'w', encoding='utf-8').write(
        json.dumps({'bad': bad, 'none': none}, ensure_ascii=False, indent=1))
    print(f'{lang} @{width}: probed {len(slugs)} | no result/FAQ/related: {len(none)} {none[:4]} | misaligned or overflowing: {len(bad)}')
    groups = {}
    for slug, f, r in bad:
        groups.setdefault(re.split(r'[-.]', slug)[0], []).append((slug, f, r))
    for g, items in groups.items():
        slug, f, r = items[0]
        print(f"  {g:12} x{len(items):2d}  e.g. {slug:30} FAQ left={f['left']} w={f['w']} | REL left={r['left']} w={r['w']} overflow={r['over']} divider={r.get('div')}")


if __name__ == '__main__':
    main()
