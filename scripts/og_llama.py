"""Llama 系列分享图（1200x630）。

默认只写 zh/en 的临时 HTML 到 .playwright-mcp/llama-og/（再用 Playwright 截图）：
    python scripts/og_llama.py
新语言和英文重出走 Chrome headless 直接截图到 assets/og/<slug>-<lang>.png（需先启动 python scripts/preview.py）：
    python scripts/og_llama.py --langs=ja,ko,es,de [--only=llama,llama-3-8b]
    python scripts/og_llama.py --langs=en
截图前用 JS 量 DOM，标题/副标题/标签越界、重叠或间距 < 8px 时自动缩小字号再出图；
仍违例的卡片不出图并报错。出图后删除临时 HTML。无图像生成服务。
"""
import glob
import os
import re
import subprocess
import sys
from html import escape
from pathlib import Path

from llama_data import BY_ID, SLUGS
from llama_pages import deal, mark

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'.playwright-mcp/llama-og'
NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
CSS = '''
*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{position:relative;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;background:#fff;color:#171717}
html[lang=ja] body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Yu Gothic UI","Meiryo",sans-serif}
html[lang=ko] body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif}
.brand{position:absolute;left:64px;top:43px;display:flex;gap:18px;align-items:center;font-size:24px;font-weight:600;letter-spacing:-.5px}.brand span{color:#888;font-size:16px;font-weight:400}
.mark{position:absolute;right:76px;top:187px;width:170px;height:170px}
.main{position:absolute;left:64px;top:157px;width:850px}.eyebrow{font:12px Consolas,monospace;letter-spacing:2px;color:#777;margin:0 0 24px}
h1{font-size:61px;font-weight:550;line-height:1.12;letter-spacing:-2.2px;max-width:830px;margin:0 0 22px;text-wrap:balance}h1.long{font-size:52px;max-width:790px}
.sub{font-size:24px;color:#666;margin:0;max-width:820px;line-height:1.4}.deal{display:inline-block;margin-top:26px;background:#171717;color:white;font-size:20px;padding:10px 23px;border-radius:999px}
.bottom{position:absolute;bottom:0;left:0;right:0;border-top:1px solid #e6e6e6;padding:28px 64px;display:flex;align-items:center;gap:26px;font-size:17px;color:#737373;white-space:nowrap}.bottom b{color:#171717;font-weight:550}.bottom span:last-child{margin-left:auto}
.n .sub{font-size:22px}.n .deal{font-size:18px}.n .bottom{font-size:16px;gap:22px}.n.k .sub,.n.k .deal,.n.k .bottom{word-break:keep-all}
'''


def L(ja, ko, es, de):
    return dict(ja=ja, ko=ko, es=es, de=de)


