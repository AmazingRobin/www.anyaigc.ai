# GPT Image 系列专题页的数据：模型、价格、官方参考数据、示例图。被 scripts/gpt_image_pages.py 引用。
# 价格来源：AnyAIGC 模型广场（https://anyaigc.ai/pricing?keyword=gpt-image-2，2026-10-25 最低价）
# 官方价与 token 数来源：developers.openai.com 模型页与 image-generation 指南计算器（2026-10-25 读取）

DATE = '2026-10-25'
VER = '20261025'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS_GEN_2 = 'https://docs.anyaigc.ai/reference/v1/images/generations?leaf=c%3A1790764474964'
DOCS_EDIT_2 = 'https://docs.anyaigc.ai/reference/v1/images/edits?leaf=c%3A1790737398263'
DOCS_GEN_25 = 'https://docs.anyaigc.ai/reference/v1/images/generations?leaf=c%3A1790765112018'
DOCS_EDIT_25 = 'https://docs.anyaigc.ai/reference/v1/images/edits?leaf=c%3A1790765179104'
OFFICIAL_POST = {'zh': 'https://openai.com/zh-Hans-CN/index/introducing-chatgpt-images-2-0/',
                 'en': 'https://openai.com/index/introducing-chatgpt-images-2-0/'}
OFFICIAL_GUIDE = 'https://developers.openai.com/api/docs/guides/image-generation'

# 按 token 计费的价格（USD / 每 100 万 tokens）
TOKEN = {
    '2':   dict(text_in='0.3971', img_in='0.6354', out='2.3830', text_cache='0.1588', img_cache='0.2541'),
    '2.5': dict(text_in='2.9700', img_in='4.7520', out='17.8200', text_cache='1.1880', img_cache='1.9010'),
}
# OpenAI 官方价（GPT Image 2 与 2.5 的 token 单价相同）
OFFICIAL = dict(text_in='5.00', img_in='8.00', out='30.00', text_cache='1.25', img_cache='2.00')
# 按次计费（USD / 张，固定价，不随尺寸和质量变化；最低价对应 1K 出图）
CALL = {'2': '0.0119', '2.5': '0.0159'}
# 英文页 2K/4K 按张价格（USD / 张，模型基础价 × 支持 2K/4K 的最低倍率，2026-10-25 读取 /api/pricing）
CALL_4K = {'2': '0.0149', '2.5': '0.0199'}
# 中文页按张计费显示人民币（元 / 张，用户提供）：1K 与 2K/4K 两档
CALL_CNY = {'2': {'1k': '0.08', '4k': '0.1'}, '2.5': {'1k': '0.1', '4k': '0.13'}}


def cny(base, tier='1k'):
    """中文页按张单价，如 ¥0.08"""
    return f'¥{CALL_CNY[base][tier]}'

# OpenAI 官方计算器：GPT Image 2.5（Sunburst 与 Flare 共用）每张图的图片输出 tokens
TOKENS_25 = {
    'low':    {'1024x1024': 196, '1536x1024': 158, '1024x1536': 158, '2048x2048': 397, '2048x1152': 157, '3840x2160': 371},
    'medium': {'1024x1024': 439, '1536x1024': 343, '1024x1536': 343, '2048x2048': 892, '2048x1152': 367, '3840x2160': 865},
    'high':   {'1024x1024': 1756, '1536x1024': 1372, '1024x1536': 1372, '2048x2048': 3568, '2048x1152': 1413, '3840x2160': 3336},
    'xhigh':  {'1024x1024': 3122, '1536x1024': 2459, '1024x1536': 2459, '2048x2048': 6343, '2048x1152': 2511, '3840x2160': 5930},
    'max':    {'1024x1024': 7024, '1536x1024': 5488, '1024x1536': 5488, '2048x2048': 14272, '2048x1152': 5650, '3840x2160': 13342},
}
# OpenAI 官方指南：GPT Image 2 每张图的官方图片输出费用（USD）
OFFICIAL_IMG_2 = {
    'low':    {'1024x1024': '0.006', '1024x1536': '0.005', '1536x1024': '0.005'},
    'medium': {'1024x1024': '0.053', '1024x1536': '0.041', '1536x1024': '0.041'},
    'high':   {'1024x1024': '0.211', '1024x1536': '0.165', '1536x1024': '0.165'},
}

SIZES = ['1024x1024', '1536x1024', '1024x1536', '2048x2048', '2048x1152', '3840x2160', '2160x3840']

# 页面顺序（总览页在前）
# -c 按张计费版不单独做页面，在对应的按 token 型号页价格版块里说明（C_OF）
SLUGS = ['gpt-image', 'gpt-image-2.5-sunburst', 'gpt-image-2.5-flare', 'gpt-image-2']
C_OF = {'gpt-image-2.5-sunburst': ['gpt-image-2.5-sunburst-c'], 'gpt-image-2.5-flare': ['gpt-image-2.5-flare-c'],
        'gpt-image-2': ['gpt-image-2-c']}

# 模型：id、展示名、基座（2 / 2.5）、计费方式（token / call）
MODELS = {
    'gpt-image-2.5-sunburst':   dict(name='GPT Image 2.5 Sunburst', base='2.5', kind='token', snap='gpt-image-2.5-sunburst-2026-09-08'),
    'gpt-image-2.5-flare':      dict(name='GPT Image 2.5 Flare', base='2.5', kind='token', snap='gpt-image-2.5-flare-2026-09-08'),
    'gpt-image-2':              dict(name='GPT Image 2', base='2', kind='token', snap='gpt-image-2-2026-04-21'),
    'gpt-image-2.5-sunburst-c': dict(name='GPT Image 2.5 Sunburst-C', base='2.5', kind='call', of='gpt-image-2.5-sunburst'),
    'gpt-image-2.5-flare-c':    dict(name='GPT Image 2.5 Flare-C', base='2.5', kind='call', of='gpt-image-2.5-flare'),
    'gpt-image-2-c':            dict(name='GPT Image 2-C', base='2', kind='call', of='gpt-image-2'),
}

