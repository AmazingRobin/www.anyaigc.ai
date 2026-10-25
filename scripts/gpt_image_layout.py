# GPT Image 系列专题页的 HTML 版块拼装（与语言无关，文案由 gpt_image_copy_zh/en.py 提供）。
import html
import json
import re

from gpt_image_data import (cny, DATE, VER, SITE, REG, PRICING, SUPPORT, IMG, MODELS, SLUGS, TOKEN, OFFICIAL, CALL, CALL_4K,
                            TOKENS_25, OFFICIAL_IMG_2, OFFICIAL_POST, money, cost_25, cost_2, save)

NL = '\n'

L = {
    'zh': dict(lang='zh-CN', og='zh_CN', og_alt='en_US', other='en', other_name='English', home='首页', hub='模型专题',
               series='GPT Image', market='模型广场', price='价格', ent='企业接入', docs='API 文档', login='登录',
               signup='免费注册', get_key='获取 API Key', see_price='查看价格', view_market='在模型广场查看',
               skip='跳到主要内容', nav='主导航', crumbs='面包屑', facts='核心信息', copy='复制', copied='已复制',
               code='代码示例', sales='联系企业客服', trial='先注册试用', signup_any='免费注册 AnyAIGC', read_docs='阅读 API 文档',
               all_hub='全部模型专题', more='更多', series_all='GPT Image 全系总览', in_other='GPT Image API in English',
               official='OpenAI 官方', item='计费项', saving='节省', per_m='每 100 万 tokens', per_img='/ 张',
               credit='示例图来自 OpenAI《ChatGPT 图像 2.0 现已上线》发布页，由 ChatGPT 图像 2.0 生成，版权归 OpenAI 所有。',
               credit_link='查看原文', home_label='AnyAIGC 首页',
               foot_desc='国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。',
               foot=('产品', '资源', '条款'), foot_links=('模型专题', '模型广场', '控制台', 'API 文档 ↗', '图像生成文档 ↗', '联系我们', '隐私政策', '服务条款'),
               legal='&copy; 2026 AnyAIGC。OpenAI、GPT、ChatGPT 是 OpenAI 的商标。AnyAIGC 是独立的 API 服务商，与 OpenAI 无隶属或合作关系。页面示例图片来自 OpenAI 发布页，版权归 OpenAI 所有；官方价格与参数引自 OpenAI 公开资料。',
               ent_cards=[('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。'),
                          ('对公转账', '公司账户直接付款', '支持企业对公转账充值，无需个人垫付，账目清晰。'),
                          ('签订合同', '满足采购与法务流程', '可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。'),
                          ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。')],
               ent_lead='设计团队、电商公司和内容平台可以直接走企业流程采购，财务、法务和技术对接都有对应支持。'),
    'en': dict(lang='en', og='en_US', og_alt='zh_CN', other='zh', other_name='中文', home='Home', hub='Model guides',
               series='GPT Image', market='Model catalog', price='Pricing', ent='Enterprise', docs='API docs', login='Log in',
               signup='Sign up free', get_key='Get an API key', see_price='See pricing', view_market='View in the model catalog',
               skip='Skip to main content', nav='Main', crumbs='Breadcrumb', facts='Key facts', copy='Copy', copied='Copied',
               code='Code examples', sales='Talk to sales', trial='Start with a free account', signup_any='Sign up for AnyAIGC',
               read_docs='Read the API docs', all_hub='All model guides', more='More', series_all='GPT Image overview',
               in_other='GPT Image API 中文版', official='OpenAI list', item='Item', saving='You save', per_m='per 1M tokens',
               per_img='/ image',
               credit='Sample images are from OpenAI\'s "Introducing ChatGPT Images 2.0" post, generated with ChatGPT Images 2.0. Images © OpenAI.',
               credit_link='Read the post', home_label='AnyAIGC home',
               foot_desc='An API gateway for global AI models. One base URL and one API key for 300+ models.',
               foot=('Product', 'Resources', 'Legal'), foot_links=('Model guides', 'Model catalog', 'Console', 'API docs ↗', 'Image API docs ↗', 'Contact us', 'Privacy Policy', 'Terms of Service'),
               legal='&copy; 2026 AnyAIGC. OpenAI, GPT and ChatGPT are trademarks of OpenAI. AnyAIGC is an independent API provider and is not affiliated with OpenAI. Sample images on this page come from OpenAI\'s announcement and are © OpenAI. Official prices and specs are quoted from OpenAI\'s public documentation.',
               ent_cards=[('Invoices', 'Including China VAT invoices', 'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.'),
                          ('Bank transfer', 'Pay from a company account', 'Top up by corporate bank transfer, so nobody has to pay on a personal card and expense it.'),
                          ('Contracts', 'Fits procurement and legal review', 'Sign a service agreement with AnyAIGC to meet your internal purchasing requirements.'),
                          ('Dedicated support', 'Account and technical contacts', 'Work with a dedicated support contact and technical engineer for onboarding, migration and troubleshooting.')],
               ent_lead='Design teams, e-commerce companies and content platforms can buy through a standard business process, with support for finance, legal and engineering.'),
}

LOGO_D = None  # 运行时从 assets/icons/openai.svg 读取


def logo(cls='', size=None):
    s = f' width="{size}" height="{size}"' if size else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<svg{c} viewBox="0 0 24 24"{s} aria-hidden="true" focusable="false"><path fill="#000000" fill-rule="evenodd" d="{LOGO_D}"></path></svg>')


def logo_white(size=24):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true" focusable="false"><path fill="#ffffff" fill-rule="evenodd" d="{LOGO_D}"></path></svg>')


def url(lang, slug):
    return f'{SITE}/{lang}/models/{slug}'


def text(h):
    """HTML 转纯文本（JSON-LD 用）"""
    t = re.sub(r'<[^>]+>', '', h)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


def shapes():
    return '<span class="gi-shapes" aria-hidden="true"><i></i><i></i><i></i></span>'


def img(name, lang, cls='', eager=False, sizes=None):
    w, h, zt, zd, et, ed = IMG[name]
    alt = f'{zt}：{zd}（ChatGPT 图像 2.0 生成）' if lang == 'zh' else f'{et}: {ed} (generated with ChatGPT Images 2.0)'
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    sz = f' sizes="{sizes}"' if sizes else ''
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="/assets/models/gpt-image/{name}.webp" width="{w}" height="{h}" alt="{html.escape(alt, quote=True)}"{load} decoding="async"{sz}>'


# ---------------- 代码高亮（极简：字符串 / 注释 / 关键字） ----------------
KW = r'\b(import|from|with|as|for|in|if|True|False|None|print)\b'


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
    if slug != 'gpt-image':
        crumbs.append(('GPT Image', url(lang, 'gpt-image')))
    crumbs.append((c['crumb'], me))
    offers = c['offers']
    cur = c.get('currency', 'USD')
    prices = [float(p) for _, p in offers]
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
    assert prices
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    e = lambda s: html.escape(s, quote=True)
    return f'''<!DOCTYPE html>
<html lang="{t['lang']}" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(c['title'])}</title>
<meta name="description" content="{e(c['desc'])}">
<meta name="keywords" content="{e(c['keywords'])}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#ffffff">
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
<link rel="stylesheet" href="/assets/models/gpt-image.css?v={VER}">
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
        <li class="gi-hide-md"><a class="o-pill" href="/{lang}/models/gpt-image">GPT Image</a></li>
        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="#pricing">{t['price']}</a></li>
        <li><a class="o-pill" href="#enterprise">{t['ent']}</a></li>
        <li class="gi-hide-md"><a class="o-pill" href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{t['docs']}</a></li>
      </ul>
    </nav>
    <ul class="o-nav-right">
      <li><a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_name']}</a></li>
      <li class="gi-hide-sm"><a class="o-pill" href="https://anyaigc.ai/console">{t['login']}</a></li>
      <li><a class="o-pill gi-nav-cta" href="{REG}">{t['signup']}</a></li>
    </ul>
  </div>
</header>

<main id="main">
'''


def hero(lang, slug, c):
    t = L[lang]
    crumbs = [f'<li><a href="/">{t["home"]}</a></li>', f'<li><a href="/{lang}/models/">{t["hub"]}</a></li>']
    if slug != 'gpt-image':
        crumbs.append(f'<li><a href="/{lang}/models/gpt-image">GPT Image</a></li>')
    crumbs.append(f'<li aria-current="page">{c["crumb"]}</li>')
    facts = ''.join(f'<li>{k} <strong>{v}</strong></li>' for k, v in c['facts'])
    notice = f'      <p class="o-notice" role="note">{c["notice"]}</p>{NL}' if c.get('notice') else ''
    a, b, d = c['hero_imgs']
    return f'''  <!-- Hero -->
  <section class="gi-hero" aria-labelledby="hero-title">
    <div class="o-wrap gi-hero-grid">
      <div>
        <nav aria-label="{t['crumbs']}">
          <ol class="o-crumbs">
            {''.join(crumbs)}
          </ol>
        </nav>
        <p class="gi-eyebrow">{logo()}<span>{c['eyebrow']}</span>{shapes()}</p>
        <h1 class="gi-h1" id="hero-title">{c['h1']}</h1>
        <p class="gi-lead">{c['lead']}</p>
        <p class="gi-lead-sub">{c['lead_sub']}</p>
        <div class="o-cta">
          <a class="o-btn o-btn-dark" href="{REG}">{t['get_key']}</a>
          <a class="o-btn o-btn-light" href="#pricing">{t['see_price']}</a>
        </div>
{notice}        <ul class="o-facts" aria-label="{t['facts']}">{facts}</ul>
      </div>
      <div>
        <div class="gi-collage">
          <figure class="gi-tall">{img(a, lang, eager=True, sizes="(max-width: 900px) 50vw, 300px")}</figure>
          <figure>{img(b, lang, eager=True, sizes="(max-width: 900px) 50vw, 300px")}</figure>
          <figure>{img(d, lang, sizes="(max-width: 900px) 50vw, 300px")}</figure>
        </div>
        <p class="gi-credit">{t['credit']} <a href="{OFFICIAL_POST[lang]}" target="_blank" rel="noopener">{t['credit_link']} ↗</a></p>
      </div>
    </div>
  </section>

'''


def section(sid, h2, inner, lead='', band=False, wide=True):
    cls = 'o-section gi-band' if band else 'o-section'
    wrap = 'o-wrap gi-wide' if wide else 'o-wrap o-col'
    lead_html = f'      <p class="o-lead o-reveal">{lead}</p>{NL}' if lead else ''
    return (f'  <section class="{cls}" id="{sid}" aria-labelledby="{sid}-title">{NL}    <div class="{wrap}">{NL}'
            f'      <h2 class="o-h2 o-reveal" id="{sid}-title">{h2}</h2>{NL}{lead_html}{inner}    </div>{NL}  </section>{NL}{NL}')


def about(c):
    ps = ''.join(f'        <p class="o-reveal">{p}</p>{NL}' for p in c['about_ps'])
    spec = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in c['spec'])
    inner = f'      <div class="gi-prose">{NL}{ps}      </div>{NL}      <dl class="gi-spec o-reveal">{spec}</dl>{NL}'
    return section('about', c['about_h2'], inner)


