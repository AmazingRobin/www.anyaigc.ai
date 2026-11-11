"""Build the Kling Image 3.0 topic pages and register them in the Kling family.

Run: python scripts/kling_image.py   (re-running gives the same result)

Facts (checked 2026-11-11, catalog detail view of aigc-image-kling and docs
leaf=398427541 / 398427540):
- Catalog id aigc-image-kling, $0.00169 per call, one image per call,
  2K and 4K at the same price (confirmed by the user).
- POST /tencent-vod/v1/aigc-image with model_name "Kling", model_version "3.0"
  (the docs list only GEM/Qwen/Hunyuan; Kling/3.0 confirmed by the user),
  output_config.resolution must be upper-case "2K" or "4K".
- Result: GET /tencent-vod/v1/query/{task_id}; Status FINISH,
  Response.AigcImageTask.Output.FileInfos[].FileUrl (temporary storage).

The Kling pages are hand-written single-line HTML; this script writes the two
new pages from scratch in the same k-* markup and patches the family list in
the other Kling pages, the Kling overview, both model hubs and the sitemap.
"""

import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.anyaigc.ai"
REG = "https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9"
SUPPORT = "https://anyaigc.ai/customersupport"
PRICING = "https://anyaigc.ai/pricing"
SLUG = "kling-image-3.0"
MODEL = "aigc-image-kling"
PRICE = "0.00169"
DATE = "2026-11-11"
VER = "20261106"
DOC = {"zh": "https://docs.anyaigc.ai/reference/tencent-vod/v1/aigc-image?leaf=398427541",
       "en": "https://docs.anyaigc.ai/en/reference/tencent-vod/v1/aigc-image?leaf=398427541"}
DOC_QUERY = {"zh": "https://docs.anyaigc.ai/reference/tencent-vod/v1/query/%7Btask_id%7D?leaf=398427540",
             "en": "https://docs.anyaigc.ai/en/reference/tencent-vod/v1/query/%7Btask_id%7D?leaf=398427540"}

