# 生成 GPT Image 系列专题页分享图（1200×630）：python scripts/og_gpt_image.py
# 先写 HTML 到 .playwright-mcp/og/gpt-image/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）
import glob
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpt_image_data import SLUGS, MODELS, TOKEN, CALL, cny  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'gpt-image')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
LOGO = re.search(r' d="([^"]+)"', io.open(os.path.join(ROOT, 'assets/icons/openai.svg'), encoding='utf-8').read()).group(1)
T2, T25, T26 = TOKEN['2']['out'], TOKEN['2.5']['out'], TOKEN['2.6']['out']

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧图片)
DATA = {
    'gpt-image': ('GPT Image API', {'zh': f'OpenAI 全系图像模型，按张 {cny("2")} 起', 'en': f'Every OpenAI image model, from ${CALL["2"]} / image'},
                  {'zh': ['按 token / 按张', '生成 · 编辑', '对公 · 专票'], 'en': ['Token or per image', 'Generate · edit', 'Self-service invoices']}, ('polyglot-collage', 'matcha-poster')),
    'gpt-image-2.6-sunburst': ('GPT Image 2.6 Sunburst', {'zh': f'多轮编辑更一致，图片输出 ${T26} / 1M', 'en': f'Steadier multi-round edits, ${T26} / 1M output'},
                               {'zh': ['最新', 'GIF · SVG', '对公 · 专票'], 'en': ['New', 'GIF · SVG', 'Self-service invoices']}, ('i26-knight-1', 'i26-knight-3')),
    'gpt-image-2.6-flare': ('GPT Image 2.6 Flare', {'zh': f'出图提速 50%，图片输出 ${T26} / 1M', 'en': f'50% faster images, ${T26} / 1M output'},
                            {'zh': ['最新', 'GIF 动图', '并发不限'], 'en': ['New', 'Animated GIFs', 'Unlimited concurrency']}, ('i26-chibi-up', 'i26-owl')),
    'gpt-image-2.5-sunburst': ('GPT Image 2.5 Sunburst', {'zh': f'编辑精度最高，图片输出 ${T25} / 1M', 'en': f'Highest editing precision, ${T25} / 1M output'},
                               {'zh': ['约 6 折', 'max 质量', '并发不限'], 'en': ['41% off', 'max quality', 'Unlimited concurrency']}, ('korean-hanok-ad', 'high-fashion')),
    'gpt-image-2.5-flare': ('GPT Image 2.5 Flare', {'zh': f'速度最快，图片输出 ${T25} / 1M', 'en': f'Fastest high-quality model, ${T25} / 1M output'},
                            {'zh': ['约 6 折', '批量出图', '并发不限'], 'en': ['41% off', 'High volume', 'Unlimited concurrency']}, ('merch-grid', 'candid-flash')),
    'gpt-image-2': ('GPT Image 2', {'zh': f'ChatGPT 图像 2.0 同款，输出 ${T2} / 1M', 'en': f'The model behind ChatGPT Images 2.0, ${T2} / 1M'},
                    {'zh': ['约 0.8 折', '中文渲染', '并发不限'], 'en': ['92% off', 'Text rendering', 'Unlimited concurrency']}, ('chinese-comic', 'rice-macro')),
}


# ---- 新语言（ja / ko / es / de）。非中文图不写合同/对公，发票写"自助开具"。价格数字与英文页一致。
NEW = ('ja', 'ko', 'es', 'de')


def _t(ja, ko, es, de):
    return {'ja': ja, 'ko': ko, 'es': es, 'de': de}


