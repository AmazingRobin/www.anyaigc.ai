# GLM 系列专题页中文文案。被 scripts/glm_pages.py 引用。
# 价格来自 glm_data.PRICE（模型广场），官方价与参数来自 docs.z.ai、z.ai 技术博客和 Hugging Face 模型卡（2026-10-30 读取）。
from glm_data import PRICE, OFFICIAL, REG, PRICING, SUPPORT, DOCS_CHAT, DOCS_CC, OFFICIAL_PRICING
from glm_layout import cost, money

UNIT = '百万 tokens'
B53 = 'https://z.ai/blog/glm-5.3'
B52 = 'https://z.ai/blog/glm-5.2'
BF = 'https://z.ai/blog/glm-5.3-flash'


def p(slug, i):
    return f'${PRICE[slug][i]}'


def o(slug, i):
    return f'${OFFICIAL[slug][i]}'


# 折扣口径：glm-5.3 / glm-5.2 输入输出为官方价的 67.5%（约 7 折），glm-5.3-flash 为 40.5%（约 4 折）
OFF = {'glm-5.3': '约 7 折', 'glm-5.2': '约 7 折', 'glm-5.3-flash': '约 4 折'}
PCT = {'glm-5.3': '67.5%', 'glm-5.2': '67.5%', 'glm-5.3-flash': '40.5%'}


