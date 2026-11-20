# 在 390px 宽的 iframe 里找出比视口更宽的元素（最多 8 个，按右边界从大到小）。
# 用法：python scripts/i18n/overflow_finder.py <lang> <slug>
import glob, html, io, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INNER = '''<script>(function(){var out=[];document.querySelectorAll("body *").forEach(function(e){var b=e.getBoundingClientRect(),s=getComputedStyle(e);
 if(b.width>0&&b.right>392&&s.position!=="fixed"&&s.display!=="none"){var p=e.parentElement,clip=false;while(p&&p!==document.body){var o=getComputedStyle(p).overflowX;if(o==="auto"||o==="hidden"||o==="scroll"){clip=true;break}p=p.parentElement}
  if(!clip)out.push({tag:e.tagName.toLowerCase(),cls:String(e.className).slice(0,40),right:Math.round(b.right),w:Math.round(b.width),txt:(e.textContent||"").trim().slice(0,30)})}});
 out.sort(function(a,b){return b.right-a.right});parent.postMessage(JSON.stringify(out.slice(0,8)),"*")})();</script>'''
CH = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]
lang, slug = sys.argv[1], sys.argv[2]
src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
base = os.path.join(ROOT, '.playwright-mcp', 'k', f'of-{lang}-{slug}')
os.makedirs(os.path.dirname(base), exist_ok=True)
io.open(base + '-in.html', 'w', encoding='utf-8').write(src.replace('</body>', INNER + '</body>', 1))
io.open(base + '.html', 'w', encoding='utf-8').write(f'<!doctype html><body style="margin:0"><pre id="o"></pre><iframe width="390" height="900" style="border:0" src="/.playwright-mcp/k/of-{lang}-{slug}-in.html"></iframe><script>addEventListener("message",function(e){{document.getElementById("o").textContent=e.data}})</script>')
out = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=700,1000', '--virtual-time-budget=8000', '--dump-dom', f'http://localhost:8765/.playwright-mcp/k/of-{lang}-{slug}.html'], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
m = re.search(r'<pre id="o">(.*?)</pre>', out, re.S)
for it in json.loads(html.unescape(m.group(1))): print(it)
for ext in ('-in.html', '.html'): os.remove(base + ext)
