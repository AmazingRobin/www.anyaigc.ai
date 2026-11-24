# 生成 Claude 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png，截完删掉临时 HTML
# 用法：python scripts/og_claude.py [--langs=ja,ko,es,de] [--slugs=claude,claude-sonnet-5-5] [--html-only]
#   需要 python scripts/preview.py 在 http://localhost:8765 运行；不带参数时 zh、en 全部重生成
# zh / en：文案从页面本身读取：标题取 H1，副标题取 og:title「｜/:」后的卖点，标签取专题首页卡片的 tags，价格取页面价格表
# ja / ko / es / de：专题首页还没做，副标题和标签直接写在下面的 SUBS_I18N、TAGS_I18N；标题和价格取英文页
# 非中文图不写"合同/对公"：开票标签一律写 "Self-service invoices"（2026-11-17 起非中文页口径）
import glob
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 品牌名区分大小写，不要转成全大写
NEW = ('ja', 'ko', 'es', 'de')

# 分享图副标题（每个模型一句卖点）。新增型号时在这里加一行；没写的从 og:title 自动截取
SUBS = {
    'claude':           {'zh': '全系 11 个型号，一个 API Key 调用', 'en': 'Every Claude model, one API key'},
    'claude-opus-5-5':  {'zh': '原生 /v1/messages 接口 · 官方价约 1.2 折', 'en': 'Native /v1/messages API · 88% off list price'},
    'claude-sonnet-5-5': {'zh': '接近 Opus 5.5，官方价约 1.2 折', 'en': 'Near-Opus results at 88% off list price'},
    'claude-haiku-5-5': {'zh': '高并发、低成本任务和子 Agent 之选', 'en': 'High-volume, low-cost work and sub-agents'},
    'claude-fable-5-2': {'zh': '新一代长任务 Agent 模型，官方约 2.4 折', 'en': 'Next-gen long-running agents, 76% off list price'},
    'claude-fable-5-1': {'zh': 'Mythos 级长任务模型，约 2.4 折', 'en': 'Mythos-level long-running agents, 76% off'},
    'claude-fable-5':   {'zh': 'Mythos 级模型，旧版仍可用', 'en': 'Mythos-class model, legacy but still live'},
    'claude-opus-5':    {'zh': '接近 Fable 5 的智能，约 1.2 折', 'en': 'Near-Fable 5 intelligence at 88% off'},
    'claude-sonnet-5':  {'zh': '接近 Opus 4.8 的 Agent 能力', 'en': 'Near-Opus 4.8 agents at 88% off'},
    'claude-opus-4-8':  {'zh': '4.x 系列最终版，约 1.2 折', 'en': 'The final 4.x Opus, 88% off list'},
    'claude-opus-4-7':  {'zh': 'SWE-bench Verified 87.6%，约 1.2 折', 'en': '87.6% SWE-bench Verified, 88% off'},
    'claude-opus-4-6':  {'zh': '旧版仍可用，约官方价 1.2 折', 'en': 'Legacy but still available, 88% off list'},
}

