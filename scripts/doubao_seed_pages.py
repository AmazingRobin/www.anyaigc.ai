"""Build the bilingual Doubao Seed guides; emit static HTML with no build runtime.

Model-specific copy and verified catalog prices live in separate data modules.
One canonical page per model, with the latest snapshot selected by default.
Full dated IDs are retained only in API examples and structured product data.
"""
from pathlib import Path
from decimal import Decimal
import html
import json
import re
import shlex

from doubao_seed_data import MODELS as SNAPSHOT_MODELS, SLUGS as SNAPSHOT_IDS
from doubao_seed_copy import COPY as SNAPSHOT_COPY
import payments
import trust

SNAPSHOTS = {}
for snapshot in SNAPSHOT_IDS:
    SNAPSHOTS.setdefault(SNAPSHOT_MODELS[snapshot]['name'], []).append(snapshot)
for snapshots in SNAPSHOTS.values():
    snapshots.sort(key=lambda snapshot: snapshot.rsplit('-', 1)[1], reverse=True)
SLUGS = list(SNAPSHOTS)
LATEST = {slug: snapshots[0] for slug, snapshots in SNAPSHOTS.items()}
MODELS = {slug: SNAPSHOT_MODELS[snapshot] for slug, snapshot in LATEST.items()}
COPY = {slug: SNAPSHOT_COPY[snapshot] for slug, snapshot in LATEST.items()}

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing?provider=Doubao'
DOCS = 'https://docs.anyaigc.ai/reference/v1/chat/completions'
SUPPORT = 'https://anyaigc.ai/customersupport'
DATE = '2026-11-10'
VER = '20261110'
# User confirmed these 16 models have no concurrency limit on 2026-11-10.
# Dates stay in runnable code only; headings, prose and price tables omit them.
CONCURRENCY = {
    'zh_short': '并发不限', 'en_short': 'Unlimited concurrency',
    'zh_audience': '本系列模型均适用', 'en_audience': 'Available across this family',
    'zh': '本系列 Doubao Seed 模型在 AnyAIGC 均无并发限制。',
    'en': 'AnyAIGC imposes no concurrency limit on this Doubao Seed family.',
}
CODE_ID_LITERAL = True

def e(s):
    return html.escape(str(s), quote=True)

def plain(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', '', s))).strip()

def tr(lang, zh, en):
    return zh if lang == 'zh' else en

def name(slug):
    return MODELS[slug]['name']

def logo(size=22):
    raw = (ROOT / 'assets/icons/bytedance-color.svg').read_text(encoding='utf-8')
    body = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S)[1], flags=re.S)
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true" focusable="false">{body}</svg>'

def section(sid, title, content, band=False, narrow=False, lead=''):
    return f'''  <section class="o-section{' sd-band' if band else ''}" id="{sid}" aria-labelledby="{sid}-title">
    <div class="o-wrap {'o-col' if narrow else 'sd-wide'}">
      <h2 class="o-h2 o-reveal" id="{sid}-title">{e(title)}</h2>
      {f'<p class="o-lead o-reveal">{lead}</p>' if lead else ''}
{content}
    </div>
  </section>

'''

def art(kind):
    return f'<div class="db-art db-art-{kind}" aria-hidden="true"><i></i><i></i><i></i></div>'

def art_kind(title):
    if re.search(r'视觉|图片|多模态|全模态|vision|visual|image|modal', title, re.I):
        return 'vision'
    if re.search(r'编程|代码|Coding|code|development', title, re.I):
        return 'code'
    if re.search(r'Agent|任务|规划|协同|task|planning|workflow', title, re.I):
        return 'flow'
    return 'text'

def currency(value):
    return '$' + format(Decimal(value).normalize(), 'f')

def price_offers(lang, slug):
    labels = {'input': tr(lang, '输入', 'Input'), 'output': tr(lang, '输出', 'Output'),
              'cache': tr(lang, '缓存命中', 'Cache hit'), 'audio': tr(lang, '音频输入', 'Audio input')}
    offers = []
    for r in MODELS[slug]['rates']:
        for kind, label in labels.items():
            if r.get(kind) is not None:
                offers.append((r['range_' + lang] + ' · ' + label + ' / 1M tokens', r[kind]))
    if MODELS[slug].get('audio_base') is not None:
        offers.append((tr(lang, '音频输入 / 1M tokens', 'Audio input / 1M tokens'), MODELS[slug]['audio_base']))
    return offers