T = {
    "zh": dict(
        title="Kling Image 3.0 API 价格与接入｜可灵图片 2K/4K - AnyAIGC",
        desc=f"可灵图片 Kling Image 3.0 API：${PRICE}/张，2K、4K 同价直出，支持文生图、图生图、多图参考与局部重绘，并发不限，支持对公转账和增值税专票。",
        keywords="Kling Image 3.0 API,可灵图片 API,Kling Image API 价格,Kling API key,Kling Image API 企业,Kling Image API 发票,可灵 API",
        h1="Kling Image 3.0 API",
        eyebrow="可灵 · AI 图像",
        lead=f"可灵图片 3.0 是快手自研的高清图像生成模型，支持文生图、图生图、多图参考、风格转绘、人像/角色参考和局部重绘，2K/4K 直出。在 AnyAIGC 上每张 <strong>${PRICE}</strong>，并发不限。",
        cta="获取 API Key", price_btn="价格",
        facts=[("模型", f"<code>{MODEL}</code>"), ("价格", f"${PRICE} / 张"), ("分辨率", "2K / 4K 同价"), ("对公 · 专票", "支持")],
        cap_kicker="MODEL CAPABILITIES", cap_h2="可灵图片 3.0 能做什么",
        cap_p="以下按模型广场和接口文档当前公开信息整理，调用参数以 API 文档为准。",
        caps=[("文生图", "用文字描述画面、光影和材质，直接生成 2K 或 4K 成图。"),
              ("图生图与风格转绘", "传入原图，按提示词改写画面内容或转换为其他风格。"),
              ("多图参考", "同时参考多张图片的主体、构图或风格，组合出新画面。"),
              ("人像 / 角色参考", "以参考图保持人物或角色外观，适合系列化内容。"),
              ("局部重绘", "只修改画面中的一部分，其余内容保持不变。"),
              ("2K / 4K 直出", "resolution 填大写 \"2K\" 或 \"4K\"，两种分辨率同一个价格。")],
        use_h2="适用场景",
        uses=[("影视分镜与概念原画", "按镜头描述快速出分镜和概念图，先确定画面方向。"),
              ("电商海报与主图", "用产品图做参考，批量生成不同场景和风格的海报。"),
              ("商业插画", "保持角色和画风一致，生成系列插画素材。")],
        price_h2="Kling Image 3.0 API 价格",
        billing=[("按张计费", "一次调用生成 1 张图"), ("2K / 4K 同价", f"每张 ${PRICE}"), ("并发不限", "所有用户默认享有"), ("余额通用", "一个 Key 调用 300+ 模型")],
        th=("功能", "模型名", "单价（USD）"),
        rows=[("文生图 / 图生图（2K）", f"${PRICE} / 张"), ("文生图 / 图生图（4K）", f"${PRICE} / 张")],
        note="单位 USD，按成功提交计费；实时价格以模型广场为准。",
        cost_h2="成本示例",
        costs=[("100 张 2K 图", f"100 × ${PRICE}", "$0.169"), ("1,000 张 4K 图", f"1,000 × ${PRICE}", "$1.69")],
        catalog="在模型广场查看",
        qs_h2="接入 Kling Image 3.0 API",
        steps=["注册 AnyAIGC 并创建 API Key，放进 ANYAIGC_API_KEY 环境变量", "POST /tencent-vod/v1/aigc-image 提交任务，拿到 TaskId", "GET /tencent-vod/v1/query/{task_id} 轮询，Status 为 FINISH 后下载图片"],
        qs_note="请求里 model_name 填 \"Kling\"，model_version 填 \"3.0\"，output_config.resolution 必须是大写的 \"2K\" 或 \"4K\"。结果在 Response.AigcImageTask.Output.FileInfos[].FileUrl，为临时存储，有过期时间，请及时下载。",
        doc_link="阅读接口文档", query_link="查看任务查询文档",
        prompt="一只橘猫坐在雨后的窗台上，窗外是霓虹灯街道，电影感光影，细节丰富",
        poll="# 每 5 秒查询一次，Status 为 FINISH 后打印图片地址",
        ent_h2="企业接入 Kling Image 3.0 API",
        ent_p="面向采购、财务、法务和技术团队提供清晰的企业服务流程。",
        ent=[("增值税发票", "普票、专票都能开", "按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。"),
             ("对公转账", "公司账户直接付款", "支持企业对公转账充值，无需个人垫付，账目清晰。"),
             ("签订合同", "满足采购与法务流程", "可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。"),
             ("专属对接", "客服与技术支持", "提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。")],
        pay_label="支持的支付方式", pay="微信支付 · 支付宝 · USDT · 信用卡 · 对公转账",
        sales="联系企业客服", trial="先注册试用",
        trust_h2="为什么可以放心用 AnyAIGC",
        trust=["注册送 200 万 tokens 试用额度", "$1 起充，未使用余额可退款，无手续费", "请求走官方模型渠道，不掺假不降智",
               '除法律法规要求外，输入输出不做持久化存储、不用于训练（<a href="/privacy">隐私政策</a>）',
               "控制台可查每次调用明细，可给每个 Key 设额度上限", f'7×24 <a href="{SUPPORT}">客服</a>'],
        trust_cta="先注册领取 200 万 tokens",
        fam_h2="同系列模型怎么选",
        fam_p="按任务选择模型：先确定是图片、视频生成、控制、声音还是素材资产，再比较模式和价格。",
        faq_h2="Kling Image 3.0 API 常见问题",
        faq=[("Kling Image 3.0 API 多少钱？", f"每次调用 ${PRICE}，生成 1 张图，2K 和 4K 同价。单位 USD，按成功提交计费，实时价格以模型广场为准。"),
             ("应该调用哪个接口？", "提交任务用 POST /tencent-vod/v1/aigc-image，body 里 model_name 填 Kling、model_version 填 3.0；查询结果用 GET /tencent-vod/v1/query/{task_id}。API 域名为 https://anyaigc.ai，请求头 Authorization: Bearer <API Key>。"),
             ("分辨率怎么设置？", "在 output_config.resolution 里填大写的 \"2K\" 或 \"4K\"，两种分辨率价格相同。"),
             ("支持哪些生成方式？", "支持文生图、图生图、多图参考、风格转绘、人像/角色参考和局部重绘。参考图通过 file_infos 传入，具体字段以接口文档为准。"),
             ("结果怎么获取？", "接口是异步的：提交后返回 Response.TaskId，轮询查询接口，Status 为 FINISH 时从 Response.AigcImageTask.Output.FileInfos[].FileUrl 下载图片。文件为临时存储，有过期时间。"),
             ("并发有限制吗？", "AnyAIGC 的 Kling 系列默认并发不限，所有用户都可以直接使用。"),
             ("生成内容可以商用吗？", "生成内容的使用权和内容政策以快手可灵官方条款为准。使用参考图时，也应具备相关权利或授权。"),
             ("AnyAIGC 能开发票吗？支持增值税专票吗？", "支持。可按实际充值金额开具增值税普通发票和增值税专用发票，联系企业客服办理即可。"),
             ("企业可以对公转账和签合同吗？", "可以。支持企业对公转账充值，可签订服务合同，并提供专属客服与技术对接。"),
             ("支持哪些支付方式？", "支持微信支付、支付宝、USDT 和信用卡充值，企业还可以对公转账，并开具增值税普通发票或专用发票。余额按美元计价，对平台所有模型通用。"),
             ("新用户有免费试用额度吗？", "有。新用户注册后赠送 200 万 tokens 的试用额度，可以先测试效果再决定是否充值。最低 1 美元起充。"),
             ("余额可以退款吗？", "可以。未使用的余额可以申请退款，不收取手续费。具体流程请联系客服。"),
             ("会不会用低配模型冒充？我的数据安全吗？", "请求走官方模型渠道，不用低配或逆向模型冒充。除法律法规要求外，我们不会对你的输入输出内容做持久化存储，也不会用于训练模型；控制台可以查看每次调用的扣费明细。")],
        final_h2="开始调用 Kling Image 3.0", final_p="注册即送 200 万 tokens 试用额度。",
        links=[("Kling 全系总览", "/zh/models/kling"), ("全部模型专题", "/zh/models/"), ("模型广场", PRICING), ("English", f"/en/models/{SLUG}")],
        nav=["模型专题", "模型广场", "价格", "企业接入", "API 文档"], other="English",
        foot_brand="国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。",
        foot=[("产品", [("模型专题", "/zh/models/"), ("模型广场", PRICING), ("控制台", "https://anyaigc.ai/console")]),
              ("资源", [("API 文档 ↗", DOC["zh"]), ("Kling 官方开发者平台 ↗", "https://kling.ai/dev"), ("联系我们", SUPPORT)]),
              ("条款", [("隐私政策", "/privacy"), ("服务条款", "/terms")])],
        legal="© 2026 AnyAIGC。Kling、可灵是快手的商标。AnyAIGC 是独立 API 服务商，与快手可灵无隶属关系。商用授权以快手可灵官方条款为准。",
        crumbs=["首页", "模型专题", "Kling", "Kling Image 3.0"],
        fam_name="Kling Image 3.0", fam_sub="可灵图片 · 2K/4K 文生图与图生图",
        hub_desc="可灵图片 3.0，2K/4K 文生图与图生图", hub_tags=["图片", "2K / 4K", "并发不限"], hub_price=f"${PRICE} / 张",
        copy="复制",
    ),
    "en": dict(
        title="Kling Image 3.0 API Pricing | 2K/4K Images - AnyAIGC",
        desc=f"Kling Image 3.0 API at ${PRICE} per image, 2K or 4K at one price. Text-to-image, image editing, multi-image reference. Unlimited concurrency, VAT invoices.",
        keywords="Kling Image 3.0 API,Kling Image API,Kling Image API pricing,Kling API key,Kling Image API for business,Kling API",
        h1="Kling Image 3.0 API",
        eyebrow="Kling · AI image",
        lead=f"Kling Image 3.0 is Kuaishou's high-resolution image model for text-to-image, image-to-image, multi-image reference, style transfer, character reference and inpainting, rendering 2K or 4K directly. On AnyAIGC it costs <strong>${PRICE}</strong> per image with unlimited concurrency.",
        cta="Get an API key", price_btn="Pricing",
        facts=[("Model", f"<code>{MODEL}</code>"), ("Price", f"${PRICE} / image"), ("Resolution", "2K / 4K, same price"), ("Contracts · invoices", "Available")],
        cap_kicker="MODEL CAPABILITIES", cap_h2="What Kling Image 3.0 can do",
        cap_p="Summarized from the current model catalog and API reference. Use the API docs for exact parameters.",
        caps=[("Text-to-image", "Describe the scene, lighting and materials and get a finished 2K or 4K image."),
              ("Image-to-image and style transfer", "Send a source image and rewrite its content or restyle it with a prompt."),
              ("Multi-image reference", "Combine the subject, composition or style of several images into a new one."),
              ("Character reference", "Keep a person or character consistent across a series of images."),
              ("Inpainting", "Change one part of the image and leave the rest untouched."),
              ("Native 2K / 4K", "Set resolution to upper-case \"2K\" or \"4K\". Both cost the same.")],
        use_h2="Use cases",
        uses=[("Storyboards and concept art", "Turn shot descriptions into storyboards and concept frames to lock the look early."),
              ("Product posters", "Use a product photo as reference and generate posters in different scenes and styles."),
              ("Commercial illustration", "Keep characters and art style consistent across an illustration series.")],
        price_h2="Kling Image 3.0 API pricing",
        billing=[("Per image", "One call returns one image"), ("2K / 4K, one price", f"${PRICE} per image"), ("Unlimited concurrency", "For every account"), ("Shared balance", "One key for 300+ models")],
        th=("Operation", "Model", "Unit price (USD)"),
        rows=[("Text/image-to-image (2K)", f"${PRICE} / image"), ("Text/image-to-image (4K)", f"${PRICE} / image")],
        note="Prices in USD, charged on successful submission. See the model catalog for current prices.",
        cost_h2="Cost examples",
        costs=[("100 images at 2K", f"100 × ${PRICE}", "$0.169"), ("1,000 images at 4K", f"1,000 × ${PRICE}", "$1.69")],
        catalog="View in the model catalog",
        qs_h2="Integrate the Kling Image 3.0 API",
        steps=["Sign up, create an API key and set ANYAIGC_API_KEY", "POST /tencent-vod/v1/aigc-image to submit a task and get its TaskId", "Poll GET /tencent-vod/v1/query/{task_id} and download the image once Status is FINISH"],
        qs_note="Set model_name to \"Kling\", model_version to \"3.0\", and output_config.resolution to upper-case \"2K\" or \"4K\". The result is at Response.AigcImageTask.Output.FileInfos[].FileUrl; it is temporary storage with an expiry time, so download it promptly.",
        doc_link="Read the API reference", query_link="See task-query documentation",
        prompt="An orange cat on a rain-soaked windowsill, a neon-lit street outside, cinematic lighting, rich detail",
        poll="# Poll every 5 seconds; print the image URL once Status is FINISH",
        ent_h2="Kling Image 3.0 API for teams and enterprises",
        ent_p="A clear process for procurement, finance, legal and engineering teams.",
        ent=[("Invoices", "Including VAT special invoices", "Invoices for every top-up, including Chinese VAT general and special invoices."),
             ("Bank transfer", "Pay from a company account", "Top up by corporate bank transfer, with no personal card needed."),
             ("Contracts", "Fits procurement and legal review", "Sign a service agreement with AnyAIGC."),
             ("Dedicated support", "Account and technical contact", "A dedicated support and technical contact for integration and day-to-day questions.")],
        pay_label="Payment methods", pay="WeChat Pay · Alipay · USDT · Credit card · Bank transfer",
        sales="Talk to sales", trial="Start with a free account",
        trust_h2="Why teams trust AnyAIGC",
        trust=["2M free tokens for new accounts", "Top up from $1; unused balance refundable, no fee", "Official model channels, no substitutes",
               'No persistent storage of prompts or outputs, no training (<a href="/privacy">privacy policy</a>)',
               "Per-request usage log and per-key spend caps", f'24/7 <a href="{SUPPORT}">support</a>'],
        trust_cta="Sign up for 2M free tokens",
        fam_h2="Choose a Kling model",
        fam_p="Pick by task first, whether that is images, video generation, control, audio or assets, then compare modes and prices.",
        faq_h2="Kling Image 3.0 API FAQ",
        faq=[("How much does the Kling Image 3.0 API cost?", f"${PRICE} per call, which returns one image, at 2K or 4K for the same price. Prices are in USD, charged on successful submission; see the model catalog for current rates."),
             ("Which endpoint should I call?", "Submit with POST /tencent-vod/v1/aigc-image, setting model_name to Kling and model_version to 3.0, and fetch results with GET /tencent-vod/v1/query/{task_id}. The API host is https://anyaigc.ai and the header is Authorization: Bearer <API Key>."),
             ("How do I set the resolution?", "Set output_config.resolution to upper-case \"2K\" or \"4K\". Both cost the same."),
             ("Which generation modes are supported?", "Text-to-image, image-to-image, multi-image reference, style transfer, character reference and inpainting. Reference images go in file_infos; see the API reference for the exact fields."),
             ("How do I get the result?", "The API is asynchronous. Submission returns Response.TaskId; poll the query endpoint and, once Status is FINISH, download the image from Response.AigcImageTask.Output.FileInfos[].FileUrl. Files are stored temporarily and expire."),
             ("Are there concurrency limits?", "Kling models on AnyAIGC have unlimited concurrency by default for every account."),
             ("Can I use the images commercially?", "Usage rights and content policy follow Kuaishou Kling's official terms. Make sure you have the rights to any reference images you upload."),
             ("Can AnyAIGC issue invoices, including VAT special invoices?", "Yes. AnyAIGC issues invoices for actual top-ups, including Chinese VAT general and VAT special invoices. Contact enterprise support to arrange them."),
             ("Can my company pay by bank transfer and sign a contract?", "Yes. Companies can top up by corporate bank transfer, sign a service agreement, and work with a dedicated support and technical contact."),
             ("Which payment methods are supported?", "You can top up with WeChat Pay, Alipay, USDT or a credit card. Companies can also pay by bank transfer and get VAT general or special invoices. Your balance is in USD and works across every model on the platform."),
             ("Is there free trial credit for new users?", "Yes. New accounts get 2 million tokens of trial credit, so you can test before deciding to top up. Top-ups start at $1."),
             ("Can I get a refund on my balance?", "Yes. Unused balance can be refunded with no fee. Contact support to start a refund."),
             ("Are these the real models? Is my data safe?", "Requests go to official model channels, never cheaper or reverse-engineered substitutes. Unless the law requires it, we do not persistently store your prompts or outputs or use them for training, and the console shows the cost of every request.")],
        final_h2="Start using Kling Image 3.0", final_p="Sign up and get 2M trial tokens.",
        links=[("All Kling models", "/en/models/kling"), ("All model guides", "/en/models/"), ("Model catalog", PRICING), ("中文", f"/zh/models/{SLUG}")],
        nav=["Models", "Model catalog", "Pricing", "Enterprise", "API docs"], other="中文",
        foot_brand="API access to 300+ models through one Base URL and one API key.",
        foot=[("Product", [("Model guides", "/en/models/"), ("Model catalog", PRICING), ("Console", "https://anyaigc.ai/console")]),
              ("Resources", [("API docs ↗", DOC["en"]), ("Kling developer platform ↗", "https://kling.ai/dev"), ("Contact us", SUPPORT)]),
              ("Legal", [("Privacy", "/privacy"), ("Terms", "/terms")])],
        legal="© 2026 AnyAIGC. Kling is a trademark of Kuaishou. AnyAIGC is an independent API provider and is not affiliated with Kuaishou Kling. Commercial use follows Kling's official terms.",
        crumbs=["Home", "Model guides", "Kling", "Kling Image 3.0"],
        fam_name="Kling Image 3.0", fam_sub="Kling image · 2K/4K text and image-to-image",
        hub_desc="Kling Image 3.0: 2K/4K text-to-image and image editing", hub_tags=["Image", "2K / 4K", "Unlimited concurrency"], hub_price=f"${PRICE} / image",
        copy="Copy",
    ),
}


