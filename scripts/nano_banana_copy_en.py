# English copy for the Nano Banana topic pages. build(slug) returns the dict used by nano_banana_pages.py.
# Same keys as nano_banana_copy_zh.py. Prices are USD: one "from" price per image per model (model catalog lowest price);
# 2K / 4K live prices are shown in the model catalog. Never show CNY on English pages.
from decimal import Decimal

from nano_banana_data import (USD, OFFICIAL, MODELS, MODEL_SLUGS, RATIOS_14, SUPPORT, PRICING,
                              DOCS_21, DOCS_GEMINI, GOOGLE_DOC, save)
import nano_banana_layout as G

NL = '\n'
CONC = 'Unlimited concurrency'
S21, S2, SP = 'nano-banana-2.1', 'nano-banana-2', 'nano-banana-pro'


def usd(slug):
    """From price, e.g. $0.0128"""
    return '$' + USD[slug]


def off_save(slug):
    """Savings vs Google 1K list price, e.g. 62"""
    return save(USD[slug], OFFICIAL[slug]['1K'])


def official_str(slug):
    o = OFFICIAL[slug]
    return f'${o["1K"]} / ${o["2K"]} / ${o["4K"]}'


def cost(n, slug):
    """(calculation, total) at the from price, exact decimal arithmetic"""
    total = Decimal(USD[slug]) * n
    return f'{n:,} × {usd(slug)}', f'${total:,.2f}'


FAMILY = [
    ('nano-banana', 'Overview', 'Nano Banana lineup', 'Compare prices and specs across 3 models'),
    (S21, 'Latest', 'Nano Banana 2.1', f'Upgrade to Nano Banana 2 · from {usd(S21)} / image'),
    (SP, 'Pro', 'Nano Banana Pro', f'4K detail and complex layouts · from {usd(SP)} / image'),
    (S2, '', 'Nano Banana 2', f'Gemini 3.1 Flash Image · from {usd(S2)} / image'),
]

COMMON_FAQ = [
    ('Can AnyAIGC issue invoices, including VAT special invoices?',
     'Yes. AnyAIGC issues invoices for the amount you top up, including Chinese VAT general invoices and VAT special invoices. Send your billing details to support to request one.'),
    ('Can my company pay by bank transfer and sign a contract?',
     f'Yes. Companies can top up by corporate bank transfer and sign a service agreement, and get a dedicated support and technical contact. <a href="{SUPPORT}">Contact AnyAIGC support</a> to get started.'),
]
LICENSE_FAQ = ('Can I use the images commercially? Are they watermarked?',
               "Usage rights and content policies follow Google's official terms. Google embeds an invisible SynthID digital watermark in every image Nano Banana generates; it is not visible in the picture. AnyAIGC only provides API access and adds no extra restrictions on how you use the output. If an image involves real people's likenesses or third-party trademarks, make sure you have the rights you need.")


def conc_faq(name):
    return ('Are there concurrency limits? Does it work from mainland China?',
            f'AnyAIGC sets no concurrency limit on {name}, and every account gets this by default. The base URL is <code>https://anyaigc.ai</code>, which is tuned for networks in mainland China, so you usually do not need a proxy, a Google account, or an overseas credit card. The same key works for 300+ other models.')


def price_str(slug):
    return (f'from {usd(slug)} per image (the lowest price in the model catalog; live 2K and 4K prices are shown in the '
            f'<a href="{PRICING}">model catalog</a>)')


# ---------------------------------------------------------------- code samples
def code_native(model, ratio='16:9', size='2K', prompt='A plate of miniature banana dishes in a fine-dining restaurant, Gemini-themed decor, soft overhead light'):
    py = f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
MODEL = "{model}"

resp = requests.post(
    f"https://anyaigc.ai/v1beta/models/{{MODEL}}:generateContent",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "contents": [{{"role": "user", "parts": [{{"text": "{prompt}"}}]}}],
        "generationConfig": {{
            "responseModalities": ["TEXT", "IMAGE"],
            # aspectRatio / imageSize must go inside imageConfig; imageSize uses an uppercase K
            "imageConfig": {{"aspectRatio": "{ratio}", "imageSize": "{size}"}},
        }},
    }},
    timeout=300,
)
resp.raise_for_status()

# The image comes back as inlineData in parts (base64, no data: prefix); any caption is in text
for part in resp.json()["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        ext = part["inlineData"]["mimeType"].split("/")[-1]
        with open("output." + ext, "wb") as f:
            f.write(base64.b64decode(part["inlineData"]["data"]))
        print("Saved output." + ext)
    elif "text" in part:
        print(part["text"])'''
    curl = f'''curl "https://anyaigc.ai/v1beta/models/{model}:generateContent" \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "contents": [{{"role": "user", "parts": [{{"text": "{prompt}"}}]}}],
    "generationConfig": {{
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {{"aspectRatio": "{ratio}", "imageSize": "{size}"}}
    }},
    "response_format": "url"
  }}\''''
    return curl, py


def code_edit(model, size='2K'):
    return f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
MODEL = "{model}"


def image_part(path, mime="image/jpeg"):
    with open(path, "rb") as f:
        return {{"inlineData": {{"mimeType": mime, "data": base64.b64encode(f.read()).decode()}}}}


# Put the instruction and all reference images in the same parts list, labeling each image in text
parts = [
    {{"text": "Place the product from image 1 into the scene from image 2. Keep the product and its label text unchanged."}},
    {{"text": "Image 1:"}},
    image_part("product.jpg"),
    {{"text": "Image 2:"}},
    image_part("scene.jpg"),
]

resp = requests.post(
    f"https://anyaigc.ai/v1beta/models/{{MODEL}}:generateContent",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "contents": [{{"role": "user", "parts": parts}}],
        "generationConfig": {{
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {{"aspectRatio": "1:1", "imageSize": "{size}"}},
        }},
        "response_format": "url",  # return a temporary download link (non-streaming only); default is base64
    }},
    timeout=300,
)
resp.raise_for_status()
for part in resp.json()["candidates"][0]["content"]["parts"]:
    if "fileData" in part:
        print(part["fileData"]["fileUri"])'''