def metadata(lang, slug):
    n = name(slug)
    c = COPY[slug][lang]
    rate = MODELS[slug]['rates'][0]['input']
    title = tr(lang, f'{n} API 价格与接入 - AnyAIGC', f'{n} API Pricing - AnyAIGC')
    desc = tr(lang,
        f'{n} API 输入每百万 tokens ${rate} 起，{c["tagline"]}，兼容 OpenAI 接口。{CONCURRENCY["zh_short"]}，支持企业对公转账、服务合同与增值税专票，300+ 模型共用一个 Key。',
        f'{n} API from ${rate}/1M input tokens. {CONCURRENCY["en_short"]}. Chat Completions, 300+ models, VAT invoices and bank transfer.')
    return title, desc

def faqs(lang, slug):
    zh = lang == 'zh'
    n = name(slug)
    r = MODELS[slug]['rates'][0]
    c = COPY[slug][lang]
    choose = tr(lang, '本页介绍和默认代码采用模型广场当前列出的最新快照。<a href="#quickstart">快速开始</a>中保留旧版代码示例，已有项目可以按需使用。不同快照的能力可能不同，本页价格在核对时一致。', 'The overview and default examples use the newest snapshot listed in the catalog. <a href="#quickstart">Quickstart</a> also includes older code examples for existing integrations. Capabilities can differ between snapshots; the listed prices matched when verified.') if len(SNAPSHOTS[slug]) > 1 else tr(lang, '当前模型广场列出一个快照，默认代码使用该版本。可以根据本页的能力介绍、场景和价格表选型，再用实际业务输入测试效果。', 'The catalog currently lists one snapshot, used by the default examples. Evaluate its capabilities, use cases and pricing against your own inputs.')
    rows = [
        (tr(lang, f'{n} API 怎么收费？', f'How is {n} API priced?'),
         tr(lang, f'按输入与输出 token 计费，输入 ${r["input"]}、输出 ${r["output"]} / 百万 tokens 起。完整档位及适用的缓存、音频价格见本页价格表；实时价格以模型广场为准。', f'Input starts at ${r["input"]} and output at ${r["output"]} per 1M tokens. The table lists all published tiers and applicable cache and audio rates. Check the model catalog for live prices.')),
        (tr(lang, '怎么接入？一次调用返回什么？', 'How do I integrate it, and what does a call return?'),
         tr(lang, f'调用 <code>POST /v1/chat/completions</code>，请求体包含 <code>model</code> 和 <code>messages</code>。本页示例不启用流式输出，返回 JSON，在 <code>choices[0].message.content</code> 读取回复，在 <code>usage</code> 读取用量。字段见<a href="{DOCS}">接口文档</a>。', f'Call <code>POST /v1/chat/completions</code> with <code>model</code> and <code>messages</code>. These non-streaming examples return JSON: read the reply from <code>choices[0].message.content</code> and token usage from <code>usage</code>. See the <a href="{DOCS}">API reference</a>.')),
        (tr(lang, '并发有限制吗？', 'Is there a concurrency limit?'), CONCURRENCY[lang]),
        (tr(lang, '这个版本适合什么任务？', 'What work is this edition designed for?'), e(c['summary'])),
        (tr(lang, '默认使用哪个版本？可以使用旧版吗？', 'Which version is used by default? Can I use an older one?'), choose),
        (tr(lang, '输出内容可以商用吗？', 'Can I use outputs commercially?'), tr(lang, '模型的商用授权和内容使用以字节跳动官方条款为准，使用涉及人物、商标或第三方材料的内容时，应确认相应权利。', 'Commercial use and content rights are governed by ByteDance’s official terms. Check the relevant rights for people, trademarks and third-party material.')),
        (tr(lang, 'AnyAIGC 能开发票吗？支持增值税专票吗？', 'Can AnyAIGC issue invoices, including VAT special invoices?'), tr(lang, '能。按实际充值金额开具增值税普通发票或增值税专用发票，将开票信息提交给客服即可。', 'Yes. AnyAIGC issues invoices for actual top-ups, including Chinese VAT general and special invoices. Send your invoicing details to support.')),
        (tr(lang, '企业可以对公转账和签合同吗？', 'Can my company pay by bank transfer and sign a contract?'), tr(lang, f'可以。支持企业对公转账充值、签订服务合同，并提供专属客服和技术对接。请<a href="{SUPPORT}">联系企业客服</a>。', f'Yes. Companies can use bank transfer, sign a service agreement and receive dedicated support and a technical contact. <a href="{SUPPORT}">Talk to sales</a>.')),
        (payments.Q[lang], payments.A[lang]),
        *trust.FAQ[lang],
    ]
    assert len(rows) == 12
    return rows

