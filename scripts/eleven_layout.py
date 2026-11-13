# ElevenLabs（Eleven）系列专题页的 HTML 版块拼装（与语言无关，文案由 eleven_copy_zh.py / eleven_copy_en.py 提供），结构沿用 spark_layout.py。
# 视觉参考 elevenlabs.io/zh/v4：近白底 #fdfcfc、黑色胶囊按钮、细体大标题、深色 #1c1917 区块、v4 橙红 → 绿渐变艺术图（素材见 scripts/eleven_assets.py）。
import html
import io
import json
import os
import re
from decimal import Decimal

from eleven_data import DATE, VER, SITE, REG, PRICING, MARKET, SUPPORT, DOCS, PRICE, OFFICIAL, MODELS, MODEL_SLUGS
from icons import svg as icon_svg

NL = '\n'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

L = {
    'zh': dict(lang='zh-CN', og='zh_CN', og_alt='en_US', other='en', other_name='English', home='首页', hub='模型专题',
               market='模型广场', price='价格', ent='企业接入', docs='API 文档', login='登录', series='Eleven 系列',
               signup='免费注册', get_key='获取 API Key', see_price='查看价格', view_market='在模型广场查看',
               skip='跳到主要内容', nav='主导航', crumbs='面包屑', facts='核心信息', copy='复制', copied='已复制', send='查看示例回答', out_label='示例回答 · 非实时生成',
               code='代码示例', sales='联系企业客服', trial='先注册试用', signup_any='免费注册 AnyAIGC', read_docs='阅读 API 文档',
               all_hub='全部模型专题', more='更多', home_label='AnyAIGC 首页',
               category='语音合成 API',
               foot_desc='国内外 AI 模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。',
               foot=('产品', '资源', '条款'), foot_links=('模型专题', '模型广场', '控制台', 'API 文档 ↗', '联系我们', '隐私政策', '服务条款'),
               legal='&copy; 2026 AnyAIGC。Eleven、ElevenLabs 是 Eleven Labs, Inc. 的商标。AnyAIGC 是独立的 API 服务商，与 ElevenLabs 无隶属或合作关系。模型参数与官方价引自 ElevenLabs 公开文档和价格页，商用授权与音色版权以 ElevenLabs 官方条款为准。',
               ent_cards=[('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。'),
                          ('对公转账', '公司账户直接付款', '支持企业对公转账充值，无需个人垫付，账目清晰。'),
                          ('签订合同', '满足采购与法务流程', '可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。'),
                          ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。')],
               ent_lead='研发团队和公司可以直接走企业流程采购，财务、法务和技术对接都有对应支持。',
               ent_h2='企业接入 {name} API', ent_kicker='企业'),
    'en': dict(lang='en', og='en_US', og_alt='zh_CN', other='zh', other_name='中文', home='Home', hub='Model guides',
               market='Model catalog', price='Pricing', ent='Enterprise', docs='API docs', login='Log in', series='Eleven models',
               signup='Sign up free', get_key='Get an API key', see_price='See pricing', view_market='View in the model catalog',
               skip='Skip to main content', nav='Main', crumbs='Breadcrumb', facts='Key facts', copy='Copy', copied='Copied', send='Show a sample reply', out_label='Sample reply · not generated live',
               code='Code examples', sales='Talk to sales', trial='Start with a free account', signup_any='Sign up for AnyAIGC',
               read_docs='Read the API docs', all_hub='All model guides', more='More',
               home_label='AnyAIGC home', category='Text-to-speech API',
               foot_desc='An API gateway for global AI models. One base URL and one API key for 300+ models.',
               foot=('Product', 'Resources', 'Legal'), foot_links=('Model guides', 'Model catalog', 'Console', 'API docs ↗', 'Contact us', 'Privacy Policy', 'Terms of Service'),
               legal='&copy; 2026 AnyAIGC. Eleven and ElevenLabs are trademarks of Eleven Labs, Inc. AnyAIGC is an independent API provider and is not affiliated with ElevenLabs. Specifications and list prices are quoted from ElevenLabs public documentation and pricing page; commercial licensing and voice rights are governed by ElevenLabs terms.',
               ent_cards=[('Invoices', 'Including China VAT invoices', 'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.'),
                          ('Bank transfer', 'Pay from a company account', 'Top up by corporate bank transfer, so nobody has to pay on a personal card and expense it.'),
                          ('Contracts', 'Fits procurement and legal review', 'Sign a service agreement with AnyAIGC to meet your internal purchasing requirements.'),
                          ('Dedicated support', 'Account and technical contacts', 'Work with a dedicated support contact and technical engineer for onboarding, migration and troubleshooting.')],
               ent_lead='Engineering teams and companies can buy through a standard business process, with support for finance, legal and engineering.',
               ent_h2='{name} API for teams and enterprises', ent_kicker='Enterprise'),
}

# ---------------- ElevenLabs logo（lobe-icons elevenlabs，单色；见 scripts/icons.py） ----------------
def logo(cls='el-mark', size=None, fill=None):
    return icon_svg('elevenlabs', cls=cls, size=size, fill=fill or '#0c0a09', evenodd=False)


# v4 / v4 Turbo 用官网 v4 橙红渐变图，其余型号用 API 页灰色流线图
HERO_IMG = {x: ('hero-v4.webp' if x in ('eleven-v4', 'eleven-v4-turbo') else 'hero-mono.webp') for x in MODEL_SLUGS}


def url(lang, slug):
    return f'{SITE}/{lang}/models/{slug}'


def text(h):
    """HTML 转纯文本（JSON-LD 用）"""
    t = re.sub(r'<[^>]+>', '', h)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


# ---------------- 代码高亮（极简：字符串 / 注释 / 关键字） ----------------
KW = r'\b(import|from|with|as|for|in|if|not|and|or|break|True|False|None|print|def|return|getattr)\b'


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


def money(d):
    """成本示例金额（Decimal，精确，不四舍五入）"""
    return '$' + fmt(d)


def cost(slug, chars, official=False):
    """按字符数计算成本（美元，Decimal）"""
    base = Decimal(OFFICIAL[slug] if official else PRICE[slug])
    return base * Decimal(chars) / Decimal(10000)


# ---------------- head ----------------
def head(lang, slug, c):
    me, zh, en = url(lang, slug), url('zh', slug), url('en', slug)
    og_img = f'{SITE}/assets/og/{slug}-{lang}.png'
    t = L[lang]
    crumbs = [(t['home'], f'{SITE}/'), (t['hub'], f'{SITE}/{lang}/models/')]
    crumbs.append((c['crumb'], me))
    offers = c['offers']
    graph = [
        {'@type': 'Organization', '@id': f'{SITE}/#org', 'name': 'AnyAIGC', 'url': 'https://anyaigc.ai', 'logo': f'{SITE}/logo.webp'},
        {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'AnyAIGC', 'publisher': {'@id': f'{SITE}/#org'}},
        {'@type': 'WebPage', '@id': f'{me}#webpage', 'url': me, 'name': c['title'], 'description': c['desc'], 'inLanguage': t['lang'],
         'isPartOf': {'@id': f'{SITE}/#website'}, 'breadcrumb': {'@id': f'{me}#breadcrumb'}, 'mainEntity': {'@id': f'{me}#product'},
         'dateModified': DATE},
        {'@type': 'BreadcrumbList', '@id': f'{me}#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]},
        {'@type': 'Product', '@id': f'{me}#product', 'name': c['product'], 'description': c['product_desc'],
         'category': t['category'], 'sku': c['sku'], 'image': og_img,
         'brand': {'@type': 'Brand', 'name': 'AnyAIGC'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'USD', 'lowPrice': min(offers, key=lambda o: float(o[1]))[1],
                    'highPrice': max(offers, key=lambda o: float(o[1]))[1], 'offerCount': len(offers),
                    'availability': 'https://schema.org/InStock', 'url': f'{me}#pricing',
                    'offers': [{'@type': 'Offer', 'name': n, 'price': p, 'priceCurrency': 'USD'} for n, p in offers]}},
        {'@type': 'FAQPage', '@id': f'{me}#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}} for q, a in c['faqs']]},
    ]
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    e = lambda s: html.escape(s, quote=True)
    hero_img = HERO_IMG[slug]
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
<link rel="preload" as="image" href="/assets/models/eleven/{hero_img}" media="(min-width:641px)">
<link rel="stylesheet" href="/assets/models/eleven.css?v={VER}">
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
        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="#pricing">{t['price']}</a></li>
        <li><a class="o-pill" href="#enterprise">{t['ent']}</a></li>
        <li class="el-hide-md"><a class="o-pill" href="{DOCS}" target="_blank" rel="noopener">{t['docs']}</a></li>
      </ul>
    </nav>
    <ul class="o-nav-right">
      <li><a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_name']}</a></li>
      <li><a class="o-pill el-nav-login" href="https://anyaigc.ai/console">{t['login']}</a></li>
      <li><a class="o-pill el-nav-cta" href="{REG}">{t['signup']}</a></li>
    </ul>
  </div>
</header>

<main id="main">
'''


def hero(lang, slug, c):
    t = L[lang]
    h = c['hero']
    facts = ''.join(f'          <li>{k} <strong>{v}</strong></li>{NL}' for k, v in h['facts'])
    notice = f'      <p class="o-notice">{h["notice"]}</p>{NL}' if h.get('notice') else ''
    mono = ' el-hero-mono' if HERO_IMG[slug] == 'hero-mono.webp' else ''
    player = ''
    if h.get('sample'):
        sm = h['sample']
        bars = ''.join(f'<i style="--h:{x}"></i>' for x in (30, 52, 38, 70, 46, 88, 58, 34, 76, 50, 92, 64, 40, 82, 54, 36, 68, 44, 78, 56, 32, 62, 48, 72))
        player = f'''      <div class="el-player" data-src="/assets/models/eleven/v4-sample.mp3" data-play="{sm['play']}" data-pause="{sm['pause']}">
        <button type="button" class="el-play" aria-label="{sm['play']}" aria-pressed="false"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path class="el-ic-play" d="M8 5.5v13l11-6.5z" fill="#ffffff"/><path class="el-ic-pause" d="M7 5h4v14H7zM13 5h4v14h-4z" fill="#ffffff"/></svg></button>
        <div class="el-player-body">
          <p class="el-player-title">{sm['title']}</p>
          <div class="el-wave" aria-hidden="true">{bars}</div>
          <p class="el-player-line">{sm['line']}</p>
        </div>
      </div>
'''
    return f'''  <!-- 首屏 -->
  <section class="el-hero{mono}" aria-labelledby="hero-title">
    <div class="o-wrap el-hero-inner">
      <nav aria-label="{t['crumbs']}">
        <ol class="o-crumbs">
          <li><a href="/">{t['home']}</a></li>
          <li><a href="/{lang}/models/">{t['hub']}</a></li>
          <li aria-current="page">{c['crumb']}</li>
        </ol>
      </nav>
      <p class="el-eyebrow">{logo(cls='el-mark', size=16)}<span>{h['eyebrow']}</span><b class="el-deal">{h['deal']}</b></p>
      <h1 class="el-h1 el-rise" id="hero-title">{h['h1']}</h1>
      <p class="el-lead el-rise">{h['lead']}</p>
{player}      <p class="el-lead-sub">{h['sub']}</p>
{notice}
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{t['get_key']}</a>
        <a class="o-btn o-btn-light" href="#pricing">{t['see_price']}<span class="el-arrow" aria-hidden="true">→</span></a>
      </div>
      <ul class="o-facts" aria-label="{t['facts']}">
{facts}      </ul>
    </div>
  </section>

'''


def head2(kicker, h2, sid, lead=None):
    out = f'      <span class="el-kicker o-reveal">{kicker}</span>{NL}      <h2 class="o-h2 o-reveal" id="{sid}">{h2}</h2>{NL}'
    if lead:
        out += f'      <p class="o-lead o-reveal">{lead}</p>{NL}'
    return out


def about(c):
    a = c['about']
    paras = ''.join(f'        <p class="o-reveal">{p}</p>{NL}' for p in a['paras'])
    spec = ''.join(f'        <div><dt>{dt}</dt><dd>{dd}' + (f'<small>{sm}</small>' if sm else '') + f'</dd></div>{NL}' for dt, dd, sm in a['spec'])
    return f'''  <!-- 模型介绍 -->
  <section class="o-section" id="about" aria-labelledby="about-title">
    <div class="o-wrap el-wide">
{head2(a['kicker'], a['h2'], 'about-title')}      <div class="el-prose">
{paras}      </div>
      <dl class="el-spec o-reveal">
{spec}      </dl>
    </div>
  </section>

'''


def features(c):
    f = c['features']
    items = ''.join(f'        <li class="o-reveal"><span class="el-num">{i + 1:02d}</span><h3>{h}</h3><p>{p}</p></li>{NL}' for i, (h, p) in enumerate(f['items']))
    sid = f.get('id', 'features')
    return f'''  <!-- 能力 -->
  <section class="o-section" id="{sid}" aria-labelledby="{sid}-title">
    <div class="o-wrap el-wide">
{head2(f['kicker'], f['h2'], sid + '-title', f.get('lead'))}      <ul class="el-caps">
{items}      </ul>
    </div>
  </section>

'''


def fmt(d):
    """精确格式化美元金额：不四舍五入，至少保留 2 位小数，去掉多余的 0"""
    q = d.quantize(Decimal('0.01'))
    if d == q:
        return f'{q:f}'
    return f'{d.normalize():f}'


def unit_price(slug, mult, official=False):
    """mult 是相对「每万字符」的倍数。AnyAIGC 的每万字符价原样显示模型广场的 4 位小数（如 0.6480），其余档位由它换算"""
    if mult == 1 and not official:
        return PRICE[slug]
    base = Decimal(OFFICIAL[slug] if official else PRICE[slug])
    return fmt(base * Decimal(mult))


def price_rows(slug, labels):
    """每行一个计费单位：单位 | 模型 ID | 官方价（删除线） | AnyAIGC 价。mult 是相对「每万字符」的倍数"""
    rows = ''
    for lab, small, mult, hl in labels:
        cls = ' class="el-row-main"' if hl else ''
        rows += (f'            <tr{cls}><th scope="row">{lab}<small>{small}</small></th><td><code>{MODELS[slug]["id"]}</code></td>'
                 f'<td class="o-num o-strike">${unit_price(slug, mult, True)}</td>'
                 f'<td class="o-num o-hl">${unit_price(slug, mult)}</td></tr>{NL}')
    return rows


def pricing(lang, slug, c):
    t = L[lang]
    p = c['pricing']
    billing = ''.join(f'        <li><strong>{s}</strong>{x}</li>{NL}' for s, x in p['billing'])
    th = ''.join(f'<th scope="col"{" class=" + chr(34) + cls + chr(34) if cls else ""}>{h}</th>' for h, cls in p['head'])
    body = f'          <tbody>{NL}' + price_rows(slug, p['labels']) + f'          </tbody>{NL}'
    costs = ''.join(f'''        <li class="o-cost o-reveal">
          <h4>{h}</h4>
          <p class="o-cost-calc">{calc}</p>
          <p class="o-cost-total">{tot}</p>
          <p class="o-cost-off">{off}</p>
        </li>{NL}''' for h, calc, tot, off in p['costs'])
    return f'''  <!-- 价格 -->
  <section class="o-section el-band" id="pricing" aria-labelledby="pricing-title">
    <div class="o-wrap el-wide">
{head2(p['kicker'], p['h2'], 'pricing-title', p['lead'])}      <ul class="o-billing o-reveal" aria-label="{p['billing_label']}">
{billing}      </ul>

      <div class="o-table-wrap o-reveal">
        <table class="o-table">
          <caption class="o-sr">{p['caption']}</caption>
          <thead>
            <tr>{th}</tr>
          </thead>
{body}        </table>
      </div>
      <p class="o-note">{p['note']}</p>

      <h3 class="el-h3 o-reveal">{p['costs_h3']}</h3>
      <p class="el-sub o-reveal">{p['costs_lead']}</p>
      <ul class="o-costs">
{costs}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-dark" href="{REG}">{t['get_key']}</a>
        <a class="o-btn o-btn-light" href="{MARKET}">{t['view_market']}<span class="el-arrow" aria-hidden="true">→</span></a>
      </div>
    </div>
  </section>

'''


def table(head_cells, rows, caption, current=None):
    """rows = [(label_html, small, [cell, ...], slug)]；每个单元格的 class 取表头对应列的 class，slug == current 的行整行高亮"""
    th = ''.join(f'<th scope="col"{" class=" + chr(34) + cls + chr(34) if cls else ""}>{h}</th>' for h, cls in head_cells)
    body = ''
    for lab, small, vals, sl in rows:
        cells = ''.join(f'<td{" class=" + chr(34) + head_cells[j + 1][1] + chr(34) if head_cells[j + 1][1] else ""}>{v}</td>' for j, v in enumerate(vals))
        sm = f'<small>{small}</small>' if small else ''
        cur = ' class="el-row-main"' if sl == current else ''
        body += f'            <tr{cur}><th scope="row">{lab}{sm}</th>{cells}</tr>{NL}'
    return f'''      <div class="o-table-wrap o-reveal">
        <table class="o-table">
          <caption class="o-sr">{caption}</caption>
          <thead>
            <tr>{th}</tr>
          </thead>
          <tbody>
{body}          </tbody>
        </table>
      </div>
'''


def compare(c, slug):
    b = c['compare']
    return f'''  <!-- 选型 -->
  <section class="o-section el-band" id="compare" aria-labelledby="compare-title">
    <div class="o-wrap el-wide">
{head2(b['kicker'], b['h2'], 'compare-title', b['lead'])}{table(b['head'], b['rows'], b['caption'], slug)}      <p class="o-note">{b['note']}</p>
    </div>
  </section>

'''


def uses(c):
    """使用场景：官网音色分类图做卡片顶图（图片为装饰，alt 留空），items = (图片文件名, 标签, 标题, 说明)"""
    u = c['uses']
    items = ''.join(f'''        <li class="o-reveal"><img src="/assets/models/eleven/{img}" width="520" height="650" alt="" loading="lazy" decoding="async"><div class="el-uses-b"><span class="el-k">{k}</span><h3>{h}</h3><p>{p}</p></div></li>{NL}''' for img, k, h, p in u['items'])
    return f'''  <!-- 使用场景 -->
  <section class="o-section" id="use-cases" aria-labelledby="uses-title">
    <div class="o-wrap el-wide">
{head2(u['kicker'], u['h2'], 'uses-title')}      <ul class="el-uses">
{items}      </ul>
    </div>
  </section>

'''


def quickstart(lang, c):
    t = L[lang]
    q = c['qs']
    steps = ''.join(f'        <li>{s}</li>{NL}' for s in q['steps'])
    tabs, panels = '', ''
    for i, (tid, label, cap, code) in enumerate(q['tabs']):
        sel = 'true' if i == 0 else 'false'
        tabs += f'        <li role="presentation"><button type="button" role="tab" id="tab-{tid}" aria-controls="panel-{tid}" aria-selected="{sel}">{label}</button></li>{NL}'
        panels += f'''      <figure class="o-code" id="panel-{tid}" role="tabpanel" aria-labelledby="tab-{tid}">
        <figcaption><b>{cap}</b><button class="o-copy" type="button" aria-controls="code-{tid}" data-done="{t['copied']}">{t['copy']}</button></figcaption>
<pre id="code-{tid}"><code>{hl(code)}</code></pre>
      </figure>

'''
    return f'''  <!-- 快速开始 -->
  <section class="o-section" id="quickstart" aria-labelledby="qs-title">
    <div class="o-wrap o-col">
{head2(q['kicker'], q['h2'], 'qs-title')}      <ol class="o-steps o-reveal">
{steps}      </ol>

      <ul class="o-tabs" role="tablist" aria-label="{t['code']}">
{tabs}      </ul>

{panels}      <p class="el-callout o-reveal">{q['callout']}</p>
      <p class="o-note">{q['note']}</p>
    </div>
  </section>

'''


def enterprise(lang, name):
    t = L[lang]
    cards = ''.join(f'        <li class="o-card o-reveal"><strong>{a}</strong><h3>{b}</h3><p>{d}</p></li>{NL}' for a, b, d in t['ent_cards'])
    return f'''  <!-- 企业接入 -->
  <section class="o-section" id="enterprise" aria-labelledby="ent-title">
    <div class="o-wrap o-col">
      <span class="el-kicker o-reveal">{t['ent_kicker']}</span>
      <h2 class="o-h2 o-reveal" id="ent-title">{t['ent_h2'].format(name=name)}</h2>
      <p class="o-lead o-reveal">{t['ent_lead']}</p>
      <ul class="o-cards">
{cards}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-dark" href="{SUPPORT}">{t['sales']}</a>
        <a class="o-btn o-btn-light" href="{REG}">{t['trial']}<span class="el-arrow" aria-hidden="true">→</span></a>
      </div>
    </div>
  </section>

'''


def family(lang, slug, items, h2, lead, kicker):
    lis = ''
    for s, tag, desc in items:
        cur = ' aria-current="page"' if s == slug else ''
        tg = f'<span class="o-tag">{tag}</span>' if tag else ''
        name = MODELS[s]['name'] if s in MODELS else desc[0]
        sub = desc if s in MODELS else desc[1]
        lis += f'        <li><a href="/{lang}/models/{s}"{cur}>{tg}<b>{name}</b><span>{sub}</span></a></li>{NL}'
    return f'''  <!-- FAMILY -->
  <section class="o-section" id="family" aria-labelledby="family-title">
    <div class="o-wrap o-col">
{head2(kicker, h2, 'family-title', lead)}      <ul class="o-family o-reveal">
{lis}      </ul>
    </div>
  </section>

'''


def faq(c):
    items = ''.join(f'        <details{" open" if i == 0 else ""}><summary><h3>{q}</h3></summary><div class="o-ans"><p>{a}</p></div></details>{NL}'
                    for i, (q, a) in enumerate(c['faqs']))
    return f'''  <!-- FAQ -->
  <section class="o-section" id="faq" aria-labelledby="faq-title">
    <div class="o-wrap o-col">
      <span class="el-kicker o-reveal">FAQ</span>
      <h2 class="o-h2 o-reveal" id="faq-title">{c['faq_h2']}</h2>
      <div class="o-faq">
{items}      </div>
    </div>
  </section>

'''


def final(lang, slug, c):
    t = L[lang]
    o = t['other']
    f = c['final']
    series = ''
    return f'''  <!-- 结尾 CTA -->
  <section class="o-final" aria-labelledby="final-title">
    <div class="o-wrap">
      {logo('el-mark el-final-mark')}
      <h2 id="final-title">{f['h2']}</h2>
      <p>{f['p']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{t['signup_any']}</a>
        <a class="o-btn o-btn-light" href="{DOCS}" target="_blank" rel="noopener">{t['read_docs']}<span class="el-arrow" aria-hidden="true">→</span></a>
      </div>
      <ul class="o-related" aria-label="{t['more']}">
        <li><a class="o-pill" href="/{lang}/models/">{t['all_hub']}</a></li>
{series}        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{f['other']}</a></li>
      </ul>
    </div>
  </section>
</main>

'''


def footer(lang, slug):
    t = L[lang]
    o = t['other']
    fl = t['foot_links']
    return f'''<footer class="o-foot">
  <div class="o-wrap">
    <div class="o-foot-top">
      <div class="o-foot-brand">
        <a class="o-brand" href="/">AnyAIGC</a>
        <p>{t['foot_desc']}</p>
      </div>
      <div class="o-foot-cols">
        <div class="o-foot-col">
          <h2>{t['foot'][0]}</h2>
          <ul>
            <li><a href="/{lang}/models/">{fl[0]}</a></li>
            <li><a href="{PRICING}">{fl[1]}</a></li>
            <li><a href="https://anyaigc.ai/console">{fl[2]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{t['foot'][1]}</h2>
          <ul>
            <li><a href="{DOCS}" target="_blank" rel="noopener">{fl[3]}</a></li>
            <li><a href="{SUPPORT}">{fl[4]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{t['foot'][2]}</h2>
          <ul>
            <li><a href="/privacy">{fl[5]}</a></li>
            <li><a href="/terms">{fl[6]}</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="o-foot-bottom">
      <p>{logo('el-mark el-foot-mark', fill='#ffffff')}<span>{t['legal']}</span></p>
      <a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_name']}</a>
    </div>
  </div>
</footer>

<script src="/assets/models/eleven.js?v={VER}" defer></script>
</body>
</html>
'''
