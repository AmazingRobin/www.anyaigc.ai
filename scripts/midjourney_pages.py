# 生成 Midjourney 统一专题页（中英文各 1 页，覆盖 14 个 mj_* 模型）：python scripts/midjourney_pages.py
# 每次整页重写，并直接调用 scripts/payments.py、scripts/trust.py 的函数补上支付方式与信任版块（只处理本页；
#   2026-11-11 时这两个脚本全站运行会在 Kling/Qwen 页面报错中断）。
# 数据见 scripts/midjourney_data.py；风格参考 midjourney.com（深海军蓝底、ASCII 扫描线、JetBrains Mono 等宽、半透明彩色胶囊按钮）。
import html
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from midjourney_data import (SLUG, DATE, VER, SITE, REG, PRICING, SUPPORT, DOCS, RATE, EXPLORE,  # noqa: E402
                             MODELS, usd, cny, IMG, VID, WALL)
from seedream_layout import hl  # noqa: E402  极简代码高亮（字符串 / 注释 / 关键字）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
BASE = 'https://anyaigc.ai'
P_IMG, P_HALF, P_UP = usd('mj_imagine'), usd('mj_describe'), usd('mj_upload')


def icon_body():
    raw = io.open(os.path.join(ROOT, 'assets/icons/midjourney.svg'), encoding='utf-8').read()
    body = re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S).group(1)
    return re.sub(r'<title>.*?</title>', '', body, flags=re.S)


LOGO = None


def logo(size, cls=''):
    c = f' class="{cls}"' if cls else ''
    return (f'<svg{c} viewBox="0 0 24 24" width="{size}" height="{size}" fill="#ffffff" fill-rule="evenodd" '
            f'aria-hidden="true" focusable="false">{LOGO}</svg>')


def img(name, alt, eager=False, cls=''):
    w, h, _ = IMG[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="/assets/models/midjourney/{name}.webp?v={VER}" width="{w}" height="{h}" '
            f'alt="{html.escape(alt, quote=True)}" {load} decoding="async">')


def video(name, label):
    w, h, _ = VID[name]
    return (f'<video class="mj-video" src="/assets/models/midjourney/{name}.mp4?v={VER}" poster="/assets/models/midjourney/{name}-poster.webp?v={VER}" '
            f'width="{w}" height="{h}" muted loop playsinline controls preload="none" aria-label="{html.escape(label, quote=True)}"></video>')


def text(h):
    t = re.sub(r'<[^>]+>', '', h)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


def p(m, lang, unit=True):
    v = usd(m)
    if v == '0':
        return '免费' if lang == 'zh' else 'Free'
    return f'${v}' + (f'<span class="mj-unit">{" / 次" if lang == "zh" else " / call"}</span>' if unit else '')


# ---------------- 代码示例 ----------------
PROMPT = {'zh': 'a lighthouse on a cliff at dawn, film grain, soft pastel sky --ar 3:2 --v 6.1',
          'en': 'a lighthouse on a cliff at dawn, film grain, soft pastel sky --ar 3:2 --v 6.1'}
CMT = {
    'zh': dict(submit='1. 提交 Imagine 任务，返回任务 ID（result）', poll='2. 轮询任务，SUCCESS 后 imageUrl 可用', fail='有 failReason 说明任务失败',
               btn='3. buttons 列出可继续执行的操作（U1–U4、V1–V4、Zoom、Pan 等）', up='4. 对第 1 张图放大：customId 必须取自 buttons，不要自己拼',
               key='Key 从环境变量读取', p='提示词里可以直接写 Midjourney 参数', code='提交成功时 code 为 1、result 为任务 ID，否则看 description',
               limit='最多等 10 分钟'),
    'en': dict(submit='1. Submit an Imagine task; result is the task ID', poll='2. Poll the task; imageUrl is ready once status is SUCCESS', fail='a failReason means the task failed',
               btn='3. buttons lists follow-up actions (U1-U4, V1-V4, Zoom, Pan and more)', up='4. Upscale image 1: always take customId from buttons, never build it yourself',
               key='Read the key from an environment variable', p='Midjourney parameters go straight into the prompt', code='On success code is 1 and result is the task ID; otherwise check description',
               limit='wait up to 10 minutes'),
}


def helpers(lang):
    c = CMT[lang]
    return f'''BASE = "{BASE}"
HEADERS = {{"Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"]}}  # {c['key']}


def submit(path, body):
    r = requests.post(BASE + path, headers=HEADERS, timeout=60, json=body).json()
    if r.get("code") != 1 or not r.get("result"):  # {c['code']}
        raise RuntimeError(f"{{r.get('code')}} {{r.get('description')}}")
    return r["result"]


def wait(task_id):
    for _ in range(120):  # {c['limit']}
        task = requests.get(f"{{BASE}}/mj/task/{{task_id}}/fetch", headers=HEADERS, timeout=30).json()
        if task.get("status") == "SUCCESS":
            return task
        if task.get("failReason"):  # {c['fail']}
            raise RuntimeError(task["failReason"])
        print(task.get("status"), task.get("progress"))
        time.sleep(5)
    raise TimeoutError(task_id)'''


def code_py(lang):
    c = CMT[lang]
    return f'''import os
import time
import requests

{helpers(lang)}


# {c['submit']}
task_id = submit("/mj/submit/imagine", {{
    "prompt": "{PROMPT[lang]}",  # {c['p']}
    "botType": "MID_JOURNEY",
}})
task = wait(task_id)  # {c['poll']}
print(task["imageUrl"])

# {c['btn']}
for b in task["buttons"]:
    print(b["label"], b["customId"])

# {c['up']}
u1 = next(b for b in task["buttons"] if b["customId"].startswith("MJ::JOB::upsample") and "::1::" in b["customId"])
up = wait(submit("/mj/submit/action", {{"taskId": task["id"], "customId": u1["customId"]}}))
print(up["imageUrl"])'''


def code_curl(lang):
    return f'''# Imagine
curl -X POST {BASE}/mj/submit/imagine \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{"prompt": "{PROMPT[lang]}", "botType": "MID_JOURNEY"}}'
# => {{"code": 1, "description": "Submit success", "result": "1730621718151844"}}

# {'查询任务' if lang == 'zh' else 'Fetch the task'}
curl {BASE}/mj/task/1730621718151844/fetch \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY"'''


def code_blend(lang):
    cm = ('2–5 张图，base64 带 data URL 前缀' if lang == 'zh' else '2-5 images as base64 with the data URL prefix')
    dm = ('SQUARE / PORTRAIT / LANDSCAPE' if lang == 'zh' else 'SQUARE / PORTRAIT / LANDSCAPE')
    ds = ('Describe：上传一张图，反推提示词' if lang == 'zh' else 'Describe: send one image, get prompts back')
    dp = ('反推结果所在字段以实际返回为准，先打印整个任务看一下' if lang == 'zh' else 'print the whole task to see which field holds the prompts')
    return f'''import base64
import mimetypes
import os
import time
import requests

{helpers(lang)}


def data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        return f"data:{{mime}};base64," + base64.b64encode(f.read()).decode()


# Blend
blend = wait(submit("/mj/submit/blend", {{
    "base64Array": [data_url("a.png"), data_url("b.jpg")],  # {cm}
    "dimensions": "SQUARE",  # {dm}
}}))
print(blend["imageUrl"])

# {ds}
desc = wait(submit("/mj/submit/describe", {{"base64": data_url("a.png"), "botType": "MID_JOURNEY"}}))
print(desc)  # {dp}'''