def code_chat(model):
    return f'''curl https://anyaigc.ai/v1/chat/completions \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "messages": [
      {{"role": "user", "content": "A minimalist product shot of a perfume bottle on white marble, side lighting"}}
    ]
  }}\''''


def codes(model, ratio='16:9', size='2K'):
    curl, py = code_native(model, ratio, size)
    return [('py', 'Python', f'Python · {model} text to image', py),
            ('curl', 'cURL', f'cURL · {model} text to image', curl),
            ('edit', 'Multi-image edit', f'Python · {model} reference image editing', code_edit(model, size)),
            ('chat', 'OpenAI compatible', 'cURL · /v1/chat/completions', code_chat(model))]


def steps(model):
    return [f'<strong>Sign up</strong>: <a href="{G.REG}">create an AnyAIGC account</a>. New accounts get 2 million tokens of trial credit, and top-ups start at $1.',
            '<strong>Create an API key</strong>: generate a key in the <a href="https://anyaigc.ai/console">console</a> and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Send a request</strong>: call <code>POST https://anyaigc.ai/v1beta/models/{model}:generateContent</code> (native Gemini format). Projects already on the OpenAI SDK can use <code>/v1/chat/completions</code> with <code>model</code> set to <code>{model}</code>.']


QS_NOTE = ('Authenticate with <code>Authorization: Bearer &lt;API Key&gt;</code>. <code>imageConfig.imageSize</code> accepts <code>1K</code>, <code>2K</code> or <code>4K</code> and defaults to 1K. '
           '<code>response_format</code> is a platform extension: set it to <code>url</code> to get a temporary <code>fileData.fileUri</code> link (non-streaming only); leave it out to get base64. '
           'When a request is blocked by safety filters, <code>finishReason</code> is <code>SAFETY</code> or <code>PROHIBITED_CONTENT</code> and no image is returned.')


# ---------------------------------------------------------------- pricing and comparison
def price_row(slug):
    m = MODELS[slug]
    ids = '<br>'.join(f'<code>{i}</code>' for i in m['ids'])
    return (f'<th scope="row">{m["name"]}<small>Save {off_save(slug)}% vs Google 1K</small></th><td>{ids}</td>'
            f'<td class="o-num o-hl">from {usd(slug)} / image</td><td class="o-num nb-off">{official_str(slug)}</td>')


PRICE_HEAD = [('Model', False), ('Model ID', False), ('AnyAIGC price (per image, from)', True), ('Google list price (1K / 2K / 4K)', True)]


def price_table(slugs):
    return G.table('Nano Banana per-image pricing (USD)', PRICE_HEAD, [(None, [price_row(s) for s in slugs])])


BILLING = [('Per image', 'Flat price per image, not per token'), ('1 image per call', 'A request usually returns 1 image'),
           (CONC, 'Default for every account'), ('Shared balance', 'One balance covers 300+ models')]
PRICE_NOTE = ('Prices are in USD and show the lowest price in the model catalog. 2K and 4K output can be priced differently; '
              f'see the live rates in the <a href="{PRICING}">model catalog</a>. You are billed per successful request, and prompts and reference images are not charged separately. '
              'Google list prices are Standard-tier USD rates from the '
              '<a href="https://ai.google.dev/gemini-api/docs/pricing" target="_blank" rel="noopener">Gemini API pricing page</a>, for reference only.')
COSTS_LEAD = 'Calculated at the from price per image. Check 2K and 4K rates in the model catalog.'


def compare_table(cur=None):
    cols = MODEL_SLUGS

    def cls(s):
        return ' class="nb-cur"' if s == cur else ''
    head = [('', False)] + [(f'<a href="/en/models/{s}">{MODELS[s]["name"]}</a>', False) for s in cols]

    def row(label, vals):
        return f'<th scope="row">{label}</th>' + ''.join(f'<td{cls(s)}>{v}</td>' for s, v in zip(cols, vals))
    rows = [
        row('AnyAIGC model ID', ['<br>'.join(f'<code>{i}</code>' for i in MODELS[s]['ids']) for s in cols]),
        row('Google name', [MODELS[s]['google'] for s in cols]),
        row('Positioning', ['Upgrade to Nano Banana 2 with better image quality, text and multi-turn consistency', 'Flash-speed workhorse image model', 'Reasoning-driven, pro-grade images for complex layouts and retouching']),
        row('Output resolution', ['1K / 2K / 4K', '1K / 2K / 4K (Google also offers 512px)', '1K / 2K / 4K']),
        row('Aspect ratios', ['14, including 1:4, 4:1, 1:8, 8:1', '14, including 1:4, 4:1, 1:8, 8:1', '10 (1:1 to 21:9)']),
        row('Reference images (up to 14)', ['10 object + 4 character', '10 object + 4 character', '6 object + 5 character + 3 style']),
        row('Google Search grounding', ['Web + image search', 'Web + image search', 'Web search']),
        row('Thinking', ['Configurable', 'Configurable', 'On by default, cannot be turned off']),
        row('AnyAIGC price', [f'from <strong>{usd(s)}</strong> / image' for s in cols]),
        row('Google list price', [f'1K ${OFFICIAL[s]["1K"]} · 2K ${OFFICIAL[s]["2K"]} · 4K ${OFFICIAL[s]["4K"]}' for s in cols]),
        row('Release', ['GA on 2026-10-06', 'Preview 2026-02-26, GA 2026-05-28', 'Preview 2025-11-20, GA 2026-05-28']),
    ]
    return G.table('Nano Banana 2.1, Nano Banana 2 and Nano Banana Pro specs compared', head, [(None, rows)], cls='nb-compare')


