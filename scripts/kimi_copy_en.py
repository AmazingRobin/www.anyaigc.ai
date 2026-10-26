# English copy for the Kimi topic pages. Used by scripts/kimi_pages.py.
# Prices come from kimi_data.PRICE (model catalog); official specs from platform.kimi.ai and Hugging Face model cards (read 2026-10-26).
from kimi_data import PRICE, OFFICIAL, MODELS, REG, PRICING, SUPPORT, DOCS_CHAT, DOCS_CC, OFFICIAL_PRICING
from kimi_layout import cost, money, save_pct

UNIT = '1M tokens'


def p(slug, i):
    return f'${PRICE[slug][i]}'


def o(slug, i):
    return f'${OFFICIAL[slug][i]}'


# ---------------- Shared FAQ ----------------
def faq_common(name, slug):
    return [
        (f'Can I call the {name} API from mainland China?',
         f'Yes. AnyAIGC is optimized for access from mainland China, so you can usually call <code>https://anyaigc.ai</code> without a proxy. Usage is billed in USD, and you can pay with WeChat Pay, Alipay, USDT or a credit card. Companies can pay by bank transfer and get VAT invoices.'),
        (f'How do I get a {name} API key?',
         f'Sign up at <a href="{REG}">anyaigc.ai</a>, add credit, and create a key in the console. The same key works for every Kimi model and 300+ other models on the platform, so you do not need a separate Moonshot platform account.'),
        ('Can AnyAIGC issue invoices, including VAT special invoices?',
         'Yes. AnyAIGC issues invoices for every top-up based on the amount you actually paid, including Chinese VAT general invoices and VAT special invoices. Send your billing details to support to get one.'),
        ('Can my company pay by bank transfer and sign a contract?',
         f'Yes. Companies can top up by corporate bank transfer and sign a service agreement with AnyAIGC, with a dedicated support and technical contact. For procurement, <a href="{SUPPORT}">contact AnyAIGC support</a>.'),
        ('Will my data be used for training?',
         'No. Except where required by law, AnyAIGC does not persistently store your prompts or outputs and does not use them to train models. Requests are encrypted over HTTPS. See the AnyAIGC <a href="/privacy">Privacy Policy</a>. The model\'s own data policy is governed by Moonshot AI\'s official terms.'),
    ]


def faq_cc(name, model):
    return (f'Can I use {name} in Claude Code?',
            f'Yes. In the env block of <code>~/.claude/settings.json</code>, set <code>ANTHROPIC_BASE_URL</code> to <code>https://anyaigc.ai</code>, <code>ANTHROPIC_AUTH_TOKEN</code> to your API key, and <code>ANTHROPIC_MODEL</code> to <code>{model}</code>. Then run <code>claude</code>.')


def faq_rpm(name, slug):
    return ('Are there concurrency or rate limits?',
            f'AnyAIGC does not cap concurrency for <code>{slug}</code>, and every user gets this by default. That suits batch jobs, CI pipelines and parallel agents. Moonshot\'s own platform limits concurrency, RPM, TPM and TPD by top-up tier; those tiers do not apply when you call through AnyAIGC.')


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
    # reasoning_content deltas arrive first, then the final answer in content
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

image = base64.b64encode(Path("screenshot.png").read_bytes()).decode()
resp = client.chat.completions.create(
    model="{model}",
    messages=[{{
        "role": "user",
        "content": [
            {{"type": "image_url", "image_url": {{"url": f"data:image/png;base64,{{image}}"}}}},
            {{"type": "text", "text": "This is a screenshot of a web page. Rebuild it in HTML + CSS."}},
        ],
    }}],
)
print(resp.choices[0].message.content)'''


def code_effort(model):
    return f'''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

