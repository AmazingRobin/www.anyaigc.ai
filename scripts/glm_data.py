# GLM 系列专题页的数据：模型、价格、官方参数。被 scripts/glm_pages.py、glm_register.py、og_glm.py 引用。
# AnyAIGC 价格（美元 / 百万 tokens）：模型广场 https://anyaigc.ai/pricing?keyword=glm 的最低价（2026-10-30 读取）
# 官方价与参数：docs.z.ai/guides/overview/pricing（美元价）、docs.z.ai/guides/llm/glm-5.3、glm-5.2、vlm/glm-5.3-flash、
#   z.ai/blog/glm-5.3、glm-5.3-flash、glm-5.2，Hugging Face zai-org 模型卡（2026-10-30 读取）

DATE = '2026-10-30'
VER = '20261030'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai'
DOCS_CHAT = 'https://docs.anyaigc.ai/reference/v1/chat/completions'
DOCS_CC = 'https://docs.anyaigc.ai/tutorials/plugins-7010249'
OFFICIAL_PRICING = 'https://docs.z.ai/guides/overview/pricing'

# 页面顺序（总览页在前）
SLUGS = ['glm', 'glm-5.3', 'glm-5.3-flash', 'glm-5.2']
MODEL_SLUGS = SLUGS[1:]

# AnyAIGC 价格：(输入, 输出, 缓存命中)
PRICE = {
    'glm-5.3':       ('0.9450', '2.9700', '0.1758'),
    'glm-5.3-flash': ('0.0607', '0.2025', '0.0122'),
    'glm-5.2':       ('0.9450', '2.9700', '0.2362'),
}
# 智谱官方美元价（docs.z.ai，美元 / 百万 tokens）：(输入, 输出, 缓存命中)
OFFICIAL = {
    'glm-5.3':       ('1.40', '4.40', '0.26'),
    'glm-5.3-flash': ('0.15', '0.50', '0.03'),
    'glm-5.2':       ('1.40', '4.40', '0.26'),
}

MODELS = {
    'glm-5.3': dict(name='GLM-5.3', short='5.3', context='1,048,576', ctx_short='1M', max_out='128K'),
    'glm-5.3-flash': dict(name='GLM-5.3-Flash', short='5.3-Flash', context='1,048,576', ctx_short='1M', max_out='128K'),
    'glm-5.2': dict(name='GLM-5.2', short='5.2', context='1,048,576', ctx_short='1M', max_out='128K'),
}
