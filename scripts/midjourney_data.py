# Midjourney 专题页共用数据：价格、模型、素材。被 midjourney_pages.py / midjourney_register.py / og_midjourney.py 引用。
# 价格：AnyAIGC 模型广场 https://anyaigc.ai/pricing?provider=Midjourney（2026-11-11 读取，逐个打开详情弹窗核对），按次计费。
#   /api/pricing：model_price × MJ 分组倍率 0.19845，例如 0.3 × 0.19845 = 0.059535，模型广场显示 $0.0595。
#   人民币按 /api/status 的 usd_exchange_rate = 6.689338 换算，只作参考，计价货币为 USD。
# 接口：docs.anyaigc.ai「Midjourney」目录（2026-11-11 读取）。
# 素材：Midjourney Explore 社区作品（https://www.midjourney.com/explore?tab=top，2026-11-11 Top month），作者见 IMG。
from decimal import Decimal

SLUG = 'midjourney'
DATE = '2026-11-11'
VER = '20261111'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai/reference/mj/submit/imagine?leaf=472893085'
RATE = Decimal('6.689338')
EXPLORE = 'https://www.midjourney.com/explore?tab=top'

# 模型名 -> (USD 单价字符串, 接口路径)
MODELS = {
    'mj_imagine': ('0.0595', '/mj/submit/imagine'),
    'mj_blend': ('0.0595', '/mj/submit/blend'),
    'mj_describe': ('0.0298', '/mj/submit/describe'),
    'mj_upscale': ('0.0298', '/mj/submit/action'),
    'mj_variation': ('0.0595', '/mj/submit/action'),
    'mj_high_variation': ('0.0595', '/mj/submit/action'),
    'mj_low_variation': ('0.0595', '/mj/submit/action'),
    'mj_reroll': ('0.0595', '/mj/submit/action'),
    'mj_zoom': ('0.0595', '/mj/submit/action'),
    'mj_pan': ('0.0595', '/mj/submit/action'),
    'mj_custom_zoom': ('0', '/mj/submit/action'),
    'mj_inpaint': ('0', '/mj/submit/action'),
    'mj_modal': ('0.0595', '/mj/submit/modal'),
    'mj_upload': ('0.000595', '/mj/submit/upload-discord-images'),
}
assert len(MODELS) == 14


def usd(m):
    return MODELS[m][0]


def cny(v, places='0.01'):
    return str((Decimal(v) * RATE).quantize(Decimal(places)))


def add(*ms):
    return str(sum(Decimal(usd(m)) for m in ms))


# 成本示例（写进页面，不用 JS 算）
assert add('mj_imagine', 'mj_upscale') == '0.0893'
assert str(Decimal('0.0893') * 100) == '8.9300'
assert str(Decimal(usd('mj_describe')) * 10) == '0.2980'
assert cny(usd('mj_imagine')) == '0.40' and cny(usd('mj_upscale')) == '0.20'

# 素材：文件名 -> (宽, 高, Explore 作者)
IMG = {
    'cave-sea': (640, 1143, 'doow'), 'portrait-35mm': (640, 1143, 'u3761941744'), 'collage-surreal': (640, 904, 'mamechiyo.'),
    'stickers': (640, 855, 'u4438155294'), 'duck-sweater': (640, 849, 'u8877563369'), 'goddess-2d': (640, 1143, 'babypinkbat'),
    'wolf-cartoon': (640, 1074, 'cats666000'), 'lowrider': (640, 1143, 'cruel-angel'), 'panther': (640, 1141, 'u6298463395'),
    'rococo': (640, 1141, 'mintflavor'), 'ink-couple': (640, 1141, 'captivate_jbl'), 'picnic-editorial': (640, 1141, 'tianyanfn'),
    'low-angle': (640, 849, 'u1849682178'), 'passion-fruit': (640, 960, 'Dishwasher Lasagna'), 'vhs-anime': (640, 640, 'u3813859956'),
    'italian-wind': (640, 849, 'annasark_2022'), 'ink-hunter': (640, 1141, '绥吉'), 'steps-fashion': (640, 960, 'YER'),
    'monet-cats': (640, 1141, 'sleepyvava'), 'night-crossing': (640, 1141, 'u3591497815'), 'chibi': (640, 1141, 'yuki0903'),
    'handstand': (640, 1143, 'u1985311791'), 'clipart': (640, 960, 'jedijappstar'),
}
VID = {'graphic-figure': (464, 832, 'reality111'), 'fish': (720, 544, 'earnestb')}
# 首屏三列滚动墙
WALL = [['cave-sea', 'duck-sweater', 'panther', 'vhs-anime', 'rococo'],
        ['portrait-35mm', 'passion-fruit', 'ink-couple', 'stickers', 'monet-cats'],
        ['goddess-2d', 'wolf-cartoon', 'picnic-editorial', 'collage-surreal', 'night-crossing']]
