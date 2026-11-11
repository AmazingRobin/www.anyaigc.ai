"""Build the Vidu overview and 7 model topic pages (zh + en).

Run: python scripts/vidu_pages.py
Facts live in vidu_data.py; this file is layout and copy only.
"""

from decimal import Decimal
from html import escape, unescape
from pathlib import Path
import json
import re

from vidu_data import (MODELS, MODEL_BY_SLUG, SLUGS, CHECKED_DATE, PRICING_URL, DOCS, EP, QUERY,
                       clip_cost)
import payments
import trust

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.anyaigc.ai"
REG = "https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9"
SUPPORT = "https://anyaigc.ai/customersupport"
VER = "20261111"
ICON = (ROOT / "assets/icons/vidu-color.svg").read_text(encoding="utf-8")
SAMPLE_IMAGE = SITE + "/assets/models/vidu/skycity.webp"


def pick(lang, zh, en):
    return zh if lang == "zh" else en


def h(value):
    return escape(str(value), quote=True)


def txt(value):
    return unescape(re.sub(r"<[^>]+>", "", value))


def url(lang, slug):
    return f"{SITE}/{lang}/models/{slug}"


def doc_url(lang, value):
    return value if lang == "zh" else value.replace("https://docs.anyaigc.ai/", "https://docs.anyaigc.ai/en/", 1)


def logo(identifier, size=28):
    svg = ICON.replace("lobe-icons-vidu-_R_0_", f"vd-grad-{identifier}")
    svg = re.sub(r"<title>.*?</title>", "", svg)
    return re.sub(r"<svg\b[^>]*>", f'<svg class="vd-mark" viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true" focusable="false">', svg, count=1)


def button(label, href, secondary=False):
    return f'<a class="vd-btn{" vd-btn-ghost" if secondary else ""}" href="{h(href)}">{h(label)}</a>'


def section(sid, kicker, title, lead, body, soft=False):
    return (f'<section class="vd-section{" vd-soft" if soft else ""}" id="{sid}" aria-labelledby="{sid}-title"><div class="vd-wrap">\n'
            f'<p class="vd-kicker">{h(kicker)}</p><h2 id="{sid}-title">{h(title)}</h2>\n'
            f'<p class="vd-lead">{lead}</p>\n{body}\n</div></section>\n')


def money(value):
    s = format(value.normalize(), "f")
    return s if "." in s else s + ".00"


def price_text(lang, p):
    if "first" in p:
        return p["text_" + lang]
    if p.get("addon"):
        return pick(lang, f'+${p["amount"]} / 次', f'+${p["amount"]} per task')
    return f'${p["amount"]} / {p["unit_" + lang]}'


def offer_name(lang, m, p):
    if "first" in p:
        return f'{m["id"]} {p["label_" + lang]} · ' + pick(lang, "首秒", "first second")
    return f'{m["id"]} {p["label_" + lang]} / {p["unit_" + lang]}'


# ---------------------------------------------------------------- metadata
def metadata(lang, m):
    if m is None:
        name = "Vidu"
        title = pick(lang, "Vidu API 价格与接入｜Q4、Q3、Q2 视频与图像 - AnyAIGC",
                     "Vidu API Pricing | Q4, Q3, Q2 video & image - AnyAIGC")
        desc = pick(lang,
                    "Vidu API 全系 7 个模型价格与接入：Q4 Preview、Q3、Q2 视频与 Q2 图像，视频 $0.0223 首秒起，图像 $0.0298/张起，并发不限，支持对公转账、合同与增值税专票。",
                    "Vidu API pricing for 7 models: Q4 Preview, Q3 and Q2 video plus Q2 Image. Video from $0.0223, images from $0.0298. Unlimited concurrency, VAT invoices.")
    else:
        name = m["name"]
        title = pick(lang, f'{name} API 价格与接入｜{m["title_zh"]} - AnyAIGC', f'{name} API Pricing | {m["title_en"]} - AnyAIGC')
        if len(title) > 65 and lang == "en":
            title = f'{name} API Pricing | {m["title_en"]}'
        caps_zh = "、".join(c.split("（")[0] for c in m["caps_zh"][:2])
        desc = pick(lang,
                    f'{name} API（{m["id"]}）价格与接入：${m["start"]}/{m["start_zh"]}起，支持{caps_zh}。附完整价格表与调用示例，并发不限，支持对公转账、合同与增值税专票。',
                    f'{name} API ({m["id"]}) from ${m["start"]} per {m["start_en"]}: {m["caps_en"][0].lower()}, {m["caps_en"][1].lower()}. Unlimited concurrency, VAT invoices, contracts.')
        if lang == "en" and len(desc) > 160:
            desc = f'{name} API ({m["id"]}) from ${m["start"]} per {m["start_en"]}. Unlimited concurrency, VAT invoices, bank transfer and contracts on AnyAIGC.'
    tw = sum(2 if ord(c) > 0x2E7F else 1 for c in title)
    assert (tw <= 64 if lang == "zh" else len(title) <= 65), (lang, title, tw, len(title))
    assert (60 <= len(desc) <= 120 if lang == "zh" else 120 <= len(desc) <= 160), (lang, len(desc), desc)
    return name, title, desc


