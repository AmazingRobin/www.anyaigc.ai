"""Build the Kling Video V4 Flash topic pages and register them in the Kling family.

Run: python scripts/kling_flash.py   (re-running gives the same result)

Facts (checked 2026-11-12, catalog detail view of kling-video-v4-flash and docs
leaf=393296337 / 393415626):
- Catalog id kling-video-v4-flash, per-second billing, std (720p) only:
  $0.1206/s without a reference video, $0.0808/s with one.
  With a reference video, billed seconds = output + max(reference total, output).
- Only POST /kling/v1/videos/omni-video documents this model (model_name
  "kling-video-v4-flash"); the catalog also lists text2video / image2video.
- Docs: duration 3-30 integer seconds (default 5); aspect_ratio 21:9/16:9/9:16/
  1:1/adaptive; image_list <=10, video_list <=5 (feature only, >=3 s each,
  <=30 s total, public URLs), element_list <=7, voice_list <=3, assets <=15;
  sound=on, multi_shot, mode=pro/4k, resolution 1080p, refer_type=base -> 400.
- Submit returns {"code":0,"data":{"task_id":...}}. The omni query docs only show
  data.status = "succeed"; the sibling text2video query documents
  data.task_status and data.task_result.videos[].url, which the Python sample uses.
  TO CONFIRM with the docs owner.
- Catalog text says 3-20 s, native audio and video editing; the docs say otherwise,
  so the pages only claim what the docs support.

Writes the two pages from the same k-* markup as the other Kling pages and patches
the family list in the other Kling pages, the Kling overview, both model hubs and
the sitemap.
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
SLUG = "kling-video-v4-flash"
MODEL = "kling-video-v4-flash"
P_STD = "0.1206"
P_REF = "0.0808"
DATE = "2026-11-12"
VER = "20261106"
CSS_VER = "20261112"
DOC = {"zh": "https://docs.anyaigc.ai/reference/kling/v1/videos/omni-video?leaf=393296337",
       "en": "https://docs.anyaigc.ai/en/reference/kling/v1/videos/omni-video?leaf=393296337"}
DOC_QUERY = {"zh": "https://docs.anyaigc.ai/reference/kling/v1/videos/omni-video/%7Bid%7D?leaf=393415626",
             "en": "https://docs.anyaigc.ai/en/reference/kling/v1/videos/omni-video/%7Bid%7D?leaf=393415626"}
FORMULA = "output + max(reference total, output)"

T = {
    "zh": dict(
        title="Kling Video V4 Flash API 价格与接入｜720p 参考生视频 - AnyAIGC",
        desc=f"Kling Video V4 Flash API：${P_STD}/秒，720p，单次 3–30 秒，支持文生视频、首帧图生视频、多图与参考视频，并发不限，支持对公转账和增值税专票。",
        keywords="Kling Video V4 Flash API,可灵 4.0 Flash API,kling-video-v4-flash,Kling V4 Flash API 价格,Kling API key,Kling V4 Flash API 企业,Kling V4 Flash API 发票,可灵 API",
        h1="Kling Video V4 Flash API",
        eyebrow="可灵 · AI 视频",
        lead=f"Kling Video V4 Flash 是快手可灵 4.0 系列的轻量版视频生成模型，面向高频创作场景，主打生成速度与性价比。支持文生视频、首帧图生视频和全能参考生视频，输出 720p。在 AnyAIGC 上按秒计费，<strong>${P_STD} / 秒</strong>，并发不限。",
        cta="获取 API Key", price_btn="价格",
        facts=[("模型", f"<code>{MODEL}</code>"), ("价格", f"${P_STD} / 秒"), ("输出", "720p · 3–30 秒"), ("对公 · 专票", "支持")],
        cap_kicker="MODEL CAPABILITIES", cap_h2="Kling Video V4 Flash 能做什么",
        cap_p="以下按模型广场和接口文档当前公开信息整理，调用参数以 API 文档为准。",
        caps=[("文生视频", "只传 prompt 和 duration，就能生成 3–30 秒的 720p 视频，duration 默认 5 秒。"),
              ("首帧与首尾帧", "在 image_list 里用 type 标记 first_frame 作为首帧；end_frame 必须和 first_frame 成对，只传尾帧会返回 400。"),
              ("多图参考", "最多 10 张参考图，在提示词里用 @image_1、@image_2 按传入顺序引用，复用角色、商品外观和场景。"),
              ("参考视频", "最多 5 段参考视频，只能作特征参考（feature）：须为公网 http(s) 地址，每段至少 3 秒、合计不超过 30 秒，用来复用运镜与动作节奏。"),
              ("主体与音色", "element_list 最多 7 个主体，voice_list 最多 3 个音色，在提示词里用 @element_1 等引用；各类素材合计不超过 15 个。"),
              ("画幅与分辨率", "输出固定 720p（mode 传 std 或不传）；画幅支持 21:9、16:9、9:16、1:1，以及按素材自适应的 adaptive。")],
        use_h2="适用场景",
        uses=[("社媒短视频批量生产", "按秒计费、单价低，适合高频出片和多版本投放素材。"),
              ("电商素材制作", "用商品图做参考，批量生成不同场景和画幅的展示短片。"),
              ("创意快速验证", "先用 720p 跑通镜头和节奏，确认方向后再投入更高成本。")],
        price_h2="Kling Video V4 Flash API 价格",
        billing=[("按秒计费", "不是按次，也不是按档位"), ("固定 720p", "mode 传 std 或不传"), ("并发不限", "所有用户默认享有"), ("余额通用", "一个 Key 调用 300+ 模型")],
        th=("功能", "模型名", "单价（USD）"),
        rows=[("文生视频 / 首帧图生视频 / 多图参考（不带参考视频）", f"${P_STD} / 秒"), ("带参考视频的全能参考", f"${P_REF} / 秒")],
        formula="带参考视频时，计费秒数 = 输出时长 + max(参考视频总时长, 输出时长)；参考图、主体、音色不另计费。",
        note="单位 USD，按成功提交计费；实时价格以模型广场为准。",
        cost_h2="成本示例",
        costs=[("5 秒文生视频", f"5 × ${P_STD}", "$0.603"), ("10 秒首帧图生视频", f"10 × ${P_STD}", "$1.206"),
               ("5 秒输出 + 5 秒参考视频", f"(5 + max(5, 5)) × ${P_REF}", "$0.808")],
        catalog="在模型广场查看",
        qs_h2="接入 Kling Video V4 Flash API",
        steps=["注册 AnyAIGC 并创建 API Key，放进 ANYAIGC_API_KEY 环境变量", "POST /kling/v1/videos/omni-video 提交任务，拿到 task_id", "GET /kling/v1/videos/omni-video/{id} 轮询，成功后下载视频"],
        qs_note="请求里 model_name 填 \"kling-video-v4-flash\"。该型号只出 720p：mode 只能传 std 或不传，resolution 只能传 720p 或不传，传 pro 或 1080p 会返回 400（不扣费）。参考图、参考视频放在 image_list、video_list，提示词里用 @image_1、@video_1 引用。",
        doc_link="阅读接口文档", query_link="查看任务查询文档",
        prompt="镜头从高空缓缓推进到雨后的霓虹街道，一只橘猫走过湿润的路面，电影感光影",
        ref_prompt="参考 @video_1 的运镜轨迹与镜头节奏，主体替换为 @image_1",
        poll="# 每 10 秒查询一次，成功后打印视频地址",
        tab_ref="参考图 + 参考视频",
        ent_h2="企业接入 Kling Video V4 Flash API",
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
        fam_p="按任务选择模型：先确定是图片、视频生成、控制、声音还是素材资产，再比较模式、时长和价格。",
        faq_h2="Kling Video V4 Flash API 常见问题",
        faq=[("Kling Video V4 Flash API 多少钱？", f"按秒计费：不带参考视频 ${P_STD} / 秒，带参考视频 ${P_REF} / 秒，输出固定 720p。单位 USD，按成功提交计费，实时价格以模型广场为准。"),
             ("应该调用哪个接口？", "提交任务用 POST /kling/v1/videos/omni-video，body 里 model_name 填 kling-video-v4-flash；查询结果用 GET /kling/v1/videos/omni-video/{id}。API 域名为 https://anyaigc.ai，请求头 Authorization: Bearer <API Key>。"),
             ("支持哪些生成方式？", "支持文生视频、首帧与首尾帧图生视频、最多 10 张参考图、最多 5 段参考视频，以及主体（最多 7 个）和音色（最多 3 个）引用，各类素材合计不超过 15 个。具体字段以接口文档为准。"),
             ("怎么计费？带参考视频为什么单价更低？", f"不带参考视频时，计费秒数等于输出时长，单价 ${P_STD} / 秒。带参考视频时单价为 ${P_REF} / 秒，但计费秒数 = 输出时长 + max(参考视频总时长, 输出时长)，例如 5 秒输出加 5 秒参考视频按 10 秒计费，合计 $0.808。参考图、主体、音色不另计费。"),
             ("分辨率、时长和画幅有什么限制？", "输出固定 720p：mode 只能传 std 或不传，resolution 只能传 720p 或不传，传 pro 或 1080p 返回 400，且不扣费。duration 为 3–30 的整数秒，默认 5。画幅可选 21:9、16:9、9:16、1:1 和 adaptive。"),
             ("有哪些参数不支持？", "该型号不支持 sound（传 on 会返回 400）、multi_shot 多镜头、4K 模式，以及 refer_type 为 base 的视频编辑；视频参考只能用 feature。"),
             ("结果怎么获取？", "接口是异步的：提交后返回 task_id，再用查询接口轮询，任务成功后从返回的 task_result 里取视频地址。任务状态值和返回字段以接口文档为准。"),
             ("并发有限制吗？", "AnyAIGC 的 Kling 系列默认并发不限，所有用户都可以直接使用。"),
             ("生成内容可以商用吗？", "生成内容的使用权和内容政策以快手可灵官方条款为准。使用参考图、参考视频时，也应具备相关权利或授权。"),
             ("AnyAIGC 能开发票吗？支持增值税专票吗？", "支持。可按实际充值金额开具增值税普通发票和增值税专用发票，联系企业客服办理即可。"),
             ("企业可以对公转账和签合同吗？", "可以。支持企业对公转账充值，可签订服务合同，并提供专属客服与技术对接。"),
             ("支持哪些支付方式？", "支持微信支付、支付宝、USDT 和信用卡充值，企业还可以对公转账，并开具增值税普通发票或专用发票。余额按美元计价，对平台所有模型通用。"),
             ("新用户有免费试用额度吗？", "有。新用户注册后赠送 200 万 tokens 的试用额度，可以先测试效果再决定是否充值。最低 1 美元起充。"),
             ("余额可以退款吗？", "可以。未使用的余额可以申请退款，不收取手续费。具体流程请联系客服。"),
             ("会不会用低配模型冒充？我的数据安全吗？", "请求走官方模型渠道，不用低配或逆向模型冒充。除法律法规要求外，我们不会对你的输入输出内容做持久化存储，也不会用于训练模型；控制台可以查看每次调用的扣费明细。")],
        final_h2="开始调用 Kling Video V4 Flash", final_p="注册即送 200 万 tokens 试用额度。",
        links=[("Kling 全系总览", "/zh/models/kling"), ("全部模型专题", "/zh/models/"), ("模型广场", PRICING), ("English", f"/en/models/{SLUG}")],
        nav=["模型专题", "模型广场", "价格", "企业接入", "API 文档"], other="English",
        foot_brand="国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。",
        foot=[("产品", [("模型专题", "/zh/models/"), ("模型广场", PRICING), ("控制台", "https://anyaigc.ai/console")]),
              ("资源", [("API 文档 ↗", DOC["zh"]), ("Kling 官方开发者平台 ↗", "https://kling.ai/dev"), ("联系我们", SUPPORT)]),
              ("条款", [("隐私政策", "/privacy"), ("服务条款", "/terms")])],
        legal="© 2026 AnyAIGC。Kling、可灵是快手的商标。示例媒体来自 Kling AI 官方开发者平台，版权归其权利人所有。AnyAIGC 是独立 API 服务商，与快手可灵无隶属关系。商用授权以快手可灵官方条款为准。",
        crumbs=["首页", "模型专题", "Kling", "Kling Video V4 Flash"],
        fam_name="Kling Video V4 Flash", fam_sub="高频创作 · 720p 参考生视频",
        hub_desc="可灵 4.0 轻量版，720p 文生、首帧与参考生视频", hub_tags=["视频", "720p", "参考生视频"], hub_price=f"${P_STD} / 秒",
        media_label="Kling 官方视频示例", media_caption="官方示例素材：Kling AI 开发者平台",
    ),
    "en": dict(
        title="Kling Video V4 Flash API Pricing | 720p Video - AnyAIGC",
        desc=f"Kling Video V4 Flash API at ${P_STD}/second: 720p clips of 3-30 s, text, first-frame and reference video. Unlimited concurrency, bank transfer, VAT invoices.",
        keywords="Kling Video V4 Flash API,Kling 4.0 Flash API,kling-video-v4-flash,Kling V4 Flash API pricing,Kling API key,Kling V4 Flash API for business,Kling API",
        h1="Kling Video V4 Flash API",
        eyebrow="Kling · AI video",
        lead=f"Kling Video V4 Flash is the lightweight model in Kuaishou's Kling 4.0 series, built for high-frequency creative work with a focus on speed and cost. It supports text-to-video, first-frame image-to-video and reference-to-video at 720p. On AnyAIGC it is billed per second at <strong>${P_STD} / second</strong> with unlimited concurrency.",
        cta="Get an API key", price_btn="Pricing",
        facts=[("Model", f"<code>{MODEL}</code>"), ("Price", f"${P_STD} / second"), ("Output", "720p · 3–30 s"), ("Contracts · invoices", "Available")],
        cap_kicker="MODEL CAPABILITIES", cap_h2="What Kling Video V4 Flash can do",
        cap_p="Summarized from the current model catalog and API reference. Use the API docs for exact parameters.",
        caps=[("Text-to-video", "Send a prompt and a duration to get a 720p clip of 3–30 seconds. Duration defaults to 5 seconds."),
              ("First and last frames", "Mark an image in image_list as first_frame. An end_frame must be paired with a first_frame; sending only an end frame returns 400."),
              ("Multi-image reference", "Up to 10 reference images, cited in the prompt as @image_1, @image_2 in the order you send them, to reuse characters, product looks and scenes."),
              ("Reference video", "Up to 5 reference videos, feature reference only: public http(s) URLs, at least 3 seconds each and 30 seconds in total, to reuse camera moves and motion rhythm."),
              ("Subjects and voices", "Up to 7 subjects in element_list and 3 voices in voice_list, cited as @element_1 and so on. All reference assets together may not exceed 15."),
              ("Aspect ratio and resolution", "Output is fixed at 720p (send mode std or omit it). Aspect ratios are 21:9, 16:9, 9:16, 1:1, or adaptive to follow your assets.")],
        use_h2="Use cases",
        uses=[("Social video at volume", "Per-second billing at a low rate suits frequent publishing and multi-version ad creative."),
              ("E-commerce clips", "Use product photos as references to batch-generate showcase clips in different scenes and aspect ratios."),
              ("Fast creative checks", "Prove out the shot and pacing at 720p before spending more on the final version.")],
        price_h2="Kling Video V4 Flash API pricing",
        billing=[("Per second", "Not per call, no tiers"), ("Fixed 720p", "Send mode std or omit it"), ("Unlimited concurrency", "For every account"), ("Shared balance", "One key for 300+ models")],
        th=("Operation", "Model", "Unit price (USD)"),
        rows=[("Text, first-frame and multi-image reference (no reference video)", f"${P_STD} / second"), ("Reference-to-video with a reference video", f"${P_REF} / second")],
        formula="With a reference video, billed seconds = output duration + max(total reference-video duration, output duration). Reference images, subjects and voices are not billed separately.",
        note="Prices in USD, charged on successful submission. See the model catalog for current prices.",
        cost_h2="Cost examples",
        costs=[("5-second text-to-video", f"5 × ${P_STD}", "$0.603"), ("10-second first-frame video", f"10 × ${P_STD}", "$1.206"),
               ("5 s output + 5 s reference video", f"(5 + max(5, 5)) × ${P_REF}", "$0.808")],
        catalog="View in the model catalog",
        qs_h2="Integrate the Kling Video V4 Flash API",
        steps=["Sign up, create an API key and set ANYAIGC_API_KEY", "POST /kling/v1/videos/omni-video to submit a task and get its task_id", "Poll GET /kling/v1/videos/omni-video/{id} and download the video when it succeeds"],
        qs_note="Set model_name to \"kling-video-v4-flash\". This model outputs 720p only: mode must be std or omitted, resolution must be 720p or omitted, and pro or 1080p returns 400 with no charge. Put reference images and videos in image_list and video_list and cite them as @image_1 and @video_1 in the prompt.",
        doc_link="Read the API reference", query_link="See task-query documentation",
        prompt="The camera glides down to a neon street after rain as an orange cat walks across the wet pavement, cinematic lighting",
        ref_prompt="Follow the camera path and pacing of @video_1, with the subject replaced by @image_1",
        poll="# Poll every 10 seconds; print the video URL once the task succeeds",
        tab_ref="Image + video reference",
        ent_h2="Kling Video V4 Flash API for teams and enterprises",
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
        fam_p="Pick by task first, whether that is images, video generation, control, audio or assets, then compare modes, durations and prices.",
        faq_h2="Kling Video V4 Flash API FAQ",
        faq=[("How much does the Kling Video V4 Flash API cost?", f"It is billed per second: ${P_STD} per second without a reference video and ${P_REF} per second with one, always at 720p. Prices are in USD, charged on successful submission; see the model catalog for current rates."),
             ("Which endpoint should I call?", "Submit with POST /kling/v1/videos/omni-video, setting model_name to kling-video-v4-flash, and fetch results with GET /kling/v1/videos/omni-video/{id}. The API host is https://anyaigc.ai and the header is Authorization: Bearer <API Key>."),
             ("Which generation modes are supported?", "Text-to-video, first-frame and first-and-last-frame image-to-video, up to 10 reference images, up to 5 reference videos, plus up to 7 subjects and 3 voices. All reference assets together may not exceed 15. See the API reference for the exact fields."),
             ("How is it billed, and why is the rate lower with a reference video?", f"Without a reference video, billed seconds equal the output duration at ${P_STD} per second. With one, the rate is ${P_REF} per second but billed seconds = output duration + max(total reference-video duration, output duration); a 5-second output with a 5-second reference video bills 10 seconds, or $0.808. Reference images, subjects and voices are free."),
             ("What are the resolution, duration and aspect-ratio limits?", "Output is fixed at 720p: mode must be std or omitted and resolution must be 720p or omitted; pro or 1080p returns 400 with no charge. duration is an integer from 3 to 30 seconds, default 5. Aspect ratios are 21:9, 16:9, 9:16, 1:1 and adaptive."),
             ("What is not supported?", "This model does not support sound (on returns 400), multi_shot, the 4K mode, or video editing with refer_type base. Reference videos must use feature."),
             ("How do I get the result?", "The API is asynchronous. Submission returns a task_id; poll the query endpoint and, once the task succeeds, read the video URL from task_result. Check the API reference for the exact status values and response fields."),
             ("Are there concurrency limits?", "Kling models on AnyAIGC have unlimited concurrency by default for every account."),
             ("Can I use the videos commercially?", "Usage rights and content policy follow Kuaishou Kling's official terms. Make sure you have the rights to any reference images or videos you upload."),
             ("Can AnyAIGC issue invoices, including VAT special invoices?", "Yes. AnyAIGC issues invoices for actual top-ups, including Chinese VAT general and VAT special invoices. Contact enterprise support to arrange them."),
             ("Can my company pay by bank transfer and sign a contract?", "Yes. Companies can top up by corporate bank transfer, sign a service agreement, and work with a dedicated support and technical contact."),
             ("Which payment methods are supported?", "You can top up with WeChat Pay, Alipay, USDT or a credit card. Companies can also pay by bank transfer and get VAT general or special invoices. Your balance is in USD and works across every model on the platform."),
             ("Is there free trial credit for new users?", "Yes. New accounts get 2 million tokens of trial credit, so you can test before deciding to top up. Top-ups start at $1."),
             ("Can I get a refund on my balance?", "Yes. Unused balance can be refunded with no fee. Contact support to start a refund."),
             ("Are these the real models? Is my data safe?", "Requests go to official model channels, never cheaper or reverse-engineered substitutes. Unless the law requires it, we do not persistently store your prompts or outputs or use them for training, and the console shows the cost of every request.")],
        final_h2="Start using Kling Video V4 Flash", final_p="Sign up and get 2M trial tokens.",
        links=[("All Kling models", "/en/models/kling"), ("All model guides", "/en/models/"), ("Model catalog", PRICING), ("中文", f"/zh/models/{SLUG}")],
        nav=["Models", "Model catalog", "Pricing", "Enterprise", "API docs"], other="中文",
        foot_brand="API access to 300+ models through one Base URL and one API key.",
        foot=[("Product", [("Model guides", "/en/models/"), ("Model catalog", PRICING), ("Console", "https://anyaigc.ai/console")]),
              ("Resources", [("API docs ↗", DOC["en"]), ("Kling developer platform ↗", "https://kling.ai/dev"), ("Contact us", SUPPORT)]),
              ("Legal", [("Privacy", "/privacy"), ("Terms", "/terms")])],
        legal="© 2026 AnyAIGC. Kling is a trademark of Kuaishou. Sample media is from the Kling AI developer platform and belongs to its respective rights holders. AnyAIGC is an independent API provider and is not affiliated with Kuaishou Kling. Commercial use follows Kling's official terms.",
        crumbs=["Home", "Model guides", "Kling", "Kling Video V4 Flash"],
        fam_name="Kling Video V4 Flash", fam_sub="High-frequency creation · 720p reference video",
        hub_desc="Kling 4.0 lightweight video model: 720p text, first-frame and reference-to-video", hub_tags=["Video", "720p", "Reference-to-video"], hub_price=f"${P_STD} / second",
        media_label="Kling official sample video", media_caption="Official sample media: Kling AI developer platform",
    ),
}


EXT = ' target="_blank" rel="noopener"'


def h(v):
    return escape(str(v), quote=True)


def payload(lang):
    return {"model_name": MODEL, "prompt": T[lang]["prompt"], "duration": 5, "aspect_ratio": "16:9"}


def payload_ref(lang):
    return {"model_name": MODEL, "prompt": T[lang]["ref_prompt"], "duration": 5,
            "image_list": [{"image_url": "https://example.com/subject.jpg"}],
            "video_list": [{"video_url": "https://example.com/motion.mp4", "refer_type": "feature"}]}


def curl(lang):
    body = json.dumps(payload(lang), ensure_ascii=False, indent=2)
    return ('curl --request POST "https://anyaigc.ai/kling/v1/videos/omni-video" \\\n'
            '  --header "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
            '  --header "Content-Type: application/json" \\\n'
            f"  --data '{body}'\n\n"
            + ("# 用返回的 data.task_id 查询结果\n" if lang == "zh" else "# Query the result with the returned data.task_id\n")
            + 'curl "https://anyaigc.ai/kling/v1/videos/omni-video/$TASK_ID" \\\n'
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

task_id = call("POST", "/kling/v1/videos/omni-video", payload)["data"]["task_id"]
print("task_id:", task_id)

__COMMENT__
for _ in range(90):
    data = call("GET", f"/kling/v1/videos/omni-video/{task_id}")["data"]
    if data["task_status"] == "succeed":
        break
    if data["task_status"] == "failed":
        raise RuntimeError(data.get("task_status_msg"))
    time.sleep(10)
else:
    raise TimeoutError(task_id)

for video in data["task_result"]["videos"]:
    print(video["url"])'''


def python(lang):
    return PY.replace("__BODY__", json.dumps(payload(lang), ensure_ascii=False, indent=4)).replace("__COMMENT__", T[lang]["poll"])


def family_items():
    """Read the Kling family list from the V4 page and put this model right after it."""
    out = {}
    for lang in ("zh", "en"):
        src = (ROOT / lang / "models" / "kling-video-v4.html").read_text(encoding="utf-8")
        ul = re.search(r'<section class="k-section k-family" id="family">.*?<ul>(.*?)</ul>', src, re.S).group(1)
        items = re.findall(r'<li class="[^"]*"><a href="/\w+/models/([^"]+)"><strong>(.*?)</strong><span>(.*?)</span></a></li>', ul)
        items = [i for i in items if i[0] != SLUG]
        at = next(k for k, i in enumerate(items) if i[0] == "kling-video-v4") + 1
        t = T[lang]
        items.insert(at, (SLUG, t["fam_name"], t["fam_sub"]))
        out[lang] = items
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
    offers = [{"@type": "Offer", "name": f"{MODEL} · {r[0]}", "price": p, "priceCurrency": "USD", "url": me + "#pricing"}
              for r, p in zip(t["rows"], (P_STD, P_REF))]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": f"{SITE}/#org", "name": "AnyAIGC", "url": "https://anyaigc.ai", "logo": f"{SITE}/logo.webp"},
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "AnyAIGC"},
        {"@type": "WebPage", "@id": me + "#webpage", "url": me, "name": t["title"], "description": t["desc"], "inLanguage": "zh-CN" if lang == "zh" else "en", "dateModified": DATE},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(zip(t["crumbs"], crumb_urls), 1)]},
        {"@type": "Product", "@id": me + "#product", "name": "Kling Video V4 Flash API (AnyAIGC)", "description": t["desc"], "sku": MODEL, "image": img, "brand": {"@type": "Brand", "name": "Kling"},
         "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": P_REF, "highPrice": P_STD, "offerCount": 2, "url": me + "#pricing", "offers": offers}},
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
    ref_body = json.dumps(payload_ref(lang), ensure_ascii=False, indent=2)
    tabs = [("cURL", curl(lang)), ("Python", python(lang)), (t["tab_ref"] + " (JSON)", ref_body)]
    code = "".join(f'<p class="k-kicker">{h(n)}</p><pre><code>{h(c)}</code></pre>' for n, c in tabs)
    ent = "".join(f"<article><span>{h(a)}</span><h3>{h(b)}</h3><p>{h(c)}</p></article>" for a, b, c in t["ent"])
    trust = "".join(f"<li>{x}</li>" for x in t["trust"])
    faq = "".join(f'<details><summary><h3>{h(q)}</h3></summary><div class="k-answer"><p>{h(a)}</p></div></details>' for q, a in t["faq"])
    crumbs = "".join(f'<li><a href="{u.removeprefix(SITE)}">{h(n)}</a></li>' for n, u in zip(t["crumbs"][:-1], crumb_urls[:-1])) + f'<li aria-current="page">{h(t["crumbs"][-1])}</li>'
    links = "".join(f'<li><a href="{h(u)}"{" hreflang=" + chr(34) + ("en" if lang == "zh" else "zh-CN") + chr(34) if u.startswith("/" + other) else ""}>{h(n)}</a></li>' for n, u in t["links"])
    foot = "".join(f'<div><h2>{h(g)}</h2><ul>' + "".join(f'<li><a href="{h(u)}"{EXT if ("docs." in u or "kling.ai" in u) else ""}>{h(n)}</a></li>' for n, u in items) + "</ul></div>" for g, items in t["foot"])
    art = (f'<figure class="k-official-media"><video src="/assets/models/kling-hub/flagship.mp4?v=20261106" poster="/assets/models/kling-hub/flash-poster.webp?v=20261112" '
           f'controls playsinline preload="metadata" aria-label="{h(t["media_label"])}"></video><figcaption>{h(t["media_caption"])}</figcaption></figure>')
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
<meta property="og:image:alt" content="AnyAIGC Kling Video V4 Flash API">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{h(t["title"])}">
<meta name="twitter:description" content="{h(t["desc"])}">
<meta name="twitter:image" content="{img}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v={VER}">
<link rel="stylesheet" href="/assets/models/kling.css?v={VER}">
<link rel="stylesheet" href="/assets/models/kling-image.css?v=20261111">
<link rel="stylesheet" href="/assets/models/kling-flash.css?v={CSS_VER}">
<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<header class="k-nav"><a class="k-brand" href="/">AnyAIGC</a><nav>{"".join(f'<a href="{h(u)}">{n}</a>' for n, u in zip(t["nav"], nav_href))}</nav><div><a href="/{other}/models/{SLUG}" hreflang="{"en" if lang == "zh" else "zh-CN"}">{t["other"]}</a><a class="k-btn" href="{h(REG)}">{t["cta"]}</a></div></header>
<main>
<section class="k-hero"><div class="k-hero-copy"><nav aria-label="breadcrumb"><ol class="k-crumbs">{crumbs}</ol></nav><p class="k-eyebrow"><img src="/assets/icons/kling.svg" alt="Kling" width="28" height="28"> {t["eyebrow"]}</p><h1>{t["h1"]}</h1><p class="k-lead">{t["lead"]}</p><div class="k-actions"><a class="k-btn" href="{h(REG)}">{t["cta"]}</a><a class="k-btn k-light" href="#pricing">{t["price_btn"]}</a></div><ul class="k-facts">{facts}</ul></div>{art}</section>
<section class="k-section" id="capabilities"><div class="k-section-intro"><p class="k-kicker">{t["cap_kicker"]}</p><h2>{h(t["cap_h2"])}</h2><p>{h(t["cap_p"])}</p></div><div class="k-detail-grid k-detail-grid-6">{caps}</div></section>
<section class="k-section k-use-cases" id="use-cases"><p class="k-kicker">USE CASES</p><h2>{h(t["use_h2"])}</h2><div class="k-use-grid">{uses}</div></section>
<section class="k-section" id="pricing"><p class="k-kicker">PRICING</p><h2>{h(t["price_h2"])}</h2><ul class="k-billing">{billing}</ul><div class="k-table-wrap"><table><thead><tr><th>{t["th"][0]}</th><th>{t["th"][1]}</th><th>{t["th"][2]}</th></tr></thead><tbody>{rows}</tbody></table></div><p class="k-note">{h(t["formula"])}</p><p class="k-note">{h(t["note"])}</p><div class="k-costs"><h3>{h(t["cost_h2"])}</h3><ul>{costs}</ul></div><div class="k-actions"><a class="k-btn" href="{h(REG)}">{t["cta"]}</a><a class="k-btn k-light" href="{PRICING}">{t["catalog"]} ↗</a></div></section>
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
        unit = "秒" if lang == "zh" else "second"
        card = (f'<li><a href="/{lang}/models/{SLUG}"><span class="kh-card-icon"><img src="/assets/icons/kling.svg" width="28" height="28" alt=""></span>'
                f'<span><strong>Kling Video V4 Flash API</strong><small>{h(T[lang]["hub_desc"])}</small></span><b>${P_STD} / {unit}</b></a></li>')
        if f'href="/{lang}/models/{SLUG}"' not in s:
            anchor = s.index(f'<li><a href="/{lang}/models/kling-video-v4">')
            end = s.index("</li>", anchor) + len("</li>")
            s = s[:end] + card + s[end:]
            s = s.replace("15 个", "16 个").replace("15 image", "16 image").replace("15 Kling", "16 Kling")
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        g = json.loads(m.group(1))
        lst = next(n for n in g["@graph"] if n.get("@type") == "ItemList")
        url = f"{SITE}/{lang}/models/{SLUG}"
        items = [i for i in lst["itemListElement"] if i["url"] != url]
        at = next(k for k, i in enumerate(items) if i["url"].endswith("/models/kling-video-v4")) + 1
        items.insert(at, {"@type": "ListItem", "position": 0, "name": "Kling Video V4 Flash API", "url": url})
        for i, it in enumerate(items, 1):
            it["position"] = i
        lst["itemListElement"] = items
        lst["numberOfItems"] = len(items)
        for node in g["@graph"]:
            if node.get("@type") == "Product":
                node["offers"]["offerCount"] = len(items)
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
                f'<div><h3><a href="{url}">Kling Video V4 Flash API</a></h3><span class="af-model-cat">Kling · {MODEL}</span></div></div><p>{h(t["hub_desc"])}</p>'
                f'<ul class="af-tags">{"".join(f"<li>{x}</li>" for x in t["hub_tags"])}</ul><div class="af-model-foot"><span><strong>{t["hub_price"]}</strong></span>'
                f'<span class="af-model-go" aria-hidden="true">{"查看专题 →" if lang == "zh" else "View guide →"}</span></div></li>\n')
        if f'href="{url}"' not in s:
            anchor = s.index(f'href="/{lang}/models/kling-video-v4"')
            end = s.index("</li>\n", anchor) + len("</li>\n")
            s = s[:end] + card + s[end:]
        m = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', s, re.S)
        g = json.loads(m.group(1))
        for node in g.get("@graph", [g]):
            if node.get("@type") != "ItemList":
                continue
            full = SITE + url
            items = [i for i in node["itemListElement"] if i["url"] != full]
            at = next(k for k, i in enumerate(items) if i["url"].endswith("/models/kling-video-v4")) + 1
            items.insert(at, {"@type": "ListItem", "position": 0, "name": "Kling Video V4 Flash API", "url": full})
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