# ---------------- 价格表 ----------------
# (分组键, [(模型, 功能, 说明, 接口)])
def groups(lang):
    z = lang == 'zh'
    return [
        ('出图' if z else 'Generate', [
            ('mj_imagine', 'Imagine 文生图 / 垫图' if z else 'Imagine (text or image prompt)', '一次出 4 张候选图' if z else 'Returns a grid of 4 images'),
            ('mj_blend', 'Blend 混图' if z else 'Blend', '2–5 张图融合成新图' if z else 'Merge 2-5 images into one'),
            ('mj_describe', 'Describe 图生文' if z else 'Describe', '上传图片，反推提示词' if z else 'Turn an image into prompts'),
        ]),
        ('对结果继续操作（/mj/submit/action）' if z else 'Follow-up actions (/mj/submit/action)', [
            ('mj_upscale', 'Upscale 放大' if z else 'Upscale', 'U1–U4 选图 / Subtle、Creative 放大' if z else 'U1-U4, Subtle and Creative upscales'),
            ('mj_variation', 'Variation 变体' if z else 'Variation', 'V1–V4' if z else 'V1-V4'),
            ('mj_high_variation', 'Vary (Strong) 强变化' if z else 'Vary (Strong)', '变化幅度大' if z else 'Bigger changes'),
            ('mj_low_variation', 'Vary (Subtle) 弱变化' if z else 'Vary (Subtle)', '只做细微调整' if z else 'Small tweaks'),
            ('mj_reroll', 'Reroll 重新生成' if z else 'Reroll', '同一提示词再出一组' if z else 'Same prompt, new grid'),
            ('mj_zoom', 'Zoom Out 扩图' if z else 'Zoom Out', '1.5x / 2x 向外扩展画面' if z else 'Expand the frame 1.5x or 2x'),
            ('mj_pan', 'Pan 平移扩图' if z else 'Pan', '向上下左右延展' if z else 'Extend up, down, left or right'),
            ('mj_custom_zoom', 'Custom Zoom 自定义扩图' if z else 'Custom Zoom', f'弹窗确认后才出图，确认按 Modal ${P_IMG} / 次计费' if z else f'Renders after the modal step (billed as Modal, ${P_IMG})'),
            ('mj_inpaint', 'Vary (Region) 局部重绘' if z else 'Vary (Region)', f'弹窗确认后才出图，确认按 Modal ${P_IMG} / 次计费' if z else f'Renders after the modal step (billed as Modal, ${P_IMG})'),
        ]),
        ('弹窗确认与工具' if z else 'Modal and utilities', [
            ('mj_modal', 'Modal 弹窗确认' if z else 'Modal', '局部重绘 / 自定义扩图的第二步，提交蒙版或提示词' if z else 'Second step for Vary (Region) and Custom Zoom, with mask or prompt'),
            ('mj_upload', '上传参考图' if z else 'Upload images', '返回图片链接，可放进提示词' if z else 'Returns URLs you can use in prompts'),
        ]),
    ]


