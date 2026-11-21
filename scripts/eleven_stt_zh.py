# ElevenLabs（Eleven）系列「语音转文字（STT）」专题页中文文案：eleven-scribe-v3、eleven-scribe-v2。由 eleven_copy_zh.build() 分发调用，返回结构和 TTS 页相同。
# 价格来自 eleven_data.PRICE（模型广场详情弹窗，按秒计费，两款同价），官方价 $0.20 / 小时来自 elevenlabs.io/pricing/api 的 Speech to Text API 一栏（2026-11-20 读取）。
# 官方能力来自 elevenlabs.io/docs/overview/models 与 docs/overview/capabilities/speech-to-text，v3 发布信息来自 docs/changelog。
# 接口文档（音频转文字 gpt-4o-transcribe）只有 file、model、language、prompt、response_format、temperature 六个请求字段：词级时间戳、说话人分离、关键词提示、
# 多声道这些官方能力在 AnyAIGC 接口上能否使用文档没写，页面一律标明「ElevenLabs 官方」并提示实测，交付时请用户确认。
from decimal import Decimal

from eleven_data import (PRICE, MODELS, REG, MARKET, SUPPORT, DOCS_TRANSCRIBE, OFFICIAL_MODELS, OFFICIAL_PRICING, OFFICIAL_STT,
                         OFFICIAL_CHANGELOG, STT_OFFICIAL_HOUR, STT_HOUR, STT_MINUTE)
from eleven_layout import money, stt_cost
import eleven_code as code

DEAL = '约官方 8.1 折'
UNIT_SEC = '/ 秒'


def p(slug):
    return f'${PRICE[slug]}'


def link(slug):
    return f'<a href="/zh/models/{slug}">{MODELS[slug]["name"]}</a>'


def off_text(seconds):
    """官方价（$0.20 / 小时）折算：能精确表示就原样写，除不尽时写「约」并保留 4 位小数"""
    d = Decimal(STT_OFFICIAL_HOUR) * Decimal(seconds) / Decimal(3600)
    q = d.quantize(Decimal('0.0001'))
    return money(d) if d == q else '约 ' + money(q)


