"""Write temporary 1200x630 HTML share cards, capture them with headless Chrome, delete the HTML.

先启动 scripts/preview.py（localhost:8765）。
  python scripts/og_doubao_seed.py                       只重绘 en（海外口径；zh 图不动）
  python scripts/og_doubao_seed.py --langs=ja,ko,es,de   新语言
  python scripts/og_doubao_seed.py --langs=zh,en         显式重绘中英
只用 CSS 和固定版本的 lobe-icons ByteDance SVG。
"""
import glob
import os
import subprocess
import sys
from doubao_seed_pages import (
    ROOT, VER, e, name, logo, tr, art,
    MODELS, COPY, SLUGS, SNAPSHOT_IDS, LATEST,
)

OUT = ROOT / '.playwright-mcp/doubao-og'
NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
TAGLINE_I18N = {
    'doubao-seed-2-1-pro': {'ja': 'サブタスクを連携して実行するエージェント', 'ko': '하위 작업을 조율하는 에이전트 실행', 'es': 'Ejecución coordinada de agentes', 'de': 'Koordinierte Agenten-Ausführung'},
    'doubao-seed-2-1-turbo': {'ja': '本番規模のコーディング', 'ko': '프로덕션 규모의 코딩', 'es': 'Programación a escala de producción', 'de': 'Coding im Produktionsmaßstab'},
    'doubao-seed-2-0-pro': {'ja': '制約のある条件での推論', 'ko': '제약 조건 하의 추론', 'es': 'Razonamiento bajo restricciones', 'de': 'Reasoning unter Randbedingungen'},
    'doubao-seed-2-0-lite': {'ja': 'ネイティブなオムニモーダル理解', 'ko': '네이티브 옴니모달 이해', 'es': 'Comprensión omnimodal nativa', 'de': 'Native omnimodale Verarbeitung'},
    'doubao-seed-1-8': {'ja': 'マルチモーダルな業務アシスタント', 'ko': '멀티모달 업무 어시스턴트', 'es': 'Asistencia empresarial multimodal', 'de': 'Multimodale Unterstützung im Business'},
    'doubao-seed-2-0-mini': {'ja': 'トークン効率の高いオムニモーダル処理', 'ko': '토큰 효율적인 옴니모달 작업', 'es': 'Tareas omnimodales con pocos tokens', 'de': 'Tokensparende omnimodale Aufgaben'},
    'doubao-seed-2-0-code-preview': {'ja': 'エンタープライズ向けコーディングとフロントエンド', 'ko': '엔터프라이즈 코딩과 프런트엔드', 'es': 'Programación y frontend para empresas', 'de': 'Enterprise-Coding und Frontend'},
    'doubao-seed-1-6': {'ja': '推論の深さを選べる', 'ko': '추론 깊이를 선택', 'es': 'Elige la profundidad de razonamiento', 'de': 'Reasoning-Tiefe wählbar'},
    'doubao-seed-1-6-flash': {'ja': '低レイテンシのマルチモーダル対応', 'ko': '지연이 짧은 멀티모달 지원', 'es': 'Asistencia multimodal con respuesta rápida', 'de': 'Schnelle multimodale Unterstützung'},
    'doubao-seed-1-6-thinking': {'ja': '視覚情報を使った深い推論', 'ko': '시각 맥락을 활용한 심층 추론', 'es': 'Contexto visual para razonamiento profundo', 'de': 'Visueller Kontext für tiefes Reasoning'},
    'doubao-seed-1-6-vision': {'ja': '画像理解と推論', 'ko': '비전 이해와 추론', 'es': 'Comprensión visual y razonamiento', 'de': 'Bildverständnis und Reasoning'},
}
TXT = {
    'models': {'ja': 'モデル', 'ko': '모델', 'es': 'modelos', 'de': 'Modelle'},
    'Self-service invoices': {'ja': '請求書を自分で発行', 'ko': '인보이스 직접 발급', 'es': 'Facturas en consola', 'de': 'Rechnungen im Konto'},
}