def head(lang, slug, faq):
    n = name(slug)
    me = f'{SITE}/{lang}/models/{slug}'
    title, desc = metadata(lang, slug)
    og = f'{SITE}/assets/og/{slug}-{lang}.png'
    offers = price_offers(lang, slug)
    lang_attr = tr(lang, 'zh-CN', 'en')
    crumbs = [(tr(lang, '首页', 'Home'), SITE + '/'), (tr(lang, '模型专题', 'Model guides'), f'{SITE}/{lang}/models/'), (n, me)]
    graph = [
        {'@type': 'Organization', '@id': SITE + '/#org', 'name': 'AnyAIGC', 'url': 'https://anyaigc.ai', 'logo': SITE + '/logo.webp'},
        {'@type': 'WebSite', '@id': SITE + '/#website', 'name': 'AnyAIGC', 'url': SITE + '/', 'publisher': {'@id': SITE + '/#org'}},
        {'@type': 'WebPage', '@id': me + '#webpage', 'url': me, 'name': title, 'description': desc, 'inLanguage': lang_attr, 'dateModified': DATE, 'isPartOf': {'@id': SITE + '/#website'}, 'breadcrumb': {'@id': me + '#breadcrumb'}, 'mainEntity': {'@id': me + '#product'}},
        {'@type': 'BreadcrumbList', '@id': me + '#breadcrumb', 'itemListElement': [{'@type': 'ListItem', 'position': i+1, 'name': label, 'item': url} for i, (label, url) in enumerate(crumbs)]},
        {'@type': 'Product', '@id': me + '#product', 'name': n + ' API', 'sku': LATEST[slug], 'description': COPY[slug][lang]['summary'], 'image': og, 'category': 'Large language model API', 'brand': {'@type': 'Brand', 'name': 'AnyAIGC'}, 'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'USD', 'lowPrice': min((p for _, p in offers), key=Decimal), 'highPrice': max((p for _, p in offers), key=Decimal), 'offerCount': len(offers), 'url': me + '#pricing', 'offers': [{'@type': 'Offer', 'name': label, 'price': price, 'priceCurrency': 'USD', 'url': me + '#pricing'} for label, price in offers]}},
        {'@type': 'FAQPage', '@id': me + '#faq', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in faq]},
    ]
    return f'''<!DOCTYPE html>
<html lang="{lang_attr}" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(n)} API,{e(n)} API pricing,{e(n)} API 企业,{e(n)} API 发票,{e(n)} API for business,Doubao Seed API,AnyAIGC">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#171719">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{slug}">
<link rel="alternate" hreflang="en" href="{SITE}/en/models/{slug}">
<link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{slug}">
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{tr(lang, 'zh_CN', 'en_US')}">
<meta property="og:locale:alternate" content="{tr(lang, 'en_US', 'zh_CN')}">
<meta property="og:url" content="{me}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AnyAIGC {e(n)} API">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261024b">
<link rel="stylesheet" href="/assets/models/doubao-seed.css?v={VER}">
<script type="application/ld+json">
{json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)}
</script>
</head>
'''

def nav(lang, slug):
    other = tr(lang, 'en', 'zh')
    links = [(f'/{lang}/models/', tr(lang, '模型专题', 'Model guides')), (PRICING, tr(lang, '模型广场', 'Model catalog')), ('#pricing', tr(lang, '价格', 'Pricing')), ('#enterprise', tr(lang, '企业接入', 'Enterprise')), (DOCS, tr(lang, 'API 文档', 'API docs'))]
    items = ''.join(f'<li><a class="o-pill" href="{url}">{label}</a></li>' for url, label in links)
    return f'''<body>
<a class="o-skip" href="#main">{tr(lang, '跳到主要内容', 'Skip to main content')}</a>
<header class="o-nav"><div class="o-wrap o-nav-inner">
<a class="o-brand" href="/">AnyAIGC</a>
<nav aria-label="{tr(lang, '主导航', 'Main navigation')}"><ul class="o-nav-left">{items}</ul></nav>
<ul class="o-nav-right">
<li><a class="o-pill" href="/{other}/models/{slug}" hreflang="{tr(lang, 'en', 'zh-CN')}" lang="{tr(lang, 'en', 'zh-CN')}">{tr(lang, 'English', '中文')}</a></li>
<li class="sd-hide-sm"><a class="o-pill" href="https://anyaigc.ai/console">{tr(lang, '登录', 'Log in')}</a></li>
<li><a class="o-btn sd-btn-white sd-nav-cta" href="{REG}">{tr(lang, '免费注册', 'Sign up free')}</a></li>
</ul></div></header>
<main id="main">
'''

