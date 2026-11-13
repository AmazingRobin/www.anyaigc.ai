# 生成 Eleven（ElevenLabs）系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_eleven.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 风格跟 assets/models/eleven.css 一致：近白底、黑色大字、官网 v4 橙红 → 绿渐变艺术图（非 v4 型号用灰色流线图）、黑色胶囊价格标签
# logo 读 assets/icons/elevenlabs.svg（lobe-icons，见 scripts/icons.py）
import glob
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eleven_data import PRICE, SLUGS  # noqa: E402
from eleven_layout import logo, HERO_IMG  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

ENT = {'zh': '对公 · 专票', 'en': 'Contracts · invoices'}
UNIT = {'zh': '/ 万字符', 'en': '/ 10K chars'}
DEAL = {'zh': '约官方 8.1 折', 'en': '19% off list price'}
TAGS = {'zh': '并发不限', 'en': 'Unlimited RPM'}
# 每个页面：标题关键词（接在 Eleven 后面）、一句卖点
PAGES = {
    'eleven-v4': ('v4', {'zh': '旗舰语音合成，有声书与专业配音', 'en': 'Flagship text-to-speech for audiobooks and voiceover'}),
    'eleven-v4-turbo': ('v4 Turbo', {'zh': '低延迟语音合成，适合语音助手', 'en': 'Low-latency text-to-speech for voice agents'}),
    'eleven-v3': ('v3', {'zh': '戏剧化配音，故事与短剧', 'en': 'Dramatic voiceover for stories and short dramas'}),
    'eleven-v3-conversational': ('v3 Conversational', {'zh': '对话语音，口语自然', 'en': 'Conversational speech with a natural tone'}),
    'eleven-multilingual-v2': ('Multilingual v2', {'zh': '长文本稳定，双语混读', 'en': 'Stable long-form and mixed-language reading'}),
    'eleven-flash-v2-5': ('Flash v2.5', {'zh': '超长文本，批量字幕配音', 'en': 'Very long text and bulk subtitle voiceover'}),
    'eleven-flash-v2': ('Flash v2', {'zh': '轻量高速，英语短句播报', 'en': 'Light and fast English announcer'}),
}
assert list(PAGES) == SLUGS

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html{overflow:hidden;background:#fdfcfc}
body{margin:0;width:1200px;height:630px;background:#fdfcfc;color:#0c0a09;font-family:-apple-system,"Segoe UI",Roboto,Arial,"PingFang SC","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.art{position:absolute;inset:0 0 0 38%;background:url(/assets/models/eleven/@IMG) center/cover no-repeat;-webkit-mask-image:linear-gradient(to right,transparent 0,#000 46%);mask-image:linear-gradient(to right,transparent 0,#000 46%)}
.mark{position:absolute;right:84px;top:92px;width:210px;height:210px;padding:56px;border-radius:52px;background:#0c0a09;box-shadow:0 10px 44px rgba(28,25,23,.28)}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:64px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:700;letter-spacing:-.02em;color:#1c1917}
.b em{font-style:normal;font-weight:500;color:#77716a}
.b svg{width:28px;height:28px}
h1{margin:64px 0 0;max-width:900px;font-size:@FSpx;line-height:1.02;font-weight:300;letter-spacing:-.035em;color:#0c0a09}
h1 span{background:linear-gradient(100deg,#e8502a 4%,#f08a5d 46%,#6f9a4a 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-weight:400}
p{margin:26px 0 0;font-size:34px;line-height:1.3;font-weight:500;color:#44403c;max-width:720px}
.r{position:absolute;left:80px;bottom:56px;display:flex;gap:12px}
.r span{padding:12px 20px;border-radius:999px;background:rgba(255,255,255,.9);border:1.5px solid #e7e3df;font-size:24px;color:#44403c}
.r .d{background:#0c0a09;color:#fff;border-color:#0c0a09}
.r .o{background:linear-gradient(100deg,#e8502a,#f08a5d 55%,#6f9a4a);color:#fff;border-color:transparent}
</style></head><body><div class="art"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· ElevenLabs</em></div><h1>Eleven <span>@KEY</span></h1><p>@SUB</p></div>
<div class="r">@CHIPS</div></body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    os.makedirs(OUT, exist_ok=True)
    names = []
    for lang in ('zh', 'en'):
        for slug, (key, sub) in PAGES.items():
            if not os.path.exists(os.path.join(ROOT, lang, 'models', slug + '.html')):
                continue
            chips = (f'<span class="d">${PRICE[slug]} {UNIT[lang]}</span><span class="o">{DEAL[lang]}</span>'
                     f'<span>{TAGS[lang]}</span><span>{ENT[lang]}</span>')
            fs = 112 if len(key) <= 8 else 84
            html = (TPL.replace('@IMG', HERO_IMG[slug]).replace('@LOGO', logo(cls='', fill='#ffffff'))
                    .replace('@SMALL', logo(cls='', fill='#0c0a09')).replace('@BRAND', BRAND)
                    .replace('@KEY', key).replace('@SUB', sub[lang]).replace('@CHIPS', chips).replace('@FS', str(fs)))
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))
    exe = chrome()
    if '--html-only' in sys.argv or not exe:
        return
    for n in names:
        png = os.path.join(ROOT, 'assets', 'og', n + '.png')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        # 无头 Chrome 的窗口尺寸含浏览器边框，截图会偏大，这里放大窗口再裁成 1200×630
        from PIL import Image
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        print('png', os.path.relpath(png, ROOT), os.path.getsize(png) if os.path.exists(png) else 'MISSING')


if __name__ == '__main__':
    main()