EXT = ' target="_blank" rel="noopener"'


def h(v):
    return escape(str(v), quote=True)


def strip(v):
    return re.sub(r"<[^>]+>", "", v)


def payload(lang):
    return {"model_name": "Kling", "model_version": "3.0", "prompt": T[lang]["prompt"],
            "output_config": {"aspect_ratio": "16:9", "resolution": "2K"}}


def curl(lang):
    body = json.dumps(payload(lang), ensure_ascii=False, indent=2)
    return ('curl --request POST "https://anyaigc.ai/tencent-vod/v1/aigc-image" \\\n'
            '  --header "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
            '  --header "Content-Type: application/json" \\\n'
            f"  --data '{body}'\n\n"
            + ("# 用返回的 Response.TaskId 查询结果\n" if lang == "zh" else "# Query the result with the returned Response.TaskId\n")
            + 'curl "https://anyaigc.ai/tencent-vod/v1/query/$TASK_ID" \\\n'
            '  --header "Authorization: Bearer $ANYAIGC_API_KEY"')


PY = '''import json
import os
import time
import urllib.request

BASE = "https://anyaigc.ai"
HEADERS = {
    "Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"],
    "Content-Type": "application/json",
}


def call(method, path, payload=None):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None
    request = urllib.request.Request(BASE + path, data=data, headers=HEADERS, method=method)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


payload = __BODY__

task_id = call("POST", "/tencent-vod/v1/aigc-image", payload)["Response"]["TaskId"]
print("task_id:", task_id)

__COMMENT__
for _ in range(60):
    result = call("GET", f"/tencent-vod/v1/query/{task_id}")["Response"]
    if result["Status"] == "FINISH":
        break
    time.sleep(5)
else:
    raise TimeoutError(task_id)

for item in result["AigcImageTask"]["Output"]["FileInfos"]:
    print(item["FileUrl"])'''


