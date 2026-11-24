# -*- coding: utf-8 -*-
"""生成站点首页：中文在 /index.html，其余语言在 /<lang>/index.html（en ja ko es de）。
文案在 scripts/home_copy/<lang>.json（六种语言结构相同，只有企业卡片、支付方式、FAQ 的条数允许不同），
样式 assets/home/home.css，脚本 assets/home/home.js。改文案或结构后重新运行：
    PYTHONIOENCODING=utf-8 python scripts/home_page.py            # 六种语言全部生成，并更新 sitemap.xml
    PYTHONIOENCODING=utf-8 python scripts/home_page.py en ja       # 只生成指定语言
不要手改生成出来的 index.html。
口径：中文页按 CLAUDE.md 的企业接入（增值税专票、对公转账、合同）；非中文页按海外口径（自助开票，不写对公转账、合同、
增值税、国内直连）。事实来源：AGENTS.md「固定信息」、CLAUDE.md「支付方式 / 信任与保障」。不写 SLA、可用率、令牌分组、企业专属线路。
"""
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = '20261123i'
MENU_CSS = '/assets/models/lang-menu.css?v=20261123c'
MENU_JS = '/assets/models/lang-menu.js?v=20261117c'
SITE = 'https://www.anyaigc.ai'
TODAY = '2026-11-23'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
CONSOLE = 'https://anyaigc.ai/console'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai'
BASE = 'https://anyaigc.ai/v1'
def legal(lang, page):
    return f'/{page}' if lang == 'zh' else f'/{lang}/{page}'

LANGS = ['zh', 'en', 'ja', 'ko', 'es', 'de']
HL = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
OG = {'zh': 'zh_CN', 'en': 'en_US', 'ja': 'ja_JP', 'ko': 'ko_KR', 'es': 'es_ES', 'de': 'de_DE'}
NATIVE = {'zh': '中文', 'en': 'English', 'ja': '日本語', 'ko': '한국어', 'es': 'Español', 'de': 'Deutsch'}
SHORT = {'zh': 'ZH', 'en': 'EN', 'ja': 'JA', 'ko': 'KO', 'es': 'ES', 'de': 'DE'}


def path(lang):
    return '/' if lang == 'zh' else f'/{lang}/'


def url(lang):
    return SITE + path(lang)


def out_file(lang):
    return os.path.join(ROOT, 'index.html' if lang == 'zh' else os.path.join(lang, 'index.html'))


def e(s):
    return html.escape(s, quote=False)


def a(s):
    return html.escape(s, quote=True)


def fill(s, lang):
    """文案里的占位符：{privacy} {support} {docs} {base}"""
    return s.replace('{privacy}', legal(lang, 'privacy')).replace('{support}', SUPPORT).replace('{docs}', DOCS).replace('{base}', BASE)


# 厂商 logo：彩色版直接用 <img>；单色版（fill=currentColor）用 mask 画成白色，深色背景下清晰可见
def ic(name, mono=False, size=22):
    if mono:
        return f'<span class="ic mono-ic" style="--u:url(/assets/icons/{name}.svg)" aria-hidden="true"></span>'
    return f'<img class="ic" src="/assets/icons/{name}.svg" width="{size}" height="{size}" alt="" loading="lazy" decoding="async">'


VENDOR_ICONS = [('claude-color', False), ('openai', True), ('gemini-color', False), ('grok', True), ('deepseek-color', False),
                ('qwen', True), ('kimi', True), ('zhipu-color', False), ('kling', True), ('bytedance-color', False), ('minimax-color', False)]

MODEL_SLUGS = [  # (slug, 图标, 是否单色)，顺序与文案 models.items 对应
    ('claude', 'claude-color', False), ('gpt', 'openai', True), ('gemini-4-hydrogen', 'gemini-color', False), ('grok-4.x', 'grok', True),
    ('deepseek', 'deepseek-color', False), ('qwen', 'qwen', True), ('kimi', 'kimi', True), ('glm', 'zhipu-color', False),
    ('kling', 'kling', True), ('seedance', 'bytedance-color', False), ('seedream', 'bytedance-color', False), ('minimax', 'minimax-color', False),
]

