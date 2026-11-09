"""Render verified media details into the bilingual media-page shell."""
import html
import json
import re
from decimal import Decimal
from qwen_media_data import (MODELS, IMG, VID, BY_SLUG, DATE, VERSION, SITE, REG,
                             MARKET, SUPPORT, VIDEO_ENDPOINT, UNITS, price_label,
                             display_currency, display_amount, money)
from trust import ITEMS as TRUST_ITEMS


def t(lang,zh,en): return zh if lang=='zh' else en
def e(value): return html.escape(str(value),quote=True)
def text(value): return html.unescape(re.sub('<[^>]+>','',value))
def replace_section(s,sid,value):
    return re.sub(r'<section\b[^>]* id="'+sid+r'"[^>]*>.*?</section>',lambda _:value,s,count=1,flags=re.S)


def has_saving(rate):
    return Decimal(str(rate.get('saving') or '0')) > 0


def price_table(lang,m):
    rows=[]
    currency=display_currency(m,lang)
    show_savings=any(has_saving(r) for r in m['rates'])
    for r in m['rates']:
        saved=t(lang,f'比官方便宜 {r["saving"]}%',f'{r["saving"]}% below official') if has_saving(r) else '—'
        saving_cell=f'<td class="qm-saving">{saved}</td>' if show_savings else ''
        rows.append(f'<tr><th scope="row">{e(r[lang])}</th><td><code>{m["slug"]}</code></td><td class="qm-price">{money(r["amount"],m,lang)} / {UNITS[r["unit"]][lang=="en"]}</td>{saving_cell}</tr>')
    heading='单价（人民币）' if currency=='CNY' else t(lang,'单价（USD）','Price (USD)')
    savings_heading=f'<th scope="col" class="qm-saving-head">{t(lang,"优惠","Savings")}</th>' if show_savings else ''
    table_class='q-table-wrap qm-table'+(' qm-table--savings' if show_savings else '')
    return f'<div class="{table_class}" tabindex="0" role="region" aria-label="{t(lang,"价格表，可横向滚动","Pricing table; scroll horizontally")}"><table><thead><tr><th scope="col">{t(lang,"功能 / 规格","Operation / specification")}</th><th scope="col">{t(lang,"模型名","Model")}</th><th scope="col">{heading}</th>{savings_heading}</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def price_rules(lang,m):
    if m.get('factors'):
        factors=''.join(f'<li><b>{e(z if lang=="zh" else en)}</b><span>×{n}</span></li>' for z,en,n in m['factors'])
        note=t(lang,'按基价与倍率计算，输出费用和参考图片费用相加。下面为估算示例，最终以控制台账单为准。','Multiply the base rate by the applicable output and reference multipliers, then add the charges. Examples are estimates; the console bill is authoritative.')
        if m['slug'].endswith('-pro'): note+=t(lang,'面积不超过 225 万像素按 1K 档计费。',' Images of up to 2.25 million pixels use the 1K tier.')
        return f'<div class="qm-billing-rule"><h3>{t(lang,"基价 × 倍率，输出与参考图相加","Base rate × multipliers")}</h3><ul>{factors}</ul><p>{note}</p></div>'
    if m['kind']=='realtime':
        return '<p class="qm-callout">'+t(lang,'语音输出时，音频和对应文本分别按各自的输出价计费。','Speech output is billed for both audio and corresponding text at their respective output rates.')+'</p>'
    if m.get('official'):
        official='、'.join(f'{res} {money(value,m,lang)}' for res,value in zip(('480P','720P','1080P'),m['official']))
        return '<p class="q-note">'+t(lang,f'优惠对比官方常规秒价（同按 6.7 换算）：{official}。官方限时 7 折活动已于 2026-09-24 结束，未用作对比基准。','Savings compare official list rates: 480P $0.05, 720P $0.10, and 1080P $0.20 per second. The 30%-off campaign ended September 24, 2026 and is not the comparison baseline.')+' <a href="https://modelstudio.console.alibabacloud.com/model-releases/wan3.0-video" target="_blank" rel="noopener">'+t(lang,'官方定价来源','Official pricing source')+' ↗</a></p>'
    return ''