def hero(lang, slug):
    c = COPY[slug][lang]
    r = MODELS[slug]['rates'][0]
    tiles = ''.join(f'<li class="db-tile">{art(art_kind(title))}<span class="db-tile-label">{e(title)}</span></li>' for title, _ in c['features'])
    tiles += f'<li class="db-tile">{art("text")}<span class="db-tile-label">Chat Completions</span></li>'
    facts = [CONCURRENCY[lang + '_short'], '300+ ' + tr(lang, '模型 · 一个 Key', 'models · one key'), tr(lang, '对公 · 专票 · 合同', 'Bank transfer · VAT invoices')]
    return f'''  <section class="sd-hero" aria-labelledby="hero-title">
    <div class="sd-hero-glow" aria-hidden="true"></div>
    <div class="o-wrap sd-hero-grid">
      <div class="sd-hero-copy">
        <nav aria-label="{tr(lang, '面包屑', 'Breadcrumb')}"><ol class="o-crumbs"><li><a href="/">{tr(lang, '首页', 'Home')}</a></li><li><a href="/{lang}/models/">{tr(lang, '模型专题', 'Model guides')}</a></li><li aria-current="page">{e(name(slug))}</li></ol></nav>
        <p class="sd-eyebrow">{logo()}<span>{tr(lang, '字节跳动 · Doubao Seed', 'ByteDance · Doubao Seed')}</span></p>
        <h1 class="sd-h1" id="hero-title">{e(name(slug))} API</h1>
        <p class="sd-lead">{e(c['tagline'])}{tr(lang, '。', '. ')}<strong>{tr(lang, f'输入 ${r["input"]} / 百万 tokens 起', f'From ${r["input"]} / 1M input tokens')}</strong></p>
        <p class="sd-lead-sub">{e(c['summary'])}</p>
        <div class="o-cta"><a class="o-btn sd-btn-glass" href="{REG}">{tr(lang, '获取 API Key', 'Get an API key')} <span class="sd-arrow" aria-hidden="true">→</span></a><a class="o-btn sd-btn-glass" href="#pricing">{tr(lang, '查看 API 价格', 'See API pricing')}</a></div>
        <ul class="o-facts">{''.join(f'<li>{e(f)}</li>' for f in facts)}</ul>
      </div>
      <figure class="db-canvas sd-hero-media" aria-label="{tr(lang, '模型能力示意', 'Model capability illustration')}"><ul>{tiles}</ul></figure>
    </div>
  </section>

'''

def capabilities(lang, slug):
    c = COPY[slug][lang]
    m = MODELS[slug]
    specs = [(tr(lang, '模型名称', 'Model'), e(m['name'])), (tr(lang, '接口', 'Endpoint'), '<code>/v1/chat/completions</code>'), (tr(lang, '计费', 'Billing'), 'USD / 1M tokens')]
    if m.get('context'):
        specs.append((tr(lang, '上下文', 'Context'), e(m['context'])))
    if m.get('max_output'):
        specs.append((tr(lang, '最大输出', 'Maximum output'), e(m['max_output'])))
    spec = '<dl class="sd-spec o-reveal">' + ''.join(f'<div><dt>{key}</dt><dd>{value}</dd></div>' for key, value in specs) + '</dl>'
    about = section('about', tr(lang, name(slug) + ' 是什么', 'About ' + name(slug)), f'<div class="sd-prose"><p>{e(c["summary"])}</p></div>\n{spec}')
    cards = '\n'.join(f'<li class="sd-feature o-reveal">{art(art_kind(title))}<div class="sd-feature-body"><h3>{e(title)}</h3><p>{e(desc)}</p></div></li>' for title, desc in c['features'])
    return about + section('features', tr(lang, name(slug) + ' 能做什么', 'Capabilities of ' + name(slug)), '<ul class="sd-features">\n' + cards + '\n</ul>', band=True)