TAG_I18N = {
    'Token or per image': _t('トークン課金／1枚課金', '토큰 / 이미지당', 'Por token o por imagen', 'Pro Token oder pro Bild'),
    'Generate · edit': _t('生成・編集', '생성 · 편집', 'Generar · editar', 'Erzeugen · bearbeiten'),
    'Self-service invoices': _t('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
    'New': _t('最新', '최신', 'Nuevo', 'Neu'),
    'GIF · SVG': _t('GIF · SVG', 'GIF · SVG', 'GIF · SVG', 'GIF · SVG'),
    'Animated GIFs': _t('GIFアニメ', '움직이는 GIF', 'GIF animados', 'Animierte GIFs'),
    'Unlimited concurrency': _t('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    '41% off': _t('41%オフ', '41% 저렴', '41 % menos', '41 % günstiger'),
    '92% off': _t('92%オフ', '92% 저렴', '92 % menos', '92 % günstiger'),
    'max quality': _t('max 品質', 'max 품질', 'Calidad max', 'Qualität max'),
    'High volume': _t('大量生成', '대량 생성', 'Alto volumen', 'Hohes Volumen'),
    'Text rendering': _t('文字レンダリング', '텍스트 렌더링', 'Texto en la imagen', 'Textdarstellung'),
}
SUB_I18N = {
    'gpt-image': lambda: _t(f'OpenAI の全画像モデル、1枚 ${CALL["2"]} から', f'OpenAI 전 이미지 모델, 이미지당 ${CALL["2"]}부터',
                            f'Todos los modelos de imagen de OpenAI, desde ${CALL["2"]} por imagen', f'Alle OpenAI-Bildmodelle, ab ${CALL["2"]} pro Bild'),
    'gpt-image-2.6-sunburst': lambda: _t(f'複数回の編集でも一貫性が向上、画像出力 ${T26} / 100万', f'다회 편집이 더 일관됨, 이미지 출력 ${T26} / 100만',
                                         f'Ediciones en varias rondas más estables, ${T26} / 1 M de salida', f'Stabilere Mehrfachbearbeitung, ${T26} / 1 Mio. Ausgabe'),
    'gpt-image-2.6-flare': lambda: _t(f'画像生成が50%高速、画像出力 ${T26} / 100万', f'이미지 생성 50% 빨라짐, 이미지 출력 ${T26} / 100만',
                                      f'Imágenes un 50 % más rápidas, ${T26} / 1 M de salida', f'Bilder 50 % schneller, ${T26} / 1 Mio. Ausgabe'),
    'gpt-image-2.5-sunburst': lambda: _t(f'編集精度が最高、画像出力 ${T25} / 100万', f'편집 정밀도 최고, 이미지 출력 ${T25} / 100만',
                                         f'Máxima precisión de edición, ${T25} / 1 M de salida', f'Höchste Bearbeitungsgenauigkeit, ${T25} / 1 Mio. Ausgabe'),
    'gpt-image-2.5-flare': lambda: _t(f'最速の高品質モデル、画像出力 ${T25} / 100万', f'가장 빠른 고품질 모델, 이미지 출력 ${T25} / 100만',
                                      f'El modelo de calidad más rápido, ${T25} / 1 M de salida', f'Schnellstes Qualitätsmodell, ${T25} / 1 Mio. Ausgabe'),
    'gpt-image-2': lambda: _t(f'ChatGPT Images 2.0 と同じモデル、${T2} / 100万', f'ChatGPT Images 2.0과 같은 모델, ${T2} / 100만',
                              f'El modelo de ChatGPT Images 2.0, ${T2} / 1 M', f'Das Modell hinter ChatGPT Images 2.0, ${T2} / 1 Mio.'),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#fff;color:#000;font-family:Inter,"PingFang SC","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",system-ui,sans-serif;position:relative;overflow:hidden}
.c{position:absolute;left:72px;top:68px;width:600px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;letter-spacing:-.01em}
.b svg{width:28px;height:28px}
.s{display:inline-flex;gap:6px;margin-left:8px}.s i{display:block;width:14px;height:14px}.s i:nth-child(1){background:#e8412c;border-radius:50%}.s i:nth-child(2){background:#2c67c5}.s i:nth-child(3){width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:14px solid #f6c543}
h1{margin:96px 0 0;font-size:@FSpx;line-height:1.02;font-weight:500;letter-spacing:-.035em}
p{margin:22px 0 0;font-size:30px;line-height:1.3;color:rgba(0,0,0,.66);letter-spacing:-.01em}
.r{position:absolute;left:72px;bottom:64px;display:flex;gap:10px}
.r span{padding:9px 18px;border-radius:999px;background:rgba(0,0,0,.05);font-size:21px;white-space:nowrap}
.r span.d{background:#000;color:#fff;font-weight:600}
.n p{font-size:26px;line-height:1.3;max-width:610px;word-break:keep-all}
.n .r{flex-wrap:wrap;width:610px;gap:8px}
.n .r span{padding:8px 14px;font-size:18px}
.g{position:absolute;right:56px;top:56px;bottom:56px;width:430px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.g div{border-radius:8px;background-size:cover;background-position:center}
</style></head><body class="@BC"><div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#000" fill-rule="evenodd"><path d="@LOGO"/></svg>AnyAIGC<span class="s"><i></i><i></i><i></i></span></div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><div style="background-image:url(/assets/models/gpt-image/@IMG1.webp)"></div><div style="background-image:url(/assets/models/gpt-image/@IMG2.webp)"></div></div>
</body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main_chrome(langs):
    """指定 --langs= 时用无头 Chrome 出图（需要预览服务在运行）。"""
    from PIL import Image
    exe = chrome()
    for slug in SLUGS:
        title, sub, tags, (a, b) = DATA[slug]
        for lang in langs:
            fs = 78 if len(title) <= 13 else (64 if len(title) <= 19 else 56)
            sub_l = SUB_I18N[slug]()[lang]
            tags_l = [TAG_I18N[x][lang] for x in tags['en']]
            t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(tags_l))
            h = (TPL.replace('@FS', str(fs)).replace('@LOGO', LOGO).replace('@TITLE', title).replace('@SUB', sub_l)
                 .replace('@TAGS', t).replace('@IMG1', a).replace('@IMG2', b).replace('@BC', 'n'))
            name = f'{slug}-{lang}'
            hp = os.path.join(OUT, name + '.html')
            io.open(hp, 'w', encoding='utf-8').write(h)
            png = os.path.join(ROOT, 'assets', 'og', name + '.png')
            subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                            '--virtual-time-budget=6000', f'--screenshot={png}',
                            f'http://localhost:8765/.playwright-mcp/og/gpt-image/{name}.html'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
            os.remove(hp)
            print('png', os.path.relpath(png, ROOT), os.path.getsize(png))


def main():
    os.makedirs(OUT, exist_ok=True)
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    if only:
        return main_chrome(only[0])
    jobs = []
    for slug in SLUGS:
        title, sub, tags, (a, b) = DATA[slug]
        for lang in ('zh', 'en'):
            fs = 78 if len(title) <= 13 else (64 if len(title) <= 19 else 56)
            t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(tags[lang]))
            h = (TPL.replace('@FS', str(fs)).replace('@LOGO', LOGO).replace('@TITLE', title).replace('@SUB', sub[lang])
                 .replace('@TAGS', t).replace('@IMG1', a).replace('@IMG2', b).replace('@BC', ''))
            name = f'{slug}-{lang}'
            io.open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(h)
            jobs.append(name)
    run = lambda *a: subprocess.run(['bash', CLI, '-s=og', *a], capture_output=True, text=True)
    run('open', 'about:blank')
    run('resize', '1200', '630')
    for name in jobs:
        run('goto', f'http://localhost:8765/.playwright-mcp/og/gpt-image/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
