import html
import io
import json
import os
import re
from decimal import Decimal
from seedance_data import *

NL = '\n'
ICON = io.open(os.path.join(ROOT, 'assets', 'icons', 'bytedance-color.svg'), encoding='utf-8').read()
ICON = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', ICON, re.S).group(1), flags=re.S)

def esc(x): return html.escape(str(x), quote=True)
def logo(size=24, cls=''): return f'<svg class="{cls}" viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true" focusable="false">{ICON}</svg>'

L = {
 'zh': {'lang':'zh-CN','other':'en','other_name':'English','home':'首页','hub':'模型专题','market':'模型广场','price':'价格','ent':'企业接入','docs':'API 文档','login':'登录','signup':'免费注册','key':'获取 API Key','see':'查看价格','crumb':'面包屑','facts':'核心信息','copy':'复制','copied':'已复制','trust':'为什么可以放心用 AnyAIGC','faq':'Seedance API 常见问题','family':'Seedance 系列模型','contact':'联系企业客服'},
 'en': {'lang':'en','other':'zh','other_name':'中文','home':'Home','hub':'Model guides','market':'Model catalog','price':'Pricing','ent':'Enterprise','docs':'API docs','login':'Log in','signup':'Sign up free','key':'Get an API key','see':'See pricing','crumb':'Breadcrumb','facts':'Key facts','copy':'Copy','copied':'Copied','trust':'Why teams trust AnyAIGC','faq':'Seedance API FAQ','family':'Seedance model family','contact':'Contact enterprise support'},
}

def faq_items(lang, slug):
    m = MODELS.get(slug)
    if lang == 'zh':
        name = m['name'] if m else 'Seedance'
        price = m['min'] if m else '1.843'
        rows = '；'.join(f'{a}（{b}）：${c} / 1M tokens' for a,b,c in (m['rows'] if m else []))
        return [
          (f'{name} API 多少钱？', f'AnyAIGC 按 1M tokens 计费，价格取决于分辨率和是否包含参考视频。{rows or "Seedance 2.0 mini 含参考视频最低为 $1.843 / 1M tokens"}。实时价格以<a href="{PRICING}">模型广场</a>为准。'),
          ('Seedance 支持哪些输入和能力？', 'Seedance 2.0 支持文字、图片、音频和视频作为参考输入，并支持视频编辑、延长与原生音频。2.0 Fast 侧重更快生成，2.0 mini 面向高频规模化场景；2.5 增强长叙事、参考和精准编辑。'),
          ('一次调用会返回几条视频？', '一次创建任务返回一个任务 ID，任务完成后通过查询接口取得一个视频链接。生成是异步的，具体时长由 duration 参数或模型选择决定。'),
          ('支持哪些分辨率、比例和时长？', 'Seedance 2.0 支持 480p、720p、1080p 和 4K，4K 当前可调用。Seedance 2.5 支持 480p、720p、1080p，duration 为 4–30 或 -1；Fast 和 mini 的价格档位为 480p / 720p。比例、时长等参数按具体型号的 API 文档传入。'),
          ('如何查询生成结果？', '创建任务后保存返回的 id，调用 GET /api/v3/contents/generations/tasks/{id} 查询。成功时从 content.video_url 取得临时视频链接，状态字段以接口返回为准。'),
          ('并发有限制吗？', 'AnyAIGC 对 Seedance 不设置并发限制，所有用户默认享有。大批量请求仍建议根据任务返回和业务队列做好重试与下载。'),
          ('AnyAIGC 能开发票吗？支持增值税专票吗？', '可以。AnyAIGC 支持按实际充值金额开具增值税普通发票和增值税专用发票。'),
          ('企业可以对公转账和签合同吗？', '可以。支持企业对公转账充值、签订服务合同，并提供专属客服和技术对接。'),
          ('支持哪些支付方式？', '支持微信支付、支付宝、USDT 和信用卡充值，企业还可以对公转账。余额按 USD 计价，对平台所有模型通用。'),
          ('新用户有免费试用额度吗？', '有。新用户注册后赠送 200 万 tokens 试用额度，最低 1 美元起充。'),
          ('余额可以退款吗？', '可以。未使用余额可申请退款，不收手续费。具体流程请联系客服。'),
          ('会不会用低配模型冒充？我的数据安全吗？', '请求走官方模型渠道，不使用低配或逆向模型冒充。除法律法规要求外，不对输入输出做持久化存储，也不用于训练；控制台可查看调用明细。'),
        ]
    name = m['name'] if m else 'Seedance'
    price = m['min'] if m else '1.843'
    rows = '; '.join(f'{a} ({b}): ${c} / 1M tokens' for a,b,c in (m['rows_en'] if m else []))
    return [
      (f'How much does the {name} API cost?', f'AnyAIGC bills per 1M tokens, with rates varying by resolution and reference-video input. {rows or "Seedance 2.0 mini starts at $1.843 / 1M tokens with video input"}. See the <a href="{PRICING}">model catalog</a> for live rates.'),
      ('What can Seedance take as input?', 'Seedance 2.0 accepts text, images, audio and video as references, with video editing, extension and native audio. 2.0 Fast prioritizes speed, 2.0 mini is designed for high-frequency workloads, and 2.5 adds stronger long narratives, references and precise edits.'),
      ('How many videos does one request return?', 'A create request returns one task ID. After the asynchronous task finishes, query it to obtain one video URL. Duration is controlled by the duration field or the model.'),
      ('Which resolutions, ratios and durations are supported?', 'Seedance 2.0 supports 480p, 720p, 1080p and 4K; the 4K tier is available now. Seedance 2.5 supports 480p, 720p and 1080p, with duration 4–30 or -1. Fast and mini have 480p / 720p pricing tiers. Follow each model’s API documentation for aspect ratio and duration parameters.'),
      ('How do I retrieve the result?', 'Save the id returned by the create call, then call GET /api/v3/contents/generations/tasks/{id}. When it succeeds, read content.video_url. The exact status values come from the API response.'),
      ('Is there a concurrency limit?', 'AnyAIGC sets no concurrency limit for Seedance, and every account gets this by default. Use a queue and retry strategy for large batches.'),
      ('Can AnyAIGC issue invoices, including VAT special invoices?', 'Yes. AnyAIGC supports Chinese VAT general and special invoices based on the actual top-up amount.'),
      ('Can a company pay by bank transfer and sign a contract?', 'Yes. Companies can top up by bank transfer, sign a service contract, and get a dedicated support and technical contact.'),
      ('Which payment methods are supported?', 'Top up with WeChat Pay, Alipay, USDT or a credit card. Companies can also pay by bank transfer. Balances are in USD and work across the platform.'),
      ('Is there free trial credit for new users?', 'Yes. New accounts get 2 million tokens of trial credit, and top-ups start at $1.'),
      ('Can I get a refund on my balance?', 'Unused balance can be refunded with no fee. Contact support for the process.'),
      ('Are these the real models? Is my data safe?', 'Requests go through official model channels. Unless required by law, prompts and outputs are not persistently stored or used for training; the console shows request details.'),
    ]

