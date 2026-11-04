# Grok Image 系列专题页中文文案。build(slug) 返回 grok_image_layout 需要的字段。
from grok_image_data import (MODELS, TIERS, INPUT, tier, REG, PRICING, SUPPORT, DOCS_GEN, DOCS_EDIT, XAI_POST, XAI_MIGRATION, XAI_PRICING, cny)

M20, M10, MQ = MODELS['grok-imagine-image-2.0'], MODELS['grok-imagine-image'], MODELS['grok-imagine-image-quality']
P20, P10, PQ = f'¥{cny(M20["usd"])}', f'¥{cny(M10["usd"])}', f'¥{cny(MQ["usd"])}'
O20 = f'¥{cny(M20["official_lo"])}–¥{cny(M20["official_hi"])}'
PIN = f'¥{cny(INPUT["grok-imagine-image-2.0"][0])}'  # 改图每张输入图
P20_HI, PQ_HI = f'¥{cny(M20["usd_hi"])}', f'¥{cny(MQ["usd_hi"])}'
P20_1KM = f'¥{cny(tier("grok-imagine-image-2.0", "1K", "Medium"))}'
SAVE_Q = f'¥{float(cny(MQ["usd"])) - float(cny(M20["usd"])):.2f}'  # Quality 比 2.0 Low 每张贵多少（1K）


def total(n, *usd):
    """n 张的人民币总价（先按美元相加再换算，避免逐项四舍五入的误差）"""
    v = n * sum(float(u) for u in usd) * 6.689338
    return f'¥{v:,.0f}' if v >= 100 else f'¥{v:,.1f}'
O10 = f'¥{cny(M10["official_lo"])}'
RATE_NOTE = '按 1 美元 ≈ ¥6.689 换算成人民币'

FAMILY = [
    ('grok-image', '总览', 'Grok Image 全系总览', '三个型号的价格对比与选型'),
    ('grok-imagine-image-2.0', '推荐', 'Grok Imagine Image 2.0', f'{P20} / 张起，文字排版与精准改图'),
    ('grok-imagine-image', '', 'Grok Imagine Image', f'{P10} / 张，第一代 Imagine 生图'),
    ('grok-imagine-image-quality', '已停用', 'Grok Imagine Image Quality', f'{PQ} / 张起，xAI 已并入 2.0'),
]
FAMILY_H2 = 'Grok Image 系列模型'
FAMILY_LEAD = '同一个 API Key、同一个接口，改 model 字段即可切换。'

# ---------------- 代码示例 ----------------
PROMPT = '一张复古演唱会海报，标题“霓虹夜行”，粗体复古字体，底部一行清晰小字“2026.12.31 · 上海”'
EDIT_PROMPT = '把背景换成雪后的城市街道，人物和光线保持不变'


def code_py(model, quality=True, resolution=True):
    q = '\n        "quality": "medium",  # low / medium / auto（仅 2.0 支持，medium 更贵）' if quality else ''
    r = '\n        "resolution": "2k",  # 1k / 1.5k / 2k，越高越贵' if resolution else ''
    return f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{PROMPT}",
        "aspect_ratio": "2:3",  # 1:1、16:9、9:16、3:2 等{r}{q}
        "n": 1,
        "response_format": "b64_json",  # 或 url
    }},
    timeout=300,
)
resp.raise_for_status()
for i, item in enumerate(resp.json()["data"], 1):
    if item.get("b64_json"):
        with open(f"grok_{{i}}.jpg", "wb") as f:
            f.write(base64.b64decode(item["b64_json"]))
        print("saved", f"grok_{{i}}.jpg")
    else:  # response_format 为 url 时返回临时链接，请及时下载
        print(item["url"])'''


def code_curl(model, resolution=True):
    r = '\n    "resolution": "1k",' if resolution else ''
    return f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "{PROMPT}",
    "aspect_ratio": "16:9",{r}
    "n": 1,
    "response_format": "url"
  }}\''''


def code_edit(model):
    return f'''import os
import requests

# 图片编辑：multipart/form-data 上传原图
API_KEY = os.environ["ANYAIGC_API_KEY"]
with open("photo.png", "rb") as img:
    resp = requests.post(
        "https://anyaigc.ai/v1/images/edits",
        headers={{"Authorization": "Bearer " + API_KEY}},
        files={{"image": img}},
        data={{"model": "{model}", "prompt": "{EDIT_PROMPT}", "n": 1}},
        timeout=300,
    )
resp.raise_for_status()
print(resp.json()["data"][0])'''


ENT_LEAD = '电商公司、设计团队和内容平台可以直接走企业流程采购，财务、法务和技术对接都有对应支持。'