def python(lang):
    return PY.replace("__BODY__", json.dumps(payload(lang), ensure_ascii=False, indent=4)).replace("__COMMENT__", T[lang]["poll"])


def family_items():
    """Read the Kling family list from an existing page and add this model first."""
    out = {}
    for lang in ("zh", "en"):
        src = (ROOT / lang / "models" / "kling-video-v4.html").read_text(encoding="utf-8")
        ul = re.search(r'<section class="k-section k-family" id="family">.*?<ul>(.*?)</ul>', src, re.S).group(1)
        items = re.findall(r'<li class="[^"]*"><a href="/\w+/models/([^"]+)"><strong>(.*?)</strong><span>(.*?)</span></a></li>', ul)
        items = [i for i in items if i[0] != SLUG]
        t = T[lang]
        out[lang] = [(SLUG, t["fam_name"], t["fam_sub"])] + items
    return out


def family_html(lang, current, items):
    lis = "".join(f'<li class="{"is-current" if s == current else ""}"><a href="/{lang}/models/{s}"><strong>{n}</strong><span>{d}</span></a></li>' for s, n, d in items)
    return f"<ul>{lis}</ul>"


def page(lang, fam):
    t = T[lang]
    other = "en" if lang == "zh" else "zh"
    me = f"{SITE}/{lang}/models/{SLUG}"
    img = f"{SITE}/assets/og/{SLUG}-{lang}.png"
    crumb_urls = [f"{SITE}/", f"{SITE}/{lang}/models/", f"{SITE}/{lang}/models/kling", me]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": f"{SITE}/#org", "name": "AnyAIGC", "url": "https://anyaigc.ai", "logo": f"{SITE}/logo.webp"},
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "AnyAIGC"},
        {"@type": "WebPage", "@id": me + "#webpage", "url": me, "name": t["title"], "description": t["desc"], "inLanguage": "zh-CN" if lang == "zh" else "en", "dateModified": DATE},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(zip(t["crumbs"], crumb_urls), 1)]},
        {"@type": "Product", "@id": me + "#product", "name": "Kling Image 3.0 API (AnyAIGC)", "description": t["desc"], "sku": MODEL, "image": img, "brand": {"@type": "Brand", "name": "Kling"},
         "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": PRICE, "highPrice": PRICE, "offerCount": 2, "url": me + "#pricing",
                    "offers": [{"@type": "Offer", "name": f"{MODEL} {r[0]}", "price": PRICE, "priceCurrency": "USD", "url": me + "#pricing"} for r in t["rows"]]}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]},
    ]}
    nav_href = [f"/{lang}/models/", PRICING, "#pricing", "#enterprise", DOC[lang]]
    facts = "".join(f"<li>{k} <b>{v}</b></li>" for k, v in t["facts"])
    caps = "".join(f"<article><h3>{h(a)}</h3><p>{h(b)}</p></article>" for a, b in t["caps"])
    uses = "".join(f"<article><span>0{i}</span><h3>{h(a)}</h3><p>{h(b)}</p></article>" for i, (a, b) in enumerate(t["uses"], 1))
    billing = "".join(f"<li><strong>{h(a)}</strong> {h(b)}</li>" for a, b in t["billing"])
    rows = "".join(f'<tr><td>{h(a)}</td><td><code>{MODEL}</code></td><td>{h(b)}</td></tr>' for a, b in t["rows"])
    costs = "".join(f"<li><strong>{h(a)}</strong><b>{h(c)}</b><span><code>{h(b)}</code></span></li>" for a, b, c in t["costs"])
    steps = "".join(f"<li><b>{i}</b>{h(s)}</li>" for i, s in enumerate(t["steps"], 1))
    tabs = [("cURL", curl(lang)), ("Python", python(lang))]
    code = "".join(f'<p class="k-kicker">{n}</p><pre><code>{h(c)}</code></pre>' for n, c in tabs)
    ent = "".join(f"<article><span>{h(a)}</span><h3>{h(b)}</h3><p>{h(c)}</p></article>" for a, b, c in t["ent"])
    trust = "".join(f"<li>{x}</li>" for x in t["trust"])
    faq = "".join(f'<details><summary><h3>{h(q)}</h3></summary><div class="k-answer"><p>{h(a)}</p></div></details>' for q, a in t["faq"])
    crumbs = "".join(f'<li><a href="{u.removeprefix(SITE)}">{h(n)}</a></li>' for n, u in zip(t["crumbs"][:-1], crumb_urls[:-1])) + f'<li aria-current="page">{h(t["crumbs"][-1])}</li>'
    links = "".join(f'<li><a href="{h(u)}"{" hreflang=" + chr(34) + ("en" if lang == "zh" else "zh-CN") + chr(34) if u.startswith("/" + other) else ""}>{h(n)}</a></li>' for n, u in t["links"])
    foot = "".join(f'<div><h2>{h(g)}</h2><ul>' + "".join(f'<li><a href="{h(u)}"{EXT if ("docs." in u or "kling.ai" in u) else ""}>{h(n)}</a></li>' for n, u in items) + "</ul></div>" for g, items in t["foot"])
    return f'''<!DOCTYPE html>
<html lang="{"zh-CN" if lang == "zh" else "en"}" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(t["title"])}</title>
<meta name="description" content="{h(t["desc"])}">
<meta name="keywords" content="{h(t["keywords"])}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{SLUG}">
<link rel="alternate" hreflang="en" href="{SITE}/en/models/{SLUG}">
<link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{SLUG}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{"zh_CN" if lang == "zh" else "en_US"}">
<meta property="og:locale:alternate" content="{"en_US" if lang == "zh" else "zh_CN"}">
<meta property="og:url" content="{me}">
<meta property="og:title" content="{h(t["title"])}">
<meta property="og:description" content="{h(t["desc"])}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AnyAIGC Kling Image 3.0 API">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{h(t["title"])}">
<meta name="twitter:description" content="{h(t["desc"])}">
<meta name="twitter:image" content="{img}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v={VER}">
<link rel="stylesheet" href="/assets/models/kling.css?v={VER}">
<link rel="stylesheet" href="/assets/models/kling-image.css?v=20261111">
<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<header class="k-nav"><a class="k-brand" href="/">AnyAIGC</a><nav>{"".join(f'<a href="{h(u)}">{n}</a>' for n, u in zip(t["nav"], nav_href))}</nav><div><a href="/{other}/models/{SLUG}" hreflang="{"en" if lang == "zh" else "zh-CN"}">{t["other"]}</a><a class="k-btn" href="{h(REG)}">{t["cta"]}</a></div></header>
<main>
<section class="k-hero k-hero-solo"><div class="k-hero-copy"><nav aria-label="breadcrumb"><ol class="k-crumbs">{crumbs}</ol></nav><p class="k-eyebrow"><img src="/assets/icons/kling.svg" alt="Kling" width="28" height="28"> {t["eyebrow"]}</p><h1>{t["h1"]}</h1><p class="k-lead">{t["lead"]}</p><div class="k-actions"><a class="k-btn" href="{h(REG)}">{t["cta"]}</a><a class="k-btn k-light" href="#pricing">{t["price_btn"]}</a></div><ul class="k-facts">{facts}</ul></div><div class="k-image-art" aria-hidden="true"><span></span><span></span><span></span><span></span><b>2K · 4K</b></div></section>
<section class="k-section" id="capabilities"><div class="k-section-intro"><p class="k-kicker">{t["cap_kicker"]}</p><h2>{h(t["cap_h2"])}</h2><p>{h(t["cap_p"])}</p></div><div class="k-detail-grid k-detail-grid-6">{caps}</div></section>
<section class="k-section k-use-cases" id="use-cases"><p class="k-kicker">USE CASES</p><h2>{h(t["use_h2"])}</h2><div class="k-use-grid">{uses}</div></section>
<section class="k-section" id="pricing"><p class="k-kicker">PRICING</p><h2>{h(t["price_h2"])}</h2><ul class="k-billing">{billing}</ul><div class="k-table-wrap"><table><thead><tr><th>{t["th"][0]}</th><th>{t["th"][1]}</th><th>{t["th"][2]}</th></tr></thead><tbody>{rows}</tbody></table></div><p class="k-note">{h(t["note"])}</p><div class="k-costs"><h3>{h(t["cost_h2"])}</h3><ul>{costs}</ul></div><div class="k-actions"><a class="k-btn" href="{h(REG)}">{t["cta"]}</a><a class="k-btn k-light" href="{PRICING}">{t["catalog"]} ↗</a></div></section>
<section class="k-section" id="quickstart"><p class="k-kicker">QUICKSTART</p><h2>{h(t["qs_h2"])}</h2><ol class="k-steps">{steps}</ol><div class="k-api-note"><p>{h(t["qs_note"])}</p><p><a href="{DOC[lang]}">{t["doc_link"]} ↗</a> · <a href="{DOC_QUERY[lang]}">{t["query_link"]} ↗</a></p></div>{code}</section>
<section class="k-section k-enterprise" id="enterprise"><div class="k-section-intro"><p class="k-kicker">ENTERPRISE</p><h2>{h(t["ent_h2"])}</h2><p>{h(t["ent_p"])}</p></div><div class="k-enterprise-grid">{ent}</div><div class="pay-row" role="group" aria-label="{t["pay_label"]}">{t["pay_label"]}：{t["pay"]}</div><div class="k-enterprise-actions"><a class="k-btn" href="{SUPPORT}">{t["sales"]}</a><a class="k-btn k-light" href="{h(REG)}">{t["trial"]}</a></div></section>
<section class="k-section" id="trust"><p class="k-kicker">TRUST</p><h2>{h(t["trust_h2"])}</h2><ul class="trust-list">{trust}</ul><div class="k-actions"><a class="k-btn" href="{h(REG)}">{t["trust_cta"]}</a></div></section>
<section class="k-section k-family" id="family"><p class="k-kicker">KLING MODEL FAMILY</p><h2>{h(t["fam_h2"])}</h2><p class="k-note">{h(t["fam_p"])}</p>{family_html(lang, SLUG, fam[lang])}</section>
<section class="k-section" id="faq"><p class="k-kicker">FAQ</p><h2>{h(t["faq_h2"])}</h2><div class="k-faq">{faq}</div></section>
<section class="k-final"><h2>{h(t["final_h2"])}</h2><p>{h(t["final_p"])}</p><a class="k-btn k-light" href="{h(REG)}">{t["cta"]}</a><ul class="k-final-links">{links}</ul></section>
</main>
<footer class="k-site-footer"><div class="k-footer-inner"><div class="k-footer-top"><div class="k-footer-brand"><a class="k-brand" href="/">AnyAIGC</a><p>{h(t["foot_brand"])}</p></div><div class="k-footer-cols">{foot}</div></div><div class="k-footer-bottom"><p>{h(t["legal"])}</p><a href="/{other}/models/{SLUG}" hreflang="{"en" if lang == "zh" else "zh-CN"}">{t["other"]}</a></div></div></footer>
</body>
</html>
'''


