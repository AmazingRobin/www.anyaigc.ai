# 生成 Kimi 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_kimi.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 风格跟 assets/models/kimi.css 一致：纯黑底、白色轻字重标题、Kimi 蓝 #1783FF 关键词与光晕、描边胶囊标签
# logo 读 assets/icons/kimi-color.svg（lobe-icons，见 scripts/icons.py），K 字形在深色底填白色
import glob
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kimi_data import PRICE  # noqa: E402
from kimi_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

ENT = {'zh': '对公 · 专票', 'en': 'Contracts · invoices'}
# 每个页面：标题前半、蓝色关键词、一句卖点、价格标签、其余标签
PAGES = {
    'kimi': ('Kimi', 'API',
             {'zh': 'K3.1 Pro、K3、K2.7 Code、K2.6 一个 Key 调用', 'en': 'K3.1 Pro, K3, K2.7 Code, K2.6 with one key'},
             {'zh': f'${PRICE["kimi-k2.6"][0]} / 1M 输入起', 'en': f'From ${PRICE["kimi-k2.6"][0]} / 1M input'},
             {'zh': ['Claude Code', '并发不限'], 'en': ['Claude Code', 'Unlimited RPM']}),
    'kimi-k3.1-pro': ('Kimi K3.1', 'Pro',
                      {'zh': 'Kimi K3.1 系列首款，约官方价 4 折', 'en': 'The first Kimi K3.1 model, ~60% off'},
                      {'zh': f'${PRICE["kimi-k3.1-pro"][0]} / 1M 输入', 'en': f'${PRICE["kimi-k3.1-pro"][0]} / 1M input'},
                      {'zh': ['1M 上下文', '并发不限'], 'en': ['1M context', 'Unlimited RPM']}),
    'kimi-k3': ('Kimi', 'K3',
                {'zh': '2.8T 参数开放权重模型，约官方价 4 折', 'en': '2.8T-parameter open-weight model, ~60% off'},
                {'zh': f'${PRICE["kimi-k3"][0]} / 1M 输入', 'en': f'${PRICE["kimi-k3"][0]} / 1M input'},
                {'zh': ['1M 上下文', '并发不限'], 'en': ['1M context', 'Unlimited RPM']}),
    'kimi-k2.7-code': ('Kimi K2.7', 'Code',
                       {'zh': 'Kimi 的编程向 Agent 模型，约官方价 4 折', 'en': "Kimi's agentic coding model, ~60% off"},
                       {'zh': f'${PRICE["kimi-k2.7-code"][0]} / 1M 输入', 'en': f'${PRICE["kimi-k2.7-code"][0]} / 1M input'},
                       {'zh': ['Claude Code', '并发不限'], 'en': ['Claude Code', 'Unlimited RPM']}),
    'kimi-k2.6': ('Kimi', 'K2.6',
                  {'zh': '开源多模态 Agent 模型，约官方价 4 折', 'en': 'Open multimodal agent model, ~60% off'},
                  {'zh': f'${PRICE["kimi-k2.6"][0]} / 1M 输入', 'en': f'${PRICE["kimi-k2.6"][0]} / 1M input'},
                  {'zh': ['256K 上下文', '并发不限'], 'en': ['256K context', 'Unlimited RPM']}),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html{overflow:hidden;background:#000}
body{margin:0;width:1200px;height:630px;background:#000 radial-gradient(560px 420px at 1010px 80px,rgba(23,131,255,.42),rgba(23,131,255,.1) 55%,transparent 100%) no-repeat;color:#fff;font-family:-apple-system,"Segoe UI",Roboto,Arial,"PingFang SC","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.mark{position:absolute;right:70px;top:120px;width:250px;height:250px;padding:44px;border-radius:56px;background:#121212;border:2px solid rgba(255,255,255,.12)}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:72px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:600;letter-spacing:-.02em}
.b em{font-style:normal;font-weight:400;color:rgba(255,255,255,.56)}
.b svg{width:30px;height:30px}
h1{margin:96px 0 0;max-width:780px;font-size:@FSpx;line-height:1;font-weight:400;letter-spacing:-.035em}
h1 span{color:#1783ff}
p{margin:28px 0 0;font-size:34px;line-height:1.3;font-weight:300;color:rgba(255,255,255,.84);max-width:720px}
.r{position:absolute;left:80px;bottom:64px;display:flex;gap:12px}
.r span{padding:12px 20px;border-radius:999px;border:1.5px solid rgba(255,255,255,.42);font-size:24px;color:rgba(255,255,255,.84)}
.r .d{background:#1783ff;color:#fff;border-color:#1783ff}
</style></head><body>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· Moonshot Kimi</em></div><h1>@NAME <span>@KEY</span></h1><p>@SUB</p></div>
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
            html = (TPL.replace('@LOGO', logo(cls='')).replace('@SMALL', logo(cls='')).replace('@BRAND', BRAND).replace('@NAME', name)
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
