# DeepSeek 系列专题页的数据：模型、价格、官方参数。被 scripts/deepseek_pages.py、deepseek_copy_*.py 引用。
# AnyAIGC 价格（美元 / 百万 tokens）：模型广场 https://anyaigc.ai/pricing?keyword=deepseek 的最低价（2026-10-30 读取）
# 官方价与参数：api-docs.deepseek.com/quick_start/pricing（美元价，分闲时 / 高峰）、api-docs.deepseek.com/updates、
#   www.deepseek.com/news/deepseek-v4-1-flash、Hugging Face deepseek-ai 模型卡（2026-10-30 读取）

DATE = '2026-10-30'
VER = '20261030'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai'
DOCS_CHAT = 'https://docs.anyaigc.ai/reference/v1/chat/completions'
DOCS_CC = 'https://docs.anyaigc.ai/tutorials/plugins-7010249'
OFFICIAL_PRICING = 'https://api-docs.deepseek.com/zh-cn/quick_start/pricing'
OFFICIAL_UPDATES = 'https://api-docs.deepseek.com/updates/'
NEWS_V41 = 'https://www.deepseek.com/news/deepseek-v4-1-flash/'
HF_V41 = 'https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash'
HF_V4F = 'https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash'
HF_V4P = 'https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro'

# 页面顺序（总览页在前）
SLUGS = ['deepseek', 'deepseek-v4.1-flash', 'deepseek-v4-pro', 'deepseek-v4-flash']
MODEL_SLUGS = SLUGS[1:]

# AnyAIGC 价格：(输入, 输出, 缓存命中)
PRICE = {
    'deepseek-v4.1-flash': ('0.1215', '0.4860', '0.0024'),
    'deepseek-v4-pro':     ('0.5346', '1.6038', '0.0178'),
    'deepseek-v4-flash':   ('0.1215', '0.4860', '0.0024'),
}
# DeepSeek 官方美元价（输入缓存未命中, 输出, 输入缓存命中）：闲时 / 高峰两档，闲时为高峰的一半。
# deepseek-v4-flash 已被官方下线，旧模型名按 deepseek-flash（V4.1 Flash）价格计费。
OFFICIAL = {
    'deepseek-v4.1-flash': {'off': ('0.15', '0.60', '0.003'), 'peak': ('0.30', '1.20', '0.006')},
    'deepseek-v4-pro':     {'off': ('0.66', '1.98', '0.022'), 'peak': ('1.32', '3.96', '0.044')},
    'deepseek-v4-flash':   {'off': ('0.15', '0.60', '0.003'), 'peak': ('0.30', '1.20', '0.006')},
}

MODELS = {
    'deepseek-v4.1-flash': dict(name='DeepSeek V4.1 Flash', short='V4.1 Flash', ctx_short='1M', max_out='384K'),
    'deepseek-v4-pro': dict(name='DeepSeek V4 Pro', short='V4 Pro', ctx_short='1M', max_out='384K'),
    'deepseek-v4-flash': dict(name='DeepSeek V4 Flash', short='V4 Flash', ctx_short='1M', max_out=''),
}
