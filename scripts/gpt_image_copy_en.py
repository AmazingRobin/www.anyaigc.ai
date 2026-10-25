# English copy for the GPT Image topic pages. build(slug) returns the dict used by gpt_image_pages.py.
# Same keys and facts as gpt_image_copy_zh.py; all prices come from gpt_image_data.
from gpt_image_data import (TOKEN, OFFICIAL, CALL, CALL_4K, C_OF, MODELS, TOKENS_25, OFFICIAL_IMG_2, PRICING, SUPPORT,
                            DOCS_GEN_2, DOCS_EDIT_2, DOCS_GEN_25, DOCS_EDIT_25, OFFICIAL_GUIDE, money, cost_25, cost_2, save)
import gpt_image_layout as G

T2, T25 = TOKEN['2'], TOKEN['2.5']
S2 = save(T2['out'], OFFICIAL['out'])     # 92
S25 = save(T25['out'], OFFICIAL['out'])   # 41

SIZE_RULES = ('the longest edge is at most 3840px, both sides are multiples of 16, the aspect ratio is no wider than 3:1, '
              'and the total pixel count is between 655,360 and 8,294,400')
CONC = 'Unlimited concurrency'

FAMILY = [
    ('gpt-image', 'Overview', 'GPT Image lineup', 'Compare prices across the 3 models'),
    ('gpt-image-2.5-sunburst', 'New', 'GPT Image 2.5 Sunburst', f'Top editing precision · ${T25["out"]} / 1M output'),
    ('gpt-image-2.5-flare', 'New', 'GPT Image 2.5 Flare', f'Fastest, built for volume · ${T25["out"]} / 1M output'),
    ('gpt-image-2', '', 'GPT Image 2', f'Released April 2026 · ${T2["out"]} / 1M output'),
]

COMMON_FAQ = [
    ('Can AnyAIGC issue invoices, including VAT special invoices?',
     'Yes. AnyAIGC issues invoices for the amount you top up, including Chinese VAT general invoices and VAT special invoices. Send your billing details to support to request one.'),
    ('Can my company pay by bank transfer and sign a contract?',
     f'Yes. Companies can top up by corporate bank transfer and sign a service agreement, and get a dedicated support and technical contact. <a href="{SUPPORT}">Contact AnyAIGC support</a> to get started.'),
]
LICENSE_FAQ = ('Can I use the generated images commercially?',
               "Usage rights and content policies follow OpenAI's official terms. AnyAIGC only provides API access and adds no extra restrictions on how you use the output. If an image involves real people's likenesses or third-party trademarks, make sure you have the rights you need.")


def conc_faq(name):
    return ('Are there concurrency limits? Does it work from mainland China?',
            f'AnyAIGC sets no concurrency limit on {name}, and every account gets this by default. The base URL is <code>https://anyaigc.ai/v1</code>, which is tuned for networks in mainland China, so you usually do not need a proxy. Billing is in USD, you can pay with WeChat Pay, Alipay, USDT or a credit card, and the same key works for 300+ other models.')


def code_gen(model, size='1536x1024', quality='medium', n=True, prompt='Product still life: matte black mechanical keyboard, studio lighting, no text'):
    nline = '\n        "n": 1,' if n else ''
    py = f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{prompt}",
        "size": "{size}",
        "quality": "{quality}",
        "format": "webp",
        "response_format": "url",{nline}
    }},
    timeout=300,
)
resp.raise_for_status()
image_url = resp.json()["data"][0]["url"]

# Download the image
with open("output.webp", "wb") as f:
    f.write(requests.get(image_url, timeout=120).content)
print("Saved output.webp")'''
    ncurl = ',\n    "n": 1' if n else ''
    curl = f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "{prompt}",
    "size": "{size}",
    "quality": "{quality}",
    "format": "webp",
    "response_format": "url"{ncurl}
  }}\''''
    return curl, py


def code_edit(model, mask=True):
    mask_part = '''
# Inpainting: transparent areas of the mask are redrawn (PNG, under 4MB, same size as the image)
# files.append(("mask", open("mask.png", "rb")))''' if mask else ''
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

# Upload several reference images (fewer than 16, 50MB total) by repeating the image field
files = [
    ("image", open("product.png", "rb")),
    ("image", open("background.png", "rb")),
]{mask_part}

