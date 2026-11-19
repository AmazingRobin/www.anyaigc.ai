# 生成 Midjourney 专题页分享图（1200×630）：python scripts/og_midjourney.py
# 先写 HTML 到 .playwright-mcp/og/midjourney/，再用 playwright-cli 截图到 assets/og/midjourney-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）
import glob
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from midjourney_data import usd, VER  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'midjourney')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
_raw = io.open(os.path.join(ROOT, 'assets/icons/midjourney.svg'), encoding='utf-8').read()
LOGO = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S)
PI, PH = usd('mj_imagine'), usd('mj_upscale')
NEW = ('ja', 'ko', 'es', 'de')
SUB = {'zh': f'Imagine ${PI} / 次，放大 ${PH} / 次', 'en': f'Imagine ${PI} per call, upscale ${PH}',
       'ja': f'Imagine 1回 ${PI}、アップスケール ${PH}', 'ko': f'Imagine 회당 ${PI}, 업스케일 ${PH}',
       'es': f'Imagine ${PI} por llamada, ampliar ${PH}', 'de': f'Imagine ${PI} pro Aufruf, Hochskalieren ${PH}'}
# 非中文图不写"合同/对公"，发票写"自助开具"（2026-11-17 起非中文页口径）
TAGS = {'zh': ['14 种操作', 'Niji', '并发不限', '对公 · 专票'],
        'en': ['14 operations', 'Niji', 'Unlimited concurrency', 'Self-service invoices'],
        'ja': ['14種類の操作', 'Niji', '同時実行数の上限なし', '請求書を自分で発行'],
        'ko': ['14가지 작업', 'Niji', '동시 실행 제한 없음', '인보이스 직접 발급'],
        'es': ['14 operaciones', 'Niji', 'Sin límite de concurrencia', 'Facturas en consola'],
        'de': ['14 Operationen', 'Niji', 'Unbegrenzte Parallelität', 'Rechnungen im Konto']}
IMGS = [['cave-sea', 'panther', 'rococo'], ['duck-sweater', 'monet-cats', 'passion-fruit'], ['vhs-anime', 'ink-couple', 'wolf-cartoon']]

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#06051d;color:#fff;font-family:"Segoe UI","PingFang SC","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",system-ui,sans-serif;position:relative;overflow:hidden}
.scan{position:absolute;inset:0;background:radial-gradient(ellipse 60% 70% at 25% 45%,rgba(61,98,153,.45),transparent 70%),repeating-linear-gradient(180deg,rgba(61,98,153,.25) 0 1px,transparent 1px 4px)}
.c{position:absolute;left:72px;top:68px;width:600px}
.b{display:flex;align-items:center;gap:12px;font-family:"JetBrains Mono","Cascadia Code",Consolas,monospace;font-size:24px;font-weight:600}
.b svg{width:34px;height:34px}
.b i{width:1px;height:22px;background:rgba(255,255,255,.3)}
.b span{font-weight:400;color:rgba(255,255,255,.65)}
h1{margin:96px 0 0;font-family:"JetBrains Mono","Cascadia Code",Consolas,monospace;font-size:78px;line-height:1.02;font-weight:600;letter-spacing:-.04em;text-shadow:0 0 28px rgba(142,162,255,.45)}
p{margin:24px 0 0;font-size:30px;line-height:1.35;color:#cfd5e6}
.r{position:absolute;left:72px;bottom:64px;display:flex;flex-wrap:wrap;gap:10px;width:640px}
.r span{padding:8px 18px;border-radius:999px;font-size:20px;white-space:nowrap;background:rgba(142,162,255,.14);border:1px solid rgba(186,198,255,.3)}
.r span:nth-child(1){background:rgba(52,211,153,.2);border-color:rgba(52,211,153,.5)}
.r span:nth-child(4){background:rgba(251,113,133,.16);border-color:rgba(251,113,133,.45)}
.g{position:absolute;right:48px;top:-40px;bottom:-40px;width:450px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.g div{display:flex;flex-direction:column;gap:10px}
.g div:nth-child(2){margin-top:-90px}
.g img{width:100%;border-radius:4px}
.n p{font-size:26px}
.n .r{width:586px}
.n .r span{font-size:18px;padding:7px 14px}
</style></head><body class="@BC"><div class="scan"></div><div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#ffffff" fill-rule="evenodd">@LOGO</svg>AnyAIGC<i></i><span>Midjourney</span></div>
<h1>Midjourney<br>API</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g">@COLS</div>
</body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main_chrome(langs, cols):
    """指定 --langs= 时用无头 Chrome 出图（不依赖 playwright-cli）；图片从 http://localhost:8765 加载，需要预览服务在运行。"""
    from PIL import Image
    exe = chrome()
    for lang in langs:
        t = ''.join(f'<span>{x}</span>' for x in TAGS[lang])
        h = (TPL.replace('@LOGO', LOGO).replace('@SUB', SUB[lang]).replace('@TAGS', t).replace('@COLS', cols)
             .replace('@BC', 'n' if lang in NEW else ''))
        name = f'midjourney-{lang}'
        html_path = os.path.join(OUT, name + '.html')
        io.open(html_path, 'w', encoding='utf-8').write(h)
        png = os.path.join(ROOT, 'assets', 'og', name + '.png')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=6000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/midjourney/{name}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        os.remove(html_path)
        print('png', os.path.relpath(png, ROOT), os.path.getsize(png))


def main():
    os.makedirs(OUT, exist_ok=True)
    cols = ''.join('<div>' + ''.join(f'<img src="/assets/models/midjourney/{n}.webp?v={VER}">' for n in c) + '</div>' for c in IMGS)
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    if only:
        return main_chrome(only[0], cols)
    run = lambda *a: subprocess.run(['bash', CLI, '-s=og', *a], capture_output=True, text=True)
    run('open', 'about:blank')
    run('resize', '1200', '630')
    for lang in ('zh', 'en'):
        t = ''.join(f'<span>{x}</span>' for x in TAGS[lang])
        h = TPL.replace('@LOGO', LOGO).replace('@SUB', SUB[lang]).replace('@TAGS', t).replace('@COLS', cols).replace('@BC', '')
        name = f'midjourney-{lang}'
        io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(h)
        run('goto', f'http://localhost:8765/.playwright-mcp/og/midjourney/{name}.html')
        run('eval', 'new Promise(r=>{const i=[...document.images];Promise.all(i.map(x=>x.complete?1:new Promise(o=>{x.onload=x.onerror=o}))).then(()=>document.fonts.ready).then(()=>r(1))})')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
