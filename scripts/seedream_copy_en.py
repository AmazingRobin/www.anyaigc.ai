# English copy for the Seedream topic pages. build(slug) returns the dict consumed by seedream_layout.py.
# Prices are USD: the lowest price shown in the AnyAIGC model catalog (see seedream_data.USD).
from decimal import Decimal

from seedream_data import MODELS, MODEL_SLUGS, USD, SUPPORT, PRICING, DOCS, VOLC_DOC, usd
import seedream_layout as G

NL = '\n'
UNIT = {'张': 'image', '次': 'request'}


def money(d):
    """$22.30 for whole cents, otherwise keep 4 decimals ($0.3045)."""
    d = Decimal(d)
    if d == d.quantize(Decimal('0.01')):
        return f'${d:,.2f}'
    return f'${d:,.4f}'


def cost(n, slug):
    return f'{n:,} × {usd(slug)}', money(Decimal(USD[slug]) * n)


FAMILY = [
    ('seedream', 'Overview', 'All Seedream models', 'Pricing and specs for 5 models'),
    ('seedream-5.0-pro', 'Latest', 'Seedream 5.0 Pro', f'Infographics, precise edits, multilingual · from {usd("seedream-5.0-pro")} / image'),
    ('seedream-5.0-lite', 'Best value', 'Seedream 5.0 lite', f'Web search, image sets, 4K · from {usd("seedream-5.0-lite")} / image'),
    ('seedream-4.5', '', 'Seedream 4.5', f'Poster layouts, multi-image fusion · from {usd("seedream-4.5")} / image'),
    ('seedream-4.0', '', 'Seedream 4.0', f'Generation and editing in one · from {usd("seedream-4.0")} / image'),
    ('seedream-3.0', 'Legacy', 'Seedream 3.0', f'Text-to-image only · {usd("seedream-3.0")} / request'),
]

COMMON_FAQ = [
    ('Can AnyAIGC issue invoices, including VAT special invoices?',
     'Yes. AnyAIGC issues invoices for every top-up based on the amount actually paid, including Chinese VAT general and special invoices. Send your billing details to support to get started.'),
    ('Can my company pay by bank transfer and sign a contract?',
     f'Yes. Companies can top up by corporate bank transfer and sign a service agreement with AnyAIGC, with a dedicated support and technical contact. For procurement, <a href="{SUPPORT}">contact AnyAIGC sales</a>.'),
]
LICENSE_FAQ = ('Can I use the images commercially? Can I remove the watermark?',
               'Usage rights and content policies follow the official ByteDance / Volcano Engine terms. Set <code>watermark</code> to <code>false</code> in the request and no "AI generated" mark is added to the bottom-right corner. AnyAIGC only provides API access and adds no extra restrictions on how you use the output; for portraits of real people, brand logos and similar content, make sure you have the rights you need.')


def conc_faq(name):
    return ('Is there a concurrency limit? What do I need to sign up?',
            f'AnyAIGC sets no concurrency limit on {name}, and every account gets this by default. The base URL is <code>https://anyaigc.ai</code>. You do not need a Volcano Engine account or ID verification, and the same key also works with 300+ other models on the platform.')


def price_note(slug=None):
    return ('Prices are in USD and show the lowest price in the model catalog. Higher output resolution tiers such as 2K and 4K cost more; '
            f'see the live rates in the <a href="{PRICING}">model catalog</a>. You are billed per successful generation, and prompts and reference images are not charged separately.')


COSTS_LEAD = 'Calculated at the from price above, with nothing else added. Check higher resolution rates in the model catalog.'

# ---------------------------------------------------------------- code examples
PROMPT = 'A vertical 4:5 poster for a coffee brand, headline “Autumn Limited”, warm tones, clean negative space, product shot in the bottom-right corner'


def code_py(model, size='2K', extra=''):
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{PROMPT}",
        "size": "{size}",  # set size explicitly; omitting it may bill a higher tier
        "response_format": "url",  # or b64_json
        "watermark": False,{extra}
    }},
    timeout=300,
)
resp.raise_for_status()
for item in resp.json()["data"]:
    print(item["url"])  # temporary link, download it soon'''


def code_curl(model, size='2K'):
    return f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "{PROMPT}",
    "size": "{size}",
    "response_format": "url",
    "watermark": false
  }}\''''


def code_edit(model, size='2K'):
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

# image takes an array of URLs: one image to edit it, several to blend them
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "Place the product from image 1 into the scene from image 2. Keep the product shape and packaging text unchanged.",
        "image": [
            "https://example.com/product.png",
            "https://example.com/scene.jpg",
        ],
        "size": "{size}",
        "response_format": "url",
        "watermark": False,
    }},
    timeout=300,
)
resp.raise_for_status()
print(resp.json()["data"][0]["url"])'''


def code_seq(model, size='2K'):
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

# Image set: one request returns several related images
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "Four illustrations of the same orange cat across the seasons: spring cherry blossoms, summer beach, autumn leaves, winter snow, in one consistent style",
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {{"max_images": 4}},
        "size": "{size}",
        "response_format": "url",
        "watermark": False,
    }},
    timeout=600,
)
resp.raise_for_status()
for i, item in enumerate(resp.json()["data"], 1):
    print(i, item["url"])'''


def code_sdk(model, size='2K'):
    return f'''import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["ANYAIGC_API_KEY"], base_url="https://anyaigc.ai/v1")

