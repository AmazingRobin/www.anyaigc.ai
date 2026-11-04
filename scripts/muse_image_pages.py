# 生成 Muse Image 专题页（中英文各 1 页）：python scripts/muse_image_pages.py
# 每次整页重写，之后需重跑 scripts/payments.py 和 scripts/trust.py 补上支付方式与信任版块（两个脚本重复运行结果不变）。
# 价格：AnyAIGC 模型广场（https://anyaigc.ai/pricing?keyword=muse-image，2026-11-03 读取）显示 $0.00596 / 张，按次计费；
#   中文页按 /api/status 的 usd_exchange_rate = 6.689338 换算，保留 2 位小数。
# 官方参数与价格：Meta Model API 文档 dev.meta.ai/docs/image-generation（2026-11-03 读取），官方 $0.01 / 张。
# 示例图：Meta 官方博客 ai.meta.com/blog/introducing-muse-image-muse-video-msl（由 Muse Image 生成），存放在 assets/models/muse-image/。
import html
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seedream_layout import hl  # noqa: E402  极简代码高亮（字符串 / 注释 / 关键字），与 Seedream 页一致

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
SLUG = 'muse-image'
DATE = '2026-11-03'
VER = '20261103'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
MODEL = 'muse-image'
RATE = 6.689338
USD = '0.00596'
OFFICIAL = '0.01'
CNY = f'{float(USD) * RATE:.2f}'  # 0.04
OFFICIAL_CNY = f'{float(OFFICIAL) * RATE:.2f}'  # 0.07，中文页官方价也按同一汇率换算成人民币，方便对比
META_BLOG = 'https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/'
META_DOC = 'https://dev.meta.ai/docs/image-generation'
NAME = 'Muse Image'
SIBLING = '<li><a class="o-pill" href="/{lang}/models/muse-video">Muse Video API</a></li>\n        '  # 结尾区链到同系列 Muse Video
ASSET = 'muse-image'  # 样式与脚本：/assets/models/<ASSET>.css / .js

# 示例图：文件名 -> (宽, 高)
IMG = {
    'poster-state-tech': (960, 1280), 'fashion-mondrian': (960, 1280), 'matcha-ad': (1280, 1280), 'polaroid-big-sur': (1280, 1280),
    'poster-agra': (960, 1280), 'patches': (1280, 853), 'infographic-moon': (1280, 1280), 'qr-manhwa': (1280, 853),
    'fractals-poster': (1280, 606), 'fog-before': (1280, 853), 'fog-after': (1280, 853), 'room-before': (1280, 952),
    'room-japandi': (1280, 952), 'room-before-after': (1280, 640), 'picnic': (1280, 853), 'cafe-menu': (1280, 853),
    'cafe-front': (1280, 853), 'magazine-gauss': (1280, 1280), 'book-cover': (853, 1280), 'lemon-still': (1280, 853),
    'bedroom-vintage': (1280, 720),
}
STRIP = ['poster-state-tech', 'matcha-ad', 'fashion-mondrian', 'polaroid-big-sur', 'patches', 'poster-agra', 'book-cover', 'lemon-still']


def icon(name):
    raw = io.open(os.path.join(ROOT, 'assets/icons', name + '.svg'), encoding='utf-8').read()
    return re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S).group(1), flags=re.S)


META_COLOR = None  # 运行时读取 assets/icons/meta-color.svg（带渐变 defs，同一页内联多次时给 id 加序号）
META_MONO = None   # assets/icons/meta.svg（单色，深色区域填白）
_n = [0]


def logo_color(size=None, cls=''):
    _n[0] += 1
    body = re.sub(r'lobe-icons-meta-(\d+)-_R_0_', lambda m: f'mt{_n[0]}-{m.group(1)}', META_COLOR)
    s = f' width="{size}" height="{size}"' if size else ''
    c = f' class="{cls}"' if cls else ''
    return f'<svg{c} viewBox="0 0 24 24"{s} aria-hidden="true" focusable="false">{body}</svg>'


def logo_white(size=None, cls=''):
    s = f' width="{size}" height="{size}"' if size else ''
    c = f' class="{cls}"' if cls else ''
    body = re.sub(r'\sfill="[^"]*"', '', META_MONO)
    return f'<svg{c} viewBox="0 0 24 24"{s} fill="#ffffff" fill-rule="evenodd" aria-hidden="true" focusable="false">{body}</svg>'


def img(name, alt, eager=False, cls=''):
    w, h = IMG[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="/assets/models/muse-image/{name}.webp?v={VER}" width="{w}" height="{h}" '
            f'alt="{html.escape(alt, quote=True)}" {load} decoding="async">')


def text(h):
    t = re.sub(r'<[^>]+>', '', h)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


# ---------------- 代码示例 ----------------
PROMPT = {'zh': '一张复古旅行海报，标题“杭州 · 西湖”，水彩风格，留白干净，底部一行小字“EST. 2026”',
          'en': 'A vintage travel poster titled “Kyoto · Arashiyama”, watercolor style, clean margins, small text “EST. 2026” at the bottom'}
CMT = {
    'zh': dict(size='只决定宽高比，实际像素由模型决定', n='一次 1–10 张，按张计费', fmt='webp（默认）/ png / jpeg',
               b64='默认返回 base64', url='response_format 填 url 时返回临时链接', sdk='OpenAI SDK 直接可用，只改 base_url 和 model'),
    'en': dict(size='sets the aspect ratio only; the model picks the pixels', n='1-10 images per request, billed per image',
               fmt='webp (default) / png / jpeg', b64='base64 is returned by default', url='with response_format "url" you get a temporary link',
               sdk='the OpenAI SDK works as is; only base_url and model change'),
}


def code_py(lang):
    c = CMT[lang]
    return f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{MODEL}",
        "prompt": "{PROMPT[lang]}",
        "size": "1024x1536",  # {c['size']}
        "n": 1,  # {c['n']}
        "output_format": "png",  # {c['fmt']}
    }},
    timeout=300,
)
resp.raise_for_status()
for i, item in enumerate(resp.json()["data"], 1):
    if item.get("b64_json"):  # {c['b64']}
        with open(f"muse_{{i}}.png", "wb") as f:
            f.write(base64.b64decode(item["b64_json"]))
        print("saved", f"muse_{{i}}.png")
    else:  # {c['url']}
        print(item["url"])'''


def code_curl(lang):
    return f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{MODEL}",
    "prompt": "{PROMPT[lang]}",
    "size": "1024x1536",
    "n": 1,
    "response_format": "url"
  }}\''''


