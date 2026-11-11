"""Generate the bilingual Llama overview and 12 model guides. No build needed."""
import json
import re
from decimal import Decimal
from html import escape as e
from pathlib import Path

from llama_data import BY_ID, DATE, DOC, MODELS, PRICING, REGISTER, SLUGS, VERSION
from payments import A as PAY_A, Q as PAY_Q, pay_row
from trust import FAQ as TRUST_FAQ, HEAD as TRUST_HEAD, ITEMS as TRUST_ITEMS

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://www.anyaigc.ai'
SUPPORT = 'https://anyaigc.ai/customersupport'


def mark(size=48, color='#171717', cls='ll-mark'):
    from icons import svg
    return svg('ollama', cls=cls, size=size, fill=color)


def discount(model=None):
    return model is None or model['id'] != 'llama-3.3-70b-instruct'


def deal(lang, model=None):
    if not discount(model):
        return '按量计费' if lang == 'zh' else 'Pay as you go'
    return ('部分型号 68 折' if model is None else '68 折 · 省 32%') if lang == 'zh' else ('Save 32% on selected models' if model is None else 'Save 32%')


def button(text, url=REGISTER, secondary=False):
    return f'<a class="ll-btn ll-{"secondary" if secondary else "primary"}" href="{e(url)}">{e(text)} <span aria-hidden="true">↗</span></a>'


def section(identifier, title, lead, content, soft=False):
    return f'<section class="ll-section{" ll-soft" if soft else ""}" id="{identifier}" aria-labelledby="{identifier}-title"><div class="ll-wrap">\n<h2 id="{identifier}-title">{e(title)}</h2><p class="ll-lead">{e(lead)}</p>\n{content}\n</div></section>\n'


def features(items, extra=''):
    return '<div class="ll-grid ' + extra + '">' + ''.join(f'<article class="ll-feature"><span class="ll-number">0{i}</span><h3>{e(t)}</h3><p>{e(d)}</p></article>' for i, (t, d) in enumerate(items, 1)) + '</div>'


