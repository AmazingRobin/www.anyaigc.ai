# Grok Video 系列专题页中文文案。build(slug) 返回 grok_video_layout / grok_image_layout 需要的字段。
from grok_video_data import (MODELS, TIERS, INPUT_IMG, INPUT_VID, DOCS_GEN, DOCS_EDIT, DOCS_QUERY, XAI_15_POST, XAI_PRICING, XAI_API, tier, cny)
from grok_image_data import REG, PRICING, SUPPORT
from grok_video_layout import money

S15, SL, S10 = 'grok-imagine-video-1.5-preview', 'grok-imagine-video-1.5-lite', 'grok-imagine-video'
Y = lambda usd: f'¥{cny(usd)}'
P15, PL, P10 = Y(MODELS[S15]['usd']), Y(MODELS[SL]['usd']), Y(MODELS[S10]['usd'])
P15_720, PL_720, P10_720 = Y(tier(S15, '720p')), Y(tier(SL, '720p')), Y(tier(S10, '720p'))
PL_1080 = Y(tier(SL, '1080p'))
IMG15, IMG10, VID10 = Y(INPUT_IMG[S15][0]), Y(INPUT_IMG[S10][0]), Y(INPUT_VID[S10][0])
RATE_NOTE = '按 1 美元 ≈ ¥6.689 换算成人民币'
SRC = f'（<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI 价格页</a>）'
TAIL = f'按成功生成的视频秒数计费，实时价格以<a href="{PRICING}">模型广场</a>为准。'

FAMILY = [
    ('grok-video', '总览', 'Grok Video 全系总览', '三个型号的价格对比与选型'),
    (S15, '推荐', 'Grok Imagine Video 1.5', f'{P15} / 秒起，画面、动作和对白更好'),
    (SL, '最低价', 'Grok Imagine Video 1.5 Lite', f'{PL} / 秒起，批量出片'),
    (S10, '', 'Grok Imagine Video', f'{P10} / 秒起，支持改视频'),
]
FAMILY_H2 = 'Grok Video 系列模型'
FAMILY_LEAD = '同一个 API Key、同一个接口，改 model 字段即可切换。'

PROMPT = '清晨的海边小镇，一只橘猫沿着石阶慢慢走下来，海浪声和远处的海鸥叫声，电影感'
IMG_URL = 'https://example.com/first-frame.jpg'


def code_py(model, res='720p'):
    return f'''import os
import time
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
HEADERS = {{"Authorization": "Bearer " + API_KEY}}

# 1. 提交任务
task = requests.post(
    "https://anyaigc.ai/v1/videos/generations",
    headers=HEADERS,
    json={{
        "model": "{model}",
        "prompt": "{PROMPT}",
        "duration": 6,  # 1–15 秒，按秒计费
        "aspect_ratio": "16:9",  # 16:9 / 9:16 / 1:1
        "resolution": "{res}",  # 分辨率越高，每秒越贵
    }},
    timeout=60,
).json()
task_id = task.get("request_id") or task.get("id")

# 2. 轮询结果（生成通常需要几十秒到几分钟）
while True:
    r = requests.get(f"https://anyaigc.ai/v1/videos/{{task_id}}", headers=HEADERS, timeout=30).json()
    if r.get("status") in ("done", "completed", "succeeded"):
        print(r.get("video_url") or r["video"]["url"])  # 临时链接，请及时下载
        break
    if r.get("status") in ("failed", "expired"):
        raise RuntimeError(r)
    time.sleep(10)'''


def code_curl(model, res='480p'):
    return f'''# 提交图生视频任务：image 传首帧图片，画面比例跟随图片
curl https://anyaigc.ai/v1/videos/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "镜头缓缓推近，人物转头微笑",
    "image": {{"url": "{IMG_URL}"}},
    "duration": 5,
    "aspect_ratio": "16:9",
    "resolution": "{res}"
  }}'

# 查询任务状态，status 为 done 时取视频链接
curl https://anyaigc.ai/v1/videos/<request_id> \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY"'''


def code_edit():
    return '''# 改视频：上传原视频链接 + 修改指令，输出时长与原视频一致
curl https://anyaigc.ai/v1/videos/edits \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "grok-imagine-video",
    "prompt": "把人物的卫衣换成红色，其余保持不变",
    "video": {"url": "https://example.com/source.mp4"},
    "aspect_ratio": "16:9",
    "resolution": "480p"
  }'
# 返回任务 ID 后，同样用 GET /v1/videos/<request_id> 查询结果'''


STEPS = lambda model: [
    f'<a href="{REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
    '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
    f'向 <code>POST https://anyaigc.ai/v1/videos/generations</code> 提交任务，<code>model</code> 填 <code>{model}</code>，再用 <code>GET /v1/videos/{{request_id}}</code> 轮询结果。',
]
QS_NOTE = (f'视频生成是异步任务：提交后返回任务 ID，轮询到完成状态再取视频链接，链接是临时的，请及时下载。字段说明见 AnyAIGC 文档：'
           f'<a href="{DOCS_GEN}" target="_blank" rel="noopener">创建视频</a>、<a href="{DOCS_QUERY}" target="_blank" rel="noopener">查询视频</a>、'
           f'<a href="{DOCS_EDIT}" target="_blank" rel="noopener">编辑视频</a>。')