# ---------------- 文案 ----------------
def copy_zh():
    pi, ph = f'${P_IMG}', f'${P_HALF}'
    ci = cny(P_IMG)
    return dict(
        lang='zh-CN', og='zh_CN', og_alt='en_US', other='en', other_name='English', other_lang='en',
        title=f'Midjourney API 价格与接入｜{pi}/次，14 种操作 - AnyAIGC',
        desc=f'Midjourney API 中转：Imagine 出图 {pi}/次（约 ¥{ci}），放大与图生文 {ph}/次，支持 Blend、Zoom、Pan、局部重绘等 14 种操作，并发不限，支持对公转账与增值税专票。',
        keywords='Midjourney API,Midjourney API 价格,Midjourney API key,MJ API,Midjourney 接口,Midjourney 中转,Niji API,mj_imagine,Midjourney API 企业,Midjourney API 发票,AnyAIGC',
        og_desc=f'Midjourney API：Imagine {pi}/次，放大 {ph}/次，14 种操作覆盖出图、变体、扩图、局部重绘与图生文，并发不限。',
        og_alt_txt='AnyAIGC Midjourney API 价格与接入',
        home='首页', hub='模型专题', market='模型广场', price='价格', ent='企业接入', docs='API 文档', login='登录', signup='免费注册',
        get_key='获取 API Key', see_price='查看价格', skip='跳到主要内容', nav_label='主导航', crumbs='面包屑', facts_label='核心信息',
        home_label='AnyAIGC 首页', wall_label='Midjourney 社区作品', img_label='Midjourney 社区作品', copy='复制', copied='已复制', code_label='代码示例',
        product='Midjourney API（AnyAIGC）',
        product_desc='通过 AnyAIGC 调用 Midjourney：Imagine、Blend、Describe、Upscale、Variation、Zoom、Pan、局部重绘等 14 种操作，按次计费。',
        category='图像生成 API',
        kicker='Midjourney · Niji · 14 种操作',
        h1='Midjourney API',
        lead=f'用 API 调用 Midjourney：一句提示词出 4 张图，再放大、变体、扩图或局部重绘。Imagine <strong>{pi} / 次</strong>（约 ¥{ci}），放大和图生文 <strong>{ph} / 次</strong>，并发不限。',
        facts=[('Imagine', f'{pi} / 次'), ('放大', f'{ph} / 次'), ('操作', '14 种'), ('并发', '不限'), ('企业', '对公 · 专票')],
        flow_h2='Midjourney API 怎么调用',
        flow_lead='和在 Discord 或网页里一样：先出一组 4 张，再在结果上点按钮。API 把每个按钮都返回给你，带上它的 customId 再提交一次就行。',
        flow=[('POST', '/mj/submit/imagine', '提交提示词', f'返回任务 ID。提示词里可直接写 <code>--ar</code>、<code>--v</code>、<code>--niji</code> 等参数。{pi} / 次'),
              ('GET', '/mj/task/{id}/fetch', '查询任务', '轮询到 <code>SUCCESS</code> 后拿到 <code>imageUrl</code>，同时返回 <code>buttons</code> 列表。查询不收费'),
              ('POST', '/mj/submit/action', '点按钮', f'传 <code>taskId</code> 和按钮的 <code>customId</code>：放大 {ph}，变体、扩图、平移 {pi}'),
              ('POST', '/mj/submit/modal', '弹窗确认', f'局部重绘、自定义扩图需要第二步，提交蒙版或新提示词。{pi} / 次')],
        features_h2='Midjourney API 能做什么',
        features=[
            ('cave-sea', 'Imagine 文生图', '一句提示词出 4 张候选，支持垫图（base64Array）。Midjourney 擅长光影、质感和构图，写实摄影和插画都很稳。'),
            ('panther', 'Niji 动漫与插画', '<code>botType</code> 填 <code>NIJI_JOURNEY</code> 切到 Niji 模型，二次元、漫画、日系插画更对味。'),
            ('wolf-cartoon', 'Variation 变体', 'V1–V4 在某一张上继续变化；Vary (Strong) 幅度大，Vary (Subtle) 只做微调。'),
            ('portrait-35mm', 'Upscale 放大', 'U1–U4 选出单张，再用 Subtle 或 Creative 放大，适合交付高清图。'),
            ('rococo', 'Zoom Out 与 Pan 扩图', '向外扩展 1.5x / 2x，或向一个方向平移延展，把竖图扩成横图也可以。'),
            ('collage-surreal', 'Blend 混图与 Describe 图生文', '2–5 张图融合成一张新图；或者上传一张图，让 Midjourney 反推 4 条提示词。'),
        ],
        gallery_h2='Midjourney 社区作品',
        gallery_lead='以下作品来自 Midjourney Explore 热门榜，说明为作者提示词的节选，用来展示 Midjourney 的画面风格；实际效果取决于完整提示词、模型版本和参数。',
        gallery=[('ink-couple', '黑白钢笔线描，相拥的情侣'), ('monet-cats', '莫奈印象派风格，白猫与黑猫在睡莲池里游泳'),
                 ('vhs-anime', '80 年代 VHS 截图质感的动画少女'), ('passion-fruit', '叠起来的三块百香果插画'),
                 ('picnic-editorial', '夏日野餐时装大片'), ('stickers', '7 枚促销主题贴纸'),
                 ('ink-hunter', '中国水墨风 2D 动画角色设定'), ('duck-sweater', '穿毛衣、戴墨镜的鸭子，数字绘画'),
                 ('night-crossing', '深夜空无一人的十字路口，电影感'), ('steps-fashion', '台阶上的浅蓝阔腿裤，杂志排版'),
                 ('chibi', '简笔 2D 萌系原创角色站在实景里'), ('clipart', '手绘儿童动物剪贴画')],
        video_h2='还能让图片动起来', video_lead='Midjourney 也有视频模型，下面两段来自 Explore 社区。AnyAIGC 目前开放的是上表 14 种图像操作，视频接口请以模型广场为准。',
        videos=[('graphic-figure', '红黑波点人物图形动画'), ('fish', '「The fish is swimming」')],
        credit='作品来自 Midjourney Explore 社区，版权归原作者所有，作者：', credit_link='查看 Explore',
        pricing_h2='Midjourney API 价格',
        pricing_lead=f'按次计费，固定单价，和出几张图、用哪个版本无关。最常用的 Imagine {pi} / 次，约 ¥{ci}。',
        billing=[('按次计费', '每次成功提交扣一次，不按 token'), ('一次 4 张', 'Imagine、Variation 等每次返回 4 张候选'), ('查询免费', '轮询任务状态不收费'), ('并发不限', '所有用户默认享有，余额 300+ 模型通用')],
        table_caption='Midjourney API 价格（美元）',
        th=('功能', '模型名', '接口', '单价（USD）', '约合人民币'),
        price_note=f'单位 USD，取自模型广场；人民币按 1 美元 ≈ ¥{RATE:.3f} 换算，仅供参考。按成功提交计费，实时价格以<a href="{PRICING}">模型广场</a>为准。',
        costs_h3='成本示例', costs_note='按上表单价直接相加，不含其他费用。',
        costs=[('出一组图并放大 1 张', f'Imagine {pi} + Upscale {ph}', '$0.0893', f'约 ¥{cny("0.0893")}'),
               ('100 个提示词各出一组再放大 1 张', '100 × $0.0893', '$8.93', f'约 ¥{cny("8.93")}'),
               ('10 张图反推提示词', f'10 × Describe {ph}', '$0.298', f'约 ¥{cny("0.298")}')],
        market_btn='在模型广场查看',
        uses_h2='Midjourney API 使用场景',
        uses=[('电商', '商品场景与主图', '用垫图保留商品，生成不同场景、季节和风格的氛围图。'),
              ('营销', '海报与社媒配图', '批量生成活动视觉，再挑一张放大交付。'),
              ('游戏', '角色与概念设定', 'Niji 出角色和场景概念，Variation 快速迭代方案。'),
              ('设计', '情绪板与灵感', 'Describe 反推参考图的提示词，Blend 把几张参考融合成方向稿。'),
              ('内容', '文章配图与封面', '用同一组风格参数，给系列文章出统一调性的头图。'),
              ('产品', '应用内 AI 绘画', '把 Midjourney 接进自己的 App 或小程序，用户在你的界面里出图。')],
        why_h2='为什么通过 AnyAIGC 调用 Midjourney',
        why=[('不用 Discord 账号', 'Midjourney 官方目前没有面向开发者的公开 API；在 AnyAIGC 拿一个 API Key 就能用 HTTP 调用，不用自己维护账号和频道。'),
             ('国内直连', f'接口地址 <code>{BASE}</code>，国内网络可以直接调用。'),
             ('按次计费', f'不用买月度订阅：Imagine {pi} / 次，放大 {ph} / 次，用多少付多少。'),
             ('一个 Key，300+ 模型', '同一个 Key 和余额还能调用 GPT Image、Nano Banana、Seedream 等生图模型，方便对比。')],
        qs_h2='快速接入 Midjourney API',
        steps=[f'<a href="{REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
               '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
               f'<code>POST {BASE}/mj/submit/imagine</code> 提交提示词，用返回的任务 ID 轮询 <code>/mj/task/{{id}}/fetch</code>。'],
        tabs=[('py', 'Python', 'Python · 出图 → 轮询 → 放大', code_py('zh')), ('curl', 'cURL', 'cURL · 提交与查询', code_curl('zh')),
              ('blend', 'Blend / Describe', 'Python · 混图与图生文', code_blend('zh'))],
        qs_note=f'请求头用 <code>Authorization: Bearer &lt;API Key&gt;</code>。提交接口返回 <code>{{"code": 1, "result": "任务 ID"}}</code>；查询接口返回 <code>status</code>、<code>progress</code>、<code>imageUrl</code>、<code>buttons</code> 等字段。完整字段见 <a href="{DOCS}" target="_blank" rel="noopener">AnyAIGC Midjourney 接口文档</a>。',
        ent_h2='企业接入 Midjourney API',
        ent_lead='电商、广告、游戏和设计团队可以走企业流程采购，财务、法务和技术对接都有对应支持。',
        ent_cards=[('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。'),
                   ('对公转账', '公司账户直接付款', '支持企业对公转账充值，不用个人垫付，账目清晰。'),
                   ('签订合同', '满足采购与法务流程', '可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。'),
                   ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。')],
        sales='联系企业客服', trial='先注册试用',
        faq_h2='Midjourney API 常见问题',
        faqs=[
            ('Midjourney API 多少钱？', f'AnyAIGC 上 Midjourney 按次计费：Imagine、Blend、Variation、Reroll、Zoom、Pan 和 Modal 每次 {pi}（约 ¥{ci}），Upscale 放大和 Describe 图生文每次 {ph}，上传参考图每次 ${P_UP}，Custom Zoom 和 Vary (Region) 免费（它们的弹窗确认按 Modal 计费）。查询任务不收费，实时价格以模型广场为准。'),
            ('Midjourney 有官方 API 吗？', 'Midjourney 官方目前没有面向开发者的公开 API，只能在网页和 Discord 里使用。AnyAIGC 把 Midjourney 服务封装成 HTTP 接口，出图的就是 Midjourney 自己的模型（含 Niji），不是用其他模型冒充；用一个 API Key 就能调用 Imagine、放大、变体、扩图等功能，不需要自己的 Discord 账号。'),
            ('14 个模型名有什么区别？分别走哪个接口？', '14 个模型名对应 Midjourney 的 14 种操作，都在本页价格表里：Imagine、Blend、Describe 各有独立接口；Upscale、Variation、Vary (Strong/Subtle)、Reroll、Zoom、Pan、Custom Zoom、Vary (Region) 都走 <code>/mj/submit/action</code>，由按钮的 <code>customId</code> 决定；Modal 是弹窗确认；Upload 用来上传参考图。'),
            ('支持哪些 Midjourney 版本？能用 Niji 吗？', '在提示词末尾用 <code>--v</code> 参数选择版本（接口文档示例为 <code>--v 6.1</code>），写法和官方一致，参数原样传给 Midjourney。<code>botType</code> 填 <code>NIJI_JOURNEY</code> 使用 Niji 动漫模型，默认 <code>MID_JOURNEY</code>。'),
            ('一次调用返回几张图？', 'Imagine、Variation、Reroll、Zoom、Pan 等每次返回一组 4 张候选（拼成一张网格图），按一次计费。要单张高清图，再对其中一张执行 Upscale。'),
            ('放大、变体这些操作怎么调用？', '先用 <code>/mj/task/{id}/fetch</code> 查到任务结果，返回的 <code>buttons</code> 里每个按钮都有 <code>customId</code>；把任务 ID 和 <code>customId</code> 传给 <code>/mj/submit/action</code> 即可。<code>customId</code> 必须取自返回结果，不要自己拼。'),
            ('并发有限制吗？国内能直接调用吗？', f'AnyAIGC 对 Midjourney 不设并发限制，所有用户默认享有。接口地址是 <code>{BASE}</code>，国内网络可以直接调用。'),
            ('AnyAIGC 能开发票吗？支持增值税专票吗？', '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
            ('企业可以对公转账和签合同吗？', f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
            ('生成的图片可以商用吗？', '图片的使用权和内容政策以 Midjourney 官方条款为准。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用。'),
        ],
        final_h2='现在开始调用 Midjourney', final_p=f'注册即送 200 万 tokens 试用额度，Imagine {pi} / 次，并发不限。',
        signup_any='免费注册 AnyAIGC', read_docs='阅读接口文档', more='更多', all_hub='全部模型专题', in_other='Midjourney API in English',
        foot_desc='国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。',
        foot=('产品', '资源', '条款'), foot_links=('模型专题', '模型广场', '控制台', 'API 文档 ↗', 'Midjourney 官网 ↗', '联系我们', '隐私政策', '服务条款'),
        legal='&copy; 2026 AnyAIGC。Midjourney 是 Midjourney, Inc. 的商标。AnyAIGC 是独立的 API 服务商，与 Midjourney 无隶属或合作关系。页面作品来自 Midjourney Explore 社区，版权归原作者所有。',
    )


def copy_en():
    pi, ph = f'${P_IMG}', f'${P_HALF}'
    return dict(
        lang='en', og='en_US', og_alt='zh_CN', other='zh', other_name='中文', other_lang='zh-CN',
        title=f'Midjourney API Pricing & Access | {pi} per call - AnyAIGC',
        desc=f'Midjourney API at {pi} per Imagine and {ph} per upscale: 14 operations incl. blend, zoom, pan, inpaint, unlimited concurrency, invoices and bank transfer.',
        keywords='Midjourney API,Midjourney API pricing,Midjourney API key,MJ API,Midjourney API access,Niji API,mj_imagine,Midjourney API for business,AnyAIGC',
        og_desc=f'Midjourney API: Imagine at {pi}, upscale at {ph}. 14 operations for generation, variations, zoom, inpainting and describe, with unlimited concurrency.',
        og_alt_txt='AnyAIGC Midjourney API pricing and access',
        home='Home', hub='Model guides', market='Model catalog', price='Pricing', ent='Enterprise', docs='API docs', login='Log in', signup='Sign up free',
        get_key='Get an API key', see_price='See pricing', skip='Skip to main content', nav_label='Main', crumbs='Breadcrumb', facts_label='Key facts',
        home_label='AnyAIGC home', wall_label='Midjourney community images', img_label='Midjourney community image', copy='Copy', copied='Copied', code_label='Code examples',
        product='Midjourney API (AnyAIGC)',
        product_desc='Call Midjourney through AnyAIGC: Imagine, Blend, Describe, Upscale, Variation, Zoom, Pan, inpainting and more: 14 operations, billed per call.',
        category='Image generation API',
        kicker='Midjourney · Niji · 14 operations',
        h1='Midjourney API',
        lead=f'Call Midjourney over HTTP: one prompt returns a grid of four, then upscale, vary, zoom out or repaint a region. Imagine is <strong>{pi} per call</strong> and upscales and describe are <strong>{ph}</strong>, with unlimited concurrency.',
        facts=[('Imagine', f'{pi} / call'), ('Upscale', f'{ph} / call'), ('Operations', '14'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
        flow_h2='How the Midjourney API works',
        flow_lead='It mirrors the web app and Discord: generate a grid of four, then press buttons on the result. The API hands you every button; send its customId back to run it.',
        flow=[('POST', '/mj/submit/imagine', 'Submit a prompt', f'Returns a task ID. Put <code>--ar</code>, <code>--v</code> or <code>--niji</code> straight into the prompt. {pi} per call'),
              ('GET', '/mj/task/{id}/fetch', 'Fetch the task', 'Poll until <code>SUCCESS</code> to get <code>imageUrl</code> and the <code>buttons</code> list. Fetching is free'),
              ('POST', '/mj/submit/action', 'Press a button', f'Send the <code>taskId</code> and a button\'s <code>customId</code>: upscales {ph}, variations, zoom and pan {pi}'),
              ('POST', '/mj/submit/modal', 'Confirm the modal', f'Vary (Region) and Custom Zoom need a second step with a mask or new prompt. {pi} per call')],
        features_h2='What you can do with the Midjourney API',
        features=[
            ('cave-sea', 'Imagine', 'One prompt returns four candidates, with optional image prompts via base64Array. Midjourney is known for light, texture and composition in both photography and illustration.'),
            ('panther', 'Niji for anime and illustration', 'Set <code>botType</code> to <code>NIJI_JOURNEY</code> to switch to Niji for anime, manga and illustrated styles.'),
            ('wolf-cartoon', 'Variations', 'V1-V4 riff on one image. Vary (Strong) moves further, Vary (Subtle) only nudges.'),
            ('portrait-35mm', 'Upscale', 'U1-U4 pull out a single image, then Subtle or Creative upscales get it ready to ship.'),
            ('rococo', 'Zoom Out and Pan', 'Expand the frame 1.5x or 2x, or extend it in one direction, for example turning a portrait into a landscape.'),
            ('collage-surreal', 'Blend and Describe', 'Merge 2-5 images into a new one, or send an image and get four prompts that describe it.'),
        ],
        gallery_h2='From the Midjourney community',
        gallery_lead='These come from top images on Midjourney Explore. Captions summarize each creator\'s prompt to show Midjourney\'s range; your results depend on the full prompt, model version and parameters.',
        gallery=[('ink-couple', 'Black ink line drawing of a couple embracing'), ('monet-cats', 'A white cat and a black cat swimming among water lilies, after Monet'),
                 ('vhs-anime', 'VHS screengrab of an 80s anime heroine'), ('passion-fruit', 'Three stacked passion fruit halves'),
                 ('picnic-editorial', 'Summer picnic fashion editorial'), ('stickers', 'Seven sale-themed stickers'),
                 ('ink-hunter', 'Chinese ink-wash 2D character sheet'), ('duck-sweater', 'A duck in a sweater and sunglasses, digital painting'),
                 ('night-crossing', 'An empty intersection late at night, cinematic'), ('steps-fashion', 'Light blue wide-leg pants on maroon steps, editorial layout'),
                 ('chibi', 'A simple 2D chibi character in a photo-real scene'), ('clipart', 'Hand-drawn animal clipart for kids')],
        video_h2='It can animate, too', video_lead='Midjourney also has a video model; these two clips come from the Explore community. AnyAIGC currently offers the 14 image operations listed below; check the model catalog for video.',
        videos=[('graphic-figure', 'Red and black halftone figure animation'), ('fish', '"The fish is swimming"')],
        credit='Images come from the Midjourney Explore community and belong to their creators:', credit_link='Open Explore',
        pricing_h2='Midjourney API pricing',
        pricing_lead=f'A flat price per call, whatever the version or number of images. The everyday Imagine call is {pi}.',
        billing=[('Per call', 'Each successful submission is one charge, no tokens'), ('Four per grid', 'Imagine, Variation and similar calls return four candidates'), ('Free polling', 'Fetching task status costs nothing'), ('Unlimited concurrency', 'On by default, one balance for 300+ models')],
        table_caption='Midjourney API pricing (USD)',
        th=('Feature', 'Model', 'Endpoint', 'Price (USD)', 'Notes'),
        price_note=f'Prices in USD as listed in the model catalog. Billed per successful submission; see the <a href="{PRICING}">model catalog</a> for live pricing.',
        costs_h3='Cost examples', costs_note='Straight addition of the prices above, nothing else added.',
        costs=[('One grid plus one upscale', f'Imagine {pi} + Upscale {ph}', '$0.0893', 'The most common flow'),
               ('100 prompts, one upscale each', '100 × $0.0893', '$8.93', 'Batch generation'),
               ('Describe 10 images', f'10 × Describe {ph}', '$0.298', 'Reverse-engineer prompts')],
        market_btn='View in the model catalog',
        uses_h2='Midjourney API use cases',
        uses=[('E-commerce', 'Product scenes', 'Keep the product with an image prompt and generate it in new settings, seasons and styles.'),
              ('Marketing', 'Campaign and social visuals', 'Generate campaign art in batches, then upscale the winner.'),
              ('Games', 'Characters and concept art', 'Use Niji for characters and environments, and Variations to iterate fast.'),
              ('Design', 'Mood boards', 'Describe a reference to get its prompt, or Blend several references into a direction.'),
              ('Content', 'Article art and covers', 'Reuse one set of style parameters for a consistent look across a series.'),
              ('Product', 'In-app image generation', 'Put Midjourney inside your own app so users create images in your interface.')],
        why_h2='Why call Midjourney through AnyAIGC',
        why=[('No Discord account', 'Midjourney does not currently offer a public API. With an AnyAIGC key you call it over HTTP, without maintaining accounts or channels.'),
             ('Unlimited concurrency', 'No concurrency cap on any account, so batch jobs run in parallel without asking for a quota increase.'),
             ('Pay per call', f'No monthly plan: Imagine is {pi} and upscales are {ph}, so you pay for what you use.'),
             ('One key, 300+ models', 'The same key and balance also run GPT Image, Nano Banana, Seedream and other image models for side-by-side tests.')],
        qs_h2='Get started with the Midjourney API',
        steps=[f'<a href="{REG}">Sign up for AnyAIGC</a>. New accounts get 2M free tokens, and top-ups start at $1.',
               'Create an API key in the <a href="https://anyaigc.ai/console">console</a> and save it as <code>ANYAIGC_API_KEY</code>.',
               f'<code>POST {BASE}/mj/submit/imagine</code> with your prompt, then poll <code>/mj/task/{{id}}/fetch</code> with the returned task ID.'],
        tabs=[('py', 'Python', 'Python · imagine, poll, upscale', code_py('en')), ('curl', 'cURL', 'cURL · submit and fetch', code_curl('en')),
              ('blend', 'Blend / Describe', 'Python · blend and describe', code_blend('en'))],
        qs_note=f'Authenticate with <code>Authorization: Bearer &lt;API Key&gt;</code>. Submit endpoints return <code>{{"code": 1, "result": "task ID"}}</code>; the fetch endpoint returns <code>status</code>, <code>progress</code>, <code>imageUrl</code>, <code>buttons</code> and more. See the <a href="{DOCS}" target="_blank" rel="noopener">AnyAIGC Midjourney API docs</a> for every field.',
        ent_h2='Midjourney API for teams and enterprises',
        ent_lead='E-commerce, advertising, game and design teams can buy through a standard business process, with support for finance, legal and engineering.',
        ent_cards=[('Invoices', 'Including China VAT invoices', 'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.'),
                   ('Bank transfer', 'Pay from a company account', 'Top up by corporate bank transfer, so nobody has to pay on a personal card and expense it.'),
                   ('Contracts', 'Fits procurement and legal review', 'Sign a service agreement with AnyAIGC to meet your internal purchasing requirements.'),
                   ('Dedicated support', 'Account and technical contacts', 'Work with a dedicated support contact and technical engineer for onboarding, migration and troubleshooting.')],
        sales='Talk to sales', trial='Start with a free account',
        faq_h2='Midjourney API FAQ',
        faqs=[
            ('How much does the Midjourney API cost?', f'AnyAIGC bills Midjourney per call: Imagine, Blend, Variation, Reroll, Zoom, Pan and Modal are {pi} each, Upscale and Describe are {ph}, image upload is ${P_UP}, and Custom Zoom and Vary (Region) are free (their modal step is billed as Modal). Fetching tasks is free, and live pricing is in the model catalog.'),
            ('Does Midjourney have an official API?', 'Midjourney does not currently offer a public API; it runs on its website and Discord. AnyAIGC wraps the Midjourney service in HTTP endpoints, so images come from Midjourney\'s own models (including Niji) rather than a substitute, and one API key can run Imagine, upscales, variations, zoom and more without a Discord account of your own.'),
            ('What are the 14 operations, and which endpoints do they use?', 'The 14 model names map to 14 Midjourney operations, all in the pricing table above. Imagine, Blend and Describe have their own endpoints. Upscale, Variation, Vary (Strong/Subtle), Reroll, Zoom, Pan, Custom Zoom and Vary (Region) all go through <code>/mj/submit/action</code>, selected by the button\'s <code>customId</code>. Modal is the confirmation step, and Upload sends reference images.'),
            ('Which Midjourney versions are supported? Can I use Niji?', 'Pick the version with the <code>--v</code> parameter at the end of the prompt (the API docs use <code>--v 6.1</code>), written the same way as in the official app and passed through to Midjourney. Set <code>botType</code> to <code>NIJI_JOURNEY</code> for the Niji anime model; the default is <code>MID_JOURNEY</code>.'),
            ('How many images does one call return?', 'Imagine, Variation, Reroll, Zoom, Pan and similar calls return a grid of four candidates and are billed once. For a single high-resolution image, run Upscale on one of them.'),
            ('How do I run upscales and variations?', 'Fetch the task with <code>/mj/task/{id}/fetch</code>. Each entry in <code>buttons</code> has a <code>customId</code>; send the task ID and that <code>customId</code> to <code>/mj/submit/action</code>. Always take <code>customId</code> from the response rather than building it yourself.'),
            ('Is there a concurrency limit?', f'No. AnyAIGC sets no concurrency limit on Midjourney for any account, so you can submit tasks in parallel. All requests go to the base URL <code>{BASE}</code>, and the same key works for 300+ other models.'),
            ('Can AnyAIGC issue invoices, including VAT special invoices?', 'Yes. AnyAIGC issues an invoice for every top-up, including Chinese VAT general and special invoices. Send your billing details to support.'),
            ('Can my company pay by bank transfer and sign a contract?', f'Yes. You can top up by corporate bank transfer and sign a service agreement, with a dedicated support and technical contact. <a href="{SUPPORT}">Contact AnyAIGC support</a> to get started.'),
            ('Can I use the images commercially?', 'Usage rights and content policies follow Midjourney\'s official terms. AnyAIGC only provides API access and places no extra limits on how you use the output.'),
        ],
        final_h2='Start building with Midjourney', final_p=f'2M free tokens to start, Imagine at {pi}, unlimited concurrency.',
        signup_any='Sign up for AnyAIGC', read_docs='Read the API docs', more='More', all_hub='All model guides', in_other='Midjourney API 中文版',
        foot_desc='An API gateway for global AI models. One base URL and one API key for 300+ models.',
        foot=('Product', 'Resources', 'Legal'), foot_links=('Model guides', 'Model catalog', 'Console', 'API docs ↗', 'Midjourney ↗', 'Contact us', 'Privacy Policy', 'Terms of Service'),
        legal='&copy; 2026 AnyAIGC. Midjourney is a trademark of Midjourney, Inc. AnyAIGC is an independent API provider and is not affiliated with Midjourney. Images on this page come from the Midjourney Explore community and belong to their creators.',
    )


# ---------------- 版块 ----------------
def page_url(lang):
    return f'{SITE}/{lang}/models/{SLUG}'


def offers(lang):
    out = []
    for _, rows in groups(lang):
        for m, name, _ in rows:
            out.append((f'{name}（{m}）' if lang == 'zh' else f'{name} ({m})', usd(m)))
    return out


def head(lang, c):
    me, zh, en = page_url(lang), page_url('zh'), page_url('en')
    og_img = f'{SITE}/assets/og/{SLUG}-{lang}.png'
    crumbs = [(c['home'], f'{SITE}/'), (c['hub'], f'{SITE}/{lang}/models/'), ('Midjourney', me)]
    of = offers(lang)
    prices = sorted(float(x) for _, x in of)
    graph = [
        {'@type': 'Organization', '@id': f'{SITE}/#org', 'name': 'AnyAIGC', 'url': 'https://anyaigc.ai', 'logo': f'{SITE}/logo.webp'},
        {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'AnyAIGC', 'publisher': {'@id': f'{SITE}/#org'}},
        {'@type': 'WebPage', '@id': f'{me}#webpage', 'url': me, 'name': c['title'], 'description': c['desc'], 'inLanguage': c['lang'],
         'isPartOf': {'@id': f'{SITE}/#website'}, 'breadcrumb': {'@id': f'{me}#breadcrumb'}, 'mainEntity': {'@id': f'{me}#product'}, 'dateModified': DATE},
        {'@type': 'BreadcrumbList', '@id': f'{me}#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]},
        {'@type': 'Product', '@id': f'{me}#product', 'name': c['product'], 'description': c['product_desc'], 'category': c['category'],
         'sku': 'mj_imagine', 'image': og_img, 'brand': {'@type': 'Brand', 'name': 'AnyAIGC'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'USD', 'lowPrice': '0', 'highPrice': P_IMG,
                    'offerCount': len(of), 'availability': 'https://schema.org/InStock', 'url': f'{me}#pricing',
                    'offers': [{'@type': 'Offer', 'name': n, 'price': x, 'priceCurrency': 'USD'} for n, x in of]}},
        {'@type': 'FAQPage', '@id': f'{me}#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}} for q, a in c['faqs']]},
    ]
    assert prices[0] == 0 and prices[-1] == float(P_IMG)
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    e = lambda s: html.escape(s, quote=True)
    return f'''<!DOCTYPE html>
<html lang="{c['lang']}" class="no-js" data-scrollbar="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(c['title'])}</title>
<meta name="description" content="{e(c['desc'])}">
<meta name="keywords" content="{e(c['keywords'])}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#06051d">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{zh}">
<link rel="alternate" hreflang="en" href="{en}">
<link rel="alternate" hreflang="x-default" href="{en}">
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{c['og']}">
<meta property="og:locale:alternate" content="{c['og_alt']}">
<meta property="og:url" content="{me}">
<meta property="og:title" content="{e(c['title'])}">
<meta property="og:description" content="{e(c['og_desc'])}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(c['og_alt_txt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(c['title'])}">
<meta name="twitter:description" content="{e(c['og_desc'])}">
<meta name="twitter:image" content="{og_img}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261024b">
<link rel="stylesheet" href="/assets/models/midjourney.css?v={VER}">
<script type="application/ld+json">
{ld}
</script>
</head>
'''


def nav(lang, c):
    o = c['other']
    return f'''<body>
<a class="o-skip" href="#main">{c['skip']}</a>

<header class="o-nav">
  <div class="o-wrap o-nav-inner">
    <a class="o-brand" href="/" aria-label="{c['home_label']}">AnyAIGC</a>
    <nav aria-label="{c['nav_label']}">
      <ul class="o-nav-left">
        <li><a class="o-pill" href="/{lang}/models/">{c['hub']}</a></li>
        <li class="mj-hide-sm"><a class="o-pill" href="{PRICING}">{c['market']}</a></li>
        <li><a class="o-pill" href="#pricing">{c['price']}</a></li>
        <li><a class="o-pill" href="#enterprise">{c['ent']}</a></li>
        <li class="mj-hide-md"><a class="o-pill" href="{DOCS}" target="_blank" rel="noopener">{c['docs']}</a></li>
      </ul>
    </nav>
    <ul class="o-nav-right">
      <li><a class="o-pill" href="/{o}/models/{SLUG}" hreflang="{c['other_lang']}" lang="{c['other_lang']}">{c['other_name']}</a></li>
      <li class="mj-hide-sm"><a class="o-pill" href="https://anyaigc.ai/console">{c['login']}</a></li>
      <li><a class="o-btn o-btn-go mj-nav-cta" href="{REG}">{c['signup']}</a></li>
    </ul>
  </div>
</header>

<main id="main">
'''


def hero(lang, c):
    facts = ''.join(f'<li>{k} <strong>{v}</strong></li>' for k, v in c['facts'])
    cols = ''
    for ci, col in enumerate(WALL):
        a = ''.join(f'<li>{img(n, f'{c["img_label"]} {ci * 5 + i + 1}', eager=(ci == 1 and i < 2))}</li>' for i, n in enumerate(col))
        b = ''.join(f'<li>{img(n, "")}</li>' for n in col)
        cols += f'<div class="mj-col mj-col-{ci + 1}"><ul>{a}</ul><ul aria-hidden="true">{b}</ul></div>'
    return f'''  <!-- Hero -->
  <section class="mj-hero" aria-labelledby="hero-title">
    <div class="mj-scan" aria-hidden="true"></div>
    <div class="o-wrap mj-hero-grid">
      <div class="mj-hero-copy">
        <nav aria-label="{c['crumbs']}">
          <ol class="o-crumbs">
            <li><a href="/">{c['home']}</a></li><li><a href="/{lang}/models/">{c['hub']}</a></li><li aria-current="page">Midjourney</li>
          </ol>
        </nav>
        <p class="mj-kicker">{logo(26)}<span>{c['kicker']}</span></p>
        <h1 class="mj-h1" id="hero-title">{c['h1']}</h1>
        <p class="mj-lead">{c['lead']}</p>
        <div class="o-cta">
          <a class="o-btn o-btn-go" href="{REG}">{c['get_key']}</a>
          <a class="o-btn o-btn-ghost" href="#pricing">{c['see_price']}</a>
        </div>
        <ul class="o-facts" aria-label="{c['facts_label']}">{facts}</ul>
      </div>
      <div class="mj-wall" role="region" aria-label="{c['wall_label']}" tabindex="0">{cols}</div>
    </div>
  </section>

'''


def section(sid, h2, inner, lead='', band=False, col=False):
    cls = 'o-section mj-band' if band else 'o-section'
    wrap = 'o-wrap o-col' if col else 'o-wrap'
    lead_html = f'      <p class="o-lead o-reveal">{lead}</p>{NL}' if lead else ''
    return (f'  <section class="{cls}" id="{sid}" aria-labelledby="{sid}-title">{NL}    <div class="{wrap}">{NL}'
            f'      <h2 class="o-h2 o-reveal" id="{sid}-title"><span class="mj-hash" aria-hidden="true">#</span>{h2}</h2>{NL}{lead_html}{inner}    </div>{NL}  </section>{NL}{NL}')


def flow(c):
    lis = ''.join(f'        <li class="mj-step o-reveal"><span class="mj-no">{i + 1:02d}</span><p class="mj-ep"><b class="mj-m mj-m-{m.lower()}">{m}</b><code>{path}</code></p>'
                  f'<h3>{h}</h3><p>{d}</p></li>{NL}' for i, (m, path, h, d) in enumerate(c['flow']))
    return section('how', c['flow_h2'], f'      <ol class="mj-flow">{NL}{lis}      </ol>{NL}', c['flow_lead'])


def features(c):
    lis = ''.join(f'        <li class="mj-feature o-reveal"><div class="mj-feature-img">{img(n, text(h))}</div><div class="mj-feature-body"><h3>{h}</h3><p>{d}</p></div></li>{NL}'
                  for n, h, d in c['features'])
    return section('features', c['features_h2'], f'      <ul class="mj-features">{NL}{lis}      </ul>{NL}', band=True)


def gallery(lang, c):
    lis = ''.join(f'        <li class="mj-shot o-reveal"><figure>{img(n, cap)}<figcaption><b>@{html.escape(IMG[n][2])}</b>{html.escape(cap, quote=False)}</figcaption></figure></li>{NL}'
                  for n, cap in c['gallery'])
    vids = ''.join(f'        <li class="mj-clip o-reveal"><figure>{video(n, cap)}<figcaption><b>@{html.escape(VID[n][2])}</b>{html.escape(cap, quote=False)}</figcaption></figure></li>{NL}'
                   for n, cap in c['videos'])
    authors = sorted({IMG[n][2] for n, _ in c['gallery']} | {IMG[n][2] for n, _, _ in c['features']} | {v[2] for v in VID.values()}
                     | {IMG[n][2] for col in WALL for n in col})
    sep, gap, end = ('、', '', '。') if lang == 'zh' else (', ', ' ', '. ')
    inner = (f'      <ul class="mj-gallery">{NL}{lis}      </ul>{NL}'
             f'      <div class="mj-video-row">{NL}        <div class="mj-video-copy o-reveal"><h3 class="mj-h3">{c["video_h2"]}</h3><p>{c["video_lead"]}</p></div>{NL}'
             f'        <ul class="mj-clips">{NL}{vids}        </ul>{NL}      </div>{NL}'
             f'      <p class="o-note">{c["credit"]}{gap}{html.escape(sep.join("@" + a for a in authors))}{end}<a href="{EXPLORE}" target="_blank" rel="noopener">{c["credit_link"]}</a></p>{NL}')
    return section('gallery', c['gallery_h2'], inner, c['gallery_lead'])


def pricing(lang, c):
    bill = ''.join(f'<li><strong>{a}</strong>{b}</li>' for a, b in c['billing'])
    th = ''.join(f'<th scope="col"{" class=\"o-num\"" if i == 3 else ""}>{t}</th>' for i, t in enumerate(c['th']))
    body = ''
    for g, rows in groups(lang):
        trs = ''
        for m, name, note in rows:
            v = usd(m)
            free = v == '0'
            price = p(m, lang)
            if lang == 'zh':
                extra = '—' if free else f'约 ¥{cny(v, "0.0001") if v == P_UP else cny(v)}'
            else:
                extra = {'mj_custom_zoom': 'Modal step billed', 'mj_inpaint': 'Modal step billed'}.get(m, 'Grid of 4' if m in ('mj_imagine', 'mj_blend', 'mj_variation', 'mj_high_variation', 'mj_low_variation', 'mj_reroll', 'mj_zoom', 'mj_pan') else '—')
            if lang == 'zh' and free:
                extra = '弹窗确认按 Modal 计费'
            trs += (f'            <tr><th scope="row">{name}<small>{note}</small></th><td><code>{m}</code></td><td><code class="mj-path">{MODELS[m][1]}</code></td>'
                    f'<td class="o-num o-hl{" mj-free" if free else ""}">{price}</td><td class="mj-extra">{extra}</td></tr>{NL}')
        body += f'          <tbody>{NL}            <tr class="mj-group"><th scope="rowgroup" colspan="5">{g}</th></tr>{NL}{trs}          </tbody>{NL}'
    costs = ''.join(f'''        <li class="o-cost o-reveal">
          <h4>{h}</h4>
          <p class="o-cost-calc">{calc}</p>
          <p class="o-cost-total">{tot}</p>
          <p class="o-cost-off">{off}</p>
        </li>{NL}''' for h, calc, tot, off in c['costs'])
    inner = f'''      <ul class="o-billing o-reveal" aria-label="{c['pricing_h2']}">{bill}</ul>
      <div class="o-table-wrap o-reveal">
        <table class="o-table">
          <caption class="o-sr">{c['table_caption']}</caption>
          <thead><tr>{th}</tr></thead>
{body}        </table>
      </div>
      <p class="o-note">{c['price_note']}</p>
      <h3 class="mj-h3 o-reveal">{c['costs_h3']}</h3>
      <p class="o-note">{c['costs_note']}</p>
      <ul class="o-costs">
{costs}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-go" href="{REG}">{c['get_key']}</a>
        <a class="o-btn o-btn-ghost" href="{PRICING}">{c['market_btn']}</a>
      </div>
'''
    return section('pricing', c['pricing_h2'], inner, c['pricing_lead'], band=True)


def uses(c):
    lis = ''.join(f'        <li class="o-reveal"><span class="mj-k">{k}</span><h3>{h}</h3><p>{d}</p></li>{NL}' for k, h, d in c['uses'])
    return section('use-cases', c['uses_h2'], f'      <ul class="mj-uses">{NL}{lis}      </ul>{NL}')


def why(c):
    lis = ''.join(f'        <li class="o-reveal"><h3>{h}</h3><p>{d}</p></li>{NL}' for h, d in c['why'])
    return section('why', c['why_h2'], f'      <ul class="mj-why">{NL}{lis}      </ul>{NL}', band=True)


def quickstart(c):
    steps = ''.join(f'<li>{s}</li>' for s in c['steps'])
    tabs = ''.join(f'        <li role="presentation"><button type="button" role="tab" id="tab-{k}" aria-controls="panel-{k}" aria-selected="{"true" if i == 0 else "false"}">{name}</button></li>{NL}'
                   for i, (k, name, _, _) in enumerate(c['tabs']))
    panels = ''.join(f'''      <figure class="o-code" id="panel-{k}" role="tabpanel" aria-labelledby="tab-{k}">
        <figcaption><b>{cap}</b><button class="o-copy" type="button" aria-controls="code-{k}" data-done="{c['copied']}">{c['copy']}</button></figcaption>
<pre id="code-{k}"><code>{hl(code)}</code></pre>
      </figure>{NL}''' for k, _, cap, code in c['tabs'])
    inner = (f'      <ol class="o-steps o-reveal">{steps}</ol>{NL}'
             f'      <ul class="o-tabs" role="tablist" aria-label="{c["code_label"]}">{NL}{tabs}      </ul>{NL}{panels}'
             f'      <p class="o-note">{c["qs_note"]}</p>{NL}')
    return section('quickstart', c['qs_h2'], inner)


def enterprise(c):
    cards = ''.join(f'        <li class="o-card o-reveal"><strong>{a}</strong><h3>{b}</h3><p>{d}</p></li>{NL}' for a, b, d in c['ent_cards'])
    return f'''  <section class="o-section mj-band" id="enterprise" aria-labelledby="ent-title">
    <div class="o-wrap o-col">
      <h2 class="o-h2 o-reveal" id="ent-title"><span class="mj-hash" aria-hidden="true">#</span>{c['ent_h2']}</h2>
      <p class="o-lead o-reveal">{c['ent_lead']}</p>
      <ul class="o-cards">
{cards}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-go" href="{SUPPORT}">{c['sales']}</a>
        <a class="o-btn o-btn-ghost" href="{REG}">{c['trial']}</a>
      </div>
    </div>
  </section>

'''


def faq(c):
    items = ''.join(f'        <details{" open" if i == 0 else ""}><summary><h3>{q}</h3></summary><div class="o-ans"><p>{a}</p></div></details>{NL}'
                    for i, (q, a) in enumerate(c['faqs']))
    return f'''  <!-- FAQ -->
  <section class="o-section" id="faq" aria-labelledby="faq-title">
    <div class="o-wrap o-col">
      <h2 class="o-h2 o-reveal" id="faq-title"><span class="mj-hash" aria-hidden="true">#</span>{c['faq_h2']}</h2>
      <div class="o-faq">
{items}      </div>
    </div>
  </section>

'''


def final(lang, c):
    o = c['other']
    return f'''  <!-- 结尾 CTA -->
  <section class="o-final" aria-labelledby="final-title">
    <div class="mj-scan" aria-hidden="true"></div>
    <div class="o-wrap">
      {logo(56, 'mj-final-logo')}
      <h2 id="final-title">{c['final_h2']}</h2>
      <p>{c['final_p']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-go" href="{REG}">{c['signup_any']}</a>
        <a class="o-btn o-btn-ghost" href="{DOCS}" target="_blank" rel="noopener">{c['read_docs']}</a>
      </div>
      <ul class="o-related" aria-label="{c['more']}">
        <li><a class="o-pill" href="/{lang}/models/">{c['all_hub']}</a></li>
        <li><a class="o-pill" href="{PRICING}">{c['market']}</a></li>
        <li><a class="o-pill" href="/{o}/models/{SLUG}" hreflang="{c['other_lang']}" lang="{c['other_lang']}">{c['in_other']}</a></li>
      </ul>
    </div>
  </section>
</main>
'''


def footer(lang, c):
    o = c['other']
    f = c['foot_links']
    return f'''<footer class="o-foot">
  <div class="o-wrap">
    <div class="o-foot-top">
      <div class="o-foot-brand">
        <a class="o-brand" href="/">AnyAIGC</a>
        <p>{c['foot_desc']}</p>
      </div>
      <div class="o-foot-cols">
        <div class="o-foot-col">
          <h2>{c['foot'][0]}</h2>
          <ul>
            <li><a href="/{lang}/models/">{f[0]}</a></li>
            <li><a href="{PRICING}">{f[1]}</a></li>
            <li><a href="https://anyaigc.ai/console">{f[2]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{c['foot'][1]}</h2>
          <ul>
            <li><a href="{DOCS}" target="_blank" rel="noopener">{f[3]}</a></li>
            <li><a href="https://www.midjourney.com" target="_blank" rel="noopener">{f[4]}</a></li>
            <li><a href="{SUPPORT}">{f[5]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{c['foot'][2]}</h2>
          <ul>
            <li><a href="/privacy">{f[6]}</a></li>
            <li><a href="/terms">{f[7]}</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="o-foot-bottom">
      <p>{logo(16)}<span>{c['legal']}</span></p>
      <a class="o-pill" href="/{o}/models/{SLUG}" hreflang="{c['other_lang']}" lang="{c['other_lang']}">{c['other_name']}</a>
    </div>
  </div>
</footer>
<script src="/assets/models/midjourney.js?v={VER}" defer></script>
</body>
</html>
'''


def page(lang):
    c = copy_zh() if lang == 'zh' else copy_en()
    return (head(lang, c) + nav(lang, c) + hero(lang, c) + flow(c) + features(c) + gallery(lang, c) + pricing(lang, c)
            + uses(c) + why(c) + quickstart(c) + enterprise(c) + faq(c) + final(lang, c) + footer(lang, c))


def finish(lang, s):
    """与 payments.py / trust.py 的 main() 对单页做的事完全一致。"""
    import payments
    import trust
    sec = s.index('id="enterprise"')
    end = s.index('</section>', sec)
    cta = s.rfind('<div class="', sec, end)
    ls = s.rfind(NL, 0, cta) + 1
    s = s[:ls] + payments.pay_row(lang, 'o') + s[ls:]
    s = payments.add_faq(s, lang, 'o-ans')
    sec = s.index('id="enterprise"')
    end = s.index('</section>', sec) + len('</section>')
    while s[end:end + 1] == NL:
        end += 1
    s = s[:end] + trust.section(lang, 'o') + s[end:]
    return trust.add_faq(s, lang, 'o-ans')


def main():
    global LOGO
    LOGO = icon_body()
    for lang in sys.argv[1:] or ['zh', 'en']:
        path = os.path.join(ROOT, lang, 'models', SLUG + '.html')
        io.open(path, 'w', encoding='utf-8', newline=NL).write(finish(lang, page(lang)))
        print('written:', f'{lang}/models/{SLUG}.html')


if __name__ == '__main__':
    main()
