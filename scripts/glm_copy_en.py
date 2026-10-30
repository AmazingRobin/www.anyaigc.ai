# English copy for the GLM topic pages. Used by scripts/glm_pages.py.
# Prices come from glm_data.PRICE (model catalog); official prices and specs from docs.z.ai, the z.ai tech blog and Hugging Face model cards (read 2026-10-30).
from glm_data import PRICE, OFFICIAL, REG, PRICING, SUPPORT, DOCS_CHAT, DOCS_CC, OFFICIAL_PRICING
from glm_layout import cost, money

UNIT = '1M tokens'
B53 = 'https://z.ai/blog/glm-5.3'
B52 = 'https://z.ai/blog/glm-5.2'
BF = 'https://z.ai/blog/glm-5.3-flash'


def p(slug, i):
    return f'${PRICE[slug][i]}'


def o(slug, i):
    return f'${OFFICIAL[slug][i]}'


# Discounts: glm-5.3 / glm-5.2 input and output are 67.5% of official (about 30% off); glm-5.3-flash is 40.5% (about 60% off)
OFF = {'glm-5.3': 'About 30% off', 'glm-5.2': 'About 30% off', 'glm-5.3-flash': 'About 60% off'}
PCT = {'glm-5.3': '67.5%', 'glm-5.2': '67.5%', 'glm-5.3-flash': '40.5%'}


# ---------------- Shared FAQ ----------------
def faq_common(name, slug):
    return [
        (f'Can I call the {name} API from mainland China?',
         f'Yes. AnyAIGC is optimized for access from mainland China, so you can usually call <code>https://anyaigc.ai</code> without a proxy. Usage is billed in USD, and you can pay with WeChat Pay, Alipay, USDT or a credit card. Companies can pay by bank transfer and get VAT invoices.'),
        (f'How do I get a {name} API key?',
         f'Sign up at <a href="{REG}">anyaigc.ai</a>, add credit, and create a key in the console. The same key works for every GLM model and 300+ other models on the platform, so you do not need a separate Zhipu platform account or a GLM Coding Plan.'),
        ('Can AnyAIGC issue invoices, including VAT special invoices?',
         'Yes. AnyAIGC issues invoices for every top-up based on the amount you actually paid, including Chinese VAT general invoices and VAT special invoices. Send your billing details to support to get one.'),
        ('Can my company pay by bank transfer and sign a contract?',
         f'Yes. Companies can top up by corporate bank transfer and sign a service agreement with AnyAIGC, with a dedicated support and technical contact. For procurement, <a href="{SUPPORT}">contact AnyAIGC support</a>.'),
        ('Will my data be used for training?',
         'No. Except where required by law, AnyAIGC does not persistently store your prompts or outputs and does not use them to train models. Requests are encrypted over HTTPS. See the AnyAIGC <a href="/privacy">Privacy Policy</a>. The model\'s own data policy is governed by Zhipu AI\'s official terms.'),
    ]


def faq_cc(name, model):
    return (f'Can I use {name} in Claude Code?',
            f'Yes. In the env block of <code>~/.claude/settings.json</code>, set <code>ANTHROPIC_BASE_URL</code> to <code>https://anyaigc.ai</code>, <code>ANTHROPIC_AUTH_TOKEN</code> to your API key, and <code>ANTHROPIC_MODEL</code> to <code>{model}</code>. Then run <code>claude</code>. You pay per token, with no 5-hour quota window like a subscription plan.')


def faq_rpm(name, slug):
    return ('Are there concurrency or rate limits?',
            f'AnyAIGC does not cap concurrency for <code>{slug}</code>, and every user gets this by default. That suits batch jobs, CI pipelines and parallel agents. Billing is per token, so there is no quota that resets on a time window like a subscription plan.')


# ---------------- Code samples ----------------
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
print(getattr(msg, "reasoning_content", None))  # reasoning trace, if any
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
    # reasoning_content deltas (if any) arrive first, then the final answer in content
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
        "description": "Run the unit tests at a path in the repo and return the failing cases",
        "parameters": {{
            "type": "object",
            "properties": {{"path": {{"type": "string", "description": "Test file or directory"}}}},
            "required": ["path"],
        }},
    }},
}}]
messages = [{{"role": "user", "content": "Run tests/test_api.py and tell me which cases fail."}}]

