# SparkDesk (iFlytek Spark) series topic pages, English copy. Used by scripts/spark_pages.py.
# Prices come from spark_data.PRICE (model catalog detail drawer, read 2026-11-13); official specs come from iFLYTEK's Web.html doc.
# No official list price was verified, so the pages show no official comparison price or discount.
# SparkDesk-v2.1 has no official source for its specs, so only the catalog description is used.
# Do not claim "works from mainland China" on English pages.
from spark_data import PRICE, MODELS, REG, PRICING, SUPPORT, DOCS_CHAT, OFFICIAL_DOC
from spark_layout import cost, money

MARKET = PRICING + '?provider=Spark'


def p(slug, i):
    return f'${PRICE[slug][i]}'


def faq_common(name, slug):
    mid = MODELS[slug]['id']
    return [
        (f'How do I get a {name} API key?',
         f'Sign up and top up at <a href="{REG}">anyaigc.ai</a>, then create a token in the console. One key works for 300+ models on the platform, so you do not need an iFLYTEK Open Platform APPID, APIKey and APISecret. Set <code>model</code> to <code>{mid}</code> in the request body.'),
        ('Can AnyAIGC issue invoices, including VAT special invoices?',
         'Yes. AnyAIGC can issue invoices for every top-up, including Chinese VAT general invoices and VAT special invoices. Send your invoicing details to support.'),
        ('Can my company pay by bank transfer and sign a contract?',
         f'Yes. You can top up by corporate bank transfer and sign a service agreement, with a dedicated support contact and technical contact. For company purchases, <a href="{SUPPORT}">contact AnyAIGC support</a>.'),
        ('Are my prompts used for training?',
         'No. Unless the law requires it, AnyAIGC does not persistently store your prompts or outputs and does not use them for training. Requests are encrypted with HTTPS. See the AnyAIGC <a href="/privacy">Privacy Policy</a>. The model vendor\'s own data policy is governed by iFLYTEK\'s terms.'),
    ]


def faq_rpm(name, slug):
    return ('Is there a rate limit?',
            f'AnyAIGC sets no concurrency limit on <code>{MODELS[slug]["id"]}</code>, and every account gets this by default, so batch jobs and parallel tasks are fine. Billing is per token, with no monthly fee or time-window quota.')


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
print(resp.usage)  # input / output tokens for this request'''


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
    return ['<strong>Sign up and top up</strong>: create an account at <a href="' + REG + '">anyaigc.ai</a>. Top-ups start at $1, and the balance works across every model on the platform.',
            '<strong>Create an API key</strong>: make a token in the console, copy the key that starts with <code>sk-</code>, and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Send a request</strong>: call <code>POST https://anyaigc.ai/v1/chat/completions</code> with <code>model</code> set to <code>{model}</code> and <code>Authorization: Bearer</code>. With the OpenAI SDK, just set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>.']


QS_NOTE = f'See the <a href="{DOCS_CHAT}" target="_blank" rel="noopener">Chat Completions reference</a> for every parameter. Swap the model name in the examples for the SparkDesk model ID.'
PRICE_HEAD = [('Item', ''), ('Model', ''), ('AnyAIGC price (USD)', 'o-num o-hl')]
LABELS = [('Input', 'per 1M tokens'), ('Output', 'per 1M tokens')]


def pricing_note(slug):
    return f'Prices are in US dollars and billed on the tokens you actually use. Input and output cost the same. These are the lowest catalog prices; live prices are on the <a href="{MARKET}">AnyAIGC model catalog</a>.'


def billing(slug):
    return [('Per-token billing', 'Input and output metered separately'), ('Same input and output price', f'{p(slug, 0)} per 1M each'),
            ('Unlimited RPM', 'On by default for every account'), ('USD', 'One balance for 300+ models')]


def costs(slug):
    return [
        ('10,000 support answers', '800 input + 300 output tokens each', money(cost(slug, 800, 300, 10000))),
        ('One long-document summary', '6,000 input + 800 output tokens', money(cost(slug, 6000, 800))),
        ('1M input + 1M output', '1M input tokens + 1M output tokens', money(cost(slug, 1000000, 1000000))),
    ]


def offers(slug):
    return [('Input (per 1M tokens)', PRICE[slug][0]), ('Output (per 1M tokens)', PRICE[slug][1])]