def gallery(lang, c):
    t = L[lang]
    figs = []
    for n in c['gallery']:
        w, h, zt, zd, et, ed = IMG[n]
        tt, dd = (zt, zd) if lang == 'zh' else (et, ed)
        figs.append(f'        <figure>{img(n, lang, sizes="(max-width: 640px) 50vw, 340px")}<figcaption><b>{tt}</b>{dd}</figcaption></figure>')
    inner = (f'      <div class="gi-gallery">{NL}' + NL.join(figs) + f'{NL}      </div>{NL}'
             f'      <p class="gi-credit">{t["credit"]} <a href="{OFFICIAL_POST[lang]}" target="_blank" rel="noopener">{t["credit_link"]} ↗</a></p>{NL}')
    return section('gallery', c['gallery_h2'], inner, c['gallery_lead'], band=True)


def uses(lang, c):
    lis = ''.join(f'        <li class="o-reveal"><figure>{img(n, lang, sizes="(max-width: 640px) 100vw, 500px")}</figure><span class="gi-k">{k}</span><h3>{h}</h3><p>{p}</p></li>{NL}'
                  for k, h, p, n in c['uses'])
    return section('use-cases', c['uses_h2'], f'      <ul class="gi-uses">{NL}{lis}      </ul>{NL}', c.get('uses_lead', ''))


