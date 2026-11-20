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

NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
# 英文图用海外口径：自助开票（2026-11-17 起非中文口径）；中文图保持「对公 · 专票」
ENT = {'zh': '对公 · 专票', 'en': 'Self-service invoices', 'ja': '請求書を自分で発行', 'ko': '인보이스 직접 발급',
       'es': 'Facturas en consola', 'de': 'Rechnungen im Konto'}
# 新语言标签词表，键是英文原文；缺词直接 KeyError，不回退英文
TXT = {
    'Claude Code': {'ja': 'Claude Code', 'ko': 'Claude Code', 'es': 'Claude Code', 'de': 'Claude Code'},
    'Unlimited RPM': {'ja': '同時実行数の上限なし', 'ko': '동시 실행 제한 없음', 'es': 'Sin límite de RPM', 'de': 'Kein RPM-Limit'},
    '1M context': {'ja': 'コンテキスト長1M', 'ko': '1M 컨텍스트', 'es': '1M de contexto', 'de': '1M Kontext'},
    '256K context': {'ja': 'コンテキスト長256K', 'ko': '256K 컨텍스트', 'es': '256K de contexto', 'de': '256K Kontext'},
    'Image input': {'ja': '画像入力', 'ko': '이미지 입력', 'es': 'Entrada de imágenes', 'de': 'Bildeingabe'},
}
PRICE_FMT = {'ja': '{p} / 1M 入力', 'ko': '{p} / 1M 입력', 'es': '{p} / 1M entrada', 'de': '{p} / 1M Eingabe'}
PRICE_FROM = {'ja': '{p} / 1M 入力から', 'ko': '{p} / 1M 입력부터', 'es': 'Desde {p} / 1M entrada', 'de': 'Ab {p} / 1M Eingabe'}
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

SUB_I18N = {
    'glm': {'ja': 'GLM-5.3、GLM-5.3-Flash、GLM-5.2 を1つのキーで', 'ko': 'GLM-5.3, GLM-5.3-Flash, GLM-5.2를 키 하나로',
            'es': 'GLM-5.3, GLM-5.3-Flash y GLM-5.2 con una sola clave', 'de': 'GLM-5.3, GLM-5.3-Flash und GLM-5.2 mit einem Key'},
    'glm-5.3': {'ja': 'Zhipuの最新フラッグシップ、約30%オフ', 'ko': 'Zhipu의 최신 플래그십, 약 30% 할인',
                'es': 'El buque insignia más reciente de Zhipu, ~30 % menos', 'de': 'Zhipus neuestes Flaggschiff, rund 30 % Rabatt'},
    'glm-5.3-flash': {'ja': 'ネイティブマルチモーダルで低コスト、約60%オフ', 'ko': '네이티브 멀티모달, 저렴한 가격, 약 60% 할인',
                      'es': 'Multimodal nativo y de bajo coste, ~60 % menos', 'de': 'Nativ multimodal und günstig, rund 60 % Rabatt'},
    'glm-5.2': {'ja': '長期タスク向けフラッグシップ、約30%オフ', 'ko': '장기 작업용 플래그십, 약 30% 할인',
                'es': 'Buque insignia para tareas largas, ~30 % menos', 'de': 'Flaggschiff für lange Aufgaben, rund 30 % Rabatt'},
}


def loc(slug, lang, sub, price, tags):
    """返回该语言的 (副标题, 价格标签, 其余标签)；新语言缺词直接报错，不回退英文。"""
    if lang not in NEW:
        return sub[lang], price[lang], tags[lang]
    en = price['en']
    p = '$' + en.replace('From ', '').split(' / ')[0].lstrip('$')
    fmt = PRICE_FROM if en.startswith('From ') else PRICE_FMT
    # 百分号前用不换行空格，避免 “60 %” 被折行拆开
    return SUB_I18N[slug][lang].replace(' %', ' %'), fmt[lang].format(p=p), [TXT[t][lang] for t in tags['en']]


TPL = '''<!doctype html><html lang="@LANG"><head><meta charset="utf-8"><style>
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
body.n{font-family:Arial,"Yu Gothic UI","Yu Gothic","Malgun Gothic","Segoe UI",sans-serif}
.n p{font-size:30px;max-width:790px}
.k p{word-break:keep-all}
.n .r span{font-size:21px;padding:11px 17px;white-space:nowrap}
</style></head><body class="@BC"><div class="glow"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· Zhipu GLM</em></div><h1>@NAME<span>@KEY</span></h1><p>@SUB</p></div>
<div class="r">@CHIPS</div></body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    os.makedirs(OUT, exist_ok=True)
    names = []
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    for lang in (only[0] if only else ('zh', 'en')):
        for slug, (name, key, sub, price, tags) in PAGES.items():
            if not os.path.exists(os.path.join(ROOT, 'en' if lang in NEW else lang, 'models', slug + '.html')):
                continue
            sub_l, price_l, tags_l = loc(slug, lang, sub, price, tags)
            chips = f'<span class="d">{price_l}</span>' + ''.join(f'<span>{t}</span>' for t in tags_l + [ENT[lang]])
            fs = '132' if len(name + key) <= 10 else '116'
            # 总览页标题 "GLM API" 中间要空格，型号页 "GLM-5.3" 不要
            nm = name + ' ' if slug == 'glm' else name
            html = (TPL.replace('@LOGO', logo(cls='')).replace('@SMALL', logo(cls='')).replace('@BRAND', BRAND).replace('@NAME', nm)
                    .replace('@KEY', key).replace('@SUB', sub_l).replace('@LANG', LANGATTR[lang]).replace('@BC', ('n' + (' k' if lang == 'ko' else '')) if lang in NEW else '').replace('@CHIPS', chips).replace('@FS', fs))
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
        os.remove(os.path.join(OUT, n + '.html'))


if __name__ == '__main__':
    main()
