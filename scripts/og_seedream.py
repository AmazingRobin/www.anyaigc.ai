# 生成 Seedream 系列专题页分享图（1200×630）：python scripts/og_seedream.py
# 先写 HTML 到 .playwright-mcp/og/seedream/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）。右侧 2×2 用官方示例图（与首屏相同），3.0 用 seedream.css 的 .sd-tile 示意图。
# 加 --langs=ja,ko,es,de（或 --langs=en）只生成指定语言：用 Chrome headless 截图、Pillow 裁成 1200×630、删临时 html。
# 不带 --langs：保持原样，用 playwright-cli 出 zh、en。
import glob
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seedream_data import SLUGS, cny, usd  # noqa: E402
import seedream_gallery as GL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'seedream')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
_raw = io.open(os.path.join(ROOT, 'assets/icons/bytedance-color.svg'), encoding='utf-8').read()
ICON = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S)

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧 4 块示意图)
DATA = {
    'seedream': ('Seedream API', {'zh': f'字节跳动全系生图模型，按张 {cny("seedream-5.0-lite")} 起', 'en': f'Every Seedream model, from {usd("seedream-5.0-lite")} / image'},
                 {'zh': ['5.0 Pro · lite · 4.5 · 4.0', '对公 · 专票'], 'en': ['5.0 Pro · lite · 4.5 · 4.0', 'Self-service invoices']},
                 ('info', 'edit', 'seq', 'lang')),
    'seedream-5.0-pro': ('Seedream 5.0 Pro', {'zh': f'旗舰生图模型，每张 {cny("seedream-5.0-pro")} 起', 'en': f'The flagship model, from {usd("seedream-5.0-pro")} / image'},
                         {'zh': ['高密度信息图', '精准编辑', '并发不限'], 'en': ['Infographics', 'Precise edits', 'Unlimited concurrency']},
                         ('info', 'edit', 'photo', 'lang')),
    'seedream-5.0-lite': ('Seedream 5.0 lite', {'zh': f'4K 与联网检索，每张 {cny("seedream-5.0-lite")} 起', 'en': f'4K and web search, from {usd("seedream-5.0-lite")} / image'},
                          {'zh': ['4K', '组图', '并发不限'], 'en': ['4K', 'Image sets', 'Unlimited concurrency']},
                          ('search', 'seq', 'multi', 'type')),
    'seedream-4.5': ('Seedream 4.5', {'zh': f'海报排版与多图融合，每张 {cny("seedream-4.5")} 起', 'en': f'Posters and multi-image blends, from {usd("seedream-4.5")}'},
                     {'zh': ['海报排版', '4K', '并发不限'], 'en': ['Typography', '4K', 'Unlimited concurrency']},
                     ('type', 'photo', 'multi', 'seq')),
    'seedream-4.0': ('Seedream 4.0', {'zh': f'生成编辑一体，每张 {cny("seedream-4.0")} 起', 'en': f'Generate and edit, from {usd("seedream-4.0")} / image'},
                     {'zh': ['组图 15 张', '4K', '并发不限'], 'en': ['Up to 15 images', '4K', 'Unlimited concurrency']},
                     ('seq', 'edit', 'multi', 'info')),
    'seedream-3.0': ('Seedream 3.0', {'zh': f'中英双语文生图，每次 {cny("seedream-3.0")}', 'en': f'Bilingual text-to-image, {usd("seedream-3.0")} / request'},
                     {'zh': ['原生 2K', '文生图', '并发不限'], 'en': ['Native 2K', 'Text-to-image', 'Unlimited concurrency']},
                     ('type', 'photo', 'info', 'lang')),
}

NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}


def _t(ja, ko, es, de):
    return {'ja': ja, 'ko': ko, 'es': es, 'de': de}


