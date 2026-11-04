# 生成 Grok Video 系列专题页分享图（1200×630）：python scripts/og_grok_video.py
# 先写 HTML 到 .playwright-mcp/og/grok-video/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grok_video_data import SLUGS, MODELS, cny  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'grok-video')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
LOGO = re.search(r'<path d="([^"]+)"', io.open(os.path.join(ROOT, 'assets/icons/grok.svg'), encoding='utf-8').read()).group(1)
P = lambda s, lang: f'¥{cny(MODELS[s]["usd"])}' if lang == 'zh' else f'${MODELS[s]["usd"]}'

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧图片：视频封面帧)
DATA = {
    'grok-video': ('Grok Video API', {'zh': f'xAI 全系视频模型，{P("grok-imagine-video-1.5-lite", "zh")} / 秒起', 'en': f'Every xAI video model, from {P("grok-imagine-video-1.5-lite", "en")} / sec'},
                   {'zh': ['3 个型号', '原生声音', '对公 · 专票'], 'en': ['3 models', 'Native audio', 'Contracts · invoices']}, ('speech-2', 'perfume')),
    'grok-imagine-video-1.5-preview': ('Grok Imagine Video 1.5', {'zh': f'画面与对白一起生成，{P("grok-imagine-video-1.5-preview", "zh")} / 秒起', 'en': f'Video with lip-synced speech, from {P("grok-imagine-video-1.5-preview", "en")} / sec'},
                                       {'zh': ['1–15 秒', '图生视频', '并发不限'], 'en': ['1–15 seconds', 'Image to video', 'Unlimited concurrency']}, ('speech-1', 'try-on')),
    'grok-imagine-video-1.5-lite': ('Grok Imagine Video 1.5 Lite', {'zh': f'系列最低价，{P("grok-imagine-video-1.5-lite", "zh")} / 秒起', 'en': f'Lowest price in the series, from {P("grok-imagine-video-1.5-lite", "en")} / sec'},
                                    {'zh': ['最高 1080p', '原生声音', '并发不限'], 'en': ['Up to 1080p', 'Native audio', 'Unlimited concurrency']}, ('property', 'dining')),
    'grok-imagine-video': ('Grok Imagine Video', {'zh': f'支持改视频，{P("grok-imagine-video", "zh")} / 秒起', 'en': f'Generate and edit video, from {P("grok-imagine-video", "en")} / sec'},
                           {'zh': ['改视频', '原生声音', '并发不限'], 'en': ['Video editing', 'Native audio', 'Unlimited concurrency']}, ('restyle-a', 'edit-a')),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#fff;color:#0a0a0a;font-family:Inter,"Segoe UI","PingFang SC","Microsoft YaHei",system-ui,sans-serif;position:relative;overflow:hidden}
.c{position:absolute;left:72px;top:68px;width:620px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;letter-spacing:-.02em}
.b svg{width:30px;height:30px}
.b i{width:1px;height:22px;background:rgba(10,10,10,.2)}
.b span{font-weight:500;color:rgba(10,10,10,.6)}
h1{margin:92px 0 0;font-size:@FSpx;line-height:1.04;font-weight:500;letter-spacing:-.03em}
p{margin:22px 0 0;font-size:29px;line-height:1.35;color:rgba(10,10,10,.66);letter-spacing:-.01em}
.r{position:absolute;left:72px;bottom:64px;display:flex;gap:10px}
.r span{padding:9px 18px;border-radius:999px;background:#f2f1ef;font-size:21px;white-space:nowrap}
.r span.d{background:#0a0a0a;color:#fff;font-weight:600}
.g{position:absolute;right:56px;top:56px;bottom:56px;width:410px;display:grid;grid-template-rows:1fr 1fr;gap:12px}
.g div{border-radius:16px;background-size:cover;background-position:center}
</style></head><body><div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#0a0a0a" fill-rule="evenodd"><path d="@LOGO"/></svg>AnyAIGC<i></i><span>xAI</span></div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><div style="background-image:url(/assets/models/grok-video/@IMG1.webp)"></div><div style="background-image:url(/assets/models/grok-video/@IMG2.webp)"></div></div>
</body></html>'''


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for slug in SLUGS:
        title, sub, tags, (a, b) = DATA[slug]
        for lang in ('zh', 'en'):
            fs = 76 if len(title) <= 16 else (62 if len(title) <= 22 else 54)
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
        run('goto', f'http://localhost:8765/.playwright-mcp/og/grok-video/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
