# Nano Banana 系列专题页的数据：模型、价格、官方参数、示例图。被 scripts/nano_banana_pages.py 引用。
# 中文页价格（人民币 / 张）：用户提供（2026-10-25）
# 英文页价格（美元 / 张）：AnyAIGC 模型广场最低价（https://anyaigc.ai/api/pricing，2026-10-25 读取，保留 4 位小数，与 GPT Image 系列一致）
# 官方价与参数：ai.google.dev/gemini-api/docs/pricing、image-generation、models、deprecations（2026-10-25 读取）

DATE = '2026-10-25'
VER = '20261025'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS_21 = 'https://docs.anyaigc.ai/reference/v1/v1beta/models/gemini-nano-banana-2.1%3AgenerateContent?leaf=c%3A1791529101208'
DOCS_GEMINI = 'https://docs.anyaigc.ai/reference/gemini-v1beta/v1beta/models/%7BmodeName%7D%3AgenerateContent?leaf=305486200'
DOCS_CHAT = 'https://docs.anyaigc.ai/reference/v1/chat/completions?leaf=g%3A275101024'
GOOGLE_DOC = {'zh': 'https://ai.google.dev/gemini-api/docs/image-generation?hl=zh-cn',
              'en': 'https://ai.google.dev/gemini-api/docs/image-generation'}
GALLERY_SRC = 'https://deepmind.google/models/gemini-image/'

# 页面顺序（总览页在前）
SLUGS = ['nano-banana', 'nano-banana-2.1', 'nano-banana-2', 'nano-banana-pro']
MODEL_SLUGS = SLUGS[1:]

# 中文页：人民币按张价格（元 / 张），按分辨率分档
CNY = {
    'nano-banana-2.1': [('1K', '0.08'), ('2K', '0.12'), ('4K', '0.28')],
    'nano-banana-2':   [('1K / 2K', '0.10'), ('4K', '0.19')],
    'nano-banana-pro': [('1K / 2K', '0.22'), ('4K', '0.39')],
}
# 英文页：模型广场最低价（美元 / 张，不分档；2K / 4K 实时价格以模型广场为准）
USD = {'nano-banana-2.1': '0.0128', 'nano-banana-2': '0.0164', 'nano-banana-pro': '0.0328'}

# Google 官方 Standard 价（美元 / 张），来自 ai.google.dev 定价页
OFFICIAL = {
    'nano-banana-2.1': {'1K': '0.0336', '2K': '0.0504', '4K': '0.113'},
    'nano-banana-2':   {'1K': '0.067', '2K': '0.101', '4K': '0.151'},
    'nano-banana-pro': {'1K': '0.134', '2K': '0.134', '4K': '0.24'},
}

MODELS = {
    'nano-banana-2.1': dict(name='Nano Banana 2.1', ids=['gemini-nano-banana-2.1'], google='Gemini Nano Banana 2.1',
                            ratios=14, refs=(10, 4, 0), released='2026-10-06'),
    'nano-banana-2':   dict(name='Nano Banana 2', ids=['gemini-3.1-flash-image', 'gemini-3.1-flash-image-preview'], google='Gemini 3.1 Flash Image',
                            ratios=14, refs=(10, 4, 0), released='2026-02-26', ga='2026-05-28'),
    'nano-banana-pro': dict(name='Nano Banana Pro', ids=['gemini-3-pro-image', 'gemini-3-pro-image-preview'], google='Gemini 3 Pro Image',
                            ratios=10, refs=(6, 5, 3), released='2025-11-20', ga='2026-05-28'),
}

