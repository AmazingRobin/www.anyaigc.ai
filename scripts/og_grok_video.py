# 生成 Grok Video 系列专题页分享图（1200×630）：python scripts/og_grok_video.py
# 先写 HTML 到 .playwright-mcp/og/grok-video/，再用 playwright-cli 截图到 assets/og/<slug>-<lang>.png
# 需要先运行 python scripts/preview.py（http://localhost:8765）
import glob
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grok_video_data import SLUGS, MODELS, cny  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og', 'grok-video')
CLI = os.path.expanduser('~/.claude/skills/playwright/scripts/playwright_cli.sh')
LOGO = re.search(r'<path d="([^"]+)"', io.open(os.path.join(ROOT, 'assets/icons/grok.svg'), encoding='utf-8').read()).group(1)
P = lambda s, lang: f'¥{cny(MODELS[s]["usd"])}' if lang == 'zh' else f'${MODELS[s]["usd"]}'

# slug -> (标题, {语言: 卖点}, {语言: 标签}, 右侧图片：视频封面帧)
DATA = {
    'grok-video': ('Grok Video API', {'zh': f'xAI 全系视频模型，{P("grok-imagine-video-1.5-lite", "zh")} / 秒起', 'en': f'Every xAI video model, from {P("grok-imagine-video-1.5-lite", "en")} / sec'},
                   {'zh': ['3 个型号', '原生声音', '对公 · 专票'], 'en': ['3 models', 'Native audio', 'Self-service invoices']}, ('speech-2', 'perfume')),
    'grok-imagine-video-1.5-preview': ('Grok Imagine Video 1.5', {'zh': f'画面与对白一起生成，{P("grok-imagine-video-1.5-preview", "zh")} / 秒起', 'en': f'Video with lip-synced speech, from {P("grok-imagine-video-1.5-preview", "en")} / sec'},
                                       {'zh': ['1–15 秒', '图生视频', '并发不限'], 'en': ['1–15 seconds', 'Image to video', 'Unlimited concurrency']}, ('speech-1', 'try-on')),
    'grok-imagine-video-1.5-lite': ('Grok Imagine Video 1.5 Lite', {'zh': f'系列最低价，{P("grok-imagine-video-1.5-lite", "zh")} / 秒起', 'en': f'Lowest price in the series, from {P("grok-imagine-video-1.5-lite", "en")} / sec'},
                                    {'zh': ['最高 1080p', '原生声音', '并发不限'], 'en': ['Up to 1080p', 'Native audio', 'Unlimited concurrency']}, ('property', 'dining')),
    'grok-imagine-video': ('Grok Imagine Video', {'zh': f'支持改视频，{P("grok-imagine-video", "zh")} / 秒起', 'en': f'Generate and edit video, from {P("grok-imagine-video", "en")} / sec'},
                           {'zh': ['改视频', '原生声音', '并发不限'], 'en': ['Video editing', 'Native audio', 'Unlimited concurrency']}, ('restyle-a', 'edit-a')),
}


NEW = ('ja', 'ko', 'es', 'de')


def _t(ja, ko, es, de):
    return {'ja': ja, 'ko': ko, 'es': es, 'de': de}