ENT_LEAD = '短视频团队、电商公司和内容平台可以直接走企业流程采购，财务、法务和技术对接都有对应支持。'
FAQ_INVOICE = ('AnyAIGC 能开发票吗？支持增值税专票吗？', '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。')
FAQ_CONTRACT = ('企业可以对公转账和签合同吗？', f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。')
FAQ_CN = ('没有 xAI 账号能调用吗？国内能直连吗？', '能。在 AnyAIGC 注册即可拿到 API Key，不需要 xAI 账号或海外信用卡。接口地址是 <code>https://anyaigc.ai</code>，国内网络可以直接调用，同一个 Key 还能调用平台上 300+ 其他模型。')
FAQ_CONC = ('并发有限制吗？', 'AnyAIGC 对 Grok Video 系列不设并发限制，所有用户默认享有，批量生成不用排队申请。')
FAQ_ASYNC = ('为什么提交后没有直接返回视频？', '视频生成是异步任务。提交后会先返回任务 ID，用 <code>GET /v1/videos/{request_id}</code> 每 10 秒左右查询一次，状态完成后取视频链接。生成通常需要几十秒到几分钟，链接是临时的，请及时下载保存。')
FAQ_AUDIO = ('生成的视频有声音吗？', '有。Grok Imagine 会同时生成画面和声音，包括音效、环境声和人物对白，不需要后期配音。Video 1.5 和 1.5 Lite 支持口型同步的对白。')
FAQ_DIFF = ('Video 1.5、1.5 Lite 和 Video 有什么区别，该选哪个？',
            f'<strong>Grok Imagine Video 1.5</strong>（<code>{S15}</code>）画面、动作和对白最好，{P15} / 秒起，适合广告和成片。'
            f'<strong>1.5 Lite</strong>（<code>{SL}</code>）是系列里最便宜的，{PL} / 秒起，支持到 1080p，适合大批量生成和草稿。'
            f'<strong>Grok Imagine Video</strong>（<code>{S10}</code>）是第一代模型，{P10} / 秒起，系列里只有它支持上传原视频修改。')

WHY = [('一个 Key，300+ 模型', 'Grok Imagine、Sora、Veo、Kling 等视频模型和对话、生图模型共用一个 API Key 和余额。'),
       ('国内直连', '接口地址 <code>https://anyaigc.ai</code>，国内网络可直接调用，不需要 xAI 账号。'),
       ('低于官方价', '按秒计费，各档单价都低于 xAI 官方价，控制台可查每次调用的扣费明细。'),
       ('并发不限', '所有用户默认不限并发，批量生成不用排队申请。')]

FEATURES = [
    ('speech-1', '原生声音与对白', '画面、音效、环境声和人物对白一次生成，口型和语音同步，不用再找配音。'),
    ('property', '文生视频与图生视频', '用一句描述生成视频，或者上传一张首帧图片，让画面动起来。'),
    ('try-on', '商品与试穿', '把商品图和人物图放进同一段视频，适合电商展示和虚拟试衣。'),
    ('mockup-moon', '把设计稿变成实拍', '草图、3D 模型或原型图转成写实镜头，再换不同场景。'),
    ('perfume', '广告氛围片', '光影、材质和运镜都做得细，适合香水、饮品和服装的广告素材。'),
    ('speech-2', '1–15 秒，多种比例', '时长 1–15 秒按秒可调，支持 16:9 横屏、9:16 竖屏和 1:1 方形。'),
]
GALLERY = [('property', '房产'), ('dining', '餐饮'), ('perfume', '香水'), ('clothing', '服装'), ('speech-1', '对白'), ('speech-2', '电影感'),
           ('mockup-3d', '原型'), ('mockup-earth', '场景替换')]
USES = [
    ('clothing', '电商', '商品视频与试穿', '把商品图做成展示视频，或者让模特换上指定服装，批量生成详情页素材。'),
    ('perfume', '广告', '品牌广告素材', '同一主题快速出多版 6–10 秒的广告片，用于投放测试。'),
    ('speech-1', '短视频', '口播与剧情片段', '人物开口说话、口型同步，适合短视频口播、剧情和社媒内容。'),
    ('property', '房产', '样板间漫游', '用一张室内图生成漫游镜头，展示户型和装修效果。'),
    ('mockup-3d', '设计', '原型与概念视频', '把 3D 模型或设计稿变成写实视频，用于提案和发布会。'),
    ('restyle-a', '创意', '风格化与改视频', '用第一代模型把已有视频换风格、换服装颜色，保留原有动作。'),
]
OFFERS = lambda s, name: [(f'{name}，{r}（每秒）', cny(u)) for r, u, _ in TIERS[s]]


def base(slug):
    return dict(family=FAMILY, family_h2=FAMILY_H2, family_lead=FAMILY_LEAD, why_h2='为什么通过 AnyAIGC 调用', why=WHY,
                docs=DOCS_GEN, ent_lead=ENT_LEAD, in_other=f'{EN_NAME[slug]} API in English', category='视频生成 API',
                in_img='图生视频每张输入图另收 {p}', in_vid='改视频按原视频每秒另收 {p}')


EN_NAME = {'grok-video': 'Grok Video', S15: 'Grok Imagine Video 1.5', SL: 'Grok Imagine Video 1.5 Lite', S10: 'Grok Imagine Video'}


def build(slug):
    c = base(slug)
    if slug == 'grok-video':
        c.update(
            title=f'Grok 视频生成 API 价格与接入｜{PL} / 秒起 - AnyAIGC',
            desc=f'Grok Imagine 视频生成 API（Video 1.5、1.5 Lite、Video）价格对比与接入：按秒计费 {PL} / 秒起，原生声音与对白，并发不限，支持对公转账与增值税专票。',
            keywords='Grok Imagine Video API,Grok Imagine Video API 价格,Grok 视频生成 API,xAI 视频生成 API,grok-imagine-video,Grok 图生视频 API,Grok 文生视频 API,Grok Video API 企业,Grok Video API 发票,AnyAIGC',
            og_desc=f'Grok Imagine 全系视频 API：{PL} / 秒起，原生声音与对白，1–15 秒，并发不限。',
            og_alt_txt='AnyAIGC Grok 视频生成 API 价格与接入', crumb='Grok Video',
            product='Grok Imagine 视频 API（AnyAIGC）', product_desc='通过 AnyAIGC 调用 xAI Grok Imagine 系列视频生成模型，按秒计费，接口 /v1/videos/generations。',
            sku=S15, offers=OFFERS(S15, 'Grok Imagine Video 1.5') + OFFERS(SL, 'Grok Imagine Video 1.5 Lite') + OFFERS(S10, 'Grok Imagine Video'),
            kicker='xAI · Grok Imagine 视频系列', h1='Grok Video API',
            lead=f'xAI 的视频生成模型，画面和声音一起生成。一个 Key 调用全系，最低 <strong>{PL} / 秒</strong>，各档都低于 xAI 官方价，并发不限。',
            hero_vid='speech-2', hero_cap='xAI 官方示例，有声视频',
            facts=[('型号', '3 个'), ('单价', f'{PL} / 秒起'), ('时长', '1–15 秒'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='Grok Video 系列有哪些型号', about_lead='三个型号都在 AnyAIGC 上架，按秒计费，改 <code>model</code> 字段即可切换。',
            lineup=[
                (S15, '推荐', 'Grok Imagine Video 1.5', 'xAI 2026 年 6 月正式发布的新一代视频模型，画面、动作和对白更好。', ['文生视频、图生视频', '口型同步的对白', '480p / 720p']),
                (SL, '最低价', 'Grok Imagine Video 1.5 Lite', 'Video 1.5 的轻量低价版，适合大批量生成和快速出草稿。', ['文生视频、图生视频', '480p / 720p / 1080p', '系列里每秒最便宜']),
                (S10, '', 'Grok Imagine Video', 'xAI 2026 年 1 月随 Imagine API 推出的第一代视频模型。', ['文生视频、图生视频', '上传原视频修改', '480p / 720p']),
            ],
            features_h2='Grok 视频模型能做什么', features_lead='以下视频由 Grok Imagine 生成，来自 xAI 官方页面，点击播放（有声音）。', features=FEATURES,
            edits_h2='改视频：换颜色、换风格', edits_lead='第一代 <code>grok-imagine-video</code> 支持上传原视频，用一句话修改服装、颜色或整体风格，人物动作保持不变（xAI 官方示例）。',
            edit_rows=[('换服装', [('edit-input', '原视频'), ('edit-a', '结果 1'), ('edit-b', '结果 2')]),
                       ('换风格', [('restyle-original', '原视频'), ('restyle-a', '结果 1'), ('restyle-b', '结果 2')])],
            edits_note='改视频走 <code>POST /v1/videos/edits</code>，目前只有 <code>grok-imagine-video</code> 支持，输出最高 720p，时长与原视频一致。',
            gallery_h2='Grok Imagine 官方示例视频', gallery_lead='以下视频由 Grok Imagine 生成，来自 xAI 官方 Imagine API 页面和 Video 1.5 发布页。', gallery=GALLERY,
            pricing_h2='Grok 视频 API 价格', pricing_lead=f'按输出视频秒数计费，按分辨率分档，最低 {PL} / 秒。',
            billing=[('按秒计费', '按生成的视频时长计，不按 token 算'), ('分档', '480p / 720p / 1080p'), ('图生视频', f'每张输入图另收 {IMG10}–{IMG15}'), ('并发不限', '所有用户默认享有')],
            price_rows=[(S15, 'Grok Imagine Video 1.5（推荐）'), (SL, 'Grok Imagine Video 1.5 Lite（最低价）'), (S10, 'Grok Imagine Video（支持改视频）')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。xAI 官方价：Video 1.5 480p $0.08、720p $0.14 / 秒；1.5 Lite 480p $0.02、720p $0.03、1080p $0.14 / 秒；Video 480p $0.05、720p $0.07 / 秒{SRC}。{TAIL}',
            costs=[('100 条 6 秒草稿', f'100 × 6 秒 × {PL}', money('zh', MODELS[SL]['usd'], 600), '1.5 Lite，480p'),
                   ('100 条 10 秒广告片', f'100 × 10 秒 × {P15_720}', money('zh', tier(S15, '720p'), 1000), 'Video 1.5，720p'),
                   ('100 条 8 秒图生视频', f'100 × (8 秒 × {P10} + {IMG10})', money('zh', MODELS[S10]['usd'], 800, 100 * float(INPUT_IMG[S10][0])), 'Video，480p')],
            uses_h2='Grok 视频 API 使用场景', uses=USES,
            qs_h2='快速接入 Grok 视频 API', steps=STEPS(S15),
            tabs=[('py', 'Python', 'Python · 文生视频 + 轮询结果', code_py(S15)),
                  ('curl', 'cURL', 'cURL · 图生视频', code_curl(SL)),
                  ('edit', '改视频', 'cURL · 上传原视频修改', code_edit())],
            qs_note=QS_NOTE, ent_h2='企业接入 Grok Video API',
            faq_h2='Grok Video API 常见问题',
            faqs=[
                ('Grok 视频 API 多少钱？', f'在 AnyAIGC 上按输出视频秒数计费：Video 1.5 为 480p {P15}、720p {P15_720} / 秒；1.5 Lite 为 480p {PL}、720p {PL_720}、1080p {PL_1080} / 秒；Video 为 480p {P10}、720p {P10_720} / 秒。图生视频每张输入图另收费。以 1.5 Lite 480p 为例，一条 6 秒视频约 {money("zh", MODELS[SL]["usd"], 6)}。实时价格以模型广场为准。'),
                FAQ_DIFF,
                ('视频最长多少秒？支持哪些分辨率和比例？', '<code>duration</code> 可填 1–15 秒，按实际秒数计费。<code>resolution</code>：Video 1.5 和 Video 支持 480p、720p，1.5 Lite 支持 480p、720p、1080p。<code>aspect_ratio</code> 支持 16:9、9:16、1:1；图生视频时画面比例跟随输入图片。'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
                ('生成的视频可以商用吗？', '视频的使用权和内容政策以 xAI 官方条款为准。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用。'),
            ],
            final_h2='现在开始调用 Grok 视频 API', final_p=f'注册即送 200 万 tokens 试用额度，{PL} / 秒起，并发不限。',
        )
    elif slug == S15:
        c.update(
            title=f'Grok Imagine Video 1.5 API 价格与接入｜{P15} / 秒起 - AnyAIGC',
            desc=f'Grok Imagine Video 1.5 API（{S15}）按秒计费 {P15} / 秒起，低于官方价：原生声音与口型同步对白，文生、图生视频，并发不限，支持对公转账与增值税专票。',
            keywords=f'Grok Imagine Video 1.5 API,{S15},grok-imagine-video-1.5,Grok Imagine Video API 价格,Grok 视频生成 API,Grok 图生视频 API,Grok Imagine Video 1.5 API 企业,Grok Imagine Video 1.5 API 发票,AnyAIGC',
            og_desc=f'Grok Imagine Video 1.5 API：{P15} / 秒起，原生声音与对白，文生、图生视频，并发不限。',
            og_alt_txt='AnyAIGC Grok Imagine Video 1.5 API 价格与接入', crumb='Grok Imagine Video 1.5',
            product='Grok Imagine Video 1.5 API（AnyAIGC）', product_desc=f'通过 AnyAIGC 调用 xAI Grok Imagine Video 1.5（{S15}）视频生成模型，按秒计费。',
            sku=S15, offers=OFFERS(S15, 'Grok Imagine Video 1.5'),
            kicker='xAI · 2026 年 6 月发布', h1='Grok Imagine Video 1.5 API',
            lead=f'xAI 新一代视频模型，画面、动作和对白都比上一代更好，声音和口型一起生成。在 AnyAIGC 上 <strong>{P15} / 秒起</strong>，各档都低于 xAI 官方价，并发不限。',
            hero_vid='speech-1', hero_cap='xAI Video 1.5 发布页示例，有声视频',
            facts=[('模型名', f'<code>{S15}</code>'), ('单价', f'{P15} / 秒起'), ('分辨率', '480p / 720p'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='Grok Imagine Video 1.5 是什么',
            about_ps=[
                f'Grok Imagine Video 1.5 是 xAI 在 2026 年 6 月 3 日以预览版推出、6 月 16 日正式发布的视频模型。xAI 文档里 <code>{S15}</code> 是 <code>grok-imagine-video-1.5</code> 的别名，两者是同一个模型。',
                '按 xAI 发布页，1.5 在声音、对白、动作和物理效果上都有提升，人物说话时口型同步。它支持文生视频和图生视频，时长 1–15 秒。',
                f'在 AnyAIGC 上 480p {P15} / 秒、720p {P15_720} / 秒，图生视频每张输入图另收 {IMG15}；xAI 官方价是 480p $0.08、720p $0.14 / 秒。',
            ],
            spec=[('模型名', f'<code>{S15}</code>'), ('创建', '/v1/videos/generations'), ('查询', '/v1/videos/{id}'),
                  ('时长', '1–15 秒'), ('分辨率', '480p / 720p'), ('比例', '16:9 / 9:16 / 1:1')],
            features_h2='Grok Imagine Video 1.5 能做什么', features_lead='以下视频由 Grok Imagine 生成，来自 xAI 官方页面，点击播放（有声音）。', features=FEATURES,
            gallery_h2='Grok Imagine 官方示例视频', gallery_lead='以下视频由 Grok Imagine 生成，来自 xAI 官方 Imagine API 页面和 Video 1.5 发布页。', gallery=GALLERY,
            pricing_h2='Grok Imagine Video 1.5 API 价格', pricing_lead=f'按输出视频秒数计费，480p {P15} / 秒，720p {P15_720} / 秒。',
            billing=[('按秒计费', '按生成的视频时长计，不按 token 算'), ('分档', '480p / 720p'), ('图生视频', f'每张输入图另收 {IMG15}'), ('并发不限', '所有用户默认享有')],
            price_rows=[(S15, 'Grok Imagine Video 1.5')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。xAI 官方价：480p $0.08 / 秒、720p $0.14 / 秒，输入图 $0.01 / 张{SRC}。{TAIL}',
            costs=[('1 条 6 秒短视频', f'6 秒 × {P15}', money('zh', MODELS[S15]['usd'], 6), '480p'),
                   ('100 条 10 秒广告片', f'100 × 10 秒 × {P15_720}', money('zh', tier(S15, '720p'), 1000), '720p'),
                   ('100 条 8 秒图生视频', f'100 × (8 秒 × {P15} + {IMG15})', money('zh', MODELS[S15]['usd'], 800, 100 * float(INPUT_IMG[S15][0])), '480p，每条 1 张首帧')],
            uses_h2='Grok Imagine Video 1.5 使用场景', uses=USES[:5] + [('dining', '餐饮', '菜品与饮品视频', '用一张菜品图生成带环境声的短片，适合外卖平台和门店宣传。')],
            qs_h2='快速接入 Grok Imagine Video 1.5 API', steps=STEPS(S15),
            tabs=[('py', 'Python', f'Python · {S15} 文生视频', code_py(S15)),
                  ('curl', 'cURL', 'cURL · 图生视频', code_curl(S15))],
            qs_note=QS_NOTE.replace(f'、<a href="{DOCS_EDIT}" target="_blank" rel="noopener">编辑视频</a>', ''),
            ent_h2='企业接入 Grok Imagine Video 1.5 API',
            faq_h2='Grok Imagine Video 1.5 API 常见问题',
            faqs=[
                ('Grok Imagine Video 1.5 API 多少钱？', f'AnyAIGC 上 Grok Imagine Video 1.5（<code>{S15}</code>）按输出视频秒数计费：480p {P15} / 秒，720p {P15_720} / 秒，图生视频每张输入图另收 {IMG15}。一条 6 秒 480p 视频约 {money("zh", MODELS[S15]["usd"], 6)}。xAI 官方价是 480p $0.08、720p $0.14 / 秒。实时价格以模型广场为准。'),
                (f'{S15} 和 grok-imagine-video-1.5 是同一个模型吗？', f'是。按 xAI 文档，<code>{S15}</code> 是 <code>grok-imagine-video-1.5</code> 的别名。1.5 在 2026 年 6 月 3 日以预览版推出，6 月 16 日正式发布，AnyAIGC 上用 <code>{S15}</code> 这个模型名调用。'),
                ('Video 1.5 和 1.5 Lite 怎么选？', f'对画面质量、复杂动作和人物对白要求高时选 Video 1.5（{P15} / 秒起）。大批量生成、草稿验证或简单场景选 1.5 Lite（{PL} / 秒起），它还支持 1080p。'),
                ('视频最长多少秒？支持哪些分辨率和比例？', '<code>duration</code> 可填 1–15 秒，按实际秒数计费；<code>resolution</code> 支持 480p、720p；<code>aspect_ratio</code> 支持 16:9、9:16、1:1，图生视频时画面比例跟随输入图片。'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
            ],
            final_h2='现在开始调用 Grok Imagine Video 1.5', final_p=f'注册即送 200 万 tokens 试用额度，{P15} / 秒起，并发不限。',
        )
    elif slug == SL:
        c.update(
            title=f'Grok Imagine Video 1.5 Lite API 价格｜{PL} / 秒起 - AnyAIGC',
            desc=f'Grok Imagine Video 1.5 Lite API（{SL}）是 Grok 视频最低价型号，{PL} / 秒起，支持 1080p 与原生声音，不限并发，可对公转账、开增值税专票。',
            keywords=f'Grok Imagine Video 1.5 Lite API,{SL},Grok Imagine Video API 价格,Grok 视频生成 API,便宜的视频生成 API,Grok 文生视频 API,Grok Imagine Video 1.5 Lite API 企业,Grok Imagine Video 1.5 Lite API 发票,AnyAIGC',
            og_desc=f'Grok Imagine Video 1.5 Lite API：{PL} / 秒起，系列最低价，支持 1080p 与原生声音，并发不限。',
            og_alt_txt='AnyAIGC Grok Imagine Video 1.5 Lite API 价格与接入', crumb='Grok Imagine Video 1.5 Lite',
            product='Grok Imagine Video 1.5 Lite API（AnyAIGC）', product_desc=f'通过 AnyAIGC 调用 xAI Grok Imagine Video 1.5 Lite（{SL}）视频生成模型，按秒计费。',
            sku=SL, offers=OFFERS(SL, 'Grok Imagine Video 1.5 Lite'),
            kicker='xAI · Video 1.5 轻量低价版', h1='Grok Imagine Video 1.5 Lite API',
            lead=f'Video 1.5 的轻量版，画面和声音一起生成，适合大批量出片和快速验证想法。在 AnyAIGC 上 <strong>{PL} / 秒起</strong>，是 Grok 视频系列里最便宜的，并发不限。',
            hero_vid='property', hero_cap='xAI 官方示例，有声视频',
            facts=[('模型名', f'<code>{SL}</code>'), ('单价', f'{PL} / 秒起'), ('分辨率', '480p–1080p'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='Grok Imagine Video 1.5 Lite 是什么',
            about_ps=[
                f'Grok Imagine Video 1.5 Lite（<code>{SL}</code>）是 xAI Video 1.5 的轻量低价版本。xAI 文档把它定位为「价格最低的文生视频和图生视频模型」，推荐用于简单视频。',
                '它同样原生生成声音，一次输出画面、音效和环境声。时长 1–15 秒按秒可调，分辨率可选 480p、720p、1080p（1080p 由 720p 放大得到），支持横屏、竖屏和方形。',
                '它不支持参考图、关键帧，复杂人物、多角色、长连贯动作和角色一致性弱于完整版 Video 1.5。对质量要求高的成片，建议用 <a href="/zh/models/grok-imagine-video-1.5-preview">Grok Imagine Video 1.5</a>。',
            ],
            spec=[('模型名', f'<code>{SL}</code>'), ('创建', '/v1/videos/generations'), ('查询', '/v1/videos/{id}'),
                  ('时长', '1–15 秒'), ('分辨率', '480p / 720p / 1080p'), ('模式', '文生 / 图生视频')],
            features_h2='Grok Imagine Video 1.5 Lite 适合做什么',
            features=[
                (None, '系列最低价', f'480p {PL} / 秒、720p {PL_720} / 秒，一条 6 秒 480p 视频约 {money("zh", MODELS[SL]["usd"], 6)}。'),
                (None, '原生声音', '画面、音效和环境声一起生成，不用后期配音。'),
                (None, '最高 1080p', '可选 480p、720p、1080p，1080p 由 720p 放大得到，适合需要高分辨率交付的场景。'),
                (None, '文生与图生视频', '一句描述直接出片，或上传首帧图片让画面动起来。'),
                (None, '1–15 秒按秒可调', '只为实际生成的秒数付费，短镜头更省。'),
                (None, '一键升级 1.5', f'需要复杂动作、多角色或更好的对白时，把 <code>model</code> 改成 <code>{S15}</code>。'),
            ],
            pricing_h2='Grok Imagine Video 1.5 Lite API 价格', pricing_lead=f'按输出视频秒数计费，480p {PL}、720p {PL_720}、1080p {PL_1080} / 秒。',
            billing=[('按秒计费', '按生成的视频时长计，不按 token 算'), ('分档', '480p / 720p / 1080p'), ('图生视频', f'每张输入图另收 {IMG15}'), ('并发不限', '所有用户默认享有')],
            price_rows=[(SL, 'Grok Imagine Video 1.5 Lite'), (S15, '对比：Grok Imagine Video 1.5')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。xAI 官方价：1.5 Lite 480p $0.02、720p $0.03、1080p $0.14 / 秒，输入图 $0.01 / 张{SRC}。{TAIL}',
            costs=[('1,000 条 6 秒草稿', f'1,000 × 6 秒 × {PL}', money('zh', MODELS[SL]['usd'], 6000), '480p'),
                   ('100 条 10 秒短视频', f'100 × 10 秒 × {PL_720}', money('zh', tier(SL, '720p'), 1000), '720p'),
                   ('10 条 10 秒 1080p 成片', f'10 × 10 秒 × {PL_1080}', money('zh', tier(SL, '1080p'), 100), '1080p')],
            uses_h2='Grok Imagine Video 1.5 Lite 使用场景',
            uses=[(None, '批量', '大批量短视频素材', '按秒最低价，适合一次生成成百上千条素材再挑选。'),
                  (None, '草稿', '分镜与创意验证', '先用 Lite 跑通分镜和创意，定稿后再换 Video 1.5 出成片。'),
                  (None, '电商', '商品动图与短视频', '用商品图生成简单的展示动效，适合详情页和信息流。'),
                  (None, '社媒', '配图视频', '给文章、帖子配上几秒的动态画面和环境声。'),
                  (None, '应用', '应用内生视频', '在 App 里接入文生视频功能，按秒结算成本清晰。'),
                  (None, '高清', '1080p 交付', '需要 1080p 输出时，Lite 是系列里唯一支持 1080p 的型号。')],
            qs_h2='快速接入 Grok Imagine Video 1.5 Lite API', steps=STEPS(SL),
            tabs=[('py', 'Python', f'Python · {SL} 文生视频', code_py(SL, '480p')),
                  ('curl', 'cURL', 'cURL · 图生视频', code_curl(SL))],
            qs_note=QS_NOTE.replace(f'、<a href="{DOCS_EDIT}" target="_blank" rel="noopener">编辑视频</a>', ''),
            ent_h2='企业接入 Grok Imagine Video 1.5 Lite API',
            faq_h2='Grok Imagine Video 1.5 Lite API 常见问题',
            faqs=[
                ('Grok Imagine Video 1.5 Lite API 多少钱？', f'AnyAIGC 上 Grok Imagine Video 1.5 Lite（<code>{SL}</code>）按输出视频秒数计费：480p {PL}、720p {PL_720}、1080p {PL_1080} / 秒，图生视频每张输入图另收 {IMG15}。一条 6 秒 480p 视频约 {money("zh", MODELS[SL]["usd"], 6)}。xAI 官方价是 480p $0.02、720p $0.03、1080p $0.14 / 秒。实时价格以模型广场为准。'),
                ('1.5 Lite 和 Video 1.5 有什么区别？', f'Lite 是轻量低价版，价格更低，还支持 1080p，但不支持参考图和关键帧，复杂人物、多角色、长连贯动作和角色一致性弱于完整版。批量素材和草稿选 Lite，广告和成片选 Video 1.5（{P15} / 秒起）。'),
                ('1080p 是原生的吗？', '按 xAI 文档，1.5 Lite 的 1080p 由 720p 放大得到，不是原生 1080p。1080p 每秒单价也明显高于 720p，按需选择。'),
                ('视频最长多少秒？支持哪些比例？', '<code>duration</code> 可填 1–15 秒，按实际秒数计费；<code>aspect_ratio</code> 支持 16:9、9:16、1:1，图生视频时画面比例跟随输入图片。'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
            ],
            final_h2='现在开始调用 Grok Imagine Video 1.5 Lite', final_p=f'注册即送 200 万 tokens 试用额度，{PL} / 秒起，并发不限。',
        )
    elif slug == S10:
        c.update(
            title=f'Grok Imagine Video API 价格与接入｜{P10} / 秒起 - AnyAIGC',
            desc=f'Grok Imagine Video API（{S10}）按秒计费 {P10} / 秒起，低于 xAI 官方价：文生、图生视频，支持上传原视频修改，原生声音，并发不限，支持对公转账与增值税专票。',
            keywords=f'Grok Imagine Video API,{S10},Grok Imagine Video API 价格,Grok 视频生成 API,Grok 视频编辑 API,Grok 图生视频 API,Grok Imagine Video API 企业,Grok Imagine Video API 发票,AnyAIGC',
            og_desc=f'Grok Imagine Video API：{P10} / 秒起，文生、图生视频，支持改视频，原生声音，并发不限。',
            og_alt_txt='AnyAIGC Grok Imagine Video API 价格与接入', crumb='Grok Imagine Video',
            product='Grok Imagine Video API（AnyAIGC）', product_desc=f'通过 AnyAIGC 调用 xAI Grok Imagine Video（{S10}）视频生成与编辑模型，按秒计费。',
            sku=S10, offers=OFFERS(S10, 'Grok Imagine Video'),
            kicker='xAI · 2026 年 1 月发布 · 支持改视频', h1='Grok Imagine Video API',
            lead=f'xAI 第一代视频模型，画面和声音一起生成，也能上传原视频改服装、改风格。在 AnyAIGC 上 <strong>{P10} / 秒起</strong>，各档都低于 xAI 官方价，并发不限。',
            hero_vid='restyle-a', hero_cap='xAI 官方改视频示例',
            facts=[('模型名', f'<code>{S10}</code>'), ('单价', f'{P10} / 秒起'), ('分辨率', '480p / 720p'), ('并发', '不限'), ('企业', '对公 · 专票')],
            about_h2='Grok Imagine Video 是什么',
            about_ps=[
                f'Grok Imagine Video（<code>{S10}</code>）是 xAI 在 2026 年 1 月 28 日随 Grok Imagine API 推出的视频模型，支持文生视频、图生视频和视频编辑，生成的视频自带声音。',
                '按 xAI 发布页，它在 Artificial Analysis 文生视频榜排第 1（2026-01-28 数据）。之后 xAI 推出了 Video 1.5 和 1.5 Lite，第一代模型没有停用，xAI 文档目前把它定位为改视频和续写视频的模型。',
                f'在 AnyAIGC 上 480p {P10} / 秒、720p {P10_720} / 秒；图生视频每张输入图另收 {IMG10}，改视频按原视频每秒另收 {VID10}。xAI 官方价是 480p $0.05、720p $0.07 / 秒。',
            ],
            spec=[('模型名', f'<code>{S10}</code>'), ('创建', '/v1/videos/generations'), ('改视频', '/v1/videos/edits'),
                  ('时长', '1–15 秒'), ('分辨率', '480p / 720p'), ('比例', '16:9 / 9:16 / 1:1')],
            features_h2='Grok Imagine Video 能做什么', features_lead='以下视频由 Grok Imagine 生成，来自 xAI 官方页面，点击播放（有声音）。',
            features=[('edit-a', '上传原视频修改', '用一句话换服装、换颜色，人物动作和镜头保持不变。'),
                      ('restyle-b', '整体换风格', '把实拍视频换成动画、方块等风格，保留原有运动轨迹。'),
                      ('property', '文生视频与图生视频', '用一句描述生成视频，或者上传首帧图片让画面动起来。'),
                      FEATURES[0], FEATURES[2], FEATURES[5]],
            edits_h2='改视频：换颜色、换风格', edits_lead='上传原视频，用一句话修改服装、颜色或整体风格，人物动作保持不变（xAI 官方示例）。',
            edit_rows=[('换服装', [('edit-input', '原视频'), ('edit-a', '结果 1'), ('edit-b', '结果 2')]),
                       ('换风格', [('restyle-original', '原视频'), ('restyle-a', '结果 1'), ('restyle-b', '结果 2')])],
            edits_note=f'改视频走 <code>POST /v1/videos/edits</code>，按 xAI 文档原视频最长 8.7 秒，输出最高 720p、时长与原视频一致。计费为输出视频每秒价格加原视频每秒 {VID10}。',
            pricing_h2='Grok Imagine Video API 价格', pricing_lead=f'按输出视频秒数计费，480p {P10} / 秒，720p {P10_720} / 秒。',
            billing=[('按秒计费', '按生成的视频时长计，不按 token 算'), ('分档', '480p / 720p'), ('图生视频', f'每张输入图另收 {IMG10}'), ('改视频', f'原视频每秒另收 {VID10}')],
            price_rows=[(S10, 'Grok Imagine Video'), (S15, '对比：Grok Imagine Video 1.5')],
            price_note=f'价格来自 AnyAIGC 模型广场，{RATE_NOTE}。xAI 官方价：480p $0.05 / 秒、720p $0.07 / 秒，输入图 $0.002 / 张，输入视频 $0.01 / 秒{SRC}。{TAIL}',
            costs=[('1 条 6 秒短视频', f'6 秒 × {P10}', money('zh', MODELS[S10]['usd'], 6), '480p'),
                   ('100 条 10 秒短视频', f'100 × 10 秒 × {P10_720}', money('zh', tier(S10, '720p'), 1000), '720p'),
                   ('改 1 条 6 秒视频', f'6 秒 × ({P10} + {VID10})', money('zh', MODELS[S10]['usd'], 6, 6 * float(INPUT_VID[S10][0])), '480p 输出')],
            uses_h2='Grok Imagine Video 使用场景', uses=[USES[5]] + USES[:5],
            qs_h2='快速接入 Grok Imagine Video API', steps=STEPS(S10),
            tabs=[('py', 'Python', f'Python · {S10} 文生视频', code_py(S10)),
                  ('curl', 'cURL', 'cURL · 图生视频', code_curl(S10)),
                  ('edit', '改视频', 'cURL · 上传原视频修改', code_edit())],
            qs_note=QS_NOTE, ent_h2='企业接入 Grok Imagine Video API',
            faq_h2='Grok Imagine Video API 常见问题',
            faqs=[
                ('Grok Imagine Video API 多少钱？', f'AnyAIGC 上 Grok Imagine Video（<code>{S10}</code>）按输出视频秒数计费：480p {P10} / 秒，720p {P10_720} / 秒；图生视频每张输入图另收 {IMG10}，改视频按原视频每秒另收 {VID10}。一条 6 秒 480p 视频约 {money("zh", MODELS[S10]["usd"], 6)}。xAI 官方价是 480p $0.05、720p $0.07 / 秒。实时价格以模型广场为准。'),
                FAQ_DIFF,
                ('怎么改视频？', f'向 <code>POST /v1/videos/edits</code> 提交 <code>model</code>、<code>prompt</code> 和原视频 <code>video</code>（链接），写清要改的部分。按 xAI 文档原视频最长 8.7 秒，输出最高 720p。目前系列里只有 <code>{S10}</code> 支持改视频。'),
                ('grok-imagine-video 会停用吗？', '目前没有。xAI 2026 年 11 月 2 日停用的是图像模型 <code>grok-imagine-image-quality</code>，视频模型不受影响。xAI 文档把第一代视频模型定位为改视频和续写视频的模型。'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
            ],
            final_h2='现在开始调用 Grok Imagine Video', final_p=f'注册即送 200 万 tokens 试用额度，{P10} / 秒起，并发不限。',
        )
    return c
