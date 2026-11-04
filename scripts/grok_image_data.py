# Grok Image 系列专题页的数据：模型、价格、官方参考、示例图。被 scripts/grok_image_pages.py 等引用。
# 价格：按张计费。2.0 与 Quality 按分辨率（和画质）分档，价格由用户提供（2026-11-04）；grok-imagine-image 为模型广场显示的固定价；
#   中文页按 /api/status 的 usd_exchange_rate = 6.689338 换算成人民币，保留 2 位小数（与 Muse Image 页一致）。
# 接口：docs.anyaigc.ai「Images / Grok」：生成 POST /v1/images/generations（JSON），编辑 POST /v1/images/edits（multipart/form-data）。
# 官方参数与价格：docs.x.ai（models、pricing、images generation、migration/imagine-image-quality-nov-2，2026-11-04 读取）。
# 示例图：xAI《Imagine Image 2.0》发布页 x.ai/news/grok-imagine-image-2（由 Imagine Image 2.0 生成），存放在 assets/models/grok-image/。

DATE = '2026-11-04'
VER = '20261104'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
RATE = 6.689338

DOCS_GEN = 'https://docs.anyaigc.ai/reference/v1/images/generations?leaf=425475208'
DOCS_EDIT = 'https://docs.anyaigc.ai/reference/v1/images/edits?leaf=425481728'
XAI_POST = 'https://x.ai/news/grok-imagine-image-2'
XAI_QUALITY_POST = 'https://x.ai/news/grok-imagine-quality-mode'
XAI_DOC = 'https://docs.x.ai/developers/model-capabilities/images/generation'
XAI_PRICING = 'https://docs.x.ai/developers/pricing'
XAI_MIGRATION = 'https://docs.x.ai/developers/migration/imagine-image-quality-nov-2'

ASSET = 'grok-image'  # /assets/models/grok-image.css / .js，示例图目录 /assets/models/grok-image/
HUB = 'grok-image'    # 系列总览页
SLUGS = ['grok-image', 'grok-imagine-image-2.0', 'grok-imagine-image', 'grok-imagine-image-quality']


def cny(usd):
    """美元单价换算成人民币，保留 2 位小数，如 0.03"""
    return f'{float(usd) * RATE:.2f}'


# 分档价格（USD / 张）：(分辨率, 画质, AnyAIGC 输出图价, xAI 官方输出图价)
# 2.0 与 Quality 的 AnyAIGC 价格由用户提供（2026-11-04）；grok-imagine-image 为模型广场显示的固定价。
# xAI 官方价来自 docs.x.ai/developers/pricing；Quality 已停用，官方价不再公布。
TIERS = {
    'grok-imagine-image-2.0': [('1K', 'Low', '0.0179', '0.04'), ('1.5K', 'Low', '0.0223', '0.05'), ('2K', 'Low', '0.0268', '0.06'),
                               ('1K', 'Medium', '0.0268', '0.06'), ('1.5K', 'Medium', '0.0313', '0.07'), ('2K', 'Medium', '0.0357', '0.08')],
    'grok-imagine-image-quality': [('1K', None, '0.0223', None), ('1.5K', None, '0.0268', None), ('2K', None, '0.0313', None)],
    'grok-imagine-image': [('1K / 2K', None, '0.0119', '0.02')],
}
# 改图时每张输入图的价格（USD / 张）：(AnyAIGC, xAI 官方)。grok-imagine-image 在 AnyAIGC 上只走生成接口，没有输入图计费。
INPUT = {'grok-imagine-image-2.0': ('0.00447', '0.01'), 'grok-imagine-image-quality': ('0.00447', None)}

# 模型：展示名、最低单价（USD / 张，取 TIERS 最低档）、xAI 官方价区间、接口、是否支持 quality 参数
MODELS = {
    'grok-imagine-image-2.0': dict(
        name='Grok Imagine Image 2.0', short='Image 2.0', edit=True, quality=True, official_lo='0.04', official_hi='0.08'),
    'grok-imagine-image': dict(
        name='Grok Imagine Image', short='Image 1.0', edit=False, quality=False,
        # xAI 官方 1K、2K 都是 $0.02 / 张；AnyAIGC 上只走生成接口（模型广场标注 dall-e-3 格式）
        official_lo='0.02', official_hi='0.02', alias='grok-imagine-image-2026-03-02'),
    'grok-imagine-image-quality': dict(
        name='Grok Imagine Image Quality', short='Quality', edit=True, quality=False, legacy=True,
        # xAI 2026-11-02 停用，官方价不再公布；xAI 侧请求由 grok-imagine-image-2.0（quality: low）处理
        official_lo=None, official_hi=None),
}
for _s, _m in MODELS.items():
    _p = [t[2] for t in TIERS[_s]]
    _m['usd'], _m['usd_hi'], _m['tiered'] = min(_p, key=float), max(_p, key=float), len(_p) > 1


def tier(slug, res, q=None):
    """取某一档的 AnyAIGC 输出图价（USD）"""
    return next(t[2] for t in TIERS[slug] if t[0] == res and t[1] == q)

# 宽高比（xAI 文档）：2.0 全部支持；21:9、5:2 为 2.0 在 2026-08-28 新增
RATIOS = ['1:1', '3:4', '4:3', '9:16', '16:9', '2:3', '3:2', '9:19.5', '19.5:9', '9:20', '20:9', '1:2', '2:1', '21:9', '5:2']