# ---------------------------------------------------------------- FAQ
def faq_items(lang, m):
    if m:
        name = m["name"]
        rows = [p for p in m["prices"] if not p.get("addon")]
        answer = "；".join(f'{p["label_zh"]} {price_text("zh", p)}' for p in rows) if lang == "zh" else \
            "; ".join(f'{p["label_en"]} {price_text("en", p)}' for p in rows)
        addons = [p for p in m["prices"] if p.get("addon")]
        if addons:
            answer += pick(lang, "。图生 / 参考生音视频直出每次另加 $0.0558，启用推荐提示词每次另加 $0.0372",
                           ". Native audio on image or reference input adds $0.0558 per task, and recommended prompts add $0.0372")
        answer += pick(lang, "。单位 USD，实时价格以模型广场为准。", ". Prices are in USD; check the model catalog for current rates.")
        eps = [EP[e][0] for e in m["endpoints"]]
        ep_answer = pick(lang,
                         f'{"、".join(eps)}，model 填 {m["id"]}。创建请求返回 task_id，再用 {QUERY} 查询结果。API 域名为 https://anyaigc.ai，用 Authorization: Bearer 传入 API Key。',
                         f'{"; ".join(eps)} with model set to {m["id"]}. Creation returns a task_id; fetch the result with {QUERY}. The base URL is https://anyaigc.ai and the key goes in Authorization: Bearer.')
        if m["id"] == "vidu-image-q2":
            detail_q = pick(lang, "支持多少张参考图、哪些分辨率和画幅？", "How many reference images, resolutions and aspect ratios are supported?")
            detail_a = pick(lang, "不传 images 为文生图，传 1–7 张为参考生图，计费按 1–3 张和 4–7 张两档。分辨率可选 1080p（默认）、2K、4K；画幅支持 16:9、9:16、1:1、3:4、4:3、21:9、2:3、3:2 和 auto。model 传 viduq2 也会按 vidu-image-q2 计费。",
                            "Omit images for text-to-image, or pass 1–7 for reference generation, billed in 1–3 and 4–7 image tiers. Resolution is 1080p (default), 2K or 4K. Aspect ratios are 16:9, 9:16, 1:1, 3:4, 4:3, 21:9, 2:3, 3:2 and auto. Passing viduq2 as the model is billed as vidu-image-q2.")
        elif "first" in m["prices"][0]:
            detail_q = pick(lang, "「第1秒 + 后续每秒」怎么算？", "How does first-second plus per-second pricing work?")
            p = m["prices"][0]
            five = money(clip_cost(p, 5))
            detail_a = pick(lang,
                            f'按视频时长累加：第 1 秒一个价，之后每多 1 秒加一次。以{p["label_zh"]}为例，5 秒视频为 ${five}。时长 {m["durations"]} 秒，分辨率 {" / ".join(m["resolutions"])}。',
                            f'Charges add up with length: one rate for the first second, then a fixed amount per extra second. For {p["label_en"]}, a 5-second clip costs ${five}. Duration is {m["durations"]} seconds at {" / ".join(m["resolutions"])}.')
        else:
            detail_q = pick(lang, "支持哪些时长和清晰度？", "Which durations and resolutions are supported?")
            detail_a = pick(lang,
                            f'{name} 时长 {m["durations"]} 秒，默认 5 秒；清晰度 {" / ".join(m["resolutions"])}。按秒计费，费用 = 每秒单价 × 视频秒数。',
                            f'{name} renders {m["durations"]} seconds (5 by default) at {" / ".join(m["resolutions"])}. Billing is per second: rate × clip length.')
            if m["id"] == "viduq4-preview":
                detail_a += pick(lang, "不传 audio 参数时默认同时生成音频。", " Audio is generated by default when you omit the audio parameter.")
        first = [(pick(lang, f"{name} API 多少钱？", f"How much does the {name} API cost?"), answer),
                 (pick(lang, "调用哪个接口？", "Which endpoint should I call?"), ep_answer),
                 (detail_q, detail_a),
                 (pick(lang, "生成结果怎么拿？", "How do I get the result?"),
                  pick(lang, f"任务是异步的。创建后保存 task_id，轮询 {QUERY}，状态完成后从返回的 creations 里取视频或图片地址；也可以在创建时传 callback_url 接收回调。下载地址有时效，请及时转存。",
                       f"Tasks are asynchronous. Keep the task_id, poll {QUERY}, and read the video or image URL from creations when the task finishes. You can also pass callback_url when creating the task. Result URLs expire, so store files promptly."))]
    else:
        name = "Vidu"
        first = [
            (pick(lang, "Vidu API 起步价是多少？", "What are the starting prices for the Vidu API?"),
             pick(lang, "视频最低是 Q2 Turbo 540p 首秒 $0.0223（之后每秒 +$0.00744）；按秒计费的 Q3 Turbo 540p 为 $0.0298/秒；Q4 Preview 540p 为 $0.0486/秒；Q2 Image 文生图 1080p 为 $0.0298/张。单位 USD，实时价格以模型广场为准。",
                  "Video starts at $0.0223 for the first second of Q2 Turbo 540p (then +$0.00744/s). Q3 Turbo 540p is $0.0298/s, Q4 Preview 540p is $0.0486/s, and Q2 Image text-to-image at 1080p is $0.0298 per image. Prices are in USD; check the model catalog for current rates.")),
            (pick(lang, "7 个模型怎么选？", "How do I choose among the 7 models?"),
             pick(lang, "要 2K / 4K 或最新效果选 Q4 Preview；要音画同出、智能切镜选 Q3 Pro，追求速度选 Q3 Turbo；纯图生或首尾帧、预算敏感选 Q2 Turbo，效果优先选 Q2 Pro；文生视频和多图参考生视频选 Q2；生成图片选 Q2 Image。",
                  "Pick Q4 Preview for 2K/4K and the newest model; Q3 Pro for synchronized audio and smart shot transitions, or Q3 Turbo for speed; Q2 Turbo for budget image or first/last-frame clips and Q2 Pro for higher quality; Q2 for text and multi-image reference video; Q2 Image for still images.")),
            (pick(lang, "这些模型用同一个接口吗？", "Do these models share endpoints?"),
             pick(lang, "按能力区分接口：文生视频 /ent/v2/text2video，图生视频 /ent/v2/img2video，首尾帧 /ent/v2/start-end2video，参考生视频 /ent/v2/reference2video，图像 /ent/v2/reference2image；用 model 字段选择型号，结果统一用 GET /ent/v2/tasks/{id}/creations 查询。",
                  "Endpoints follow the task: /ent/v2/text2video, /ent/v2/img2video, /ent/v2/start-end2video, /ent/v2/reference2video and /ent/v2/reference2image. Choose the model with the model field and fetch every result with GET /ent/v2/tasks/{id}/creations.")),
            (pick(lang, "生成结果怎么拿？", "How do I get the result?"),
             pick(lang, "所有任务都是异步的：创建请求返回 task_id，轮询查询接口，完成后从 creations 里取视频或图片地址；也可以传 callback_url 接收回调。",
                  "Every task is asynchronous: creation returns a task_id, you poll the query endpoint and read the video or image URL from creations, or pass callback_url to receive a callback.")),
        ]
    first += [
        (pick(lang, "并发和 RPM 有限制吗？", "Are there concurrency or RPM limits?"),
         pick(lang, "AnyAIGC 的 Vidu 接入并发不限，所有用户默认享有，不设固定 RPM 上限。视频生成需要处理时间，请在应用里设置轮询间隔和超时。",
              "Vidu on AnyAIGC has unlimited concurrency for every account by default, with no fixed RPM cap. Video generation takes time, so set a polling interval and timeout in your application.")),
        (pick(lang, "生成的内容可以商用吗？", "Can I use the output commercially?"),
         pick(lang, "模型与生成内容的商用授权以生数科技（Vidu）官方条款为准；使用的参考图、人物和品牌素材需要你有相应权利。AnyAIGC 是独立 API 服务商。",
              "Commercial use is governed by Vidu's (ShengShu Technology) official terms, and you need rights to any reference images, people or brand assets you upload. AnyAIGC is an independent API provider.")),
        (pick(lang, "AnyAIGC 能开发票吗？支持增值税专票吗？", "Can AnyAIGC issue invoices, including VAT special invoices?"),
         pick(lang, "支持。可按实际充值金额开具增值税普通发票和增值税专用发票，联系企业客服办理即可。",
              "Yes. AnyAIGC issues invoices for actual top-ups, including Chinese VAT general and VAT special invoices. Contact enterprise support to arrange them.")),
        (pick(lang, "企业可以对公转账和签合同吗？", "Can my company pay by bank transfer and sign a contract?"),
         pick(lang, "可以。支持企业对公转账充值，可签订服务合同，并提供专属客服与技术对接。",
              "Yes. Companies can top up by corporate bank transfer, sign a service agreement, and work with dedicated support and a technical contact.")),
    ]
    items = first + [(payments.Q[lang], payments.A[lang])] + trust.FAQ[lang]
    assert len(items) == 12
    return items


