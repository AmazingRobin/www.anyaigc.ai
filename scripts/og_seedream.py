# 生成 Seedream 系列专题页分享图（1200×630）：python scripts/og_seedream.py
# 先写 HTML 到 .playwright-mcp/og/seedream/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）。右侧 2×2 用官方示例图（与首屏相同），3.0 用 seedream.css 的 .sd-tile 示意图。
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seedream_data import SLUGS, cny, usd  # noqa: E402
import seedream_gallery as GL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'seedream')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
_raw = io.open(os.path.join(ROOT, 'assets/icons/bytedance-color.svg'), encoding='utf-8').read()
ICON = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S)

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧 4 块示意图)
DATA = {
    'seedream': ('Seedream API', {'zh': f'字节跳动全系生图模型，按张 {cny("seedream-5.0-lite")} 起', 'en': f'Every Seedream model, from {usd("seedream-5.0-lite")} / image'},
                 {'zh': ['5.0 Pro · lite · 4.5 · 4.0', '对公 · 专票'], 'en': ['5.0 Pro · lite · 4.5 · 4.0', 'Contracts · invoices']},
                 ('info', 'edit', 'seq', 'lang')),
    'seedream-5.0-pro': ('Seedream 5.0 Pro', {'zh': f'旗舰生图模型，每张 {cny("seedream-5.0-pro")} 起', 'en': f'The flagship model, from {usd("seedream-5.0-pro")} / image'},
                         {'zh': ['高密度信息图', '精准编辑', '并发不限'], 'en': ['Infographics', 'Precise edits', 'Unlimited concurrency']},
                         ('info', 'edit', 'photo', 'lang')),
    'seedream-5.0-lite': ('Seedream 5.0 lite', {'zh': f'4K 与联网检索，每张 {cny("seedream-5.0-lite")} 起', 'en': f'4K and web search, from {usd("seedream-5.0-lite")} / image'},
                          {'zh': ['4K', '组图', '并发不限'], 'en': ['4K', 'Image sets', 'Unlimited concurrency']},
                          ('search', 'seq', 'multi', 'type')),
    'seedream-4.5': ('Seedream 4.5', {'zh': f'海报排版与多图融合，每张 {cny("seedream-4.5")} 起', 'en': f'Posters and multi-image blends, from {usd("seedream-4.5")}'},
                     {'zh': ['海报排版', '4K', '并发不限'], 'en': ['Typography', '4K', 'Unlimited concurrency']},
                     ('type', 'photo', 'multi', 'seq')),
    'seedream-4.0': ('Seedream 4.0', {'zh': f'生成编辑一体，每张 {cny("seedream-4.0")} 起', 'en': f'Generate and edit, from {usd("seedream-4.0")} / image'},
                     {'zh': ['组图 15 张', '4K', '并发不限'], 'en': ['Up to 15 images', '4K', 'Unlimited concurrency']},
                     ('seq', 'edit', 'multi', 'info')),
    'seedream-3.0': ('Seedream 3.0', {'zh': f'中英双语文生图，每次 {cny("seedream-3.0")}', 'en': f'Bilingual text-to-image, {usd("seedream-3.0")} / request'},
                     {'zh': ['原生 2K', '文生图', '并发不限'], 'en': ['Native 2K', 'Text-to-image', 'Unlimited concurrency']},
                     ('type', 'photo', 'info', 'lang')),
}

TPL = '''<!doctype html><html class="no-js"><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/models/seedream.css"><style>
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:linear-gradient(180deg,#171719,#0f1013)}
body{position:relative;color:#fff;font-family:"Stack Sans Headline",Inter,"PingFang SC","Microsoft YaHei",system-ui,sans-serif}
.glow{position:absolute;inset:-30% -10% auto auto;width:75%;height:140%;background:radial-gradient(45% 45% at 70% 40%,rgba(60,86,244,.45),transparent 70%),radial-gradient(35% 35% at 40% 70%,rgba(0,200,210,.2),transparent 70%)}
.c{position:absolute;left:72px;top:64px;width:600px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;color:#fcfcfd}
.b svg{width:34px;height:34px}
h1{margin:96px 0 0;color:#fff;font-size:@FSpx;line-height:1;font-weight:600;letter-spacing:-2px}
p{margin:24px 0 0;font-size:29px;line-height:1.35;color:rgba(252,252,253,.72)}
.r{position:absolute;left:72px;bottom:62px;display:flex;gap:10px}
.r span{padding:9px 20px;border-radius:999px;background:rgba(249,249,251,.1);font-size:21px;white-space:nowrap;color:#fcfcfd}
.r span.d{background:#fff;color:#171719;font-weight:600}
.g{position:absolute;right:56px;top:50px;width:430px}
.g ul{display:grid;grid-template-columns:1fr 1fr;gap:14px;list-style:none;margin:0;padding:0}
.g .sd-tile{aspect-ratio:auto;height:250px;transform:none}
.g .sd-tile:nth-child(odd){transform:translateY(16px)}
.g .sd-tile span{font-size:15px}
.g .sd-tile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
</style></head><body><div class="glow"></div><div class="c"><div class="b"><svg viewBox="0 0 24 24">@ICON</svg>AnyAIGC</div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><ul>@TILES</ul></div>
</body></html>'''

LABEL = {'zh': {'info': '信息图', 'edit': '精准编辑', 'photo': '人像质感', 'lang': '多语种', 'search': '联网检索', 'seq': '组图', 'multi': '多图融合', 'type': '海报排版'},
         'en': {'info': 'Infographics', 'edit': 'Precise edits', 'photo': 'Photoreal', 'lang': 'Multilingual', 'search': 'Web search', 'seq': 'Image sets', 'multi': 'Multi-image', 'type': 'Typography'}}


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for slug in SLUGS:
        title, sub, tags, tiles = DATA[slug]
        for lang in ('zh', 'en'):
            fs = 92 if len(title) <= 13 else 76
            t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(tags[lang]))
            keys = [f'{a}/{b}' for a, b in GL.OVERVIEW] if slug == 'seedream' else [f'{slug}/{k}' for k in GL.PICK[slug]['hero']] if slug in GL.PICK else None
            if keys:
                tl = ''.join(f'<li class="sd-tile"><img src="/assets/models/seedream/{GL.IMAGES[k]["file"]}" alt=""></li>' for k in keys)
            else:
                tl = ''.join(f'<li class="sd-tile sd-tile-{k}"><span>{LABEL[lang][k]}</span></li>' for k in tiles)
            h = (TPL.replace('@FS', str(fs)).replace('@ICON', ICON).replace('@TITLE', title).replace('@SUB', sub[lang])
                 .replace('@TAGS', t).replace('@TILES', tl))
            name = f'{slug}-{lang}'
            io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(h)
            jobs.append(name)
    run = lambda *a: subprocess.run(['bash', CLI, '-s=og', *a], capture_output=True, text=True)
    run('open', 'about:blank')
    run('resize', '1200', '630')
    for name in jobs:
        run('goto', f'http://localhost:8765/.playwright-mcp/og/seedream/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