SUBS_I18N = {
    'claude': {'ja': 'Claude 全11モデルを1つのAPIキーで', 'ko': 'Claude 전 모델 11종을 API 키 하나로',
               'es': 'Todos los modelos Claude con una sola clave', 'de': 'Alle Claude-Modelle mit einem Schlüssel'},
    'claude-opus-5-5': {'ja': 'ネイティブ /v1/messages API・定価より88%オフ', 'ko': '네이티브 /v1/messages API · 정가 대비 88% 저렴',
                        'es': 'API nativa /v1/messages · 88 % menos que el precio de lista', 'de': 'Native /v1/messages-API · 88 % unter Listenpreis'},
    'claude-sonnet-5-5': {'ja': 'Opusに迫る性能を定価より88%オフで', 'ko': 'Opus에 근접한 성능, 정가 대비 88% 저렴',
                          'es': 'Resultados cercanos a Opus con un 88 % menos', 'de': 'Ergebnisse nahe Opus, 88 % unter Listenpreis'},
    'claude-haiku-5-5': {'ja': '大量処理・低コストのタスクとサブエージェント向け', 'ko': '대량·저비용 작업과 서브 에이전트용',
                         'es': 'Tareas de alto volumen, bajo coste y subagentes', 'de': 'Hohes Volumen, niedrige Kosten, Sub-Agents'},
    'claude-fable-5-2': {'ja': '次世代の長時間エージェント、定価より76%オフ', 'ko': '차세대 장시간 에이전트, 정가 대비 76% 저렴',
                         'es': 'Agentes de larga duración de nueva generación, 76 % menos', 'de': 'Langlaufende Agenten der nächsten Generation, 76 % günstiger'},
    'claude-fable-5-1': {'ja': 'Mythos級の長時間エージェント、76%オフ', 'ko': 'Mythos급 장시간 에이전트, 76% 저렴',
                         'es': 'Agentes de larga duración nivel Mythos, 76 % menos', 'de': 'Langlaufende Agenten auf Mythos-Niveau, 76 % günstiger'},
    'claude-fable-5': {'ja': 'Mythosクラスのモデル。旧世代ですが利用可能', 'ko': 'Mythos급 모델, 이전 세대지만 계속 사용 가능',
                       'es': 'Modelo clase Mythos, generación anterior pero disponible', 'de': 'Modell der Mythos-Klasse, ältere Generation, weiter verfügbar'},
    'claude-opus-5': {'ja': 'Fable 5に迫る知能を88%オフで', 'ko': 'Fable 5에 근접한 지능, 88% 저렴',
                      'es': 'Inteligencia cercana a Fable 5 con un 88 % menos', 'de': 'Intelligenz nahe Fable 5, 88 % günstiger'},
    'claude-sonnet-5': {'ja': 'Opus 4.8に迫るエージェント性能を88%オフで', 'ko': 'Opus 4.8에 근접한 에이전트, 88% 저렴',
                        'es': 'Agentes cercanos a Opus 4.8 con un 88 % menos', 'de': 'Agenten nahe Opus 4.8, 88 % günstiger'},
    'claude-opus-4-8': {'ja': '4.x系の最終Opus、定価より88%オフ', 'ko': '4.x 마지막 Opus, 정가 대비 88% 저렴',
                        'es': 'El último Opus 4.x, 88 % menos que el precio de lista', 'de': 'Das letzte Opus 4.x, 88 % unter Listenpreis'},
    'claude-opus-4-7': {'ja': 'SWE-bench Verified 87.6%、88%オフ', 'ko': 'SWE-bench Verified 87.6%, 88% 저렴',
                        'es': 'SWE-bench Verified 87.6 %, 88 % menos', 'de': 'SWE-bench Verified 87.6 %, 88 % günstiger'},
    'claude-opus-4-6': {'ja': '旧世代ですが利用可能、定価より88%オフ', 'ko': '이전 세대지만 사용 가능, 정가 대비 88% 저렴',
                        'es': 'Generación anterior, aún disponible, 88 % menos', 'de': 'Ältere Generation, weiter verfügbar, 88 % günstiger'},
}