def estimates(lang,m):
    if m.get('factors'):
        base=Decimal(m['rates'][0]['amount']); multiplier=m['factors'][0][2]
        examples=[(t(lang,'1 张输出，无参考图','One output, no reference'),t(lang,f'原始基价 × {multiplier}，再换算人民币',f'{money(base,m,lang)} × {multiplier}'),base*multiplier),
                  (t(lang,'1 张输出 + 1 张参考图','One output + one reference'),t(lang,f'原始基价 × ({multiplier} + 2)，再换算人民币',f'{money(base,m,lang)} × ({multiplier} + 2)'),base*(multiplier+2))]
    elif m['kind']=='realtime':
        examples=[(t(lang,'100 万音频输入 tokens','1M audio input tokens'),'$1.3810 × 1',Decimal('1.3810')),
                  (t(lang,'100 万音频输出 + 100 万文本输出 tokens','1M audio + 1M text output tokens'),'$2.7770 + $1.0400',Decimal('3.8170'))]
    else:
        first=m['rates'][0]; price=Decimal(first['amount']); unit=UNITS[first['unit']][lang=='en']
        quantities=[5,10] if first['unit']=='second' else [1,10]
        examples=[(f'{first[lang]} · {n} {unit}',t(lang,f'原始单价 × {n}，再换算人民币',f'{money(first["amount"],m,lang)} × {n}'),price*n) for n in quantities]
    return '<ul class="qm-costs">'+''.join(f'<li><h3>{e(title)}</h3><p>{formula}</p><strong>{money(value,m,lang)}</strong></li>' for title,formula,value in examples)+'</ul>'


def pricing(lang,m):
    show_savings=any(has_saving(r) for r in m['rates'])
    saving_basis='优惠比例按原始美元价格计算，' if show_savings else ''
    unit_note='人民币参考价按 1 USD = ¥6.70 换算，显示保留两位小数；成本示例先按原始美元单价计算，再换算并四舍五入。'+saving_basis+'实际结算仍以 USD 为准。' if display_currency(m,lang)=='CNY' else '单位 USD，'
    missing_saving_note=t(lang,'“—”表示未列出已核实的官方同规格优惠。',' “—” means no verified same-specification official saving is listed.') if show_savings and any(not has_saving(r) for r in m['rates']) else ''
    return f'''<section class="q-section q-tint" id="pricing"><div class="q-wrap">
<p class="q-kicker">02 / {t(lang,'价格','Pricing')}</p><h2>{e(m.get('short',m['name']))} API {t(lang,'价格','pricing')}</h2>
<ul class="q-billing"><li><strong>{t(lang,'按规格计费','Specification-based billing')}</strong>{t(lang,'按下表核对输入与输出计费项','Check the input and output billing items below')}</li><li><strong>{t(lang,'并发不限','No concurrency cap')}</strong>{t(lang,'所有用户默认享有','Available to all users')}</li><li><strong>{t(lang,'余额通用','Shared balance')}</strong>300+ {t(lang,'模型，一个 Key','models, one key')}</li></ul>
{price_table(lang,m)}{price_rules(lang,m)}{estimates(lang,m)}
<p class="q-note">{t(lang,unit_note+'按成功提交计费。2026-11-07 核对，实时价格以模型广场为准。','USD, charged for successful requests. Checked November 7, 2026; the live catalog takes precedence.')}{missing_saving_note}</p>
<div class="qm-actions"><a class="q-btn q-primary" href="{REG}">{t(lang,'获取 API Key','Get an API key')}</a><a href="{MARKET}">{t(lang,'在模型广场查看','View the model catalog')} ↗</a></div></div></section>'''


