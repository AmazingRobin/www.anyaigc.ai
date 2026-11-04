# Grok Video 系列专题页的数据：模型、价格、官方参考、示例视频。被 scripts/grok_video_pages.py 等引用。
# 价格：AnyAIGC 模型广场（https://anyaigc.ai/pricing?provider=Grok+%28xAI%29&category=音视频，2026-11-04 读取，
#   点开模型详情的「分组价格」表），按输出视频秒数计费，按分辨率分档；输入图片按张、输入视频按秒另计。
#   中文页按 /api/status 的 usd_exchange_rate = 6.689338 换算成人民币。
# 接口：docs.anyaigc.ai「Grok」：创建 POST /v1/videos/generations，编辑 POST /v1/videos/edits，查询 GET /v1/videos/{id}。
# 官方参数与价格：docs.x.ai（models、pricing、model-capabilities/video，2026-11-04 读取）。
# 示例视频：xAI 官方 x.ai/api/imagine 与 x.ai/news/grok-imagine-video-1-5（由 Grok Imagine 生成），
#   转码为 960 宽 H.264 存放在 assets/models/grok-video/，封面帧为同名 .webp。

DATE = '2026-11-04'
VER = '20261104'
RATE = 6.689338

DOCS_GEN = 'https://docs.anyaigc.ai/reference/grok/v1/videos/generations?leaf=472718623'
DOCS_EDIT = 'https://docs.anyaigc.ai/reference/grok/v1/videos/edits?leaf=472719019'
DOCS_QUERY = 'https://docs.anyaigc.ai/reference/grok/v1/videos/%7Brequest_id%7D?leaf=472719601'
XAI_API = 'https://x.ai/api/imagine'
XAI_15_POST = 'https://x.ai/news/grok-imagine-video-1-5'
XAI_DOC = 'https://docs.x.ai/developers/model-capabilities/video/overview'
XAI_PRICING = 'https://docs.x.ai/developers/pricing'

HUB = 'grok-video'
SLUGS = ['grok-video', 'grok-imagine-video-1.5-preview', 'grok-imagine-video-1.5-lite', 'grok-imagine-video']
MEDIA = '/assets/models/grok-video'


def cny(usd, nd=2):
    """美元换算成人民币，默认保留 2 位小数"""
    return f'{float(usd) * RATE:.{nd}f}'


# 按秒价格（USD / 秒）：(分辨率, AnyAIGC 输出视频, xAI 官方输出视频)
TIERS = {
    'grok-imagine-video-1.5-preview': [('480p', '0.0476', '0.08'), ('720p', '0.0834', '0.14')],
    'grok-imagine-video-1.5-lite': [('480p', '0.0119', '0.02'), ('720p', '0.0179', '0.03'), ('1080p', '0.0834', '0.14')],
    'grok-imagine-video': [('480p', '0.0298', '0.05'), ('720p', '0.0417', '0.07')],
}
# 输入：图片按张、视频按秒（视频编辑时）。(AnyAIGC, xAI 官方)
INPUT_IMG = {'grok-imagine-video-1.5-preview': ('0.00596', '0.01'), 'grok-imagine-video-1.5-lite': ('0.00596', '0.01'),
             'grok-imagine-video': ('0.00119', '0.002')}
INPUT_VID = {'grok-imagine-video': ('0.00596', '0.01')}

MODELS = {
    'grok-imagine-video-1.5-preview': dict(name='Grok Imagine Video 1.5', res='480p / 720p', modes=('t2v', 'i2v')),
    'grok-imagine-video-1.5-lite': dict(name='Grok Imagine Video 1.5 Lite', res='480p / 720p / 1080p', modes=('t2v', 'i2v')),
    'grok-imagine-video': dict(name='Grok Imagine Video', res='480p / 720p', modes=('t2v', 'i2v', 'edit')),
}
for _s, _m in MODELS.items():
    _p = [t[1] for t in TIERS[_s]]
    _m['usd'], _m['usd_hi'] = min(_p, key=float), max(_p, key=float)


def tier(slug, res):
    """某分辨率的 AnyAIGC 每秒价格（USD）"""
    return next(t[1] for t in TIERS[slug] if t[0] == res)


# 示例视频：文件名 -> (宽, 高, 是否有声音, 中文说明, 英文说明)
VIDS = {
    'property': (960, 540, True, '室内样板间漫游', 'A walkthrough of a bright apartment'),
    'dining': (960, 644, True, '暖光下的橙色饮品特写', 'An orange drink in warm afternoon light'),
    'perfume': (960, 540, False, '月下沙丘，香水广告氛围片', 'Moonlit dunes for a perfume ad'),
    'clothing': (960, 540, False, '果园里的服装广告', 'A clothing ad set in an orchard'),
    'try-on': (960, 644, True, '虚拟试衣：人物换上指定的上衣', 'Virtual try-on with a chosen top'),
    'edit-input': (960, 540, True, '原视频', 'Source video'),
    'edit-a': (960, 540, True, '把卫衣换成豹纹皮草', 'Hoodie swapped for leopard fur'),
    'edit-b': (960, 540, True, '把卫衣换成红色', 'Hoodie recolored red'),
    'restyle-original': (960, 540, True, '原视频：穿过城市的列车', 'Original: a train through the city'),
    'restyle-a': (960, 540, True, '换成动画风格', 'Restyled as animation'),
    'restyle-b': (960, 540, True, '换成方块风格', 'Restyled in blocks'),
    'mockup-3d': (960, 632, True, '3D 模型变成实拍：月面上的建筑', '3D mockup to footage: a building on the Moon'),
    'mockup-moon': (960, 632, True, '原型放到月面，地球挂在天上', 'The prototype on the Moon, Earth in the sky'),
    'mockup-earth': (960, 632, True, '同一原型放进森林', 'The same prototype placed in a forest'),
    'speech-1': (960, 540, True, '镜子前护肤，人物开口说话', 'Skincare at a mirror, with speech'),
    'speech-2': (960, 546, True, '酒店大堂的电影感镜头，带环境声', 'A cinematic hotel lobby with ambient sound'),
}
# 静态图（试衣素材、草图）
STILLS = {'try-on-dress': (960, 960), 'try-on-person': (960, 960), 'sketch': (960, 640)}