def pricing(lang, slug):
    rates = MODELS[slug]['rates']
    labels = {'input': tr(lang, '输入', 'Input'), 'output': tr(lang, '输出', 'Output'),
              'cache': tr(lang, '缓存命中', 'Cache hit'), 'audio': tr(lang, '音频输入', 'Audio input')}
    body = ''
    for rate in rates:
        rows = ''.join(f'<tr><th scope="row">{label}</th><td><code>{e(name(slug))}</code></td><td class="o-num o-hl">${rate[kind]} / 1M</td></tr>\n' for kind, label in labels.items() if rate.get(kind) is not None)
        body += f'<tbody><tr><th colspan="3" scope="rowgroup">{e(rate["range_" + lang])}</th></tr>\n{rows}</tbody>\n'
    model = MODELS[slug]
    if model.get('audio_base') is not None:
        body += f'<tbody><tr><th scope="row">{tr(lang, "音频输入", "Audio input")}</th><td><code>{e(name(slug))}</code></td><td class="o-num o-hl">${model["audio_base"]} / 1M</td></tr></tbody>\n'
    notes = [f'{rate["range_" + lang]}: {rate["missing_" + lang]}' for rate in rates if rate.get('missing_' + lang)]
    if model.get('audio_base') is not None:
        notes.append(model['audio_scope_' + lang])
    note_html = ''.join(f'<p class="o-note">{e(note)}</p>\n' for note in notes)
    billing = [(tr(lang, '按 token 计费', 'Pay per token'), tr(lang, '输入、输出分别计价', 'Input and output billed separately')),
               (tr(lang, '按实际用量', 'Actual usage'), tr(lang, '回复长度随请求而变', 'Reply length depends on the request')),
               (CONCURRENCY[lang + '_short'], CONCURRENCY[lang + '_audience']),
               (tr(lang, '余额通用', 'Shared balance'), tr(lang, '300+ 模型共用余额', 'One balance across 300+ models'))]
    bill = '<ul class="o-billing o-reveal">' + ''.join(f'<li><strong>{e(title)}</strong>{e(desc)}</li>' for title, desc in billing) + '</ul>'
    cost_cards = []
    for count, inp, out in [(100, 1000, 200), (1000, 1000, 200), (1000, 2000, 500)]:
        total_in = Decimal(count * inp) / Decimal(1000000)
        total_out = Decimal(count * out) / Decimal(1000000)
        r = rates[0]
        total = total_in * Decimal(r['input']) + total_out * Decimal(r['output'])
        title = tr(lang, f'{count:,} 次请求', f'{count:,} requests')
        desc = tr(lang, f'每次输入 {inp:,}、输出 {out:,} tokens', f'{inp:,} input + {out:,} output tokens per call')
        calc = f'{total_in.normalize():f} × ${r["input"]} + {total_out.normalize():f} × ${r["output"]}'
        cost_cards.append(f'<li class="o-cost o-reveal"><h4>{title}</h4><p class="o-cost-off">{desc}</p><p class="o-cost-calc">{calc}</p><p class="o-cost-total">{currency(total)}</p></li>')
    note = tr(lang, '单位 USD；展示模型广场最低可用价，按成功提交后的实际 token 用量计费。阶梯取决于单次请求输入长度，实时价格以模型广场为准。', 'Prices are in USD at the lowest available catalog rate, based on actual token usage after successful submission. Tiers depend on input length per request. Check the catalog for live prices.')
    cost_note = tr(lang, '示例采用首档文本价格，不含缓存命中或音频输入；每次请求的输入长度均在首档以内。', 'Examples use first-tier text rates without cache hits or audio input; each request stays within the first input tier.')
    content = f'''{bill}
      <p class="db-table-hint">{tr(lang, '左右滑动查看完整价格表', 'Scroll sideways to see the full pricing table')}</p>
      <div class="o-table-wrap o-reveal" tabindex="0" role="region" aria-label="{tr(lang, 'API 价格表，可横向滚动', 'API pricing table, horizontally scrollable')}">
        <table class="o-table"><caption class="o-sr">{e(name(slug))} API {tr(lang, '价格（USD / 百万 tokens）', 'prices (USD / 1M tokens)')}</caption>
        <thead><tr><th scope="col">{tr(lang, '计费项目', 'Billing item')}</th><th scope="col">{tr(lang, '模型名称', 'Model')}</th><th class="o-num" scope="col">{tr(lang, '单价（USD）', 'Unit price (USD)')}</th></tr></thead>
{body}        </table>
      </div>
      {note_html}
      <p class="o-note">{note}</p>
      <h3 class="sd-h3">{tr(lang, '成本示例', 'Cost examples')}</h3><p class="o-note">{cost_note}</p>
      <ul class="o-costs">{''.join(cost_cards)}</ul>
      <div class="o-price-cta"><a class="o-btn o-btn-dark" href="{REG}">{tr(lang, '获取 API Key', 'Get an API key')}</a><a class="o-btn o-btn-light" href="{PRICING}">{tr(lang, '在模型广场查看', 'View in the model catalog')}</a></div>'''
    return section('pricing', name(slug) + tr(lang, ' API 价格', ' API pricing'), content)