M = {
    'eleven-scribe-v3': dict(
        sell='高精度录音转写', lead='ElevenLabs 录音文件转写模型，90+ 种语言，适合会议纪要、字幕和访谈整理',
        tag='ElevenLabs 面向录音文件的语音转文字模型：官方称是其最准确的录音识别模型，覆盖 90+ 种语言。',
        about=['Eleven Scribe v3 是 ElevenLabs 面向录音文件的语音转文字（STT）模型。官方模型文档称它是「最准确的录音语音识别模型」，覆盖 90+ 种语言；ElevenLabs 更新日志显示 Scribe v3 于 2026 年 11 月 9 日发布，并称它在 FLEURS 基准的 102 种语言上，词错误比 Scribe v2 少 27%。模型广场的说明是「同价同接口，准确率与说话人分离明显提升」。',
               '官方文档列出的能力包括：词级时间戳、最多 32 位说话人的说话人分离、最多 1,000 个关键词提示（keyterm prompting）、笑声和掌声这类音频事件标注、实体检测。官方能力页写明单个文件最大 5 GB、最长 15 小时，多声道最多 5 个声道。以上是 ElevenLabs 官方文档列出的能力。',
               '在 AnyAIGC 上，<code>scribe_v3</code> 走 <code>POST /v1/audio/transcriptions</code>，用 multipart/form-data 上传音频，按音频秒数计费，并发不限，一个 Bearer Key 即可调用，不需要单独注册 ElevenLabs 账号。'],
        feats=[('90+ 种语言', '官方文档列出 90+ 种语言，普通话和粤语都在官方语言列表里，覆盖常见的出海语种。'),
               ('词级时间戳', '官方称 v3 能返回词级时间戳，可用于字幕对齐和按词定位。'),
               ('说话人分离', '官方称 v3 支持最多 32 位说话人的说话人分离，适合多人会议和访谈录音。'),
               ('关键词提示与音频事件', '官方称 v3 支持最多 1,000 个关键词提示，用来纠正专有名词和产品名，并能标注笑声、掌声等非语音事件。')],
        uses=[('voice-conversational.webp', '01 · 会议', '会议纪要与录音整理', '把会议录音转成文字稿，再交给大模型提炼要点和待办。官方称 v3 能区分多位说话人。'),
              ('voice-entertainment.webp', '02 · 字幕', '视频字幕与播客文稿', '视频和播客里的口语内容转成文字，作为字幕和文稿的初稿，再人工校对。'),
              ('voice-ads.webp', '03 · 质检', '客服录音质检', '通话录音转写后做关键词检索和服务质量抽检，按音频时长计费，批量处理成本可算。'),
              ('voice-narration.webp', '04 · 访谈', '访谈与采访整理', '采访、调研录音转成文字，方便检索、引用和归档。')]),
    'eleven-scribe-v2': dict(
        sell='录音转写', lead='ElevenLabs 上一代录音转写模型，90+ 种语言，适合会议纪要和字幕',
        tag='ElevenLabs 上一代主力语音转文字模型：90+ 种语言，官方文档仍列为可用，已由 Scribe v3 接替。',
        about=['Eleven Scribe v2 是 ElevenLabs 的语音转文字（STT）模型。官方模型文档称它是「上一代最先进的语音识别模型」，已由 <code>scribe_v3</code> 接替，针对 90+ 种语言的准确转写设计，并且仍然可用，不在官方的停用模型列表里。模型广场的说明是「上一代主力版本，支持 90+ 语言、词级时间戳、说话人分离、关键词提示与多声道分轨」。',
               '官方文档列出的 v2 能力包括：词级时间戳、说话人分离、动态音频标注、关键词提示、实体检测。官方能力页写明单个文件最大 5 GB、最长 15 小时，多声道最多 5 个声道。这些是 ElevenLabs 官方文档列出的能力。',
               '在 AnyAIGC 上，<code>scribe_v2</code> 走 <code>POST /v1/audio/transcriptions</code>，按音频秒数计费，价格和 ' + '<a href="/zh/models/eleven-scribe-v3">Eleven Scribe v3</a> 相同，并发不限。新项目可以先用同一段录音分别转写，再决定用哪个版本。'],
        feats=[('90+ 种语言', '官方文档列出 90+ 种语言，普通话和粤语都在官方语言列表里。'),
               ('词级时间戳', '官方称 v2 能返回词级时间戳，可用于字幕对齐。'),
               ('说话人分离', '官方文档把说话人分离列为 v2 的能力，适合多人会议和访谈。模型广场还提到多声道分轨，可以把不同声道的说话人分开。'),
               ('关键词提示', '官方文档把关键词提示列为 v2 的能力，可以提示专有名词和行业术语，减少误识别。')],
        uses=[('voice-conversational.webp', '01 · 会议', '会议纪要与录音整理', '会议录音转成文字稿，再用大模型提炼要点和待办。'),
              ('voice-entertainment.webp', '02 · 字幕', '视频字幕与播客文稿', '口语内容转成文字，作为字幕和文稿的初稿，再人工校对。'),
              ('voice-ads.webp', '03 · 质检', '客服录音质检', '通话录音批量转写后做关键词检索和服务质量抽检。'),
              ('voice-narration.webp', '04 · 访谈', '访谈与采访整理', '采访、调研录音转成文字，方便检索、引用和归档。')]),
}

POS = {'eleven-scribe-v3': '最新录音转写，准确率更高', 'eleven-scribe-v2': '上一代录音转写，仍可用'}
STATUS = {'eleven-scribe-v3': '最新，2026-11-09 发布（官方更新日志）', 'eleven-scribe-v2': '上一代，由 Scribe v3 接替，仍可用'}

