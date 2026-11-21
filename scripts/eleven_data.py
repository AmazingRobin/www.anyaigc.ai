# ElevenLabs（Eleven）系列专题页的数据：模型、价格、官方参数。被 eleven_pages.py、eleven_register.py、og_eleven.py 引用。
# AnyAIGC 价格（美元 / 万字符）：模型广场 https://anyaigc.ai/pricing?provider=ElevenLabs 点开模型详情弹窗「分组价格」（2026-11-13 读取），
#   与 /api/pricing 的 model_ratio × 分组倍率 × 2 一致。7 款模型端点都是 POST /v1/audio/speech（接口文档：docs.anyaigc.ai 创建语音）。
# 官方价（美元 / 千字符）：https://elevenlabs.io/pricing/api 的 Text to Speech API 表（2026-11-13 读取，所有套餐档位同价）。
#   AnyAIGC 价 ÷ 官方价 = 0.81，7 款全部一致，所以写「约官方 8.1 折」（英文 19% off list price），下面用 assert 锁定。
# 官方参数：https://elevenlabs.io/docs/overview/models（语言数、单次字符上限、延迟）、https://elevenlabs.io/zh/v4（v4 / v4 Turbo 介绍）。
# 并发：用户确认无限制。接口请求体字段：model、input、voice、response_format、speed（以接口文档为准）。
#
# 2026-11-20 新增 2 个语音转文字（STT）型号 eleven-scribe-v3 / eleven-scribe-v2（请求体 model 为 scribe_v3 / scribe_v2）：
#   模型广场（分组 Eleven-1，端点 POST /v1/audio/transcriptions，类型 Speech to text）按秒计费 $0.0000450 / 秒，两款同价。
#   官方价：https://elevenlabs.io/pricing/api 的 Speech to Text API 一栏，Scribe v3 / Scribe v2 / Scribe v2 Medical 都是 $0.20 / 小时（所有套餐档位同价，2026-11-20 读取）。
#   $0.0000450 × 3600 = $0.162 / 小时，÷ 官方 $0.20 = 0.81，与 TTS 同为约官方 8.1 折，下面用 assert 锁定。
#   接口文档（最接近的）：docs.anyaigc.ai「音频转文字 gpt-4o-transcribe」，POST /v1/audio/transcriptions，multipart/form-data：file、model、language、prompt、response_format、temperature；200 返回 {"text": "..."}。
#   官方参数：https://elevenlabs.io/docs/overview/models（Scribe 型号说明）、https://elevenlabs.io/docs/overview/capabilities/speech-to-text（语言、文件上限、功能）、https://elevenlabs.io/docs/changelog（v3 发布说明）。
from decimal import Decimal

DATE = '2026-11-20'
VER = '20261120'
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
MARKET = PRICING + '?provider=ElevenLabs'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOCS = 'https://docs.anyaigc.ai'
DOCS_SPEECH = 'https://docs.anyaigc.ai/reference/v1/audio/speech?leaf=232421913'
OFFICIAL_MODELS = 'https://elevenlabs.io/docs/overview/models'
OFFICIAL_PRICING = 'https://elevenlabs.io/pricing/api'
DOCS_TRANSCRIBE = 'https://docs.anyaigc.ai/reference/v1/audio/transcriptions?leaf=232421914'
OFFICIAL_STT = 'https://elevenlabs.io/docs/overview/capabilities/speech-to-text'
OFFICIAL_CHANGELOG = 'https://elevenlabs.io/docs/changelog'

# 页面顺序也是专题首页卡片顺序：先 7 款语音合成（TTS），再 2 款语音转文字（STT）
TTS_SLUGS = ['eleven-v4', 'eleven-v4-turbo', 'eleven-v3', 'eleven-v3-conversational',
             'eleven-multilingual-v2', 'eleven-flash-v2-5', 'eleven-flash-v2']
STT_SLUGS = ['eleven-scribe-v3', 'eleven-scribe-v2']
SLUGS = TTS_SLUGS + STT_SLUGS
MODEL_SLUGS = SLUGS


def is_stt(slug):
    return slug in STT_SLUGS

