# English copy for the DeepSeek topic pages. Used by scripts/deepseek_pages.py.
# Prices come from deepseek_data.PRICE (lowest price in the model catalog); official prices, specs and benchmarks come from
# api-docs.deepseek.com, the deepseek.com news page and the deepseek-ai Hugging Face model cards (read 2026-10-30).
# Anything DeepSeek has not confirmed (V4.1-Flash-1017 parameter count, 0813 / 1017 benchmarks, legacy V4 Flash max output, etc.) is left out.
from deepseek_data import (PRICE, OFFICIAL, REG, PRICING, SUPPORT, DOCS_CHAT, DOCS_CC,
                           OFFICIAL_UPDATES, HF_V41, HF_V4F)
from deepseek_layout import cost, money

F41, PRO, F4 = 'deepseek-v4.1-flash', 'deepseek-v4-pro', 'deepseek-v4-flash'
PEAK = 'weekdays 01:00–04:00 and 06:00–10:00 UTC (9:00–12:00 and 14:00–18:00 Beijing time)'
OFFICIAL_PRICING = 'https://api-docs.deepseek.com/quick_start/pricing/'


def p(slug, i):
    return f'${PRICE[slug][i]}'


def o(slug, kind, i):
    return f'${OFFICIAL[slug][kind][i]}'


# ---------------- Shared FAQ ----------------
def faq_common(name):
    return [
        (f'Can I call the {name} API from mainland China?',
         'Yes. AnyAIGC is optimized for networks in mainland China, so you can usually call <code>https://anyaigc.ai</code> without a proxy. Usage is billed in USD, and you can pay with WeChat Pay, Alipay, USDT or a credit card. Companies can pay by bank transfer and get VAT invoices.'),
        (f'How do I get a {name} API key?',
         f'Sign up at <a href="{REG}">anyaigc.ai</a>, add credit, and create a key in the console. The same key works for every DeepSeek model and 300+ other models on the platform, so you do not need a separate DeepSeek Platform account.'),
        ('Can AnyAIGC issue invoices, including VAT special invoices?',
         'Yes. AnyAIGC issues invoices for every top-up based on the amount you actually paid, including Chinese VAT general invoices and VAT special invoices. Send your billing details to support to get one.'),
        ('Can my company pay by bank transfer and sign a contract?',
         f'Yes. Companies can top up by corporate bank transfer and sign a service agreement with AnyAIGC, with a dedicated support and technical contact. For procurement, <a href="{SUPPORT}">contact AnyAIGC support</a>.'),
    ]


def faq_cc(name, model):
    return (f'Can I use {name} in Claude Code?',
            f'Yes. DeepSeek models on AnyAIGC support both the OpenAI and the Anthropic API formats. In the env block of <code>~/.claude/settings.json</code>, set <code>ANTHROPIC_BASE_URL</code> to <code>https://anyaigc.ai</code>, <code>ANTHROPIC_AUTH_TOKEN</code> to your API key and <code>ANTHROPIC_MODEL</code> to <code>{model}</code>, then run <code>claude</code>. You pay per token.')


def faq_rpm(scope):
    return ('Are there concurrency or rate limits?',
            f'AnyAIGC does not cap concurrency for {scope}, and every user gets this by default. That suits batch jobs, CI pipelines and parallel agents.')


def faq_peak(scope):
    return ('Does AnyAIGC have peak and off-peak pricing?',
            f'No. The official DeepSeek API uses time-of-day pricing: {PEAK} is peak time, and peak prices are double the off-peak prices. On AnyAIGC, {scope} is billed at one rate around the clock. '
            'That rate is about 60% off the official peak price. Live prices are shown in the model catalog.')


# ---------------- Code samples (@MODEL placeholders avoid escaping braces in f-strings) ----------------
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
print(resp.usage)  # prompt_tokens_details.cached_tokens = tokens billed at the cache-hit rate'''

STREAM = '''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

stream = client.chat.completions.create(
    model="@MODEL",
    messages=[{"role": "user", "content": "@USER"}],
    stream=True,
    stream_options={"include_usage": True},  # the last chunk carries token usage
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()'''

THINK = '''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# Toggle thinking with the thinking field (enabled / disabled); set depth with reasoning_effort
resp = client.chat.completions.create(
    model="@MODEL",
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
    messages=[{"role": "user", "content": "@USER"}],
)
print(resp.choices[0].message.content)
print(resp.usage.completion_tokens_details.reasoning_tokens)  # tokens spent on thinking'''

TOOLS = '''import json
import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

tools = [{
    "type": "function",
    "function": {
        "name": "run_tests",
        "description": "Run the unit tests at a path in the repo and return the failing cases",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Test file or directory"}},
            "required": ["path"],
        },
    },
}]
messages = [{"role": "user", "content": "Run tests/test_api.py and tell me which cases fail."}]

resp = client.chat.completions.create(model="@MODEL", messages=messages, tools=tools)
msg = resp.choices[0].message
# Send the full assistant message back unchanged, then append the tool results
messages.append(msg.model_dump(exclude_none=True))
for call in msg.tool_calls or []:
    args = json.loads(call.function.arguments)
    result = {"path": args["path"], "failed": ["test_login_timeout"]}  # replace with the real result
    messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

final = client.chat.completions.create(model="@MODEL", messages=messages, tools=tools)
print(final.choices[0].message.content)'''

VISION = '''import base64
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# Encode a local image as a Base64 data URL; a public image URL works too
b64 = base64.b64encode(Path("chart.png").read_bytes()).decode()

resp = client.chat.completions.create(
    model="@MODEL",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Read the value for each quarter in this chart and return a Markdown table."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ],
    }],
)
print(resp.choices[0].message.content)'''

