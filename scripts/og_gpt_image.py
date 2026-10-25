# 生成 GPT Image 系列专题页分享图（1200×630）：python scripts/og_gpt_image.py
# 先写 HTML 到 .playwright-mcp/og/gpt-image/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpt_image_data import SLUGS, MODELS, TOKEN, CALL, cny  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'gpt-image')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
LOGO = re.search(r' d="([^"]+)"', io.open(os.path.join(ROOT, 'assets/icons/openai.svg'), encoding='utf-8').read()).group(1)
T2, T25 = TOKEN['2']['out'], TOKEN['2.5']['out']

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧图片)
DATA = {
    'gpt-image': ('GPT Image API', {'zh': f'OpenAI 全系图像模型，按张 {cny("2")} 起', 'en': f'Every OpenAI image model, from ${CALL["2"]} / image'},
                  {'zh': ['按 token / 按张', '生成 · 编辑', '对公 · 专票'], 'en': ['Token or per image', 'Generate · edit', 'Contracts · invoices']}, ('polyglot-collage', 'matcha-poster')),
    'gpt-image-2.5-sunburst': ('GPT Image 2.5 Sunburst', {'zh': f'编辑精度最高，图片输出 ${T25} / 1M', 'en': f'Highest editing precision, ${T25} / 1M output'},
                               {'zh': ['约 6 折', 'max 质量', '并发不限'], 'en': ['41% off', 'max quality', 'Unlimited concurrency']}, ('korean-hanok-ad', 'high-fashion')),
    'gpt-image-2.5-flare': ('GPT Image 2.5 Flare', {'zh': f'速度最快，图片输出 ${T25} / 1M', 'en': f'Fastest high-quality model, ${T25} / 1M output'},
                            {'zh': ['约 6 折', '批量出图', '并发不限'], 'en': ['41% off', 'High volume', 'Unlimited concurrency']}, ('merch-grid', 'candid-flash')),
    'gpt-image-2': ('GPT Image 2', {'zh': f'ChatGPT 图像 2.0 同款，输出 ${T2} / 1M', 'en': f'The model behind ChatGPT Images 2.0, ${T2} / 1M'},
                    {'zh': ['约 0.8 折', '中文渲染', '并发不限'], 'en': ['92% off', 'Text rendering', 'Unlimited concurrency']}, ('chinese-comic', 'rice-macro')),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#fff;color:#000;font-family:Inter,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;position:relative;overflow:hidden}
.c{position:absolute;left:72px;top:68px;width:600px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;letter-spacing:-.01em}
.b svg{width:28px;height:28px}
.s{display:inline-flex;gap:6px;margin-left:8px}.s i{display:block;width:14px;height:14px}.s i:nth-child(1){background:#e8412c;border-radius:50%}.s i:nth-child(2){background:#2c67c5}.s i:nth-child(3){width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:14px solid #f6c543}
h1{margin:96px 0 0;font-size:@FSpx;line-height:1.02;font-weight:500;letter-spacing:-.035em}
p{margin:22px 0 0;font-size:30px;line-height:1.3;color:rgba(0,0,0,.66);letter-spacing:-.01em}
.r{position:absolute;left:72px;bottom:64px;display:flex;gap:10px}
.r span{padding:9px 18px;border-radius:999px;background:rgba(0,0,0,.05);font-size:21px;white-space:nowrap}
.r span.d{background:#000;color:#fff;font-weight:600}
.g{position:absolute;right:56px;top:56px;bottom:56px;width:430px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.g div{border-radius:8px;background-size:cover;background-position:center}
</style></head><body><div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#000" fill-rule="evenodd"><path d="@LOGO"/></svg>AnyAIGC<span class="s"><i></i><i></i><i></i></span></div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><div style="background-image:url(/assets/models/gpt-image/@IMG1.webp)"></div><div style="background-image:url(/assets/models/gpt-image/@IMG2.webp)"></div></div>
</body></html>'''


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for slug in SLUGS:
        title, sub, tags, (a, b) = DATA[slug]
        for lang in ('zh', 'en'):
            fs = 78 if len(title) <= 13 else (64 if len(title) <= 19 else 56)
            t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(tags[lang]))
            h = (TPL.replace('@FS', str(fs)).replace('@LOGO', LOGO).replace('@TITLE', title).replace('@SUB', sub[lang])
                 .replace('@TAGS', t).replace('@IMG1', a).replace('@IMG2', b))
            name = f'{slug}-{lang}'
            io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(h)
            jobs.append(name)
    run = lambda *a: subprocess.run(['bash', CLI, '-s=og', *a], capture_output=True, text=True)
    run('open', 'about:blank')
    run('resize', '1200', '630')
    for name in jobs:
        run('goto', f'http://localhost:8765/.playwright-mcp/og/gpt-image/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