# AnyAIGC 价格：美元 / 万字符
PRICE = {
    'eleven-v4': '0.6480',
    'eleven-v4-turbo': '0.3240',
    'eleven-v3': '0.6480',
    'eleven-v3-conversational': '0.3240',
    'eleven-multilingual-v2': '0.6480',
    'eleven-flash-v2-5': '0.3240',
    'eleven-flash-v2': '0.3240',
    # 语音转文字：美元 / 秒（模型广场计价单位）
    'eleven-scribe-v3': '0.0000450',
    'eleven-scribe-v2': '0.0000450',
}
# 官方价：美元 / 千字符（elevenlabs.io/pricing/api）
OFFICIAL_1K = {
    'eleven-v4': '0.08',
    'eleven-v4-turbo': '0.04',
    'eleven-v3': '0.08',
    'eleven-v3-conversational': '0.04',
    'eleven-multilingual-v2': '0.08',
    'eleven-flash-v2-5': '0.04',  # 官方价格页 Flash / Turbo 行
    'eleven-flash-v2': '0.04',
}
# 官方价折算成每万字符，用于价格表和成本示例
OFFICIAL = {k: str(Decimal(v) * 10) for k, v in OFFICIAL_1K.items()}
for _k in TTS_SLUGS:
    assert Decimal(PRICE[_k]) / Decimal(OFFICIAL[_k]) == Decimal('0.81'), _k

# 语音转文字：官方价按小时标价（美元 / 小时），AnyAIGC 价按秒标价；两者换算用精确算术，不四舍五入
STT_OFFICIAL_HOUR = '0.20'
STT_HOUR = '0.162'        # = 0.0000450 × 3600，页面上的「每小时」价
STT_MINUTE = '0.0027'     # = 0.0000450 × 60，页面上的「每分钟」价
for _k in STT_SLUGS:
    assert Decimal(PRICE[_k]) * 3600 == Decimal(STT_HOUR), _k
    assert Decimal(PRICE[_k]) * 60 == Decimal(STT_MINUTE), _k
    assert Decimal(STT_HOUR) / Decimal(STT_OFFICIAL_HOUR) == Decimal('0.81'), _k
    assert Decimal(PRICE[_k]) * 600 == Decimal('0.027'), _k    # 10 分钟播客
    assert Decimal(PRICE[_k]) * 1800 == Decimal('0.081'), _k   # 30 分钟访谈

# id 是请求体里的 model 字段（区分大小写）。langs / limit / latency 来自 ElevenLabs 官方文档 docs/overview/models（延迟是官方标注的中位推理延迟，不含网络和应用延迟；
# 官方价格页对 Flash 和 v3 Conversational 的延迟数字与文档不一致，这里一律取文档）。没有标注的写空串；langs='en' 表示官方文档只列了英语
MODELS = {
    'eleven-v4': dict(id='eleven_v4', name='Eleven v4', short='v4', langs='90+', limit='10,000', latency=''),
    'eleven-v4-turbo': dict(id='eleven_v4_turbo', name='Eleven v4 Turbo', short='v4 Turbo', langs='90+', limit='', latency='~100ms'),
    'eleven-v3': dict(id='eleven_v3', name='Eleven v3', short='v3', langs='70+', limit='5,000', latency=''),
    'eleven-v3-conversational': dict(id='eleven_v3_conversational', name='Eleven v3 Conversational', short='v3 Conversational', langs='70+', limit='', latency='~165ms'),
    'eleven-multilingual-v2': dict(id='eleven_multilingual_v2', name='Eleven Multilingual v2', short='Multilingual v2', langs='29', limit='10,000', latency=''),
    'eleven-flash-v2-5': dict(id='eleven_flash_v2_5', name='Eleven Flash v2.5', short='Flash v2.5', langs='32', limit='40,000', latency='~100ms'),
    'eleven-flash-v2': dict(id='eleven_flash_v2', name='Eleven Flash v2', short='Flash v2', langs='en', limit='30,000', latency='~135ms'),
    # 语音转文字：langs 来自 docs/overview/models 的 Scribe 条目（90+ languages）；单文件上限（5 GB、15 小时）来自 speech-to-text 能力页，不放进这里
    'eleven-scribe-v3': dict(id='scribe_v3', name='Eleven Scribe v3', short='Scribe v3', langs='90+', limit='', latency='', kind='stt'),
    'eleven-scribe-v2': dict(id='scribe_v2', name='Eleven Scribe v2', short='Scribe v2', langs='90+', limit='', latency='', kind='stt'),
}

# 接口文档请求示例里的 voice_id（docs.anyaigc.ai 创建语音 → ElevenLabs 语音合成），请求体 voice 字段填 ElevenLabs 的 voice_id；不存在或不可用时接口返回 400。音色名没有核实，页面不写
VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb'
