# 生成 Muse Video 专题页（中英文各 1 页）：python scripts/muse_video_pages.py
# 每次整页重写，之后需重跑 scripts/payments.py 和 scripts/trust.py 补上支付方式与信任版块（两个脚本重复运行结果不变）。
# 版式与 Muse Image 页共用（scripts/muse_image_pages.py 的版块函数 + assets/models/muse-image.css），视频组件样式在 assets/models/muse-video.css。
# 价格：AnyAIGC 模型广场（https://anyaigc.ai/pricing?keyword=muse-video，2026-11-04 读取）显示 $0.0397 / 秒，按视频时长计费；
#   中文页按 /api/status 的 usd_exchange_rate = 6.689338 换算。Meta 尚未公布 Muse Video 的 API 官方价，页面不写官方价对比。
# 接口：AnyAIGC 文档「Create Video muse-video」POST /v1/videos 与「Query Video muse-video」GET /v1/videos/{id}（2026-11-04 读取）。
# 示例视频：Meta 官方博客 ai.meta.com/blog/introducing-muse-image-muse-video-msl（由 Muse Video 生成，1280×720 带音频），
#   转码为 960 宽 H.264 存放在 assets/models/muse-video/，封面帧为同名 .webp。
import html
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import muse_image_pages as B  # noqa: E402  共用 head / nav / section / enterprise / faq / final / footer
from seedream_layout import hl  # noqa: E402

ROOT = B.ROOT
NL = '\n'
SLUG = 'muse-video'
NAME = 'Muse Video'
DATE = '2026-11-04'
VER = '20261104'
MODEL = 'muse-video'
RATE = 6.689338
USD = '0.0397'           # 每秒
CNY = f'{float(USD) * RATE:.2f}'  # 0.27
SITE, REG, PRICING, SUPPORT = B.SITE, B.REG, B.PRICING, B.SUPPORT
META_BLOG = B.META_BLOG
DOCS_CREATE = 'https://docs.anyaigc.ai/reference/v1/videos?leaf=c%3A1793756879519'
DOCS_QUERY = 'https://docs.anyaigc.ai/reference/v1/videos/%7Bid%7D?leaf=c%3A1793756955011'

# 请求秒数 → 实际时长（文档：只会向上取整，不会比请求短）
ROUND = [('4、5', '5'), ('6', '6'), ('7、8', '8'), ('9、10', '10'), ('11–15', '15'), ('16–20', '20'), ('21–25', '25'), ('26–30', '30')]
# 示例视频（文件名, 中文标签, 中文说明, 英文标签, 英文说明）；提示词来自 Meta 官方博客
VIDS = [
    ('panda', '动作', '一只大熊猫幼崽从小草坡上翻着跟头滚下来', 'Motion', 'A baby panda tumbling head over heels down a small grassy slope'),
    ('juggler', '叙事', '男人抛三个橙子，又加一个，全掉了，还是鞠了个躬。完整的起承转合，单镜头约 10 秒', 'Story', 'A man juggles three oranges, adds a fourth, drops them all, and takes a bow anyway, in one continuous 10-second take'),
    ('blush-fizz', '广告', '气泡柠檬水广告：俯拍旋转、慢动作倒酒，气泡声和旁白同步', 'Ad', 'A sparkling lemonade commercial with a slow-motion pour, fizz foley and a synced voiceover'),
    ('kettle-ad', 'UGC 广告', '手持竖拍风格的厨房种草视频，人物对着镜头说台词', 'UGC ad', 'A handheld UGC-style kitchen ad with the creator speaking to camera'),
    ('ducklings', '数量一致', '鸭妈妈带着恰好 5 只小鸭上台阶，全程 5 只不多不少', 'Consistency', 'A mother duck leads exactly five ducklings up a step, and the count stays at five throughout'),
    ('snow-pond', '第一人称', '夜里沿着半结冰的池塘散步，雪花飘落，脚步声和水声', 'First person', 'A night walk along a half-frozen pond in falling snow, with footsteps and trickling water'),
    ('otter', '自然', '一只小水獭仰面漂浮，肚子上抱着一颗鹅卵石', 'Nature', 'A baby otter floating on its back, holding a smooth pebble on its belly'),
    ('podcast', '对白', '播客主播对着麦克风说话，口型与声音同步', 'Dialogue', 'A podcast host talking into a microphone with lip-synced speech'),
    ('airfoil', '科普', '纸艺风格的机翼升力原理动画，画面里的文字清晰可读', 'Explainer', 'A paper-craft explainer of how an airfoil creates lift, with legible on-screen text'),
]
HERO = 'blush-fizz'


def vid(name, label, eager=False):
    poster = f'/assets/models/muse-video/{name}.webp?v={VER}'
    pre = 'metadata' if eager else 'none'
    return (f'<video src="/assets/models/muse-video/{name}.mp4?v={VER}" poster="{poster}" width="1280" height="720" '
            f'controls playsinline preload="{pre}" aria-label="{html.escape(label, quote=True)}"></video>')


# ---------------- 代码示例 ----------------
PROMPT = {'zh': '清晨的海边小镇，一只橘猫沿着石阶慢慢走下来，海浪声和远处的海鸥叫声，电影感',
          'en': 'A small seaside town at dawn, an orange cat strolls down stone steps, sound of waves and distant gulls, cinematic'}
