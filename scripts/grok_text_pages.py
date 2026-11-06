"""Generate bilingual Grok text guides; run payments.py and trust.py afterward."""
import html
import json
import re
from decimal import Decimal
from pathlib import Path

from grok_text_data import DATE, VER, SITE, REG, MARKET, SUPPORT, CHAT, MESSAGES, OFFICIAL, HUB, MODELS, SLUGS
import payments
import trust

ROOT = Path(__file__).resolve().parent.parent
RAW = (ROOT / 'assets/icons/grok.svg').read_text(encoding='utf-8')
PATHS = re.findall(r'<path\b[^>]*d="([^"]+)"', RAW)


def logo(cls='gt-mark', fill='#0a0a0a'):
    size = 24 if cls == 'gt-card-mark' else 30
    return f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" fill-rule="evenodd" aria-hidden="true" focusable="false">' + ''.join(f'<path d="{p}"></path>' for p in PATHS) + '</svg>'


def e(s):
    return html.escape(str(s), quote=True)


def url(lang, slug):
    return f'{SITE}/{lang}/models/{slug}'


def tr(lang, zh, en):
    return zh if lang == 'zh' else en


def rows(lang, selected):
    """One table, grouped by model and billing tier; no undocumented cache prices."""
    bodies, offers = [], []
    for slug in selected:
        m = MODELS[slug]
        p = m['prices']
        tiers = [(tr(lang, '普通输入档 · 输入 ≤ 200,000 tokens', 'Base tier · input ≤ 200,000 tokens') if p[3] else tr(lang, '输入 / 输出', 'Input / output'), p[:3])]
        if p[3]:
            tiers.append((tr(lang, '长输入档 · 200,000 < 输入 ≤ 500,000 tokens', 'Long-input tier · 200,000 < input ≤ 500,000 tokens'), (p[3], p[4], None)))
        for tier_name, prices in tiers:
            body = f'<tbody><tr class="gt-tier"><th colspan="3">{e(m["name"])} <span>{e(tier_name)}</span></th></tr>'
            for label, value in zip((tr(lang, '输入', 'Input'), tr(lang, '输出', 'Output'), tr(lang, '缓存命中输入', 'Cache-hit input')), prices):
                if value is None:
                    continue
                body += f'<tr><th scope="row">{label}</th><td><code>{slug}</code></td><td><strong>${value}</strong><small> / 1M tokens</small></td></tr>'
                offers.append({'@type': 'Offer', 'name': f'{slug} · {tier_name} · {label} / 1M tokens', 'price': value, 'priceCurrency': 'USD', 'url': MARKET})
            bodies.append(body + '</tbody>')
    return ''.join(bodies), offers


