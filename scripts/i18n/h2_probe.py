# 量页面里几个版块 h2 的真实样式（颜色、透明度、可见性、字重、字号、高度），确认标题没有被样式改动弄丢。
# 用法：python scripts/i18n/h2_probe.py <lang> <slug>...     需要 python scripts/preview.py 在 8765 端口运行
import glob, html, io, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = '''<pre id="hp" hidden></pre><script>(function(){var r={};
["spec-unique","faq","related"].forEach(function(id){var s=document.getElementById(id);if(!s){r[id]=null;return}
var h=s.querySelector("h2");if(!h){r[id]="no h2";return}var c=getComputedStyle(h),b=h.getBoundingClientRect();
r[id]={txt:h.textContent.trim().slice(0,22),color:c.color,op:c.opacity,vis:c.visibility,disp:c.display,wt:c.fontWeight,fs:c.fontSize,w:Math.round(b.width),h:Math.round(b.height),
 clip:c.webkitTextFillColor,bgclip:c.webkitBackgroundClip,tr:c.transform}});
document.getElementById("hp").textContent=JSON.stringify(r)})();</script>'''
CH = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]
lang = sys.argv[1]
for slug in sys.argv[2:]:
    src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
    name = f'h2-{lang}-{slug}.html'
    p = os.path.join(ROOT, '.playwright-mcp', 'k', name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(src.replace('</body>', PROBE + '</body>', 1))
    out = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=1200,900', '--virtual-time-budget=6000', '--dump-dom',
                          f'http://localhost:8765/.playwright-mcp/k/{name}'], capture_output=True, timeout=90).stdout.decode('utf-8', 'replace')
    m = re.search(r'<pre id="hp"[^>]*>(.*?)</pre>', out, re.S)
    d = json.loads(html.unescape(m.group(1))) if m and m.group(1) else None
    os.remove(p)
    print('==', lang, slug)
    for k, v in (d or {}).items():
        print('  ', k, v)