CMT = {
    'zh': dict(sec='4–30 秒，按这个秒数计费；字段名是 seconds，不是 duration', size='1280x720 横屏 或 720x1280 竖屏',
               poll='建议每 10–20 秒查询一次', fail='失败自动退款', first='图生视频：input_reference 传首帧图片 URL'),
    'en': dict(sec='4-30 seconds, billed on this value; the field is seconds, not duration', size='1280x720 landscape or 720x1280 portrait',
               poll='poll every 10-20 seconds', fail='failed tasks are refunded automatically', first='image-to-video: pass the first frame URL as input_reference'),
}


def code_py(lang):
    c = CMT[lang]
    return f'''import os
import time
import requests

API = "https://anyaigc.ai/v1/videos"
HEADERS = {{"Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"]}}

task = requests.post(API, headers=HEADERS, json={{
    "model": "{MODEL}",
    "prompt": "{PROMPT[lang]}",
    "seconds": "5",  # {c['sec']}
    "size": "1280x720",  # {c['size']}
}}, timeout=60).json()
print(task["id"], task["status"])  # queued

while True:
    time.sleep(15)  # {c['poll']}
    job = requests.get(f"{{API}}/{{task['id']}}", headers=HEADERS, timeout=30).json()
    print(job["status"], job.get("progress"))
    if job["status"] in ("completed", "failed"):  # {c['fail']}
        break
print(job)'''


def code_curl(lang):
    return f'''# 1. 创建任务
curl https://anyaigc.ai/v1/videos \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{MODEL}",
    "prompt": "{PROMPT[lang]}",
    "seconds": "5",
    "size": "1280x720"
  }}'

# 2. 用返回的 id 查询状态
curl https://anyaigc.ai/v1/videos/task_xxxxxxxx \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY"''' if lang == 'zh' else f'''# 1. Create the task
curl https://anyaigc.ai/v1/videos \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{MODEL}",
    "prompt": "{PROMPT[lang]}",
    "seconds": "5",
    "size": "1280x720"
  }}'

# 2. Poll with the returned id
curl https://anyaigc.ai/v1/videos/task_xxxxxxxx \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY"'''


def code_i2v(lang):
    c = CMT[lang]
    p = '让画面里的人物转头看向镜头并微笑，镜头缓慢推近' if lang == 'zh' else 'The person turns to the camera and smiles as the camera slowly pushes in'
    return f'''import os
import requests

resp = requests.post(
    "https://anyaigc.ai/v1/videos",
    headers={{"Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"]}},
    json={{
        "model": "{MODEL}",
        "prompt": "{p}",
        "input_reference": "https://example.com/first-frame.jpg",  # {c['first']}
        "seconds": "8",
        "size": "720x1280",
    }},
    timeout=60,
)
print(resp.json())  # {{"id": "task_...", "status": "queued", ...}}'''


# ---------------- 文案 ----------------
def cost(sec, lang):
    v = sec * float(USD) * (RATE if lang == 'zh' else 1)
    return f'¥{v:.2f}' if lang == 'zh' else f'${v:.3f}'.rstrip('0').rstrip('.') if v < 1 else f'${v:.2f}'