CHIPS = ['gpt-6.2-sol', 'deepseek-v4-flash', 'kimi-k3', 'glm-5.3', 'qwen3.8-max']  # 都在各自专题页的 /v1/chat/completions 示例里出现过


def load(lang):
    with io.open(os.path.join(ROOT, 'scripts', 'home_copy', lang + '.json'), encoding='utf-8') as f:
        return json.load(f)


def lines(items):
    out = []
    for i, (cls, text) in enumerate(items):
        out.append(f'<span class="ln" style="--i:{i}"><span class="{cls}">{text}</span></span>' if cls else
                   f'<span class="ln" style="--i:{i}">{text}</span>')
    return ''.join(out)


def code_blocks(c):
    m = f'<span class="m">{CHIPS[0]}</span>'
    msg = e(c['term']['user_msg'])
    curl = lines([
        ('', f'<span class="k">curl</span> {BASE}/chat/completions \\'),
        ('', '  -H <span class="s">"Authorization: Bearer $ANYAIGC_API_KEY"</span> \\'),
        ('', '  -H <span class="s">"Content-Type: application/json"</span> \\'),
        ('', "  -d <span class=\"s\">'{</span>"),
        ('', f'    <span class="s">"model": "</span>{m}<span class="s">",</span>'),
        ('', f'    <span class="s">"messages": [{{"role": "user", "content": "{msg}"}}]</span>'),
        ('', "  <span class=\"s\">}'</span>"),
        ('c', e(c['term']['comment'])),
    ])
    py = lines([
        ('', '<span class="k">import</span> os'),
        ('', '<span class="k">from</span> openai <span class="k">import</span> OpenAI'),
        ('', ''),
        ('', 'client = OpenAI('),
        ('', f'    base_url=<span class="s">"{BASE}"</span>,'),
        ('', '    api_key=os.environ[<span class="s">"ANYAIGC_API_KEY"</span>],'),
        ('', ')'),
        ('', 'resp = client.chat.completions.create('),
        ('', f'    model=<span class="s">"</span>{m}<span class="s">"</span>,'),
        ('', f'    messages=[{{<span class="s">"role"</span>: <span class="s">"user"</span>, <span class="s">"content"</span>: <span class="s">"{msg}"</span>}}],'),
        ('', ')'),
        ('', 'print(resp.choices[0].message.content)'),
    ])
    return curl, py


def lang_menu(lang):
    items = ''.join(f'<li><a href="{path(c)}" hreflang="{HL[c]}" lang="{HL[c]}">{NATIVE[c]}</a></li>' for c in LANGS if c != lang)
    return (f'<details class="lang-menu"><summary aria-label="Language: {NATIVE[lang]}">{SHORT[lang]}</summary>'
            f'<ul class="lang-menu-list">{items}</ul></details>')


