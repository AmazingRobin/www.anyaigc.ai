# 生成 Jev 系列专题页分享图（1200×630）的 HTML 源文件，输出到 .playwright-mcp/og/，再用 Playwright 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_jev.py → 在 http://localhost:8765/.playwright-mcp/og/<name>.html 截图（1200×630）
# 风格跟 assets/models/jev.css 一致：纸白 #FEFEFE、墨黑 #1E1E1E、粉 #F386A1、品红 #E551BA；直角、1px 细线、点阵、黑色标题栏的系统窗口
# logo 读 assets/icons/typesafeai.svg（lobe-icons，见 scripts/icons.py）
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写
PRICE = {'zh': '$0.0227 / 1M 输入', 'en': '$0.0227 / 1M input'}

# 每个页面：显示名、一句卖点、3 个标签（价格标签另加在最前）
PAGES = {
    'jev':        ('Jev API',
                   {'zh': '不生成文字，直接给出带概率的判断', 'en': 'No prose. Just decisions with probabilities.'},
                   {'zh': ['输出免费', '并发不限', '对公 · 专票'], 'en': ['Free output', 'Unlimited RPM', 'Contracts · invoices']}),
    'jev-1.14.0': ('jev-1.14.0',
                   {'zh': 'Jev 1.14：256k 上下文，还能看图定位', 'en': 'Jev 1.14: 256k context, image input'},
                   {'zh': ['输出免费', '256k 上下文', '对公 · 专票'], 'en': ['Free output', '256k context', 'Contracts · invoices']}),
    'jev-1.13.0': ('jev-1.13.0',
                   {'zh': '首个公开的 System One 决策模型', 'en': 'The first public System One model'},
                   {'zh': ['输出免费', '并发不限', '对公 · 专票'], 'en': ['Free output', 'Unlimited RPM', 'Contracts · invoices']}),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
body{margin:0;width:1200px;height:630px;background:#FEFEFE;color:#1E1E1E;font-family:Inter,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(30,30,30,.22) 1.2px,transparent 1.4px);background-size:22px 22px}
.band{position:absolute;left:0;right:0;top:404px;height:84px;background:#F386A1}
.win{position:absolute;left:56px;top:56px;width:1088px;height:518px;background:#FEFEFE;border:1px solid #1E1E1E}
.bar{height:34px;background:#1E1E1E;color:#FEFEFE;display:flex;align-items:center;justify-content:space-between;padding:0 14px;font:500 17px "JetBrains Mono",Consolas,monospace}
.bar i{display:flex;gap:8px}.bar i b{width:12px;height:12px;border:1.5px solid #FEFEFE;display:block}
.c{padding:44px 56px 0}
.b{display:flex;align-items:center;gap:14px;font-size:26px;font-weight:700;letter-spacing:-.01em}
.b svg{width:34px;height:34px;padding:3px;border:1px solid #1E1E1E;background:#FEFEFE}
.b em{font-style:normal;font-weight:500;color:rgba(30,30,30,.6)}
h1{margin:54px 0 0;font-size:@FSpx;line-height:1;font-weight:800;letter-spacing:-.04em;white-space:nowrap}
p{margin:22px 0 0;font-size:34px;line-height:1.3;color:rgba(30,30,30,.86);letter-spacing:-.01em;white-space:nowrap}
.r{position:absolute;left:56px;bottom:44px;display:flex;gap:12px}
.r span{padding:10px 18px;border:1px solid #1E1E1E;background:#FEFEFE;font-size:23px;white-space:nowrap}
.r span.d{background:#1E1E1E;color:#FEFEFE;font-weight:600}
.r span.p{background:#F386A1}
.mark{position:absolute;right:56px;top:78px;width:150px;height:150px;border:1px solid #1E1E1E;background:#FEFEFE;padding:20px}
.mark svg{width:100%;height:100%}
.mark:before,.mark:after{content:"";position:absolute;width:16px;height:16px;border:2px solid #E551BA}
.mark:before{left:-9px;top:-9px;border-right:0;border-bottom:0}
.mark:after{right:-9px;bottom:-9px;border-left:0;border-top:0}
</style></head><body><div class="dots"></div><div class="band"></div>
<div class="win"><div class="bar"><span>@BAR</span><i><b></b><b></b></i></div>
<div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#1E1E1E"><path d="@LOGO"/></svg>@BRAND<em>· TypeSafe Jev</em></div><h1>@NAME</h1><p>@SUB</p></div>
<div class="mark"><svg viewBox="0 0 24 24" fill="#1E1E1E"><path d="@LOGO"/></svg></div>
<div class="r">@CHIPS</div></div></body></html>'''


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = re.search(r' d="([^"]+)"', read('assets/icons/typesafeai.svg')).group(1)
    names = []
    for lang in ('zh', 'en'):
        for slug, (name, sub, tags) in PAGES.items():
            if not os.path.exists(os.path.join(ROOT, lang, 'models', slug + '.html')):
                continue
            chips = f'<span class="d">{PRICE[lang]}</span><span class="p">{tags[lang][0]}</span>' + ''.join(f'<span>{t}</span>' for t in tags[lang][1:])
            fs = '132' if len(name) <= 8 else '118'
            html = (TPL.replace('@LOGO', logo).replace('@BRAND', BRAND).replace('@NAME', name)
                    .replace('@SUB', sub[lang]).replace('@CHIPS', chips).replace('@FS', fs)
                    .replace('@BAR', f'POST /v1/systemone · {slug}'))
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))


if __name__ == '__main__':
    main()