# ---------------- 共用 FAQ ----------------
def faq_common(name, slug):
    return [
        (f'国内可以直接调用 {name} API 吗？',
         f'可以。AnyAIGC 面向国内网络优化，通常无需额外代理即可调用 <code>https://anyaigc.ai</code>，按美元价格计费，支持微信支付、支付宝、USDT 和信用卡，企业可对公转账并开具增值税发票。'),
        (f'如何获取 {name} API Key？',
         f'在 <a href="{REG}">anyaigc.ai</a> 注册并充值，进入控制台创建令牌即可。同一个 Key 可以调用 GLM 全系以及平台上 300+ 其他模型，不需要单独注册智谱开放平台或购买 GLM Coding Plan。'),
        ('AnyAIGC 能开发票吗？支持增值税专票吗？',
         '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
        ('企业可以对公转账和签合同吗？',
         f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
        ('我的数据会被用于训练吗？',
         '不会。除法律法规要求外，AnyAIGC 不对你的输入输出内容做持久化存储，也不会用于训练模型，请求通过 HTTPS 加密传输，详见 AnyAIGC <a href="/privacy">隐私政策</a>。模型本身的数据政策以智谱官方条款为准。'),
    ]


def faq_cc(name, model):
    return (f'可以在 Claude Code 里使用 {name} 吗？',
            f'可以。在 <code>~/.claude/settings.json</code> 的 env 中设置 <code>ANTHROPIC_BASE_URL</code> 为 <code>https://anyaigc.ai</code>、<code>ANTHROPIC_AUTH_TOKEN</code> 为你的 API Key、<code>ANTHROPIC_MODEL</code> 为 <code>{model}</code>，然后运行 <code>claude</code> 即可。按 token 计费，没有订阅套餐的 5 小时额度窗口。')


def faq_rpm(name, slug):
    return ('并发和速率有限制吗？',
            f'AnyAIGC 对 <code>{slug}</code> 不设并发限制，所有用户默认享有，适合批量任务、CI 流水线和多 Agent 并行。按 token 计费，也没有订阅套餐那种按时间窗口重置的额度。')


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
    # 先输出思考增量 reasoning_content（如有），再输出最终回答 content
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

# 本地图片转成 Base64 Data URL；也可以直接填公网图片 URL
b64 = base64.b64encode(Path("design.png").read_bytes()).decode()

resp = client.chat.completions.create(
    model="{model}",
    messages=[{{
        "role": "user",
        "content": [
            {{"type": "image_url", "image_url": {{"url": f"data:image/png;base64,{{b64}}"}}}},
            {{"type": "text", "text": "按这张设计稿写一个响应式的 HTML + CSS 页面。"}},
        ],
    }}],
)
print(resp.choices[0].message.content)'''


def code_effort(model):
    return f'''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# 用 reasoning_effort 调整思考深度：low / high / max（默认 max，编程任务官方推荐 max）
resp = client.chat.completions.create(
    model="{model}",
    reasoning_effort="low",
    messages=[{{"role": "user", "content": "把这段 SQL 改写成使用窗口函数的版本：SELECT ..."}}],
)
print(resp.choices[0].message.content)'''


def cc_code(model, haiku=None):
    return f'''{{
  "env": {{
    "ANTHROPIC_BASE_URL": "https://anyaigc.ai",
    "ANTHROPIC_AUTH_TOKEN": "sk-你的 API Key",
    "ANTHROPIC_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "{haiku or model}",
    "API_TIMEOUT_MS": "300000",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }}
}}'''


def cc(name, model, lead, callout, haiku=None):
    return dict(
        kicker='Claude Code', h2=f'在 Claude Code 中使用 {name}', lead=lead,
        steps=['<strong>安装 Claude Code</strong>：按官方方式安装，例如 macOS / Linux 运行 <code>curl -fsSL https://claude.ai/install.sh | bash</code>。',
               '<strong>写入配置</strong>：编辑 <code>~/.claude/settings.json</code>，把下面的 env 加进去，<code>ANTHROPIC_AUTH_TOKEN</code> 换成你在 AnyAIGC 创建的 Key。',
               f'<strong>开始使用</strong>：在项目目录运行 <code>claude</code>，输入 <code>/model</code> 可以确认当前模型是 <code>{model}</code>。'],
        code=cc_code(model, haiku), callout=callout,
        note=f'完整步骤和常见报错见 <a href="{DOCS_CC}" target="_blank" rel="noopener">Claude Code 安装与使用教程</a>，教程里的模型名换成 <code>{model}</code> 即可。')


def qs_steps(model):
    return ['<strong>注册并充值</strong>：在 <a href="' + REG + '">anyaigc.ai</a> 注册账号，最低 $1 起充，余额对平台所有模型通用。',
            '<strong>创建 API Key</strong>：在控制台创建令牌，复制以 <code>sk-</code> 开头的 Key，存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'<strong>发起请求</strong>：请求 <code>POST https://anyaigc.ai/v1/chat/completions</code>，<code>model</code> 填 <code>{model}</code>，鉴权用 <code>Authorization: Bearer</code>。OpenAI SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。']


QS_NOTE = f'完整参数见 <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions 接口文档</a>，文档示例里的模型名换成对应的 GLM 模型 ID 即可。'

PRICE_HEAD = [('计费项', ''), ('模型名', ''), ('AnyAIGC', 'o-num o-hl'), ('智谱官方', 'o-num'), ('节省', 'o-num')]
LABELS = [('输入', '每 100 万 tokens'), ('输出', '每 100 万 tokens，含思考'), ('缓存命中', '每 100 万 tokens')]


def pricing_note(slug):
    q = f'?keyword={slug}' if slug else '?keyword=glm'
    return (f'价格单位为美元，按实际消耗的 tokens 计费，输出包含思考 tokens，重复的请求前缀自动按缓存命中价计费。'
            f'官方价来自 <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">智谱 Z.ai 价格页</a>（美元价），'
            f'表中为模型广场最低价，实时价格以 <a href="{PRICING}{q}">AnyAIGC 模型广场</a> 为准。')


def cost_card(slug, title, calc, inp=0, out=0, cache=0, n=1):
    a = money(cost(slug, inp, out, cache, n))
    b = money(cost(slug, inp, out, cache, n, official=True))
    return (title, calc, a, f'官方 <s>{b}</s>')


def offers(slug):
    return [('输入（每 100 万 tokens）', PRICE[slug][0]), ('输出（每 100 万 tokens）', PRICE[slug][1]),
            ('缓存命中（每 100 万 tokens）', PRICE[slug][2])]


def billing(slug_off):
    return [('按 token 计费', '输入、输出、缓存分别计价'), (slug_off, '相比智谱官方美元价'), ('并发不限', '所有用户默认享有'), ('USD', '余额 300+ 模型通用')]


FAMILY = [
    ('glm', '', ('GLM 全系总览', 'GLM-5.3、GLM-5.3-Flash、GLM-5.2 价格对比与选型')),
    ('glm-5.3', '最新', f'智谱旗舰，编程与 Agent，1M 上下文 · 输入 {p("glm-5.3", 0)} / 1M'),
    ('glm-5.3-flash', '低价', f'原生多模态，320B 总参 18B 激活 · 输入 {p("glm-5.3-flash", 0)} / 1M'),
    ('glm-5.2', '', f'长程任务旗舰，思考可关 · 输入 {p("glm-5.2", 0)} / 1M'),
]


def build(slug):
    return {'glm': hub, 'glm-5.3': g53, 'glm-5.3-flash': gf, 'glm-5.2': g52}[slug]()


# ======================================================================
# 总览页
# ======================================================================
def hub():
    a, f, b = 'glm-5.3', 'glm-5.3-flash', 'glm-5.2'
    faqs = [
        ('GLM API 多少钱？',
         f'AnyAIGC 上 GLM 系列按 token 计费，每百万 tokens：<code>glm-5.3</code> 输入 {p(a, 0)}、输出 {p(a, 1)}、缓存命中 {p(a, 2)}；<code>glm-5.3-flash</code> 输入 {p(f, 0)}、输出 {p(f, 1)}、缓存命中 {p(f, 2)}；'
         f'<code>glm-5.2</code> 输入 {p(b, 0)}、输出 {p(b, 1)}、缓存命中 {p(b, 2)}。GLM-5.3 和 GLM-5.2 约为智谱官方美元价的 7 折，GLM-5.3-Flash 约 4 折，实时价格以模型广场为准。'),
        ('AnyAIGC 上有哪些 GLM 模型？模型 ID 是什么？',
         '本页介绍三款：<code>glm-5.3</code>（智谱最新旗舰，复杂编程与 Agent）、<code>glm-5.3-flash</code>（GLM-5 系列首个原生多模态模型，低价）、<code>glm-5.2</code>（面向长程任务的上一代旗舰）。'
         '调用时把模型 ID 写在请求体的 <code>model</code> 字段里，切换模型只需要改这一个字段。平台上还有 GLM-5.1、GLM-5、GLM-4.5 等更早的型号，可在模型广场查看。'),
        ('GLM-5.3、GLM-5.3-Flash 和 GLM-5.2 怎么选？',
         f'最难的编程、终端和 Agent 任务选 <a href="/zh/models/glm-5.3">GLM-5.3</a>；高频、预算敏感或需要看图的任务选 <a href="/zh/models/glm-5.3-flash">GLM-5.3-Flash</a>，单价约为 GLM-5.3 的十五分之一，官方称它整体超过 GLM-5.2；'
         f'需要关闭思考、或已在生产里跑 GLM-5.2 的业务可以继续用 <a href="/zh/models/glm-5.2">GLM-5.2</a>。GLM-5.3 和 GLM-5.2 单价相同，新项目建议直接用 GLM-5.3。'),
        ('GLM API 兼容 OpenAI 吗？',
         '兼容。三款模型都走 <code>POST https://anyaigc.ai/v1/chat/completions</code>，请求和返回格式与 OpenAI Chat Completions 一致，OpenAI 官方 SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。思考过程（如有）在返回的 <code>reasoning_content</code> 字段里。'),
        faq_cc('GLM', 'glm-5.3'),
        ('上下文窗口有多大？',
         '智谱官方公布：GLM-5.3、GLM-5.3-Flash、GLM-5.2 都支持 1M tokens 上下文，最大输出 128K tokens。GLM-5.3 和 GLM-5.2 只支持文本输入，GLM-5.3-Flash 支持图片输入。'),
        ('GLM 和 GLM Coding Plan 有什么区别？',
         'GLM Coding Plan 是智谱的编程订阅套餐，按月付费，额度按 5 小时和每周窗口重置。AnyAIGC 是按 token 计费的 API：用多少付多少，$1 起充，没有时间窗口限制，并发不限，同一个 Key 还能调用平台上 300+ 其他模型。'),
        ('GLM 模型是开源的吗？可以商用吗？',
         '智谱已在 Hugging Face 公开 GLM-5.3、GLM-5.3-Flash 和 GLM-5.2 的权重：GLM-5.2 和 GLM-5.3-Flash 为 MIT 许可，GLM-5.3 为 GLM-5.3 License（宽松许可，另有针对超大型 MaaS 企业的安全审查条款）。通过 AnyAIGC 调用 API 不需要自己部署，模型许可和商用授权以智谱官方条款为准。'),
        faq_rpm('GLM', 'glm-5.3、glm-5.3-flash、glm-5.2'),
    ] + faq_common('GLM', 'glm')
    faqs[8] = ('并发和速率有限制吗？',
               'AnyAIGC 对 GLM 系列不设并发限制，所有用户默认享有，适合批量任务、CI 流水线和多 Agent 并行。按 token 计费，也没有订阅套餐那种按时间窗口重置的额度。')
    return dict(
        title='GLM API 价格与接入｜智谱 GLM-5.3 / 5.3-Flash / 5.2 - AnyAIGC',
        desc=f'智谱 GLM API：一个 Key 调用 GLM-5.3、GLM-5.3-Flash、GLM-5.2，输入 {p(f, 0)}/1M 起，1M 上下文，约官方 4–7 折，可接入 Claude Code，并发不限，支持对公转账与专票。',
        og_desc='GLM-5.3、GLM-5.3-Flash、GLM-5.2 一个 Key 调用，约智谱官方价 4–7 折，OpenAI 兼容接口，可接入 Claude Code，并发不限，支持对公转账与增值税专票。',
        og_alt='AnyAIGC GLM API：GLM-5.3、GLM-5.3-Flash、GLM-5.2 约官方价 4–7 折',
        keywords='GLM API,智谱 API,智谱 GLM API,GLM API 价格,GLM API key,GLM-5.3 API,GLM-5.3-Flash API,GLM-5.2 API,GLM Claude Code,GLM Coding Plan 替代,智谱 API 国内,GLM API 企业,GLM API 发票,GLM API 对公转账,AnyAIGC',
        crumb='GLM API', product='GLM API（AnyAIGC）', sku='glm',
        product_desc='通过 AnyAIGC 调用智谱 GLM 系列模型（glm-5.3、glm-5.3-flash、glm-5.2）：OpenAI 兼容 /v1/chat/completions，按 token 计费，约官方价 4–7 折，并发不限。',
        offers=[(f'{n} 输入（每 100 万 tokens）', PRICE[s][0]) for s, n in ((a, 'GLM-5.3'), (f, 'GLM-5.3-Flash'), (b, 'GLM-5.2'))]
        + [(f'{n} 输出（每 100 万 tokens）', PRICE[s][1]) for s, n in ((a, 'GLM-5.3'), (f, 'GLM-5.3-Flash'), (b, 'GLM-5.2'))],
        hero=dict(eyebrow='智谱 Z.ai · GLM',
                  h1='GLM <span class="g-blue">API</span>',
                  lead='智谱 GLM-5.3、GLM-5.3-Flash、GLM-5.2 三款模型，一个 API Key 全部调用。GLM-5.3 约为官方价的 7 折，GLM-5.3-Flash 约 4 折。',
                  ask='用 GLM 读完这个仓库，修好失败的测试并补上缺失的类型定义',
                  chips=['复杂编程', '1M 上下文', 'Agent'],
                  sub=f'OpenAI 兼容的 <code>/v1/chat/completions</code>，也能直接接入 Claude Code。<code>glm-5.3-flash</code> 输入 {p(f, 0)} / 百万 tokens 起，并发不限。',
                  facts=[('型号', 'GLM-5.3 · 5.3-Flash · 5.2'), ('上下文', '1M'), ('输入', f'{p(f, 0)} / 1M 起'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        models=dict(kicker='型号', h2='GLM 系列三款模型', lead='同一个 Key、同一个接口，按任务换模型 ID 即可。',
                    unit_in='1M 输入', unit_out='1M 输出', go='查看专题',
                    items=[(a, '最新', '智谱最新旗舰，与 GLM-5.2 同一基座，靠扩展后训练全面提升复杂编程、终端任务和 Agent 能力。', ['1M 上下文，最大输出 128K', '官方称 Z.ai Code Bench 比 5.2 提升 50%', '思考始终开启，reasoning_effort 可调']),
                           (f, '低价', 'GLM-5 系列首个原生多模态模型，320B 总参数、18B 激活，官方称整体超过 GLM-5.2，价格约为其十分之一。', ['1M 上下文，支持图片输入', 'Toolathlon Verified 78.4', '单价约为 GLM-5.3 的 1/15']),
                           (b, '', '面向长程任务的上一代旗舰，真正可用的 1M 上下文，能在单个任务里完成从需求到多端部署的完整开发链路。', ['1M 上下文，最大输出 128K', '思考可开可关', 'MIT 开源许可'])]),
        pricing=dict(kicker='价格', h2='GLM API 价格', lead='按 token 计费，固定单价，没有订阅和月费。GLM-5.3、GLM-5.2 约为智谱官方美元价的 7 折，GLM-5.3-Flash 约 4 折。',
                     billing_label='计费要点',
                     billing=billing('约 4–7 折'),
                     head=[('计费项', ''), ('AnyAIGC', 'o-num o-hl'), ('智谱官方', 'o-num'), ('节省', 'o-num')],
                     labels=LABELS, caption='GLM 系列每百万 tokens 价格（美元），AnyAIGC 与智谱官方对比',
                     note=pricing_note(''),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的智谱官方价。',
                     costs=[cost_card(a, 'GLM-5.3 · Agent 编程 20 轮', '每轮 5 万 tokens 缓存命中 + 5,000 输入 + 3,000 输出', 5000, 3000, 50000, 20),
                            cost_card(f, 'GLM-5.3-Flash · 1 万条工单分类', '每条 2,000 tokens 输入 + 300 输出', 2000, 300, 0, 10000),
                            cost_card(b, 'GLM-5.2 · 审查 100 个 PR', '每个 PR 2 万 tokens 输入 + 2,000 输出', 20000, 2000, 0, 100)]),
        compare=dict(kicker='选型', h2='GLM-5.3、GLM-5.3-Flash、GLM-5.2 怎么选', lead='最难的任务交给 GLM-5.3，高频和看图用 GLM-5.3-Flash，要关闭思考用 GLM-5.2。',
                     head=[('对比项', ''), ('GLM-5.3', 'o-num o-hl'), ('GLM-5.3-Flash', 'o-num'), ('GLM-5.2', 'o-num')],
                     rows=[('定位', '', '最新旗舰', '原生多模态，低价', '长程任务旗舰'),
                           ('上下文 / 最大输出', '', '1M / 128K', '1M / 128K', '1M / 128K'),
                           ('输入模态', '', '文本', '文本、图片', '文本'),
                           ('思考模式', '', '始终开启', '始终开启', '可开可关'),
                           ('AnyAIGC 输入', '每百万 tokens', p(a, 0), p(f, 0), p(b, 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(a, 1), p(f, 1), p(b, 1)),
                           ('缓存命中', '每百万 tokens', p(a, 2), p(f, 2), p(b, 2))],
                     caption='GLM-5.3、GLM-5.3-Flash、GLM-5.2 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自智谱 Z.ai 官方文档，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。'),
        uses=dict(kicker='使用场景', h2='用 GLM API 做什么',
                  items=[('01 · 复杂编程', '大仓库重构和终端任务', 'GLM-5.3 的 1M 上下文能放下整个代码库，配合终端工具连续工作。官方公布 Terminal Bench 2.1 为 88.2。'),
                         ('02 · Coding Agent', 'Claude Code、CI 和自动修复', '把 GLM 接进 Claude Code 或自己的 Agent 框架，跑测试、读报错、改代码。AnyAIGC 不限并发，多个 Agent 可以同时跑。'),
                         ('03 · 看图写代码', '从设计稿生成界面', 'GLM-5.3-Flash 支持图片输入，把设计稿或页面截图交给它，直接输出 HTML、CSS 或组件代码。'),
                         ('04 · 批量处理', '分类、抽取和摘要', 'GLM-5.3-Flash 输入 ' + p(f, 0) + ' / 百万 tokens，适合工单分类、字段抽取、长文档摘要这类大批量任务。')]),
        qs=dict(kicker='快速开始', h2='三步接入 GLM API', steps=qs_steps('glm-5.3'),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl('glm-5.3', '用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py('glm-5.3', '你是资深后端工程师，回答要给出可运行的代码。', '用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('stream', '流式输出', 'Python · stream=True', code_stream('glm-5.3-flash', '给一个 SaaS 产品写 5 条更新日志。'))],
                callout='<strong>参数提示：</strong>GLM 的思考过程在 <code>reasoning_content</code> 字段，流式输出时先返回思考增量，再返回最终回答。思考深度用 <code>reasoning_effort</code> 调整（<code>low</code> / <code>high</code> / <code>max</code>，默认 <code>max</code>）。多轮对话和工具调用时，要把 API 返回的完整 assistant 消息（包括 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('GLM', 'glm-5.3', '把 Claude Code 的模型换成 GLM：改一个配置文件，终端里的编程 Agent 就由 GLM-5.3 驱动，按 token 计费。',
              '<strong>省钱搭配：</strong>配置里已把 <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> 设成 <code>glm-5.3-flash</code>，Claude Code 的轻量子任务走更便宜的模型，主任务继续用 GLM-5.3。', haiku='glm-5.3-flash'),
        family_h2='GLM 系列全部型号', family_lead='同一个 API Key 可以调用下面所有 GLM 模型，按任务难度和预算选择。',
        faq_h2='GLM API 常见问题', faqs=faqs,
        final=dict(h2='用约 7 折的价格跑 GLM', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 GLM-5.3、GLM-5.3-Flash 和 GLM-5.2。',
                   other='GLM API in English'),
        ent_name='GLM',
    )


# ======================================================================
# GLM-5.3
# ======================================================================
def g53():
    s = 'glm-5.3'
    faqs = [
        ('GLM-5.3 API 多少钱？',
         f'AnyAIGC 上 <code>glm-5.3</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'智谱官方美元价为输入 {o(s, 0)}、输出 {o(s, 1)}、缓存命中 {o(s, 2)}，AnyAIGC 的输入、输出约为官方价的 67.5%（约 7 折）。输出包含思考 tokens，实时价格以模型广场为准。'),
        ('GLM-5.3 的模型 ID 是什么？上下文多大？',
         '模型 ID 是 <code>glm-5.3</code>。智谱官方公布的上下文窗口为 1M tokens，最大输出 128K tokens，目前只支持文本输入。'),
        ('GLM-5.3 和 GLM-5.2 有什么区别？',
         f'官方说明 GLM-5.3 与 <a href="/zh/models/glm-5.2">GLM-5.2</a> 使用同一个基座模型，所有提升都来自扩展后训练。官方公布的变化：Z.ai Code Bench 比 GLM-5.2 提升 50%，Terminal Bench 3.0 从 4.6 提升到 28.3，DeepSWE 从 46.2 提升到 66.9。'
         f'另一个区别是 GLM-5.3 思考始终开启，不能关闭。两者在 AnyAIGC 输入、输出单价相同，GLM-5.3 的缓存命中价更低（{p(s, 2)} 对 {p("glm-5.2", 2)}）。'),
        ('怎么调整 GLM-5.3 的思考深度？能关闭思考吗？',
         'GLM-5.3 思考始终开启，官方不支持关闭。用请求体的 <code>reasoning_effort</code> 字段调整思考深度，可选 <code>low</code>、<code>high</code>、<code>max</code>，默认 <code>max</code>，编程任务官方推荐 <code>max</code>。简单任务用 <code>low</code> 可以减少输出 tokens。'),
        ('GLM-5.3 支持工具调用和结构化输出吗？',
         '支持。官方文档列出函数调用、结构化输出（JSON）、流式输出和上下文缓存。多轮和工具调用时，需要把返回的完整 assistant 消息（含 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。'),
        faq_cc('GLM-5.3', s),
        ('GLM-5.3 是开源的吗？',
         '是。智谱已在 Hugging Face 发布 GLM-5.3 权重（zai-org/GLM-5.3），许可为 GLM-5.3 License：整体是宽松许可，另规定集团年收入超过 100 亿美元、经营模型即服务业务的企业，商用前需通过 Z.ai 的安全审查。通过 AnyAIGC 调用 API 不需要自己部署，商用授权以智谱官方条款为准。'),
        faq_rpm('GLM-5.3', s),
    ] + faq_common('GLM-5.3', s)
    return dict(
        title='GLM-5.3 API 价格与接入｜智谱旗舰 1M 上下文 约官方 7 折 - AnyAIGC',
        desc=f'glm-5.3 API：智谱最新旗舰，复杂编程与 Agent 任务全面进阶，1M 上下文，输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方价 7 折，可接入 Claude Code，并发不限，支持对公转账与专票。',
        og_desc=f'glm-5.3 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约智谱官方价 7 折。智谱最新旗舰，1M 上下文，官方称编程能力比 GLM-5.2 提升 50%，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC GLM-5.3 API：约官方价 7 折',
        keywords='GLM-5.3 API,glm-5.3,GLM-5.3 API 价格,GLM-5.3 接入,GLM-5.3 API key,GLM-5.3 Claude Code,GLM-5.3 1M 上下文,GLM-5.3 和 GLM-5.2 区别,智谱 GLM-5.3,智谱 API,GLM API,GLM-5.3 API 企业,GLM-5.3 API 发票,GLM API 对公转账,AnyAIGC',
        crumb='GLM-5.3 API', product='GLM-5.3 API（AnyAIGC）', sku=s,
        product_desc='通过 AnyAIGC 调用智谱 GLM-5.3（glm-5.3）：OpenAI 兼容 /v1/chat/completions，1M 上下文，按 token 计费，约官方价 7 折，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow='智谱 Z.ai · glm-5.3',
                  h1='GLM-<span class="g-blue">5.3</span><span class="o-sr"> API</span>',
                  lead='智谱最新旗舰，复杂软件工程与 Agent 任务全面进阶。和 GLM-5.2 同一个基座，靠扩展后训练把编程能力再提升一截。在 AnyAIGC 调用约为官方价的 7 折。',
                  ask='在终端里排查这个服务的内存泄漏，给出修复补丁和回归测试',
                  chips=['终端编程', '1M 上下文', 'Agent'],
                  sub=f'<code>glm-5.3</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='同一个基座，后训练全面加强',
                   paras=['智谱称 GLM-5.3 是其最新旗舰模型，复杂软件工程与 Agent 任务能力全面进阶。官方说明它与 GLM-5.2 使用同一个基座模型，所有提升都来自扩展后训练，沿用了 GLM-5.2 引入的强化学习策略。',
                          '官方公布的提升集中在编程和 Agent：内部 Z.ai Code Bench 比 GLM-5.2 提升 50%，而且同样的任务输出 tokens 更少；Terminal Bench 3.0 从 4.6 提升到 28.3。官方还称它在漏洞挖掘基准 CyberGym 上达到 SOTA。上下文 1M tokens，最大输出 128K，思考始终开启。',
                          '在 AnyAIGC 上，<code>glm-5.3</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，也能在 Claude Code 里直接使用。不需要智谱开放平台账号，也不用买 Coding Plan，按 token 计费，并发不限。'],
                   spec=[('上下文窗口', '1M', 'tokens'), ('最大输出', '128K', 'tokens'),
                         ('架构', 'MoE + DSA', '稀疏注意力，与 GLM-5.2 同基座'), ('输入模态', '文本', '仅文本输入'),
                         ('思考模式', '始终开启', 'reasoning_effort：low / high / max'), ('权重', '开放', 'Hugging Face zai-org/GLM-5.3')]),
        features=dict(kicker='能力', h2='GLM-5.3 能做什么',
                      items=[('终端与长程编程', '官方公布 Terminal Bench 2.1 为 88.2，Terminal Bench 3.0 为 28.3（GLM-5.2 为 4.6），适合在终端里连续完成长周期工程任务。'),
                             ('软件工程', '官方公布 DeepSWE v1.1 为 66.9、FrontierSWE 为 78.1、NL2Repo 为 58，从修 bug 到从零搭仓库都能做。'),
                             ('更省 tokens 的编程', '官方内部 Z.ai Code Bench：max 深度下 GLM-5.3 为 34.5%、平均约 75K 输出 tokens，GLM-5.2 为 23.4%、约 96K tokens。'),
                             ('安全研究', '官方称 GLM-5.3 在 CyberGym 漏洞复现基准上为 84.5，在 269 个开源项目里发现了 2,436 个漏洞。'),
                             ('Agent 与工具调用', '官方公布 Toolathlon Verified 73、AutomationBench 48.2、Agents\' Last Exam 28.5，支持函数调用和结构化输出。'),
                             ('思考深度可调', '思考始终开启，用 reasoning_effort 在 low、high、max 之间调节，简单任务省 tokens，难题用 max。')]),
        pricing=dict(kicker='价格', h2='GLM-5.3 API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入、输出约为智谱官方美元价的 67.5%（约 7 折）。',
                     billing_label='计费要点',
                     billing=billing('约 7 折'),
                     head=PRICE_HEAD, labels=LABELS, caption='glm-5.3 每百万 tokens 价格（美元），AnyAIGC 与智谱官方对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的智谱官方价。',
                     costs=[cost_card(s, 'Agent 编程 20 轮', '每轮 5 万 tokens 缓存命中 + 5,000 输入 + 3,000 输出', 5000, 3000, 50000, 20),
                            cost_card(s, '50 万 tokens 代码库分析', '50 万 tokens 输入 + 5,000 输出', 500000, 5000),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='GLM-5.3 的官方基准成绩', lead='智谱在 GLM-5.3 技术博客中公布的成绩，下表列出与 GLM-5.2 的对比。',
                   chart=('GLM-5.3 对比 GLM-5.2 · 官方评测', [('GLM-5.3 · DeepSWE', 66.9, True), ('GLM-5.2 · DeepSWE', 46.2, False),
                                                       ('GLM-5.3 · FrontierSWE', 78.1, True), ('GLM-5.2 · FrontierSWE', 67.5, False),
                                                       ('GLM-5.3 · Toolathlon', 73, True), ('GLM-5.2 · Toolathlon', 59.9, False)]),
                   head=[('基准', ''), ('GLM-5.3', 'o-num o-hl'), ('GLM-5.2', 'o-num')],
                   rows=[('Terminal Bench 2.1', '终端编程', '88.2', '81.0'), ('Terminal Bench 3.0', '终端编程', '28.3', '4.6'),
                         ('DeepSWE v1.1', '软件工程', '66.9', '46.2'), ('NL2Repo', '从零生成仓库', '58.0', '48.9'),
                         ('FrontierSWE', '软件工程', '78.1', '67.5'), ('SWE-Marathon v1.1', '长程软件工程', '42.5', '19.4'),
                         ('PostTrainBench', '模型后训练任务', '39.8', '31.7'), ('CyberGym', '漏洞复现', '84.5', '77.2'),
                         ('ExploitBench', '漏洞利用', '54.4', '24.4'), ('Toolathlon Verified', '工具调用', '73.0', '59.9'),
                         ('AutomationBench v1.0.6', '自动化 Agent', '48.2', '26.2'), ("Agents' Last Exam", 'Agent 综合', '28.5', '23.8'),
                         ('HLE w/ Tools', '综合推理，带工具', '62.5', '54.7'), ('GDPval-AA v2', '知识工作，Elo', '1769', '1508')],
                   caption='GLM-5.3 与 GLM-5.2 的官方基准对比（智谱公布）',
                   note=f'数据来自 <a href="{B53}" target="_blank" rel="noopener">GLM-5.3 技术博客</a>，为智谱公布的成绩，博客中还列出了与其他开源和闭源模型的对比。'),
        compare=dict(kicker='选型', h2='GLM-5.3 和 GLM-5.3-Flash、GLM-5.2 怎么选', lead='新项目优先用 GLM-5.3。高频、预算敏感或需要看图的任务可以用 GLM-5.3-Flash。',
                     head=[('对比项', ''), ('GLM-5.3', 'o-num o-hl'), ('GLM-5.3-Flash', 'o-num'), ('GLM-5.2', 'o-num')],
                     rows=[('定位', '', '最新旗舰', '原生多模态，低价', '长程任务旗舰'), ('上下文', '', '1M', '1M', '1M'),
                           ('输入模态', '', '文本', '文本、图片', '文本'), ('思考模式', '', '始终开启', '始终开启', '可开可关'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p('glm-5.3-flash', 0), p('glm-5.2', 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p('glm-5.3-flash', 1), p('glm-5.2', 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p('glm-5.3-flash', 2), p('glm-5.2', 2))],
                     caption='GLM-5.3、GLM-5.3-Flash、GLM-5.2 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自智谱 Z.ai 官方文档，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。详见 <a href="/zh/models/glm-5.3-flash">GLM-5.3-Flash API</a> 和 <a href="/zh/models/glm-5.2">GLM-5.2 API</a>。'),
        uses=dict(kicker='使用场景', h2='GLM-5.3 适合做什么',
                  items=[('01 · 大仓库', '跨模块重构与迁移', '把整个代码库放进 1M 上下文，让 GLM-5.3 理清依赖后给出改动方案，再配合终端工具逐步执行和验证。'),
                         ('02 · Coding Agent', 'Claude Code 和自研 Agent', '在 Claude Code 或自己的 Agent 框架里跑几十上百步的任务：读代码、跑测试、修报错。AnyAIGC 不限并发。'),
                         ('03 · 安全', '代码审计与漏洞排查', '让模型审查依赖和业务代码、复现已知漏洞、给出修复补丁。官方称 GLM-5.3 在 CyberGym 上为 SOTA。'),
                         ('04 · 自动化', '工具调用和流程编排', '函数调用加结构化输出，把内部系统、脚本和 API 串成自动化流程。重复的系统提示按缓存命中价计费。')]),
        qs=dict(kicker='快速开始', h2='三步接入 GLM-5.3 API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, '用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, '你是资深后端工程师，回答要给出可运行的代码。', '用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('effort', '思考深度', 'Python · reasoning_effort', code_effort(s)),
                      ('tools', '工具调用', 'Python · tools', code_tools(s))],
                callout='<strong>参数提示：</strong>GLM-5.3 思考始终开启，思考过程在 <code>reasoning_content</code> 字段，思考深度用 <code>reasoning_effort</code> 调整。官方默认 <code>temperature=1.0</code>、<code>top_p=0.95</code>，建议只调其中一个。多轮对话和工具调用时，要把 API 返回的完整 assistant 消息（包括 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('GLM-5.3', s, '把 Claude Code 的模型换成 GLM-5.3：改一个配置文件，在终端里用智谱最新旗舰写代码，按 token 计费。',
              '<strong>省钱搭配：</strong>配置里已把 <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> 设成 <code>glm-5.3-flash</code>，Claude Code 的轻量子任务走更便宜的模型，主任务继续用 GLM-5.3。', haiku='glm-5.3-flash'),
        family_h2='GLM 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 GLM 模型，按任务难度和预算选择。',
        faq_h2='GLM-5.3 API 常见问题', faqs=faqs,
        final=dict(h2='用约 7 折的价格跑 GLM-5.3', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 glm-5.3。', other='GLM-5.3 API in English'),
        ent_name='GLM-5.3',
    )


# ======================================================================
# GLM-5.3-Flash
# ======================================================================
def gf():
    s = 'glm-5.3-flash'
    faqs = [
        ('GLM-5.3-Flash API 多少钱？',
         f'AnyAIGC 上 <code>glm-5.3-flash</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'智谱官方美元价为输入 {o(s, 0)}、输出 {o(s, 1)}、缓存命中 {o(s, 2)}，AnyAIGC 约为官方价的 40.5%（约 4 折）。输出包含思考 tokens，实时价格以模型广场为准。'),
        ('GLM-5.3-Flash 的模型 ID 是什么？上下文多大？',
         '模型 ID 是 <code>glm-5.3-flash</code>。智谱官方公布的上下文窗口为 1M tokens，最大输出 128K tokens，通过 AnyAIGC 支持文本和图片输入。'),
        ('GLM-5.3-Flash 和 GLM-5.3 有什么区别？',
         f'GLM-5.3-Flash 基于全新训练的基座：320B 总参数、18B 激活，混合稀疏注意力与线性注意力，是 GLM-5 系列首个原生多模态模型。官方称相比 <a href="/zh/models/glm-5.3">GLM-5.3</a>，注意力计算降低约 3 倍、KV cache 降低约 4.4 倍。'
         f'GLM-5.3 是更强的旗舰，适合最难的编程任务，只支持文本；Flash 支持图片输入，单价约为 GLM-5.3 的十五分之一（输入 {p(s, 0)} 对 {p("glm-5.3", 0)}）。'),
        ('GLM-5.3-Flash 比 GLM-5.2 强吗？',
         f'官方称 GLM-5.3-Flash 整体超过 <a href="/zh/models/glm-5.2">GLM-5.2</a>，价格约为其十分之一。官方公布的对比：DeepSWE 63.4 对 46.2，Toolathlon Verified 78.4 对 59.9，AutomationBench 48.8 对 26.2，GDPval-AA v2 1773 对 1504。'),
        ('GLM-5.3-Flash 支持图片输入吗？怎么传？',
         '支持。在 <code>messages[].content</code> 数组里放 <code>{"type": "image_url", "image_url": {"url": ...}}</code> 内容块，<code>url</code> 可以是公网图片地址，也可以是 Base64 Data URL，多张图就放多个内容块。'),
        faq_cc('GLM-5.3-Flash', s),
        ('GLM-5.3-Flash 能关闭思考吗？',
         'GLM-5.3-Flash 思考始终开启，官方不支持关闭。用 <code>reasoning_effort</code> 调整思考深度，可选 <code>low</code>、<code>high</code>、<code>max</code>，默认 <code>max</code>。分类、抽取这类简单任务用 <code>low</code> 可以减少输出 tokens。'),
        ('GLM-5.3-Flash 是开源的吗？',
         '是。智谱已在 Hugging Face 以 MIT 许可发布 GLM-5.3-Flash 权重（zai-org/GLM-5.3-Flash）。通过 AnyAIGC 调用 API 不需要自己部署，商用授权以智谱官方条款为准。'),
        faq_rpm('GLM-5.3-Flash', s),
    ] + faq_common('GLM-5.3-Flash', s)
    return dict(
        title='GLM-5.3-Flash API 价格与接入｜原生多模态 约官方 4 折 - AnyAIGC',
        desc=f'glm-5.3-flash API：智谱 GLM-5 系列首个原生多模态模型，支持图片输入，1M 上下文，输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方价 4 折，并发不限，支持对公转账与专票。',
        og_desc=f'glm-5.3-flash 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约智谱官方价 4 折。原生多模态，320B 总参 18B 激活，官方称整体超过 GLM-5.2，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC GLM-5.3-Flash API：约官方价 4 折',
        keywords='GLM-5.3-Flash API,glm-5.3-flash,GLM-5.3-Flash API 价格,GLM-5.3-Flash 接入,GLM-5.3-Flash 多模态,GLM-5.3-Flash 图片输入,GLM-5.3-Flash Claude Code,GLM-5.3-Flash 和 GLM-5.3 区别,智谱 Flash API,GLM API,GLM-5.3-Flash API 企业,GLM-5.3-Flash API 发票,GLM API 对公转账,AnyAIGC',
        crumb='GLM-5.3-Flash API', product='GLM-5.3-Flash API（AnyAIGC）', sku=s,
        product_desc='通过 AnyAIGC 调用智谱 GLM-5.3-Flash（glm-5.3-flash）：OpenAI 兼容 /v1/chat/completions，原生多模态，1M 上下文，按 token 计费，约官方价 4 折，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow='智谱 Z.ai · glm-5.3-flash',
                  h1='GLM-5.3-<span class="g-blue">Flash</span><span class="o-sr"> API</span>',
                  lead='GLM-5 系列首个原生多模态模型，320B 总参数、18B 激活。官方称它整体超过 GLM-5.2，价格只有其十分之一。在 AnyAIGC 调用约为官方价的 4 折。',
                  ask='看这张页面截图，把它还原成可上线的 React 组件',
                  chips=['原生多模态', '低价', '1M 上下文'],
                  sub=f'<code>glm-5.3-flash</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，约为 GLM-5.3 的十五分之一。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='新基座、新架构的原生多模态模型',
                   paras=['智谱称 GLM-5.3-Flash 是 GLM-5 系列首个原生多模态模型，以极低成本提供超过 GLM-5.2 的能力。和 GLM-5.3 不同，它从一个全新训练的基座开始，预训练语料约 30T tokens，覆盖多模态数据。',
                          '架构上是 320B 总参数、18B 激活的 MoE，官方称它是首个把稀疏注意力和线性注意力结合起来的开源前沿模型，并采用流形约束超连接（mHC）。相比 GLM-5.3，注意力计算降低约 3 倍、KV cache 降低约 4.4 倍，在保持长上下文能力的同时大幅降低了服务成本。上下文 1M tokens，最大输出 128K，思考始终开启。',
                          '在 AnyAIGC 上，<code>glm-5.3-flash</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，支持文本和图片输入，也能在 Claude Code 里直接使用，并发不限。'],
                   spec=[('上下文窗口', '1M', 'tokens'), ('最大输出', '128K', 'tokens'),
                         ('参数规模', '320B', '18B 激活，MoE'), ('输入模态', '文本、图片', '原生多模态'),
                         ('思考模式', '始终开启', 'reasoning_effort：low / high / max'), ('权重', '开放', 'MIT 许可')]),
        features=dict(kicker='能力', h2='GLM-5.3-Flash 能做什么',
                      items=[('看图写代码', '官方公布 Vision2Web 77.8，根据设计稿、截图生成和修正前端界面。'),
                             ('图表与文档理解', '官方公布 CharXiv Reasoning（带工具）89.4、OfficeQA Pro 62.4，适合读图表、读报表、做办公交付物。'),
                             ('编程与 Agent', '官方公布 Terminal Bench 2.1 为 84.3、DeepSWE 为 63.4、Toolathlon Verified 为 78.4，整体超过 GLM-5.2。'),
                             ('计算机操作', '官方公布 OSWorld 2.0 为 59.1，能根据屏幕截图规划和执行操作。'),
                             ('低成本长上下文', f'1M 上下文，输入 {p(s, 0)}、缓存命中 {p(s, 2)} / 百万 tokens，长文档和多轮 Agent 都更省。'),
                             ('适合高频调用', 'AnyAIGC 不限并发，批量分类、抽取、摘要和多 Agent 并行都能直接跑。')]),
        pricing=dict(kicker='价格', h2='GLM-5.3-Flash API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入、输出、缓存命中都约为智谱官方美元价的 40.5%（约 4 折）。',
                     billing_label='计费要点',
                     billing=billing('约 4 折'),
                     head=PRICE_HEAD, labels=LABELS, caption='glm-5.3-flash 每百万 tokens 价格（美元），AnyAIGC 与智谱官方对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的智谱官方价。',
                     costs=[cost_card(s, '1 万条工单分类', '每条 2,000 tokens 输入 + 300 输出', 2000, 300, 0, 10000),
                            cost_card(s, 'Coding Agent 50 轮', '每轮 4 万 tokens 缓存命中 + 4,000 输入 + 2,000 输出', 4000, 2000, 40000, 50),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='比 GLM-5.2 强在哪里', lead='智谱在 GLM-5.3-Flash 技术博客中公布的成绩，下表列出与 GLM-5.2 的对比；视觉类基准 GLM-5.2 不支持，只列 Flash 的成绩。',
                   chart=('GLM-5.3-Flash 对比 GLM-5.2 · 官方评测', [('5.3-Flash · DeepSWE', 63.4, True), ('5.2 · DeepSWE', 46.2, False),
                                                              ('5.3-Flash · Toolathlon', 78.4, True), ('5.2 · Toolathlon', 59.9, False),
                                                              ('5.3-Flash · AutomationBench', 48.8, True), ('5.2 · AutomationBench', 26.2, False)]),
                   head=[('基准', ''), ('GLM-5.3-Flash', 'o-num o-hl'), ('GLM-5.2', 'o-num')],
                   rows=[('Terminal Bench 2.1', '终端编程', '84.3', '81.0'), ('DeepSWE v1.1', '软件工程', '63.4', '46.2'),
                         ('NL2Repo', '从零生成仓库', '56.3', '48.9'), ('Toolathlon Verified', '工具调用', '78.4', '59.9'),
                         ('AutomationBench v1.0.6', '自动化 Agent', '48.8', '26.2'), ("Agents' Last Exam", 'Agent 综合', '26.3', '20.4'),
                         ('HLE w/ Tools', '综合推理，带工具', '55.3', '54.7'), ('GDPval-AA v2', '知识工作，Elo', '1773', '1504'),
                         ('OfficeQA Pro', '办公与金融问答', '62.4', '–'), ('CharXiv Reasoning', '图表推理，带工具', '89.4', '–'),
                         ('OSWorld 2.0', '计算机操作', '59.1', '–'), ('Vision2Web', '截图生成网页', '77.8', '–')],
                   caption='GLM-5.3-Flash 与 GLM-5.2 的官方基准对比（智谱公布）',
                   note=f'数据来自 <a href="{BF}" target="_blank" rel="noopener">GLM-5.3-Flash 技术博客</a>，为智谱公布的成绩；“–”表示 GLM-5.2 不支持该类任务或官方未公布。'),
        compare=dict(kicker='选型', h2='GLM-5.3-Flash、GLM-5.3 和 GLM-5.2 怎么选', lead='高频、看图和预算敏感的任务用 Flash，最难的编程任务交给 GLM-5.3。',
                     head=[('对比项', ''), ('GLM-5.3-Flash', 'o-num o-hl'), ('GLM-5.3', 'o-num'), ('GLM-5.2', 'o-num')],
                     rows=[('定位', '', '原生多模态，低价', '最新旗舰', '长程任务旗舰'), ('上下文', '', '1M', '1M', '1M'),
                           ('输入模态', '', '文本、图片', '文本', '文本'), ('思考模式', '', '始终开启', '始终开启', '可开可关'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p('glm-5.3', 0), p('glm-5.2', 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p('glm-5.3', 1), p('glm-5.2', 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p('glm-5.3', 2), p('glm-5.2', 2))],
                     caption='GLM-5.3-Flash、GLM-5.3、GLM-5.2 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自智谱 Z.ai 官方文档，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。详见 <a href="/zh/models/glm-5.3">GLM-5.3 API</a>。'),
        uses=dict(kicker='使用场景', h2='GLM-5.3-Flash 适合做什么',
                  items=[('01 · 前端', '设计稿到组件', '上传设计稿或页面截图，生成 React、Vue 或原生 HTML/CSS，再按渲染结果迭代。'),
                         ('02 · 批量处理', '分类、抽取和摘要', '工单分类、字段抽取、评论打标、长文档摘要。单价低、不限并发，适合大批量并行。'),
                         ('03 · 文档与图表', '报表、PDF 截图和图表', '把报表截图、扫描件页面或图表交给模型，抽取数据、核对数字、写分析结论。'),
                         ('04 · Coding Agent', 'Claude Code 的经济选择', '在 Claude Code 里用 Flash 处理日常编码，或者只把它设成轻量子任务模型，主任务交给 GLM-5.3。')]),
        qs=dict(kicker='快速开始', h2='三步接入 GLM-5.3-Flash API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, '用三句话解释什么是数据库索引')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, '你是资深前端工程师，回答要给出可运行的代码。', '写一个无障碍友好的下拉菜单组件。')),
                      ('vision', '图片输入', 'Python · image_url', code_vision(s)),
                      ('stream', '流式输出', 'Python · stream=True', code_stream(s, '给一个 SaaS 产品写 5 条更新日志。'))],
                callout='<strong>参数提示：</strong>GLM-5.3-Flash 思考始终开启，思考过程在 <code>reasoning_content</code> 字段，用 <code>reasoning_effort</code>（<code>low</code> / <code>high</code> / <code>max</code>）调整思考深度。图片用 <code>image_url</code> 内容块传入，支持公网 URL 和 Base64。多轮对话和工具调用时，要把完整的 assistant 消息原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('GLM-5.3-Flash', s, '把 Claude Code 的模型换成 GLM-5.3-Flash：单价约为 GLM-5.3 的十五分之一，日常编码和读图改界面都能用。',
              '<strong>遇到难题：</strong>复杂的跨模块重构或长周期任务，可以把配置里的 <code>ANTHROPIC_MODEL</code> 换成 <code>glm-5.3</code>，轻量子任务继续用 Flash。'),
        family_h2='GLM 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 GLM 模型，按任务难度和预算选择。',
        faq_h2='GLM-5.3-Flash API 常见问题', faqs=faqs,
        final=dict(h2='用约 4 折的价格跑 GLM-5.3-Flash', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 glm-5.3-flash。', other='GLM-5.3-Flash API in English'),
        ent_name='GLM-5.3-Flash',
    )


# ======================================================================
# GLM-5.2
# ======================================================================
def g52():
    s = 'glm-5.2'
    faqs = [
        ('GLM-5.2 API 多少钱？',
         f'AnyAIGC 上 <code>glm-5.2</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'智谱官方美元价为输入 {o(s, 0)}、输出 {o(s, 1)}、缓存命中 {o(s, 2)}，AnyAIGC 的输入、输出约为官方价的 67.5%（约 7 折）。实时价格以模型广场为准。'),
        ('GLM-5.2 的模型 ID 是什么？上下文多大？',
         '模型 ID 是 <code>glm-5.2</code>。智谱官方公布的上下文窗口为 1M tokens，最大输出 128K tokens，只支持文本输入。'),
        ('GLM-5.2 能关闭思考吗？',
         f'能。智谱官方说明 GLM-5.2 默认开启动态思考，由模型自行判断是否需要思考，也支持关闭思考；这是它和 <a href="/zh/models/glm-5.3">GLM-5.3</a> 的主要区别之一（GLM-5.3 思考始终开启）。在 AnyAIGC 上可以用 <code>reasoning_effort</code> 调整思考深度。'),
        ('GLM-5.2 有什么特点？',
         '官方把 GLM-5.2 定位为面向长任务时代的旗舰模型：提供真正可用的 1M 上下文，能装下项目级工程上下文；长程任务执行更稳定，更可靠地遵循工程规范，可以在单个任务里完成从需求到多端部署的完整开发链路。官方称 IndexShare 设计在 1M 上下文下把每 token 计算量降低 2.9 倍。'),
        ('GLM-5.2 和 GLM-5.3 怎么选？',
         f'两者是同一个基座，在 AnyAIGC 输入、输出单价相同。GLM-5.3 在此基础上扩展了后训练，官方称编程能力提升 50%，缓存命中价也更低（{p("glm-5.3", 2)} 对 {p(s, 2)}），新项目建议直接用 GLM-5.3；需要关闭思考、或已经在生产里调好 GLM-5.2 的业务，可以继续用 GLM-5.2。'),
        faq_cc('GLM-5.2', s),
        ('GLM-5.2 是开源的吗？可以商用吗？',
         '是。智谱以 MIT 许可在 Hugging Face（zai-org/GLM-5.2）和魔搭社区发布了 GLM-5.2 权重。通过 AnyAIGC 调用 API 不需要自己部署，商用授权以智谱官方条款为准。'),
        faq_rpm('GLM-5.2', s),
    ] + faq_common('GLM-5.2', s)
    return dict(
        title='GLM-5.2 API 价格与接入｜1M 上下文 长程任务 约官方 7 折 - AnyAIGC',
        desc=f'glm-5.2 API：智谱面向长程任务的旗舰，1M 上下文，思考可开可关，输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方价 7 折，可接入 Claude Code，并发不限，支持对公转账与专票。',
        og_desc=f'glm-5.2 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约智谱官方价 7 折。面向长程任务的旗舰，真正可用的 1M 上下文，MIT 开源，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC GLM-5.2 API：约官方价 7 折',
        keywords='GLM-5.2 API,glm-5.2,GLM-5.2 API 价格,GLM-5.2 接入,GLM-5.2 API key,GLM-5.2 Claude Code,GLM-5.2 1M 上下文,GLM-5.2 关闭思考,智谱 GLM-5.2,GLM API,GLM-5.2 API 企业,GLM-5.2 API 发票,GLM API 对公转账,AnyAIGC',
        crumb='GLM-5.2 API', product='GLM-5.2 API（AnyAIGC）', sku=s,
        product_desc='通过 AnyAIGC 调用智谱 GLM-5.2（glm-5.2）：OpenAI 兼容 /v1/chat/completions，1M 上下文，按 token 计费，约官方价 7 折，并发不限。',
        offers=offers(s),
        hero=dict(eyebrow='智谱 Z.ai · glm-5.2',
                  h1='GLM-<span class="g-blue">5.2</span><span class="o-sr"> API</span>',
                  lead='智谱面向长程任务的旗舰，真正可用的 1M 上下文，能在单个任务里完成从需求到多端部署的完整开发链路，思考可开可关。在 AnyAIGC 调用约为官方价的 7 折。',
                  ask='把这个小程序迁移到 H5 和 App 三端，并保持接口和样式一致',
                  chips=['长程任务', '1M 上下文', '思考可关'],
                  sub=f'<code>glm-5.2</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='为长程任务设计的 1M 上下文旗舰',
                   paras=['智谱把 GLM-5.2 定位为面向长任务时代的旗舰模型。官方称它提供真正可用的 1M 上下文，能装下项目级的工程上下文，长程任务执行更稳定，也更可靠地遵循工程规范。',
                          '上下文从 GLM-5.1 的 200K 扩展到 1M。架构上沿用 MoE 加 DSA 稀疏注意力，并引入 IndexShare：每 4 个稀疏注意力层共享一个索引器，官方称在 1M 上下文下每 token 计算量降低 2.9 倍。GLM-5.2 默认动态思考，也可以关闭，以 MIT 许可开源。',
                          '在 AnyAIGC 上，<code>glm-5.2</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，也能在 Claude Code 里直接使用，并发不限。新项目可以考虑同价的 <a href="/zh/models/glm-5.3">GLM-5.3</a>，它在同一基座上进一步提升了编程能力。'],
                   spec=[('上下文窗口', '1M', 'tokens，GLM-5.1 为 200K'), ('最大输出', '128K', 'tokens'),
                         ('架构', 'MoE + DSA', 'IndexShare 稀疏注意力'), ('输入模态', '文本', '仅文本输入'),
                         ('思考模式', '可开可关', '默认动态思考'), ('权重', '开放', 'MIT 许可')]),
        features=dict(kicker='能力', h2='GLM-5.2 能做什么',
                      items=[('项目级工程', '1M 上下文装下整个项目，官方公布 SWE-bench Pro 62.1、FrontierSWE 74.4，适合接管和重构现有工程。'),
                             ('终端编程', '官方公布 Terminal Bench 2.1 为 81.0，搭配 Claude Code 时为 82.7。'),
                             ('数学与推理', '官方公布 AIME 2026 为 99.2、HMMT Nov. 2025 为 94.4、GPQA-Diamond 为 91.2。'),
                             ('工具调用', '官方公布 MCP-Atlas（公开集）76.8，支持函数调用、结构化输出和 MCP。'),
                             ('思考可开可关', '默认由模型自行判断是否思考，简单请求也可以关闭思考，响应更快、输出更省。'),
                             ('MIT 开源', '权重以 MIT 许可在 Hugging Face 和魔搭发布，通过 AnyAIGC 调用不需要自己部署。')]),
        pricing=dict(kicker='价格', h2='GLM-5.2 API 价格', lead='按 token 计费，固定单价，没有订阅和月费。输入、输出约为智谱官方美元价的 67.5%（约 7 折）。',
                     billing_label='计费要点',
                     billing=billing('约 7 折'),
                     head=PRICE_HEAD, labels=LABELS, caption='glm-5.2 每百万 tokens 价格（美元），AnyAIGC 与智谱官方对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的智谱官方价。',
                     costs=[cost_card(s, '审查 100 个 PR', '每个 PR 2 万 tokens 输入 + 2,000 输出', 20000, 2000, 0, 100),
                            cost_card(s, '50 万 tokens 长文档分析', '50 万 tokens 输入 + 5,000 输出', 500000, 5000),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='GLM-5.2 的官方基准成绩', lead='智谱在 GLM-5.2 技术博客中公布的成绩，下表列出与上一代 GLM-5.1 的对比。',
                   chart=('GLM-5.2 对比 GLM-5.1 · 官方评测', [('GLM-5.2 · FrontierSWE', 74.4, True), ('GLM-5.1 · FrontierSWE', 30.5, False),
                                                       ('GLM-5.2 · Terminal Bench 2.1', 81, True), ('GLM-5.1 · Terminal Bench 2.1', 63.5, False),
                                                       ('GLM-5.2 · SWE-bench Pro', 62.1, True), ('GLM-5.1 · SWE-bench Pro', 58.4, False)]),
                   head=[('基准', ''), ('GLM-5.2', 'o-num o-hl'), ('GLM-5.1', 'o-num')],
                   rows=[('HLE', '综合推理', '40.5', '31.0'), ('HLE w/ Tools', '综合推理，带工具', '54.7', '52.3'),
                         ('AIME 2026', '数学', '99.2', '95.3'), ('GPQA-Diamond', '科学推理', '91.2', '86.2'),
                         ('SWE-bench Pro', '软件工程', '62.1', '58.4'), ('NL2Repo', '从零生成仓库', '48.9', '42.7'),
                         ('DeepSWE', '软件工程', '46.2', '18.0'), ('ProgramBench', '编程', '63.7', '50.9'),
                         ('Terminal Bench 2.1', '终端编程', '81.0', '63.5'), ('FrontierSWE', '软件工程', '74.4', '30.5'),
                         ('MCP-Atlas', '工具调用，公开集', '76.8', '71.8'), ('Tool-Decathlon', '工具调用', '48.2', '40.7')],
                   caption='GLM-5.2 与 GLM-5.1 的官方基准对比（智谱公布）',
                   note=f'数据来自 <a href="{B52}" target="_blank" rel="noopener">GLM-5.2 技术博客</a>，为智谱公布的成绩。GLM-5.3 博客中对 GLM-5.2 的部分成绩采用了不同版本或统计日期，两者不宜直接混用。'),
        compare=dict(kicker='选型', h2='GLM-5.2 和 GLM-5.3、GLM-5.3-Flash 怎么选', lead='新项目优先用同价的 GLM-5.3；需要关闭思考时用 GLM-5.2；预算敏感用 GLM-5.3-Flash。',
                     head=[('对比项', ''), ('GLM-5.2', 'o-num o-hl'), ('GLM-5.3', 'o-num'), ('GLM-5.3-Flash', 'o-num')],
                     rows=[('定位', '', '长程任务旗舰', '最新旗舰', '原生多模态，低价'), ('上下文', '', '1M', '1M', '1M'),
                           ('输入模态', '', '文本', '文本', '文本、图片'), ('思考模式', '', '可开可关', '始终开启', '始终开启'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p('glm-5.3', 0), p('glm-5.3-flash', 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p('glm-5.3', 1), p('glm-5.3-flash', 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p('glm-5.3', 2), p('glm-5.3-flash', 2))],
                     caption='GLM-5.2、GLM-5.3、GLM-5.3-Flash 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note='参数来自智谱 Z.ai 官方文档，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。详见 <a href="/zh/models/glm-5.3">GLM-5.3 API</a> 和 <a href="/zh/models/glm-5.3-flash">GLM-5.3-Flash API</a>。'),
        uses=dict(kicker='使用场景', h2='GLM-5.2 适合做什么',
                  items=[('01 · 工程接管', '读懂并接手现有项目', '把整个项目放进 1M 上下文，梳理架构、补文档、按工程规范持续迭代。'),
                         ('02 · 多端迁移', '小程序、H5 和 App', '官方推荐场景之一：在单个任务里完成从需求到多端部署的完整开发链路。'),
                         ('03 · 论文复现', '读论文写实验代码', '整篇论文和参考代码放进上下文，复现实验、对齐指标、写报告。'),
                         ('04 · 快速问答', '关闭思考的轻量请求', '客服、分类这类不需要深度推理的请求可以关闭思考，响应更快。')]),
        qs=dict(kicker='快速开始', h2='三步接入 GLM-5.2 API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, '用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, '你是资深后端工程师，回答要给出可运行的代码。', '用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('tools', '工具调用', 'Python · tools', code_tools(s)),
                      ('stream', '流式输出', 'Python · stream=True', code_stream(s, '解释为什么天空是蓝色的。'))],
                callout='<strong>参数提示：</strong>GLM-5.2 默认动态思考，思考过程（如有）在 <code>reasoning_content</code> 字段，可以用 <code>reasoning_effort</code> 调整思考深度。多轮对话和工具调用时，要把 API 返回的完整 assistant 消息（包括 <code>reasoning_content</code> 和 <code>tool_calls</code>）原样放回下一次请求。',
                note=QS_NOTE),
        cc=cc('GLM-5.2', s, '把 Claude Code 的模型换成 GLM-5.2：1M 上下文适合在大仓库里做长周期的编码任务。',
              '<strong>升级提示：</strong>想要更高的编程成功率，把配置里的 <code>glm-5.2</code> 全部换成 <code>glm-5.3</code> 即可，两者单价相同。'),
        family_h2='GLM 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 GLM 模型，按任务难度和预算选择。',
        faq_h2='GLM-5.2 API 常见问题', faqs=faqs,
        final=dict(h2='用约 7 折的价格跑 GLM-5.2', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 glm-5.2。', other='GLM-5.2 API in English'),
        ent_name='GLM-5.2',
    )