FAMILY = [
    ('sparkdesk-v3.5', 'Latest', f'iFLYTEK Spark Max tier, the newest of the three · input {p("sparkdesk-v3.5", 0)} / 1M'),
    ('sparkdesk-v3.1', '', f'iFLYTEK Spark Pro tier for chat and Q&A · input {p("sparkdesk-v3.1", 0)} / 1M'),
    ('sparkdesk-v2.1', 'Legacy', f'Early 2.x release for existing workloads · input {p("sparkdesk-v2.1", 0)} / 1M'),
]

COMPARE_HEAD = [('Item', ''), ('SparkDesk-v3.5', 'o-num o-hl'), ('SparkDesk-v3.1', 'o-num'), ('SparkDesk-v2.1', 'o-num')]


def compare_rows():
    a, b, c = 'sparkdesk-v3.5', 'sparkdesk-v3.1', 'sparkdesk-v2.1'
    return [('iFLYTEK tier', '', 'Spark Max', 'Spark Pro', 'Early 2.x release'),
            ('API version', '', 'v3.5', 'v3.1', 'v2.1'),
            ('Context / max output', 'official doc', '8,192 / 8,192', '8,192 / 8,192', 'Not listed'),
            ('System prompt (system role)', 'official doc', 'Supported', 'Not supported', 'Not listed'),
            ('AnyAIGC input', 'per 1M tokens', p(a, 0), p(b, 0), p(c, 0)),
            ('AnyAIGC output', 'per 1M tokens', p(a, 1), p(b, 1), p(c, 1))]


COMPARE_NOTE = ('Tiers and specs come from the <a href="' + OFFICIAL_DOC + '" target="_blank" rel="noopener">iFLYTEK Open Platform docs</a>. Prices are AnyAIGC\'s current prices; live prices are in the model catalog. '
                'Details: <a href="/en/models/sparkdesk-v3.5">SparkDesk-v3.5</a>, <a href="/en/models/sparkdesk-v3.1">SparkDesk-v3.1</a>, <a href="/en/models/sparkdesk-v2.1">SparkDesk-v2.1</a>.')