def patch_family(fam):
    """Rewrite the family <ul> in every other Kling model page."""
    changed = []
    for lang in ("zh", "en"):
        for p in sorted((ROOT / lang / "models").glob("kling-*.html")):
            if p.stem == SLUG:
                continue
            s = p.read_text(encoding="utf-8")
            m = re.search(r'(<section class="k-section k-family" id="family">.*?)<ul>.*?</ul>', s, re.S)
            if not m:
                continue
            new = s[:m.start()] + m.group(1) + family_html(lang, p.stem, fam[lang]) + s[m.end():]
            if new != s:
                p.write_text(new, encoding="utf-8", newline="\n")
                changed.append(f"{lang}/{p.name}")
    return changed


def patch_overview():
    for lang in ("zh", "en"):
        p = ROOT / lang / "models" / "kling.html"
        s = p.read_text(encoding="utf-8")
        o = s
        card = (f'<li><a href="/{lang}/models/{SLUG}"><span class="kh-card-icon"><img src="/assets/icons/kling.svg" width="28" height="28" alt=""></span>'
                f'<span><strong>Kling Image 3.0 API</strong><small>{h(T[lang]["hub_desc"])}</small></span><b>${PRICE} / {"张" if lang == "zh" else "image"}</b></a></li>')
        if f'href="/{lang}/models/{SLUG}"' not in s:
            s = s.replace('<ul class="kh-models">', '<ul class="kh-models">' + card, 1)
            s = s.replace("14 个", "15 个").replace("14 Kling", "15 Kling").replace("14 video", "15 image, video").replace("14 models", "15 models")
            s = s.replace("Kling 系列包含 15 个视频、音频与创作工具模型", "Kling 系列包含 15 个图片、视频、音频与创作工具模型")
            s = s.replace("15 image, video, audio and creative-tool", "15 image, video, audio and creative-tool")
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        g = json.loads(m.group(1))
        for node in g["@graph"]:
            if node.get("@type") == "ItemList":
                url = f"{SITE}/{lang}/models/{SLUG}"
                items = [i for i in node["itemListElement"] if i["url"] != url]
                items.insert(0, {"@type": "ListItem", "position": 1, "name": "Kling Image 3.0 API", "url": url})
                for i, it in enumerate(items, 1):
                    it["position"] = i
                node["itemListElement"] = items
                node["numberOfItems"] = len(items)
            if node.get("@type") == "Product":
                node["offers"]["offerCount"] = len([n for n in g["@graph"] if n.get("@type") == "ItemList"][0]["itemListElement"])
        s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False) + s[m.end(1):]
        if s != o:
            p.write_text(s, encoding="utf-8", newline="\n")


