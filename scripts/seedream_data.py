# Seedream 系列专题页的数据：模型、价格、官方参数。被 scripts/seedream_pages.py 引用。
# 价格：AnyAIGC 模型广场最低价（https://anyaigc.ai/pricing?keyword=seedream，2026-10-28 读取，用户确认「显示最低的就行」）。
#   英文页写美元；中文页按模型广场的人民币汇率（/api/status 的 usd_exchange_rate = 6.718）换算，保留 2 位小数。
#   不同分辨率单价不同，页面只写起步价，并注明实时价格以模型广场为准。
# 参数：火山方舟图片生成 API 文档（https://www.volcengine.com/docs/82379/1541523，2026-10-28 读取）、
#   seed.bytedance.com 各型号页、AnyAIGC 文档（Seedream /v1/images/generations）。
# AnyAIGC 上线时间：anyaigc.ai/api/status 公告。
# Seedream 5.5（2026-11-20）：价格来自模型广场详情弹窗（分组 doubao-image-2，按张计费，有分辨率分档和输入图片单价），
#   并发不限由用户确认；参数读自火山方舟文档 VOLC_DOC 与 seed.bytedance.com/zh/seedream5_5。人民币换算沿用同一个 RATE。

DATE = '2026-11-20'
VER = '20261120'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai/reference/v1/images/generations?leaf=g%3A328094105'
VOLC_DOC = 'https://www.volcengine.com/docs/82379/1541523'
RATE = 6.718

# 页面顺序（总览页在前）
SLUGS = ['seedream', 'seedream-5.5', 'seedream-5.0-pro', 'seedream-5.0-lite', 'seedream-4.5', 'seedream-4.0', 'seedream-3.0']
MODEL_SLUGS = SLUGS[1:]

# 模型广场显示的最低价（美元）
USD = {'seedream-5.5': '0.0229', 'seedream-5.0-pro': '0.0441', 'seedream-5.0-lite': '0.0223', 'seedream-4.5': '0.0253',
       'seedream-4.0': '0.0203', 'seedream-3.0': '0.0101'}
CNY = {s: f'{float(v) * RATE:.2f}' for s, v in USD.items()}

# Seedream 5.5 的分档价（美元，原样写，不改写）：按单张输出像素分两档；输入图片（参考图或待拆分的原图）另按张计费
TIERS_55 = [('1K / 1.5K', '0.0229'), ('2K', '0.0402')]
INPUT_55 = '0.00918'
PIXELS_55 = {'1K / 1.5K': '≤ 2,601,123', '2K': '2,601,124 ~ 4,624,220'}


def cny_num(v):
    return f'{float(v) * RATE:.2f}'


def cny_of(v):
    return '¥' + cny_num(v)

MODELS = {
    'seedream-5.5': dict(name='Seedream 5.5', id='doubao-seedream-5-5-261028', unit='张',
                         sizes='1K / 1.5K / 2K', sizes_en='1K / 1.5K / 2K', refs=10, seq=0, online='',
                         official='https://seed.bytedance.com/zh/seedream5_5'),
    'seedream-5.0-pro': dict(name='Seedream 5.0 Pro', id='doubao-seedream-5-0-pro-260628', unit='张',
                             sizes='1K / 1.5K / 2K', sizes_en='1K / 1.5K / 2K', refs=10, seq=0, online='2026-08-03',
                             official='https://seed.bytedance.com/zh/seedream5_0_pro'),
    'seedream-5.0-lite': dict(name='Seedream 5.0 lite', id='doubao-seedream-5-0-260128', unit='张',
                              sizes='2K / 3K / 4K', sizes_en='2K / 3K / 4K', refs=14, seq=15, online='2026-02-26',
                              official='https://seed.bytedance.com/zh/seedream5_0_lite'),
    'seedream-4.5': dict(name='Seedream 4.5', id='doubao-seedream-4-5-251128', unit='张',
                         sizes='2K / 4K', sizes_en='2K / 4K', refs=14, seq=15, online='2025-12-03',
                         official='https://seed.bytedance.com/zh/seedream4_5'),
    'seedream-4.0': dict(name='Seedream 4.0', id='doubao-seedream-4-0-250828', unit='张',
                         sizes='1K / 2K / 4K', sizes_en='1K / 2K / 4K', refs=14, seq=15, online='2025-09-09',
                         official='https://seed.bytedance.com/zh/seedream4_0'),
    'seedream-3.0': dict(name='Seedream 3.0', id='doubao-seedream-3-0-t2i-250415', unit='次',
                         sizes='像素尺寸，如 1024x1024', sizes_en='Pixel sizes, e.g. 1024x1024', refs=0, seq=0, online='',
                         official='https://seed.bytedance.com/en/blog/seedream-3-0-text-to-image-model-technical-report-released'),
}


def cny(slug):
    return '¥' + CNY[slug]


def usd(slug):
    return '$' + USD[slug]
