# 生成 Nano Banana 系列专题页分享图（1200×630）：python scripts/og_nano_banana.py
# 先写 HTML 到 .playwright-mcp/og/nano-banana/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nano_banana_data import SLUGS, USD, CNY, cny_min  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'nano-banana')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
_raw = io.open(os.path.join(ROOT, 'assets/icons/nanobanana-color.svg'), encoding='utf-8').read()
ICON = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S)

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧图片)
DATA = {
    'nano-banana': ('Nano Banana API', {'zh': f'Google 全系图像模型，按张 {cny_min("nano-banana-2.1")} 起', 'en': f'Every Nano Banana model, from ${USD["nano-banana-2.1"]} / image'},
                    {'zh': ['2.1 · 2 · Pro', '4K 出图', '对公 · 专票'], 'en': ['2.1 · 2 · Pro', '4K output', 'Contracts · invoices']},
                    ('desert-poster-design', 'neon-portrait')),
    'nano-banana-2.1': ('Nano Banana 2.1', {'zh': f'最新升级版，1K 每张 {cny_min("nano-banana-2.1")}', 'en': f'The latest update, from ${USD["nano-banana-2.1"]} / image'},
                        {'zh': ['4K 出图', '14 种比例', '并发不限'], 'en': ['4K output', '14 aspect ratios', 'Unlimited concurrency']},
                        ('indie-film-posters', 'foggy-orange-sedan')),
    'nano-banana-2': ('Nano Banana 2', {'zh': f'Gemini 3.1 Flash Image，每张 {cny_min("nano-banana-2")} 起', 'en': f'Gemini 3.1 Flash Image, from ${USD["nano-banana-2"]} / image'},
                      {'zh': ['1K/2K 同价', '多图编辑', '并发不限'], 'en': ['Flash speed', 'Multi-image edits', 'Unlimited concurrency']},
                      ('earth-layers-infographic', 'spinning-red-dress')),
    'nano-banana-pro': ('Nano Banana Pro', {'zh': f'Gemini 3 Pro Image，每张 {cny_min("nano-banana-pro")} 起', 'en': f'Gemini 3 Pro Image, from ${USD["nano-banana-pro"]} / image'},
                        {'zh': ['专业级排版', '4K 出图', '并发不限'], 'en': ['Pro typography', '4K output', 'Unlimited concurrency']},
                        ('can-localization', 'futuristic-city')),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#000;color:#fff;font-family:"Google Sans Flex","Google Sans","PingFang SC","Microsoft YaHei",system-ui,sans-serif;position:relative;overflow:hidden}
.glow{position:absolute;inset:auto -10% -55% -10%;height:90%;background:radial-gradient(45% 55% at 25% 100%,rgba(49,134,255,.35),transparent 70%),radial-gradient(35% 45% at 75% 100%,rgba(252,213,63,.18),transparent 70%)}
.c{position:absolute;left:72px;top:64px;width:600px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:500;color:#cdd4dc}
.b svg{width:34px;height:34px}
h1{margin:92px 0 0;font-size:@FSpx;line-height:1.02;font-weight:500;letter-spacing:-.03em}
p{margin:22px 0 0;font-size:29px;line-height:1.3;color:#b2bbc5}
.r{position:absolute;left:72px;bottom:62px;display:flex;gap:10px}
.r span{padding:9px 18px;border-radius:12px;background:#18191d;border:1px solid #2a2b30;font-size:21px;white-space:nowrap;color:#cdd4dc}
.r span.d{background:#fff;color:#0e0f12;border-color:#fff;font-weight:600}
.g{position:absolute;right:56px;top:56px;bottom:56px;width:420px;display:grid;grid-template-rows:1fr 1fr;gap:14px}
.g div{border-radius:24px;background-size:cover;background-position:center}
</style></head><body><div class="glow"></div><div class="c"><div class="b"><svg viewBox="0 0 24 24">@ICON</svg>AnyAIGC</div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><div style="background-image:url(/assets/models/nano-banana/@IMG1.webp)"></div><div style="background-image:url(/assets/models/nano-banana/@IMG2.webp)"></div></div>
</body></html>'''


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for slug in SLUGS:
        title, sub, tags, (a, b) = DATA[slug]
        for lang in ('zh', 'en'):
            fs = 80 if len(title) <= 13 else 70
            t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(tags[lang]))
            h = (TPL.replace('@FS', str(fs)).replace('@ICON', ICON).replace('@TITLE', title).replace('@SUB', sub[lang])
                 .replace('@TAGS', t).replace('@IMG1', a).replace('@IMG2', b))
            name = f'{slug}-{lang}'
            io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(h)
            jobs.append(name)
    run = lambda *a: subprocess.run(['bash', CLI, '-s=og', *a], capture_output=True, text=True)
    run('open', 'about:blank')
    run('resize', '1200', '630')
    for name in jobs:
        run('goto', f'http://localhost:8765/.playwright-mcp/og/nano-banana/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