TAG_I18N = {
    '3 models': _t('3モデル', '3개 모델', '3 modelos', '3 Modelle'),
    'Generate · edit': _t('生成・編集', '생성 · 편집', 'Generar · editar', 'Erzeugen · bearbeiten'),
    'Self-service invoices': _t('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
    '15 aspect ratios': _t('15種類のアスペクト比', '15가지 종횡비', '15 relaciones de aspecto', '15 Seitenverhältnisse'),
    '1k / 1.5k / 2k': _t('1k / 1.5k / 2k', '1k / 1.5k / 2k', '1k / 1.5k / 2k', '1k / 1.5k / 2k'),
    '1k / 2k': _t('1k / 2k', '1k / 2k', '1k / 2k', '1k / 2k'),
    'Unlimited concurrency': _t('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    'Text to image': _t('テキストから画像', '텍스트→이미지', 'Texto a imagen', 'Text-zu-Bild'),
    'Migration guide': _t('移行ガイド', '마이그레이션 가이드', 'Guía de migración', 'Migrationsleitfaden'),
    'Native audio': _t('ネイティブ音声', '네이티브 오디오', 'Audio nativo', 'Natives Audio'),
    '1–15 seconds': _t('1〜15秒', '1–15초', '1–15 segundos', '1–15 Sekunden'),
    'Image to video': _t('画像から動画', '이미지→비디오', 'De imagen a vídeo', 'Bild-zu-Video'),
    'Up to 1080p': _t('最大1080p', '최대 1080p', 'Hasta 1080p', 'Bis zu 1080p'),
    'Video editing': _t('動画編集', '비디오 편집', 'Edición de vídeo', 'Videobearbeitung'),
}
FROM_I18N = {'ja': '{p}から', 'ko': '{p}부터', 'es': 'Desde {p}', 'de': 'Ab {p}'}


def tag_i18n(x, lang):
    if x.startswith('From $'):
        return FROM_I18N[lang].format(p=x[5:])
    return TAG_I18N[x][lang]


def _u(slug):
    return MODELS[slug]['usd']


SUB_I18N = {
    'grok-video': lambda l: {'ja': f'xAI の全動画モデル、1秒 ${_u("grok-imagine-video-1.5-lite")} から', 'ko': f'xAI 전 비디오 모델, 초당 ${_u("grok-imagine-video-1.5-lite")}부터',
                             'es': f'Todos los modelos de vídeo de xAI, desde ${_u("grok-imagine-video-1.5-lite")} por segundo', 'de': f'Alle xAI-Videomodelle, ab ${_u("grok-imagine-video-1.5-lite")} pro Sekunde'}[l],
    'grok-imagine-video-1.5-preview': lambda l: {'ja': f'映像とリップシンクのセリフを同時に生成、1秒 ${_u("grok-imagine-video-1.5-preview")} から', 'ko': f'영상과 립싱크 대사를 함께 생성, 초당 ${_u("grok-imagine-video-1.5-preview")}부터',
                                                 'es': f'Vídeo con voz sincronizada, desde ${_u("grok-imagine-video-1.5-preview")} por segundo', 'de': f'Video mit lippensynchroner Sprache, ab ${_u("grok-imagine-video-1.5-preview")} pro Sekunde'}[l],
    'grok-imagine-video-1.5-lite': lambda l: {'ja': f'シリーズ最安、1秒 ${_u("grok-imagine-video-1.5-lite")} から', 'ko': f'시리즈 최저가, 초당 ${_u("grok-imagine-video-1.5-lite")}부터',
                                              'es': f'El precio más bajo de la serie, desde ${_u("grok-imagine-video-1.5-lite")} por segundo', 'de': f'Günstigster Preis der Serie, ab ${_u("grok-imagine-video-1.5-lite")} pro Sekunde'}[l],
    'grok-imagine-video': lambda l: {'ja': f'動画の生成と編集に対応、1秒 ${_u("grok-imagine-video")} から', 'ko': f'비디오 생성과 편집 지원, 초당 ${_u("grok-imagine-video")}부터',
                                     'es': f'Genera y edita vídeo, desde ${_u("grok-imagine-video")} por segundo', 'de': f'Videos erzeugen und bearbeiten, ab ${_u("grok-imagine-video")} pro Sekunde'}[l],
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#fff;color:#0a0a0a;font-family:Inter,"Segoe UI","PingFang SC","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",system-ui,sans-serif;position:relative;overflow:hidden}
.c{position:absolute;left:72px;top:68px;width:620px}
.b{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600;letter-spacing:-.02em}
.b svg{width:30px;height:30px}
.b i{width:1px;height:22px;background:rgba(10,10,10,.2)}
.b span{font-weight:500;color:rgba(10,10,10,.6)}
h1{margin:92px 0 0;font-size:@FSpx;line-height:1.04;font-weight:500;letter-spacing:-.03em}
p{margin:22px 0 0;font-size:29px;line-height:1.35;color:rgba(10,10,10,.66);letter-spacing:-.01em}
.r{position:absolute;left:72px;bottom:64px;display:flex;gap:10px}
.r span{padding:9px 18px;border-radius:999px;background:#f2f1ef;font-size:21px;white-space:nowrap}
.r span.d{background:#0a0a0a;color:#fff;font-weight:600}
.n p{font-size:25px;line-height:1.3;max-width:610px;word-break:keep-all}
.n .r{flex-wrap:wrap;width:610px;gap:8px}
.n .r span{padding:8px 14px;font-size:18px}
.g{position:absolute;right:56px;top:56px;bottom:56px;width:410px;display:grid;grid-template-rows:1fr 1fr;gap:12px}
.g div{border-radius:16px;background-size:cover;background-position:center}
</style></head><body class="@BC"><div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#0a0a0a" fill-rule="evenodd"><path d="@LOGO"/></svg>AnyAIGC<i></i><span>xAI</span></div>
<h1>@TITLE</h1><p>@SUB</p></div>
<div class="r">@TAGS</div>
<div class="g"><div style="background-image:url(/assets/models/grok-video/@IMG1.webp)"></div><div style="background-image:url(/assets/models/grok-video/@IMG2.webp)"></div></div>
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
            fs = 76 if len(title) <= 16 else (62 if len(title) <= 22 else 54)
            if lang in NEW:
                sub_l = SUB_I18N[slug](lang)
                tags_l = [tag_i18n(x, lang) for x in tags['en']]
            else:
                sub_l, tags_l = sub[lang], tags[lang]
            t = ''.join(f'<span class="{"d" if i == 0 else ""}">{x}</span>' for i, x in enumerate(tags_l))
            h = (TPL.replace('@FS', str(fs)).replace('@LOGO', LOGO).replace('@TITLE', title).replace('@SUB', sub_l)
                 .replace('@TAGS', t).replace('@IMG1', a).replace('@IMG2', b).replace('@BC', 'n' if lang in NEW else ''))
            name = f'{slug}-{lang}'
            hp = os.path.join(OUT, name + '.html')
            io.open(hp, 'w', encoding='utf-8').write(h)
            png = os.path.join(ROOT, 'assets', 'og', name + '.png')
            subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                            '--virtual-time-budget=6000', f'--screenshot={png}',
                            f'http://localhost:8765/.playwright-mcp/og/grok-video/{name}.html'],
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
            fs = 76 if len(title) <= 16 else (62 if len(title) <= 22 else 54)
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
        run('goto', f'http://localhost:8765/.playwright-mcp/og/grok-video/{name}.html')
        run('eval', 'document.fonts.ready.then(()=>1)')
        dst = os.path.join(ROOT, 'assets', 'og', name + '.png')
        run('screenshot', f'--filename={dst}')
        print(name, os.path.getsize(dst) if os.path.exists(dst) else 'MISSING')
    run('close')


if __name__ == '__main__':
    main()
