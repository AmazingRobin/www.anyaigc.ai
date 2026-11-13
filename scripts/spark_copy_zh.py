# SparkDesk（讯飞星火）系列专题页中文文案。被 scripts/spark_pages.py 引用。
# 价格来自 spark_data.PRICE（模型广场详情弹窗，2026-11-13），官方参数来自讯飞开放平台 Web.html 文档。
# 官方价没有核实到，所以页面不写官方对比价和折扣；SparkDesk-v2.1 的能力没有官方来源，只写模型广场的描述。
from spark_data import PRICE, MODELS, REG, PRICING, SUPPORT, DOCS_CHAT, OFFICIAL_DOC
from spark_layout import cost, money

UNIT = '百万 tokens'
MARKET = PRICING + '?provider=Spark'


def p(slug, i):
    return f'${PRICE[slug][i]}'


# ---------------- 共用 FAQ ----------------
def faq_common(name, slug):
    mid = MODELS[slug]['id']
    return [
        (f'国内可以直接调用 {name} API 吗？',
         '可以。AnyAIGC 面向国内网络优化，通常无需额外代理即可调用 <code>https://anyaigc.ai</code>，按美元价格计费，支持微信支付、支付宝、USDT 和信用卡，企业可对公转账并开具增值税发票。'),
        (f'如何获取 {name} API Key？',
         f'在 <a href="{REG}">anyaigc.ai</a> 注册并充值，进入控制台创建令牌即可。同一个 Key 可以调用平台上 300+ 个模型，不需要单独申请讯飞开放平台的 APPID、APIKey 和 APISecret。请求体的 <code>model</code> 填 <code>{mid}</code>。'),
        ('AnyAIGC 能开发票吗？支持增值税专票吗？',
         '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
        ('企业可以对公转账和签合同吗？',
         f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
        ('我的数据会被用于训练吗？',
         '不会。除法律法规要求外，AnyAIGC 不对你的输入输出内容做持久化存储，也不会用于训练模型，请求通过 HTTPS 加密传输，详见 AnyAIGC <a href="/privacy">隐私政策</a>。模型本身的数据政策以科大讯飞官方条款为准。'),
    ]


def faq_rpm(name, slug):
    return ('并发和速率有限制吗？',
            f'AnyAIGC 对 <code>{MODELS[slug]["id"]}</code> 不设并发限制，所有用户默认享有，适合批量处理和多任务并行。按 token 计费，没有月费和按时间窗口重置的额度。')


# ---------------- 代码示例 ----------------
def code_curl(model, prompt):
    return f'''curl https://anyaigc.ai/v1/chat/completions \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "messages": [
      {{"role": "user", "content": "{prompt}"}}
    ]
  }}\''''


def code_py(model, system, user):
    sys_line = f'''        {{"role": "system", "content": "{system}"}},
''' if system else ''
    return f'''import os
from openai import OpenAI

client = OpenAI(
    base_url="https://anyaigc.ai/v1",
    api_key=os.environ["ANYAIGC_API_KEY"],
)

resp = client.chat.completions.create(
    model="{model}",
    messages=[
{sys_line}        {{"role": "user", "content": "{user}"}},
    ],
)
print(resp.choices[0].message.content)
print(resp.usage)  # 本次请求的输入 / 输出 tokens'''


def code_stream(model, user):
    return f'''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

stream = client.chat.completions.create(
    model="{model}",
    messages=[{{"role": "user", "content": "{user}"}}],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
print()'''


def qs_steps(model):
    return ['<strong>注册并充值</strong>：在 <a href="' + REG + '">anyaigc.ai</a> 注册账号，最低 $1 起充，余额对平台所有模型通用。',
            '<strong>创建 API Key</strong>：在控制台创建令牌，复制以 <code>sk-</code> 开头的 Key，存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'<strong>发起请求</strong>：请求 <code>POST https://anyaigc.ai/v1/chat/completions</code>，<code>model</code> 填 <code>{model}</code>，鉴权用 <code>Authorization: Bearer</code>。OpenAI SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。']


QS_NOTE = f'完整参数见 <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions 接口文档</a>，文档示例里的模型名换成对应的 SparkDesk 模型 ID 即可。'
PRICE_HEAD = [('计费项', ''), ('模型名', ''), ('AnyAIGC 单价（USD）', 'o-num o-hl')]
LABELS = [('输入', '每 100 万 tokens'), ('输出', '每 100 万 tokens')]


def pricing_note(slug):
    return (f'价格单位为美元，按实际消耗的 tokens 计费，输入和输出同价。表中为模型广场最低价，实时价格以 <a href="{MARKET}">AnyAIGC 模型广场</a> 为准。')


def billing(slug):
    return [('按 token 计费', '输入、输出分别计量'), ('输入输出同价', f'均为 {p(slug, 0)} / 百万'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')]


def costs(slug):
    return [
        ('客服问答 1 万次', '每次 800 tokens 输入 + 300 tokens 输出', money(cost(slug, 800, 300, 10000))),
        ('单篇长文摘要', '6,000 tokens 输入 + 800 tokens 输出', money(cost(slug, 6000, 800))),
        ('每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', money(cost(slug, 1000000, 1000000))),
    ]


def offers(slug):
    return [('输入（每 100 万 tokens）', PRICE[slug][0]), ('输出（每 100 万 tokens）', PRICE[slug][1])]


FAMILY = [
    ('sparkdesk-v3.5', '最新', f'讯飞星火 Max 档，三款里版本最新 · 输入 {p("sparkdesk-v3.5", 0)} / 1M'),
    ('sparkdesk-v3.1', '', f'讯飞星火 Pro 档，对话与问答 · 输入 {p("sparkdesk-v3.1", 0)} / 1M'),
    ('sparkdesk-v2.1', '旧版', f'早期 2.x 版本，存量业务沿用 · 输入 {p("sparkdesk-v2.1", 0)} / 1M'),
]

COMPARE_HEAD = [('对比项', ''), ('SparkDesk-v3.5', 'o-num o-hl'), ('SparkDesk-v3.1', 'o-num'), ('SparkDesk-v2.1', 'o-num')]


def compare_rows():
    a, b, c = 'sparkdesk-v3.5', 'sparkdesk-v3.1', 'sparkdesk-v2.1'
    return [('讯飞官方档位', '', '星火 Max', '星火 Pro', '早期 2.x 版本'),
            ('接口版本', '', 'v3.5', 'v3.1', 'v2.1'),
            ('上下文 / 最大输出', '官方文档', '8,192 / 8,192', '8,192 / 8,192', '官方文档未列出'),
            ('系统提示词（system 角色）', '官方文档', '支持', '不支持', '未列出'),
            ('AnyAIGC 输入', '每百万 tokens', p(a, 0), p(b, 0), p(c, 0)),
            ('AnyAIGC 输出', '每百万 tokens', p(a, 1), p(b, 1), p(c, 1))]


COMPARE_NOTE = ('官方档位与参数来自<a href="' + OFFICIAL_DOC + '" target="_blank" rel="noopener">讯飞开放平台文档</a>，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。'
                '各型号详情见 <a href="/zh/models/sparkdesk-v3.5">SparkDesk-v3.5</a>、<a href="/zh/models/sparkdesk-v3.1">SparkDesk-v3.1</a>、<a href="/zh/models/sparkdesk-v2.1">SparkDesk-v2.1</a>。')

# 每个型号的差异化内容
M = {
    'sparkdesk-v3.5': dict(
        title='SparkDesk-v3.5 API 价格与接入｜讯飞星火 Max 档 - AnyAIGC',
        tier='星火 Max', mid='SparkDesk-v3.5',
        desc_lead='讯飞星火 Max 档（接口版本 v3.5），多轮对话、知识问答、逻辑推理和代码理解',
        notice=f'讯飞官方文档称 Max 套餐已于 2026 年 3 月 10 日下线，后端升级为 Ultra。SparkDesk-v3.5 在 AnyAIGC 模型广场当前仍可调用，可用性以 <a href="{MARKET}">模型广场</a> 为准。',
        ask='把这批客服对话整理成工单摘要，并给出下一步处理建议',
        answer="工单摘要：用户反映订单支付后三天仍显示“待发货”，两次联系仓库都没有回复，希望尽快发货或退款。\n下一步建议：\n1. 今天内联系仓库，确认库存和发货时间；\n2. 向用户同步预计发货日期并致歉；\n3. 如超过 48 小时仍无法发货，主动提供退款或补偿方案。",
        chips=['多轮对话', '知识问答', '代码理解'],
        about_h2='讯飞星火 Max 档的 3.5 版本',
        about=['SparkDesk-v3.5 是科大讯飞星火认知大模型的 3.5 版本接口，对应讯飞官方的星火 Max 档。模型广场的说明是：具备跨领域知识和语言理解能力，能通过自然对话理解并执行任务，覆盖语言理解、知识问答、逻辑推理、数学解题和代码理解。',
               '讯飞官方文档标注该档位的上下文窗口和单次最大输出均为 8,192 tokens，并列出系统提示词（仅 Max、Ultra 支持）和联网搜索插件（Pro、Max、Ultra 支持）；官方文档说明函数调用需要改用 HTTP 协议，没有按档位列出。通过 AnyAIGC 调用时的实际支持情况，以接口文档和实测为准。',
               '在 AnyAIGC 上，<code>SparkDesk-v3.5</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，一个 Bearer Key 即可调用，不需要自己申请讯飞开放平台的 APPID、APIKey 和 APISecret，也不用处理官方的 WebSocket 签名。按 token 计费，并发不限。'],
        spec=[('模型 ID', 'SparkDesk-v3.5', '请求体 model 字段，区分大小写'), ('对应官方档位', '星火 Max', 'domain：generalv3.5'),
              ('上下文窗口', '8,192', 'tokens，官方文档标注'), ('最大输出', '8,192', 'tokens，官方文档标注'),
              ('接口', 'Chat Completions', 'POST /v1/chat/completions'), ('输入 / 输出', '同价', None)],
        feat_h2='SparkDesk-v3.5 能做什么',
        feats=[('多轮自然对话', '通过自然对话理解并执行任务，适合客服、助手和问答类应用。'),
               ('知识问答', '跨领域知识问答，覆盖常见的百科、办公和行业咨询场景。'),
               ('逻辑推理', '对多步条件、规则判断和对比分析类问题给出推理过程和结论。'),
               ('数学解题', '模型广场列出数学问题求解能力，可用于学习辅导和公式类问答。'),
               ('代码理解', '解释代码片段、定位明显错误、补全简单函数，适合开发辅助场景。'),
               ('系统提示词', '官方文档列出 Max 档支持用 system 角色设置对话背景，可用来固定角色口吻和回答规则。')],
        uses=[('01 · 客服', '客服问答与工单摘要', '把用户咨询和历史对话交给 SparkDesk-v3.5，生成回复草稿或工单摘要，由人工确认后发送。'),
              ('02 · 知识库', '文档与知识库问答', '把检索到的文档片段放进提示词，让模型据此回答，注意单次上下文约 8K tokens，长文档需要先分段。'),
              ('03 · 写作', '文案改写与润色', '营销文案、通知、邮件的改写和润色，输入输出同价，批量处理时成本容易估算。'),
              ('04 · 开发', '代码解释与简单补全', '为内部工具加一个代码解释或注释生成功能，复杂工程任务建议选更长上下文的模型。')],
        final_h2='用一个 Key 调用 SparkDesk-v3.5',
    ),
    'sparkdesk-v3.1': dict(
        title='SparkDesk-v3.1 API 价格与接入｜讯飞星火 Pro 档 - AnyAIGC',
        tier='星火 Pro', mid='SparkDesk-v3.1',
        desc_lead='讯飞星火 Pro 档（接口版本 v3.1），对话、知识问答、逻辑推理和代码理解',
        notice=None,
        ask='根据这段产品说明，写三条适合发在公众号的推广文案',
        answer="1. 每天五分钟，把零散的待办理清楚。试试我们的任务清单，让工作有条不紊。\n2. 总说没时间整理？一键导入，自动分类，今天的事今天做完。\n3. 效率不是加班换来的。用对工具，下班前就能把事情收尾。",
        chips=['对话问答', '文案改写', '数学解题'],
        about_h2='讯飞星火 Pro 档的 3.1 版本',
        about=['SparkDesk-v3.1 是科大讯飞星火认知大模型的 3.1 版本接口，对应讯飞官方的星火 Pro 档。模型广场的说明是：具备跨领域知识和语言理解能力，通过自然对话理解并执行任务，覆盖语言理解、知识问答、逻辑推理、数学解题和代码理解。',
               '讯飞官方文档标注该档位的上下文窗口和单次最大输出均为 8,192 tokens。官方文档说明 system 角色（设置对话背景）仅 Max 和 Ultra 支持，Pro 档支持联网搜索插件；如果你的应用需要固定角色提示词，请改用 <a href="/zh/models/sparkdesk-v3.5">SparkDesk-v3.5</a>。',
               '在 AnyAIGC 上，<code>SparkDesk-v3.1</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，一个 Bearer Key 即可调用，不需要自己申请讯飞开放平台的 APPID、APIKey 和 APISecret。按 token 计费，并发不限。'],
        spec=[('模型 ID', 'SparkDesk-v3.1', '请求体 model 字段，区分大小写'), ('对应官方档位', '星火 Pro', 'domain：generalv3'),
              ('上下文窗口', '8,192', 'tokens，官方文档标注'), ('最大输出', '8,192', 'tokens，官方文档标注'),
              ('接口', 'Chat Completions', 'POST /v1/chat/completions'), ('输入 / 输出', '同价', None)],
        feat_h2='SparkDesk-v3.1 能做什么',
        feats=[('自然对话', '通过自然对话理解并执行任务，适合问答机器人和助手类应用。'),
               ('知识问答', '跨领域知识问答，覆盖常见的百科、办公和行业咨询场景。'),
               ('逻辑推理', '对规则判断、对比分析类问题给出推理过程和结论。'),
               ('数学解题', '模型广场列出数学问题求解能力，可用于学习辅导和公式类问答。'),
               ('代码理解', '解释代码片段、定位明显错误，适合开发辅助场景。'),
               ('联网搜索插件', '官方文档列出 Pro、Max、Ultra 档支持联网搜索插件；system 角色仅 Max 和 Ultra 支持。')],
        uses=[('01 · 问答', '知识问答与智能助手', '给内部员工或用户做一个常见问题助手，把规则和资料写进提示词，让模型据此回答。'),
              ('02 · 写作', '文案与摘要', '公众号文案、商品描述、会议纪要摘要等文本生成任务，输入输出同价，容易估算批量成本。'),
              ('03 · 教育', '数学与学习辅导', '给出解题步骤和思路讲解，适合学习类应用的原型验证。'),
              ('04 · 开发', '代码解释', '为内部工具加一个代码解释功能，需要系统提示词时换用 SparkDesk-v3.5。')],
        final_h2='用一个 Key 调用 SparkDesk-v3.1',
    ),
    'sparkdesk-v2.1': dict(
        title='SparkDesk-v2.1 API 价格与接入｜讯飞星火 2.x 旧版 - AnyAIGC',
        tier='早期 2.x 版本', mid='SparkDesk-v2.1',
        desc_lead='讯飞星火早期的 2.x 版本（接口版本 v2.1），对话、知识问答、逻辑推理和代码理解',
        notice=f'SparkDesk-v2.1 是讯飞星火较早的版本，讯飞开放平台当前文档的版本表已不再列出。新项目建议选 <a href="/zh/models/sparkdesk-v3.1">SparkDesk-v3.1</a> 或 <a href="/zh/models/sparkdesk-v3.5">SparkDesk-v3.5</a>，该型号是否可用以 <a href="{MARKET}">模型广场</a> 为准。',
        ask='用三句话向新同事解释什么是 API 限流，并举一个例子',
        answer="API 限流就是限制一个调用方在单位时间内能发多少次请求，防止个别用户把服务拖垮。超过限制的请求会被拒绝，通常返回 HTTP 429。比如接口规定每分钟最多 60 次，你在一分钟内发到第 61 次，就会收到 429，需要等下一分钟再试。",
        chips=['对话问答', '最低单价', '存量业务'],
        about_h2='讯飞星火早期的 2.x 版本',
        about=['SparkDesk-v2.1 是科大讯飞星火认知大模型早期的 2.x 版本接口。模型广场的说明是：具备跨领域知识和语言理解能力，通过自然对话理解并执行任务，覆盖语言理解、知识问答、逻辑推理、数学解题和代码理解。',
               '讯飞开放平台当前文档的版本表里已经没有这一档，所以本页不列官方的上下文窗口、最大输出和功能边界，避免写出没有来源的数字。它在 AnyAIGC 上的单价是三款里最低的，适合已经接入、不想改模型 ID 的存量业务，或对效果要求不高的低成本场景。',
               '在 AnyAIGC 上，<code>SparkDesk-v2.1</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，一个 Bearer Key 即可调用。新项目建议先评估 <a href="/zh/models/sparkdesk-v3.1">SparkDesk-v3.1</a> 或 <a href="/zh/models/sparkdesk-v3.5">SparkDesk-v3.5</a>。按 token 计费，并发不限。'],
        spec=[('模型 ID', 'SparkDesk-v2.1', '请求体 model 字段，区分大小写'), ('官方档位', '早期 2.x', '官方当前文档未列出'),
              ('上下文窗口', '未列出', '以实测为准'), ('最大输出', '未列出', '以实测为准'),
              ('接口', 'Chat Completions', 'POST /v1/chat/completions'), ('输入 / 输出', '同价', None)],
        feat_h2='SparkDesk-v2.1 能做什么',
        feats=[('自然对话', '通过自然对话理解并执行任务，适合简单的问答和助手类应用。'),
               ('知识问答', '跨领域知识问答，覆盖常见的百科和办公咨询场景。'),
               ('逻辑推理', '对简单的规则判断和对比分析类问题给出推理结论。'),
               ('数学解题', '模型广场列出数学问题求解能力，可用于基础的学习辅导问答。'),
               ('代码理解', '解释简短的代码片段，适合轻量的开发辅助。'),
               ('存量业务沿用', '已经接入 SparkDesk-v2.1 的应用，换到 AnyAIGC 只需改 base_url 和 Key，不用改模型 ID。')],
        uses=[('01 · 存量', '沿用旧模型的业务', '线上已经在用 SparkDesk-v2.1 的应用，保持模型 ID 不变，把请求地址换成 AnyAIGC 即可。'),
              ('02 · 低成本', '对效果要求不高的批量文本', '三款里单价最低，适合简单分类、改写这类对质量不敏感的批量任务，上线前请先用样本实测。'),
              ('03 · 对比', '新旧版本效果对比', '用同一批提示词跑 v2.1、v3.1、v3.5，量化升级前后的效果差异再决定是否迁移。'),
              ('04 · 原型', '低成本原型验证', '在不确定需求时先用低单价模型把流程跑通，再按效果换更高档位。')],
        final_h2='用一个 Key 调用 SparkDesk-v2.1',
    ),
}


def build(slug):
    m = M[slug]
    mid, name, tier = m['mid'], MODELS[slug]['name'], m['tier']
    s = slug
    price_in, price_out = p(s, 0), p(s, 1)
    others = [x for x in ('sparkdesk-v3.5', 'sparkdesk-v3.1', 'sparkdesk-v2.1') if x != s]
    link = lambda x: f'<a href="/zh/models/{x}">{MODELS[x]["name"]}</a>'

    faqs = [
        (f'{name} API 多少钱？',
         f'AnyAIGC 上 <code>{mid}</code> 按 token 计费：输入 {price_in}/百万 tokens，输出 {price_out}/百万 tokens，输入和输出同价。固定单价，没有订阅和月费，实时价格以模型广场为准。'),
        (f'{name} 的模型 ID 是什么？和讯飞星火是什么关系？',
         f'模型 ID 是 <code>{mid}</code>（区分大小写）。它是科大讯飞星火认知大模型的一个版本，AnyAIGC 提供 OpenAI 兼容的调用方式。注意它和 Apache Spark、Spark 邮箱等同名产品无关。'),
        (f'{name} 和其他 SparkDesk 型号怎么选？',
         f'{link(others[0])} 和 {link(others[1])} 是同系列的另外两款。版本号越大，对应讯飞官方的档位越新：v3.5 对应 Max，v3.1 对应 Pro，v2.1 是早期 2.x 版本。'
         f'需要系统提示词时选 v3.5；预算优先且质量要求不高时可以看 v2.1，上线前请用自己的数据实测。三款在 AnyAIGC 上都是输入输出同价。'),
        ('SparkDesk 兼容 OpenAI 接口吗？怎么调用？',
         f'兼容。{name} 走 <code>POST https://anyaigc.ai/v1/chat/completions</code>，请求和返回格式与 OpenAI Chat Completions 一致，OpenAI 官方 SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。讯飞官方的 WebSocket 签名鉴权不需要处理，只要 <code>Authorization: Bearer</code>。'),
        (f'{name} 的上下文窗口有多大？',
         ('讯飞官方文档标注该档位的上下文窗口和最大输出均为 8,192 tokens，长文档需要先分段或检索后再提问。通过 AnyAIGC 调用时以实测为准。' if s != 'sparkdesk-v2.1'
          else '讯飞开放平台当前文档的版本表已不再列出 2.x 版本，所以没有可引用的官方上下文数字。建议用你的真实输入长度实测，需要更确定的参数时选 SparkDesk-v3.1 或 SparkDesk-v3.5。')),
        faq_rpm(name, s),
        (f'{name} 停用了吗？',
         {'sparkdesk-v3.5': '讯飞官方文档称 Max 套餐已于 2026 年 3 月 10 日下线，后端升级为 Ultra。SparkDesk-v3.5 在 AnyAIGC 模型广场当前仍可调用，是否继续可用以模型广场为准。',
          'sparkdesk-v3.1': '讯飞开放平台当前文档的版本表仍列出 Pro 档。SparkDesk-v3.1 在 AnyAIGC 模型广场当前可调用，是否继续可用以模型广场为准。',
          'sparkdesk-v2.1': '讯飞开放平台当前文档的版本表已不再列出 2.x 版本，属于较早的旧版。SparkDesk-v2.1 在 AnyAIGC 模型广场当前仍可调用，新项目建议用 SparkDesk-v3.1 或 SparkDesk-v3.5，是否继续可用以模型广场为准。'}[s]),
    ] + faq_common(name, s)

    return dict(
        title=m['title'],
        desc=f'{mid} API：{m["desc_lead"]}。输入 {price_in}/1M、输出 {price_out}/1M，并发不限，支持对公转账与增值税专票。',
        og_desc=f'{mid} 输入 {price_in}/1M、输出 {price_out}/1M，输入输出同价。{m["desc_lead"]}，OpenAI 兼容接口，并发不限，支持对公转账与增值税专票。',
        og_alt=f'AnyAIGC {mid} API：输入 {price_in}/1M，并发不限',
        keywords=f'{mid} API,{mid},{mid} API 价格,{mid} 接入,{mid} API key,讯飞星火 API,星火大模型 API,星火 API 价格,星火 API 中转,SparkDesk API,星火 API OpenAI 兼容,{mid} API 企业,{mid} API 发票,星火 API 对公转账,AnyAIGC',
        crumb=f'{mid} API', product=f'{mid} API（AnyAIGC）', sku=s,
        product_desc=f'通过 AnyAIGC 调用讯飞星火 {mid}：OpenAI 兼容 /v1/chat/completions，按 token 计费，输入 {price_in}/1M、输出 {price_out}/1M，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow=f'科大讯飞 · {mid}',
                  h1=f'SparkDesk-<span class="sp-blue">{mid.split("-")[1]}</span><span class="o-sr"> API</span>',
                  lead=f'{m["desc_lead"]}。一个 API Key 调用，OpenAI 兼容接口，输入输出同价，按 token 计费。',
                  ask=m['ask'], answer=m['answer'], chips=m['chips'],
                  sub=f'<code>{mid}</code> 输入 {price_in} / 百万 tokens、输出 {price_out} / 百万 tokens，并发不限，支持对公转账与增值税专票。',
                  notice=m['notice'],
                  facts=[('模型 ID', mid), ('官方档位', tier), ('输入', f'{price_in} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2=m['about_h2'], paras=m['about'], spec=[(a, b, c) for a, b, c in m['spec'][:5]] + [('输入 / 输出', '同价', f'均为 {price_in} / 百万 tokens')]),
        features=dict(kicker='能力', h2=m['feat_h2'], items=m['feats']),
        pricing=dict(kicker='价格', h2=f'{name} API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入和输出同价。',
                     billing_label='计费要点', billing=billing(s), head=PRICE_HEAD, labels=LABELS,
                     caption=f'{mid} 每百万 tokens 价格（美元）', note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，用上面的单价相加得出。', costs=costs(s)),
        compare=dict(kicker='选型', h2='SparkDesk-v3.5、v3.1、v2.1 怎么选', lead='需要系统提示词选 v3.5，一般对话问答用 v3.1，存量业务和低成本场景看 v2.1。',
                     head=COMPARE_HEAD, rows=compare_rows(), caption='SparkDesk-v3.5、SparkDesk-v3.1、SparkDesk-v2.1 对比，价格为 AnyAIGC 每百万 tokens 美元', note=COMPARE_NOTE),
        uses=dict(kicker='使用场景', h2=f'{name} 适合做什么', items=m['uses']),
        qs=dict(kicker='快速开始', h2=f'三步接入 {name} API', steps=qs_steps(mid),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(mid, '用三句话解释什么是 API 限流')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(mid, '你是一名耐心的技术支持，回答简洁并给出示例。' if s == 'sparkdesk-v3.5' else None, '用户反馈接口返回 429，应该怎么排查？')),
                      ('stream', '流式输出', 'Python · stream=True', code_stream(mid, '给一个 SaaS 产品写 5 条更新日志。'))],
                callout=f'<strong>参数提示：</strong>模型 ID 区分大小写，写成 <code>{mid}</code>。返回格式与 OpenAI Chat Completions 一致，本次请求的 tokens 在 <code>usage</code> 字段里。该型号上下文有限，长文档请先分段或检索后再提问。',
                note=QS_NOTE),
        family_h2='SparkDesk 系列全部型号', family_lead='同一个 API Key 可以调用下面所有 SparkDesk 模型，按效果和预算选择。',
        faq_h2=f'{name} API 常见问题', faqs=faqs,
        final=dict(h2=m['final_h2'], p=f'注册后创建 API Key，几分钟就能在代码里用上 {mid}，余额对平台 300+ 模型通用。', other=f'{mid} API in English'),
        ent_name=name,
    )