def faq(lang, model):
    zh = lang == 'zh'
    name = model['name'] if model else 'Llama'
    if zh:
        price = (f'输入 ${model["input"]}，输出 ${model["output"]}，均为每百万 tokens 的美元单价。' if model else '12 个型号分别按输入和输出 tokens 计费。Llama 3.2 1B Instruct 输入 $0.3375、输出 $0.0844/百万 tokens。')
        price += ('标有优惠的型号为 68 折（模型广场显示省 32%），表内已是优惠后价格，无需再次打折。' if discount(model) else '该型号当前未显示 68 折优惠标记。') + '实时价格以模型广场为准。'
        result = [
            (f'{name} API 多少钱？68 折如何计算？' if discount(model) else f'{name} API 多少钱？', price),
            ('Llama 和 Ollama 是什么关系？支持哪些版本？', 'Llama 是 Meta 开发的模型系列；Ollama 是模型运行工具，也是 AnyAIGC 模型广场的供应商分类。本专题收录 Llama 2、3、3.1、3.2 和 3.3 共 12 个型号。商用授权以 Meta 官方条款为准。'),
            ('应该填写哪个模型名？一次调用返回什么？', f'使用 POST /v1/chat/completions，model 填写 {model["id"] if model else "llama-3.3-70b-instruct 等完整型号"}，通过 Bearer API Key 鉴权。本页示例设置 n=1、stream=false，返回一个助手回复候选和 token 用量信息；llama 是专题总览名。'),
            ('并发和 RPM 有限制吗？需要安装 Ollama 吗？', '所有用户默认并发不限，无固定 RPM 上限。通过 AnyAIGC 云端 API 调用，无需在本地安装 Ollama 或部署模型。应用仍应处理网络超时和接口错误。'),
            ('可以处理图片和中文吗？', 'Llama 3.2 的 11B/90B Vision Instruct 是视觉型号，其余型号为文本模型。Llama 3.1–3.3 官方支持的文本语言列表未包含中文；图文任务官方支持英语。中文任务请先用实际数据评估，本页只展示文本接入示例。'),
            ('AnyAIGC 能开发票吗？支持增值税专票吗？', '支持。按实际充值金额开具增值税普通发票和增值税专用发票，可联系企业客服办理。'),
            ('企业可以对公转账和签合同吗？', '可以。支持企业对公转账充值、签订服务合同，并提供专属客服与技术对接。'),
        ]
    else:
        price = (f'Input is ${model["input"]} and output is ${model["output"]} per million tokens, in USD. ' if model else 'Each of the 12 models has separate input and output rates. Llama 3.2 1B Instruct costs $0.3375 for input and $0.0844 for output per million tokens. ')
        price += ('Models marked with the offer save 32% as displayed in the marketplace. Listed rates already include the discount; do not apply it again. ' if discount(model) else 'This model currently has no 32% discount badge. ') + 'Check the marketplace for current rates.'
        result = [
            (f'How much does {name} API cost?', price),
            ('How are Llama and Ollama related? Which versions are listed?', 'Meta develops the Llama model family. Ollama is a model runtime and the provider category used in the AnyAIGC marketplace. These guides cover 12 models across Llama 2, 3, 3.1, 3.2 and 3.3. Commercial use is subject to Meta’s official terms.'),
            ('Which model ID do I send, and what does a request return?', f'Use POST /v1/chat/completions with {model["id"] if model else "an exact ID such as llama-3.3-70b-instruct"} and Bearer API key authentication. The examples set n=1 and stream=false to return one assistant reply candidate and token usage. The name llama is used for this overview.'),
            ('Are concurrency or RPM limited? Do I need to install Ollama?', 'All users have unlimited concurrency and no fixed RPM cap by default. Call the AnyAIGC cloud API without installing Ollama or deploying the model locally. Your application should still handle network timeouts and API errors.'),
            ('Which models accept images? What about language support?', 'The 11B and 90B Llama 3.2 Vision Instruct models are vision models; the other listed models are text models. Llama 3.1–3.3 officially support eight text languages, excluding Chinese. Image-text tasks officially support English. Evaluate other languages on your own data; these examples demonstrate text requests.'),
            ('Can AnyAIGC issue invoices, including VAT special invoices?', 'Yes. AnyAIGC issues Chinese VAT general and special invoices based on the actual top-up amount. Contact the enterprise support team to arrange invoicing.'),
            ('Can my company pay by bank transfer and sign a contract?', 'Yes. Corporate bank transfer, service contracts, dedicated support and a technical contact are available.'),
        ]
    return result + [(PAY_Q[lang], PAY_A[lang])] + TRUST_FAQ[lang]


def prices(lang, models, overview):
    zh = lang == 'zh'
    body = ''
    for model in models:
        label = ' <span class="ll-price-badge">' + deal(lang, model) + '</span>' if discount(model) else ''
        head = f'<a href="/{lang}/models/{model["id"]}">{e(model["name"])}</a>' if overview else e(model['name'])
        body += f'<tbody><tr class="ll-table-model"><th colspan="3">{head}{label}</th></tr>'
        for key, title in [('input', '输入' if zh else 'Input'), ('output', '输出' if zh else 'Output')]:
            body += f'<tr><th scope="row">{title}</th><td><code>{model["id"]}</code></td><td><strong>${model[key]}</strong><small>/ {"百万 tokens" if zh else "1M tokens"}</small></td></tr>'
        body += '</tbody>'
    return '<div class="ll-table-wrap"><table class="ll-table"><caption>' + ('Llama API 单价 · USD / 百万 tokens' if zh else 'Llama API rates · USD / 1M tokens') + '</caption><thead><tr>' + ''.join('<th scope="col">' + t + '</th>' for t in (['功能', '模型名', '单价（USD）'] if zh else ['Usage', 'Model ID', 'Price (USD)'])) + '</tr></thead>' + body + '</table></div>'


