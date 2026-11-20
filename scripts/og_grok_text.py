"""Write temporary OG HTML, capture with Playwright at 1200x630, then remove HTML."""
from grok_text_data import MODELS, HUB, SLUGS
from grok_text_pages import ROOT, logo, tr as _tr, e
import glob
import os
import subprocess
import sys

NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
SUB_I18N = {
    'grok-4.x': {'ja': 'コーディング、エージェント、ナレッジワーク向けに構築。', 'ko': '코딩, 에이전트, 지식 작업을 위해 만들어졌습니다.',
                 'es': 'Creado para programar, agentes y trabajo del conocimiento.', 'de': 'Gebaut für Coding, Agenten und Wissensarbeit.'},
    'grok-4.7': {'ja': '長いタスクと入念な検証向け', 'ko': '긴 작업과 꼼꼼한 검증용', 'es': 'Tareas largas y verificación minuciosa', 'de': 'Lange Aufgaben, sorgfältige Prüfung'},
    'grok-4.6': {'ja': 'マルチステップのエージェントワークフロー向け', 'ko': '다단계 에이전트 워크플로용', 'es': 'Flujos de trabajo de agentes de varios pasos', 'de': 'Mehrstufige Agenten-Workflows'},
    'grok-4.5': {'ja': 'コーディングとエンジニアリング作業向け', 'ko': '코딩과 엔지니어링 작업용', 'es': 'Programación e ingeniería', 'de': 'Coding und Engineering'},
    'grok-4.3': {'ja': '指示追従とツール呼び出し向け', 'ko': '지시 수행과 도구 호출용', 'es': 'Instrucciones y llamadas a herramientas', 'de': 'Anweisungen und Tool-Aufrufe'},
    'grok-4': {'ja': 'テキストと画像の理解向け', 'ko': '텍스트와 이미지 이해용', 'es': 'Comprensión de texto e imágenes', 'de': 'Text- und Bildverständnis'},
    'grok-4-20-reasoning': {'ja': '複数ステップの問題を推論で解く', 'ko': '다단계 문제를 위한 추론', 'es': 'Razonamiento para problemas de varios pasos', 'de': 'Reasoning für mehrstufige Probleme'},
    'grok-4-20-non-reasoning': {'ja': '日常タスク向けの推論なしモデル', 'ko': '일상 작업용 비추론형 모델', 'es': 'Sin razonamiento, para tareas cotidianas', 'de': 'Ohne Reasoning, für Alltagsaufgaben'},
    'grok-build-0.1': {'ja': 'ソフトウェア開発向けモデル', 'ko': '소프트웨어 개발용 모델', 'es': 'Un modelo para desarrollo de software', 'de': 'Ein Modell für Softwareentwicklung'},
}
TXT = {
    'input': {'ja': '入力', 'ko': '입력', 'es': 'entrada', 'de': 'Eingabe'},
    'Unlimited concurrency': {'ja': '同時実行数の上限なし', 'ko': '동시 실행 제한 없음', 'es': 'Sin límite de RPM', 'de': 'Kein RPM-Limit'},
    'Contracts · invoices': {'ja': '請求書を自分で発行', 'ko': '인보이스 직접 발급', 'es': 'Facturas en consola', 'de': 'Rechnungen im Konto'},
    'Built for coding, agents, and knowledge work.': SUB_I18N['grok-4.x'],
}


def tr(lang, zh, en):
    """新语言查 TXT 表（缺词直接报错）；英文图的合同标签改成自助开票（2026-11-17 起非中文口径）。"""
    if lang in NEW:
        return TXT[en][lang]
    if lang == 'en' and en == 'Contracts · invoices':
        return 'Self-service invoices'
    return _tr(lang, zh, en)


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None