def family(lang,m):
    peers=IMG if m['kind']=='image' else VID
    cards=''.join(f'<li><a href="/{lang}/models/{p["slug"]}"'+(' aria-current="page"' if p['slug']==m['slug'] else '')+f'><b>{e(p["name"])}</b><span>{price_label(p,lang)}</span></a></li>' for p in peers)
    return f'<section class="q-section" id="family"><div class="q-wrap"><p class="q-kicker">Qwen</p><h2>{t(lang,"同系列模型","Related models")}</h2><ul class="q-family">{cards}</ul><p class="q-note"><a href="/{lang}/models/qwen">{t(lang,"Qwen 对话模型总览","Qwen conversation-model overview")} →</a></p></div></section>'


def quickstart(lang,m):
    method,path=('POST','/v1/images/generations') if m['kind']=='image' else ('WS','/v1/realtime') if m['kind']=='realtime' else ('POST',VIDEO_ENDPOINT)
    return f'''<section class="q-section q-tint" id="quickstart"><div class="q-wrap q-narrow"><p class="q-kicker">04 / {t(lang,'接入','Access')}</p><h2>{t(lang,'从一个 API Key 开始','Start with one API key')}</h2>
<ol class="q-steps"><li>{t(lang,'注册后在控制台创建 API Key。','Register and create an API key in the console.')}</li><li>{t(lang,'选择模型','Select model')} <code>{m['slug']}</code>{t(lang,'，确认输入、输出规格与预算。',', and confirm the inputs, output specification, and budget.')}</li><li>{t(lang,'使用 Bearer 鉴权；请求参数和结果查询可联系技术支持确认。','Use Bearer authentication; contact technical support for request parameters and result retrieval.')}</li></ol>
<div class="qm-endpoint"><span>{method}</span><code>{path}</code></div><p class="q-note">{t(lang,'接口路径来自模型广场详情。','Endpoint from the model catalog details.')} <a href="{SUPPORT}">{t(lang,'联系技术支持','Contact technical support')} ↗</a></p></div></section>'''