def faqs(lang, slug):
    hub = slug == HUB
    m = MODELS['grok-4.7' if hub else slug]
    p = m['prices']
    ids = '、'.join(MODELS) if lang == 'zh' else ', '.join(MODELS)
    price_answer = (f'输入 ${p[0]}、输出 ${p[1]}/百万 tokens。' if lang == 'zh' else f'Input costs ${p[0]} and output costs ${p[1]} per million tokens. ')
    if hub:
        price_answer = tr(lang, '系列输入最低 $0.0993/百万 tokens（grok-build-0.1）；grok-4.7 输入 $0.1985、输出 $0.5956/百万 tokens。', 'Series input starts at $0.0993 per million tokens for grok-build-0.1. Grok 4.7 input is $0.1985 and output is $0.5956 per million tokens. ')
    if p[3]:
        price_answer += tr(lang, f'输入超过 200,000 且不超过 500,000 tokens 时，{m["name"]} 输入 ${p[3]}、输出 ${p[4]}/百万 tokens。', f'For {m["name"]} requests with over 200,000 and up to 500,000 input tokens, input is ${p[3]} and output is ${p[4]} per million tokens. ')
    price_answer += tr(lang, '以上为模型广场最低展示价，实时价格以模型广场为准。', 'These are the lowest displayed catalog rates; check the model catalog for current pricing.')
    endpoint = tr(lang, '所有型号支持 POST /v1/chat/completions；grok-4.7、4.6、4.5、4.3 另支持 POST /v1/messages。', 'All listed models support POST /v1/chat/completions. Grok 4.7, 4.6, 4.5, and 4.3 also support POST /v1/messages.') if hub else tr(lang, '支持 POST /v1/chat/completions' + (' 和 POST /v1/messages。' if m['messages'] else '，按模型广场当前标注接入。'), 'Supports POST /v1/chat/completions' + (' and POST /v1/messages.' if m['messages'] else ', as currently listed in the model catalog.'))
    out = [
        (tr(lang, 'Grok API 支持哪些型号？' if hub else f'{m["name"]} 的 API 模型名是什么？', 'Which Grok models are available?' if hub else f'What model ID should I use for {m["name"]}?'), tr(lang, f'本页覆盖 {ids}。grok-4.x 是系列专题地址；调用时使用具体模型名，示例默认使用 grok-4.7。' if hub else f'使用 {slug}，保持大小写和符号一致。Grok 4.x 总览可查看同系列其他型号。', f'This guide covers {ids}. grok-4.x is the guide URL, not an API model ID; examples use grok-4.7.' if hub else f'Use {slug} exactly as written. See the Grok 4.x overview for other models in the series.')),
        (tr(lang, 'Grok API 如何计费？', 'How is the Grok API priced?'), price_answer),
        (tr(lang, '支持哪些 API 接口？', 'Which API endpoints are supported?'), endpoint),
        (tr(lang, '并发和 RPM 有限制吗？', 'Are there concurrency or RPM limits?'), tr(lang, '以上型号所有用户默认并发不限，无需单独申请开通。请在应用中合理管理连接、超时与重试。', 'All models listed here have unlimited concurrency by default for every user, with no separate activation. Manage connections, timeouts, and retries in your application.')),
        (tr(lang, 'Grok API 能直接获取 X 的实时数据吗？', 'Does the API automatically include live X data?'), tr(lang, '普通对话不会自动获得实时事件。xAI 官方文档要求启用搜索工具才能使用实时数据；本页基础示例不包含搜索，也不承诺 AnyAIGC 支持所有上游搜索工具。商用以 xAI 官方条款为准。', 'Ordinary chat does not automatically include live events. xAI requires search tools for live data; the basic examples here do not use search or promise support for every upstream search tool. Commercial use is governed by xAI terms.')),
        (tr(lang, 'AnyAIGC 能开发票吗？支持增值税专票吗？', 'Can AnyAIGC issue invoices, including VAT special invoices?'), tr(lang, '支持增值税普通发票和增值税专用发票，按实际充值金额开具。', 'Yes. AnyAIGC issues Chinese VAT general and VAT special invoices based on the actual top-up amount.')),
        (tr(lang, '企业可以对公转账和签合同吗？', 'Can my company pay by bank transfer and sign a contract?'), tr(lang, '可以。支持企业对公转账充值、签订服务合同，并提供专属客服和技术对接。', 'Yes. Companies can top up by corporate bank transfer, sign a service contract, and work with dedicated support and technical contacts.')),
        (payments.Q[lang], payments.A[lang]),
        *trust.FAQ[lang],
    ]
    return out


def code_examples(lang, slug):
    m = MODELS[slug]
    payload = {'model': slug, 'messages': [{'role': 'user', 'content': m[f'prompt_{lang}']}], 'stream': False}
    curl = 'curl https://anyaigc.ai/v1/chat/completions \\\n  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d \'' + json.dumps(payload, ensure_ascii=False, indent=2) + "'"
    py = 'import json\nimport os\nimport urllib.request\n\npayload = ' + repr(payload) + '\nrequest = urllib.request.Request(\n    "https://anyaigc.ai/v1/chat/completions",\n    data=json.dumps(payload).encode("utf-8"),\n    headers={\n        "Authorization": f"Bearer {os.environ[\'ANYAIGC_API_KEY\']}",\n        "Content-Type": "application/json",\n    },\n    method="POST",\n)\nwith urllib.request.urlopen(request, timeout=180) as response:\n    result = json.load(response)\nprint(result["choices"][0]["message"]["content"])'
    samples = [('cURL', curl), ('Python · ' + tr(lang, '标准库', 'standard library'), py)]
    if m['messages']:
        msg = payload.copy()
        msg['max_tokens'] = 1024
        samples.append(('Messages · cURL', 'curl https://anyaigc.ai/v1/messages \\\n  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n  -H "Content-Type: application/json" \\\n  -d \'' + json.dumps(msg, ensure_ascii=False, indent=2) + "'"))
    return ''.join(f'<div class="gt-code"><div class="gt-code-bar"><span>{label}</span><button type="button" data-copy>{tr(lang,"复制","Copy")}</button></div><pre><code>{e(code)}</code></pre></div>' for label, code in samples)