# K3 always thinks; reasoning_effort sets the depth: low / high / max (default max)
resp = client.chat.completions.create(
    model="{model}",
    reasoning_effort="low",
    messages=[{{"role": "user", "content": "Rewrite this SQL to use window functions: SELECT ..."}}],
)
print(resp.choices[0].message.content)'''


def cc_code(model):
    return f'''{{
  "env": {{
    "ANTHROPIC_BASE_URL": "https://anyaigc.ai",
    "ANTHROPIC_AUTH_TOKEN": "sk-your-API-key",
    "ANTHROPIC_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "{model}",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "{model}",
    "API_TIMEOUT_MS": "300000"
  }}
}}'''


def cc(name, model, lead, callout):
    return dict(
        kicker='Claude Code', h2=f'Use {name} in Claude Code', lead=lead,
        steps=['<strong>Install Claude Code</strong>: use the official installer (for example <code>npm install -g @anthropic-ai/claude-code</code>).',
               '<strong>Add the config</strong>: edit <code>~/.claude/settings.json</code>, add the env block below, and replace <code>ANTHROPIC_AUTH_TOKEN</code> with the key you created on AnyAIGC.',
               f'<strong>Start coding</strong>: run <code>claude</code> in your project folder. Type <code>/model</code> to confirm the current model is <code>{model}</code>.'],
        code=cc_code(model), callout=callout,
        note=f'For the full walkthrough and common errors, see the <a href="{DOCS_CC}" target="_blank" rel="noopener">Claude Code setup guide</a>. Swap the model name in the guide for <code>{model}</code>.')


def qs_steps(model):
    return ['<strong>Sign up and add credit</strong>: create an account at <a href="' + REG + '">anyaigc.ai</a>. Top up from $1; your balance works across every model on the platform.',
            '<strong>Create an API key</strong>: create a key in the console, copy the value that starts with <code>sk-</code>, and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Send a request</strong>: call <code>POST https://anyaigc.ai/v1/chat/completions</code> with <code>model</code> set to <code>{model}</code> and an <code>Authorization: Bearer</code> header. With the OpenAI SDK, just set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>.']


QS_NOTE = f'See the <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions reference</a> for every parameter. Replace the model name in the docs examples with the Kimi model ID you want.'

PRICE_HEAD = [('Item', ''), ('Model', ''), ('AnyAIGC', 'o-num o-hl'), ('Moonshot official', 'o-num'), ('Savings', 'o-num')]
LABELS = [('Input', 'per 1M tokens'), ('Output', 'per 1M tokens, incl. thinking'), ('Cache hit', 'per 1M tokens')]
BILLING = [('Per token', 'Input, output and cache priced separately'), ('About 60% off', 'vs Moonshot official USD prices'),
           ('Unlimited concurrency', 'On by default for every user'), ('USD', 'One balance for 300+ models')]
COSTS_LEAD = 'Estimates for common workloads. The struck-through figure is the same usage at Moonshot official prices.'


def pricing_note(slug):
    q = f'?keyword={slug}' if slug else '?keyword=kimi'
    return (f'Prices are in USD and billed on the tokens you actually use. Output includes thinking tokens, and repeated prompt prefixes are billed at the cache-hit rate automatically. '
            f'Official prices come from the <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">Kimi platform pricing page</a> (USD). '
            f'The table shows the lowest price in the model catalog; see the <a href="{PRICING}{q}">AnyAIGC model catalog</a> for live pricing.')


def cost_card(slug, title, calc, inp=0, out=0, cache=0, n=1):
    a = money(cost(slug, inp, out, cache, n))
    b = money(cost(slug, inp, out, cache, n, official=True))
    return (title, calc, a, f'Official <s>{b}</s>')


def offers(slug):
    return [('Input (per 1M tokens)', PRICE[slug][0]), ('Output (per 1M tokens)', PRICE[slug][1]),
            ('Cache hit (per 1M tokens)', PRICE[slug][2])]


FAMILY = [
    ('kimi', '', ('Kimi overview', 'K3, K2.7 Code and K2.6 pricing compared')),
    ('kimi-k3', 'Flagship', f'2.8T-parameter open weights, 1M context · input {p("kimi-k3", 0)} / 1M'),
    ('kimi-k2.7-code', 'Coding', f'Coding-tuned K2.6, always thinks · input {p("kimi-k2.7-code", 0)} / 1M'),
    ('kimi-k2.6', '', f'General multimodal agent, thinking optional · input {p("kimi-k2.6", 0)} / 1M'),
]


def build(slug):
    return {'kimi': hub, 'kimi-k3': k3, 'kimi-k2.7-code': k27, 'kimi-k2.6': k26}[slug]()


FAMILY_LEAD = 'One API key calls every Kimi model below. Pick by task difficulty and budget.'


# ======================================================================
# Overview
# ======================================================================
def hub():
    k3, c, k6 = 'kimi-k3', 'kimi-k2.7-code', 'kimi-k2.6'
    faqs = [
        ('How much does the Kimi API cost?',
         f'Kimi models on AnyAIGC are billed per token. Per 1M tokens: <code>kimi-k3</code> input {p(k3, 0)}, output {p(k3, 1)}, cache hit {p(k3, 2)}; '
         f'<code>kimi-k2.7-code</code> input {p(c, 0)}, output {p(c, 1)}, cache hit {p(c, 2)}; <code>kimi-k2.6</code> input {p(k6, 0)}, output {p(k6, 1)}, cache hit {p(k6, 2)}. '
         f'That is about 40% of Moonshot\'s official USD prices. See the model catalog for live pricing.'),
        ('Which Kimi models are on AnyAIGC, and what are the model IDs?',
         'This page covers three: <code>kimi-k3</code> (a 2.8T-parameter open-weight model with 1M context), <code>kimi-k2.7-code</code> (a coding agent model) and <code>kimi-k2.6</code> (a general multimodal agent model). '
         'Put the model ID in the <code>model</code> field of the request body. Switching models only means changing that one field.'),
        ('Kimi K3, K2.7 Code or K2.6: which should I use?',
         f'Pick <a href="/en/models/kimi-k3">Kimi K3</a> when you need 1M context, the hardest long-horizon coding or deep reasoning. Pick <a href="/en/models/kimi-k2.7-code">K2.7 Code</a> for everyday coding and coding agents; Moonshot says it scores 21.8% higher than K2.6 on Kimi Code Bench v2. '
         f'Pick <a href="/en/models/kimi-k2.6">K2.6</a> when you want non-thinking mode, fast responses or general chat. K2.7 Code and K2.6 cost the same, about a third of K3.'),
        ('Is the Kimi API OpenAI compatible?',
         'Yes. All three models use <code>POST https://anyaigc.ai/v1/chat/completions</code> with the same request and response format as OpenAI Chat Completions. With the official OpenAI SDK, set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>. The reasoning trace comes back in the <code>reasoning_content</code> field.'),
        faq_cc('Kimi', 'kimi-k3'),
        ('How large is the context window?',
         'According to Moonshot, Kimi K3 supports a 1,048,576-token context; K2.7 Code and K2.6 support 262,144 tokens (256K). All three accept image input and support tool calls.'),
        ('Are Kimi models open source? Can I use them commercially?',
         'Moonshot AI has published the weights for Kimi K3, K2.7 Code and K2.6 on Hugging Face. Calling the API through AnyAIGC means you do not have to host them yourself. Model licenses and commercial use are governed by Moonshot AI\'s official terms.'),
        ('Are there concurrency or rate limits?',
         'AnyAIGC does not cap concurrency for Kimi models, and every user gets this by default. That suits batch jobs, CI pipelines and parallel agents. Moonshot\'s own platform limits concurrency, RPM, TPM and TPD by top-up tier; those tiers do not apply when you call through AnyAIGC.'),
    ] + faq_common('Kimi', 'kimi')
    return dict(
        title='Kimi API Pricing & Access | K3, K2.7 Code, K2.6 - AnyAIGC',
        desc=f'Kimi API for kimi-k3, kimi-k2.7-code and kimi-k2.6 from {p(c, 0)}/1M input, about 60% off official. 1M context, unlimited concurrency, bank transfer and invoices.',
        og_desc=f'Call Kimi K3, K2.7 Code and K2.6 with one key at about 40% of Moonshot official prices. OpenAI-compatible API, works in Claude Code, unlimited concurrency, bank transfer and VAT invoices.',
        og_alt='AnyAIGC Kimi API: K3, K2.7 Code and K2.6 at about 60% off official prices',
        keywords='Kimi API,Kimi API pricing,Kimi API key,Moonshot API,Moonshot AI API,Kimi K3 API,Kimi K2.7 Code API,Kimi K2.6 API,Kimi OpenAI compatible,Kimi Claude Code,Kimi API for business,Kimi API invoice,AnyAIGC',
        crumb='Kimi API', product='Kimi API (AnyAIGC)', sku='kimi',
        product_desc='Moonshot AI Kimi models (kimi-k3, kimi-k2.7-code, kimi-k2.6) through AnyAIGC: OpenAI-compatible /v1/chat/completions, per-token billing at about 40% of official prices, unlimited concurrency.',
        offers=[(f'{n} input (per 1M tokens)', PRICE[s][0]) for s, n in ((k3, 'Kimi K3'), (c, 'Kimi K2.7 Code'), (k6, 'Kimi K2.6'))]
        + [(f'{n} output (per 1M tokens)', PRICE[s][1]) for s, n in ((k3, 'Kimi K3'), (c, 'Kimi K2.7 Code'), (k6, 'Kimi K2.6'))],
        hero=dict(eyebrow='Moonshot AI · Kimi',
                  h1='Kimi <span class="k-blue">API</span>',
                  lead='Kimi K3, K2.7 Code and K2.6 on one API key, at about 40% of Moonshot\'s official prices.',
                  ask='Use Kimi to refactor this repo\'s payments module and fill in the unit tests',
                  chips=['Long-horizon coding', '1M context', 'Agents'],
                  sub=f'OpenAI-compatible <code>/v1/chat/completions</code> that also plugs into Claude Code. <code>kimi-k2.7-code</code> and <code>kimi-k2.6</code> start at {p(c, 0)} per 1M input tokens, with unlimited concurrency.',
                  facts=[('Models', 'K3 · K2.7 Code · K2.6'), ('Context', 'Up to 1M'), ('Input', f'From {p(c, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        models=dict(kicker='Models', h2='Three Kimi models', lead='Same key, same endpoint. Change the model ID to match the task.',
                    unit_in='1M input', unit_out='1M output', go='View guide',
                    items=[(k3, 'Flagship', 'Moonshot\'s open-weight 2.8T-parameter model for long-horizon coding, knowledge work and deep reasoning.', ['1,048,576-token context', 'Always thinks, adjustable reasoning_effort', 'Native vision']),
                           (c, 'Coding', 'A coding agent model built on K2.6. Follows instructions more reliably over long context and uses fewer thinking tokens.', ['256K context', 'Thinking always on, interleaved tool calls', 'Kimi Code Bench v2 62.0']),
                           (k6, '', 'An open native multimodal agent model with thinking and non-thinking modes, for coding and general chat.', ['256K context', 'Thinking on or off', 'SWE-Bench Verified 80.2'])]),
        pricing=dict(kicker='Pricing', h2='Kimi API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. All three models cost about 40% of Moonshot\'s official USD prices.',
                     billing_label='Billing basics', billing=BILLING,
                     head=[('Item', ''), ('AnyAIGC', 'o-num o-hl'), ('Moonshot official', 'o-num'), ('Savings', 'o-num')],
                     labels=LABELS, caption='Kimi prices per 1M tokens (USD), AnyAIGC vs Moonshot official',
                     note=pricing_note(''),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(k3, 'K3 · 20 agent coding turns', 'Each turn: 50K cache-hit tokens + 5,000 input + 3,000 output', 5000, 3000, 50000, 20),
                            cost_card(c, 'K2.7 Code · review 100 PRs', 'Each PR: 20K input tokens + 2,000 output', 20000, 2000, 0, 100),
                            cost_card(k6, 'K2.6 · classify 10,000 tickets', 'Each ticket: 2,000 input tokens + 300 output', 2000, 300, 0, 10000)]),
        compare=dict(kicker='Compare', h2='Kimi K3 vs K2.7 Code vs K2.6', lead='Send the hardest work to K3, everyday coding to K2.7 Code, and use K2.6 for fast replies or when thinking should be off.',
                     head=[('Spec', ''), ('K3', 'o-num o-hl'), ('K2.7 Code', 'o-num'), ('K2.6', 'o-num')],
                     rows=[('Role', '', 'Flagship general', 'Coding agent', 'General multimodal agent'),
                           ('Total parameters', '', '2.8T', '1T', '1T'),
                           ('Context', '', '1M', '256K', '256K'),
                           ('Thinking', '', 'Always on', 'Always on', 'On or off'),
                           ('AnyAIGC input', 'per 1M tokens', p(k3, 0), p(c, 0), p(k6, 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(k3, 1), p(c, 1), p(k6, 1)),
                           ('Cache hit', 'per 1M tokens', p(k3, 2), p(c, 2), p(k6, 2))],
                     caption='Kimi K3, K2.7 Code and K2.6 compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Moonshot AI\'s Hugging Face and Kimi platform materials. Prices are current AnyAIGC prices; see the model catalog for live pricing.'),
        uses=dict(kicker='Use cases', h2='What teams build with the Kimi API',
                  items=[('01 · Long-horizon coding', 'Large refactors and cross-file changes', 'K3\'s 1M context holds a whole codebase and works through terminal tools step by step. On a tighter budget, switch to K2.7 Code at about a third of the price.'),
                         ('02 · Coding agents', 'Claude Code, CI and auto-fix', 'Plug Kimi into Claude Code or your own agent framework to run tests, read errors and patch code. AnyAIGC does not cap concurrency, so many agents can run at once.'),
                         ('03 · Front end and design', 'Screenshots to shippable UI', 'All three models read images. Hand over a design file or page screenshot and get HTML, CSS or component code back.'),
                         ('04 · Knowledge work', 'Long-document research and structured output', 'Load whole contracts, financial reports or research packs into context to extract fields, compare clauses and draft reports. Reused material is billed at the cache-hit rate.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the Kimi API in three steps', steps=qs_steps('kimi-k3'),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl('kimi-k3', 'Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py('kimi-k2.7-code', 'You are a senior backend engineer. Answer with runnable code.', 'Write an HTTP client in Go with timeouts and retries.')),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream('kimi-k2.6', 'Write 5 changelog entries for a SaaS product.'))],
                callout='<strong>Tip:</strong> Kimi returns its reasoning in the <code>reasoning_content</code> field. When streaming, reasoning deltas arrive first, then the final answer. In multi-turn chats and tool calls, send the full assistant message from the API (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.',
                note=QS_NOTE),
        cc=cc('Kimi', 'kimi-k3', 'Switch Claude Code to Kimi by editing one config file, and the coding agent in your terminal runs on Kimi.',
              '<strong>Switching models:</strong> for a cheaper coding model, replace every <code>kimi-k3</code> in the config with <code>kimi-k2.7-code</code>. K3 has 1M context for large repos; K2.7 Code costs about a third as much.'),
        family_h2='All Kimi models', family_lead=FAMILY_LEAD,
        faq_h2='Kimi API FAQ', faqs=faqs,
        final=dict(h2='Run Kimi at about 40% of the official price', p='Sign up, create an API key, and you can use Kimi K3, K2.7 Code and K2.6 in your code or Claude Code within minutes.',
                   other='Kimi API 中文版'),
        ent_name='Kimi',
    )


# ======================================================================
# Kimi K3
# ======================================================================
def k3():
    s = 'kimi-k3'
    faqs = [
        ('How much does the Kimi K3 API cost?',
         f'On AnyAIGC, <code>kimi-k3</code> is billed per token: input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)} per 1M tokens. '
         f'Moonshot\'s official USD prices are input {o(s, 0)}, output {o(s, 1)} and cache hit {o(s, 2)}, so AnyAIGC is about 40% of official. Output includes thinking tokens. See the model catalog for live pricing.'),
        ('What is the Kimi K3 model ID, and how large is the context?',
         'The model ID is <code>kimi-k3</code>. Moonshot lists a 1,048,576-token (1M) context window. <code>max_completion_tokens</code> defaults to 131,072 and can be set as high as 1,048,576.'),
        ('What sets Kimi K3 apart?',
         'Moonshot says Kimi K3 is the first open-source model to reach 2.8 trillion parameters. It is built on Kimi Delta Attention (KDA) hybrid linear attention and Attention Residuals, and its MoE activates 16 of 896 experts per token, with native vision. Moonshot reports about 2.5x the overall scaling efficiency of K2, aimed at long-horizon coding, knowledge work and reasoning.'),
        ('How do I adjust Kimi K3\'s thinking depth?',
         'K3 always thinks and thinking cannot be turned off. Use the top-level <code>reasoning_effort</code> field in the request body to set depth: <code>low</code>, <code>high</code> or <code>max</code> (default <code>max</code>). Use <code>low</code> on simple tasks to cut output tokens.'),
        ('Does Kimi K3 support tool calls and image input?',
         'Yes. K3 supports function calling (<code>tools</code> / <code>tool_choice</code>), structured output (<code>json_schema</code>), streaming and image input. In multi-turn chats and tool calls, send the full assistant message (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.'),
        faq_cc('Kimi K3', s),
        ('Kimi K3 or K2.7 Code: which should I use?',
         f'K3 is the 2.8T-parameter flagship with 1M context, suited to large repos, long-running tasks and the hardest reasoning. <a href="/en/models/kimi-k2.7-code">K2.7 Code</a> is a 1T-parameter coding model with 256K context at {p("kimi-k2.7-code", 0)} input and {p("kimi-k2.7-code", 1)} output on AnyAIGC, about a third of K3. Many teams use K2.7 Code day to day and switch to K3 for hard problems, with the same key.'),
        faq_rpm('Kimi K3', s),
    ] + faq_common('Kimi K3', s)
    return dict(
        title='Kimi K3 API Pricing & Access | 1M Context Coding - AnyAIGC',
        desc=f'kimi-k3 API: Moonshot\'s 2.8T open-weight model with 1M context. Input {p(s, 0)}/1M, output {p(s, 1)}/1M, unlimited concurrency, bank transfer and invoices.',
        og_desc=f'kimi-k3 at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 40% of Moonshot official prices. 1M context for long-horizon coding and reasoning, OpenAI compatible, works in Claude Code.',
        og_alt='AnyAIGC Kimi K3 API at about 60% off official prices',
        keywords='Kimi K3 API,kimi-k3,Kimi K3 API pricing,Kimi K3 API key,Kimi K3 1M context,Kimi K3 Claude Code,Moonshot K3 API,Kimi API,Kimi K3 API for business,Kimi K3 API invoice,AnyAIGC',
        crumb='Kimi K3 API', product='Kimi K3 API (AnyAIGC)', sku=s,
        product_desc='Moonshot AI Kimi K3 (kimi-k3) through AnyAIGC: OpenAI-compatible /v1/chat/completions, 1M context, per-token billing at about 40% of official prices, unlimited concurrency.',
        offers=offers(s),
        hero=dict(eyebrow='Moonshot AI · kimi-k3',
                  h1='Kimi <span class="k-blue">K3</span><span class="o-sr"> API</span>',
                  lead='A 2.8-trillion-parameter open-weight model with 1M context, built for long-horizon coding, knowledge work and deep reasoning. On AnyAIGC it costs about 40% of the official price.',
                  ask='Read the whole repo, split the monolith into three services, and write the migration plan',
                  chips=['1M context', 'reasoning_effort', 'Vision'],
                  sub=f'<code>kimi-k3</code> input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)}. Works with the OpenAI-compatible API and in Claude Code.',
                  facts=[('Model ID', s), ('Context', '1M tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About', h2='A trillion-scale open-weight model for long tasks',
                   paras=['Moonshot AI says Kimi K3 is the first open-source model to reach 2.8 trillion parameters. It is built on Kimi Delta Attention (KDA) hybrid linear attention and Attention Residuals, two architecture changes meant to keep information flowing across longer sequences and deeper networks.',
                          'Under the Stable LatentMoE framework, K3 activates 16 of 896 experts per token. Moonshot says that together with improved training methods and data recipes, K3 reaches about 2.5x the overall scaling efficiency of K2. It has native vision, a 1,048,576-token context window, and thinking is always on.',
                          'On AnyAIGC, <code>kimi-k3</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint and works directly in Claude Code. You do not need a Moonshot platform account, there are no top-up tiers, and concurrency is unlimited.'],
                   spec=[('Context window', '1,048,576', 'Max input tokens'), ('Max output', '131,072', 'Default, can be set up to 1,048,576'),
                         ('Total parameters', '2.8T', 'MoE, 16 of 896 experts active'), ('Input', 'Text, images', 'Native vision'),
                         ('Thinking', 'Always on', 'reasoning_effort: low / high / max'), ('Weights', 'Open', 'Hugging Face moonshotai/Kimi-K3')]),
        features=dict(kicker='Capabilities', h2='What Kimi K3 can do',
                      items=[('Long-horizon coding', 'Works through long engineering tasks with little human input, understands large codebases and coordinates terminal tools. Moonshot reports 88.3 on Terminal-Bench 2.1.'),
                             ('Vision plus code', 'Uses screenshots and visual feedback to improve front end, game development and CAD workflows: read a design, write the UI, adjust styles against the render.'),
                             ('End-to-end knowledge work', 'Deep research, data visualization, dashboards and reports. Moonshot reports 91.2 on BrowseComp and 93.5 on GPQA Diamond.'),
                             ('1M-token context', 'Fit a full codebase, a contract set or long research material in one request. Repeated prefixes are cached automatically, and cache hits cost only ' + p(s, 2) + ' per 1M tokens.'),
                             ('Agents and tool calls', 'Supports function calling, tool_choice, dynamic tool loading and structured output. Moonshot reports 94.5 on MCPMark-Verified and 84.8 on OSWorld-Verified.'),
                             ('Adjustable thinking', 'Thinking is always on. Set reasoning_effort to low, high or max: save tokens on simple tasks, use max on hard ones.')]),
        pricing=dict(kicker='Pricing', h2='Kimi K3 API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. Input, output and cache hits all cost about 40% of Moonshot\'s official USD prices.',
                     billing_label='Billing basics', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption='kimi-k3 prices per 1M tokens (USD), AnyAIGC vs Moonshot official',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(s, '20 agent coding turns', 'Each turn: 50K cache-hit tokens + 5,000 input + 3,000 output', 5000, 3000, 50000, 20),
                            cost_card(s, 'Analyze a 500K-token document', '500K input tokens + 5,000 output', 500000, 5000),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='Kimi K3 official benchmarks', lead='Kimi K3 scores published by Moonshot AI (max reasoning effort) across reasoning, coding, agent and vision tasks.',
                   chart=('Kimi K3 · selected benchmarks', [('Terminal-Bench 2.1', 88.3, True), ('BrowseComp', 91.2, True), ('MCPMark-Verified', 94.5, True),
                                                            ('GPQA Diamond', 93.5, True), ('OSWorld-Verified', 84.8, True)]),
                   head=[('Benchmark', ''), ('Kimi K3', 'o-num o-hl')],
                   rows=[('GPQA Diamond', 'Science reasoning', '93.5'), ('AA-LCR', 'Long-context reasoning', '74.7'),
                         ('Terminal-Bench 2.1', 'Terminal coding', '88.3'), ('ProgramBench', 'Coding', '77.8'), ('FrontierSWE', 'Software engineering', '81.2'),
                         ('DeepSWE', 'Long-horizon software engineering', '67.5'), ('Kimi Code Bench 2.0', 'Coding', '72.9'),
                         ('BrowseComp', 'Web browsing agent', '91.2'), ('MCPMark-Verified', 'Tool use', '94.5'), ('MCP-Atlas', 'Tool use', '84.2'),
                         ('OSWorld-Verified', 'Computer use', '84.8'), ('OmniDocBench', 'Document understanding', '91.1'), ('Video-MME', 'Video understanding', '90.0')],
                   caption='Kimi K3 official benchmark scores (published by Moonshot AI)',
                   note='Source: the <a href="https://huggingface.co/moonshotai/Kimi-K3" target="_blank" rel="noopener">Kimi K3 model card on Hugging Face</a>. Scores are Moonshot AI\'s published results at max reasoning effort.'),
        compare=dict(kicker='Compare', h2='Kimi K3 vs K2.7 Code vs K2.6', lead='K3 handles the hardest and longest tasks. K2.7 Code and K2.6 cost about a third as much.',
                     head=[('Spec', ''), ('K3', 'o-num o-hl'), ('K2.7 Code', 'o-num'), ('K2.6', 'o-num')],
                     rows=[('Role', '', 'Flagship general', 'Coding agent', 'General multimodal agent'), ('Total parameters', '', '2.8T', '1T', '1T'),
                           ('Context', '', '1M', '256K', '256K'), ('Thinking', '', 'Always on', 'Always on', 'On or off'),
                           ('AnyAIGC input', 'per 1M tokens', p(s, 0), p('kimi-k2.7-code', 0), p('kimi-k2.6', 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(s, 1), p('kimi-k2.7-code', 1), p('kimi-k2.6', 1))],
                     caption='Kimi K3, K2.7 Code and K2.6 compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Moonshot AI\'s public materials. Prices are current AnyAIGC prices; see the model catalog for live pricing. More on the <a href="/en/models/kimi-k2.7-code">Kimi K2.7 Code API</a> and <a href="/en/models/kimi-k2.6">Kimi K2.6 API</a>.'),
        uses=dict(kicker='Use cases', h2='Where Kimi K3 fits',
                  items=[('01 · Large repos', 'Cross-module refactors and migrations', 'Load the whole codebase into 1M context, let K3 map the dependencies and propose the change in one pass, then execute and verify it step by step with terminal tools.'),
                         ('02 · Agents', 'Long-running autonomous tasks', 'Run tasks with dozens or hundreds of steps in Claude Code or your own agent: research, write code, run tests, fix errors. AnyAIGC does not cap concurrency.'),
                         ('03 · Research', 'Deep research and reports', 'Read a stack of papers, financial reports or research files, cross-check them, and produce structured findings, chart code and a deliverable report.'),
                         ('04 · Vision', 'Screenshot to code', 'Give K3 a design file, an error screenshot or a render, and have it write or fix front-end, game and visualization code.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the Kimi K3 API in three steps', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, 'Explain what a MoE model is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, 'You are a senior backend engineer. Answer with runnable code.', 'Write an HTTP client in Go with timeouts and retries.')),
                      ('effort', 'Thinking depth', 'Python · reasoning_effort', code_effort(s)),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream(s, 'Explain why the sky is blue.'))],
                callout='<strong>Tip:</strong> K3 always thinks, and the reasoning comes back in <code>reasoning_content</code>. Moonshot recommends <code>temperature=1.0</code> and <code>top_p=0.95</code>. In multi-turn chats and tool calls, send the full assistant message from the API (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged, not just the content.',
                note=QS_NOTE),
        cc=cc('Kimi K3', s, 'Switch Claude Code to Kimi K3. The 1M context suits long coding sessions in large repos.',
              '<strong>Save on side tasks:</strong> set <code>ANTHROPIC_DEFAULT_HAIKU_MODEL</code> to <code>kimi-k2.7-code</code> so Claude Code\'s lightweight subtasks use the cheaper model while the main task stays on K3.'),
        family_h2='Other Kimi models', family_lead=FAMILY_LEAD,
        faq_h2='Kimi K3 API FAQ', faqs=faqs,
        final=dict(h2='Run Kimi K3 at about 40% of the official price', p='Sign up, create an API key, and you can use kimi-k3 in your code or Claude Code within minutes.', other='Kimi K3 API 中文版'),
        ent_name='Kimi K3',
    )


# ======================================================================
# Kimi K2.7 Code
# ======================================================================
def k27():
    s = 'kimi-k2.7-code'
    faqs = [
        ('How much does the Kimi K2.7 Code API cost?',
         f'On AnyAIGC, <code>kimi-k2.7-code</code> is billed per token: input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)} per 1M tokens. '
         f'Moonshot\'s official USD prices are input {o(s, 0)}, output {o(s, 1)} and cache hit {o(s, 2)}, so AnyAIGC is about 40% of official. Output includes thinking tokens. See the model catalog for live pricing.'),
        ('What is the Kimi K2.7 Code model ID, and how large is the context?',
         'The model ID is <code>kimi-k2.7-code</code>. Moonshot lists a 262,144-token (256K) context window, with text and image input.'),
        ('How is Kimi K2.7 Code different from K2.6?',
         f'K2.7 Code is further trained from K2.6 with a focus on coding, on the same architecture (1T total, 32B active parameters). Moonshot says it follows instructions more reliably over long context, completes more coding tasks, and uses about 30% fewer thinking tokens than K2.6; Kimi Code Bench v2 goes from 50.9 to 62.0. K2.7 Code only runs in thinking mode, while <a href="/en/models/kimi-k2.6">K2.6</a> can turn thinking off. Both have the same input and output prices on AnyAIGC.'),
        ('Can I turn off thinking in Kimi K2.7 Code?',
         'No. Moonshot says K2.7 Code always runs with thinking and preserve thinking on, and does not support non-thinking mode. For fast, non-thinking responses, use <code>kimi-k2.6</code>. Moonshot recommends <code>temperature=1.0</code> and <code>top_p=0.95</code>.'),
        ('Does Kimi K2.7 Code support tool calls?',
         'Yes. K2.7 Code supports interleaved thinking and multi-step tool calls, which suits coding agents. In multi-turn chats and tool calls, send the full assistant message (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.'),
        faq_cc('Kimi K2.7 Code', s),
        ('Kimi K2.7 Code or Kimi K3: which should I use?',
         f'K2.7 Code is a 1T-parameter coding model with 256K context at {p(s, 0)} input and {p(s, 1)} output on AnyAIGC, suited to everyday coding and high-volume agent calls. <a href="/en/models/kimi-k3">Kimi K3</a> is the 2.8T-parameter flagship with 1M context at {p("kimi-k3", 0)} input and {p("kimi-k3", 1)} output, suited to large repos and the hardest tasks. Both use the same key.'),
        faq_rpm('Kimi K2.7 Code', s),
    ] + faq_common('Kimi K2.7 Code', s)
    return dict(
        title='Kimi K2.7 Code API Pricing | Agentic Coding Model - AnyAIGC',
        desc=f'kimi-k2.7-code API: Moonshot\'s coding agent model. Input {p(s, 0)}/1M, output {p(s, 1)}/1M, works in Claude Code, unlimited concurrency, bank transfer.',
        og_desc=f'kimi-k2.7-code at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 40% of Moonshot official prices. 21.8% higher than K2.6 on Kimi Code Bench v2, works in Claude Code.',
        og_alt='AnyAIGC Kimi K2.7 Code API at about 60% off official prices',
        keywords='Kimi K2.7 Code API,kimi-k2.7-code,Kimi K2.7 Code pricing,Kimi coding model API,Kimi K2.7 Code Claude Code,Kimi coding API,K2.7 Code vs K2.6,Kimi API,Kimi K2.7 Code API for business,Kimi K2.7 Code API invoice,AnyAIGC',
        crumb='Kimi K2.7 Code API', product='Kimi K2.7 Code API (AnyAIGC)', sku=s,
        product_desc='Moonshot AI Kimi K2.7 Code (kimi-k2.7-code) through AnyAIGC: OpenAI-compatible /v1/chat/completions, 256K context, per-token billing at about 40% of official prices, unlimited concurrency.',
        offers=offers(s),
        hero=dict(eyebrow='Moonshot AI · kimi-k2.7-code',
                  h1='Kimi K2.7 <span class="k-blue">Code</span><span class="o-sr"> API</span>',
                  lead='Kimi\'s coding agent model. It follows instructions more reliably over long context and completes more coding tasks. On AnyAIGC it costs about 40% of the official price.',
                  ask='Run the tests, find out why test_checkout fails, and fix it',
                  chips=['Coding agent', 'Interleaved thinking', '256K'],
                  sub=f'<code>kimi-k2.7-code</code> input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, about a third of K3. Works with the OpenAI-compatible API and in Claude Code.',
                  facts=[('Model ID', s), ('Context', '256K tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About', h2='K2.6, further trained for coding',
                   paras=['Moonshot AI calls Kimi K2.7 Code its strongest coding model so far. It is further trained from K2.6, follows instructions more reliably over long context, completes more coding tasks, and uses about 30% fewer thinking tokens than K2.6.',
                          'The architecture matches K2.6: MoE with 1T total and 32B active parameters, 8 of 384 experts per token, 256K context, and text and image input. K2.7 Code always thinks and supports interleaved thinking with multi-step tool calls, which suits coding agents.',
                          'On AnyAIGC, <code>kimi-k2.7-code</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint and works directly in Claude Code, with unlimited concurrency.'],
                   spec=[('Context window', '262,144', '256K tokens'), ('Total parameters', '1T', '32B active, MoE'),
                         ('Input', 'Text, images', 'Native multimodal'), ('Thinking', 'Always on', 'No non-thinking mode'),
                         ('Recommended', 'temperature 1.0', 'top_p 0.95'), ('Weights', 'Open', 'Modified MIT license')]),
        features=dict(kicker='Capabilities', h2='What Kimi K2.7 Code can do',
                      items=[('Higher coding success', 'Moonshot reports Kimi Code Bench v2 up from 50.9 on K2.6 to 62.0, and Program Bench up from 48.3 to 53.6.'),
                             ('Instruction following at length', 'Sticks to complex instructions across a 256K context and is less likely to drift in long sessions.'),
                             ('Fewer thinking tokens', 'Moonshot says it uses about 30% fewer thinking tokens than K2.6, so the same task costs less output.'),
                             ('Interleaved thinking with tools', 'Thinks between every tool call, which fits the run-tests, read-errors, fix-code loop. MCP Mark Verified 81.1.'),
                             ('Code from images', 'Accepts image input, so it can write and fix code from design files, screenshots or error screens.'),
                             ('Built for volume', f'Input {p(s, 0)} and cache hit {p(s, 2)} per 1M tokens. AnyAIGC does not cap concurrency, so many agents can run at once.')]),
        pricing=dict(kicker='Pricing', h2='Kimi K2.7 Code API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. Input, output and cache hits all cost about 40% of Moonshot\'s official USD prices.',
                     billing_label='Billing basics', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption='kimi-k2.7-code prices per 1M tokens (USD), AnyAIGC vs Moonshot official',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(s, '50 coding agent turns', 'Each turn: 40K cache-hit tokens + 4,000 input + 2,000 output', 4000, 2000, 40000, 50),
                            cost_card(s, 'Review 100 PRs', 'Each PR: 20K input tokens + 2,000 output', 20000, 2000, 0, 100),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='Where it beats K2.6', lead='K2.7 Code vs K2.6 scores published by Moonshot AI. It improves on every coding and tool-use task listed.',
                   chart=('Kimi Code Bench v2 · coding', [('Kimi K2.7 Code', 62.0, True), ('Kimi K2.6', 50.9, False)]),
                   head=[('Benchmark', ''), ('K2.7 Code', 'o-num o-hl'), ('K2.6', 'o-num')],
                   rows=[('Kimi Code Bench v2', 'Coding', '62.0', '50.9'), ('Program Bench', 'Coding', '53.6', '48.3'),
                         ('MLS Bench Lite', 'ML engineering', '35.1', '26.7'), ('Kimi Claw 24/7', 'Long-running agent', '46.9', '42.9'),
                         ('MCP Atlas', 'Tool use', '76.0', '69.4'), ('MCP Mark Verified', 'Tool use', '81.1', '72.8')],
                   caption='Kimi K2.7 Code vs Kimi K2.6 benchmarks (published by Moonshot AI)',
                   note='Source: the <a href="https://huggingface.co/moonshotai/Kimi-K2.7-Code" target="_blank" rel="noopener">Kimi K2.7 Code model card on Hugging Face</a>.'),
        compare=dict(kicker='Compare', h2='Kimi K2.7 Code vs K2.6 vs K3', lead='Use K2.7 Code for coding, K2.6 when thinking should be off, and K3 for large repos and the hardest tasks.',
                     head=[('Spec', ''), ('K2.7 Code', 'o-num o-hl'), ('K2.6', 'o-num'), ('K3', 'o-num')],
                     rows=[('Role', '', 'Coding agent', 'General multimodal agent', 'Flagship general'), ('Context', '', '256K', '256K', '1M'),
                           ('Thinking', '', 'Always on', 'On or off', 'Always on'),
                           ('AnyAIGC input', 'per 1M tokens', p(s, 0), p('kimi-k2.6', 0), p('kimi-k3', 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(s, 1), p('kimi-k2.6', 1), p('kimi-k3', 1)),
                           ('Cache hit', 'per 1M tokens', p(s, 2), p('kimi-k2.6', 2), p('kimi-k3', 2))],
                     caption='Kimi K2.7 Code, K2.6 and K3 compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Moonshot AI\'s public materials. Prices are current AnyAIGC prices; see the model catalog for live pricing. More on the <a href="/en/models/kimi-k3">Kimi K3 API</a>.'),
        uses=dict(kicker='Use cases', h2='Where Kimi K2.7 Code fits',
                  items=[('01 · Claude Code', 'A coding partner in your terminal', 'Switch Claude Code to K2.7 Code to read code, fix bugs and write tests at about a third of K3\'s price.'),
                         ('02 · CI', 'Auto-fix and code review', 'Review PRs, fix failing tests and write change summaries inside your pipeline. AnyAIGC does not cap concurrency, so large parallel batches work.'),
                         ('03 · Front end', 'Design files to components', 'Upload a design or page screenshot, generate React, Vue or plain HTML/CSS components, then iterate against the render.'),
                         ('04 · ML engineering', 'Experiment scripts and data work', 'About 31% higher than K2.6 on MLS Bench Lite. Good for training scripts, data cleaning and evaluation code.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the Kimi K2.7 Code API in three steps', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, 'Write an LRU cache in Python with unit tests.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, 'You are a senior backend engineer. Answer with runnable code.', 'Write an HTTP client in Go with timeouts and retries.')),
                      ('tools', 'Tool calls', 'Python · tools', code_tools(s)),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream(s, 'Explain this regex: ^(?=.*\\\\d)(?=.*[a-z]).{8,}$'))],
                callout='<strong>Tip:</strong> K2.7 Code always thinks, and the reasoning comes back in <code>reasoning_content</code>. Moonshot recommends <code>temperature=1.0</code> and <code>top_p=0.95</code>. In multi-turn chats and tool calls, send the full assistant message from the API (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.',
                note=QS_NOTE),
        cc=cc('Kimi K2.7 Code', s, 'Switch Claude Code to Kimi K2.7 Code. It is trained for coding and costs about a third of K3.',
              '<strong>For large repos:</strong> K2.7 Code has a 256K context. If a project is too big to read in one go, switch the model in the config to <code>kimi-k3</code> (1M context).'),
        family_h2='Other Kimi models', family_lead=FAMILY_LEAD,
        faq_h2='Kimi K2.7 Code API FAQ', faqs=faqs,
        final=dict(h2='Run Kimi K2.7 Code at about 40% of the official price', p='Sign up, create an API key, and you can use kimi-k2.7-code in your code or Claude Code within minutes.', other='Kimi K2.7 Code API 中文版'),
        ent_name='Kimi K2.7 Code',
    )


# ======================================================================
# Kimi K2.6
# ======================================================================
def k26():
    s = 'kimi-k2.6'
    faqs = [
        ('How much does the Kimi K2.6 API cost?',
         f'On AnyAIGC, <code>kimi-k2.6</code> is billed per token: input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)} per 1M tokens. '
         f'Moonshot\'s official USD prices are input {o(s, 0)}, output {o(s, 1)} and cache hit {o(s, 2)}, so AnyAIGC is about 40% of official. See the model catalog for live pricing.'),
        ('What is the Kimi K2.6 model ID, and how large is the context?',
         'The model ID is <code>kimi-k2.6</code>. Moonshot lists a 262,144-token (256K) context window, with text and image input.'),
        ('Can I turn off thinking in Kimi K2.6?',
         'K2.6 supports both thinking and non-thinking (Instant) modes. On Moonshot\'s API, <code>thinking: {"type": "disabled"}</code> turns thinking off; with the OpenAI SDK, pass it in <code>extra_body</code>. Moonshot recommends <code>temperature=1.0</code> for thinking mode and <code>temperature=0.6</code> for non-thinking mode, with <code>top_p</code> 0.95 for both.'),
        ('What sets Kimi K2.6 apart?',
         'Moonshot positions K2.6 as an open native multimodal agent model with four focus areas: long-horizon coding (Rust, Go, Python, front end, DevOps and performance tuning), production-ready UI from prompts or images, Agent Swarm (scaling out to 300 sub-agents and 4,000 coordinated steps), and proactive agents that run in the background 24/7.'),
        ('Kimi K2.6 or K2.7 Code: which should I use?',
         f'They share an architecture and cost the same for input and output on AnyAIGC. <a href="/en/models/kimi-k2.7-code">K2.7 Code</a> is K2.6 further trained for coding, with higher coding scores and fewer thinking tokens, but it only runs in thinking mode. K2.6 can turn thinking off, which fits fast chat, classification, extraction and general agents.'),
        faq_cc('Kimi K2.6', s),
        ('Does Kimi K2.6 support tool calls and image input?',
         'Yes. K2.6 supports multi-step tool calls, streaming and image input. In thinking mode, for multi-turn chats and tool calls, send the full assistant message (including <code>reasoning_content</code> and <code>tool_calls</code>) back in the next request unchanged.'),
        faq_rpm('Kimi K2.6', s),
    ] + faq_common('Kimi K2.6', s)
    return dict(
        title='Kimi K2.6 API Pricing & Access | Multimodal Agent - AnyAIGC',
        desc=f'kimi-k2.6 API: Moonshot\'s open multimodal agent model, thinking on or off. Input {p(s, 0)}/1M, output {p(s, 1)}/1M, unlimited concurrency, bank transfer.',
        og_desc=f'kimi-k2.6 at {p(s, 0)}/1M input and {p(s, 1)}/1M output, about 40% of Moonshot official prices. SWE-Bench Verified 80.2, thinking on or off, works in Claude Code.',
        og_alt='AnyAIGC Kimi K2.6 API at about 60% off official prices',
        keywords='Kimi K2.6 API,kimi-k2.6,Kimi K2.6 API pricing,Kimi K2.6 API key,Kimi K2.6 multimodal,Kimi K2.6 thinking mode,Kimi K2.6 agent,Kimi K2.6 Claude Code,Kimi API,Kimi K2.6 API for business,Kimi K2.6 API invoice,AnyAIGC',
        crumb='Kimi K2.6 API', product='Kimi K2.6 API (AnyAIGC)', sku=s,
        product_desc='Moonshot AI Kimi K2.6 (kimi-k2.6) through AnyAIGC: OpenAI-compatible /v1/chat/completions, 256K context, thinking on or off, per-token billing at about 40% of official prices, unlimited concurrency.',
        offers=offers(s),
        hero=dict(eyebrow='Moonshot AI · kimi-k2.6',
                  h1='Kimi <span class="k-blue">K2.6</span><span class="o-sr"> API</span>',
                  lead='An open native multimodal agent model for long-horizon coding, UI generation and agent swarms, with thinking on or off. On AnyAIGC it costs about 40% of the official price.',
                  ask='Build a responsive landing page from this design and wire up form validation',
                  chips=['Multimodal', 'Thinking on / off', 'Agent Swarm'],
                  sub=f'<code>kimi-k2.6</code> input {p(s, 0)} per 1M tokens, output {p(s, 1)} per 1M tokens, cache hit {p(s, 2)}. Works with the OpenAI-compatible API and in Claude Code.',
                  facts=[('Model ID', s), ('Context', '256K tokens'), ('Input', f'{p(s, 0)} / 1M'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')]),
        about=dict(kicker='About', h2='A general-purpose open multimodal agent model',
                   paras=['Moonshot AI positions Kimi K2.6 as an open native multimodal agent model. Moonshot says it writes long code more capably and more consistently, with clear gains in instruction following and self-correction. It takes text and image input and has thinking and non-thinking modes, so it works for chat and agent tasks alike.',
                          'Under the hood it is MoE with 1T total and 32B active parameters, 256K context and native INT4 quantization. Moonshot highlights four areas: long-horizon coding, UI from prompts or images (Coding-Driven Design), Agent Swarm scaling out to 300 sub-agents, and proactive agents that run 24/7.',
                          'On AnyAIGC, <code>kimi-k2.6</code> runs on the OpenAI-compatible <code>/v1/chat/completions</code> endpoint and works directly in Claude Code, with unlimited concurrency.'],
                   spec=[('Context window', '262,144', '256K tokens'), ('Total parameters', '1T', '32B active, MoE'),
                         ('Input', 'Text, images', 'Native multimodal'), ('Thinking', 'On or off', 'Thinking / non-thinking (Instant)'),
                         ('Recommended', 'temperature 1.0', 'Non-thinking 0.6, top_p 0.95'), ('Weights', 'Open', 'Modified MIT license')]),
        features=dict(kicker='Capabilities', h2='What Kimi K2.6 can do',
                      items=[('Long-horizon coding', 'Covers Rust, Go, Python, front end, DevOps and performance tuning. Moonshot reports 80.2 on SWE-Bench Verified and 58.6 on SWE-Bench Pro.'),
                             ('UI from images', 'Generates production-ready UI code from prompts or design files, for landing pages, admin panels and components.'),
                             ('Agent Swarm', 'Moonshot demonstrates scaling out to 300 sub-agents and 4,000 coordinated steps. AnyAIGC does not cap concurrency, which suits parallel agents.'),
                             ('Thinking on or off', 'Turn thinking on for hard problems and off for classification, extraction and support chat, for faster replies and less output.'),
                             ('Search and research', 'Moonshot reports 83.2 on BrowseComp (86.3 with Agent Swarm) and 92.5 f1 on DeepSearchQA, a good fit for deep-search agents.'),
                             ('Math and reasoning', 'Moonshot reports 96.4 on AIME 2026 and 90.5 on GPQA-Diamond.')]),
        pricing=dict(kicker='Pricing', h2='Kimi K2.6 API pricing', lead='Pay per token at fixed rates, with no subscription or monthly fee. Input, output and cache hits all cost about 40% of Moonshot\'s official USD prices.',
                     billing_label='Billing basics', billing=BILLING,
                     head=PRICE_HEAD, labels=LABELS, caption='kimi-k2.6 prices per 1M tokens (USD), AnyAIGC vs Moonshot official',
                     note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                     costs=[cost_card(s, 'Classify 10,000 tickets', 'Each ticket: 2,000 input tokens + 300 output', 2000, 300, 0, 10000),
                            cost_card(s, '1,000 support chat turns', 'Each turn: 8,000 cache-hit tokens + 1,000 input + 500 output', 1000, 500, 8000, 1000),
                            cost_card(s, '1M input + 1M output', '1M input tokens + 1M output tokens', 1000000, 1000000)]),
        bench=dict(kicker='Benchmarks', h2='Kimi K2.6 official benchmarks', lead='Kimi K2.6 scores published by Moonshot AI across coding, agent, reasoning and vision tasks.',
                   chart=('Kimi K2.6 · selected benchmarks', [('SWE-Bench Verified', 80.2, True), ('LiveCodeBench v6', 89.6, True), ('BrowseComp', 83.2, True),
                                                              ('AIME 2026', 96.4, True), ('GPQA-Diamond', 90.5, True)]),
                   head=[('Benchmark', ''), ('Kimi K2.6', 'o-num o-hl')],
                   rows=[('SWE-Bench Verified', 'Software engineering', '80.2'), ('SWE-Bench Pro', 'Software engineering', '58.6'), ('SWE-Bench Multilingual', 'Multilingual coding', '76.7'),
                         ('Terminal-Bench 2.0', 'Terminal coding', '66.7'), ('LiveCodeBench v6', 'Competitive coding', '89.6'),
                         ('HLE-Full', 'General reasoning, with tools', '54.0'), ('BrowseComp', 'Web browsing agent', '83.2'), ('DeepSearchQA', 'Deep search, f1', '92.5'),
                         ('AIME 2026', 'Math', '96.4'), ('GPQA-Diamond', 'Science reasoning', '90.5'), ('MMMU-Pro', 'Multimodal understanding', '79.4'), ('OSWorld-Verified', 'Computer use', '73.1')],
                   caption='Kimi K2.6 official benchmark scores (published by Moonshot AI)',
                   note='Source: the <a href="https://huggingface.co/moonshotai/Kimi-K2.6" target="_blank" rel="noopener">Kimi K2.6 model card on Hugging Face</a>. BrowseComp is 86.3 in the Agent Swarm setting.'),
        compare=dict(kicker='Compare', h2='Kimi K2.6 vs K2.7 Code vs K3', lead='Use K2.6 for general tasks or when thinking should be off, K2.7 Code for focused coding, and K3 for the hardest tasks.',
                     head=[('Spec', ''), ('K2.6', 'o-num o-hl'), ('K2.7 Code', 'o-num'), ('K3', 'o-num')],
                     rows=[('Role', '', 'General multimodal agent', 'Coding agent', 'Flagship general'), ('Context', '', '256K', '256K', '1M'),
                           ('Thinking', '', 'On or off', 'Always on', 'Always on'),
                           ('AnyAIGC input', 'per 1M tokens', p(s, 0), p('kimi-k2.7-code', 0), p('kimi-k3', 0)),
                           ('AnyAIGC output', 'per 1M tokens', p(s, 1), p('kimi-k2.7-code', 1), p('kimi-k3', 1)),
                           ('Cache hit', 'per 1M tokens', p(s, 2), p('kimi-k2.7-code', 2), p('kimi-k3', 2))],
                     caption='Kimi K2.6, K2.7 Code and K3 compared; prices are AnyAIGC USD per 1M tokens',
                     note='Specs come from Moonshot AI\'s public materials. Prices are current AnyAIGC prices; see the model catalog for live pricing. More on the <a href="/en/models/kimi-k2.7-code">Kimi K2.7 Code API</a>.'),
        uses=dict(kicker='Use cases', h2='Where Kimi K2.6 fits',
                  items=[('01 · Batch jobs', 'Classification, extraction and summaries', 'Turn thinking off for ticket triage, field extraction and review tagging: fast replies, short outputs. AnyAIGC does not cap concurrency.'),
                         ('02 · UI generation', 'Design files to live pages', 'Upload a design or reference screenshot and generate landing pages, admin screens and component code.'),
                         ('03 · Multi-agent', 'Agent Swarm and background jobs', 'Split a large task across sub-agents running in parallel, or keep an agent monitoring, organizing and reporting in the background 24/7.'),
                         ('04 · Coding', 'Everyday coding and Claude Code', 'Use K2.6 in Claude Code to read code and fix bugs. For a higher coding success rate, switch to K2.7 Code at the same price.')]),
        qs=dict(kicker='Quickstart', h2='Connect to the Kimi K2.6 API in three steps', steps=qs_steps(s),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(s, 'Explain what a database index is in three sentences.')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(s, 'You are a senior front-end engineer. Answer with runnable code.', 'Write an accessible dropdown menu component.')),
                      ('vision', 'Image input', 'Python · image_url', code_vision(s)),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream(s, 'Write 5 changelog entries for a SaaS product.'))],
                callout='<strong>Tip:</strong> K2.6 thinks by default, and the reasoning comes back in <code>reasoning_content</code>. On Moonshot\'s API, <code>thinking: {"type": "disabled"}</code> turns thinking off (pass it in <code>extra_body</code> with the OpenAI SDK); Moonshot recommends <code>temperature=0.6</code> in non-thinking mode. In thinking mode, for multi-turn chats and tool calls, send the full assistant message back in the next request unchanged.',
                note=QS_NOTE),
        cc=cc('Kimi K2.6', s, 'Switch Claude Code to Kimi K2.6. It is multimodal and low cost, good for everyday coding and fixing UI from screenshots.',
              '<strong>Switch to the coding model:</strong> for a higher coding success rate, replace <code>kimi-k2.6</code> in the config with <code>kimi-k2.7-code</code>. Both cost the same.'),
        family_h2='Other Kimi models', family_lead=FAMILY_LEAD,
        faq_h2='Kimi K2.6 API FAQ', faqs=faqs,
        final=dict(h2='Run Kimi K2.6 at about 40% of the official price', p='Sign up, create an API key, and you can use kimi-k2.6 in your code or Claude Code within minutes.', other='Kimi K2.6 API 中文版'),
        ent_name='Kimi K2.6',
    )