COMPARE_NOTE = (f'Specs are from the Google <a href="{GOOGLE_DOC["en"]}" target="_blank" rel="noopener">Gemini API image generation docs</a> and model list (read 2026-10-25). '
                f'Request fields follow the <a href="{DOCS_21}" target="_blank" rel="noopener">AnyAIGC API docs</a>.')

USES = [
    ('E-commerce', 'Product and lifestyle shots', 'Upload a product photo and swap the background, scene or model while keeping the packaging and label text intact. Get every aspect ratio a SKU needs in one go.'),
    ('Marketing', 'Posters and localized copy', 'Write headlines and selling points straight into the image, or translate the text on an existing poster into another language without touching the layout.'),
    ('Social', 'Assets for every platform', 'Render one concept at 1:1, 4:5, 9:16 and 16:9 for Instagram, TikTok, YouTube thumbnails and web banners.'),
    ('Education', 'Infographics and diagrams', 'Turn a concept, process or dataset into a labeled infographic, with Google Search grounding to keep the facts on screen accurate.'),
    ('Characters', 'Consistent characters', 'Use a few character references to produce a series of scenes and poses, ideal for picture books, comic storyboards and brand mascots.'),
    ('Design', 'Sketch to render', 'Add a one-line brief to a hand sketch, floor plan or product drawing and get a photoreal render, then keep refining it in conversation.'),
]


