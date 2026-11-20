# 生成 GPT 系列专题页分享图（1200×630）的 HTML 源文件，输出到 .playwright-mcp/og/，再用 Playwright 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_gpt.py → 在 http://localhost:8765/.playwright-mcp/og/<name>.html 截图
# 价格读 .playwright-mcp/gpt_data.json 不稳定（临时文件），所以直接读页面价格表第一行的 AnyAIGC 价格
import glob
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写

# 每个页面一句卖点 + 3 个标签
SUBS = {
    'gpt':           ({'zh': 'OpenAI 全系 10 个型号，一个 API Key 调用', 'en': 'Every OpenAI GPT model, one API key'},
                      {'zh': ['10 个型号', '约官方 0.5 折起', '对公 · 专票'], 'en': ['10 models', 'Up to 95% off', 'Self-service invoices']}),
    'gpt-6-astra':   ({'zh': 'OpenAI 旗舰模型，约官方价 0.5 折', 'en': "OpenAI's flagship model at 95% off"},
                      {'zh': ['最高智能', 'Codex', '并发不限'], 'en': ['Top tier', 'Codex', 'Unlimited concurrency']}),
    'gpt-6.1-sol':   ({'zh': '接近 Astra 的智能，约官方价 0.5 折', 'en': 'Near-Astra intelligence at 95% off'},
                      {'zh': ['Responses API', 'Codex', '并发不限'], 'en': ['Responses API', 'Codex', 'Unlimited concurrency']}),
    'gpt-6.1-terra': ({'zh': '识图与电脑操作，约官方价 0.5 折', 'en': 'Vision and computer use at 95% off'},
                      {'zh': ['Computer Use', '视觉推理', '并发不限'], 'en': ['Computer use', 'Visual reasoning', 'Unlimited concurrency']}),
    'gpt-6-luna':    ({'zh': '高频批量任务，速度快、成本低', 'en': 'Fast, low-cost, built for volume'},
                      {'zh': ['约 1.3 折', '高频批量', '并发不限'], 'en': ['86% off', 'High volume', 'Unlimited concurrency']}),
    'gpt-6-sol':     ({'zh': '官方价比 GPT-5.6 Sol 低 50%', 'en': '50% below GPT-5.6 Sol list price'},
                      {'zh': ['约 0.5 折', '已有 6.1 Sol', '仍可调用'], 'en': ['95% off', 'Newer: 6.1 Sol', 'Still available']}),
    'gpt-5.6-sol':   ({'zh': 'GPT-5.6 旗舰，推广价约 0.6 折', 'en': 'GPT-5.6 flagship at 94% off promo price'},
                      {'zh': ['ultra 多智能体', 'Codex', '并发不限'], 'en': ['Ultra multi-agent', 'Codex', 'Unlimited concurrency']}),
    'gpt-5.6-terra': ({'zh': '比肩 GPT-5.5 的日常模型，约 0.5 折', 'en': 'GPT-5.5-class everyday model at 95% off'},
                      {'zh': ['均衡', '约 0.5 折', '并发不限'], 'en': ['Balanced', '95% off', 'Unlimited concurrency']}),
    'gpt-5.6-luna':  ({'zh': '大批量低价任务，约官方价 1.3 折', 'en': 'High-volume, low-cost at 86% off'},
                      {'zh': ['工具调用', '多步工作流', '并发不限'], 'en': ['Tool use', 'Multistep', 'Unlimited concurrency']}),
    'gpt-5.5':       ({'zh': '上一代旗舰，仍可调用，约 0.5 折', 'en': 'Previous flagship, still available, 95% off'},
                      {'zh': ['Terminal-Bench 2.0', 'Codex', '并发不限'], 'en': ['Terminal-Bench 2.0', 'Codex', 'Unlimited concurrency']}),
    'gpt-5.5-pro':   ({'zh': '高算力深度推理，仅 Responses API', 'en': 'More compute, deeper reasoning, Responses API'},
                      {'zh': ['约 5.9 折', '高准确率', 'Responses'], 'en': ['41% off', 'High accuracy', 'Responses only']}),
}


