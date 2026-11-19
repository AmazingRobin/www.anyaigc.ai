"""Generate Suno sharing-image HTML; render at 1200x630 with Playwright."""
import glob
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.playwright-mcp/og'
NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
# 非中文图不写"合同/对公"，发票写"自助开具"（2026-11-17 起非中文页口径）
SUBTITLE = {
    'zh': 'AI 音乐生成接口 · 发起创作 ¥0.80/次',
    'en': 'AI music generation API · from $0.1191 per song',
    'ja': 'AI音楽生成API・1曲 $0.1191から',
    'ko': 'AI 음악 생성 API · 곡당 $0.1191부터',
    'es': 'API de música con IA · desde $0.1191 por canción',
    'de': 'KI-Musik-API · ab $0.1191 pro Song',
}
TAGS = {
    'zh': ['v3 – v6', '200 RPM', '分轨 + MIDI', '对公 · 专票'],
    'en': ['v3 – v6', '200 RPM', 'Stems + MIDI', 'Self-service invoices'],
    'ja': ['v3 – v6', '200 RPM', 'ステム + MIDI', '請求書を自分で発行'],
    'ko': ['v3 – v6', '200 RPM', '스템 + MIDI', '인보이스 직접 발급'],
    'es': ['v3 – v6', '200 RPM', 'Stems + MIDI', 'Facturas en consola'],
    'de': ['v3 – v6', '200 RPM', 'Stems + MIDI', 'Rechnungen im Konto'],
}


def arg(prefix):
    for a in sys.argv[1:]:
        if a.startswith(prefix):
            return a.split('=', 1)[1].split(',')
    return None


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    logo = (ROOT / 'assets/icons/suno.svg').read_text(encoding='utf-8').replace('fill="currentColor"', 'fill="#ffffff"')
    langs = arg('--langs=') or ['zh', 'en']
    for lang in langs:
        subtitle = SUBTITLE[lang]
        tags = TAGS[lang]
        chips = ''.join(f'<span>{tag}</span>' for tag in tags)
        BC = 'n' if lang in NEW else ''
        html = f'''<!doctype html><html lang="{LANGATTR[lang]}"><head><meta charset="utf-8"><title>Suno API | AnyAIGC</title><style>
*{{box-sizing:border-box}}body{{margin:0;width:1200px;height:630px;overflow:hidden;position:relative;background:#101012;color:#fff;font-family:Arial,"Microsoft YaHei","Yu Gothic UI","Malgun Gothic",sans-serif}}
.aura{{position:absolute;border-radius:50%;filter:blur(90px)}}
.a1{{width:600px;height:600px;left:-300px;top:-330px;background:#ffb003;opacity:.6}}
.a2{{width:600px;height:600px;right:-50px;top:-400px;background:#fe3c7d;opacity:.45}}
.a3{{width:500px;height:500px;left:280px;top:340px;background:#e8502a;opacity:.3}}
.content{{position:absolute;left:80px;right:80px;top:98px}}.brand{{font-size:24px;font-weight:700}}.title{{display:flex;align-items:center;gap:30px;margin-top:42px}}.logo{{width:100px;height:132px;display:flex;align-items:center}}.logo svg{{width:100px;height:132px;fill:#fff}}h1{{font-size:104px;font-weight:700;letter-spacing:-2px;line-height:1;margin:0}}p{{font-size:36px;margin:42px 0 0;color:#f0edef}}.n p{{font-size:31px}}.n .tags span{{font-size:21px;padding:13px 18px}}
.tags{{position:absolute;left:80px;bottom:74px;display:flex;gap:16px}}.tags span{{font-size:23px;white-space:nowrap;padding:15px 22px;border:1px solid #ffffff30;border-radius:999px;background:#10101255}}
</style></head><body class="{BC}"><div class="aura a1"></div><div class="aura a2"></div><div class="aura a3"></div><div class="content"><div class="brand">AnyAIGC</div><div class="title"><div class="logo">{logo}</div><h1>Suno API</h1></div><p>{subtitle}</p></div><div class="tags">{chips}</div></body></html>'''
        path = OUT / f'suno-{lang}.html'
        path.write_text(html, encoding='utf-8')
        print(path.relative_to(ROOT))
        if '--langs=' in ' '.join(sys.argv[1:]) and '--html-only' not in sys.argv and chrome():
            from PIL import Image
            png = ROOT / 'assets' / 'og' / f'suno-{lang}.png'
            subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                            '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/suno-{lang}.html'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
            path.unlink()
            print('png', png.relative_to(ROOT), png.stat().st_size)


if __name__ == '__main__':
    main()