def build(lang):
    c = load(lang)
    hub = f'/{lang}/models/'
    sep = '。' if lang in ('zh', 'ja') else '. '
    marq = ''.join(f'<li>{ic(icon, mono)}{e(name)}</li>' for name, (icon, mono) in zip(c['vendors'], VENDOR_ICONS))
    models = ''.join(
        f'<a class="card mc rv" href="{hub}{slug}"><span class="tile">{ic(icon, mono, 24)}</span>'
        f'<div><h3>{e(name)}</h3><p>{e(desc)}</p></div><span class="go" aria-hidden="true">→</span></a>'
        for (name, desc), (slug, icon, mono) in zip(c['models']['items'], MODEL_SLUGS))
    tools = ''.join(f'<a href="{DOCS}" target="_blank" rel="noopener" class="rv"><b>{e(n)}</b><span>{e(d)}</span></a>' for n, d in c['tools']['items'])
    faq_items = [(q, fill(ans, lang)) for q, ans in c['faq']['items']]
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{ans}</p></details>' for q, ans in faq_items)
    chips = ''.join(f'<button type="button" data-m="{m}" aria-pressed="{"true" if i == 0 else "false"}">{m}</button>' for i, m in enumerate(CHIPS))
    curl, py = code_blocks(c)
    why = ''.join(
        f'<div class="card rv"><span class="tag">{e(x["tag"])}</span>' + (f'<div class="big">{e(x["big"])}</div>' if x.get('big') else '')
        + f'<h3>{e(x["h"])}</h3><p>{e(x["p"])}</p></div>' for x in c['why']['cards'])
    steps = ''.join(f'<div class="card rv"><div class="n mono">{i + 1:02d}</div><h3>{e(h)}</h3><p>{e(p)}</p></div>' for i, (h, p) in enumerate(c['start']['steps']))
    ent_cards = c['ent']['cards']
    ent = ''.join(f'<div class="card rv"><span class="tag">{e(x["tag"])}</span><h3>{e(x["h"])}</h3><p>{e(x["p"])}</p></div>' for x in ent_cards)
    pay = ''.join(f'<em>{e(p)}</em>' for p in c['ent']['pay'])
    trust = ''.join(f'<li>{fill(x, lang)}</li>' for x in c['trust']['items'])
    stats = ''.join(f'<div><b>{e(b)}</b><span>{e(s)}</span></div>' for b, s in c['stats'])
    nav = c['nav']
    fl = c['foot']['links']
    foot_urls = [hub, PRICING, DOCS, SUPPORT, legal(lang, 'privacy'), legal(lang, 'terms')]
    foot_links = ''.join(
        f'<a href="{u}"' + (' target="_blank" rel="noopener"' if u == DOCS else '') + f'>{e(t)}</a>' for t, u in zip(fl, foot_urls))
    other_langs = ''.join(f'<a href="{path(x)}" hreflang="{HL[x]}" lang="{HL[x]}">{NATIVE[x]}</a>' for x in LANGS if x != lang)

    title = c['title']
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'Organization', '@id': SITE + '/#org', 'name': 'AnyAIGC', 'url': SITE + '/', 'logo': SITE + '/assets/home/logo-512.png'},
            {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'AnyAIGC', 'publisher': {'@id': SITE + '/#org'}},
            {'@type': 'WebPage', '@id': url(lang) + '#webpage', 'url': url(lang), 'name': title, 'inLanguage': HL[lang],
             'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'}},
            {'@type': 'FAQPage', 'inLanguage': HL[lang], 'mainEntity': [
                {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(re.sub(r'<[^>]+>', '', ans))}} for q, ans in faq_items]},
        ],
    }
    alts = '\n'.join(f'<link rel="alternate" hreflang="{HL[x]}" href="{url(x)}">' for x in LANGS)
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{url("en")}">'
    og_alts = '\n'.join(f'<meta property="og:locale:alternate" content="{OG[x]}">' for x in LANGS if x != lang)

    return f'''<!DOCTYPE html>
<html lang="{HL[lang]}" data-scrollbar="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{a(c['desc'])}">
<meta name="keywords" content="{a(c['keywords'])}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0f0b0a">
<link rel="canonical" href="{url(lang)}">
{alts}
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{OG[lang]}">
{og_alts}
<meta property="og:url" content="{url(lang)}">
<meta property="og:title" content="{a(title)}">
<meta property="og:description" content="{a(c['og_desc'])}">
<meta property="og:image" content="{SITE}/assets/og/models-{lang}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{a(c['og_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{a(title)}">
<meta name="twitter:description" content="{a(c['og_desc'])}">
<meta name="twitter:image" content="{SITE}/assets/og/models-{lang}.png">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261125">
<link rel="stylesheet" href="{MENU_CSS}">
<link rel="stylesheet" href="/assets/home/home.css?v={VER}">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<a class="skip" href="#main">{e(c['skip'])}</a>
<header class="nav">
  <div class="nav-in">
    <a class="brand" href="{path(lang)}" aria-label="{a(c['brand_aria'])}"><img src="/assets/home/logo.webp?v={VER}" width="102" height="42" alt="AnyAIGC"></a>
    <nav class="nav-links" aria-label="{a(c['nav_aria'])}">
      <a href="{hub}">{e(nav[0])}</a>
      <a href="{PRICING}">{e(nav[1])}</a>
      <a href="#start">{e(nav[2])}</a>
      <a href="#enterprise">{e(nav[3])}</a>
      <a href="{DOCS}" target="_blank" rel="noopener">{e(nav[4])}</a>
    </nav>
    <div class="nav-r">
      {lang_menu(lang)}
      <a class="login" href="{CONSOLE}">{e(c['login'])}</a>
      <a class="btn btn-p btn-s" href="{a(REG)}">{e(c['cta_key'])}</a>
    </div>
  </div>
</header>
<main id="main">
<section class="hero">
  <i class="aur a1" aria-hidden="true"></i><i class="aur a2" aria-hidden="true"></i><i class="aur a3" aria-hidden="true"></i>
  <div class="wrap">
    <div class="hero-in">
      <div>
        <span class="badge"><i class="dot" aria-hidden="true"></i>{e(c['hero']['badge'])}</span>
        <h1>{e(c['hero']['h1a'])}<br><span class="g">{e(c['hero']['h1b'])}</span></h1>
        <p class="lead">{e(c['hero']['lead'])}</p>
        <div class="cta">
          <a class="btn btn-p" href="{a(REG)}">{e(c['cta_key'])}</a>
          <a class="btn" href="{DOCS}" target="_blank" rel="noopener">{e(c['hero']['btn_docs'])}</a>
        </div>
        <a class="sub-link" href="{SUPPORT}">{e(c['hero']['sub_link'])}</a>
      </div>
      <div class="term" id="demo">
        <div class="term-bar">
          <i></i><i></i><i></i>
          <div class="tabs" role="tablist" aria-label="{a(c['term']['tabs_aria'])}">
            <button type="button" role="tab" data-t="curl" aria-selected="true">cURL</button>
            <button type="button" role="tab" data-t="py" aria-selected="false">Python</button>
          </div>
          <span class="term-url">POST /v1/chat/completions</span>
        </div>
        <div class="chips" role="group" aria-label="{a(c['term']['chips_aria'])}">{chips}</div>
        <pre class="code" data-p="curl" lang="en"><code>{curl}<span class="cur" aria-hidden="true"></span></code></pre>
        <pre class="code" data-p="py" lang="en" hidden><code>{py}</code></pre>
        <p class="term-note">{c['term']['note']}</p>
      </div>
    </div>
    <div class="stats" aria-label="{a(c['stats_aria'])}">{stats}</div>
  </div>
</section>

<div class="marq" aria-label="{a(c['marq_aria'])}">
  <div class="track"><ul>{marq}</ul><ul aria-hidden="true">{marq}</ul></div>
</div>

<section class="sec cv" id="why">
  <div class="wrap">
    <p class="eyebrow">01 / WHY ANYAIGC</p>
    <h2>{e(c['why']['h2'])}</h2>
    <p class="sec-lead">{e(c['why']['lead'])}</p>
    <div class="bento">{why}</div>
  </div>
</section>

<section class="sec cv" id="models">
  <div class="wrap">
    <p class="eyebrow">02 / MODELS</p>
    <h2>{e(c['models']['h2'])}</h2>
    <p class="sec-lead">{e(c['models']['lead'])}</p>
    <div class="models">{models}</div>
    <a class="more" href="{hub}">{e(c['models']['more'])}</a>
  </div>
</section>

<section class="sec cv" id="start">
  <div class="wrap">
    <p class="eyebrow">03 / QUICK START</p>
    <h2>{e(c['start']['h2'])}</h2>
    <p class="sec-lead">{e(c['start']['lead'])}</p>
    <div class="steps">{steps}</div>
    <div class="base">
      <span class="mono" style="color:var(--mu);font-size:13px">Base URL</span>
      <code>{BASE}</code>
      <button type="button" class="btn btn-s" data-copy="{BASE}" data-done="{a(c['start']['done'])}">{e(c['start']['copy'])}</button>
    </div>
    <p class="base-note">{e(c['start']['note'])}</p>
  </div>
</section>

<section class="sec cv" id="tools" style="padding-top:24px">
  <div class="wrap">
    <p class="eyebrow">04 / TOOLS</p>
    <h2>{e(c['tools']['h2'])}</h2>
    <p class="sec-lead">{e(c['tools']['lead'])}</p>
    <div class="tools">{tools}</div>
  </div>
</section>

<section class="sec cv ent" id="enterprise">
  <div class="wrap">
    <p class="eyebrow">05 / ENTERPRISE</p>
    <h2>{e(c['ent']['h2'])}</h2>
    <p class="sec-lead">{e(c['ent']['lead'])}</p>
    <div class="ent-grid c{len(ent_cards)}">{ent}</div>
    <div class="pay"><span class="l">{e(c['ent']['pay_label'])}</span>{pay}</div>
    <div class="cta">
      <a class="btn btn-p" href="{SUPPORT}">{e(c['ent']['btn_support'])}</a>
      <a class="btn" href="{a(REG)}">{e(c['ent']['btn_reg'])}</a>
    </div>
  </div>
</section>

<section class="sec cv" id="trust">
  <div class="wrap">
    <p class="eyebrow">06 / TRUST</p>
    <h2>{e(c['trust']['h2'])}</h2>
    <ul class="trust">{trust}</ul>
    <div class="cta" style="margin-top:28px"><a class="btn btn-p" href="{a(REG)}">{e(c['trust']['btn'])}</a></div>
  </div>
</section>

<section class="sec cv" id="faq" style="padding-top:24px">
  <div class="wrap">
    <p class="eyebrow">07 / FAQ</p>
    <h2>{e(c['faq']['h2'])}</h2>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="sec cv" style="padding-top:24px">
  <div class="wrap">
    <div class="final">
      <h2>{e(c['final']['h2'])}</h2>
      <p>{e(c['final']['p'])}</p>
      <div class="cta">
        <a class="btn btn-p" href="{a(REG)}">{e(c['final']['btn_reg'])}</a>
        <a class="btn" href="{PRICING}">{e(c['final']['btn_pricing'])}</a>
      </div>
    </div>
  </div>
</section>
</main>
<footer class="foot">
  <div class="wrap">
    <a class="foot-logo" href="{path(lang)}" aria-label="{a(c['brand_aria'])}"><img src="/assets/home/logo.webp?v={VER}" width="78" height="32" alt="AnyAIGC" loading="lazy"></a>
    <div class="foot-links">{foot_links}</div>
    <div class="foot-links foot-langs">{other_langs}</div>
    <p>&copy; 2026 AnyAIGC{sep}{e(c['foot']['note'])}</p>
  </div>
</footer>
<script src="{MENU_JS}" defer></script>
<script src="/assets/home/home.js?v={VER}" defer></script>
</body>
</html>
'''


