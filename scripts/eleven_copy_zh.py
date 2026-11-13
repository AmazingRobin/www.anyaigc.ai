# ElevenLabs（Eleven）系列专题页中文文案。被 scripts/eleven_pages.py 引用，7 款型号共用一套结构，build(slug) 返回版式需要的全部内容。
# 价格来自 eleven_data.PRICE（模型广场详情弹窗，2026-11-13），官方价来自 elevenlabs.io/pricing/api，参数来自 elevenlabs.io/docs/overview/models。
# 只写有来源的事实：官方能力一律标注「官方」，AnyAIGC 接口文档没写明的（响应格式、自有克隆音色、流式、字符计数口径）不下结论，交付时请用户确认。
from decimal import Decimal

from eleven_data import PRICE, OFFICIAL, OFFICIAL_1K, MODELS, SLUGS, REG, MARKET, SUPPORT, DOCS_SPEECH, OFFICIAL_MODELS, OFFICIAL_PRICING
from eleven_layout import cost, money, unit_price
import eleven_code as code

DEAL = '约官方 8.1 折'
OFF_NOTE = '约官方 8.1 折'


def p(slug):
    return f'${PRICE[slug]}'


def off(slug):
    return f'${OFFICIAL[slug]}'


def link(slug):
    return f'<a href="/zh/models/{slug}">{MODELS[slug]["name"]}</a>'