def copy_zh():
    p = f'¥{CNY}'
    return dict(
        lang='zh-CN', og='zh_CN', og_alt='en_US', other='en', other_name='English', other_lang='en',
        title=f'Muse Video API 价格与接入｜Meta 生视频 {p} / 秒 - AnyAIGC',
        desc=f'Muse Video API（muse-video）是 Meta 超级智能实验室的视频生成模型，按秒计费 {p} / 秒，文生视频与首帧图生视频，720P 带原生音频，4–30 秒，并发不限，支持对公转账与增值税专票。',
        keywords='Muse Video API,Muse Video API 价格,muse-video,Meta Muse Video,Meta 视频生成 API,Muse Video 接入,Muse Video 图生视频,Muse Video API Key,Muse Video API 企业,Muse Video API 发票,AnyAIGC',
        og_desc=f'Meta Muse Video API：{p} / 秒，720P 带原生音频，文生视频与首帧图生视频，4–30 秒，并发不限。',
        og_alt_txt='AnyAIGC Muse Video API 价格与接入',
        home='首页', hub='模型专题', market='模型广场', price='价格', ent='企业接入', docs='API 文档', login='登录', signup='免费注册',
        get_key='获取 API Key', see_price='查看价格', skip='跳到主要内容', nav_label='主导航', crumbs='面包屑', facts_label='核心信息',
        home_label='AnyAIGC 首页', copy='复制', copied='已复制', code_label='代码示例',
        product='Muse Video API（AnyAIGC）',
        product_desc='通过 AnyAIGC 调用 Meta Muse Video（muse-video）视频生成模型，按秒计费，POST /v1/videos 异步任务，720P 带音频。',
        category='视频生成 API', currency='CNY', offers=[('Muse Video（每秒）', CNY)],
        badge='Preview', kicker='Meta 超级智能实验室 · 早期预览版',
        h1='Muse Video API',
        lead=f'Meta 超级智能实验室的视频生成模型，和 Muse Image 同一个预训练底座。一次生成带原生音频的 720P 视频，最长 30 秒。在 AnyAIGC 上按秒计费 <strong>{p} / 秒</strong>，并发不限。',
        facts=[('模型名', f'<code>{MODEL}</code>'), ('单价', f'{p} / 秒'), ('时长', '4–30 秒'), ('画质', '720P · 带音频'), ('并发', '不限'), ('企业', '对公 · 专票')],
        hero_cap='官方示例：气泡柠檬水广告，慢动作倒酒、气泡声与旁白同步（由 Muse Video 生成）',
        about_h2='Muse Video 是什么',
        about_ps=[
            'Muse Video 是 Meta 超级智能实验室（Meta Superintelligence Labs）随 Muse Image 一起发布的视频生成模型，两者基于同一个预训练底座。Meta 称它在提示词贴合度、画面保真度和时间一致性上有竞争力，并且原生支持音频：环境声、动作音效、旁白和对白会和画面一起生成。',
            '按 Meta 官方博客，Muse Video 在 Arena 文生视频人类偏好排名中位列第 3（2026-07-05 数据）。目前是早期预览版，Meta 也写明还在改进音画同步和快速运动的物理准确性这两块短板。',
            f'在 AnyAIGC 上，模型名是 <code>{MODEL}</code>，走 <code>POST /v1/videos</code> 异步任务接口，支持文生视频和首帧图生视频，输出 1280×720 横屏或 720×1280 竖屏的 MP4，每秒 {p}。',
        ],
        spec=[('模型名', f'<code>{MODEL}</code>'), ('接口', 'POST /v1/videos'), ('时长', '4–30 秒（seconds）'),
              ('尺寸', '1280×720 / 720×1280'), ('输出', '720P MP4 · 带音频'), ('输入', '文本 · 首帧图片')],
        features_h2='Muse Video 能做什么',
        features=[
            ('juggler', '原生音频', '音效、环境声、旁白和对白和画面一起生成，不用另外配音。官方示例里橙子落地、杯子碰撞都有对应的声音。'),
            ('ducklings', '提示词贴合', '数量、顺序和动作按提示词来。示例要求「恰好 5 只小鸭」，从头到尾都是 5 只。'),
            ('panda', '时间一致性', '主体在整段视频里保持同一个样子，翻滚、转身之后外形不走样。'),
            ('kettle-ad', 'UGC 风格广告', '手持晃动、对焦变化、人物对着镜头说台词，生成像真人拍的种草视频，不需要演员和拍摄。'),
            ('podcast', '人物说话', '提示词里写台词，人物会开口说出来，口型和声音同步，适合口播和对白片段。'),
            ('snow-pond', '运镜与氛围', '第一人称步行、手持跟拍等运镜按提示词执行，光线、天气和环境声一起营造氛围。'),
        ],
        gallery_h2='Muse Video 官方示例', gallery_lead='以下视频由 Muse Video 生成，来自 Meta 官方博客，带声音，点击播放。说明为官方提示词的节选翻译。',
        credit='示例视频来自 Meta 官方博客，由 Muse Video 生成，版权归 Meta 所有。', credit_link='查看来源',
        pricing_h2='Muse Video API 价格', pricing_lead=f'按视频秒数计费，每秒 {p}，提交时按请求秒数预扣，失败自动退款。',
        billing=[('按秒计费', '按请求的 seconds 计费'), ('失败退款', '任务失败自动退回'), ('并发不限', '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')],
        table_caption='Muse Video API 价格（人民币）', th=('功能', '模型名', '计费方式', 'AnyAIGC 单价'),
        rows=[('文生视频', '只传提示词'), ('首帧图生视频', '传 input_reference')], unit='秒', billing_word='按秒',
        price_note=f'单价为模型广场显示的价格（${USD} / 秒），按 1 美元 ≈ ¥{RATE:.3f} 换算成人民币。Meta 暂未公布 Muse Video 的 API 官方价。按提交时请求的 seconds 预扣，参数不合法返回 400 不扣费，实时价格以<a href="{PRICING}">模型广场</a>为准。',
        round_h3='时长怎么取整', round_note='实际视频只会向上取整，不会比请求的短；计费按请求的秒数。超过 10 秒的视频分段生成再拼接，在第 10、20 秒处换镜头。',
        round_th=('请求 seconds', '实际时长（秒）'),
        costs_h3='成本示例', costs_note='按每秒单价直接相乘。',
        costs=[('一条 5 秒短视频', '5 × 每秒单价', 5, '1–2 分钟出片'), ('一条 10 秒广告', '10 × 每秒单价', 10, '单镜头完整叙事'),
               ('一条 30 秒长视频', '30 × 每秒单价', 30, '3–7 分钟出片')],
        market_btn='在模型广场查看',
        uses_h2='Muse Video API 使用场景',
        uses=[('电商', '商品短视频', '用商品图做首帧，生成开箱、使用和场景展示视频，横竖屏都能出。'),
              ('营销', '广告与种草视频', '在提示词里写好镜头、台词和音效，直接生成带旁白的 10 秒广告。'),
              ('社媒', '竖屏短视频', '720×1280 竖屏，适合抖音、视频号、Reels 和 Shorts。'),
              ('内容', '科普与解说', '把原理拆成镜头描述，生成带文字和配音的讲解片段。'),
              ('影视', '分镜与预演', '快速把剧本片段变成带声音的动态分镜，用来对齐镜头和节奏。'),
              ('游戏', '宣传与过场', '生成角色动作和场景过场片段，做预告片素材。')],
        why_h2='为什么通过 AnyAIGC 调用',
        why=[('一个 Key，300+ 模型', 'Muse Video、Muse Image、Seedance、Kling 等视频和图像模型共用一个 API Key 和余额。'),
             ('国内直连', '接口地址 <code>https://anyaigc.ai</code>，国内网络可直接调用，不需要 Meta 账号。'),
             ('按秒计费，失败退款', f'每秒 {p}，按请求秒数预扣，生成失败自动退回。'),
             ('并发不限', '所有用户默认不限并发，批量出片不用排队申请。')],
        qs_h2='快速接入 Muse Video API',
        steps=[f'<a href="{REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
               '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
               f'向 <code>POST https://anyaigc.ai/v1/videos</code> 提交任务，<code>model</code> 填 <code>{MODEL}</code>，拿到 <code>id</code> 后用 <code>GET /v1/videos/{{id}}</code> 轮询，<code>status</code> 变成 <code>completed</code> 就完成了。'],
        tabs=[('py', 'Python', 'Python · 提交任务并轮询', code_py('zh')), ('curl', 'cURL', 'cURL · 创建与查询', code_curl('zh')),
              ('i2v', '图生视频', 'Python · 首帧图生视频（竖屏 8 秒）', code_i2v('zh'))],
        qs_note=f'状态依次是 <code>queued</code> → <code>in_progress</code> → <code>completed</code> / <code>failed</code>。10 秒以内约 1–2 分钟，15–30 秒约 3–7 分钟。失败时返回 <code>error</code>，<code>video_generation_failed</code> 是没产出视频（内容不合规或上游临时错误），改写提示词或稍后重试；<code>video_rejected</code> 是成片不合格被丢弃，直接重试。参数和返回字段以 <a href="{DOCS_CREATE}" target="_blank" rel="noopener">AnyAIGC 接口文档</a>为准。',
        ent_h2='企业接入 Muse Video API',
        ent_lead='电商公司、广告和内容团队可以直接走企业流程采购，财务、法务和技术对接都有对应支持。',
        ent_cards=[('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。'),
                   ('对公转账', '公司账户直接付款', '支持企业对公转账充值，无需个人垫付，账目清晰。'),
                   ('签订合同', '满足采购与法务流程', '可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。'),
                   ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。')],
        sales='联系企业客服', trial='先注册试用',
        faq_h2='Muse Video API 常见问题',
        faqs=[
            ('Muse Video API 多少钱？', f'AnyAIGC 上 Muse Video（<code>{MODEL}</code>）每秒 {p}，按请求的 <code>seconds</code> 计费：5 秒 {cost(5, "zh")}，10 秒 {cost(10, "zh")}，30 秒 {cost(30, "zh")}。提交时预扣，任务失败自动退款，实时价格以模型广场为准。'),
            ('Muse Video 是什么？', 'Muse Video 是 Meta 超级智能实验室和 Muse Image 一起发布的视频生成模型，两者用同一个预训练底座，原生支持音频。目前是早期预览版，按 Meta 官方博客在 Arena 文生视频排名第 3（2026-07-05）。'),
            ('支持多长的视频？', '<code>seconds</code> 填 4–30 的整数，默认 4。实际时长只会向上取整：4、5 秒出 5 秒，7、8 秒出 8 秒，11–15 秒出 15 秒，以此类推；超过 10 秒会分段生成再拼接，在第 10、20 秒处换镜头。计费按请求的秒数。'),
            ('支持哪些尺寸和画质？', '<code>size</code> 支持 <code>1280x720</code> 横屏和 <code>720x1280</code> 竖屏，不填默认横屏；<code>resolution</code> 只能是 <code>720p</code>，可以不传。输出 MP4，带音频。'),
            ('能用图片生成视频吗？', '能。<code>input_reference</code> 传一张图片作为第一帧，支持图片 URL 或 data URL（PNG / JPEG / WebP），也可以用 multipart/form-data 直接上传文件，不支持 file ID。'),
            ('生成要多久？怎么拿结果？', '这是异步接口：<code>POST /v1/videos</code> 返回任务 <code>id</code>，再用 <code>GET /v1/videos/{id}</code> 查询，建议每 10–20 秒查一次。10 秒以内约 1–2 分钟，15–30 秒约 3–7 分钟。'),
            ('生成失败会扣费吗？', '不会。任务失败自动退款；参数不合法返回 400（<code>client_local_validation</code>），任务不会创建，也不扣费。'),
            ('并发有限制吗？国内能直接调用吗？', 'AnyAIGC 对 Muse Video 不设并发限制，所有用户默认享有。接口地址是 <code>https://anyaigc.ai</code>，国内网络可以直接调用，不需要 Meta 账号；同一个 Key 还能调用平台上 300+ 其他模型。'),
            ('AnyAIGC 能开发票吗？支持增值税专票吗？', '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
            ('企业可以对公转账和签合同吗？', f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
            ('生成的视频可以商用吗？', '视频的使用权和内容政策以 Meta 官方条款为准。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用。'),
        ],
        final_h2='现在开始调用 Muse Video', final_p=f'注册即送 200 万 tokens 试用额度，每秒 {p}，并发不限。',
        signup_any='免费注册 AnyAIGC', read_docs='阅读 API 文档', more='更多', all_hub='全部模型专题', in_other='Muse Video API in English',
        sibling=('Muse Image API', '/zh/models/muse-image'),
        foot_desc='国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。',
        foot=('产品', '资源', '条款'), foot_links=('模型专题', '模型广场', '控制台', 'API 文档 ↗', 'Meta 官方博客 ↗', '联系我们', '隐私政策', '服务条款'),
        legal='&copy; 2026 AnyAIGC。Muse、Meta 是 Meta Platforms, Inc. 的商标。AnyAIGC 是独立的 API 服务商，与 Meta 无隶属或合作关系。页面示例视频来自 Meta 官方博客，版权归 Meta 所有。',
    )


def copy_en():
    p = f'${USD}'
    return dict(
        lang='en', og='en_US', og_alt='zh_CN', other='zh', other_name='中文', other_lang='zh-CN',
        title=f'Muse Video API Pricing & Access | {p}/second - AnyAIGC',
        desc=f'Meta Muse Video API (muse-video) at {p} per second: text and first-frame image to 720p video with native audio, 4-30s, bank transfer and invoices.',
        keywords='Muse Video API,Muse Video API pricing,muse-video,Meta Muse Video,Meta video generation API,Muse Video image to video,Muse Video API key,Muse Video API for business,AnyAIGC',
        og_desc=f'Meta Muse Video API at {p} per second: 720p video with native audio, text-to-video and first-frame image-to-video, 4-30 seconds, unlimited concurrency.',
        og_alt_txt='AnyAIGC Muse Video API pricing and access',
        home='Home', hub='Model guides', market='Model catalog', price='Pricing', ent='Enterprise', docs='API docs', login='Log in', signup='Sign up free',
        get_key='Get an API key', see_price='See pricing', skip='Skip to main content', nav_label='Main', crumbs='Breadcrumb', facts_label='Key facts',
        home_label='AnyAIGC home', copy='Copy', copied='Copied', code_label='Code examples',
        product='Muse Video API (AnyAIGC)',
        product_desc='Call Meta Muse Video (muse-video) through AnyAIGC, billed per second, as an async POST /v1/videos task with 720p output and audio.',
        category='Video generation API', currency='USD', offers=[('Muse Video (per second)', USD)],
        badge='Preview', kicker='Meta Superintelligence Labs · early preview',
        h1='Muse Video API',
        lead=f'The video model from Meta Superintelligence Labs, built on the same pretraining base as Muse Image. It renders 720p video with native audio in one pass, up to 30 seconds. On AnyAIGC it costs <strong>{p} per second</strong> with unlimited concurrency.',
        facts=[('Model', f'<code>{MODEL}</code>'), ('Price', f'{p} / second'), ('Length', '4–30 s'), ('Output', '720p · audio'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
        hero_cap='Official sample: a sparkling lemonade ad with a slow-motion pour, fizz foley and a synced voiceover (generated by Muse Video)',
        about_h2='What is Muse Video?',
        about_ps=[
            'Muse Video is the video model Meta Superintelligence Labs previewed alongside Muse Image, built on the same pretraining base. Meta says it is competitive on prompt adherence, visual fidelity and temporal consistency, and it generates audio natively: ambience, foley, voiceover and dialogue come out with the picture.',
            'According to Meta, Muse Video ranked No. 3 on Arena for text-to-video as of July 5, 2026. It is an early preview, and Meta notes it is still closing gaps in audio-video sync and physically accurate fast motion.',
            f'On AnyAIGC the model name is <code>{MODEL}</code>. It runs as an async task on <code>POST /v1/videos</code>, supports text-to-video and first-frame image-to-video, and returns a 1280×720 landscape or 720×1280 portrait MP4 at {p} per second.',
        ],
        spec=[('Model', f'<code>{MODEL}</code>'), ('Endpoint', 'POST /v1/videos'), ('Length', '4–30 s (seconds)'),
              ('Size', '1280×720 / 720×1280'), ('Output', '720p MP4 · audio'), ('Input', 'Text · first frame')],
        features_h2='What Muse Video can do',
        features=[
            ('juggler', 'Native audio', 'Foley, ambience, voiceover and dialogue are generated with the picture, so there is no separate dubbing step. In Meta\'s sample every dropped orange lands with a sound.'),
            ('ducklings', 'Prompt adherence', 'Counts, order and actions follow the prompt. The sample asks for exactly five ducklings and keeps five on screen the whole time.'),
            ('panda', 'Temporal consistency', 'Subjects keep the same look through the clip, even after tumbling or turning around.'),
            ('kettle-ad', 'UGC-style ads', 'Handheld shake, focus shifts and a creator talking to camera, so you get a spot that looks self-shot without actors or a crew.'),
            ('podcast', 'Talking characters', 'Write the lines in your prompt and the character says them, with lip movement matched to the audio.'),
            ('snow-pond', 'Camera and mood', 'First-person walks and handheld follow shots track the prompt, with lighting, weather and ambient sound setting the mood.'),
        ],
        gallery_h2='Official Muse Video samples', gallery_lead='These clips were generated by Muse Video and come from Meta\'s launch post. They have sound; press play. Captions summarize the official prompts.',
        credit='Sample videos come from Meta\'s launch post, were generated by Muse Video, and are copyrighted by Meta.', credit_link='View source',
        pricing_h2='Muse Video API pricing', pricing_lead=f'Billed per second of video at {p}, reserved on submit and refunded automatically if the task fails.',
        billing=[('Per second', 'Billed on the requested seconds'), ('Refund on failure', 'Failed tasks are refunded automatically'), ('Unlimited concurrency', 'On by default for every account'), ('One balance', 'Works across 300+ models')],
        table_caption='Muse Video API pricing (USD)', th=('Feature', 'Model', 'Billing', 'AnyAIGC price'),
        rows=[('Text-to-video', 'Prompt only'), ('First-frame image-to-video', 'With input_reference')], unit='second', billing_word='Per second',
        price_note=f'Prices are in USD as listed in the model catalog. Meta has not published API pricing for Muse Video yet. The requested seconds are reserved on submit, invalid parameters return 400 with no charge, and live pricing is in the <a href="{PRICING}">model catalog</a>.',
        round_h3='How length is rounded', round_note='Output length only rounds up, never below what you asked for; billing uses the requested seconds. Clips over 10 seconds are generated in segments and stitched, with a cut at 10 and 20 seconds.',
        round_th=('Requested seconds', 'Output length (s)'),
        costs_h3='Cost examples', costs_note='Straight multiplication of the per-second price.',
        costs=[('A 5-second clip', '5 × per-second price', 5, '1–2 minutes to render'), ('A 10-second ad', '10 × per-second price', 10, 'One continuous take'),
               ('A 30-second video', '30 × per-second price', 30, '3–7 minutes to render')],
        market_btn='View in the model catalog',
        uses_h2='Muse Video API use cases',
        uses=[('E-commerce', 'Product videos', 'Use a product photo as the first frame for unboxing, in-use and lifestyle clips in either orientation.'),
              ('Marketing', 'Ads and UGC-style spots', 'Script the shots, lines and sound in the prompt and get a 10-second ad with voiceover.'),
              ('Social', 'Vertical shorts', '720×1280 portrait output for TikTok, Reels and Shorts.'),
              ('Content', 'Explainers', 'Break a concept into shot descriptions and get narrated clips with on-screen text.'),
              ('Film', 'Animatics and previs', 'Turn script pages into moving storyboards with sound to lock timing and framing.'),
              ('Games', 'Trailers and cutscenes', 'Generate character action and scene transitions for trailer material.')],
        why_h2='Why call it through AnyAIGC',
        why=[('One key, 300+ models', 'Muse Video, Muse Image, Seedance, Kling and other video and image models share one API key and balance.'),
             ('Works from mainland China', 'The base URL <code>https://anyaigc.ai</code> is reachable from China, with no Meta account needed.'),
             ('Per-second billing, refunds', f'{p} per second, reserved on submit and refunded if generation fails.'),
             ('Unlimited concurrency', 'No concurrency cap by default, so batch jobs never wait for a quota request.')],
        qs_h2='Get started with the Muse Video API',
        steps=[f'<a href="{REG}">Sign up for AnyAIGC</a>. New accounts get 2M free tokens, and top-ups start at $1.',
               'Create an API key in the <a href="https://anyaigc.ai/console">console</a> and save it as <code>ANYAIGC_API_KEY</code>.',
               f'Submit a task to <code>POST https://anyaigc.ai/v1/videos</code> with <code>model</code> set to <code>{MODEL}</code>, then poll <code>GET /v1/videos/{{id}}</code> until <code>status</code> is <code>completed</code>.'],
        tabs=[('py', 'Python', 'Python · submit and poll', code_py('en')), ('curl', 'cURL', 'cURL · create and query', code_curl('en')),
              ('i2v', 'Image to video', 'Python · first-frame image-to-video (portrait, 8 s)', code_i2v('en'))],
        qs_note=f'Status goes <code>queued</code> → <code>in_progress</code> → <code>completed</code> / <code>failed</code>. Clips up to 10 seconds take about 1–2 minutes, 15–30 seconds about 3–7 minutes. On failure you get an <code>error</code>: <code>video_generation_failed</code> means no video was produced (policy or a temporary upstream error), so rephrase or retry later; <code>video_rejected</code> means the output failed checks and was discarded, so just retry. See the <a href="{DOCS_CREATE}" target="_blank" rel="noopener">AnyAIGC API docs</a> for every field.',
        ent_h2='Muse Video API for teams and enterprises',
        ent_lead='E-commerce companies, ad agencies and content teams can buy through a standard business process, with support for finance, legal and engineering.',
        ent_cards=[('Invoices', 'Including China VAT invoices', 'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.'),
                   ('Bank transfer', 'Pay from a company account', 'Top up by corporate bank transfer, so nobody has to pay on a personal card and expense it.'),
                   ('Contracts', 'Fits procurement and legal review', 'Sign a service agreement with AnyAIGC to meet your internal purchasing requirements.'),
                   ('Dedicated support', 'Account and technical contacts', 'Work with a dedicated support contact and technical engineer for onboarding, migration and troubleshooting.')],
        sales='Talk to sales', trial='Start with a free account',
        faq_h2='Muse Video API FAQ',
        faqs=[
            ('How much does the Muse Video API cost?', f'On AnyAIGC, Muse Video (<code>{MODEL}</code>) costs {p} per second, billed on the requested <code>seconds</code>: {cost(5, "en")} for 5 seconds, {cost(10, "en")} for 10 and {cost(30, "en")} for 30. The amount is reserved on submit, failed tasks are refunded, and live pricing is in the model catalog.'),
            ('What is Muse Video?', 'Muse Video is the video model Meta Superintelligence Labs previewed alongside Muse Image, on the same pretraining base, with native audio. It is an early preview and, per Meta, ranked No. 3 on Arena for text-to-video as of July 5, 2026.'),
            ('How long can a video be?', '<code>seconds</code> takes an integer from 4 to 30 (default 4). Output only rounds up: 4 or 5 gives 5 seconds, 7 or 8 gives 8, 11–15 gives 15, and so on. Clips over 10 seconds are generated in segments with a cut at 10 and 20 seconds. Billing uses the requested seconds.'),
            ('Which sizes and resolutions are supported?', '<code>size</code> is <code>1280x720</code> (landscape) or <code>720x1280</code> (portrait), landscape by default. <code>resolution</code> can only be <code>720p</code> and may be omitted. Output is MP4 with audio.'),
            ('Can I generate video from an image?', 'Yes. Pass an image as <code>input_reference</code> to use it as the first frame: an image URL or data URL (PNG, JPEG or WebP), or upload the file directly with multipart/form-data. File IDs are not supported.'),
            ('How long does it take, and how do I get the result?', 'It is asynchronous: <code>POST /v1/videos</code> returns a task <code>id</code>, then poll <code>GET /v1/videos/{id}</code> every 10–20 seconds. Clips up to 10 seconds take about 1–2 minutes, 15–30 seconds about 3–7 minutes.'),
            ('Am I charged if generation fails?', 'No. Failed tasks are refunded automatically, and invalid parameters return 400 (<code>client_local_validation</code>) without creating a task or charging you.'),
            ('Is there a concurrency limit? Does it work from China?', 'AnyAIGC sets no concurrency limit on Muse Video for any account. The base URL is <code>https://anyaigc.ai</code>, reachable from mainland China, with no Meta account needed, and the same key works for 300+ other models.'),
            ('Can AnyAIGC issue invoices, including VAT special invoices?', 'Yes. AnyAIGC issues an invoice for every top-up, including Chinese VAT general and special invoices. Send your billing details to support.'),
            ('Can my company pay by bank transfer and sign a contract?', f'Yes. You can top up by corporate bank transfer and sign a service agreement, with a dedicated support and technical contact. <a href="{SUPPORT}">Contact AnyAIGC support</a> to get started.'),
            ('Can I use the videos commercially?', 'Usage rights and content policies follow Meta\'s official terms. AnyAIGC only provides API access and places no extra limits on how you use the output.'),
        ],
        final_h2='Start building with Muse Video', final_p=f'2M free tokens to start, {p} per second, unlimited concurrency.',
        signup_any='Sign up for AnyAIGC', read_docs='Read the API docs', more='More', all_hub='All model guides', in_other='Muse Video API 中文版',
        sibling=('Muse Image API', '/en/models/muse-image'),
        foot_desc='An API gateway for global AI models. One base URL and one API key for 300+ models.',
        foot=('Product', 'Resources', 'Legal'), foot_links=('Model guides', 'Model catalog', 'Console', 'API docs ↗', 'Meta blog ↗', 'Contact us', 'Privacy Policy', 'Terms of Service'),
        legal='&copy; 2026 AnyAIGC. Muse and Meta are trademarks of Meta Platforms, Inc. AnyAIGC is an independent API provider and is not affiliated with Meta. Sample videos come from Meta\'s launch post and are copyrighted by Meta.',
    )


# ---------------- 版块（视频专用；其余沿用 muse_image_pages） ----------------
def hero(lang, c):
    facts = ''.join(f'<li>{k} <strong>{v}</strong></li>' for k, v in c['facts'])
    return f'''  <!-- Hero -->
  <section class="mi-hero" aria-labelledby="hero-title">
    <div class="o-wrap">
      <nav aria-label="{c['crumbs']}">
        <ol class="o-crumbs">
          <li><a href="/">{c['home']}</a></li><li><a href="/{lang}/models/">{c['hub']}</a></li><li aria-current="page">{NAME}</li>
        </ol>
      </nav>
      <p class="mi-badge">{c['badge']}</p>
      <p class="mi-kicker">{B.logo_color(28)}<span>{c['kicker']}</span></p>
      <h1 class="mi-h1" id="hero-title">{c['h1']}</h1>
      <p class="mi-lead">{c['lead']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{c['get_key']}</a>
        <a class="o-btn o-btn-light" href="#pricing">{c['see_price']}</a>
      </div>
      <ul class="o-facts" aria-label="{c['facts_label']}">{facts}</ul>
      <figure class="mv-hero-video">{vid(HERO, c['hero_cap'], eager=True)}<figcaption>{c['hero_cap']}</figcaption></figure>
    </div>
  </section>

'''


def features(lang, c):
    lis = ''.join(f'        <li class="mi-feature o-reveal"><div class="mi-feature-img mv-frame">{vid(n, h)}</div>'
                  f'<div class="mi-feature-body"><h3>{h}</h3><p>{p}</p></div></li>{NL}' for n, h, p in c['features'])
    return B.section('features', c['features_h2'], f'      <ul class="mi-features">{NL}{lis}      </ul>{NL}', band=True)


def gallery(lang, c):
    i = 1 if lang == 'zh' else 3
    pick = [v for v in VIDS if v[0] not in {f[0] for f in c['features']} | {HERO}]
    lis = ''.join(f'        <li class="mv-shot o-reveal"><figure>{vid(v[0], v[i + 1])}<figcaption><b>{v[i]}</b>{html.escape(v[i + 1], quote=False)}</figcaption></figure></li>{NL}'
                  for v in pick)
    inner = (f'      <ul class="mv-gallery">{NL}{lis}      </ul>{NL}'
             f'      <p class="o-note">{c["credit"]} <a href="{META_BLOG}" target="_blank" rel="noopener">{c["credit_link"]}</a></p>{NL}')
    return B.section('gallery', c['gallery_h2'], inner, c['gallery_lead'])


def pricing(lang, c):
    bill = ''.join(f'<li><strong>{a}</strong>{b}</li>' for a, b in c['billing'])
    th = ''.join(f'<th scope="col"{" class=\"o-num\"" if i >= 3 else ""}>{t}</th>' for i, t in enumerate(c['th']))
    price = f'¥{CNY}' if lang == 'zh' else f'${USD}'
    rows = ''.join(f'            <tr><th scope="row">{a}<small>{b}</small></th><td><code>{MODEL}</code></td><td>{c["billing_word"]}</td>'
                   f'<td class="o-num o-hl">{price} / {c["unit"]}</td></tr>{NL}' for a, b in c['rows'])
    rnd = ''.join(f'<tr><td>{a if lang == "zh" else a.replace("、", ", ")}</td><td class="o-num">{b}</td></tr>' for a, b in ROUND)
    costs = ''.join(f'''        <li class="o-cost o-reveal">
          <h4>{h}</h4>
          <p class="o-cost-calc">{calc}</p>
          <p class="o-cost-total">{cost(sec, lang)}</p>
          <p class="o-cost-off">{off}</p>
        </li>{NL}''' for h, calc, sec, off in c['costs'])
    inner = f'''      <ul class="o-billing o-reveal" aria-label="{c['pricing_h2']}">{bill}</ul>
      <div class="o-table-wrap o-reveal">
        <table class="o-table">
          <caption class="o-sr">{c['table_caption']}</caption>
          <thead><tr>{th}</tr></thead>
          <tbody>
{rows}          </tbody>
        </table>
      </div>
      <p class="o-note">{c['price_note']}</p>
      <h3 class="mi-h3 o-reveal">{c['round_h3']}</h3>
      <p class="o-note">{c['round_note']}</p>
      <div class="o-table-wrap mv-round o-reveal">
        <table class="o-table">
          <caption class="o-sr">{c['round_h3']}</caption>
          <thead><tr><th scope="col">{c['round_th'][0]}</th><th scope="col" class="o-num">{c['round_th'][1]}</th></tr></thead>
          <tbody>{rnd}</tbody>
        </table>
      </div>
      <h3 class="mi-h3 o-reveal">{c['costs_h3']}</h3>
      <p class="o-note">{c['costs_note']}</p>
      <ul class="o-costs">
{costs}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-dark" href="{REG}">{c['get_key']}</a>
        <a class="o-btn o-btn-light" href="{PRICING}">{c['market_btn']}</a>
      </div>
'''
    return B.section('pricing', c['pricing_h2'], inner, c['pricing_lead'])


def final(lang, c):
    s = B.final(lang, c)
    name, href = c['sibling']
    return s.replace('<li><a class="o-pill" href="' + PRICING + '">', f'<li><a class="o-pill" href="{href}">{name}</a></li>\n        <li><a class="o-pill" href="{PRICING}">', 1)


def footer(lang, c):
    return B.footer(lang, c).replace(B.META_DOC, META_BLOG)


def page(lang):
    c = copy_zh() if lang == 'zh' else copy_en()
    B._n[0] = 0
    out = (B.head(lang, c) + B.nav(lang, c) + hero(lang, c) + B.about(c) + features(lang, c) + gallery(lang, c) + pricing(lang, c)
           + B.uses(c) + B.why(c) + B.quickstart(c) + B.enterprise(c) + B.faq(c) + final(lang, c) + footer(lang, c))
    # head() 只引入 muse-image.css；视频页再加一份 muse-video.css
    return out.replace(f'<link rel="stylesheet" href="/assets/models/{B.ASSET}.css?v={B.VER}">',
                       f'<link rel="stylesheet" href="/assets/models/muse-image.css?v={B.VER}">\n<link rel="stylesheet" href="/assets/models/muse-video.css?v={VER}">', 1)


def main():
    # 把共用版块指向 Muse Video（URL、名称、日期）
    B.SLUG, B.NAME, B.DATE, B.MODEL = SLUG, NAME, DATE, MODEL
    B.META_COLOR, B.META_MONO = B.icon('meta-color'), B.icon('meta')
    for lang in sys.argv[1:] or ['zh', 'en']:
        p = os.path.join(ROOT, lang, 'models', SLUG + '.html')
        io.open(p, 'w', encoding='utf-8', newline=NL).write(page(lang))
        print('written:', f'{lang}/models/{SLUG}.html')


if __name__ == '__main__':
    main()