def page(lang, slug):
    hub = slug == HUB
    key = 'grok-4.7' if hub else slug
    m = MODELS[key]
    name = 'Grok 4.x' if hub else m['name']
    other = 'en' if lang == 'zh' else 'zh'
    title = tr(lang, f'{name} API 价格与接入 - AnyAIGC', f'{name} API Pricing & Integration - AnyAIGC')
    p = m['prices']
    low = '0.0993' if hub else p[0]
    desc = tr(lang, f'{name} API 输入 ${low}/百万 tokens 起，支持文本对话、编程与知识工作，所有用户默认并发不限，国内直连、按量计费，提供企业对公转账、合同与增值税专票。', f'{name} API from ${low}/1M input tokens. Coding and chat, unlimited concurrency, usage billing, bank transfers and VAT invoices via AnyAIGC.')
    selected = list(MODELS) if hub else [slug]
    table, offers = rows(lang, selected)
    faq = faqs(lang, slug)
    crumbs = [(tr(lang, '首页', 'Home'), f'{SITE}/'), (tr(lang, '模型专题', 'Model guides'), f'{SITE}/{lang}/models/')]
    if not hub:
        crumbs.append(('Grok 4.x', url(lang, HUB)))
    crumbs.append((name, url(lang, slug)))
    graph = [
        {'@type': 'Organization', '@id': f'{SITE}/#org', 'name': 'AnyAIGC', 'url': 'https://anyaigc.ai', 'logo': f'{SITE}/logo.webp'},
        {'@type': 'WebSite', '@id': f'{SITE}/#website', 'name': 'AnyAIGC', 'url': f'{SITE}/', 'publisher': {'@id': f'{SITE}/#org'}},
        {'@type': 'WebPage', '@id': url(lang, slug) + '#webpage', 'url': url(lang, slug), 'name': title, 'description': desc, 'dateModified': DATE, 'inLanguage': 'zh-CN' if lang == 'zh' else 'en', 'isPartOf': {'@id': f'{SITE}/#website'}, 'breadcrumb': {'@id': url(lang, slug) + '#breadcrumb'}},
        {'@type': 'BreadcrumbList', '@id': url(lang, slug) + '#breadcrumb', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]},
        {'@type': 'Product', '@id': url(lang, slug) + '#product', 'name': f'{name} API', 'description': desc, 'image': f'{SITE}/assets/og/{slug}-{lang}.png', 'brand': {'@type': 'Brand', 'name': 'Grok'}, 'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'USD', 'lowPrice': min(offers, key=lambda x: Decimal(x['price']))['price'], 'highPrice': max(offers, key=lambda x: Decimal(x['price']))['price'], 'offerCount': len(offers), 'offers': offers}},
        {'@type': 'FAQPage', '@id': url(lang, slug) + '#faq', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]},
    ]
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    headline, intro, focus, tags, features = m[lang]
    if hub:
        headline = tr(lang, '从一个想法，\n到下一个构建。', 'From your next idea.\nTo your next build.')
        intro = tr(lang, 'Grok 4.7、4.6、4.5、4.3、4、4.20 与 Build 0.1，一个 API Key 接入。为编程、智能体与知识工作选择合适的型号。', 'One API key for Grok 4.7, 4.6, 4.5, 4.3, 4, 4.20, and Build 0.1. Choose a model for coding, agents, and knowledge work.')
    breadcrumb = ''.join(f'<a href="{u[len(SITE):]}">{n}</a><span aria-hidden="true">/</span>' for n, u in crumbs[:-1]) + f'<span aria-current="page">{name}</span>'
    family = ''.join(f'<a href="/{lang}/models/{s}"' + (' aria-current="page"' if s == slug else '') + f'><span>{v["name"]}</span><small>{e(v[lang][2])}</small><b aria-hidden="true">↗</b></a>' for s, v in MODELS.items())
    feature_html = ''.join(f'<article><span class="gt-number">0{i+1}</span><h3>{h}</h3><p>{d}</p></article>' for i, (h, d) in enumerate(features))
    # Exact decimal sums from the displayed base rates. Each request remains in the <=200K input tier.
    ci, co = Decimal(p[0]), Decimal(p[1])
    cost1, cost2 = ci / 10 + co / 50, ci + co / 5
    costs = tr(lang,
        f'<article><h3>单次分析</h3><p>100,000 输入 + 20,000 输出 tokens</p><code>${p[0]} × 0.1 + ${p[1]} × 0.02</code><strong>${cost1:f}</strong></article><article><h3>10 次相同规模任务</h3><p>每次 100,000 输入 + 20,000 输出 tokens</p><code>10 × ${cost1:f}</code><strong>${cost2:f}</strong></article>',
        f'<article><h3>One analysis</h3><p>100,000 input + 20,000 output tokens</p><code>${p[0]} × 0.1 + ${p[1]} × 0.02</code><strong>${cost1:f}</strong></article><article><h3>Ten tasks of the same size</h3><p>100,000 input + 20,000 output tokens each</p><code>10 × ${cost1:f}</code><strong>${cost2:f}</strong></article>')
    ent_cards = tr(lang, [('增值税发票', '按实际充值金额开具增值税普通发票或专用发票，普票、专票均支持。'), ('对公转账', '支持企业对公转账充值，方便公司采购与财务核算。'), ('签订合同', '可签订服务合同，满足采购、审批和法务流程。'), ('专属对接', '提供专属客服与技术对接，协助接入和问题排查。')], [('Invoices', 'Chinese VAT general and special invoices based on the actual top-up amount.'), ('Bank transfer', 'Top up directly from your corporate bank account for company procurement.'), ('Contracts', 'Sign a service contract for procurement and legal review.'), ('Dedicated support', 'Dedicated support and technical contacts for integration and troubleshooting.')])
    enterprise = ''.join(f'<article><span class="gt-number">0{i+1}</span><h3>{h}</h3><p>{d}</p></article>' for i,(h,d) in enumerate(ent_cards))
    faq_html = '\n'.join(f'<details><summary><h3>{e(q)}</h3></summary><div class="o-ans"><p>{e(a)}</p></div></details>' for q,a in faq)
    ep_extra = f'<a href="{MESSAGES}"><code>POST /v1/messages</code> ↗</a>' if m['messages'] else ''
    brief = tr(lang, f'输入 ${low}/百万 tokens 起 · 所有用户默认并发不限', f'Input from ${low}/1M tokens · Unlimited concurrency for every user')
    return f'''<!DOCTYPE html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{name} API,{name} API pricing,{name} API key,{name} API 企业,{name} API 发票,{name} API for business,AnyAIGC">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#ffffff">
<link rel="canonical" href="{url(lang,slug)}">
<link rel="alternate" hreflang="zh-CN" href="{url('zh',slug)}">
<link rel="alternate" hreflang="en" href="{url('en',slug)}">
<link rel="alternate" hreflang="x-default" href="{url('en',slug)}">
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{'zh_CN' if lang=='zh' else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if lang=='zh' else 'zh_CN'}">
<meta property="og:url" content="{url(lang,slug)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/assets/og/{slug}-{lang}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AnyAIGC · {name} API · {e(brief)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og/{slug}-{lang}.png">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v={VER}">
<link rel="stylesheet" href="/assets/models/grok-text.css?v={VER}">
<script type="application/ld+json">
{ld}
</script>
<script src="/assets/models/grok-text.js?v={VER}" defer></script>
</head>
<body>
<a class="gt-skip" href="#main">{tr(lang,'跳到主要内容','Skip to main content')}</a>
<header class="gt-nav"><a class="gt-brand" href="/">AnyAIGC<span> / Grok</span></a>
<nav aria-label="{tr(lang,'主导航','Main navigation')}">
<a href="/{lang}/models/">{tr(lang,'模型专题','Model guides')}</a><a href="{MARKET}">{tr(lang,'模型广场','Catalog')}</a><a href="#pricing">{tr(lang,'价格','Pricing')}</a><a href="#enterprise">{tr(lang,'企业接入','Enterprise')}</a><a href="{CHAT}">{tr(lang,'API 文档','API docs')}</a>
</nav><div class="gt-nav-actions"><a class="gt-language" href="/{other}/models/{slug}" hreflang="{'en' if other=='en' else 'zh-CN'}">{tr(lang,'English','中文')}</a><a class="gt-login" href="https://anyaigc.ai/console">{tr(lang,'登录','Log in')}</a><a class="gt-btn gt-btn-dark gt-signup" href="{REG}">{tr(lang,'注册','Sign up')} <span aria-hidden="true">↗</span></a></div></header>
<main id="main">
<div class="gt-wrap"><nav class="gt-crumbs" aria-label="{tr(lang,'面包屑','Breadcrumb')}">{breadcrumb}</nav></div>
<section class="gt-hero gt-wrap" aria-labelledby="hero-title"><p class="gt-eyebrow">{logo()} xAI / {tr(lang,'文本与编程','TEXT & CODE')}</p>
<h1 id="hero-title">{name} API</h1><p class="gt-headline">{headline.replace(chr(10),'<br>')}</p><p class="gt-intro">{intro}</p><p class="gt-price-line">{brief}</p><div class="gt-actions"><a class="gt-btn gt-btn-dark" href="{REG}">{tr(lang,'获取 API Key','Get an API key')} <span aria-hidden="true">↗</span></a><a class="gt-btn gt-btn-soft" href="#pricing">{tr(lang,'查看 API 价格','Explore pricing')} <span aria-hidden="true">↓</span></a></div><div class="gt-chips"><span>{tr(lang,'300+ 模型一个 Key','300+ models, one key')}</span><span>{tr(lang,'国内直连','Direct API access')}</span><span>{tr(lang,'对公 · 专票','Contracts · invoices')}</span></div>
</section>
<section class="gt-wrap gt-section" id="capabilities"><div class="gt-section-head"><p class="gt-kicker">01 / {tr(lang,'能力','CAPABILITIES')}</p><h2>{tr(lang,'为真正的工作而构建。','Built for work that matters.')}</h2><p>{e(tags)}</p></div><div class="gt-grid gt-features">{feature_html}</div><p class="gt-note">{tr(lang,'模型能力根据官方发布页与模型广场整理；不同型号的能力和接口分别以对应文档为准。','Capabilities are based on official release notes and the catalog. Check the documentation for the model and endpoint you use.')} <a href="{OFFICIAL}">{tr(lang,'Grok 4.7 官方发布说明','Grok 4.7 release notes')} ↗</a></p></section>
<section class="gt-section gt-tint" id="pricing"><div class="gt-wrap"><div class="gt-section-head"><p class="gt-kicker">02 / {tr(lang,'按量计费','USAGE PRICING')}</p><h2>{name} API {tr(lang,'价格','pricing')}</h2><p>{tr(lang,'按输入与输出 tokens 计费，价格直接列清楚。','Clear input and output rates, billed by token usage.')}</p></div><div class="gt-billing"><span>{tr(lang,'USD / 百万 tokens','USD / 1M tokens')}</span><span>{tr(lang,'所有用户默认并发不限','Unlimited concurrency by default')}</span><span>{tr(lang,'余额跨模型通用','One balance across models')}</span></div>
<div class="gt-table-wrap" role="region" aria-label="{name} API {tr(lang,'价格表','price table')}" tabindex="0"><table><caption>{tr(lang,'模型广场最低展示价 · 核对日期','Lowest displayed catalog rates · checked')} {DATE}</caption><thead><tr><th scope="col">{tr(lang,'功能 / 档位','Operation / tier')}</th><th scope="col">{tr(lang,'模型名','Model ID')}</th><th scope="col">{tr(lang,'单价（USD）','Price (USD)')}</th></tr></thead>{table}</table></div>
<p class="gt-note">{tr(lang,'单位 USD。按成功提交的请求计量，依据实际输入、输出 tokens 扣费；实时价格以模型广场为准。200K / 500K 是输入计费档位边界，不代表所有型号的上下文上限。未列出的缓存费用不视为免费；缓存命中和其他计费项以实际账单为准。','Prices are in USD. Successfully submitted requests are metered by actual input and output tokens; current catalog rates apply. The 200K / 500K boundaries describe input billing tiers, not context limits for every model. Unlisted cache rates do not mean free usage; actual cache hits and other charges follow your bill.')}</p>
<h3 class="gt-cost-heading">{tr(lang,'成本示例','Cost examples')} · {key}</h3><div class="gt-costs">{costs}</div><p class="gt-note">{tr(lang,'示例均按普通输入档计算，不含缓存命中或其他工具费用。','Examples use the base input tier, without cache hits or additional tool charges.')}</p><div class="gt-actions"><a class="gt-btn gt-btn-dark" href="{REG}">{tr(lang,'获取 API Key','Get an API key')} ↗</a><a class="gt-text-link" href="{MARKET}">{tr(lang,'在模型广场查看','View in the model catalog')} ↗</a></div></div></section>
<section class="gt-section gt-wrap" id="use-cases"><div class="gt-section-head"><p class="gt-kicker">03 / {tr(lang,'应用场景','USE CASES')}</p><h2>{tr(lang,'接进你的工作流。','Bring it into your workflow.')}</h2></div><div class="gt-grid"><article><h3>{tr(lang,'开发与代码评审','Development & code review')}</h3><p>{tr(lang,'提供代码和约束，生成实现建议、测试计划与评审意见，再由项目工具验证。','Supply code and constraints for implementation suggestions, test plans, and review notes. Verify with your project tools.')}</p></article><article><h3>{tr(lang,'业务智能体','Business agents')}</h3><p>{tr(lang,'连接查询、计算与内部系统，把多个步骤编排成可追踪的任务。工具可用性按具体型号确认。','Connect queries, calculations, and internal systems into traceable multi-step tasks. Confirm tool support for your chosen model.')}</p></article><article><h3>{tr(lang,'资料与知识工作','Research & knowledge work')}</h3><p>{tr(lang,'围绕提供的资料组织摘要、方案和报告草稿，为关键事实保留来源与复核。','Turn supplied material into summaries, proposals, and report drafts, with sources and review for key facts.')}</p></article></div></section>
<section class="gt-section gt-wrap" id="platform"><div class="gt-platform"><div><p class="gt-kicker">AnyAIGC</p><h2>{tr(lang,'一个 Key，连接下一步。','One key. More ways forward.')}</h2></div><div class="gt-platform-list"><p>{tr(lang,'300+ 模型统一接入，余额通用。','One API key and shared balance for 300+ models.')}</p><p>{tr(lang,'国内直连，按公开单价计算成本。','Direct access with published unit rates for budgeting.')}</p><p>{tr(lang,'本系列所有用户默认并发不限。','Unlimited concurrency for every user of this series.')}</p></div></div></section>
<section class="gt-section gt-tint" id="quickstart"><div class="gt-wrap"><div class="gt-section-head"><p class="gt-kicker">04 / {tr(lang,'快速开始','QUICKSTART')}</p><h2>{tr(lang,'接入','Integrate')} {name} API</h2><p>{tr(lang,'从最小请求开始，逐步接进你的应用。','Start with a minimal request, then connect it to your application.')}</p></div><ol class="gt-steps"><li><b>01</b><span>{tr(lang,'注册 AnyAIGC，进入控制台创建 API Key。','Sign up and create an API key in the console.')}</span></li><li><b>02</b><span>{tr(lang,'设置环境变量 ANYAIGC_API_KEY。','Set the ANYAIGC_API_KEY environment variable.')}</span></li><li><b>03</b><span>{tr(lang,f'使用 {key} 发起请求，在控制台查看用量。',f'Send a request with {key} and inspect usage in the console.')}</span></li></ol><div class="gt-endpoints"><a href="{CHAT}"><code>POST /v1/chat/completions</code> ↗</a>{ep_extra}</div>
<p class="gt-note">{tr(lang,'cURL 示例适用于 Bash / WSL；Python 使用标准库，无需安装 SDK。请求返回完整 JSON，Python 示例读取 choices[0].message.content。','The cURL examples use Bash / WSL. Python uses the standard library without an SDK. Requests return complete JSON; Python reads choices[0].message.content.')}</p>{code_examples(lang,key)}<p class="gt-note">{tr(lang,'接口字段与返回格式以 AnyAIGC 文档为准。Messages 文档未单独说明 Grok 的响应差异，因此示例仅展示请求，不假设额外返回字段。','AnyAIGC documentation defines request and response fields. The Messages page does not document Grok-specific response differences, so that example shows the request without assuming extra response fields.')}</p></div></section>
<section class="gt-section gt-wrap" id="enterprise"><div class="gt-section-head"><p class="gt-kicker">05 / {tr(lang,'企业接入','ENTERPRISE')}</p><h2>{tr(lang,f'企业接入 {name} API',f'{name} API for teams and enterprises')}</h2><p>{tr(lang,'从采购、财务到研发，按企业的方式接入。','Bring procurement, finance, and engineering into one integration process.')}</p></div><div class="gt-grid gt-enterprise">{enterprise}</div>{payments.pay_row(lang,'o')}<div class="gt-actions"><a class="gt-btn gt-btn-dark" href="{SUPPORT}">{tr(lang,'联系企业客服','Talk to sales')} ↗</a><a class="gt-btn gt-btn-soft" href="{REG}">{tr(lang,'先注册试用','Start with a free account')}</a></div></section>
{trust.section(lang,'o')}
<section class="gt-section gt-wrap" id="family"><div class="gt-section-head"><p class="gt-kicker">06 / {tr(lang,'同系列模型','MODEL FAMILY')}</p><h2>{tr(lang,'找到适合下一项任务的 Grok。','Find Grok for your next task.')}</h2><a class="gt-text-link" href="/{lang}/models/{HUB}">{tr(lang,'Grok 4.x 全系总览与价格对比','Grok 4.x overview and price comparison')} ↗</a></div><div class="gt-family">{family}</div><div class="gt-related"><a href="/{lang}/models/grok-image">Grok Image ↗</a><a href="/{lang}/models/grok-video">Grok Video ↗</a></div></section>
<section class="gt-section gt-wrap" id="faq"><div class="gt-faq-head"><p class="gt-kicker">07 / FAQ</p><h2>{name} API {tr(lang,'常见问题','FAQ')}</h2></div><div class="gt-faq">{faq_html}</div></section>
<section class="gt-final"><div class="gt-wrap">{logo(fill='#ffffff')}<p>{tr(lang,'你的下一个构建，从这里开始。','Your next build starts here.')}</p><a class="gt-btn gt-btn-white" href="{REG}">{tr(lang,'获取 API Key','Get an API key')} ↗</a><div class="gt-final-links"><a href="/{lang}/models/">{tr(lang,'模型专题','Model guides')}</a><a href="{MARKET}">{tr(lang,'模型广场','Model catalog')}</a><a href="{CHAT}">{tr(lang,'API 文档','API docs')}</a><a href="/{other}/models/{slug}" hreflang="{'en' if other=='en' else 'zh-CN'}">{tr(lang,'English','中文')}</a></div></div></section>
</main><footer class="gt-footer gt-wrap"><div><a class="gt-brand" href="/">AnyAIGC</a><p>{tr(lang,'300+ 模型，一个 API Key。','300+ models. One API key.')}</p></div><div><a href="/privacy">{tr(lang,'隐私政策','Privacy')}</a><a href="/terms">{tr(lang,'服务条款','Terms')}</a><a href="{SUPPORT}">{tr(lang,'联系客服','Support')}</a></div><p class="gt-legal">{tr(lang,'Grok 是 xAI 的商标。AnyAIGC 是独立 API 服务商，与其无隶属关系。商用授权以 xAI 官方条款为准。','Grok is a trademark of xAI. AnyAIGC is an independent API provider and is not affiliated with xAI. Commercial use is governed by xAI terms.')} © 2026 AnyAIGC</p></footer>
</body></html>
'''


if __name__ == '__main__':
    for lang in ('zh', 'en'):
        for slug in SLUGS:
            (ROOT / lang / 'models' / f'{slug}.html').write_text(page(lang, slug), encoding='utf-8', newline='\n')
    print('Generated 18 Grok text pages.')