M = {
    'sparkdesk-v3.5': dict(
        title='SparkDesk-v3.5 API Pricing | iFlytek Spark Max - AnyAIGC',
        tier='Spark Max', mid='SparkDesk-v3.5',
        desc_lead='iFLYTEK Spark Max tier (API version v3.5) for chat, knowledge Q&A, reasoning and code understanding',
        short='iFLYTEK Spark Max tier for chat, Q&A and code',
        notice=f'iFLYTEK\'s docs say the Max plan went offline on March 10, 2026, with the backend upgraded to Ultra. SparkDesk-v3.5 is still callable in the AnyAIGC <a href="{MARKET}">model catalog</a>; check the catalog for current availability.',
        ask='Turn these support chats into ticket summaries and suggest next steps',
        answer="Ticket summary: The customer paid three days ago and the order still shows Pending shipment. They contacted the warehouse twice with no reply and want it shipped or refunded.\nNext steps:\n1. Contact the warehouse today to confirm stock and the ship date.\n2. Tell the customer the expected date and apologize.\n3. If it still cannot ship within 48 hours, offer a refund or compensation.",
        chips=['Multi-turn chat', 'Knowledge Q&A', 'Code understanding'],
        about_h2='The 3.5 release of iFLYTEK Spark Max',
        about=['SparkDesk-v3.5 is the 3.5 API release of iFLYTEK\'s Spark cognitive model and maps to the official Spark Max tier. The catalog describes it as a model with cross-domain knowledge and language understanding that carries out tasks through natural conversation, covering language understanding, knowledge Q&A, logical reasoning, math problem solving and code comprehension.',
               'iFLYTEK\'s docs list an 8,192-token context window and an 8,192-token maximum output for this tier, with system prompts (Max and Ultra only) and a web search plugin (Pro, Max and Ultra). The doc says function calling requires the HTTP protocol and does not list it by tier. What works through AnyAIGC in practice is best confirmed in the API docs and with a test request.',
               'On AnyAIGC, <code>SparkDesk-v3.5</code> uses the OpenAI-compatible <code>/v1/chat/completions</code> endpoint with a single Bearer key. You do not need an iFLYTEK APPID, APIKey and APISecret or the official WebSocket signing. Billing is per token with no concurrency limit.'],
        spec=[('Model ID', 'SparkDesk-v3.5', 'the model field, case-sensitive'), ('Official tier', 'Spark Max', 'domain: generalv3.5'),
              ('Context window', '8,192', 'tokens, per official doc'), ('Max output', '8,192', 'tokens, per official doc'),
              ('Endpoint', 'Chat Completions', 'POST /v1/chat/completions')],
        feat_h2='What SparkDesk-v3.5 can do',
        feats=[('Multi-turn conversation', 'Understands and carries out tasks through natural conversation, a fit for support bots and assistants.'),
               ('Knowledge Q&A', 'Cross-domain question answering across common reference, office and industry topics.'),
               ('Logical reasoning', 'Works through multi-step conditions, rule checks and comparisons, then states a conclusion.'),
               ('Math problem solving', 'The catalog lists math problem solving, useful for tutoring and formula questions.'),
               ('Code understanding', 'Explains snippets, spots obvious errors and completes simple functions for developer tools.'),
               ('System prompt', 'The official doc lists the system role for the Max tier, so you can fix a persona and answer rules.')],
        uses=[('01 · Support', 'Support answers and ticket summaries', 'Pass a customer question and chat history to SparkDesk-v3.5 for a draft reply or a ticket summary, then have a person review it before sending.'),
              ('02 · Knowledge base', 'Document and knowledge-base Q&A', 'Put retrieved passages in the prompt and let the model answer from them. The context is about 8K tokens, so split long documents first.'),
              ('03 · Writing', 'Copy rewriting and polishing', 'Rewrite marketing copy, notices and emails. Input and output cost the same, so batch costs are easy to estimate.'),
              ('04 · Development', 'Code explanation and simple completion', 'Add code explanation or comment generation to an internal tool. For heavier engineering work, pick a model with a longer context.')],
        final_h2='Call SparkDesk-v3.5 with one key',
    ),
    'sparkdesk-v3.1': dict(
        title='SparkDesk-v3.1 API Pricing | iFlytek Spark Pro - AnyAIGC',
        tier='Spark Pro', mid='SparkDesk-v3.1',
        desc_lead='iFLYTEK Spark Pro tier (API version v3.1) for chat, knowledge Q&A, reasoning and code understanding',
        short='iFLYTEK Spark Pro tier for chat, Q&A and math',
        notice=None,
        ask='Write three promotional posts for a social account from this product description',
        answer="1. Five minutes a day is all it takes to sort out your to-dos. Try our task list and keep work on track.\n2. Never time to organize? Import in one click, auto-sort, and finish today's tasks today.\n3. Productivity is not overtime. The right tool lets you wrap up before you leave.",
        chips=['Chat Q&A', 'Copy rewriting', 'Math help'],
        about_h2='The 3.1 release of iFLYTEK Spark Pro',
        about=['SparkDesk-v3.1 is the 3.1 API release of iFLYTEK\'s Spark cognitive model and maps to the official Spark Pro tier. The catalog describes it as a model with cross-domain knowledge and language understanding that carries out tasks through natural conversation, covering language understanding, knowledge Q&A, logical reasoning, math problem solving and code comprehension.',
               'iFLYTEK\'s docs list an 8,192-token context window and an 8,192-token maximum output for this tier. The docs limit the system role to Max and Ultra, and list the web search plugin for Pro. If your app needs a fixed system prompt, use <a href="/en/models/sparkdesk-v3.5">SparkDesk-v3.5</a> instead.',
               'On AnyAIGC, <code>SparkDesk-v3.1</code> uses the OpenAI-compatible <code>/v1/chat/completions</code> endpoint with a single Bearer key, with no iFLYTEK APPID, APIKey or APISecret needed. Billing is per token with no concurrency limit.'],
        spec=[('Model ID', 'SparkDesk-v3.1', 'the model field, case-sensitive'), ('Official tier', 'Spark Pro', 'domain: generalv3'),
              ('Context window', '8,192', 'tokens, per official doc'), ('Max output', '8,192', 'tokens, per official doc'),
              ('Endpoint', 'Chat Completions', 'POST /v1/chat/completions')],
        feat_h2='What SparkDesk-v3.1 can do',
        feats=[('Natural conversation', 'Understands and carries out tasks through conversation, a fit for Q&A bots and assistants.'),
               ('Knowledge Q&A', 'Cross-domain question answering across common reference, office and industry topics.'),
               ('Logical reasoning', 'Works through rule checks and comparisons, then states a conclusion.'),
               ('Math problem solving', 'The catalog lists math problem solving, useful for tutoring and formula questions.'),
               ('Code understanding', 'Explains snippets and spots obvious errors for developer tools.'),
               ('Web search plugin', 'The official doc lists the web search plugin for Pro, Max and Ultra; the system role is limited to Max and Ultra.')],
        uses=[('01 · Q&A', 'Knowledge Q&A and assistants', 'Build a help assistant for staff or users, with your rules and reference text in the prompt so the model answers from them.'),
              ('02 · Writing', 'Copy and summaries', 'Social posts, product descriptions and meeting-note summaries. Input and output cost the same, so batch costs are easy to estimate.'),
              ('03 · Education', 'Math and study help', 'Step-by-step solutions and explanations, enough to validate a learning-app prototype.'),
              ('04 · Development', 'Code explanation', 'Add code explanation to an internal tool. Switch to SparkDesk-v3.5 if you need a system prompt.')],
        final_h2='Call SparkDesk-v3.1 with one key',
    ),
    'sparkdesk-v2.1': dict(
        title='SparkDesk-v2.1 API Pricing | iFlytek Spark 2.x - AnyAIGC',
        tier='Early 2.x release', mid='SparkDesk-v2.1',
        desc_lead='iFLYTEK Spark\'s early 2.x release (API version v2.1) for chat, knowledge Q&A, reasoning and code understanding',
        short='iFLYTEK Spark early 2.x release for chat and Q&A',
        notice=f'SparkDesk-v2.1 is an early iFLYTEK Spark release that the current iFLYTEK Open Platform version table no longer lists. New projects should look at <a href="/en/models/sparkdesk-v3.1">SparkDesk-v3.1</a> or <a href="/en/models/sparkdesk-v3.5">SparkDesk-v3.5</a>. Check the <a href="{MARKET}">model catalog</a> for current availability.',
        ask='Explain API rate limiting to a new teammate in three sentences, with an example',
        answer="API rate limiting caps how many requests one caller can send in a set time, so a single user cannot overload the service. Requests over the cap are rejected, usually with HTTP 429. For example, if the limit is 60 requests per minute, the 61st request in that minute gets a 429 and must wait for the next minute.",
        chips=['Chat Q&A', 'Lowest price', 'Existing apps'],
        about_h2='iFLYTEK Spark\'s early 2.x release',
        about=['SparkDesk-v2.1 is an early 2.x API release of iFLYTEK\'s Spark cognitive model. The catalog describes it as a model with cross-domain knowledge and language understanding that carries out tasks through natural conversation, covering language understanding, knowledge Q&A, logical reasoning, math problem solving and code comprehension.',
               'The current iFLYTEK Open Platform version table no longer lists this tier, so this page gives no official context window, maximum output or feature limits rather than print numbers without a source. It has the lowest price of the three on AnyAIGC, which suits workloads that already use it or low-cost tasks where quality matters less.',
               'On AnyAIGC, <code>SparkDesk-v2.1</code> uses the OpenAI-compatible <code>/v1/chat/completions</code> endpoint with a single Bearer key. For new projects, evaluate <a href="/en/models/sparkdesk-v3.1">SparkDesk-v3.1</a> or <a href="/en/models/sparkdesk-v3.5">SparkDesk-v3.5</a> first. Billing is per token with no concurrency limit.'],
        spec=[('Model ID', 'SparkDesk-v2.1', 'the model field, case-sensitive'), ('Official tier', 'Early 2.x', 'not in the current official doc'),
              ('Context window', 'Not listed', 'confirm by testing'), ('Max output', 'Not listed', 'confirm by testing'),
              ('Endpoint', 'Chat Completions', 'POST /v1/chat/completions')],
        feat_h2='What SparkDesk-v2.1 can do',
        feats=[('Natural conversation', 'Understands and carries out tasks through conversation, a fit for simple Q&A and assistants.'),
               ('Knowledge Q&A', 'Cross-domain question answering across common reference and office topics.'),
               ('Logical reasoning', 'Handles simple rule checks and comparisons.'),
               ('Math problem solving', 'The catalog lists math problem solving, useful for basic study help.'),
               ('Code understanding', 'Explains short snippets for lightweight developer help.'),
               ('Drop-in for existing apps', 'An app already calling SparkDesk-v2.1 only needs a new base_url and key. The model ID stays the same.')],
        uses=[('01 · Existing apps', 'Workloads that already use it', 'For an app running SparkDesk-v2.1 today, keep the model ID and point requests at AnyAIGC.'),
              ('02 · Low cost', 'Batch text where quality matters less', 'The lowest price of the three, a fit for simple classification or rewriting. Test on your own samples before launch.'),
              ('03 · Comparison', 'Old versus new release', 'Run the same prompts through v2.1, v3.1 and v3.5 to measure the gap before deciding whether to migrate.'),
              ('04 · Prototypes', 'Cheap prototype validation', 'Get a flow working on a low-priced model first, then move to a higher tier if the results call for it.')],
        final_h2='Call SparkDesk-v2.1 with one key',
    ),
}