QS_NOTE = f'完整说明见 <a href="{DOCS_TRANSCRIBE}" target="_blank" rel="noopener">音频转文字接口文档</a>。调用 Scribe 时，把 model 填成 scribe_v3 或 scribe_v2。'
PRICE_HEAD = [('计费单位', ''), ('模型名', ''), ('ElevenLabs 官方价（USD）', 'o-num'), ('AnyAIGC 单价（USD）', 'o-num o-hl')]
COMPARE_HEAD = [('型号', ''), ('定位', 'el-txt'), ('语言（官方）', 'el-txt'), ('官方状态', 'el-txt'), ('AnyAIGC 每小时', 'o-num o-hl')]


def compare_rows():
    slugs = ['eleven-scribe-v3', 'eleven-scribe-v2']
    return [(f'<a href="/zh/models/{s}">{MODELS[s]["name"]}</a>', '', [POS[s], '90+ 种', STATUS[s], f'${STT_HOUR}'], s) for s in slugs]


COMPARE_NOTE = ('语言数和型号状态来自 <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs 官方模型文档</a>，v3 发布日期来自 <a href="' + OFFICIAL_CHANGELOG
                + '" target="_blank" rel="noopener">官方更新日志</a>。两款模型在 AnyAIGC 上价格相同，每小时价格是每秒价格 × 3600。实时价格以模型广场为准。')


def costs(slug):
    c = lambda sec: money(stt_cost(slug, sec))
    o = lambda sec: f'ElevenLabs 官方同用量 {off_text(sec)}'
    return [('10 分钟播客', '600 秒 × 单价', c(600), o(600)),
            ('1 小时会议录音', '3,600 秒 × 单价', c(3600), o(3600)),
            ('100 小时客服录音', '360,000 秒 × 单价', c(360000), o(360000))]