TAGS_I18N = {
    'claude': {'ja': ['11モデル', '最大88%オフ', '請求書を自分で発行'], 'ko': ['11개 모델', '최대 88% 저렴', '인보이스 직접 발급'],
               'es': ['11 modelos', 'Hasta 88 % menos', 'Facturas en consola'], 'de': ['11 Modelle', 'Bis zu 88 % günstiger', 'Rechnungen im Konto']},
    'claude-opus-5-5': {'ja': ['コーディング', 'プロンプトキャッシュ', 'Claude Code'], 'ko': ['코딩 / 에이전트', '프롬프트 캐싱', 'Claude Code'],
                        'es': ['Código / agentes', 'Caché de prompts', 'Claude Code'], 'de': ['Coding / Agenten', 'Prompt-Caching', 'Claude Code']},
    'claude-sonnet-5-5': {'ja': ['88%オフ', 'Sonnet 5より30%以上高速', '請求書を自分で発行'], 'ko': ['88% 저렴', '30%+ 더 빠름', '인보이스 직접 발급'],
                          'es': ['88 % menos', '30 %+ más rápido', 'Facturas en consola'], 'de': ['88 % günstiger', '30 %+ schneller', 'Rechnungen im Konto']},
    'claude-haiku-5-5': {'ja': ['88%オフ', 'サブエージェント', '同時実行数の上限なし'], 'ko': ['88% 저렴', '서브 에이전트', '동시 실행 제한 없음'],
                         'es': ['88 % menos', 'Subagentes', 'Sin límite de RPM'], 'de': ['88 % günstiger', 'Sub-Agents', 'Kein RPM-Limit']},
    'claude-fable-5-2': {'ja': ['長時間エージェント', 'マルチエージェント', '76%オフ'], 'ko': ['장시간 에이전트', '멀티 에이전트', '76% 저렴'],
                         'es': ['Larga duración', 'Multiagente', '76 % menos'], 'de': ['Langlaufend', 'Multi-Agent', '76 % günstiger']},
    'claude-fable-5-1': {'ja': ['Mythos級', '長時間エージェント', '76%オフ'], 'ko': ['Mythos급', '장시간 에이전트', '76% 저렴'],
                         'es': ['Nivel Mythos', 'Larga duración', '76 % menos'], 'de': ['Mythos-Niveau', 'Langlaufend', '76 % günstiger']},
    'claude-fable-5': {'ja': ['Mythosクラス', '76%オフ', '旧世代・利用可'], 'ko': ['Mythos급', '76% 저렴', '이전 세대, 사용 가능'],
                       'es': ['Clase Mythos', '76 % menos', 'Anterior, disponible'], 'de': ['Mythos-Klasse', '76 % günstiger', 'Älter, verfügbar']},
    'claude-opus-5': {'ja': ['88%オフ', 'Frontier-Bench', '旧世代・利用可'], 'ko': ['88% 저렴', 'Frontier-Bench', '이전 세대, 사용 가능'],
                      'es': ['88 % menos', 'Frontier-Bench', 'Anterior, disponible'], 'de': ['88 % günstiger', 'Frontier-Bench', 'Älter, verfügbar']},
    'claude-sonnet-5': {'ja': ['エージェント', 'コーディング', '88%オフ'], 'ko': ['에이전트', '코딩', '88% 저렴'],
                        'es': ['Agentes', 'Código', '88 % menos'], 'de': ['Agenten', 'Coding', '88 % günstiger']},
    'claude-opus-4-8': {'ja': ['4.x最終版', '88%オフ', 'Claude Code'], 'ko': ['4.x 최종', '88% 저렴', 'Claude Code'],
                        'es': ['Último 4.x', '88 % menos', 'Claude Code'], 'de': ['Letztes 4.x', '88 % günstiger', 'Claude Code']},
    'claude-opus-4-7': {'ja': ['SWE-bench 87.6%', '高解像度の画像入力', '88%オフ'], 'ko': ['SWE-bench 87.6%', '고해상도 비전', '88% 저렴'],
                        'es': ['SWE-bench 87.6 %', 'Visión en alta resolución', '88 % menos'], 'de': ['SWE-bench 87.6 %', 'Hochauflösende Bilder', '88 % günstiger']},
    'claude-opus-4-6': {'ja': ['利用可能', '1Mコンテキスト長', '88%オフ'], 'ko': ['사용 가능', '1M 컨텍스트', '88% 저렴'],
                        'es': ['Disponible', 'Contexto de 1M', '88 % menos'], 'de': ['Verfügbar', '1M Kontext', '88 % günstiger']},
}
OVERVIEW_PRICE = {'ja': '$0.0119 / 100万トークンから', 'ko': '$0.0119 / 100만 토큰부터', 'es': 'Desde $0.0119 / 1 M', 'de': 'Ab $0.0119 / 1 Mio.'}
PRICE_UNIT = {'zh': ' / 1M 输入', 'en': ' / 1M input', 'ja': ' / 100万入力トークン', 'ko': ' / 100만 입력 토큰', 'es': ' / 1 M entrada', 'de': ' / 1 Mio. Eingabe'}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#faf9f5;color:#141413;font-family:Inter,"Segoe UI","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",sans-serif;position:relative;overflow:hidden}
.c{position:absolute;left:90px;top:96px;right:90px}
.b{font-size:28px;font-weight:700;letter-spacing:.01em}
.t{display:flex;align-items:center;gap:26px;margin-top:38px}
h1{margin:0;font-family:Georgia,"Songti SC","SimSun",serif;font-size:@FSpx;line-height:1;font-weight:500;letter-spacing:-2px;white-space:nowrap}
p{margin:30px 0 0;font-family:Georgia,"Songti SC","SimSun",serif;font-size:34px;color:#30302e}
.n p{font-family:"Segoe UI","Yu Gothic UI","Malgun Gothic",sans-serif;font-size:31px;line-height:1.3}
.r{position:absolute;left:90px;bottom:80px;display:flex;gap:14px}
.r span{padding:10px 20px;border-radius:999px;background:#f5f4ed;border:1px solid #e8e6dc;font-size:24px;color:#3d3d3a;white-space:nowrap}
.r.s{gap:12px}
.r.s span{padding:9px 16px;font-size:21px}
.r span.d{background:#141413;border-color:#141413;color:#faf9f5}
</style></head><body class="@BC"><div class="c"><div class="b">@BRAND</div><div class="t"><svg viewBox="0 0 24 24" width="92" height="92" fill="#d97757"><path d="@STAR"/></svg><h1>@NAME</h1></div><p>@SUB</p></div><div class="r @RC">@CHIPS</div></body></html>'''


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def arg(prefix):
    for a in sys.argv[1:]:
        if a.startswith(prefix):
            return a.split('=', 1)[1].split(',')
    return None


def render(star, name, sub, chips, fs, lang):
    new = lang in NEW
    return (TPL.replace('@BRAND', BRAND).replace('@STAR', star).replace('@NAME', name).replace('@SUB', sub)
            .replace('@CHIPS', chips).replace('@FS', fs).replace('@BC', 'n' if new else '').replace('@RC', 's' if new else ''))


def main():
    os.makedirs(OUT, exist_ok=True)
    names = []
    langs = arg('--langs=') or ['zh', 'en']
    only = arg('--slugs=')
    star = re.search(r'<path\b[^>]*?d="([^"]+)"', read('assets/icons/claude-color.svg')).group(1)  # lobe-icons claude-color
    for lang in langs:
        src_lang = lang if lang in ('zh', 'en') else 'en'         # 新语言的标题、价格取英文页
        hub = read(f'{lang}/models/index.html') if lang in ('zh', 'en') else ''
        for f in sorted(os.listdir(os.path.join(ROOT, src_lang, 'models'))):
            if not (f.startswith('claude') and f.endswith('.html')):
                continue
            slug = f[:-5]
            if only and slug not in only:
                continue
            s = read(f'{src_lang}/models/{f}')
            n = f'{slug}-{lang}'
            if slug == 'claude':
                # 系列总览页：标题固定为 Claude API，标签取全系卖点
                if lang in NEW:
                    tags, first = TAGS_I18N['claude'][lang], OVERVIEW_PRICE[lang]
                    sub = SUBS_I18N['claude'][lang]
                else:
                    tags = ['11 个型号', '约官方 1.2 折起', '对公 · 专票'] if lang == 'zh' else ['11 models', 'Up to 88% off', 'Self-service invoices']
                    first = '$0.0119 / 1M 起' if lang == 'zh' else 'From $0.0119 / 1M'
                    sub = SUBS['claude'][lang]
                chips = f'<span class="d">{first}</span>' + ''.join(f'<span>{t}</span>' for t in tags)
                html = render(star, 'Claude API', sub, chips, '104', lang)
            else:
                name = re.sub(r'\s*API$', '', re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)).strip())
                price = re.search(r'<td class="o-num o-hl">(\$[0-9.]+)</td>', s).group(1)
                if lang in NEW:
                    sub, tags = SUBS_I18N[slug][lang], TAGS_I18N[slug][lang]
                else:
                    sub = SUBS.get(slug, {}).get(lang)
                    if not sub:
                        og_title = re.search(r'property="og:title" content="([^"]*)"', s).group(1)
                        sub = re.split(r'[｜:]', og_title, maxsplit=1)[-1]
                        sub = re.sub(r'\s*[-|]\s*AnyAIGC.*$', '', sub).strip()
                    card = re.search(r'href="/' + lang + '/models/' + re.escape(slug) + r'">.*?<ul class="af-tags">(.*?)</ul>', hub, re.S)
                    tags = re.findall(r'<li>([^<]*)</li>', card.group(1))[:3] if card else []
                    chips = f'<span class="d">{price}{PRICE_UNIT[lang]}</span>' + ''.join(f'<span>{t}</span>' for t in tags)
                html = render(star, name, sub, chips, '96' if len(name) <= 15 else '88', lang)
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))
    exe = chrome()
    if '--html-only' in sys.argv or not exe:
        return
    from PIL import Image
    for n in names:
        png = os.path.join(ROOT, 'assets', 'og', n + '.png')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        # 无头 Chrome 的窗口尺寸含浏览器边框，截得偏矮；放大窗口再裁成 1200×630
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        print('png', os.path.relpath(png, ROOT), os.path.getsize(png) if os.path.exists(png) else 'MISSING')
    for n in names:
        os.remove(os.path.join(OUT, n + '.html'))
    if os.path.isdir(OUT) and not os.listdir(OUT):
        os.rmdir(OUT)


if __name__ == '__main__':
    main()