# ---------------- 每个型号的差异化内容 ----------------
M = {
    'eleven-v4': dict(
        sell='旗舰语音合成', lead='ElevenLabs 旗舰语音合成模型，情感层次细腻，适合有声书、配音和高质量成品音频',
        tag='ElevenLabs 的旗舰语音合成模型：情感层次细腻，支持内联指令，覆盖 90+ 种语言。',
        sample_line='官网 v4 示例音频（澳洲电台主持人，带笑声和停顿），24 秒，非本页实时生成。',
        about=['Eleven v4 是 ElevenLabs 的旗舰语音合成模型。官方介绍它基于全新架构，像配音演员一样理解脚本：知道谁在说话、前面发生了什么、每句台词该怎么处理。模型广场的说明是「旗舰顶配，情感层次最细腻，有声书专业配音首选」。',
               '官方文档标注 v4 支持 90+ 种语言（含普通话和粤语），单次生成上限 10,000 字符，并支持在脚本里直接写 [laughs]、[whispers]、[door slams] 这类内联指令控制语气和音效。',
               '在 AnyAIGC 上，<code>eleven_v4</code> 走 <code>POST /v1/audio/speech</code>，一个 Bearer Key 即可调用，不需要单独注册 ElevenLabs 账号。按输入文本的字符数计费，并发不限。'],
        feats=[('情感与上下文理解', '官方称 v4 能结合上下文理解台词，在同一段脚本里处理不同说话人和情绪，适合需要表演感的内容。'),
               ('内联音频标签', '官方称可以在脚本里直接加入 [laughs]、[whispers]、[door slams] 等指令，且 v4 对标签序列的遵循比 v3 更可靠。'),
               ('90+ 种语言', '官方文档列出 90+ 种语言，包含普通话（zh）和粤语（yue），多语言内容可以用同一个模型。'),
               ('同一声音反复生成', '官方称重复生成同一句话时说话人特征保持稳定，便于多次试听、挑选和重做。')],
        uses=[('voice-narration.webp', '01 · 有声书', '有声书与长篇旁白', '章节旁白、小说播讲、课程讲解。官方文档把有声书和长篇情感叙述列为 v4 的典型场景。'),
              ('voice-character.webp', '02 · 角色', '游戏与动画角色配音', '官方文档称 v4 的情绪范围适合游戏和动画角色，可以给不同角色写不同标签。'),
              ('voice-entertainment.webp', '03 · 影视', '短剧、预告片与剧情旁白', '带情绪起伏的剧情台词，用音频标签标出停顿、叹息和语气变化。'),
              ('voice-multilingual.webp', '04 · 多语言', '多语言内容出海', '同一脚本翻译成多种语言后分别生成，保持相近的声音质感，用于视频、课程和产品介绍。')],
        text='[warm] 欢迎回来。[long pause] 今天的科技早报，现在开始。', has_tags=True),
    'eleven-v4-turbo': dict(
        sell='低延迟语音合成', lead='Eleven v4 的低延迟版本，保留 v4 的表现力，面向语音助手、客服和互动角色',
        tag='Eleven v4 的低延迟版本：官方标注中位推理延迟约 100ms，面向语音助手和互动角色。',
        sample_line=None,
        about=['Eleven v4 Turbo 是 Eleven v4 的低延迟版本。官方介绍它保留 v4 的表现力，中位推理延迟约 100ms，主打语音助手、客服、互动角色等需要快速响应的场景。模型广场的说明是「V4 实时流式版本，低延迟，兼顾情感和响应速度」。',
               '要注意两点：一是官方的 100ms 是中位推理延迟，不含网络和应用延迟，通过 HTTP 网关调用时实际首包时间会更长；二是官方的 WebSocket 双向流式输入不在 AnyAIGC 当前提供的接口里，模型广场对这款模型只列了 <code>POST /v1/audio/speech</code> 一个端点。',
               '在 AnyAIGC 上，<code>eleven_v4_turbo</code> 按输入文本的字符数计费，价格是 Eleven v4 的一半，并发不限。'],
        feats=[('低延迟', '官方标注中位推理延迟约 100ms（不含网络和应用延迟），适合对响应速度敏感的语音交互。'),
               ('保留 v4 的表现力', '官方称 Turbo 具备 v4 完整的表现力，并同样支持用音频标签控制语气。'),
               ('90+ 种语言', '与 Eleven v4 相同，官方文档列出 90+ 种语言，含普通话和粤语。'),
               ('价格是 v4 的一半', f'{p("eleven-v4-turbo")} / 万字符，Eleven v4 为 {p("eleven-v4")} / 万字符，对话类内容用量大时差别明显。')],
        uses=[('voice-conversational.webp', '01 · 助手', '语音助手与智能客服', '把大模型生成的回复转成语音播报，官方文档把客服代理和 AI 助手列为 v4 Turbo 的典型场景。'),
              ('voice-character.webp', '02 · 互动', '互动角色与游戏 NPC', '角色台词需要即时播放，对延迟敏感，可以按句分段请求。'),
              ('voice-social.webp', '03 · 短视频', '短视频与直播口播', '大量短句口播的批量生成，成本比 v4 低一半。'),
              ('voice-ads.webp', '04 · 播报', '通知与广告播报', '门店、活动、客服外呼的短播报，语气自然、生成快。')],
        text='[warm] 您好，这里是智能客服。请问有什么可以帮您？', has_tags=True),
    'eleven-v3': dict(
        sell='戏剧化配音', lead='ElevenLabs 上一代旗舰模型，戏剧表现力强，适合故事、短剧和角色配音',
        tag='戏剧表现力强，适合故事、短剧配音，70+ 种语言。',
        sample_line=None,
        about=['Eleven v3 是 ElevenLabs 的上一代旗舰语音合成模型，官方介绍它能生成自然、有生命力的语音，情绪范围大，对上下文的理解到位。模型广场的说明是「戏剧表现力强，适合故事、短剧配音，氛围感拉满」。',
               '官方文档标注 v3 支持 70+ 种语言，单次生成上限 5,000 字符。官方文档已把 v3 称为上一代模型，最新旗舰是 Eleven v4；两者在 AnyAIGC 的价格相同，新项目可以先用同一段文本分别试听再选。',
               '在 AnyAIGC 上，<code>eleven_v3</code> 走 <code>POST /v1/audio/speech</code>，按输入文本的字符数计费，并发不限。'],
        feats=[('戏剧化表现', '官方称 v3 的特点是戏剧化的演绎和较大的情绪范围，适合有表演感的内容。'),
               ('70+ 种语言', '官方文档列出 70+ 种语言，含普通话和粤语。'),
               ('故事与短剧配音', '模型广场把它定位为故事、短剧配音，氛围感强，适合有情节起伏的文本。'),
               ('与 v4 同价', f'{p("eleven-v3")} / 万字符，和 Eleven v4 一样，可以用同一段文本对比两个模型再决定。')],
        uses=[('voice-entertainment.webp', '01 · 短剧', '短剧与剧情配音', '剧情台词、旁白和反转桥段，需要情绪起伏时选 v3。'),
              ('voice-character.webp', '02 · 角色', '故事角色与游戏旁白', '给不同角色指定不同声音，分段生成后在剪辑软件里合成。'),
              ('voice-narration.webp', '03 · 有声书', '故事播讲', '儿童故事、悬疑小说等需要氛围感的播讲内容。'),
              ('voice-social.webp', '04 · 短视频', '剧情类短视频', '口播加情绪的短视频脚本，单次不超过官方 5,000 字符的上限。')],
        text='他推开那扇门的时候，屋里一个人也没有。只有窗外的雨，还在下。', has_tags=False,
        notice=True),
    'eleven-v3-conversational': dict(
        sell='对话语音', lead='v3 的低延迟对话版本，口语自然，适合聊天交互和语音角色',
        tag='v3 的对话版本：口语松弛自然，官方标注延迟约 165ms。',
        sample_line=None,
        about=['Eleven v3 Conversational 是 v3 面向实时对话调优的版本。官方介绍它保留 v3 的戏剧化演绎，延迟更低，并支持自定义音频标签。模型广场的说明是「对话专用，口语松弛自然，适合闲聊交互」。',
               '官方文档标注 v3 Conversational 的延迟约 165ms（中位推理延迟，不含网络和应用延迟），支持 70+ 种语言。官方的实时流式接口不在 AnyAIGC 当前提供的范围内，模型广场对它只列了 <code>POST /v1/audio/speech</code>。',
               '在 AnyAIGC 上，<code>eleven_v3_conversational</code> 按输入文本的字符数计费，价格是 Eleven v3 的一半，并发不限。'],
        feats=[('口语化对话', '语气松弛自然，适合闲聊、陪伴和角色扮演类的对话内容。'),
               ('较低延迟', '官方文档标注约 165ms 的中位推理延迟（不含网络和应用延迟）。'),
               ('自定义音频标签', '官方称支持自定义音频标签，可以在文本里标注语气变化。'),
               ('价格是 v3 的一半', f'{p("eleven-v3-conversational")} / 万字符，Eleven v3 为 {p("eleven-v3")} / 万字符。')],
        uses=[('voice-conversational.webp', '01 · 聊天', '闲聊机器人与陪伴应用', '把对话模型的回复转成口语化的语音，适合聊天和陪伴类产品。'),
              ('voice-character.webp', '02 · 角色', '虚拟角色与 NPC 对话', '角色台词的语气更接近真人说话，而不是播音腔。'),
              ('voice-social.webp', '03 · 短视频', '口语化口播', '生活、探店、种草类的口语口播。'),
              ('voice-education.webp', '04 · 教学', '口语陪练与讲解', '语言陪练、答疑讲解等需要自然语气的场景。')],
        text='哎，你今天怎么这么早？是不是又没睡好呀。', has_tags=False),
    'eleven-multilingual-v2': dict(
        sell='长文本语音', lead='长篇文稿表现稳定，双语混读不容易崩坏，适合旁白和课程',
        tag='长篇文稿稳定，官方称其在长文本生成上最稳定，29 种语言。',
        sample_line=None,
        about=['Eleven Multilingual v2 是 ElevenLabs 面向长篇内容的语音合成模型。官方介绍它音质自然、风格一致，在长文本生成上表现稳定。模型广场的说明是「长篇文稿稳定，双语混读音色不容易崩坏」。',
               '官方文档标注它支持 29 种语言（含普通话），单次生成上限 10,000 字符。官方文档还提到，手机号、日期、金额这类数字内容，Multilingual v2 的规范化处理比 Flash v2.5 更好，这类文本建议选它。',
               '在 AnyAIGC 上，<code>eleven_multilingual_v2</code> 走 <code>POST /v1/audio/speech</code>，按输入文本的字符数计费，并发不限。'],
        feats=[('长文本更稳', '官方称它在长文本生成上最稳定，适合整段旁白、课程讲解和文章朗读。'),
               ('双语混读', '中英混合的文本里，声音不容易在语言切换处走样，适合科技、教育类内容。'),
               ('数字读法更好', '官方文档说明 Multilingual v2 对数字的规范化处理更好，手机号、日期、金额类文本建议选它。'),
               ('29 种语言', '官方文档列出 29 种语言，含普通话，覆盖常见出海语种。')],
        uses=[('voice-narration.webp', '01 · 旁白', '长篇旁白与文章朗读', '公众号文章、新闻稿、报告的整段朗读。'),
              ('voice-education.webp', '02 · 教育', '课程讲解与培训', '中英混合的课程讲解，术语读音稳定。'),
              ('voice-multilingual.webp', '03 · 多语言', '多语言视频配音', '同一脚本翻译成多种语言分别生成。'),
              ('voice-ads.webp', '04 · 播报', '说明与播报类内容', '带数字、日期的产品说明、活动播报。')],
        text='本次课程共分为三个部分，第一部分介绍 API 的基本概念。', has_tags=False),
    'eleven-flash-v2-5': dict(
        sell='超长文本批量', lead='轻量高速模型，单次文本上限高，适合超长文本和大批量字幕生成',
        tag='轻量高速，官方单次上限 40,000 字符，32 种语言，适合批量生成。',
        sample_line=None,
        about=['Eleven Flash v2.5 是 ElevenLabs 的快速、经济型语音合成模型。官方介绍它延迟低（约 100ms），支持 32 种语言，单次生成上限 40,000 字符。模型广场的说明是「超长文本专用，价格最低，适合大批量字幕生成」。',
               '官方文档提醒：Flash v2.5 默认不做文本规范化，手机号、日期、金额可能读得不清楚。这类内容请先在文本里写成要读的样子，或者改用 Multilingual v2。',
               '在 AnyAIGC 上，<code>eleven_flash_v2_5</code> 走 <code>POST /v1/audio/speech</code>，按输入文本的字符数计费，价格是 Eleven v4 的一半，并发不限。'],
        feats=[('超长文本', '官方单次上限 40,000 字符，在 ElevenLabs 的语音合成模型里最高，长文稿分段更少。'),
               ('速度快', '官方标注约 100ms 的中位推理延迟（不含网络和应用延迟），适合批量任务。'),
               ('32 种语言', '官方文档列出 32 种语言，含普通话。'),
               ('数字需要自己处理', '官方文档说明默认不做文本规范化，数字、日期、金额类文本建议先改写成要读的样子。')],
        uses=[('voice-education.webp', '01 · 字幕', '批量字幕与课程配音', '大量字幕条目、课程脚本的批量转语音。'),
              ('voice-narration.webp', '02 · 朗读', '长文章与资讯朗读', '资讯、公告、文档的整篇朗读。'),
              ('voice-ads.webp', '03 · 播报', '通知与播报', '批量通知、门店广播、电话语音提示。'),
              ('voice-social.webp', '04 · 短视频', '大批量口播素材', '电商、资讯类短视频的批量口播。')],
        text='各位乘客请注意，前方到站，北京南站。', has_tags=False),
    'eleven-flash-v2': dict(
        sell='轻量高速播报', lead='轻量高速的英语语音合成模型，适合短句朗读和提示音',
        tag='轻量高速，官方文档只列了英语，官方标注延迟约 135ms。',
        sample_line=None,
        about=['Eleven Flash v2 是 ElevenLabs 的轻量高速语音合成模型。官方文档的模型表里它只列了英语（en），官方标注延迟约 135ms，单次生成上限 30,000 字符。模型广场的说明是「轻量高速播报模型，性价比高，适合短句朗读」。',
               '要注意：官方文档只列了英语，所以中文等其他语言请选 Eleven Flash v2.5、Multilingual v2 或 v4 等多语言型号。',
               '在 AnyAIGC 上，<code>eleven_flash_v2</code> 走 <code>POST /v1/audio/speech</code>，按输入文本的字符数计费，价格是 Eleven v4 的一半，并发不限。'],
        feats=[('轻量高速', '官方标注约 135ms 的中位推理延迟（不含网络和应用延迟）。'),
               ('英语播报', '官方文档只列了英语，适合英文提示音、短句朗读和英语教学素材。'),
               ('单次 30,000 字符', '官方单次上限 30,000 字符，英文长文也能一次生成。'),
               ('成本低', f'{p("eleven-flash-v2")} / 万字符，约为 Eleven v4 的一半。')],
        uses=[('voice-education.webp', '01 · 教学', '英语教学素材', '单词、例句和短文的朗读音频。'),
              ('voice-ads.webp', '02 · 播报', '英文提示音与播报', '产品内英文语音提示、门店英文广播。'),
              ('voice-social.webp', '03 · 短视频', '英文口播', '英文短视频口播的批量生成。'),
              ('voice-narration.webp', '04 · 朗读', '英文文章朗读', '英文资讯、博客的整篇朗读。')],
        text='Welcome back. Your order has been shipped.', has_tags=False),
}