# 示例图（OpenAI《ChatGPT 图像 2.0 现已上线》发布页，由 ChatGPT 图像 2.0 生成）：文件名 -> (宽, 高, 中文标题, 中文说明, 英文标题, 英文说明)
IMG = {
    'academic-poster':      (1200, 844, '学术海报', '把 GPT-1 论文重排成会议海报', 'Academic poster', 'The GPT-1 paper redesigned as a conference poster'),
    'aliens-cafe':          (1200, 900, '写实场景', '街边咖啡馆里喝饮料的两个外星人', 'Photoreal scene', 'Two aliens having drinks at a street cafe'),
    'art-deco-bookmark':    (800, 2259, '印刷物料', '带出血线和安全边距的装饰艺术风书签', 'Print-ready artwork', 'Art Deco bookmark with bleed and safe margins'),
    'candid-coast':         (1200, 800, '人像摄影', '海岸公路观景台上回头的瞬间', 'Candid portrait', 'A glance back at a coastal lookout'),
    'candid-flash':         (1200, 808, '闪光灯抓拍', '夜晚街头的胶片感合影', 'Flash snapshot', 'Friends on a city street at night, shot on flash'),
    'cantor-infographic':   (800, 1129, '教学信息图', '康托尔对角线证明的图解', 'Explainer graphic', "Cantor's diagonal argument, explained visually"),
    'character-sheet':      (800, 1000, '角色设定', '动漫角色的多角度设定页', 'Character sheet', 'Anime character turnaround with poses and notes'),
    'chinese-comic':        (800, 1422, '中文文字', '带中文对白、海报和聊天记录的漫画页', 'Chinese text', 'Comic page with Chinese dialogue, posters and chats'),
    'color-analysis':       (800, 880, '色彩分析', '个人色彩季型分析板', 'Color analysis', 'Personal seasonal color analysis board'),
    'computer-lab':         (1200, 805, '年代感照片', '2000 年代初的学校电脑教室', 'Period photo', 'A school computer lab from the early 2000s'),
    'dunk-keyframes':       (1200, 422, '动作分解', '扣篮动作的逐帧关键帧', 'Motion keyframes', 'A slam dunk broken into keyframes'),
    'high-fashion':         (1200, 796, '时尚大片', '杂志风格的高定礼服人像', 'Fashion editorial', 'Magazine-style couture portraits'),
    'korean-hanok-ad':      (800, 1000, '旅游广告', '韩屋民宿的多栏宣传册', 'Travel campaign', 'Multi-panel brochure for a Korean hanok stay'),
    'matcha-poster':        (1200, 900, '门店海报', '抹茶店开业海报，含品牌与产品图', 'Store launch poster', 'Opening poster for a matcha cafe'),
    'merch-grid':           (800, 1004, '周边样机', 'T 恤、帽子、马克杯等一组周边', 'Merch mockups', 'T-shirt, cap, mug and more in one grid'),
    'miami-comic':          (800, 1200, '连续叙事', '角色前后一致的复古漫画页', 'Consistent story', 'Retro comic page with consistent characters'),
    'moodboard':            (800, 1000, '灵感板', '用食材拼出 GPT IMAGE 的杂志内页', 'Moodboard', 'Magazine page with GPT IMAGE spelled in food'),
    'polyglot-collage':     (800, 997, '拼贴海报', '艺术、科学、地图与建筑的拼贴', 'Collage poster', 'Art, science, maps and architecture in one collage'),
    'rice-macro':           (1200, 675, '微距细节', '粗麻布上堆起的米粒', 'Macro detail', 'A mound of rice grains on burlap'),
    'surreal-portrait':     (800, 1067, '超现实人像', '抱着贵宾犬、头顶黑鸟的模特', 'Surreal portrait', 'A model holding a poodle, a blackbird on her head'),
    'thai-street-panorama': (1200, 419, '宽幅全景', '带泰文招牌的曼谷街道全景', 'Wide panorama', 'Busy Thai street with Thai-script signs'),
    'typography-poster':    (800, 1004, '多语言字体', '日文、阿拉伯文、韩文等多种文字的字体海报', 'Multilingual type', 'Poster mixing Japanese, Arabic, Korean and more'),
    'wolf-magazine':        (800, 1067, '杂志跨页', '北美灰狼科普信息图', 'Magazine spread', 'Wildlife infographic about North American wolves'),
}


def money(x, nd=4):
    """美元金额，保留 nd 位小数"""
    return f'${x:.{nd}f}'


def cost_25(quality, size):
    """GPT Image 2.5 单张图片输出费用：(AnyAIGC, 官方)"""
    t = TOKENS_25[quality][size]
    return t * float(TOKEN['2.5']['out']) / 1e6, t * float(OFFICIAL['out']) / 1e6


def cost_2(quality, size):
    """GPT Image 2 单张图片输出费用：按官方单张费用 × (AnyAIGC 输出单价 / 官方输出单价)"""
    off = float(OFFICIAL_IMG_2[quality][size])
    return off * float(TOKEN['2']['out']) / float(OFFICIAL['out']), off


def save(a, b):
    """相对官方价节省的百分比（整数）"""
    return round((1 - float(a) / float(b)) * 100)
