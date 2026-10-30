# 生成 GLM 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_glm.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 风格跟 assets/models/glm.css 一致：浅灰底 #F7F8FA + 淡蓝/粉紫光晕、黑色标题、蓝→紫渐变关键词、白色毛玻璃卡片标签
# logo 读 assets/icons/zhipu-color.svg（lobe-icons，见 scripts/icons.py）
import glob
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glm_data import PRICE  # noqa: E402
from glm_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

ENT = {'zh': '对公 · 专票', 'en': 'Contracts · invoices'}
# 每个页面：标题前半、渐变关键词、一句卖点、价格标签、其余标签
PAGES = {
    'glm': ('GLM', 'API',
            {'zh': 'GLM-5.3、GLM-5.3-Flash、GLM-5.2 一个 Key 调用', 'en': 'GLM-5.3, GLM-5.3-Flash, GLM-5.2 with one key'},
            {'zh': f'${PRICE["glm-5.3-flash"][0]} / 1M 输入起', 'en': f'From ${PRICE["glm-5.3-flash"][0]} / 1M input'},
            {'zh': ['Claude Code', '并发不限'], 'en': ['Claude Code', 'Unlimited RPM']}),
    'glm-5.3': ('GLM-', '5.3',
                {'zh': '智谱最新旗舰，约官方价 7 折', 'en': "Zhipu's latest flagship, ~30% off"},
                {'zh': f'${PRICE["glm-5.3"][0]} / 1M 输入', 'en': f'${PRICE["glm-5.3"][0]} / 1M input'},
                {'zh': ['1M 上下文', '并发不限'], 'en': ['1M context', 'Unlimited RPM']}),
    'glm-5.3-flash': ('GLM-5.3-', 'Flash',
                      {'zh': '原生多模态低价模型，约官方价 4 折', 'en': 'Natively multimodal and low cost, ~60% off'},
                      {'zh': f'${PRICE["glm-5.3-flash"][0]} / 1M 输入', 'en': f'${PRICE["glm-5.3-flash"][0]} / 1M input'},
                      {'zh': ['图片输入', '并发不限'], 'en': ['Image input', 'Unlimited RPM']}),
    'glm-5.2': ('GLM-', '5.2',
                {'zh': '面向长程任务的旗舰，约官方价 7 折', 'en': 'A long-horizon flagship, ~30% off'},
                {'zh': f'${PRICE["glm-5.2"][0]} / 1M 输入', 'en': f'${PRICE["glm-5.2"][0]} / 1M input'},
                {'zh': ['1M 上下文', '并发不限'], 'en': ['1M context', 'Unlimited RPM']}),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html{overflow:hidden;background:#f7f8fa}
body{margin:0;width:1200px;height:630px;background:#f7f8fa;color:#131212;font-family:-apple-system,"Segoe UI",Roboto,Arial,"PingFang SC","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.glow{position:absolute;inset:0;background:radial-gradient(420px 360px at 960px 150px,rgba(120,150,255,.5),transparent 70%),radial-gradient(360px 300px at 1120px 470px,rgba(214,170,255,.55),transparent 72%),radial-gradient(420px 260px at 160px 0,rgba(170,215,255,.55),transparent 72%)}
.mark{position:absolute;right:80px;top:130px;width:240px;height:240px;padding:44px;border-radius:40px;background:rgba(255,255,255,.72);border:2px solid #fff}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:72px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:600;letter-spacing:-.02em}
.b em{font-style:normal;font-weight:400;color:#5e5e66}
.b svg{width:30px;height:30px}
h1{margin:96px 0 0;max-width:780px;font-size:@FSpx;line-height:1;font-weight:500;letter-spacing:-.03em;color:#080808}
h1 span{background:linear-gradient(91deg,#0746ff 10%,#9747ff 90%);-webkit-background-clip:text;background-clip:text;color:transparent}
p{margin:28px 0 0;font-size:34px;line-height:1.3;font-weight:400;color:#41464f;max-width:720px}
.r{position:absolute;left:80px;bottom:64px;display:flex;gap:12px}
.r span{padding:12px 20px;border-radius:999px;background:rgba(255,255,255,.8);border:1.5px solid #fff;font-size:24px;color:#41464f}
.r .d{background:#131212;color:#fff;border-color:#131212}
</style></head><body><div class="glow"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· Zhipu GLM</em></div><h1>@NAME<span>@KEY</span></h1><p>@SUB</p></div>
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
            fs = '132' if len(name + key) <= 10 else '116'
            # 总览页标题 "GLM API" 中间要空格，型号页 "GLM-5.3" 不要
            nm = name + ' ' if slug == 'glm' else name
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


if __name__ == '__main__':
    main()