def costs(lang, model):
    zh = lang == 'zh'
    items = []
    for amount, out in [('1', '0.25'), ('10', '2.5')]:
        total = Decimal(amount) * Decimal(model['input']) + Decimal(out) * Decimal(model['output'])
        price = format(total, 'f').rstrip('0').rstrip('.')
        title = f'{amount}M ' + ('输入' if zh else 'input') + f' + {out}M ' + ('输出' if zh else 'output')
        items.append(f'<article class="ll-cost"><h3>{title}</h3><p>{e(model["name"])}</p><p><code>{amount} × ${model["input"]} + {out} × ${model["output"]}</code></p><strong>${price}</strong><p>{"按多次成功请求的累计用量估算。" if zh else "Estimated across multiple successful requests."}</p></article>')
    return '<div class="ll-costs">' + ''.join(items) + '</div>'


def code_examples(lang, model):
    zh = lang == 'zh'
    prompt = '请用三句话解释什么是 API。' if zh else 'Explain what an API is in three sentences.'
    payload = {'model': model['id'], 'messages': [{'role': 'user', 'content': prompt}], 'n': 1, 'stream': False}
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    curl = 'curl --request POST "https://anyaigc.ai/v1/chat/completions" \\\n  --header "Authorization: Bearer $ANYAIGC_API_KEY" \\\n  --header "Content-Type: application/json" \\\n  --data \'' + body + "'"
    python = '''import json
import os
import urllib.request

payload = PAYLOAD
request = urllib.request.Request(
    "https://anyaigc.ai/v1/chat/completions",
    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    headers={
        "Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"],
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(request, timeout=120) as response:
    result = json.load(response)

print(json.dumps(result, ensure_ascii=False, indent=2))'''.replace('PAYLOAD', body.replace('false', 'False'))
    tabs = '<div class="ll-tabs" role="tablist" aria-label="' + ('代码语言' if zh else 'Code language') + '">'
    panels = ''
    for i, (name, code) in enumerate([('cURL', curl), ('Python', python)]):
        tabs += f'<button type="button" role="tab" id="ll-tab-{i}" aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}" aria-controls="ll-panel-{i}">{name}</button>'
        panels += f'<div class="ll-code" role="tabpanel" id="ll-panel-{i}" aria-labelledby="ll-tab-{i}"{ " hidden" if i else ""}><div class="ll-code-head"><span>{name}</span><button class="ll-copy" type="button" data-copy="ll-code-{i}" aria-live="polite">{"复制" if zh else "Copy"}</button></div><pre><code id="ll-code-{i}">{e(code)}</code></pre></div>'
    return tabs + '</div>' + panels