def uses(lang, slug):
    items = ''.join(f'<li class="o-reveal"><span class="sd-k">{e(label)}</span><h3>{e(title)}</h3><p>{e(desc)}</p></li>\n' for label, title, desc in COPY[slug][lang]['uses'])
    return section('use-cases', tr(lang, '把模型用在这些任务里', 'Where this model fits'), '<ul class="sd-uses">' + items + '</ul>', band=True)

def platform(lang):
    items = [(tr(lang, '一个 Key，300+ 模型', 'One key, 300+ models'), tr(lang, '在同一个账户管理调用和余额，按业务需要选择模型。', 'Manage usage and balance in one account, choosing models for each workload.')),
             (tr(lang, '国内直接调用', 'Direct access from mainland China'), tr(lang, '通过 AnyAIGC 接口接入，无需单独注册火山引擎账号。', 'Use the AnyAIGC endpoint without a separate Volcano Engine account.')),
             (tr(lang, '公开单价', 'Published unit rates'), tr(lang, '输入、输出和适用的缓存价格分别列明，控制台可查调用明细。', 'Separate input, output and applicable cache rates, with per-request records in the console.')),
             (CONCURRENCY[lang + '_short'], CONCURRENCY[lang])]
    cards = ''.join(f'<li class="o-card o-reveal"><h3>{e(title)}</h3><p>{e(desc)}</p></li>\n' for title, desc in items)
    return section('platform', tr(lang, '通过 AnyAIGC 接入 Doubao Seed', 'Access Doubao Seed through AnyAIGC'), '<ul class="o-cards">' + cards + '</ul>')