# ---------------------------------------------------------------- overview page
def hub():
    models = [
        (f'/en/models/{S21}', 'Latest · Recommended', 'Nano Banana 2.1', 'gemini-nano-banana-2.1',
         "Google's October 2026 upgrade to Nano Banana 2, with better image quality, text rendering and multi-turn character consistency, plus 1:8 and 8:1 ultra-wide ratios.", usd(S21), '/ image, from', False),
        (f'/en/models/{SP}', 'Pro grade', 'Nano Banana Pro', 'gemini-3-pro-image',
         'A reasoning image model built on Gemini 3 Pro, suited to complex layouts, dense text, commercial retouching and scenes that need real-world knowledge.', usd(SP), '/ image, from', False),
        (f'/en/models/{S2}', 'Flash speed', 'Nano Banana 2', 'gemini-3.1-flash-image',
         'Gemini 3.1 Flash Image: fast and low cost. Google recommends 2.1 for new projects, and existing integrations keep working.', usd(S2), '/ image, from', False),
    ]
    choose = G.table('How to choose a Nano Banana model', [('If you need', False), ('Use', False), ('Why', False)], [(None, [
        f'<th scope="row">New projects, everyday images, batch jobs</th><td><a href="/en/models/{S21}">Nano Banana 2.1</a></td><td>Lowest price in the lineup (from {usd(S21)} / image) and Google\'s main image model</td>',
        f'<th scope="row">Posters, infographics, dense text layouts</th><td><a href="/en/models/{SP}">Nano Banana Pro</a></td><td>Stronger reasoning keeps complex layouts and text more reliable</td>',
        f'<th scope="row">4K images and print materials</th><td><a href="/en/models/{SP}">Nano Banana Pro</a> / <a href="/en/models/{S21}">2.1</a></td><td>Both output 4K; Pro has finer detail, 2.1 costs less (see 4K rates in the model catalog)</td>',
        f'<th scope="row">Ultra-wide banners and long images (1:8, 8:1)</th><td><a href="/en/models/{S21}">Nano Banana 2.1</a></td><td>2.1 fixes stitching issues at extreme ratios in 2K / 4K</td>',
        f'<th scope="row">Existing gemini-3.1-flash-image integrations</th><td><a href="/en/models/{S2}">Nano Banana 2</a></td><td>Keeps working as is; moving to 2.1 only means changing the model name</td>',
    ])])
    faqs = [
        ('How much does the Nano Banana API cost?',
         f'Every Nano Banana model on AnyAIGC is billed per image: Nano Banana 2.1 from {usd(S21)}, Nano Banana 2 from {usd(S2)}, and Nano Banana Pro from {usd(SP)} per image. These are the lowest prices in the model catalog; live 2K and 4K prices are shown in the <a href="{PRICING}">model catalog</a>. You are billed per successful request.'),
        ('What is the difference between Nano Banana 2.1, Nano Banana 2 and Nano Banana Pro?',
         'Nano Banana 2.1 (gemini-nano-banana-2.1) is the upgrade to Nano Banana 2 that Google released on October 6, 2026, with better image quality, text rendering and multi-turn consistency. Nano Banana 2 (gemini-3.1-flash-image) is a Flash-class, high-throughput image model. Nano Banana Pro (gemini-3-pro-image) is built on Gemini 3 Pro with reasoning, for complex layouts and pro-grade retouching. All three output 1K, 2K and 4K.'),
        ('What is Nano Banana, and how does it relate to Gemini?',
         'Nano Banana is the nickname for Google Gemini image generation models. The original Nano Banana was Gemini 2.5 Flash Image, followed by Nano Banana Pro (Gemini 3 Pro Image), Nano Banana 2 (Gemini 3.1 Flash Image) and Nano Banana 2.1. All of them are called through the Gemini API generateContent endpoint.'),
        ('Which endpoints are supported? Can I edit images?',
         f'Both the native Gemini format <code>POST /v1beta/models/&lt;model&gt;:generateContent</code> and the OpenAI-compatible <code>/v1/chat/completions</code> are supported. For text to image, send a single text part. To edit or composite, put the instruction and the reference images (inlineData) in the same parts list, up to 14 reference images. See the <a href="{DOCS_21}">AnyAIGC API docs</a> for every field.'),
        conc_faq('every Nano Banana model'),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(
        name='Nano Banana', docs=DOCS_21,
        title='Nano Banana API Pricing & Access | 2.1, 2 and Pro - AnyAIGC',
        desc=f'Nano Banana API for 2.1, 2 and Pro from {usd(S21)} per image. 4K output, multi-image editing, unlimited concurrency, bank transfer and VAT special invoices.',
        og_desc=f'One key for every Google Nano Banana model: 2.1, 2 and Pro, from {usd(S21)} per image, 4K output, unlimited concurrency.',
        og_alt='AnyAIGC Nano Banana API: 2.1, 2 and Pro',
        keywords='Nano Banana API,Nano Banana API pricing,Nano Banana 2.1 API,Nano Banana Pro API,Nano Banana 2 API,gemini-nano-banana-2.1,gemini-3-pro-image,gemini-3.1-flash-image,Gemini image generation API,Nano Banana API key,Nano Banana API for business,AnyAIGC',
        crumb='Nano Banana', product='Nano Banana API (AnyAIGC)', sku='nano-banana', currency='USD',
        product_desc='Access every Google Nano Banana image model through AnyAIGC: gemini-nano-banana-2.1, gemini-3.1-flash-image and gemini-3-pro-image, compatible with Gemini generateContent and /v1/chat/completions.',
        offers=[(f'{MODELS[s]["name"]} (per image)', USD[s]) for s in (S21, S2, SP)],
        eyebrow='Google · Nano Banana', h1='Nano Banana API<small>Nano Banana 2.1, 2 and Pro</small>',
        lead=f'One API key for every Google Nano Banana model, <strong>from {usd(S21)} per image</strong>.',
        lead_sub='Text rendering, multi-image compositing, conversational editing and 4K output, all over the API. Flat per-image pricing instead of tokens, so costs are easy to plan.',
        facts=[('From', f'{usd(S21)} / image'), ('Up to', '4K'), ('References', 'Up to 14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
        hero_imgs=('golden-hour-portrait', 'neon-portrait', 'can-localization'),
        quote='Imagine it, then make it.<span>Photoreal, playful, precise or surreal: a single sentence is enough.</span>',
        models_h2='The Nano Banana lineup', models_lead='All three models share the same API; just switch <code>model</code>. Open a card for pricing, specs and code samples.',
        models=models,
        compare_h2='Nano Banana 2.1 vs 2 vs Pro', compare_lead='Resolution, aspect ratios, reference images and list prices in one table.', compare_table=compare_table(),
        compare_note=COMPARE_NOTE,
        choose=choose,
        price_h2='Nano Banana API pricing', price_lead='Every model is billed per image. One API key and one balance cover the whole lineup.',
        billing=BILLING, billing_label='Billing basics', price_tables=price_table([S21, SP, S2]), price_note=PRICE_NOTE,
        price_extra=f'      <h3 class="nb-h3 o-reveal">How to choose</h3>{NL}' + choose,
        costs_h3='Cost examples', costs_lead=COSTS_LEAD,
        costs=[('1,000 product shots', 'Nano Banana 2.1, ' + cost(1000, S21)[0], cost(1000, S21)[1], 'Everyday batch work'),
               ('100 posters', 'Nano Banana Pro, ' + cost(100, SP)[0], cost(100, SP)[1], 'Complex layouts and text'),
               ('1,000 images on Nano Banana 2', 'Nano Banana 2, ' + cost(1000, S2)[0], cost(1000, S2)[1], f'{cost(1000, S21)[1]} on 2.1')],
        gallery_h2='What Nano Banana can make', gallery_lead='Poster layouts, localized text, multi-image compositing, infographics and photoreal shots. These samples were published by Google.',
        gallery=['can-localization', 'multi-character-composite', 'woodchuck-text', 'stag-day-night-edit', 'earth-layers-infographic', 'golden-hour-portrait',
                 'sketch-to-car', 'impossible-typography', 'spinning-red-dress'],
        uses_h2='Nano Banana API use cases', uses=USES,
        qs_h2='Get started with the Nano Banana API', steps=steps('gemini-nano-banana-2.1'), codes=codes('gemini-nano-banana-2.1'),
        callout='To switch models, change only <code>MODEL</code>: <code>gemini-nano-banana-2.1</code>, <code>gemini-3.1-flash-image</code> or <code>gemini-3-pro-image</code>. Requests and responses are identical.',
        qs_note=QS_NOTE,
        family_h2='Nano Banana model pages', family_lead='Each model has its own page with full pricing and code samples.',
        faq_h2='Nano Banana API FAQ', faqs=faqs,
        final_h2='Start building with Nano Banana', final_p='Sign up for 2 million free tokens and use one key for the whole Nano Banana lineup and 300+ other models.',
    )


# ---------------------------------------------------------------- model pages
def model_page(slug):
    m = MODELS[slug]
    name, mid = m['name'], m['ids'][0]
    base = dict(name=name, crumb=name, sku=mid, currency='USD', docs=DOCS_21 if slug == S21 else DOCS_GEMINI,
                product=f'{name} API (AnyAIGC)',
                offers=[(f'{name} (per image)', USD[slug])],
                billing=BILLING, billing_label='Billing basics', price_tables=price_table([slug]), price_note=PRICE_NOTE,
                costs_h3='Cost examples', costs_lead=COSTS_LEAD,
                compare_h2=f'{name} vs the rest of the lineup', compare_table=compare_table(slug), compare_note=COMPARE_NOTE,
                uses_h2=f'{name} API use cases', uses=USES,
                qs_h2=f'Get started with the {name} API', steps=steps(mid),
                qs_note=QS_NOTE,
                family_h2='Other Nano Banana models', family_lead='Same API; change <code>model</code> to switch.',
                faq_h2=f'{name} API FAQ',
                quote='Imagine it, then make it.<span>Photoreal, playful, precise or surreal: a single sentence is enough.</span>')

    if slug == S21:
        faqs = [
            ('How much does the Nano Banana 2.1 API cost?',
             f'On AnyAIGC, Nano Banana 2.1 is billed per image, {price_str(slug)}. Google lists it at {official_str(slug)} per image for 1K / 2K / 4K. You are billed per successful request.'),
            ('What is Nano Banana 2.1 and when was it released?',
             'Nano Banana 2.1 (Gemini Nano Banana 2.1, model ID gemini-nano-banana-2.1) is an image generation and editing model Google released on October 6, 2026, as the upgrade to Nano Banana 2 (Gemini 3.1 Flash Image). Google positions it as the main high-efficiency model in the Nano Banana line.'),
            ('How is Nano Banana 2.1 different from Nano Banana 2?',
             '2.1 improves image quality, text rendering and character consistency across multi-turn edits, and fixes stitching issues at extreme ratios such as 1:4, 4:1, 1:8 and 8:1 in 2K / 4K. It also costs less per image. 2.1 drops the 512px (0.5K) tier and supports 1K, 2K and 4K only. The API is identical, so migrating means changing <code>model</code> to <code>gemini-nano-banana-2.1</code>.'),
            ('Should I use Nano Banana 2.1 or Nano Banana Pro?',
             f'Pick 2.1 for everyday images, batch jobs and ultra-wide ratios; it costs less (from {usd(slug)} / image). Pick Pro (from {usd(SP)} / image) for complex layouts, dense text and commercial assets that need stronger reasoning and detail.'),
            ('Which resolutions and aspect ratios are supported?',
             f'<code>imageConfig.imageSize</code> accepts <code>1K</code>, <code>2K</code> or <code>4K</code> and defaults to 1K; 512 is not supported. <code>imageConfig.aspectRatio</code> supports 14 ratios: {", ".join(RATIOS_14)}. For example, 16:9 renders at 2752×1536 in 2K and 5504×3072 in 4K.'),
            ('How many reference images can I upload? Can I turn thinking on or off?',
             'Up to 14 reference images per request: up to 10 object images and 4 character images. Thinking is controlled with <code>thinkingConfig.thinkingLevel</code>, which accepts <code>minimal</code> and <code>high</code>; thinkingBudget is not supported. You can also append <code>-thinking</code> or <code>-nothinking</code> to the model name.'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Nano Banana 2.1 API Pricing & Access | From {usd(slug)} - AnyAIGC',
            desc=f'Nano Banana 2.1 API (gemini-nano-banana-2.1) from {usd(slug)} per image, 4K output, 14 ratios, unlimited concurrency, bank transfer and VAT special invoices.',
            og_desc=f'Google Nano Banana 2.1 API from {usd(slug)} per image: 4K output, 14 aspect ratios, multi-image editing, unlimited concurrency.',
            og_alt='AnyAIGC Nano Banana 2.1 API pricing and access',
            keywords='Nano Banana 2.1 API,Nano Banana 2.1 API pricing,gemini-nano-banana-2.1,Nano Banana 2.1 API key,Nano Banana 2.1 4K,Nano Banana 2.1 vs Pro,Nano Banana 2.1 API for business,Nano Banana API for business,AnyAIGC',
            product_desc='Access Google Nano Banana 2.1 (gemini-nano-banana-2.1) image generation and editing through AnyAIGC, billed per image and compatible with Gemini generateContent.',
            eyebrow='Google · Nano Banana 2.1', h1='Nano Banana 2.1 API<small>gemini-nano-banana-2.1</small>',
            lead=f"Google's newest Nano Banana upgrade, <strong>from {usd(slug)} per image</strong>.",
            lead_sub='Better image quality, text rendering and multi-turn character consistency than Nano Banana 2, with 1K, 2K and 4K output and 1:8 and 8:1 ultra-wide ratios.',
            facts=[('From', f'{usd(slug)} / image'), ('vs Google 1K', f'Save {off_save(slug)}%'), ('Output', 'Up to 4K'), ('Ratios', '14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
            hero_imgs=('foggy-orange-sedan', 'indie-film-posters', 'spinning-red-dress'),
            about_h2='What is Nano Banana 2.1',
            about_ps=['Nano Banana 2.1 is an image generation and editing model Google released on October 6, 2026. Its official name is Gemini Nano Banana 2.1, and it upgrades Nano Banana 2 (Gemini 3.1 Flash Image). It keeps Flash-class speed and cost while improving image quality, text rendering and character consistency in multi-turn conversations.',
                      f'On AnyAIGC the model ID is <code>gemini-nano-banana-2.1</code>, billed per image from {usd(slug)}; live 2K and 4K prices are in the <a href="{PRICING}">model catalog</a>. You do not need a Google account or an overseas credit card, and it works directly from mainland China.'],
            spec=[('Model ID', '<code>gemini-nano-banana-2.1</code>'), ('Output', '1K / 2K / 4K (default 1K)'), ('Aspect ratios', '14, including 1:4, 4:1, 1:8, 8:1'),
                  ('References', 'Up to 14 (10 object + 4 character)'), ('Thinking', 'minimal / high'), ('Endpoints', 'generateContent · chat/completions')],
            features_h2='What Nano Banana 2.1 can do',
            features=[('Sharper text', 'Poster headlines, packaging copy, menus and infographic labels render cleanly, and you can set the type style and layout.', 'desert-poster-design'),
                      ('One-line edits', 'Upload an image and say what to change: lighting, background, removing an object. Everything else stays put, and you can keep refining over several turns.', 'stag-day-night-edit'),
                      ('Compositing with consistent characters', 'Up to 14 reference images, including 4 character images that keep people looking the same across shots.', 'multi-character-composite'),
                      ('Ultra-wide and tall ratios', 'Supports 4:1, 8:1, 1:4 and 1:8. 2.1 fixes stitching at these ratios in 2K / 4K, so banners and long images come out clean.', 'indie-film-posters')],
            price_h2='Nano Banana 2.1 API pricing', price_lead=f'Billed per image from {usd(slug)}. Live 2K and 4K prices are in the model catalog.',
            costs=[('1,000 product shots', cost(1000, slug)[0], cost(1000, slug)[1], 'Everyday batch work'),
                   ('500 social posts', cost(500, slug)[0], cost(500, slug)[1], 'Great for 4:5 and 9:16'),
                   ('10,000 catalog images', cost(10000, slug)[0], cost(10000, slug)[1], 'Large SKU catalogs')],
            gallery_h2='Nano Banana 2.1 samples', gallery_lead='These samples were published by Google on its Nano Banana model page.',
            gallery=['desert-poster-design', 'indie-film-posters', 'earth-layers-infographic', 'foggy-orange-sedan', 'spinning-red-dress', 'neon-portrait'],
            codes=codes(mid),
            callout='For faster responses without thinking, use the model name <code>gemini-nano-banana-2.1-nothinking</code>; for stronger composition reasoning, use <code>-thinking</code>.',
            faqs=faqs,
            final_h2='Start building with Nano Banana 2.1', final_p=f'Sign up for 2 million free tokens. From {usd(slug)} per image with unlimited concurrency.',
        )

    if slug == S2:
        faqs = [
            ('How much does the Nano Banana 2 API cost?',
             f'On AnyAIGC, Nano Banana 2 is billed per image, {price_str(slug)}. Both <code>gemini-3.1-flash-image</code> and <code>gemini-3.1-flash-image-preview</code> are available. Google lists it at {official_str(slug)} per image for 1K / 2K / 4K.'),
            ('Is Nano Banana 2 being shut down? Should I move to 2.1?',
             f'Google lists Nano Banana 2.1 as the recommended replacement for gemini-3.1-flash-image but has not announced a shutdown date, so you can keep calling it on AnyAIGC. For new projects, use <a href="/en/models/{S21}">Nano Banana 2.1</a>. Migrating only means changing the model name; the request format stays the same.'),
            ('Which model is Nano Banana 2?',
             'Nano Banana 2 is the nickname for Google Gemini 3.1 Flash Image. The preview launched on February 26, 2026, and the GA model gemini-3.1-flash-image followed on May 28. It brings most Pro-level capabilities to Flash-class speed and pricing.'),
            ('Is Nano Banana 2 better than Nano Banana Pro?',
             'The "2" does not mean it is a newer generation than Pro. Nano Banana 2 is a Flash-class model: faster and cheaper, good for batch work. Pro is built on Gemini 3 Pro, with stronger reasoning that keeps complex layouts and fine detail more reliable.'),
            ('Which resolutions and aspect ratios are supported?',
             f'<code>imageConfig.imageSize</code> accepts <code>1K</code>, <code>2K</code> or <code>4K</code>; the from price is in the table above and live 2K and 4K prices are in the <a href="{PRICING}">model catalog</a>. <code>imageConfig.aspectRatio</code> supports 14 ratios: {", ".join(RATIOS_14)}. Each request takes up to 14 reference images (10 object + 4 character).'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Nano Banana 2 API Pricing & Access | From {usd(slug)} - AnyAIGC',
            desc=f'Nano Banana 2 API (gemini-3.1-flash-image) from {usd(slug)} per image, 4K output, 14 ratios, unlimited concurrency, bank transfer and VAT special invoices.',
            og_desc=f'Google Nano Banana 2 (Gemini 3.1 Flash Image) API from {usd(slug)} per image, 4K output, unlimited concurrency.',
            og_alt='AnyAIGC Nano Banana 2 API pricing and access',
            keywords='Nano Banana 2 API,Nano Banana 2 API pricing,gemini-3.1-flash-image API,Gemini 3.1 Flash Image API,gemini-3.1-flash-image-preview,Nano Banana 2 to 2.1 migration,Nano Banana 2 API for business,Nano Banana API for business,AnyAIGC',
            product_desc='Access Google Nano Banana 2 (gemini-3.1-flash-image) image generation and editing through AnyAIGC, billed per image and compatible with Gemini generateContent.',
            eyebrow='Google · Nano Banana 2', h1='Nano Banana 2 API<small>gemini-3.1-flash-image</small>',
            lead=f'Gemini 3.1 Flash Image, <strong>from {usd(slug)} per image</strong>.',
            lead_sub='Flash-class speed with most Pro-level capabilities: text rendering, multi-image compositing, Google Search grounding and 4K output.',
            notice=f'Google recommends <a href="/en/models/{S21}">Nano Banana 2.1</a> for new projects (lower price, better quality). Nano Banana 2 has no announced shutdown date and keeps working.',
            facts=[('From', f'{usd(slug)} / image'), ('vs Google 1K', f'Save {off_save(slug)}%'), ('Ratios', '14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
            hero_imgs=('earth-layers-infographic', 'spinning-red-dress', 'foggy-orange-sedan'),
            about_h2='What is Nano Banana 2',
            about_ps=['Nano Banana 2 is the nickname for Google Gemini 3.1 Flash Image. The preview launched on February 26, 2026, and the GA release followed on May 28. It targets high-throughput development, delivering close to Pro-level quality, text rendering and editing at Flash-class speed and cost.',
                      f'On AnyAIGC you can call both the GA <code>gemini-3.1-flash-image</code> and the preview <code>gemini-3.1-flash-image-preview</code>, billed per image from {usd(slug)}; live 2K and 4K prices are in the <a href="{PRICING}">model catalog</a>.'],
            spec=[('Model ID', '<code>gemini-3.1-flash-image</code>'), ('Preview', '<code>gemini-3.1-flash-image-preview</code>'), ('Aspect ratios', '14, including 1:4, 4:1, 1:8, 8:1'),
                  ('References', 'Up to 14 (10 object + 4 character)'), ('Google Search', 'Web + image search'), ('Endpoints', 'generateContent · chat/completions')],
            features_h2='What Nano Banana 2 can do',
            features=[('Grounded in search', 'Google web and image search keep landmarks, niche objects and infographic facts accurate.', 'earth-layers-infographic'),
                      ('Conversational editing', 'Upload an image and change it with one sentence, over as many turns as you need. Handy for iterating on posters and product shots.', 'stag-day-night-edit'),
                      ('Legible text', 'Headlines, labels and captions stay clear and readable, ready for posters, menus and social posts.', 'woodchuck-text'),
                      ('Cinematic realism', 'Control lighting, depth of field and motion blur from the prompt, with fast turnaround.', 'spinning-red-dress')],
            price_h2='Nano Banana 2 API pricing', price_lead=f'Billed per image from {usd(slug)}. Live 2K and 4K prices are in the model catalog.',
            costs=[('1,000 product shots', cost(1000, slug)[0], cost(1000, slug)[1], 'Everyday batch work'),
                   ('500 social posts', cost(500, slug)[0], cost(500, slug)[1], 'Square and vertical formats'),
                   ('1,000 images on 2.1 instead', cost(1000, S21)[0], cost(1000, S21)[1], 'Same API, lower from price')],
            gallery_h2='Nano Banana 2 samples', gallery_lead='These samples were published by Google on its Nano Banana model page.',
            gallery=['earth-layers-infographic', 'woodchuck-text', 'spinning-red-dress', 'foggy-orange-sedan', 'spider-macro', 'golden-hour-portrait'],
            codes=codes(mid),
            callout='To move to Nano Banana 2.1, change <code>MODEL</code> to <code>gemini-nano-banana-2.1</code>. Requests and responses stay the same.',
            faqs=faqs,
            final_h2='Start building with Nano Banana 2', final_p=f'Sign up for 2 million free tokens. From {usd(slug)} per image with unlimited concurrency.',
        )

    # Nano Banana Pro
    faqs = [
        ('How much does the Nano Banana Pro API cost?',
         f'On AnyAIGC, Nano Banana Pro is billed per image, {price_str(slug)}. Both <code>gemini-3-pro-image</code> and <code>gemini-3-pro-image-preview</code> are available. Google lists it at {official_str(slug)} per image for 1K / 2K / 4K.'),
        ('Which model is Nano Banana Pro?',
         'Nano Banana Pro is the nickname for Google Gemini 3 Pro Image. The preview launched on November 20, 2025, and the GA model gemini-3-pro-image followed on May 28, 2026. It reasons before drawing, which suits complex layouts, dense text, commercial retouching and scenes that need real-world knowledge.'),
        ('Should I use Nano Banana Pro or Nano Banana 2.1?',
         f'Pick Pro for complex layouts, dense text, consistent multi-character scenes or pro-grade detail. Pick <a href="/en/models/{S21}">Nano Banana 2.1</a> for everyday images, batch jobs or 1:8 and 8:1 ultra-wide ratios; it costs less (from {usd(S21)} / image).'),
        ('Does Nano Banana Pro support 4K? Which aspect ratios?',
         f'Yes. <code>imageConfig.imageSize</code> accepts <code>1K</code>, <code>2K</code> or <code>4K</code>; live 2K and 4K prices are in the <a href="{PRICING}">model catalog</a>. <code>imageConfig.aspectRatio</code> supports 10 ratios: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9 and 21:9.'),
        ('How many reference images can I upload? Does it keep characters consistent?',
         'Up to 14 reference images per request: up to 6 object images, 5 character images and 3 style references. Character images keep the same person consistent across multiple shots.'),
        conc_faq(name),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(base,
        title=f'Nano Banana Pro API Pricing & Access | From {usd(slug)} - AnyAIGC',
        desc=f'Nano Banana Pro API (gemini-3-pro-image) from {usd(slug)} per image, 4K output, strong text and layouts, unlimited concurrency, bank transfer and VAT invoices.',
        og_desc=f'Google Nano Banana Pro (Gemini 3 Pro Image) API from {usd(slug)} per image, 4K output, unlimited concurrency.',
        og_alt='AnyAIGC Nano Banana Pro API pricing and access',
        keywords='Nano Banana Pro API,Nano Banana Pro API pricing,gemini-3-pro-image API,Gemini 3 Pro Image API,gemini-3-pro-image-preview,Nano Banana Pro 4K,Nano Banana Pro API key,Nano Banana Pro API for business,Nano Banana API for business,AnyAIGC',
        product_desc='Access Google Nano Banana Pro (gemini-3-pro-image) pro-grade image generation and editing through AnyAIGC, billed per image and compatible with Gemini generateContent.',
        eyebrow='Google · Nano Banana Pro', h1='Nano Banana Pro API<small>gemini-3-pro-image</small>',
        lead=f'Gemini 3 Pro Image, <strong>from {usd(slug)} per image</strong>.',
        lead_sub='Reasoning-driven, pro-grade images: complex layouts, dense text, consistent characters and 4K detail for commercial assets and retouching.',
        facts=[('From', f'{usd(slug)} / image'), ('vs Google 1K', f'Save {off_save(slug)}%'), ('References', 'Up to 14'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
        hero_imgs=('can-localization', 'futuristic-city', 'solar-infographic'),
        about_h2='What is Nano Banana Pro',
        about_ps=['Nano Banana Pro is the nickname for Google Gemini 3 Pro Image, built on Gemini 3 Pro. The preview launched on November 20, 2025, and the GA release followed on May 28, 2026. It reasons through composition and content before rendering, which suits complex graphic design, high-fidelity product shots and infographics that need real-world knowledge.',
                  f'On AnyAIGC you can call both the GA <code>gemini-3-pro-image</code> and the preview <code>gemini-3-pro-image-preview</code>, billed per image from {usd(slug)}; live 2K and 4K prices are in the <a href="{PRICING}">model catalog</a>.'],
        spec=[('Model ID', '<code>gemini-3-pro-image</code>'), ('Preview', '<code>gemini-3-pro-image-preview</code>'), ('Output', '1K / 2K / 4K'),
              ('Aspect ratios', '10 (1:1 to 21:9)'), ('References', '6 object + 5 character + 3 style'), ('Endpoints', 'generateContent · chat/completions')],
        features_h2='What Nano Banana Pro can do',
        features=[('Precise text localization', 'Translate the text on packaging or posters into another language while keeping the typeface and layout.', 'can-localization'),
                  ('Dense text and infographics', 'Long sentences, multi-paragraph notes and labels stay legible, ready for teaching visuals and product explainers.', 'solar-infographic'),
                  ('Multi-image compositing', 'Combine up to 14 references into one scene: character images keep people consistent, style images unify the look.', 'multi-character-composite'),
                  ('Sketch to render', 'Pair a line drawing with a material reference and get a photoreal 3D render.', 'sketch-to-car')],
        price_h2='Nano Banana Pro API pricing', price_lead=f'Billed per image from {usd(slug)}. Live 2K and 4K prices are in the model catalog.',
        costs=[('100 posters', cost(100, slug)[0], cost(100, slug)[1], 'Complex layouts and text'),
               ('1,000 retouched product shots', cost(1000, slug)[0], cost(1000, slug)[1], 'Commercial assets'),
               ('5,000 catalog images', cost(5000, slug)[0], cost(5000, slug)[1], 'Large campaigns')],
        gallery_h2='Nano Banana Pro samples', gallery_lead='These samples were published by Google on its Nano Banana Pro model page.',
        gallery=['can-localization', 'woodchuck-text', 'impossible-typography', 'futuristic-city', 'sketch-to-car', 'stag-day-night-edit'],
        codes=codes(mid, '4:3', '4K'),
        callout='Thinking is always on for Nano Banana Pro and cannot be turned off. It supports 10 aspect ratios only, not 1:4, 4:1, 1:8 or 8:1.',
        faqs=faqs,
        final_h2='Start building with Nano Banana Pro', final_p=f'Sign up for 2 million free tokens. From {usd(slug)} per image with unlimited concurrency.',
    )


def build(slug):
    return hub() if slug == 'nano-banana' else model_page(slug)