def caps(c):
    lis = ''.join(f'        <li class="o-reveal"><h3>{h}</h3><p>{p}</p></li>{NL}' for h, p in c['caps'])
    return section('features', c['caps_h2'], f'      <ul class="gi-caps">{NL}{lis}      </ul>{NL}', c.get('caps_lead', ''))


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
             f'      <p class="gi-callout o-reveal">{c["callout"]}</p>{NL}      <p class="o-note">{c["qs_note"]}</p>{NL}')
    return section('quickstart', c['qs_h2'], inner, band=True)


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
             f'      <h3 class="gi-h3 o-reveal">{c["costs_h3"]}</h3>{NL}      <p class="o-note">{c["costs_lead"]}</p>{NL}'
             f'      <ul class="o-costs">{NL}{costs}      </ul>{NL}'
             f'      <div class="o-price-cta o-reveal">{NL}        <a class="o-btn o-btn-dark" href="{REG}">{t["get_key"]}</a>{NL}'
             f'        <a class="o-btn o-btn-light" href="{PRICING}">{t["view_market"]}</a>{NL}      </div>{NL}')
    return section('pricing', c['price_h2'], inner, c['price_lead'])


def table(caption, head_cells, groups):
    """groups: [(组标题或 None, [行 html])]；head_cells: [(文字, 是否数字列)]"""
    th = ''.join(f'<th scope="col"{" class=\"o-num\"" if num else ""}>{h}</th>' for h, num in head_cells)
    body = ''
    for title, rows in groups:
        cls = ' class="gi-group"' if title else ''
        body += f'          <tbody{cls}>{NL}'
        if title:
            body += f'            <tr><th scope="rowgroup" colspan="{len(head_cells)}">{title}</th></tr>{NL}'
        body += ''.join(f'            <tr>{r}</tr>{NL}' for r in rows)
        body += f'          </tbody>{NL}'
    return (f'      <div class="o-table-wrap o-reveal">{NL}        <table class="o-table">{NL}'
            f'          <caption class="o-sr">{caption}</caption>{NL}          <thead><tr>{th}</tr></thead>{NL}{body}'
            f'        </table>{NL}      </div>{NL}')