CC = '''{
  "env": {
    "ANTHROPIC_BASE_URL": "https://anyaigc.ai",
    "ANTHROPIC_AUTH_TOKEN": "sk-your-API-key",
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
        kicker='Claude Code', h2=f'Use {name} in Claude Code', lead=lead,
        steps=['<strong>Install Claude Code</strong>: use the official installer, for example <code>curl -fsSL https://claude.ai/install.sh | bash</code> on macOS or Linux.',
               '<strong>Add the config</strong>: edit <code>~/.claude/settings.json</code>, add the env block below, and replace <code>ANTHROPIC_AUTH_TOKEN</code> with the key you created on AnyAIGC.',
               f'<strong>Start coding</strong>: run <code>claude</code> in your project folder. Type <code>/model</code> to confirm the current model is <code>{model}</code>.'],
        code=fill(CC, model=model, haiku=haiku or model), callout=callout,
        note=f'For full steps and common errors, see the <a href="{DOCS_CC}" target="_blank" rel="noopener">Claude Code setup guide</a>. Swap the model name in the guide for <code>{model}</code>.')


def qs_steps(model):
    return ['<strong>Sign up and add credit</strong>: create an account at <a href="' + REG + '">anyaigc.ai</a>. Top up from $1; your balance works across every model on the platform.',
            '<strong>Create an API key</strong>: create a key in the console, copy the <code>sk-</code> key, and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Send a request</strong>: call <code>POST https://anyaigc.ai/v1/chat/completions</code> with <code>model</code> set to <code>{model}</code> and an <code>Authorization: Bearer</code> header. With the OpenAI SDK, just set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>.']


QS_NOTE = f'See the <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions API reference</a> for every parameter. Swap the model name in the doc examples for the DeepSeek model ID you want.'
THINK_CALLOUT = ('<strong>Parameters:</strong> DeepSeek says the V4 series thinks by default. The <code>thinking</code> field in the request body turns it on or off (<code>{"type": "enabled"}</code> or <code>{"type": "disabled"}</code>), '
                 'and <code>reasoning_effort</code> sets the depth (officially <code>low</code> / <code>high</code> / <code>max</code>). Thinking tokens count as output and show up in <code>usage.completion_tokens_details.reasoning_tokens</code>. '
                 'Sampling parameters such as <code>temperature</code> have no effect in thinking mode.')

PRICE_HEAD = [('Item', ''), ('Model', ''), ('AnyAIGC', 'o-num o-hl'), ('Official off-peak', 'o-num'), ('Official peak', 'o-num'), ('Discount', 'o-num')]
LABELS = [('Input', 'Cache miss, per 1M tokens'), ('Output', 'Per 1M tokens, incl. thinking'), ('Cache hit', 'Per 1M tokens')]


def pricing_note(q):
    return (f'Prices are in USD and billed on the tokens you actually use. Output includes thinking tokens, and repeated prompt prefixes are billed at the cache-hit rate. '
            f'Official prices come from the <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">DeepSeek API pricing page</a> (USD). Peak time is {PEAK}; all other hours are off-peak. '
            f'The table shows the lowest price in the model catalog. Live prices are shown in the <a href="{PRICING}?keyword={q}">AnyAIGC model catalog</a>.')


def cost_card(slug, title, calc, inp=0, out=0, cache=0, n=1):
    a = money(cost(slug, inp, out, cache, n))
    off = money(cost(slug, inp, out, cache, n, official='off'))
    peak = money(cost(slug, inp, out, cache, n, official='peak'))
    return (title, calc, a, f'Official peak <s>{peak}</s> · off-peak <s>{off}</s>')


def offers(slug):
    return [('Input (per 1M tokens)', PRICE[slug][0]), ('Output (per 1M tokens)', PRICE[slug][1]),
            ('Cache hit (per 1M tokens)', PRICE[slug][2])]


BILLING = [('Per-token billing', 'Input, output and cache hits priced separately'), ('One rate all day', 'Official peak price is 2× off-peak'),
           ('About 60% off', "Vs. DeepSeek's official peak price"), ('No concurrency cap', 'On by default for every user')]

FAMILY = [
    ('deepseek', '', ('DeepSeek overview', 'Compare V4.1 Flash, V4 Pro and V4 Flash pricing')),
    (F41, 'Latest', f'Native vision, 552B MoE, 1M context · input {p(F41, 0)} / 1M'),
    (PRO, '', f'1.6T MoE flagship, adjustable reasoning effort · input {p(PRO, 0)} / 1M'),
    (F4, 'Legacy', f'Upgraded to V4.1 Flash by DeepSeek · input {p(F4, 0)} / 1M'),
]

FACT_SRC = f'Specs come from the official DeepSeek <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">API docs</a> and Hugging Face model cards. Prices are current AnyAIGC prices; live prices are shown in the model catalog.'

# V4 preview (2026-04) instruct model results at Max reasoning effort, from the DeepSeek-V4-Flash Hugging Face model card
V4_ROWS = [('SWE-bench Verified', 'Software engineering, Resolved', '80.6', '79.0'), ('LiveCodeBench', 'Coding, Pass@1', '93.5', '91.6'),
           ('GPQA Diamond', 'Science reasoning, Pass@1', '90.1', '88.1'), ('HLE', 'General reasoning, Pass@1', '37.7', '34.8'),
           ('Terminal Bench 2.0', 'Terminal coding, Acc', '67.9', '56.9'), ('BrowseComp', 'Web browsing, Pass@1', '83.4', '73.2'),
           ('Codeforces', 'Competitive programming, Rating', '3206', '3052')]


def build(slug):
    return {'deepseek': hub, F41: v41, PRO: pro, F4: v4f}[slug]()


# ======================================================================
# Overview page
# ======================================================================
def hub():
    faqs = [
        ('How much does the DeepSeek API cost?',
         f'DeepSeek on AnyAIGC is billed per token. Per 1M tokens: <code>{F41}</code> is {p(F41, 0)} input, {p(F41, 1)} output and {p(F41, 2)} cache hit; '
         f'<code>{PRO}</code> is {p(PRO, 0)} input, {p(PRO, 1)} output and {p(PRO, 2)} cache hit; <code>{F4}</code> costs the same as V4.1 Flash. Live prices are shown in the model catalog.'),
        faq_peak('every DeepSeek model'),
        ('Which DeepSeek models does AnyAIGC offer, and what are the model IDs?',
         f'This page covers three: <code>{F41}</code> (DeepSeek\'s latest Flash model, with native vision), <code>{PRO}</code> (the 1.6T-parameter V4 flagship) and <code>{F4}</code> (the V4 preview Flash model, which DeepSeek has replaced with V4.1 Flash). '
         'Put the model ID in the <code>model</code> field of the request body. Switching models means changing only that field.'),
        ('Should I use V4.1 Flash or V4 Pro?',
         f'Start with <a href="/en/models/{F41}">V4.1 Flash</a> for most work. DeepSeek says it now beats V4 Pro on performance, cost, speed and total task time, its input price is about a quarter of V4 Pro\'s, and it can read images. '
         f'If you already have V4 Pro tuned in production, you can keep using <a href="/en/models/{PRO}">V4 Pro</a>: DeepSeek has said it will keep serving the V4 Pro API after September 14, 2026.'),
        ('How big is the context window? Can I send images?',
         'DeepSeek lists a 1M-token context and up to 384K output tokens for both V4.1 Flash and V4 Pro. Only V4.1 Flash accepts images; V4 Pro and V4 Flash are text-only.'),
        ('Is the DeepSeek API OpenAI-compatible?',
         'Yes. All three models use <code>POST https://anyaigc.ai/v1/chat/completions</code> with the same request and response format as OpenAI Chat Completions. With the official OpenAI SDK, set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>. The Anthropic format is supported too, so Claude Code works.'),
        faq_cc('DeepSeek', F41),
        faq_rpm('the DeepSeek series'),
    ] + faq_common('DeepSeek')
    return dict(
        title='DeepSeek API Pricing & Access | V4.1 Flash, V4 Pro - AnyAIGC',
        desc=f'DeepSeek V4.1 Flash and V4 Pro on one OpenAI-compatible API key. From {p(F41, 0)} per 1M input tokens, one rate all day, 1M context, no rate limits, VAT invoices.',
        og_desc=f'Call DeepSeek V4.1 Flash, V4 Pro and V4 Flash with one key. From {p(F41, 0)}/1M input, about 60% off official peak pricing, no peak pricing, OpenAI-compatible, works with Claude Code, invoices and contracts.',
        og_alt='AnyAIGC DeepSeek API: V4.1 Flash, V4 Pro, V4 Flash',
        keywords='DeepSeek API,DeepSeek API pricing,DeepSeek API key,DeepSeek V4 API,DeepSeek V4.1 Flash API,DeepSeek V4 Pro API,DeepSeek Claude Code,DeepSeek API for business,DeepSeek API invoice,AnyAIGC',
        crumb='DeepSeek API', product='DeepSeek API (AnyAIGC)', sku='deepseek',
        product_desc=f'Call DeepSeek models ({F41}, {PRO}, {F4}) through AnyAIGC: OpenAI-compatible /v1/chat/completions, per-token billing, one rate all day, no concurrency cap.',
        offers=[(f'{n} input (per 1M tokens)', PRICE[s][0]) for s, n in ((F41, 'V4.1 Flash'), (PRO, 'V4 Pro'), (F4, 'V4 Flash'))]
        + [(f'{n} output (per 1M tokens)', PRICE[s][1]) for s, n in ((F41, 'V4.1 Flash'), (PRO, 'V4 Pro'), (F4, 'V4 Flash'))],
        hero=dict(announce=f'DeepSeek V4.1 Flash is live on AnyAIGC at {p(F41, 0)} per 1M input tokens, one rate all day',
                  eyebrow='DeepSeek',
                  h1='DeepSeek <span class="d-blue">API</span>',
                  lead='DeepSeek V4.1 Flash, V4 Pro and V4 Flash, all on one API key. Per-token billing with no peak hours, about 60% off DeepSeek\'s official peak price.',
                  ask='Read this repo, fix the failing tests and add the missing type definitions',
                  think='Read the repo and found 3 failing tests and 2 missing type definitions',
                  out=['Failing tests: <code>test_parse_date</code>, <code>test_retry</code> and <code>test_config_merge</code>.', 'Causes: <code>utils/date.py</code> ignores time zones, the backoff cap in <code>retry()</code> is inverted, and <code>merge()</code> shallow-copies and mutates the defaults.', 'Patched 3 files and added types for <code>Config</code> and <code>RetryPolicy</code>.', 'Re-run: <code>42 passed, 0 failed</code>.'],
                  chips=['DeepThink', '1M context', 'Vision'],
                  qs_btn='Quick start',
                  sub=f'OpenAI-compatible <code>/v1/chat/completions</code> that also plugs straight into Claude Code. <code>{F41}</code> starts at {p(F41, 0)} per 1M input tokens, with no concurrency cap.',
                  facts=[('Models', 'V4.1 Flash · V4 Pro · V4 Flash'), ('Context', '1M'), ('Input', f'from {p(F41, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        models=dict(kicker='Models', h2='Three DeepSeek models', lead='One key, one endpoint. Change the model ID to match the task.',
                    unit_in='1M input', unit_out='1M output', go='View guide', legacy_tag='Legacy',
                    items=[(F41, 'Latest', 'The smallest model in DeepSeek\'s new architecture family: a 552B MoE with native vision. DeepSeek says it beats V4 Pro across the board.', ['1M context, up to 384K output', 'Image input and tool calls', 'Input about 1/4 the price of V4 Pro']),
                           (PRO, '', 'The DeepSeek V4 flagship: 1.6T total and 49B active parameters. The August GA release added low / high / max reasoning effort.', ['1M context, up to 384K output', 'Adjustable reasoning effort', 'MIT license']),
                           (F4, 'Legacy', 'The V4 preview Flash model: 284B total and 13B active parameters. DeepSeek has retired it and routes the old name to V4.1 Flash.', ['1M context', 'Same price as V4.1 Flash', 'Use V4.1 Flash for new projects'])]),
        pricing=dict(kicker='Pricing', h2='DeepSeek API pricing', lead='Per-token billing at one rate all day, with no subscription or monthly fee. The table compares DeepSeek\'s official off-peak and peak USD prices.',
                     billing_label='Billing at a glance', billing=BILLING,
                     head=[('Item', ''), ('AnyAIGC', 'o-num o-hl'), ('Official off-peak', 'o-num'), ('Official peak', 'o-num'), ('Discount', 'o-num')],
                     labels=LABELS, caption='DeepSeek prices per 1M tokens (USD): AnyAIGC vs. DeepSeek official off-peak and peak',
                     note=pricing_note('deepseek') + ' DeepSeek has retired V4 Flash, so the official price for <code>deepseek-v4-flash</code> is the V4.1 Flash price.',
                     costs_h3='Cost examples', costs_lead='Estimates for common workloads. Struck-through figures are the same usage at DeepSeek\'s official off-peak and peak prices.',
                     costs=[cost_card(F41, 'V4.1 Flash · 50-turn coding agent', 'Each turn: 60K cache-hit tokens + 4,000 input + 2,000 output', 4000, 2000, 60000, 50),
                            cost_card(F41, 'V4.1 Flash · 10,000 ticket labels', 'Each: 2,000 input tokens + 300 output', 2000, 300, 0, 10000),
                            cost_card(PRO, 'V4 Pro · 500K-token codebase review', '500K input tokens + 5,000 output', 500000, 5000)]),
        compare=dict(kicker='Compare', h2='V4.1 Flash vs. V4 Pro vs. V4 Flash', lead='Start new projects on V4.1 Flash. Keep V4 Pro if it is already tuned in production. Move off V4 Flash.',
                     head=[('Spec', ''), ('V4.1 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num'), ('V4 Flash', 'o-num')],
                     rows=[('Status', '', 'Latest', 'Available', 'Retired by DeepSeek'),
                           ('Parameters', '', '552B MoE', '1.6T / 49B active', '284B / 13B active'),
                           ('Context / max output', '', '1M / 384K', '1M / 384K', '1M / –'),
                           ('Input', '', 'Text, images', 'Text', 'Text'),
                           ('AnyAIGC input', 'Per 1M tokens', p(F41, 0), p(PRO, 0), p(F4, 0)),
                           ('AnyAIGC output', 'Per 1M tokens', p(F41, 1), p(PRO, 1), p(F4, 1)),
                           ('Cache hit', 'Per 1M tokens', p(F41, 2), p(PRO, 2), p(F4, 2))],
                     caption='DeepSeek V4.1 Flash, V4 Pro and V4 Flash compared; prices are AnyAIGC USD per 1M tokens',
                     note=FACT_SRC + ' “–” means DeepSeek has not published the figure.'),
        uses=dict(kicker='Use cases', h2='What teams build with the DeepSeek API',
                  items=[('01 · Coding agents', 'Claude Code, CI and auto-fix', 'Plug DeepSeek into Claude Code or your own agent framework to read code, run tests and fix errors. AnyAIGC has no concurrency cap, so many agents can run at once.'),
                         ('02 · Long context', 'Large repos and long documents', 'A 1M-token context holds a whole codebase or hundreds of pages. Repeated prefixes bill at the cache-hit rate, just ' + p(F41, 2) + ' per 1M tokens on V4.1 Flash.'),
                         ('03 · Vision', 'Charts, screenshots and scans', 'V4.1 Flash takes images natively, so it can read charts, inspect UI screenshots and pull fields out of scanned documents.'),
                         ('04 · Batch jobs', 'Classification, extraction, summaries', 'V4.1 Flash input is ' + p(F41, 0) + ' per 1M tokens at one rate all day, a good fit for ticket triage, field extraction and review tagging at scale.')]),
        qs=dict(kicker='Quick start', h2='Get started with the DeepSeek API in three steps', steps=qs_steps(F41),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=F41, prompt='Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', fill(PY, model=F41, system='You are a senior backend engineer. Answer with runnable code.', user='Write a Go HTTP client with timeouts and retries.')),
                      ('think', 'Thinking mode', 'Python · thinking', fill(THINK, model=PRO, user='Prove that the square root of 2 is irrational and point out the key step.')),
                      ('stream', 'Streaming', 'Python · stream=True', fill(STREAM, model=F41, user='Write 5 changelog entries for a SaaS product.'))],
                callout=THINK_CALLOUT, note=QS_NOTE),
        cc=cc('DeepSeek', F41, 'Point Claude Code at DeepSeek: edit one config file and your terminal coding agent runs on DeepSeek V4.1 Flash, billed per token.',
              f'<strong>Switch models:</strong> to use V4 Pro, replace <code>{F41}</code> with <code>{PRO}</code> in the config. You can also keep <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> on V4.1 Flash for lightweight subtasks.'),
        family_h2='Every DeepSeek model', family_lead='One API key calls every DeepSeek model below. Pick by task and budget.',
        faq_h2='DeepSeek API FAQ', faqs=faqs,
        final=dict(h2='Run every DeepSeek model on one key', p='Sign up, create an API key, and you can use DeepSeek V4.1 Flash and V4 Pro in your code or Claude Code within minutes.',
                   other='DeepSeek API 中文版'),
        ent_name='DeepSeek',
    )


# ======================================================================
# DeepSeek V4.1 Flash
# ======================================================================
def v41():
    s = F41
    faqs = [
        ('How much does the DeepSeek V4.1 Flash API cost?',
         f'<code>{s}</code> on AnyAIGC is billed per token: {p(s, 0)} per 1M input tokens, {p(s, 1)} per 1M output tokens and {p(s, 2)} per 1M cache-hit tokens. '
         f'DeepSeek\'s official off-peak USD price is {o(s, "off", 0)} input, {o(s, "off", 1)} output and {o(s, "off", 2)} cache hit, and it doubles at peak times. Output includes thinking tokens. Live prices are shown in the model catalog.'),
        faq_peak(f'<code>{s}</code>'),
        ('What is new in DeepSeek V4.1 Flash?',
         'According to DeepSeek, V4.1 Flash is the smallest model in its new architecture family: a 552B-parameter MoE with an asymmetric Causal-Encoder-Decoder design, 8B active parameters on input and 16B on output, and native vision. '
         'DeepSeek says its KV cache needs 1/4 the HBM and 1/8 the SSD of the previous generation, which sharply cuts caching costs for agent workloads.'),
        ('Is V4.1 Flash better than V4 Pro?',
         f'DeepSeek says that across multiple tests, V4.1 Flash now beats <a href="/en/models/{PRO}">V4 Pro</a> on performance, cost, speed and total task time. Its model card reports DeepSWE v1.1 at 74.2 vs. 62.7 and Terminal-Bench 2.1 at 90.6 vs. 87.9. '
         f'On AnyAIGC, V4.1 Flash input costs {p(s, 0)}, about a quarter of V4 Pro ({p(PRO, 0)}).'),
        ('Does DeepSeek V4.1 Flash accept images? How do I send one?',
         'Yes. Add an <code>{"type": "image_url", "image_url": {"url": ...}}</code> block to the <code>messages[].content</code> array. The <code>url</code> can be a public image URL or a Base64 data URL.'),
        ('How long is the context? Does it support thinking mode?',
         'DeepSeek lists a 1M-token context and up to 384K output tokens for V4.1 Flash. It supports both thinking and non-thinking modes (thinking is on by default), plus tool calls and JSON output.'),
        faq_cc('DeepSeek V4.1 Flash', s),
        faq_rpm(f'<code>{s}</code>'),
    ] + faq_common('DeepSeek V4.1 Flash')
    return dict(
        title='DeepSeek V4.1 Flash API Pricing | 1M Context, Vision - AnyAIGC',
        desc=f'DeepSeek V4.1 Flash API: {p(s, 0)} input / {p(s, 1)} output per 1M tokens, no peak pricing, native vision, 1M context, no rate limits. Bank transfer, VAT invoices.',
        og_desc=f'deepseek-v4.1-flash at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 60% off official peak pricing. 552B MoE, native vision, 1M context, works with Claude Code. Invoices and contracts for teams.',
        og_alt='AnyAIGC DeepSeek V4.1 Flash API: 1M context, native vision',
        keywords='DeepSeek V4.1 Flash API,deepseek-v4.1-flash,deepseek-v4.1-flash pricing,DeepSeek Flash API,DeepSeek V4.1 API key,DeepSeek V4.1 Flash vision,DeepSeek V4.1 Flash Claude Code,DeepSeek V4.1 Flash API for business,DeepSeek API invoice,AnyAIGC',
        crumb='DeepSeek V4.1 Flash API', product='DeepSeek V4.1 Flash API (AnyAIGC)', sku=s,
        product_desc=f'Call DeepSeek V4.1 Flash ({s}) through AnyAIGC: OpenAI-compatible /v1/chat/completions, native vision, 1M context, per-token billing, one rate all day, no concurrency cap.',
        offers=offers(s),
        hero=dict(announce='DeepSeek says V4.1 Flash now beats V4 Pro on performance, cost and speed',
                  eyebrow=f'DeepSeek · {s}',
                  h1='DeepSeek V4.1 <span class="d-blue">Flash</span><span class="o-sr"> API</span>',
                  lead='The smallest model in DeepSeek\'s new architecture family: a 552B MoE with native vision. In DeepSeek\'s words, stronger, faster and more affordable.',
                  ask='Look at this report screenshot, find the three biggest month-over-month drops and explain why',
                  think='Read the table in the screenshot: 12 metrics, month-over-month change computed for each',
                  out=['The three biggest drops:', '1. New-customer conversion −18.4%: spend moved from feed ads to search, bringing lower-intent traffic.', '2. Average order value −11.2%: the spend-and-save promo lowered basket size while order count rose.', '3. Repeat purchase rate −7.9%: fewer touchpoints with existing customers after the loyalty points change.', 'Start with #1, which has the largest revenue impact.'],
                  chips=['Vision', 'DeepThink', '1M context'],
                  qs_btn='Quick start',
                  sub=f'<code>{s}</code> costs {p(s, 0)} per 1M input tokens, {p(s, 1)} per 1M output tokens and {p(s, 2)} per 1M cache hits, at one rate all day. It works with OpenAI-compatible clients and Claude Code.',
                  facts=[('Model ID', s), ('Context', '1M tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About the model', h2='Asymmetric design, more intelligence per dollar',
                   paras=['DeepSeek released V4.1 Flash in September 2026, describing it as the smallest model in a new architecture family, with native vision. The new design aims for a higher ceiling, faster inference, more throughput and room to scale to larger models.',
                          'It is a 552B-parameter MoE built on a Causal-Encoder-Decoder design where input and output are asymmetric: 8B parameters are active on input and 16B on output. DeepSeek says the KV cache needs 1/4 the HBM and 1/8 the SSD of the previous generation, which cuts the cache costs that dominate agent workloads. In October DeepSeek updated it to V4.1-Flash-1017, citing clear gains on project-level coding.',
                          f'On AnyAIGC, <code>{s}</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint with text and image input. It also works directly in Claude Code, at one rate all day with no concurrency cap.'],
                   spec=[('Context window', '1M', 'tokens'), ('Max output', '384K', 'tokens'),
                         ('Parameters', '552B', 'MoE, 8B active input / 16B active output'), ('Input', 'Text, images', 'Native multimodal'),
                         ('Thinking', 'On or off', 'On by default'), ('Weights', 'Open', 'MIT license')]),
        features=dict(kicker='Capabilities', h2='What DeepSeek V4.1 Flash can do',
                      items=[('Agentic coding', 'The model card reports DeepSWE v1.1 at 74.2 and Terminal-Bench 2.1 at 90.6, both ahead of V4 Pro.'),
                             ('Image understanding', 'Native vision: send charts, UI screenshots and scanned documents as input.'),
                             ('Thinking on or off', 'Thinking is on by default. Turn it off for simple requests to get faster, shorter responses.'),
                             ('Tool calls and JSON', 'DeepSeek\'s docs list tool calls and JSON output, so it fits agent frameworks and automation pipelines.'),
                             ('Cheaper caching', f'DeepSeek says the KV cache is much smaller. On AnyAIGC cache hits cost {p(s, 2)} per 1M tokens, so repeated context in multi-turn agents stays cheap.'),
                             ('1M context', 'Up to 384K output tokens. Large repos and long documents fit in a single context.')]),
        pricing=dict(kicker='Pricing', h2='DeepSeek V4.1 Flash API pricing', lead='Per-token billing at one rate all day, with no subscription or monthly fee. About 60% off DeepSeek\'s official peak price.',
                     billing_label='Billing at a glance', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption=f'{s} prices per 1M tokens (USD): AnyAIGC vs. DeepSeek official off-peak and peak',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead='Estimates for common workloads. Struck-through figures are the same usage at DeepSeek\'s official off-peak and peak prices.',
                     costs=[cost_card(s, '50-turn coding agent', 'Each turn: 60K cache-hit tokens + 4,000 input + 2,000 output', 4000, 2000, 60000, 50),
                            cost_card(s, '10,000 ticket labels', 'Each: 2,000 input tokens + 300 output', 2000, 300, 0, 10000),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='V4.1 Flash vs. V4 Pro', lead='Results DeepSeek published in the V4.1 Flash model card, compared with V4 Pro.',
                   chart=('V4.1 Flash vs. V4 Pro · official evals', [('V4.1 Flash · DeepSWE', 74.2, True), ('V4 Pro · DeepSWE', 62.7, False),
                                                                   ('V4.1 Flash · Terminal-Bench', 90.6, True), ('V4 Pro · Terminal-Bench', 87.9, False),
                                                                   ('V4.1 Flash · HumanEval', 79.4, True), ('V4 Pro · HumanEval', 76.8, False)]),
                   head=[('Benchmark', ''), ('V4.1 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num')],
                   rows=[('DeepSWE v1.1', 'Software engineering, Resolved', '74.2', '62.7'), ('Terminal-Bench 2.1', 'Terminal coding', '90.6', '87.9'),
                         ('HumanEval', 'Coding, Pass@1', '79.4', '76.8'), ('GSM8K', 'Math, EM', '93.0', '92.6'),
                         ('MMLU-Pro', 'General knowledge, EM', '74.1', '73.5')],
                   caption='DeepSeek V4.1 Flash vs. V4 Pro official benchmarks',
                   note=f'Source: the <a href="{HF_V41}" target="_blank" rel="noopener">DeepSeek-V4.1-Flash model card</a>, results as published by DeepSeek. DeepSeek has not published text results for the October V4.1-Flash-1017 update, so they are not listed here.'),
        compare=dict(kicker='Compare', h2='V4.1 Flash vs. V4 Pro vs. V4 Flash', lead='Start new projects on V4.1 Flash. It is the only one of the three that reads images.',
                     head=[('Spec', ''), ('V4.1 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num'), ('V4 Flash', 'o-num')],
                     rows=[('Status', '', 'Latest', 'Available', 'Retired by DeepSeek'), ('Context', '', '1M', '1M', '1M'),
                           ('Input', '', 'Text, images', 'Text', 'Text'),
                           ('AnyAIGC input', 'Per 1M tokens', p(s, 0), p(PRO, 0), p(F4, 0)),
                           ('AnyAIGC output', 'Per 1M tokens', p(s, 1), p(PRO, 1), p(F4, 1)),
                           ('Cache hit', 'Per 1M tokens', p(s, 2), p(PRO, 2), p(F4, 2))],
                     caption='DeepSeek V4.1 Flash, V4 Pro and V4 Flash compared; prices are AnyAIGC USD per 1M tokens',
                     note=FACT_SRC + f' See the <a href="/en/models/{PRO}">DeepSeek V4 Pro API</a> guide.'),
        uses=dict(kicker='Use cases', h2='What DeepSeek V4.1 Flash is good for',
                  items=[('01 · Coding agents', 'Claude Code and custom agents', 'Run tasks of dozens or hundreds of steps in Claude Code or your own agent framework. Cache hits are cheap, so repeated context in long sessions costs little.'),
                         ('02 · Vision', 'Reports, screenshots and scans', 'Hand the model report screenshots, UI captures or scans to pull out data, check figures and write up findings.'),
                         ('03 · Batch jobs', 'Classification, extraction, summaries', 'Ticket triage, field extraction, review tagging and long-document summaries. Low unit price, one rate all day, no concurrency cap.'),
                         ('04 · Long context', 'Large repos and long documents', 'Fit a whole codebase or a full contract set into 1M tokens, then ask the model to map the structure and answer questions.')]),
        qs=dict(kicker='Quick start', h2='Get started with the DeepSeek V4.1 Flash API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=s, prompt='Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', fill(PY, model=s, system='You are a senior backend engineer. Answer with runnable code.', user='Write a Go HTTP client with timeouts and retries.')),
                      ('vision', 'Image input', 'Python · image_url', fill(VISION, model=s)),
                      ('think', 'Thinking mode', 'Python · thinking', fill(THINK, model=s, user='Rewrite this SQL to use window functions: SELECT ...')),
                      ('tools', 'Tool calls', 'Python · tools', fill(TOOLS, model=s))],
                callout=THINK_CALLOUT, note=QS_NOTE),
        cc=cc('DeepSeek V4.1 Flash', s, 'Point Claude Code at DeepSeek V4.1 Flash: edit one config file and write code with DeepSeek in your terminal, billed per token.',
              f'<strong>Switch models:</strong> to compare with V4 Pro, replace <code>{s}</code> with <code>{PRO}</code> in the config. Nothing else changes.'),
        family_h2='Other DeepSeek models', family_lead='One API key calls every DeepSeek model below. Pick by task and budget.',
        faq_h2='DeepSeek V4.1 Flash API FAQ', faqs=faqs,
        final=dict(h2='Run DeepSeek V4.1 Flash at one rate all day', p=f'Sign up, create an API key, and you can use {s} in your code or Claude Code within minutes.', other='DeepSeek V4.1 Flash API 中文版'),
        ent_name='DeepSeek V4.1 Flash',
    )


# ======================================================================
# DeepSeek V4 Pro
# ======================================================================
def pro():
    s = PRO
    faqs = [
        ('How much does the DeepSeek V4 Pro API cost?',
         f'<code>{s}</code> on AnyAIGC is billed per token: {p(s, 0)} per 1M input tokens, {p(s, 1)} per 1M output tokens and {p(s, 2)} per 1M cache-hit tokens. '
         f'DeepSeek\'s official off-peak USD price is {o(s, "off", 0)} input, {o(s, "off", 1)} output and {o(s, "off", 2)} cache hit, and it doubles at peak times. Output includes thinking tokens. Live prices are shown in the model catalog.'),
        faq_peak(f'<code>{s}</code>'),
        ('Is DeepSeek V4 Pro being retired?',
         f'Not at this time. On September 10, 2026 DeepSeek announced a plan to retire V4 Pro, then said in its official <a href="{OFFICIAL_UPDATES}" target="_blank" rel="noopener">changelog</a> that, in response to user demand, it will keep serving the V4 Pro API after September 14 with billing unchanged.'),
        ('Should I use V4 Pro or V4.1 Flash?',
         f'DeepSeek says <a href="/en/models/{F41}">V4.1 Flash</a> now beats V4 Pro on performance, cost, speed and total task time. Its input price is about a quarter of V4 Pro\'s and it accepts images, so try it first on new projects. '
         'If your prompts and workflows are already tuned for V4 Pro in production, you can keep using V4 Pro.'),
        ('How do I set V4 Pro\'s reasoning effort?',
         'The August V4 Pro GA release added three reasoning effort levels: <code>low</code>, <code>high</code> and <code>max</code>. Thinking is on by default at <code>high</code>. '
         'Set the level with <code>reasoning_effort</code>, or turn thinking off with <code>{"type": "disabled"}</code> in the <code>thinking</code> field. See the quick start on this page for an example.'),
        ('What are V4 Pro\'s parameters and context length?',
         'DeepSeek lists V4 Pro as an MoE with 1.6T total and 49B active parameters, a hybrid attention design and 32T pretraining tokens. It has a 1M-token context and up to 384K output tokens, accepts text only, and its weights are open under the MIT license.'),
        faq_cc('DeepSeek V4 Pro', s),
        faq_rpm(f'<code>{s}</code>'),
    ] + faq_common('DeepSeek V4 Pro')
    return dict(
        title='DeepSeek V4 Pro API Pricing | 1M Context Agentic Coding - AnyAIGC',
        desc=f'DeepSeek V4 Pro API (1.6T MoE): {p(s, 0)} input / {p(s, 1)} output per 1M tokens, one rate all day, 1M context, works with Claude Code. Invoices and contracts.',
        og_desc=f'deepseek-v4-pro at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 60% off official peak pricing. 1.6T MoE flagship, 1M context, low / high / max reasoning effort, works with Claude Code. Invoices and contracts.',
        og_alt='AnyAIGC DeepSeek V4 Pro API: 1.6T MoE, 1M context',
        keywords='DeepSeek V4 Pro API,deepseek-v4-pro,deepseek-v4-pro pricing,DeepSeek V4 Pro API key,DeepSeek V4 Pro Claude Code,DeepSeek V4 Pro reasoning effort,DeepSeek V4 Pro deprecation,DeepSeek V4 Pro API for business,DeepSeek API invoice,AnyAIGC',
        crumb='DeepSeek V4 Pro API', product='DeepSeek V4 Pro API (AnyAIGC)', sku=s,
        product_desc=f'Call DeepSeek V4 Pro ({s}) through AnyAIGC: OpenAI-compatible /v1/chat/completions, 1M context, per-token billing, one rate all day, no concurrency cap.',
        offers=offers(s),
        hero=dict(announce='DeepSeek will keep serving the V4 Pro API after September 14, with billing unchanged',
                  eyebrow=f'DeepSeek · {s}',
                  h1='DeepSeek V4 <span class="d-blue">Pro</span><span class="o-sr"> API</span>',
                  lead='The DeepSeek V4 flagship, an MoE with 1.6T total and 49B active parameters. The August GA release added low, high and max reasoning effort for hard coding and agent work.',
                  ask='Track down the memory leak in this service from the terminal and write a fix plus a regression test',
                  think='Ran 6 commands and compared two heap snapshots to find the leak',
                  out=['<code>ps</code> and <code>tracemalloc</code> show <code>RequestCache</code> growing about 40 MB per minute.', 'Cause: the cache is keyed by request objects and never evicts, so they stay referenced.', 'Patch: key by URL, cap with an LRU of 2,048 entries and add a TTL.', 'Regression test <code>test_cache_bounded</code>: 100,000 requests, memory stays under 120 MB. Passed.'],
                  chips=['DeepThink', '1M context', 'Agents'],
                  qs_btn='Quick start',
                  sub=f'<code>{s}</code> costs {p(s, 0)} per 1M input tokens, {p(s, 1)} per 1M output tokens and {p(s, 2)} per 1M cache hits, at one rate all day. It works with OpenAI-compatible clients and Claude Code.',
                  facts=[('Model ID', s), ('Context', '1M tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About the model', h2='The 1.6T-parameter V4 flagship',
                   paras=['DeepSeek released the V4 preview in April 2026 with two models, V4 Pro and V4 Flash, and made a 1M-token context the default. V4 Pro reached general availability on August 13 with three reasoning effort levels: low, high and max.',
                          'V4 Pro is an MoE with 1.6T total and 49B active parameters. It uses a hybrid of Compressed Sparse Attention and Heavily Compressed Attention, was pretrained on 32T tokens, and has open weights under the MIT license. It offers a 1M-token context, up to 384K output tokens, and both thinking and non-thinking modes, with thinking on by default.',
                          f'After V4.1 Flash shipped in September, DeepSeek briefly planned to retire V4 Pro, then said it would keep serving it with billing unchanged. On AnyAIGC, <code>{s}</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint and works directly in Claude Code, at one rate all day with no concurrency cap.'],
                   spec=[('Context window', '1M', 'tokens'), ('Max output', '384K', 'tokens'),
                         ('Parameters', '1.6T', '49B active, MoE'), ('Input', 'Text', 'Text only'),
                         ('Thinking', 'On or off', 'reasoning_effort: low / high / max'), ('Weights', 'Open', 'MIT license')]),
        features=dict(kicker='Capabilities', h2='What DeepSeek V4 Pro can do',
                      items=[('Software engineering', 'At Max effort, DeepSeek reports SWE-bench Verified 80.6 and LiveCodeBench 93.5 for the V4 preview.'),
                             ('Terminal and agents', 'DeepSeek reports Terminal Bench 2.0 at 67.9 and BrowseComp at 83.4 (V4 preview, Max effort).'),
                             ('Science reasoning', 'DeepSeek reports GPQA Diamond 90.1 and HLE 37.7 (V4 preview, Max effort).'),
                             ('Adjustable reasoning', 'The GA release offers low, high and max. Use low on simple tasks to save tokens and max on hard problems.'),
                             ('Tool calls and JSON', 'DeepSeek\'s docs list tool calls and JSON output, so it fits agent frameworks and automation pipelines.'),
                             ('1M context', 'Up to 384K output tokens. A whole repo or long document fits in a single context.')]),
        pricing=dict(kicker='Pricing', h2='DeepSeek V4 Pro API pricing', lead='Per-token billing at one rate all day, with no subscription or monthly fee. About 60% off DeepSeek\'s official peak price.',
                     billing_label='Billing at a glance', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption=f'{s} prices per 1M tokens (USD): AnyAIGC vs. DeepSeek official off-peak and peak',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead='Estimates for common workloads. Struck-through figures are the same usage at DeepSeek\'s official off-peak and peak prices.',
                     costs=[cost_card(s, '20-turn coding agent', 'Each turn: 50K cache-hit tokens + 5,000 input + 3,000 output', 5000, 3000, 50000, 20),
                            cost_card(s, '500K-token codebase review', '500K input tokens + 5,000 output', 500000, 5000),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='DeepSeek V4 Pro official benchmarks', lead='Instruct model results DeepSeek published with the V4 preview (Max reasoning effort), compared with V4 Flash from the same release.',
                   chart=('V4 Pro vs. V4 Flash · official evals', [('V4 Pro · SWE-bench Verified', 80.6, True), ('V4 Flash · SWE-bench Verified', 79.0, False),
                                                                ('V4 Pro · Terminal Bench 2.0', 67.9, True), ('V4 Flash · Terminal Bench 2.0', 56.9, False),
                                                                ('V4 Pro · BrowseComp', 83.4, True), ('V4 Flash · BrowseComp', 73.2, False)]),
                   head=[('Benchmark', ''), ('V4 Pro', 'o-num o-hl'), ('V4 Flash', 'o-num')],
                   rows=V4_ROWS,
                   caption='DeepSeek V4 Pro vs. V4 Flash official benchmarks (V4 preview, Max reasoning effort)',
                   note=f'Source: the <a href="{HF_V4F}" target="_blank" rel="noopener">DeepSeek V4 model card</a>, results from the April 2026 V4 preview. DeepSeek published the August V4 Pro GA results as images only, so they are not listed here.'),
        compare=dict(kicker='Compare', h2='V4 Pro vs. V4.1 Flash vs. V4 Flash', lead='DeepSeek says V4.1 Flash now beats V4 Pro, so try it first on new projects. Workloads already tuned for V4 Pro can stay put.',
                     head=[('Spec', ''), ('V4 Pro', 'o-num o-hl'), ('V4.1 Flash', 'o-num'), ('V4 Flash', 'o-num')],
                     rows=[('Status', '', 'Available', 'Latest', 'Retired by DeepSeek'), ('Context', '', '1M', '1M', '1M'),
                           ('Input', '', 'Text', 'Text, images', 'Text'),
                           ('AnyAIGC input', 'Per 1M tokens', p(s, 0), p(F41, 0), p(F4, 0)),
                           ('AnyAIGC output', 'Per 1M tokens', p(s, 1), p(F41, 1), p(F4, 1)),
                           ('Cache hit', 'Per 1M tokens', p(s, 2), p(F41, 2), p(F4, 2))],
                     caption='DeepSeek V4 Pro, V4.1 Flash and V4 Flash compared; prices are AnyAIGC USD per 1M tokens',
                     note=FACT_SRC + f' See the <a href="/en/models/{F41}">DeepSeek V4.1 Flash API</a> guide.'),
        uses=dict(kicker='Use cases', h2='What DeepSeek V4 Pro is good for',
                  items=[('01 · Large repos', 'Cross-module refactors and migrations', 'Load a whole codebase into the 1M context, let V4 Pro map the dependencies and propose a plan, then execute and verify it step by step with terminal tools.'),
                         ('02 · Coding agents', 'Claude Code and custom agents', 'Run long tasks in Claude Code or your own agent framework: read code, run tests, fix errors. AnyAIGC has no concurrency cap.'),
                         ('03 · Deep reasoning', 'Math, research and analysis', 'Use max effort on hard problems for a full derivation, and low effort for everyday questions to save output tokens.'),
                         ('04 · Stable production', 'Workflows already tuned', 'Teams that have tuned prompts and eval sets for V4 Pro can keep using it. DeepSeek has confirmed it will keep serving the model.')]),
        qs=dict(kicker='Quick start', h2='Get started with the DeepSeek V4 Pro API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=s, prompt='Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', fill(PY, model=s, system='You are a senior backend engineer. Answer with runnable code.', user='Write a Go HTTP client with timeouts and retries.')),
                      ('think', 'Reasoning effort', 'Python · reasoning_effort', fill(THINK, model=s, user='Prove that the square root of 2 is irrational and point out the key step.')),
                      ('tools', 'Tool calls', 'Python · tools', fill(TOOLS, model=s))],
                callout=THINK_CALLOUT, note=QS_NOTE),
        cc=cc('DeepSeek V4 Pro', s, 'Point Claude Code at DeepSeek V4 Pro: edit one config file and your terminal coding agent runs on V4 Pro, billed per token.',
              f'<strong>Save on subtasks:</strong> the config sets <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> to <code>{F41}</code>, so Claude Code sends lightweight subtasks to the cheaper model while the main task stays on V4 Pro.', haiku=F41),
        family_h2='Other DeepSeek models', family_lead='One API key calls every DeepSeek model below. Pick by task and budget.',
        faq_h2='DeepSeek V4 Pro API FAQ', faqs=faqs,
        final=dict(h2='Run DeepSeek V4 Pro at one rate all day', p=f'Sign up, create an API key, and you can use {s} in your code or Claude Code within minutes.', other='DeepSeek V4 Pro API 中文版'),
        ent_name='DeepSeek V4 Pro',
    )


# ======================================================================
# DeepSeek V4 Flash (legacy)
# ======================================================================
def v4f():
    s = F4
    faqs = [
        ('Has DeepSeek V4 Flash been deprecated?',
         f'Yes. DeepSeek retired V4 Flash when it released V4.1 Flash on September 10, 2026. For compatibility, the official API still accepts the <code>{s}</code> model name, serves those requests with V4.1 Flash and bills them at the Flash price. '
         f'For new projects, use <a href="/en/models/{F41}">deepseek-v4.1-flash</a> directly; both cost the same on AnyAIGC.'),
        ('How much does the DeepSeek V4 Flash API cost?',
         f'<code>{s}</code> on AnyAIGC is billed per token: {p(s, 0)} per 1M input tokens, {p(s, 1)} per 1M output tokens and {p(s, 2)} per 1M cache-hit tokens, the same as V4.1 Flash. '
         f'DeepSeek bills the legacy name at the Flash price: off-peak {o(s, "off", 0)} input, {o(s, "off", 1)} output and {o(s, "off", 2)} cache hit, doubled at peak times. Live prices are shown in the model catalog.'),
        faq_peak(f'<code>{s}</code>'),
        ('What do I change to move from V4 Flash to V4.1 Flash?',
         f'Change <code>model</code> in the request body from <code>{s}</code> to <code>{F41}</code>. The endpoint, auth and parameters stay the same. V4.1 Flash adds image input, and DeepSeek says it outperforms V4 Pro on benchmarks.'),
        ('What are V4 Flash\'s parameters and context length?',
         'DeepSeek lists V4 Flash as an MoE with 284B total and 13B active parameters, sharing V4 Pro\'s architecture. It has a 1M-token context, accepts text only, and its weights are open under the MIT license.'),
        faq_cc('DeepSeek V4 Flash', s),
        faq_rpm(f'<code>{s}</code>'),
    ] + faq_common('DeepSeek V4 Flash')
    notice = (f'<strong>DeepSeek has retired V4 Flash.</strong> The official API now serves <code>{s}</code> requests with V4.1 Flash. '
              f'For new projects, use <a href="/en/models/{F41}">DeepSeek V4.1 Flash</a> directly; both cost the same on AnyAIGC.')
    return dict(
        title='DeepSeek V4 Flash API Pricing | Low Cost, No RPM Cap - AnyAIGC',
        desc=f'DeepSeek V4 Flash API: {p(s, 0)} input / {p(s, 1)} output per 1M tokens, 1M context, no rate limits, invoices. Upgraded to V4.1 Flash; see migration notes.',
        og_desc=f'deepseek-v4-flash at {p(s, 0)}/1M input and {p(s, 1)}/1M output, 1M context, OpenAI-compatible, no concurrency cap. DeepSeek has upgraded it to V4.1 Flash; migrate by changing one model name. Invoices and contracts.',
        og_alt='AnyAIGC DeepSeek V4 Flash API: upgraded to V4.1 Flash',
        keywords='DeepSeek V4 Flash API,deepseek-v4-flash,deepseek-v4-flash pricing,DeepSeek V4 Flash deprecated,DeepSeek V4 Flash migration,DeepSeek V4.1 Flash,DeepSeek V4 Flash API for business,DeepSeek API invoice,AnyAIGC',
        crumb='DeepSeek V4 Flash API', product='DeepSeek V4 Flash API (AnyAIGC)', sku=s,
        product_desc=f'Call DeepSeek V4 Flash ({s}) through AnyAIGC: OpenAI-compatible /v1/chat/completions, 1M context, per-token billing, one rate all day, no concurrency cap.',
        offers=offers(s),
        hero=dict(announce=f'DeepSeek has upgraded to V4.1 Flash. Change model to {F41} to migrate',
                  eyebrow=f'DeepSeek · {s}',
                  h1='DeepSeek V4 <span class="d-blue">Flash</span><span class="o-sr"> API</span>',
                  lead='The V4 preview Flash model: 284B total and 13B active parameters, with a 1M context. DeepSeek has replaced it with V4.1 Flash; this page covers pricing and migration.',
                  notice=notice,
                  ask='Sort these 10,000 user feedback messages by issue type and return JSON',
                  think='Read all 10,000 messages in batches and grouped them into 5 issue types',
                  out=['{"total": 10000, "categories": [', '{"type": "payment_failed", "count": 3120},', '{"type": "shipping_delay", "count": 2480},', '{"type": "login_issue", "count": 1960},', '{"type": "feature_request", "count": 1530},', '{"type": "other", "count": 910}]}'],
                  chips=['Low cost', '1M context', 'Tool calls'],
                  qs_btn='Migration example',
                  sub=f'<code>{s}</code> costs {p(s, 0)} per 1M input tokens, {p(s, 1)} per 1M output tokens and {p(s, 2)} per 1M cache hits, the same as V4.1 Flash.',
                  facts=[('Model ID', s), ('Context', '1M tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About the model', h2='The lightweight model from the V4 preview',
                   paras=['DeepSeek released the V4 preview in April 2026 with two models, V4 Pro and V4 Flash. V4 Flash is the lighter one: an MoE with 284B total and 13B active parameters, sharing V4 Pro\'s architecture, with a 1M-token context and open weights under the MIT license.',
                          f'On September 10 DeepSeek released V4.1 Flash and retired V4 Flash. For compatibility, the official API temporarily routes <code>{s}</code> requests to V4.1 Flash and bills them at the Flash price.',
                          f'If your code still says <code>{s}</code>, you can keep calling it on AnyAIGC. For new projects, switch the model name to <code>{F41}</code>: it costs the same and also accepts images.'],
                   spec=[('Context window', '1M', 'tokens'), ('Parameters', '284B', '13B active, MoE'),
                         ('Input', 'Text', 'Text only'), ('Thinking', 'Three modes', 'Non-think / Think High / Think Max'),
                         ('Weights', 'Open', 'MIT license'), ('Official status', 'Retired', f'Replaced by {F41}')]),
        features=dict(kicker='Capabilities', h2='What DeepSeek V4 Flash can do',
                      items=[('Software engineering', 'At Max effort, DeepSeek reports SWE-bench Verified 79.0 and LiveCodeBench 91.6 for the V4 preview.'),
                             ('Science reasoning', 'DeepSeek reports GPQA Diamond 88.1 and HLE 34.8 (Max effort).'),
                             ('Web browsing agents', 'DeepSeek reports BrowseComp 73.2 and Terminal Bench 2.0 at 56.9 (Max effort).'),
                             ('Three thinking modes', 'DeepSeek lists Non-think, Think High and Think Max.'),
                             ('1M context', 'Long documents and large repos fit in a single context.'),
                             ('Easy migration', f'Change only the model field to move to {F41}. Endpoint, auth and parameters stay the same.')]),
        pricing=dict(kicker='Pricing', h2='DeepSeek V4 Flash API pricing', lead='Per-token billing at one rate all day, the same as V4.1 Flash. DeepSeek bills the legacy name at the Flash price, shown below for comparison.',
                     billing_label='Billing at a glance', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption=f'{s} prices per 1M tokens (USD): AnyAIGC vs. DeepSeek official off-peak and peak',
                     note=pricing_note(s) + ' The official price is the Flash price DeepSeek charges after routing the legacy name to V4.1 Flash.',
                     costs_h3='Cost examples', costs_lead='Estimates for common workloads. Struck-through figures are the same usage at DeepSeek\'s official off-peak and peak prices.',
                     costs=[cost_card(s, '10,000 ticket labels', 'Each: 2,000 input tokens + 300 output', 2000, 300, 0, 10000),
                            cost_card(s, '50-turn coding agent', 'Each turn: 60K cache-hit tokens + 4,000 input + 2,000 output', 4000, 2000, 60000, 50),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='DeepSeek V4 Flash official benchmarks', lead='Instruct model results DeepSeek published with the V4 preview (Max reasoning effort), compared with V4 Pro from the same release.',
                   chart=('V4 Flash vs. V4 Pro · official evals', [('V4 Flash · SWE-bench Verified', 79.0, True), ('V4 Pro · SWE-bench Verified', 80.6, False),
                                                                ('V4 Flash · LiveCodeBench', 91.6, True), ('V4 Pro · LiveCodeBench', 93.5, False),
                                                                ('V4 Flash · GPQA Diamond', 88.1, True), ('V4 Pro · GPQA Diamond', 90.1, False)]),
                   head=[('Benchmark', ''), ('V4 Flash', 'o-num o-hl'), ('V4 Pro', 'o-num')],
                   rows=[(a, b, y, x) for a, b, x, y in V4_ROWS],
                   caption='DeepSeek V4 Flash vs. V4 Pro official benchmarks (V4 preview, Max reasoning effort)',
                   note=f'Source: the <a href="{HF_V4F}" target="_blank" rel="noopener">DeepSeek-V4-Flash model card</a>, results as published by DeepSeek.'),
        compare=dict(kicker='Compare', h2='V4 Flash vs. V4.1 Flash vs. V4 Pro', lead='DeepSeek has replaced V4 Flash. Start new projects on V4.1 Flash, which costs the same.',
                     head=[('Spec', ''), ('V4 Flash', 'o-num o-hl'), ('V4.1 Flash', 'o-num'), ('V4 Pro', 'o-num')],
                     rows=[('Status', '', 'Retired by DeepSeek', 'Latest', 'Available'), ('Context', '', '1M', '1M', '1M'),
                           ('Input', '', 'Text', 'Text, images', 'Text'),
                           ('AnyAIGC input', 'Per 1M tokens', p(s, 0), p(F41, 0), p(PRO, 0)),
                           ('AnyAIGC output', 'Per 1M tokens', p(s, 1), p(F41, 1), p(PRO, 1)),
                           ('Cache hit', 'Per 1M tokens', p(s, 2), p(F41, 2), p(PRO, 2))],
                     caption='DeepSeek V4 Flash, V4.1 Flash and V4 Pro compared; prices are AnyAIGC USD per 1M tokens',
                     note=FACT_SRC + f' See the <a href="/en/models/{F41}">DeepSeek V4.1 Flash API</a> guide.'),
        uses=dict(kicker='Use cases', h2='Where V4 Flash is still in use',
                  items=[('01 · Existing code', 'Keep it running as is', f'Scripts and services that hard-code <code>{s}</code> keep working and are billed at the same rate.'),
                         ('02 · Batch jobs', 'Classification, extraction, summaries', 'Ticket triage, field extraction and review tagging. Low unit price, one rate all day, no concurrency cap.'),
                         ('03 · Staged migration', 'Compare old and new', f'Run the same samples through <code>{s}</code> and <code>{F41}</code>, compare outputs, then switch over.'),
                         ('04 · Coding agents', 'Everyday coding in Claude Code', f'Use it for everyday coding in Claude Code. For better results, switch the model to <code>{F41}</code>.')]),
        qs=dict(kicker='Quick start', h2='Get started with the DeepSeek V4 Flash API', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', fill(CURL, model=s, prompt='Explain what a MoE model is in three sentences.')),
                      ('migrate', 'Migrate to V4.1 Flash', 'Python · change model only', fill(PY, model=F41, system='You are a senior backend engineer. Answer with runnable code.', user='Write a Go HTTP client with timeouts and retries.')),
                      ('stream', 'Streaming', 'Python · stream=True', fill(STREAM, model=s, user='Write 5 changelog entries for a SaaS product.')),
                      ('tools', 'Tool calls', 'Python · tools', fill(TOOLS, model=s))],
                callout=f'<strong>Migration tip:</strong> moving from <code>{s}</code> to <code>{F41}</code> only means changing the <code>model</code> field. Parameters, endpoint and auth stay the same, and so does the price.',
                note=QS_NOTE),
        cc=cc('DeepSeek V4 Flash', s, f'Claude Code works with V4 Flash, but we recommend configuring <code>{F41}</code> instead. Just swap the model name in the config below.',
              f'<strong>Recommended:</strong> replace every <code>{s}</code> in the config with <code>{F41}</code>. Same price, better results.'),
        family_h2='Other DeepSeek models', family_lead='One API key calls every DeepSeek model below. Pick by task and budget.',
        faq_h2='DeepSeek V4 Flash API FAQ', faqs=faqs,
        final=dict(h2='Change one model name to upgrade to V4.1 Flash', p=f'Sign up, create an API key, and use either {s} or {F41} at the same price.', other='DeepSeek V4 Flash API 中文版'),
        ent_name='DeepSeek V4 Flash',
    )
