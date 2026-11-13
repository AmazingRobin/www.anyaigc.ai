# 生成 SparkDesk 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_spark.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 风格跟 assets/models/sparkdesk.css 一致：淡青 → 薰衣草底色 + 官网玻璃艺术图、深色标题、蓝→紫渐变关键词、白色毛玻璃标签
# logo 读 assets/icons/spark-color.svg（lobe-icons，见 scripts/icons.py）
import glob
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spark_data import PRICE  # noqa: E402
from spark_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

ENT = {'zh': '对公 · 专票', 'en': 'Contracts · invoices'}
# 每个页面：标题前半、渐变关键词、一句卖点、价格标签、其余标签
PAGES = {
    'sparkdesk-v3.5': ('SparkDesk-', 'v3.5',
                       {'zh': '讯飞星火 Max 档，对话与代码理解', 'en': 'iFLYTEK Spark Max tier for chat and code'},
                       {'zh': f'${PRICE["sparkdesk-v3.5"][0]} / 1M 输入', 'en': f'${PRICE["sparkdesk-v3.5"][0]} / 1M input'},
                       {'zh': ['输入输出同价', '并发不限'], 'en': ['Same in/out price', 'Unlimited RPM']}),
    'sparkdesk-v3.1': ('SparkDesk-', 'v3.1',
                       {'zh': '讯飞星火 Pro 档，问答与文案改写', 'en': 'iFLYTEK Spark Pro tier for Q&A and writing'},
                       {'zh': f'${PRICE["sparkdesk-v3.1"][0]} / 1M 输入', 'en': f'${PRICE["sparkdesk-v3.1"][0]} / 1M input'},
                       {'zh': ['输入输出同价', '并发不限'], 'en': ['Same in/out price', 'Unlimited RPM']}),
    'sparkdesk-v2.1': ('SparkDesk-', 'v2.1',
                       {'zh': '讯飞星火早期 2.x 版本，三款里单价最低', 'en': 'Early Spark 2.x release, the lowest price of three'},
                       {'zh': f'${PRICE["sparkdesk-v2.1"][0]} / 1M 输入', 'en': f'${PRICE["sparkdesk-v2.1"][0]} / 1M input'},
                       {'zh': ['输入输出同价', '并发不限'], 'en': ['Same in/out price', 'Unlimited RPM']}),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html{overflow:hidden;background:#f4f8ff}
body{margin:0;width:1200px;height:630px;background:linear-gradient(180deg,#e6f4ff 0,#f4f8ff 45%,#fff 100%);color:#191919;font-family:-apple-system,"Segoe UI",Roboto,Arial,"PingFang SC","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.art{position:absolute;inset:0;background:url(/assets/models/sparkdesk/hero.webp) center bottom/1500px auto no-repeat;opacity:.95}
.fade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(255,255,255,.55),rgba(255,255,255,0) 70%)}
.mark{position:absolute;right:84px;top:92px;width:230px;height:230px;padding:44px;border-radius:56px;background:rgba(255,255,255,.78);border:2px solid #fff;box-shadow:0 8px 40px rgba(25,117,255,.18)}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:64px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:700;letter-spacing:-.02em;color:#2c3045}
.b em{font-style:normal;font-weight:500;color:#566074}
.b svg{width:30px;height:30px}
h1{margin:70px 0 0;max-width:820px;font-size:@FSpx;line-height:1;font-weight:800;letter-spacing:-.03em;color:#191919}
h1 span{background:linear-gradient(90deg,#3b73ff 10%,#a75ff5 92%);-webkit-background-clip:text;background-clip:text;color:transparent}
p{margin:26px 0 0;font-size:34px;line-height:1.3;font-weight:500;color:#3d4352;max-width:760px}
.r{position:absolute;left:80px;bottom:56px;display:flex;gap:12px}
.r span{padding:12px 20px;border-radius:999px;background:rgba(255,255,255,.88);border:1.5px solid #fff;box-shadow:0 3px 16px #e4e8f3;font-size:24px;color:#3d4352}
.r .d{background:linear-gradient(90deg,#3b73ff,#a75ff5);color:#fff;border-color:transparent;box-shadow:none}
</style></head><body><div class="art"></div><div class="fade"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· iFLYTEK Spark</em></div><h1>@NAME<span>@KEY</span></h1><p>@SUB</p></div>
<div class="r">@CHIPS</div></body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    os.makedirs(OUT, exist_ok=True)
    names = []
    for lang in ('zh', 'en'):
        for slug, (name, key, sub, price, tags) in PAGES.items():
            if not os.path.exists(os.path.join(ROOT, lang, 'models', slug + '.html')):
                continue
            chips = f'<span class="d">{price[lang]}</span>' + ''.join(f'<span>{t}</span>' for t in tags[lang] + [ENT[lang]])
            html = (TPL.replace('@LOGO', logo(cls='')).replace('@SMALL', logo(cls='')).replace('@BRAND', BRAND).replace('@NAME', name)
                    .replace('@KEY', key).replace('@SUB', sub[lang]).replace('@CHIPS', chips).replace('@FS', '124'))
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


if __name__ == '__main__':
    main()