QS_NOTE = f'完整参数见 <a href="{DOCS_SPEECH}" target="_blank" rel="noopener">创建语音接口文档</a>，文档示例里的模型名换成对应的 Eleven 模型 ID 即可。'
PRICE_HEAD = [('计费单位', ''), ('模型名', ''), ('ElevenLabs 官方价（USD）', 'o-num'), ('AnyAIGC 单价（USD）', 'o-num o-hl')]
COMPARE_HEAD = [('型号', ''), ('定位', 'el-txt'), ('语言（官方）', 'el-txt'), ('单次字符上限（官方）', 'el-txt'), ('延迟（官方标注）', 'el-txt'), ('AnyAIGC 每万字符', 'o-num o-hl')]
POS = {'eleven-v4': '旗舰，有声书与专业配音', 'eleven-v4-turbo': '低延迟，语音助手', 'eleven-v3': '戏剧化，故事与短剧',
       'eleven-v3-conversational': '对话，口语自然', 'eleven-multilingual-v2': '长文稳定，双语混读',
       'eleven-flash-v2-5': '超长文本，批量字幕', 'eleven-flash-v2': '轻量高速，英语短句'}


def langs_text(slug):
    l = MODELS[slug]['langs']
    return '仅英语' if l == 'en' else f'{l} 种'