def codes(lang, slug, snapshot=None):
    snapshot = snapshot or LATEST[slug]
    assert snapshot in SNAPSHOTS[slug]
    prompt = SNAPSHOT_COPY[snapshot][lang]['prompt']
    model_py = json.dumps(snapshot) if CODE_ID_LITERAL else 'os.environ["ANYAIGC_MODEL"]'
    payload = {'model': snapshot if CODE_ID_LITERAL else '${ANYAIGC_MODEL}', 'messages': [{'role': 'user', 'content': prompt}], 'stream': False}
    if CODE_ID_LITERAL:
        curl_json = shlex.quote(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        # Expand only the model variable; JSON quotes are shell-escaped.
        curl_json = '"' + json.dumps(payload, ensure_ascii=False, indent=2).replace('"', '\\"') + '"'
    curl = f'''curl https://anyaigc.ai/v1/chat/completions \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d {curl_json}'''
    py = f'''import json
import os
from urllib.request import Request, urlopen

payload = {{
    "model": {model_py},
    "messages": [{{"role": "user", "content": {json.dumps(prompt, ensure_ascii=False)}}}],
    "stream": False,
}}
request = Request(
    "https://anyaigc.ai/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={{
        "Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"],
        "Content-Type": "application/json",
    }},
    method="POST",
)
with urlopen(request, timeout=120) as response:
    result = json.load(response)
print(result["choices"][0]["message"]["content"])
print(result.get("usage", {{}}))'''
    sdk = f'''import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["ANYAIGC_API_KEY"],
    base_url="https://anyaigc.ai/v1",
)
reply = client.chat.completions.create(
    model={model_py},
    messages=[{{"role": "user", "content": {json.dumps(prompt, ensure_ascii=False)}}}],
    stream=False,
)
print(reply.choices[0].message.content)'''
    return [('py', 'Python', py), ('curl', 'cURL', curl), ('sdk', 'OpenAI SDK', sdk)]

def quickstart(lang, slug):
    steps = [tr(lang, f'<a href="{REG}">注册 AnyAIGC</a>，新用户可先使用 200 万 tokens 试用额度。', f'<a href="{REG}">Create an AnyAIGC account</a> and start with 2M free trial tokens.'),
             tr(lang, '在<a href="https://anyaigc.ai/console">控制台</a>创建 Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。', 'Create a key in the <a href="https://anyaigc.ai/console">console</a> and save it as <code>ANYAIGC_API_KEY</code>.'),
             tr(lang, '向 <code>POST /v1/chat/completions</code> 发送对话请求，读取 JSON 中的回复。', 'Send a chat request to <code>POST /v1/chat/completions</code> and read the reply from its JSON response.')]
    if not CODE_ID_LITERAL:
        steps[1] += tr(lang, ' 从模型广场复制本版本的完整模型 ID，设置为 <code>ANYAIGC_MODEL</code>。', ' Copy this edition’s full model ID from the catalog into <code>ANYAIGC_MODEL</code>.')
    tabs, panels = [], []
    examples = codes(lang, slug)
    for ordinal, snapshot in enumerate(SNAPSHOTS[slug][1:], 1):
        for tid, label, code in codes(lang, slug, snapshot):
            prefix = tr(lang, '旧版', 'Older') + (f' {ordinal}' if len(SNAPSHOTS[slug]) > 2 else '')
            examples.append((f'old-{ordinal}-{tid}', prefix + ' ' + label, code))
    for i, (tid, label, code) in enumerate(examples):
        tabs.append(f'<li role="presentation"><button type="button" role="tab" id="tab-{tid}" aria-controls="panel-{tid}" aria-selected="{str(i == 0).lower()}">{label}</button></li>')
        panels.append(f'''      <figure class="o-code" id="panel-{tid}" role="tabpanel" aria-labelledby="tab-{tid}">
        <figcaption><b>{label} · /v1/chat/completions</b><button class="o-copy" type="button" aria-controls="code-{tid}" data-done="{tr(lang, '已复制', 'Copied')}">{tr(lang, '复制', 'Copy')}</button></figcaption>
<pre id="code-{tid}"><code>{e(code)}</code></pre>
      </figure>''')
    note = tr(lang, f'Python 示例仅使用标准库；SDK 示例需先安装 <code>openai</code>。本页展示非流式对话，返回 <code>choices</code> 与 <code>usage</code>。更多字段见<a href="{DOCS}">Chat Completions 文档</a>。', f'The Python example uses the standard library; install <code>openai</code> for the SDK example. These non-streaming calls return <code>choices</code> and <code>usage</code>. See the <a href="{DOCS}">Chat Completions reference</a> for more fields.')
    content = '<ol class="o-steps">' + ''.join(f'<li>{s}</li>' for s in steps) + '</ol>\n'
    if len(SNAPSHOTS[slug]) > 1:
        content += '<p class="o-note">' + tr(lang, '默认示例使用当前最新快照。已有项目可选择「旧版」标签查看原版本的完整调用代码；页面介绍以最新快照为准。', 'The default examples use the latest snapshot. Choose an “Older” tab for complete code for the previous snapshot. The overview describes the latest version.') + '</p>\n'
    content += '<ul class="o-tabs" role="tablist" aria-label="Code examples">' + ''.join(tabs) + '</ul>\n' + '\n'.join(panels) + f'\n<p class="sd-callout">{note}</p>'
    return section('quickstart', tr(lang, '快速接入 ', 'Integrate ') + name(slug) + ' API', content, band=True, narrow=True)

def enterprise(lang, slug):
    cards = tr(lang,
        [('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票。'), ('对公转账', '公司账户直接付款', '支持企业对公转账充值，方便财务核对。'), ('签订合同', '配合企业采购', '可签订服务合同，支持企业采购与法务流程。'), ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入与日常问题排查。')],
        [('Invoices', 'Chinese VAT invoices', 'Invoices for each top-up, including Chinese VAT general and special invoices.'), ('Bank transfer', 'Use a company account', 'Top up by corporate bank transfer for straightforward reconciliation.'), ('Contracts', 'Business procurement', 'Sign a service agreement to support procurement and legal review.'), ('Dedicated support', 'Customer and technical contacts', 'Dedicated support and a technical contact for onboarding and troubleshooting.')])
    content = '<ul class="o-cards">' + ''.join(f'<li class="o-card o-reveal"><strong>{e(label)}</strong><h3>{e(title)}</h3><p>{e(desc)}</p></li>\n' for label, title, desc in cards) + '</ul>\n'
    content += payments.pay_row(lang, 'o')
    content += f'<div class="o-price-cta"><a class="o-btn o-btn-dark" href="{SUPPORT}">{tr(lang, "联系企业客服", "Talk to sales")}</a><a class="o-btn o-btn-light" href="{REG}">{tr(lang, "先注册试用", "Start with a free account")}</a></div>'
    return section('enterprise', tr(lang, f'企业接入 {name(slug)} API', f'{name(slug)} API for teams and enterprises'), content, narrow=True)

def family(lang, slug):
    items = []
    for s in SLUGS:
        active = ' aria-current="page"' if s == slug else ''
        items.append(f'<li><a href="/{lang}/models/{s}"{active}><b>{e(name(s))}</b><span>{e(COPY[s][lang]["tagline"])}</span></a></li>')
    content = '<ul class="o-family">' + '\n'.join(items) + '</ul>'
    return section('family', tr(lang, '同系列 Doubao Seed 模型', 'Explore the Doubao Seed family'), content, band=True)

def faq_section(lang, slug, rows):
    content = '      <div class="o-faq">\n' + ''.join(f'        <details{" open" if i == 0 else ""}><summary><h3>{e(q)}</h3></summary><div class="o-ans"><p>{a}</p></div></details>\n' for i, (q, a) in enumerate(rows)) + '      </div>'
    return section('faq', name(slug) + tr(lang, ' API 常见问题', ' API FAQ'), content, narrow=True)

def footer(lang, slug):
    other = tr(lang, 'en', 'zh')
    switch = f'<a class="o-pill" href="/{other}/models/{slug}" hreflang="{tr(lang, "en", "zh-CN")}">{tr(lang, "English", "中文")}</a>'
    legal = tr(lang, 'Doubao、Seed 是字节跳动的商标。AnyAIGC 是独立 API 服务商，与字节跳动无隶属关系。', 'Doubao and Seed are trademarks of ByteDance. AnyAIGC is an independent API provider and is not affiliated with ByteDance.')
    return f'''  <section class="o-final" aria-labelledby="final-title"><div class="o-wrap">
    <div class="sd-final-logo">{logo(52)}</div>
    <h2 id="final-title">{tr(lang, '让模型进入你的工作流', 'Bring the model into your workflow')}</h2>
    <p>{tr(lang, '从一次调用开始，使用一个 Key 接入 300+ 模型。', 'Start with one request. Use a single key across 300+ models.')}</p>
    <div class="o-cta"><a class="o-btn o-btn-dark" href="{REG}">{tr(lang, '获取 API Key', 'Get an API key')}</a><a class="o-btn o-btn-light" href="{DOCS}">{tr(lang, '阅读 API 文档', 'Read the API docs')}</a></div>
    <ul class="o-related"><li><a class="o-pill" href="/{lang}/models/">{tr(lang, '全部模型专题', 'All model guides')}</a></li><li><a class="o-pill" href="{PRICING}">{tr(lang, '模型广场', 'Model catalog')}</a></li><li>{switch}</li></ul>
  </div></section>
</main>
<footer class="o-foot"><div class="o-wrap"><div class="o-foot-top">
<div class="o-foot-brand"><a class="o-brand" href="/">AnyAIGC</a><p>{tr(lang, '一个 Base URL、一个 API Key，统一调用 300+ 模型。', 'One base URL and one API key for 300+ models.')}</p></div>
<div class="o-foot-cols"><div class="o-foot-col"><h2>{tr(lang, '产品', 'Product')}</h2><ul><li><a href="/{lang}/models/">{tr(lang, '模型专题', 'Model guides')}</a></li><li><a href="https://anyaigc.ai/console">{tr(lang, '控制台', 'Console')}</a></li></ul></div><div class="o-foot-col"><h2>{tr(lang, '资源', 'Resources')}</h2><ul><li><a href="{DOCS}">{tr(lang, 'API 文档', 'API docs')}</a></li><li><a href="{SUPPORT}">{tr(lang, '联系客服', 'Contact support')}</a></li></ul></div><div class="o-foot-col"><h2>{tr(lang, '条款', 'Legal')}</h2><ul><li><a href="/privacy">{tr(lang, '隐私政策', 'Privacy policy')}</a></li><li><a href="/terms">{tr(lang, '服务条款', 'Terms of service')}</a></li></ul></div></div>
</div><div class="o-foot-bottom"><p>{logo(16)}<span>© 2026 AnyAIGC. {legal}</span></p>{switch}</div></div></footer>
<script src="/assets/models/doubao-seed.js?v={VER}" defer></script>
</body>
</html>
'''

def page(lang, slug):
    if CONCURRENCY is None or CODE_ID_LITERAL is None:
        raise ValueError('Confirm concurrency/RPM and code model-ID display before generating guides.')
    rows = faqs(lang, slug)
    return (head(lang, slug, rows) + nav(lang, slug) + hero(lang, slug) + capabilities(lang, slug)
            + pricing(lang, slug) + uses(lang, slug) + platform(lang) + quickstart(lang, slug)
            + enterprise(lang, slug) + trust.section(lang, 'o') + family(lang, slug)
            + faq_section(lang, slug, rows) + footer(lang, slug))

def main():
    for lang in ('zh', 'en'):
        for slug in SLUGS:
            (ROOT / lang / 'models' / (slug + '.html')).write_text(page(lang, slug), encoding='utf-8', newline='\n')
    print(f'Written {len(SLUGS)*2} Doubao Seed guides.')

if __name__ == '__main__':
    main()