def patch_hub():
    for lang in ("zh", "en"):
        p = ROOT / lang / "models" / "index.html"
        s = p.read_text(encoding="utf-8")
        o = s
        t = T[lang]
        url = f"/{lang}/models/{SLUG}"
        card = (f'        <li class="af-model"><div class="af-model-head"><span class="af-model-logo" style="background:#fff;border:1px solid #e1e6ec" aria-hidden="true"><img src="/assets/icons/kling.svg" width="26" height="26" alt=""></span>'
                f'<div><h3><a href="{url}">Kling Image 3.0 API</a></h3><span class="af-model-cat">Kling · {MODEL}</span></div></div><p>{h(t["hub_desc"])}</p>'
                f'<ul class="af-tags">{"".join(f"<li>{x}</li>" for x in t["hub_tags"])}</ul><div class="af-model-foot"><span><strong>{t["hub_price"]}</strong></span>'
                f'<span class="af-model-go" aria-hidden="true">{"查看专题 →" if lang == "zh" else "View guide →"}</span></div></li>\n')
        if f'href="{url}"' not in s:
            i = s.index('id="cat-kling"')
            j = s.index('<ul class="af-models">\n', i) + len('<ul class="af-models">\n')
            s = s[:j] + card + s[j:]
        m = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', s, re.S)
        g = json.loads(m.group(1))
        for node in g.get("@graph", [g]):
            if node.get("@type") != "ItemList":
                continue
            full = SITE + url
            items = [i for i in node["itemListElement"] if i["url"] != full]
            at = next(k for k, i in enumerate(items) if i["url"].endswith("/models/kling-video-v4"))
            items.insert(at, {"@type": "ListItem", "position": 0, "name": "Kling Image 3.0 API", "url": full})
            for k, it in enumerate(items, 1):
                it["position"] = k
            node["itemListElement"] = items
            node["numberOfItems"] = len(items)
        s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False, indent=2) + s[m.end(1):]
        if s != o:
            p.write_text(s, encoding="utf-8", newline="\n")