def limit_text(slug):
    l = MODELS[slug]['limit']
    return f'{l} 字符' if l else '未列出'


def latency_text(slug):
    return MODELS[slug]['latency'] or '未标注'


def compare_rows():
    return [(f'<a href="/zh/models/{s}">{MODELS[s]["name"]}</a>', '', [POS[s], langs_text(s), limit_text(s), latency_text(s), p(s)], s) for s in SLUGS]


COMPARE_NOTE = ('语言数、字符上限和延迟来自 <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs 官方模型文档</a>；延迟是官方标注的中位推理延迟，不含网络和应用延迟。价格为 AnyAIGC 当前价格，实时价格以模型广场为准。'
                '「未列出」「未标注」表示官方文档没有给出该项。')

FAMILY = [(s, '', f'{POS[s]} · {p(s)} / 万字符') for s in SLUGS]
FAMILY[0] = (FAMILY[0][0], '旗舰', FAMILY[0][2])
FAMILY[1] = (FAMILY[1][0], '低延迟', FAMILY[1][2])


def costs(slug):
    c = lambda n: money(cost(slug, n))
    o = lambda n: f'ElevenLabs 官方同用量 {money(cost(slug, n, True))}'
    return [('一条短视频口播', '约 300 字符', c(300), o(300)),
            ('一章有声书', '约 8,000 字符', c(8000), o(8000)),
            ('批量生成 100 万字符', '约 100 万字符，按单价 × 100 计算', c(1000000), o(1000000))]