# 英文标签 -> 新语言（缺词直接 KeyError，不回退英文）
TAG_I18N = {
    '5.0 Pro · lite · 4.5 · 4.0': _t('5.0 Pro · lite · 4.5 · 4.0', '5.0 Pro · lite · 4.5 · 4.0', '5.0 Pro · lite · 4.5 · 4.0', '5.0 Pro · lite · 4.5 · 4.0'),
    'Self-service invoices': _t('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
    'Unlimited concurrency': _t('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    'Infographics': _t('インフォグラフィック', '인포그래픽', 'Infografías', 'Infografiken'),
    'Precise edits': _t('精密な編集', '정밀 편집', 'Ediciones precisas', 'Präzise Bearbeitung'),
    '4K': _t('4K', '4K', '4K', '4K'),
    'Image sets': _t('画像セット', '이미지 세트', 'Conjuntos de imágenes', 'Bildserien'),
    'Typography': _t('タイポグラフィ', '타이포그래피', 'Tipografía', 'Typografie'),
    'Up to 15 images': _t('最大15枚', '최대 15장', 'Hasta 15 imágenes', 'Bis zu 15 Bilder'),
    'Native 2K': _t('ネイティブ 2K', '네이티브 2K', '2K nativo', 'Natives 2K'),
    'Text-to-image': _t('テキストから画像', '텍스트→이미지', 'Texto a imagen', 'Text-zu-Bild'),
}
# 新语言副标题，参数 u 为美元价（与英文图一致）
SUB_I18N = {
    'seedream': lambda u: _t(f'Seedream 全モデル、1枚 {u} から', f'Seedream 전 모델, 이미지당 {u}부터',
                             f'Todos los modelos Seedream, desde {u} / imagen', f'Alle Seedream-Modelle, ab {u} / Bild'),
    'seedream-5.0-pro': lambda u: _t(f'フラッグシップモデル、1枚 {u} から', f'플래그십 모델, 이미지당 {u}부터',
                                     f'El modelo insignia, desde {u} / imagen', f'Das Flaggschiff, ab {u} / Bild'),
    'seedream-5.0-lite': lambda u: _t(f'4K とウェブ検索、1枚 {u} から', f'4K와 웹 검색, 이미지당 {u}부터',
                                      f'4K y búsqueda web, desde {u} / imagen', f'4K und Websuche, ab {u} / Bild'),
    'seedream-4.5': lambda u: _t(f'ポスターのレイアウトと複数画像の合成、{u} から', f'포스터 레이아웃과 다중 이미지 합성, {u}부터',
                                 f'Pósteres y fusión de varias imágenes, desde {u}', f'Poster und Mehrbild-Kompositionen, ab {u}'),
    'seedream-4.0': lambda u: _t(f'生成と編集を1つに、1枚 {u} から', f'생성과 편집을 하나로, 이미지당 {u}부터',
                                 f'Generar y editar, desde {u} / imagen', f'Erzeugen und bearbeiten, ab {u} / Bild'),
    'seedream-3.0': lambda u: _t(f'中英バイリンガルのテキストから画像、1回 {u}', f'중영 이중 언어 텍스트→이미지, 요청당 {u}',
                                 f'Texto a imagen bilingüe (chino e inglés), {u} / solicitud', f'Bilinguales Text-zu-Bild (Chinesisch/Englisch), {u} / Anfrage'),
}
USD_OF = {'seedream': 'seedream-5.0-lite'}  # 总览页用 5.0 lite 的起步价

TPL = '''<!doctype html><html class="no-js@N" lang="@LANG"><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/models/seedream.css"><style>
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:linear-gradient(180deg,#171719,#0f1013)}
body{position:relative;color:#fff;font-family:"Stack Sans Headline",Inter,"PingFang SC","Microsoft YaHei",system-ui,sans-serif}
.glow{position:absolute;inset:-30% -10% auto auto;width:75%;height:140%;background:radial-gradient(45% 45% at 70% 40%,rgba(60,86,244,.45),transparent 70%),radial-gradient(35% 35% at 40% 70%,rgba(0,200,210,.2),transparent 70%)}
.c{position:absolute;left:72px;top:64px;width:600px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;color:#fcfcfd}
.b svg{width:34px;height:34px}
h1{margin:96px 0 0;color:#fff;font-size:@FSpx;line-height:1;font-weight:600;letter-spacing:-2px}
p{margin:24px 0 0;font-size:29px;line-height:1.35;color:rgba(252,252,253,.72)}
.r{position:absolute;left:72px;bottom:62px;display:flex;gap:10px}
.r span{padding:9px 20px;border-radius:999px;background:rgba(249,249,251,.1);font-size:21px;white-space:nowrap;color:#fcfcfd}
.r span.d{background:#fff;color:#171719;font-weight:600}
.g{position:absolute;right:56px;top:50px;width:430px}
.g ul{display:grid;grid-template-columns:1fr 1fr;gap:14px;list-style:none;margin:0;padding:0}
.g .sd-tile{aspect-ratio:auto;height:250px;transform:none}
.g .sd-tile:nth-child(odd){transform:translateY(16px)}
.g .sd-tile span{font-size:15px}
.g .sd-tile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.n body{font-family:"Stack Sans Headline",Inter,"Yu Gothic UI","Malgun Gothic","Segoe UI",system-ui,sans-serif}
.n p{font-size:26px;line-height:1.4}.n .r{gap:8px}.n .r span{font-size:17px;padding:9px 16px}
.n.ko p{word-break:keep-all}.n .g .sd-tile span{font-size:14px;word-break:keep-all}
</style></head><body><div class="glow"></div><div class="c"><div class="b"><svg viewBox="0 0 24 24">@ICON</svg>AnyAIGC</div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><ul>@TILES</ul></div>
</body></html>'''

LABEL = {'zh': {'info': '信息图', 'edit': '精准编辑', 'photo': '人像质感', 'lang': '多语种', 'search': '联网检索', 'seq': '组图', 'multi': '多图融合', 'type': '海报排版'},
         'en': {'info': 'Infographics', 'edit': 'Precise edits', 'photo': 'Photoreal', 'lang': 'Multilingual', 'search': 'Web search', 'seq': 'Image sets', 'multi': 'Multi-image', 'type': 'Typography'},
         'ja': {'info': 'インフォグラフィック', 'edit': '精密な編集', 'photo': 'フォトリアル', 'lang': '多言語', 'search': 'ウェブ検索', 'seq': '画像セット', 'multi': 'マルチ画像', 'type': 'タイポグラフィ'},
         'ko': {'info': '인포그래픽', 'edit': '정밀 편집', 'photo': '실사 표현', 'lang': '다국어', 'search': '웹 검색', 'seq': '이미지 세트', 'multi': '다중 이미지', 'type': '타이포그래피'},
         'es': {'info': 'Infografías', 'edit': 'Ediciones precisas', 'photo': 'Fotorrealismo', 'lang': 'Multilingüe', 'search': 'Búsqueda web', 'seq': 'Conjuntos de imágenes', 'multi': 'Multimagen', 'type': 'Tipografía'},
         'de': {'info': 'Infografiken', 'edit': 'Präzise Bearbeitung', 'photo': 'Fotorealismus', 'lang': 'Mehrsprachig', 'search': 'Websuche', 'seq': 'Bildserien', 'multi': 'Mehrbild', 'type': 'Typografie'}}


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def texts(slug, lang):
    """返回 (副标题, 标签列表)；新语言缺词直接 KeyError，不回退英文。"""
    title, sub, tags, tiles = DATA[slug]
    if lang not in NEW:
        return sub[lang], tags[lang]
    u = usd(USD_OF.get(slug, slug))
    return SUB_I18N[slug](u)[lang], [TAG_I18N[x][lang] for x in tags['en']]


def main():
    os.makedirs(OUT, exist_ok=True)
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    langs = only[0] if only else ['zh', 'en']
    jobs = []
    for slug in SLUGS:
        title, sub, tags, tiles = DATA[slug]
        for lang in langs:
            fs = 92 if len(title) <= 13 else 76
            subtxt, taglist = texts(slug, lang)
            t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(taglist))
            keys = [f'{a}/{b}' for a, b in GL.OVERVIEW] if slug == 'seedream' else [f'{slug}/{k}' for k in GL.PICK[slug]['hero']] if slug in GL.PICK else None
            if keys:
                tl = ''.join(f'<li class="sd-tile"><img src="/assets/models/seedream/{GL.IMAGES[k]["file"]}" alt=""></li>' for k in keys)
            else:
                tl = ''.join(f'<li class="sd-tile sd-tile-{k}"><span>{LABEL[lang][k]}</span></li>' for k in tiles)
            h = (TPL.replace('@FS', str(fs)).replace('@ICON', ICON).replace('@TITLE', title).replace('@SUB', subtxt)
                 .replace('@TAGS', t).replace('@TILES', tl).replace('@LANG', LANGATTR[lang])
                 .replace('@N', ' n ' + lang if lang in NEW else ''))
            name = f'{slug}-{lang}'
            io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(h)
            jobs.append(name)
    if only:
        from PIL import Image
        for name in jobs:
            hp = os.path.join(OUT, name + '.html')
            dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
            subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                            '--virtual-time-budget=6000', f'--screenshot={dst}',
                            f'http://localhost:8765/.playwright-mcp/og/seedream/{name}.html'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            Image.open(dst).crop((0, 0, 1200, 630)).save(dst, optimize=True)
            os.unlink(hp)
            print(name, os.path.getsize(dst))
        return
    run =lambda *a: subprocess.run(['bash', CLI, '-s=og', *a], capture_output=True, text=True)
    run('open', 'about:blank')
    run('resize', '1200', '630')
    for name in jobs:
        run('goto', f'http://localhost:8765/.playwright-mcp/og/seedream/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