def token_rows(lang, base):
    """按 token 计费的单价行"""
    z = lang == 'zh'
    names = [('text_in', '文本输入' if z else 'Text input', '提示词' if z else 'Prompt text'),
             ('img_in', '图片输入' if z else 'Image input', '编辑时上传的参考图' if z else 'Reference images for edits'),
             ('out', '图片输出' if z else 'Image output', '生成的图片' if z else 'Generated images'),
             ('text_cache', '文本缓存输入' if z else 'Cached text input', '上游返回缓存用量时' if z else 'When upstream reports cache usage'),
             ('img_cache', '图片缓存输入' if z else 'Cached image input', '上游返回缓存用量时' if z else 'When upstream reports cache usage')]
    rows = []
    for k, n, sub in names:
        a, o = TOKEN[base][k], OFFICIAL[k]
        rows.append(f'<th scope="row">{n}<small>{sub}</small></th><td class="o-num o-hl">${a}</td><td class="o-num o-strike">${o}</td><td class="o-num o-save">{save(a, o)}%</td>')
    return rows


def per_image_25(lang):
    z = lang == 'zh'
    sizes = ['1024x1024', '1536x1024', '2048x2048', '3840x2160']
    rows = []
    for q in ['low', 'medium', 'high', 'xhigh', 'max']:
        cells = ''
        for s in sizes:
            a, o = cost_25(q, s)
            cells += f'<td class="o-num"><span class="o-hl">{money(a)}</span><small>{"官方" if z else "List"} {money(o)}</small></td>'
        rows.append(f'<th scope="row"><code>{q}</code></th>{cells}')
    head = [('质量' if z else 'Quality', False)] + [(s.replace('x', '×'), True) for s in sizes]
    cap = 'GPT Image 2.5 每张图片输出费用估算（美元），按 OpenAI 官方计算器的输出 tokens' if z else 'Estimated image output cost per image for GPT Image 2.5 (USD), using output tokens from OpenAI\'s calculator'
    return table(cap, head, [(None, rows)])