def patch_sitemap():
    p = ROOT / "sitemap.xml"
    s = p.read_text(encoding="utf-8")
    for lang in ("zh", "en"):
        loc = f"{SITE}/{lang}/models/{SLUG}"
        entry = (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{DATE}</lastmod>\n"
                 f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{SLUG}"/>\n'
                 f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{SLUG}"/>\n'
                 f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{SLUG}"/>\n  </url>\n')
        pat = r"  <url>\s*<loc>" + re.escape(loc) + r"</loc>.*?</url>\n"
        if re.search(pat, s, re.S):
            s = re.sub(pat, lambda _: entry, s, count=1, flags=re.S)
        else:
            s = s.replace("</urlset>", entry + "</urlset>")
        kl = f"{SITE}/{lang}/models/kling"
        s = re.sub(r"(<loc>" + re.escape(kl) + r"</loc>\s*<lastmod>)[^<]+", lambda m: m.group(1) + DATE, s)
    s = re.sub(r"(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+", lambda m: m.group(1) + DATE, s)
    p.write_text(s, encoding="utf-8", newline="\n")


def main():
    fam = family_items()
    for lang in ("zh", "en"):
        (ROOT / lang / "models" / f"{SLUG}.html").write_text(page(lang, fam), encoding="utf-8", newline="\n")
    print("family updated:", len(patch_family(fam)))
    patch_overview()
    patch_hub()
    patch_sitemap()
    print("done")


if __name__ == "__main__":
    main()
