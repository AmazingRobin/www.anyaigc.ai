"""Create 1200x630 share cards through temporary HTML and headless Chrome.

先启动 scripts/preview.py（localhost:8765）。临时 HTML 放在 .playwright-mcp/og/seedance，截图后删除。
  python scripts/og_seedance.py                       只重绘 en（海外口径；zh 图不动）
  python scripts/og_seedance.py --langs=ja,ko,es,de   新语言
  python scripts/og_seedance.py --langs=zh,en         显式重绘中英
"""
import glob
import os
import subprocess
import sys
from pathlib import Path
from seedance_data import ROOT, SLUGS, MODELS
from seedance_pages import logo

NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
# 新语言文案表：缺词直接 KeyError，不回退到英文
TXT = {
    '5 models': {'ja': '5モデル', 'ko': '5개 모델', 'es': '5 modelos', 'de': '5 Modelle'},
    'Efficient generation': {'ja': '高効率な生成', 'ko': '효율적인 생성', 'es': 'Generación eficiente', 'de': 'Effiziente Generierung'},
    'Up to 720p': {'ja': '最大720p出力', 'ko': '최대 720p 출력', 'es': 'Hasta 720p', 'de': 'Bis zu 720p'},
    'Native audio': {'ja': 'ネイティブ音声', 'ko': '네이티브 오디오', 'es': 'Audio nativo', 'de': 'Natives Audio'},
    'Unlimited concurrency': {'ja': '同時実行数の上限なし', 'ko': '동시 실행 제한 없음', 'es': 'Sin límite de RPM', 'de': 'Kein RPM-Limit'},
    'Self-service invoices': {'ja': '請求書を自分で発行', 'ko': '인보이스 직접 발급', 'es': 'Facturas en consola', 'de': 'Rechnungen im Konto'},
    '30-second stories': {'ja': '30秒のストーリー', 'ko': '30초 스토리', 'es': 'Historias de 30 s', 'de': '30-Sekunden-Stories'},
    'Multimodal references': {'ja': 'マルチモーダル参照', 'ko': '멀티모달 레퍼런스', 'es': 'Referencias multimodales', 'de': 'Multimodale Referenzen'},
    'Faster generation': {'ja': '高速生成', 'ko': '더 빠른 생성', 'es': 'Generación más rápida', 'de': 'Schnellere Generierung'},
    'High-frequency workloads': {'ja': '高頻度の大量生成', 'ko': '고빈도 작업', 'es': 'Cargas de alta frecuencia', 'de': 'Hochfrequente Workloads'},
    'Token-based billing': {'ja': 'トークン課金', 'ko': '토큰 과금', 'es': 'Facturación por tokens', 'de': 'Abrechnung nach Tokens'},
}
SUB_FMT = {
    'multi': {'ja': 'マルチモーダル動画 · ${p} / 100万トークンから', 'ko': '멀티모달 영상 · ${p} / 100만 토큰부터',
              'es': 'Vídeo multimodal · desde ${p} / 1 M de tokens', 'de': 'Multimodales Video · ab ${p} / 1 Mio. Tokens'},
    'flash': {'ja': '高効率な動画生成 · ${p} / 100万トークンから', 'ko': '효율적인 영상 생성 · ${p} / 100만 토큰부터',
              'es': 'Vídeo eficiente · desde ${p} / 1 M de tokens', 'de': 'Effizientes Video · ab ${p} / 1 Mio. Tokens'},
    'mini': {'ja': '高頻度の動画生成 · ${p} / 100万トークンから', 'ko': '고빈도 영상 생성 · ${p} / 100만 토큰부터',
             'es': 'Vídeo de alta frecuencia · desde ${p} / 1 M de tokens', 'de': 'Hochfrequentes Video · ab ${p} / 1 Mio. Tokens'},
}


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    out = Path(ROOT) / '.playwright-mcp' / 'og' / 'seedance'
    out.mkdir(parents=True, exist_ok=True)
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    langs = only[0] if only else ['en']  # 不带参数只重绘 en，zh 图保持原样
    jobs = []
    for slug in SLUGS:
        overview = slug == 'seedance'
        model = MODELS.get(slug)
        name = 'Seedance' if overview else model['name']
        price = '1.843' if overview else model['min']
        for lang in langs:
            zh = lang == 'zh'
            subtitle = (f'多模态视频生成 · ${price} / 1M tokens 起' if zh else f'Multimodal video · from ${price} / 1M tokens')
            # 英文键；zh 保持原中文文案，新语言按键查 TXT
            tags = ['五个型号', '音画同步', '并发不限', '对公 · 专票'] if zh else ['5 models', 'Native audio', 'Unlimited concurrency', 'Self-service invoices']
            if not overview:
                tags[0] = {'doubao-seedance-2-5': '30 秒长叙事' if zh else '30-second stories',
                           'doubao-seedance-2-5-flash': '高效生成' if zh else 'Efficient generation',
                           'doubao-seedance-2-0': '全模态参考' if zh else 'Multimodal references',
                           'doubao-seedance-2-0-fast': '更快生成' if zh else 'Faster generation',
                           'doubao-seedance-2-0-mini': '高频与规模化' if zh else 'High-frequency workloads'}[slug]
                if slug == 'doubao-seedance-2-5-flash':
                    tags[1] = '最高 720p' if zh else 'Up to 720p'
                    subtitle = f'高效视频生成 · ${price} / 1M tokens 起' if zh else f'Efficient video · from ${price} / 1M tokens'
                if slug == 'doubao-seedance-2-0-mini':
                    tags[1] = '按 tokens 计费' if zh else 'Token-based billing'
                    subtitle = f'高频视频生成 · ${price} / 1M tokens 起' if zh else f'High-frequency video · from ${price} / 1M tokens'
            if lang in NEW:
                tags = [TXT[x][lang] for x in tags]
                subtitle = SUB_FMT['mini' if slug == 'doubao-seedance-2-0-mini' else 'flash' if slug == 'doubao-seedance-2-5-flash' else 'multi'][lang].replace('{p}', price)
            elif lang == 'en':
                pass  # 英文标签已是海外口径（Self-service invoices）
            h = f'''<!doctype html><html lang="{LANGATTR[lang]}"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}}body{{position:relative;width:1200px;height:630px;margin:0;overflow:hidden;background:{'#f8f8f8' if overview else '#0e1014'};color:{'#212121' if overview else '#fff'};font-family:Arial,"Microsoft YaHei","Yu Gothic UI","Malgun Gothic",sans-serif}}
.glow{{position:absolute;inset:0;background:radial-gradient(ellipse at 90% 10%,{'#dae7fa' if overview else '#363543'},transparent 65%)}}
.logo{{position:absolute;left:66px;top:54px;display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600}}.logo i{{height:22px;width:1px;background:#9599a2;margin:0 8px}}.logo span{{font-size:20px;font-weight:400;opacity:.6}}
.title{{position:absolute;left:66px;top:188px;width:850px}}h1{{font-size:{78 if len(name)<18 else 68}px;font-weight:600;letter-spacing:-3px;line-height:1.05;margin:0}}h1 span{{display:block;font-size:46px;font-weight:400;letter-spacing:-1px;margin-top:13px}}p{{font-size:27px;line-height:1.5;margin:26px 0 0;opacity:.68}}
.tags{{position:absolute;left:66px;bottom:66px;display:flex;gap:10px}}.tags span{{font-size:18px;padding:10px 17px;border:1px solid {'#d1d4db' if overview else '#646771'};border-radius:999px;white-space:nowrap}}
.orb{{position:absolute;right:-120px;top:100px;width:420px;height:420px;border-radius:50%;border:1px solid {'#a4afc5' if overview else '#8c827d'};background:radial-gradient(circle at 25% 20%,{'#78e6dc' if overview else '#b8a18c'},transparent 55%);opacity:.45;transform:rotate(-25deg) scaleX(.75)}}
.n .tags span{{font-size:17px;padding:10px 14px}}.n p{{font-size:25px;word-break:keep-all}}
</style></head><body class="{'n' if lang in NEW else ''}"><div class="glow"></div><div class="orb"></div><div class="logo">{logo(32)} AnyAIGC<i></i><span>ByteDance Seed</span></div><div class="title"><h1>{name}<span>Video API</span></h1><p>{subtitle}</p></div><div class="tags">{''.join('<span>'+x+'</span>' for x in tags)}</div></body></html>'''
            filename = slug + '-' + lang
            (out / (filename + '.html')).write_text(h, encoding='utf-8')
            jobs.append(filename)
    exe = chrome()
    if '--html-only' in sys.argv or not exe:
        print(f'Wrote {len(jobs)} temporary HTML files in {out}')
        return
    from PIL import Image
    for fn in jobs:
        png = Path(ROOT) / 'assets' / 'og' / (fn + '.png')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=6000', f'--screenshot={png}',
                        f'http://localhost:8765/.playwright-mcp/og/seedance/{fn}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        (out / (fn + '.html')).unlink()
        print('png', png.relative_to(ROOT), png.stat().st_size)
    if not os.listdir(out):
        out.rmdir()


if __name__ == '__main__':
    main()