def price_table(lang, slug):
    if slug == 'seedance':
        rows = []
        for s in SLUGS[1:]:
            m = MODELS[s]; rows.append(f'<tr><th scope="row"><a href="/{lang}/models/{s}">{m["name"]}</a><small><code>{m["id"]}</code></small></th><td>按 1M tokens / per 1M tokens</td><td class="o-num"><strong>${m["min"]}</strong> 起 / from</td></tr>')
        return '<div class="sd-table-wrap o-reveal"><table class="sd-table"><caption class="sr-only">Seedance model pricing</caption><thead><tr><th>型号 / Model</th><th>计费 / Billing</th><th>起步价 / From</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
    m = MODELS[slug]; data = m['rows'] if lang == 'zh' else m['rows_en']
    rows = ''.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class="o-num"><strong>${c}</strong> / 1M tokens</td></tr>' for a,b,c in data)
    return f'<div class="sd-table-wrap o-reveal"><table class="sd-table"><caption class="sr-only">{esc(m["name"])} API pricing</caption><thead><tr><th>分辨率 / Resolution</th><th>适用档位 / Tier</th><th>价格 / Price</th></tr></thead><tbody>{rows}</tbody></table></div>'

def code(lang, slug):
    model = MODELS['doubao-seedance-2-0']['id'] if slug == 'seedance' else MODELS[slug]['id']
    prompt = '一只橘猫沿着海边石阶走下，电影感，环境声自然同步' if lang == 'zh' else 'An orange cat walks down seaside steps, cinematic, with natural synced ambience'
    return f'''curl -X POST "https://anyaigc.ai/api/v3/contents/generations/tasks" \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "content": [{{"text": "{prompt}", "type": "text"}}],
    "model": "{model}",
    "duration": 8,
    "generate_audio": true,
    "ratio": "16:9",
    "resolution": "720p",
    "watermark": false
  }}'

# Save the returned id, then query the asynchronous task
curl "https://anyaigc.ai/api/v3/contents/generations/tasks/<task_id>" \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY"'''

def hero_media(lang, slug):
    version = '2.5' if slug in ('seedance', 'doubao-seedance-2-5') else '2.0'
    filename = 'seedance-' + version.replace('.', '-') + '-official'
    official = 'https://seed.bytedance.com/zh/seedance' + version.replace('.', '_')
    zh = lang == 'zh'
    caption = f'Seedance {version} 官方演示' if zh else f'Official Seedance {version} demo'
    if slug in ('doubao-seedance-2-0-fast', 'doubao-seedance-2-0-mini'):
        caption += ' · 系列能力参考' if zh else ' · Family capability reference'
    credit = '来源：字节跳动 Seed · 版权归字节跳动所有' if zh else 'Source: ByteDance Seed · Copyright ByteDance'
    return f'''<figure class="sd-hero-media">
<div class="sd-hero-art">
<video src="/assets/models/seedance/{filename}.mp4?v={VER}" poster="/assets/models/seedance/{filename}.webp?v={VER}" width="1280" height="720" controls playsinline preload="metadata" aria-label="{esc(caption)}"></video>
</div>
<figcaption><b>{caption}</b><a href="{official}" target="_blank" rel="noopener">{credit} ↗</a></figcaption>
</figure>'''