def build(slug):
    m = M[slug]
    mid, name, tier = m['mid'], MODELS[slug]['name'], m['tier']
    s = slug
    price_in, price_out = p(s, 0), p(s, 1)
    others = [x for x in ('sparkdesk-v3.5', 'sparkdesk-v3.1', 'sparkdesk-v2.1') if x != s]
    link = lambda x: f'<a href="/en/models/{x}">{MODELS[x]["name"]}</a>'

    faqs = [
        (f'How much does the {name} API cost?',
         f'On AnyAIGC, <code>{mid}</code> is billed per token: {price_in} per million input tokens and {price_out} per million output tokens, the same for both. Prices are fixed, with no subscription or monthly fee. Live prices are in the model catalog.'),
        (f'What is the {name} model ID, and how does it relate to iFLYTEK Spark?',
         f'The model ID is <code>{mid}</code> (case-sensitive). It is a release of iFLYTEK\'s Spark cognitive model, and AnyAIGC exposes it through an OpenAI-compatible API. It is unrelated to Apache Spark or the Spark email app.'),
        (f'How do I choose between {name} and the other SparkDesk models?',
         f'{link(others[0])} and {link(others[1])} are the other two in the series. A higher version number maps to a newer iFLYTEK tier: v3.5 is Max, v3.1 is Pro, and v2.1 is an early 2.x release. '
         'Pick v3.5 if you need a system prompt. Consider v2.1 when cost matters most and quality needs are modest, and test on your own data before launch. All three charge the same for input and output on AnyAIGC.'),
        ('Is SparkDesk compatible with the OpenAI API, and how do I call it?',
         f'Yes. {name} uses <code>POST https://anyaigc.ai/v1/chat/completions</code>, and requests and responses match OpenAI Chat Completions. With the official OpenAI SDK, set <code>base_url</code> to <code>https://anyaigc.ai/v1</code>. You do not need iFLYTEK\'s WebSocket signing, only <code>Authorization: Bearer</code>.'),
        (f'How large is the {name} context window?',
         ('iFLYTEK\'s docs list an 8,192-token context window and an 8,192-token maximum output for this tier, so split long documents or retrieve passages before asking. Confirm actual behavior with a test request through AnyAIGC.' if s != 'sparkdesk-v2.1'
          else 'The current iFLYTEK Open Platform version table no longer lists the 2.x release, so there is no official context figure to quote. Test with your real input lengths, or choose SparkDesk-v3.1 or SparkDesk-v3.5 when you need documented limits.')),
        faq_rpm(name, s),
        (f'Is {name} deprecated?',
         {'sparkdesk-v3.5': 'iFLYTEK\'s docs say the Max plan went offline on March 10, 2026, with the backend upgraded to Ultra. SparkDesk-v3.5 is still callable in the AnyAIGC model catalog today; check the catalog for current availability.',
          'sparkdesk-v3.1': 'The current iFLYTEK Open Platform version table still lists the Pro tier. SparkDesk-v3.1 is callable in the AnyAIGC model catalog today; check the catalog for current availability.',
          'sparkdesk-v2.1': 'The current iFLYTEK Open Platform version table no longer lists the 2.x release, so treat it as a legacy model. SparkDesk-v2.1 is still callable in the AnyAIGC model catalog today. New projects should use SparkDesk-v3.1 or SparkDesk-v3.5; check the catalog for current availability.'}[s]),
    ] + faq_common(name, s)

    return dict(
        title=m['title'],
        desc=f'{mid} API: {m["short"]}. Input {price_in}/1M, output {price_out}/1M, unlimited RPM, bank transfer and VAT invoices.',
        og_desc=f'{mid} costs {price_in}/1M input and {price_out}/1M output. {m["desc_lead"]}. OpenAI-compatible, unlimited RPM, with bank transfer and VAT special invoices.',
        og_alt=f'AnyAIGC {mid} API: input {price_in}/1M, unlimited RPM',
        keywords=f'{mid} API,{mid},{mid} API pricing,{mid} API key,SparkDesk API,iFlytek Spark API,iFlytek Spark API pricing,Xinghuo API,Spark LLM API,iFlytek Spark OpenAI compatible,{mid} API for business,SparkDesk API for business,AnyAIGC',
        crumb=f'{mid} API', product=f'{mid} API (AnyAIGC)', sku=s,
        product_desc=f'Call iFLYTEK Spark {mid} through AnyAIGC: OpenAI-compatible /v1/chat/completions, billed per token, input {price_in}/1M and output {price_out}/1M, unlimited RPM.',
        offers=offers(s),
        hero=dict(eyebrow=f'iFLYTEK · {mid}',
                  h1=f'SparkDesk-<span class="sp-blue">{mid.split("-")[1]}</span><span class="o-sr"> API</span>',
                  lead=f'{m["desc_lead"][0].upper() + m["desc_lead"][1:]}. One API key, an OpenAI-compatible endpoint and the same price for input and output.',
                  ask=m['ask'], answer=m['answer'], chips=m['chips'],
                  sub=f'<code>{mid}</code> costs {price_in} per million input tokens and {price_out} per million output tokens, with unlimited RPM and bank transfer plus VAT special invoices for teams.',
                  notice=m['notice'],
                  facts=[('Model ID', mid), ('Official tier', tier), ('Input', f'{price_in} / 1M'), ('RPM', 'Unlimited'), ('Teams', 'Contracts · invoices')]),
        about=dict(kicker='About the model', h2=m['about_h2'], paras=m['about'], spec=[(a, b, c) for a, b, c in m['spec']] + [('Input / output', 'Same price', f'{price_in} per 1M tokens each')]),
        features=dict(kicker='Capabilities', h2=m['feat_h2'], items=m['feats']),
        pricing=dict(kicker='Pricing', h2=f'{name} API pricing', lead='Billed per token at a fixed price, with no subscription or monthly fee. Input and output cost the same.',
                     billing_label='Billing basics', billing=billing(s), head=PRICE_HEAD, labels=LABELS,
                     caption=f'{mid} price per 1M tokens in USD', note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead='Estimated for typical usage by adding up the unit prices above.', costs=costs(s)),
        compare=dict(kicker='Compare', h2='SparkDesk-v3.5, v3.1 or v2.1?', lead='Choose v3.5 for system prompts, v3.1 for general chat and Q&A, and v2.1 for existing apps and low-cost tasks.',
                     head=COMPARE_HEAD, rows=compare_rows(), caption='SparkDesk-v3.5, SparkDesk-v3.1 and SparkDesk-v2.1 compared, with AnyAIGC prices per 1M tokens in USD', note=COMPARE_NOTE),
        uses=dict(kicker='Use cases', h2=f'What {name} is good for', items=m['uses']),
        qs=dict(kicker='Quickstart', h2=f'Call the {name} API in three steps', steps=qs_steps(mid),
                tabs=[('curl', 'cURL', 'POST /v1/chat/completions', code_curl(mid, 'Explain API rate limiting in three sentences')),
                      ('py', 'Python · OpenAI SDK', 'Python · openai SDK', code_py(mid, 'You are a patient support engineer. Keep answers short and give an example.' if s == 'sparkdesk-v3.5' else None, 'A customer reports HTTP 429 from our API. How should I troubleshoot it?')),
                      ('stream', 'Streaming', 'Python · stream=True', code_stream(mid, 'Write five release notes for a SaaS product.'))],
                callout=f'<strong>Parameter tip:</strong> the model ID is case-sensitive, so write <code>{mid}</code>. The response format matches OpenAI Chat Completions, and token counts for the request are in the <code>usage</code> field. The context is limited, so split or retrieve long documents before asking.',
                note=QS_NOTE),
        family_h2='All SparkDesk models', family_lead='One API key calls every SparkDesk model below. Pick by quality and budget.',
        faq_h2=f'{name} API FAQ', faqs=faqs,
        final=dict(h2=m['final_h2'], p=f'Sign up, create an API key and call {mid} in minutes. Your balance works across 300+ models on the platform.', other=f'{mid} API 中文版'),
        ent_name=name,
    )
