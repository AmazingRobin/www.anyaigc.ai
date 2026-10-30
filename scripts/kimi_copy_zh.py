# Kimi 系列专题页中文文案。被 scripts/kimi_pages.py 引用。
# 价格来自 kimi_data.PRICE（模型广场），官方参数来自 platform.kimi.ai 与 Hugging Face 模型卡（2026-10-26 读取）。
from kimi_data import PRICE, OFFICIAL, MODELS, REG, PRICING, SUPPORT, DOCS_CHAT, DOCS_CC, OFFICIAL_PRICING
from kimi_layout import cost, money, save_pct

UNIT = '百万 tokens'


def p(slug, i):
    return f'${PRICE[slug][i]}'


def o(slug, i):
    return f'${OFFICIAL[slug][i]}'


# ---------------- 共用 FAQ ----------------
def faq_common(name, slug):
    return [
        (f'国内可以直接调用 {name} API 吗？',
         f'可以。AnyAIGC 面向国内网络优化，通常无需额外代理即可调用 <code>https://anyaigc.ai</code>，按美元价格计费，支持微信支付、支付宝、USDT 和信用卡，企业可对公转账并开具增值税发票。'),
        (f'如何获取 {name} API Key？',
         f'在 <a href="{REG}">anyaigc.ai</a> 注册并充值，进入控制台创建令牌即可。同一个 Key 可以调用 Kimi 全系以及平台上 300+ 其他模型，不需要单独注册 Moonshot 开放平台账号。'),
        ('AnyAIGC 能开发票吗？支持增值税专票吗？',
         '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
        ('企业可以对公转账和签合同吗？',
         f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
        ('我的数据会被用于训练吗？',
         '不会。除法律法规要求外，AnyAIGC 不对你的输入输出内容做持久化存储，也不会用于训练模型，请求通过 HTTPS 加密传输，详见 AnyAIGC <a href="/privacy">隐私政策</a>。模型本身的数据政策以 Moonshot AI 官方条款为准。'),
    ]


def faq_cc(name, model):
    return (f'可以在 Claude Code 里使用 {name} 吗？',
            f'可以。在 <code>~/.claude/settings.json</code> 的 env 中设置 <code>ANTHROPIC_BASE_URL</code> 为 <code>https://anyaigc.ai</code>、<code>ANTHROPIC_AUTH_TOKEN</code> 为你的 API Key、<code>ANTHROPIC_MODEL</code> 为 <code>{model}</code>，然后运行 <code>claude</code> 即可。')


def faq_rpm(name, slug):
    return ('并发和速率有限制吗？',
            f'AnyAIGC 对 <code>{slug}</code> 不设并发限制，所有用户默认享有，适合批量任务、CI 流水线和多 Agent 并行。Moonshot 官方平台按充值等级限制并发、RPM、TPM 和 TPD，通过 AnyAIGC 调用不受这些等级限制。')


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
    return f'''import os
from openai import OpenAI

client = OpenAI(
    base_url="https://anyaigc.ai/v1",
    api_key=os.environ["ANYAIGC_API_KEY"],
)

resp = client.chat.completions.create(
    model="{model}",
    messages=[
        {{"role": "system", "content": "{system}"}},
        {{"role": "user", "content": "{user}"}},
    ],
)
msg = resp.choices[0].message
print(getattr(msg, "reasoning_content", None))  # 思考过程（如有）
print(msg.content)
print(resp.usage)'''


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
    # 先输出思考增量 reasoning_content，再输出最终回答 content
    reasoning = getattr(delta, "reasoning_content", None)
    if reasoning:
        print(reasoning, end="", flush=True)
    if delta.content:
        print(delta.content, end="", flush=True)
print()'''


def code_tools(model):
    return f'''import json
import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

tools = [{{
    "type": "function",
    "function": {{
        "name": "run_tests",
        "description": "在仓库里运行指定路径的单元测试，返回失败用例",
        "parameters": {{
            "type": "object",
            "properties": {{"path": {{"type": "string", "description": "测试文件或目录"}}}},
            "required": ["path"],
        }},
    }},
}}]
messages = [{{"role": "user", "content": "跑一下 tests/test_api.py，告诉我哪些用例失败了。"}}]

resp = client.chat.completions.create(model="{model}", messages=messages, tools=tools)
msg = resp.choices[0].message
# 多轮和工具调用时，把完整的 assistant 消息（含 reasoning_content 和 tool_calls）原样放回 messages
messages.append(msg.model_dump(exclude_none=True))
for call in msg.tool_calls or []:
    args = json.loads(call.function.arguments)
    result = {{"path": args["path"], "failed": ["test_login_timeout"]}}  # 这里换成真实的执行结果
    messages.append({{"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)}})

final = client.chat.completions.create(model="{model}", messages=messages, tools=tools)
print(final.choices[0].message.content)'''


def code_vision(model):
    return f'''import base64
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

image = base64.b64encode(Path("screenshot.png").read_bytes()).decode()
resp = client.chat.completions.create(
    model="{model}",
    messages=[{{
        "role": "user",
        "content": [
            {{"type": "image_url", "image_url": {{"url": f"data:image/png;base64,{{image}}"}}}},
            {{"type": "text", "text": "这是一个网页截图，用 HTML + CSS 还原它。"}},
        ],
    }}],
)
print(resp.choices[0].message.content)'''


def code_effort(model):
    return f'''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# K3 系列始终开启思考，用 reasoning_effort 调整深度：low / high / max（默认 max）
resp = client.chat.completions.create(
    model="{model}",
    reasoning_effort="low",
    messages=[{{"role": "user", "content": "把这段 SQL 改写成使用窗口函数的版本：SELECT ..."}}],
)
print(resp.choices[0].message.content)'''


def cc_code(model):
    return f'''{{
  "env": {{
    "ANTHROPIC_BASE_URL": "https://anyaigc.ai",
    "ANTHROPIC_AUTH_TOKEN": "sk-你的 API Key",
    "ANTHROPIC_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "{model}",
    "API_TIMEOUT_MS": "300000"
  }}
}}'''


def cc(name, model, lead, callout):
    return dict(
        kicker='Claude Code', h2=f'在 Claude Code 中使用 {name}', lead=lead,
        steps=['<strong>安装 Claude Code</strong>：按官方方式安装（如 <code>npm install -g @anthropic-ai/claude-code</code>）。',
               '<strong>写入配置</strong>：编辑 <code>~/.claude/settings.json</code>，把下面的 env 加进去，<code>ANTHROPIC_AUTH_TOKEN</code> 换成你在 AnyAIGC 创建的 Key。',
               f'<strong>开始使用</strong>：在项目目录运行 <code>claude</code>，输入 <code>/model</code> 可以确认当前模型是 <code>{model}</code>。'],
        code=cc_code(model), callout=callout,
        note=f'完整步骤和常见报错见 <a href="{DOCS_CC}" target="_blank" rel="noopener">Claude Code 安装与使用教程</a>，教程里的模型名换成 <code>{model}</code> 即可。')


def qs_steps(model):
    return ['<strong>注册并充值</strong>：在 <a href="' + REG + '">anyaigc.ai</a> 注册账号，最低 $1 起充，余额对平台所有模型通用。',
            '<strong>创建 API Key</strong>：在控制台创建令牌，复制以 <code>sk-</code> 开头的 Key，存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'<strong>发起请求</strong>：请求 <code>POST https://anyaigc.ai/v1/chat/completions</code>，<code>model</code> 填 <code>{model}</code>，鉴权用 <code>Authorization: Bearer</code>。OpenAI SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。']


QS_NOTE = f'完整参数见 <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions 接口文档</a>，文档示例里的模型名换成对应的 Kimi 模型 ID 即可。'

PRICE_HEAD = [('计费项', ''), ('模型名', ''), ('AnyAIGC', 'o-num o-hl'), ('Moonshot 官方', 'o-num'), ('节省', 'o-num')]
LABELS = [('输入', '每 100 万 tokens'), ('输出', '每 100 万 tokens，含思考'), ('缓存命中', '每 100 万 tokens')]


def pricing_note(slug):
    q = f'?keyword={slug}' if slug else '?keyword=kimi'
    return (f'价格单位为美元，按实际消耗的 tokens 计费，输出包含思考 tokens，重复的请求前缀自动按缓存命中价计费。'
            f'官方价来自 <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">Kimi 开放平台价格页</a>（美元价），'
            f'表中为模型广场最低价，实时价格以 <a href="{PRICING}{q}">AnyAIGC 模型广场</a> 为准。')


def cost_card(slug, title, calc, inp=0, out=0, cache=0, n=1):
    a = money(cost(slug, inp, out, cache, n))
    b = money(cost(slug, inp, out, cache, n, official=True))
    return (title, calc, a, f'官方 <s>{b}</s>')


def offers(slug):
    return [('输入（每 100 万 tokens）', PRICE[slug][0]), ('输出（每 100 万 tokens）', PRICE[slug][1]),
            ('缓存命中（每 100 万 tokens）', PRICE[slug][2])]


FAMILY = [
    ('kimi', '', ('Kimi 全系总览', 'K3.1 Pro、K3、K2.7 Code、K2.6 价格对比与选型')),
    ('kimi-k3.1-pro', '最新', f'K3.1 系列首款，1M 上下文 · 输入 {p("kimi-k3.1-pro", 0)} / 1M'),
    ('kimi-k3', '', f'2.8T 参数开放权重，1M 上下文 · 输入 {p("kimi-k3", 0)} / 1M'),
    ('kimi-k2.7-code', '编程', f'K2.6 的编程强化版，强制思考 · 输入 {p("kimi-k2.7-code", 0)} / 1M'),
    ('kimi-k2.6', '', f'通用多模态 Agent，可关闭思考 · 输入 {p("kimi-k2.6", 0)} / 1M'),
]


def build(slug):
    return {'kimi': hub, 'kimi-k3.1-pro': k31, 'kimi-k3': k3, 'kimi-k2.7-code': k27, 'kimi-k2.6': k26}[slug]()


# ======================================================================
# 总览页
# ======================================================================
def hub():
    k31, k3, c, k6 = 'kimi-k3.1-pro', 'kimi-k3', 'kimi-k2.7-code', 'kimi-k2.6'
    faqs = [
        ('Kimi API 多少钱？',
         f'AnyAIGC 上 Kimi 系列按 token 计费，每百万 tokens：<code>kimi-k3.1-pro</code> 输入 {p(k31, 0)}、输出 {p(k31, 1)}、缓存命中 {p(k31, 2)}；<code>kimi-k3</code> 输入 {p(k3, 0)}、输出 {p(k3, 1)}、缓存命中 {p(k3, 2)}；'
         f'<code>kimi-k2.7-code</code> 输入 {p(c, 0)}、输出 {p(c, 1)}、缓存命中 {p(c, 2)}；<code>kimi-k2.6</code> 输入 {p(k6, 0)}、输出 {p(k6, 1)}、缓存命中 {p(k6, 2)}。'
         f'约为 Moonshot 官方美元价的 4 折，实时价格以模型广场为准。'),
        ('AnyAIGC 上有哪些 Kimi 模型？模型 ID 是什么？',
         '本页介绍四款：<code>kimi-k3.1-pro</code>（K3.1 系列首款，1M 上下文）、<code>kimi-k3</code>（上一代旗舰，2.8T 参数开放权重模型）、<code>kimi-k2.7-code</code>（编程向 Agent 模型）、<code>kimi-k2.6</code>（通用多模态 Agent 模型）。'
         '调用时把模型 ID 写在请求体的 <code>model</code> 字段里，切换模型只需要改这一个字段。'),
        ('Kimi K3.1 Pro、K3、K2.7 Code 和 K2.6 怎么选？',
         f'需要 1M 上下文、最难的长程编程、3D 创作和金融研究时选 <a href="/zh/models/kimi-k3.1-pro">Kimi K3.1 Pro</a>，它是最新一代，单价还比 K3 低三分之一；已经在用 K3 的业务可以继续用 <a href="/zh/models/kimi-k3">K3</a>；日常写代码、跑 Coding Agent 选 <a href="/zh/models/kimi-k2.7-code">K2.7 Code</a>，官方称它在 Kimi Code Bench v2 上比 K2.6 提升 21.8%；'
         f'需要非思考模式、快速响应或通用对话选 <a href="/zh/models/kimi-k2.6">K2.6</a>。K2.7 Code 和 K2.6 单价相同，约为 K3.1 Pro 的一半。'),
        ('Kimi API 兼容 OpenAI 吗？',
         '兼容。四款模型都走 <code>POST https://anyaigc.ai/v1/chat/completions</code>，请求和返回格式与 OpenAI Chat Completions 一致，OpenAI 官方 SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。思考过程在返回的 <code>reasoning_content</code> 字段里。'),
        faq_cc('Kimi', 'kimi-k3.1-pro'),
        ('上下文窗口有多大？',
         'Moonshot 官方公布：Kimi K3.1 Pro 和 K3 支持 1,048,576 tokens 上下文；K2.7 Code 和 K2.6 支持 262,144 tokens（256K）。四款都支持图片输入和工具调用。'),
        ('Kimi 模型是开源的吗？可以商用吗？',
         'Kimi K3、K2.7 Code 和 K2.6 都由 Moonshot AI 在 Hugging Face 公开了模型权重；官方表示 K3.1 Pro 的完整权重将在 2026 年 11 月 4 日前发布。通过 AnyAIGC 调用 API 不需要自己部署。模型许可和商用授权以 Moonshot AI 官方条款为准。'),
        faq_rpm('Kimi', 'kimi-k3.1-pro、kimi-k3、kimi-k2.7-code、kimi-k2.6'),
    ] + faq_common('Kimi', 'kimi')
    faqs[7] = ('并发和速率有限制吗？',
               'AnyAIGC 对 Kimi 系列不设并发限制，所有用户默认享有，适合批量任务、CI 流水线和多 Agent 并行。Moonshot 官方平台按充值等级限制并发、RPM、TPM 和 TPD，通过 AnyAIGC 调用不受这些等级限制。')
    rows = []
    return dict(
        title='Kimi API 价格与接入｜K3.1 Pro / K3 / K2.7 Code - AnyAIGC',
        desc=f'Kimi API 全系价格：kimi-k3.1-pro 输入 {p(k31, 0)}/1M、kimi-k2.7-code 与 kimi-k2.6 输入 {p(c, 0)}/1M，约官方 4 折，可接入 Claude Code，并发不限，支持对公转账。',
        og_desc=f'Kimi K3.1 Pro、K3、K2.7 Code、K2.6 一个 Key 调用，约 Moonshot 官方价 4 折，OpenAI 兼容接口，可接入 Claude Code，并发不限，支持对公转账与增值税专票。',
        og_alt='AnyAIGC Kimi API：K3.1 Pro、K3、K2.7 Code、K2.6 约官方价 4 折',
        keywords='Kimi API,Kimi API 价格,Kimi API key,月之暗面 API,Moonshot API,Kimi 模型 API,Kimi K3.1 Pro API,Kimi K3 API,Kimi K2.7 Code API,Kimi K2.6 API,Kimi API 国内,Kimi Claude Code,Kimi API 企业,Kimi API 发票,Kimi API 对公转账,AnyAIGC',
        crumb='Kimi API', product='Kimi API（AnyAIGC）', sku='kimi',
        product_desc='通过 AnyAIGC 调用 Moonshot AI 的 Kimi 系列模型（kimi-k3.1-pro、kimi-k3、kimi-k2.7-code、kimi-k2.6）：OpenAI 兼容 /v1/chat/completions，按 token 计费，约官方价 4 折，并发不限。',
        offers=[(f'{n} 输入（每 100 万 tokens）', PRICE[s][0]) for s, n in ((k31, 'Kimi K3.1 Pro'), (k3, 'Kimi K3'), (c, 'Kimi K2.7 Code'), (k6, 'Kimi K2.6'))]
        + [(f'{n} 输出（每 100 万 tokens）', PRICE[s][1]) for s, n in ((k31, 'Kimi K3.1 Pro'), (k3, 'Kimi K3'), (c, 'Kimi K2.7 Code'), (k6, 'Kimi K2.6'))],
        hero=dict(eyebrow='Moonshot AI · Kimi',
                  h1='Kimi <span class="k-blue">API</span>',
                  lead='Kimi K3.1 Pro、K3、K2.7 Code、K2.6 四款模型，一个 API Key 全部调用，价格约为 Moonshot 官方的 4 折。',
                  ask='用 Kimi 重构这个仓库的支付模块，并补齐单元测试',
                  chips=['长程编程', '1M 上下文', 'Agent'],
                  sub=f'OpenAI 兼容的 <code>/v1/chat/completions</code>，也能直接接入 Claude Code。<code>kimi-k2.7-code</code> 与 <code>kimi-k2.6</code> 输入 {p(c, 0)} / 百万 tokens 起，并发不限。',
                  facts=[('型号', 'K3.1 Pro · K3 · K2.7 Code · K2.6'), ('上下文', '最高 1M'), ('输入', f'{p(c, 0)} / 1M 起'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        models=dict(kicker='型号', h2='Kimi 系列四款模型', lead='同一个 Key、同一个接口，按任务换模型 ID 即可。',
                    unit_in='1M 输入', unit_out='1M 输出', go='查看专题',
                    items=[(k31, '最新', 'K3.1 系列首款，在 K3 基础上加大后训练，代码、3D 创作、金融研究和长程 Agent 提升明显。', ['1,048,576 tokens 上下文', '幻觉率从 23.4% 降到 8.3%', '单价比 K3 低三分之一']),
                           (k3, '', '上一代旗舰，Moonshot 开源的 2.8T 参数模型，面向长程编程、知识工作和深度推理。', ['1,048,576 tokens 上下文', '始终思考，reasoning_effort 可调', '原生视觉理解']),
                           (c, '编程', '基于 K2.6 的编程向 Agent 模型，长上下文里更稳地遵循指令，思考 tokens 更少。', ['256K 上下文', '强制思考，交错工具调用', 'Kimi Code Bench v2 62.0']),
                           (k6, '', '开源原生多模态 Agent 模型，支持思考和非思考两种模式，兼顾编码与通用对话。', ['256K 上下文', '思考 / 非思考可切换', 'SWE-Bench Verified 80.2'])]),
        pricing=dict(kicker='价格', h2='Kimi API 价格', lead='按 token 计费，固定单价，没有订阅和月费。四款模型都约为 Moonshot 官方美元价的 40%。',
                     billing_label='计费要点',
                     billing=[('按 token 计费', '输入、输出、缓存分别计价'), ('约 4 折', '相比 Moonshot 官方美元价'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')],
                     head=[('计费项', ''), ('AnyAIGC', 'o-num o-hl'), ('Moonshot 官方', 'o-num'), ('节省', 'o-num')],
                     labels=LABELS, caption='Kimi 系列每百万 tokens 价格（美元），AnyAIGC 与 Moonshot 官方对比',
                     note=pricing_note(''),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 Moonshot 官方价。',
                     costs=[cost_card(k31, 'K3.1 Pro · Agent 编程 20 轮', '每轮 5 万 tokens 缓存命中 + 5,000 输入 + 3,000 输出', 5000, 3000, 50000, 20),
                            cost_card(c, 'K2.7 Code · 审查 100 个 PR', '每个 PR 2 万 tokens 输入 + 2,000 输出', 20000, 2000, 0, 100),
                            cost_card(k6, 'K2.6 · 1 万条工单分类', '每条 2,000 tokens 输入 + 300 输出', 2000, 300, 0, 10000)]),
        compare=dict(kicker='选型', h2='Kimi K3.1 Pro、K3、K2.7 Code、K2.6 怎么选', lead='最难的任务交给 K3.1 Pro，日常编码用 K2.7 Code，要快速响应或关掉思考用 K2.6。',
                     head=[('对比项', ''), ('K3.1 Pro', 'o-num o-hl'), ('K3', 'o-num'), ('K2.7 Code', 'o-num'), ('K2.6', 'o-num')],
                     rows=[('定位', '', '最新旗舰', '上一代旗舰', '编程 Agent', '通用多模态 Agent'),
                           ('总参数', '', '3T 级', '2.8T', '1T', '1T'),
                           ('上下文', '', '1M', '1M', '256K', '256K'),
                           ('思考模式', '', '始终开启', '始终开启', '始终开启', '可开可关'),
                           ('AnyAIGC 输入', '每百万 tokens', p(k31, 0), p(k3, 0), p(c, 0), p(k6, 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(k31, 1), p(k3, 1), p(c, 1), p(k6, 1)),
                           ('缓存命中', '每百万 tokens', p(k31, 2), p(k3, 2), p(c, 2), p(k6, 2))],
                     caption='Kimi K3.1 Pro、K3、K2.7 Code、K2.6 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自 Moonshot AI 在 Hugging Face 和 Kimi 开放平台公布的资料，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。'),
        uses=dict(kicker='使用场景', h2='用 Kimi API 做什么',
                  items=[('01 · 长程编程', '大仓库重构和跨文件改动', 'K3.1 Pro 的 1M 上下文能放下整个代码库，配合终端工具连续工作；预算紧时换成 K2.7 Code，单价约为 K3.1 Pro 的一半。'),
                         ('02 · Coding Agent', 'Claude Code、CI 和自动修复', '把 Kimi 接进 Claude Code 或自己的 Agent 框架，跑测试、读报错、改代码。AnyAIGC 不限并发，多个 Agent 可以同时跑。'),
                         ('03 · 前端与设计', '从截图生成可上线的界面', '三款模型都能读图。把设计稿或网页截图交给模型，直接输出 HTML、CSS 或组件代码。'),
                         ('04 · 知识工作', '金融研究与长文档', '财报、合同、调研资料整份放进上下文，抽取字段、搭建财务模型、生成报告。官方公布 K3.1 Pro 的 OfficeQA Pro v2 为 64.4。')]),
        qs=dict(kicker='快速开始', h2='三步接入 Kimi API', steps=qs_steps('kimi-k3.1-pro'),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl('kimi-k3.1-pro', '用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py('kimi-k2.7-code', '你是资深后端工程师，回答要给出可运行的代码。', '用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('stream', '流式输出', 'Python · stream=True', code_stream('kimi-k2.6', '给一个 SaaS 产品写 5 条更新日志。'))],
                callout='<strong>参数提示：</strong>Kimi 的思考过程在 <code>reasoning_content</code> 字段，流式输出时先返回思考增量，再返回最终回答。多轮对话和工具调用时，要把 API 返回的完整 assistant 消息（包括 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('Kimi', 'kimi-k3.1-pro', '把 Claude Code 的模型换成 Kimi：改一个配置文件，终端里的编程 Agent 就由 Kimi 驱动。',
              '<strong>换模型：</strong>想用更便宜的编程模型，把配置里的 <code>kimi-k3.1-pro</code> 全部换成 <code>kimi-k2.7-code</code> 即可。K3.1 Pro 有 1M 上下文，适合大仓库；K2.7 Code 单价约为它的一半。'),
        family_h2='Kimi 系列全部型号', family_lead='同一个 API Key 可以调用下面所有 Kimi 模型，按任务难度和预算选择。',
        faq_h2='Kimi API 常见问题', faqs=faqs,
        final=dict(h2='用约 4 折的价格跑 Kimi', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 Kimi K3.1 Pro、K3、K2.7 Code 和 K2.6。',
                   other='Kimi API in English'),
        ent_name='Kimi',
    )


# ======================================================================
# Kimi K3.1 Pro
# ======================================================================
def k31():
    s = 'kimi-k3.1-pro'
    faqs = [
        ('Kimi K3.1 Pro API 多少钱？',
         f'AnyAIGC 上 <code>kimi-k3.1-pro</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'Moonshot 官方美元价为输入 {o(s, 0)}、输出 {o(s, 1)}、缓存命中 {o(s, 2)}，AnyAIGC 约为官方价的 40%（约 4 折）。输出包含思考 tokens，实时价格以模型广场为准。'),
        ('Kimi K3.1 Pro 的模型 ID 是什么？上下文多大？',
         '模型 ID 是 <code>kimi-k3.1-pro</code>。Moonshot 官方公布的上下文窗口为 1,048,576 tokens（1M），<code>max_completion_tokens</code> 默认 131,072，最大可设到 1,048,576。'),
        ('Kimi K3.1 Pro 和 K3 有什么区别？',
         f'官方说明 K3.1 Pro 是在 <a href="/zh/models/kimi-k3">Kimi K3</a> 基础上用大幅增加的后训练算力得到的版本，在数百个下游领域做联合强化学习。官方公布的提升包括：长程编程（Kimi Code Bench 3.0 从 55.95 到 61.2）、金融研究（内部评测从 58.8 到 70.4）、事实准确性（逐条事实幻觉率从 23.4% 降到 8.3%）。'
         f'参数约束与 K3 相同，迁移只要改模型名。AnyAIGC 上 K3.1 Pro 输入 {p(s, 0)}、输出 {p(s, 1)}，比 K3 低三分之一。'),
        ('怎么调整 Kimi K3.1 Pro 的思考深度？',
         'K3.1 Pro 始终开启思考，不能关闭。用请求体顶层的 <code>reasoning_effort</code> 字段调整思考深度，可选 <code>low</code>、<code>high</code>、<code>max</code>，默认 <code>max</code>。<code>temperature</code>、<code>top_p</code> 等采样参数由官方固定，请求里不用传。'),
        ('Kimi K3.1 Pro 支持工具调用、图片和视频输入吗？',
         '支持。官方文档列出函数调用（<code>tools</code> / <code>tool_choice</code>）、结构化输出（<code>json_schema</code>）、流式输出，以及图片和视频输入。多轮和工具调用时，需要把返回的完整 assistant 消息（含 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。'),
        faq_cc('Kimi K3.1 Pro', s),
        ('Kimi K3.1 Pro 是开源的吗？',
         'Moonshot 称 K3.1 Pro 是其迄今最强的 3T 级开放权重模型，官方表示完整权重将在 2026 年 11 月 4 日前发布。通过 AnyAIGC 调用 API 不需要自己部署，模型许可和商用授权以 Moonshot AI 官方条款为准。'),
        faq_rpm('Kimi K3.1 Pro', s),
    ] + faq_common('Kimi K3.1 Pro', s)
    return dict(
        title='Kimi K3.1 Pro API 价格与接入｜1M 上下文 约官方 4 折 - AnyAIGC',
        desc=f'kimi-k3.1-pro API：Kimi K3.1 系列首款，1M 上下文，长程编程与金融研究更强，输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方价 4 折，并发不限，支持对公转账与专票。',
        og_desc=f'kimi-k3.1-pro 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约 Moonshot 官方价 4 折。K3.1 系列首款，1M 上下文，代码、3D 创作和金融研究提升明显，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC Kimi K3.1 Pro API：约官方价 4 折',
        keywords='Kimi K3.1 Pro API,kimi-k3.1-pro,Kimi K3.1 Pro API 价格,Kimi K3.1 Pro 接入,Kimi K3.1 Pro 和 K3 区别,Kimi K3.1 Pro Claude Code,Kimi K3.1 API,月之暗面 K3.1 Pro,Moonshot K3.1 Pro API,Kimi API,Kimi K3.1 Pro API 企业,Kimi K3.1 Pro API 发票,Kimi API 对公转账,AnyAIGC',
        crumb='Kimi K3.1 Pro API', product='Kimi K3.1 Pro API（AnyAIGC）', sku=s,
        product_desc='通过 AnyAIGC 调用 Moonshot AI Kimi K3.1 Pro（kimi-k3.1-pro）：OpenAI 兼容 /v1/chat/completions，1M 上下文，按 token 计费，约官方价 4 折，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow='Moonshot AI · kimi-k3.1-pro',
                  h1='Kimi <span class="k-blue">K3.1 Pro</span><span class="o-sr"> API</span>',
                  lead='Kimi K3.1 系列首款，1M 上下文，代码、3D 创作、金融研究和长程 Agent 都比 K3 更强，单价还低三分之一。在 AnyAIGC 调用约为官方价的 4 折。',
                  ask='读完这三家公司的年报，搭一个可比公司估值模型并写出结论',
                  chips=['1M 上下文', '长程 Agent', '金融研究'],
                  sub=f'<code>kimi-k3.1-pro</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='K3.1 系列首款，后训练全面加强',
                   paras=['Moonshot AI 称 Kimi K3.1 Pro 是全新 K3.1 系列的第一个模型，也是其迄今最强的 3T 级开放权重模型。官方说明它是 Kimi K3 的后训练版本，投入了大幅增加的后训练算力，并在数百个下游领域做联合强化学习。',
                          '官方公布的提升集中在四个方向：长程编程（支持 Unity、Unreal Engine、Godot，前端和 Three.js 的构图、排版和动画更完整）、3D 创作（可直接写 Blender 和 CAD 脚本做参数化建模）、金融研究（OfficeQA Pro v2 得分 64.4），以及更低的幻觉率。上下文 1,048,576 tokens，思考始终开启，支持文本、图片和视频输入。',
                          '在 AnyAIGC 上，<code>kimi-k3.1-pro</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，参数约束和 K3 相同，从 K3 迁移只需要改模型名。也能在 Claude Code 里直接使用，并发不限。'],
                   spec=[('上下文窗口', '1,048,576', '输入 tokens 上限'), ('最大输出', '131,072', '默认值，最大可设到 1,048,576'),
                         ('参数规模', '3T 级', '基于 Kimi K3 后训练'), ('输入模态', '文本、图片、视频', '原生视觉理解'),
                         ('思考模式', '始终开启', 'reasoning_effort：low / high / max'), ('权重', '即将开放', '官方称 11 月 4 日前发布')]),
        features=dict(kicker='能力', h2='Kimi K3.1 Pro 能做什么',
                      items=[('长程编程', '官方公布 Kimi Code Bench 3.0 长程编程 61.2（K3 为 55.95），SWE Marathon v1.1 为 51.7，Terminal-Bench 4.0 为 65.7。'),
                             ('游戏与 3D 前端', '覆盖 Unity、Unreal Engine、Godot 和 Three.js，官方称生成的前端在构图、排版、动画和完成度上更好。'),
                             ('3D 创作与 CAD', '擅长参数化建模，不用 MCP 连接器也能直接写 Blender 和 CAD 脚本。官方公布 BenchCAD（带工具）为 92.7。'),
                             ('金融研究', '官方内部评测：金融研究从 58.8 提升到 70.4，财务建模从 50.4 提升到 57.6；OfficeQA Pro v2 为 64.4。'),
                             ('更少幻觉', '官方称逐条事实幻觉率从 K3 的 23.4% 降到 8.3%，有事实错误的回答比例降到 K3 的 42.4%。'),
                             ('长程 Agent', '官方公布 BrowseComp 92.1、HLE-Full（带工具）70.0、Automation Bench-AA 73.3。AnyAIGC 不限并发，适合多 Agent 并行。')]),
        pricing=dict(kicker='价格', h2='Kimi K3.1 Pro API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入、输出、缓存命中都约为 Moonshot 官方美元价的 40%，也比 K3 低三分之一。',
                     billing_label='计费要点',
                     billing=[('按 token 计费', '输入、输出、缓存分别计价'), ('约 4 折', '相比 Moonshot 官方美元价'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')],
                     head=PRICE_HEAD, labels=LABELS, caption='kimi-k3.1-pro 每百万 tokens 价格（美元），AnyAIGC 与 Moonshot 官方对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 Moonshot 官方价。',
                     costs=[cost_card(s, 'Agent 编程 20 轮', '每轮 5 万 tokens 缓存命中 + 5,000 输入 + 3,000 输出', 5000, 3000, 50000, 20),
                            cost_card(s, '50 万 tokens 财报分析', '50 万 tokens 输入 + 5,000 输出', 500000, 5000),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='Kimi K3.1 Pro 的官方基准成绩', lead='Moonshot AI 在 K3.1 Pro 技术博客中公布的成绩（max 思考深度），并列出了同场对比的其他模型。',
                   chart=('K3.1 Pro 对比 K3 · 官方评测', [('K3.1 Pro · 长程编程', 61.2, True), ('K3 · 长程编程', 55.95, False),
                                                       ('K3.1 Pro · 金融研究', 70.4, True), ('K3 · 金融研究', 58.8, False),
                                                       ('K3.1 Pro · 财务建模', 57.6, True), ('K3 · 财务建模', 50.4, False)]),
                   head=[('基准', ''), ('K3.1 Pro', 'o-num o-hl'), ('Claude Opus 5.5', 'o-num'), ('GPT-6 Astra', 'o-num')],
                   rows=[('Terminal-Bench 4.0', '终端编程', '65.7', '66.4', '58.2'), ('SWE Marathon v1.1', '长程软件工程', '51.7', '46.3', '42.5'),
                         ('DeepSWE v1.1', '软件工程', '75.5', '74.2', '74.1'), ('Kimi Code Bench 3.0', '长程编程，内部', '61.2', '58.5', '66.5'),
                         ('BenchCAD', 'CAD 建模，带工具', '92.7', '96.2', '95.9'), ('HLE-Full', '综合推理，带工具', '70.0', '67.7', '57.2'),
                         ('BrowseComp', '网页检索 Agent', '92.1', '90.8', '91.5'), ('OSWorld V2.1', '计算机操作', '79.6', '81.8', '75.8'),
                         ('OfficeQA Pro v2', '办公与金融问答', '64.4', '62.2', '54.4'), ('Frontier Finance', '金融', '58.6', '56.7', '45.0'),
                         ('Automation Bench-AA', '自动化 Agent', '73.3', '69.5', '68.5'), ('GDPval-AA v2.1', '知识工作，Elo', '1846', '1866', '1573'),
                         ('GPQA-Diamond', '科学推理', '94.2', '93.9', '96.1'), ('MMMU-Pro', '多模态理解', '84.1', '87.7', '86.9')],
                   caption='Kimi K3.1 Pro 官方基准成绩及同场对比（Moonshot AI 公布）',
                   note='数据来自 <a href="https://www.kimi.com/blog/kimi-k3-1-pro" target="_blank" rel="noopener">Kimi K3.1 Pro 技术博客</a>，为 Moonshot AI 公布的 max 思考深度成绩，大部分编程成绩使用 Claude Code 作为测试框架。K3 对比数据为官方内部评测。'),
        compare=dict(kicker='选型', h2='Kimi K3.1 Pro 和 K3、K2.7 Code 怎么选', lead='新项目优先用 K3.1 Pro：比 K3 更新、更便宜。高频、预算敏感的编码任务可以用 K2.7 Code。',
                     head=[('对比项', ''), ('K3.1 Pro', 'o-num o-hl'), ('K3', 'o-num'), ('K2.7 Code', 'o-num')],
                     rows=[('定位', '', '最新旗舰', '上一代旗舰', '编程 Agent'), ('参数规模', '', '3T 级', '2.8T', '1T'),
                           ('上下文', '', '1M', '1M', '256K'), ('输入模态', '', '文本、图片、视频', '文本、图片', '文本、图片'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p('kimi-k3', 0), p('kimi-k2.7-code', 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p('kimi-k3', 1), p('kimi-k2.7-code', 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p('kimi-k3', 2), p('kimi-k2.7-code', 2))],
                     caption='Kimi K3.1 Pro、K3、K2.7 Code 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自 Moonshot AI 公开资料，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。详见 <a href="/zh/models/kimi-k3">Kimi K3 API</a> 和 <a href="/zh/models/kimi-k2.7-code">Kimi K2.7 Code API</a>。'),
        uses=dict(kicker='使用场景', h2='Kimi K3.1 Pro 适合做什么',
                  items=[('01 · 长程编程', '大仓库与游戏开发', '把整个代码库放进 1M 上下文，跨模块重构、迁移，或者在 Unity、Godot、Three.js 项目里连续迭代。'),
                         ('02 · 金融研究', '财报、估值和行业研究', '整份年报、招股书和研报放进上下文，抽取数据、搭财务模型、写研究结论。重复引用的资料按缓存命中价计费。'),
                         ('03 · 3D 创作', '参数化建模与 CAD 脚本', '描述零件或场景，让模型直接写 Blender、CAD 脚本，再根据渲染截图修正。'),
                         ('04 · Agent', '长周期自主任务', '在 Claude Code 或自研 Agent 里跑几十上百步的任务。幻觉率更低，长链路里更少出错。AnyAIGC 不限并发。')]),
        qs=dict(kicker='快速开始', h2='三步接入 Kimi K3.1 Pro API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, '用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, '你是资深金融分析师，结论要给出数据来源。', '比较两家公司近三年的毛利率变化，并解释原因。')),
                      ('effort', '思考深度', 'Python · reasoning_effort', code_effort(s)),
                      ('stream', '流式输出', 'Python · stream=True', code_stream(s, '解释为什么天空是蓝色的。'))],
                callout='<strong>参数提示：</strong>K3.1 Pro 思考始终开启，思考过程在 <code>reasoning_content</code> 字段。<code>temperature</code>、<code>top_p</code> 等采样参数由官方固定，请求里不要传。多轮对话和工具调用时，要把 API 返回的完整 assistant 消息（包括 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('Kimi K3.1 Pro', s, '把 Claude Code 的模型换成 Kimi K3.1 Pro：1M 上下文，官方的大部分编程成绩就是用 Claude Code 测出来的。',
              '<strong>省钱搭配：</strong>可以把 <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> 换成 <code>kimi-k2.7-code</code>，让 Claude Code 的轻量子任务用更便宜的模型，主任务继续用 K3.1 Pro。'),
        family_h2='Kimi 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 Kimi 模型，按任务难度和预算选择。',
        faq_h2='Kimi K3.1 Pro API 常见问题', faqs=faqs,
        final=dict(h2='用约 4 折的价格跑 Kimi K3.1 Pro', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 kimi-k3.1-pro。', other='Kimi K3.1 Pro API in English'),
        ent_name='Kimi K3.1 Pro',
    )


# ======================================================================
# Kimi K3
# ======================================================================
def k3():
    s = 'kimi-k3'
    faqs = [
        ('Kimi K3 API 多少钱？',
         f'AnyAIGC 上 <code>kimi-k3</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'Moonshot 官方美元价为输入 {o(s, 0)}、输出 {o(s, 1)}、缓存命中 {o(s, 2)}，AnyAIGC 约为官方价的 40%（约 4 折）。输出包含思考 tokens，实时价格以模型广场为准。'),
        ('Kimi K3 的模型 ID 是什么？上下文多大？',
         '模型 ID 是 <code>kimi-k3</code>。Moonshot 官方公布的上下文窗口为 1,048,576 tokens（1M），<code>max_completion_tokens</code> 默认 131,072，最大可设到 1,048,576。'),
        ('Kimi K3 有什么特点？',
         'Moonshot 称 Kimi K3 是首个达到 2.8 万亿参数的开源模型，基于 Kimi Delta Attention（KDA）混合线性注意力和注意力残差构建，MoE 每个 token 从 896 个专家中激活 16 个，原生支持视觉理解。官方说整体扩展效率约为 K2 的 2.5 倍，面向长程编程、知识工作和推理。'),
        ('怎么调整 Kimi K3 的思考深度？',
         'K3 始终开启思考，不能关闭。官方用请求体顶层的 <code>reasoning_effort</code> 字段调整思考深度，可选 <code>low</code>、<code>high</code>、<code>max</code>，默认 <code>max</code>。简单任务用 <code>low</code> 可以减少输出 tokens。'),
        ('Kimi K3 支持工具调用和图片输入吗？',
         '支持。K3 支持函数调用（<code>tools</code> / <code>tool_choice</code>）、结构化输出（<code>json_schema</code>）、流式输出和图片输入。多轮和工具调用时，需要把返回的完整 assistant 消息（含 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。'),
        faq_cc('Kimi K3', s),
        ('Kimi K3 和 K3.1 Pro 有什么区别？',
         f'<a href="/zh/models/kimi-k3.1-pro">Kimi K3.1 Pro</a> 是 K3.1 系列首款，官方说明它是在 K3 基础上用更多后训练算力得到的版本，代码、3D 创作、金融研究和长程 Agent 提升明显，参数约束和 K3 相同，迁移只需要改模型名。AnyAIGC 上 K3.1 Pro 输入 {p("kimi-k3.1-pro", 0)}、输出 {p("kimi-k3.1-pro", 1)}，比 K3 低三分之一。新项目建议直接用 K3.1 Pro。'),
        ('Kimi K3 和 K2.7 Code 怎么选？',
         f'K3 是 2.8T 参数的上一代旗舰，有 1M 上下文，适合大仓库、长周期任务和最难的推理；<a href="/zh/models/kimi-k2.7-code">K2.7 Code</a> 是 1T 参数的编程模型，上下文 256K，AnyAIGC 输入 {p("kimi-k2.7-code", 0)}、输出 {p("kimi-k2.7-code", 1)}，约为 K3 的三分之一。可以日常用 K2.7 Code，难题切到 K3，两者共用同一个 Key。'),
        faq_rpm('Kimi K3', s),
    ] + faq_common('Kimi K3', s)
    return dict(
        title='Kimi K3 API 价格与接入｜1M 上下文 约官方 4 折 - AnyAIGC',
        desc=f'kimi-k3 API：Moonshot 上一代旗舰，2.8T 参数开放权重，1M 上下文，输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方价 4 折，可接入 Claude Code，并发不限，支持对公转账与专票。',
        og_desc=f'kimi-k3 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约 Moonshot 官方价 4 折。1M 上下文、长程编程与深度推理，OpenAI 兼容接口，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC Kimi K3 API：约官方价 4 折',
        keywords='Kimi K3 API,kimi-k3,Kimi K3 API 价格,Kimi K3 接入,Kimi K3 1M 上下文,Kimi K3 Claude Code,Kimi K3 API key,月之暗面 K3,Moonshot K3 API,Kimi API,Kimi K3 API 企业,Kimi K3 API 发票,Kimi API 对公转账,AnyAIGC',
        crumb='Kimi K3 API', product='Kimi K3 API（AnyAIGC）', sku=s,
        product_desc='通过 AnyAIGC 调用 Moonshot AI Kimi K3（kimi-k3）：OpenAI 兼容 /v1/chat/completions，1M 上下文，按 token 计费，约官方价 4 折，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow='Moonshot AI · kimi-k3',
                  h1='Kimi <span class="k-blue">K3</span><span class="o-sr"> API</span>',
                  lead='Moonshot 上一代旗舰，2.8 万亿参数的开放权重模型，1M 上下文，面向长程编程、知识工作和深度推理。在 AnyAIGC 调用约为官方价的 4 折。',
                  ask='读完整个仓库，把单体服务拆成三个微服务，并给出迁移步骤',
                  chips=['1M 上下文', 'reasoning_effort', '视觉理解'],
                  sub=f'<code>kimi-k3</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='三万亿级开放权重模型，为长程任务设计',
                   paras=['Moonshot AI 称 Kimi K3 是首个达到 2.8 万亿参数的开源模型。它基于 Kimi Delta Attention（KDA）混合线性注意力和注意力残差（Attention Residuals）构建，两项结构改动都是为了让信息在更长的序列和更深的网络里流动得更顺。',
                          '在 Stable LatentMoE 框架下，K3 每个 token 从 896 个专家中激活 16 个。官方表示，结合训练方法和数据配方的改进，K3 的整体扩展效率约为 K2 的 2.5 倍。模型原生支持视觉理解，上下文窗口 1,048,576 tokens，思考模式始终开启。',
                          f'在 AnyAIGC 上，<code>kimi-k3</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，也能在 Claude Code 里直接使用。不需要 Moonshot 开放平台账号，没有充值等级限制，并发不限。'],
                   spec=[('上下文窗口', '1,048,576', '输入 tokens 上限'), ('最大输出', '131,072', '默认值，最大可设到 1,048,576'),
                         ('总参数', '2.8T', 'MoE，896 专家激活 16 个'), ('输入模态', '文本、图片', '原生视觉理解'),
                         ('思考模式', '始终开启', 'reasoning_effort：low / high / max'), ('权重', '开放', 'Hugging Face moonshotai/Kimi-K3')]),
        features=dict(kicker='能力', h2='Kimi K3 能做什么',
                      items=[('长程编程', '在很少人工干预下持续完成长周期工程任务，理解大型代码库，协调终端工具。官方公布 Terminal-Bench 2.1 为 88.3。'),
                             ('视觉 + 编码', '用截图和视觉反馈改进前端、游戏开发、CAD 等工作流，看图写界面、对着渲染结果调样式。'),
                             ('端到端知识工作', '深度研究、数据可视化、仪表盘和报告生成。官方公布 BrowseComp 为 91.2，GPQA Diamond 为 93.5。'),
                             ('1M tokens 上下文', '整个代码库、成套合同或长篇资料一次放进去。重复的前缀自动缓存，缓存命中只要 ' + p(s, 2) + ' / 百万 tokens。'),
                             ('Agent 与工具调用', '支持函数调用、tool_choice、动态工具加载和结构化输出。官方公布 MCPMark-Verified 94.5、OSWorld-Verified 84.8。'),
                             ('思考深度可调', '思考始终开启，用 reasoning_effort 在 low、high、max 之间调节，简单任务省 tokens，难题用 max。')]),
        pricing=dict(kicker='价格', h2='Kimi K3 API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入、输出、缓存命中都约为 Moonshot 官方美元价的 40%。',
                     billing_label='计费要点',
                     billing=[('按 token 计费', '输入、输出、缓存分别计价'), ('约 4 折', '相比 Moonshot 官方美元价'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')],
                     head=PRICE_HEAD, labels=LABELS, caption='kimi-k3 每百万 tokens 价格（美元），AnyAIGC 与 Moonshot 官方对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 Moonshot 官方价。',
                     costs=[cost_card(s, 'Agent 编程 20 轮', '每轮 5 万 tokens 缓存命中 + 5,000 输入 + 3,000 输出', 5000, 3000, 50000, 20),
                            cost_card(s, '50 万 tokens 长文档分析', '50 万 tokens 输入 + 5,000 输出', 500000, 5000),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='Kimi K3 的官方基准成绩', lead='Moonshot AI 公布的 Kimi K3（max 思考深度）成绩，覆盖推理、编程、Agent 和视觉四类任务。',
                   chart=('Kimi K3 · 部分基准成绩', [('Terminal-Bench 2.1', 88.3, True), ('BrowseComp', 91.2, True), ('MCPMark-Verified', 94.5, True), ('GPQA Diamond', 93.5, True), ('OSWorld-Verified', 84.8, True)]),
                   head=[('基准', ''), ('Kimi K3', 'o-num o-hl')],
                   rows=[('GPQA Diamond', '科学推理', '93.5'), ('AA-LCR', '长上下文推理', '74.7'),
                         ('Terminal-Bench 2.1', '终端编程', '88.3'), ('ProgramBench', '编程', '77.8'), ('FrontierSWE', '软件工程', '81.2'),
                         ('DeepSWE', '长周期软件工程', '67.5'), ('Kimi Code Bench 2.0', '编程', '72.9'),
                         ('BrowseComp', '网页检索 Agent', '91.2'), ('MCPMark-Verified', '工具调用', '94.5'), ('MCP-Atlas', '工具调用', '84.2'),
                         ('OSWorld-Verified', '计算机操作', '84.8'), ('OmniDocBench', '文档理解', '91.1'), ('Video-MME', '视频理解', '90.0')],
                   caption='Kimi K3 官方基准成绩（Moonshot AI 公布）',
                   note='数据来自 <a href="https://huggingface.co/moonshotai/Kimi-K3" target="_blank" rel="noopener">Hugging Face Kimi K3 模型卡</a>，为 Moonshot AI 公布的 max 思考深度成绩。'),
        compare=dict(kicker='选型', h2='Kimi K3 和 K3.1 Pro、K2.7 Code、K2.6 怎么选', lead='新项目优先用 K3.1 Pro，它更新、更便宜；K2.7 Code 和 K2.6 单价约为 K3 的三分之一。',
                     head=[('对比项', ''), ('K3', 'o-num o-hl'), ('K3.1 Pro', 'o-num'), ('K2.7 Code', 'o-num'), ('K2.6', 'o-num')],
                     rows=[('定位', '', '上一代旗舰', '最新旗舰', '编程 Agent', '通用多模态 Agent'), ('总参数', '', '2.8T', '3T 级', '1T', '1T'),
                           ('上下文', '', '1M', '1M', '256K', '256K'), ('思考模式', '', '始终开启', '始终开启', '始终开启', '可开可关'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p('kimi-k3.1-pro', 0), p('kimi-k2.7-code', 0), p('kimi-k2.6', 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p('kimi-k3.1-pro', 1), p('kimi-k2.7-code', 1), p('kimi-k2.6', 1))],
                     caption='Kimi K3、K3.1 Pro、K2.7 Code、K2.6 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自 Moonshot AI 公开资料，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。详见 <a href="/zh/models/kimi-k3.1-pro">Kimi K3.1 Pro API</a>、<a href="/zh/models/kimi-k2.7-code">Kimi K2.7 Code API</a> 和 <a href="/zh/models/kimi-k2.6">Kimi K2.6 API</a>。'),
        uses=dict(kicker='使用场景', h2='Kimi K3 适合做什么',
                  items=[('01 · 大仓库', '跨模块重构与迁移', '把整个代码库放进 1M 上下文，让 K3 理清依赖后一次给出改动方案，再配合终端工具逐步执行和验证。'),
                         ('02 · Agent', '长周期自主任务', '在 Claude Code 或自研 Agent 里跑几十上百步的任务：查资料、写代码、跑测试、修报错。AnyAIGC 不限并发。'),
                         ('03 · 研究', '深度研究与报告', '读完成批论文、财报或调研资料，交叉核对后输出结构化结论、图表代码和可交付的报告。'),
                         ('04 · 视觉', '截图到代码', '把设计稿、报错截图或渲染结果交给 K3，生成或修正前端、游戏和可视化代码。')]),
        qs=dict(kicker='快速开始', h2='三步接入 Kimi K3 API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, '用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, '你是资深后端工程师，回答要给出可运行的代码。', '用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('effort', '思考深度', 'Python · reasoning_effort', code_effort(s)),
                      ('stream', '流式输出', 'Python · stream=True', code_stream(s, '解释为什么天空是蓝色的。'))],
                callout='<strong>参数提示：</strong>K3 思考始终开启，思考过程在 <code>reasoning_content</code> 字段。官方推荐 <code>temperature=1.0</code>、<code>top_p=0.95</code>。多轮对话和工具调用时，要把 API 返回的完整 assistant 消息（包括 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求，不要只保留 content。',
                note=QS_NOTE),
        cc=cc('Kimi K3', s, '把 Claude Code 的模型换成 Kimi K3：1M 上下文适合在大仓库里做长周期的编码任务。',
              '<strong>省钱搭配：</strong>可以把 <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> 换成 <code>kimi-k2.7-code</code>，让 Claude Code 的轻量子任务用更便宜的模型，主任务继续用 K3。'),
        family_h2='Kimi 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 Kimi 模型，按任务难度和预算选择。',
        faq_h2='Kimi K3 API 常见问题', faqs=faqs,
        final=dict(h2='用约 4 折的价格跑 Kimi K3', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 kimi-k3。', other='Kimi K3 API in English'),
        ent_name='Kimi K3',
    )


# ======================================================================
# Kimi K2.7 Code
# ======================================================================
def k27():
    s = 'kimi-k2.7-code'
    faqs = [
        ('Kimi K2.7 Code API 多少钱？',
         f'AnyAIGC 上 <code>kimi-k2.7-code</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'Moonshot 官方美元价为输入 {o(s, 0)}、输出 {o(s, 1)}、缓存命中 {o(s, 2)}，AnyAIGC 约为官方价的 40%（约 4 折）。输出包含思考 tokens，实时价格以模型广场为准。'),
        ('Kimi K2.7 Code 的模型 ID 是什么？上下文多大？',
         '模型 ID 是 <code>kimi-k2.7-code</code>。Moonshot 官方公布的上下文窗口为 262,144 tokens（256K），支持文本和图片输入。'),
        ('Kimi K2.7 Code 和 K2.6 有什么区别？',
         f'K2.7 Code 基于 K2.6 继续训练，专注编程，架构相同（1T 总参数、32B 激活）。官方称它在长上下文里更稳定地遵循指令，编程任务成功率更高，思考 tokens 比 K2.6 少约 30%；Kimi Code Bench v2 从 50.9 提升到 62.0。区别是 K2.7 Code 只有思考模式，<a href="/zh/models/kimi-k2.6">K2.6</a> 可以关闭思考。两者在 AnyAIGC 输入、输出单价相同。'),
        ('Kimi K2.7 Code 能关闭思考模式吗？',
         '不能。官方说明 K2.7 Code 强制开启思考和保留思考（preserve thinking），不支持非思考模式。需要快速、非思考的响应可以用 <code>kimi-k2.6</code>。官方推荐参数为 <code>temperature=1.0</code>、<code>top_p=0.95</code>。'),
        ('Kimi K2.7 Code 支持工具调用吗？',
         '支持。K2.7 Code 支持交错思考（interleaved thinking）和多步工具调用，适合 Coding Agent。多轮和工具调用时，需要把返回的完整 assistant 消息（含 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。'),
        faq_cc('Kimi K2.7 Code', s),
        ('Kimi K2.7 Code 和 Kimi K3.1 Pro 怎么选？',
         f'K2.7 Code 是 1T 参数的编程模型，上下文 256K，AnyAIGC 输入 {p(s, 0)}、输出 {p(s, 1)}，适合日常编码和高频 Agent 调用；<a href="/zh/models/kimi-k3.1-pro">Kimi K3.1 Pro</a> 是最新一代 3T 级模型，有 1M 上下文，输入 {p("kimi-k3.1-pro", 0)}、输出 {p("kimi-k3.1-pro", 1)}，适合大仓库和最难的任务。两者共用同一个 Key。'),
        faq_rpm('Kimi K2.7 Code', s),
    ] + faq_common('Kimi K2.7 Code', s)
    return dict(
        title='Kimi K2.7 Code API 价格与接入｜编程 Agent 模型 - AnyAIGC',
        desc=f'kimi-k2.7-code API：Moonshot 编程向 Agent 模型，输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方价 4 折，256K 上下文，可接入 Claude Code，并发不限，支持对公转账与专票。',
        og_desc=f'kimi-k2.7-code 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约 Moonshot 官方价 4 折。Kimi Code Bench v2 比 K2.6 提升 21.8%，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC Kimi K2.7 Code API：约官方价 4 折',
        keywords='Kimi K2.7 Code API,kimi-k2.7-code,Kimi K2.7 Code 价格,Kimi 编程模型 API,Kimi K2.7 Code Claude Code,Kimi Coding API,K2.7 Code 和 K2.6 区别,Kimi API,Kimi K2.7 Code API 企业,Kimi K2.7 Code API 发票,Kimi API 对公转账,AnyAIGC',
        crumb='Kimi K2.7 Code API', product='Kimi K2.7 Code API（AnyAIGC）', sku=s,
        product_desc='通过 AnyAIGC 调用 Moonshot AI Kimi K2.7 Code（kimi-k2.7-code）：OpenAI 兼容 /v1/chat/completions，256K 上下文，按 token 计费，约官方价 4 折，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow='Moonshot AI · kimi-k2.7-code',
                  h1='Kimi K2.7 <span class="k-blue">Code</span><span class="o-sr"> API</span>',
                  lead='Kimi 的编程向 Agent 模型，在长上下文里更稳定地遵循指令，编程任务成功率更高。在 AnyAIGC 调用约为官方价的 4 折。',
                  ask='跑一遍测试，定位 test_checkout 失败的原因并修好',
                  chips=['Coding Agent', '交错思考', '256K'],
                  sub=f'<code>kimi-k2.7-code</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens，约为 K3.1 Pro 的一半，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '256K tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='基于 K2.6 的编程强化版',
                   paras=['Moonshot AI 称 Kimi K2.7 Code 是 Kimi 迄今最强的编程模型。它基于 K2.6 继续训练，在长上下文里更稳定地遵循指令，编程任务的完成率更高，同时思考 tokens 比 K2.6 少约 30%。',
                          '模型架构与 K2.6 相同：MoE，1T 总参数、32B 激活参数，384 个专家每 token 选 8 个，上下文 256K，支持文本和图片输入。K2.7 Code 强制开启思考，支持交错思考和多步工具调用，适合 Coding Agent 场景。',
                          f'在 AnyAIGC 上，<code>kimi-k2.7-code</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，也能在 Claude Code 里直接使用，并发不限。'],
                   spec=[('上下文窗口', '262,144', '256K tokens'), ('总参数', '1T', '32B 激活，MoE'),
                         ('输入模态', '文本、图片', '原生多模态'), ('思考模式', '强制开启', '不支持非思考模式'),
                         ('推荐参数', 'temperature 1.0', 'top_p 0.95'), ('权重', '开放', 'Modified MIT 许可')]),
        features=dict(kicker='能力', h2='Kimi K2.7 Code 能做什么',
                      items=[('更高的编程成功率', '官方公布 Kimi Code Bench v2 从 K2.6 的 50.9 提升到 62.0，Program Bench 从 48.3 提升到 53.6。'),
                             ('长上下文指令遵循', '在 256K 上下文里更稳定地遵循复杂指令，长会话里不容易跑偏。'),
                             ('更少的思考 tokens', '官方称思考 tokens 比 K2.6 少约 30%，同样的任务输出更省。'),
                             ('交错思考 + 工具调用', '每一步工具调用之间都能思考，适合跑测试、读报错、改代码的循环。MCP Mark Verified 81.1。'),
                             ('看图写代码', '支持图片输入，可以根据设计稿、截图或报错画面生成和修正代码。'),
                             ('适合高频调用', f'输入 {p(s, 0)}、缓存命中 {p(s, 2)} / 百万 tokens，AnyAIGC 不限并发，多个 Agent 可以同时跑。')]),
        pricing=dict(kicker='价格', h2='Kimi K2.7 Code API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入、输出、缓存命中都约为 Moonshot 官方美元价的 40%。',
                     billing_label='计费要点',
                     billing=[('按 token 计费', '输入、输出、缓存分别计价'), ('约 4 折', '相比 Moonshot 官方美元价'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')],
                     head=PRICE_HEAD, labels=LABELS, caption='kimi-k2.7-code 每百万 tokens 价格（美元），AnyAIGC 与 Moonshot 官方对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 Moonshot 官方价。',
                     costs=[cost_card(s, 'Coding Agent 50 轮', '每轮 4 万 tokens 缓存命中 + 4,000 输入 + 2,000 输出', 4000, 2000, 40000, 50),
                            cost_card(s, '审查 100 个 PR', '每个 PR 2 万 tokens 输入 + 2,000 输出', 20000, 2000, 0, 100),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='比 K2.6 强在哪里', lead='Moonshot AI 公布的 K2.7 Code 与 K2.6 对比成绩，编程和工具调用类任务全面提升。',
                   chart=('Kimi Code Bench v2 · 编程', [('Kimi K2.7 Code', 62.0, True), ('Kimi K2.6', 50.9, False)]),
                   head=[('基准', ''), ('K2.7 Code', 'o-num o-hl'), ('K2.6', 'o-num')],
                   rows=[('Kimi Code Bench v2', '编程', '62.0', '50.9'), ('Program Bench', '编程', '53.6', '48.3'),
                         ('MLS Bench Lite', '机器学习工程', '35.1', '26.7'), ('Kimi Claw 24/7', '长时间 Agent', '46.9', '42.9'),
                         ('MCP Atlas', '工具调用', '76.0', '69.4'), ('MCP Mark Verified', '工具调用', '81.1', '72.8')],
                   caption='Kimi K2.7 Code 与 Kimi K2.6 的基准对比（Moonshot AI 公布）',
                   note='数据来自 <a href="https://huggingface.co/moonshotai/Kimi-K2.7-Code" target="_blank" rel="noopener">Hugging Face Kimi K2.7 Code 模型卡</a>。'),
        compare=dict(kicker='选型', h2='Kimi K2.7 Code、K2.6 和 K3 怎么选', lead='写代码优先 K2.7 Code，需要关闭思考用 K2.6，大仓库和最难的任务交给 K3.1 Pro。',
                     head=[('对比项', ''), ('K2.7 Code', 'o-num o-hl'), ('K2.6', 'o-num'), ('K3.1 Pro', 'o-num')],
                     rows=[('定位', '', '编程 Agent', '通用多模态 Agent', '最新旗舰'), ('上下文', '', '256K', '256K', '1M'),
                           ('思考模式', '', '始终开启', '可开可关', '始终开启'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p('kimi-k2.6', 0), p('kimi-k3.1-pro', 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p('kimi-k2.6', 1), p('kimi-k3.1-pro', 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p('kimi-k2.6', 2), p('kimi-k3.1-pro', 2))],
                     caption='Kimi K2.7 Code、K2.6、K3.1 Pro 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自 Moonshot AI 公开资料，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。详见 <a href="/zh/models/kimi-k3.1-pro">Kimi K3.1 Pro API</a>。'),
        uses=dict(kicker='使用场景', h2='Kimi K2.7 Code 适合做什么',
                  items=[('01 · Claude Code', '终端里的编程搭档', '把 Claude Code 的模型换成 K2.7 Code，读代码、改 bug、写测试，单价约为 K3.1 Pro 的一半。'),
                         ('02 · CI', '自动修复和代码审查', '在流水线里自动审查 PR、修复失败的测试、生成变更说明。AnyAIGC 不限并发，适合大批量并行。'),
                         ('03 · 前端', '设计稿到组件', '上传设计稿或页面截图，生成 React、Vue 或原生 HTML/CSS 组件，再按渲染结果迭代。'),
                         ('04 · 机器学习工程', '实验脚本和数据处理', 'MLS Bench Lite 比 K2.6 提升约 31%，适合写训练脚本、数据清洗和评测代码。')]),
        qs=dict(kicker='快速开始', h2='三步接入 Kimi K2.7 Code API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, '用 Python 写一个 LRU 缓存，附带单元测试')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, '你是资深后端工程师，回答要给出可运行的代码。', '用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('tools', '工具调用', 'Python · tools', code_tools(s)),
                      ('stream', '流式输出', 'Python · stream=True', code_stream(s, '解释这段正则：^(?=.*\\\\d)(?=.*[a-z]).{8,}$'))],
                callout='<strong>参数提示：</strong>K2.7 Code 强制开启思考，思考过程在 <code>reasoning_content</code> 字段。官方推荐 <code>temperature=1.0</code>、<code>top_p=0.95</code>。多轮对话和工具调用时，要把 API 返回的完整 assistant 消息（包括 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('Kimi K2.7 Code', s, '把 Claude Code 的模型换成 Kimi K2.7 Code：专为编程训练，价格约为 K3.1 Pro 的一半。',
              '<strong>遇到大仓库：</strong>K2.7 Code 的上下文是 256K。项目特别大、需要一次读完更多代码时，可以把配置里的模型换成 <code>kimi-k3.1-pro</code>（1M 上下文）。'),
        family_h2='Kimi 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 Kimi 模型，按任务难度和预算选择。',
        faq_h2='Kimi K2.7 Code API 常见问题', faqs=faqs,
        final=dict(h2='用约 4 折的价格跑 Kimi K2.7 Code', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 kimi-k2.7-code。', other='Kimi K2.7 Code API in English'),
        ent_name='Kimi K2.7 Code',
    )


# ======================================================================
# Kimi K2.6
# ======================================================================
def k26():
    s = 'kimi-k2.6'
    faqs = [
        ('Kimi K2.6 API 多少钱？',
         f'AnyAIGC 上 <code>kimi-k2.6</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'Moonshot 官方美元价为输入 {o(s, 0)}、输出 {o(s, 1)}、缓存命中 {o(s, 2)}，AnyAIGC 约为官方价的 40%（约 4 折）。实时价格以模型广场为准。'),
        ('Kimi K2.6 的模型 ID 是什么？上下文多大？',
         '模型 ID 是 <code>kimi-k2.6</code>。Moonshot 官方公布的上下文窗口为 262,144 tokens（256K），支持文本和图片输入。'),
        ('Kimi K2.6 能关闭思考模式吗？',
         'K2.6 支持思考和非思考（Instant）两种模式。Moonshot 官方 API 用 <code>thinking: {"type": "disabled"}</code> 关闭思考，OpenAI SDK 里写在 <code>extra_body</code>。官方推荐思考模式 <code>temperature=1.0</code>，非思考模式 <code>temperature=0.6</code>，<code>top_p</code> 都是 0.95。'),
        ('Kimi K2.6 有什么特点？',
         '官方把 K2.6 定位为开源原生多模态 Agent 模型，重点在四个方向：长程编程（Rust、Go、Python，前端、运维和性能优化）、从提示词或图片生成可上线的界面、Agent Swarm（横向扩展到 300 个子 Agent、4,000 个协同步骤），以及 7×24 后台运行的主动式 Agent。'),
        ('Kimi K2.6 和 K2.7 Code 怎么选？',
         f'两者架构相同、在 AnyAIGC 输入和输出单价相同。<a href="/zh/models/kimi-k2.7-code">K2.7 Code</a> 是基于 K2.6 的编程强化版，编程基准更高、思考 tokens 更少，但只能思考模式；K2.6 可以关闭思考，更适合需要快速响应的对话、分类、抽取和通用 Agent。'),
        faq_cc('Kimi K2.6', s),
        ('Kimi K2.6 支持工具调用和图片输入吗？',
         '支持。K2.6 支持多步工具调用、流式输出和图片输入。思考模式下多轮和工具调用时，需要把返回的完整 assistant 消息（含 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。'),
        faq_rpm('Kimi K2.6', s),
    ] + faq_common('Kimi K2.6', s)
    return dict(
        title='Kimi K2.6 API 价格与接入｜多模态 Agent 编程 - AnyAIGC',
        desc=f'kimi-k2.6 API：Moonshot 开源多模态 Agent 模型，思考与非思考可切换，输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方价 4 折，256K 上下文，并发不限，支持对公转账与专票。',
        og_desc=f'kimi-k2.6 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约 Moonshot 官方价 4 折。SWE-Bench Verified 80.2，思考与非思考可切换，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC Kimi K2.6 API：约官方价 4 折',
        keywords='Kimi K2.6 API,kimi-k2.6,Kimi K2.6 API 价格,Kimi K2.6 接入,Kimi K2.6 多模态,Kimi K2.6 思考模式,Kimi K2.6 Agent,Kimi K2.6 Claude Code,Kimi API,Kimi K2.6 API 企业,Kimi K2.6 API 发票,Kimi API 对公转账,AnyAIGC',
        crumb='Kimi K2.6 API', product='Kimi K2.6 API（AnyAIGC）', sku=s,
        product_desc='通过 AnyAIGC 调用 Moonshot AI Kimi K2.6（kimi-k2.6）：OpenAI 兼容 /v1/chat/completions，256K 上下文，思考与非思考可切换，按 token 计费，约官方价 4 折，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow='Moonshot AI · kimi-k2.6',
                  h1='Kimi <span class="k-blue">K2.6</span><span class="o-sr"> API</span>',
                  lead='开源原生多模态 Agent 模型，长程编程、界面生成和 Agent 集群都能做，思考模式可开可关。在 AnyAIGC 调用约为官方价的 4 折。',
                  ask='根据这张设计稿生成响应式落地页，并接上表单校验',
                  chips=['多模态', '思考 / 非思考', 'Agent Swarm'],
                  sub=f'<code>kimi-k2.6</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '256K tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='通用的开源多模态 Agent 模型',
                   paras=['Moonshot AI 把 Kimi K2.6 定位为开源原生多模态 Agent 模型。官方称它的长程代码编写更强、更稳定，指令遵循和自我纠错明显提升，支持文本、图片输入，支持思考和非思考两种模式，对话和 Agent 任务都能用。',
                          '架构上是 MoE，1T 总参数、32B 激活参数，上下文 256K，原生 INT4 量化。官方重点展示了四个方向：长程编程、从提示词或图片生成界面（Coding-Driven Design）、横向扩展到 300 个子 Agent 的 Agent Swarm，以及 7×24 运行的主动式 Agent。',
                          f'在 AnyAIGC 上，<code>kimi-k2.6</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，也能在 Claude Code 里直接使用，并发不限。'],
                   spec=[('上下文窗口', '262,144', '256K tokens'), ('总参数', '1T', '32B 激活，MoE'),
                         ('输入模态', '文本、图片', '原生多模态'), ('思考模式', '可开可关', '思考 / 非思考（Instant）'),
                         ('推荐参数', 'temperature 1.0', '非思考 0.6，top_p 0.95'), ('权重', '开放', 'Modified MIT 许可')]),
        features=dict(kicker='能力', h2='Kimi K2.6 能做什么',
                      items=[('长程编程', '覆盖 Rust、Go、Python 和前端、运维、性能优化。官方公布 SWE-Bench Verified 80.2、SWE-Bench Pro 58.6。'),
                             ('从图片生成界面', '根据提示词或设计稿生成可上线的界面代码，适合落地页、后台和组件开发。'),
                             ('Agent Swarm', '官方展示横向扩展到 300 个子 Agent、4,000 个协同步骤。AnyAIGC 不限并发，适合多 Agent 并行。'),
                             ('思考 / 非思考切换', '难题打开思考，分类、抽取、客服对话这类请求关掉思考，响应更快、输出更省。'),
                             ('检索与研究', '官方公布 BrowseComp 83.2（Agent Swarm 86.3）、DeepSearchQA f1 92.5，适合深度检索类 Agent。'),
                             ('数学与推理', '官方公布 AIME 2026 为 96.4，GPQA-Diamond 为 90.5。')]),
        pricing=dict(kicker='价格', h2='Kimi K2.6 API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入、输出、缓存命中都约为 Moonshot 官方美元价的 40%。',
                     billing_label='计费要点',
                     billing=[('按 token 计费', '输入、输出、缓存分别计价'), ('约 4 折', '相比 Moonshot 官方美元价'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')],
                     head=PRICE_HEAD, labels=LABELS, caption='kimi-k2.6 每百万 tokens 价格（美元），AnyAIGC 与 Moonshot 官方对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 Moonshot 官方价。',
                     costs=[cost_card(s, '1 万条工单分类', '每条 2,000 tokens 输入 + 300 输出', 2000, 300, 0, 10000),
                            cost_card(s, '客服对话 1,000 轮', '每轮 8,000 tokens 缓存命中 + 1,000 输入 + 500 输出', 1000, 500, 8000, 1000),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='Kimi K2.6 的官方基准成绩', lead='Moonshot AI 公布的 Kimi K2.6 成绩，覆盖编程、Agent、推理和视觉任务。',
                   chart=('Kimi K2.6 · 部分基准成绩', [('SWE-Bench Verified', 80.2, True), ('LiveCodeBench v6', 89.6, True), ('BrowseComp', 83.2, True), ('AIME 2026', 96.4, True), ('GPQA-Diamond', 90.5, True)]),
                   head=[('基准', ''), ('Kimi K2.6', 'o-num o-hl')],
                   rows=[('SWE-Bench Verified', '软件工程', '80.2'), ('SWE-Bench Pro', '软件工程', '58.6'), ('SWE-Bench Multilingual', '多语言编程', '76.7'),
                         ('Terminal-Bench 2.0', '终端编程', '66.7'), ('LiveCodeBench v6', '算法编程', '89.6'),
                         ('HLE-Full', '综合推理，带工具', '54.0'), ('BrowseComp', '网页检索 Agent', '83.2'), ('DeepSearchQA', '深度检索，f1', '92.5'),
                         ('AIME 2026', '数学', '96.4'), ('GPQA-Diamond', '科学推理', '90.5'), ('MMMU-Pro', '多模态理解', '79.4'), ('OSWorld-Verified', '计算机操作', '73.1')],
                   caption='Kimi K2.6 官方基准成绩（Moonshot AI 公布）',
                   note='数据来自 <a href="https://huggingface.co/moonshotai/Kimi-K2.6" target="_blank" rel="noopener">Hugging Face Kimi K2.6 模型卡</a>。BrowseComp 在 Agent Swarm 设置下为 86.3。'),
        compare=dict(kicker='选型', h2='Kimi K2.6、K2.7 Code 和 K3 怎么选', lead='通用任务和需要关掉思考时用 K2.6，专心写代码用 K2.7 Code，最难的任务交给 K3.1 Pro。',
                     head=[('对比项', ''), ('K2.6', 'o-num o-hl'), ('K2.7 Code', 'o-num'), ('K3.1 Pro', 'o-num')],
                     rows=[('定位', '', '通用多模态 Agent', '编程 Agent', '最新旗舰'), ('上下文', '', '256K', '256K', '1M'),
                           ('思考模式', '', '可开可关', '始终开启', '始终开启'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p('kimi-k2.7-code', 0), p('kimi-k3.1-pro', 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p('kimi-k2.7-code', 1), p('kimi-k3.1-pro', 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p('kimi-k2.7-code', 2), p('kimi-k3.1-pro', 2))],
                     caption='Kimi K2.6、K2.7 Code、K3.1 Pro 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自 Moonshot AI 公开资料，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。详见 <a href="/zh/models/kimi-k2.7-code">Kimi K2.7 Code API</a>。'),
        uses=dict(kicker='使用场景', h2='Kimi K2.6 适合做什么',
                  items=[('01 · 批量处理', '分类、抽取和摘要', '关掉思考跑工单分类、字段抽取、评论打标，响应快、输出短。AnyAIGC 不限并发。'),
                         ('02 · 界面生成', '设计稿到可上线页面', '上传设计稿或参考截图，生成落地页、后台页面和组件代码。'),
                         ('03 · 多 Agent', 'Agent Swarm 和后台任务', '把大任务拆给多个子 Agent 并行处理，或者让 Agent 7×24 在后台监控、整理和汇报。'),
                         ('04 · 编码', '日常编程和 Claude Code', '在 Claude Code 里用 K2.6 读代码、改 bug；想要更高的编程成功率可以换成 K2.7 Code，单价相同。')]),
        qs=dict(kicker='快速开始', h2='三步接入 Kimi K2.6 API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, '用三句话解释什么是数据库索引')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, '你是资深前端工程师，回答要给出可运行的代码。', '写一个无障碍友好的下拉菜单组件。')),
                      ('vision', '图片输入', 'Python · image_url', code_vision(s)),
                      ('stream', '流式输出', 'Python · stream=True', code_stream(s, '给一个 SaaS 产品写 5 条更新日志。'))],
                callout='<strong>参数提示：</strong>K2.6 默认开启思考，思考过程在 <code>reasoning_content</code> 字段。Moonshot 官方 API 用 <code>thinking: {"type": "disabled"}</code> 关闭思考（OpenAI SDK 写在 <code>extra_body</code>），非思考模式官方推荐 <code>temperature=0.6</code>。思考模式下多轮和工具调用时，要把完整的 assistant 消息原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('Kimi K2.6', s, '把 Claude Code 的模型换成 Kimi K2.6：多模态、价格低，日常编码和读图改界面都能用。',
              '<strong>换成编程模型：</strong>想要更高的编程成功率，把配置里的 <code>kimi-k2.6</code> 换成 <code>kimi-k2.7-code</code> 即可，两者单价相同。'),
        family_h2='Kimi 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 Kimi 模型，按任务难度和预算选择。',
        faq_h2='Kimi K2.6 API 常见问题', faqs=faqs,
        final=dict(h2='用约 4 折的价格跑 Kimi K2.6', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 kimi-k2.6。', other='Kimi K2.6 API in English'),
        ent_name='Kimi K2.6',
    )