def page(lang, slug):
    t=L[lang]; overview=slug=='seedance'; m=MODELS.get(slug); name='Seedance' if overview else m['name']; other=f'/{t["other"]}/models/{slug}'
    title = ('Seedance API 价格与接入｜多模态视频生成 - AnyAIGC' if lang=='zh' else 'Seedance API Pricing & Access | Multimodal Video - AnyAIGC') if overview else (f'{name} API 价格与接入｜视频生成 - AnyAIGC' if lang=='zh' else f'{name} API Pricing & Access | Video Generation - AnyAIGC')
    desc = (f'Seedance 视频生成 API：Seedance 2.0、2.0 Fast、2.0 mini 与 2.5，按 1M tokens 计费，起步 $1.843，支持多模态参考、异步任务、并发不限、对公转账与增值税专票。' if lang=='zh' else 'Seedance video API for 2.0, 2.0 Fast, 2.0 mini and 2.5. From $1.843 per 1M tokens, multimodal references, async tasks, unlimited concurrency, bank transfer and VAT invoices.') if overview else (f'{name} 视频生成 API，按 1M tokens 计费，最低 ${m["min"]}，支持异步任务、多模态参考、并发不限、对公转账与增值税专票。' if lang=='zh' else f'{name} video API from ${m["min"]} per 1M tokens with async tasks, multimodal references, unlimited concurrency, bank transfer and VAT invoices.')
    me=f'{SITE}/{lang}/models/{slug}'; faqs=faq_items(lang,slug)
    graph=[{'@type':'Organization','@id':SITE+'/#org','name':'AnyAIGC','url':'https://anyaigc.ai','logo':SITE+'/logo.webp'},{'@type':'WebSite','@id':SITE+'/#website','url':SITE+'/','name':'AnyAIGC','publisher':{'@id':SITE+'/#org'}},{'@type':'WebPage','@id':me+'#webpage','url':me,'name':title,'description':desc,'inLanguage':t['lang'],'dateModified':DATE},{'@type':'BreadcrumbList','@id':me+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':1,'name':t['home'],'item':SITE+'/'},{'@type':'ListItem','position':2,'name':t['hub'],'item':f'{SITE}/{lang}/models/'},{'@type':'ListItem','position':3,'name':name,'item':me}]},{'@type':'Product','@id':me+'#product','name':name+' API (AnyAIGC)','description':desc,'category':'视频生成 API' if lang=='zh' else 'Video generation API','sku':m['id'] if m else 'seedance','image':SITE+f'/assets/og/{slug}-{lang}.png','brand':{'@type':'Brand','name':'AnyAIGC'},'offers':{'@type':'AggregateOffer','priceCurrency':'USD','lowPrice':m['min'] if m else '1.843','highPrice':m['min'] if m else '14.216','offerCount':len(m['rows']) if m else 4,'availability':'https://schema.org/InStock','url':me+'#pricing','offers':[{'@type':'Offer','name':(m['name'] if m else s),'price':(m['min'] if m else MODELS[s]['min']),'priceCurrency':'USD'} for s in ([slug] if m else SLUGS[1:])] }},{'@type':'FAQPage','@id':me+'#faq','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':re.sub(r'<[^>]+>','',a)}} for q,a in faqs]}]
    ld=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False,indent=2)
    family=''.join(f'<li><a href="/{lang}/models/{s}"'+(' aria-current="page"' if s==slug else '')+f'><b>{MODELS[s]["name"]}</b><span>${MODELS[s]["min"]} / 1M tokens 起</span></a></li>' for s in SLUGS[1:])
    feature_cards=[('全模态参考','文字、图片、视频和音频可以组合为参考素材。'),('原生音画','通过 generate_audio 请求同步生成声音，适合广告和社媒内容。'),('导演级控制','用 content 数组描述镜头、角色、动作、对白和参考素材。'),('异步任务','提交后返回任务 ID，完成后从 content.video_url 下载结果。')]
    if lang=='en': feature_cards=[('Multimodal references','Combine text, images, video and audio as reference material.'),('Native audiovisual output','Set generate_audio to create synchronized sound for ads and social content.'),('Director-level control','Use the content array to describe shots, characters, actions, dialogue and references.'),('Async tasks','Create a task, poll its ID, then download content.video_url.')]
    features=''.join(f'<li class="sd-card o-reveal"><span class="sd-card-no">{i+1:02d}</span><h3>{h}</h3><p>{p}</p></li>' for i,(h,p) in enumerate(feature_cards))
    uses=[('广告','产品故事、镜头脚本和音画同步展示。'),('影视','参考素材驱动的角色、运镜与场景预演。'),('社媒','短视频草稿、批量变体与高频内容生产。')] if lang=='zh' else [('Advertising','Product stories, shot scripts and synced audiovisual demos.'),('Film','Reference-driven character, camera and scene previsualization.'),('Social','Short-form drafts, batch variants and high-frequency content.')]
    uses_html=''.join(f'<li><b>{h}</b><p>{p}</p></li>' for h,p in uses)
    faq_html=''.join(f'<details'+(' open' if i==0 else '')+f'><summary><h3>{q}</h3></summary><div class="o-ans"><p>{a}</p></div></details>' for i,(q,a) in enumerate(faqs))
    price_intro=('四个型号共用同一套异步任务接口；价格按生成消耗的 1M tokens 计费，参考视频输入有单独价格。' if lang=='zh' else 'All four models use the same async task endpoint. Billing is per 1M generated tokens, with separate rates when a reference video is included.') if not overview else ('按型号、分辨率和参考视频输入计费。以下是模型广场当前可见的最低档位，详情页列出每个型号的全部价格。' if lang=='zh' else 'Rates vary by model, resolution and reference-video input. The table shows current catalog starting rates; each model page lists every tier.')
    billing=('按 1M tokens','含参考视频有单独价格','一次提交返回一个任务','并发不限') if lang=='zh' else ('Per 1M tokens','Reference video has a separate rate','One task ID per request','Unlimited concurrency')
    billing_html=''.join(f'<li><strong>{x}</strong></li>' for x in billing)
    return finalize(f'''<!doctype html><html lang="{t['lang']}" data-scrollbar="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="keywords" content="{esc(name)} API,{esc(name)} API pricing,{esc(name)} API 企业,{esc(name)} API 发票,{esc(name)} API for business,AnyAIGC"><link rel="icon" href="/favicon.ico"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{me}"><link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{slug}"><link rel="alternate" hreflang="en" href="{SITE}/en/models/{slug}"><link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{slug}"><meta property="og:type" content="website"><meta property="og:site_name" content="AnyAIGC"><meta property="og:locale" content="{'zh_CN' if lang=='zh' else 'en_US'}"><meta property="og:locale:alternate" content="{'en_US' if lang=='zh' else 'zh_CN'}"><meta property="og:url" content="{me}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:image" content="{SITE}/assets/og/{slug}-{lang}.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="AnyAIGC {esc(name)} API"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{SITE}/assets/og/{slug}-{lang}.png"><link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261105"><link rel="stylesheet" href="/assets/models/seedance.css?v={VER}"><script type="application/ld+json">{ld}</script></head><body><a class="o-skip" href="#main">Skip to main content</a><header class="o-nav"><div class="o-wrap o-nav-inner"><a class="o-brand" href="/">AnyAIGC</a><nav><ul><li><a href="/{lang}/models/">{t['hub']}</a></li><li><a href="{PRICING}">{t['market']}</a></li><li><a href="#pricing">{t['price']}</a></li><li><a href="#enterprise">{t['ent']}</a></li><li><a href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{t['docs']}</a></li></ul></nav><ul class="o-nav-right"><li><a href="{other}" hreflang="{t['other']}">{t['other_name']}</a></li><li><a href="https://anyaigc.ai/console">{t['login']}</a></li><li><a class="sd-btn" href="{REG}">{t['signup']}</a></li></ul></div></header><main id="main"><section class="sd-hero"><div class="o-wrap"><ol class="o-crumbs"><li><a href="/">{t['home']}</a></li><li><a href="/{lang}/models/">{t['hub']}</a></li><li aria-current="page">{name}</li></ol><div class="sd-hero-grid"><div><p class="sd-eyebrow">{logo(22)}<span>ByteDance Seed · Video API</span></p><h1>{name} API</h1><p class="sd-lead">{('一个 Key 调用 Seedance 2.5、2.0、2.0 Fast 与 2.0 mini，最低 $1.843 / 1M tokens。' if lang=='zh' else 'One key for Seedance 2.5, 2.0, 2.0 Fast and 2.0 mini, from $1.843 / 1M tokens.') if overview else (m['desc_zh'] if lang=='zh' else m['desc_en'])}</p><div class="o-cta"><a class="sd-btn sd-btn-primary" href="{REG}">{t['key']} →</a><a class="sd-btn sd-btn-light" href="#pricing">{t['see']}</a></div><ul class="o-facts"><li>模型名 <strong><code>{'Seedance family' if overview else m['id']}</code></strong></li><li>计费 <strong>USD / 1M tokens</strong></li><li>接口 <strong><code>POST /api/v3/contents/generations/tasks</code></strong></li><li>{'并发' if lang=='zh' else 'Concurrency'} <strong>{'不限' if lang=='zh' else 'Unlimited'}</strong></li><li>{'企业' if lang=='zh' else 'Enterprise'} <strong>{'对公 · 专票' if lang=='zh' else 'Contracts · invoices'}</strong></li></ul></div>{hero_media(lang, slug)}</div></div></section><section class="o-section" id="features"><div class="o-wrap"><h2>Seedance {('视频模型能做什么' if lang=='zh' else 'video capabilities')}</h2><p class="o-lead">{('从文字和参考素材出发，把镜头、动作与声音放进同一套创作流程。' if lang=='zh' else 'Bring prompts, reference material, motion and sound into one video creation workflow.')}</p><ul class="sd-cards">{features}</ul></div></section><section class="o-section sd-band" id="pricing"><div class="o-wrap"><h2>{name} API {('价格' if lang=='zh' else 'pricing')}</h2><p class="o-lead">{price_intro}</p><ul class="o-billing">{billing_html}</ul>{price_table(lang,slug)}<p class="o-note">{('单位 USD；按成功提交的生成消耗计费，实时价格以模型广场为准。' if lang=='zh' else 'Prices are in USD and billed on successful generation usage. Live rates are shown in the model catalog.')}</p><div class="o-price-cta"><a class="sd-btn sd-btn-primary" href="{REG}">{t['key']}</a><a class="sd-btn sd-btn-light" href="{PRICING}">{t['market']}</a></div></div></section><section class="o-section" id="use-cases"><div class="o-wrap"><h2>{name} API {('使用场景' if lang=='zh' else 'use cases')}</h2><ul class="sd-uses">{uses_html}</ul></div></section><section class="o-section sd-band" id="quickstart"><div class="o-wrap"><h2>{('快速开始' if lang=='zh' else 'Quick start')}</h2><ol class="o-steps"><li>{('注册 AnyAIGC，创建 API Key。' if lang=='zh' else 'Sign up for AnyAIGC and create an API key.')}</li><li>{('向创建任务接口发送 JSON，保存返回的 id。' if lang=='zh' else 'POST JSON to the create-task endpoint and save the returned id.')}</li><li>{('轮询查询接口，成功后下载 content.video_url。' if lang=='zh' else 'Poll the query endpoint and download content.video_url when it succeeds.')}</li></ol><figure class="o-code"><figcaption><b>cURL · {'创建任务与查询结果' if lang=='zh' else 'Create and query a task'}</b><button class="o-copy" data-target="seedance-code">{t['copy']}</button></figcaption><pre id="seedance-code"><code>{esc(code(lang,slug))}</code></pre></figure><p class="o-note">{('接口字段和返回结构以' if lang=='zh' else 'Fields and response structure follow the ')}<a href="{DOC_CREATE_25 if slug=='doubao-seedance-2-5' else DOC_CREATE_20}" target="_blank" rel="noopener">{('AnyAIGC Seedance API 文档' if lang=='zh' else 'AnyAIGC Seedance API docs')}</a>{('为准。' if lang=='zh' else '.') } <a href="{DOC_QUERY}" target="_blank" rel="noopener">{('查询任务文档' if lang=='zh' else 'Query task docs')}</a></p></div></section><section class="o-section" id="enterprise"><div class="o-wrap"><h2>{('企业接入 '+name if lang=='zh' else 'Enterprise access for '+name)}</h2><p class="o-lead">{('企业可按采购、财务和技术流程接入 Seedance。' if lang=='zh' else 'Teams can adopt Seedance through a standard procurement, finance and engineering process.')}</p><ul class="sd-enterprise"><li><b>{'增值税发票' if lang=='zh' else 'VAT invoices'}</b><p>{'支持普票和专票。' if lang=='zh' else 'Chinese VAT general and special invoices are available.'}</p></li><li><b>{'对公转账' if lang=='zh' else 'Bank transfer'}</b><p>{'公司账户直接付款，账目清晰。' if lang=='zh' else 'Pay from a company account with clear records.'}</p></li><li><b>{'签订合同' if lang=='zh' else 'Service contracts'}</b><p>{'适配企业采购与法务流程。' if lang=='zh' else 'Fits procurement and legal review.'}</p></li><li><b>{'专属客服与技术对接' if lang=='zh' else 'Dedicated support'}</b><p>{'协助接入、迁移和问题排查。' if lang=='zh' else 'Support onboarding, migration and troubleshooting.'}</p></li></ul><div class="pay-row" role="group" aria-label="{'支持的支付方式' if lang=='zh' else 'Payment methods'}"><span class="pay-label">{'支持的支付方式' if lang=='zh' else 'Payment methods'}</span><ul class="pay-list">{''.join('<li>'+x+'</li>' for x in (['微信支付','支付宝','USDT','信用卡','对公转账'] if lang=='zh' else ['WeChat Pay','Alipay','USDT','Credit card','Bank transfer']))}</ul></div><div class="o-price-cta"><a class="sd-btn sd-btn-primary" href="{SUPPORT}">{t['contact']}</a><a class="sd-btn sd-btn-light" href="{REG}">{t['signup']}</a></div></div></section><section class="o-section" id="trust"><div class="o-wrap"><h2>{t['trust']}</h2><p class="o-lead">{'试用、充值、退款、数据和账单，关心的事项提前写清楚。' if lang=='zh' else 'Trial credit, top-ups, refunds, data handling and billing, spelled out up front.'}</p><ul class="trust-list"><li><h3>{'注册送 200 万 tokens' if lang=='zh' else '2M free tokens to start'}</h3><p>{'新用户注册即送试用额度。' if lang=='zh' else 'New accounts get trial credit.'}</p></li><li><h3>{'$1 起充，余额可退' if lang=='zh' else 'Top up from $1, refundable'}</h3><p>{'未使用余额可申请退款。' if lang=='zh' else 'Unused balance can be refunded.'}</p></li><li><h3>{'官方渠道，不掺假不降智' if lang=='zh' else 'Official channels, real models'}</h3><p>{'请求走官方模型渠道。' if lang=='zh' else 'Requests use official model channels.'}</p></li><li><h3>{'内容不留存、不训练' if lang=='zh' else 'No retention, no training'}</h3><p>{'除法律法规要求外，不持久化存储输入输出。' if lang=='zh' else 'Unless required by law, prompts and outputs are not persistently stored.'}</p></li><li><h3>{'账单透明，可设额度' if lang=='zh' else 'Transparent billing, spend caps'}</h3><p>{'控制台可查调用明细。' if lang=='zh' else 'The console shows request details.'}</p></li><li><h3>{'7×24 客服' if lang=='zh' else '24/7 support'}</h3><p><a href="{SUPPORT}">{'联系客服' if lang=='zh' else 'Contact support'}</a></p></li></ul></div></section><section class="o-section" id="family"><div class="o-wrap"><h2>{t['family']}</h2><p class="o-lead">{('同一个 API Key，改 model 字段即可切换型号。' if lang=='zh' else 'Use one API key and switch models by changing the model field.')}</p><ul class="o-family">{family}</ul></div></section><section class="o-section" id="faq"><div class="o-wrap"><h2>{t['faq']}</h2><div class="o-faq">{faq_html}</div></div></section><section class="o-final"><div class="o-wrap">{logo(48)}<h2>{'现在开始调用 Seedance' if lang=='zh' else 'Start using Seedance'}</h2><p>{'注册即送 200 万 tokens，使用一个 Key 调用全系模型。' if lang=='zh' else 'Sign up for 2M free tokens and call the entire family with one key.'}</p><div class="o-cta"><a class="sd-btn sd-btn-primary" href="{REG}">{t['signup']}</a><a class="sd-btn sd-btn-light" href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{t['docs']}</a></div></div></section></main><footer class="o-foot"><div class="o-wrap"><b>AnyAIGC</b><p>{'Seedance、豆包是北京字节跳动科技有限公司的商标。AnyAIGC 是独立 API 服务商，与字节跳动无隶属关系。' if lang=='zh' else 'Seedance and Doubao are trademarks of ByteDance. AnyAIGC is an independent API provider and is not affiliated with ByteDance.'}</p></div></footer><script src="/assets/models/seedance.js?v={VER}" defer></script></body></html>''', lang, slug)

def python_code(lang, slug):
    mid = MODELS[slug if slug != 'seedance' else 'doubao-seedance-2-0']['id']
    zh = lang == 'zh'
    prompt = '橘猫走下海边石阶，镜头缓缓跟随，海浪声与画面同步。' if zh else 'An orange cat walks down seaside steps. A slow tracking shot with synced ocean ambience.'
    return f'''import json
import os
import time
import urllib.request

BASE_URL = "https://anyaigc.ai/api/v3/contents/generations/tasks"
HEADERS = {{
    "Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"],
    "Content-Type": "application/json",
}}
payload = {{
    "model": "{mid}",
    "content": [{{"type": "text", "text": "{prompt}"}}],
    "duration": 8,
    "generate_audio": True,
    "ratio": "16:9",
    "resolution": "720p",
    "watermark": False,
}}

# {'创建任务，保存返回的 id' if zh else 'Create a task and save its id'}
request = urllib.request.Request(
    BASE_URL, json.dumps(payload).encode("utf-8"), HEADERS, method="POST"
)
with urllib.request.urlopen(request, timeout=60) as response:
    task_id = json.load(response)["id"]
print("task_id:", task_id)

# {'每 10 秒查询一次；最多等待 15 分钟' if zh else 'Poll every 10 seconds for up to 15 minutes'}
for _ in range(90):
    request = urllib.request.Request(BASE_URL + "/" + task_id, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    if result.get("status") == "succeeded":
        print(result["content"]["video_url"])
        break
    if result.get("error"):
        raise RuntimeError(result["error"])
    print(result.get("status"))
    time.sleep(10)
else:
    raise TimeoutError("{'查询超时，请保存任务 ID 后继续查询' if zh else 'Polling timed out. Keep the task ID and query again later.'}")'''


def pricing_block(lang, slug):
    zh = lang == 'zh'
    picked = list(MODELS) if slug == 'seedance' else [slug]
    headings = ['功能与分辨率', '模型名', '单价（USD）'] if zh else ['Operation and resolution', 'Model ID', 'Unit price (USD)']
    groups = []
    for s in picked:
        m = MODELS[s]
        rows = []
        for resolution, mode, price in m['rows' if zh else 'rows_en']:
            label = '视频生成' if mode == '不含参考视频' else '视频参考生成'
            if not zh:
                label = 'Video generation' if mode == 'Without reference video' else 'Video reference'
            rows.append(f'<tr><td>{label}<small>{resolution} · {mode}</small></td><td><code>{m["id"]}</code></td><td class="o-num"><strong>${price}</strong><small>/ 1M tokens</small></td></tr>')
        groups.append(f'<tbody><tr class="sd-price-heading"><th colspan="3" scope="rowgroup">{m["name"]}</th></tr>{"".join(rows)}</tbody>')
    table = f'<div class="sd-table-wrap"><table class="sd-table"><caption class="sr-only">Seedance API {"价格表" if zh else "pricing"}</caption><thead><tr>{"".join("<th scope=\"col\">"+h+"</th>" for h in headings)}</tr></thead>{"".join(groups)}</table></div>'
    # Scenarios use measured token totals rather than claiming a fixed cost per second.
    cost_models = ['doubao-seedance-2-0-mini', 'doubao-seedance-2-0-fast', 'doubao-seedance-2-5'] if slug == 'seedance' else [slug] * 3
    cards = []
    for i, s in enumerate(cost_models):
        resolution, mode, price = MODELS[s]['rows' if zh else 'rows_en'][0 if i != 1 else 1]
        quantity = [Decimal('0.1'), Decimal('0.2'), Decimal('1')][i]
        total = format(Decimal(price) * quantity, 'f')
        tokens = ['100,000', '200,000', '1,000,000'][i]
        cards.append(f'<li><h3>{MODELS[s]["name"]}</h3><p>{resolution} · {mode}</p><p>{tokens} tokens ÷ 1M × ${price}</p><strong>${total}</strong></li>')
    costs = f'<h3 class="sd-subheading">{"成本示例" if zh else "Cost examples"}</h3><p class="o-note">{"假设实际计费消耗如下；这不是固定时长视频的报价。实际费用以任务 usage 和账单为准。" if zh else "Assuming the following billed token usage. These are not fixed-duration video quotes; actual cost follows task usage and billing."}</p><ul class="sd-costs">{"".join(cards)}</ul>'
    cue = '<p class="sd-table-hint">' + ('← 左右滑动查看完整价格表 →' if zh else '← Scroll horizontally to view the full pricing table →') + '</p>'
    return table + cue + costs


def finalize(source, lang, slug):
    """Localize metadata, structured prices and shared sections before writing static HTML."""
    zh = lang == 'zh'
    overview = slug == 'seedance'
    name = 'Seedance' if overview else MODELS[slug]['name']
    doc = DOC_CREATE_25 if slug == 'doubao-seedance-2-5' else DOC_CREATE_20
    query_doc = DOC_QUERY if slug == 'doubao-seedance-2-5' else DOC_QUERY_20
    price = '1.843' if overview else MODELS[slug]['min']
    title = f'{name} API 价格与接入｜多模态视频 - AnyAIGC' if zh else f'{name} API Pricing & Access - AnyAIGC'
    desc = (f'{name} API 每百万 tokens ${price} 起，文字、图片、音频与视频参考生成，原生音画与异步任务，并发不限；AnyAIGC 支持企业对公转账、合同及增值税专票。' if zh else
            f'{name} API from ${price}/1M tokens. Multimodal video, native audio, async tasks and unlimited concurrency. VAT invoices and bank transfers.')
    if len(desc) > 160 and not zh:
        desc = f'{name} API from ${price}/1M tokens. Multimodal video, native audio, unlimited concurrency, async tasks, VAT invoices and bank transfers.'
    if slug == 'doubao-seedance-2-0-mini':
        desc = (f'{name} API 每百万 tokens ${price} 起，面向高频视频生成与规模化应用，采用异步任务接口，并发不限；AnyAIGC 支持企业对公转账、合同及增值税专票。' if zh else f'{name} API from ${price}/1M tokens. Cost-effective video with async tasks and unlimited concurrency. VAT invoices and corporate bank transfers.')
    source = re.sub(r'<title>.*?</title>', lambda _: f'<title>{esc(title)}</title>', source, count=1)
    source = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*', lambda m: m.group(1) + esc(desc), source)
    source = re.sub(r'(<meta (?:name|property)="(?:og:title|twitter:title)" content=")[^"]*', lambda m: m.group(1) + esc(title), source)
    source = source.replace('<body>', '<body class="sd-overview">' if overview else '<body class="sd-model-page">')
    if not overview:
        source = source.replace('data-scrollbar="light"', 'data-scrollbar="dark"')
        source = source.replace('</h1><p class="sd-lead">', f'</h1><p class="sd-price-line">{"最低" if zh else "From"} <strong>${price}</strong> / 1M tokens</p><p class="sd-lead">', 1)
    source = source.replace('href="/zh/models/' + slug + '" hreflang="zh"', 'href="/zh/models/' + slug + '" hreflang="zh-CN" lang="zh-CN"')
    source = source.replace('href="/en/models/' + slug + '" hreflang="en"', 'href="/en/models/' + slug + '" hreflang="en" lang="en"')
    source = source.replace('<ol class="o-crumbs">', f'<nav aria-label="{"面包屑" if zh else "Breadcrumb"}"><ol class="o-crumbs">').replace('</ol><div class="sd-hero-grid">', '</ol></nav><div class="sd-hero-grid">')
    source = source.replace('<header class="o-nav"><div', '<header class="o-nav"><div', 1).replace('<nav><ul>', f'<nav aria-label="{"主导航" if zh else "Main navigation"}"><ul>', 1)
    if not zh:
        source = source.replace('<li>模型名 ', '<li>Model ').replace('<li>计费 ', '<li>Billing ').replace('<li>接口 ', '<li>Endpoint ')
        source = source.replace(' / 1M tokens 起', ' / 1M tokens, from')
    source = source.replace('<h2>企业接入 ' + name + '</h2>', '<h2>企业接入 ' + name + ' API</h2>')
    source = source.replace('<h2>Enterprise access for ' + name + '</h2>', '<h2>' + name + ' API for teams and enterprises</h2>')
    # Give each model an editorial focus drawn from its official positioning.
    if slug == 'doubao-seedance-2-5':
        focused = [('30 秒长叙事', '单段最长 30 秒，兼顾叙事衔接、运动稳定性与画面真实感。'), ('精细参考与编辑', '从参考素材理解镜头语言，用 reference、edit 或 extend 明确任务意图。'), ('专业创作控制', '官方展示白模控制与绿幕编辑能力，适合复杂镜头和专业制作流程。'), ('可选输出格式', '通过 output_format 选择 mp4 或 mov，默认 mp4。')] if zh else [('30-second narratives', 'Create a single clip up to 30 seconds, with a focus on coherent stories, stable motion and realistic scenes.'), ('Precise references and edits', 'Guide shot language with references and specify reference, edit or extend as the task intent.'), ('Professional creative control', 'The official model page demonstrates white-model control and green-screen editing for production workflows.'), ('MP4 or MOV output', 'Choose mp4 or mov with output_format. The default format is mp4.')]
    elif slug == 'doubao-seedance-2-0-fast':
        focused = [('更快迭代', '延续 Seedance 2.0 的核心能力，侧重更快生成与创意迭代。'), ('素材参考', '文字与多模态素材可用于描述主体、动作和镜头方向。'), ('低成本试镜', '先试多个镜头和创意，再把选中的方案放入制作流程。'), ('异步批量流程', '保存任务 ID 后查询结果，适合接入自己的作业队列。')] if zh else [('Faster iteration', 'Retain the core Seedance 2.0 workflow with an emphasis on faster generation and creative iteration.'), ('Reference-led direction', 'Use prompts and multimodal material to describe subjects, motion and camera direction.'), ('Explore more concepts', 'Try multiple shots and concepts before committing a selected direction to production.'), ('Async batch workflows', 'Save task IDs and query the results from your own job queue.')]
    elif slug == 'doubao-seedance-2-0-mini':
        focused = [('高频视频生成', '面向更广泛的视频需求，适合持续生成短视频素材。'), ('更低使用门槛', '以模型广场的较低单价开展创意实验，按实际 tokens 消耗计费。'), ('规模化内容', '把视频任务集成到商品、内容与营销生产流程。'), ('统一任务接口', '沿用 Seedance 任务路径管理创建、查询和结果下载。')] if zh else [('High-frequency video', 'Designed for broader video needs and a steady flow of short-form material.'), ('Lower entry cost', 'Experiment at lower catalog rates, billed by actual token usage.'), ('Content at scale', 'Bring video jobs into product, content and marketing production workflows.'), ('One task endpoint', 'Use the Seedance task path to manage creation, querying and result downloads.')]
    else:
        focused = None
    if focused:
        cards = ''.join(f'<li class="sd-card"><span class="sd-card-no">{i+1:02d}</span><h3>{h}</h3><p>{p}</p></li>' for i,(h,p) in enumerate(focused))
        source = re.sub(r'<ul class="sd-cards">.*?</ul>', lambda _: '<ul class="sd-cards">' + cards + '</ul>', source, count=1, flags=re.S)
    # A visible overview navigation uses model names and real IDs, without subscription-style pricing cards.
    if overview:
        model_rows = ''.join(f'<li><span>{i+1:02d}</span><div><h3><a href="/{lang}/models/{s}">{m["name"]} ↗</a></h3><code>{m["id"]}</code></div><p>{m["desc_zh" if zh else "desc_en"]}</p></li>' for i,(s,m) in enumerate(MODELS.items()))
        model_block = '<section class="o-section" id="models"><div class="o-wrap"><h2>' + ('选择适合工作流的 Seedance' if zh else 'Choose a Seedance model for your workflow') + '</h2><ul class="sd-model-list">' + model_rows + '</ul></div></section>'
        source = source.replace('<section class="o-section" id="features">', model_block + '<section class="o-section" id="features">')
    source = source.replace('Skip to main content</a>', ('跳到主要内容' if zh else 'Skip to main content') + '</a>')
    # Full pricing table, with all offers mirrored into JSON-LD below.
    start = source.index('<div class="sd-table-wrap', source.index('id="pricing"'))
    end = source.index('<p class="o-note">', start)
    source = source[:start] + pricing_block(lang, slug) + source[end:]
    source = source.replace('以下是模型广场当前可见的最低档位，详情页列出每个型号的全部价格。', '表格列出各型号的最低接入价格，包含不同分辨率与参考视频输入档位。')
    source = source.replace('The table shows current catalog starting rates; each model page lists every tier.', 'The table lists the lowest catalog rate for each resolution and reference-video input tier.')
    # Add runnable Python using only the standard library.
    marker = '<p class="o-note">' + ('接口字段和返回结构以' if zh else 'Fields and response structure follow the ')
    py = f'<figure class="o-code"><figcaption><b>Python · {"创建与轮询（无需第三方库）" if zh else "Create and poll (standard library)"}</b><button class="o-copy" type="button" data-target="seedance-python">{"复制" if zh else "Copy"}</button></figcaption><pre id="seedance-python"><code>{esc(python_code(lang, slug))}</code></pre></figure>'
    source = source.replace(marker, py + marker, 1)
    source = source.replace(f'href="{DOC_QUERY}"', f'href="{query_doc}"')
    source = source.replace('# Save the returned id, then query the asynchronous task', '# 保存返回的 id，再查询异步任务' if zh else '# Save the returned id, then query the asynchronous task')
    source = source.replace('class="o-copy" data-target', 'class="o-copy" type="button" data-target')
    if slug == 'doubao-seedance-2-5':
        extra_note = ('2.5 支持 480p / 720p / 1080p，默认 720p；duration 为 4–30 或 -1。视频编辑、延长与首帧 / 首尾帧任务使用 ratio="adaptive"；编辑任务的 duration 为 -1。带参考视频且指定时长时，设置 omni_reference_task_type="reference"。' if zh else '2.5 supports 480p / 720p / 1080p (default 720p), with duration 4–30 or -1. Editing, extension and first / first-last frame tasks require ratio="adaptive"; editing requires duration=-1. For a reference video with a specified duration, set omni_reference_task_type="reference".')
        source = source.replace(py + marker, py + f'<p class="sd-callout">{extra_note}</p>' + marker)
    source = source.replace('<h2>快速开始</h2>', f'<h2>快速接入 {name} API</h2>').replace('<h2>Quick start</h2>', f'<h2>Get started with the {name} API</h2>')
    if slug == 'doubao-seedance-2-0-mini':
        note = ('mini 使用同样的 content[] 请求结构，model 填 doubao-seedance-2-0-mini-260615；每次任务生成 1 条视频，所有用户默认享有不限并发。' if zh else 'mini uses the same content[] request structure. Set model to doubao-seedance-2-0-mini-260615. Each task generates one video, with unlimited concurrency by default for every user.')
        source = source.replace('<ol class="o-steps">', f'<p class="sd-callout">{note}</p><ol class="o-steps">', 1)
    if overview or slug == 'doubao-seedance-2-0':
        note = ('Seedance 2.0 的 4K 档位当前可调用：不含参考视频 $4.860、含参考视频 $2.916 / 1M tokens。' if zh else 'The Seedance 2.0 4K tier is available now: $4.860 without reference video or $2.916 with reference video, per 1M tokens.')
        price_end = source.index('<div class="o-price-cta">', source.index('id="pricing"'))
        source = source[:price_end] + f'<p class="o-note">{note}</p>' + source[price_end:]
    # Add common platform benefits without claiming per-model benchmark results.
    benefits = [('一个 Key，300+ 模型', '视频、图像、对话模型共用 API Key 和余额。'), ('国内直连', '通过 https://anyaigc.ai 接入，无需切换多个厂商账户。'), ('公开价格，并发不限', '单价公开，按实际 tokens 计费，所有用户默认享有不限并发。')] if zh else [('One key, 300+ models', 'Video, image and chat models share one API key and balance.'), ('Direct access in China', 'Connect through https://anyaigc.ai with one provider account.'), ('Published rates, unlimited concurrency', 'Clear per-token rates and unlimited concurrency by default for every user.')]
    block = '<section class="o-section" id="platform"><div class="o-wrap"><h2>' + ('在 AnyAIGC 接入 Seedance' if zh else 'Access Seedance through AnyAIGC') + '</h2><ul class="sd-uses">' + ''.join(f'<li><h3>{h}</h3><p>{p}</p></li>' for h,p in benefits) + '</ul></div></section>'
    source = source.replace('<section class="o-section sd-band" id="quickstart">', block + '<section class="o-section sd-band" id="quickstart">')
    # Link every member back to the overview, including in its family list.
    overview_link = f'<li><a href="/{lang}/models/seedance"' + (' aria-current="page"' if overview else '') + f'><b>{"Seedance 全系总览" if zh else "Seedance overview"}</b><span>{"四个型号的价格与选型" if zh else "Pricing and model selection"}</span></a></li>'
    source = source.replace('<ul class="o-family">', '<ul class="o-family">' + overview_link)
    related = f'<ul class="sd-related"><li><a href="/{lang}/models/">{"全部模型专题" if zh else "All model guides"}</a></li><li><a href="{PRICING}">{"模型广场" if zh else "Model catalog"}</a></li><li><a href="{doc}">{"接口文档" if zh else "API docs"}</a></li><li><a href="/{"en" if zh else "zh"}/models/{slug}" hreflang="{"en" if zh else "zh-CN"}">{"English" if zh else "中文版"}</a></li></ul>'
    source = source.replace('</div></section></main>', related + '</div></section></main>')
    license_note = '视频使用权与商用授权以字节跳动 / Seed 官方条款为准。' if zh else 'Video usage rights and commercial licensing follow ByteDance / Seed official terms.'
    source = source.replace('</p></div></footer>', f'</p><p>{license_note}</p></div></footer>')
    source_links = f'<p class="o-note">{"资料来源：" if zh else "Sources: "}<a href="https://seed.bytedance.com/zh/seedance2_0" target="_blank" rel="noopener">Seedance 2.0</a> · <a href="https://seed.bytedance.com/zh/seedance2_5" target="_blank" rel="noopener">Seedance 2.5</a> · <a href="{PRICING}?keyword=seedance" target="_blank" rel="noopener">{"AnyAIGC 模型广场" if zh else "AnyAIGC model catalog"}</a> ({DATE})</p>'
    features_end = source.index('</section>', source.index('id="features"'))
    wrap_end = source.rfind('</div>', source.index('id="features"'), features_end)
    source = source[:wrap_end] + source_links + source[wrap_end:]
    source = source.replace('支持普票和专票。', '按实际充值金额开具增值税普通发票（普票）或增值税专用发票（专票）。')
    source = source.replace('Unused balance can be refunded.', 'Unused balance can be refunded with no fee.')
    source = source.replace('未使用余额可申请退款。', '未使用余额可申请退款，不收手续费。')
    source = source.replace('除法律法规要求外，不持久化存储输入输出。', '除法律法规要求外，不持久化存储输入输出，也不用于训练。详见<a href="/privacy">隐私政策</a>。')
    source = source.replace('Unless required by law, prompts and outputs are not persistently stored.', 'Unless required by law, prompts and outputs are not persistently stored or used for training. See the <a href="/privacy">privacy policy</a>.')
    import trust
    source = re.sub(r'<section class="o-section" id="trust">.*?</section>', lambda _: '\n' + trust.section(lang, 'o'), source, count=1, flags=re.S)
    # Use exact documented prices and exact visible FAQ text in structured data.
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)
    data = json.loads(match.group(1))
    picked = list(MODELS) if overview else [slug]
    offers = [{'@type': 'Offer', 'name': f'{MODELS[s]["name"]} · {res} · {mode} / 1M tokens', 'price': price, 'priceCurrency': 'USD'} for s in picked for res,mode,price in MODELS[s]['rows' if zh else 'rows_en']]
    for node in data['@graph']:
        if node['@type'] == 'WebPage':
            node.update(name=title, description=desc, isPartOf={'@id': SITE+'/#website'}, breadcrumb={'@id': f'{SITE}/{lang}/models/{slug}#breadcrumb'})
        if node['@type'] == 'Product':
            node['description'] = desc
            node['offers'].update(offers=offers, offerCount=len(offers), lowPrice=min((x['price'] for x in offers), key=Decimal), highPrice=max((x['price'] for x in offers), key=Decimal))
        if node['@type'] == 'FAQPage':
            # Read the rendered FAQ source after localized adjustments so the schema always matches.
            faq_source = re.search(r'id="faq".*?</section>', source, re.S).group(0)
            visible = re.findall(r'<details[^>]*><summary><h3>(.*?)</h3></summary><div class="o-ans"><p>(.*?)</p>', faq_source, re.S)
            node['mainEntity'] = [{'@type': 'Question', 'name': html.unescape(q), 'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(re.sub(r'<[^>]+>', '', a))}} for q,a in visible]
    source = source[:match.start(1)] + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + source[match.end(1):]
    # Newlines make generated pages reviewable while preserving code whitespace.
    return re.sub(r'>(?=<(?:!?/?[a-zA-Z]))', '>\n', source) + '\n'


def main():
    for lang in ('zh','en'):
        for slug in SLUGS:
            io.open(os.path.join(ROOT,lang,'models',slug+'.html'),'w',encoding='utf-8',newline='\n').write(page(lang,slug))
    print('written seedance pages')

if __name__=='__main__': main()