# 副标题，键为型号 id（总览页为 llama），英文原文来自 llama_data 的 tag_en
SUB_I18N = {
    'llama': L('12 モデル、APIキーは 1 つ。', '모델 12개, API 키 하나.', '12 modelos. Una sola clave de API.', '12 Modelle. Ein API-Schlüssel.'),
    'llama-3.3-70b-instruct': L('対話向けの 70B インストラクトモデル', '대화용 70B 인스트럭트 모델',
                                'Un modelo instruct de 70B para conversación', 'Ein 70B-Instruct-Modell für Dialoge'),
    'llama-3.2-90b-vision-instruct': L('対話に画像理解を', '대화에 이미지 이해 기능을 더하세요',
                                       'Lleva la comprensión de imágenes a la conversación', 'Bildverständnis für Dialoge'),
    'llama-3.2-11b-vision-instruct': L('11B 規模の画像・テキスト理解', '11B 규모의 이미지·텍스트 이해',
                                       'Comprensión de imágenes y texto en 11B', 'Bild- und Textverständnis mit 11B'),
    'llama-3.2-3b-instruct': L('テキスト処理向けのコンパクトな選択肢', '텍스트 워크플로를 위한 컴팩트한 선택',
                               'Una opción compacta para flujos de texto', 'Eine kompakte Wahl für Text-Workflows'),
    'llama-3.2-1b-instruct': L('低コストなテキストリクエストで手軽に開始', '저비용 텍스트 요청으로 가볍게 시작',
                               'Empieza con peticiones de texto de bajo coste', 'Klein starten mit günstigen Text-Anfragen'),
    'llama-3.1-405b': L('汎用的な言語タスク向けの 405B モデル', '범용 언어 작업을 위한 405B 모델',
                        'Un modelo de 405B para tareas de lenguaje general', 'Ein 405B-Modell für allgemeine Sprachaufgaben'),
    'llama-3.1-70b': L('70B 規模の汎用テキスト利用', '70B 규모의 범용 텍스트 접근',
                       'Acceso a texto de propósito general en 70B', 'Allzweck-Textzugriff mit 70B'),
    'llama-3.1-8b': L('Llama 3.1 への 8B の入り口', 'Llama 3.1을 시작하는 8B 모델',
                      'Una puerta de entrada de 8B a Llama 3.1', 'Der 8B-Einstieg in Llama 3.1'),
    'llama-3-70b': L('Llama 3 70B のワークフローをそのまま', 'Llama 3 70B 워크플로를 그대로',
                     'Mantén tu flujo de trabajo con Llama 3 70B', 'Ihren Llama-3-70B-Workflow beibehalten'),
    'llama-3-8b': L('Llama 3 の 8B テキストモデル', 'Llama 3의 8B 텍스트 모델',
                    'El modelo de texto de 8B de Llama 3', 'Das 8B-Textmodell von Llama 3'),
    'llama-2-70b': L('既存の Llama 2 プロジェクト向け API アクセス', '기존 Llama 2 프로젝트를 위한 API 접근',
                     'Acceso por API para proyectos existentes de Llama 2', 'API-Zugang für bestehende Llama-2-Projekte'),
    'llama-2-7b': L('Llama 2 7B で使い慣れたインターフェース', 'Llama 2 7B를 위한 익숙한 인터페이스',
                    'Una interfaz conocida para Llama 2 7B', 'Eine vertraute Schnittstelle für Llama 2 7B'),
}
# 标签词表，键为英文图上的原文；缺词直接 KeyError，不回退英文
TXT = {
    'Unlimited concurrency': L('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    'Self-service invoices': L('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
    'Save 32% on selected models': L('一部モデルが 32%オフ', '일부 모델 32% 저렴',
                                     'Ahorra un 32 % en modelos seleccionados', '32 % sparen bei ausgewählten Modellen'),
    'Save 32%': L('32%オフ', '32% 저렴', 'Ahorra un 32 %', '32 % sparen'),
    'Pay as you go': L('従量課金', '사용한 만큼 결제', 'Pago por uso', 'Nutzungsbasierte Abrechnung'),
}
PRICE_IN = L('入力 100万トークン {p} から', '입력 100만 토큰 {p}부터', 'desde {p} / 1M de entrada', 'ab {p} / 1 Mio. Eingabe')


def money(amount, lang):
    """各语言小数一律用点；仍为美元。"""
    return '$' + amount


def deal_en(model):
    """英文图上的 deal 原文（与 llama_pages.deal 一致），新语言按它查词表。"""
    return deal('en', model)


def page(lang, slug, fit=False):
    model = BY_ID.get(slug)
    zh = lang == 'zh'
    new = lang in NEW
    name = (model['name'] if model else 'Llama') + ' API'
    price = model['input'] if model else '0.3375'
    if new:
        sub = SUB_I18N[slug][lang]
        deal_txt = TXT[deal_en(model)][lang]
        left = PRICE_IN[lang].format(p=money(price, lang))
        conc = TXT['Unlimited concurrency'][lang]
        inv = TXT['Self-service invoices'][lang]
    else:
        sub = model['tag_'+lang] if model else ('12 个型号，一个 API Key。' if zh else '12 models. One API key.')
        deal_txt = deal(lang, model)
        left = f"{'输入' if zh else 'Input'} ${price} / 1M tokens"
        conc = '并发不限' if zh else 'Unlimited concurrency'
        inv = '对公 · 专票' if zh else 'Self-service invoices'
    body = ('n' + (' k' if lang == 'ko' else '')) if new else ''
    s = f'''<!DOCTYPE html><html lang="{LANGATTR[lang]}"><head><meta charset="UTF-8"><title>{name}</title><style>{CSS}</style></head><body class="{body}">
<div class="brand">AnyAIGC <span>× Llama</span></div><div class="mark">{mark(170)}</div>
<div class="main"><p class="eyebrow">META LLAMA · OLLAMA COLLECTION</p><h1 class="{'long' if len(name)>23 else ''}">{escape(name)}</h1><p class="sub">{escape(sub)}</p><div class="deal">{escape(deal_txt)}</div></div>
<div class="bottom"><b>{escape(left)}</b><span>{escape(conc)}</span><span>{escape(inv)}</span><span>www.anyaigc.ai</span></div></body></html>'''
    return s.replace('</body>', FIT_JS + '</body>') if fit else s


# 版面自检：量 DOM，越界/重叠/间距不足时整体缩小字号再重量，结果写进 body[data-fit]
FIT_JS = '''<script>(function(){
var q=function(x){return document.querySelector(x)},all=function(x){return Array.prototype.slice.call(document.querySelectorAll(x))},R=function(e){return e.getBoundingClientRect()};
var kids=all('.bottom>*'),els=[q('h1'),q('.sub'),q('.deal')].concat(kids),base=els.map(function(e){return parseFloat(getComputedStyle(e).fontSize)});
function bad(){var o=[],h=R(q('h1')),s=R(q('.sub')),d=R(q('.deal')),bb=R(q('.bottom')),ey=R(q('.eyebrow')),mk=R(q('.mark')),k=kids.map(R);
 els.forEach(function(e){var r=R(e);if(r.left<0||r.top<0||r.right>1200||r.bottom>630)o.push('out:'+e.textContent.slice(0,16))});
 [h,s,d].forEach(function(r){if(r.right>mk.left-8)o.push('mark-overlap')});
 if(h.top<ey.bottom)o.push('h1-eyebrow');if(s.top<h.bottom-1)o.push('sub-h1');if(d.top<s.bottom)o.push('deal-sub');
 if(d.height>60)o.push('deal-wrap');if(d.bottom>bb.top-8)o.push('main-bottom');
 for(var i=0;i<k.length-1;i++)if(k[i+1].left-k[i].right<8)o.push('gap:'+i);
 if(k[k.length-1].right>1200-64+1)o.push('bottom-overflow');
 return o}
var m=1,n=0;while(bad().length&&n<14){m*=.93;n++;els.forEach(function(e,i){e.style.fontSize=(base[i]*m).toFixed(2)+'px'})}
document.body.setAttribute('data-fit',JSON.stringify({scale:+m.toFixed(3),steps:n,bad:bad()}));
})()</script>'''


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
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for lang in langs:
        for slug in slugs:
            path = OUT/f'{slug}-{lang}.html'
            path.write_text(page(lang, slug, fit=shoot), encoding='utf-8')
            jobs.append((slug, lang, path, ROOT/'assets/og'/f'{slug}-{lang}.png'))
    if not shoot:
        print(f'Prepared {len(jobs)} sharing cards in', OUT)
        return
    exe = chrome()
    if not exe:
        raise SystemExit('找不到 Playwright 的 Chromium，无法截图')
    from PIL import Image
    fails, shrunk = [], 0
    for slug, lang, path, png in jobs:
        url = f'http://localhost:8765/.playwright-mcp/llama-og/{slug}-{lang}.html'
        flags = [exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800', '--virtual-time-budget=6000']
        dom = subprocess.run(flags + ['--dump-dom', url], capture_output=True, timeout=90).stdout.decode('utf-8', 'replace')
        m = re.search(r"data-fit='([^']*)'|data-fit=\"([^\"]*)\"", dom)
        fit = (m.group(1) or m.group(2)).replace('&quot;', '"') if m else 'NO-REPORT'
        ok = '"bad":[]' in fit
        if ok:
            for _ in range(3):  # Chrome 偶发不写文件，重试
                png.unlink(missing_ok=True)
                subprocess.run(flags + [f'--screenshot={png}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
                if png.exists():
                    break
            Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
            shrunk += '"steps":0' not in fit
        else:
            fails.append(f'{slug}-{lang}')
        path.unlink()
        print('png' if ok else 'SKIP', png.relative_to(ROOT), png.stat().st_size if ok else '', 'fit', fit)
    if not any(OUT.iterdir()):
        OUT.rmdir()
    print(f'共 {len(jobs)} 张，缩小字号 {shrunk} 张，违例 {len(fails)} 张')
    if fails:
        raise SystemExit('版面自检未通过，未出图: ' + ', '.join(fails))


if __name__ == '__main__':
    main()