def main():
    out=ROOT/'.playwright-mcp/og-grok-text'
    out.mkdir(parents=True,exist_ok=True)
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    for lang in (only[0] if only else ('zh', 'en')):
        for slug in SLUGS:
            m=MODELS['grok-4.7' if slug==HUB else slug]
            name='Grok 4.x' if slug==HUB else m['name']
            sub=tr(lang,'为编程、智能体与知识工作而构建。','Built for coding, agents, and knowledge work.') if slug==HUB else (SUB_I18N[slug][lang] if lang in NEW else m[lang][2])
            price='0.0993' if slug==HUB else m['prices'][0]
            fs=64 if len(name)>20 else 82
            s=f'''<!doctype html><html lang="{LANGATTR[lang]}"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}}body{{width:1200px;height:630px;margin:0;background:#fff;color:#0a0a0a;font-family:Arial,"Microsoft YaHei","Yu Gothic UI","Malgun Gothic",sans-serif;position:relative;overflow:hidden}}.top{{position:absolute;left:64px;right:64px;top:45px;display:flex;align-items:center;justify-content:space-between;font-size:24px;letter-spacing:-.6px}}.brand{{font-weight:700}}.top small{{font:13px Consolas,monospace;color:#777;letter-spacing:1.5px}}.mark{{position:absolute;right:72px;top:145px;border:1px solid #deddd9;border-radius:32px;padding:35px;background:#f7f7f5}}.mark svg{{width:120px;height:120px}}h1{{position:absolute;left:64px;top:157px;margin:0;max-width:920px;font-size:{fs}px;line-height:1.15;font-weight:400;letter-spacing:-3px}}h1 span{{display:block;font-size:45px;margin-top:7px;letter-spacing:-1px;color:#777}}p{{position:absolute;left:64px;top:331px;font-size:29px;margin:0;max-width:1000px;line-height:1.5;font-weight:400}}.tags{{position:absolute;left:64px;bottom:65px;display:flex;gap:12px;align-items:center}}.tags span{{font-size:18px;border:1px solid #d7d6d1;border-radius:999px;padding:13px 21px;white-space:nowrap}}.tags .price{{background:#0a0a0a;color:#fff;border-color:#0a0a0a}}.rule{{position:absolute;left:64px;right:64px;bottom:30px;height:1px;background:#deddd9}}
.n .tags span{{font-size:17px;padding:12px 15px}}.n p{{font-size:26px;max-width:1000px;word-break:keep-all}}</style></head><body class="{'n' if lang in NEW else ''}"><div class="top"><span class="brand">AnyAIGC <span style="font-weight:400;color:#777">/ Grok</span></span><small>TEXT & CODE / API</small></div>{'<div class="mark">'+logo()+'</div>' if len(name)<22 else ''}<h1>{e(name)}<span>API</span></h1><p>{e(sub)}</p><div class="tags"><span class="price">${price} / 1M {tr(lang,'输入起','input')}</span><span>{tr(lang,'并发不限','Unlimited concurrency')}</span><span>{tr(lang,'对公 · 专票','Contracts · invoices')}</span></div><div class="rule"></div></body></html>'''
            s=s.replace('<span class="brand">AnyAIGC', '<span class="brand" style="display:flex;align-items:center;gap:10px">'+logo()+'AnyAIGC')
            s=s.replace('.brand{font-weight:700}', '.brand{font-weight:700}.brand svg{width:25px;height:25px}')
            (out/f'{slug}-{lang}.html').write_text(s,encoding='utf-8')
    if only and '--html-only' not in sys.argv and chrome():
        from PIL import Image
        for lang in only[0]:
            for slug in SLUGS:
                hp = out / f'{slug}-{lang}.html'
                png = ROOT / 'assets' / 'og' / f'{slug}-{lang}.png'
                subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                                '--virtual-time-budget=6000', f'--screenshot={png}',
                                f'http://localhost:8765/.playwright-mcp/og-grok-text/{slug}-{lang}.html'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
                Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
                hp.unlink()
                print('png', png.relative_to(ROOT), png.stat().st_size)
        return
    print('Wrote 18 temporary OG HTML files.')


if __name__=='__main__':
    main()