def t(lang, zh, en):
    """新语言查 TXT 表（缺词直接报错）；英文图的开票标签改成自助开票（2026-11-17 起非中文口径）。"""
    if lang in NEW:
        return TXT[en][lang]
    if lang == 'en' and en == 'Self-service invoices':
        return 'Self-service invoices'
    return tr(lang, zh, en)


def tagline(lang, slug):
    return TAGLINE_I18N[slug][lang] if lang in NEW else COPY[slug][lang]['tagline']


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def card(lang, slug):
    tags = ['Chat Completions', '300+ ' + t(lang, '模型', 'models'), t(lang, '对公 · 专票', 'Self-service invoices')]
    title = name(slug).replace('doubao-seed-', 'doubao-seed-<br>', 1)
    return f'''<!DOCTYPE html><html lang="{LANGATTR[lang]}" class="no-js"><head><meta charset="utf-8">
<link rel="stylesheet" href="/assets/models/doubao-seed.css?v={VER}">
<style>
html,body{{width:1200px;height:630px;margin:0;overflow:hidden;background:#101116;color:#fff}}
body{{position:relative;background:radial-gradient(ellipse at 88% 30%,#26387388,transparent 60%),radial-gradient(ellipse at 90% 95%,#00c8d233,transparent 48%),#101116}}
.content{{position:absolute;left:64px;top:48px;width:735px}}
.brand{{display:flex;align-items:center;gap:14px;color:#fff;font-size:27px;font-weight:600}}
.content h1{{margin:66px 0 20px;color:#fff;font-size:60px;line-height:1.1;letter-spacing:-1.5px;font-weight:600;overflow-wrap:anywhere}}
.content p{{max-width:720px;font-size:26px;line-height:1.45;color:#b8c8e7}}
.tags{{position:absolute;left:64px;bottom:55px;display:flex;gap:10px}}
.tags span{{font-size:19px;padding:8px 17px;background:#ffffff14;border-radius:999px;color:#ebf4ff;white-space:nowrap}}
.art{{position:absolute;right:54px;top:158px;width:300px;display:grid;gap:14px}}
.art .db-art{{height:145px;border-radius:20px;aspect-ratio:auto}}
.art .db-art:nth-child(2){{transform:translateX(-25px)}}
.n,.n *{{font-family:Inter,"Yu Gothic UI","Meiryo","Malgun Gothic","Microsoft YaHei",Arial,sans-serif}}
.n .content p{{font-size:25px;word-break:keep-all}}.n .tags span{{font-size:18px;padding:8px 15px}}
</style></head><body class="{'n' if lang in NEW else ''}"><div class="content"><div class="brand">{logo(34)}AnyAIGC</div><h1>{title} API</h1><p>{e(tagline(lang, slug))}</p></div>
<div class="tags">{''.join(f'<span>{e(x)}</span>' for x in tags)}</div><div class="art">{art('code')}{art('flow')}</div></body></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    langs = only[0] if only else ['en']  # 不带参数只重绘 en，zh 图保持原样
    jobs = []
    for slug in SLUGS:
        for lang in langs:
            filename = f'{slug}-{lang}'
            (OUT / (filename + '.html')).write_text(card(lang, slug), encoding='utf-8')
            jobs.append(filename)
    if '--html-only' in sys.argv or not chrome():
        print(f'Prepared {len(jobs)} share cards in {OUT}')
        return
    from PIL import Image
    for fn in jobs:
        png = ROOT / 'assets' / 'og' / f'{fn}.png'
        subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=6000', f'--screenshot={png}',
                        f'http://localhost:8765/.playwright-mcp/doubao-og/{fn}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        (OUT / (fn + '.html')).unlink()
        print('png', png.relative_to(ROOT), png.stat().st_size)
    if not os.listdir(OUT):
        OUT.rmdir()


if __name__ == '__main__':
    main()
