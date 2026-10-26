# Kimi 系列专题页的数据：模型、价格、官方参数。被 scripts/kimi_pages.py、kimi_register.py、og_kimi.py 引用。
# AnyAIGC 价格（美元 / 百万 tokens）：模型广场 https://anyaigc.ai/pricing?keyword=kimi 的最低价（2026-10-26 读取）
# 官方价与参数：platform.kimi.ai/docs/pricing/chat、kimi-k3 / kimi-k2-7-code / kimi-k2-6 quickstart、Hugging Face 模型卡（2026-10-26 读取）

DATE = '2026-10-26'
VER = '20261026'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai'
DOCS_CHAT = 'https://docs.anyaigc.ai/reference/v1/chat/completions'
DOCS_CC = 'https://docs.anyaigc.ai/tutorials/plugins-7010249'
OFFICIAL_PRICING = 'https://platform.kimi.ai/docs/pricing/chat'

# 页面顺序（总览页在前）
SLUGS = ['kimi', 'kimi-k3', 'kimi-k2.7-code', 'kimi-k2.6']
MODEL_SLUGS = SLUGS[1:]

# AnyAIGC 价格：(输入, 输出, 缓存命中)
PRICE = {
    'kimi-k3':        ('1.2150', '6.0750', '0.1215'),
    'kimi-k2.7-code': ('0.3847', '1.5980', '0.0770'),
    'kimi-k2.6':      ('0.3847', '1.5980', '0.0651'),
}
# Moonshot 官方价（platform.kimi.ai，美元 / 百万 tokens）：(输入, 输出, 缓存命中)
OFFICIAL = {
    'kimi-k3':        ('3.00', '15.00', '0.30'),
    'kimi-k2.7-code': ('0.95', '4.00', '0.19'),
    'kimi-k2.6':      ('0.95', '4.00', '0.16'),
}

MODELS = {
    'kimi-k3': dict(name='Kimi K3', short='K3', context='1,048,576', ctx_short='1M', params='2.8T', active='16 / 896'),
    'kimi-k2.7-code': dict(name='Kimi K2.7 Code', short='K2.7 Code', context='262,144', ctx_short='256K', params='1T', active='32B'),
    'kimi-k2.6': dict(name='Kimi K2.6', short='K2.6', context='262,144', ctx_short='256K', params='1T', active='32B'),
}

