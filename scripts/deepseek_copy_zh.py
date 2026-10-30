# DeepSeek 系列专题页中文文案。被 scripts/deepseek_pages.py 引用。
# 价格来自 deepseek_data.PRICE（模型广场最低价）；官方价、参数、跑分来自 api-docs.deepseek.com、deepseek.com 新闻页、
# Hugging Face deepseek-ai 模型卡（2026-10-30 读取）。未经官方确认的信息（V4.1-Flash-1017 参数量、0813 / 1017 跑分、
# 旧版 V4 Flash 最大输出等）一律不写。
from deepseek_data import (PRICE, OFFICIAL, REG, PRICING, SUPPORT, DOCS_CHAT, DOCS_CC, OFFICIAL_PRICING,
                           OFFICIAL_UPDATES, NEWS_V41, HF_V41, HF_V4F)
from deepseek_layout import cost, money

F41, PRO, F4 = 'deepseek-v4.1-flash', 'deepseek-v4-pro', 'deepseek-v4-flash'
PEAK = '北京时间工作日 9:00–12:00、14:00–18:00'


def p(slug, i):
    return f'${PRICE[slug][i]}'


def o(slug, kind, i):
    return f'${OFFICIAL[slug][kind][i]}'


# ---------------- 共用 FAQ ----------------
def faq_common(name):
    return [
        (f'国内可以直接调用 {name} API 吗？',
         '可以。AnyAIGC 面向国内网络优化，通常无需额外代理即可调用 <code>https://anyaigc.ai</code>，按美元价格计费，支持微信支付、支付宝、USDT 和信用卡，企业可对公转账并开具增值税发票。'),
        (f'如何获取 {name} API Key？',
         f'在 <a href="{REG}">anyaigc.ai</a> 注册并充值，进入控制台创建令牌即可。同一个 Key 可以调用 DeepSeek 全系以及平台上 300+ 其他模型，不需要单独注册 DeepSeek 开放平台。'),
        ('AnyAIGC 能开发票吗？支持增值税专票吗？',
         '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
        ('企业可以对公转账和签合同吗？',
         f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
    ]


def faq_cc(name, model):
    return (f'可以在 Claude Code 里使用 {name} 吗？',
            f'可以。AnyAIGC 上的 DeepSeek 模型同时支持 OpenAI 和 Anthropic 两种接口格式。在 <code>~/.claude/settings.json</code> 的 env 中设置 <code>ANTHROPIC_BASE_URL</code> 为 <code>https://anyaigc.ai</code>、<code>ANTHROPIC_AUTH_TOKEN</code> 为你的 API Key、<code>ANTHROPIC_MODEL</code> 为 <code>{model}</code>，然后运行 <code>claude</code> 即可，按 token 计费。')


def faq_rpm(scope):
    return ('并发和速率有限制吗？',
            f'AnyAIGC 对 {scope} 不设并发限制，所有用户默认享有，适合批量任务、CI 流水线和多 Agent 并行。')


def faq_peak(scope):
    return ('AnyAIGC 也分高峰和闲时价格吗？',
            f'不分。DeepSeek 官方 API 采用峰谷定价，{PEAK}为高峰时段，高峰价是闲时价的 2 倍。AnyAIGC 上 {scope} 全天按模型广场的同一单价计费，约为官方高峰价的 4 折，实时价格以模型广场为准。')


# ---------------- 代码示例（用 @MODEL 占位，避免 f-string 花括号转义） ----------------
CURL = '''curl https://anyaigc.ai/v1/chat/completions \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "@MODEL",
    "messages": [
      {"role": "user", "content": "@PROMPT"}
    ]
  }\''''

PY = '''import os
from openai import OpenAI

client = OpenAI(
    base_url="https://anyaigc.ai/v1",
    api_key=os.environ["ANYAIGC_API_KEY"],
)

resp = client.chat.completions.create(
    model="@MODEL",
    messages=[
        {"role": "system", "content": "@SYSTEM"},
        {"role": "user", "content": "@USER"},
    ],
)
print(resp.choices[0].message.content)
print(resp.usage)  # prompt_tokens_details.cached_tokens 为缓存命中的 tokens'''

STREAM = '''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

stream = client.chat.completions.create(
    model="@MODEL",
    messages=[{"role": "user", "content": "@USER"}],
    stream=True,
    stream_options={"include_usage": True},  # 最后一个分片返回 token 用量
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()'''

THINK = '''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# 思考开关写在 thinking 里：enabled 开启，disabled 关闭；思考强度用 reasoning_effort
resp = client.chat.completions.create(
    model="@MODEL",
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
    messages=[{"role": "user", "content": "@USER"}],
)
print(resp.choices[0].message.content)
print(resp.usage.completion_tokens_details.reasoning_tokens)  # 思考消耗的 tokens'''

TOOLS = '''import json
import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

tools = [{
    "type": "function",
    "function": {
        "name": "run_tests",
        "description": "在仓库里运行指定路径的单元测试，返回失败用例",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "测试文件或目录"}},
            "required": ["path"],
        },
    },
}]
messages = [{"role": "user", "content": "跑一下 tests/test_api.py，告诉我哪些用例失败了。"}]

resp = client.chat.completions.create(model="@MODEL", messages=messages, tools=tools)
msg = resp.choices[0].message
# 把完整的 assistant 消息原样放回 messages，再追加工具结果
messages.append(msg.model_dump(exclude_none=True))
for call in msg.tool_calls or []:
    args = json.loads(call.function.arguments)
    result = {"path": args["path"], "failed": ["test_login_timeout"]}  # 这里换成真实的执行结果
    messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)})

final = client.chat.completions.create(model="@MODEL", messages=messages, tools=tools)
print(final.choices[0].message.content)'''

VISION = '''import base64
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# 本地图片转成 Base64 Data URL；也可以直接填公网图片 URL
b64 = base64.b64encode(Path("chart.png").read_bytes()).decode()

resp = client.chat.completions.create(
    model="@MODEL",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "读出这张图表里每个季度的数值，整理成 Markdown 表格。"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ],
    }],
)
print(resp.choices[0].message.content)'''

CC = '''{
  "env": {
    "ANTHROPIC_BASE_URL": "https://anyaigc.ai",
    "ANTHROPIC_AUTH_TOKEN": "sk-你的 API Key",
    "ANTHROPIC_MODEL": "@MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "@MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "@MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "@HAIKU",
    "API_TIMEOUT_MS": "300000",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}'''


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace('@' + k.upper(), v)
    return tpl


def cc(name, model, lead, callout, haiku=None):
    return dict(
        kicker='Claude Code', h2=f'在 Claude Code 中使用 {name}', lead=lead,
        steps=['<strong>安装 Claude Code</strong>：按官方方式安装，例如 macOS / Linux 运行 <code>curl -fsSL https://claude.ai/install.sh | bash</code>。',
               '<strong>写入配置</strong>：编辑 <code>~/.claude/settings.json</code>，把下面的 env 加进去，<code>ANTHROPIC_AUTH_TOKEN</code> 换成你在 AnyAIGC 创建的 Key。',
               f'<strong>开始使用</strong>：在项目目录运行 <code>claude</code>，输入 <code>/model</code> 可以确认当前模型是 <code>{model}</code>。'],
        code=fill(CC, model=model, haiku=haiku or model), callout=callout,
        note=f'完整步骤和常见报错见 <a href="{DOCS_CC}" target="_blank" rel="noopener">Claude Code 安装与使用教程</a>，教程里的模型名换成 <code>{model}</code> 即可。')


def qs_steps(model):
    return ['<strong>注册并充值</strong>：在 <a href="' + REG + '">anyaigc.ai</a> 注册账号，最低 $1 起充，余额对平台所有模型通用。',
            '<strong>创建 API Key</strong>：在控制台创建令牌，复制以 <code>sk-</code> 开头的 Key，存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'<strong>发起请求</strong>：请求 <code>POST https://anyaigc.ai/v1/chat/completions</code>，<code>model</code> 填 <code>{model}</code>，鉴权用 <code>Authorization: Bearer</code>。OpenAI SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。']


QS_NOTE = f'完整参数见 <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions 接口文档</a>，文档示例里的模型名换成对应的 DeepSeek 模型 ID 即可。'
THINK_CALLOUT = ('<strong>参数提示：</strong>DeepSeek 官方说明 V4 系列默认开启思考。请求体里的 <code>thinking</code> 字段控制开关（<code>{"type": "enabled"}</code> 或 <code>{"type": "disabled"}</code>），'
                 '<code>reasoning_effort</code> 调整思考强度（官方可选 <code>low</code> / <code>high</code> / <code>max</code>）。思考消耗的 tokens 计入输出，可在 <code>usage.completion_tokens_details.reasoning_tokens</code> 查看。'
                 '思考模式下 <code>temperature</code> 等采样参数不生效。')

PRICE_HEAD = [('计费项', ''), ('模型名', ''), ('AnyAIGC', 'o-num o-hl'), ('官方闲时', 'o-num'), ('官方高峰', 'o-num'), ('折扣', 'o-num')]
LABELS = [('输入', '缓存未命中，每 100 万 tokens'), ('输出', '每 100 万 tokens，含思考'), ('缓存命中', '每 100 万 tokens')]


def pricing_note(q):
    return (f'价格单位为美元，按实际消耗的 tokens 计费，输出包含思考 tokens，重复的请求前缀按缓存命中价计费。'
            f'官方价来自 <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">DeepSeek API 价格页</a>（美元价），高峰时段为{PEAK}，其余为闲时。'
            f'表中为模型广场最低价，实时价格以 <a href="{PRICING}?keyword={q}">AnyAIGC 模型广场</a> 为准。')


def cost_card(slug, title, calc, inp=0, out=0, cache=0, n=1):
    a = money(cost(slug, inp, out, cache, n))
    off = money(cost(slug, inp, out, cache, n, official='off'))
    peak = money(cost(slug, inp, out, cache, n, official='peak'))
    return (title, calc, a, f'官方高峰 <s>{peak}</s> · 闲时 <s>{off}</s>')


def offers(slug):
    return [('输入（每 100 万 tokens）', PRICE[slug][0]), ('输出（每 100 万 tokens）', PRICE[slug][1]),
            ('缓存命中（每 100 万 tokens）', PRICE[slug][2])]


BILLING = [('按 token 计费', '输入、输出、缓存命中分别计价'), ('不分时段', '全天同一单价，官方高峰价为闲时 2 倍'),
           ('约官方 4 折', '对比 DeepSeek 官方高峰价'), ('并发不限', '所有用户默认享有')]

FAMILY = [
    ('deepseek', '', ('DeepSeek 全系总览', 'V4.1 Flash、V4 Pro、V4 Flash 价格对比与选型')),
    (F41, '最新', f'原生多模态，1M 上下文 · 输入 {p(F41, 0)} / 1M'),
    (PRO, '', f'1.6T MoE 旗舰，思考强度可调 · 输入 {p(PRO, 0)} / 1M'),
    (F4, '旧版', f'官方已升级到 V4.1 Flash · 输入 {p(F4, 0)} / 1M'),
]

FACT_SRC = f'参数来自 DeepSeek 官方 <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">API 文档</a>和 Hugging Face 模型卡，价格为 AnyAIGC 当前价格，实时价格以模型广场为准。'

# V4 预览版（2026-04）指令模型 Max 推理强度成绩，来自 Hugging Face DeepSeek-V4-Flash 模型卡
V4_ROWS = [('SWE-bench Verified', '软件工程，Resolved', '80.6', '79.0'), ('LiveCodeBench', '编程，Pass@1', '93.5', '91.6'),
           ('GPQA Diamond', '科学推理，Pass@1', '90.1', '88.1'), ("HLE", '综合推理，Pass@1', '37.7', '34.8'),
           ('Terminal Bench 2.0', '终端编程，Acc', '67.9', '56.9'), ('BrowseComp', '网页检索，Pass@1', '83.4', '73.2'),
           ('Codeforces', '竞赛编程，Rating', '3206', '3052')]


def build(slug):
    return {'deepseek': hub, F41: v41, PRO: pro, F4: v4f}[slug]()


# ======================================================================
# 总览页
# ======================================================================
def hub():
    faqs = [
        ('DeepSeek API 多少钱？',
         f'AnyAIGC 上 DeepSeek 按 token 计费，每百万 tokens：<code>{F41}</code> 输入 {p(F41, 0)}、输出 {p(F41, 1)}、缓存命中 {p(F41, 2)}；'
         f'<code>{PRO}</code> 输入 {p(PRO, 0)}、输出 {p(PRO, 1)}、缓存命中 {p(PRO, 2)}；<code>{F4}</code> 与 V4.1 Flash 同价。实时价格以模型广场为准。'),
        faq_peak('DeepSeek 各型号'),
        ('AnyAIGC 上有哪些 DeepSeek 模型？模型 ID 是什么？',
         f'本页介绍三款：<code>{F41}</code>（DeepSeek 最新的 Flash 模型，原生多模态）、<code>{PRO}</code>（1.6T 参数的 V4 旗舰）、<code>{F4}</code>（V4 预览版的 Flash 模型，官方已升级到 V4.1 Flash）。'
         '调用时把模型 ID 写在请求体的 <code>model</code> 字段里，切换模型只需要改这一个字段。'),
        ('V4.1 Flash 和 V4 Pro 怎么选？',
         f'大多数任务优先用 <a href="/zh/models/{F41}">V4.1 Flash</a>：DeepSeek 官方称它在性能、费用、速度和总用时上已全面超越 V4 Pro，输入单价约为 V4 Pro 的四分之一，还能看图。'
         f'已经在生产里调好 V4 Pro 的业务可以继续用 <a href="/zh/models/{PRO}">V4 Pro</a>，官方已宣布在 2026 年 9 月 14 日之后继续提供 V4 Pro API 服务。'),
        ('上下文窗口有多大？支持图片输入吗？',
         'DeepSeek 官方公布 V4.1 Flash 和 V4 Pro 都支持 1M tokens 上下文，最大输出 384K tokens。图片输入只有 V4.1 Flash 支持，V4 Pro 和 V4 Flash 只支持文本。'),
        ('DeepSeek API 兼容 OpenAI 吗？',
         '兼容。三款模型都走 <code>POST https://anyaigc.ai/v1/chat/completions</code>，请求和返回格式与 OpenAI Chat Completions 一致，OpenAI 官方 SDK 把 <code>base_url</code> 改成 <code>https://anyaigc.ai/v1</code> 即可。也支持 Anthropic 接口格式，可以接入 Claude Code。'),
        faq_cc('DeepSeek', F41),
        faq_rpm('DeepSeek 系列'),
    ] + faq_common('DeepSeek')
    return dict(
        title='DeepSeek API 价格与接入｜V4.1 Flash、V4 Pro 国内直连 - AnyAIGC',
        desc=f'AnyAIGC 提供 DeepSeek API：V4.1 Flash、V4 Pro 一个 Key 接入，输入低至 {p(F41, 0)}/百万 tokens，不分高峰闲时，1M 上下文，兼容 OpenAI 接口，并发不限，支持对公转账和增值税专票。',
        og_desc=f'DeepSeek V4.1 Flash、V4 Pro、V4 Flash 一个 Key 调用，输入 {p(F41, 0)}/1M 起，约官方高峰价 4 折，不分高峰闲时，OpenAI 兼容，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC DeepSeek API：V4.1 Flash、V4 Pro、V4 Flash',
        keywords='DeepSeek API,DeepSeek API 价格,DeepSeek API key,DeepSeek V4 API,DeepSeek V4.1 Flash API,DeepSeek V4 Pro API,DeepSeek API 国内,DeepSeek Claude Code,DeepSeek API 企业,DeepSeek API 发票,DeepSeek API 对公转账,AnyAIGC',
        crumb='DeepSeek API', product='DeepSeek API（AnyAIGC）', sku='deepseek',
        product_desc=f'通过 AnyAIGC 调用 DeepSeek 系列模型（{F41}、{PRO}、{F4}）：OpenAI 兼容 /v1/chat/completions，按 token 计费，不分高峰闲时，并发不限。',
        offers=[(f'{n} 输入（每 100 万 tokens）', PRICE[s][0]) for s, n in ((F41, 'V4.1 Flash'), (PRO, 'V4 Pro'), (F4, 'V4 Flash'))]
        + [(f'{n} 输出（每 100 万 tokens）', PRICE[s][1]) for s, n in ((F41, 'V4.1 Flash'), (PRO, 'V4 Pro'), (F4, 'V4 Flash'))],
        hero=dict(announce=f'DeepSeek V4.1 Flash 已可在 AnyAIGC 调用，输入 {p(F41, 0)} / 百万 tokens，全天同价',
                  eyebrow='深度求索 · DeepSeek',
                  h1='DeepSeek <span class="d-blue">API</span>',
                  lead='DeepSeek V4.1 Flash、V4 Pro、V4 Flash，一个 API Key 全部调用。按 token 计费，不分高峰闲时，约为 DeepSeek 官方高峰价的 4 折。',
                  ask='读完这个仓库，修好失败的测试并补上缺失的类型定义',
                  think='已读完仓库，定位到 3 个失败的测试和 2 处缺失的类型定义',
                  out=['定位到 3 个失败用例：<code>test_parse_date</code>、<code>test_retry</code>、<code>test_config_merge</code>。', '原因：<code>utils/date.py</code> 没处理时区；<code>retry()</code> 的退避上限写反；<code>merge()</code> 浅拷贝改到了默认配置。', '已修改 3 个文件，并给 <code>Config</code>、<code>RetryPolicy</code> 补上类型定义。', '重新运行：<code>42 passed, 0 failed</code>。'],
                  chips=['深度思考', '1M 上下文', '看图'],
                  qs_btn='三步接入',
                  sub=f'OpenAI 兼容的 <code>/v1/chat/completions</code>，也能直接接入 Claude Code。<code>{F41}</code> 输入 {p(F41, 0)} / 百万 tokens 起，并发不限。',
                  facts=[('型号', 'V4.1 Flash · V4 Pro · V4 Flash'), ('上下文', '1M'), ('输入', f'{p(F41, 0)} / 1M 起'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        models=dict(kicker='型号', h2='DeepSeek 系列三款模型', lead='同一个 Key、同一个接口，按任务换模型 ID 即可。',
                    unit_in='1M 输入', unit_out='1M 输出', go='查看专题', legacy_tag='旧版',
                    items=[(F41, '最新', 'DeepSeek 全新模型结构系列中尺寸最小的模型，原生多模态。官方称它已全面超越 V4 Pro。', ['1M 上下文，最大输出 384K', '支持图片输入和工具调用', '输入单价约为 V4 Pro 的 1/4']),
                           (PRO, '', 'DeepSeek V4 旗舰，1.6T 总参数、49B 激活。8 月发布正式版，新增 low / high / max 三档思考强度。', ['1M 上下文，最大输出 384K', '思考强度可调', 'MIT 开源许可']),
                           (F4, '旧版', 'V4 预览版的 Flash 模型，284B 总参数、13B 激活。官方已下线，旧模型名路由到 V4.1 Flash。', ['1M 上下文', '与 V4.1 Flash 同价', '新项目建议换 V4.1 Flash'])]),
        pricing=dict(kicker='价格', h2='DeepSeek API 价格', lead='按 token 计费，全天同一单价，没有订阅和月费。下表对比 DeepSeek 官方的闲时与高峰美元价。',
                     billing_label='计费要点', billing=BILLING,
                     head=[('计费项', ''), ('AnyAIGC', 'o-num o-hl'), ('官方闲时', 'o-num'), ('官方高峰', 'o-num'), ('折扣', 'o-num')],
                     labels=LABELS, caption='DeepSeek 系列每百万 tokens 价格（美元），AnyAIGC 与 DeepSeek 官方闲时、高峰价对比',
                     note=pricing_note('deepseek') + ' 官方已下线 V4 Flash，<code>deepseek-v4-flash</code> 的官方价按 V4.1 Flash 计。',
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 DeepSeek 官方高峰价和闲时价。',
                     costs=[cost_card(F41, 'V4.1 Flash · Agent 编程 50 轮', '每轮 6 万 tokens 缓存命中 + 4,000 输入 + 2,000 输出', 4000, 2000, 60000, 50),
                            cost_card(F41, 'V4.1 Flash · 1 万条工单分类', '每条 2,000 tokens 输入 + 300 输出', 2000, 300, 0, 10000),
                            cost_card(PRO, 'V4 Pro · 50 万 tokens 代码库分析', '50 万 tokens 输入 + 5,000 输出', 500000, 5000)]),
        compare=dict(kicker='选型', h2='V4.1 Flash、V4 Pro、V4 Flash 怎么选', lead='新项目优先用 V4.1 Flash；已在生产里调好 V4 Pro 的可以继续用；V4 Flash 建议迁移。',
                     head=[('对比项', ''), ('V4.1 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num'), ('V4 Flash', 'o-num')],
                     rows=[('状态', '', '最新', '在售', '官方已下线'),
                           ('参数规模', '', '552B MoE', '1.6T / 49B 激活', '284B / 13B 激活'),
                           ('上下文 / 最大输出', '', '1M / 384K', '1M / 384K', '1M / –'),
                           ('输入模态', '', '文本、图片', '文本', '文本'),
                           ('AnyAIGC 输入', '每百万 tokens', p(F41, 0), p(PRO, 0), p(F4, 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(F41, 1), p(PRO, 1), p(F4, 1)),
                           ('缓存命中', '每百万 tokens', p(F41, 2), p(PRO, 2), p(F4, 2))],
                     caption='DeepSeek V4.1 Flash、V4 Pro、V4 Flash 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note=FACT_SRC + ' “–”表示官方未公布。'),
        uses=dict(kicker='使用场景', h2='用 DeepSeek API 做什么',
                  items=[('01 · Coding Agent', 'Claude Code、CI 和自动修复', '把 DeepSeek 接进 Claude Code 或自己的 Agent 框架，读代码、跑测试、修报错。AnyAIGC 不限并发，多个 Agent 可以同时跑。'),
                         ('02 · 长上下文', '大仓库和长文档', '1M tokens 上下文能放下整个代码库或几百页文档。重复的前缀按缓存命中价计费，V4.1 Flash 缓存命中只要 ' + p(F41, 2) + ' / 百万 tokens。'),
                         ('03 · 看图', '图表、截图和扫描件', 'V4.1 Flash 原生支持图片输入，可以读图表、看页面截图、从扫描件里抽取字段。'),
                         ('04 · 批量处理', '分类、抽取和摘要', 'V4.1 Flash 输入 ' + p(F41, 0) + ' / 百万 tokens，全天同价，适合工单分类、字段抽取、评论打标这类大批量任务。')]),
        qs=dict(kicker='快速开始', h2='三步接入 DeepSeek API', steps=qs_steps(F41),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=F41, prompt='用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', fill(PY, model=F41, system='你是资深后端工程师，回答要给出可运行的代码。', user='用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('think', '思考模式', 'Python · thinking', fill(THINK, model=PRO, user='证明根号 2 是无理数，并指出证明里最关键的一步。')),
                      ('stream', '流式输出', 'Python · stream=True', fill(STREAM, model=F41, user='给一个 SaaS 产品写 5 条更新日志。'))],
                callout=THINK_CALLOUT, note=QS_NOTE),
        cc=cc('DeepSeek', F41, '把 Claude Code 的模型换成 DeepSeek：改一个配置文件，终端里的编程 Agent 就由 DeepSeek V4.1 Flash 驱动，按 token 计费。',
              f'<strong>换模型：</strong>想用 V4 Pro，把配置里的 <code>{F41}</code> 换成 <code>{PRO}</code> 即可；也可以只把 <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> 留给 V4.1 Flash 处理轻量子任务。'),
        family_h2='DeepSeek 系列全部型号', family_lead='同一个 API Key 可以调用下面所有 DeepSeek 模型，按任务和预算选择。',
        faq_h2='DeepSeek API 常见问题', faqs=faqs,
        final=dict(h2='用一个 Key 跑 DeepSeek 全系', p='注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 DeepSeek V4.1 Flash 和 V4 Pro。',
                   other='DeepSeek API in English'),
        ent_name='DeepSeek',
    )


# ======================================================================
# DeepSeek V4.1 Flash
# ======================================================================
def v41():
    s = F41
    faqs = [
        ('DeepSeek V4.1 Flash API 多少钱？',
         f'AnyAIGC 上 <code>{s}</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'DeepSeek 官方美元价闲时为输入 {o(s, "off", 0)}、输出 {o(s, "off", 1)}、缓存命中 {o(s, "off", 2)}，高峰时段翻倍。输出包含思考 tokens，实时价格以模型广场为准。'),
        faq_peak(f'<code>{s}</code>'),
        ('DeepSeek V4.1 Flash 有什么新变化？',
         'DeepSeek 官方介绍，V4.1 Flash 是全新模型结构系列中尺寸最小的模型：552B 参数的 MoE，采用 Causal-Encoder-Decoder 非对称结构，输入激活 8B、输出激活 16B，具备原生多模态视觉理解能力。'
         '官方称它的 KV Cache 对 HBM 的需求减少到上一代的 1/4、对 SSD 的需求减少到 1/8，Agent 场景的缓存成本明显降低。'),
        ('V4.1 Flash 比 V4 Pro 强吗？',
         f'DeepSeek 官方称，经多方测试，V4.1 Flash 在性能、费用、速度、总用时等指标上已全面超越 <a href="/zh/models/{PRO}">V4 Pro</a>。官方模型卡公布的对比：DeepSWE v1.1 74.2 对 62.7，Terminal-Bench 2.1 90.6 对 87.9。'
         f'在 AnyAIGC 上，V4.1 Flash 的输入单价 {p(s, 0)}，约为 V4 Pro（{p(PRO, 0)}）的四分之一。'),
        ('DeepSeek V4.1 Flash 支持图片输入吗？怎么传？',
         '支持。在 <code>messages[].content</code> 数组里放 <code>{"type": "image_url", "image_url": {"url": ...}}</code> 内容块，<code>url</code> 可以是公网图片地址，也可以是 Base64 Data URL。'),
        ('上下文多长？支持思考模式吗？',
         'DeepSeek 官方公布 V4.1 Flash 上下文 1M tokens，最大输出 384K tokens，支持思考和非思考两种模式，默认开启思考，同时支持工具调用和 JSON 输出。'),
        faq_cc('DeepSeek V4.1 Flash', s),
        faq_rpm(f'<code>{s}</code>'),
    ] + faq_common('DeepSeek V4.1 Flash')
    return dict(
        title='DeepSeek V4.1 Flash API 价格与接入｜1M 上下文多模态 - AnyAIGC',
        desc=f'DeepSeek V4.1 Flash API 输入 {p(s, 0)} / 输出 {p(s, 1)} 每百万 tokens，不分高峰闲时，原生多模态、1M 上下文，适合编程 Agent 和批量任务，并发不限，支持对公转账和专票。',
        og_desc=f'deepseek-v4.1-flash 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方高峰价 4 折。原生多模态，1M 上下文，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC DeepSeek V4.1 Flash API：1M 上下文，原生多模态',
        keywords='DeepSeek V4.1 Flash API,deepseek-v4.1-flash,DeepSeek V4.1 Flash 价格,DeepSeek Flash API,DeepSeek V4.1 API key,DeepSeek V4.1 Flash 多模态,DeepSeek V4.1 Flash Claude Code,DeepSeek V4.1 Flash API 企业,DeepSeek API 发票,DeepSeek API 对公转账,AnyAIGC',
        crumb='DeepSeek V4.1 Flash API', product='DeepSeek V4.1 Flash API（AnyAIGC）', sku=s,
        product_desc=f'通过 AnyAIGC 调用 DeepSeek V4.1 Flash（{s}）：OpenAI 兼容 /v1/chat/completions，原生多模态，1M 上下文，按 token 计费，不分高峰闲时，并发不限。',
        offers=offers(s),
        hero=dict(announce='DeepSeek 官方称 V4.1 Flash 在性能、费用、速度上已全面超越 V4 Pro',
                  eyebrow=f'DeepSeek · {s}',
                  h1='DeepSeek V4.1 <span class="d-blue">Flash</span><span class="o-sr"> API</span>',
                  lead='DeepSeek 全新模型结构系列中尺寸最小的模型，原生多模态视觉理解。官方的说法是：更强、更快、更普惠。',
                  ask='看这张报表截图，找出环比下降最多的三项并分析原因',
                  think='已识别截图中的表格，共 12 个指标，逐项计算环比',
                  out=['环比下降最多的三项：', '1. 新客转化率 −18.4%：投放渠道从信息流切到搜索，新流量意图更弱。', '2. 客单价 −11.2%：满减活动拉低单笔金额，但订单量同期上涨。', '3. 复购率 −7.9%：会员积分规则调整后，老客触达减少。', '建议先排查第 1 项，它对总营收影响最大。'],
                  chips=['看图', '深度思考', '1M 上下文'],
                  qs_btn='三步接入',
                  sub=f'<code>{s}</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，全天同价，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='非对称结构，小成本大智能',
                   paras=['DeepSeek 在 2026 年 9 月发布 V4.1 Flash，官方称它是全新模型结构系列中尺寸最小的模型，具备原生多模态视觉理解能力。新结构的设计目标是能力上限更高、推理更快、吞吐更大，并且可以扩展到更大参数的模型。',
                          '架构上是 552B 参数的 MoE，采用 Causal-Encoder-Decoder 结构，输入和输出不对称：输入激活 8B，输出激活 16B。官方称新一代模型的 KV Cache 对 HBM 的需求减少到上一代的 1/4、对 SSD 的需求减少到 1/8，Agent 场景里占比较高的缓存费用因此明显下降。10 月官方又把它更新到 V4.1-Flash-1017 版本，称项目开发能力提升显著。',
                          f'在 AnyAIGC 上，<code>{s}</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，支持文本和图片输入，也能在 Claude Code 里直接使用，全天同价，并发不限。'],
                   spec=[('上下文窗口', '1M', 'tokens'), ('最大输出', '384K', 'tokens'),
                         ('参数规模', '552B', 'MoE，输入激活 8B / 输出激活 16B'), ('输入模态', '文本、图片', '原生多模态'),
                         ('思考模式', '可开可关', '默认开启'), ('权重', '开放', 'MIT 许可')]),
        features=dict(kicker='能力', h2='DeepSeek V4.1 Flash 能做什么',
                      items=[('Agent 编程', '官方模型卡公布 DeepSWE v1.1 为 74.2、Terminal-Bench 2.1 为 90.6，均高于 V4 Pro。'),
                             ('看图理解', '原生多模态，图表、页面截图、扫描件都可以直接作为输入。'),
                             ('思考可开可关', '默认开启思考，简单请求可以关闭，响应更快、输出更省。'),
                             ('工具调用与 JSON', '官方文档列出工具调用和 JSON 输出，适合接入 Agent 框架和自动化流程。'),
                             ('更省的缓存', f'官方称 KV Cache 显著缩小。AnyAIGC 缓存命中 {p(s, 2)} / 百万 tokens，多轮 Agent 的重复上下文成本很低。'),
                             ('1M 上下文', '最大输出 384K tokens，大仓库、长文档可以一次放进上下文。')]),
        pricing=dict(kicker='价格', h2='DeepSeek V4.1 Flash API 价格', lead='按 token 计费，全天同一单价，没有订阅和月费。约为 DeepSeek 官方高峰价的 4 折。',
                     billing_label='计费要点', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption=f'{s} 每百万 tokens 价格（美元），AnyAIGC 与 DeepSeek 官方闲时、高峰价对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 DeepSeek 官方高峰价和闲时价。',
                     costs=[cost_card(s, 'Agent 编程 50 轮', '每轮 6 万 tokens 缓存命中 + 4,000 输入 + 2,000 输出', 4000, 2000, 60000, 50),
                            cost_card(s, '1 万条工单分类', '每条 2,000 tokens 输入 + 300 输出', 2000, 300, 0, 10000),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='V4.1 Flash 对比 V4 Pro', lead='DeepSeek 在 V4.1 Flash 模型卡中公布的成绩，与 V4 Pro 对比。',
                   chart=('V4.1 Flash 对比 V4 Pro · 官方评测', [('V4.1 Flash · DeepSWE', 74.2, True), ('V4 Pro · DeepSWE', 62.7, False),
                                                           ('V4.1 Flash · Terminal-Bench', 90.6, True), ('V4 Pro · Terminal-Bench', 87.9, False),
                                                           ('V4.1 Flash · HumanEval', 79.4, True), ('V4 Pro · HumanEval', 76.8, False)]),
                   head=[('基准', ''), ('V4.1 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num')],
                   rows=[('DeepSWE v1.1', '软件工程，Resolved', '74.2', '62.7'), ('Terminal-Bench 2.1', '终端编程', '90.6', '87.9'),
                         ('HumanEval', '编程，Pass@1', '79.4', '76.8'), ('GSM8K', '数学，EM', '93.0', '92.6'),
                         ('MMLU-Pro', '综合知识，EM', '74.1', '73.5')],
                   caption='DeepSeek V4.1 Flash 与 V4 Pro 的官方基准对比',
                   note=f'数据来自 <a href="{HF_V41}" target="_blank" rel="noopener">DeepSeek-V4.1-Flash 模型卡</a>，为 DeepSeek 公布的成绩。10 月的 V4.1-Flash-1017 版本官方未单独公布文字版成绩，本页未收录。'),
        compare=dict(kicker='选型', h2='V4.1 Flash、V4 Pro、V4 Flash 怎么选', lead='新项目优先用 V4.1 Flash，需要看图时只能选它。',
                     head=[('对比项', ''), ('V4.1 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num'), ('V4 Flash', 'o-num')],
                     rows=[('状态', '', '最新', '在售', '官方已下线'), ('上下文', '', '1M', '1M', '1M'),
                           ('输入模态', '', '文本、图片', '文本', '文本'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p(PRO, 0), p(F4, 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p(PRO, 1), p(F4, 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p(PRO, 2), p(F4, 2))],
                     caption='DeepSeek V4.1 Flash、V4 Pro、V4 Flash 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note=FACT_SRC + f' 详见 <a href="/zh/models/{PRO}">DeepSeek V4 Pro API</a>。'),
        uses=dict(kicker='使用场景', h2='DeepSeek V4.1 Flash 适合做什么',
                  items=[('01 · Coding Agent', 'Claude Code 和自研 Agent', '在 Claude Code 或自己的 Agent 框架里跑几十上百步的任务。缓存命中价很低，长对话的重复上下文成本很低。'),
                         ('02 · 看图', '报表、截图和扫描件', '把报表截图、页面截图或扫描件交给模型，抽取数据、核对数字、写分析结论。'),
                         ('03 · 批量处理', '分类、抽取和摘要', '工单分类、字段抽取、评论打标、长文档摘要。单价低、全天同价、不限并发。'),
                         ('04 · 长上下文', '大仓库与长文档', '1M tokens 上下文放下整个代码库或合同全集，再让模型梳理结构、回答问题。')]),
        qs=dict(kicker='快速开始', h2='三步接入 DeepSeek V4.1 Flash API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=s, prompt='用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', fill(PY, model=s, system='你是资深后端工程师，回答要给出可运行的代码。', user='用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('vision', '图片输入', 'Python · image_url', fill(VISION, model=s)),
                      ('think', '思考模式', 'Python · thinking', fill(THINK, model=s, user='把这段 SQL 改写成使用窗口函数的版本：SELECT ...')),
                      ('tools', '工具调用', 'Python · tools', fill(TOOLS, model=s))],
                callout=THINK_CALLOUT, note=QS_NOTE),
        cc=cc('DeepSeek V4.1 Flash', s, '把 Claude Code 的模型换成 DeepSeek V4.1 Flash：改一个配置文件，在终端里用 DeepSeek 写代码，按 token 计费。',
              f'<strong>换模型：</strong>想对比 V4 Pro 的效果，把配置里的 <code>{s}</code> 换成 <code>{PRO}</code> 即可，其余配置不用改。'),
        family_h2='DeepSeek 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 DeepSeek 模型，按任务和预算选择。',
        faq_h2='DeepSeek V4.1 Flash API 常见问题', faqs=faqs,
        final=dict(h2='用全天同价跑 DeepSeek V4.1 Flash', p=f'注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 {s}。', other='DeepSeek V4.1 Flash API in English'),
        ent_name='DeepSeek V4.1 Flash',
    )


# ======================================================================
# DeepSeek V4 Pro
# ======================================================================
def pro():
    s = PRO
    faqs = [
        ('DeepSeek V4 Pro API 多少钱？',
         f'AnyAIGC 上 <code>{s}</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens。'
         f'DeepSeek 官方美元价闲时为输入 {o(s, "off", 0)}、输出 {o(s, "off", 1)}、缓存命中 {o(s, "off", 2)}，高峰时段翻倍。输出包含思考 tokens，实时价格以模型广场为准。'),
        faq_peak(f'<code>{s}</code>'),
        ('DeepSeek V4 Pro 会下线吗？',
         f'目前不会。DeepSeek 在 2026 年 9 月 10 日曾计划下线 V4 Pro，之后在官方<a href="{OFFICIAL_UPDATES}" target="_blank" rel="noopener">更新日志</a>中宣布，应用户需求，9 月 14 日之后继续提供 V4 Pro 的 API 服务，计费方式不变。'),
        ('V4 Pro 和 V4.1 Flash 怎么选？',
         f'DeepSeek 官方称 <a href="/zh/models/{F41}">V4.1 Flash</a> 在性能、费用、速度、总用时上已全面超越 V4 Pro，输入单价约为 V4 Pro 的四分之一，还支持图片输入，新项目建议优先试 V4.1 Flash。'
         '已经在生产里针对 V4 Pro 调好提示词和流程的业务，可以继续用 V4 Pro。'),
        ('怎么调整 V4 Pro 的思考强度？',
         'DeepSeek 官方在 8 月的 V4 Pro 正式版中新增了 <code>low</code>、<code>high</code>、<code>max</code> 三档思考强度，默认开启思考、强度 <code>high</code>。'
         '请求时用 <code>reasoning_effort</code> 设置强度，用 <code>thinking</code> 字段的 <code>{"type": "disabled"}</code> 关闭思考，示例见本页快速开始。'),
        ('V4 Pro 的参数和上下文是多少？',
         'DeepSeek 官方公布 V4 Pro 为 1.6T 总参数、49B 激活的 MoE，采用混合注意力结构，预训练 32T tokens；上下文 1M tokens，最大输出 384K tokens，只支持文本输入，以 MIT 许可开放权重。'),
        faq_cc('DeepSeek V4 Pro', s),
        faq_rpm(f'<code>{s}</code>'),
    ] + faq_common('DeepSeek V4 Pro')
    return dict(
        title='DeepSeek V4 Pro API 价格与接入｜1M 上下文 Agent 编程 - AnyAIGC',
        desc=f'DeepSeek V4 Pro API（1.6T MoE）输入 {p(s, 0)} / 输出 {p(s, 1)} 每百万 tokens，不分高峰闲时，1M 上下文，思考强度可调，可接入 Claude Code，并发不限，支持对公转账和增值税专票。',
        og_desc=f'deepseek-v4-pro 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，约官方高峰价 4 折。1.6T MoE 旗舰，1M 上下文，low / high / max 思考强度，可接入 Claude Code，支持对公转账与增值税专票。',
        og_alt='AnyAIGC DeepSeek V4 Pro API：1.6T MoE，1M 上下文',
        keywords='DeepSeek V4 Pro API,deepseek-v4-pro,DeepSeek V4 Pro 价格,DeepSeek V4 Pro API key,DeepSeek V4 Pro Claude Code,DeepSeek V4 Pro 思考强度,DeepSeek V4 Pro 下线,DeepSeek V4 Pro API 企业,DeepSeek API 发票,DeepSeek API 对公转账,AnyAIGC',
        crumb='DeepSeek V4 Pro API', product='DeepSeek V4 Pro API（AnyAIGC）', sku=s,
        product_desc=f'通过 AnyAIGC 调用 DeepSeek V4 Pro（{s}）：OpenAI 兼容 /v1/chat/completions，1M 上下文，按 token 计费，不分高峰闲时，并发不限。',
        offers=offers(s),
        hero=dict(announce='DeepSeek 已宣布 9 月 14 日后继续提供 V4 Pro API，计费方式不变',
                  eyebrow=f'DeepSeek · {s}',
                  h1='DeepSeek V4 <span class="d-blue">Pro</span><span class="o-sr"> API</span>',
                  lead='DeepSeek V4 旗舰，1.6T 总参数、49B 激活的 MoE。8 月正式版新增 low、high、max 三档思考强度，适合复杂编程和 Agent 任务。',
                  ask='在终端里排查这个服务的内存泄漏，给出修复补丁和回归测试',
                  think='运行了 6 条命令，对比两次堆快照，锁定泄漏位置',
                  out=['<code>ps</code> / <code>tracemalloc</code> 显示 <code>RequestCache</code> 每分钟增长约 40 MB。', '原因：缓存以请求对象为键，请求结束后没有淘汰，对象一直被引用。', '补丁：改为按 URL 做键，加 LRU 上限 2048 条并设置 TTL。', '回归测试 <code>test_cache_bounded</code>：压测 10 万次请求，内存稳定在 120 MB 以内，通过。'],
                  chips=['深度思考', '1M 上下文', 'Agent'],
                  qs_btn='三步接入',
                  sub=f'<code>{s}</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，全天同价，OpenAI 兼容接口和 Claude Code 都能直接用。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='1.6T 参数的 V4 旗舰',
                   paras=['DeepSeek 在 2026 年 4 月发布 V4 预览版，同时推出 V4 Pro 和 V4 Flash，百万 tokens 上下文成为默认配置。8 月 13 日 V4 Pro 正式版上线，新增 low、high、max 三档思考强度。',
                          'V4 Pro 是 1.6T 总参数、49B 激活的 MoE，采用 Compressed Sparse Attention 与 Heavily Compressed Attention 的混合注意力结构，预训练语料 32T tokens，以 MIT 许可开放权重。上下文 1M tokens，最大输出 384K tokens，支持思考和非思考模式，默认开启思考。',
                          f'9 月 V4.1 Flash 发布后，官方曾计划下线 V4 Pro，随后宣布继续提供服务、计费不变。在 AnyAIGC 上，<code>{s}</code> 走 OpenAI 兼容的 <code>/v1/chat/completions</code>，也能在 Claude Code 里直接使用，全天同价，并发不限。'],
                   spec=[('上下文窗口', '1M', 'tokens'), ('最大输出', '384K', 'tokens'),
                         ('参数规模', '1.6T', '49B 激活，MoE'), ('输入模态', '文本', '仅文本输入'),
                         ('思考模式', '可开可关', 'reasoning_effort：low / high / max'), ('权重', '开放', 'MIT 许可')]),
        features=dict(kicker='能力', h2='DeepSeek V4 Pro 能做什么',
                      items=[('软件工程', 'V4 预览版 Max 强度下，官方公布 SWE-bench Verified 80.6、LiveCodeBench 93.5。'),
                             ('终端与 Agent', '官方公布 Terminal Bench 2.0 为 67.9、BrowseComp 为 83.4（V4 预览版，Max 强度）。'),
                             ('科学推理', '官方公布 GPQA Diamond 90.1、HLE 37.7（V4 预览版，Max 强度）。'),
                             ('思考强度可调', '正式版支持 low、high、max 三档，简单任务用 low 省 tokens，难题用 max。'),
                             ('工具调用与 JSON', '官方文档列出工具调用和 JSON 输出，适合接入 Agent 框架和自动化流程。'),
                             ('1M 上下文', '最大输出 384K tokens，整仓代码、长文档可以一次放进上下文。')]),
        pricing=dict(kicker='价格', h2='DeepSeek V4 Pro API 价格', lead='按 token 计费，全天同一单价，没有订阅和月费。约为 DeepSeek 官方高峰价的 4 折。',
                     billing_label='计费要点', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption=f'{s} 每百万 tokens 价格（美元），AnyAIGC 与 DeepSeek 官方闲时、高峰价对比',
                     note=pricing_note(s),
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 DeepSeek 官方高峰价和闲时价。',
                     costs=[cost_card(s, 'Agent 编程 20 轮', '每轮 5 万 tokens 缓存命中 + 5,000 输入 + 3,000 输出', 5000, 3000, 50000, 20),
                            cost_card(s, '50 万 tokens 代码库分析', '50 万 tokens 输入 + 5,000 输出', 500000, 5000),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='DeepSeek V4 Pro 的官方基准成绩', lead='DeepSeek 在 V4 预览版发布时公布的指令模型成绩（Max 推理强度），与同期的 V4 Flash 对比。',
                   chart=('V4 Pro 对比 V4 Flash · 官方评测', [('V4 Pro · SWE-bench Verified', 80.6, True), ('V4 Flash · SWE-bench Verified', 79.0, False),
                                                         ('V4 Pro · Terminal Bench 2.0', 67.9, True), ('V4 Flash · Terminal Bench 2.0', 56.9, False),
                                                         ('V4 Pro · BrowseComp', 83.4, True), ('V4 Flash · BrowseComp', 73.2, False)]),
                   head=[('基准', ''), ('V4 Pro', 'o-num o-hl'), ('V4 Flash', 'o-num')],
                   rows=V4_ROWS,
                   caption='DeepSeek V4 Pro 与 V4 Flash 的官方基准对比（V4 预览版，Max 推理强度）',
                   note=f'数据来自 <a href="{HF_V4F}" target="_blank" rel="noopener">DeepSeek V4 模型卡</a>，为 2026 年 4 月 V4 预览版的成绩。8 月 V4 Pro 正式版的成绩官方以图片发布，本页未收录。'),
        compare=dict(kicker='选型', h2='V4 Pro、V4.1 Flash、V4 Flash 怎么选', lead='官方称 V4.1 Flash 已全面超越 V4 Pro，新项目可以先试 V4.1 Flash；已调好 V4 Pro 的业务可以继续用。',
                     head=[('对比项', ''), ('V4 Pro', 'o-num o-hl'), ('V4.1 Flash', 'o-num'), ('V4 Flash', 'o-num')],
                     rows=[('状态', '', '在售', '最新', '官方已下线'), ('上下文', '', '1M', '1M', '1M'),
                           ('输入模态', '', '文本', '文本、图片', '文本'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p(F41, 0), p(F4, 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p(F41, 1), p(F4, 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p(F41, 2), p(F4, 2))],
                     caption='DeepSeek V4 Pro、V4.1 Flash、V4 Flash 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note=FACT_SRC + f' 详见 <a href="/zh/models/{F41}">DeepSeek V4.1 Flash API</a>。'),
        uses=dict(kicker='使用场景', h2='DeepSeek V4 Pro 适合做什么',
                  items=[('01 · 大仓库', '跨模块重构与迁移', '把整个代码库放进 1M 上下文，让 V4 Pro 理清依赖后给出改动方案，再配合终端工具逐步执行和验证。'),
                         ('02 · Coding Agent', 'Claude Code 和自研 Agent', '在 Claude Code 或自己的 Agent 框架里跑长周期任务：读代码、跑测试、修报错。AnyAIGC 不限并发。'),
                         ('03 · 深度推理', '数学、科研和分析', '难题用 max 思考强度，让模型给出完整推导；日常问答用 low，节省输出 tokens。'),
                         ('04 · 稳定生产', '已调好的线上流程', '已经针对 V4 Pro 调好提示词和评测集的业务，可以继续沿用，官方已确认继续提供服务。')]),
        qs=dict(kicker='快速开始', h2='三步接入 DeepSeek V4 Pro API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=s, prompt='用三句话解释什么是 MoE 模型')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', fill(PY, model=s, system='你是资深后端工程师，回答要给出可运行的代码。', user='用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('think', '思考强度', 'Python · reasoning_effort', fill(THINK, model=s, user='证明根号 2 是无理数，并指出证明里最关键的一步。')),
                      ('tools', '工具调用', 'Python · tools', fill(TOOLS, model=s))],
                callout=THINK_CALLOUT, note=QS_NOTE),
        cc=cc('DeepSeek V4 Pro', s, '把 Claude Code 的模型换成 DeepSeek V4 Pro：改一个配置文件，终端里的编程 Agent 就由 V4 Pro 驱动，按 token 计费。',
              f'<strong>省钱搭配：</strong>配置里已把 <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> 设成 <code>{F41}</code>，Claude Code 的轻量子任务走更便宜的模型，主任务继续用 V4 Pro。', haiku=F41),
        family_h2='DeepSeek 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 DeepSeek 模型，按任务和预算选择。',
        faq_h2='DeepSeek V4 Pro API 常见问题', faqs=faqs,
        final=dict(h2='用全天同价跑 DeepSeek V4 Pro', p=f'注册后创建 API Key，几分钟就能在代码或 Claude Code 里用上 {s}。', other='DeepSeek V4 Pro API in English'),
        ent_name='DeepSeek V4 Pro',
    )


# ======================================================================
# DeepSeek V4 Flash（旧版）
# ======================================================================
def v4f():
    s = F4
    faqs = [
        ('DeepSeek V4 Flash 停用了吗？',
         f'DeepSeek 官方已在 2026 年 9 月 10 日发布 V4.1 Flash 时下线 V4 Flash。出于兼容考虑，官方 API 仍接受 <code>{s}</code> 这个模型名，请求由 V4.1 Flash 处理，按 Flash 价格计费。'
         f'新项目建议直接使用 <a href="/zh/models/{F41}">deepseek-v4.1-flash</a>，在 AnyAIGC 上两者单价相同。'),
        ('DeepSeek V4 Flash API 多少钱？',
         f'AnyAIGC 上 <code>{s}</code> 按 token 计费：输入 {p(s, 0)}/百万 tokens，输出 {p(s, 1)}/百万 tokens，缓存命中 {p(s, 2)}/百万 tokens，与 V4.1 Flash 相同。'
         f'DeepSeek 官方对旧模型名按 Flash 价格计费，闲时为输入 {o(s, "off", 0)}、输出 {o(s, "off", 1)}、缓存命中 {o(s, "off", 2)}，高峰时段翻倍。实时价格以模型广场为准。'),
        faq_peak(f'<code>{s}</code>'),
        ('从 V4 Flash 迁移到 V4.1 Flash 要改什么？',
         f'把请求体里的 <code>model</code> 从 <code>{s}</code> 改成 <code>{F41}</code> 即可，接口地址、鉴权和参数都不用变。V4.1 Flash 额外支持图片输入，官方称它在基准测试中超越了 V4 Pro。'),
        ('V4 Flash 的参数和上下文是多少？',
         'DeepSeek 官方公布 V4 Flash 为 284B 总参数、13B 激活的 MoE，与 V4 Pro 同架构，上下文 1M tokens，只支持文本输入，以 MIT 许可开放权重。'),
        faq_cc('DeepSeek V4 Flash', s),
        faq_rpm(f'<code>{s}</code>'),
    ] + faq_common('DeepSeek V4 Flash')
    notice = (f'<strong>DeepSeek 官方已下线 V4 Flash。</strong>官方 API 把 <code>{s}</code> 的请求交给 V4.1 Flash 处理。'
              f'新项目建议直接用 <a href="/zh/models/{F41}">DeepSeek V4.1 Flash</a>，在 AnyAIGC 上两者单价相同。')
    return dict(
        title='DeepSeek V4 Flash API 价格与接入｜低价高并发 - AnyAIGC',
        desc=f'DeepSeek V4 Flash API 输入 {p(s, 0)} / 输出 {p(s, 1)} 每百万 tokens，1M 上下文，兼容 OpenAI 接口，并发不限。官方已升级到 V4.1 Flash，本页说明迁移方式。支持对公转账和专票。',
        og_desc=f'deepseek-v4-flash 输入 {p(s, 0)}/1M、输出 {p(s, 1)}/1M，1M 上下文，OpenAI 兼容，并发不限。DeepSeek 官方已升级到 V4.1 Flash，改一个模型名即可迁移。支持对公转账与增值税专票。',
        og_alt='AnyAIGC DeepSeek V4 Flash API：已升级到 V4.1 Flash',
        keywords='DeepSeek V4 Flash API,deepseek-v4-flash,DeepSeek V4 Flash 价格,DeepSeek V4 Flash 停用,DeepSeek V4 Flash 迁移,DeepSeek V4.1 Flash,DeepSeek V4 Flash API 企业,DeepSeek API 发票,DeepSeek API 对公转账,AnyAIGC',
        crumb='DeepSeek V4 Flash API', product='DeepSeek V4 Flash API（AnyAIGC）', sku=s,
        product_desc=f'通过 AnyAIGC 调用 DeepSeek V4 Flash（{s}）：OpenAI 兼容 /v1/chat/completions，1M 上下文，按 token 计费，不分高峰闲时，并发不限。',
        offers=offers(s),
        hero=dict(announce=f'官方已升级到 V4.1 Flash，把 model 改成 {F41} 即可迁移',
                  eyebrow=f'DeepSeek · {s}',
                  h1='DeepSeek V4 <span class="d-blue">Flash</span><span class="o-sr"> API</span>',
                  lead='V4 预览版的 Flash 模型，284B 总参数、13B 激活，1M 上下文。DeepSeek 官方已用 V4.1 Flash 替代它，本页说明价格和迁移方式。',
                  notice=notice,
                  ask='把这 1 万条用户反馈按问题类型分类，输出 JSON',
                  think='已分批读取 10,000 条反馈，归纳出 5 个问题类型',
                  out=['{"total": 10000, "categories": [', '{"type": "支付失败", "count": 3120},', '{"type": "物流延迟", "count": 2480},', '{"type": "账号登录", "count": 1960},', '{"type": "功能建议", "count": 1530},', '{"type": "其他", "count": 910}]}'],
                  chips=['低价', '1M 上下文', '工具调用'],
                  qs_btn='迁移示例',
                  sub=f'<code>{s}</code> 输入 {p(s, 0)} / 百万 tokens、输出 {p(s, 1)} / 百万 tokens、缓存命中 {p(s, 2)}，与 V4.1 Flash 同价。',
                  facts=[('模型 ID', s), ('上下文', '1M tokens'), ('输入', f'{p(s, 0)} / 1M'), ('并发', '不限'), ('企业', '对公 · 专票')]),
        about=dict(kicker='关于模型', h2='V4 预览版的轻量模型',
                   paras=['DeepSeek 在 2026 年 4 月发布 V4 预览版，同时推出 V4 Pro 和 V4 Flash。V4 Flash 是其中的轻量型号：284B 总参数、13B 激活的 MoE，与 V4 Pro 同架构，上下文 1M tokens，以 MIT 许可开放权重。',
                          f'9 月 10 日 DeepSeek 发布 V4.1 Flash，同时下线 V4 Flash。出于兼容考虑，官方 API 暂时把 <code>{s}</code> 的请求路由到 V4.1 Flash，并按 Flash 价格计费。',
                          f'如果你的代码里还写着 <code>{s}</code>，在 AnyAIGC 上可以继续调用；新项目建议把模型名换成 <code>{F41}</code>，两者单价相同，V4.1 Flash 还支持图片输入。'],
                   spec=[('上下文窗口', '1M', 'tokens'), ('参数规模', '284B', '13B 激活，MoE'),
                         ('输入模态', '文本', '仅文本输入'), ('思考模式', '三档', 'Non-think / Think High / Think Max'),
                         ('权重', '开放', 'MIT 许可'), ('官方状态', '已下线', f'替代型号 {F41}')]),
        features=dict(kicker='能力', h2='DeepSeek V4 Flash 能做什么',
                      items=[('软件工程', 'V4 预览版 Max 强度下，官方公布 SWE-bench Verified 79.0、LiveCodeBench 91.6。'),
                             ('科学推理', '官方公布 GPQA Diamond 88.1、HLE 34.8（Max 强度）。'),
                             ('网页检索 Agent', '官方公布 BrowseComp 73.2、Terminal Bench 2.0 为 56.9（Max 强度）。'),
                             ('三档思考', '官方列出 Non-think、Think High、Think Max 三种模式。'),
                             ('1M 上下文', '长文档、大仓库可以一次放进上下文。'),
                             ('平滑迁移', f'只改 model 字段就能换到 {F41}，接口、鉴权和参数都不用变。')]),
        pricing=dict(kicker='价格', h2='DeepSeek V4 Flash API 价格', lead='按 token 计费，全天同一单价，与 V4.1 Flash 相同。DeepSeek 官方对旧模型名按 Flash 价格计费，下表一并对比。',
                     billing_label='计费要点', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption=f'{s} 每百万 tokens 价格（美元），AnyAIGC 与 DeepSeek 官方闲时、高峰价对比',
                     note=pricing_note(s) + ' 官方价为旧模型名路由到 V4.1 Flash 后的 Flash 价格。',
                     costs_h3='成本示例', costs_lead='按常见用法估算，划线为同样用量的 DeepSeek 官方高峰价和闲时价。',
                     costs=[cost_card(s, '1 万条工单分类', '每条 2,000 tokens 输入 + 300 输出', 2000, 300, 0, 10000),
                            cost_card(s, 'Agent 编程 50 轮', '每轮 6 万 tokens 缓存命中 + 4,000 输入 + 2,000 输出', 4000, 2000, 60000, 50),
                            cost_card(s, '每百万输入 + 百万输出', '100 万 tokens 输入 + 100 万 tokens 输出', 1000000, 1000000)]),
        bench=dict(kicker='基准成绩', h2='DeepSeek V4 Flash 的官方基准成绩', lead='DeepSeek 在 V4 预览版发布时公布的指令模型成绩（Max 推理强度），与同期的 V4 Pro 对比。',
                   chart=('V4 Flash 对比 V4 Pro · 官方评测', [('V4 Flash · SWE-bench Verified', 79.0, True), ('V4 Pro · SWE-bench Verified', 80.6, False),
                                                         ('V4 Flash · LiveCodeBench', 91.6, True), ('V4 Pro · LiveCodeBench', 93.5, False),
                                                         ('V4 Flash · GPQA Diamond', 88.1, True), ('V4 Pro · GPQA Diamond', 90.1, False)]),
                   head=[('基准', ''), ('V4 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num')],
                   rows=[(a, b, y, x) for a, b, x, y in V4_ROWS],
                   caption='DeepSeek V4 Flash 与 V4 Pro 的官方基准对比（V4 预览版，Max 推理强度）',
                   note=f'数据来自 <a href="{HF_V4F}" target="_blank" rel="noopener">DeepSeek-V4-Flash 模型卡</a>，为 DeepSeek 公布的成绩。'),
        compare=dict(kicker='选型', h2='V4 Flash、V4.1 Flash、V4 Pro 怎么选', lead='V4 Flash 已被官方替代，新项目直接用同价的 V4.1 Flash。',
                     head=[('对比项', ''), ('V4 Flash', 'o-num o-hl'), ('V4.1 Flash', 'o-num'), ('V4 Pro', 'o-num')],
                     rows=[('状态', '', '官方已下线', '最新', '在售'), ('上下文', '', '1M', '1M', '1M'),
                           ('输入模态', '', '文本', '文本、图片', '文本'),
                           ('AnyAIGC 输入', '每百万 tokens', p(s, 0), p(F41, 0), p(PRO, 0)),
                           ('AnyAIGC 输出', '每百万 tokens', p(s, 1), p(F41, 1), p(PRO, 1)),
                           ('缓存命中', '每百万 tokens', p(s, 2), p(F41, 2), p(PRO, 2))],
                     caption='DeepSeek V4 Flash、V4.1 Flash、V4 Pro 对比，价格为 AnyAIGC 每百万 tokens 美元',
                     note=FACT_SRC + f' 详见 <a href="/zh/models/{F41}">DeepSeek V4.1 Flash API</a>。'),
        uses=dict(kicker='使用场景', h2='还在用 V4 Flash 的场景',
                  items=[('01 · 存量代码', '不改代码先跑着', f'已经写死 <code>{s}</code> 的脚本和服务可以继续调用，按同样的单价计费。'),
                         ('02 · 批量处理', '分类、抽取和摘要', '工单分类、字段抽取、评论打标。单价低、全天同价、不限并发。'),
                         ('03 · 灰度迁移', '新旧模型对比', f'同一批样本分别跑 <code>{s}</code> 和 <code>{F41}</code>，对比输出后再整体切换。'),
                         ('04 · Coding Agent', 'Claude Code 日常编码', f'在 Claude Code 里做日常编码。想要更好的效果，把模型换成 <code>{F41}</code>。')]),
        qs=dict(kicker='快速开始', h2='三步接入 DeepSeek V4 Flash API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=s, prompt='用三句话解释什么是 MoE 模型')),
                      ('migrate', '迁移到 V4.1 Flash', 'Python · 只改 model', fill(PY, model=F41, system='你是资深后端工程师，回答要给出可运行的代码。', user='用 Go 写一个带超时和重试的 HTTP 客户端。')),
                      ('stream', '流式输出', 'Python · stream=True', fill(STREAM, model=s, user='给一个 SaaS 产品写 5 条更新日志。')),
                      ('tools', '工具调用', 'Python · tools', fill(TOOLS, model=s))],
                callout=f'<strong>迁移提示：</strong>从 <code>{s}</code> 换到 <code>{F41}</code> 只需要改 <code>model</code> 字段，其余参数、接口地址和鉴权方式都一样，单价也相同。',
                note=QS_NOTE),
        cc=cc('DeepSeek V4 Flash', s, f'Claude Code 也能用 V4 Flash，不过更推荐直接配置 <code>{F41}</code>。下面的配置把模型名换掉即可。',
              f'<strong>推荐：</strong>把配置里的 <code>{s}</code> 全部换成 <code>{F41}</code>，单价相同，效果更好。'),
        family_h2='DeepSeek 系列其他模型', family_lead='同一个 API Key 可以调用下面所有 DeepSeek 模型，按任务和预算选择。',
        faq_h2='DeepSeek V4 Flash API 常见问题', faqs=faqs,
        final=dict(h2='改一个模型名，升级到 V4.1 Flash', p=f'注册后创建 API Key，{s} 和 {F41} 都能用，单价相同。', other='DeepSeek V4 Flash API in English'),
        ent_name='DeepSeek V4 Flash',
    )