# ---------------------------------------------------------------- head
def head(lang, slug, m, faqs):
    name, title, desc = metadata(lang, m)
    me = url(lang, slug)
    image = f"{SITE}/assets/og/{slug}-{lang}.png"
    pairs = [(x, p) for x in ([m] if m else MODELS) for p in x["prices"]]
    offers = [{"@type": "Offer", "name": offer_name(lang, x, p), "price": p["amount"], "priceCurrency": "USD", "url": me + "#pricing"} for x, p in pairs]
    amounts = [Decimal(p["amount"]) for _, p in pairs]
    crumbs = [(pick(lang, "模型专题", "Model guides"), f"{SITE}/{lang}/models/"), ("Vidu", url(lang, "vidu"))]
    if m:
        crumbs.append((m["short"], me))
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": SITE + "/#org", "name": "AnyAIGC", "url": "https://anyaigc.ai", "logo": SITE + "/logo.webp"},
        {"@type": "WebSite", "@id": SITE + "/#website", "name": "AnyAIGC", "url": SITE + "/", "publisher": {"@id": SITE + "/#org"}},
        {"@type": "WebPage", "@id": me + "#webpage", "url": me, "name": title, "description": desc, "inLanguage": pick(lang, "zh-CN", "en"),
         "dateModified": CHECKED_DATE, "isPartOf": {"@id": SITE + "/#website"}, "breadcrumb": {"@id": me + "#breadcrumb"}, "mainEntity": {"@id": me + "#product"}},
        {"@type": "BreadcrumbList", "@id": me + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(crumbs, 1)]},
        {"@type": "Product", "@id": me + "#product", "name": name + " API (AnyAIGC)", "description": desc, "sku": m["id"] if m else "vidu",
         "image": image, "brand": {"@type": "Brand", "name": "Vidu"},
         "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": str(min(amounts)), "highPrice": str(max(amounts)),
                    "offerCount": len(offers), "url": me + "#pricing", "offers": offers}},
        {"@type": "FAQPage", "@id": me + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": txt(a)}} for q, a in faqs]},
    ]}
    locale, alternate = ("zh_CN", "en_US") if lang == "zh" else ("en_US", "zh_CN")
    keys = pick(lang, f"{name} API,{name} API 价格,{name} API key,{name} API 企业,{name} API 发票,Vidu API,Vidu 视频生成 API",
                f"{name} API,{name} API pricing,{name} API key,{name} API for business,Vidu API,Vidu video API")
    return f'''<!DOCTYPE html>
<html lang="{pick(lang, 'zh-CN', 'en')}" data-scrollbar="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{h(title)}</title>
<meta name="description" content="{h(desc)}">
<meta name="keywords" content="{h(keys)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#020b13">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{url('zh', slug)}">
<link rel="alternate" hreflang="en" href="{url('en', slug)}">
<link rel="alternate" hreflang="x-default" href="{url('en', slug)}">
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{locale}">
<meta property="og:locale:alternate" content="{alternate}">
<meta property="og:url" content="{me}">
<meta property="og:title" content="{h(title)}">
<meta property="og:description" content="{h(desc)}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{h(name)} API · AnyAIGC">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{h(title)}">
<meta name="twitter:description" content="{h(desc)}">
<meta name="twitter:image" content="{image}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261024b">
<link rel="stylesheet" href="/assets/models/vidu.css?v={VER}">
<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
'''


