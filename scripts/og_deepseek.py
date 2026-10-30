# 生成 DeepSeek 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png，截完删掉临时 HTML
# 用法：python scripts/og_deepseek.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 风格跟 assets/models/deepseek.css 一致：暖白底 #F9F8F8 + 顶部 #9CC1E7 冷蓝雾面渐变 + 模糊蓝色光斑 + 极淡网格、
#   细字重宽字距标题 #152443、品牌蓝 #4D6BFE 关键词、半透明白色玻璃胶囊标签、暖黑 #1A1615 价格胶囊
# logo 读 assets/icons/deepseek-color.svg（lobe-icons，见 scripts/icons.py），fill 直接写在 SVG 上
import glob
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deepseek_data import PRICE  # noqa: E402
from deepseek_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

ENT = {'zh': '对公 · 专票', 'en': 'Contracts · invoices'}
# 每个页面：标题前半、品牌蓝关键词、一句卖点、价格标签、其余标签
PAGES = {
    'deepseek': ('DeepSeek', 'API',
                 {'zh': 'V4.1 Flash、V4 Pro、V4 Flash 一个 Key 调用', 'en': 'V4.1 Flash, V4 Pro and V4 Flash with one key'},
                 {'zh': f'${PRICE["deepseek-v4.1-flash"][0]} / 1M 输入起', 'en': f'From ${PRICE["deepseek-v4.1-flash"][0]} / 1M input'},
                 {'zh': ['Claude Code', '并发不限'], 'en': ['Claude Code', 'Unlimited RPM']}),
    'deepseek-v4.1-flash': ('DeepSeek ', 'V4.1 Flash',
                            {'zh': '原生多模态，约官方高峰价 4 折', 'en': 'Natively multimodal, ~60% off official peak price'},
                            {'zh': f'${PRICE["deepseek-v4.1-flash"][0]} / 1M 输入', 'en': f'${PRICE["deepseek-v4.1-flash"][0]} / 1M input'},
                            {'zh': ['图片理解', '1M 上下文'], 'en': ['Vision', '1M context']}),
    'deepseek-v4-pro': ('DeepSeek ', 'V4 Pro',
                        {'zh': '1.6T 旗舰，三档思考强度', 'en': '1.6T flagship with three reasoning levels'},
                        {'zh': f'${PRICE["deepseek-v4-pro"][0]} / 1M 输入', 'en': f'${PRICE["deepseek-v4-pro"][0]} / 1M input'},
                        {'zh': ['思考模式', '1M 上下文'], 'en': ['Thinking', '1M context']}),
    'deepseek-v4-flash': ('DeepSeek ', 'V4 Flash',
                          {'zh': '旧版 Flash，可继续调用，同 V4.1 Flash 价', 'en': 'Legacy Flash, still callable at V4.1 Flash pricing'},
                          {'zh': f'${PRICE["deepseek-v4-flash"][0]} / 1M 输入', 'en': f'${PRICE["deepseek-v4-flash"][0]} / 1M input'},
                          {'zh': ['工具调用', '并发不限'], 'en': ['Tool calling', 'Unlimited RPM']}),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html{overflow:hidden;background:#f9f8f8}
body{margin:0;width:1200px;height:630px;background:#f9f8f8;color:#1e232c;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.mist{position:absolute;inset:0;background:linear-gradient(180deg,rgba(156,193,231,.85) 0%,rgba(156,193,231,.35) 45%,rgba(249,248,248,0) 82%)}
.blob{position:absolute;left:-120px;top:-160px;width:560px;height:460px;border-radius:50%;background:#679efe;opacity:.45;filter:blur(90px)}
.blob2{position:absolute;right:40px;top:300px;width:420px;height:320px;border-radius:50%;background:#b7c8fe;opacity:.6;filter:blur(80px)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(21,36,67,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(21,36,67,.05) 1px,transparent 1px);background-size:60px 60px;-webkit-mask-image:linear-gradient(180deg,#000,transparent 85%);mask-image:linear-gradient(180deg,#000,transparent 85%)}
.mark{position:absolute;right:80px;top:140px;width:236px;height:236px;padding:46px;border-radius:999px;background:rgba(255,255,255,.5);border:1.5px solid rgba(255,255,255,.9)}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:72px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:600;letter-spacing:-.01em;color:#152443}
.b em{font-style:normal;font-weight:400;color:#6b7586}
.b svg{width:32px;height:32px}
h1{margin:92px 0 0;max-width:800px;font-size:@FSpx;line-height:1.02;font-weight:300;letter-spacing:.01em;color:#152443}
h1 span{color:#4d6bfe;font-weight:400}
p{margin:28px 0 0;font-size:32px;line-height:1.3;font-weight:400;color:rgba(0,0,0,.66);max-width:740px}
.r{position:absolute;left:80px;bottom:64px;display:flex;gap:12px}
.r span{padding:12px 22px;border-radius:999px;background:rgba(255,255,255,.55);border:1.5px solid rgba(9,45,78,.18);font-size:24px;color:#1e232c}
.r .d{background:#1a1615;color:#fff;border-color:#1a1615}
</style></head><body><div class="mist"></div><div class="blob"></div><div class="blob2"></div><div class="grid"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· DeepSeek</em></div><h1>@NAME<span>@KEY</span></h1><p>@SUB</p></div>
<div class="r">@CHIPS</div></body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    os.makedirs(OUT, exist_ok=True)
    names = []
    for lang in ('zh', 'en'):
        for slug, (name, key, sub, price, tags) in PAGES.items():
            chips = f'<span class="d">{price[lang]}</span>' + ''.join(f'<span>{t}</span>' for t in tags[lang] + [ENT[lang]])
            fs = '112' if len(name + key) <= 12 else '92'
            # 总览页标题 "DeepSeek API" 中间要空格
            nm = name + ' ' if slug == 'deepseek' else name
            html = (TPL.replace('@LOGO', logo(cls='')).replace('@SMALL', logo(cls='')).replace('@BRAND', BRAND).replace('@NAME', nm)
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
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        # 无头 Chrome 的窗口尺寸含浏览器边框，截得偏矮；放大窗口再裁成 1200×630
        from PIL import Image
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        print('png', os.path.relpath(png, ROOT), os.path.getsize(png) if os.path.exists(png) else 'MISSING')
    # 截图完成后删掉临时 HTML
    for n in names:
        os.remove(os.path.join(OUT, n + '.html'))
    if os.path.isdir(OUT) and not os.listdir(OUT):
        os.rmdir(OUT)


if __name__ == '__main__':
    main()
