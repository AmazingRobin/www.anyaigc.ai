# 量导航栏是否在某个视口宽度下溢出：给页面末尾注入同步脚本，用无头 Chrome 的 --dump-dom 读结果。
# 用法：python scripts/i18n/nav_probe.py <slug> [lang,lang..] [width,width..]    需要 python scripts/preview.py 在 8765 端口运行
import glob
import html
import io
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = '''<pre id="probe" hidden></pre><script>(function(){var d=document,W=innerWidth,max=0,who='';
d.querySelectorAll('header a,header button,header summary,nav a,nav button,nav summary,ul.o-nav-right a,ul.o-nav-right summary').forEach(function(e){
var b=e.getBoundingClientRect(),s=getComputedStyle(e);if(b.width>0&&s.display!=='none'&&s.visibility!=='hidden'&&b.right>max){max=b.right;who=(e.textContent||'').trim().slice(0,22)}});
d.getElementById('probe').textContent='inner='+W+' scrollW='+d.documentElement.scrollWidth+' navRightmost='+Math.round(max)+' ('+who+')'+(max>W+1?' CUT-OFF':' ok')})();</script>'''


def chrome():
    return sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))[-1]


def main():
    slug = sys.argv[1]
    langs = (sys.argv[2] if len(sys.argv) > 2 else 'es,de,ja,ko').split(',')
    widths = [int(w) for w in (sys.argv[3] if len(sys.argv) > 3 else '390,1024,1200,1440').split(',')]
    os.makedirs(os.path.join(ROOT, '.playwright-mcp', 'm'), exist_ok=True)
    for lang in langs:
        src = io.open(os.path.join(ROOT, lang, 'models', slug + '.html'), encoding='utf-8').read()
        tmp = os.path.join(ROOT, '.playwright-mcp', 'm', f'probe-{lang}.html')
        io.open(tmp, 'w', encoding='utf-8').write(src.replace('</body>', PROBE + '</body>', 1))
        for w in widths:
            out = subprocess.run([chrome(), '--headless=new', '--disable-gpu', f'--window-size={w},800', '--virtual-time-budget=6000',
                                  '--dump-dom', f'http://localhost:8765/.playwright-mcp/m/probe-{lang}.html'],
                                 capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
            m = re.search(r'<pre id="probe"[^>]*>(.*?)</pre>', out, re.S)
            print(f'{lang} @{w:5d}  ' + (html.unescape(m.group(1)) if m and m.group(1) else 'NO RESULT'))


if __name__ == '__main__':
    main()