def per_image_2(lang):
    z = lang == 'zh'
    sizes = ['1024x1024', '1024x1536', '1536x1024']
    rows = []
    for q in ['low', 'medium', 'high']:
        cells = ''
        for s in sizes:
            a, o = cost_2(q, s)
            cells += f'<td class="o-num"><span class="o-hl">{money(a)}</span><small>{"官方" if z else "List"} ${OFFICIAL_IMG_2[q][s]}</small></td>'
        rows.append(f'<th scope="row"><code>{q}</code></th>{cells}')
    head = [('质量' if z else 'Quality', False)] + [(s.replace('x', '×'), True) for s in sizes]
    cap = 'GPT Image 2 每张图片输出费用估算（美元），按 OpenAI 官方单张价格折算' if z else 'Estimated image output cost per image for GPT Image 2 (USD), scaled from OpenAI\'s per-image list prices'
    return table(cap, head, [(None, rows)])


def call_vs(lang, base):
    """按次版与按 token 版、官方价的单张对比（1024×1024）"""
    z = lang == 'zh'
    fixed = float(CALL[base])
    qs = ['low', 'medium', 'high', 'xhigh', 'max'] if base == '2.5' else ['low', 'medium', 'high']
    rows = []
    for q in qs:
        a, o = (cost_25(q, '1024x1024') if base == '2.5' else cost_2(q, '1024x1024'))
        better = ('按张版更省' if z else 'Per-image is cheaper') if fixed < a else ('按 token 版更省' if z else 'Token-billed is cheaper')
        rows.append(f'<th scope="row"><code>{q}</code></th><td class="o-num o-hl">{cny(base) if z else '$' + CALL[base]}</td><td class="o-num">{money(a)}</td><td class="o-num o-strike">{money(o)}</td><td>{better}</td>')
    head = [('质量' if z else 'Quality', False), ('按张版（1K）' if z else 'Per image (1K)', True),
            ('按 token 版' if z else 'Token-billed', True), ('OpenAI 官方' if z else 'OpenAI list', True), ('对比' if z else 'Verdict', False)]
    cap = ('1024×1024 单张图片费用对比' if z else 'Cost per 1024×1024 image (USD)')
    return table(cap, head, [(None, rows)])


