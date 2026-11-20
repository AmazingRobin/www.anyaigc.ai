# 量每个页面里 FAQ 版块"自己有没有顶部分隔线"：#faq 本身的 border-top、它第一个子元素的 border-top、
# 以及它前一个兄弟版块的 border-bottom。三处任何一处有，就算 FAQ 上方有线。
# 用法：python scripts/i18n/faq_border_scan.py <lang> [前缀...]    需要 python scripts/preview.py 在 8765 端口运行
import collections, concurrent.futures, glob, html, io, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = '''<pre id="fb" hidden></pre><script>(function(){var f=document.getElementById("faq"),r={};
function bt(e){var s=getComputedStyle(e);return parseFloat(s.borderTopWidth)>0&&s.borderTopStyle!=="none"&&s.borderTopColor!=="rgba(0, 0, 0, 0)"}
function bb(e){var s=getComputedStyle(e);return parseFloat(s.borderBottomWidth)>0&&s.borderBottomStyle!=="none"&&s.borderBottomColor!=="rgba(0, 0, 0, 0)"}
if(f){r.self=bt(f);var c=f.firstElementChild;r.child=c?bt(c):false;var p=f.previousElementSibling;while(p&&p.nodeType===1&&/COMMENT/.test(p.nodeName))p=p.previousElementSibling;r.prevBottom=p?bb(p):false;
 r.bgDiffers=false;r.sec=String(f.className).slice(0,30)}
document.getElementById("fb").textContent=JSON.stringify(r)})();</script>'''
CH = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]
def probe(lang, slug):
    src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
    # 量的是"没有同类模型版块时 FAQ 自己的样子"，所以先把同类模型版块摘掉，避免它影响兄弟选择器
    src = re.sub(r'<!-- related-models -->.*?<!-- /related-models -->', '', src, flags=re.S)
    name = f'fb-{lang}-{slug}.html'
    p = os.path.join(ROOT, '.playwright-mcp', 'k', name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(src.replace('</body>', PROBE + '</body>', 1))
    d = None
    for _ in range(3):
        try:
            out = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=1440,900', '--virtual-time-budget=5000', '--dump-dom',
                                  f'http://localhost:8765/.playwright-mcp/k/{name}'], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
        except subprocess.TimeoutExpired:
            continue
        m = re.search(r'<pre id="fb"[^>]*>(.*?)</pre>', out, re.S)
        if m and m.group(1):
            d = json.loads(html.unescape(m.group(1))); break
    os.remove(p)
    return slug, d
lang = sys.argv[1]; pre = [a for a in sys.argv[2:] if not a.startswith('--')]
slugs = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, lang, 'models', '*.html')))
slugs = [s for s in slugs if s != 'index' and (not pre or any(s.startswith(x) for x in pre))]
res = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    for slug, d in ex.map(lambda s: probe(lang, s), slugs):
        res[slug] = d
io.open(os.path.join(ROOT, 'drafts', 'i18n', f'faq_border_{lang}.json'), 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
g = collections.defaultdict(collections.Counter)
for slug, d in res.items():
    series = re.split(r'[-.]', slug)[0]
    if not d: g[series]['NO RESULT'] += 1; continue
    has = d.get('self') or d.get('child') or d.get('prevBottom')
    g[series]['line above FAQ' if has else 'NO line above FAQ'] += 1
for s, c in sorted(g.items()):
    print(f'{s:12}', dict(c))