# 示例图：文件名 -> (宽, 高, 中文说明, 英文说明)。说明改写自 xAI 发布页的图片 alt 文本。
IMG = {
    'hero-10': (1200, 1200, '超现实旅行海报，帽檐上是一整个世界', 'Surreal "World is so vast" travel poster with a whole world in a hat'),
    'hero-20': (1280, 853, '木桌上叠放的手工织物产品图', 'Product shot of handwoven textiles stacked on a wooden table'),
    'hero-22': (1280, 548, '穿过彩虹色沙丘的斗篷旅人', 'Cloaked figure crossing dunes streaked with iridescent color'),
    'hero-26': (1280, 720, '中国古典水墨：瀑布与长袍人物', 'Classical Chinese ink painting of a waterfall and a robed figure'),
    'hero-31': (1280, 720, '铅笔画马的分步教程页', 'Step-by-step pencil horse drawing tutorial'),
    'hero-32': (853, 1280, '黄昏樱花里的少女漫画页', 'Soft manga page of a girl among cherry blossoms at dusk'),
    'hero-33': (1280, 960, '复古像素 RPG 标题画面', 'Retro pixel-art RPG title screen'),
    'hero-34': (1280, 720, '像素风 SpaceX 火箭信息图', 'Pixel-art SpaceX infographic of Falcon 9, Dragon and Starship'),
    'hero-35': (1280, 548, '像素风黄昏山谷与松林', 'Pixel-art twilight valley with pine forests'),
    'hero-36': (1280, 720, '橙黑配色的短跑励志海报', 'Gritty motivational poster of a sprinter in orange and black'),
    'hero-37': (853, 1280, '意大利里维埃拉复古旅行海报', 'Vintage travel poster of an Italian Riviera town'),
    'hero-38': (1280, 720, '从活字到数字字体的字体史信息图', 'Typography history from movable type to digital fonts'),
    'hero-39': (1280, 853, '苏州三日游行程信息图，含日程与贴士', 'Suzhou three-day itinerary infographic with schedule and tips'),
    'hero-40': (1280, 720, '《奥德赛》归乡航线信息图', 'Illustrated Odyssey infographic mapping the voyage home'),
    'hero-41': (1280, 1280, '全部由白色细点构成的半调人像', 'Halftone portrait rendered entirely in fine white dots'),
    'hero-42': (1280, 720, '悬崖神殿上的披风剑客与飞龙', 'Caped swordsman watching a dragon over an Aegean bay'),
    'hero-43': (1280, 720, '烛光舞厅里回眸的电影感特写', 'Cinematic close-up glancing back across a candlelit ballroom'),
    'hero-44': (1280, 834, '星舰试飞摄影画册跨页', 'Photo book spread on a Starship flight test'),
    'hero-45': (1280, 853, '手写《奥德赛》手账，配水彩插画', 'Handwritten Odyssey journal with watercolor illustrations'),
    'hero-47': (1280, 720, '雪中石台上的符文鹿角王冠', 'Rune-carved antler crown on a snowy stone plinth'),
    'hero-48': (1280, 720, '雪峰之上被雾气包围的石堡', 'Fog-wrapped stone keep on a snowy clifftop'),
    'hero-49': (1280, 640, '灰蓝色眼睛的极近特写', 'Extreme close-up of a grey-blue eye'),
    'world-character': (1280, 720, '角色：雪中城堡庭院里的弓箭手', 'Character: an archer in a snowbound castle courtyard'),
    'world-character-2': (1280, 654, '同一角色：暴风雪中呵手取暖', 'Same character in a blizzard, warming her hand'),
    'world-location-1': (1280, 720, '场景：冰封港口里的长船', 'Location: longships frozen into a snowed-in harbor'),
    'world-location-2': (1280, 720, '场景：雪中的营寨与瞭望塔', 'Location: a walled war camp under snowfall'),
    'world-location-3': (1280, 720, '场景：冰川壁上冒着雾的隧道口', 'Location: a fog-breathing tunnel in a glacier wall'),
    'world-prop-1': (1280, 720, '道具：符文小刀与皮囊', 'Prop: a rune-carved knife and leather pouch'),
    'world-prop-2': (1280, 720, '道具：刻有符文的鹿角王冠', 'Prop: an antler crown inscribed with runes'),
    'tpl-background-removal': (853, 1280, '模板：去背景与换背景', 'Template: background removal and change'),
    'tpl-ecommerce-listing': (853, 1280, '模板：电商商品图', 'Template: e-commerce product photos'),
    'tpl-editorial-poster': (853, 1280, '模板：杂志风产品海报', 'Template: editorial product poster'),
    'tpl-icon-maker': (853, 1280, '模板：图标生成', 'Template: icon maker'),
    'tpl-merch-maker': (853, 1280, '模板：周边样机', 'Template: merch maker'),
    'tpl-product-color-change': (852, 1280, '模板：商品换色', 'Template: product color change'),
    'tpl-professional-headshot': (853, 1280, '模板：职业形象照', 'Template: professional headshot'),
    'resize-1x2': (640, 1280, '1:2', '1:2'),
    'resize-9x16': (720, 1280, '9:16', '9:16'),
    'resize-3x4': (864, 1152, '3:4', '3:4'),
    'resize-1x1': (1280, 1280, '1:1', '1:1'),
    'resize-16x9': (1280, 720, '16:9', '16:9'),
    'resize-2x1': (1280, 640, '2:1', '2:1'),
}

# 首屏横向图片带
STRIP = ['hero-41', 'hero-39', 'hero-37', 'hero-43', 'hero-33', 'hero-10', 'hero-26', 'hero-36', 'hero-32', 'hero-44']
