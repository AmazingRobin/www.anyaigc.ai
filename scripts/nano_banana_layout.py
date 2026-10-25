# Nano Banana 系列专题页的 HTML 版块拼装（与语言无关，文案由 nano_banana_copy_zh/en.py 提供）。
import html
import json
import re

from nano_banana_data import DATE, VER, SITE, REG, PRICING, SUPPORT, IMG, GALLERY_SRC

NL = '\n'

L = {
    'zh': dict(lang='zh-CN', og='zh_CN', og_alt='en_US', other='en', other_name='English', home='首页', hub='模型专题',
               market='模型广场', price='价格', ent='企业接入', docs='API 文档', login='登录',
               signup='免费注册', get_key='获取 API Key', see_price='查看价格', view_market='在模型广场查看',
               skip='跳到主要内容', nav='主导航', crumbs='面包屑', facts='核心信息', copy='复制', copied='已复制',
               code='代码示例', sales='联系企业客服', trial='先注册试用', signup_any='免费注册 AnyAIGC', read_docs='阅读 API 文档',
               all_hub='全部模型专题', more='更多', series_all='Nano Banana 全系总览', in_other='Nano Banana API in English',
               credit='示例图来自 Google DeepMind 的 Nano Banana 模型页，由 Nano Banana 系列模型生成，版权归 Google 所有。',
               credit_link='查看来源', home_label='AnyAIGC 首页',
               foot_desc='国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。',
               foot=('产品', '资源', '条款'), foot_links=('模型专题', '模型广场', '控制台', 'API 文档 ↗', '图像接口文档 ↗', '联系我们', '隐私政策', '服务条款'),
               legal='&copy; 2026 AnyAIGC。Google、Gemini、Nano Banana 是 Google LLC 的商标。AnyAIGC 是独立的 API 服务商，与 Google 无隶属或合作关系。页面示例图片来自 Google DeepMind，版权归 Google 所有；官方价格与参数引自 Google 公开资料。',
               ent_cards=[('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。'),
                          ('对公转账', '公司账户直接付款', '支持企业对公转账充值，无需个人垫付，账目清晰。'),
                          ('签订合同', '满足采购与法务流程', '可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。'),
                          ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。')],
               ent_lead='电商公司、设计团队和内容平台可以直接走企业流程采购，财务、法务和技术对接都有对应支持。'),
    'en': dict(lang='en', og='en_US', og_alt='zh_CN', other='zh', other_name='中文', home='Home', hub='Model guides',
               market='Model catalog', price='Pricing', ent='Enterprise', docs='API docs', login='Log in',
               signup='Sign up free', get_key='Get an API key', see_price='See pricing', view_market='View in the model catalog',
               skip='Skip to main content', nav='Main', crumbs='Breadcrumb', facts='Key facts', copy='Copy', copied='Copied',
               code='Code examples', sales='Talk to sales', trial='Start with a free account', signup_any='Sign up for AnyAIGC',
               read_docs='Read the API docs', all_hub='All model guides', more='More', series_all='Nano Banana overview',
               in_other='Nano Banana API 中文版',
               credit="Sample images are from Google DeepMind's Nano Banana model pages, generated with Nano Banana models. Images © Google.",
               credit_link='View source', home_label='AnyAIGC home',
               foot_desc='An API gateway for global AI models. One base URL and one API key for 300+ models.',
               foot=('Product', 'Resources', 'Legal'), foot_links=('Model guides', 'Model catalog', 'Console', 'API docs ↗', 'Image API docs ↗', 'Contact us', 'Privacy Policy', 'Terms of Service'),
               legal='&copy; 2026 AnyAIGC. Google, Gemini and Nano Banana are trademarks of Google LLC. AnyAIGC is an independent API provider and is not affiliated with Google. Sample images come from Google DeepMind and are © Google. Official prices and specs are quoted from Google\'s public documentation.',
               ent_cards=[('Invoices', 'Including China VAT invoices', 'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.'),
                          ('Bank transfer', 'Pay from a company account', 'Top up by corporate bank transfer, so nobody has to pay on a personal card and expense it.'),
                          ('Contracts', 'Fits procurement and legal review', 'Sign a service agreement with AnyAIGC to meet your internal purchasing requirements.'),
                          ('Dedicated support', 'Account and technical contacts', 'Work with a dedicated support contact and technical engineer for onboarding, migration and troubleshooting.')],
               ent_lead='E-commerce companies, design teams and content platforms can buy through a standard business process, with support for finance, legal and engineering.'),
}

ICON = None  # 运行时从 assets/icons/nanobanana-color.svg 读取（彩色版，颜色写在 path 的 fill 上）


def logo(size=None, cls=''):
    s = f' width="{size}" height="{size}"' if size else ''
    c = f' class="{cls}"' if cls else ''
    return f'<svg{c} viewBox="0 0 24 24"{s} aria-hidden="true" focusable="false">{ICON}</svg>'


def url(lang, slug):
    return f'{SITE}/{lang}/models/{slug}'


def text(h):
    """HTML 转纯文本（JSON-LD 用）"""
    t = re.sub(r'<[^>]+>', '', h)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


def img(name, lang, cls='', eager=False, sizes=None):
    w, h, zt, zd, et, ed = IMG[name]
    alt = f'{zt}：{zd}（Nano Banana 生成）' if lang == 'zh' else f'{et}: {ed} (generated with Nano Banana)'
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    sz = f' sizes="{sizes}"' if sizes else ''
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="/assets/models/nano-banana/{name}.webp" width="{w}" height="{h}" alt="{html.escape(alt, quote=True)}"{load} decoding="async"{sz}>'


def credit(lang):
    t = L[lang]
    return f'<p class="nb-credit">{t["credit"]} <a href="{GALLERY_SRC}" target="_blank" rel="noopener">{t["credit_link"]} ↗</a></p>'


# ---------------- 代码高亮（极简：字符串 / 注释 / 关键字） ----------------
KW = r'\b(import|from|with|as|for|in|if|not|break|True|False|None|print|def|return)\b'


def hl(code):
    out = []
    for line in code.split(NL):
        parts = re.split(r'("(?:[^"\\]|\\.)*")', line)
        buf = ''
        comment = False
        for i, p in enumerate(parts):
            if comment:
                buf += html.escape(p, quote=False)
                continue
            if i % 2 == 1:
                buf += f'<span class="s">{html.escape(p, quote=False)}</span>'
                continue
            m = re.search(r'(^|\s)#\s', p)
            if m:
                pre, post = p[:m.start() + len(m.group(1))], p[m.start() + len(m.group(1)):]
                buf += re.sub(KW, r'<span class="k">\1</span>', html.escape(pre, quote=False))
                buf += '<span class="c">' + html.escape(post, quote=False)
                comment = True
                continue
            buf += re.sub(KW, r'<span class="k">\1</span>', html.escape(p, quote=False))
        if comment:
            buf += '</span>'
        out.append(buf)
    return NL.join(out)


# ---------------- head ----------------
def head(lang, slug, c):
    me, zh, en = url(lang, slug), url('zh', slug), url('en', slug)
    og_img = f'{SITE}/assets/og/{slug}-{lang}.png'
    t = L[lang]
    crumbs = [(t['home'], f'{SITE}/'), (t['hub'], f'{SITE}/{lang}/models/')]
    if slug != 'nano-banana':
        crumbs.append(('Nano Banana', url(lang, 'nano-banana')))
    crumbs.append((c['crumb'], me))
    offers = c['offers']
    cur = c['currency']
    graph = [
        {'@type': 'Organization', '@id': f'{SITE}/#org', 'name': 'AnyAIGC', 'url': 'https://anyaigc.ai', 'logo': f'{SITE}/logo.webp'},
        {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'AnyAIGC', 'publisher': {'@id': f'{SITE}/#org'}},
        {'@type': 'WebPage', '@id': f'{me}#webpage', 'url': me, 'name': c['title'], 'description': c['desc'], 'inLanguage': t['lang'],
         'isPartOf': {'@id': f'{SITE}/#website'}, 'breadcrumb': {'@id': f'{me}#breadcrumb'}, 'mainEntity': {'@id': f'{me}#product'},
         'dateModified': DATE},
        {'@type': 'BreadcrumbList', '@id': f'{me}#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]},
        {'@type': 'Product', '@id': f'{me}#product', 'name': c['product'], 'description': c['product_desc'],
         'category': '图像生成 API' if lang == 'zh' else 'Image generation API', 'sku': c['sku'], 'image': og_img,
         'brand': {'@type': 'Brand', 'name': 'AnyAIGC'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': cur, 'lowPrice': min(offers, key=lambda o: float(o[1]))[1],
                    'highPrice': max(offers, key=lambda o: float(o[1]))[1], 'offerCount': len(offers),
                    'availability': 'https://schema.org/InStock', 'url': f'{me}#pricing',
                    'offers': [{'@type': 'Offer', 'name': n, 'price': p, 'priceCurrency': cur} for n, p in offers]}},
        {'@type': 'FAQPage', '@id': f'{me}#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}} for q, a in c['faqs']]},
    ]
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    e = lambda s: html.escape(s, quote=True)
    return f'''<!DOCTYPE html>
<html lang="{t['lang']}" class="no-js" data-scrollbar="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(c['title'])}</title>
<meta name="description" content="{e(c['desc'])}">
<meta name="keywords" content="{e(c['keywords'])}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#121317">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{zh}">
<link rel="alternate" hreflang="en" href="{en}">
<link rel="alternate" hreflang="x-default" href="{en}">
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{t['og']}">
<meta property="og:locale:alternate" content="{t['og_alt']}">
<meta property="og:url" content="{me}">
<meta property="og:title" content="{e(c['title'])}">
<meta property="og:description" content="{e(c['og_desc'])}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(c['og_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(c['title'])}">
<meta name="twitter:description" content="{e(c['og_desc'])}">
<meta name="twitter:image" content="{og_img}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261024b">
<link rel="stylesheet" href="/assets/models/nano-banana.css?v={VER}">
<script type="application/ld+json">
{ld}
</script>
</head>
'''


def nav(lang, slug):
    t = L[lang]
    o = t['other']
    return f'''<body>
<a class="o-skip" href="#main">{t['skip']}</a>

<header class="o-nav">
  <div class="o-wrap o-nav-inner">
    <a class="o-brand" href="/" aria-label="{t['home_label']}">AnyAIGC</a>
    <nav aria-label="{t['nav']}">
      <ul class="o-nav-left">
        <li><a class="o-pill" href="/{lang}/models/">{t['hub']}</a></li>
        <li class="nb-hide-md"><a class="o-pill" href="/{lang}/models/nano-banana">Nano Banana</a></li>
        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="#pricing">{t['price']}</a></li>
        <li><a class="o-pill" href="#enterprise">{t['ent']}</a></li>
        <li class="nb-hide-md"><a class="o-pill" href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{t['docs']}</a></li>
      </ul>
    </nav>
    <ul class="o-nav-right">
      <li><a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_name']}</a></li>
      <li class="nb-hide-sm"><a class="o-pill" href="https://anyaigc.ai/console">{t['login']}</a></li>
      <li><a class="o-btn o-btn-dark nb-nav-cta" href="{REG}">{t['signup']}</a></li>
    </ul>
  </div>
</header>

<main id="main">
'''


def hero(lang, slug, c):
    t = L[lang]
    crumbs = [f'<li><a href="/">{t["home"]}</a></li>', f'<li><a href="/{lang}/models/">{t["hub"]}</a></li>']
    if slug != 'nano-banana':
        crumbs.append(f'<li><a href="/{lang}/models/nano-banana">Nano Banana</a></li>')
    crumbs.append(f'<li aria-current="page">{c["crumb"]}</li>')
    facts = ''.join(f'<li>{k} <strong>{v}</strong></li>' for k, v in c['facts'])
    notice = f'        <p class="o-notice" role="note">{c["notice"]}</p>{NL}' if c.get('notice') else ''
    a, b, d = c['hero_imgs']
    return f'''  <!-- Hero -->
  <section class="nb-hero" aria-labelledby="hero-title">
    <div class="nb-hero-glow" aria-hidden="true"></div>
    <div class="o-wrap nb-hero-grid">
      <div class="nb-hero-copy">
        <nav aria-label="{t['crumbs']}">
          <ol class="o-crumbs">
            {''.join(crumbs)}
          </ol>
        </nav>
        <p class="nb-eyebrow">{logo(22)}<span>{c['eyebrow']}</span></p>
        <h1 class="nb-h1" id="hero-title">{c['h1']}</h1>
        <p class="nb-lead">{c['lead']}</p>
        <p class="nb-lead-sub">{c['lead_sub']}</p>
        <div class="o-cta">
          <a class="o-btn o-btn-dark" href="{REG}">{t['get_key']}</a>
          <a class="o-btn o-btn-light" href="#pricing">{t['see_price']}</a>
        </div>
{notice}        <ul class="o-facts" aria-label="{t['facts']}">{facts}</ul>
      </div>
      <div class="nb-hero-media">
        <div class="nb-collage">
          <figure class="nb-main">{img(a, lang, eager=True, sizes="(max-width: 900px) 100vw, 600px")}</figure>
          <figure>{img(b, lang, eager=True, sizes="(max-width: 900px) 50vw, 300px")}</figure>
          <figure>{img(d, lang, sizes="(max-width: 900px) 50vw, 300px")}</figure>
        </div>
        {credit(lang)}
      </div>
    </div>
  </section>

'''


def section(sid, h2, inner, lead='', band=False, wide=True, title_id=None):
    cls = 'o-section nb-band' if band else 'o-section'
    wrap = 'o-wrap nb-wide' if wide else 'o-wrap o-col'
    tid = title_id or f'{sid}-title'
    lead_html = f'      <p class="o-lead o-reveal">{lead}</p>{NL}' if lead else ''
    return (f'  <section class="{cls}" id="{sid}" aria-labelledby="{tid}">{NL}    <div class="{wrap}">{NL}'
            f'      <h2 class="o-h2 o-reveal" id="{tid}">{h2}</h2>{NL}{lead_html}{inner}    </div>{NL}  </section>{NL}{NL}')


def quote(c):
    return (f'  <section class="nb-quote" aria-label="{html.escape(text(c["quote"]), quote=True)}">{NL}'
            f'    <div class="o-wrap"><p class="o-reveal">{c["quote"]}</p></div>{NL}  </section>{NL}{NL}')


def about(c):
    ps = ''.join(f'        <p class="o-reveal">{p}</p>{NL}' for p in c['about_ps'])
    spec = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in c['spec'])
    inner = f'      <div class="nb-prose">{NL}{ps}      </div>{NL}      <dl class="nb-spec o-reveal">{spec}</dl>{NL}'
    return section('about', c['about_h2'], inner)


def models(c):
    lis = ''
    for href, tag, name, mid, p, price, unit, cur in c['models']:
        cls = ' is-current' if cur else ''
        lis += (f'        <li class="o-reveal"><a class="nb-model{cls}" href="{href}"><span class="nb-tag">{tag}</span>'
                f'<h3>{name}</h3><code>{mid}</code><p>{p}</p>'
                f'<span class="nb-model-price"><strong>{price}</strong>{unit}</span><span class="nb-go" aria-hidden="true">→</span></a></li>{NL}')
    return section('models', c['models_h2'], f'      <ul class="nb-models">{NL}{lis}      </ul>{NL}', c.get('models_lead', ''))


def features(lang, c):
    lis = ''.join(f'        <li class="nb-feature o-reveal"><figure>{img(n, lang, sizes="(max-width: 900px) 100vw, 400px")}</figure>'
                  f'<div><h3>{h}</h3><p>{p}</p></div></li>{NL}' for h, p, n in c['features'])
    return section('features', c['features_h2'], f'      <ul class="nb-features">{NL}{lis}      </ul>{NL}', c.get('features_lead', ''))


def table(caption, head_cells, groups, cls=''):
    """groups: [(组标题或 None, [行 html])]；head_cells: [(文字, 是否数字列)]"""
    th = ''.join(f'<th scope="col"{" class=\"o-num\"" if num else ""}>{h}</th>' for h, num in head_cells)
    body = ''
    for title, rows in groups:
        gcls = ' class="nb-group"' if title else ''
        body += f'          <tbody{gcls}>{NL}'
        if title:
            body += f'            <tr><th scope="rowgroup" colspan="{len(head_cells)}">{title}</th></tr>{NL}'
        body += ''.join(f'            <tr>{r}</tr>{NL}' for r in rows)
        body += f'          </tbody>{NL}'
    wcls = f'o-table-wrap {cls} o-reveal' if cls else 'o-table-wrap o-reveal'
    return (f'      <div class="{wcls}">{NL}        <table class="o-table">{NL}'
            f'          <caption class="o-sr">{caption}</caption>{NL}          <thead><tr>{th}</tr></thead>{NL}{body}'
            f'        </table>{NL}      </div>{NL}')


def pricing(lang, c):
    t = L[lang]
    bill = ''.join(f'<li><strong>{a}</strong>{b}</li>' for a, b in c['billing'])
    costs = ''.join(f'''        <li class="o-cost o-reveal">
          <h4>{h}</h4>
          <p class="o-cost-calc">{calc}</p>
          <p class="o-cost-total">{tot}</p>
          <p class="o-cost-off">{off}</p>
        </li>{NL}''' for h, calc, tot, off in c['costs'])
    inner = (f'      <ul class="o-billing o-reveal" aria-label="{c["billing_label"]}">{bill}</ul>{NL}'
             + c['price_tables'] +
             f'      <p class="o-note">{c["price_note"]}</p>{NL}'
             + c.get('price_extra', '') +
             f'      <h3 class="nb-h3 o-reveal">{c["costs_h3"]}</h3>{NL}      <p class="o-note">{c["costs_lead"]}</p>{NL}'
             f'      <ul class="o-costs">{NL}{costs}      </ul>{NL}'
             f'      <div class="o-price-cta o-reveal">{NL}        <a class="o-btn o-btn-dark" href="{REG}">{t["get_key"]}</a>{NL}'
             f'        <a class="o-btn o-btn-light" href="{PRICING}">{t["view_market"]}</a>{NL}      </div>{NL}')
    return section('pricing', c['price_h2'], inner, c['price_lead'])


def compare(c):
    inner = c['compare_table'] + (f'      <p class="o-note">{c["compare_note"]}</p>{NL}' if c.get('compare_note') else '')
    return section('compare', c['compare_h2'], inner, c.get('compare_lead', ''), band=True)


def gallery(lang, c):
    figs = []
    for n in c['gallery']:
        w, h, zt, zd, et, ed = IMG[n]
        tt, dd = (zt, zd) if lang == 'zh' else (et, ed)
        figs.append(f'        <figure class="o-reveal">{img(n, lang, sizes="(max-width: 640px) 100vw, (max-width: 900px) 50vw, 400px")}<figcaption><b>{tt}</b>{dd}</figcaption></figure>')
    inner = (f'      <div class="nb-gallery">{NL}' + NL.join(figs) + f'{NL}      </div>{NL}      {credit(lang)}{NL}')
    return section('gallery', c['gallery_h2'], inner, c['gallery_lead'])


def uses(c):
    lis = ''.join(f'        <li class="o-reveal"><span class="nb-k">{k}</span><h3>{h}</h3><p>{p}</p></li>{NL}' for k, h, p in c['uses'])
    return section('use-cases', c['uses_h2'], f'      <ul class="nb-uses">{NL}{lis}      </ul>{NL}', c.get('uses_lead', ''), band=True)


def quickstart(lang, c):
    t = L[lang]
    steps = ''.join(f'        <li>{s}</li>{NL}' for s in c['steps'])
    tabs, panels = [], []
    for i, (tid, label, cap, code) in enumerate(c['codes']):
        sel = 'true' if i == 0 else 'false'
        tabs.append(f'        <li role="presentation"><button type="button" role="tab" id="tab-{tid}" aria-controls="panel-{tid}" aria-selected="{sel}">{label}</button></li>')
        panels.append(f'''      <figure class="o-code" id="panel-{tid}" role="tabpanel" aria-labelledby="tab-{tid}">
        <figcaption><b>{cap}</b><button class="o-copy" type="button" aria-controls="code-{tid}" data-done="{t['copied']}">{t['copy']}</button></figcaption>
<pre id="code-{tid}"><code>{hl(code)}</code></pre>
      </figure>''')
    inner = (f'      <ol class="o-steps o-reveal">{NL}{steps}      </ol>{NL}'
             f'      <ul class="o-tabs" role="tablist" aria-label="{t["code"]}">{NL}' + NL.join(tabs) + f'{NL}      </ul>{NL}'
             + NL.join(panels) + NL +
             f'      <p class="nb-callout o-reveal">{c["callout"]}</p>{NL}      <p class="o-note">{c["qs_note"]}</p>{NL}')
    return section('quickstart', c['qs_h2'], inner)


def enterprise(lang, name):
    t = L[lang]
    h2 = f'企业接入 {name} API' if lang == 'zh' else f'{name} API for teams and enterprises'
    cards = ''.join(f'        <li class="o-card o-reveal"><strong>{a}</strong><h3>{b}</h3><p>{d}</p></li>{NL}' for a, b, d in t['ent_cards'])
    inner = (f'      <ul class="o-cards">{NL}{cards}      </ul>{NL}'
             f'      <div class="o-price-cta o-reveal">{NL}        <a class="o-btn o-btn-dark" href="{SUPPORT}">{t["sales"]}</a>{NL}'
             f'        <a class="o-btn o-btn-light" href="{REG}">{t["trial"]}</a>{NL}      </div>{NL}')
    return section('enterprise', h2, inner, t['ent_lead'], band=True, wide=False, title_id='ent-title')


def family(lang, slug, items, h2, lead):
    lis = []
    for s, tag, title, sub in items:
        cur = ' aria-current="page"' if s == slug else ''
        tg = f'<span class="o-tag">{tag}</span>' if tag else ''
        lis.append(f'        <li><a href="/{lang}/models/{s}"{cur}>{tg}<b>{title}</b><span>{sub}</span></a></li>')
    inner = f'      <ul class="o-family o-reveal">{NL}' + NL.join(lis) + f'{NL}      </ul>{NL}'
    return f'  <!-- FAMILY -->{NL}' + section('family', h2, inner, lead, wide=False)


def faq(c):
    items = []
    for i, (q, a) in enumerate(c['faqs']):
        op = ' open' if i == 0 else ''
        items.append(f'        <details{op}><summary><h3>{q}</h3></summary><div class="o-ans"><p>{a}</p></div></details>')
    inner = f'      <div class="o-faq">{NL}' + NL.join(items) + f'{NL}      </div>{NL}'
    return f'  <!-- FAQ -->{NL}' + section('faq', c['faq_h2'], inner, wide=False)


def final(lang, slug, c):
    t = L[lang]
    o = t['other']
    series = '' if slug == 'nano-banana' else f'        <li><a class="o-pill" href="/{lang}/models/nano-banana">{t["series_all"]}</a></li>{NL}'
    return f'''  <!-- 结尾 CTA -->
  <section class="o-final" aria-labelledby="final-title">
    <div class="o-wrap">
      {logo(44, 'nb-final-logo')}
      <h2 id="final-title">{c['final_h2']}</h2>
      <p>{c['final_p']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{t['signup_any']}</a>
        <a class="o-btn o-btn-light" href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{t['read_docs']}</a>
      </div>
      <ul class="o-related" aria-label="{t['more']}">
        <li><a class="o-pill" href="/{lang}/models/">{t['all_hub']}</a></li>
{series}        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['in_other']}</a></li>
      </ul>
    </div>
  </section>
</main>

'''


def footer(lang, slug, docs_url):
    t = L[lang]
    o = t['other']
    a, b, cc = t['foot']
    k = t['foot_links']
    return f'''<footer class="o-foot">
  <div class="o-wrap">
    <div class="o-foot-top">
      <div class="o-foot-brand">
        <a class="o-brand" href="/">AnyAIGC</a>
        <p>{t['foot_desc']}</p>
      </div>
      <div class="o-foot-cols">
        <div class="o-foot-col">
          <h2>{a}</h2>
          <ul>
            <li><a href="/{lang}/models/">{k[0]}</a></li>
            <li><a href="{PRICING}">{k[1]}</a></li>
            <li><a href="https://anyaigc.ai/console">{k[2]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{b}</h2>
          <ul>
            <li><a href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{k[3]}</a></li>
            <li><a href="{docs_url}" target="_blank" rel="noopener">{k[4]}</a></li>
            <li><a href="{SUPPORT}">{k[5]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{cc}</h2>
          <ul>
            <li><a href="/privacy">{k[6]}</a></li>
            <li><a href="/terms">{k[7]}</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="o-foot-bottom">
      <p>{logo(16)}<span>{t['legal']}</span></p>
      <a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_name']}</a>
    </div>
  </div>
</footer>

<script src="/assets/models/nano-banana.js?v={VER}" defer></script>
</body>
</html>
'''
