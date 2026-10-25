# 生成 Gemini 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_gemini.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 风格跟 assets/models/gemini.css 一致：纯白底、#121317 墨色、Gemini 渐变（#217bfe → #078efb → #ac87eb → #ee4d5d）光晕和标题关键词
# logo 读 assets/icons/gemini-color.svg（lobe-icons，见 scripts/icons.py）
import glob
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

# 每个页面：标题前半、渐变关键词、一句卖点、价格标签、其余标签
PAGES = {
    'gemini-4-argon': ('Gemini 4', 'Argon',
                       {'zh': 'Google 旗舰推理模型，约官方价 1 折', 'en': "Google's flagship reasoning model, ~90% off"},
                       {'zh': '$0.1985 / 1M 输入', 'en': '$0.1985 / 1M input'},
                       {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Contracts · invoices']}),
    'gemini-3.8-flash': ('Gemini 3.8', 'Flash',
                         {'zh': 'Google 最强 Flash，快且便宜', 'en': "Google's most capable Flash model"},
                         {'zh': '$0.0744 / 1M 输入', 'en': '$0.0744 / 1M input'},
                         {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Contracts · invoices']}),
    'gemini-3.7-flash': ('Gemini 3.7', 'Flash',
                         {'zh': '旧代码照常调用，推荐升级 3.8 Flash', 'en': 'Legacy calls keep working. 3.8 Flash recommended.'},
                         {'zh': '$0.0744 / 1M 输入', 'en': '$0.0744 / 1M input'},
                         {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Contracts · invoices']}),
    'gemini-3.1-pro-preview': ('Gemini 3.1', 'Pro',
                               {'zh': 'Gemini 3 代 Pro 预览版，复杂推理与多模态', 'en': 'Gemini 3 Pro preview for complex reasoning'},
                               {'zh': '$0.1985 / 1M 输入', 'en': '$0.1985 / 1M input'},
                               {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Contracts · invoices']}),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
body{margin:0;width:1200px;height:630px;background:#fff;color:#121317;font-family:"Google Sans Flex","Google Sans",Inter,"Segoe UI",Arial,"PingFang SC","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.g1,.g2{position:absolute;border-radius:50%;filter:blur(80px)}
.g1{width:760px;height:520px;right:-180px;top:-160px;background:radial-gradient(closest-side,rgba(33,123,254,.55),rgba(7,142,251,.22) 60%,transparent)}
.g2{width:620px;height:420px;right:60px;top:220px;background:radial-gradient(closest-side,rgba(172,135,235,.5),rgba(238,77,93,.2) 60%,transparent)}
.mark{position:absolute;right:64px;top:110px;width:220px;height:220px}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:72px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:600;letter-spacing:-.02em}
.b em{font-style:normal;font-weight:400;color:#5f6368}
.b svg{width:30px;height:30px}
h1{margin:96px 0 0;max-width:860px;font-size:@FSpx;line-height:1;font-weight:450;letter-spacing:-.035em}
h1 span{background:linear-gradient(90deg,#217bfe 0%,#078efb 33.53%,#ac87eb 67.74%,#ee4d5d 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
p{margin:26px 0 0;font-size:34px;line-height:1.3;color:#45474d;max-width:700px}
.r{position:absolute;left:80px;bottom:64px;display:flex;gap:12px}
.r span{padding:12px 20px;border-radius:999px;background:#f8f9fc;border:1px solid rgba(33,34,38,.1);font-size:24px;color:#45474d}
.r .d{background:#121317;color:#fff;border-color:#121317}
.line{position:absolute;left:0;right:0;bottom:0;height:8px;background:linear-gradient(90deg,#217bfe 0%,#078efb 33.53%,#ac87eb 67.74%,#ee4d5d 100%)}
</style></head><body><div class="g1"></div><div class="g2"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· Google Gemini</em></div><h1>@NAME <span>@KEY</span></h1><p>@SUB</p></div>
<div class="r">@CHIPS</div><div class="line"></div></body></html>'''


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = read('assets/icons/gemini-color.svg')
    names = []
    for lang in ('zh', 'en'):
        for slug, (name, key, sub, price, tags) in PAGES.items():
            if not os.path.exists(os.path.join(ROOT, lang, 'models', slug + '.html')):
                continue
            chips = f'<span class="d">{price[lang]}</span>' + ''.join(f'<span>{t}</span>' for t in tags[lang])
            fs = '120' if len(name + key) <= 14 else '108'
            small = logo.replace('lobe-icons-gemini-', 'sm-')
            html = (TPL.replace('@LOGO', logo).replace('@SMALL', small).replace('@BRAND', BRAND).replace('@NAME', name)
                    .replace('@KEY', key).replace('@SUB', sub[lang]).replace('@CHIPS', chips).replace('@FS', fs))
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))
    exe = chrome()
    if '--html-only' in sys.argv or not exe:
        return
    for n in names:
        png = os.path.join(ROOT, 'assets', 'og', n + '.png')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1200,800',
                        '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        # 无头 Chrome 的窗口尺寸含浏览器边框，截得偏矮；放大窗口再裁成 1200×630
        from PIL import Image
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        print('png', os.path.relpath(png, ROOT), os.path.getsize(png) if os.path.exists(png) else 'MISSING')


if __name__ == '__main__':
    main()
