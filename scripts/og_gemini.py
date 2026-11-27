# 生成 Gemini 系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_gemini.py（需要 python scripts/preview.py 在 http://localhost:8765 运行，或传 --html-only 只生成 HTML）
# 风格跟 assets/models/gemini.css 一致：纯白底、#121317 墨色、Gemini 渐变（#217bfe → #078efb → #ac87eb → #ee4d5d）光晕和标题关键词
# logo 读 assets/icons/gemini-color.svg（lobe-icons，见 scripts/icons.py）
import glob
import io
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

# 每个页面：标题前半、渐变关键词、一句卖点、价格标签、其余标签
PAGES = {
    'gemini-4-hydrogen': ('Gemini 4', 'Hydrogen',
                          {'zh': '日常编码与 Agent 的快速模型，约官方 3.6 折', 'en': 'Fast model for everyday coding and agents, 64% off'},
                          {'zh': '$0.5360 / 1M 输入', 'en': '$0.5360 / 1M input'},
                          {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Self-service invoices']}),
    'gemini-4-carbon': ('Gemini 4', 'Carbon',
                        {'zh': '长周期 Agent 前沿模型，约官方 3.6 折', 'en': 'Frontier model for long-horizon agents, 64% off'},
                        {'zh': '$0.7147 / 1M 输入', 'en': '$0.7147 / 1M input'},
                        {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Self-service invoices']}),
    'gemini-4-argon': ('Gemini 4', 'Argon',
                       {'zh': 'Google 旗舰推理模型，约官方价 2.1 折', 'en': "Google's flagship reasoning model, ~79% off"},
                       {'zh': '$0.4200 / 1M 输入', 'en': '$0.4200 / 1M input'},
                       {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Self-service invoices']}),
    'gemini-3.8-flash': ('Gemini 3.8', 'Flash',
                         {'zh': 'Google 称最智能的 Flash，快且便宜', 'en': "Google's most intelligent Flash model"},
                         {'zh': '$0.1575 / 1M 输入', 'en': '$0.1575 / 1M input'},
                         {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Self-service invoices']}),
    'gemini-3.8-flash-tts': ('Gemini 3.8', 'Flash TTS',
                             {'zh': '语音合成，30 种音色、双人对话', 'en': 'Text to speech with 30 voices and two speakers'},
                             {'zh': '¥1.2 / 1M 输入 · 官方 3.6 折', 'en': '36% of Google list price'},
                             {'zh': ['130+ 语言', '并发不限', '对公 · 专票'], 'en': ['130+ languages', 'Unlimited RPM', 'Self-service invoices']}),
    'gemini-3.1-pro-preview': ('Gemini 3.1', 'Pro',
                               {'zh': 'Gemini 3 代 Pro 预览版，复杂推理与多模态', 'en': 'Gemini 3 Pro preview for complex reasoning'},
                               {'zh': '$0.1985 / 1M 输入', 'en': '$0.1985 / 1M input'},
                               {'zh': ['1M 上下文', '并发不限', '对公 · 专票'], 'en': ['1M context', 'Unlimited RPM', 'Self-service invoices']}),
}


# 新语言（ja / ko / es / de）的卖点和标签。标题（型号名）和价格数字取自上面的英文条目；非中文图不写合同/对公，发票写"自助开具"。
NEW = ('ja', 'ko', 'es', 'de')
SUBS_I18N = {
    'gemini-4-hydrogen': {'ja': '日常のコーディングとエージェント向けの高速モデル、64%オフ', 'ko': '일상 코딩과 에이전트용 고속 모델, 64% 저렴',
                          'es': 'Modelo rápido para programar y agentes, 64 % menos', 'de': 'Schnelles Modell für Coding und Agenten, 64 % günstiger'},
    'gemini-4-carbon': {'ja': '長時間エージェント向けのフロンティアモデル、64%オフ', 'ko': '장시간 에이전트용 프런티어 모델, 64% 저렴',
                        'es': 'Modelo de frontera para agentes de larga duración, 64 % menos', 'de': 'Frontier-Modell für langlaufende Agenten, 64 % günstiger'},
    'gemini-4-argon': {'ja': 'Googleのフラッグシップ推論モデル、約79%オフ', 'ko': 'Google 플래그십 추론 모델, 약 79% 저렴',
                       'es': 'Modelo insignia de razonamiento de Google, aprox. 79 % menos', 'de': 'Googles Flaggschiff-Reasoning-Modell, rund 79 % günstiger'},
    'gemini-3.8-flash': {'ja': 'Google最高性能のFlashモデル', 'ko': 'Google에서 가장 똑똑한 Flash 모델',
                         'es': 'El modelo Flash más inteligente de Google', 'de': 'Googles intelligentestes Flash-Modell'},
    'gemini-3.8-flash-tts': {'ja': '30種類の音声と2人の話者に対応した音声合成', 'ko': '30가지 음성과 2명의 화자를 지원하는 음성 합성',
                             'es': 'Síntesis de voz con 30 voces y dos hablantes', 'de': 'Sprachsynthese mit 30 Stimmen und zwei Sprechern'},
    'gemini-3.1-pro-preview': {'ja': '複雑な推論向けの Gemini 3 Pro プレビュー', 'ko': '복잡한 추론을 위한 Gemini 3 Pro 프리뷰',
                               'es': 'Vista previa de Gemini 3 Pro para razonamiento complejo', 'de': 'Gemini 3 Pro Preview für komplexes Reasoning'},
}
TAGS_I18N = {
    'ctx': {'ja': ['1Mコンテキスト長', '同時実行数の上限なし', '請求書を自分で発行'], 'ko': ['1M 컨텍스트', '동시 실행 제한 없음', '인보이스 직접 발급'],
            'es': ['Contexto de 1M', 'Sin límite de RPM', 'Facturas en consola'], 'de': ['1M Kontext', 'Kein RPM-Limit', 'Rechnungen im Konto']},
    'tts': {'ja': ['130以上の言語', '同時実行数の上限なし', '請求書を自分で発行'], 'ko': ['130개 이상 언어', '동시 실행 제한 없음', '인보이스 직접 발급'],
            'es': ['130+ idiomas', 'Sin límite de RPM', 'Facturas en consola'], 'de': ['130+ Sprachen', 'Kein RPM-Limit', 'Rechnungen im Konto']},
}
PRICE_FMT = {'ja': '{p} / 100万入力トークン', 'ko': '{p} / 100만 입력 토큰', 'es': '{p} / 1 M entrada', 'de': '{p} / 1 Mio. Eingabe'}
TTS_PRICE = {'ja': 'Google定価の36%', 'ko': 'Google 정가의 36%', 'es': '36 % del precio de lista de Google', 'de': '36 % des Google-Listenpreises'}


def i18n_texts(slug, lang, price_en):
    sub = SUBS_I18N[slug][lang]
    tags = TAGS_I18N['tts' if slug.endswith('flash-tts') else 'ctx'][lang]
    if price_en.startswith('$'):
        price = PRICE_FMT[lang].format(p=price_en.split(' / ')[0])
    else:
        price = TTS_PRICE[lang]
    return sub, price, tags

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
body{margin:0;width:1200px;height:630px;background:#fff;color:#121317;font-family:"Google Sans Flex","Google Sans",Inter,"Segoe UI",Arial,"PingFang SC","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",sans-serif;position:relative;overflow:hidden}
.g1,.g2{position:absolute;border-radius:50%;filter:blur(80px)}
.g1{width:760px;height:520px;right:-180px;top:-160px;background:radial-gradient(closest-side,rgba(33,123,254,.55),rgba(7,142,251,.22) 60%,transparent)}
.g2{width:620px;height:420px;right:60px;top:220px;background:radial-gradient(closest-side,rgba(172,135,235,.5),rgba(238,77,93,.2) 60%,transparent)}
.mark{position:absolute;right:64px;top:110px;width:220px;height:220px}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:72px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:600;letter-spacing:-.02em}
.b em{font-style:normal;font-weight:400;color:#5f6368}
.b svg{width:30px;height:30px}
h1{margin:96px 0 0;max-width:860px;font-size:@FSpx;line-height:1;font-weight:450;letter-spacing:-.035em}
h1 span{background:linear-gradient(90deg,#217bfe 0%,#078efb 33.53%,#ac87eb 67.74%,#ee4d5d 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
p{margin:26px 0 0;font-size:34px;line-height:1.3;color:#45474d;max-width:700px}
.n p{font-size:27px;max-width:800px;line-height:1.25}
.r{position:absolute;left:80px;bottom:64px;display:flex;gap:12px}
.r span{padding:12px 20px;border-radius:999px;background:#f8f9fc;border:1px solid rgba(33,34,38,.1);font-size:24px;color:#45474d;white-space:nowrap}
.r.s{gap:10px}
.r.s span{padding:10px 16px;font-size:21px}
.r .d{background:#121317;color:#fff;border-color:#121317}
.line{position:absolute;left:0;right:0;bottom:0;height:8px;background:linear-gradient(90deg,#217bfe 0%,#078efb 33.53%,#ac87eb 67.74%,#ee4d5d 100%)}
</style></head><body class="@BC"><div class="g1"></div><div class="g2"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· Google Gemini</em></div><h1>@NAME <span>@KEY</span></h1><p>@SUB</p></div>
<div class="r @RC">@CHIPS</div><div class="line"></div></body></html>'''


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = read('assets/icons/gemini-color.svg')
    names = []
    only = [a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--langs=')]
    for lang in (only[0] if only else ('zh', 'en')):
        for slug, (name, key, sub, price, tags) in PAGES.items():
            if not os.path.exists(os.path.join(ROOT, 'en' if lang in NEW else lang, 'models', slug + '.html')):
                continue
            if lang in NEW:
                sub, price, tags = dict(sub), dict(price), dict(tags)
                sub[lang], price[lang], tags[lang] = i18n_texts(slug, lang, PAGES[slug][3]['en'])
            chips = f'<span class="d">{price[lang]}</span>' + ''.join(f'<span>{t}</span>' for t in tags[lang])
            fs = '120' if len(name + key) <= 14 else ('108' if len(name + key) <= 17 else '92')
            small = logo.replace('lobe-icons-gemini-', 'sm-')
            html = (TPL.replace('@LOGO', logo).replace('@SMALL', small).replace('@BRAND', BRAND).replace('@NAME', name)
                    .replace('@KEY', key).replace('@SUB', sub[lang]).replace('@CHIPS', chips).replace('@FS', fs)
                    .replace('@BC', 'n' if lang in NEW else '').replace('@RC', 's' if lang in NEW else ''))
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))
    exe = chrome()
    if '--html-only' in sys.argv or not exe:
        return
    for n in names:
        png = os.path.join(ROOT, 'assets', 'og', n + '.png')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1200,800',
                        '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        # 无头 Chrome 的窗口尺寸含浏览器边框，截得偏矮；放大窗口再裁成 1200×630
        from PIL import Image
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        print('png', os.path.relpath(png, ROOT), os.path.getsize(png) if os.path.exists(png) else 'MISSING')


if __name__ == '__main__':
    main()
