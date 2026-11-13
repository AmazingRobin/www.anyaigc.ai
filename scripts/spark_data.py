# SparkDesk（讯飞星火）系列专题页的数据：模型、价格、官方参数。被 spark_pages.py、spark_register.py、og_spark.py 引用。
# AnyAIGC 价格（美元 / 百万 tokens）：模型广场 https://anyaigc.ai/pricing?provider=Spark 点开模型详情弹窗「分组价格」的输入 / 补全价格（2026-11-13 读取），
#   与 /api/pricing 的 model_ratio × 分组倍率 × 2 一致。三款模型端点都是 POST /v1/chat/completions（openai 类型）。
# 官方参数：讯飞开放平台 https://www.xfyun.cn/doc/spark/Web.html（Pro / Max 上下文 8,192、最大输出 8,192；Max 套餐 2026-03-10 下线并升级为 Ultra；
#   文档当前版本表不再列出 generalv2）。官方价没有核实到，页面不写官方对比价和折扣。

DATE = '2026-11-13'
VER = '20261113b'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai'
DOCS_CHAT = 'https://docs.anyaigc.ai/reference/v1/chat/completions'
OFFICIAL_DOC = 'https://www.xfyun.cn/doc/spark/Web.html'

SLUGS = ['sparkdesk-v3.5', 'sparkdesk-v3.1', 'sparkdesk-v2.1']
MODEL_SLUGS = SLUGS

# AnyAIGC 价格：(输入, 输出)，美元 / 百万 tokens
PRICE = {
    'sparkdesk-v3.5': ('13.1040', '13.1040'),
    'sparkdesk-v3.1': ('13.1040', '13.1040'),
    'sparkdesk-v2.1': ('8.7360', '8.7360'),
}

# id 是请求体里的 model 字段（区分大小写）；official 是讯飞官方对应的档位
MODELS = {
    'sparkdesk-v3.5': dict(id='SparkDesk-v3.5', name='SparkDesk-v3.5', zh_tier='星火 Max', en_tier='Spark Max', context='8,192', ctx_short='8K', max_out='8,192'),
    'sparkdesk-v3.1': dict(id='SparkDesk-v3.1', name='SparkDesk-v3.1', zh_tier='星火 Pro', en_tier='Spark Pro', context='8,192', ctx_short='8K', max_out='8,192'),
    'sparkdesk-v2.1': dict(id='SparkDesk-v2.1', name='SparkDesk-v2.1', zh_tier='星火 V2.0', en_tier='Spark V2.0', context='', ctx_short='', max_out=''),
}
