# 生成 Nano Banana 系列专题页分享图（1200×630）：python scripts/og_nano_banana.py
# 默认（zh/en）：先写 HTML 到 .playwright-mcp/og/nano-banana/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）
#
# 新语言和英文重出走 Chrome headless 直接截图（同样需要预览服务）：
#     python scripts/og_nano_banana.py --langs=ja,ko,es,de [--only=nano-banana,nano-banana-pro]
#     python scripts/og_nano_banana.py --langs=en
# 截图前用 JS 量 DOM，标题/副标题/标签越界、重叠、间距 < 8px 或压到右侧图片时自动缩小字号再出图；
# 仍违例的卡片不出图并报错。出图后删除临时 HTML。
import glob
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nano_banana_data import SLUGS, USD, CNY, cny_min  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'nano-banana')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
_raw = io.open(os.path.join(ROOT, 'assets/icons/nanobanana-color.svg'), encoding='utf-8').read()
ICON = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S)

NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧图片)
DATA = {
    'nano-banana': ('Nano Banana API', {'zh': f'Google 全系图像模型，按张 {cny_min("nano-banana-2.1")} 起', 'en': f'Every Nano Banana model, from ${USD["nano-banana-2.1"]} / image'},
                    {'zh': ['2.1 · 2 · Pro', '4K 出图', '对公 · 专票'], 'en': ['2.1 · 2 · Pro', '4K output', 'Self-service invoices']},
                    ('desert-poster-design', 'neon-portrait')),
    'nano-banana-2.1': ('Nano Banana 2.1', {'zh': f'最新升级版，1K 每张 {cny_min("nano-banana-2.1")}', 'en': f'The latest update, from ${USD["nano-banana-2.1"]} / image'},
                        {'zh': ['4K 出图', '14 种比例', '并发不限'], 'en': ['4K output', '14 aspect ratios', 'Unlimited concurrency']},
                        ('indie-film-posters', 'foggy-orange-sedan')),
    'nano-banana-2': ('Nano Banana 2', {'zh': f'Gemini 3.1 Flash Image，每张 {cny_min("nano-banana-2")} 起', 'en': f'Gemini 3.1 Flash Image, from ${USD["nano-banana-2"]} / image'},
                      {'zh': ['1K/2K 同价', '多图编辑', '并发不限'], 'en': ['Flash speed', 'Multi-image edits', 'Unlimited concurrency']},
                      ('earth-layers-infographic', 'spinning-red-dress')),
    'nano-banana-pro': ('Nano Banana Pro', {'zh': f'Gemini 3 Pro Image，每张 {cny_min("nano-banana-pro")} 起', 'en': f'Gemini 3 Pro Image, from ${USD["nano-banana-pro"]} / image'},
                        {'zh': ['专业级排版', '4K 出图', '并发不限'], 'en': ['Pro typography', '4K output', 'Unlimited concurrency']},
                        ('can-localization', 'futuristic-city')),
}


def L(ja, ko, es, de):
    return dict(ja=ja, ko=ko, es=es, de=de)