resp = client.chat.completions.create(model="{model}", messages=messages, tools=tools)
msg = resp.choices[0].message
# In multi-turn and tool calls, send the full assistant message (incl. reasoning_content and tool_calls) back unchanged
messages.append(msg.model_dump(exclude_none=True))
for call in msg.tool_calls or []:
    args = json.loads(call.function.arguments)
    result = {{"path": args["path"], "failed": ["test_login_timeout"]}}  # replace with the real result
    messages.append({{"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)}})

final = client.chat.completions.create(model="{model}", messages=messages, tools=tools)
print(final.choices[0].message.content)'''


def code_vision(model):
    return f'''import base64
import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# Encode a local image as a Base64 data URL; a public image URL works too
b64 = base64.b64encode(Path("design.png").read_bytes()).decode()

resp = client.chat.completions.create(
    model="{model}",
    messages=[{{
        "role": "user",
        "content": [
            {{"type": "image_url", "image_url": {{"url": f"data:image/png;base64,{{b64}}"}}}},
            {{"type": "text", "text": "Build a responsive HTML + CSS page from this design."}},
        ],
    }}],
)
print(resp.choices[0].message.content)'''


def code_effort(model):
    return f'''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# reasoning_effort sets thinking depth: low / high / max (default max; Zhipu recommends max for coding)
resp = client.chat.completions.create(
    model="{model}",
    reasoning_effort="low",
    messages=[{{"role": "user", "content": "Rewrite this SQL to use window functions: SELECT ..."}}],
)
print(resp.choices[0].message.content)'''


def cc_code(model, haiku=None):
    return f'''{{
  "env": {{
    "ANTHROPIC_BASE_URL": "https://anyaigc.ai",
    "ANTHROPIC_AUTH_TOKEN": "sk-your-API-key",
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
        kicker='Claude Code', h2=f'Use {name} in Claude Code', lead=lead,
        steps=['<strong>Install Claude Code</strong>: use the official installer, for example <code>curl -fsSL https://claude.ai/install.sh | bash</code> on macOS or Linux.',
               '<strong>Add the config</strong>: edit <code>~/.claude/settings.json</code>, add the env block below, and replace <code>ANTHROPIC_AUTH_TOKEN</code> with the key you created on AnyAIGC.',
               f'<strong>Start coding</strong>: run <code>claude</code> in your project folder. Type <code>/model</code> to confirm the current model is <code>{model}</code>.'],
        code=cc_code(model, haiku), callout=callout,
        note=f'For the full walkthrough and common errors, see the <a href="{DOCS_CC}" target="_blank" rel="noopener">Claude Code setup guide</a>. Swap the model name in the guide for <code>{model}</code>.')


def qs_steps(model):
    return ['<strong>Sign up and add credit</strong>: create an account at <a href="' + REG + '">anyaigc.ai</a>. Top up from $1; your balance works across every model on the platform.',
            '<strong>Create an API key</strong>: create a key in the console, copy the value that starts with <code>sk-</code>, and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Send a request</strong>: call <code>POST https://anyaigc.ai/v1/chat/completions</code> with <code>model</code> set to <code>{model}</code> and an <code>Authorization: Bearer</code> header. With the OpenAI SDK, just set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>.']


QS_NOTE = f'See the <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions reference</a> for every parameter. Replace the model name in the docs examples with the GLM model ID you want.'

PRICE_HEAD = [('Item', ''), ('Model', ''), ('AnyAIGC', 'o-num o-hl'), ('Zhipu official', 'o-num'), ('Savings', 'o-num')]
LABELS = [('Input', 'per 1M tokens'), ('Output', 'per 1M tokens, incl. thinking'), ('Cache hit', 'per 1M tokens')]
COSTS_LEAD = 'Estimates for common workloads. The struck-through figure is the same usage at Zhipu official prices.'


def pricing_note(slug):
    q = f'?keyword={slug}' if slug else '?keyword=glm'
    return (f'Prices are in USD and billed on the tokens you actually use. Output includes thinking tokens, and repeated prompt prefixes are billed at the cache-hit rate automatically. '
            f'Official prices come from the <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">Zhipu Z.ai pricing page</a> (USD). '
            f'The table shows the lowest price in the model catalog; see the <a href="{PRICING}{q}">AnyAIGC model catalog</a> for live pricing.')


def cost_card(slug, title, calc, inp=0, out=0, cache=0, n=1):
    a = money(cost(slug, inp, out, cache, n))
    b = money(cost(slug, inp, out, cache, n, official=True))
    return (title, calc, a, f'Official <s>{b}</s>')


def offers(slug):
    return [('Input (per 1M tokens)', PRICE[slug][0]), ('Output (per 1M tokens)', PRICE[slug][1]),
            ('Cache hit (per 1M tokens)', PRICE[slug][2])]


def billing(slug_off):
    return [('Per token', 'Input, output and cache priced separately'), (slug_off, 'vs Zhipu official USD prices'),
            ('Unlimited concurrency', 'On by default for every user'), ('USD', 'One balance for 300+ models')]


FAMILY = [
    ('glm', '', ('GLM overview', 'GLM-5.3, GLM-5.3-Flash and GLM-5.2 pricing compared')),
    ('glm-5.3', 'Latest', f'Zhipu flagship for coding and agents, 1M context · input {p("glm-5.3", 0)} / 1M'),
    ('glm-5.3-flash', 'Low cost', f'Native multimodal, 320B total / 18B active · input {p("glm-5.3-flash", 0)} / 1M'),
    ('glm-5.2', '', f'Long-horizon flagship, thinking optional · input {p("glm-5.2", 0)} / 1M'),
]

FAMILY_LEAD = 'One API key calls every GLM model below. Pick by task difficulty and budget.'


def build(slug):
    return {'glm': hub, 'glm-5.3': g53, 'glm-5.3-flash': gf, 'glm-5.2': g52}[slug]()


# ======================================================================
# Overview
# ======================================================================
def hub():
    a, f, b = 'glm-5.3', 'glm-5.3-flash', 'glm-5.2'
    faqs = [
        ('How much does the GLM API cost?',
         f'GLM models on AnyAIGC are billed per token. Per 1M tokens: <code>glm-5.3</code> input {p(a, 0)}, output {p(a, 1)}, cache hit {p(a, 2)}; <code>glm-5.3-flash</code> input {p(f, 0)}, output {p(f, 1)}, cache hit {p(f, 2)}; '
         f'<code>glm-5.2</code> input {p(b, 0)}, output {p(b, 1)}, cache hit {p(b, 2)}. GLM-5.3 and GLM-5.2 are about 30% off Zhipu\'s official USD prices, and GLM-5.3-Flash is about 60% off. See the model catalog for live pricing.'),
        ('Which GLM models are on AnyAIGC, and what are the model IDs?',
         'This page covers three: <code>glm-5.3</code> (Zhipu\'s latest flagship, for complex coding and agents), <code>glm-5.3-flash</code> (the first natively multimodal GLM-5 model, at a low price) and <code>glm-5.2</code> (the previous flagship, built for long-horizon tasks). '
         'Put the model ID in the <code>model</code> field of the request body. Switching models only means changing that one field. Older models such as GLM-5.1, GLM-5 and GLM-4.5 are also on the platform; see the model catalog.'),
        ('GLM-5.3, GLM-5.3-Flash or GLM-5.2: which should I use?',
         f'Pick <a href="/en/models/glm-5.3">GLM-5.3</a> for the hardest coding, terminal and agent work. Pick <a href="/en/models/glm-5.3-flash">GLM-5.3-Flash</a> for high-volume, budget-sensitive or image tasks; it costs about 1/15 of GLM-5.3, and Zhipu says it beats GLM-5.2 overall. '
         f'Stay on <a href="/en/models/glm-5.2">GLM-5.2</a> if you need to turn thinking off or already run it in production. GLM-5.3 and GLM-5.2 cost the same, so new projects should start with GLM-5.3.'),
        ('Is the GLM API OpenAI compatible?',
         'Yes. All three models use <code>POST https://anyaigc.ai/v1/chat/completions</code> with the same request and response format as OpenAI Chat Completions. With the official OpenAI SDK, set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>. The reasoning trace, if any, comes back in the <code>reasoning_content</code> field.'),
        faq_cc('GLM', 'glm-5.3'),
        ('How large is the context window?',
         'According to Zhipu, GLM-5.3, GLM-5.3-Flash and GLM-5.2 all support a 1M-token context and up to 128K output tokens. GLM-5.3 and GLM-5.2 accept text only; GLM-5.3-Flash also accepts images.'),
        ('How is this different from the GLM Coding Plan?',
         'The GLM Coding Plan is Zhipu\'s monthly coding subscription, with quotas that reset on 5-hour and weekly windows. AnyAIGC is a pay-per-token API: you pay for what you use, top up from $1, with no time windows and unlimited concurrency, and the same key calls 300+ other models.'),
        ('Are GLM models open source? Can I use them commercially?',
         'Zhipu has published the weights for GLM-5.3, GLM-5.3-Flash and GLM-5.2 on Hugging Face. GLM-5.2 and GLM-5.3-Flash use the MIT license; GLM-5.3 uses the GLM-5.3 License, a permissive license with an extra security review clause for very large MaaS companies. Calling the API through AnyAIGC means you do not have to host them yourself. Model licenses and commercial use are governed by Zhipu AI\'s official terms.'),
        faq_rpm('GLM', 'glm-5.3, glm-5.3-flash, glm-5.2'),
    ] + faq_common('GLM', 'glm')
    faqs[8] = ('Are there concurrency or rate limits?',
               'AnyAIGC does not cap concurrency for GLM models, and every user gets this by default. That suits batch jobs, CI pipelines and parallel agents. Billing is per token, so there is no quota that resets on a time window like a subscription plan.')
    return dict(
        title='GLM API Pricing & Access | GLM-5.3, 5.3-Flash, 5.2 - AnyAIGC',
        desc=f'Zhipu GLM API: GLM-5.3, 5.3-Flash and 5.2 on one key from {p(f, 0)}/1M input, 1M context, 30–60% off official. Works in Claude Code, bank transfer, invoices.',
        og_desc='Call GLM-5.3, GLM-5.3-Flash and GLM-5.2 with one key at 30–60% off Zhipu official prices. OpenAI-compatible API, works in Claude Code, unlimited concurrency, bank transfer and VAT invoices.',
        og_alt='AnyAIGC GLM API: GLM-5.3, GLM-5.3-Flash and GLM-5.2 at 30–60% off official prices',
        keywords='GLM API,Zhipu API,Zhipu GLM API,GLM API pricing,GLM API key,GLM-5.3 API,GLM-5.3-Flash API,GLM-5.2 API,GLM Claude Code,GLM Coding Plan alternative,Z.ai API,GLM API for business,GLM API invoice,AnyAIGC',
        crumb='GLM API', product='GLM API (AnyAIGC)', sku='glm',
        product_desc='Zhipu GLM models (glm-5.3, glm-5.3-flash, glm-5.2) through AnyAIGC: OpenAI-compatible /v1/chat/completions, per-token billing at 30–60% off official prices, unlimited concurrency.',
        offers=[(f'{n} input (per 1M tokens)', PRICE[s][0]) for s, n in ((a, 'GLM-5.3'), (f, 'GLM-5.3-Flash'), (b, 'GLM-5.2'))]
        + [(f'{n} output (per 1M tokens)', PRICE[s][1]) for s, n in ((a, 'GLM-5.3'), (f, 'GLM-5.3-Flash'), (b, 'GLM-5.2'))],
        hero=dict(eyebrow='Zhipu Z.ai · GLM',
                  h1='GLM <span class="g-blue">API</span>',
                  lead='Zhipu\'s GLM-5.3, GLM-5.3-Flash and GLM-5.2 on one API key. GLM-5.3 is about 30% off the official price, and GLM-5.3-Flash about 60% off.',
                  ask='Use GLM to read this repo, fix the failing tests and add the missing type definitions',
                  chips=['Complex coding', '1M context', 'Agents'],
                  sub=f'OpenAI-compatible <code>/v1/chat/completions</code> that also plugs into Claude Code. <code>glm-5.3-flash</code> starts at {p(f, 0)} per 1M input tokens, with unlimited concurrency.',
                  facts=[('Models', 'GLM-5.3 · 5.3-Flash · 5.2'), ('Context', '1M'), ('Input', f'From {p(f, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        models=dict(kicker='Models', h2='Three GLM models', lead='Same key, same endpoint. Change the model ID to match the task.',
                    unit_in='1M input', unit_out='1M output', go='View guide',
                    items=[(a, 'Latest', 'Zhipu\'s latest flagship. It shares GLM-5.2\'s base model, and scaled-up post-training lifts complex coding, terminal tasks and agent work across the board.', ['1M context, up to 128K output', 'Zhipu reports 50% higher Z.ai Code Bench than 5.2', 'Always thinks, adjustable reasoning_effort']),
                           (f, 'Low cost', 'The first natively multimodal GLM-5 model, with 320B total and 18B active parameters. Zhipu says it beats GLM-5.2 overall at about a tenth of the price.', ['1M context, image input', 'Toolathlon Verified 78.4', 'About 1/15 the price of GLM-5.3']),
                           (b, '', 'The previous flagship, built for long-horizon tasks. Its 1M context is usable in practice, and it can take one task from requirements to multi-platform deployment.', ['1M context, up to 128K output', 'Thinking on or off', 'MIT open-source license'])]),
        pricing=dict(kicker='Pricing', h2='GLM API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. GLM-5.3 and GLM-5.2 are about 30% off Zhipu\'s official USD prices, and GLM-5.3-Flash about 60% off.',
                     billing_label='Billing basics',
                     billing=billing('30–60% off'),
                     head=[('Item', ''), ('AnyAIGC', 'o-num o-hl'), ('Zhipu official', 'o-num'), ('Savings', 'o-num')],
                     labels=LABELS, caption='GLM prices per 1M tokens (USD), AnyAIGC vs Zhipu official',
                     note=pricing_note(''),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(a, 'GLM-5.3 · 20 agent coding turns', 'Each turn: 50K cache-hit tokens + 5,000 input + 3,000 output', 5000, 3000, 50000, 20),
                            cost_card(f, 'GLM-5.3-Flash · classify 10,000 tickets', 'Each ticket: 2,000 input tokens + 300 output', 2000, 300, 0, 10000),
                            cost_card(b, 'GLM-5.2 · review 100 PRs', 'Each PR: 20K input tokens + 2,000 output', 20000, 2000, 0, 100)]),
        compare=dict(kicker='Compare', h2='GLM-5.3 vs GLM-5.3-Flash vs GLM-5.2', lead='Send the hardest work to GLM-5.3, high-volume and image tasks to GLM-5.3-Flash, and use GLM-5.2 when thinking should be off.',
                     head=[('Spec', ''), ('GLM-5.3', 'o-num o-hl'), ('GLM-5.3-Flash', 'o-num'), ('GLM-5.2', 'o-num')],
                     rows=[('Role', '', 'Latest flagship', 'Native multimodal, low cost', 'Long-horizon flagship'),
                           ('Context / max output', '', '1M / 128K', '1M / 128K', '1M / 128K'),
                           ('Input', '', 'Text', 'Text, images', 'Text'),
                           ('Thinking', '', 'Always on', 'Always on', 'On or off'),
                           ('AnyAIGC input', 'per 1M tokens', p(a, 0), p(f, 0), p(b, 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(a, 1), p(f, 1), p(b, 1)),
                           ('Cache hit', 'per 1M tokens', p(a, 2), p(f, 2), p(b, 2))],
                     caption='GLM-5.3, GLM-5.3-Flash and GLM-5.2 compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Zhipu Z.ai\'s official docs. Prices are current AnyAIGC prices; see the model catalog for live pricing.'),
        uses=dict(kicker='Use cases', h2='What teams build with the GLM API',
                  items=[('01 · Complex coding', 'Large refactors and terminal tasks', 'GLM-5.3\'s 1M context holds a whole codebase and keeps working through terminal tools. Zhipu reports 88.2 on Terminal Bench 2.1.'),
                         ('02 · Coding agents', 'Claude Code, CI and auto-fix', 'Plug GLM into Claude Code or your own agent framework to run tests, read errors and patch code. AnyAIGC does not cap concurrency, so many agents can run at once.'),
                         ('03 · Design to code', 'Screenshots to UI', 'GLM-5.3-Flash reads images. Hand over a design file or page screenshot and get HTML, CSS or component code back.'),
                         ('04 · Batch jobs', 'Classification, extraction and summaries', 'GLM-5.3-Flash costs ' + p(f, 0) + ' per 1M input tokens, which suits high-volume work like ticket triage, field extraction and long-document summaries.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the GLM API in three steps', steps=qs_steps('glm-5.3'),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl('glm-5.3', 'Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py('glm-5.3', 'You are a senior backend engineer. Answer with runnable code.', 'Write an HTTP client in Go with timeouts and retries.')),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream('glm-5.3-flash', 'Write 5 changelog entries for a SaaS product.'))],
                callout='<strong>Tip:</strong> GLM returns its reasoning in the <code>reasoning_content</code> field. When streaming, reasoning deltas arrive first, then the final answer. Set thinking depth with <code>reasoning_effort</code> (<code>low</code> / <code>high</code> / <code>max</code>, default <code>max</code>). In multi-turn chats and tool calls, send the full assistant message from the API (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.',
                note=QS_NOTE),
        cc=cc('GLM', 'glm-5.3', 'Switch Claude Code to GLM by editing one config file, and the coding agent in your terminal runs on GLM-5.3, billed per token.',
              '<strong>Save on light tasks:</strong> the config sets <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> to <code>glm-5.3-flash</code>, so Claude Code\'s lightweight subtasks use the cheaper model while the main work stays on GLM-5.3.', haiku='glm-5.3-flash'),
        family_h2='All GLM models', family_lead=FAMILY_LEAD,
        faq_h2='GLM API FAQ', faqs=faqs,
        final=dict(h2='Run GLM at about 30% off the official price', p='Sign up, create an API key, and you can use GLM-5.3, GLM-5.3-Flash and GLM-5.2 in your code or Claude Code within minutes.',
                   other='GLM API 中文版'),
        ent_name='GLM',
    )


# ======================================================================
# GLM-5.3
# ======================================================================
def g53():
    s = 'glm-5.3'
    faqs = [
        ('How much does the GLM-5.3 API cost?',
         f'On AnyAIGC, <code>glm-5.3</code> is billed per token: input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)} per 1M tokens. '
         f'Zhipu\'s official USD prices are input {o(s, 0)}, output {o(s, 1)} and cache hit {o(s, 2)}, so AnyAIGC input and output cost about 67.5% of official (about 30% off). Output includes thinking tokens. See the model catalog for live pricing.'),
        ('What is the GLM-5.3 model ID, and how large is the context?',
         'The model ID is <code>glm-5.3</code>. Zhipu lists a 1M-token context window and up to 128K output tokens. It currently accepts text input only.'),
        ('How is GLM-5.3 different from GLM-5.2?',
         f'Zhipu says GLM-5.3 uses the same base model as <a href="/en/models/glm-5.2">GLM-5.2</a>, and every gain comes from scaled-up post-training. Reported changes: Z.ai Code Bench is 50% higher than GLM-5.2, Terminal Bench 3.0 rose from 4.6 to 28.3, and DeepSWE rose from 46.2 to 66.9. '
         f'GLM-5.3 also always thinks and thinking cannot be turned off. On AnyAIGC both cost the same for input and output, and GLM-5.3 has a lower cache-hit price ({p(s, 2)} vs {p("glm-5.2", 2)}).'),
        ('How do I adjust GLM-5.3\'s thinking depth? Can I turn thinking off?',
         'GLM-5.3 always thinks, and Zhipu does not support turning it off. Use the <code>reasoning_effort</code> field in the request body to set depth: <code>low</code>, <code>high</code> or <code>max</code> (default <code>max</code>, which Zhipu recommends for coding). Use <code>low</code> on simple tasks to cut output tokens.'),
        ('Does GLM-5.3 support tool calls and structured output?',
         'Yes. Zhipu\'s docs list function calling, structured output (JSON), streaming and context caching. In multi-turn chats and tool calls, send the full assistant message (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.'),
        faq_cc('GLM-5.3', s),
        ('Is GLM-5.3 open source?',
         'Yes. Zhipu has published the GLM-5.3 weights on Hugging Face (zai-org/GLM-5.3) under the GLM-5.3 License. It is a permissive license overall, with one extra rule: companies with annual revenue above $10 billion that run model-as-a-service businesses must pass a Z.ai security review before commercial use. Calling the API through AnyAIGC means you do not have to host it yourself. Commercial use is governed by Zhipu AI\'s official terms.'),
        faq_rpm('GLM-5.3', s),
    ] + faq_common('GLM-5.3', s)
    return dict(
        title='GLM-5.3 API Pricing & Access | 1M Context, ~30% Off - AnyAIGC',
        desc=f'glm-5.3 API: Zhipu\'s latest flagship for coding and agents, 1M context. Input {p(s, 0)}/1M, output {p(s, 1)}/1M, about 30% off. Bank transfer, invoices.',
        og_desc=f'glm-5.3 at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 30% off Zhipu official prices. Zhipu\'s latest flagship with 1M context; Zhipu reports 50% better coding than GLM-5.2. Works in Claude Code, with bank transfer and VAT invoices.',
        og_alt='AnyAIGC GLM-5.3 API at about 30% off official prices',
        keywords='GLM-5.3 API,glm-5.3,GLM-5.3 API pricing,GLM-5.3 API key,GLM-5.3 Claude Code,GLM-5.3 1M context,GLM-5.3 vs GLM-5.2,Zhipu GLM-5.3,Zhipu API,GLM API,GLM-5.3 API for business,GLM-5.3 API invoice,AnyAIGC',
        crumb='GLM-5.3 API', product='GLM-5.3 API (AnyAIGC)', sku=s,
        product_desc='Zhipu GLM-5.3 (glm-5.3) through AnyAIGC: OpenAI-compatible /v1/chat/completions, 1M context, per-token billing at about 30% off official prices, unlimited concurrency.',
        offers=offers(s),
        hero=dict(eyebrow='Zhipu Z.ai · glm-5.3',
                  h1='GLM-<span class="g-blue">5.3</span><span class="o-sr"> API</span>',
                  lead='Zhipu\'s latest flagship, a step up in complex software engineering and agent work. It shares GLM-5.2\'s base model, and scaled-up post-training pushes coding further. On AnyAIGC it costs about 30% less than the official price.',
                  ask='Track down the memory leak in this service from the terminal, then write a fix and a regression test',
                  chips=['Terminal coding', '1M context', 'Agents'],
                  sub=f'<code>glm-5.3</code> input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)}. Works with the OpenAI-compatible API and in Claude Code.',
                  facts=[('Model ID', s), ('Context', '1M tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About', h2='Same base model, much stronger post-training',
                   paras=['Zhipu calls GLM-5.3 its latest flagship, with across-the-board gains in complex software engineering and agent tasks. Zhipu says it uses the same base model as GLM-5.2, and every improvement comes from scaled-up post-training that builds on the reinforcement learning approach introduced with GLM-5.2.',
                          'The reported gains center on coding and agents: Zhipu\'s internal Z.ai Code Bench is 50% higher than GLM-5.2 while using fewer output tokens on the same tasks, and Terminal Bench 3.0 rose from 4.6 to 28.3. Zhipu also reports state-of-the-art results on the CyberGym vulnerability benchmark. It has a 1M-token context, up to 128K output, and thinking is always on.',
                          'On AnyAIGC, <code>glm-5.3</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint and works directly in Claude Code. No Zhipu platform account or Coding Plan needed: you pay per token, with unlimited concurrency.'],
                   spec=[('Context window', '1M', 'tokens'), ('Max output', '128K', 'tokens'),
                         ('Architecture', 'MoE + DSA', 'Sparse attention, same base as GLM-5.2'), ('Input', 'Text', 'Text only'),
                         ('Thinking', 'Always on', 'reasoning_effort: low / high / max'), ('Weights', 'Open', 'Hugging Face zai-org/GLM-5.3')]),
        features=dict(kicker='Capabilities', h2='What GLM-5.3 can do',
                      items=[('Terminal and long-horizon coding', 'Zhipu reports 88.2 on Terminal Bench 2.1 and 28.3 on Terminal Bench 3.0 (GLM-5.2: 4.6), for long engineering tasks that run in the terminal.'),
                             ('Software engineering', 'Zhipu reports 66.9 on DeepSWE v1.1, 78.1 on FrontierSWE and 58 on NL2Repo, from fixing bugs to building a repo from scratch.'),
                             ('Coding with fewer tokens', 'On Zhipu\'s internal Z.ai Code Bench at max effort, GLM-5.3 scores 34.5% with about 75K output tokens on average; GLM-5.2 scores 23.4% with about 96K.'),
                             ('Security research', 'Zhipu reports 84.5 on the CyberGym vulnerability reproduction benchmark, and says GLM-5.3 found 2,436 vulnerabilities across 269 open-source projects.'),
                             ('Agents and tool calls', 'Zhipu reports 73 on Toolathlon Verified, 48.2 on AutomationBench and 28.5 on Agents\' Last Exam, with function calling and structured output.'),
                             ('Adjustable thinking depth', 'Thinking is always on. Set reasoning_effort to low, high or max: save tokens on simple tasks and use max for hard problems.')]),
        pricing=dict(kicker='Pricing', h2='GLM-5.3 API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. Input and output cost about 67.5% of Zhipu\'s official USD prices (about 30% off).',
                     billing_label='Billing basics',
                     billing=billing(OFF[s]),
                     head=PRICE_HEAD, labels=LABELS, caption='glm-5.3 prices per 1M tokens (USD), AnyAIGC vs Zhipu official',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(s, '20 agent coding turns', 'Each turn: 50K cache-hit tokens + 5,000 input + 3,000 output', 5000, 3000, 50000, 20),
                            cost_card(s, 'Analyze a 500K-token codebase', '500K input tokens + 5,000 output', 500000, 5000),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='GLM-5.3 official benchmarks', lead='Scores Zhipu published in the GLM-5.3 technical blog, compared with GLM-5.2.',
                   chart=('GLM-5.3 vs GLM-5.2 · Zhipu evals', [('GLM-5.3 · DeepSWE', 66.9, True), ('GLM-5.2 · DeepSWE', 46.2, False),
                                                           ('GLM-5.3 · FrontierSWE', 78.1, True), ('GLM-5.2 · FrontierSWE', 67.5, False),
                                                           ('GLM-5.3 · Toolathlon', 73, True), ('GLM-5.2 · Toolathlon', 59.9, False)]),
                   head=[('Benchmark', ''), ('GLM-5.3', 'o-num o-hl'), ('GLM-5.2', 'o-num')],
                   rows=[('Terminal Bench 2.1', 'Terminal coding', '88.2', '81.0'), ('Terminal Bench 3.0', 'Terminal coding', '28.3', '4.6'),
                         ('DeepSWE v1.1', 'Software engineering', '66.9', '46.2'), ('NL2Repo', 'Repo from scratch', '58.0', '48.9'),
                         ('FrontierSWE', 'Software engineering', '78.1', '67.5'), ('SWE-Marathon v1.1', 'Long-horizon software engineering', '42.5', '19.4'),
                         ('PostTrainBench', 'Model post-training tasks', '39.8', '31.7'), ('CyberGym', 'Vulnerability reproduction', '84.5', '77.2'),
                         ('ExploitBench', 'Exploit development', '54.4', '24.4'), ('Toolathlon Verified', 'Tool use', '73.0', '59.9'),
                         ('AutomationBench v1.0.6', 'Automation agent', '48.2', '26.2'), ("Agents' Last Exam", 'General agent', '28.5', '23.8'),
                         ('HLE w/ Tools', 'General reasoning, with tools', '62.5', '54.7'), ('GDPval-AA v2', 'Knowledge work, Elo', '1769', '1508')],
                   caption='GLM-5.3 vs GLM-5.2 official benchmarks (published by Zhipu)',
                   note=f'Source: the <a href="{B53}" target="_blank" rel="noopener">GLM-5.3 technical blog</a>. Scores are Zhipu\'s published results; the blog also compares against other open and closed models.'),
        compare=dict(kicker='Compare', h2='GLM-5.3 vs GLM-5.3-Flash vs GLM-5.2', lead='Start new projects on GLM-5.3. For high-volume, budget-sensitive or image tasks, use GLM-5.3-Flash.',
                     head=[('Spec', ''), ('GLM-5.3', 'o-num o-hl'), ('GLM-5.3-Flash', 'o-num'), ('GLM-5.2', 'o-num')],
                     rows=[('Role', '', 'Latest flagship', 'Native multimodal, low cost', 'Long-horizon flagship'), ('Context', '', '1M', '1M', '1M'),
                           ('Input', '', 'Text', 'Text, images', 'Text'), ('Thinking', '', 'Always on', 'Always on', 'On or off'),
                           ('AnyAIGC input', 'per 1M tokens', p(s, 0), p('glm-5.3-flash', 0), p('glm-5.2', 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(s, 1), p('glm-5.3-flash', 1), p('glm-5.2', 1)),
                           ('Cache hit', 'per 1M tokens', p(s, 2), p('glm-5.3-flash', 2), p('glm-5.2', 2))],
                     caption='GLM-5.3, GLM-5.3-Flash and GLM-5.2 compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Zhipu Z.ai\'s official docs. Prices are current AnyAIGC prices; see the model catalog for live pricing. More on the <a href="/en/models/glm-5.3-flash">GLM-5.3-Flash API</a> and <a href="/en/models/glm-5.2">GLM-5.2 API</a>.'),
        uses=dict(kicker='Use cases', h2='Where GLM-5.3 fits',
                  items=[('01 · Large repos', 'Cross-module refactors and migrations', 'Load the whole codebase into 1M context, let GLM-5.3 map the dependencies and propose changes, then execute and verify them step by step with terminal tools.'),
                         ('02 · Coding agents', 'Claude Code and custom agents', 'Run tasks of dozens or hundreds of steps in Claude Code or your own agent framework: read code, run tests, fix errors. AnyAIGC does not cap concurrency.'),
                         ('03 · Security', 'Code audits and vulnerability hunting', 'Have the model review dependencies and application code, reproduce known vulnerabilities and write patches. Zhipu reports state-of-the-art results on CyberGym.'),
                         ('04 · Automation', 'Tool calls and workflow orchestration', 'Combine function calling and structured output to chain internal systems, scripts and APIs into automated workflows. Repeated system prompts are billed at the cache-hit rate.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the GLM-5.3 API in three steps', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, 'Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, 'You are a senior backend engineer. Answer with runnable code.', 'Write an HTTP client in Go with timeouts and retries.')),
                      ('effort', 'Thinking depth', 'Python · reasoning_effort', code_effort(s)),
                      ('tools', 'Tool calls', 'Python · tools', code_tools(s))],
                callout='<strong>Tip:</strong> GLM-5.3 always thinks. Its reasoning comes back in the <code>reasoning_content</code> field, and <code>reasoning_effort</code> sets the depth. Zhipu\'s defaults are <code>temperature=1.0</code> and <code>top_p=0.95</code>; if you tune them, change only one. In multi-turn chats and tool calls, send the full assistant message from the API (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.',
                note=QS_NOTE),
        cc=cc('GLM-5.3', s, 'Switch Claude Code to GLM-5.3 by editing one config file, and code in your terminal with Zhipu\'s latest flagship, billed per token.',
              '<strong>Save on light tasks:</strong> the config sets <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> to <code>glm-5.3-flash</code>, so Claude Code\'s lightweight subtasks use the cheaper model while the main work stays on GLM-5.3.', haiku='glm-5.3-flash'),
        family_h2='Other GLM models', family_lead=FAMILY_LEAD,
        faq_h2='GLM-5.3 API FAQ', faqs=faqs,
        final=dict(h2='Run GLM-5.3 at about 30% off the official price', p='Sign up, create an API key, and you can use glm-5.3 in your code or Claude Code within minutes.', other='GLM-5.3 API 中文版'),
        ent_name='GLM-5.3',
    )


# ======================================================================
# GLM-5.3-Flash
# ======================================================================
def gf():
    s = 'glm-5.3-flash'
    faqs = [
        ('How much does the GLM-5.3-Flash API cost?',
         f'On AnyAIGC, <code>glm-5.3-flash</code> is billed per token: input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)} per 1M tokens. '
         f'Zhipu\'s official USD prices are input {o(s, 0)}, output {o(s, 1)} and cache hit {o(s, 2)}, so AnyAIGC costs about 40.5% of official (about 60% off). Output includes thinking tokens. See the model catalog for live pricing.'),
        ('What is the GLM-5.3-Flash model ID, and how large is the context?',
         'The model ID is <code>glm-5.3-flash</code>. Zhipu lists a 1M-token context window and up to 128K output tokens. Through AnyAIGC it accepts text and image input.'),
        ('How is GLM-5.3-Flash different from GLM-5.3?',
         f'GLM-5.3-Flash is built on a newly trained base model: 320B total and 18B active parameters, with hybrid sparse and linear attention. It is the first natively multimodal GLM-5 model. Zhipu says that compared with <a href="/en/models/glm-5.3">GLM-5.3</a>, it needs about 3x less attention compute and about 4.4x less KV cache. '
         f'GLM-5.3 is the stronger flagship for the hardest coding work and accepts text only. Flash accepts images and costs about 1/15 as much (input {p(s, 0)} vs {p("glm-5.3", 0)}).'),
        ('Is GLM-5.3-Flash better than GLM-5.2?',
         f'Zhipu says GLM-5.3-Flash beats <a href="/en/models/glm-5.2">GLM-5.2</a> overall at about a tenth of the price. Reported comparisons: DeepSWE 63.4 vs 46.2, Toolathlon Verified 78.4 vs 59.9, AutomationBench 48.8 vs 26.2, and GDPval-AA v2 1773 vs 1504.'),
        ('Does GLM-5.3-Flash accept images? How do I send them?',
         'Yes. Add a <code>{"type": "image_url", "image_url": {"url": ...}}</code> content block to the <code>messages[].content</code> array. The <code>url</code> can be a public image URL or a Base64 data URL. For several images, add several blocks.'),
        faq_cc('GLM-5.3-Flash', s),
        ('Can I turn off thinking on GLM-5.3-Flash?',
         'No. GLM-5.3-Flash always thinks, and Zhipu does not support turning it off. Use <code>reasoning_effort</code> to set depth: <code>low</code>, <code>high</code> or <code>max</code> (default <code>max</code>). For simple tasks like classification and extraction, <code>low</code> cuts output tokens.'),
        ('Is GLM-5.3-Flash open source?',
         'Yes. Zhipu has published the GLM-5.3-Flash weights on Hugging Face (zai-org/GLM-5.3-Flash) under the MIT license. Calling the API through AnyAIGC means you do not have to host it yourself. Commercial use is governed by Zhipu AI\'s official terms.'),
        faq_rpm('GLM-5.3-Flash', s),
    ] + faq_common('GLM-5.3-Flash', s)
    return dict(
        title='GLM-5.3-Flash API Pricing | Multimodal, ~60% Off - AnyAIGC',
        desc=f'glm-5.3-flash API: Zhipu\'s first natively multimodal GLM-5 model, 1M context. Input {p(s, 0)}/1M, output {p(s, 1)}/1M, about 60% off. Bank transfer, invoices.',
        og_desc=f'glm-5.3-flash at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 60% off Zhipu official prices. Native multimodal, 320B total / 18B active; Zhipu says it beats GLM-5.2 overall. Works in Claude Code, with bank transfer and VAT invoices.',
        og_alt='AnyAIGC GLM-5.3-Flash API at about 60% off official prices',
        keywords='GLM-5.3-Flash API,glm-5.3-flash,GLM-5.3-Flash API pricing,GLM-5.3-Flash API key,GLM-5.3-Flash multimodal,GLM-5.3-Flash image input,GLM-5.3-Flash Claude Code,GLM-5.3-Flash vs GLM-5.3,Zhipu Flash API,GLM API,GLM-5.3-Flash API for business,GLM-5.3-Flash API invoice,AnyAIGC',
        crumb='GLM-5.3-Flash API', product='GLM-5.3-Flash API (AnyAIGC)', sku=s,
        product_desc='Zhipu GLM-5.3-Flash (glm-5.3-flash) through AnyAIGC: OpenAI-compatible /v1/chat/completions, native multimodal, 1M context, per-token billing at about 60% off official prices, unlimited concurrency.',
        offers=offers(s),
        hero=dict(eyebrow='Zhipu Z.ai · glm-5.3-flash',
                  h1='GLM-5.3-<span class="g-blue">Flash</span><span class="o-sr"> API</span>',
                  lead='The first natively multimodal GLM-5 model, with 320B total and 18B active parameters. Zhipu says it beats GLM-5.2 overall at a tenth of the price. On AnyAIGC it costs about 60% less than the official price.',
                  ask='Look at this page screenshot and rebuild it as a production-ready React component',
                  chips=['Native multimodal', 'Low cost', '1M context'],
                  sub=f'<code>glm-5.3-flash</code> input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)}: about 1/15 the price of GLM-5.3.',
                  facts=[('Model ID', s), ('Context', '1M tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About', h2='A natively multimodal model on a new base and architecture',
                   paras=['Zhipu calls GLM-5.3-Flash the first natively multimodal GLM-5 model, delivering more than GLM-5.2 at a very low cost. Unlike GLM-5.3, it starts from a newly trained base model, pretrained on about 30T tokens that include multimodal data.',
                          'It is a MoE with 320B total and 18B active parameters. Zhipu says it is the first open frontier model to combine sparse attention with linear attention, and it uses manifold-constrained hyper-connections (mHC). Compared with GLM-5.3, attention compute drops about 3x and KV cache about 4.4x, which keeps long-context ability while cutting serving cost sharply. It has a 1M-token context, up to 128K output, and thinking is always on.',
                          'On AnyAIGC, <code>glm-5.3-flash</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint, accepts text and images, and works directly in Claude Code, with unlimited concurrency.'],
                   spec=[('Context window', '1M', 'tokens'), ('Max output', '128K', 'tokens'),
                         ('Parameters', '320B', '18B active, MoE'), ('Input', 'Text, images', 'Native multimodal'),
                         ('Thinking', 'Always on', 'reasoning_effort: low / high / max'), ('Weights', 'Open', 'MIT license')]),
        features=dict(kicker='Capabilities', h2='What GLM-5.3-Flash can do',
                      items=[('Design to code', 'Zhipu reports 77.8 on Vision2Web. It builds and fixes front-end UI from design files and screenshots.'),
                             ('Charts and documents', 'Zhipu reports 89.4 on CharXiv Reasoning (with tools) and 62.4 on OfficeQA Pro, for reading charts and reports and producing office deliverables.'),
                             ('Coding and agents', 'Zhipu reports 84.3 on Terminal Bench 2.1, 63.4 on DeepSWE and 78.4 on Toolathlon Verified, beating GLM-5.2 overall.'),
                             ('Computer use', 'Zhipu reports 59.1 on OSWorld 2.0. It plans and carries out actions from screenshots.'),
                             ('Low-cost long context', f'1M context at {p(s, 0)} input and {p(s, 2)} cache hit per 1M tokens, so long documents and multi-turn agents cost less.'),
                             ('Built for high volume', 'AnyAIGC does not cap concurrency, so batch classification, extraction, summaries and parallel agents run as-is.')]),
        pricing=dict(kicker='Pricing', h2='GLM-5.3-Flash API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. Input, output and cache hits all cost about 40.5% of Zhipu\'s official USD prices (about 60% off).',
                     billing_label='Billing basics',
                     billing=billing(OFF[s]),
                     head=PRICE_HEAD, labels=LABELS, caption='glm-5.3-flash prices per 1M tokens (USD), AnyAIGC vs Zhipu official',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(s, 'Classify 10,000 tickets', 'Each ticket: 2,000 input tokens + 300 output', 2000, 300, 0, 10000),
                            cost_card(s, '50 coding agent turns', 'Each turn: 40K cache-hit tokens + 4,000 input + 2,000 output', 4000, 2000, 40000, 50),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='Where it beats GLM-5.2', lead='Scores Zhipu published in the GLM-5.3-Flash technical blog, compared with GLM-5.2. GLM-5.2 does not support vision benchmarks, so only Flash scores are listed there.',
                   chart=('GLM-5.3-Flash vs GLM-5.2 · Zhipu evals', [('5.3-Flash · DeepSWE', 63.4, True), ('5.2 · DeepSWE', 46.2, False),
                                                                 ('5.3-Flash · Toolathlon', 78.4, True), ('5.2 · Toolathlon', 59.9, False),
                                                                 ('5.3-Flash · AutomationBench', 48.8, True), ('5.2 · AutomationBench', 26.2, False)]),
                   head=[('Benchmark', ''), ('GLM-5.3-Flash', 'o-num o-hl'), ('GLM-5.2', 'o-num')],
                   rows=[('Terminal Bench 2.1', 'Terminal coding', '84.3', '81.0'), ('DeepSWE v1.1', 'Software engineering', '63.4', '46.2'),
                         ('NL2Repo', 'Repo from scratch', '56.3', '48.9'), ('Toolathlon Verified', 'Tool use', '78.4', '59.9'),
                         ('AutomationBench v1.0.6', 'Automation agent', '48.8', '26.2'), ("Agents' Last Exam", 'General agent', '26.3', '20.4'),
                         ('HLE w/ Tools', 'General reasoning, with tools', '55.3', '54.7'), ('GDPval-AA v2', 'Knowledge work, Elo', '1773', '1504'),
                         ('OfficeQA Pro', 'Office and finance QA', '62.4', '–'), ('CharXiv Reasoning', 'Chart reasoning, with tools', '89.4', '–'),
                         ('OSWorld 2.0', 'Computer use', '59.1', '–'), ('Vision2Web', 'Screenshot to web page', '77.8', '–')],
                   caption='GLM-5.3-Flash vs GLM-5.2 official benchmarks (published by Zhipu)',
                   note=f'Source: the <a href="{BF}" target="_blank" rel="noopener">GLM-5.3-Flash technical blog</a>. Scores are Zhipu\'s published results; "–" means GLM-5.2 does not support that task type or Zhipu did not publish a score.'),
        compare=dict(kicker='Compare', h2='GLM-5.3-Flash vs GLM-5.3 vs GLM-5.2', lead='Use Flash for high-volume, image and budget-sensitive tasks, and hand the hardest coding work to GLM-5.3.',
                     head=[('Spec', ''), ('GLM-5.3-Flash', 'o-num o-hl'), ('GLM-5.3', 'o-num'), ('GLM-5.2', 'o-num')],
                     rows=[('Role', '', 'Native multimodal, low cost', 'Latest flagship', 'Long-horizon flagship'), ('Context', '', '1M', '1M', '1M'),
                           ('Input', '', 'Text, images', 'Text', 'Text'), ('Thinking', '', 'Always on', 'Always on', 'On or off'),
                           ('AnyAIGC input', 'per 1M tokens', p(s, 0), p('glm-5.3', 0), p('glm-5.2', 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(s, 1), p('glm-5.3', 1), p('glm-5.2', 1)),
                           ('Cache hit', 'per 1M tokens', p(s, 2), p('glm-5.3', 2), p('glm-5.2', 2))],
                     caption='GLM-5.3-Flash, GLM-5.3 and GLM-5.2 compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Zhipu Z.ai\'s official docs. Prices are current AnyAIGC prices; see the model catalog for live pricing. More on the <a href="/en/models/glm-5.3">GLM-5.3 API</a>.'),
        uses=dict(kicker='Use cases', h2='Where GLM-5.3-Flash fits',
                  items=[('01 · Front end', 'Designs to components', 'Upload a design file or page screenshot, generate React, Vue or plain HTML/CSS, and iterate on the rendered result.'),
                         ('02 · Batch jobs', 'Classification, extraction and summaries', 'Ticket triage, field extraction, review tagging and long-document summaries. Low unit prices and no concurrency cap suit large parallel runs.'),
                         ('03 · Documents and charts', 'Reports, PDF scans and charts', 'Hand over report screenshots, scanned pages or charts to extract data, check numbers and write up the analysis.'),
                         ('04 · Coding agents', 'A budget option for Claude Code', 'Use Flash for everyday coding in Claude Code, or set it only as the lightweight subtask model and leave the main work to GLM-5.3.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the GLM-5.3-Flash API in three steps', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, 'Explain what a database index is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, 'You are a senior front-end engineer. Answer with runnable code.', 'Write an accessible dropdown menu component.')),
                      ('vision', 'Image input', 'Python · image_url', code_vision(s)),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream(s, 'Write 5 changelog entries for a SaaS product.'))],
                callout='<strong>Tip:</strong> GLM-5.3-Flash always thinks. Its reasoning comes back in the <code>reasoning_content</code> field, and <code>reasoning_effort</code> (<code>low</code> / <code>high</code> / <code>max</code>) sets the depth. Send images as <code>image_url</code> content blocks, using a public URL or Base64. In multi-turn chats and tool calls, send the full assistant message back in the next request unchanged.',
                note=QS_NOTE),
        cc=cc('GLM-5.3-Flash', s, 'Switch Claude Code to GLM-5.3-Flash: at about 1/15 the price of GLM-5.3, it handles everyday coding and reads screenshots to fix UI.',
              '<strong>For hard problems:</strong> for complex cross-module refactors or long-running tasks, change <code>ANTHROPIC_MODEL</code> in the config to <code>glm-5.3</code> and keep Flash for lightweight subtasks.'),
        family_h2='Other GLM models', family_lead=FAMILY_LEAD,
        faq_h2='GLM-5.3-Flash API FAQ', faqs=faqs,
        final=dict(h2='Run GLM-5.3-Flash at about 60% off the official price', p='Sign up, create an API key, and you can use glm-5.3-flash in your code or Claude Code within minutes.', other='GLM-5.3-Flash API 中文版'),
        ent_name='GLM-5.3-Flash',
    )


# ======================================================================
# GLM-5.2
# ======================================================================
def g52():
    s = 'glm-5.2'
    faqs = [
        ('How much does the GLM-5.2 API cost?',
         f'On AnyAIGC, <code>glm-5.2</code> is billed per token: input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)} per 1M tokens. '
         f'Zhipu\'s official USD prices are input {o(s, 0)}, output {o(s, 1)} and cache hit {o(s, 2)}, so AnyAIGC input and output cost about 67.5% of official (about 30% off). See the model catalog for live pricing.'),
        ('What is the GLM-5.2 model ID, and how large is the context?',
         'The model ID is <code>glm-5.2</code>. Zhipu lists a 1M-token context window and up to 128K output tokens. It accepts text input only.'),
        ('Can I turn off thinking on GLM-5.2?',
         f'Yes. Zhipu says GLM-5.2 uses dynamic thinking by default, letting the model decide whether to think, and thinking can also be turned off. That is one of the main differences from <a href="/en/models/glm-5.3">GLM-5.3</a>, which always thinks. On AnyAIGC you can set thinking depth with <code>reasoning_effort</code>.'),
        ('What makes GLM-5.2 stand out?',
         'Zhipu positions GLM-5.2 as a flagship for the era of long tasks. Its 1M context is usable in practice and fits project-scale engineering context. It runs long tasks more reliably, follows engineering conventions more consistently, and can take one task from requirements to multi-platform deployment. Zhipu says its IndexShare design cuts per-token compute by 2.9x at 1M context.'),
        ('GLM-5.2 or GLM-5.3: which should I use?',
         f'They share the same base model and cost the same for input and output on AnyAIGC. GLM-5.3 adds scaled-up post-training; Zhipu reports 50% better coding, and its cache-hit price is lower ({p("glm-5.3", 2)} vs {p(s, 2)}). New projects should start with GLM-5.3. Stay on GLM-5.2 if you need to turn thinking off or already have it tuned in production.'),
        faq_cc('GLM-5.2', s),
        ('Is GLM-5.2 open source? Can I use it commercially?',
         'Yes. Zhipu has published the GLM-5.2 weights under the MIT license on Hugging Face (zai-org/GLM-5.2) and ModelScope. Calling the API through AnyAIGC means you do not have to host it yourself. Commercial use is governed by Zhipu AI\'s official terms.'),
        faq_rpm('GLM-5.2', s),
    ] + faq_common('GLM-5.2', s)
    return dict(
        title='GLM-5.2 API Pricing & Access | 1M Context, ~30% Off - AnyAIGC',
        desc=f'glm-5.2 API: Zhipu\'s long-horizon flagship, 1M context, thinking optional. Input {p(s, 0)}/1M, output {p(s, 1)}/1M, about 30% off. Bank transfer, invoices.',
        og_desc=f'glm-5.2 at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 30% off Zhipu official prices. A long-horizon flagship with a 1M context you can actually use, MIT open source. Works in Claude Code, with bank transfer and VAT invoices.',
        og_alt='AnyAIGC GLM-5.2 API at about 30% off official prices',
        keywords='GLM-5.2 API,glm-5.2,GLM-5.2 API pricing,GLM-5.2 API key,GLM-5.2 Claude Code,GLM-5.2 1M context,GLM-5.2 disable thinking,Zhipu GLM-5.2,GLM API,GLM-5.2 API for business,GLM-5.2 API invoice,AnyAIGC',
        crumb='GLM-5.2 API', product='GLM-5.2 API (AnyAIGC)', sku=s,
        product_desc='Zhipu GLM-5.2 (glm-5.2) through AnyAIGC: OpenAI-compatible /v1/chat/completions, 1M context, per-token billing at about 30% off official prices, unlimited concurrency.',
        offers=offers(s),
        hero=dict(eyebrow='Zhipu Z.ai · glm-5.2',
                  h1='GLM-<span class="g-blue">5.2</span><span class="o-sr"> API</span>',
                  lead='Zhipu\'s flagship for long-horizon tasks. Its 1M context is usable in practice, it can take one task from requirements to multi-platform deployment, and thinking can be on or off. On AnyAIGC it costs about 30% less than the official price.',
                  ask='Port this mini program to H5 and a native app, keeping the APIs and styles consistent across all three',
                  chips=['Long-horizon tasks', '1M context', 'Thinking optional'],
                  sub=f'<code>glm-5.2</code> input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)}. Works with the OpenAI-compatible API and in Claude Code.',
                  facts=[('Model ID', s), ('Context', '1M tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About', h2='A 1M-context flagship built for long tasks',
                   paras=['Zhipu positions GLM-5.2 as a flagship for the era of long tasks. Zhipu says its 1M context is usable in practice and fits project-scale engineering context, and that it runs long tasks more reliably and follows engineering conventions more consistently.',
                          'Context grew from 200K on GLM-5.1 to 1M. The architecture keeps MoE with DSA sparse attention and adds IndexShare, where every 4 sparse attention layers share one indexer; Zhipu says this cuts per-token compute by 2.9x at 1M context. GLM-5.2 uses dynamic thinking by default, thinking can be turned off, and it is open source under the MIT license.',
                          'On AnyAIGC, <code>glm-5.2</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint and works directly in Claude Code, with unlimited concurrency. For new projects, consider <a href="/en/models/glm-5.3">GLM-5.3</a> at the same price; it builds on the same base model with stronger coding.'],
                   spec=[('Context window', '1M', 'tokens; GLM-5.1 had 200K'), ('Max output', '128K', 'tokens'),
                         ('Architecture', 'MoE + DSA', 'IndexShare sparse attention'), ('Input', 'Text', 'Text only'),
                         ('Thinking', 'On or off', 'Dynamic thinking by default'), ('Weights', 'Open', 'MIT license')]),
        features=dict(kicker='Capabilities', h2='What GLM-5.2 can do',
                      items=[('Project-scale engineering', '1M context fits a whole project. Zhipu reports 62.1 on SWE-bench Pro and 74.4 on FrontierSWE, for taking over and refactoring existing codebases.'),
                             ('Terminal coding', 'Zhipu reports 81.0 on Terminal Bench 2.1, and 82.7 when paired with Claude Code.'),
                             ('Math and reasoning', 'Zhipu reports 99.2 on AIME 2026, 94.4 on HMMT Nov. 2025 and 91.2 on GPQA-Diamond.'),
                             ('Tool calls', 'Zhipu reports 76.8 on MCP-Atlas (public set), with function calling, structured output and MCP support.'),
                             ('Thinking on or off', 'By default the model decides whether to think. You can turn thinking off for simple requests to get faster, shorter responses.'),
                             ('MIT open source', 'Weights are published under the MIT license on Hugging Face and ModelScope. Calling through AnyAIGC means no self-hosting.')]),
        pricing=dict(kicker='Pricing', h2='GLM-5.2 API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. Input and output cost about 67.5% of Zhipu\'s official USD prices (about 30% off).',
                     billing_label='Billing basics',
                     billing=billing(OFF[s]),
                     head=PRICE_HEAD, labels=LABELS, caption='glm-5.2 prices per 1M tokens (USD), AnyAIGC vs Zhipu official',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(s, 'Review 100 PRs', 'Each PR: 20K input tokens + 2,000 output', 20000, 2000, 0, 100),
                            cost_card(s, 'Analyze a 500K-token document', '500K input tokens + 5,000 output', 500000, 5000),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='GLM-5.2 official benchmarks', lead='Scores Zhipu published in the GLM-5.2 technical blog, compared with the previous GLM-5.1.',
                   chart=('GLM-5.2 vs GLM-5.1 · Zhipu evals', [('GLM-5.2 · FrontierSWE', 74.4, True), ('GLM-5.1 · FrontierSWE', 30.5, False),
                                                           ('GLM-5.2 · Terminal Bench 2.1', 81, True), ('GLM-5.1 · Terminal Bench 2.1', 63.5, False),
                                                           ('GLM-5.2 · SWE-bench Pro', 62.1, True), ('GLM-5.1 · SWE-bench Pro', 58.4, False)]),
                   head=[('Benchmark', ''), ('GLM-5.2', 'o-num o-hl'), ('GLM-5.1', 'o-num')],
                   rows=[('HLE', 'General reasoning', '40.5', '31.0'), ('HLE w/ Tools', 'General reasoning, with tools', '54.7', '52.3'),
                         ('AIME 2026', 'Math', '99.2', '95.3'), ('GPQA-Diamond', 'Science reasoning', '91.2', '86.2'),
                         ('SWE-bench Pro', 'Software engineering', '62.1', '58.4'), ('NL2Repo', 'Repo from scratch', '48.9', '42.7'),
                         ('DeepSWE', 'Software engineering', '46.2', '18.0'), ('ProgramBench', 'Programming', '63.7', '50.9'),
                         ('Terminal Bench 2.1', 'Terminal coding', '81.0', '63.5'), ('FrontierSWE', 'Software engineering', '74.4', '30.5'),
                         ('MCP-Atlas', 'Tool use, public set', '76.8', '71.8'), ('Tool-Decathlon', 'Tool use', '48.2', '40.7')],
                   caption='GLM-5.2 vs GLM-5.1 official benchmarks (published by Zhipu)',
                   note=f'Source: the <a href="{B52}" target="_blank" rel="noopener">GLM-5.2 technical blog</a>. Scores are Zhipu\'s published results. Some GLM-5.2 scores in the GLM-5.3 blog use different benchmark versions or dates, so do not mix the two sets directly.'),
        compare=dict(kicker='Compare', h2='GLM-5.2 vs GLM-5.3 vs GLM-5.3-Flash', lead='Start new projects on GLM-5.3 at the same price. Use GLM-5.2 when thinking should be off, and GLM-5.3-Flash when budget matters most.',
                     head=[('Spec', ''), ('GLM-5.2', 'o-num o-hl'), ('GLM-5.3', 'o-num'), ('GLM-5.3-Flash', 'o-num')],
                     rows=[('Role', '', 'Long-horizon flagship', 'Latest flagship', 'Native multimodal, low cost'), ('Context', '', '1M', '1M', '1M'),
                           ('Input', '', 'Text', 'Text', 'Text, images'), ('Thinking', '', 'On or off', 'Always on', 'Always on'),
                           ('AnyAIGC input', 'per 1M tokens', p(s, 0), p('glm-5.3', 0), p('glm-5.3-flash', 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(s, 1), p('glm-5.3', 1), p('glm-5.3-flash', 1)),
                           ('Cache hit', 'per 1M tokens', p(s, 2), p('glm-5.3', 2), p('glm-5.3-flash', 2))],
                     caption='GLM-5.2, GLM-5.3 and GLM-5.3-Flash compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Zhipu Z.ai\'s official docs. Prices are current AnyAIGC prices; see the model catalog for live pricing. More on the <a href="/en/models/glm-5.3">GLM-5.3 API</a> and <a href="/en/models/glm-5.3-flash">GLM-5.3-Flash API</a>.'),
        uses=dict(kicker='Use cases', h2='Where GLM-5.2 fits',
                  items=[('01 · Taking over a codebase', 'Understand and own an existing project', 'Load the whole project into 1M context to map the architecture, fill in docs and keep iterating within your engineering conventions.'),
                         ('02 · Multi-platform ports', 'Mini programs, H5 and native apps', 'One of Zhipu\'s recommended scenarios: take a single task from requirements all the way to multi-platform deployment.'),
                         ('03 · Paper reproduction', 'From paper to experiment code', 'Put a full paper and its reference code in context, reproduce the experiments, match the metrics and write the report.'),
                         ('04 · Quick answers', 'Lightweight requests with thinking off', 'Turn thinking off for support replies, classification and other requests that do not need deep reasoning, and get faster responses.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the GLM-5.2 API in three steps', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, 'Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, 'You are a senior backend engineer. Answer with runnable code.', 'Write an HTTP client in Go with timeouts and retries.')),
                      ('tools', 'Tool calls', 'Python · tools', code_tools(s)),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream(s, 'Explain why the sky is blue.'))],
                callout='<strong>Tip:</strong> GLM-5.2 uses dynamic thinking by default. Its reasoning, if any, comes back in the <code>reasoning_content</code> field, and <code>reasoning_effort</code> sets the depth. In multi-turn chats and tool calls, send the full assistant message from the API (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.',
                note=QS_NOTE),
        cc=cc('GLM-5.2', s, 'Switch Claude Code to GLM-5.2: its 1M context suits long coding sessions in large repos.',
              '<strong>Upgrade tip:</strong> for a higher coding success rate, replace every <code>glm-5.2</code> in the config with <code>glm-5.3</code>. Both cost the same.'),
        family_h2='Other GLM models', family_lead=FAMILY_LEAD,
        faq_h2='GLM-5.2 API FAQ', faqs=faqs,
        final=dict(h2='Run GLM-5.2 at about 30% off the official price', p='Sign up, create an API key, and you can use glm-5.2 in your code or Claude Code within minutes.', other='GLM-5.2 API 中文版'),
        ent_name='GLM-5.2',
    )