FAQ_INVOICE = ('AnyAIGC 能开发票吗？支持增值税专票吗？', '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。')
FAQ_CONTRACT = ('企业可以对公转账和签合同吗？', f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。')
FAQ_CN = ('没有 xAI 账号能调用吗？国内能直连吗？', '能。在 AnyAIGC 注册即可拿到 API Key，不需要 xAI 账号或海外信用卡。接口地址是 <code>https://anyaigc.ai</code>，国内网络可以直接调用，同一个 Key 还能调用平台上 300+ 其他模型。')
FAQ_CONC = ('并发有限制吗？', 'AnyAIGC 对 Grok Image 系列不设并发限制，所有用户默认享有，批量出图不用排队申请。')
FAQ_COMMERCIAL = ('生成的图片可以商用吗？', '图片的使用权和内容政策以 xAI 官方条款为准。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用。')
FAQ_DIFF = ('Image 2.0、Image 和 Quality 有什么区别，该选哪个？',
            f'Grok Imagine Image 2.0（<code>grok-imagine-image-2.0</code>）是 xAI 当前推荐的型号，文字排版、指令遵循和改图都更强，在 AnyAIGC 上 {P20} / 张起，新项目直接选它。'
            f'Grok Imagine Image（<code>grok-imagine-image</code>）是第一代 Imagine 生图模型，{P10} / 张，是系列里最便宜的，适合只需要文生图的场景。'
            f'Grok Imagine Image Quality 已被 xAI 在 2026 年 11 月 2 日并入 2.0，在 AnyAIGC 上 {PQ} / 张起，比 2.0 Low 每档贵约 {SAVE_Q}，建议迁移。')

STEPS = lambda model, edit: [
    f'<a href="{REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
    '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
    f'向 <code>POST https://anyaigc.ai/v1/images/generations</code> 发请求，<code>model</code> 填 <code>{model}</code>'
    + ('；改图走 <code>POST /v1/images/edits</code>。' if edit else '。'),
]

QS_NOTE = (f'请求头用 <code>Authorization: Bearer &lt;API Key&gt;</code>。返回体是 <code>{{"created": ..., "data": [{{"b64_json": ...}}], "usage": {{"generated_images": 1, ...}}}}</code>，'
           f'<code>response_format</code> 填 <code>url</code> 时返回临时链接，请及时下载。字段说明见 AnyAIGC 文档：<a href="{DOCS_GEN}" target="_blank" rel="noopener">生成图片</a>、<a href="{DOCS_EDIT}" target="_blank" rel="noopener">编辑图片</a>。')

WHY = [('一个 Key，300+ 模型', 'Grok Imagine、GPT Image、Nano Banana、Seedream 共用一个 API Key 和余额。'),
       ('国内直连', '接口地址 <code>https://anyaigc.ai</code>，国内网络可直接调用，不需要 xAI 账号。'),
       ('低于官方价', '按张计费，各档单价都低于 xAI 官方价，控制台可查每次调用的扣费明细。'),
       ('并发不限', '所有用户默认不限并发，批量出图不用排队申请。')]


def base(slug):
    return dict(family=FAMILY, family_h2=FAMILY_H2, family_lead=FAMILY_LEAD, why_h2='为什么通过 AnyAIGC 调用', why=WHY,
                docs=DOCS_GEN, ent_lead=ENT_LEAD, in_other=f'{FAMILY_TITLE_EN[slug]} in English', category='图像生成 API')


FAMILY_TITLE_EN = {'grok-image': 'Grok Image API', 'grok-imagine-image-2.0': 'Grok Imagine Image 2.0 API',
                   'grok-imagine-image': 'Grok Imagine Image API', 'grok-imagine-image-quality': 'Grok Imagine Image Quality API'}

FEATURES_20 = [
    ('hero-39', '文字与版式', '标题、小字、日程和图注按设计师的思路排进画面，信息密集的海报、行程单和信息图也不乱。'),
    ('tpl-background-removal', '精准改图', '只改你指定的部分，其余保持不变。换背景、换颜色、去掉杂物都能用一句话完成。'),
    ('world-character', '风格前后一致', '分开生成的角色、场景和道具保持同一种画风，适合做分镜、绘本和游戏素材。'),
    ('hero-34', '多种画风', '写实摄影、水墨、像素风、漫画、复古海报都能稳定输出，细节和材质清晰。'),
    ('resize-16x9', '15 种宽高比', '从 1:2 竖图到 21:9 宽屏，选好比例模型会自动重新构图，不是简单裁切。'),
    ('tpl-ecommerce-listing', '商品图与营销图', '商品换色、电商主图、杂志风产品海报，一次调用直接出可用素材。'),
]

GALLERY_20 = [('hero-41', '质感'), ('hero-37', '旅行海报'), ('hero-40', '信息图'), ('hero-43', '电影感'), ('hero-32', '漫画'),
              ('hero-26', '水墨'), ('hero-33', '像素风'), ('hero-38', '文字排版'), ('hero-45', '手账'), ('hero-20', '产品图'),
              ('hero-10', '超现实'), ('hero-36', '海报')]

USES_20 = [
    ('tpl-ecommerce-listing', '电商', '商品主图与场景图', '上传商品照片换背景、换颜色，批量生成不同场景的主图。'),
    ('tpl-editorial-poster', '营销', '海报与广告图', '标题、卖点和小字直接写进画面，适合活动海报、社媒配图和 banner。'),
    ('hero-39', '内容', '信息图与行程单', '时间线、地图、日程和贴士排在一张图里，适合旅游、科普和知识卡片。'),
    ('world-location-1', '游戏', '角色与场景设定', '角色、场景、道具分开生成也保持同一画风，可直接做概念设定。'),
    ('tpl-professional-headshot', '人像', '职业形象照', '用一张自拍生成正装、简洁背景的职业照，适合简历和团队页。'),
    ('tpl-icon-maker', '设计', '图标与周边', '图标、表情包、T 恤和马克杯样机，先出图再交给设计师细化。'),
]


def build(slug):
    c = base(slug)
    if slug == 'grok-image':
        c.update(
            title=f'Grok Imagine API 价格与接入｜xAI 生图 {P10} / 张起 - AnyAIGC',
            desc=f'Grok Imagine 生图 API（grok-imagine-image-2.0 等 3 个型号）价格对比与接入：按张计费 {P10} / 张起，文字排版、精准改图，并发不限，支持对公转账与增值税专票。',
            keywords='Grok Imagine API,Grok Imagine API 价格,Grok 生图 API,xAI 生图 API,grok-imagine-image-2.0,Grok 图片生成 API,Grok API Key,Grok Image API 企业,Grok Image API 发票,AnyAIGC',
            og_desc=f'Grok Imagine 全系生图 API：{P10} / 张起，文字排版、精准改图、15 种宽高比，并发不限。',
            og_alt_txt='AnyAIGC Grok Imagine API 价格与接入', crumb='Grok Image',
            product='Grok Imagine 图像 API（AnyAIGC）', product_desc='通过 AnyAIGC 调用 xAI Grok Imagine 系列图像生成与编辑模型，按张计费，接口 /v1/images/generations。',
            sku='grok-imagine-image-2.0', offers=[('Grok Imagine Image 2.0，1K Low（每张）', cny(M20['usd'])), ('Grok Imagine Image（每张）', cny(M10['usd'])),
                                                  ('Grok Imagine Image Quality，1K（每张）', cny(MQ['usd']))],
            kicker='xAI · Grok Imagine 图像系列', h1='Grok Imagine API',
            lead=f'xAI 的生图与改图模型，一个 Key 调用全系。全系 <strong>{P10} / 张起</strong>，推荐的 Image 2.0 {P20} / 张起，各档都低于 xAI 官方价，并发不限。',
            facts=[('型号', '3 个'), ('单价', f'{P10} / 张起'), ('接口', '生成 · 编辑'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='Grok Image 系列有哪些型号', about_lead='三个型号都在 AnyAIGC 上架，按张计费，改 <code>model</code> 字段即可切换。',
            lineup=[
                ('grok-imagine-image-2.0', '推荐', 'Grok Imagine Image 2.0', 'xAI 2026 年 8 月发布的新一代模型，也是 grok.com 上的 Quality 模式。',
                 ['文字排版、小字清晰', '生成与编辑同一个模型', '1k / 1.5k / 2k，low / medium 画质'], ),
                ('grok-imagine-image', '', 'Grok Imagine Image', 'xAI 第一代 Imagine 生图模型，2026 年初随 Imagine API 上线。',
                 ['文生图', '1k / 2k 同价', '系列里单价最低']),
                ('grok-imagine-image-quality', '已停用', 'Grok Imagine Image Quality', 'xAI 2026 年 5 月推出的高画质模式，11 月 2 日起并入 2.0。',
                 ['旧代码不用改', '1k / 1.5k / 2k 分档', '比 2.0 Low 贵，建议迁移']),
            ],
            features_h2='Grok Imagine 能做什么', features_lead='以下示例由 Imagine Image 2.0 生成，来自 xAI 官方发布页。', features=FEATURES_20,
            ratio_h2='一张图，任意比例', ratio_lead='同一画面在不同宽高比下由模型重新构图（xAI 官方示例）。用 <code>aspect_ratio</code> 参数指定。',
            ratio_alt='同一画面按 {r} 重新构图', ratio_list=['1:1', '3:4', '4:3', '9:16', '16:9', '2:3', '3:2', '9:19.5', '19.5:9', '9:20', '20:9', '1:2', '2:1', '21:9', '5:2', 'auto'],
            gallery_h2='Grok Imagine 官方示例', gallery_lead='以下图片由 Imagine Image 2.0 生成，来自 xAI 官方发布页。', gallery=GALLERY_20,
            pricing_h2='Grok Imagine API 价格', pricing_lead=f'按张计费，最低 {P10} / 张。Image 2.0 和 Quality 按分辨率和画质分档，改图另收输入图费用。',
            billing=[('按张计费', '按生成的图片张数计，不按 token 算'), ('分档', '2.0 / Quality 按分辨率和画质定价'), ('改图', f'每张输入图另收 {PIN}'), ('并发不限', '所有用户默认享有')],
            price_rows=[('grok-imagine-image-2.0', 'Grok Imagine Image 2.0（推荐）'), ('grok-imagine-image', 'Grok Imagine Image'),
                        ('grok-imagine-image-quality', 'Grok Imagine Image Quality（xAI 已并入 2.0）')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。改图时每张输入图另收 {PIN}；Grok Imagine Image 只支持生成，不收输入图费用。xAI 官方价：2.0 输出图 Low $0.04 / $0.05 / $0.06、Medium $0.06 / $0.07 / $0.08（1K / 1.5K / 2K），输入图 $0.01 / 张，Image $0.02 / 张（<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI 价格页</a>）。按成功生成计费，实时价格以<a href="{PRICING}">模型广场</a>为准。',
            costs=[('1,000 张第一代生图', f'1,000 × {P10}', total(1000, M10['usd']), 'Image，1K / 2K 同价'),
                   ('1,000 张 2.0 电商主图', f'1,000 × {P20}', total(1000, M20['usd']), 'Image 2.0，1K Low'),
                   ('1,000 张 2.0 高清海报', f'1,000 × {P20_HI}', total(1000, M20['usd_hi']), 'Image 2.0，2K Medium')],
            uses_h2='Grok Imagine API 使用场景', uses=USES_20,
            qs_h2='快速接入 Grok Imagine API', steps=STEPS('grok-imagine-image-2.0', True),
            tabs=[('py', 'Python', 'Python · Image 2.0 文生图', code_py('grok-imagine-image-2.0')),
                  ('curl', 'cURL', 'cURL · 返回图片链接', code_curl('grok-imagine-image-2.0')),
                  ('edit', '改图', 'Python · 上传图片编辑', code_edit('grok-imagine-image-2.0'))],
            qs_note=QS_NOTE, ent_h2='企业接入 Grok Imagine API',
            faq_h2='Grok Imagine API 常见问题',
            faqs=[
                ('Grok Imagine API 多少钱？', f'在 AnyAIGC 上都按张计费，不按 token 算：Grok Imagine Image 每张 {P10}（1K、2K 同价）；Image 2.0 按分辨率和画质分档，{P20}–{P20_HI} / 张；Quality {PQ}–{PQ_HI} / 张。改图时每张输入图另收 {PIN}。xAI 官方价 2.0 为 ${M20["official_lo"]}–${M20["official_hi"]} / 张（约 {O20}），Image 为 ${M10["official_lo"]} / 张（约 {O10}）。实时价格以模型广场为准。'),
                FAQ_DIFF,
                ('grok-imagine-image-quality 停用了吗？', f'xAI 在 2026 年 11 月 2 日停用了 <code>grok-imagine-image-quality</code>，之后发往这个模型名的请求会由 <code>grok-imagine-image-2.0</code> 以 <code>quality: "low"</code> 处理，请求和返回格式不变。AnyAIGC 上这个模型名仍可调用，{PQ}–{PQ_HI} / 张，比 2.0 Low 同分辨率贵约 {SAVE_Q}；建议直接把 <code>model</code> 改成 <code>grok-imagine-image-2.0</code>。'),
                ('支持哪些宽高比和分辨率？', '用 <code>aspect_ratio</code> 指定比例，支持 1:1、3:4、4:3、9:16、16:9、2:3、3:2、1:2、2:1、21:9 等，也可以填 <code>auto</code> 让模型决定；用 <code>resolution</code> 选分辨率：Image 2.0 和 Quality 支持 <code>1k</code>、<code>1.5k</code>、<code>2k</code>，Image 支持 <code>1k</code>、<code>2k</code>。Image 2.0 还支持 <code>quality</code>（low / medium / auto）。分辨率和画质越高，单价越高。'),
                ('能用参考图改图吗？', 'Image 2.0 支持图片编辑：向 <code>POST /v1/images/edits</code> 用 multipart/form-data 上传原图和修改指令即可。xAI 官方支持一次最多 5 张参考图合成，AnyAIGC 文档目前给出的是单张原图的示例，多图请以 AnyAIGC 接口文档为准。'),
                FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='现在开始调用 Grok Imagine', final_p=f'注册即送 200 万 tokens 试用额度，{P10} / 张起，并发不限。',
        )
    elif slug == 'grok-imagine-image-2.0':
        c.update(
            title=f'Grok Imagine Image 2.0 API 价格与接入｜{P20} / 张起 - AnyAIGC',
            desc=f'Grok Imagine Image 2.0 API（grok-imagine-image-2.0）按张计费 {P20} / 张起，各档低于 xAI 官方价：文字排版、精准改图、15 种宽高比，并发不限，支持对公转账与增值税专票。',
            keywords='Grok Imagine Image 2.0 API,grok-imagine-image-2.0,Grok Imagine API 价格,Grok 生图 API,Grok 图片编辑 API,xAI 生图 API,Grok Imagine Image 2.0 API 企业,Grok Imagine Image 2.0 API 发票,AnyAIGC',
            og_desc=f'Grok Imagine Image 2.0 API：{P20} / 张起，文字排版、精准改图、15 种宽高比，并发不限。',
            og_alt_txt='AnyAIGC Grok Imagine Image 2.0 API 价格与接入', crumb='Grok Imagine Image 2.0',
            product='Grok Imagine Image 2.0 API（AnyAIGC）', product_desc='通过 AnyAIGC 调用 xAI Grok Imagine Image 2.0（grok-imagine-image-2.0）图像生成与编辑模型，按张计费。',
            sku='grok-imagine-image-2.0', offers=[(f'Grok Imagine Image 2.0，{a} {q}（每张）', cny(u)) for a, q, u, _ in TIERS['grok-imagine-image-2.0']],
            kicker='xAI · 2026 年 8 月发布', h1='Grok Imagine Image 2.0 API',
            lead=f'xAI 新一代生图与改图模型，按设计师的思路排文字和版式，小字也清晰。在 AnyAIGC 上 <strong>{P20} / 张起</strong>，各档都低于 xAI 官方价，并发不限。',
            facts=[('模型名', '<code>grok-imagine-image-2.0</code>'), ('单价', f'{P20} / 张起'), ('分辨率', '1k / 1.5k / 2k'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='Grok Imagine Image 2.0 是什么',
            about_ps=[
                'Grok Imagine Image 2.0 是 xAI 在 2026 年 8 月发布的图像模型，在 grok.com 和 Grok App 里是新的 Quality 模式，在 API 里叫 <code>grok-imagine-image-2.0</code>。xAI 的定位是「做能直接用在工作里的图」：紧跟提示词的细节，像设计师一样规划文字和版式，多次生成和编辑时保留你给的内容。',
                f'按 xAI 发布页，它在 Arena 图像编辑榜和文生图榜都排第 2（2026-08-07 数据）。2026 年 11 月起，xAI 把旧的 <code>grok-imagine-image-quality</code> 并入这个模型。',
                f'在 AnyAIGC 上按分辨率和画质分档，{P20}–{P20_HI} / 张，改图每张输入图另收 {PIN}；xAI 官方价是 ${M20["official_lo"]}–${M20["official_hi"]} / 张（约 {O20}）。',
            ],
            spec=[('模型名', '<code>grok-imagine-image-2.0</code>'), ('生成', '/v1/images/generations'), ('编辑', '/v1/images/edits'),
                  ('分辨率', '1k / 1.5k / 2k'), ('画质', 'low / medium / auto'), ('宽高比', '15 种 + auto')],
            features_h2='Grok Imagine Image 2.0 能做什么', features_lead='以下示例由 Imagine Image 2.0 生成，来自 xAI 官方发布页。', features=FEATURES_20,
            ratio_h2='一张图，任意比例', ratio_lead='同一画面在不同宽高比下由模型重新构图（xAI 官方示例）。用 <code>aspect_ratio</code> 参数指定。',
            ratio_alt='同一画面按 {r} 重新构图', ratio_list=['1:1', '3:4', '4:3', '9:16', '16:9', '2:3', '3:2', '9:19.5', '19.5:9', '9:20', '20:9', '1:2', '2:1', '21:9', '5:2', 'auto'],
            world_h2='一套画风，做完整个世界观', world_lead='角色、场景和道具分别用几句提示词生成，画风保持一致，可直接用作视频分镜和游戏设定（xAI 官方示例）。',
            gallery_h2='Grok Imagine Image 2.0 官方示例', gallery_lead='以下图片由 Imagine Image 2.0 生成，来自 xAI 官方发布页，说明根据官方图片描述改写。', gallery=GALLERY_20,
            pricing_h2='Grok Imagine Image 2.0 API 价格', pricing_lead=f'按张计费，按分辨率和画质分 6 档，{P20}–{P20_HI} / 张。',
            billing=[('按张计费', '按生成的图片张数计，不按 token 算'), ('分档', '1K / 1.5K / 2K × Low / Medium'), ('改图', f'每张输入图另收 {PIN}'), ('并发不限', '所有用户默认享有')],
            price_rows=[('grok-imagine-image-2.0', 'Grok Imagine Image 2.0')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。改图时每张输入图另收 {PIN}。xAI 官方价：2.0 输出图 Low $0.04 / $0.05 / $0.06、Medium $0.06 / $0.07 / $0.08（1K / 1.5K / 2K），输入图 $0.01 / 张（<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI 价格页</a>）。按成功生成计费，实时价格以<a href="{PRICING}">模型广场</a>为准。',
            costs=[('1,000 张电商主图', f'1,000 × {P20}', total(1000, M20['usd']), '1K Low'),
                   ('1,000 张高清海报', f'1,000 × {P20_HI}', total(1000, M20['usd_hi']), '2K Medium'),
                   ('100 次改图', f'100 × ({P20} + {PIN})', total(100, M20['usd'], INPUT['grok-imagine-image-2.0'][0]), '1K Low，每次 1 张输入图')],
            uses_h2='Grok Imagine Image 2.0 使用场景', uses=USES_20,
            qs_h2='快速接入 Grok Imagine Image 2.0 API', steps=STEPS('grok-imagine-image-2.0', True),
            tabs=[('py', 'Python', 'Python · grok-imagine-image-2.0 文生图', code_py('grok-imagine-image-2.0')),
                  ('curl', 'cURL', 'cURL · 返回图片链接', code_curl('grok-imagine-image-2.0')),
                  ('edit', '改图', 'Python · 上传图片编辑', code_edit('grok-imagine-image-2.0'))],
            qs_note=QS_NOTE, ent_h2='企业接入 Grok Imagine Image 2.0 API',
            faq_h2='Grok Imagine Image 2.0 API 常见问题',
            faqs=[
                ('Grok Imagine Image 2.0 API 多少钱？', f'AnyAIGC 上 Grok Imagine Image 2.0（<code>grok-imagine-image-2.0</code>）按张计费，按分辨率和画质分档：Low 画质 1K / 1.5K / 2K 为 {P20} / ¥{cny(tier("grok-imagine-image-2.0", "1.5K", "Low"))} / ¥{cny(tier("grok-imagine-image-2.0", "2K", "Low"))}，Medium 为 {P20_1KM} / ¥{cny(tier("grok-imagine-image-2.0", "1.5K", "Medium"))} / {P20_HI}；改图每张输入图另收 {PIN}。xAI 官方价是 ${M20["official_lo"]}–${M20["official_hi"]} / 张（约 {O20}），另收输入图费用。按成功生成计费，实时价格以模型广场为准。'),
                ('Image 2.0 和之前的 Grok Imagine 有什么区别？', f'2.0 在文字排版、指令遵循和改图上都有提升，信息图、海报里的小字更清晰，多轮编辑时保留原图内容。它同时支持 <code>quality</code>（low / medium / auto）和 21:9、5:2 两种新比例。第一代 <code>grok-imagine-image</code> 仍可调用，{P10} / 张，只做文生图的话更便宜。'),
                ('quality 参数怎么选？', f'<code>quality</code> 可填 <code>low</code>、<code>medium</code> 或 <code>auto</code>。按 xAI 文档，默认 <code>auto</code> 目前生成时用 low、编辑时用 medium；low 速度更快、价格更低，medium 细节更多。以 1K 为例，Low {P20} / 张，Medium {P20_1KM} / 张。'),
                ('支持哪些宽高比和分辨率？', '<code>aspect_ratio</code> 支持 1:1、3:4、4:3、9:16、16:9、2:3、3:2、9:19.5、19.5:9、9:20、20:9、1:2、2:1、21:9、5:2，也可以填 <code>auto</code>；<code>resolution</code> 填 <code>1k</code>、<code>1.5k</code> 或 <code>2k</code>，分辨率越高单价越高。'),
                ('怎么改图？能用多张参考图吗？', '向 <code>POST /v1/images/edits</code> 用 multipart/form-data 上传 <code>image</code>、<code>prompt</code> 和 <code>model</code>，只写需要修改的部分，其余会保持不变。xAI 官方支持一次最多 5 张参考图合成，AnyAIGC 文档目前给出的是单张原图的示例，多图请以 AnyAIGC 接口文档为准。'),
                ('grok-imagine-image-quality 还能用吗？', f'xAI 已在 2026 年 11 月 2 日把 <code>grok-imagine-image-quality</code> 并入 2.0，请求会由 2.0 以 low 画质处理。旧代码在 AnyAIGC 上仍可调用（{PQ}–{PQ_HI} / 张），比 2.0 Low 同分辨率贵约 {SAVE_Q}，建议把 <code>model</code> 直接改成 <code>grok-imagine-image-2.0</code>。'),
                FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='现在开始调用 Grok Imagine Image 2.0', final_p=f'注册即送 200 万 tokens 试用额度，{P20} / 张起，并发不限。',
        )
    elif slug == 'grok-imagine-image':
        c.update(
            title=f'Grok Imagine Image API 价格与接入｜{P10} / 张 - AnyAIGC',
            desc=f'Grok Imagine Image API（grok-imagine-image）是 xAI 第一代 Imagine 生图模型，按张计费 {P10} / 张，低于官方价，1k / 2k 输出，并发不限，支持对公转账与增值税专票。',
            keywords='Grok Imagine Image API,grok-imagine-image,Grok Imagine API 价格,Grok 生图 API,xAI 生图 API,Grok API Key,Grok Imagine Image API 企业,Grok Imagine Image API 发票,AnyAIGC',
            og_desc=f'Grok Imagine Image API：{P10} / 张，xAI 第一代 Imagine 生图模型，1k / 2k 输出，并发不限。',
            og_alt_txt='AnyAIGC Grok Imagine Image API 价格与接入', crumb='Grok Imagine Image',
            product='Grok Imagine Image API（AnyAIGC）', product_desc='通过 AnyAIGC 调用 xAI Grok Imagine Image（grok-imagine-image）文生图模型，按张计费。',
            sku='grok-imagine-image', offers=[('Grok Imagine Image（每张）', cny(M10['usd']))],
            kicker='xAI · 第一代 Imagine 生图模型', h1='Grok Imagine Image API',
            lead=f'xAI 随 Imagine API 推出的第一代文生图模型，接口简单、出图稳定。在 AnyAIGC 上 <strong>{P10} / 张</strong>，约为官方价的 6 折，并发不限。',
            facts=[('模型名', '<code>grok-imagine-image</code>'), ('单价', f'{P10} / 张'), ('分辨率', '1k / 2k'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='Grok Imagine Image 是什么',
            about_ps=[
                f'Grok Imagine Image（<code>grok-imagine-image</code>）是 xAI 在 2026 年初随 Grok Imagine API 推出的图像生成模型，xAI 文档里称为 1.0，快照名 <code>{M10["alias"]}</code>。它根据文字描述生成图片，支持多种宽高比和 1k / 2k 输出。',
                f'xAI 在 2026 年 8 月推出了 Image 2.0，文字排版和改图更强，在 AnyAIGC 上 {P20} / 张起。第一代模型没有停用，只做文生图时它更便宜（{P10} / 张），已经接好的代码也可以继续用。',
                f'在 AnyAIGC 上每张 {P10}，xAI 官方价 ${M10["official_lo"]} / 张（约 {O10}）。AnyAIGC 上这个模型走 <code>/v1/images/generations</code> 生成接口。',
            ],
            spec=[('模型名', '<code>grok-imagine-image</code>'), ('接口', '/v1/images/generations'), ('分辨率', '1k / 2k'),
                  ('宽高比', '1:1、16:9、9:16 等'), ('返回', 'b64_json / url'), ('快照', f'<code>{M10["alias"]}</code>')],
            features_h2='Grok Imagine Image 能做什么',
            features=[
                (None, '文生图', '根据一句文字描述生成图片，写实、插画、海报等常见风格都能出。'),
                (None, '多种宽高比', '用 <code>aspect_ratio</code> 指定 1:1、16:9、9:16、3:2 等比例，适配封面、竖版海报和横幅。'),
                (None, '1k / 2k 输出', '用 <code>resolution</code> 选择 1k 或 2k，xAI 官方两档同价。'),
                (None, 'base64 或链接', '<code>response_format</code> 选 <code>b64_json</code> 直接拿图片数据，或选 <code>url</code> 拿临时链接。'),
                (None, '接口兼容', '请求格式和 OpenAI 的 <code>/v1/images/generations</code> 一致，已有的生图代码改 <code>model</code> 即可。'),
                (None, '一键升级 2.0', f'需要改图或更好的文字排版时，把 <code>model</code> 改成 <code>grok-imagine-image-2.0</code>（{P20} / 张起）。'),
            ],
            pricing_h2='Grok Imagine Image API 价格', pricing_lead=f'固定单价，每张 {P10}，不按 token 算。',
            billing=[('按张计费', '固定单价，不按 token 算'), ('不分档', '1k / 2k 同价'), ('并发不限', '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')],
            price_rows=[('grok-imagine-image', 'Grok Imagine Image'), ('grok-imagine-image-2.0', '对比：Grok Imagine Image 2.0')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。Grok Imagine Image 1K、2K 同价，只支持生成。xAI 官方价：Image 1K、2K 都是 $0.02 / 张（<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI 价格页</a>）。Image 2.0 的完整分档见 <a href="/zh/models/grok-imagine-image-2.0#pricing">Image 2.0 价格</a>。按成功生成计费，实时价格以<a href="{PRICING}">模型广场</a>为准。',
            costs=[('100 张配图', f'100 × {P10}', total(100, M10['usd']), '一次 1 张'),
                   ('1,000 张批量出图', f'1,000 × {P10}', total(1000, M10['usd']), '并发不限'),
                   ('同样 1,000 张用 2.0', f'1,000 × {P20}', total(1000, M20['usd']), 'Image 2.0，1K Low')],
            uses_h2='Grok Imagine Image API 使用场景',
            uses=[(None, '内容', '文章与社媒配图', '按标题或摘要生成配图，批量处理文章封面。'),
                  (None, '营销', '广告素材', '同一主题快速出多版画面，用于投放测试。'),
                  (None, '产品', '应用内生图', '在 App 或小程序里接入文生图功能，按张结算成本清晰。'),
                  (None, '设计', '灵感草图', '先出几张草图确认方向，再交给设计师细化。'),
                  (None, '游戏', '概念图', '快速生成场景、道具和角色的概念图。'),
                  (None, '迁移', '已有代码继续用', '接入 xAI 时写好的代码只需换 Base URL 和 Key。')],
            qs_h2='快速接入 Grok Imagine Image API', steps=STEPS('grok-imagine-image', False),
            tabs=[('py', 'Python', 'Python · grok-imagine-image 文生图', code_py('grok-imagine-image', quality=False)),
                  ('curl', 'cURL', 'cURL · 返回图片链接', code_curl('grok-imagine-image'))],
            qs_note=QS_NOTE.replace(f'、<a href="{DOCS_EDIT}" target="_blank" rel="noopener">编辑图片</a>', ''),
            ent_h2='企业接入 Grok Imagine Image API',
            faq_h2='Grok Imagine Image API 常见问题',
            faqs=[
                ('Grok Imagine Image API 多少钱？', f'AnyAIGC 上 Grok Imagine Image（<code>grok-imagine-image</code>）每张 {P10}，按张计费，1k 和 2k 同价。xAI 官方价是 ${M10["official_lo"]} / 张（约 {O10}）。按成功生成计费，实时价格以模型广场为准。'),
                FAQ_DIFF,
                ('grok-imagine-image 会停用吗？', f'不会受这次调整影响。xAI 2026 年 11 月 2 日停用的是 <code>grok-imagine-image-quality</code>，<code>grok-imagine-image</code> 仍正常提供。如果需要改图或更好的文字效果，建议换成 <code>grok-imagine-image-2.0</code>（{P20} / 张）。'),
                ('支持哪些宽高比和分辨率？', '用 <code>aspect_ratio</code> 指定比例，例如 1:1、16:9、9:16、3:2、2:3、4:3、3:4；用 <code>resolution</code> 选 <code>1k</code> 或 <code>2k</code>。<code>quality</code> 参数只有 Image 2.0 支持。'),
                ('能改图吗？', '在 AnyAIGC 上，<code>grok-imagine-image</code> 走生成接口 <code>/v1/images/generations</code>。需要上传原图修改的话，请用 <code>grok-imagine-image-2.0</code> 调用 <code>/v1/images/edits</code>。'),
                FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='现在开始调用 Grok Imagine Image', final_p=f'注册即送 200 万 tokens 试用额度，每张 {P10}，并发不限。',
        )
    elif slug == 'grok-imagine-image-quality':
        c.update(
            title=f'Grok Imagine Image Quality API 价格与迁移｜{PQ} 起 - AnyAIGC',
            desc=f'Grok Imagine Image Quality API（grok-imagine-image-quality）已被 xAI 并入 Image 2.0，旧代码仍可用，{PQ} / 张起，附迁移说明，并发不限，支持对公转账与增值税专票。',
            keywords='Grok Imagine Image Quality API,grok-imagine-image-quality,grok-imagine-image-quality 停用,Grok Imagine API 价格,Grok 生图 API,grok-imagine-image-2.0,Grok Imagine Image Quality API 企业,Grok Imagine Image Quality API 发票,AnyAIGC',
            og_desc=f'grok-imagine-image-quality 已并入 Image 2.0：旧代码在 AnyAIGC 上继续可用，{PQ} / 张起，换成 2.0 更便宜。',
            og_alt_txt='AnyAIGC Grok Imagine Image Quality API 价格与迁移', crumb='Grok Imagine Image Quality',
            product='Grok Imagine Image Quality API（AnyAIGC）', product_desc='通过 AnyAIGC 调用 grok-imagine-image-quality（xAI 已并入 Grok Imagine Image 2.0），按张计费。',
            sku='grok-imagine-image-quality', offers=[(f'Grok Imagine Image Quality，{a}（每张）', cny(u)) for a, _, u, _ in TIERS['grok-imagine-image-quality']],
            kicker='xAI · 2026 年 5 月发布 · 已并入 2.0', h1='Grok Imagine Image Quality API',
            lead=f'xAI 曾经的高画质生图模式。2026 年 11 月 2 日起官方把它并入 Image 2.0，旧代码在 AnyAIGC 上仍可调用，<strong>{PQ} / 张起</strong>，换成 2.0 Low 每张便宜约 {SAVE_Q}。',
            notice=f'<strong>xAI 已停用此模型。</strong>自 2026 年 11 月 2 日起，发往 <code>grok-imagine-image-quality</code> 的请求由 Grok Imagine Image 2.0 以 low 画质处理。新项目请直接使用 <a href="/zh/models/grok-imagine-image-2.0">Grok Imagine Image 2.0</a>。',
            strip_label='Imagine Image 2.0 官方示例图（Quality 请求现由 2.0 处理）',
            facts=[('模型名', '<code>grok-imagine-image-quality</code>'), ('单价', f'{PQ} / 张起'), ('状态', '已并入 2.0'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='grok-imagine-image-quality 现在是什么情况',
            about_ps=[
                'Grok Imagine Image Quality 是 xAI 在 2026 年 5 月推出的高画质生图与改图模式，主打更真实的画面和更好的多语言文字渲染。2026 年 8 月，xAI 发布 Image 2.0，并把 grok.com 上的 Quality 模式换成了 2.0。',
                f'xAI 在 2026 年 9 月宣布、11 月 2 日正式停用 <code>grok-imagine-image-quality</code>。之后发往这个模型名的生成和编辑请求，都由 <code>grok-imagine-image-2.0</code> 以 <code>quality: "low"</code> 处理，请求和返回格式不变（<a href="{XAI_MIGRATION}" target="_blank" rel="noopener">xAI 迁移说明</a>）。',
                f'在 AnyAIGC 上这个模型名仍可调用，按分辨率计费，1K / 1.5K / 2K 为 {PQ} / ¥{cny(tier("grok-imagine-image-quality", "1.5K"))} / {PQ_HI}。换成 <code>grok-imagine-image-2.0</code> 的 Low 画质，每档便宜约 {SAVE_Q}，还能用 <code>quality: "medium"</code> 和 21:9、5:2 两种新比例。',
            ],
            spec=[('模型名', '<code>grok-imagine-image-quality</code>'), ('状态', 'xAI 已停用'), ('实际处理', '<code>grok-imagine-image-2.0</code>'),
                  ('分辨率', '1k / 1.5k / 2k'), ('生成', '/v1/images/generations'), ('编辑', '/v1/images/edits')],
            features_h2='迁移到 Image 2.0 能多得到什么', features_lead='以下示例由 Imagine Image 2.0 生成，来自 xAI 官方发布页。',
            features=[FEATURES_20[0], FEATURES_20[1], FEATURES_20[4]],
            gallery_h2='Image 2.0 官方示例', gallery_lead='Quality 的请求现在由 Image 2.0 处理。以下图片由 Image 2.0 生成，来自 xAI 官方发布页。', gallery=GALLERY_20[:6],
            pricing_h2='Grok Imagine Image Quality API 价格', pricing_lead=f'按分辨率分 3 档，{PQ}–{PQ_HI} / 张。同分辨率下 Image 2.0 Low 更便宜。',
            billing=[('按张计费', '按生成的图片张数计，不按 token 算'), ('分档', '1K / 1.5K / 2K'), ('改图', f'每张输入图另收 {PIN}'), ('迁移更省', f'2.0 Low 每张便宜约 {SAVE_Q}')],
            price_rows=[('grok-imagine-image-quality', '旧模型名（xAI 已并入 2.0）'), ('grok-imagine-image-2.0', '推荐：Grok Imagine Image 2.0')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。改图时每张输入图另收 {PIN}。xAI 已不再公布 Quality 的官方价。按成功生成计费，实时价格以<a href="{PRICING}">模型广场</a>为准。',
            costs=[('1,000 张图（Quality）', f'1,000 × {PQ}', total(1000, MQ['usd']), '1K'),
                   ('同样 1,000 张用 2.0', f'1,000 × {P20}', total(1000, M20['usd']), '2.0，1K Low'),
                   ('迁移后每 1,000 张省', f'1,000 × ({PQ} − {P20})', f"¥{1000 * (float(MQ['usd']) - float(M20['usd'])) * 6.689338:,.0f}", '同为 1K')],
            uses_h2='三步完成迁移',
            uses=[(None, '第 1 步', '改模型名', '把请求里的 <code>"model": "grok-imagine-image-quality"</code> 改成 <code>"grok-imagine-image-2.0"</code>。'),
                  (None, '第 2 步', '按需加 quality', '想要更多细节就加 <code>"quality": "medium"</code>，不加则默认 <code>auto</code>。'),
                  (None, '第 3 步', '核对返回', '返回格式不变，<code>data</code> 里仍是 <code>b64_json</code> 或 <code>url</code>，原有解析代码不用改。')],
            qs_h2='调用示例', steps=STEPS('grok-imagine-image-2.0', True),
            tabs=[('py', 'Python', 'Python · 迁移后写法（grok-imagine-image-2.0）', code_py('grok-imagine-image-2.0')),
                  ('curl', 'cURL', 'cURL · 旧模型名仍可调用', code_curl('grok-imagine-image-quality'))],
            qs_note=QS_NOTE, ent_h2='企业接入 Grok Imagine Image Quality API',
            faq_h2='Grok Imagine Image Quality API 常见问题',
            faqs=[
                ('grok-imagine-image-quality 停用了吗？', f'是的。xAI 在 2026 年 11 月 2 日停用了 <code>grok-imagine-image-quality</code>，之后的请求由 <code>grok-imagine-image-2.0</code> 以 <code>quality: "low"</code> 处理，请求和返回格式不变。AnyAIGC 上这个模型名仍可调用，新项目请直接用 <a href="/zh/models/grok-imagine-image-2.0">Grok Imagine Image 2.0</a>。'),
                ('Grok Imagine Image Quality API 多少钱？', f'AnyAIGC 上按分辨率计费：1K {PQ}、1.5K ¥{cny(tier("grok-imagine-image-quality", "1.5K"))}、2K {PQ_HI} / 张，改图每张输入图另收 {PIN}。同分辨率下 Image 2.0 Low 每张便宜约 {SAVE_Q}。xAI 已不再单独公布 Quality 的官方价。按成功生成计费，实时价格以模型广场为准。'),
                ('迁移到 2.0 要改哪些代码？', '只需要把 <code>model</code> 改成 <code>grok-imagine-image-2.0</code>，接口地址、请求字段和返回格式都不变。2.0 额外支持 <code>quality</code>（low / medium / auto）和 21:9、5:2 两种比例。用 Low 画质时同分辨率更便宜，Medium 画质单价更高。'),
                ('不改代码会有什么影响？', '请求不会报错，会由 2.0 以 low 画质处理，返回里的 <code>model</code> 字段会显示实际处理的模型。如果你需要 medium 画质，就需要改成 2.0 并传 <code>quality</code>。'),
                FAQ_DIFF, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='把 Quality 换成 Image 2.0', final_p=f'2.0 Low {P20} / 张起，同分辨率比 Quality 更便宜，并发不限。',
        )
    return c