# 副标题，键为英文原文里的前缀（价格部分 "from $X / image" 统一换成各语言的句式，{p} 为 "$x"）
SUB_I18N = {
    'nano-banana': L('Nano Banana 全モデル、1枚 {p} から', 'Nano Banana 전 모델, 이미지당 {p}부터',
                     'Todos los modelos Nano Banana, desde {p} / imagen', 'Alle Nano Banana Modelle, ab {p} / Bild'),
    'nano-banana-2.1': L('最新アップデート、1枚 {p} から', '최신 업데이트, 이미지당 {p}부터',
                         'La actualización más reciente, desde {p} / imagen', 'Das neueste Update, ab {p} / Bild'),
    'nano-banana-2': L('Gemini 3.1 Flash Image、1枚 {p} から', 'Gemini 3.1 Flash Image, 이미지당 {p}부터',
                       'Gemini 3.1 Flash Image, desde {p} / imagen', 'Gemini 3.1 Flash Image, ab {p} / Bild'),
    'nano-banana-pro': L('Gemini 3 Pro Image、1枚 {p} から', 'Gemini 3 Pro Image, 이미지당 {p}부터',
                         'Gemini 3 Pro Image, desde {p} / imagen', 'Gemini 3 Pro Image, ab {p} / Bild'),
}
# 标签词表，键为英文图上的原文；缺词直接 KeyError，不回退英文
KEEP = {'2.1 · 2 · Pro'}  # 型号名，各语言原样
TXT = {
    '4K output': L('4K 出力', '4K 출력', 'Salida en 4K', '4K-Ausgabe'),
    '14 aspect ratios': L('14 種類のアスペクト比', '14가지 화면 비율', '14 relaciones de aspecto', '14 Seitenverhältnisse'),
    'Flash speed': L('Flash の速度', 'Flash 속도', 'Velocidad Flash', 'Flash-Tempo'),
    'Multi-image edits': L('複数画像の編集', '다중 이미지 편집', 'Edición con varias imágenes', 'Bearbeitung mehrerer Bilder'),
    'Pro typography': L('プロ品質のタイポグラフィ', '프로급 타이포그래피', 'Tipografía profesional', 'Professionelle Typografie'),
    'Unlimited concurrency': L('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    'Self-service invoices': L('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
}


def money(amount, lang):
    """各语言小数一律用点；仍为美元。"""
    return '$' + amount


def texts(slug, lang):
    """返回 (卖点, 标签列表)。新语言按词表逐项翻译。"""
    _, sub, tags, _ = DATA[slug]
    if lang not in NEW:
        return sub[lang], tags[lang]
    m = re.search(r'\$([0-9.]+) / image$', sub['en'])
    if not m:
        raise KeyError(f'{slug}: 英文卖点里找不到价格 {sub["en"]!r}')
    return (SUB_I18N[slug][lang].format(p=money(m.group(1), lang)),
            [t if t in KEEP else TXT[t][lang] for t in tags['en']])


TPL = '''<!doctype html><html lang="@LANG"><head><meta charset="utf-8"><style>
html{background:#000}
body{margin:0;width:1200px;height:630px;background:#000;color:#fff;font-family:"Google Sans Flex","Google Sans","PingFang SC","Microsoft YaHei",system-ui,sans-serif;position:relative;overflow:hidden}
html[lang=ja] body{font-family:"Google Sans Flex","Google Sans","Yu Gothic UI","Meiryo",system-ui,sans-serif}
html[lang=ko] body{font-family:"Google Sans Flex","Google Sans","Malgun Gothic",system-ui,sans-serif}
.glow{position:absolute;inset:auto -10% -55% -10%;height:90%;background:radial-gradient(45% 55% at 25% 100%,rgba(49,134,255,.35),transparent 70%),radial-gradient(35% 45% at 75% 100%,rgba(252,213,63,.18),transparent 70%)}
.c{position:absolute;left:72px;top:64px;width:600px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:500;color:#cdd4dc}
.b svg{width:34px;height:34px}
h1{margin:92px 0 0;font-size:@FSpx;line-height:1.02;font-weight:500;letter-spacing:-.03em}
p{margin:22px 0 0;font-size:29px;line-height:1.3;color:#b2bbc5}
.r{position:absolute;left:72px;bottom:62px;display:flex;gap:10px}
.r span{padding:9px 18px;border-radius:12px;background:#18191d;border:1px solid #2a2b30;font-size:21px;white-space:nowrap;color:#cdd4dc}
.r span.d{background:#fff;color:#0e0f12;border-color:#fff;font-weight:600}
.g{position:absolute;right:56px;top:56px;bottom:56px;width:420px;display:grid;grid-template-rows:1fr 1fr;gap:14px}
.g div{border-radius:24px;background-size:cover;background-position:center}
.n p{font-size:26px}.n .r span{font-size:19px;padding:9px 15px}.n.k p,.n.k .r span{word-break:keep-all}
</style></head><body class="@BODY"><div class="glow"></div><div class="c"><div class="b"><svg viewBox="0 0 24 24">@ICON</svg>AnyAIGC</div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><div style="background-image:url(/assets/models/nano-banana/@IMG1.webp)"></div><div style="background-image:url(/assets/models/nano-banana/@IMG2.webp)"></div></div>
</body></html>'''

# 版面自检：量 DOM，越界/重叠/间距不足/压到右侧图片时整体缩小字号再重量，结果写进 body[data-fit]
FIT_JS = '''<script>(function(){
var q=function(x){return document.querySelector(x)},all=function(x){return Array.prototype.slice.call(document.querySelectorAll(x))},R=function(e){return e.getBoundingClientRect()};
var tags=all('.r span'),els=[q('h1'),q('p')].concat(tags),base=els.map(function(e){return parseFloat(getComputedStyle(e).fontSize)});
function bad(){var o=[],b=R(q('.b')),h=R(q('h1')),p=R(q('p')),r=R(q('.r')),g=R(q('.g')),t=tags.map(R);
 els.forEach(function(e){var x=R(e);if(x.left<0||x.top<0||x.right>1200||x.bottom>630)o.push('out:'+e.textContent.slice(0,16));
  if(e.scrollWidth>e.clientWidth+1)o.push('clip:'+e.textContent.slice(0,16))});
 if(h.top<b.bottom)o.push('h1-brand');if(p.top<h.bottom-1)o.push('p-h1');if(p.bottom>r.top-8)o.push('p-tags');
 if(h.right>g.left-8||p.right>g.left-8)o.push('text-img');
 if(r.right>g.left-8)o.push('tags-img');
 for(var i=0;i<t.length-1;i++)if(t[i+1].left-t[i].right<8)o.push('gap:'+i);
 return o}
var m=1,n=0;while(bad().length&&n<14){m*=.93;n++;els.forEach(function(e,i){e.style.fontSize=(base[i]*m).toFixed(2)+'px'})}
document.body.setAttribute('data-fit',JSON.stringify({scale:+m.toFixed(3),steps:n,bad:bad()}));
})()</script>'''


def render(slug, lang, fit=False):
    title, _, _, (a, b) = DATA[slug]
    sub, tags = texts(slug, lang)
    fs = 80 if len(title) <= 13 else 70
    t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(tags))
    body = ('n' + (' k' if lang == 'ko' else '')) if lang in NEW else ''
    h = (TPL.replace('@LANG', LANGATTR[lang]).replace('@BODY', body).replace('@FS', str(fs)).replace('@ICON', ICON)
         .replace('@TITLE', title).replace('@SUB', sub).replace('@TAGS', t).replace('@IMG1', a).replace('@IMG2', b))
    return h.replace('</body>', FIT_JS + '</body>') if fit else h


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    langs, only = ('zh', 'en'), None
    for a in sys.argv[1:]:
        if a.startswith('--langs='):
            langs = tuple(a.split('=', 1)[1].split(','))
        elif a.startswith('--only='):
            only = a.split('=', 1)[1].split(',')
    for lang in langs:
        if lang not in LANGATTR:
            raise ValueError(f'Unknown language: {lang}')
    shoot = any(a.startswith('--langs=') for a in sys.argv[1:])
    slugs = [s for s in SLUGS if only is None or s in only]
    if only and len(slugs) != len(only):
        raise ValueError('Unknown slug in --only: ' + ','.join(set(only) - set(slugs)))
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for slug in slugs:
        for lang in langs:
            name = f'{slug}-{lang}'
            path = os.path.join(OUT, name + '.html')
            io.open(path, 'w', encoding='utf-8').write(render(slug, lang, fit=shoot))
            jobs.append((name, path))

    if shoot:
        exe = chrome()
        if not exe:
            raise SystemExit('找不到 Playwright 的 Chromium，无法截图')
        from PIL import Image
        fails, shrunk = [], 0
        for name, path in jobs:
            dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
            url = f'http://localhost:8765/.playwright-mcp/og/nano-banana/{name}.html'
            flags = [exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800', '--virtual-time-budget=6000']
            dom = subprocess.run(flags + ['--dump-dom', url], capture_output=True, timeout=90).stdout.decode('utf-8', 'replace')
            m = re.search(r"data-fit='([^']*)'|data-fit=\"([^\"]*)\"", dom)
            fit = (m.group(1) or m.group(2)).replace('&quot;', '"') if m else 'NO-REPORT'
            ok = '"bad":[]' in fit
            if ok:
                for _ in range(3):  # Chrome 偶发不写文件，重试
                    if os.path.exists(dst):
                        os.remove(dst)
                    subprocess.run(flags + [f'--screenshot={dst}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
                    if os.path.exists(dst):
                        break
                Image.open(dst).crop((0, 0, 1200, 630)).save(dst, optimize=True)
                shrunk += '"steps":0' not in fit
            else:
                fails.append(name)
            os.remove(path)
            print('png' if ok else 'SKIP', os.path.relpath(dst, ROOT), os.path.getsize(dst) if ok else '', 'fit', fit)
        for d in (OUT, os.path.dirname(OUT)):  # 清空后顺手删目录（og 目录里还有别的脚本文件时保留）
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
        print(f'共 {len(jobs)} 张，缩小字号 {shrunk} 张，违例 {len(fails)} 张')
        if fails:
            raise SystemExit('版面自检未通过，未出图: ' + ', '.join(fails))
        return

    run = lambda *a: subprocess.run(['bash', CLI, '-s=og', *a], capture_output=True, text=True)
    run('open', 'about:blank')
    run('resize', '1200', '630')
    for name, _ in jobs:
        run('goto', f'http://localhost:8765/.playwright-mcp/og/nano-banana/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
