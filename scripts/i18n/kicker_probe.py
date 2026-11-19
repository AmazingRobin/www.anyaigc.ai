# 用无头 Chrome 量每个页面里「规格」版块（#spec-unique）小标题的实际样式，并和同页其它版块的小标题比较：
# 颜色、字号、字重、下边距、是否有小标题。只比较"实际渲染出来的样子"，不看 class 名。
# 用法：python scripts/i18n/kicker_probe.py [--lang=en] [前缀...]     需要 python scripts/preview.py 在 8765 端口运行
# 输出：每个页面一行；不一致的标出差在哪。结果同时写入 drafts/i18n/kicker_probe.json
import concurrent.futures
import glob
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP = os.path.join(ROOT, '.playwright-mcp', 'k')
PROBE = '''<pre id="kprobe" hidden></pre><script>(function(){
function st(e){var s=getComputedStyle(e);return {tag:e.tagName.toLowerCase(),cls:e.className,color:s.color,size:s.fontSize,weight:s.fontWeight,mb:s.marginBottom,ls:s.letterSpacing,tt:s.textTransform,lh:s.lineHeight,mw:s.maxWidth,disp:s.display,txt:(e.textContent||"").trim().slice(0,20)}}
var out={spec:null,others:[]};
var sec=document.getElementById("spec-unique");
if(sec){var h=sec.querySelector("h2");var p=h&&h.previousElementSibling;
  out.spec=(p&&/kicker/i.test(p.className))?st(p):{none:true,prevTag:p?p.tagName.toLowerCase():null,prevCls:p?p.className:null}}
document.querySelectorAll("section").forEach(function(s){if(s.id==="spec-unique")return;var h=s.querySelector("h2");if(!h)return;
  var p=h.previousElementSibling;if(p&&/kicker/i.test(p.className))out.others.push(st(p))});
document.getElementById("kprobe").textContent=JSON.stringify(out)})();</script>'''


def chrome():
    return sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]


def probe(lang, slug):
    src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
    os.makedirs(TMP, exist_ok=True)
    name = f'{lang}-{slug}.html'
    io.open(os.path.join(TMP, name), 'w', encoding='utf-8').write(src.replace('</body>', PROBE + '</body>', 1))
    d = None
    for attempt in range(3):
        try:
            out = subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--window-size=1200,900',
                                  '--virtual-time-budget=4000', '--dump-dom', f'http://localhost:8765/.playwright-mcp/k/{name}'],
                                 capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
        except subprocess.TimeoutExpired:
            out = ''
        m = re.search(r'<pre id="kprobe"[^>]*>(.*?)</pre>', out, re.S)
        try:
            d = json.loads(html.unescape(m.group(1))) if m and m.group(1) else None
        except ValueError:
            d = None
        if d is not None:
            break
    os.remove(os.path.join(TMP, name))
    return slug, d


def verdict(d):
    if d is None:
        return 'NO RESULT'
    if d['spec'] is None:
        return 'no spec section'
    others = d['others']
    if d['spec'].get('none'):
        return 'ok (no kicker on spec; others have none)' if not others else 'MISSING kicker (others have one)'
    if not others:
        return 'EXTRA kicker (other sections have none)'
    ref = max(others, key=lambda o: sum(1 for x in others if (x['color'], x['size'], x['weight']) == (o['color'], o['size'], o['weight'])))
    diff = [k for k in ('color', 'size', 'weight', 'mb', 'ls', 'tt', 'lh', 'mw') if d['spec'].get(k) != ref.get(k)]
    return 'ok' if not diff else 'DIFFERS ' + ', '.join(f'{k}: {d["spec"][k]} vs {ref[k]}' for k in diff)


def main():
    lang = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--lang=')), 'en')
    prefixes = [a for a in sys.argv[1:] if not a.startswith('--')]
    slugs = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, lang, 'models', '*.html')))
    slugs = [s for s in slugs if s != 'index' and (not prefixes or any(s.startswith(p) for p in prefixes))]
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        for slug, d in ex.map(lambda s: probe(lang, s), slugs):
            results[slug] = d
    bad = {}
    for slug in slugs:
        v = verdict(results[slug])
        if not v.startswith('ok') and v != 'no spec section':
            bad[slug] = v
    io.open(os.path.join(ROOT, 'drafts', 'i18n', 'kicker_probe.json'), 'w', encoding='utf-8').write(json.dumps(results, ensure_ascii=False, indent=1))
    print(f'{lang}: probed {len(slugs)} pages | with a spec section: {sum(1 for s in slugs if results[s] and results[s]["spec"])} | inconsistent: {len(bad)}')
    for slug, v in bad.items():
        print(f'  {slug:34} {v}')


if __name__ == '__main__':
    main()