def sitemap_block(lang):
    alts = ''.join(f'    <xhtml:link rel="alternate" hreflang="{HL[x]}" href="{url(x)}"/>\n' for x in LANGS)
    alts += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url("en")}"/>\n'
    return f'  <url>\n    <loc>{url(lang)}</loc>\n    <lastmod>{TODAY}</lastmod>\n{alts}  </url>'


def update_sitemap():
    p = os.path.join(ROOT, 'sitemap.xml')
    s = io.open(p, encoding='utf-8').read()
    pat = {x: re.compile(r'[ \t]*<url>\s*<loc>' + re.escape(url(x)) + r'</loc>.*?</url>\n?', re.S) for x in LANGS}
    first = pat['zh'].search(s)
    if not first:
        raise SystemExit('sitemap.xml 里找不到首页条目')
    for x in LANGS[1:]:
        s = pat[x].sub('', s)
    first = pat['zh'].search(s)
    blocks = '\n'.join(sitemap_block(x) for x in LANGS) + '\n'
    s = s[:first.start()] + blocks + s[first.end():]
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)


if __name__ == '__main__':
    want = [x for x in sys.argv[1:] if x in LANGS] or LANGS
    for lang in want:
        out = build(lang)
        p = out_file(lang)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        io.open(p, 'w', encoding='utf-8', newline='\n').write(out)
        print(p.replace(ROOT + os.sep, ''), len(out.encode('utf-8')) // 1024, 'KB')
    if len(sys.argv) == 1:
        update_sitemap()
        print('sitemap.xml 已更新')