# ---- 新语言（ja / ko / es / de）：副标题按型号写，标签按英文原文查表。非中文图不写合同/对公，发票写"自助开具"。
NEW = ('ja', 'ko', 'es', 'de')
SUB_I18N = {
    'gpt': {'ja': 'OpenAI GPT 全10モデルを1つのAPIキーで', 'ko': 'OpenAI GPT 전 모델 10종을 API 키 하나로',
            'es': 'Todos los modelos GPT de OpenAI con una sola clave', 'de': 'Alle OpenAI-GPT-Modelle mit einem Schlüssel'},
    'gpt-6-astra': {'ja': 'OpenAIのフラッグシップ、定価より95%オフ', 'ko': 'OpenAI 플래그십, 정가 대비 95% 저렴',
                    'es': 'Modelo insignia de OpenAI, 95 % menos', 'de': 'OpenAIs Flaggschiff, 95 % günstiger'},
    'gpt-6.1-sol': {'ja': 'Astraに迫る知能を95%オフで', 'ko': 'Astra에 근접한 지능, 95% 저렴',
                    'es': 'Inteligencia cercana a Astra con un 95 % menos', 'de': 'Intelligenz nahe Astra, 95 % günstiger'},
    'gpt-6.1-terra': {'ja': '画像理解とコンピュータ操作を95%オフで', 'ko': '비전과 컴퓨터 사용, 95% 저렴',
                      'es': 'Visión y uso del ordenador con un 95 % menos', 'de': 'Bildverständnis und Computer Use, 95 % günstiger'},
    'gpt-6-luna': {'ja': '高速・低コストの大量処理向け', 'ko': '빠르고 저렴한 대량 처리용',
                   'es': 'Rápido, económico y pensado para volumen', 'de': 'Schnell, günstig, für hohes Volumen'},
    'gpt-6-sol': {'ja': 'GPT-5.6 Sol の定価より50%安い', 'ko': 'GPT-5.6 Sol 정가보다 50% 저렴',
                  'es': '50 % menos que el precio de lista de GPT-5.6 Sol', 'de': '50 % unter dem Listenpreis von GPT-5.6 Sol'},
    'gpt-5.6-sol': {'ja': 'GPT-5.6 のフラッグシップ、プロモ価格で94%オフ', 'ko': 'GPT-5.6 플래그십, 프로모션가 94% 저렴',
                    'es': 'Modelo insignia GPT-5.6, 94 % menos (precio promocional)', 'de': 'GPT-5.6-Flaggschiff, 94 % günstiger (Aktionspreis)'},
    'gpt-5.6-terra': {'ja': 'GPT-5.5級の日常モデルを95%オフで', 'ko': 'GPT-5.5급 일상용 모델, 95% 저렴',
                      'es': 'Modelo cotidiano de nivel GPT-5.5, 95 % menos', 'de': 'Alltagsmodell auf GPT-5.5-Niveau, 95 % günstiger'},
    'gpt-5.6-luna': {'ja': '大量・低コスト向け、86%オフ', 'ko': '대량·저비용 작업용, 86% 저렴',
                     'es': 'Alto volumen y bajo coste, 86 % menos', 'de': 'Hohes Volumen, niedrige Kosten, 86 % günstiger'},
    'gpt-5.5': {'ja': '前世代のフラッグシップ、利用可能、95%オフ', 'ko': '이전 세대 플래그십, 계속 사용 가능, 95% 저렴',
                'es': 'Anterior modelo insignia, aún disponible, 95 % menos', 'de': 'Früheres Flaggschiff, weiter verfügbar, 95 % günstiger'},
    'gpt-5.5-pro': {'ja': '高い計算量で深く推論、Responses API', 'ko': '더 많은 연산으로 깊은 추론, Responses API',
                    'es': 'Más cómputo y razonamiento más profundo, Responses API', 'de': 'Mehr Rechenleistung, tieferes Reasoning, Responses API'},
}