img = client.images.generate(
    model="{model}",
    prompt="{PROMPT}",
    size="{size}",
    response_format="url",
    extra_body={{"watermark": False}},  # Seedream-specific fields go in extra_body
)
print(img.data[0].url)'''


def codes(slug):
    m = MODELS[slug]
    mid = m['id']
    if slug == 'seedream-3.0':
        return [('py', 'Python', f'Python · {mid} text-to-image', code_py(mid, '1024x1024')),
                ('curl', 'cURL', f'cURL · {mid} text-to-image', code_curl(mid, '1024x1024')),
                ('sdk', 'OpenAI SDK', 'Python · OpenAI SDK', code_sdk(mid, '1024x1024'))]
    out = [('py', 'Python', f'Python · {mid} text-to-image', code_py(mid)),
           ('curl', 'cURL', f'cURL · {mid} text-to-image', code_curl(mid)),
           ('edit', 'Reference images', f'Python · {mid} multi-image fusion', code_edit(mid))]
    if m['seq']:
        out.append(('seq', 'Image sets', f'Python · {mid} image set', code_seq(mid)))
    out.append(('sdk', 'OpenAI SDK', 'Python · OpenAI SDK', code_sdk(mid)))
    return out


def steps(mid):
    return [f'<a href="{G.REG}">Sign up for AnyAIGC</a>. New accounts get 2M free tokens, and you can top up from $1.',
            'Create an API key in the <a href="https://anyaigc.ai/console">console</a> and save it as the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'Send a request to <code>POST https://anyaigc.ai/v1/images/generations</code> (OpenAI-compatible) with <code>model</code> set to <code>{mid}</code>.']


QS_NOTE = (f'Authenticate with <code>Authorization: Bearer &lt;API Key&gt;</code>. The response looks like <code>{{"created": ..., "data": [{{"url": ...}}]}}</code>; '
           f'set <code>response_format</code> to <code>b64_json</code> to get base64 instead. <code>watermark</code> defaults to true, so pass false explicitly for clean images. '
           f'Field details are in the <a href="{DOCS}" target="_blank" rel="noopener">AnyAIGC Seedream API docs</a>.')


# ---------------------------------------------------------------- pricing and comparison
PRICE_HEAD = [('Model', False), ('Model ID', False), ('Billing', False), ('AnyAIGC from (USD)', True)]


def price_row(slug):
    m = MODELS[slug]
    billing = 'Per request' if m['unit'] == '次' else 'Per image'
    return (f'<th scope="row"><a href="/en/models/{slug}">{m["name"]}</a><small>{m["sizes_en"]}</small></th><td><code>{m["id"]}</code></td>'
            f'<td>{billing}</td><td class="o-num o-hl">{usd(slug)} / {UNIT[m["unit"]]}</td>')


def price_table(slugs):
    return G.table('Seedream API pricing (USD)', PRICE_HEAD, [(None, [price_row(s) for s in slugs])])


def billing(slug=None):
    one = ('1 image per request; image sets are billed per image generated' if slug in (None, 'seedream-5.0-lite', 'seedream-4.5', 'seedream-4.0')
           else '1 image per request')
    return [('Per image', 'Flat price, not token-based'), ('Output', one), ('Unlimited concurrency', 'Default for every account'),
            ('One balance', 'Works across 300+ models')]


def compare_table(cur=None):
    cols = MODEL_SLUGS

    def cls(s):
        return ' class="sd-cur"' if s == cur else ''
    head = [('', False)] + [(f'<a href="/en/models/{s}">{MODELS[s]["name"]}</a>', False) for s in cols]

    def row(label, vals):
        return f'<th scope="row">{label}</th>' + ''.join(f'<td{cls(s)}>{v}</td>' for s, v in zip(cols, vals))
    rows = [
        row('AnyAIGC model ID', [f'<code>{MODELS[s]["id"]}</code>' for s in cols]),
        row('Positioning', ['Flagship: reasoning, dense infographics, interactive precise editing', 'Lightweight: deep thinking + web search, up to 4K',
                            'Poster layouts, legible small text, multi-image fusion', 'Generation and editing in one, image sets', 'Legacy, text-to-image only']),
        row('Output resolution', [MODELS[s]['sizes_en'] for s in cols]),
        row('Reference images', ['Up to 10', 'Up to 14', 'Up to 14', 'Up to 14', 'Not supported']),
        row('Image sets (several per request)', ['Not supported', 'Up to 15', 'Up to 15', 'Up to 15', 'Not supported']),
        row('Distinct features', ['Layer separation, region editing, transparent backgrounds, 10+ languages', 'Web search (web_search)',
                                  'Keeps faces and lighting from the source', 'Style transfer, knowledge-based illustrations', 'Chinese and English']),
        row('AnyAIGC from', [f'<strong>{usd(s)}</strong> / {UNIT[MODELS[s]["unit"]]}' for s in cols]),
    ]
    return G.table('Seedream 5.0 Pro, 5.0 lite, 4.5, 4.0 and 3.0 compared', head, [(None, rows)], cls='sd-compare')


COMPARE_NOTE = (f'Specs are quoted from the <a href="{VOLC_DOC}" target="_blank" rel="noopener">Volcano Engine Ark image generation API docs</a> and the ByteDance Seed model pages (read 2026-10-28); '
                '3.0 specs come from the Seedream 3.0 technical report. Request fields follow the AnyAIGC API docs.')

USES = [
    ('E-commerce', 'Product shots and lifestyle scenes', 'Swap backgrounds and scenes while keeping the packaging and its text intact, and render the same SKU at 1:1, 3:4 and 16:9.'),
    ('Marketing', 'Posters with real typography', 'Headlines, selling points and fine print render directly in the image, for campaign posters, long-form graphics and social covers.'),
    ('Education', 'Infographics and explainers', 'Turn concepts, processes and data into clearly structured infographics. 5.0 Pro handles dense layouts well.'),
    ('Content', 'Illustration series and storyboards', 'Generate several images in one consistent style per request, for picture books, comic panels and brand mascots.'),
    ('Design', 'Sketches to finished renders', 'Turn a hand-drawn sketch, an annotated screenshot or a UI wireframe plus one sentence into a usable render.'),
    ('Global', 'Multilingual assets', 'Localize the same poster into English, Japanese, Arabic and more while keeping the layout.'),
]


# ---------------------------------------------------------------- overview page
def hub():
    sp, sl, s45, s40, s30 = MODEL_SLUGS
    models = [
        (f'/en/models/{sp}', 'Latest flagship', 'Seedream 5.0 Pro', MODELS[sp]['id'],
         'A multimodal image model with reasoning built in. Strong at dense infographics, interactive precise editing and realistic portraits, with native support for 10+ languages.', usd(sp), ' / image'),
        (f'/en/models/{sl}', 'Best value', 'Seedream 5.0 lite', MODELS[sl]['id'],
         'The lightweight 5.0 model with deep thinking and web search, up to 4K output, image sets and up to 14 reference images.', usd(sl), ' / image'),
        (f'/en/models/{s45}', 'Poster layouts', 'Seedream 4.5', MODELS[s45]['id'],
         'Keeps faces and lighting from the source image, lays out posters and logos reliably with legible small text, and stays consistent across multi-image fusion.', usd(s45), ' / image'),
        (f'/en/models/{s40}', 'Generate + edit', 'Seedream 4.0', MODELS[s40]['id'],
         'Text-to-image, editing and multi-image compositing in one model, with up to 15 related images per request and 4K support.', usd(s40), ' / image'),
        (f'/en/models/{s30}', 'Legacy', 'Seedream 3.0', MODELS[s30]['id'],
         'A bilingual Chinese and English text-to-image model with native 2K output. Text-to-image only; use 4.0 or newer for new projects.', usd(s30), ' / request'),
    ]
    choose = G.table('Which Seedream model to use', [('Need', False), ('Recommended', False), ('Why', False)], [(None, [
        f'<th scope="row">Infographics, posters, UI and other text-heavy images</th><td><a href="/en/models/{sp}">Seedream 5.0 Pro</a></td><td>Built for dense information, with the most reliable layouts and small text</td>',
        f'<th scope="row">Precise edits from annotations or selected regions</th><td><a href="/en/models/{sp}">Seedream 5.0 Pro</a></td><td>Follows selections and scribbled notes, supports layer separation and transparent backgrounds</td>',
        f'<th scope="row">Everyday batch work on a budget</th><td><a href="/en/models/{sl}">Seedream 5.0 lite</a></td><td>Lowest price in the 5.0 generation ({usd(sl)} / image), up to 4K</td>',
        f'<th scope="row">Several related images per request (image sets)</th><td><a href="/en/models/{sl}">5.0 lite</a> / <a href="/en/models/{s45}">4.5</a> / <a href="/en/models/{s40}">4.0</a></td><td>All three return up to 15 per request; 5.0 Pro does not support image sets</td>',
        f'<th scope="row">Real-time information (holidays, trending topics)</th><td><a href="/en/models/{sl}">Seedream 5.0 lite</a></td><td>The only model with web search</td>',
    ])])
    faqs = [
        ('How much does the Seedream API cost?',
         f'Every Seedream model on AnyAIGC has a flat price: 5.0 Pro from {usd(sp)} / image, 5.0 lite from {usd(sl)} / image, 4.5 from {usd(s45)} / image, 4.0 from {usd(s40)} / image and 3.0 at {usd(s30)} / request. Higher resolutions cost more; live prices are in the model catalog.'),
        ('What is Seedream? How does it relate to Doubao and Jimeng?',
         'Seedream is the image generation model family from the ByteDance Seed team. On Volcano Engine it is offered as "Doubao Seedream" (doubao-seedream), and image generation in ByteDance products such as Jimeng is built on it. AnyAIGC provides API access to the official Seedream models.'),
        ('What is the difference between 5.0 Pro, 5.0 lite, 4.5 and 4.0?',
         '5.0 Pro is the flagship: strong at infographics, precise editing and multilingual text, up to 2K, no image sets. 5.0 lite is the lightweight model with web search, up to 4K. 4.5 excels at poster layouts and keeping source details. 4.0 was the release that merged generation and editing. 5.0 lite, 4.5 and 4.0 all support image sets and up to 14 reference images.'),
        ('Which endpoint does it use? Can it edit images?',
         f'Every model uses the OpenAI-compatible <code>POST /v1/images/generations</code>; switching models only changes <code>model</code>. For editing and multi-image fusion, pass an array of image URLs in <code>image</code>. For image sets, use <code>sequential_image_generation: "auto"</code>. See the <a href="{DOCS}">AnyAIGC API docs</a> for every field.'),
        conc_faq('every Seedream model'),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(
        name='Seedream', crumb='Seedream', product='Seedream API (AnyAIGC)', sku='seedream', currency='USD',
        title=f'Seedream API Pricing & Access | From {usd(sl)}/Image - AnyAIGC',
        desc=f'Seedream API for 5.0 Pro, 5.0 lite, 4.5 and 4.0 from {usd(sl)} per image. Multi-image fusion, image sets, 4K, unlimited concurrency, VAT invoices.',
        og_desc=f'One key for every ByteDance Seedream model: 5.0 Pro, 5.0 lite, 4.5 and 4.0, from {usd(sl)} per image, unlimited concurrency.',
        og_alt='AnyAIGC Seedream API: 5.0 Pro, 5.0 lite, 4.5 and 4.0',
        keywords='Seedream API,Seedream API pricing,Seedream 5.0 API,Seedream 5.0 Pro API,Seedream 4.5 API,Doubao Seedream API,ByteDance image API,doubao-seedream,Seedream API key,Seedream image sets,Seedream API for business,Seedream API invoice,AnyAIGC',
        product_desc='Access every ByteDance Seedream image model through AnyAIGC: doubao-seedream-5-0-pro, 5-0 (lite), 4-5, 4-0 and 3-0, via the OpenAI-compatible /v1/images/generations.',
        offers=[(f'{MODELS[s]["name"]} (per {UNIT[MODELS[s]["unit"]]}, from)', USD[s]) for s in MODEL_SLUGS],
        eyebrow='ByteDance · Seedream family', h1='Seedream API<small>Doubao Seedream 5.0 Pro, 5.0 lite, 4.5 and 4.0</small>',
        lead=f'One API key for every ByteDance Seedream model, <strong>from {usd(sl)} per image</strong>.',
        lead_sub='Infographics, poster layouts, multi-image fusion, image sets and 4K output, all over the API. Flat per-image pricing instead of tokens, with no Volcano Engine account needed.',
        facts=[('From', f'{usd(sl)} / image'), ('Up to', '4K'), ('Reference images', 'Up to 14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
        tiles=[('info', 'Seedream 5.0 Pro'), ('seq', 'Seedream 5.0 lite'), ('multi', 'Seedream 4.5'), ('edit', 'Seedream 4.0')],
        models_h2='Every Seedream model', models_lead='All models share one API; just change <code>model</code>. Open a card for that model\'s pricing, specs and code samples.',
        models=models,
        compare_h2='Seedream 5.0 Pro vs 5.0 lite vs 4.5 vs 4.0', compare_lead='Resolution, reference images, image sets and distinct features side by side.',
        compare_table=compare_table(), compare_note=COMPARE_NOTE,
        price_h2='Seedream API pricing', price_lead='Flat prices across the lineup. One API key and one balance for every model.',
        billing=billing(), billing_label='Billing basics', price_tables=price_table(MODEL_SLUGS), price_note=price_note(),
        price_extra=f'      <h3 class="sd-h3 o-reveal">Which model to use</h3>{NL}' + choose,
        costs_h3='Cost examples', costs_lead=COSTS_LEAD,
        costs=[('1,000 product shots', 'Seedream 5.0 lite, ' + cost(1000, sl)[0], cost(1000, sl)[1], 'Everyday batch work'),
               ('100 infographic posters', 'Seedream 5.0 Pro, ' + cost(100, sp)[0], cost(100, sp)[1], 'Text-heavy layouts'),
               ('A 15-image illustration set', 'Seedream 4.0 image set, ' + cost(15, s40)[0], cost(15, s40)[1], '15 images in one request')],
        uses_h2='Seedream API use cases', uses=USES,
        qs_h2='Get started with the Seedream API', steps=steps(MODELS[sp]['id']), codes=codes(sp),
        callout='Switch models by changing <code>model</code> to <code>doubao-seedream-5-0-pro-260628</code>, <code>doubao-seedream-5-0-260128</code>, <code>doubao-seedream-4-5-251128</code> or <code>doubao-seedream-4-0-250828</code>. Requests and responses keep the same format.',
        qs_note=QS_NOTE,
        family_h2='Seedream model guides', family_lead='Each model has its own page with full pricing, specs and code samples.',
        faq_h2='Seedream API FAQ', faqs=faqs,
        final_h2='Start using Seedream', final_p='Sign up and get 2M free tokens. One key covers every Seedream model and 300+ others.',
    )


# ---------------------------------------------------------------- model pages
def model_page(slug):
    m = MODELS[slug]
    name, mid = m['name'], m['id']
    unit = UNIT[m['unit']]
    p = usd(slug)
    base = dict(name=name, crumb=name, sku=mid, currency='USD', product=f'{name} API (AnyAIGC)',
                offers=[(f'{name} (per {unit}, from)', USD[slug])],
                billing=billing(slug), billing_label='Billing basics', price_tables=price_table([slug]), price_note=price_note(slug),
                costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                compare_h2=f'{name} vs the rest of the lineup', compare_table=compare_table(slug), compare_note=COMPARE_NOTE,
                uses_h2=f'{name} API use cases', uses=USES,
                qs_h2=f'Get started with the {name} API', steps=steps(mid), codes=codes(slug), qs_note=QS_NOTE,
                family_h2='Other Seedream models', family_lead='Same API; change <code>model</code> to switch.',
                faq_h2=f'{name} API FAQ',
                price_h2=f'{name} API pricing', price_lead=f'Flat pricing. {name} starts at {p} / {unit}.',
                final_h2=f'Start using {name}', final_p=f'Sign up and get 2M free tokens. From {p} / {unit}, with unlimited concurrency.',
                h1=f'{name} API<small>{mid}</small>', eyebrow=f'ByteDance · {name}')

    def price_faq(extra=''):
        return (f'How much does the {name} API cost?',
                f'On AnyAIGC, {name} (<code>{mid}</code>) starts at {p} / {unit}. {extra}You are billed per successful generation; live prices are in the model catalog.')

    def costs3(n1, n2, n3, l1, l2, l3):
        return [(lab[0], *cost(n, slug), lab[1]) for n, lab in ((n1, l1), (n2, l2), (n3, l3))]

    if slug == 'seedream-5.0-pro':
        faqs = [
            price_faq('Prices vary by resolution, and omitting <code>size</code> may bill a higher tier, so pass <code>1K</code> or <code>2K</code> explicitly. '),
            ('What is Seedream 5.0 Pro?',
             'Seedream 5.0 Pro is the flagship image model from the ByteDance Seed team, described officially as a multimodal image generation model with reasoning built in for efficient creation and production. It focuses on dense information layouts, interactive precise editing, realistic photography and portraits, and native support for 10+ languages. AnyAIGC added it in August 2026.'),
            ('Which resolutions are supported? Can it output 4K?',
             'No 4K. Per the Volcano Engine Ark docs, 5.0 Pro accepts <code>size</code> values of <code>1K</code>, <code>1.5K</code> and <code>2K</code> (default 2K), or pixel dimensions such as <code>2048x2048</code> and <code>2816x1584</code>, with aspect ratios from 1:16 to 16:1. For 4K, use <a href="/en/models/seedream-5.0-lite">Seedream 5.0 lite</a> or 4.5.'),
            ('How many reference images can I send? Does it support image sets?',
             '<code>image</code> accepts up to 10 reference images for editing and multi-image fusion. 5.0 Pro does not support image sets (several related images per request); use 5.0 lite, 4.5 or 4.0 for that.'),
            ('Should I pick 5.0 Pro or 5.0 lite?',
             f'Pick 5.0 Pro for text-heavy images such as infographics, posters and UI, and for precise edits driven by annotations or selected regions. Pick <a href="/en/models/seedream-5.0-lite">5.0 lite</a> for everyday batch work, 4K, image sets or web search; it also costs less (from {usd("seedream-5.0-lite")} / image).'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 5.0 Pro API Pricing | From {p} per Image - AnyAIGC',
            desc=f'Seedream 5.0 Pro API (doubao-seedream-5-0-pro-260628) from {p} per image: infographics, precise edits, 10+ languages, unlimited concurrency, VAT invoices.',
            og_desc=f'ByteDance Seedream 5.0 Pro API from {p} per image: dense infographics, region editing, 10+ languages, unlimited concurrency.',
            og_alt='AnyAIGC Seedream 5.0 Pro API pricing and access',
            keywords='Seedream 5.0 Pro API,Seedream 5.0 Pro API pricing,doubao-seedream-5-0-pro-260628,Doubao Seedream 5.0 Pro,Seedream 5.0 Pro access,Seedream 5.0 Pro vs lite,Seedream API key,Seedream API for business,Seedream API invoice,AnyAIGC',
            product_desc='Access ByteDance Seedream 5.0 Pro (doubao-seedream-5-0-pro-260628) image generation and editing through AnyAIGC, billed per image via the OpenAI-compatible /v1/images/generations.',
            lead=f'The ByteDance Seed flagship image model, <strong>from {p} per image</strong>.',
            lead_sub='Reasoning built in: dense infographics, precise edits from annotations and selections, realistic portraits, and native text rendering in 10+ languages.',
            facts=[('From', f'{p} / image'), ('Up to', '2K'), ('Reference images', 'Up to 10'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
            tiles=[('info', 'Dense infographics'), ('edit', 'E-commerce UI'), ('photo', 'Realistic portraits'), ('lang', 'Multilingual posters')],
            about_h2='What is Seedream 5.0 Pro',
            about_ps=['Seedream 5.0 Pro is the flagship image model released by the ByteDance Seed team, positioned as a multimodal image generation model with reasoning built in for efficient creation and production. It understands complex instructions and visual input, and produces usable results for information-dense images such as infographics, storyboards and UI.',
                      f'On AnyAIGC the model ID is <code>{mid}</code>, served through the OpenAI-compatible <code>/v1/images/generations</code>, from {p} per image. You do not need a Volcano Engine account or ID verification.'],
            spec=[('Model ID', f'<code>{mid}</code>'), ('Output resolution', '1K / 1.5K / 2K (default 2K)'), ('Reference images', 'Up to 10'),
                  ('Image sets', 'Not supported'), ('Distinct features', 'Layer separation · transparent backgrounds'), ('Endpoint', '/v1/images/generations')],
            features_h2='What Seedream 5.0 Pro can do',
            features_lead='These four capabilities come from the official ByteDance Seed model page.',
            features=[('info', 'Dense information layouts', 'Handles complex information: infographics, technical drawings, game UI, storyboards and education posters, with layouts and small text ready to use.'),
                      ('edit', 'Interactive precise editing', 'Responds to selected regions, scribbled sketches and handwritten notes, changing only what you mark and leaving the rest intact; supports layer separation.'),
                      ('photo', 'Realistic photos and portraits', 'Reproduces real-world lighting and skin texture for lifestyle photography, portrait retouching and makeup changes.'),
                      ('lang', 'Native multilingual support', 'Write prompts and render in-image text in 10+ common languages, translate a poster while keeping its layout, and lay out Arabic right to left.')],
            costs=costs3(100, 500, 1000, ('100 infographic posters', 'Text-heavy layouts'), ('500 retouched product shots', 'Edits from annotations'), ('1,000 multilingual assets', 'Ads for global markets')),
            callout='5.0 Pro does not support image sets (<code>sequential_image_generation</code>). To get several related images per request, change <code>model</code> to <code>doubao-seedream-5-0-260128</code> (5.0 lite).',
            faqs=faqs,
        )

    if slug == 'seedream-5.0-lite':
        faqs = [
            price_faq('Prices vary by resolution; live 2K, 3K and 4K rates are in the model catalog. An image set returns several images and is billed per image generated. '),
            ('What is Seedream 5.0 lite?',
             'Seedream 5.0 lite is the lightweight model in the Seedream 5.0 generation, with the model ID doubao-seedream-5-0-260128 on AnyAIGC. Its official focus is deep thinking plus real-time retrieval: it reads intent more accurately, controls style and layout, and can pull in live information from the web. AnyAIGC added it in February 2026.'),
            ('Which resolutions are supported? Can it output 4K?',
             'Yes. Per the Volcano Engine Ark docs, 5.0 lite accepts <code>size</code> values of <code>2K</code>, <code>3K</code> and <code>4K</code>, or pixel dimensions, with aspect ratios from 1:16 to 16:1.'),
            ('How do image sets work, and how many images can I get?',
             'Pass <code>sequential_image_generation: "auto"</code> and set the cap with <code>sequential_image_generation_options.max_images</code> (1–15). Text-only prompts return up to 15 images; with reference images, references plus generated images cannot exceed 15.'),
            ('How many reference images can I send? Can it search the web?',
             '<code>image</code> accepts up to 14 reference images. 5.0 lite is the only Seedream model with web search, which helps with holiday themes, trending topics and anything that needs current information.'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 5.0 lite API Pricing | 4K from {p} - AnyAIGC',
            desc=f'Seedream 5.0 lite API (doubao-seedream-5-0-260128) from {p} per image, up to 4K, image sets, web search, unlimited concurrency, VAT invoices.',
            og_desc=f'ByteDance Seedream 5.0 lite API from {p} per image: up to 4K, image sets and web search, unlimited concurrency.',
            og_alt='AnyAIGC Seedream 5.0 lite API pricing and access',
            keywords='Seedream 5.0 lite API,Seedream 5.0 API,Seedream 5.0 lite pricing,doubao-seedream-5-0-260128,Doubao Seedream 5.0,Seedream 4K,Seedream image sets,Seedream API key,Seedream API for business,Seedream API invoice,AnyAIGC',
            product_desc='Access ByteDance Seedream 5.0 lite (doubao-seedream-5-0-260128) image generation through AnyAIGC, billed per image via the OpenAI-compatible /v1/images/generations.',
            lead=f'The lightweight Seedream 5.0 model, <strong>from {p} per image</strong>, up to 4K.',
            lead_sub='Deep thinking plus real-time retrieval: sharper intent, controllable style and layout, and live web information for holidays and trending topics.',
            facts=[('From', f'{p} / image'), ('Up to', '4K'), ('Image sets', 'Up to 15'), ('Reference images', 'Up to 14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
            tiles=[('seq', '16-shot image set'), ('multi', 'Vintage stickers'), ('photo', 'Calorie labels'), ('type', 'Trend-aware art')],
            about_h2='What is Seedream 5.0 lite',
            about_ps=['Seedream 5.0 lite is the lightweight model in the ByteDance Seed team\'s Seedream 5.0 generation. Its official focus is deep thinking plus real-time retrieval, which makes it better at reading complex intent and controlling style and layout, and lets it pull live information from web search.',
                      f'On AnyAIGC the model ID is <code>{mid}</code>, from {p} per image, the lowest price in the 5.0 generation.'],
            spec=[('Model ID', f'<code>{mid}</code>'), ('Output resolution', '2K / 3K / 4K'), ('Reference images', 'Up to 14'),
                  ('Image sets', 'Up to 15'), ('Web search', 'Supported'), ('Endpoint', '/v1/images/generations')],
            features_h2='What Seedream 5.0 lite can do',
            features=[('search', 'Live web information', 'With web search on, the model draws on current information, useful for holiday posters, trending-topic visuals and anything that needs recent facts.'),
                      ('seq', 'Image sets', 'Up to 15 related images in one consistent style per request, for illustration series, storyboards and multi-angle product shots.'),
                      ('multi', 'Multi-image fusion', 'Up to 14 reference images to combine products, people and scenes in one frame.'),
                      ('type', 'Style and layout control', 'Control art style, composition and typography precisely from the prompt, with output up to 4K.')],
            costs=costs3(1000, 200, 15, ('1,000 product shots', 'Everyday batch work'), ('200 social images', 'Multiple aspect ratios'), ('A 15-image illustration set', 'One image set request')),
            callout='5.0 lite supports <code>stream</code> for image sets, and web search is enabled with <code>tools: [{"type": "web_search"}]</code> (see the AnyAIGC API docs for the current fields).',
            faqs=faqs,
        )

    if slug == 'seedream-4.5':
        faqs = [
            price_faq('Prices vary by resolution; live 2K and 4K rates are in the model catalog. Image sets are billed per image generated. '),
            ('What is Seedream 4.5?',
             'Seedream 4.5 is an image creation model from the ByteDance Seed team, with the model ID doubao-seedream-4-5-251128 on AnyAIGC. It takes text, a single image or several images as input and handles subject-consistent multi-image fusion, image editing and image sets. Officially it keeps faces, lighting and detail from the source image, lays out posters and logos more reliably, and renders small text legibly.'),
            ('Which resolutions are supported?',
             'Per the Volcano Engine Ark docs, 4.5 accepts <code>size</code> values of <code>2K</code> and <code>4K</code>, or pixel dimensions, with aspect ratios from 1:16 to 16:1.'),
            ('How many reference images can I send? How large can an image set be?',
             '<code>image</code> accepts up to 14 reference images. Image sets use <code>sequential_image_generation: "auto"</code> and return up to 15 images per request; with reference images, references plus generated images cannot exceed 15.'),
            ('Should I pick 4.5 or 5.0 lite?',
             f'Both support 4K, image sets and 14 reference images. Pick <a href="/en/models/seedream-5.0-lite">5.0 lite</a> (from {usd("seedream-5.0-lite")} / image) for web search or stronger intent understanding. If you already integrate 4.5 and care most about poster layouts and preserving source details, keep using 4.5.'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 4.5 API Pricing | Posters from {p} - AnyAIGC',
            desc=f'Seedream 4.5 API (doubao-seedream-4-5-251128) from {p} per image: poster layouts, multi-image fusion, 4K, image sets, unlimited concurrency, VAT invoices.',
            og_desc=f'ByteDance Seedream 4.5 API from {p} per image: poster layouts, multi-image fusion, 4K and image sets, unlimited concurrency.',
            og_alt='AnyAIGC Seedream 4.5 API pricing and access',
            keywords='Seedream 4.5 API,Seedream 4.5 API pricing,doubao-seedream-4-5-251128,Doubao Seedream 4.5,Seedream 4.5 access,Seedream multi-image fusion,Seedream image sets,Seedream API key,Seedream API for business,Seedream API invoice,AnyAIGC',
            product_desc='Access ByteDance Seedream 4.5 (doubao-seedream-4-5-251128) image generation and editing through AnyAIGC, billed per image via the OpenAI-compatible /v1/images/generations.',
            lead=f'Poster layouts and multi-image fusion, <strong>from {p} per image</strong>.',
            lead_sub='Keeps faces, lighting and detail from the source, lays out posters and logos reliably with legible small text, and keeps characters consistent across inputs. Supports 4K and image sets.',
            facts=[('From', f'{p} / image'), ('Up to', '4K'), ('Image sets', 'Up to 15'), ('Reference images', 'Up to 14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
            tiles=[('type', 'Translate text in place'), ('photo', 'Invitation layout'), ('multi', 'Storybook cover'), ('seq', 'Riff on a reference')],
            about_h2='What is Seedream 4.5',
            about_ps=['Seedream 4.5 is an image creation model from the ByteDance Seed team. It takes text, a single image or several images as input and handles subject-consistent multi-image fusion, image editing and image sets in one model.',
                      f'The official highlights are threefold: edits keep the faces, lighting and detail of the source image; posters and logos lay out more reliably with legible small text; and multi-image fusion locks onto the subject so characters stay consistent. On AnyAIGC the model ID is <code>{mid}</code>, from {p} per image.'],
            spec=[('Model ID', f'<code>{mid}</code>'), ('Output resolution', '2K / 4K'), ('Reference images', 'Up to 14'),
                  ('Image sets', 'Up to 15'), ('Input', 'Text · single image · multiple images'), ('Endpoint', '/v1/images/generations')],
            features_h2='What Seedream 4.5 can do',
            features=[('type', 'Poster layouts and small text', 'Headlines, selling points and fine print all land cleanly in the image, for campaign posters, packaging and logo design.'),
                      ('photo', 'Edits that keep source detail', 'Swap backgrounds or styles while faces, lighting and detail stay put, instead of redrawing the whole image.'),
                      ('multi', 'Consistent characters across images', 'Up to 14 reference images; the model identifies and locks onto the subject so characters stay consistent from frame to frame.'),
                      ('seq', 'Image sets', 'Up to 15 related images per request, for poster series, picture books and multi-angle product shots.')],
            costs=costs3(500, 1000, 15, ('500 campaign posters', 'Headlines and fine print included'), ('1,000 product scene shots', 'Multi-image fusion'), ('A 15-image series', 'One image set request')),
            callout='For new projects, try <code>doubao-seedream-5-0-260128</code> (5.0 lite). It costs less with nearly the same parameters, so migrating only changes <code>model</code>.',
            faqs=faqs,
        )

    if slug == 'seedream-4.0':
        faqs = [
            price_faq('Prices vary by resolution; live 2K and 4K rates are in the model catalog. Image sets are billed per image generated. '),
            ('What is Seedream 4.0?',
             'Seedream 4.0 is a multimodal image model from the ByteDance Seed team, with the model ID doubao-seedream-4-0-250828 on AnyAIGC. It unifies text-to-image, image editing and multi-image compositing in one framework, picks a suitable aspect ratio and image count from the prompt, returns up to 15 related images per request, and supports 4K.'),
            ('Which resolutions are supported?',
             'Per the Volcano Engine Ark docs, 4.0 accepts <code>size</code> values of <code>1K</code>, <code>2K</code> and <code>4K</code>, or pixel dimensions, with aspect ratios from 1:16 to 16:1.'),
            ('How many reference images can I send? How large can an image set be?',
             '<code>image</code> accepts up to 14 reference images (per the current Volcano Engine Ark docs). Image sets return up to 15 images per request; with reference images, references plus generated images cannot exceed 15.'),
            ('Is 4.0 still worth using?',
             f'4.0 remains available, costs less than 4.5 (from {p} / image) and offers a 1K tier. For new projects, try <a href="/en/models/seedream-5.0-lite">5.0 lite</a> or <a href="/en/models/seedream-4.5">4.5</a> first. The API is identical, so migrating only changes the model ID.'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 4.0 API Pricing & Access | From {p} - AnyAIGC',
            desc=f'Seedream 4.0 API (doubao-seedream-4-0-250828) from {p} per image: generation, editing and image sets of up to 15, 4K, unlimited concurrency, VAT invoices.',
            og_desc=f'ByteDance Seedream 4.0 API from {p} per image: generation and editing in one, up to 15 images per request, 4K, unlimited concurrency.',
            og_alt='AnyAIGC Seedream 4.0 API pricing and access',
            keywords='Seedream 4.0 API,Seedream 4.0 API pricing,doubao-seedream-4-0-250828,Doubao Seedream 4.0,Seedream 4.0 access,Seedream image editing API,Seedream image sets,Seedream API key,Seedream API for business,Seedream API invoice,AnyAIGC',
            product_desc='Access ByteDance Seedream 4.0 (doubao-seedream-4-0-250828) image generation and editing through AnyAIGC, billed per image via the OpenAI-compatible /v1/images/generations.',
            lead=f'Text-to-image, editing and compositing in one model, <strong>from {p} per image</strong>.',
            lead_sub='Picks aspect ratio and image count from the prompt and returns up to 15 related images per request, with more accurate Chinese text and 4K support.',
            facts=[('From', f'{p} / image'), ('Up to', '4K'), ('Image sets', 'Up to 15'), ('Reference images', 'Up to 14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
            tiles=[('multi', 'Multi-image'), ('edit', 'Edit poster text'), ('seq', 'One image, four styles'), ('info', 'Worked solutions')],
            about_h2='What is Seedream 4.0',
            about_ps=['Seedream 4.0 is a multimodal image model from the ByteDance Seed team that unifies text-to-image, image editing and multi-image compositing in one framework. It reasons over the prompt to choose a suitable aspect ratio and image count, returning up to 15 thematically related images per request.',
                      f'ByteDance also reports clear gains in Chinese text accuracy and output variety, plus 4K output. On AnyAIGC the model ID is <code>{mid}</code>, from {p} per image.'],
            spec=[('Model ID', f'<code>{mid}</code>'), ('Output resolution', '1K / 2K / 4K'), ('Reference images', 'Up to 14'),
                  ('Image sets', 'Up to 15'), ('Capabilities', 'Generate · edit · composite'), ('Endpoint', '/v1/images/generations')],
            features_h2='What Seedream 4.0 can do',
            features=[('seq', 'Image sets', 'Up to 15 thematically related images per request, with the model choosing the count and ratio.'),
                      ('edit', 'Instruction editing', 'Edit with one sentence: add or remove elements, change style or background, no mask needed.'),
                      ('multi', 'Multi-image compositing', 'Combine people, products and scenes from several reference images into one frame.'),
                      ('info', 'Knowledge illustrations', 'Draws formulas, science explainers and other knowledge-based images, with more accurate Chinese text.')],
            costs=costs3(1000, 300, 15, ('1,000 product shots', 'Batch work from the 1K tier'), ('300 edits', 'Instruction editing'), ('A 15-image related set', 'One image set request')),
            callout='Among the three models that support image sets, 4.0 is the only one with a <code>1K</code> tier, which suits batch jobs that do not need high resolution.',
            faqs=faqs,
        )

    # Seedream 3.0 (legacy)
    faqs = [
        price_faq('3.0 is billed per request in the model catalog, and each request returns 1 image. '),
        ('Has Seedream 3.0 been retired?',
         'No. <code>doubao-seedream-3-0-t2i-250415</code> works normally on AnyAIGC today. However, the current Volcano Engine Ark image generation docs no longer list 3.0, so it may be retired later. For new projects, use <a href="/en/models/seedream-4.0">Seedream 4.0</a> or <a href="/en/models/seedream-5.0-lite">5.0 lite</a>; the API is identical, so migrating only changes the model ID.'),
        ('What is Seedream 3.0?',
         'Seedream 3.0 is a bilingual Chinese and English text-to-image foundation model released by the ByteDance Seed team in April 2025. It outputs native 2K, renders small text and typography more accurately, and improves instruction following and aesthetics over the previous generation.'),
        ('Can 3.0 edit images or take reference images?',
         'No. 3.0 (t2i) is text-to-image only, with no reference images, editing or image sets. Use 4.0 or newer for editing.'),
        ('What should I put in size?',
         '3.0 takes pixel dimensions for <code>size</code>, for example <code>1024x1024</code>, <code>1280x720</code> or <code>720x1280</code>.'),
        conc_faq(name),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(base,
        title=f'Seedream 3.0 API Pricing & Access | {p}/Request - AnyAIGC',
        desc=f'Seedream 3.0 API (doubao-seedream-3-0-t2i-250415) at {p} per request: bilingual text-to-image, native 2K, unlimited concurrency, VAT invoices.',
        og_desc=f'ByteDance Seedream 3.0 text-to-image API at {p} per request: Chinese and English prompts, native 2K, unlimited concurrency.',
        og_alt='AnyAIGC Seedream 3.0 API pricing and access',
        keywords='Seedream 3.0 API,Seedream 3.0 API pricing,doubao-seedream-3-0-t2i-250415,Doubao Seedream 3.0,Seedream text-to-image API,Seedream API key,Seedream API for business,Seedream API invoice,AnyAIGC',
        product_desc='Access ByteDance Seedream 3.0 (doubao-seedream-3-0-t2i-250415) text-to-image through AnyAIGC, billed per request via the OpenAI-compatible /v1/images/generations.',
        lead=f'Bilingual text-to-image, <strong>{p} per request</strong>.',
        lead_sub='Native 2K output with more accurate small text and typography. Text-to-image only; a fit for projects that already integrate 3.0.',
        notice='The current Volcano Engine Ark docs no longer list Seedream 3.0. For new projects, use <a href="/en/models/seedream-4.0">Seedream 4.0</a> or <a href="/en/models/seedream-5.0-lite">5.0 lite</a>; migrating only changes the model ID.',
        facts=[('Price', f'{p} / request'), ('Resolution', 'Native 2K'), ('Capability', 'Text-to-image'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
        tiles=[('type', 'Chinese and English text'), ('photo', 'Native 2K'), ('info', 'Small-text layout'), ('lang', 'Instruction following')],
        price_lead=f'Billed per request at {p}, with 1 image per request.',
        billing=[('Per request', 'Flat price, not token-based'), ('1 image per request', 'Each request returns 1 image'),
                 ('Unlimited concurrency', 'Default for every account'), ('One balance', 'Works across 300+ models')],
        about_h2='What is Seedream 3.0',
        about_ps=['Seedream 3.0 is a bilingual Chinese and English image generation foundation model released by the ByteDance Seed team in April 2025. It outputs native 2K and clearly improves on the previous generation in small text, typography, instruction following and aesthetics.',
                  f'On AnyAIGC the model ID is <code>{mid}</code>, billed at {p} per request. It is text-to-image only, with no reference images, editing or image sets.'],
        spec=[('Model ID', f'<code>{mid}</code>'), ('Resolution', 'Native 2K'), ('size', 'Pixel sizes, e.g. 1024x1024'),
              ('Reference images', 'Not supported'), ('Languages', 'Chinese · English'), ('Endpoint', '/v1/images/generations')],
        features_h2='What Seedream 3.0 can do',
        features=[('type', 'Chinese and English text', 'Prompt in Chinese or English, with more accurate text rendered in the image.'),
                  ('photo', 'Native 2K', 'Outputs 2K images directly for sharper detail.'),
                  ('info', 'Small text and typography', 'Renders small text and layouts more accurately than the previous generation.'),
                  ('lang', 'Instruction following', 'Understands and executes prompts more reliably, with better composition and aesthetics.')],
        costs=costs3(1000, 500, 100, ('1,000 illustrations', 'Text-to-image only'), ('500 covers', 'Chinese or English headlines'), ('100 test images', 'Quality comparisons')),
        callout='To migrate, change <code>model</code> to <code>doubao-seedream-4-0-250828</code> or another newer model, and switch <code>size</code> to tier values such as <code>2K</code>.',
        faqs=faqs,
    )


def build(slug):
    return hub() if slug == 'seedream' else model_page(slug)
