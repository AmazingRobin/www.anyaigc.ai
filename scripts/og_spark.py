# 生成 SparkDesk 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_spark.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 新语言 / 重出英文图：python scripts/og_spark.py --langs=ja,ko,es,de [--only=sparkdesk-v3.5]；--langs=en 只重出英文图
#   截图前量 DOM 自检，越界/重叠自动缩小字号，仍违例不出图；zh 图不在这里重出（不带 --langs 时行为保持原样）
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
import og_newlang as nl  # noqa: E402
from og_newlang import L  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

ENT = {'zh': '对公 · 专票', 'en': nl.ENT_EN}  # 英文图用海外口径：自助开票；中文图保持原样
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

# 新语言文案（事实只取上面 PAGES 的英文原文）；缺词直接 KeyError，不回退英文
SUB_I18N = {
    'sparkdesk-v3.5': L('iFLYTEK Spark の Max ティア、チャットとコード向け', 'iFLYTEK Spark Max 등급, 대화와 코드용',
                        'Nivel Max de iFLYTEK Spark para chat y código', 'iFLYTEK Spark Max-Stufe für Chat und Code'),
    'sparkdesk-v3.1': L('iFLYTEK Spark の Pro ティア、Q&A と文章作成向け', 'iFLYTEK Spark Pro 등급, Q&A와 글쓰기용',
                        'Nivel Pro de iFLYTEK Spark para preguntas y redacción', 'iFLYTEK Spark Pro-Stufe für Q&A und Texte'),
    'sparkdesk-v2.1': L('初期の Spark 2.x、3 モデルで最安', '초기 Spark 2.x 버전, 3개 중 최저가',
                        'Versión inicial de Spark 2.x, la más barata de las tres', 'Frühe Spark-2.x-Version, die günstigste der drei'),
}
TXT = {'Same in/out price': L('入力と出力は同価格', '입력·출력 동일 가격', 'Mismo precio de entrada y salida', 'Gleicher Preis für Ein- und Ausgabe')}

TPL = '''<!doctype html><html lang="@LANG"><head><meta charset="utf-8"><style>
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
.n p{font-size:30px}.n .r span{font-size:20px;padding:11px 16px}
.r{position:absolute;left:80px;bottom:56px;display:flex;gap:12px;white-space:nowrap}
.r span{padding:12px 20px;border-radius:999px;background:rgba(255,255,255,.88);border:1.5px solid #fff;box-shadow:0 3px 16px #e4e8f3;font-size:24px;color:#3d4352}
.r .d{background:linear-gradient(90deg,#3b73ff,#a75ff5);color:#fff;border-color:transparent;box-shadow:none}
</style></head><body><div class="art"></div><div class="fade"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· iFLYTEK Spark</em></div><h1>@NAME<span>@KEY</span></h1><p>@SUB</p></div>
<div class="r">@CHIPS</div></body></html>'''


def card(slug, lang):
    """返回一张图的 HTML。新语言逐项查词表，不回退英文。"""
    name, key, sub, price, tags = PAGES[slug]
    if lang in nl.NEW:
        sub_t = SUB_I18N[slug][lang]
        price_t = nl.PRICE_IN[lang].format(p=nl.money(PRICE[slug][0], lang))
        tag_l = [nl.word(t, lang, TXT) for t in tags['en'] + [ENT['en']]]
    else:
        sub_t, price_t, tag_l = sub[lang], price[lang], tags[lang] + [ENT[lang]]
    chips = f'<span class="d">{price_t}</span>' + ''.join(f'<span>{t}</span>' for t in tag_l)
    return (TPL.replace('@LANG', nl.LANGATTR[lang]).replace('@LOGO', logo(cls='')).replace('@SMALL', logo(cls='')).replace('@BRAND', BRAND)
            .replace('@NAME', name).replace('@KEY', key).replace('@SUB', sub_t).replace('@CHIPS', chips).replace('@FS', '124'))


# 版面自检配置：右上角 logo 方块不能压到文字，标签不能越出画面
CFG = {'scale': ['h1', 'p'], 'chips': ['.r span'], 'check': ['h1', 'p', '.b'], 'obst': ['.mark'], 'max': [1200, 630]}


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    langs, only, html_only = nl.parse_args(sys.argv, PAGES)
    if langs:
        jobs = [(slug, lang, card(slug, lang)) for lang in langs for slug in PAGES
                if (only is None or slug in only) and os.path.exists(os.path.join(ROOT, 'en', 'models', slug + '.html'))]
        nl.shoot(jobs, ROOT, OUT, '.playwright-mcp/og', CFG, html_only)
        return
    os.makedirs(OUT, exist_ok=True)
    names = []
    for lang in ('zh', 'en'):
        for slug in PAGES:
            if not os.path.exists(os.path.join(ROOT, lang, 'models', slug + '.html')):
                continue
            html = card(slug, lang)
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