def code_sdk(lang):
    c = CMT[lang]
    return f'''import base64
import os
from openai import OpenAI

# {c['sdk']}
client = OpenAI(api_key=os.environ["ANYAIGC_API_KEY"], base_url="https://anyaigc.ai/v1")
img = client.images.generate(
    model="{MODEL}",
    prompt="{PROMPT[lang]}",
    size="1536x1024",
    n=2,
)
for i, d in enumerate(img.data, 1):
    with open(f"muse_{{i}}.webp", "wb") as f:
        f.write(base64.b64decode(d.b64_json))'''


# ---------------- 文案 ----------------
def copy_zh():
    p = f'¥{CNY}'
    return dict(
        lang='zh-CN', og='zh_CN', og_alt='en_US', other='en', other_name='English', other_lang='en',
        title=f'Muse Image API 价格与接入｜Meta 生图 {p} / 张 - AnyAIGC',
        desc=f'Muse Image API（muse-image）是 Meta 超级智能实验室的生图模型，按张计费 {p} / 张，会自己联网检索、写代码作图，支持精准改图与多图合成，并发不限，支持对公转账与增值税专票。',
        keywords='Muse Image API,Muse Image API 价格,muse-image,Meta Muse Image,Meta 生图 API,Muse Image 接入,Muse Image API Key,Muse Image API 企业,Muse Image API 发票,AnyAIGC',
        og_desc=f'Meta Muse Image API：{p} / 张，指令遵循、精准改图、多图合成，内置联网检索，并发不限。',
        og_alt_txt='AnyAIGC Muse Image API 价格与接入',
        home='首页', hub='模型专题', market='模型广场', price='价格', ent='企业接入', docs='API 文档', login='登录', signup='免费注册',
        get_key='获取 API Key', see_price='查看价格', skip='跳到主要内容', nav_label='主导航', crumbs='面包屑', facts_label='核心信息',
        home_label='AnyAIGC 首页', strip_label='Muse Image 官方示例图', copy='复制', copied='已复制', code_label='代码示例',
        product='Muse Image API（AnyAIGC）',
        product_desc='通过 AnyAIGC 调用 Meta Muse Image（muse-image）图像生成与编辑模型，按张计费，OpenAI 兼容 /v1/images/generations。',
        category='图像生成 API', currency='CNY', offers=[('Muse Image（每张）', CNY)],
        badge='Featured', kicker='Meta 超级智能实验室 · 2026 年 7 月发布',
        h1='Muse Image API',
        lead=f'Meta 第一款由超级智能实验室开发的生图模型。它会先联网查资料、写代码画图表，再生成并自我修正。在 AnyAIGC 上按张计费 <strong>{p} / 张</strong>，并发不限。',
        facts=[('模型名', f'<code>{MODEL}</code>'), ('单价', f'{p} / 张'), ('一次', '1–10 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
        about_h2='Muse Image 是什么',
        about_ps=[
            'Muse Image 是 Meta 超级智能实验室（Meta Superintelligence Labs）在 2026 年 7 月发布的图像生成模型，和 Muse Spark 同属 Muse 系列。官方的定位是三件事：忠实遵循指令、精准编辑、从多张参考图合成画面。',
            '它和一般的「提示词进、图片出」不同：生成前会按需调用搜索和代码工具，比如查真实的地标、商品和时事，或者先写代码算出准确的图表、二维码，再据此出图；生成过程中还会检查草稿并自我修正。按 Meta 官方博客，Muse Image 在 Arena 的文生图、单图编辑、多图编辑三项人类偏好排名中均位列第 2（2026-07-05 数据）。',
            f'在 AnyAIGC 上，模型名是 <code>{MODEL}</code>，走 OpenAI 兼容的 <code>/v1/images/generations</code>，每张 {p}，比 Meta 官方的 ¥{OFFICIAL_CNY} / 张更低。',
        ],
        spec=[('模型名', f'<code>{MODEL}</code>'), ('接口', '/v1/images/generations'), ('单次张数', '1–10 张（n）'),
              ('尺寸', 'size 决定宽高比'), ('输出格式', 'webp / png / jpeg'), ('内置工具', '联网检索 · 图片检索 · 代码')],
        features_h2='Muse Image 能做什么',
        features=[
            ('img', 'poster-state-tech', '复古橄榄球海报，手写标题与票根小字都清晰可读', '指令遵循与文字排版', '标题、小字、日期和票价都能按提示词准确写进画面，适合海报、封面和包装。'),
            ('pair', ('fog-before', 'fog-after'), '把雾气散开，露出下方山谷', '精准改图', '只改你要求的部分。示例指令：「把雾散开，露出下面美丽的山谷」，车、路牌和构图保持不变。'),
            ('pair', ('room-before', 'room-japandi'), '把客厅改成日式侘寂风', '多轮迭代', '在对话里一轮轮修改，前后保持一致。示例：先把客厅改成 Japandi 风，再把原图里的台灯和柜子放回来。'),
            ('img', 'picnic', '参考两张宠物照片合成的猫狗野餐图', '多图合成', '把多张参考图里的人物、物品、服装、风格和场景组合到一张图里，可以在提示词里穿插图片。'),
            ('img', 'infographic-moon', '月球形成大碰撞假说信息图', '联网检索事实', '先搜索科学资料和参考图，再生成信息图，知识密集或涉及时事的提示词更准确。'),
            ('img', 'qr-manhwa', '韩漫风格场景里一张可扫描的二维码海报', '写代码作图', '训练中学会写代码生成准确的图表和二维码，再把结果画进图里。示例里的二维码指向 meta.ai，可以扫描。'),
        ],
        gallery_h2='Muse Image 官方示例', gallery_lead='以下图片由 Muse Image 生成，来自 Meta 官方博客，说明为官方示例的指令（节选翻译）。',
        gallery=[
            ('room-before-after', '多轮编辑', '「把我的第一张图和最后一张做成前后对比图」'),
            ('cafe-front', '多轮编辑', '「画出这家咖啡馆的门面，从橱窗里能看到那张裱起来的照片」'),
            ('cafe-menu', '多轮编辑', '「设计这家店的纸质菜单，用店名，加一道配猫狗小插画的“野餐特餐”」'),
            ('fractals-poster', '写代码作图', '先用 Python 算出 Julia 集和谢尔宾斯基三角，再排成瑞士风海报'),
            ('magazine-gauss', '自我修正', '杂志版面里的求和公式漏了除号，模型自己发现并改成 S = n(n+1)/2'),
            ('bedroom-vintage', '联网检索', '在二手平台检索复古家具，用搜到的物品重新布置卧室'),
            ('matcha-ad', '文生图', '草莓抹茶拿铁广告，英文与日文小字'),
            ('polaroid-big-sur', '文生图', '老式拍立得，手写「Big Sur – Aug ’83」'),
            ('poster-agra', '文生图', '阿格拉泰姬陵蓝色线描旅行海报'),
            ('fashion-mondrian', '文生图', '蒙德里安色块风格时装大片'),
            ('patches', '文生图', '六枚刺绣徽章，文字清晰'),
            ('book-cover', '文生图', '极简书封《The Salt Tide》'),
        ],
        credit='示例图来自 Meta 官方博客，由 Muse Image 生成，版权归 Meta 所有。', credit_link='查看来源',
        pricing_h2='Muse Image API 价格', pricing_lead=f'固定单价，每张 {p}，不按 token 算。',
        billing=[('按张计费', '固定单价，不按 token 算'), ('产出', '一次 1–10 张，按实际返回张数计'), ('并发不限', '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')],
        table_caption='Muse Image API 价格（人民币）',
        th=('功能', '模型名', '计费方式', 'AnyAIGC 单价', 'Meta 官方价'),
        rows=[('文生图', '按提示词生成'), ('图片编辑 / 多图合成', '带参考图')],
        unit='张', free_note='联网检索、图片检索与代码工具不另收费',
        price_note=f'单价为模型广场显示的价格（${USD} / 张），按 1 美元 ≈ ¥{RATE:.3f} 换算成人民币；Meta 官方价 ${OFFICIAL} / 张，按同一汇率约 ¥{OFFICIAL_CNY} / 张。按成功生成计费，实时价格以<a href="{PRICING}">模型广场</a>为准。',
        costs_h3='成本示例', costs_note='按上表单价直接相加，不含其他费用。',
        costs=[('100 张活动海报', f'100 × {p}', f'¥{100 * float(CNY):.0f}', '一次 1 张'),
               ('1,000 张商品场景图', f'1,000 × {p}', f'¥{1000 * float(CNY):,.0f}', '批量出图'),
               ('一次出 10 张挑选', f'10 × {p}', f'¥{10 * float(CNY):.2f}', 'n = 10')],
        market_btn='在模型广场查看',
        uses_h2='Muse Image API 使用场景',
        uses=[('电商', '商品图与场景图', '上传商品照片换背景、换场景，或把多件商品组合进同一张生活方式图。'),
              ('营销', '海报与广告图', '标题、卖点、价格和小字直接写进画面，适合活动海报、社媒配图和 banner。'),
              ('内容', '信息图与科普图', '模型会先查资料再画，适合时事图解、知识卡片和数据可视化。'),
              ('设计', '方案迭代', '在同一个对话里多轮修改，保留满意的部分，只改需要调整的地方。'),
              ('家居', '空间改造效果图', '拍一张房间照片，换成指定风格，或放进指定的家具。'),
              ('游戏', '角色与分镜', '用参考图锁定角色形象，连续生成动作分镜和表情差分。')],
        why_h2='为什么通过 AnyAIGC 调用',
        why=[('一个 Key，300+ 模型', 'Muse Image、GPT Image、Nano Banana、Seedream 共用一个 API Key 和余额。'),
             ('国内直连', f'接口地址 <code>https://anyaigc.ai</code>，国内网络可直接调用，不需要 Meta 开发者账号。'),
             ('固定价格', f'每张 {p}，低于 Meta 官方价，账单按张可查。'),
             ('并发不限', '所有用户默认不限并发，批量出图不用排队申请。')],
        qs_h2='快速接入 Muse Image API',
        steps=[f'<a href="{REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
               '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
               f'向 <code>POST https://anyaigc.ai/v1/images/generations</code> 发请求（OpenAI 兼容格式），<code>model</code> 填 <code>{MODEL}</code>。'],
        tabs=[('py', 'Python', 'Python · muse-image 文生图', code_py('zh')), ('curl', 'cURL', 'cURL · 返回图片链接', code_curl('zh')),
              ('sdk', 'OpenAI SDK', 'Python · OpenAI SDK 一次 2 张', code_sdk('zh'))],
        qs_note=f'请求头用 <code>Authorization: Bearer &lt;API Key&gt;</code>。返回体是 <code>{{"created": ..., "data": [{{"b64_json": ...}}]}}</code>；<code>response_format</code> 填 <code>url</code> 时返回临时链接，请及时下载。参数说明参考 <a href="{META_DOC}" target="_blank" rel="noopener">Meta 官方文档</a>，调用地址和 Key 以 AnyAIGC 为准。',
        ent_h2='企业接入 Muse Image API',
        ent_lead='电商公司、设计团队和内容平台可以直接走企业流程采购，财务、法务和技术对接都有对应支持。',
        ent_cards=[('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。'),
                   ('对公转账', '公司账户直接付款', '支持企业对公转账充值，无需个人垫付，账目清晰。'),
                   ('签订合同', '满足采购与法务流程', '可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。'),
                   ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。')],
        sales='联系企业客服', trial='先注册试用',
        faq_h2='Muse Image API 常见问题',
        faqs=[
            ('Muse Image API 多少钱？', f'AnyAIGC 上 Muse Image（<code>{MODEL}</code>）每张 {p}，按次计费，不按 token 算；Meta 官方价约 ¥{OFFICIAL_CNY} / 张（${OFFICIAL}）。一次请求生成 n 张就按 n 张计费，按成功生成计费，实时价格以模型广场为准。'),
            ('Muse Image 是什么？', 'Muse Image 是 Meta 超级智能实验室在 2026 年 7 月发布的图像生成与编辑模型。它在生成前会按需联网检索、写代码作图，并在生成过程中自我修正，擅长指令遵循、精准编辑和多图合成。'),
            ('怎么控制尺寸和比例？', '用 <code>size</code> 传 <code>"宽x高"</code>，例如 <code>"1024x1536"</code>。按 Meta 官方文档，这个值只决定宽高比，实际像素由模型自己决定，返回尺寸不会和数字完全一致；宽高比超过 16:1 会报错。不传则用默认比例。'),
            ('一次能生成几张？输出什么格式？', '<code>n</code> 可填 1–10，默认 1，<code>data</code> 里每张图一条。<code>output_format</code> 支持 <code>webp</code>（默认）、<code>png</code>、<code>jpeg</code>；<code>response_format</code> 默认返回 base64，填 <code>url</code> 返回临时链接。'),
            ('能改图和多图合成吗？', '能。Muse Image 用同一个模型做生成和编辑：传入一张图加指令只改指定部分，传入多张图可以把不同图里的元素合成到一个场景。AnyAIGC 模型广场显示 muse-image 同时支持图片编辑接口 <code>/v1/images/edits</code>，字段以 AnyAIGC 接口文档为准。'),
            ('联网检索和写代码要额外付费吗？', f'不用。按 Meta 官方说明，检索和代码工具是模型内置能力，包含在每张图的价格里。在 AnyAIGC 上同样按张计费，每张 {p}，不另外收工具费用。'),
            ('并发有限制吗？国内能直接调用吗？', 'AnyAIGC 对 Muse Image 不设并发限制，所有用户默认享有。接口地址是 <code>https://anyaigc.ai</code>，国内网络可以直接调用，不需要 Meta 开发者账号；同一个 Key 还能调用平台上 300+ 其他模型。'),
            ('AnyAIGC 能开发票吗？支持增值税专票吗？', '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
            ('企业可以对公转账和签合同吗？', f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
            ('生成的图片可以商用吗？', '图片的使用权和内容政策以 Meta 官方条款为准。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用。'),
        ],
        final_h2='现在开始调用 Muse Image', final_p=f'注册即送 200 万 tokens 试用额度，每张 {p}，并发不限。',
        signup_any='免费注册 AnyAIGC', read_docs='阅读 API 文档', more='更多', all_hub='全部模型专题', in_other='Muse Image API in English',
        foot_desc='国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。',
        foot=('产品', '资源', '条款'), foot_links=('模型专题', '模型广场', '控制台', 'API 文档 ↗', 'Meta 官方文档 ↗', '联系我们', '隐私政策', '服务条款'),
        legal='&copy; 2026 AnyAIGC。Muse、Meta 是 Meta Platforms, Inc. 的商标。AnyAIGC 是独立的 API 服务商，与 Meta 无隶属或合作关系。页面示例图片来自 Meta 官方博客，版权归 Meta 所有；模型参数引自 Meta Model API 公开文档。',
    )


def copy_en():
    p = f'${USD}'
    return dict(
        lang='en', og='en_US', og_alt='zh_CN', other='zh', other_name='中文', other_lang='zh-CN',
        title=f'Muse Image API Pricing & Access | {p}/image - AnyAIGC',
        desc=f'Meta Muse Image API (muse-image) at {p} per image: web-grounded generation, precise edits, multi-image composition, bank transfer and invoices.',
        keywords='Muse Image API,Muse Image API pricing,muse-image,Meta Muse Image,Meta image generation API,Muse Image API key,Muse Image API for business,AnyAIGC',
        og_desc=f'Meta Muse Image API at {p} per image: faithful prompts, precise edits, multi-image composition and built-in search, with unlimited concurrency.',
        og_alt_txt='AnyAIGC Muse Image API pricing and access',
        home='Home', hub='Model guides', market='Model catalog', price='Pricing', ent='Enterprise', docs='API docs', login='Log in', signup='Sign up free',
        get_key='Get an API key', see_price='See pricing', skip='Skip to main content', nav_label='Main', crumbs='Breadcrumb', facts_label='Key facts',
        home_label='AnyAIGC home', strip_label='Official Muse Image samples', copy='Copy', copied='Copied', code_label='Code examples',
        product='Muse Image API (AnyAIGC)',
        product_desc='Call Meta Muse Image (muse-image) for image generation and editing through AnyAIGC, billed per image, OpenAI-compatible /v1/images/generations.',
        category='Image generation API', currency='USD', offers=[('Muse Image (per image)', USD)],
        badge='Featured', kicker='Meta Superintelligence Labs · released July 2026',
        h1='Muse Image API',
        lead=f'The first image model from Meta Superintelligence Labs. It searches the web and writes code before it renders, then checks and refines its own draft. On AnyAIGC it costs <strong>{p} per image</strong> with unlimited concurrency.',
        facts=[('Model', f'<code>{MODEL}</code>'), ('Price', f'{p} / image'), ('Per request', '1–10 images'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
        about_h2='What is Muse Image?',
        about_ps=[
            'Muse Image is the image generation model Meta Superintelligence Labs released in July 2026, part of the same Muse family as Muse Spark. Meta positions it around three things: following instructions faithfully, editing with precision, and composing from multiple references.',
            'It is not a straight prompt-to-pixels model. Before it renders, it can search for real landmarks, products and current events, or write code to get charts and QR codes exactly right, and it reviews and fixes its own drafts along the way. According to Meta, Muse Image ranked No. 2 on Arena for text-to-image, single-image editing and multi-image editing as of July 5, 2026.',
            f'On AnyAIGC the model name is <code>{MODEL}</code>. It uses the OpenAI-compatible <code>/v1/images/generations</code> endpoint and costs {p} per image, below Meta\'s list price of ${OFFICIAL}.',
        ],
        spec=[('Model', f'<code>{MODEL}</code>'), ('Endpoint', '/v1/images/generations'), ('Images per request', '1–10 (n)'),
              ('Size', 'size sets the aspect ratio'), ('Output', 'webp / png / jpeg'), ('Built-in tools', 'Web search · image search · code')],
        features_h2='What Muse Image can do',
        features=[
            ('img', 'poster-state-tech', 'Vintage football program cover with legible hand-lettered title and ticket text', 'Faithful prompts and typography', 'Headlines, fine print, dates and prices land in the image as written, which suits posters, covers and packaging.'),
            ('pair', ('fog-before', 'fog-after'), 'Clear the fog to reveal the valley below', 'Precise edits', 'It changes only what you ask for. Prompt: "Edit this to clear up the fog and reveal the beautiful valley below." The car, sign and framing stay put.'),
            ('pair', ('room-before', 'room-japandi'), 'Living room restyled in Japandi', 'Multi-turn refinement', 'Keep editing in one conversation and every turn stays coherent. Restyle a living room in Japandi, then bring the original lamp and cabinet back.'),
            ('img', 'picnic', 'A cat and a dog from two reference photos having a picnic', 'Multi-image composition', 'Combine people, objects, clothing, styles and settings from several reference images, with text and images interleaved in the prompt.'),
            ('img', 'infographic-moon', 'Giant impact hypothesis infographic', 'Web-grounded facts', 'It looks up sources and reference images first, so knowledge-heavy and current-events prompts come out more accurate.'),
            ('img', 'qr-manhwa', 'Manhwa-style scene with a scannable QR code poster', 'Code for precise graphics', 'It learned to write code for accurate plots and QR codes and then draws the result in. The QR code in this sample points to meta.ai and scans.'),
        ],
        gallery_h2='Official Muse Image samples', gallery_lead='These images were generated by Muse Image and come from Meta\'s launch post. Captions summarize the official prompts.',
        gallery=[
            ('room-before-after', 'Multi-turn edit', '"Make a before-after picture of my first image and the last one."'),
            ('cafe-front', 'Multi-turn edit', '"Show the front of the cafe. We should be able to see the framed photo from the window too."'),
            ('cafe-menu', 'Multi-turn edit', '"Design this cafe\'s paper menu with a ‘The Picnic Special’ item and a tiny illustration of the cat and dog."'),
            ('fractals-poster', 'Code', 'Computes a Julia set and a Sierpinski triangle in Python, then lays them out as a Swiss-style poster'),
            ('magazine-gauss', 'Self-refinement', 'Spots a missing division slash in its own magazine layout and corrects it to S = n(n+1)/2'),
            ('bedroom-vintage', 'Search', 'Searches marketplace listings for vintage pieces and restyles a bedroom with them'),
            ('matcha-ad', 'Text-to-image', 'Strawberry matcha latte ad with English and Japanese fine print'),
            ('polaroid-big-sur', 'Text-to-image', 'A worn Polaroid captioned "Big Sur – Aug ’83"'),
            ('poster-agra', 'Text-to-image', 'Blue line-art travel poster of the Taj Mahal'),
            ('fashion-mondrian', 'Text-to-image', 'Mondrian color-block fashion editorial'),
            ('patches', 'Text-to-image', 'Six embroidered patches with crisp lettering'),
            ('book-cover', 'Text-to-image', 'Minimal book cover for "The Salt Tide"'),
        ],
        credit='Sample images come from Meta\'s launch post, were generated by Muse Image, and are copyrighted by Meta.', credit_link='View source',
        pricing_h2='Muse Image API pricing', pricing_lead=f'One flat price: {p} per image, not billed by tokens.',
        billing=[('Per image', 'Flat price, no token math'), ('Output', '1–10 images per request, billed per image returned'), ('Unlimited concurrency', 'On by default for every account'), ('One balance', 'Works across 300+ models')],
        table_caption='Muse Image API pricing (USD)',
        th=('Feature', 'Model', 'Billing', 'AnyAIGC price', 'Meta list price'),
        rows=[('Text-to-image', 'From a prompt'), ('Edit / multi-image', 'With reference images')],
        unit='image', free_note='Web search, image search and code tools are included',
        price_note=f'Prices are in USD as listed in the model catalog. Meta\'s list price is ${OFFICIAL} per image. Billed only for images generated successfully; see the <a href="{PRICING}">model catalog</a> for live pricing.',
        costs_h3='Cost examples', costs_note='Straight multiplication of the price above, nothing else added.',
        costs=[('100 campaign posters', f'100 × {p}', f'${100 * float(USD):.3f}'.rstrip('0'), 'One image per request'),
               ('1,000 product scenes', f'1,000 × {p}', f'${1000 * float(USD):.2f}', 'Batch generation'),
               ('10 options to pick from', f'10 × {p}', f'${10 * float(USD):.4f}'.rstrip('0'), 'n = 10')],
        market_btn='View in the model catalog',
        uses_h2='Muse Image API use cases',
        uses=[('E-commerce', 'Product and lifestyle shots', 'Swap backgrounds and settings for product photos, or combine several products into one lifestyle scene.'),
              ('Marketing', 'Posters and ads', 'Put headlines, selling points, prices and fine print straight into the image for campaigns, social posts and banners.'),
              ('Content', 'Infographics and explainers', 'The model researches before it draws, which suits news explainers, knowledge cards and data graphics.'),
              ('Design', 'Iterating on concepts', 'Refine across turns in one conversation, keeping what works and changing only what needs to move.'),
              ('Interiors', 'Room makeovers', 'Restyle a photo of a room or drop specific furniture into it.'),
              ('Games', 'Characters and storyboards', 'Lock a character with reference images, then generate action frames and expression sheets.')],
        why_h2='Why call it through AnyAIGC',
        why=[('One key, 300+ models', 'Muse Image, GPT Image, Nano Banana and Seedream share one API key and one balance.'),
             ('Works from mainland China', 'The base URL <code>https://anyaigc.ai</code> is reachable from China, with no Meta developer account needed.'),
             ('Flat pricing', f'{p} per image, below Meta\'s list price, with per-image billing in the console.'),
             ('Unlimited concurrency', 'No concurrency cap by default, so batch jobs never wait for a quota request.')],
        qs_h2='Get started with the Muse Image API',
        steps=[f'<a href="{REG}">Sign up for AnyAIGC</a>. New accounts get 2M free tokens, and top-ups start at $1.',
               'Create an API key in the <a href="https://anyaigc.ai/console">console</a> and save it as <code>ANYAIGC_API_KEY</code>.',
               f'Send <code>POST https://anyaigc.ai/v1/images/generations</code> (OpenAI-compatible) with <code>model</code> set to <code>{MODEL}</code>.'],
        tabs=[('py', 'Python', 'Python · muse-image text-to-image', code_py('en')), ('curl', 'cURL', 'cURL · return an image URL', code_curl('en')),
              ('sdk', 'OpenAI SDK', 'Python · OpenAI SDK, 2 images', code_sdk('en'))],
        qs_note=f'Authenticate with <code>Authorization: Bearer &lt;API Key&gt;</code>. The response is <code>{{"created": ..., "data": [{{"b64_json": ...}}]}}</code>; set <code>response_format</code> to <code>url</code> for a temporary link and download it promptly. For parameter details see <a href="{META_DOC}" target="_blank" rel="noopener">Meta\'s documentation</a>; use the AnyAIGC base URL and key.',
        ent_h2='Muse Image API for teams and enterprises',
        ent_lead='E-commerce companies, design teams and content platforms can buy through a standard business process, with support for finance, legal and engineering.',
        ent_cards=[('Invoices', 'Including China VAT invoices', 'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.'),
                   ('Bank transfer', 'Pay from a company account', 'Top up by corporate bank transfer, so nobody has to pay on a personal card and expense it.'),
                   ('Contracts', 'Fits procurement and legal review', 'Sign a service agreement with AnyAIGC to meet your internal purchasing requirements.'),
                   ('Dedicated support', 'Account and technical contacts', 'Work with a dedicated support contact and technical engineer for onboarding, migration and troubleshooting.')],
        sales='Talk to sales', trial='Start with a free account',
        faq_h2='Muse Image API FAQ',
        faqs=[
            ('How much does the Muse Image API cost?', f'On AnyAIGC, Muse Image (<code>{MODEL}</code>) costs {p} per image, billed per request rather than by tokens. Meta\'s list price is ${OFFICIAL} per image. A request for n images is billed for n images, only successful generations are charged, and live pricing is in the model catalog.'),
            ('What is Muse Image?', 'Muse Image is the image generation and editing model Meta Superintelligence Labs released in July 2026. It can search the web and write code before rendering, refines its own drafts, and is built for faithful prompts, precise edits and multi-image composition.'),
            ('How do I control size and aspect ratio?', 'Pass <code>size</code> as <code>"WxH"</code>, for example <code>"1024x1536"</code>. Per Meta\'s docs this sets the aspect ratio only; the model renders at its own resolution, so returned dimensions will not match exactly. Ratios beyond 16:1 return an error, and omitting size uses the default ratio.'),
            ('How many images per request, and in what format?', '<code>n</code> accepts 1 to 10 (default 1), with one <code>data</code> entry per image. <code>output_format</code> is <code>webp</code> (default), <code>png</code> or <code>jpeg</code>. <code>response_format</code> returns base64 by default, or a temporary link with <code>url</code>.'),
            ('Can it edit images and combine several references?', 'Yes. One model handles generation and editing: send an image with an instruction to change only that part, or several images to compose them into one scene. The AnyAIGC model catalog lists muse-image on the image edit endpoint <code>/v1/images/edits</code> as well; check the AnyAIGC API docs for its fields.'),
            ('Do web search and code tools cost extra?', f'No. Meta includes its built-in search and code tools in the per-image price, and AnyAIGC bills the same way: {p} per image with no separate tool charge.'),
            ('Is there a concurrency limit? Does it work from China?', 'AnyAIGC sets no concurrency limit on Muse Image for any account. The base URL is <code>https://anyaigc.ai</code>, reachable from mainland China, with no Meta developer account needed, and the same key works for 300+ other models.'),
            ('Can AnyAIGC issue invoices, including VAT special invoices?', 'Yes. AnyAIGC issues an invoice for every top-up, including Chinese VAT general and special invoices. Send your billing details to support.'),
            ('Can my company pay by bank transfer and sign a contract?', f'Yes. You can top up by corporate bank transfer and sign a service agreement, with a dedicated support and technical contact. <a href="{SUPPORT}">Contact AnyAIGC support</a> to get started.'),
            ('Can I use the images commercially?', 'Usage rights and content policies follow Meta\'s official terms. AnyAIGC only provides API access and places no extra limits on how you use the output.'),
        ],
        final_h2='Start building with Muse Image', final_p=f'2M free tokens to start, {p} per image, unlimited concurrency.',
        signup_any='Sign up for AnyAIGC', read_docs='Read the API docs', more='More', all_hub='All model guides', in_other='Muse Image API 中文版',
        foot_desc='An API gateway for global AI models. One base URL and one API key for 300+ models.',
        foot=('Product', 'Resources', 'Legal'), foot_links=('Model guides', 'Model catalog', 'Console', 'API docs ↗', 'Meta docs ↗', 'Contact us', 'Privacy Policy', 'Terms of Service'),
        legal='&copy; 2026 AnyAIGC. Muse and Meta are trademarks of Meta Platforms, Inc. AnyAIGC is an independent API provider and is not affiliated with Meta. Sample images come from Meta\'s launch post and are copyrighted by Meta; model specs are quoted from Meta Model API public documentation.',
    )


# ---------------- 版块 ----------------
def page_url(lang):
    return f'{SITE}/{lang}/models/{SLUG}'


def head(lang, c):
    me, zh, en = page_url(lang), page_url('zh'), page_url('en')
    og_img = f'{SITE}/assets/og/{SLUG}-{lang}.png'
    crumbs = [(c['home'], f'{SITE}/'), (c['hub'], f'{SITE}/{lang}/models/'), (NAME, me)]
    cur = c['currency']
    graph = [
        {'@type': 'Organization', '@id': f'{SITE}/#org', 'name': 'AnyAIGC', 'url': 'https://anyaigc.ai', 'logo': f'{SITE}/logo.webp'},
        {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'AnyAIGC', 'publisher': {'@id': f'{SITE}/#org'}},
        {'@type': 'WebPage', '@id': f'{me}#webpage', 'url': me, 'name': c['title'], 'description': c['desc'], 'inLanguage': c['lang'],
         'isPartOf': {'@id': f'{SITE}/#website'}, 'breadcrumb': {'@id': f'{me}#breadcrumb'}, 'mainEntity': {'@id': f'{me}#product'}, 'dateModified': DATE},
        {'@type': 'BreadcrumbList', '@id': f'{me}#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]},
        {'@type': 'Product', '@id': f'{me}#product', 'name': c['product'], 'description': c['product_desc'], 'category': c['category'],
         'sku': MODEL, 'image': og_img, 'brand': {'@type': 'Brand', 'name': 'AnyAIGC'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': cur, 'lowPrice': c['offers'][0][1], 'highPrice': c['offers'][0][1],
                    'offerCount': len(c['offers']), 'availability': 'https://schema.org/InStock', 'url': f'{me}#pricing',
                    'offers': [{'@type': 'Offer', 'name': n, 'price': p, 'priceCurrency': cur} for n, p in c['offers']]}},
        {'@type': 'FAQPage', '@id': f'{me}#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}} for q, a in c['faqs']]},
    ]
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    e = lambda s: html.escape(s, quote=True)
    return f'''<!DOCTYPE html>
<html lang="{c['lang']}" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(c['title'])}</title>
<meta name="description" content="{e(c['desc'])}">
<meta name="keywords" content="{e(c['keywords'])}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#ffffff">
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
<link rel="stylesheet" href="/assets/models/{ASSET}.css?v={VER}">
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
        <li class="mi-hide-sm"><a class="o-pill" href="{PRICING}">{c['market']}</a></li>
        <li><a class="o-pill" href="#pricing">{c['price']}</a></li>
        <li><a class="o-pill" href="#enterprise">{c['ent']}</a></li>
        <li class="mi-hide-md"><a class="o-pill" href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{c['docs']}</a></li>
      </ul>
    </nav>
    <ul class="o-nav-right">
      <li><a class="o-pill" href="/{o}/models/{SLUG}" hreflang="{c['other_lang']}" lang="{c['other_lang']}">{c['other_name']}</a></li>
      <li class="mi-hide-sm"><a class="o-pill" href="https://anyaigc.ai/console">{c['login']}</a></li>
      <li><a class="o-btn o-btn-dark mi-nav-cta" href="{REG}">{c['signup']}</a></li>
    </ul>
  </div>
</header>

<main id="main">
'''


def hero(lang, c):
    facts = ''.join(f'<li>{k} <strong>{v}</strong></li>' for k, v in c['facts'])
    items = lambda eager: ''.join(f'<li>{img(n, "" if not eager else c["strip_label"] + " " + str(i + 1), eager=eager and i < 3)}</li>'
                                  for i, n in enumerate(STRIP))
    return f'''  <!-- Hero -->
  <section class="mi-hero" aria-labelledby="hero-title">
    <div class="o-wrap">
      <nav aria-label="{c['crumbs']}">
        <ol class="o-crumbs">
          <li><a href="/">{c['home']}</a></li><li><a href="/{lang}/models/">{c['hub']}</a></li><li aria-current="page">{NAME}</li>
        </ol>
      </nav>
      <p class="mi-badge">{c['badge']}</p>
      <p class="mi-kicker">{logo_color(28)}<span>{c['kicker']}</span></p>
      <h1 class="mi-h1" id="hero-title">{c['h1']}</h1>
      <p class="mi-lead">{c['lead']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{c['get_key']}</a>
        <a class="o-btn o-btn-light" href="#pricing">{c['see_price']}</a>
      </div>
      <ul class="o-facts" aria-label="{c['facts_label']}">{facts}</ul>
    </div>
    <div class="mi-strip" role="region" aria-label="{c['strip_label']}" tabindex="0">
      <div class="mi-track">
        <ul>{items(True)}</ul>
        <ul aria-hidden="true">{items(False)}</ul>
      </div>
    </div>
  </section>

'''


def section(sid, h2, inner, lead='', band=False, col=False):
    cls = 'o-section mi-band' if band else 'o-section'
    wrap = 'o-wrap o-col' if col else 'o-wrap'
    lead_html = f'      <p class="o-lead o-reveal">{lead}</p>{NL}' if lead else ''
    return (f'  <section class="{cls}" id="{sid}" aria-labelledby="{sid}-title">{NL}    <div class="{wrap}">{NL}'
            f'      <h2 class="o-h2 o-reveal" id="{sid}-title">{h2}</h2>{NL}{lead_html}{inner}    </div>{NL}  </section>{NL}{NL}')


def about(c):
    ps = ''.join(f'          <p>{p}</p>{NL}' for p in c['about_ps'])
    spec = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in c['spec'])
    inner = (f'      <div class="mi-about">{NL}        <div class="mi-prose o-reveal">{NL}{ps}        </div>{NL}'
             f'        <dl class="mi-spec o-reveal">{spec}</dl>{NL}      </div>{NL}')
    return section('about', c['about_h2'], inner)


def features(lang, c):
    before, after = ('原图', '修改后') if lang == 'zh' else ('Before', 'After')
    lis = ''
    for kind, src, alt, h, p in c['features']:
        if kind == 'pair':
            art = (f'<div class="mi-feature-img mi-pair"><figure>{img(src[0], alt + "（" + before + "）" if lang == "zh" else alt + " (" + before.lower() + ")")}<figcaption>{before}</figcaption></figure>'
                   f'<figure>{img(src[1], alt + "（" + after + "）" if lang == "zh" else alt + " (" + after.lower() + ")")}<figcaption>{after}</figcaption></figure></div>')
        else:
            art = f'<div class="mi-feature-img">{img(src, alt)}</div>'
        lis += f'        <li class="mi-feature o-reveal">{art}<div class="mi-feature-body"><h3>{h}</h3><p>{p}</p></div></li>{NL}'
    return section('features', c['features_h2'], f'      <ul class="mi-features">{NL}{lis}      </ul>{NL}', band=True)


def gallery(c):
    lis = ''.join(f'        <li class="mi-shot o-reveal"><figure>{img(n, cap)}<figcaption><b>{tag}</b>{html.escape(cap, quote=False)}</figcaption></figure></li>{NL}'
                  for n, tag, cap in c['gallery'])
    inner = (f'      <ul class="mi-gallery">{NL}{lis}      </ul>{NL}'
             f'      <p class="o-note">{c["credit"]} <a href="{META_BLOG}" target="_blank" rel="noopener">{c["credit_link"]}</a></p>{NL}')
    return section('gallery', c['gallery_h2'], inner, c['gallery_lead'])


def pricing(lang, c):
    bill = ''.join(f'<li><strong>{a}</strong>{b}</li>' for a, b in c['billing'])
    th = ''.join(f'<th scope="col"{" class=\"o-num\"" if i >= 3 else ""}>{t}</th>' for i, t in enumerate(c['th']))
    price = f'¥{CNY}' if lang == 'zh' else f'${USD}'
    official = f'¥{OFFICIAL_CNY}' if lang == 'zh' else f'${OFFICIAL}'
    billing = '按张' if lang == 'zh' else 'Per image'
    rows = ''.join(f'            <tr><th scope="row">{a}<small>{b}</small></th><td><code>{MODEL}</code></td><td>{billing}</td>'
                   f'<td class="o-num o-hl">{price} / {c["unit"]}</td><td class="o-num mi-off">{official}</td></tr>{NL}' for a, b in c['rows'])
    free = '免费' if lang == 'zh' else 'Free'
    tools = '内置工具' if lang == 'zh' else 'Built-in tools'
    costs = ''.join(f'''        <li class="o-cost o-reveal">
          <h4>{h}</h4>
          <p class="o-cost-calc">{calc}</p>
          <p class="o-cost-total">{tot}</p>
          <p class="o-cost-off">{off}</p>
        </li>{NL}''' for h, calc, tot, off in c['costs'])
    group = '图像生成' if lang == 'zh' else 'Image generation'
    inner = f'''      <ul class="o-billing o-reveal" aria-label="{c['pricing_h2']}">{bill}</ul>
      <div class="o-table-wrap o-reveal">
        <table class="o-table">
          <caption class="o-sr">{c['table_caption']}</caption>
          <thead><tr>{th}</tr></thead>
          <tbody>
            <tr class="mi-group"><th scope="rowgroup" colspan="5">{group}</th></tr>
{rows}          </tbody>
          <tbody>
            <tr class="mi-group"><th scope="rowgroup" colspan="5">{tools}</th></tr>
            <tr><th scope="row">{c['free_note']}</th><td><code>{MODEL}</code></td><td>—</td><td class="o-num o-hl">{free}</td><td class="o-num">{free}</td></tr>
          </tbody>
        </table>
      </div>
      <p class="o-note">{c['price_note']}</p>
      <h3 class="mi-h3 o-reveal">{c['costs_h3']}</h3>
      <p class="o-note">{c['costs_note']}</p>
      <ul class="o-costs">
{costs}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-dark" href="{REG}">{c['get_key']}</a>
        <a class="o-btn o-btn-light" href="{PRICING}">{c['market_btn']}</a>
      </div>
'''
    return section('pricing', c['pricing_h2'], inner, c['pricing_lead'])


def uses(c):
    lis = ''.join(f'        <li class="o-reveal"><span class="mi-k">{k}</span><h3>{h}</h3><p>{p}</p></li>{NL}' for k, h, p in c['uses'])
    return section('use-cases', c['uses_h2'], f'      <ul class="mi-uses">{NL}{lis}      </ul>{NL}', band=True)


def why(c):
    lis = ''.join(f'        <li class="o-reveal"><h3>{h}</h3><p>{p}</p></li>{NL}' for h, p in c['why'])
    return section('why', c['why_h2'], f'      <ul class="mi-why">{NL}{lis}      </ul>{NL}')


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
    return section('quickstart', c['qs_h2'], inner, band=True)


def enterprise(c):
    cards = ''.join(f'        <li class="o-card o-reveal"><strong>{a}</strong><h3>{b}</h3><p>{d}</p></li>{NL}' for a, b, d in c['ent_cards'])
    return f'''  <section class="o-section" id="enterprise" aria-labelledby="ent-title">
    <div class="o-wrap o-col">
      <h2 class="o-h2 o-reveal" id="ent-title">{c['ent_h2']}</h2>
      <p class="o-lead o-reveal">{c['ent_lead']}</p>
      <ul class="o-cards">
{cards}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-dark" href="{SUPPORT}">{c['sales']}</a>
        <a class="o-btn o-btn-light" href="{REG}">{c['trial']}</a>
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
      <h2 class="o-h2 o-reveal" id="faq-title">{c['faq_h2']}</h2>
      <div class="o-faq">
{items}      </div>
    </div>
  </section>

'''


def final(lang, c):
    o = c['other']
    return f'''  <!-- 结尾 CTA -->
  <section class="o-final" aria-labelledby="final-title">
    <div class="o-wrap">
      {logo_white(52, 'mi-final-logo')}
      <h2 id="final-title">{c['final_h2']}</h2>
      <p>{c['final_p']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{c['signup_any']}</a>
        <a class="o-btn o-btn-light" href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{c['read_docs']}</a>
      </div>
      <ul class="o-related" aria-label="{c['more']}">
        <li><a class="o-pill" href="/{lang}/models/">{c['all_hub']}</a></li>
        {SIBLING.format(lang=lang) if SLUG == 'muse-image' else ''}<li><a class="o-pill" href="{PRICING}">{c['market']}</a></li>
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
            <li><a href="https://docs.anyaigc.ai" target="_blank" rel="noopener">{f[3]}</a></li>
            <li><a href="{META_DOC}" target="_blank" rel="noopener">{f[4]}</a></li>
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
      <p>{logo_white(16)}<span>{c['legal']}</span></p>
      <a class="o-pill" href="/{o}/models/{SLUG}" hreflang="{c['other_lang']}" lang="{c['other_lang']}">{c['other_name']}</a>
    </div>
  </div>
</footer>
<script src="/assets/models/{ASSET}.js?v={VER}" defer></script>
</body>
</html>
'''


def page(lang):
    c = copy_zh() if lang == 'zh' else copy_en()
    _n[0] = 0
    return (head(lang, c) + nav(lang, c) + hero(lang, c) + about(c) + features(lang, c) + gallery(c) + pricing(lang, c)
            + uses(c) + why(c) + quickstart(c) + enterprise(c) + faq(c) + final(lang, c) + footer(lang, c))


def main():
    global META_COLOR, META_MONO
    META_COLOR, META_MONO = icon('meta-color'), icon('meta')
    for lang in sys.argv[1:] or ['zh', 'en']:
        p = os.path.join(ROOT, lang, 'models', SLUG + '.html')
        io.open(p, 'w', encoding='utf-8', newline=NL).write(page(lang))
        print('written:', f'{lang}/models/{SLUG}.html')


if __name__ == '__main__':
    main()