def offers(slug):
    return [('每万字符', PRICE[slug])]


def billing(slug):
    return [('按字符计费', '按输入文本的字符数'), ('约官方 8.1 折', f'官方 {off(slug)} / 万字符'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')]


def pricing_labels():
    # (名称, 说明, 相对「每万字符」的倍数, 是否主行)
    return [('每万字符', '模型广场计价单位', 1, True), ('每千字符', '与 ElevenLabs 官方价格页对照', Decimal('0.1'), False), ('每百万字符', '大批量参考', 100, False)]


def pricing_note(slug):
    extra = '官方价取自价格页的 Flash / Turbo 一档。' if slug in ('eleven-flash-v2-5', 'eleven-flash-v2') else ''
    return (f'价格单位为美元，按输入文本的字符数计费，表中为模型广场最低价，实时价格以 <a href="{MARKET}">AnyAIGC 模型广场</a> 为准。'
            f'官方价来自 <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">ElevenLabs 价格页</a>的 Text to Speech API 表，按每千字符 ${OFFICIAL_1K[slug]} '
            f'折算，AnyAIGC 价格是官方价的 81%（约 8.1 折）。{extra}')


def qs_steps(model):
    return ['<strong>注册并充值</strong>：在 <a href="' + REG + '">anyaigc.ai</a> 注册账号，最低 $1 起充，余额对平台所有模型通用。',
            '<strong>创建 API Key</strong>：在控制台创建令牌，复制以 <code>sk-</code> 开头的 Key，存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'<strong>发起请求</strong>：请求 <code>POST https://anyaigc.ai/v1/audio/speech</code>，<code>model</code> 填 <code>{model}</code>，<code>voice</code> 填 ElevenLabs 的 voice_id，鉴权用 <code>Authorization: Bearer</code>，把返回的音频保存为 mp3。']


# ---------------- FAQ ----------------
def faq_common(name, slug):
    return [
        ('国内可以直接调用 ' + name + ' API 吗？',
         '可以。AnyAIGC 面向国内网络优化，通常无需额外代理即可调用 <code>https://anyaigc.ai</code>，按美元价格计费，支持微信支付、支付宝、USDT 和信用卡，企业可对公转账并开具增值税发票。'),
        ('AnyAIGC 能开发票吗？支持增值税专票吗？',
         '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
        ('企业可以对公转账和签合同吗？',
         f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
        ('我的文本和生成的音频会被用于训练吗？',
         '不会。除法律法规要求外，AnyAIGC 不对你的输入输出内容做持久化存储，也不会用于训练模型，请求通过 HTTPS 加密传输，详见 AnyAIGC <a href="/privacy">隐私政策</a>。模型本身的数据政策以 ElevenLabs 官方为准。'),
    ]


def faq_rpm(slug):
    return ('并发和速率有限制吗？',
            f'AnyAIGC 对 <code>{MODELS[slug]["id"]}</code> 不设并发限制，所有用户默认享有，适合批量生成和多任务并行。按字符计费，没有月费和按时间窗口重置的额度。')


def special_faq(slug):
    if slug == 'eleven-v4':
        return ('可以在文本里写 [laughs]、[whispers] 这样的标签吗？',
                'ElevenLabs 官网介绍 Eleven v4 支持在脚本里直接加入 [laughs]、[whispers]、[door slams] 等指令，并称 v4 对标签序列的遵循比 v3 更可靠。AnyAIGC 接口文档没有单独说明标签参数，标签的实际效果请先用一小段文本试听确认。')
    if slug == 'eleven-v4-turbo':
        return ('Eleven v4 Turbo 的延迟到底有多低？',
                '官方标注的是约 100ms 的中位推理延迟，这个数字不含网络和应用延迟。AnyAIGC 当前提供的是 HTTP 的 <code>/v1/audio/speech</code> 接口，没有官方的 WebSocket 双向流，所以实际等待时间取决于文本长短和网络，做实时对话请先实测，并尽量按句分段请求。')
    if slug == 'eleven-v3':
        return ('Eleven v3 停用了吗？',
                '没有。官方文档把 v3 称为上一代模型，最新旗舰是 Eleven v4，官方文档的停用模型列表里没有 v3（列出的是 eleven_turbo_v2_5、eleven_turbo_v2 等）。新项目可以先用 ' + link('eleven-v4') + ' 对比试听，两者在 AnyAIGC 价格相同。是否继续可用以模型广场为准。')
    if slug == 'eleven-v3-conversational':
        return ('Eleven v3 Conversational 和 Eleven v3 有什么区别？',
                '前者面向对话场景，口语更自然，官方标注延迟约 165ms，价格是 Eleven v3 的一半；后者戏剧化表现更强，适合故事和短剧配音。可以用同一段文本分别试听。详见 ' + link('eleven-v3') + '。')
    if slug == 'eleven-multilingual-v2':
        return ('手机号、日期、金额这类数字内容用哪个模型？',
                '官方文档说明 Multilingual v2 对数字的规范化处理比 Flash v2.5 更好，手机号、日期等内容建议选 Multilingual v2。也可以先在文本里把数字改写成要读的样子再生成。')
    if slug == 'eleven-flash-v2-5':
        return ('Flash v2.5 读数字、日期不准怎么办？',
                '官方文档说明 Flash v2.5 默认不做文本规范化，手机号、日期、金额可能读得不清楚（企业版客户可以开启规范化）。建议在文本里先把数字改写成要读的样子，或者改用 ' + link('eleven-multilingual-v2') + '。')
    return ('Eleven Flash v2 支持中文吗？',
            '官方文档的模型表里 Flash v2 只列了英语（en），所以中文等其他语言不要选它，请用 ' + link('eleven-flash-v2-5') + '、' + link('eleven-multilingual-v2') + ' 或 ' + link('eleven-v4') + '。')


def fit_title(core, brand, limit=64):
    """中文 title 显示宽度（汉字计 2）不超过 limit：放得下就带品牌后缀，放不下就只保留正文"""
    w = lambda t: sum(2 if ord(c) > 0x2e7f else 1 for c in t)
    return core + brand if w(core + brand) <= limit else core


def build(slug):
    m = M[slug]
    d = MODELS[slug]
    mid, name = d['id'], d['name']
    s = slug
    others = [x for x in SLUGS if x != s]
    price, offp = p(s), off(s)
    text = m['text']
    has_sample = m['sample_line'] is not None

    faqs = [
        (f'{name} API 多少钱？',
         f'AnyAIGC 上 <code>{mid}</code> 按字符计费：{price} / 万字符，约为 ElevenLabs 官方价（{offp} / 万字符）的 8.1 折。固定单价，没有订阅和月费，实时价格以模型广场为准。'),
        (f'{name} 的模型 ID 是什么？和 ElevenLabs 是什么关系？',
         f'模型 ID 是 <code>{mid}</code>（区分大小写），和 ElevenLabs 官方的 model_id 一致。AnyAIGC 是独立的 API 服务商，提供 OpenAI 风格的 <code>/v1/audio/speech</code> 调用方式，与 ElevenLabs 没有隶属关系。'),
        (f'{name} 和其他 Eleven 型号怎么选？',
         f'平台上共有 7 款 Eleven 语音模型：{link("eleven-v4")}（旗舰）、{link("eleven-v4-turbo")}（低延迟）、{link("eleven-v3")}、{link("eleven-v3-conversational")}、{link("eleven-multilingual-v2")}、{link("eleven-flash-v2-5")}、{link("eleven-flash-v2")}。'
         '追求成品音质选 v4，做语音助手选 v4 Turbo，长文本和双语混读选 Multilingual v2，大批量字幕选 Flash v2.5，同一段文本建议分别试听再定。'),
        (f'怎么调用 {name} API？voice 填什么？',
         f'请求 <code>POST https://anyaigc.ai/v1/audio/speech</code>，必填 <code>model</code>、<code>input</code>、<code>voice</code>。<code>voice</code> 填 ElevenLabs 的 voice_id，voice_id 不存在或不可用时接口返回 400；<code>response_format</code> 支持 mp3、opus、aac、flac。完整参数见<a href="{DOCS_SPEECH}" target="_blank" rel="noopener">接口文档</a>。'),
        (f'{name} 一次能合成多长的文本？',
         ('ElevenLabs 官方文档标注该模型单次生成上限为 ' + d['limit'] + ' 字符。' if d['limit'] else 'ElevenLabs 官方文档没有给出该模型的单次字符上限。')
         + 'AnyAIGC 创建语音接口文档里 <code>input</code> 一栏标注的最大长度是 4,096 字符，长文本请按这个长度分段请求，再把音频拼接起来。'),
        (f'{name} 支持中文吗？支持多少种语言？',
         ('官方文档的模型表里它只列了英语，中文请改用其他型号。' if d['langs'] == 'en'
          else f'支持。官方文档标注该模型支持 {d["langs"]} 种语言，普通话（zh）在列表里。')
         + '具体语种以 <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs 官方文档</a>为准。'),
        special_faq(s),
        faq_rpm(s),
    ]
    faqs += [
        (f'能用自己克隆的声音吗？',
         '接口文档只写明 <code>voice</code> 填 ElevenLabs 的 voice_id。你自己 ElevenLabs 账号里的克隆音色能否通过 AnyAIGC 的 Key 调用，文档没有说明，请联系 <a href="' + SUPPORT + '">AnyAIGC 客服</a>确认。'),
    ]
    faqs += faq_common(name, s)
    key_q = (f'如何获取 {name} API Key？',
             f'在 <a href="{REG}">anyaigc.ai</a> 注册并充值，进入控制台创建令牌即可。同一个 Key 可以调用平台上 300+ 个模型，不需要单独注册 ElevenLabs 账号。请求体的 <code>model</code> 填 <code>{mid}</code>。')
    faqs.insert(3, key_q)

    sell = m['sell']
    hero_notice = None
    if m.get('notice'):
        hero_notice = f'ElevenLabs 官方文档把 Eleven v3 称为上一代模型，最新旗舰是 <a href="/zh/models/eleven-v4">Eleven v4</a>（AnyAIGC 价格相同）。v3 在模型广场当前仍可调用，是否继续可用以 <a href="{MARKET}">模型广场</a> 为准。'

    sample = None
    if has_sample:
        sample = dict(play='播放示例音频', pause='暂停示例音频', title='ElevenLabs 官网 v4 示例', line=m['sample_line'])

    langs_fact = '仅英语' if d['langs'] == 'en' else f'{d["langs"]} 种语言'
    facts = [('模型 ID', mid), ('价格', f'{price} / 万字符'), ('语言', langs_fact), ('并发', '不限'), ('企业', '对公 · 专票')]

    return dict(
        title=fit_title(f'{name} API 价格｜{sell}，官方 8.1 折', ' - AnyAIGC'),
        desc=f'{mid} API：{m["lead"]}。{price}/万字符，约官方 8.1 折，并发不限，支持对公转账与增值税专票。',
        og_desc=f'{mid} {price}/万字符，约官方 8.1 折。{m["lead"]}，并发不限，支持对公转账与增值税专票。',
        og_alt=f'AnyAIGC {mid} API：{price}/万字符，约官方 8.1 折',
        keywords=f'{mid} API,{mid},{name} API 价格,{name} API 接入,{name} API key,ElevenLabs API,ElevenLabs API 价格,ElevenLabs 中转,Eleven 语音合成 API,AI 配音 API,文字转语音 API,{name} API 企业,{name} API 发票,ElevenLabs API 对公转账,AnyAIGC',
        crumb=f'{name} API', product=f'{name} API（AnyAIGC）', sku=s,
        product_desc=f'通过 AnyAIGC 调用 ElevenLabs {name}：POST /v1/audio/speech，按字符计费，{price}/万字符（约官方 8.1 折），并发不限。',
        offers=offers(s),
        hero=dict(eyebrow=f'ElevenLabs · {mid}', deal=DEAL,
                  h1=f'Eleven <b>{d["short"]}</b><span class="o-sr"> API</span>',
                  lead=f'{m["tag"]}一个 API Key 调用，按字符计费，价格约为官方的 8.1 折。',
                  sample=sample,
                  sub=f'<code>{mid}</code> {price} / 万字符（ElevenLabs 官方 {offp} / 万字符），并发不限，支持对公转账与增值税专票。',
                  notice=hero_notice, facts=facts),
        about=dict(kicker='关于模型', h2=f'{name}：{sell}', paras=m['about'],
                   spec=[('模型 ID', mid, '请求体 model 字段，区分大小写'), ('接口', 'Text to speech', 'POST /v1/audio/speech'),
                         ('价格', price, '每万字符，约官方 8.1 折'), ('语言', langs_fact, 'ElevenLabs 官方文档'),
                         ('单次字符上限', limit_text(s), '官方文档；AnyAIGC 接口文档标注 input 最大 4,096 字符'),
                         ('延迟', latency_text(s), '官方标注的中位推理延迟，不含网络')]),
        features=dict(kicker='能力', h2=f'{name} 能做什么',
                      items=m['feats'] + [('OpenAI 风格接口', '一个 Bearer Key，请求 <code>/v1/audio/speech</code>，传 model、input、voice，得到音频文件，OpenAI SDK 的 audio.speech 也能直接用。'),
                                          ('并发不限，约官方 8.1 折', f'所有用户默认不限并发；{price} / 万字符，官方价为 {offp} / 万字符。')]),
        pricing=dict(kicker='价格', h2=f'{name} API 价格', lead='按输入文本的字符数计费，固定单价，没有订阅和月费，约为 ElevenLabs 官方价的 8.1 折。',
                     billing_label='计费要点', billing=billing(s), head=PRICE_HEAD, labels=pricing_labels(),
                     caption=f'{mid} 价格对照（美元）：ElevenLabs 官方价与 AnyAIGC 价', note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，用上面的单价相乘得出，并和官方价对比。', costs=costs(s)),
        compare=dict(kicker='选型', h2='7 款 Eleven 语音模型怎么选', lead='成品音质选 v4，语音助手选 v4 Turbo，长文本和双语混读选 Multilingual v2，大批量字幕选 Flash v2.5。',
                     head=COMPARE_HEAD, rows=compare_rows(), caption='7 款 Eleven 语音模型对比，价格为 AnyAIGC 每万字符美元', note=COMPARE_NOTE),
        uses=dict(kicker='使用场景', h2=f'{name} 适合做什么', items=m['uses']),
        qs=dict(kicker='快速开始', h2=f'三步接入 {name} API', steps=qs_steps(mid),
                tabs=[('curl', 'cURL', 'POST /v1/audio/speech', code.curl(mid, text)),
                      ('py', 'Python · requests', 'Python · requests', code.requests_py(mid, text)),
                      ('sdk', 'Python · OpenAI SDK', 'Python · openai SDK', code.sdk_py(mid, text))],
                callout=f'<strong>参数提示：</strong>模型 ID 区分大小写，写成 <code>{mid}</code>；<code>voice</code> 填 ElevenLabs 的 voice_id，不存在或不可用时返回 400；接口文档标注 <code>input</code> 最大 4,096 字符，长文本请分段。示例把响应体按音频文件保存为 mp3。',
                note=QS_NOTE),
        family_h2='Eleven 系列全部型号', family_lead='同一个 API Key 可以调用下面所有 Eleven 语音模型，按场景和预算选择。',
        faq_h2=f'{name} API 常见问题', faqs=faqs,
        final=dict(h2=f'用一个 Key 调用 {name}', p=f'注册后创建 API Key，几分钟就能在代码里用上 {mid}，余额对平台 300+ 模型通用。', other=f'{name} API in English'),
        ent_name=name,
    )