# ---------------------------------------------------------------- layout blocks
def nav(lang, slug, m):
    other = "en" if lang == "zh" else "zh"
    doc = doc_url(lang, DOCS[m["example"]] if m else DOCS["text2video"])
    links = [(f"/{lang}/models/", pick(lang, "模型专题", "Model guides")),
             (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
             ("#pricing", pick(lang, "价格", "Pricing")),
             ("#enterprise", pick(lang, "企业接入", "Enterprise")),
             (doc, pick(lang, "API 文档", "API docs"))]
    return (f'<a class="vd-skip" href="#main">{pick(lang, "跳到主要内容", "Skip to main content")}</a>\n'
            '<header class="vd-nav"><div class="vd-nav-inner">'
            f'<a class="vd-brand" href="/">AnyAIGC<span>{logo("nav", 18)}Vidu</span></a>'
            f'<nav id="vd-navigation" aria-label="{pick(lang, "主导航", "Main navigation")}"><ul class="vd-nav-links">'
            + "".join(f'<li><a href="{h(u)}">{h(t)}</a></li>' for u, t in links)
            + '</ul></nav><ul class="vd-nav-actions">'
            f'<li><a href="/{other}/models/{slug}" hreflang="{pick(other, "zh-CN", "en")}">{pick(lang, "EN", "中文")}</a></li>'
            f'<li><a href="https://anyaigc.ai/console">{pick(lang, "登录", "Log in")}</a></li>'
            f'<li><a class="vd-nav-cta" href="{h(REG)}">{pick(lang, "注册", "Sign up")}</a></li></ul>'
            f'<button class="vd-menu" type="button" aria-controls="vd-navigation" aria-expanded="false" aria-label="{pick(lang, "打开导航菜单", "Open navigation menu")}"><span></span></button>'
            '</div></header>\n')


PROMPTS = {
    "text2video": ("清晨的雪山湖面，一只红狐狸踩着薄冰走过，镜头低机位缓慢跟拍，呼出的白气在阳光里散开。",
                   "A red fox crosses thin ice on a mountain lake at dawn; low tracking shot, its breath drifting in the sunlight."),
    "img2video": ("镜头缓慢推进，云海翻涌，远处的城市亮起灯光，少女的红色披风被风吹起。",
                  "Slow push-in as the sea of clouds rolls, distant city lights flicker on and the girl's red cape lifts in the wind."),
    "reference2image": ("以参考图中的天空之城为背景，生成一张电影海报，黄昏光线，中央留出标题位置。",
                        "Use the sky city in the reference as the backdrop for a film poster at golden hour, with space for a title in the center."),
}


def hero(lang, slug, m):
    media = m["media"] if m else "football"
    items = [(pick(lang, "模型专题", "Model guides"), f"/{lang}/models/"), ("Vidu", f"/{lang}/models/vidu")]
    if m:
        items.append((m["short"], None))
    crumbs = "".join(f'<li><a href="{h(u)}">{h(t)}</a></li>' if u else f'<li aria-current="page">{h(t)}</li>' for t, u in items)
    if not m:
        crumbs = crumbs.replace('<li><a href="/' + lang + '/models/vidu">Vidu</a></li>', '<li aria-current="page">Vidu</li>')
    if m:
        h1 = f'{h(m["name"])} API'
        eyebrow = f'{m["id"]} · {m["tag_" + lang]}'
        lead = h(m["desc_" + lang])
        price = pick(lang, f'<strong>${m["start"]}</strong> / {h(m["start_zh"])}起', f'From <strong>${m["start"]}</strong> per {h(m["start_en"])}')
        prompt = PROMPTS[m["example"] if m["example"] in PROMPTS else "text2video"]
    else:
        h1 = "Vidu API"
        eyebrow = pick(lang, "Q4 · Q3 · Q2 · Q2 Image", "Q4 · Q3 · Q2 · Q2 Image")
        lead = pick(lang, "生数科技 Vidu 全系 7 个模型：文生、图生、首尾帧、参考生视频，以及参考生图。一个 AnyAIGC API Key 全部接入。",
                    "All 7 Vidu models from ShengShu: text, image, first/last-frame and reference-to-video, plus reference image generation, behind one AnyAIGC API key.")
        price = pick(lang, "视频 <strong>$0.0223</strong> 首秒起 · 图像 <strong>$0.0298</strong> / 张起", "Video from <strong>$0.0223</strong> · images from <strong>$0.0298</strong>")
        prompt = PROMPTS["text2video"]
    facts = [pick(lang, "并发不限", "Unlimited concurrency"), pick(lang, "300+ 模型 · 一个 Key", "300+ models · one key"),
             pick(lang, "对公 · 专票", "Contracts · invoices")]
    return ('<main id="main">\n<section class="vd-hero" aria-labelledby="hero-title">'
            f'<video class="vd-hero-bg" muted loop playsinline preload="metadata" poster="/assets/models/vidu/{media}.webp" aria-hidden="true">'
            f'<source src="/assets/models/vidu/{media}.mp4" type="video/mp4"></video><div class="vd-hero-shade"></div>'
            '<div class="vd-wrap vd-hero-inner">'
            f'<nav class="vd-crumbs" aria-label="{pick(lang, "面包屑", "Breadcrumb")}"><ol>{crumbs}</ol></nav>'
            f'<p class="vd-eyebrow">{logo("hero", 22)}<span>{h(eyebrow)}</span></p>'
            f'<h1 id="hero-title">{h1}</h1><p class="vd-hero-lead">{lead}</p><p class="vd-hero-price">{price}</p>'
            f'<div class="vd-prompt"><p><span class="vd-prompt-tag">Prompt</span>{h(pick(lang, *prompt))}</p>'
            f'<a class="vd-btn" href="{h(REG)}">{pick(lang, "获取 API Key", "Get an API key")}</a></div>'
            '<ul class="vd-facts">' + "".join(f"<li>{h(f)}</li>" for f in facts) + '</ul></div>'
            f'<button class="vd-motion" type="button" data-video-toggle hidden>{pick(lang, "播放背景", "Play motion")}</button>'
            '</section>\n')


def lineup(lang):
    cards = []
    for m in MODELS:
        cards.append(f'<li class="vd-card"><a href="/{lang}/models/{m["slug"]}">'
                     f'<span class="vd-card-media"><img src="/assets/models/vidu/{m["media"]}.webp" alt="" loading="lazy" width="640" height="360"><em>{h(m["tag_" + lang])}</em></span>'
                     f'<span class="vd-card-body"><strong>{h(m["name"])}</strong><code>{h(m["id"])}</code>'
                     f'<span class="vd-card-desc">{h(m["desc_" + lang])}</span>'
                     f'<span class="vd-card-price">${m["start"]} / {h(m["start_" + lang])}</span></span></a></li>')
    return section("models", pick(lang, "模型阵容", "LINEUP"), pick(lang, "Vidu 全系 7 个模型", "Seven Vidu models"),
                   pick(lang, "从 4K 旗舰到快速草稿，再到静态图像，按任务和预算选择。", "From the 4K flagship to fast drafts and still images, pick by task and budget."),
                   '<ul class="vd-cards">' + "".join(cards) + '</ul>')


CAP_TEXT = {
    "图生视频": ("用一张首帧图片定下画面，模型补全动作和镜头。", None),
}


def capabilities(lang, m):
    descs = {
        "viduq4-preview": [("一张首帧图片定下构图，模型补全动作、镜头和光影。", "One first frame sets the composition; the model fills in motion, camera and light."),
                           ("用多张参考图锁定人物、服装和道具，保持主体一致。", "Several reference images lock in characters, outfits and props for consistency."),
                           ("540p 出草稿，2K / 4K 出成片，同一模型五档清晰度。", "Draft at 540p and finish at 2K or 4K with five resolutions in one model."),
                           ("不传 audio 时默认生成配套音频，一次拿到有声片段。", "Audio is generated by default, so one call returns a clip with sound.")],
        "viduq3-pro": [("台词、环境声和背景音乐与画面同步生成。", "Dialogue, ambience and music are generated in sync with the picture."),
                       ("在一段视频里自动切换景别和机位，节奏更像剪辑过的成片。", "Shots and angles change within one clip, so it reads like an edited sequence."),
                       ("文字、首帧图或首尾两帧都可以作为输入。", "Start from text, a first frame, or a first and last frame."),
                       ("最长 16 秒，适合一个完整的段落或广告镜头。", "Up to 16 seconds, enough for a full beat or an ad shot.")],
        "viduq3-turbo": [("同为 Q3 系列，生成速度比 Q3 Pro 更快。", "Same Q3 family, faster generation than Q3 Pro."),
                         ("画面与声音一起生成，不用另外配乐配音。", "Picture and sound come out together; no separate scoring pass."),
                         ("文字、首帧图或首尾两帧都能直接生成。", "Generate from text, a first frame, or first and last frames."),
                         ("540p 每秒 $0.0298，适合批量出样片。", "At $0.0298 per second for 540p, it suits batch previews.")],
        "viduq2-pro": [("以首帧图片为起点，Q2 系列里画面效果更好的版本。", "Starts from a first frame; the higher-quality option in the Q2 family."),
                       ("给出起止两帧，模型生成中间的过渡与动作。", "Give opening and closing frames and the model builds the motion between them."),
                       ("支持多图或主体参考，保持角色一致。", "Use several images or subjects as references to keep characters consistent."),
                       ("1–10 秒，540p 到 1080p，第 1 秒起按秒递增计费。", "1–10 seconds at 540p to 1080p, priced from the first second upward.")],
        "viduq2": [("纯文字描述即可生成视频，运动幅度大、细节丰富。", "Generate from text alone with strong motion and rich detail."),
                   ("多张参考图或已建主体作为参考，角色和道具保持一致。", "Use several images or saved subjects to keep characters and props consistent."),
                   ("540p / 720p / 1080p 三档，按首秒加后续每秒计费。", "540p, 720p or 1080p, billed by first second plus each extra second."),
                   ("同一模型名调用 /ent/v2/reference2image 会按 Q2 Image 生成并计费。", "Calling /ent/v2/reference2image with this name generates and bills as Q2 Image.")],
        "viduq2-turbo": [("Q2 系列里生成更快的版本，适合大批量出片。", "The fastest Q2 option, suited to high-volume runs."),
                         ("一张首帧图片就能动起来。", "Animate a single first-frame image."),
                         ("给起止两帧，控制转场和动作终点。", "Set opening and closing frames to control transitions and end poses."),
                         ("540p 首秒 $0.0223，之后每秒 +$0.00744。", "540p costs $0.0223 for the first second, then +$0.00744 per second.")],
        "vidu-image-q2": [("不传参考图时，按文字描述直接生成图片。", "Without references, it generates straight from the prompt."),
                          ("传 1–7 张参考图，保持人物、商品或场景一致。", "Pass 1–7 reference images to keep people, products or scenes consistent."),
                          ("1080p、2K、4K 三档输出，按张计费。", "Output at 1080p, 2K or 4K, billed per image."),
                          ("16:9、9:16、1:1、21:9 等 8 种画幅，也可跟随首张参考图。", "Eight aspect ratios such as 16:9, 9:16, 1:1 and 21:9, or match the first reference.")],
    }
    if m:
        caps = list(zip(m["caps_" + lang], descs[m["slug"]]))
        title = pick(lang, f'{m["name"]} 能做什么', f'What {m["name"]} does')
    else:
        caps = [(pick(lang, "文生视频", "Text to video"), ("Q3 Pro、Q3 Turbo、Q2 都可以从一段文字直接生成视频。", "Q3 Pro, Q3 Turbo and Q2 generate video straight from text.")),
                (pick(lang, "图生与首尾帧", "Image and first/last frame"), ("Q4、Q3、Q2 Pro / Turbo 支持首帧图生；Q3 与 Q2 Pro / Turbo 支持首尾帧。", "Q4, Q3 and Q2 Pro/Turbo animate a first frame; Q3 and Q2 Pro/Turbo also take a last frame.")),
                (pick(lang, "参考生视频", "Reference to video"), ("多图或主体参考保持角色一致，Q4 Preview、Q2、Q2 Pro 可用。", "Keep characters consistent with several images or subjects in Q4 Preview, Q2 and Q2 Pro.")),
                (pick(lang, "音画同出", "Native audio"), ("Q4 Preview 与 Q3 默认同时生成声音；Q2 可按次开启音视频直出。", "Q4 Preview and Q3 generate sound by default; Q2 can add native audio per task.")),
                (pick(lang, "540p 到 4K", "540p to 4K"), ("Q4 Preview 最高 4K，Q3 / Q2 最高 1080p，按秒计费。", "Q4 Preview reaches 4K; Q3 and Q2 reach 1080p, billed per second.")),
                (pick(lang, "图像生成", "Image generation"), ("Q2 Image 文生图与 1–7 张参考生图，最高 4K。", "Q2 Image handles text-to-image and 1–7-image references up to 4K."))]
        title = pick(lang, "一个 Key，覆盖视频与图像创作", "One key for video and image work")
    body = "".join(f'<article class="vd-feature"><span>{i:02d}</span><h3>{h(t)}</h3><p>{h(pick(lang, *d))}</p></article>' for i, (t, d) in enumerate(caps, 1))
    return section("capabilities", pick(lang, "能力", "CAPABILITIES"), title,
                   pick(lang, "把 Vidu 的生成能力直接接进你的产品和工作流。", "Put Vidu generation straight into your product and pipeline."),
                   f'<div class="vd-features">{body}</div>')


GALLERY = [("football", "图生视频 · 运动镜头", "Image to video · sports shot"),
           ("tiger", "Q4 · 特写质感", "Q4 · close-up detail"),
           ("skycity", "参考生视频 · 奇幻场景", "Reference video · fantasy scene"),
           ("warzone", "电影感 · 战争场面", "Cinematic · battle scene"),
           ("astronaut", "角色表演", "Character performance"),
           ("tarot", "室内光影", "Interior lighting")]


def gallery(lang, m):
    first = m["media"] if m else "football"
    order = [g for g in GALLERY if g[0] == first] + [g for g in GALLERY if g[0] != first]
    tiles = "".join(f'<figure class="vd-tile{" vd-tile-wide" if i == 0 else ""}">'
                    f'<video class="vd-clip" muted loop playsinline preload="none" poster="/assets/models/vidu/{k}.webp" aria-hidden="true"><source src="/assets/models/vidu/{k}.mp4" type="video/mp4"></video>'
                    f'<figcaption>{h(pick(lang, zh, en))}</figcaption></figure>' for i, (k, zh, en) in enumerate(order[:5]))
    return section("showcase", pick(lang, "官方示例", "SHOWCASE"), pick(lang, "Vidu 生成效果", "What Vidu generates"),
                   pick(lang, "以下片段来自 Vidu 官网公开示例，用于展示模型风格，不代表某一次调用的固定效果。",
                        "These clips are public samples from vidu.cn. They show the model's range, not a guaranteed result for any single request."),
                   f'<div class="vd-gallery">{tiles}</div>')


def cost_cards(lang, m):
    picks = []
    if m:
        for idx, n in m["costs"]:
            picks.append((m, idx, n))
    else:
        picks = [(MODEL_BY_SLUG["viduq2-turbo"], 0, 5), (MODEL_BY_SLUG["viduq3-pro"], 0, 10), (MODEL_BY_SLUG["vidu-image-q2"], 4, 10)]
    cards = []
    for x, idx, n in picks:
        p = x["prices"][idx]
        if p["unit_en"] == "image":
            cost = Decimal(p["amount"]) * n
            label = pick(lang, f'{n} 张 · {p["label_zh"]}', f'{n} images · {p["label_en"]}')
            calc = f'{n} × ${p["amount"]}'
        elif "first" in p:
            cost = clip_cost(p, n)
            label = pick(lang, f'{n} 秒 · {p["label_zh"]}', f'{n}-second clip · {p["label_en"]}')
            if p["second"]:
                calc = f'${p["second"]} + {n - 2} × ${p["add"]}'
            else:
                calc = f'${p["first"]} + {n - 1} × ${p["add"]}'
        else:
            cost = Decimal(p["amount"]) * n
            label = pick(lang, f'{n} 秒 · {p["label_zh"]}', f'{n}-second clip · {p["label_en"]}')
            calc = f'{n} × ${p["amount"]}'
        cards.append(f'<article class="vd-cost"><h3>{h(x["short"])} · {h(label)}</h3><p><code>{h(calc)}</code></p><strong>${money(cost)}</strong></article>')
    note = pick(lang, "示例按表内单价相加，不含音视频直出、推荐提示词等附加项。", "Examples add up the listed rates and exclude add-ons such as native audio or recommended prompts.")
    return f'<div class="vd-costs">{"".join(cards)}</div><p class="vd-note">{h(note)}</p>'


def pricing(lang, m):
    rows = []
    for x in ([m] if m else MODELS):
        rows.append(f'<tbody><tr class="vd-group"><th colspan="3" scope="rowgroup">{h(x["name"])} <span>{h(x["tag_" + lang])}</span></th></tr>')
        for p in x["prices"]:
            rows.append(f'<tr{" class=\"vd-addon\"" if p.get("addon") else ""}><th scope="row">{h(p["label_" + lang])}</th><td><code>{h(x["id"])}</code></td><td>{h(price_text(lang, p))}</td></tr>')
        rows.append('</tbody>')
    if m and m["id"] == "vidu-image-q2":
        points = [(pick(lang, "按张计费", "Per image"), pick(lang, "每成功生成 1 张图片计费一次。", "Each generated image is billed once.")),
                  (pick(lang, "参考图分档", "Reference tiers"), pick(lang, "0 张、1–3 张、4–7 张三档价格。", "Priced for 0, 1–3 and 4–7 reference images.")),
                  (pick(lang, "并发不限", "Unlimited concurrency"), pick(lang, "所有用户默认享有。", "On by default for every account.")),
                  (pick(lang, "余额通用", "Shared balance"), pick(lang, "一个 Key 调用 300+ 模型。", "One key works across 300+ models."))]
    else:
        points = [(pick(lang, "按秒计费", "Per second"), pick(lang, "费用随视频时长累加，一次调用产出 1 段视频。", "Cost grows with clip length; one call returns one video.")),
                  (pick(lang, "分辨率分档", "By resolution"), pick(lang, "清晰度越高单价越高，可先低清出样。", "Higher resolutions cost more, so draft low first.")),
                  (pick(lang, "并发不限", "Unlimited concurrency"), pick(lang, "所有用户默认享有。", "On by default for every account.")),
                  (pick(lang, "余额通用", "Shared balance"), pick(lang, "一个 Key 调用 300+ 模型。", "One key works across 300+ models."))]
    billing = '<ul class="vd-billing">' + "".join(f'<li><strong>{h(a)}</strong>{h(b)}</li>' for a, b in points) + '</ul>'
    note = pick(lang, "单位 USD，按成功提交计费，实时价格以模型广场为准。Q2 系列「第2秒 $x」为 2 秒视频的总价。",
                "Prices in USD, charged on successful submission; the model catalog shows current rates. For the Q2 family, “$x for 2 seconds” is the total for a 2-second clip.")
    table = (f'<div class="vd-table-wrap"><table class="vd-table"><caption>{pick(lang, "Vidu API 价格表", "Vidu API price table")}</caption>'
             f'<thead><tr><th scope="col">{pick(lang, "功能", "Operation")}</th><th scope="col">{pick(lang, "模型名", "Model")}</th><th scope="col">{pick(lang, "单价（USD）", "Price (USD)")}</th></tr></thead>'
             + "".join(rows) + '</table></div>')
    body = (billing + table + f'<p class="vd-note">{h(note)}</p>' + cost_cards(lang, m)
            + f'<div class="vd-actions">{button(pick(lang, "获取 API Key", "Get an API key"), REG)}'
              f'<a class="vd-link" href="{h(PRICING_URL)}">{pick(lang, "在模型广场查看", "View in the model catalog")} ↗</a></div>')
    title = pick(lang, f'{m["name"] if m else "Vidu"} API 价格', f'{m["name"] if m else "Vidu"} API pricing')
    return section("pricing", pick(lang, "价格", "PRICING"), title,
                   pick(lang, "按模型广场当前最低价展示，每一行写明计费方式。", "Current catalog rates, with the billing rule on every row."), body, soft=True)


# ---------------------------------------------------------------- code
def payload(lang, m):
    kind = m["example"] if m else "text2video"
    model = m["id"] if m else "viduq3-turbo"
    if kind == "text2video":
        return "/ent/v2/text2video", {"model": model, "prompt": pick(lang, *PROMPTS["text2video"]), "duration": 5,
                                      "resolution": "540p", "aspect_ratio": "16:9"}
    if kind == "img2video":
        res = "1080p" if model == "viduq4-preview" else "540p"
        return "/ent/v2/img2video", {"model": model, "images": [SAMPLE_IMAGE], "prompt": pick(lang, *PROMPTS["img2video"]),
                                     "duration": 5, "resolution": res}
    return "/ent/v2/reference2image", {"model": model, "images": [SAMPLE_IMAGE], "prompt": pick(lang, *PROMPTS["reference2image"]),
                                       "resolution": "1080p", "aspect_ratio": "16:9"}


PY = """import json
import os
import time
import urllib.request

BASE = "https://anyaigc.ai"
HEADERS = {
    "Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"],
    "Content-Type": "application/json",
}


def call(method, path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None
    request = urllib.request.Request(BASE + path, data=data, headers=HEADERS, method=method)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


payload = __BODY__

created = call("POST", "__PATH__", payload)
task_id = (created.get("data") or created)["task_id"]
print("task_id:", task_id)

__C1__
for _ in range(120):
    result = call("GET", f"/ent/v2/tasks/{task_id}/creations")
    state = (result.get("data") or result).get("state") or (result.get("data") or result).get("status")
    if state not in ("created", "queueing", "processing"):
        break
    time.sleep(10)

__C2__
print(json.dumps(result, ensure_ascii=False, indent=2))"""


def code_tabs(lang, m):
    path, body = payload(lang, m)
    curl = (f'# {pick(lang, "1. 创建任务，返回 task_id", "1. Create the task; the response contains task_id")}\n'
            f'curl -X POST "https://anyaigc.ai{path}" \\\n'
            '  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            f"  -d '{json.dumps(body, ensure_ascii=False, indent=2)}'\n\n"
            f'# {pick(lang, "2. 用 task_id 查询结果", "2. Fetch the result with the task_id")}\n'
            'curl "https://anyaigc.ai/ent/v2/tasks/$TASK_ID/creations" \\\n'
            '  -H "Authorization: Bearer $ANYAIGC_API_KEY"')
    py = (PY.replace("__BODY__", json.dumps(body, ensure_ascii=False, indent=4)).replace("__PATH__", path)
          .replace("__C1__", pick(lang, "# 每 10 秒查询一次，直到任务不再处于排队或处理中", "# Poll every 10 seconds until the task leaves the queue"))
          .replace("__C2__", pick(lang, "# creations 里是视频或图片地址，地址有时效，请及时下载", "# creations holds the video or image URLs; they expire, so download promptly")))
    tabs, panels = [], []
    for i, (label, code) in enumerate([("cURL", curl), ("Python", py)]):
        pid = f"vd-code-{i}"
        tabs.append(f'<button type="button" data-panel="{pid}" aria-selected="{"true" if i == 0 else "false"}">{label}</button>')
        panels.append(f'<div class="vd-code-panel" id="{pid}"{"" if i == 0 else " hidden"}><div class="vd-code-head"><span>{label}</span>'
                      f'<button class="vd-copy" type="button" data-copy="{pid}-src">{pick(lang, "复制", "Copy")}</button></div>'
                      f'<pre><code id="{pid}-src">{h(code)}</code></pre></div>')
    return f'<div class="vd-code-tabs">{"".join(tabs)}</div>{"".join(panels)}'


def quickstart(lang, m):
    steps = [pick(lang, "注册 AnyAIGC，在控制台创建 API Key。", "Sign up and create an API key in the console."),
             pick(lang, "把 Key 写进环境变量 ANYAIGC_API_KEY。", "Put the key in the ANYAIGC_API_KEY environment variable."),
             pick(lang, f"提交任务拿到 task_id，再轮询 {QUERY} 取结果。", f"Submit a task for a task_id, then poll {QUERY}.")]
    eps = [EP[e] for e in (m["endpoints"] if m else ["text2video", "img2video", "start-end2video", "reference2video", "reference2image"])]
    ep_list = "".join(f'<li><code>{h(e[0])}</code><span>{h(pick(lang, e[1], e[2]))}</span></li>' for e in eps)
    ep_list += f'<li><code>{h(QUERY)}</code><span>{pick(lang, "查询结果", "Fetch result")}</span></li>'
    doc = doc_url(lang, DOCS[m["example"]] if m else DOCS["text2video"])
    body = ('<ol class="vd-steps">' + "".join(f'<li><b>{i:02d}</b><span>{h(s)}</span></li>' for i, s in enumerate(steps, 1)) + '</ol>'
            f'<div class="vd-api"><ul class="vd-endpoints">{ep_list}</ul>'
            f'<a class="vd-link" href="{h(doc)}">{pick(lang, "阅读 API 文档", "Read the API reference")} ↗</a>'
            f'<a class="vd-link" href="{h(doc_url(lang, DOCS["creations"]))}">{pick(lang, "任务查询文档", "Task query reference")} ↗</a></div>'
            + code_tabs(lang, m)
            + f'<p class="vd-note">{h(pick(lang, "示例图片可换成你自己的 URL 或 Base64（png / jpeg / webp，≤50MB）。查询结果的状态字段以实际返回为准，示例在任务离开 created / queueing / processing 后停止轮询。", "Replace the sample image with your own URL or Base64 (png, jpeg or webp, up to 50 MB). Read the status field from the live response; the example stops polling once the task leaves created, queueing or processing."))}</p>')
    return section("quickstart", pick(lang, "快速开始", "QUICKSTART"), pick(lang, f'三步接入 {m["name"] if m else "Vidu"} API', f'Call {m["name"] if m else "Vidu"} in three steps'),
                   pick(lang, "从一个最小请求开始，跑通后再接进你的产品。", "Start with the smallest request, then wire it into your product."), body)


def uses(lang, m):
    image = m and m["id"] == "vidu-image-q2"
    scenes = ([("电商主图与海报", "Product shots and posters", "用商品或人物参考图批量出主图、海报和多尺寸素材。", "Batch product shots, posters and resized assets from product or model references."),
               ("角色设定与分镜", "Character sheets and boards", "多张参考图锁定角色形象，快速出分镜和设定图。", "Lock a character with several references, then draft boards and turnarounds."),
               ("视频首帧准备", "First frames for video", "先生成高质量静帧，再交给 Vidu 视频模型做图生视频。", "Generate a strong still first, then animate it with a Vidu video model.")]
              if image else
              [("短视频与广告", "Short-form and ads", "用一句话或一张图快速出镜头，先低清筛方向再高清成片。", "Turn a line or an image into shots; screen ideas at low resolution, finish in high."),
               ("动画与漫剧", "Animation and comics", "参考图保持角色一致，首尾帧控制每段的起止画面。", "References keep characters consistent and first/last frames pin each segment."),
               ("电商与产品展示", "E-commerce and products", "商品图直接图生视频，批量生成展示镜头。", "Animate product photos directly and generate showcase shots at scale.")])
    body = "".join(f'<article class="vd-feature"><span>0{i}</span><h3>{h(pick(lang, a, b))}</h3><p>{h(pick(lang, c, d))}</p></article>' for i, (a, b, c, d) in enumerate(scenes, 1))
    return section("use-cases", pick(lang, "使用场景", "USE CASES"), pick(lang, "从一个具体任务开始", "Start with a concrete task"),
                   pick(lang, "选对模型和输入方式，结果直接进入你的生产流程。", "Pick the right model and input, then send results straight into production."),
                   f'<div class="vd-features vd-features-3">{body}</div>')


def platform(lang):
    items = [("300+ 模型，一个 Key", "300+ models, one key", "同一个 API Key 和余额，视频、图像、对话模型随时切换。", "One API key and balance across video, image and chat models."),
             (pick(lang, "国内直连，并发不限", ""), "Unlimited concurrency", "通过 AnyAIGC 域名国内直接调用，Vidu 并发不限，所有用户默认享有。", "Vidu on AnyAIGC has no concurrency cap and no fixed RPM limit, for every account."),
             ("单价透明，按量付费", "Clear rates, pay as you go", "按秒或按张计费，控制台可查每次调用的扣费明细。", "Billed per second or per image, with every charge visible in the console.")]
    body = "".join(f'<article class="vd-feature"><span>0{i}</span><h3>{h(pick(lang, a or b, b))}</h3><p>{h(pick(lang, c, d))}</p></article>' for i, (a, b, c, d) in enumerate(items, 1))
    return section("platform", "AnyAIGC", pick(lang, "为什么通过 AnyAIGC 调用 Vidu", "Why call Vidu through AnyAIGC"),
                   pick(lang, "鉴权、余额、账单集中在一个平台，你只需要关心生成本身。", "Auth, balance and billing in one place, so you focus on generation."),
                   f'<div class="vd-features vd-features-3">{body}</div>', soft=True)


def enterprise(lang, name):
    cards = [(pick(lang, "增值税发票", "Invoices"), pick(lang, "普票、专票都能开（增值税普通发票 / 增值税专用发票），按实际充值金额开具。", "Invoices for every top-up, including Chinese VAT general and special invoices.")),
             (pick(lang, "对公转账", "Bank transfer"), pick(lang, "支持企业对公转账充值。", "Top up by corporate bank transfer.")),
             (pick(lang, "签订合同", "Contracts"), pick(lang, "可签订服务合同，配合采购与法务流程。", "Sign a service agreement for procurement and legal review.")),
             (pick(lang, "专属对接", "Dedicated support"), pick(lang, "专属客服和技术对接。", "A dedicated support and technical contact."))]
    body = "".join(f'<article><span>{i:02d}</span><h3>{h(t)}</h3><p>{h(d)}</p></article>' for i, (t, d) in enumerate(cards, 1))
    return section("enterprise", pick(lang, "企业接入", "ENTERPRISE"), pick(lang, f"企业接入 {name} API", f"{name} API for teams and enterprises"),
                   pick(lang, "研发、财务、法务和采购可以一起推进。", "Engineering, finance, legal and procurement can move together."),
                   f'<div class="vd-enterprise">{body}</div>{payments.pay_row(lang, "vd").strip()}'
                   f'<div class="vd-actions">{button(pick(lang, "联系企业客服", "Talk to sales"), SUPPORT)}{button(pick(lang, "先注册试用", "Start with a free account"), REG, True)}</div>', soft=True)


def trust_block(lang):
    items = "".join(f'<li><h3>{h(t)}</h3><p>{d}</p></li>' for t, d in trust.ITEMS[lang])
    return section("trust", pick(lang, "信任与保障", "TRUST"), trust.HEAD[lang][0], h(trust.HEAD[lang][1]),
                   f'<ul class="trust-list">{items}</ul><div class="vd-actions">{button(pick(lang, "先注册领取 200 万 tokens", "Sign up for 2M free tokens"), REG)}</div>')


def family(lang, slug):
    links = [f'<li><a href="/{lang}/models/vidu"{" aria-current=\"page\"" if slug == "vidu" else ""}><strong>Vidu API</strong><small>{pick(lang, "全系总览", "Overview")}</small></a></li>']
    for m in MODELS:
        cur = ' aria-current="page"' if m["slug"] == slug else ""
        links.append(f'<li><a href="/{lang}/models/{m["slug"]}"{cur}><strong>{h(m["name"])}</strong><small>{h(m["id"])} · ${m["start"]}</small></a></li>')
    return section("family", pick(lang, "同系列模型", "FAMILY"), pick(lang, "Vidu 全系模型", "All Vidu models"),
                   pick(lang, "按清晰度、速度和输入方式选择。", "Choose by resolution, speed and input type."),
                   f'<ul class="vd-family">{"".join(links)}</ul>')


def faq(lang, items, name):
    body = "".join(f'<details><summary><h3>{h(q)}</h3></summary><div class="vd-answer"><p>{h(a)}</p></div></details>' for q, a in items)
    return section("faq", "FAQ", pick(lang, f"{name} API 常见问题", f"{name} API FAQ"),
                   pick(lang, "价格、接口、结果和企业接入，一次说清楚。", "Pricing, endpoints, results and enterprise access in one place."),
                   f'<div class="vd-faq">{body}</div>')


def final(lang, slug, m):
    other = "en" if lang == "zh" else "zh"
    name = m["name"] if m else "Vidu"
    doc = doc_url(lang, DOCS[m["example"]] if m else DOCS["text2video"])
    links = [(f"/{lang}/models/", pick(lang, "全部模型专题", "All model guides")), (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
             (doc, pick(lang, "API 文档", "API documentation")), (f"/{other}/models/{slug}", pick(lang, "English 版本", "中文版"))]
    if m:
        links.insert(1, (f"/{lang}/models/vidu", pick(lang, "Vidu 全系总览", "Vidu overview")))
    ll = "".join(f'<li><a href="{h(u)}"{" hreflang=\"" + pick(other, "zh-CN", "en") + "\"" if u.startswith("/" + other + "/") else ""}>{h(t)}</a></li>' for u, t in links)
    return (f'<section class="vd-final" aria-labelledby="final-title"><div class="vd-wrap">{logo("final", 44)}'
            f'<h2 id="final-title">{h(pick(lang, f"把 {name} 接进你的下一个作品", f"Put {name} into your next project"))}</h2>'
            f'<p>{h(pick(lang, "注册 AnyAIGC，一个 API Key 调用 300+ 模型。", "Sign up for AnyAIGC and call 300+ models with one API key."))}</p>'
            f'<div class="vd-actions">{button(pick(lang, "获取 API Key", "Get an API key"), REG)}{button(pick(lang, "查看模型广场", "Open the model catalog"), PRICING_URL, True)}</div>'
            f'<ul class="vd-final-links">{ll}</ul></div></section></main>\n'
            f'<footer class="vd-footer"><div class="vd-wrap"><a class="vd-brand" href="/">AnyAIGC<span>{logo("foot", 18)}Vidu</span></a>'
            f'<nav aria-label="{pick(lang, "页脚", "Footer")}"><a href="/{lang}/models/">{pick(lang, "模型专题", "Model guides")}</a><a href="{PRICING_URL}">{pick(lang, "模型广场", "Model catalog")}</a>'
            f'<a href="https://anyaigc.ai/console">{pick(lang, "控制台", "Console")}</a><a href="/privacy">{pick(lang, "隐私政策", "Privacy")}</a><a href="/terms">{pick(lang, "服务条款", "Terms")}</a></nav>'
            f'<p class="vd-legal">{h(pick(lang, "Vidu 是生数科技（ShengShu Technology）的商标，AnyAIGC 是独立 API 服务商，与其无隶属关系。示例视频来自 Vidu 官网公开素材。模型许可与商用条款以 Vidu 官方条款为准。", "Vidu is a trademark of ShengShu Technology. AnyAIGC is an independent API provider and is not affiliated with ShengShu. Sample clips are public material from vidu.cn. Model licenses and commercial terms follow Vidu official terms."))}</p></div></footer>\n')


def render(lang, slug):
    m = MODEL_BY_SLUG.get(slug)
    items = faq_items(lang, m)
    name = m["name"] if m else "Vidu"
    html = head(lang, slug, m, items) + nav(lang, slug, m) + hero(lang, slug, m)
    if not m:
        html += lineup(lang)
    html += (capabilities(lang, m) + gallery(lang, m) + pricing(lang, m) + uses(lang, m) + platform(lang) + quickstart(lang, m)
             + enterprise(lang, name) + trust_block(lang) + family(lang, slug) + faq(lang, items, name) + final(lang, slug, m))
    return html + f'<script src="/assets/models/vidu.js?v={VER}" defer></script>\n</body>\n</html>\n'


def main():
    for lang in ("zh", "en"):
        for slug in SLUGS:
            (ROOT / lang / "models" / f"{slug}.html").write_text(render(lang, slug), encoding="utf-8", newline="\n")
            print(lang, slug)


if __name__ == "__main__":
    main()