RATIOS_14 = ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9', '1:4', '4:1', '1:8', '8:1']
RATIOS_10 = RATIOS_14[:10]
# 官方像素尺寸（ai.google.dev image-generation，Nano Banana 2.1 / 3.1 Flash Image 表）
SIZES = [('1:1', '1024×1024', '2048×2048', '4096×4096'), ('16:9', '1376×768', '2752×1536', '5504×3072'),
         ('9:16', '768×1376', '1536×2752', '3072×5504'), ('4:3', '1200×896', '2400×1792', '4800×3584'),
         ('21:9', '1584×672', '3168×1344', '6336×2688'), ('8:1', '3072×384', '6144×768', '12288×1536')]

# 示例图（Google DeepMind Nano Banana 模型页，由 Nano Banana 系列模型生成）：文件名 -> (宽, 高, 中文标题, 中文说明, 英文标题, 英文说明)
IMG = {
    'can-localization':          (1200, 675, '多语言改字', '把三罐饮料包装上的英文换成韩文，其余保持不变', 'Text localization', 'English on three cans translated into Korean, everything else unchanged'),
    'desert-poster-design':      (1200, 675, '海报设计', '瑞士风运动海报与 70 年代旅行海报', 'Poster design', 'A Swiss-style sports poster and a 1970s travel poster'),
    'earth-layers-infographic':  (1200, 675, '科普信息图', '带标注的地球分层等距剖面图', 'Explainer graphic', "Labeled isometric cutaway of the Earth's layers"),
    'foggy-orange-sedan':        (1200, 900, '电影感场景', '夜晚青色雾气里的复古橙色轿车', 'Cinematic scene', 'A vintage orange sedan in teal night fog'),
    'futuristic-city':           (1200, 675, '概念场景', '黄昏时分俯瞰未来城市与巨型飞船', 'Concept art', 'Starships over a futuristic city at twilight'),
    'golden-hour-portrait':      (1200, 675, '写实人像', '黄金时刻草地里佩戴金色项圈的人像', 'Photoreal portrait', 'A portrait in tall grass at golden hour'),
    'impossible-typography':     (1200, 675, '创意字体', '用不可能图形拼出的 IMPOSSIBLE', 'Creative type', 'IMPOSSIBLE spelled with impossible shapes'),
    'indie-film-posters':        (1200, 675, '街头海报', '洛杉矶街墙上一排独立电影节海报', 'Street posters', 'Indie film fest posters on a Los Angeles wall'),
    'multi-character-composite': (1200, 675, '多图合成', '把 14 张角色参考图合成到同一张沙发场景', 'Multi-image compositing', '14 character references combined into one sofa scene'),
    'neon-portrait':             (1200, 675, '霓虹人像', '红青霓虹灯下的夜街特写', 'Neon portrait', 'A close-up lit by red and cyan neon at night'),
    'sketch-to-car':             (1200, 675, '草图转实物', '线稿加纸扇纹理变成立体的折纸汽车', 'Sketch to render', 'A line sketch and a paper texture turned into a 3D car'),
    'solar-infographic':         (1200, 675, '平铺信息图', '手作风格的家用太阳能原理图', 'Flat-lay infographic', 'A DIY-style explainer of home solar power'),
    'spider-macro':              (1200, 675, '微距摄影', '挂满露珠的蛛网上的彩色蜘蛛', 'Macro photo', 'A colorful spider on a dew-covered web'),
    'spinning-red-dress':        (1200, 675, '动态瞬间', '旋转的红色刺绣长裙与动态模糊', 'Motion moment', 'A spinning red embroidered dress with motion blur'),
    'stag-day-night-edit':       (1200, 675, '一句话改图', '“改成白天”：把日落改成白天光线', 'One-line edit', '"Change to daytime" applied to a sunset scene'),
    'woodchuck-text':            (1200, 675, '文字渲染', '用木头拼出整句英文绕口令', 'Text rendering', 'A full tongue twister spelled out in wood'),
}


def cny_min(slug):
    """中文页起步价，如 ¥0.08"""
    return '¥' + CNY[slug][0][1]


def save(a, b):
    """相对官方价节省的百分比（整数）"""
    return round((1 - float(a) / float(b)) * 100)