def call_block(lang, slugs):
    """价格版块里的「按张计费版」小节：说明平台上的 -c 模型、价格、限制，并与按 token 版对比。
    slugs：本页对应的 -c 模型 ID（2.5 Sunburst / Flare 页各一个，GPT Image 2 页一个）"""
    z = lang == 'zh'
    base = MODELS[slugs[0]]['base']
    p1 = cny(base) if z else '$' + CALL[base]
    p4 = cny(base, '4k') if z else '$' + CALL_4K[base]
    ids = '、'.join(f'<code>{s}</code>' for s in slugs) if z else ', '.join(f'<code>{s}</code>' for s in slugs)
    unit = '张' if z else 'image'
    price = table('按张计费版价格' if z else 'Per-image pricing',
                  [('模型' if z else 'Model', False), ('1K 出图' if z else '1K output', True), ('2K / 4K 出图' if z else '2K / 4K output', True)],
                  [(None, [f'<th scope="row"><code>{s}</code></th><td class="o-num o-hl">{p1} / {unit}</td><td class="o-num o-hl">{p4} / {unit}</td>' for s in slugs])])
    if z:
        head = (f'      <h3 class="gi-h3 o-reveal" id="per-image">按张计费：{ids}</h3>{NL}'
                f'      <p class="o-note">AnyAIGC 平台还提供按张计费的版本，接口和调用方式相同，只把 <code>model</code> 换成带 <code>-c</code> 的 ID。'
                f'每张固定价，质量档位不影响单价：1K 出图（如 1024×1024、1536×1024、1024×1536）每张 {p1}，2K、4K 出图每张 {p4}。'
                f'每次请求出 1 张，不支持 <code>n</code>、<code>mask</code> 参数，也不支持透明背景。</p>{NL}')
        vs = (f'      <p class="o-note">和按 token 计费比：以 1024×1024 为例，按张版为人民币价格，按 token 版和 OpenAI 官方为美元价格，只算图片输出 tokens。</p>{NL}')
    else:
        head = (f'      <h3 class="gi-h3 o-reveal" id="per-image">Per-image billing: {ids}</h3>{NL}'
                f'      <p class="o-note">AnyAIGC also offers a per-image version with the same endpoints. Just switch <code>model</code> to the <code>-c</code> ID. '
                f'Each image has a flat price at any quality level: {p1} per image for 1K output (such as 1024×1024, 1536×1024 or 1024×1536) and {p4} per image for 2K and 4K output. '
                f'Each request returns one image, and <code>n</code>, <code>mask</code> and transparent backgrounds are not supported.</p>{NL}')
        vs = f'      <p class="o-note">Compared with token billing at 1024×1024, counting image output tokens only.</p>{NL}'
    return head + price + vs + call_vs(lang, base)


def enterprise(lang, name):
    t = L[lang]
    h2 = f'企业接入 {name} API' if lang == 'zh' else f'{name} API for teams and enterprises'
    cards = ''.join(f'        <li class="o-card o-reveal"><strong>{a}</strong><h3>{b}</h3><p>{d}</p></li>{NL}' for a, b, d in t['ent_cards'])
    inner = (f'      <ul class="o-cards">{NL}{cards}      </ul>{NL}'
             f'      <div class="o-price-cta o-reveal">{NL}        <a class="o-btn o-btn-dark" href="{SUPPORT}">{t["sales"]}</a>{NL}'
             f'        <a class="o-btn o-btn-light" href="{REG}">{t["trial"]}</a>{NL}      </div>{NL}')
    return section('enterprise', h2, inner, t['ent_lead'], wide=False).replace('id="enterprise-title"', 'id="ent-title"').replace('aria-labelledby="enterprise-title"', 'aria-labelledby="ent-title"')


def family(lang, slug, items, h2, lead):
    lis = []
    for s, tag, title, sub in items:
        cur = ' aria-current="page"' if s == slug else ''
        tg = f'<span class="o-tag">{tag}</span>' if tag else ''
        lis.append(f'        <li><a href="/{lang}/models/{s}"{cur}>{tg}<b>{title}</b><span>{sub}</span></a></li>')
    inner = f'      <ul class="o-family o-reveal">{NL}' + NL.join(lis) + f'{NL}      </ul>{NL}'
    return (f'  <!-- FAMILY -->{NL}' + section('family', h2, inner, lead, wide=False))


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
    other = c.get('final_other', t['in_other'])
    series = '' if slug == 'gpt-image' else f'        <li><a class="o-pill" href="/{lang}/models/gpt-image">{t["series_all"]}</a></li>{NL}'
    return f'''  <!-- 结尾 CTA -->
  <section class="o-final" aria-labelledby="final-title">
    <div class="o-wrap">
      {shapes()}
      <h2 id="final-title">{c['final_h2']}</h2>
      <p>{c['final_p']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{t['signup_any']}</a>
        <a class="o-btn o-btn-light" href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{t['read_docs']}</a>
      </div>
      <ul class="o-related" aria-label="{t['more']}">
        <li><a class="o-pill" href="/{lang}/models/">{t['all_hub']}</a></li>
{series}        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{other}</a></li>
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
      <p>{logo()}<span>{t['legal']}</span></p>
      <a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_name']}</a>
    </div>
  </div>
</footer>

<script src="/assets/models/gpt-image.js?v={VER}" defer></script>
</body>
</html>
'''