def _t(ja, ko, es, de):
    return {'ja': ja, 'ko': ko, 'es': es, 'de': de}


TAG_I18N = {
    'Self-service invoices': _t('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
    'Unlimited concurrency': _t('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    '10 models': _t('10モデル', '10개 모델', '10 modelos', '10 Modelle'),
    'Up to 95% off': _t('最大95%オフ', '최대 95% 저렴', 'Hasta 95 % menos', 'Bis zu 95 % günstiger'),
    'Top tier': _t('最上位', '최상위', 'Gama alta', 'Spitzenklasse'),
    'Codex': _t('Codex', 'Codex', 'Codex', 'Codex'),
    'Responses API': _t('Responses API', 'Responses API', 'Responses API', 'Responses API'),
    'Computer use': _t('コンピュータ操作', '컴퓨터 사용', 'Uso del ordenador', 'Computer Use'),
    'Visual reasoning': _t('視覚推論', '시각 추론', 'Razonamiento visual', 'Visuelles Reasoning'),
    '86% off': _t('86%オフ', '86% 저렴', '86 % menos', '86 % günstiger'),
    '95% off': _t('95%オフ', '95% 저렴', '95 % menos', '95 % günstiger'),
    '41% off': _t('41%オフ', '41% 저렴', '41 % menos', '41 % günstiger'),
    'High volume': _t('大量処理', '대량 처리', 'Alto volumen', 'Hohes Volumen'),
    'Newer: 6.1 Sol': _t('新型: 6.1 Sol', '신형: 6.1 Sol', 'Nuevo: 6.1 Sol', 'Neuer: 6.1 Sol'),
    'Still available': _t('利用可能', '계속 사용 가능', 'Aún disponible', 'Weiter verfügbar'),
    'Ultra multi-agent': _t('ultra マルチエージェント', 'ultra 멀티 에이전트', 'Multiagente ultra', 'Ultra-Multi-Agent'),
    'Balanced': _t('バランス型', '균형형', 'Equilibrado', 'Ausgewogen'),
    'Tool use': _t('ツール利用', '도구 사용', 'Uso de herramientas', 'Tool-Nutzung'),
    'Multistep': _t('マルチステップ', '다단계', 'Varios pasos', 'Mehrstufig'),
    'Terminal-Bench 2.0': _t('Terminal-Bench 2.0', 'Terminal-Bench 2.0', 'Terminal-Bench 2.0', 'Terminal-Bench 2.0'),
    'High accuracy': _t('高精度', '높은 정확도', 'Alta precisión', 'Hohe Genauigkeit'),
    'Responses only': _t('Responses のみ', 'Responses 전용', 'Solo Responses', 'Nur Responses'),
}
PRICE_FMT = {'ja': '{p} / 100万入力トークン', 'ko': '{p} / 100만 입력 토큰', 'es': '{p} / 1 M entrada', 'de': '{p} / 1 Mio. Eingabe'}
OVERVIEW_PRICE = {'ja': '$0.0135 / 100万トークンから', 'ko': '$0.0135 / 100만 토큰부터', 'es': 'Desde $0.0135 / 1 M', 'de': 'Ab $0.0135 / 1 Mio.'}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#000;color:#fff;font-family:Inter,"PingFang SC","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",system-ui,sans-serif;position:relative;overflow:hidden}
.glow{position:absolute;inset:0;background:radial-gradient(circle at 74% 44%,rgba(250,229,152,.22),rgba(184,128,43,.10) 22%,transparent 46%),radial-gradient(circle at 50% 50%,#0d1a22 0%,#071016 40%,#000 75%)}
.disc{position:absolute;left:640px;top:70px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle at 45% 40%,#1b2a30,#071016 70%);box-shadow:0 0 120px rgba(250,229,152,.10)}
.c{position:absolute;left:80px;top:80px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:26px;font-weight:600;letter-spacing:-.01em}
.b svg{width:30px;height:30px}
h1{margin:120px 0 0;font-size:@FSpx;line-height:1;font-weight:500;letter-spacing:-.03em;color:#f5f6fb;white-space:nowrap}
p{margin:22px 0 0;font-size:34px;line-height:1.3;color:rgba(255,255,255,.82);letter-spacing:-.01em}
.r{position:absolute;left:80px;bottom:64px;display:flex;gap:12px}
.r span{padding:10px 20px;border-radius:999px;border:1px solid rgba(255,255,255,.28);font-size:23px;color:rgba(255,255,255,.9);white-space:nowrap}
.r span.d{background:#fff;border-color:#fff;color:#000;font-weight:600}
.n p{font-size:30px;max-width:760px;line-height:1.25}
.r.s{gap:10px}
.r.s span{padding:9px 15px;font-size:20px}
</style></head><body class="@BC"><div class="glow"></div><div class="disc"></div><div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#ffffff" fill-rule="evenodd"><path d="@LOGO"/></svg>@BRAND</div><h1>@NAME</h1><p>@SUB</p></div><div class="r @RC">@CHIPS</div></body></html>'''


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = re.search(r' d="([^"]+)"', read('assets/icons/openai.svg')).group(1)
    names = []
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    for lang in (only[0] if only else ('zh', 'en')):
        src_lang = 'en' if lang in NEW else lang
        for slug, (sub, tags) in SUBS.items():
            p = f'{src_lang}/models/{slug}.html'
            if not os.path.exists(os.path.join(ROOT, p)):
                continue
            s = read(p)
            if slug == 'gpt':
                name = 'GPT API'
                price = OVERVIEW_PRICE[lang] if lang in NEW else ('$0.0135 / 1M 起' if lang == 'zh' else 'From $0.0135 / 1M')
            else:
                h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)
                h1 = re.sub(r'<span class="o-sr">.*?</span>', '', h1, flags=re.S)
                name = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h1)).strip()
                name = re.sub(r'\s*API$', '', name)
                name = re.sub(r'^GPT (\d)', r'GPT-\1', name)  # 拆分标题 GPT / 5.5 还原为 GPT-5.5
                m = re.search(r'<td class="o-num o-hl">(\$[0-9.]+)</td>', s)
                if lang in NEW:
                    price = PRICE_FMT[lang].format(p=m.group(1))
                else:
                    price = m.group(1) + (' / 1M 输入' if lang == 'zh' else ' / 1M input')
            if lang in NEW:
                sub_l, tags_l = SUB_I18N[slug][lang], [TAG_I18N[t][lang] for t in tags['en']]
            else:
                sub_l, tags_l = sub[lang], tags[lang]
            chips = f'<span class="d">{price}</span>' + ''.join(f'<span>{t}</span>' for t in tags_l)
            fs = '120' if len(name) <= 11 else ('104' if len(name) <= 13 else '92')
            html = (TPL.replace('@LOGO', logo).replace('@BRAND', BRAND).replace('@NAME', name)
                    .replace('@SUB', sub_l).replace('@CHIPS', chips).replace('@FS', fs)
                    .replace('@BC', 'n' if lang in NEW else '').replace('@RC', 's' if lang in NEW else ''))
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))
    exe = chrome()
    if not only or '--html-only' in sys.argv or not exe:
        return
    from PIL import Image
    for n in names:
        png = os.path.join(ROOT, 'assets', 'og', n + '.png')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        os.remove(os.path.join(OUT, n + '.html'))
        print('png', os.path.relpath(png, ROOT), os.path.getsize(png))


if __name__ == '__main__':
    main()