def billing(slug):
    return [('按音频秒数计费', '按成功转写的音频时长'), ('约官方 8.1 折', f'官方 ${STT_OFFICIAL_HOUR} / 小时'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')]


def price_rows(slug):
    mid = MODELS[slug]['id']
    return [('每秒', '模型广场计价单位', '—', '$' + PRICE[slug], mid, True),
            ('每分钟', '每秒 × 60', '—', '$' + STT_MINUTE, mid, False),
            ('每小时', '每秒 × 3600，与官方价格页对照', '$' + STT_OFFICIAL_HOUR, '$' + STT_HOUR, mid, False)]


def pricing_note():
    return (f'价格单位为美元，按音频时长（秒）计费，表中为模型广场最低价，实时价格以 <a href="{MARKET}">AnyAIGC 模型广场</a> 为准。'
            f'官方价来自 <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">ElevenLabs 价格页</a>的 Speech to Text API 一栏，Scribe v3 和 Scribe v2 都是 ${STT_OFFICIAL_HOUR} / 小时。'
            f'AnyAIGC 每小时 ${STT_HOUR}（每秒 ${PRICE["eleven-scribe-v3"]} × 3600），是官方价的 81%（约 8.1 折）。官方按小时标价，所以每秒、每分钟两行官方价留空。')


def qs_steps(model):
    return ['<strong>注册并充值</strong>：在 <a href="' + REG + '">anyaigc.ai</a> 注册账号，最低 $1 起充，余额对平台所有模型通用。',
            '<strong>创建 API Key</strong>：在控制台创建令牌，复制以 <code>sk-</code> 开头的 Key，存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'<strong>上传录音</strong>：请求 <code>POST https://anyaigc.ai/v1/audio/transcriptions</code>，用 multipart/form-data 提交 <code>file</code>（音频文件）和 <code>model</code>（填 <code>{model}</code>），鉴权用 <code>Authorization: Bearer</code>，返回里的 <code>text</code> 就是转写文字。']


def faq_common(name):
    return [
        ('国内可以直接调用 ' + name + ' API 吗？',
         '可以。AnyAIGC 面向国内网络优化，通常无需额外代理即可调用 <code>https://anyaigc.ai</code>，按美元价格计费，支持微信支付、支付宝、USDT 和信用卡，企业可对公转账并开具增值税发票。'),
        ('AnyAIGC 能开发票吗？支持增值税专票吗？',
         '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
        ('企业可以对公转账和签合同吗？',
         f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
        ('我上传的录音和转写出来的文字会被用于训练吗？',
         '不会。除法律法规要求外，AnyAIGC 不对你的输入输出内容做持久化存储，也不会用于训练模型，请求通过 HTTPS 加密传输，详见 AnyAIGC <a href="/privacy">隐私政策</a>。模型本身的数据政策以 ElevenLabs 官方为准。录音里如果含个人信息，请先确认已获得授权。'),
    ]


def special_faq(slug):
    if slug == 'eleven-scribe-v3':
        return ('Scribe v3 和 Scribe v2 有什么区别？',
                'ElevenLabs 更新日志称 Scribe v3 在 FLEURS 基准的 102 种语言上，词错误比 Scribe v2 少 27%，并说它能更准确地标注说话人。在 AnyAIGC 上两者价格相同、接口相同，只有 model 字段不同。新项目优先试 v3，也可以用同一段录音分别转写后对比。v2 详见 ' + link('eleven-scribe-v2') + '。')
    return ('Scribe v2 还能用吗？和 Scribe v3 怎么选？',
            '能用。官方模型文档称 Scribe v2 是上一代模型，已由 Scribe v3 接替，但仍可用，不在官方的停用模型列表里。两者在 AnyAIGC 上价格相同。已经在用 v2 的项目可以继续用，新项目建议同一段录音分别转写对比后再选，详见 ' + link('eleven-scribe-v3') + '。是否继续提供以模型广场为准。')


def build(slug):
    m = M[slug]
    d = MODELS[slug]
    mid, name = d['id'], d['name']
    s = slug
    price = p(s)
    other = 'eleven-scribe-v2' if s == 'eleven-scribe-v3' else 'eleven-scribe-v3'

    faqs = [
        (f'{name} API 多少钱？',
         f'AnyAIGC 上 <code>{mid}</code> 按音频秒数计费：{price} / 秒，折合 ${STT_MINUTE} / 分钟、${STT_HOUR} / 小时，约为 ElevenLabs 官方价（${STT_OFFICIAL_HOUR} / 小时）的 8.1 折。固定单价，没有订阅和月费，实时价格以模型广场为准。'),
        (f'{name} 的模型 ID 是什么？和 ElevenLabs 是什么关系？',
         f'模型 ID 是 <code>{mid}</code>（区分大小写），和 ElevenLabs 官方的 model_id 一致。AnyAIGC 是独立的 API 服务商，提供 OpenAI 风格的 <code>/v1/audio/transcriptions</code> 调用方式，与 ElevenLabs 没有隶属关系。'),
        (f'{name} 和其他 Eleven 型号怎么选？',
         f'Eleven 系列在 AnyAIGC 上分两类：语音合成（文字转语音）7 款，见 {link("eleven-v4")} 等页面；语音转文字（录音转写）2 款，即 {link("eleven-scribe-v3")} 和 {link("eleven-scribe-v2")}。要把录音变成文字选 Scribe，要把文字变成语音选 v4、Multilingual v2 等合成模型。'),
        (f'怎么调用 {name} API？',
         f'请求 <code>POST https://anyaigc.ai/v1/audio/transcriptions</code>，用 multipart/form-data 提交 <code>file</code>（音频文件）和 <code>model</code>（填 <code>{mid}</code>），鉴权用 <code>Authorization: Bearer</code>。成功时返回 <code>{{"text": "..."}}</code>。完整说明见<a href="{DOCS_TRANSCRIBE}" target="_blank" rel="noopener">接口文档</a>。'),
        (f'{name} 支持哪些音频格式？文件最大多少？',
         '接口文档列出的 file 格式有 flac、mp3、mp4、mpeg、mpga、m4a、ogg、wav、webm。ElevenLabs 官方能力页写明单个文件最大 5 GB、最长 15 小时。'),
        (f'{name} 支持中文吗？支持多少种语言？',
         '支持。官方文档标注 Scribe 支持 90+ 种语言，普通话和粤语在官方语言列表里。具体语种以 <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs 官方文档</a>为准。'),
        special_faq(s),
        ('这里有实时转写（流式）模型吗？',
         '本页只覆盖录音文件转写模型 <code>scribe_v3</code> 和 <code>scribe_v2</code>，走 HTTP 的 <code>/v1/audio/transcriptions</code>，上传完整音频后返回文字。ElevenLabs 官方另有实时转写模型（scribe_v3_live 等），不在本页范围，是否提供以模型广场为准。'),
        ('并发和速率有限制吗？',
         f'AnyAIGC 对 <code>{mid}</code> 不设并发限制，所有用户默认享有，适合批量转写和多任务并行。按音频秒数计费，没有月费和按时间窗口重置的额度。'),
    ]
    faqs += faq_common(name)
    key_q = (f'如何获取 {name} API Key？',
             f'在 <a href="{REG}">anyaigc.ai</a> 注册并充值，进入控制台创建令牌即可。同一个 Key 可以调用平台上 300+ 个模型，不需要单独注册 ElevenLabs 账号。请求体的 <code>model</code> 填 <code>{mid}</code>。')
    faqs.insert(3, key_q)

    sell = m['sell']
    facts = [('模型 ID', mid), ('价格', f'{price} / 秒'), ('语言', '90+ 种语言'), ('并发', '不限'), ('企业', '对公 · 专票')]
    hero_notice = None
    if s == 'eleven-scribe-v2':
        hero_notice = f'ElevenLabs 官方文档把 Scribe v2 称为上一代模型，已由 <a href="/zh/models/eleven-scribe-v3">Scribe v3</a> 接替（AnyAIGC 价格相同）。v2 官方仍可用，在模型广场当前可调用，是否继续提供以 <a href="{MARKET}">模型广场</a> 为准。'

    from eleven_copy_zh import fit_title
    return dict(
        title=fit_title(f'{name} API 价格与接入｜约官方 8.1 折', ' - AnyAIGC'),
        desc=f'{mid} API：{m["lead"]}。{price}/秒（${STT_HOUR}/小时），约官方 8.1 折，并发不限，支持对公转账与增值税专票。',
        og_desc=f'{mid} {price}/秒（${STT_HOUR}/小时），约官方 8.1 折。{m["lead"]}，并发不限，支持对公转账与增值税专票。',
        og_alt=f'AnyAIGC {mid} API：{price}/秒，约官方 8.1 折',
        keywords=f'{mid} API,{mid},{name} API 价格,{name} API 接入,{name} API key,ElevenLabs Scribe API,ElevenLabs API,ElevenLabs 语音转文字,Eleven 语音识别 API,语音转文字 API,录音转文字 API,会议纪要 API,{name} API 企业,{name} API 发票,ElevenLabs API 对公转账,AnyAIGC',
        crumb=f'{name} API', product=f'{name} API（AnyAIGC）', sku=s, category='语音转文字 API',
        product_desc=f'通过 AnyAIGC 调用 ElevenLabs {name}：POST /v1/audio/transcriptions，按音频秒数计费，{price}/秒（${STT_HOUR}/小时，约官方 8.1 折），并发不限。',
        offers=[('每秒', PRICE[s])],
        hero=dict(eyebrow=f'ElevenLabs · {mid}', deal=DEAL,
                  h1=f'Eleven <b>{d["short"]}</b><span class="o-sr"> API</span>',
                  lead=f'{m["tag"]}一个 API Key 调用，按音频秒数计费，价格约为官方的 8.1 折。',
                  sample=None,
                  sub=f'<code>{mid}</code> {price} / 秒（${STT_HOUR} / 小时，ElevenLabs 官方 ${STT_OFFICIAL_HOUR} / 小时），并发不限，支持对公转账与增值税专票。',
                  notice=hero_notice, facts=facts),
        about=dict(kicker='关于模型', h2=f'{name}：{sell}', paras=m['about'],
                   spec=[('模型 ID', mid, '请求体 model 字段，区分大小写'), ('接口', 'Speech to text', 'POST /v1/audio/transcriptions'),
                         ('价格', price, '每秒，约官方 8.1 折'), ('语言', '90+ 种语言', 'ElevenLabs 官方文档'),
                         ('单文件上限', '5 GB / 15 小时', 'ElevenLabs 官方能力页'),
                         ('音频格式', 'mp3、wav、m4a 等', 'AnyAIGC 接口文档：flac、mp3、mp4、mpeg、mpga、m4a、ogg、wav、webm')]),
        features=dict(kicker='能力', h2=f'{name} 能做什么',
                      items=m['feats'] + [('OpenAI 风格接口', '一个 Bearer Key，用 multipart 上传音频到 <code>/v1/audio/transcriptions</code>，传 file 和 model，返回 <code>{"text": "..."}</code>，OpenAI SDK 的 audio.transcriptions 也能直接用。'),
                                          ('并发不限，约官方 8.1 折', f'所有用户默认不限并发；{price} / 秒，折合 ${STT_HOUR} / 小时，官方价为 ${STT_OFFICIAL_HOUR} / 小时。')]),
        pricing=dict(kicker='价格', h2=f'{name} API 价格', lead='按音频时长（秒）计费，固定单价，没有订阅和月费，约为 ElevenLabs 官方价的 8.1 折。',
                     billing_label='计费要点', billing=billing(s), head=PRICE_HEAD, labels=None, rows=price_rows(s),
                     caption=f'{mid} 价格对照（美元）：ElevenLabs 官方价与 AnyAIGC 价', note=pricing_note(),
                     costs_h3='成本示例', costs_lead='按常见用法估算，用上面的单价相乘得出，并和官方价对比。', costs=costs(s)),
        compare=dict(kicker='选型', h2='Scribe v3 和 Scribe v2 怎么选', lead='两款价格相同、接口相同。新项目优先试 Scribe v3，已经在用 v2 的项目可以继续用，也可以用同一段录音分别转写后再决定。',
                     head=COMPARE_HEAD, rows=compare_rows(), caption='Eleven Scribe 语音转文字模型对比，价格为 AnyAIGC 每小时美元', note=COMPARE_NOTE),
        uses=dict(kicker='使用场景', h2=f'{name} 适合做什么', items=m['uses']),
        qs=dict(kicker='快速开始', h2=f'三步接入 {name} API', steps=qs_steps(mid),
                tabs=[('curl', 'cURL', 'POST /v1/audio/transcriptions', code.curl_stt(mid)),
                      ('py', 'Python · requests', 'Python · requests', code.requests_stt(mid)),
                      ('sdk', 'Python · OpenAI SDK', 'Python · openai SDK', code.sdk_stt(mid))],
                callout=f'<strong>参数提示：</strong>模型 ID 区分大小写，写成 <code>{mid}</code>；请求体是 multipart/form-data，<code>file</code> 是音频文件本身（不是文件名）；成功时返回 <code>{{"text": "..."}}</code>。',
                note=QS_NOTE),
        family_h2='Eleven 系列全部型号', family_lead='同一个 API Key 可以调用下面所有 Eleven 模型：语音合成 7 款，语音转文字 2 款，按场景和预算选择。',
        faq_h2=f'{name} API 常见问题', faqs=faqs,
        final=dict(h2=f'用一个 Key 调用 {name}', p=f'注册后创建 API Key，几分钟就能在代码里用上 {mid}，余额对平台 300+ 模型通用。', other=f'{name} API in English'),
        ent_name=name,
    )