def head(lang, slug, name, title, desc, models, questions):
    zh = lang == 'zh'
    url = f'{SITE}/{lang}/models/{slug}'
    og = f'{SITE}/assets/og/{slug}-{lang}.png'
    crumbs = [{'@type':'ListItem','position':1,'name':'首页' if zh else 'Home','item':SITE + '/'}, {'@type':'ListItem','position':2,'name':'模型专题' if zh else 'Model guides','item':f'{SITE}/{lang}/models/'}]
    if slug != 'llama':
        crumbs.append({'@type':'ListItem','position':3,'name':'Llama','item':f'{SITE}/{lang}/models/llama'})
    crumbs.append({'@type':'ListItem','position':len(crumbs)+1,'name':name,'item':url})
    offers = [{'@type':'Offer', 'name':m['id'] + ' ' + ('输入' if zh else 'input') if k == 'input' else m['id'] + ' ' + ('输出' if zh else 'output'), 'price':m[k], 'priceCurrency':'USD', 'url':url + '#pricing', 'priceSpecification':{'@type':'UnitPriceSpecification','price':m[k],'priceCurrency':'USD','unitText':'1M tokens'}} for m in models for k in ('input','output')]
    amounts = [o['price'] for o in offers]
    graph = {'@context':'https://schema.org','@graph':[
        {'@type':'Organization','@id':SITE+'/#org','name':'AnyAIGC','url':SITE,'logo':SITE+'/logo.webp'},
        {'@type':'WebSite','@id':SITE+'/#website','name':'AnyAIGC','url':SITE+'/','publisher':{'@id':SITE+'/#org'}},
        {'@type':'WebPage','@id':url+'#webpage','name':title,'url':url,'description':desc,'inLanguage':'zh-CN' if zh else 'en','dateModified':DATE,'isPartOf':{'@id':SITE+'/#website'},'breadcrumb':{'@id':url+'#breadcrumb'}},
        {'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':crumbs},
        {'@type':'Product','@id':url+'#product','name':name+' API (AnyAIGC)','description':desc,'image':og,'brand':{'@type':'Brand','name':'Meta Llama'},'offers':{'@type':'AggregateOffer','priceCurrency':'USD','lowPrice':min(amounts,key=Decimal),'highPrice':max(amounts,key=Decimal),'offerCount':len(offers),'offers':offers}},
        {'@type':'FAQPage','@id':url+'#faq','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in questions]},
    ]}
    tags = [('name','description',desc),('name','keywords',name+' API, '+name+(' API 价格, Llama API 企业, Llama API 发票' if zh else ' API pricing, Llama API for business')),('name','robots','index,follow,max-image-preview:large'),('name','theme-color','#ffffff'),('property','og:type','website'),('property','og:site_name','AnyAIGC'),('property','og:locale','zh_CN' if zh else 'en_US'),('property','og:locale:alternate','en_US' if zh else 'zh_CN'),('property','og:url',url),('property','og:title',title),('property','og:description',desc),('property','og:image',og),('property','og:image:width','1200'),('property','og:image:height','630'),('property','og:image:alt',name+' API · AnyAIGC'),('name','twitter:card','summary_large_image'),('name','twitter:title',title),('name','twitter:description',desc),('name','twitter:image',og)]
    out = f'<!DOCTYPE html>\n<html lang="{"zh-CN" if zh else "en"}">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{e(title)}</title>\n'
    out += '\n'.join(f'<meta {attr}="{key}" content="{e(value)}">' for attr,key,value in tags)
    out += f'\n<link rel="canonical" href="{url}">\n'
    out += '\n'.join(f'<link rel="alternate" hreflang="{code}" href="{SITE}/{folder}/models/{slug}">' for code,folder in [('zh-CN','zh'),('en','en'),('x-default','en')])
    return out + f'\n<link rel="icon" href="/favicon.ico">\n<link rel="stylesheet" href="/assets/models/scrollbar.css?v={VERSION}">\n<link rel="stylesheet" href="/assets/models/llama.css?v={VERSION}">\n<script type="application/ld+json">\n' + json.dumps(graph,ensure_ascii=False,indent=2) + '\n</script>\n</head>\n'


def page(lang, slug):
    zh = lang == 'zh'
    def t(cn, en): return cn if zh else en
    model = BY_ID.get(slug)
    name = model['name'] if model else 'Llama'
    models = [model] if model else MODELS
    example = model or MODELS[0]
    start = model['input'] if model else '0.3375'
    title = name + ((' API 价格与接入｜68折 - AnyAIGC' if discount(model) else ' API 价格与接入 - AnyAIGC') if zh else (' API Pricing & Access - AnyAIGC'))
    # Keep long vision names inside the Chinese title display-width limit.
    if len(title) + sum(ord(c)>0x2e7f for c in title) > 64 and zh:
        title = name + ' API 价格｜68折 - AnyAIGC'
    desc = t(f'{name} API 输入 ${start}/百万 tokens 起，提供对话与文本生成接入、完整价格表和代码示例。'+('部分型号68折，' if not model else ('68折，' if discount(model) else ''))+'并发不限，支持对公转账、合同与增值税专票。', f'{name} API from ${start}/1M input tokens. Chat, code examples, unlimited concurrency, no fixed RPM cap and VAT invoices.')
    if not zh and model is None:
        desc = 'Llama API from $0.3375/1M input tokens. Explore 12 models, save 32% on selected models, with unlimited concurrency and VAT invoices.'
    questions = faq(lang, model)
    html = head(lang,slug,name,title,desc,models,questions)
    other = 'en' if zh else 'zh'
    nav = [(f'/{lang}/models/',t('模型专题','Models')),(PRICING,t('模型广场','Marketplace')),('#pricing',t('价格','Pricing')),('#enterprise',t('企业接入','Enterprise')),(DOC,t('API 文档','API docs')),(f'/{other}/models/{slug}',t('English','中文')),('https://anyaigc.ai/console',t('登录','Log in'))]
    html += f'<body><a class="ll-skip" href="#main">{t("跳至内容","Skip to content")}</a><header class="ll-header"><nav class="ll-nav" aria-label="{t("主导航","Main navigation")}"><a class="ll-brand" href="/">AnyAIGC<span>× Llama</span></a><button class="ll-menu" type="button" aria-controls="ll-links" aria-expanded="false">{t("菜单","Menu")}</button><div class="ll-links" id="ll-links">'
    html += ''.join(f'<a href="{e(url)}"'+(f' hreflang="{"en" if zh else "zh-CN"}"' if url.startswith('/'+other+'/') else '')+f'>{label}</a>' for url,label in nav) + button(t('获取 API Key','Get API key')) + '</div></nav></header>\n<main id="main">'
    html += f'<div class="ll-wrap"><nav class="ll-breadcrumb" aria-label="{t("面包屑","Breadcrumb")}"><a href="/">{t("首页","Home")}</a><span>/</span><a href="/{lang}/models/">{t("模型专题","Model guides")}</a><span>/</span>'
    if model:
        html += f'<a href="/{lang}/models/llama">Llama</a><span>/</span>'
    html += f'<span aria-current="page">{e(name)}</span></nav></div>\n'
    tagline = model['tag_'+lang] if model else t('开放模型，简单接入。','Open models. One simple API.')
    intro = model['desc_'+lang] if model else t('从轻量文本到视觉问答，选择适合任务的 Llama。一个 API Key，接入 Llama 2、3、3.1、3.2 和 3.3 共 12 个型号。','From compact text models to visual question answering, choose the Llama for your task. One API key covers 12 models across Llama 2, 3, 3.1, 3.2 and 3.3.')
    html += '<section class="ll-hero"><div class="ll-wrap">' + mark(74,cls='ll-hero-mark') + '<p class="ll-eyebrow">META LLAMA · OLLAMA COLLECTION</p>' + f'<h1>{e(name)} API</h1><p class="ll-tagline">{e(tagline)}</p><p class="ll-intro">{e(intro)}</p><p class="ll-intro">{t("输入", "Input from")} <strong>${start}</strong> / {t("百万 tokens 起", "1M tokens")}</p>'
    html += '<div class="ll-actions">'+button(t('获取 API Key','Get API key'))+button(t('查看价格','Explore pricing'),'#pricing',True)+'</div><ul class="ll-chips">'
    for i,chip in enumerate([deal(lang,model), 'OpenAI '+t('兼容','compatible'),t('并发不限','Unlimited concurrency'),t('对公 · 专票','Contracts · invoices')]):
        html += f'<li{ " class=\"ll-deal\"" if i == 0 else ""}>{chip}</li>'
    html += f'</ul><div class="ll-command"><code><span>$ </span>model: "{example["id"]}"</code><span>POST /v1/chat/completions</span></div></div></section>\n'
    html += '<div class="ll-wrap"><div class="ll-stats">'+''.join(f'<div><b>{a}</b><span>{b}</span></div>' for a,b in [('12',t('个 Llama 型号','Llama models')),('300+',t('模型共用一个 Key','models, one API key')),('USD',t('按 tokens 计费','token-based billing'))])+'</div></div>\n'
    items = [(t('对话与文本生成','Conversation and text'),t('将历史消息放进 messages，让模型围绕上下文生成回复、摘要与草稿。','Send conversation history in messages to generate replies, summaries and drafts.')),(t('按任务选择规模','Choose the right size'),t('从 1B、3B 到 70B、405B，使用真实任务比较结果，再选择合适型号。','Compare compact 1B and 3B models with 70B and 405B options on your actual tasks.')),(t('图文理解','Image-text understanding'),t('Llama 3.2 Vision Instruct 提供 11B 与 90B 两种视觉型号，面向图片描述和视觉问答。','Llama 3.2 Vision Instruct offers 11B and 90B variants for image descriptions and visual questions.'))]
    if model:
        items[1] = (name,model['desc_'+lang])
        if 'vision' not in slug:
            items[2] = (t('与现有应用对接','Connect to your application'),t('通过标准 HTTP 请求调用，将文本回复接入你的内容、客服或知识处理流程。','Use standard HTTP requests to bring text replies into content, support or knowledge workflows.'))
    source = 'https://ollama.com/library/' + (model['source'] if model else 'llama3.3')
    html += section('features',t('用 Llama 处理你的下一项任务','Build your next workflow with Llama'),t('模型由 Meta 开发；Ollama 是模型运行工具及本页采用的广场分类。','Llama is developed by Meta. Ollama is the runtime and marketplace category used here.'),features(items)+f'<p class="ll-source"><a href="{source}">{t("查看模型说明", "Read the model card")} ↗</a></p>')
    price_copy = t('已按模型广场的最低展示单价列出；输入与输出分别计费。','The lowest displayed marketplace rates are listed below. Input and output are billed separately.')
    highlight = ''
    if discount(model):
        highlight = '<div class="ll-highlight"><strong>'+t('68 折','32% off')+'</strong><p><b>'+t('部分型号省 32%' if not model else '该型号省 32%', 'Selected models save 32%' if not model else 'Save 32% on this model')+'</b>'+t('优惠依据模型广场标记，表格展示优惠后单价，无需再乘折扣。Llama 3.3 70B Instruct 当前未标注此优惠。' if not model else '优惠依据模型广场标记，以下已经是优惠后单价，无需再次乘以折扣。','Based on the marketplace offer badge. Rates below already include the discount. Llama 3.3 70B Instruct is not currently marked with this offer.' if not model else 'Based on the marketplace offer badge. The rates below already include the discount.')+'</p></div>'
    billing = [t('按输入 / 输出 tokens 计费','Pay per input / output token'),t('示例一次返回 1 个回复','One reply in the examples'),t('默认并发不限 · 无固定 RPM 上限','Unlimited concurrency · no fixed RPM cap'),t('账户余额通用','Shared account balance')]
    price_content = highlight + '<ul class="ll-billing">'+''.join(f'<li>{b}</li>' for b in billing)+'</ul>'+prices(lang,models,not model)
    price_content += '<p class="ll-note">'+t('单位 USD，按成功提交计费，按实际输入与输出 tokens 结算；实时价格以模型广场为准。核对日期：2026-11-11。','All rates are in USD. Successfully submitted requests are billed by actual input and output tokens. Current marketplace prices prevail. Checked November 11, 2026.')+'</p>'+costs(lang,model or BY_ID['llama-3.2-1b-instruct'])+'<div class="ll-actions">'+button(t('获取 API Key','Get API key'))+f'<a href="{PRICING}">{t("在模型广场查看", "View in marketplace")} ↗</a></div>'
    html += section('pricing',name+t(' API 价格',' API pricing'),price_copy,price_content,True)
    use = [(t('内容工作流','Content workflows'),t('根据提供的资料生成摘要、改写或文案初稿，再由业务流程校对发布。','Turn supplied material into summaries, rewrites and first drafts, then review them in your publishing workflow.')),(t('知识问答','Knowledge Q&A'),t('将检索到的片段与问题一并传入，由应用管理资料来源与上下文。','Pass retrieved passages alongside a question. Your application controls the sources and conversation context.')),(t('版本评估','Model evaluations'),t('用同一组提示词比较不同型号的输出和 token 成本，为迁移选型提供依据。','Compare outputs and token costs across versions using the same prompts before choosing or migrating models.'))]
    html += section('use-cases',t('从具体场景开始','Start with a real use case'),t('接入后，用你的业务数据验证模型是否适合。','Evaluate each model on the work your application actually needs to do.'),features(use))
    html += section('platform',t('一个 Key，连接你的模型工具箱','One API key for your model toolkit'),t('在 AnyAIGC 统一管理接入、用量与账单。','Manage access, usage and billing in AnyAIGC.'),features([(t('300+ 模型','300+ models'),t('对话、图像、视频与语音模型共用 API Key 和账户余额。','Use the same API key and balance for chat, image, video and audio models.')),(t('国内直连 · 并发不限','Direct access · unlimited concurrency'),t('通过 AnyAIGC 域名直接调用，Llama 接入并发不限。','Connect directly through AnyAIGC with unlimited concurrency for Llama.')),(t('单价明确 · 用量可查','Clear rates · visible usage'),t('按表中单价计费，在控制台查看每次调用的 tokens 与扣费。','Pay the listed rates and inspect tokens and charges for each request in the console.'))]),True)
    steps = [t('注册 AnyAIGC，在控制台创建 API Key。','Create an AnyAIGC account and API key in the console.'),t('将 Key 保存到 ANYAIGC_API_KEY 环境变量。','Set the ANYAIGC_API_KEY environment variable.'),t('复制完整模型名，发送一条消息开始调用。','Send a message with the exact model ID.')]
    quick = '<ol class="ll-steps">'+''.join(f'<li><b>0{i}</b>{step}</li>' for i,step in enumerate(steps,1))+'</ol><div class="ll-api"><code>POST https://anyaigc.ai/v1/chat/completions</code><a href="'+DOC+'">'+t('阅读接入文档','Read the API reference')+' ↗</a></div>'+code_examples(lang,example)
    quick += '<p class="ll-note">'+t('cURL 示例适用于 Bash / zsh；Python 示例仅依赖标准库。n=1 返回一个候选回复，stream=false 返回完整 JSON；响应包含 choices 和 usage。可将 stream 改为 true 接收 SSE 增量输出。','The cURL example uses Bash / zsh syntax; Python uses only the standard library. With n=1 and stream=false, the response contains one reply candidate in choices plus usage. Set stream=true for SSE output.')+'</p>'
    html += section('quickstart',t('接入 ', 'Connect to ')+name+' API',t('无需本地部署。先完成一个文本请求，再接入应用。','No local deployment required. Start with one text request, then connect your application.'),quick)
    ent = [(t('增值税发票','Invoices'),t('按实际充值金额开具增值税普通发票与专用发票，普票、专票都支持。','Chinese VAT general and special invoices for the actual top-up amount.')),(t('对公转账','Bank transfer'),t('支持企业使用对公转账充值，配合财务支付流程。','Pay through corporate bank transfer to fit your finance process.')),(t('签订合同','Contracts'),t('可签订服务合同，满足企业采购与法务流程。','Service contracts are available for procurement and legal review.')),(t('专属对接','Dedicated support'),t('提供专属客服与技术对接，协助 API 集成。','Dedicated support and a technical contact for your integration.'))]
    html += section('enterprise',t('企业接入 '+name+' API',name+' API for teams and enterprises'),t('让研发、财务与采购一起完成接入。','Bring engineering, finance and procurement into one integration process.'),features(ent,'ll-enterprise')+pay_row(lang,'ll')+'<div class="ll-actions">'+button(t('联系企业客服','Talk to sales'),SUPPORT)+button(t('先注册试用','Start with a free account'),secondary=True)+'</div>',True)
    trust = '<ul class="trust-list">'+''.join(f'<li><h3>{title}</h3><p>{text}</p></li>' for title,text in TRUST_ITEMS[lang])+'</ul><div class="ll-actions">'+button(t('先注册领取 200 万 tokens','Sign up for 2M free tokens'))+'</div>'
    html += section('trust',*TRUST_HEAD[lang],trust)
    family = '<div class="ll-family">'
    for member in SLUGS:
        item = BY_ID.get(member)
        label = item['name'] if item else t('Llama 全系总览','Llama overview')
        hint = deal(lang,item) if item else t('12 个型号 · 价格与接入','12 models · pricing and access')
        family += f'<a href="/{lang}/models/{member}"'+(' aria-current="page"' if member==slug else '')+f'><span>{e(label)}</span><small>{e(hint)}</small></a>'
    html += section('family',t('同系列 Llama 模型','Explore the Llama family'),t('保留相同的接口结构，按任务选择模型。','Keep the same API structure and choose a model for your task.'),family+'</div>',True)
    html += section('faq',name+t(' API 常见问题',' API FAQ'),t('价格、版本、接入与企业采购。','Pricing, versions, integration and enterprise purchasing.'),'<div class="ll-faq">'+''.join(f'<details><summary><h3>{e(q)}</h3></summary><div class="ll-answer"><p>{e(a)}</p></div></details>' for q,a in questions)+'</div>')
    html += '<section class="ll-final"><div class="ll-wrap">'+mark(52,'#ffffff')+f'<h2>{t("让下一个想法，用上 Llama。","Put Llama behind your next idea.")}</h2><p>{t("从一个 API Key 开始，按实际用量付费。","Start with one API key. Pay for what you use.")}</p><div class="ll-actions">'+button(t('获取 API Key','Get API key'))+'</div><div class="ll-final-links">'+f'<a href="/{lang}/models/">{t("全部模型专题","All model guides")}</a><a href="{PRICING}">{t("模型广场","Marketplace")}</a><a href="{DOC}">API {t("文档","reference")}</a><a href="/{other}/models/{slug}" hreflang="{"en" if zh else "zh-CN"}">{t("English 版本","中文版")}</a></div></div></section></main>\n'
    html += '<footer class="ll-footer"><div class="ll-wrap"><div class="ll-footer-top"><a class="ll-brand" href="/">AnyAIGC<span>× Llama</span></a><nav aria-label="'+t('页脚','Footer')+'">'+f'<a href="/{lang}/models/">{t("模型专题","Model guides")}</a><a href="https://anyaigc.ai/console">{t("控制台","Console")}</a><a href="/privacy">{t("隐私政策","Privacy")}</a><a href="/terms">{t("服务条款","Terms")}</a></nav></div><p>'+t('Llama 是 Meta 的商标，Ollama 是其各自权利人的商标。AnyAIGC 是独立 API 服务商，与 Meta 或 Ollama 无隶属关系。模型与输出的商用授权以 Meta 官方条款为准。','Llama is a trademark of Meta. Ollama is a trademark of its respective owner. AnyAIGC is an independent API provider and is not affiliated with Meta or Ollama. Commercial use of the models and outputs is subject to Meta’s official terms.')+'</p></div></footer>\n'+f'<script src="/assets/models/llama.js?v={VERSION}" defer></script>\n</body>\n</html>\n'
    return html


if __name__ == '__main__':
    for language in ('zh','en'):
        for slug in SLUGS:
            path = ROOT / language / 'models' / (slug+'.html')
            path.write_text(page(language,slug),encoding='utf-8',newline='\n')
            print(path.relative_to(ROOT))