resp = requests.post(
    "https://anyaigc.ai/v1/images/edits",
    headers={{"Authorization": "Bearer " + API_KEY}},
    data={{
        "model": "{model}",
        "prompt": "Place the product from the first image into the scene from the second image. Keep the product and its label text unchanged.",
        "size": "1024x1024",
        "quality": "high",
    }},
    files=files,
    timeout=300,
)
resp.raise_for_status()
print(resp.json()["data"][0]["url"])'''


def steps(model):
    return [f'<strong>Sign up</strong>: <a href="{G.REG}">create an AnyAIGC account</a>. New accounts get 2 million tokens of trial credit, and top-ups start at $1.',
            '<strong>Create an API key</strong>: generate a key in the <a href="https://anyaigc.ai/console">console</a> and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Send a request</strong>: call <code>https://anyaigc.ai/v1/images/generations</code> with <code>model</code> set to <code>{model}</code>. Use <code>/v1/images/edits</code> to edit images.']


def token_price_tables(base):
    return G.table(f'GPT Image {base} token pricing (USD per 1M tokens)',
                   [('Item', False), ('AnyAIGC', True), ('OpenAI list', True), ('You save', True)],
                   [(None, G.token_rows('en', base))])


def token_billing():
    return [('Token billing', 'Prompt text, reference images and output priced separately'), ('1–10 images per call', 'Set with the n parameter'),
            (CONC, 'On by default for every account'), ('One balance', 'Works across 300+ models')]




def token_costs_25():
    out = []
    for h, q, s, n in [('E-commerce product shots in bulk', 'medium', '1536x1024', 1000), ('4K posters', 'high', '3840x2160', 100), ('One max-quality square image', 'max', '1024x1024', 1)]:
        a, o = cost_25(q, s)
        t = TOKENS_25[q][s]
        unit = 'image' if n == 1 else 'images'
        out.append((h, f'{n:,} {unit} at {s.replace("x", "×")}, <code>quality={q}</code>, about {t:,} output tokens each × ${T25["out"]} / 1M',
                    money(a * n, 2 if n > 1 else 4), f'List <s>{money(o * n, 2 if n > 1 else 4)}</s>'))
    return out


def token_costs_2():
    out = []
    for h, q, s, n in [('E-commerce product shots in bulk', 'medium', '1024x1024', 1000), ('High-quality banners', 'high', '1536x1024', 100), ('Quick drafts', 'low', '1024x1024', 1000)]:
        a, o = cost_2(q, s)
        out.append((h, f'{n:,} images at {s.replace("x", "×")}, <code>quality={q}</code>, OpenAI list ${OFFICIAL_IMG_2[q][s]} per image scaled by the ${T2["out"]} / 1M output rate',
                    money(a * n, 2), f'List <s>{money(o * n, 2)}</s>'))
    return out


def call_costs(base, model):
    p = float(CALL[base])
    ref = cost_25('high', '1024x1024') if base == '2.5' else cost_2('high', '1024x1024')
    return [('1,000 product images', f'1,000 × ${CALL[base]}, same price at any quality', money(p * 1000, 2), '1K output'),
            ('10,000 assets in bulk', f'10,000 × ${CALL[base]}', money(p * 10000, 2), '1K output'),
            ('One high-quality square image', f'${CALL[base]} per image on -c; about {money(ref[0])} token-billed', f'${CALL[base]}', f'List <s>{money(ref[1])}</s>'),
            ][:2] + [('100 posters at 4K', f'100 × ${CALL_4K[base]}, same price for 2K and 4K', money(float(CALL_4K[base]) * 100, 2), '2K / 4K output')]


def build(slug):
    if slug == 'gpt-image':
        return hub()
    m = MODELS[slug]
    return token_page(slug, m)


# ---------------------------------------------------------------- hub page
def hub():
    tok = []
    for s in ['gpt-image-2.5-sunburst', 'gpt-image-2.5-flare', 'gpt-image-2']:
        b = MODELS[s]['base']
        t = TOKEN[b]
        tok.append(f'<th scope="row"><a href="/en/models/{s}">{MODELS[s]["name"]}</a><small><code>{s}</code></small></th>'
                   f'<td class="o-num">${t["text_in"]}</td><td class="o-num">${t["img_in"]}</td><td class="o-num o-hl">${t["out"]}</td><td class="o-num o-save">{save(t["out"], OFFICIAL["out"])}%</td>')
    call = []
    for s in ['gpt-image-2.5-sunburst-c', 'gpt-image-2.5-flare-c', 'gpt-image-2-c']:
        b = MODELS[s]['base']
        call.append(f'<th scope="row"><a href="/en/models/{MODELS[s]["of"]}#per-image">{MODELS[s]["name"]}</a><small><code>{s}</code></small></th>'
                    f'<td class="o-num" colspan="2">1K ${CALL[b]} · 2K/4K ${CALL_4K[b]}</td><td class="o-num o-hl">from ${CALL[b]} / image</td><td class="o-num">-</td>')
    tables = G.table('GPT Image pricing (USD)', [('Model', False), ('Text input / 1M', True), ('Image input / 1M', True), ('Image output', True), ('Off list', True)],
                     [(f'Token-billed · OpenAI list: text input ${OFFICIAL["text_in"]}, image input ${OFFICIAL["img_in"]}, image output ${OFFICIAL["out"]} / 1M', tok), ('Per image (-c versions)', call)])
    models_html = ''
    cards = [
        ('gpt-image-2.5-sunburst', 'is-red', 'Top editing precision', "OpenAI's most capable image generation and editing model. Use it for retouching, commercial posters and edits where detail matters.", f'${T25["out"]}', 'image output / 1M tokens'),
        ('gpt-image-2.5-flare', 'is-blue', 'Fastest', "OpenAI's fastest high-quality image model, for everyday generation, bulk jobs and product features that need quick responses.", f'${T25["out"]}', 'image output / 1M tokens'),
        ('gpt-image-2', '', 'Previous generation', f'Released April 2026, the model behind ChatGPT Images 2.0. The lowest token rates in the lineup, about {S2}% off list.', f'${T2["out"]}', 'image output / 1M tokens'),
    ]
    for s, cls, tag, p, price, unit in cards:
        models_html += (f'        <li class="o-reveal"><a class="gi-model" href="/en/models/{s}"><span class="gi-model-tag {cls}">{tag}</span>'
                        f'<h3>{MODELS[s]["name"]}</h3><code>{s}</code><p>{p}</p>'
                        f'<span class="gi-model-price"><strong>{price}</strong>{unit}</span><span class="gi-model-go">View guide →</span></a></li>\n')
    choose = G.table('Which GPT Image model to use', [('If you need', False), ('Use', False), ('Why', False)], [(None, [
        '<th scope="row">Retouching, edits, commercial posters</th><td><a href="/en/models/gpt-image-2.5-sunburst">2.5 Sunburst</a></td><td>OpenAI positions it as the most precise editor, with xhigh and max quality</td>',
        '<th scope="row">Real-time generation in your product, bulk jobs</th><td><a href="/en/models/gpt-image-2.5-flare">2.5 Flare</a></td><td>Rated Very fast by OpenAI, same price as Sunburst</td>',
        f'<th scope="row">Existing gpt-image-2 integrations, lowest cost</th><td><a href="/en/models/gpt-image-2">GPT Image 2</a></td><td>Token rates about {S2}% off list, the lowest in the lineup</td>',
        '<th scope="row">High quality, large sizes, per-image budget</th><td><a href="/en/models/gpt-image-2.5-sunburst#per-image">2.5 Sunburst-c</a> / <a href="/en/models/gpt-image-2.5-flare#per-image">Flare-c</a></td><td>Flat price per image, cheaper than token billing at high quality and above</td>',
        '<th scope="row">Huge volumes at the lowest unit cost</th><td><a href="/en/models/gpt-image-2#per-image">GPT Image 2-c</a></td><td>' + f'${CALL["2"]} per 1K image at any quality</td>',
    ])])
    a25 = cost_25('high', '1024x1024')
    faqs = [
        ('How much does the GPT Image API cost?',
         f'Token-billed models: GPT Image 2.5 Sunburst and Flare cost ${T25["text_in"]} for text input, ${T25["img_in"]} for image input and ${T25["out"]} for image output per 1M tokens, about {S25}% off list. GPT Image 2 costs ${T2["text_in"]}, ${T2["img_in"]} and ${T2["out"]}, about {S2}% off list. Per-image -c versions: gpt-image-2.5-sunburst-c and gpt-image-2.5-flare-c are ${CALL["2.5"]} per 1K image and ${CALL_4K["2.5"]} per 2K/4K image; gpt-image-2-c is ${CALL["2"]} and ${CALL_4K["2"]}. See the model catalog for live prices.'),
        ('What is the difference between Sunburst, Flare and GPT Image 2?',
         'Sunburst and Flare make up GPT Image 2.5, released by OpenAI in September 2026. OpenAI positions Sunburst as the model with the highest editing precision and Flare as the fastest high-quality model for everyday work. They share the same official token rates and both add xhigh and max quality levels. GPT Image 2 is the previous generation, released in April 2026, with low, medium, high and auto quality.'),
        ('Token billing or per-image billing (-c): which should I pick?',
         f'With token billing, cost depends on size and quality: small low-quality images are very cheap, and cost rises with quality and resolution. The -c versions charge a flat price per image at any quality (1K and 2K/4K tiers), but return one image per request and do not support <code>n</code>, <code>mask</code> or transparent backgrounds. At 1024×1024 and high quality, GPT Image 2.5 costs about {money(a25[0])} per image with token billing versus ${CALL["2.5"]} on -c.'),
        ('Which endpoints are supported? Can I edit images?',
         f'Every GPT Image model, including the per-image -c versions, supports <code>POST /v1/images/generations</code> (text to image) and <code>POST /v1/images/edits</code> (image to image and multi-image compositing). Edits accept fewer than 16 reference images, 50MB in total. Token-billed models also support inpainting with a mask. See the <a href="{DOCS_GEN_25}">AnyAIGC API docs</a> for every field.'),
        conc_faq('the whole GPT Image lineup'),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    curl, py = code_gen('gpt-image-2.5-flare')
    return dict(
        title='GPT Image API pricing | gpt-image-2 and 2.5 models - AnyAIGC',
        desc=f'GPT Image API for gpt-image-2.5 Sunburst, Flare and gpt-image-2: up to {S2}% off list, ${CALL["2"]} per image, unlimited concurrency. Bank transfer and VAT invoices.',
        og_desc=f'One key for every GPT Image model: 2.5 Sunburst, 2.5 Flare and gpt-image-2, plus per-image versions from ${CALL["2"]} / image, with unlimited concurrency.',
        og_alt='AnyAIGC GPT Image API: gpt-image-2 and GPT Image 2.5',
        keywords='GPT Image API,gpt-image-2 API,gpt-image-2.5 API,gpt-image-2 API pricing,GPT Image API pricing,gpt-image-2.5-sunburst,gpt-image-2.5-flare,cheap GPT Image API,OpenAI image API alternative,GPT Image API for business,GPT Image API invoice,AnyAIGC',
        crumb='GPT Image', product='GPT Image API (AnyAIGC)', sku='gpt-image',
        product_desc='Access the OpenAI GPT Image lineup through AnyAIGC: gpt-image-2.5-sunburst, gpt-image-2.5-flare, gpt-image-2 and per-image versions, compatible with /v1/images/generations and /v1/images/edits.',
        offers=[('GPT Image 2.5 image output (per 1M tokens)', T25['out']), ('GPT Image 2 image output (per 1M tokens)', T2['out']),
                ('gpt-image-2.5 -c versions (per 1K image)', CALL['2.5']), ('gpt-image-2-c (per 1K image)', CALL['2'])],
        eyebrow='OpenAI · GPT Image', h1='GPT Image API<small>gpt-image-2 and the GPT Image 2.5 lineup</small>',
        lead=f'One API key for every OpenAI GPT Image model, <strong>from ${CALL["2"]} per image</strong>.',
        lead_sub=f'Text rendering, photoreal portraits, multilingual layouts and multi-image edits, all through the API. Token billing goes as low as {S2}% off list, or pick a -c version with a flat price per image.',
        facts=[('Models', '3 + per-image'), ('Endpoints', '/v1/images/generations · edits'), ('Max size', '3840×2160'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
        hero_imgs=('polyglot-collage', 'matcha-poster', 'candid-coast'),
        about_h2='Pick a GPT Image model',
        about_ps=[],
        models_html=models_html, choose=choose,
        gallery=['chinese-comic', 'matcha-poster', 'typography-poster', 'aliens-cafe', 'cantor-infographic', 'korean-hanok-ad', 'candid-flash', 'merch-grid', 'miami-comic'],
        gallery_h2='What GPT Image can make', gallery_lead='Every image below was generated with ChatGPT Images 2.0, which runs on gpt-image-2. Chinese typography, magazine infographics, photoreal shots and consistent comics all come out in one pass.',
        price_h2='GPT Image API pricing', price_lead='The 3 models are billed per token, so cost varies with size and quality. Each also has a per-image -c version with a flat price.',
        billing_label='Billing at a glance', billing=[('Two billing modes', 'Per token or flat per image'), ('One key', 'Works for the whole lineup'), (CONC, 'On by default for every account'), ('One balance', 'Works across 300+ models')],
        price_tables=tables + '      <h3 class="gi-h3 o-reveal">Choose by use case</h3>\n' + choose,
        price_note=f'Prices in USD. Token rates are the lowest listed in the model catalog; custom sizes, transparent backgrounds and similar options may cost more. -c prices: gpt-image-2.5-sunburst-c and flare-c ${CALL["2.5"]} per 1K image and ${CALL_4K["2.5"]} per 2K/4K image; gpt-image-2-c ${CALL["2"]} and ${CALL_4K["2"]}. See the <a href="{PRICING}">model catalog</a> for live prices.',
        costs_h3='Cost examples', costs_lead="Calculated from the rates above and output tokens from OpenAI's official calculator, excluding prompt text tokens.",
        costs=[(h, c, t, o) for h, c, t, o in [token_costs_25()[0], token_costs_2()[0], call_costs('2', 'gpt-image-2-c')[0]]],
        uses_h2='Where teams use it',
        uses=[('01 · E-commerce', 'Product shots and lifestyle scenes', 'Upload a product photo and swap the background or scene with the edits endpoint, while labels and packaging text stay sharp.', 'matcha-poster'),
              ('02 · Marketing', 'Posters, banners and ad creative', 'Generate finished posters with headlines, body copy and brand elements, up to 3840×2160.', 'korean-hanok-ad'),
              ('03 · Content', 'Infographics and explainers', 'Science explainers, academic posters and data cards with layout and text right on the first try.', 'cantor-infographic'),
              ('04 · Localization', 'Multilingual versions', 'Renders Chinese, Japanese, Korean, Arabic and more, so one design can ship in several languages quickly.', 'typography-poster')],
        steps=steps('gpt-image-2.5-flare'),
        codes=[('py', 'Python', 'POST /v1/images/generations', py), ('curl', 'cURL', 'POST /v1/images/generations', curl),
               ('edit', 'Image edits', 'POST /v1/images/edits', code_edit('gpt-image-2.5-sunburst'))],
        qs_h2='Get started with the GPT Image API in three steps',
        callout='To switch models, change only the <code>model</code> field: <code>gpt-image-2.5-sunburst</code>, <code>gpt-image-2.5-flare</code>, <code>gpt-image-2</code>, or a per-image <code>-c</code> version. Do not send <code>n</code> or <code>mask</code> to -c versions.',
        qs_note=f'The output format field is <code>format</code> (png / jpeg / webp), and the response returns <code>data[0].url</code>. Pass <code>response_format=b64_json</code> to get base64 instead. See the <a href="{DOCS_GEN_25}" target="_blank" rel="noopener">generations docs</a> and <a href="{DOCS_EDIT_25}" target="_blank" rel="noopener">edits docs</a> for every parameter.',
        family_h2='All GPT Image models', family_lead='Same API key; switch models by changing the model field.',
        faq_h2='GPT Image API FAQ', faqs=faqs,
        final_h2='One key for the whole GPT Image lineup', final_p='New accounts get 2 million tokens of trial credit. Generate a few images and see the results.',
        name='GPT Image', docs=DOCS_GEN_25,
    )


# ---------------------------------------------------------------- token-billed model pages
def token_page(slug, m):
    b = m['base']
    t = TOKEN[b]
    name = m['name']
    is25 = b == '2.5'
    short = {'gpt-image-2.5-sunburst': '2.5 Sunburst', 'gpt-image-2.5-flare': '2.5 Flare', 'gpt-image-2': 'GPT Image 2'}[slug]
    off = S25 if is25 else S2
    per = G.per_image_25('en') if is25 else G.per_image_2('en')
    tables = token_price_tables(b) + '      <h3 class="gi-h3 o-reveal">What one image costs</h3>\n' + \
        ("      <p class=\"o-note\">Estimated from output tokens per image in OpenAI's official calculator × the AnyAIGC output rate. Prompt and reference image input tokens are not included.</p>\n" if is25 else
         "      <p class=\"o-note\">Estimated from OpenAI's per-image output prices for GPT Image 2, scaled by the ratio of the AnyAIGC output rate to the list rate. Input tokens are not included.</p>\n") + per
    costs = token_costs_25() if is25 else token_costs_2()
    tables += G.call_block('en', C_OF[slug])
    q_levels = 'low, medium, high, xhigh, max and auto' if is25 else 'low, medium, high and auto'
    c_slug = C_OF[slug][0]
    c_link = f'<a href="#per-image"><code>{c_slug}</code></a>'
    if slug == 'gpt-image-2.5-sunburst':
        eyebrow, h1sub = 'OpenAI · gpt-image-2.5-sunburst', 'The GPT Image flagship for precise edits'
        lead = f"OpenAI's most capable image generation and editing model, <strong>about {off}% off list</strong>."
        lead_sub = f'OpenAI recommends it for workflows where editing precision matters most. On AnyAIGC, <code>{slug}</code> image output is ${t["out"]} per 1M tokens, versus ${OFFICIAL["out"]} list.'
        about_h2 = 'GPT Image 2.5 Sunburst: the most precise editor'
        about = ['OpenAI released GPT Image 2.5 in September 2026 as two models, Sunburst and Flare. OpenAI calls Sunburst its most capable model for image generation and editing, rates its performance as Highest, and recommends it for workflows where editing precision matters most. Flare is the one built for speed.',
                 'Sunburst takes text and image input and returns images. It adds xhigh and max quality levels on top of what GPT Image 2 offers. Sizes are flexible as long as ' + SIZE_RULES + '; OpenAI notes that resolutions above 2560×1440 are experimental. The snapshot is <code>gpt-image-2.5-sunburst-2026-09-08</code>.',
                 f'On AnyAIGC, Sunburst and Flare cost the same, about {100 - S25}% of the list price. If you would rather pay a fixed amount per image, use {c_link} at ${CALL["2.5"]} per 1K image.']
        spec = [('Performance (OpenAI)', 'Highest'), ('Speed (OpenAI)', 'Medium'), ('Quality', 'low – max'), ('Max size', '3840×2160'), ('Snapshot', '2026-09-08'), ('Endpoints', 'generations · edits')]
        hero_imgs = ('korean-hanok-ad', 'high-fashion', 'academic-poster')
        gallery = ['high-fashion', 'academic-poster', 'wolf-magazine', 'surreal-portrait', 'art-deco-bookmark', 'color-analysis']
        uses = [('01 · Polish', 'Commercial posters and key visuals', 'Generate finished posters at high, xhigh or max quality with more reliable detail and text.', 'korean-hanok-ad'),
                ('02 · Edits', 'Product scene swaps and inpainting', 'Upload a product photo and a mask to change only the background or one area while the product and its label stay intact.', 'matcha-poster'),
                ('03 · Publishing', 'Magazine layouts and print assets', 'Infographics, spreads and bookmarks with complex layouts come out close to final.', 'wolf-magazine'),
                ('04 · Fashion', 'Portraits and editorials', 'Photoreal portraits, styling and lighting for ad pitches and creative tests.', 'high-fashion')]
        diff = ('What is the difference between Sunburst and Flare?',
                f'Both are GPT Image 2.5, with the same official token rates and quality from low to max. OpenAI positions Sunburst as the model with the highest editing precision (performance Highest, speed Medium) and Flare as the fastest high-quality model for everyday work (performance Higher, speed Very fast). Pick Sunburst for retouching and edits, and <a href="/en/models/gpt-image-2.5-flare">Flare</a> for volume and speed. They cost the same on AnyAIGC.')
        default_q = 'high'
    elif slug == 'gpt-image-2.5-flare':
        eyebrow, h1sub = 'OpenAI · gpt-image-2.5-flare', 'The fastest high-quality GPT Image'
        lead = f"OpenAI's fastest high-quality image model for everyday and bulk generation, <strong>about {off}% off list</strong>."
        lead_sub = f'OpenAI rates its speed as Very fast. On AnyAIGC, <code>{slug}</code> image output is ${t["out"]} per 1M tokens, versus ${OFFICIAL["out"]} list, with unlimited concurrency.'
        about_h2 = 'GPT Image 2.5 Flare: fast without losing quality'
        about = ['GPT Image 2.5 Flare shipped alongside Sunburst when OpenAI released GPT Image 2.5 in September 2026. OpenAI describes it as the fastest high-quality model for everyday image generation, rating its performance as Higher and its speed as Very fast.',
                 'Flare uses the same parameters as Sunburst: text and image input, image output, quality from low to max, and flexible sizes as long as ' + SIZE_RULES + '. The snapshot is <code>gpt-image-2.5-flare-2026-09-08</code>.',
                 f'On AnyAIGC, Flare and Sunburst cost the same. At low quality an image costs a fraction of a cent, which suits drafts, bulk assets and real-time generation inside your product. For a fixed cost per image, use {c_link} at ${CALL["2.5"]} per 1K image.']
        spec = [('Performance (OpenAI)', 'Higher'), ('Speed (OpenAI)', 'Very fast'), ('Quality', 'low – max'), ('Max size', '3840×2160'), ('Snapshot', '2026-09-08'), ('Endpoints', 'generations · edits')]
        hero_imgs = ('merch-grid', 'candid-flash', 'matcha-poster')
        gallery = ['merch-grid', 'candid-flash', 'character-sheet', 'dunk-keyframes', 'moodboard', 'thai-street-panorama']
        uses = [('01 · Product features', 'Real-time generation in your app', 'AI avatars, greeting cards and wallpapers respond quickly, so the experience feels smooth.', 'candid-flash'),
                ('02 · E-commerce', 'Product images in bulk', 'Run one prompt template across thousands of images and keep costs down with medium quality.', 'merch-grid'),
                ('03 · Games and anime', 'Character sheets and storyboards', 'Character turnarounds, motion breakdowns and storyboard drafts for fast iteration.', 'character-sheet'),
                ('04 · Social', 'Everyday post images', 'Blog headers, social posts and video thumbnails in landscape, portrait or square.', 'moodboard')]
        diff = ('What is the difference between Flare and Sunburst?',
                f'Both are GPT Image 2.5, with the same official token rates and quality from low to max. Flare is built for speed (OpenAI rates it Very fast, performance Higher) and suits everyday and bulk generation. <a href="/en/models/gpt-image-2.5-sunburst">Sunburst</a> is built for editing precision (performance Highest, speed Medium). They cost the same on AnyAIGC.')
        default_q = 'medium'
    else:
        eyebrow, h1sub = 'OpenAI · gpt-image-2', 'The model behind ChatGPT Images 2.0'
        lead = f'GPT Image 2, released in April 2026, has the lowest token rates in the lineup, <strong>about {off}% off list</strong>.'
        lead_sub = f'On AnyAIGC, <code>{slug}</code> costs ${t["text_in"]} for text input and ${t["out"]} for image output per 1M tokens, versus ${OFFICIAL["text_in"]} and ${OFFICIAL["out"]} list.'
        about_h2 = 'GPT Image 2: a leap in text rendering and realism'
        about = ['OpenAI launched ChatGPT Images 2.0 on April 21, 2026, and released <code>gpt-image-2</code> in the API at the same time (snapshot <code>gpt-image-2-2026-04-21</code>). OpenAI describes it as fast, high-quality image generation and editing with flexible sizes. Image inputs are always processed at high fidelity, so <code>input_fidelity</code> is neither needed nor accepted.',
                 'Quality levels are low, medium, high and auto. Sizes are flexible as long as ' + SIZE_RULES + '. Common sizes include 1024×1024, 1536×1024, 1024×1536, 2048×2048, 2048×1152 and 3840×2160.',
                 f'OpenAI has since released GPT Image 2.5 (Sunburst and Flare), and its guide recommends 2.5 for new integrations. gpt-image-2 still works in the API, and on AnyAIGC it costs roughly one-seventh of 2.5, which makes it a good fit for cost-sensitive bulk jobs. For per-image billing, use {c_link} at ${CALL["2"]} per 1K image.']
        spec = [('Released', '2026-04-21'), ('Performance (OpenAI)', 'Higher'), ('Quality', 'low – high'), ('Max size', '3840×2160'), ('Image input', 'Always high fidelity'), ('Endpoints', 'generations · edits')]
        hero_imgs = ('chinese-comic', 'rice-macro', 'computer-lab')
        gallery = ['chinese-comic', 'rice-macro', 'computer-lab', 'cantor-infographic', 'polyglot-collage', 'aliens-cafe']
        uses = [('01 · CJK text', 'Posters and comics with Chinese text', 'Chinese headlines, dialogue and signage render cleanly, which helps for China-market creative.', 'chinese-comic'),
                ('02 · Photoreal', 'Photography-style assets', 'Macro, street and period photos with a texture close to real shots.', 'rice-macro'),
                ('03 · Education', 'Explainers and course visuals', 'Math proofs, science explainers and slide illustrations with a clear structure.', 'cantor-infographic'),
                ('04 · Cost first', 'High-volume asset production', 'The lowest token rates in the lineup; a low-quality image costs less than a tenth of a cent.', 'computer-lab')]
        diff = ('Can I still use gpt-image-2? Should I switch to GPT Image 2.5?',
                f'Yes, it still works. OpenAI\'s guide recommends GPT Image 2.5 for new integrations, but there is no deprecation notice for gpt-image-2 and it runs normally on AnyAIGC. GPT Image 2.5 adds xhigh and max quality; gpt-image-2 wins on price, with image output at ${T2["out"]} per 1M tokens on AnyAIGC versus ${T25["out"]} for 2.5. Switching only means changing the <code>model</code> field, so you can run the same prompts against <a href="/en/models/gpt-image-2.5-flare">2.5 Flare</a> and compare.')
        default_q = 'medium'
    notice = None if is25 else '<span><strong>A newer version is available:</strong> OpenAI has released GPT Image 2.5 and recommends it for new integrations. gpt-image-2 still works and has no deprecation notice. For new projects, take a look at <a href="/en/models/gpt-image-2.5-flare">GPT Image 2.5 Flare</a>.</span>'
    a1, o1 = (cost_25('medium', '1024x1024') if is25 else cost_2('medium', '1024x1024'))
    faqs = [
        (f'How much does the {name} API cost?',
         f'On AnyAIGC, <code>{slug}</code> is billed per token: ${t["text_in"]} for text input, ${t["img_in"]} for image input and ${t["out"]} for image output per 1M tokens, with cached text input at ${t["text_cache"]} and cached image input at ${t["img_cache"]}. OpenAI lists ${OFFICIAL["text_in"]}, ${OFFICIAL["img_in"]} and ${OFFICIAL["out"]}. A 1024×1024 image at medium quality costs about {money(a1)} in image output (about {money(o1)} at list). See the model catalog for live prices.'),
        diff,
        ('Which sizes, quality levels and formats are supported?',
         f'Common sizes are 1024×1024, 1536×1024, 1024×1536, 2048×2048, 2048×1152, 3840×2160, 2160×3840 and auto. Custom sizes work as long as {SIZE_RULES}. Quality levels are {q_levels}. Pick png, jpeg or webp with the <code>format</code> field, and get back an image URL or base64. The lowest price covers {"custom sizes" if is25 else "the preset sizes above"}; {"transparent backgrounds cost" if is25 else "custom sizes and transparent backgrounds cost"} more, as listed in the model catalog.'),
        ('How do I do image-to-image edits and inpainting?',
         f'Call <code>POST /v1/images/edits</code> with multipart/form-data. The <code>image</code> field accepts fewer than 16 reference images, 50MB in total. For inpainting, also send a <code>mask</code>: its transparent areas are what gets redrawn, and it must be a PNG under 4MB with the same size as the first image. See the <a href="{DOCS_EDIT_25 if is25 else DOCS_EDIT_2}">edits docs</a> for parameters.'),
        (f'Is there a per-image version? How is {c_slug} priced?',
         f'Yes. <code>{c_slug}</code> on AnyAIGC is the per-image version of {name}. It uses the same endpoints; only the <code>model</code> field changes. Each image has a flat price at any quality: ${CALL[b]} for 1K output and ${CALL_4K[b]} for 2K and 4K output. Each request returns one image, and <code>n</code>, <code>mask</code> and transparent backgrounds are not supported. At {"high quality and above" if is25 else "high quality"} or larger sizes, per-image billing is usually cheaper.'),
        conc_faq(slug),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    curl, py = code_gen(slug, quality=default_q)
    title = f'{name} API pricing | {off}% off list - AnyAIGC'
    pitch = ('the most precise OpenAI image editor' if slug.endswith('sunburst') else
             ('the fastest high-quality GPT Image' if slug.endswith('flare') else 'the model behind ChatGPT Images 2.0'))
    return dict(
        title=title,
        desc=f'{name} API, {pitch}: ${t["out"]}/1M image output, {off}% off list, unlimited concurrency, bank transfer and VAT invoices.',
        og_desc=f'{slug}: ${t["text_in"]} text input and ${t["out"]} image output per 1M tokens, about {off}% off list. Works with /v1/images/generations and /v1/images/edits, unlimited concurrency.',
        og_alt=f'AnyAIGC {name} API: about {off}% off list',
        keywords=f'{name} API,{slug},{slug} API,{slug} API pricing,{name} pricing,GPT Image API,cheap GPT Image API,OpenAI image API alternative,{name} API for business,GPT Image API invoice,AnyAIGC',
        crumb=f'{short} API' if is25 else 'GPT Image 2 API', product=f'{name} API (AnyAIGC)', sku=slug,
        product_desc=f'Access OpenAI {name} ({slug}) through AnyAIGC: compatible with /v1/images/generations and /v1/images/edits, billed per token at about {off}% off list, with unlimited concurrency.',
        offers=[('Text input (per 1M tokens)', t['text_in']), ('Image input (per 1M tokens)', t['img_in']), ('Image output (per 1M tokens)', t['out']),
                ('Cached text input (per 1M tokens)', t['text_cache']), ('Cached image input (per 1M tokens)', t['img_cache'])],
        eyebrow=eyebrow, h1=f'{name}<span class="o-sr"> API</span><small>{h1sub}</small>', lead=lead, lead_sub=lead_sub, notice=notice,
        facts=[('Model ID', slug), ('Image output', f'${t["out"]} / 1M'), ('Price', f'{off}% off list'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
        hero_imgs=hero_imgs, about_h2=about_h2, about_ps=about, spec=spec,
        gallery=gallery, gallery_h2=f'What {short} can make' if is25 else 'What GPT Image 2 can make',
        gallery_lead='Sample images were generated with ChatGPT Images 2.0 and show the text rendering, layout and realism of the GPT Image family.' + (' GPT Image 2.5 builds on this with finer detail and more precise edits.' if is25 else ''),
        price_h2=f'{name} API pricing', price_lead=f'Billed per token at fixed rates, with no subscription or monthly fee. Text input, image input and image output all cost about {100 - off}% of the OpenAI list price.',
        billing_label='Billing at a glance', billing=token_billing(), price_tables=tables,
        price_note=f'Prices in USD, charged per successful request. The table shows the lowest price in the model catalog; {"transparent backgrounds" if is25 else "custom sizes, transparent backgrounds"} and similar options cost more. Cached rates apply only when upstream reports cache usage. See the <a href="{PRICING}">model catalog</a> for live prices.',
        costs_h3='Cost examples', costs_lead='Calculated from the rates above, counting image output tokens only and excluding prompt text.',
        costs=costs,
        uses_h2=f'What {short} is good for', uses=uses,
        steps=steps(slug),
        codes=[('py', 'Python', 'POST /v1/images/generations', py), ('curl', 'cURL', 'POST /v1/images/generations', curl), ('edit', 'Image edits', 'POST /v1/images/edits', code_edit(slug))],
        qs_h2=f'Get started with the {name} API in three steps',
        callout=f'Want a flat price per image? Change <code>model</code> to <code>{c_slug}</code> (${CALL[b]} per 1K image, ${CALL_4K[b]} at 2K/4K) and drop <code>n</code> and <code>mask</code>.',
        qs_note=f'The response returns <code>data[0].url</code>; pass <code>response_format=b64_json</code> to get base64. Prompts can be up to 1000 characters. See the <a href="{DOCS_GEN_25 if is25 else DOCS_GEN_2}" target="_blank" rel="noopener">generations docs</a> for every parameter.',
        family_h2='All GPT Image models', family_lead='Same API key; switch models by changing the model field.',
        faq_h2=f'{name} API FAQ', faqs=faqs,
        final_h2=f'Start building with {name}', final_p='New accounts get 2 million tokens of trial credit. Generate a few images and see the results.',
        name=name, docs=DOCS_GEN_25 if is25 else DOCS_GEN_2,
    )