def enhance(s,lang,slug):
    m=BY_SLUG[slug]; n=m.get('short',m['name']); kind=m['kind']; zh=lang=='zh'
    title=f'{n} API 价格与接入 - AnyAIGC' if zh else f'{n} API Pricing & Access - AnyAIGC'
    cap=t(lang,'图像生成','image generation') if kind=='image' else t(lang,'实时音视频交互','live audio/video') if kind=='realtime' else t(lang,'视频创作','video creation')
    desc=(f'{n} API，{price_label(m,lang)}起，支持{cap}，并发不限。通过 AnyAIGC 统一账户与余额接入，支持企业对公转账、服务合同及增值税专票。' if zh else f'{n} API: {cap} from {price_label(m,lang)}, no concurrency cap, bank transfer and VAT invoices on AnyAIGC.')
    if not zh and len(desc)<120:
        desc=desc[:-1]+', for teams.'
    s=re.sub('<title>.*?</title>',lambda _:f'<title>{e(title)}</title>',s,count=1)
    for attr in ['name="description"','property="og:description"','name="twitter:description"']:
        s=re.sub(r'(<meta '+attr+r' content=")[^"]*',lambda match:match[1]+e(desc),s,count=1)
    for attr in ['property="og:title"','name="twitter:title"']:
        s=re.sub(r'(<meta '+attr+r' content=")[^"]*',lambda match:match[1]+e(title),s,count=1)
    s=s.replace('<meta name="twitter:card"',f'<meta property="og:image:alt" content="{e(n)} API · AnyAIGC"><link rel="icon" href="/favicon.ico"><meta name="twitter:card"',1)
    s=s.replace('<body class="q-media-'+kind+'">','<body class="qm-page qm-'+kind+'">')
    s=s.replace('<main>','<main id="main">',1)
    s=s.replace('<section class="q-hero">','<section class="q-hero qm-hero">',1)
    s=s.replace('<h1>'+n+' API</h1>',f'<h1>{e(m["name"])} API</h1>',1)
    s=re.sub(r'<p class="q-sub">.*?</p>',lambda _:f'<p class="qm-tagline">{e(m["lead"][not zh])}</p><p class="q-sub">{e(m["summary"][not zh])}</p><div class="qm-entry-price"><b>{price_label(m,lang)}</b><span>{t(lang,"起 · 完整计费规则见下表","starting rate · see billing details below")}</span></div>',s,count=1,flags=re.S)
    # Scope billing units and realtime labels correctly.
    if kind=='realtime':s=s.replace('<li>视频生成</li>','<li>实时音视频交互</li>').replace('<li>Video generation</li>','<li>Real-time audio / video</li>').replace('<li>按秒计费</li>','<li>按 tokens 计费</li>')
    if kind=='image' and m['rates'][0]['unit']=='request':s=s.replace('<li>按张计费</li>','<li>按次计费</li>').replace('<li>Per image</li>','<li>Per request</li>')
    if m['rates'][0]['unit']=='clip':s=s.replace('<li>按秒计费</li>','<li>按分辨率与时长计费</li>').replace('<li>Per second</li>','<li>Resolution / duration pricing</li>')
    features=''.join(f'<article><b>0{i+1}</b><h3>{e(f[not zh])}</h3><p>{e(f[2+(not zh)])}</p></article>' for i,f in enumerate(m['features']))
    feature_section=f'<section class="q-section" id="capabilities"><div class="q-wrap"><p class="q-kicker">01 / {t(lang,"模型能力","Capabilities")}</p><h2>{t(lang,"为这类创作而设计","Designed for this kind of work")}</h2><div class="q-cards">{features}</div></div></section>'
    s=re.sub(r'<section class="q-section">.*?</section>',lambda _:feature_section,s,count=1,flags=re.S)
    s=replace_section(s,'pricing',pricing(lang,m))
    s=re.sub(r'<section class="q-section">.*?</section>',lambda _:quickstart(lang,m),s,count=1,flags=re.S)
    uses=m.get('uses') or m['features'][:2]
    cards=''.join(f'<article><span>0{i+1}</span><h3>{e(x[not zh])}</h3><p>{e(x[2+(not zh)])}</p></article>' for i,x in enumerate(uses))
    use_section=f'<section class="q-section" id="uses"><div class="q-wrap"><p class="q-kicker">03 / {t(lang,"工作流","Workflow")}</p><h2>{t(lang,"把模型放进实际工作","Put the model to work")}</h2><div class="qm-workflows">{cards}</div></div></section>'
    s=s.replace('<section class="q-section q-tint" id="quickstart">',use_section+'<section class="q-section q-tint" id="quickstart">',1)
    s=s.replace('<section class="q-section" id="faq">',family(lang,m)+'<section class="q-section" id="faq">',1)
    items=''.join(f'<li><h3>{a}</h3><p>{b}</p></li>' for a,b in TRUST_ITEMS[lang])
    s=re.sub(r'<ul class="trust-list">.*?</ul>',lambda _:'<ul class="trust-list">'+items+'</ul><div class="qm-actions"><a class="q-btn q-primary" href="'+REG+'">'+t(lang,'先注册领取 200 万 tokens','Sign up for 2M free tokens')+'</a></div>',s,count=1,flags=re.S)
    if zh:s=s.replace('<li>WeChat Pay</li>','<li>微信支付</li>').replace('<li>Alipay</li>','<li>支付宝</li>')
    entdetails=[('按实际充值金额开具增值税普通发票和专用发票。','VAT general and special invoices for the actual top-up amount.'),('支持公司账户对公转账充值。','Top up by corporate bank transfer.'),('可签订服务合同，配合采购和法务流程。','Service agreements for procurement and legal review.'),('提供专属客服与技术对接，协助接入和排查。','Dedicated support and technical contact for integration and troubleshooting.')]
    idx=[0]
    def entcard(match):
        copy=entdetails[idx[0]][not zh];idx[0]+=1
        return match[0].replace('</article>',f'<p>{copy}</p></article>')
    ent=re.search(r'<section[^>]*id="enterprise".*?</section>',s,re.S)
    s=s[:ent.start()]+re.sub(r'<article>.*?</article>',entcard,ent[0],flags=re.S)+s[ent.end():]
    # Replace generic FAQ content and keep structured answers identical to visible text.
    faq=re.search(r'<section[^>]*id="faq".*?</section>',s,re.S)
    faqhtml=faq[0]
    qa=list(re.finditer(r'<details(?: open)?><summary><h3>(.*?)</h3></summary><div class="q-ans"><p>(.*?)</p></div></details>',faqhtml,re.S))
    values=[(x[1],x[2]) for x in qa]
    values[0]=(t(lang,f'{n} 适合什么任务？',f'What is {n} for?'),e(m['summary'][not zh]))
    rates='；'.join(f'{r[lang]} {money(r["amount"],m,lang)}/{UNITS[r["unit"]][not zh]}' for r in m['rates'])
    if m.get('factors'):
        factors='; '.join(f'{x[not zh]} ×{x[2]}' for x in m['factors'])
        rates+=t(lang,f'。实际按倍率计费：{factors}；输出与参考图费用相加，基价不是输出一张图的最终费用。',f'. Apply these multipliers: {factors}; output and reference fees are added. The base rate is not the final price of one output image.')
    elif kind=='realtime':rates+=t(lang,'。语音输出同时计算音频和对应文本费用。','. Speech output is billed for audio and corresponding text.')
    if display_currency(m,lang)=='CNY':
        rates+=' 人民币价格按美元价 × 6.7 换算并保留两位小数；实际费用按原始美元单价计算，以 USD 结算。'
    values[1]=(t(lang,'API 价格如何计算？','How is API usage priced?'),e(rates+t(lang,' 实时价格以模型广场为准。',' See the catalog for live prices.')))
    faqhtml=re.sub(r'<div class="q-faq">.*?</div></div></section>',lambda _:'<div class="q-faq">'+''.join(f'<details><summary><h3>{q}</h3></summary><div class="q-ans"><p>{a}</p></div></details>' for q,a in values)+'</div></div></section>',faqhtml,flags=re.S)
    s=s[:faq.start()]+faqhtml+s[faq.end():]
    js=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S); data=json.loads(js[1])
    for node in data['@graph']:
        if node['@type']=='WebPage':node.update(name=title,description=desc,dateModified='2026-11-09' if kind=='video' else DATE)
        if node['@type']=='Product':
            currency=display_currency(m,lang)
            offers=[{'@type':'Offer','name':r[lang],'price':display_amount(r['amount'],m,lang),'priceCurrency':currency,'priceSpecification':{'@type':'UnitPriceSpecification','price':display_amount(r['amount'],m,lang),'priceCurrency':currency,'unitText':UNITS[r['unit']][not zh]}} for r in m['rates']]
            node.update(description=desc,image=f'{SITE}/assets/og/{slug}-{lang}.png',brand={'@type':'Brand','name':'AnyAIGC'})
            node['offers'].update(priceCurrency=currency,lowPrice=min(offers,key=lambda x:Decimal(x['price']))['price'],highPrice=max(offers,key=lambda x:Decimal(x['price']))['price'],offerCount=len(offers),offers=offers)
        if node['@type']=='FAQPage':node['mainEntity']=[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':text(a)}} for q,a in values]
    s=s[:js.start(1)]+'\n'+json.dumps(data,ensure_ascii=False,indent=2)+'\n'+s[js.end(1):]
    theme='qwen-image' if kind=='image' else 'wan'
    theme_version='20261109' if theme=='wan' else VERSION
    s=s.replace('</head>',f'<link rel="stylesheet" href="/assets/models/qwen-media.css?v=20261107g"><link rel="stylesheet" href="/assets/models/{theme}.css?v={theme_version}"></head>')
    s=re.sub(r'/assets/models/qwen\.js\?v=[^" ]+','/assets/models/qwen.js?v=20261107f',s)
    s=s.replace('<header class="q-nav">',f'<a class="qm-skip" href="#main">{t(lang,"跳到主要内容","Skip to main content")}</a><header class="q-nav">',1)
    art=''
    if slug.startswith('qwen-image-3.0'):
        art=f'<figure class="qm-hero-art"><img src="/assets/models/qwen-media/qwen-image-3-layout.webp" width="1600" height="904" alt="{t(lang,"Qwen Image 3.0 官方复杂排版示例","Official Qwen Image 3.0 complex-layout example")}" fetchpriority="high"><figcaption><a href="https://qwen.ai/blog?id=qwen-image-3.0" target="_blank" rel="noopener">{t(lang,"Qwen Image 3.0 官方示例","Official Qwen Image 3.0 example")} ↗</a></figcaption></figure>'
    elif kind=='video':
        s=s.replace('class="qm-page qm-video"','class="qm-page qm-video qm-video-background"',1)
        hero=re.search('<section class="q-hero qm-hero">.*?</section>',s,re.S)
        content=hero[0]
        content=content.replace('<section class="q-hero qm-hero"><div class="q-wrap">',f'''<section class="q-hero qm-hero wan-hero" aria-label="{e(m['name'])} API">
<div class="wan-hero-backdrop" aria-hidden="true"><video id="wan-hero-video" class="wan-hero-video" autoplay muted loop playsinline preload="auto" poster="/assets/models/qwen-media/wan3-poster.webp" tabindex="-1"><source src="/assets/models/qwen-media/wan3-sparring.mp4" type="video/mp4"></video></div>
<div class="q-wrap wan-hero-content">''',1)
        source_label=t(lang,'万相 3.0 官方演示 · 废墟对练','Official Wan 3.0 demo · Sparring in the ruins') if slug=='wan3.0-video' else t(lang,'背景素材：Wan 3.0 官方演示','Background footage: official Wan 3.0 demo')
        controls=f'''<div class="q-wrap wan-hero-meta"><a href="https://modelstudio.console.alibabacloud.com/model-releases/wan3.0-video" target="_blank" rel="noopener">{source_label} ↗</a><button class="wan-hero-toggle" type="button" aria-controls="wan-hero-video" data-play-label="{t(lang,'播放背景视频','Play background video')}" data-pause-label="{t(lang,'暂停背景视频','Pause background video')}" hidden><span data-video-toggle-label>{t(lang,'暂停背景视频','Pause background video')}</span></button></div>'''
        content=content.replace('</div></section>','</div>'+controls+'</section>',1)
        s=s[:hero.start()]+content+s[hero.end():]
        s=s.replace('</body>','<script src="/assets/models/wan-hero.js?v=20261107" defer></script></body>',1)
    if art:
        hero=re.search('<section class="q-hero qm-hero">.*?</section>',s,re.S)
        s=s[:hero.start()]+hero[0].replace('</div></section>',art+'</div></section>')+s[hero.end():]
    # Footer keeps the approved layout; clarify trademark attribution by product family.
    brand='万相（Wan）' if slug.startswith('wan') else 'HappyHorse' if slug.startswith('happyhorse') else 'Z-Image' if slug=='z-image-turbo' else '千问（Qwen）'
    s=s.replace('千问（Qwen）是阿里云的商标。',f'{brand} 名称及商标归阿里巴巴相关权利人所有。').replace('Qwen is a trademark of Alibaba Cloud.',f'{e(n)} names and trademarks belong to their respective Alibaba owners.')
    s=s.replace('</footer>', '</footer>',1)
    return re.sub(r'><(?=section|/section|header|footer|main|/main|meta|link|body|/body)', '>\n<',s)
