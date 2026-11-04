# English copy for the Grok Image topic pages. build(slug) returns the fields grok_image_layout needs.
# Mirrors grok_image_copy_zh.py (same keys and list lengths); prices in USD straight from the model catalog.
from grok_image_data import (MODELS, TIERS, INPUT, tier, REG, PRICING, SUPPORT, DOCS_GEN, DOCS_EDIT, XAI_POST, XAI_MIGRATION, XAI_PRICING)

M20, M10, MQ = MODELS['grok-imagine-image-2.0'], MODELS['grok-imagine-image'], MODELS['grok-imagine-image-quality']
P20, P10, PQ = f'${M20["usd"]}', f'${M10["usd"]}', f'${MQ["usd"]}'
P20_HI, PQ_HI = f'${M20["usd_hi"]}', f'${MQ["usd_hi"]}'
O20 = f'${M20["official_lo"]}–${M20["official_hi"]}'
O10 = f'${M10["official_lo"]}'
IN = f'${INPUT["grok-imagine-image-2.0"][0]}'  # AnyAIGC price per input image for edits (2.0 and Quality)
XIN = f'${INPUT["grok-imagine-image-2.0"][1]}'  # xAI list price per input image for 2.0
T20 = lambda res, q: tier('grok-imagine-image-2.0', res, q)
TQ = lambda res: tier('grok-imagine-image-quality', res)
# Quality vs 2.0 Low at each resolution (AnyAIGC), e.g. $0.0044–$0.0045
_gap = sorted({f'{float(TQ(x)) - float(T20(x, "Low")):.4f}' for x in ('1K', '1.5K', '2K')})
GAP = f'${_gap[0]}' if len(_gap) == 1 else f'${_gap[0]}–${_gap[-1]}'


def usd(n, usd_price):
    """Cost example total in USD, 2 decimals: n images x unit price, e.g. $17.90"""
    return f'${n * float(usd_price):,.2f}'


def tier_offers(name, slug):
    """JSON-LD offers, one per tier: (name, raw USD price)"""
    return [(f'{name}, {res}{" " + q if q else ""} (per image)', p) for res, q, p, _ in TIERS[slug]]


FAMILY = [
    ('grok-image', 'Overview', 'Grok Image overview', 'Prices and model picks for all three'),
    ('grok-imagine-image-2.0', 'Recommended', 'Grok Imagine Image 2.0', f'From {P20} / image, typography and precise edits'),
    ('grok-imagine-image', '', 'Grok Imagine Image', f'{P10} / image, the lowest price in the series'),
    ('grok-imagine-image-quality', 'Retired', 'Grok Imagine Image Quality', 'Merged into 2.0 by xAI, old code still works'),
]
FAMILY_H2 = 'Grok Image models'
FAMILY_LEAD = 'Same API key, same endpoint. Switch models by changing the model field.'

# ---------------- Code examples ----------------
PROMPT = 'A retro concert poster titled “Neon Night Drive”, bold vintage type, sharp small print “Dec 31, 2026 · Austin” at the bottom'
EDIT_PROMPT = 'Replace the background with a snowy city street, keep the person and lighting unchanged'


def code_py(model, quality=True, resolution=True):
    q = '\n        "quality": "medium",  # low / medium / auto (2.0 only)' if quality else ''
    res = '1k / 2k' if model == 'grok-imagine-image' else '1k / 1.5k / 2k'
    r = f'\n        "resolution": "2k",  # {res}' if resolution else ''
    return f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{PROMPT}",
        "aspect_ratio": "2:3",  # 1:1, 16:9, 9:16, 3:2 and more{r}{q}
        "n": 1,
        "response_format": "b64_json",  # or url
    }},
    timeout=300,
)
resp.raise_for_status()
for i, item in enumerate(resp.json()["data"], 1):
    if item.get("b64_json"):
        with open(f"grok_{{i}}.jpg", "wb") as f:
            f.write(base64.b64decode(item["b64_json"]))
        print("saved", f"grok_{{i}}.jpg")
    else:  # with response_format url you get a temporary link, download it soon
        print(item["url"])'''


def code_curl(model, resolution=True):
    r = '\n    "resolution": "1k",' if resolution else ''
    return f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "{PROMPT}",
    "aspect_ratio": "16:9",{r}
    "n": 1,
    "response_format": "url"
  }}\''''


def code_edit(model):
    return f'''import os
import requests

# Image editing: upload the source image as multipart/form-data
API_KEY = os.environ["ANYAIGC_API_KEY"]
with open("photo.png", "rb") as img:
    resp = requests.post(
        "https://anyaigc.ai/v1/images/edits",
        headers={{"Authorization": "Bearer " + API_KEY}},
        files={{"image": img}},
        data={{"model": "{model}", "prompt": "{EDIT_PROMPT}", "n": 1}},
        timeout=300,
    )
resp.raise_for_status()
print(resp.json()["data"][0])'''


ENT_LEAD = 'E-commerce companies, design studios and content platforms can buy through a proper business process, with support for finance, legal and engineering.'

FAQ_INVOICE = ('Can AnyAIGC issue invoices, including VAT special invoices?',
               'Yes. AnyAIGC issues invoices for every top-up, including Chinese VAT general and special invoices based on the amount you actually top up. Send your billing details to support to get one.')
FAQ_CONTRACT = ('Can my company pay by bank transfer and sign a contract?',
                f'Yes. You can top up by corporate bank transfer, sign a service agreement, and get dedicated support and a technical contact. For business purchases, <a href="{SUPPORT}">talk to AnyAIGC sales</a>.')
FAQ_CN = ('Do I need an xAI account? Does it work from mainland China?',
          'No xAI account needed. Sign up on AnyAIGC to get an API key, no overseas credit card required. The endpoint is <code>https://anyaigc.ai</code>, reachable directly from mainland China, and the same key works with 300+ other models on the platform.')
FAQ_CONC = ('Is there a concurrency limit?', 'AnyAIGC sets no concurrency limit on the Grok Image models. Every account gets this by default, so batch jobs don’t need a quota request.')
FAQ_COMMERCIAL = ('Can I use the images commercially?', 'Usage rights and content policy follow xAI’s official terms. AnyAIGC only provides API access and adds no extra restrictions on what you do with the output.')
FAQ_DIFF = ('Image 2.0, Image or Quality: which one should I use?',
            f'Grok Imagine Image 2.0 (<code>grok-imagine-image-2.0</code>) is the model xAI currently recommends, with stronger typography, prompt following and editing. It starts at {P20} / image on AnyAIGC, so start new projects here. '
            f'Grok Imagine Image (<code>grok-imagine-image</code>) is the first-generation Imagine model at {P10} / image, the lowest price in the series, fine for plain text to image and existing code. '
            f'Grok Imagine Image Quality was retired by xAI on Nov 2, 2026, and its requests are now served by 2.0 at low quality.')

STEPS = lambda model, edit: [
    f'<a href="{REG}">Sign up for AnyAIGC</a>. New accounts get 2M free tokens, and you can top up from $1.',
    'Create an API key in the <a href="https://anyaigc.ai/console">console</a> and save it as the <code>ANYAIGC_API_KEY</code> environment variable.',
    f'Send a request to <code>POST https://anyaigc.ai/v1/images/generations</code> with <code>model</code> set to <code>{model}</code>'
    + ('. For edits, use <code>POST /v1/images/edits</code>.' if edit else '.'),
]

QS_NOTE = (f'Authenticate with <code>Authorization: Bearer &lt;API Key&gt;</code>. The response looks like <code>{{"created": ..., "data": [{{"b64_json": ...}}], "usage": {{"generated_images": 1, ...}}}}</code>; '
           f'with <code>response_format</code> set to <code>url</code> you get a temporary link, so download it promptly. Field reference in the AnyAIGC docs: <a href="{DOCS_GEN}" target="_blank" rel="noopener">Create image</a>, <a href="{DOCS_EDIT}" target="_blank" rel="noopener">Edit image</a>.')

WHY = [('One key, 300+ models', 'Grok Imagine, GPT Image, Nano Banana and Seedream share one API key and one balance.'),
       ('Direct access from China', 'The endpoint <code>https://anyaigc.ai</code> works on mainland networks, no xAI account needed.'),
       ('Fixed prices', 'A flat price per image, below xAI’s list price, with every charge visible in the console.'),
       ('Unlimited concurrency', 'Every account runs without a concurrency cap, so batch jobs don’t wait for approval.')]


def base(slug):
    return dict(family=FAMILY, family_h2=FAMILY_H2, family_lead=FAMILY_LEAD, why_h2='Why call it through AnyAIGC', why=WHY,
                docs=DOCS_GEN, ent_lead=ENT_LEAD, in_other=f'{FAMILY_TITLE_EN[slug]} 中文版', category='Image generation API')


FAMILY_TITLE_EN = {'grok-image': 'Grok Image API', 'grok-imagine-image-2.0': 'Grok Imagine Image 2.0 API',
                   'grok-imagine-image': 'Grok Imagine Image API', 'grok-imagine-image-quality': 'Grok Imagine Image Quality API'}

FEATURES_20 = [
    ('hero-39', 'Text and layout', 'Headlines, small print, schedules and captions are laid out the way a designer would, so dense posters, itineraries and infographics stay readable.'),
    ('tpl-background-removal', 'Precise edits', 'Change only what you ask for and keep the rest. Swap a background, recolor a product or remove clutter with one sentence.'),
    ('world-character', 'Consistent style', 'Characters, locations and props generated separately keep the same look, which suits storyboards, picture books and game assets.'),
    ('hero-34', 'Many styles', 'Photoreal, ink wash, pixel art, manga and retro posters all come out reliably, with clear detail and texture.'),
    ('resize-16x9', '15 aspect ratios', 'From 1:2 portrait to 21:9 widescreen. Pick a ratio and the model recomposes the scene instead of cropping it.'),
    ('tpl-ecommerce-listing', 'Product and marketing shots', 'Colorways, marketplace hero images and editorial product posters, ready to use from a single call.'),
]

GALLERY_20 = [('hero-41', 'Texture'), ('hero-37', 'Travel poster'), ('hero-40', 'Infographic'), ('hero-43', 'Cinematic'), ('hero-32', 'Manga'),
              ('hero-26', 'Ink wash'), ('hero-33', 'Pixel art'), ('hero-38', 'Typography'), ('hero-45', 'Journal'), ('hero-20', 'Product shot'),
              ('hero-10', 'Surreal'), ('hero-36', 'Poster')]

USES_20 = [
    ('tpl-ecommerce-listing', 'E-commerce', 'Product and lifestyle shots', 'Upload a product photo, change the background or color, and batch out hero images for different scenes.'),
    ('tpl-editorial-poster', 'Marketing', 'Posters and ads', 'Put the headline, selling points and fine print right in the image for event posters, social posts and banners.'),
    ('hero-39', 'Content', 'Infographics and itineraries', 'Timelines, maps, schedules and tips on one page, made for travel guides, explainers and study cards.'),
    ('world-location-1', 'Games', 'Characters and worlds', 'Characters, locations and props keep one art style even when generated separately, ready for concept art.'),
    ('tpl-professional-headshot', 'Portraits', 'Professional headshots', 'Turn one selfie into a clean, business-attire headshot for resumes and team pages.'),
    ('tpl-icon-maker', 'Design', 'Icons and merch', 'Icons, stickers, T-shirt and mug mockups. Generate a first pass, then hand it to a designer.'),
]


def build(slug):
    c = base(slug)
    if slug == 'grok-image':
        c.update(
            title=f'Grok Imagine API Pricing & Access | From {P10} - AnyAIGC',
            desc=f'Grok Imagine API pricing for 3 xAI image models, from {P10} per image: sharp typography, precise edits, unlimited concurrency, bank transfer and invoices.',
            keywords='Grok Imagine API,Grok Imagine API pricing,Grok image API,xAI image API,grok-imagine-image-2.0,Grok image generation API,Grok API key,Grok Image API for business,AnyAIGC',
            og_desc=f'The full Grok Imagine image API lineup from {P10} per image: typography, precise edits, 15 aspect ratios and unlimited concurrency.',
            og_alt_txt='AnyAIGC Grok Imagine API pricing and access', crumb='Grok Image',
            product='Grok Imagine Image API (AnyAIGC)', product_desc='Call xAI’s Grok Imagine image generation and editing models through AnyAIGC, billed per image, via /v1/images/generations.',
            sku='grok-imagine-image-2.0', offers=[('Grok Imagine Image 2.0, 1K Low (per image)', M20['usd']), ('Grok Imagine Image (per image)', M10['usd']),
                                                  ('Grok Imagine Image Quality, 1K (per image)', MQ['usd'])],
            kicker='xAI · Grok Imagine image models', h1='Grok Imagine API',
            lead=f'xAI’s image generation and editing models, all on one key. The recommended Image 2.0 starts at <strong>{P20} / image</strong> on AnyAIGC, about 55% below xAI’s list price, and the first-gen Image is {P10}. Unlimited concurrency.',
            facts=[('Models', '3'), ('Price', f'From {P10} / image'), ('Endpoints', 'Generate · Edit'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='Which Grok Image models are there', about_lead='All three are live on AnyAIGC, billed per image. Switch by changing the <code>model</code> field.',
            lineup=[
                ('grok-imagine-image-2.0', 'Recommended', 'Grok Imagine Image 2.0', 'xAI’s new model from August 2026, also the Quality mode on grok.com.',
                 ['Clean typography and small text', 'One model for generation and editing', '1k / 1.5k / 2k, low / medium quality'], ),
                ('grok-imagine-image', '', 'Grok Imagine Image', 'xAI’s first-generation Imagine model, launched with the Imagine API in early 2026.',
                 ['Text to image', '1k / 2k output', 'Fine for existing code']),
                ('grok-imagine-image-quality', 'Retired', 'Grok Imagine Image Quality', 'xAI’s high-quality mode from May 2026, merged into 2.0 on Nov 2.',
                 ['Served by 2.0 at low quality', 'No code changes required', 'Use 2.0 for new projects']),
            ],
            features_h2='What Grok Imagine can do', features_lead='These samples were generated by Imagine Image 2.0 and come from xAI’s launch post.', features=FEATURES_20,
            ratio_h2='One image, any aspect ratio', ratio_lead='The model recomposes the same scene for each aspect ratio (xAI samples). Set it with the <code>aspect_ratio</code> parameter.',
            ratio_alt='The same scene recomposed at {r}', ratio_list=['1:1', '3:4', '4:3', '9:16', '16:9', '2:3', '3:2', '9:19.5', '19.5:9', '9:20', '20:9', '1:2', '2:1', '21:9', '5:2', 'auto'],
            gallery_h2='Official Grok Imagine samples', gallery_lead='These images were generated by Imagine Image 2.0 and come from xAI’s launch post.', gallery=GALLERY_20,
            pricing_h2='Grok Imagine API pricing', pricing_lead=f'Billed per image, from {P10} / image (Image) and {P20} / image (Image 2.0).',
            billing=[('Per image', 'Billed per generated image, not per token'), ('By resolution and quality', '2.0 and Quality are priced per tier'), ('Edits', f'Plus {IN} per input image'), ('Unlimited concurrency', 'On by default for everyone')],
            price_rows=[('grok-imagine-image-2.0', 'Grok Imagine Image 2.0 (recommended)'), ('grok-imagine-image', 'Grok Imagine Image'),
                        ('grok-imagine-image-quality', 'Grok Imagine Image Quality (retired by xAI)')],
            price_note=f'Prices from the AnyAIGC model catalog; edits on 2.0 and Quality add {IN} per input image. xAI list prices: 2.0 is {O20} / image depending on resolution and quality, plus {XIN} per input image; Image is {O10} / image (<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI pricing</a>). Billed per successful generation; live prices are in the <a href="{PRICING}">model catalog</a>.',
            costs=[('1,000 first-gen images', f'1,000 × {P10}', usd(1000, M10['usd']), 'Image'),
                   ('1,000 Image 2.0 images', f'1,000 × 1K Low ${T20("1K", "Low")}', usd(1000, T20('1K', 'Low')), 'Image 2.0 · 1K Low'),
                   ('1,000 at 2K Medium', f'1,000 × 2K Medium ${T20("2K", "Medium")}', usd(1000, T20('2K', 'Medium')), 'Image 2.0 · 2K Medium')],
            uses_h2='Grok Imagine API use cases', uses=USES_20,
            qs_h2='Get started with the Grok Imagine API', steps=STEPS('grok-imagine-image-2.0', True),
            tabs=[('py', 'Python', 'Python · Image 2.0 text to image', code_py('grok-imagine-image-2.0')),
                  ('curl', 'cURL', 'cURL · returns an image URL', code_curl('grok-imagine-image-2.0')),
                  ('edit', 'Edit', 'Python · upload and edit an image', code_edit('grok-imagine-image-2.0'))],
            qs_note=QS_NOTE, ent_h2='Grok Imagine API for teams and enterprises',
            faq_h2='Grok Imagine API FAQ',
            faqs=[
                ('How much does the Grok Imagine API cost?', f'On AnyAIGC, Grok Imagine Image costs {P10} per image at 1k or 2k. Image 2.0 is priced by resolution and quality, from {P20} (1K Low) to {P20_HI} (2K Medium) per image, and Quality from {PQ} to {PQ_HI}. Edits add {IN} per input image. Everything is billed per image, not per token. xAI’s list price is {O20} / image for 2.0 and {O10} / image for Image. Live prices are in the model catalog.'),
                FAQ_DIFF,
                ('Has grok-imagine-image-quality been retired?', f'Yes. xAI retired <code>grok-imagine-image-quality</code> on Nov 2, 2026. Requests sent to that model name are now handled by <code>grok-imagine-image-2.0</code> with <code>quality: "low"</code>, and the request and response formats are unchanged. The model name still works on AnyAIGC from {PQ} / image, but 2.0 at Low quality is {GAP} cheaper per image at every resolution, so set <code>model</code> to <code>grok-imagine-image-2.0</code>.'),
                ('Which aspect ratios and resolutions are supported?', 'Set <code>aspect_ratio</code> to 1:1, 3:4, 4:3, 9:16, 16:9, 2:3, 3:2, 1:2, 2:1, 21:9 and more, or <code>auto</code> to let the model decide. Use <code>resolution</code> for <code>1k</code>, <code>1.5k</code> or <code>2k</code> (the first-gen Image supports 1k and 2k). Image 2.0 also supports <code>quality</code> (low / medium / auto).'),
                ('Can I edit an image from a reference?', 'Image 2.0 supports editing: send the source image and your instruction to <code>POST /v1/images/edits</code> as multipart/form-data. xAI supports compositing up to 5 reference images per request; the AnyAIGC docs currently show a single-image example, so check the AnyAIGC API docs for multi-image input.'),
                FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='Start building with Grok Imagine', final_p=f'Sign up and get 2M free tokens. From {P10} / image, unlimited concurrency.',
        )
    elif slug == 'grok-imagine-image-2.0':
        c.update(
            title=f'Grok Imagine Image 2.0 API Pricing | From {P20}/image - AnyAIGC',
            desc=f'Grok Imagine Image 2.0 API from {P20} per image, about 55% below xAI’s list price: sharp typography, precise edits, unlimited concurrency, invoices.',
            keywords='Grok Imagine Image 2.0 API,grok-imagine-image-2.0,Grok Imagine API pricing,Grok image API,Grok image editing API,xAI image API,Grok Imagine Image 2.0 API for business,AnyAIGC',
            og_desc=f'Grok Imagine Image 2.0 API from {P20} per image: typography, precise edits, 15 aspect ratios and unlimited concurrency.',
            og_alt_txt='AnyAIGC Grok Imagine Image 2.0 API pricing and access', crumb='Grok Imagine Image 2.0',
            product='Grok Imagine Image 2.0 API (AnyAIGC)', product_desc='Call xAI’s Grok Imagine Image 2.0 (grok-imagine-image-2.0) image generation and editing model through AnyAIGC, billed per image.',
            sku='grok-imagine-image-2.0', offers=tier_offers('Grok Imagine Image 2.0', 'grok-imagine-image-2.0'),
            kicker='xAI · Released August 2026', h1='Grok Imagine Image 2.0 API',
            lead=f'xAI’s new image generation and editing model lays out text like a designer, small print included. On AnyAIGC it starts at <strong>{P20} / image</strong> (1K Low), about 55% below xAI’s list price, with unlimited concurrency.',
            facts=[('Model', '<code>grok-imagine-image-2.0</code>'), ('Price', f'From {P20} / image'), ('Resolution', '1k / 1.5k / 2k'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='What is Grok Imagine Image 2.0',
            about_ps=[
                'Grok Imagine Image 2.0 is the image model xAI released in August 2026. It’s the new Quality mode on grok.com and in the Grok app, and <code>grok-imagine-image-2.0</code> in the API. xAI pitches it as a model for images you can actually use at work: it follows prompt details closely, plans text and layout like a designer, and keeps what you gave it across generations and edits.',
                f'According to xAI’s launch post, it placed second on both Arena’s image edit and text-to-image leaderboards (data as of Aug 7, 2026). Starting November 2026, xAI folded the older <code>grok-imagine-image-quality</code> into this model.',
                f'On AnyAIGC it’s priced by resolution and quality, from {P20} (1K Low) to {P20_HI} (2K Medium) per image, about 55% below xAI’s list price of {O20} / image. Edits add {IN} per input image.',
            ],
            spec=[('Model', '<code>grok-imagine-image-2.0</code>'), ('Generate', '/v1/images/generations'), ('Edit', '/v1/images/edits'),
                  ('Resolution', '1k / 1.5k / 2k'), ('Quality', 'low / medium / auto'), ('Aspect ratios', '15 + auto')],
            features_h2='What Grok Imagine Image 2.0 can do', features_lead='These samples were generated by Imagine Image 2.0 and come from xAI’s launch post.', features=FEATURES_20,
            ratio_h2='One image, any aspect ratio', ratio_lead='The model recomposes the same scene for each aspect ratio (xAI samples). Set it with the <code>aspect_ratio</code> parameter.',
            ratio_alt='The same scene recomposed at {r}', ratio_list=['1:1', '3:4', '4:3', '9:16', '16:9', '2:3', '3:2', '9:19.5', '19.5:9', '9:20', '20:9', '1:2', '2:1', '21:9', '5:2', 'auto'],
            world_h2='One art style for a whole world', world_lead='Characters, locations and props each come from a few lines of prompt and share one look, ready for storyboards and game design (xAI samples).',
            gallery_h2='Official Grok Imagine Image 2.0 samples', gallery_lead='These images were generated by Imagine Image 2.0 and come from xAI’s launch post; captions are adapted from xAI’s image descriptions.', gallery=GALLERY_20,
            pricing_h2='Grok Imagine Image 2.0 API pricing', pricing_lead=f'Priced by resolution and quality, from {P20} to {P20_HI} per image, not per token.',
            billing=[('Per image', 'Billed per generated image, not per token'), ('By resolution and quality', '1K / 1.5K / 2K, Low / Medium'), ('Edits', f'Plus {IN} per input image'), ('Unlimited concurrency', 'On by default for everyone')],
            price_rows=[('grok-imagine-image-2.0', 'Grok Imagine Image 2.0')],
            price_note=f'Prices from the AnyAIGC model catalog; edits add {IN} per input image. xAI list prices (Low–Medium): 1K $0.04–$0.06, 1.5K $0.05–$0.07, 2K $0.06–$0.08 / image, plus {XIN} per input image (<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI pricing</a>). Billed per successful generation; live prices are in the <a href="{PRICING}">model catalog</a>.',
            costs=[('1,000 images at 1K Low', f'1,000 × ${T20("1K", "Low")}', usd(1000, T20('1K', 'Low')), 'Batch generation'),
                   ('1,000 images at 2K Medium', f'1,000 × ${T20("2K", "Medium")}', usd(1000, T20('2K', 'Medium')), 'Most detail'),
                   ('100 edits at 1K Low', f'100 × (${T20("1K", "Low")} + {IN})', usd(100, float(T20('1K', 'Low')) + float(INPUT['grok-imagine-image-2.0'][0])), 'Output + input image')],
            uses_h2='Grok Imagine Image 2.0 use cases', uses=USES_20,
            qs_h2='Get started with the Grok Imagine Image 2.0 API', steps=STEPS('grok-imagine-image-2.0', True),
            tabs=[('py', 'Python', 'Python · grok-imagine-image-2.0 text to image', code_py('grok-imagine-image-2.0')),
                  ('curl', 'cURL', 'cURL · returns an image URL', code_curl('grok-imagine-image-2.0')),
                  ('edit', 'Edit', 'Python · upload and edit an image', code_edit('grok-imagine-image-2.0'))],
            qs_note=QS_NOTE, ent_h2='Grok Imagine Image 2.0 API for teams and enterprises',
            faq_h2='Grok Imagine Image 2.0 API FAQ',
            faqs=[
                ('How much does the Grok Imagine Image 2.0 API cost?', f'On AnyAIGC, Grok Imagine Image 2.0 (<code>grok-imagine-image-2.0</code>) is priced by resolution and quality. Low is ${T20("1K", "Low")} / ${T20("1.5K", "Low")} / ${T20("2K", "Low")} and Medium is ${T20("1K", "Medium")} / ${T20("1.5K", "Medium")} / ${T20("2K", "Medium")} per image at 1K / 1.5K / 2K. Edits add {IN} per input image. xAI’s list price is {O20} / image plus {XIN} per input image, so AnyAIGC is about 55% below it. Billed per successful generation; live prices are in the model catalog.'),
                ('How is Image 2.0 different from the earlier Grok Imagine?', f'2.0 improves typography, prompt following and editing. Small text in infographics and posters is sharper, and multi-turn edits keep the original content. It also adds <code>quality</code> (low / medium / auto) and two new ratios, 21:9 and 5:2. The first-gen <code>grok-imagine-image</code> is still available at {P10} / image.'),
                ('How should I set the quality parameter?', '<code>quality</code> accepts <code>low</code>, <code>medium</code> or <code>auto</code>. Per xAI’s docs, the default <code>auto</code> currently uses low for generation and medium for edits. Low is faster, medium adds detail. Medium costs more on AnyAIGC: at 1K, Low is ${T20("1K", "Low")} and Medium is ${T20("1K", "Medium")} per image.'),
                ('Which aspect ratios and resolutions are supported?', '<code>aspect_ratio</code> supports 1:1, 3:4, 4:3, 9:16, 16:9, 2:3, 3:2, 9:19.5, 19.5:9, 9:20, 20:9, 1:2, 2:1, 21:9 and 5:2, or <code>auto</code>. Set <code>resolution</code> to <code>1k</code>, <code>1.5k</code> or <code>2k</code>.'),
                ('How do I edit an image? Can I use several references?', 'Send <code>image</code>, <code>prompt</code> and <code>model</code> to <code>POST /v1/images/edits</code> as multipart/form-data. Describe only what should change and the rest stays as is. xAI supports compositing up to 5 reference images per request; the AnyAIGC docs currently show a single-image example, so check the AnyAIGC API docs for multi-image input.'),
                ('Does grok-imagine-image-quality still work?', f'xAI merged <code>grok-imagine-image-quality</code> into 2.0 on Nov 2, 2026, so those requests are served by 2.0 at low quality. Old code still runs on AnyAIGC (from {PQ} / image), but 2.0 at Low quality is {GAP} cheaper per image at every resolution, so switching <code>model</code> to <code>grok-imagine-image-2.0</code> saves money.'),
                FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='Start building with Grok Imagine Image 2.0', final_p=f'Sign up and get 2M free tokens. From {P20} per image, unlimited concurrency.',
        )
    elif slug == 'grok-imagine-image':
        c.update(
            title=f'Grok Imagine Image API Pricing & Access | {P10} - AnyAIGC',
            desc=f'Grok Imagine Image API, xAI’s first-gen model, at {P10} per image, about 40% below xAI’s $0.02 list price. 1k/2k output, unlimited concurrency, invoices.',
            keywords='Grok Imagine Image API,grok-imagine-image,Grok Imagine API pricing,Grok image API,xAI image API,Grok API key,Grok Imagine Image API for business,AnyAIGC',
            og_desc=f'Grok Imagine Image API at {P10} per image: xAI’s first-generation Imagine model, 1k / 2k output, unlimited concurrency.',
            og_alt_txt='AnyAIGC Grok Imagine Image API pricing and access', crumb='Grok Imagine Image',
            product='Grok Imagine Image API (AnyAIGC)', product_desc='Call xAI’s Grok Imagine Image (grok-imagine-image) text-to-image model through AnyAIGC, billed per image.',
            sku='grok-imagine-image', offers=[('Grok Imagine Image (per image)', M10['usd'])],
            kicker='xAI · First-generation Imagine model', h1='Grok Imagine Image API',
            lead=f'xAI’s first-generation text-to-image model from the Imagine API launch, with a simple interface and steady output. On AnyAIGC it’s <strong>{P10} / image</strong>, about 40% below xAI’s list price, with unlimited concurrency.',
            facts=[('Model', '<code>grok-imagine-image</code>'), ('Price', f'{P10} / image'), ('Resolution', '1k / 2k'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='What is Grok Imagine Image',
            about_ps=[
                f'Grok Imagine Image (<code>grok-imagine-image</code>) is the image model xAI launched with the Grok Imagine API in early 2026. xAI’s docs call it 1.0, with the snapshot name <code>{M10["alias"]}</code>. It turns a text description into an image, with multiple aspect ratios and 1k / 2k output.',
                f'In August 2026 xAI released Image 2.0, which is stronger at typography and editing for a slightly higher price on AnyAIGC (from {P20} / image versus {P10}). The first-gen model hasn’t been retired, so existing integrations keep working.',
                f'On AnyAIGC it’s {P10} per image; xAI’s list price is {O10} / image. On AnyAIGC this model uses the <code>/v1/images/generations</code> endpoint.',
            ],
            spec=[('Model', '<code>grok-imagine-image</code>'), ('Endpoint', '/v1/images/generations'), ('Resolution', '1k / 2k'),
                  ('Aspect ratios', '1:1, 16:9, 9:16 and more'), ('Output', 'b64_json / url'), ('Snapshot', f'<code>{M10["alias"]}</code>')],
            features_h2='What Grok Imagine Image can do',
            features=[
                (None, 'Text to image', 'Generate an image from one sentence, in common styles like photoreal, illustration and poster.'),
                (None, 'Multiple aspect ratios', 'Use <code>aspect_ratio</code> for 1:1, 16:9, 9:16, 3:2 and more, to fit covers, portrait posters and banners.'),
                (None, '1k / 2k output', 'Pick 1k or 2k with <code>resolution</code>. xAI prices both the same.'),
                (None, 'base64 or URL', 'Set <code>response_format</code> to <code>b64_json</code> for raw image data, or <code>url</code> for a temporary link.'),
                (None, 'Compatible interface', 'The request format matches OpenAI’s <code>/v1/images/generations</code>, so existing image code only needs a new <code>model</code>.'),
                (None, 'Easy upgrade to 2.0', f'When you need edits or better typography, switch <code>model</code> to <code>grok-imagine-image-2.0</code>, from {P20} / image.'),
            ],
            pricing_h2='Grok Imagine Image API pricing', pricing_lead=f'A flat {P10} per image, not per token.',
            billing=[('Per image', 'Billed per generated image, not per token'), ('One price', '1k and 2k cost the same'), ('Unlimited concurrency', 'On by default for everyone'), ('Shared balance', 'One balance for 300+ models')],
            price_rows=[('grok-imagine-image', 'Grok Imagine Image'), ('grok-imagine-image-2.0', 'Compare: Grok Imagine Image 2.0')],
            price_note=f'Prices from the AnyAIGC model catalog (Image {P10} / image; Image 2.0 from {P20} / image, with edits adding {IN} per input image). xAI list price: Image is {O10} / image at both 1K and 2K (<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI pricing</a>). Billed per successful generation; live prices are in the <a href="{PRICING}">model catalog</a>.',
            costs=[('100 illustrations', f'100 × {P10}', usd(100, M10['usd']), '1 image per call'),
                   ('1,000 batch images', f'1,000 × {P10}', usd(1000, M10['usd']), 'Unlimited concurrency'),
                   ('The same 1,000 on 2.0', f'1,000 × 1K Low {P20}', usd(1000, M20['usd']), '2.0 · adds editing')],
            uses_h2='Grok Imagine Image API use cases',
            uses=[(None, 'Content', 'Article and social images', 'Generate images from a headline or summary, and batch out article covers.'),
                  (None, 'Marketing', 'Ad creative', 'Spin up several takes on one theme for ad testing.'),
                  (None, 'Product', 'In-app image generation', 'Add text-to-image to your app with a clear per-image cost.'),
                  (None, 'Design', 'Concept sketches', 'Generate a few drafts to settle on a direction, then hand off to a designer.'),
                  (None, 'Games', 'Concept art', 'Quickly produce concept art for scenes, props and characters.'),
                  (None, 'Migration', 'Keep your existing code', 'Code written for xAI only needs a new base URL and key.')],
            qs_h2='Get started with the Grok Imagine Image API', steps=STEPS('grok-imagine-image', False),
            tabs=[('py', 'Python', 'Python · grok-imagine-image text to image', code_py('grok-imagine-image', quality=False)),
                  ('curl', 'cURL', 'cURL · returns an image URL', code_curl('grok-imagine-image'))],
            qs_note=QS_NOTE.replace(f', <a href="{DOCS_EDIT}" target="_blank" rel="noopener">Edit image</a>', ''),
            ent_h2='Grok Imagine Image API for teams and enterprises',
            faq_h2='Grok Imagine Image API FAQ',
            faqs=[
                ('How much does the Grok Imagine Image API cost?', f'On AnyAIGC, Grok Imagine Image (<code>grok-imagine-image</code>) costs {P10} per image, the same at 1k and 2k. xAI’s list price is {O10} / image. Billed per successful generation; live prices are in the model catalog.'),
                FAQ_DIFF,
                ('Will grok-imagine-image be retired?', f'This change doesn’t affect it. The model xAI retired on Nov 2, 2026 is <code>grok-imagine-image-quality</code>; <code>grok-imagine-image</code> is still available. If you need edits or better text rendering, consider <code>grok-imagine-image-2.0</code> (from {P20} / image).'),
                ('Which aspect ratios and resolutions are supported?', 'Set <code>aspect_ratio</code> to values like 1:1, 16:9, 9:16, 3:2, 2:3, 4:3 or 3:4, and <code>resolution</code> to <code>1k</code> or <code>2k</code>. The <code>quality</code> parameter is only supported by Image 2.0.'),
                ('Can it edit images?', 'On AnyAIGC, <code>grok-imagine-image</code> uses the generation endpoint <code>/v1/images/generations</code>. To upload and modify an image, call <code>/v1/images/edits</code> with <code>grok-imagine-image-2.0</code>.'),
                FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='Start building with Grok Imagine Image', final_p=f'Sign up and get 2M free tokens. {P10} per image, unlimited concurrency.',
        )
    elif slug == 'grok-imagine-image-quality':
        c.update(
            title='Grok Imagine Image Quality API Pricing & Migration - AnyAIGC',
            desc=f'Grok Imagine Image Quality API is now part of Image 2.0. Old code runs on AnyAIGC from {PQ}/image; migration steps, unlimited concurrency, invoices.',
            keywords='Grok Imagine Image Quality API,grok-imagine-image-quality,grok-imagine-image-quality retired,Grok Imagine API pricing,Grok image API,grok-imagine-image-2.0,Grok Imagine Image Quality API for business,AnyAIGC',
            og_desc=f'grok-imagine-image-quality is now part of Image 2.0. Old code keeps working on AnyAIGC from {PQ} per image, and moving to 2.0 costs less.',
            og_alt_txt='AnyAIGC Grok Imagine Image Quality API pricing and migration', crumb='Grok Imagine Image Quality',
            product='Grok Imagine Image Quality API (AnyAIGC)', product_desc='Call grok-imagine-image-quality (merged by xAI into Grok Imagine Image 2.0) through AnyAIGC, billed per image.',
            sku='grok-imagine-image-quality', offers=tier_offers('Grok Imagine Image Quality', 'grok-imagine-image-quality'),
            kicker='xAI · Released May 2026 · Merged into 2.0', h1='Grok Imagine Image Quality API',
            lead=f'xAI’s former high-quality image mode. Since Nov 2, 2026 it’s part of Image 2.0, and old code still runs on AnyAIGC from <strong>{PQ} / image</strong> with unlimited concurrency.',
            notice='<strong>xAI has retired this model.</strong> Since Nov 2, 2026, requests to <code>grok-imagine-image-quality</code> are served by Grok Imagine Image 2.0 at low quality. For new projects, use <a href="/en/models/grok-imagine-image-2.0">Grok Imagine Image 2.0</a>.',
            strip_label='Official Imagine Image 2.0 samples (Quality requests are now served by 2.0)',
            facts=[('Model', '<code>grok-imagine-image-quality</code>'), ('Price', f'From {PQ} / image'), ('Status', 'Merged into 2.0'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='What happened to grok-imagine-image-quality',
            about_ps=[
                'Grok Imagine Image Quality was the high-quality generation and editing mode xAI introduced in May 2026, focused on more realistic images and better multilingual text rendering. In August 2026 xAI released Image 2.0 and made it the new Quality mode on grok.com.',
                f'xAI announced in September 2026 and completed on Nov 2 the retirement of <code>grok-imagine-image-quality</code>. Generation and edit requests to that model name are now handled by <code>grok-imagine-image-2.0</code> with <code>quality: "low"</code>, and request and response formats are unchanged (<a href="{XAI_MIGRATION}" target="_blank" rel="noopener">xAI migration guide</a>).',
                f'The model name still works on AnyAIGC from {PQ} (1K) to {PQ_HI} (2K) per image. Image 2.0 at Low quality is {GAP} cheaper per image at every resolution, so moving to <code>grok-imagine-image-2.0</code> saves money and adds <code>quality: "medium"</code> and the new 21:9 and 5:2 ratios.',
            ],
            spec=[('Model', '<code>grok-imagine-image-quality</code>'), ('Status', 'Retired by xAI'), ('Served by', '<code>grok-imagine-image-2.0</code>'),
                  ('Quality', 'low'), ('Generate', '/v1/images/generations'), ('Edit', '/v1/images/edits')],
            features_h2='What you gain by moving to Image 2.0', features_lead='These samples were generated by Imagine Image 2.0 and come from xAI’s launch post.',
            features=[FEATURES_20[0], FEATURES_20[1], FEATURES_20[4]],
            gallery_h2='Official Image 2.0 samples', gallery_lead='Quality requests are now served by Image 2.0. These images were generated by Image 2.0 and come from xAI’s launch post.', gallery=GALLERY_20[:6],
            pricing_h2='Grok Imagine Image Quality API pricing', pricing_lead=f'Priced by resolution, from {PQ} to {PQ_HI} per image. Image 2.0 at Low quality costs less at every resolution.',
            billing=[('Per image', 'Billed per generated image, not per token'), ('By resolution', '1K / 1.5K / 2K, no quality parameter'), ('Edits', f'Plus {IN} per input image'), ('Unlimited concurrency', 'On by default for everyone')],
            price_rows=[('grok-imagine-image-quality', 'Legacy model name (retired by xAI)'), ('grok-imagine-image-2.0', 'Recommended: Grok Imagine Image 2.0')],
            price_note=f'Prices from the AnyAIGC model catalog; edits add {IN} per input image. xAI no longer publishes a list price for Quality; per xAI’s migration guide, its requests are now served as 2.0 at low quality (<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI pricing</a>). Billed per successful generation; live prices are in the <a href="{PRICING}">model catalog</a>.',
            costs=[('1,000 images on Quality', f'1,000 × 1K ${TQ("1K")}', usd(1000, TQ('1K')), 'Legacy model name'),
                   ('The same 1,000 on 2.0', f'1,000 × 1K Low ${T20("1K", "Low")}', usd(1000, T20('1K', 'Low')), 'Image 2.0 · Low'),
                   ('What you save', f'{usd(1000, TQ("1K"))} − {usd(1000, T20("1K", "Low"))}', f'Save {usd(1000, float(TQ("1K")) - float(T20("1K", "Low")))}', 'Per 1,000 images at 1K')],
            uses_h2='Migrate in three steps',
            uses=[(None, 'Step 1', 'Change the model name', 'Replace <code>"model": "grok-imagine-image-quality"</code> with <code>"grok-imagine-image-2.0"</code> in your request.'),
                  (None, 'Step 2', 'Add quality if needed', 'Add <code>"quality": "medium"</code> for more detail (it costs more than Low); leave it out to use the default <code>auto</code>.'),
                  (None, 'Step 3', 'Check the response', 'The format is unchanged: <code>data</code> still holds <code>b64_json</code> or <code>url</code>, so your parsing code stays the same.')],
            qs_h2='Code examples', steps=STEPS('grok-imagine-image-2.0', True),
            tabs=[('py', 'Python', 'Python · after migration (grok-imagine-image-2.0)', code_py('grok-imagine-image-2.0')),
                  ('curl', 'cURL', 'cURL · legacy model name still works', code_curl('grok-imagine-image-quality'))],
            qs_note=QS_NOTE, ent_h2='Grok Imagine Image Quality API for teams and enterprises',
            faq_h2='Grok Imagine Image Quality API FAQ',
            faqs=[
                ('Has grok-imagine-image-quality been retired?', 'Yes. xAI retired <code>grok-imagine-image-quality</code> on Nov 2, 2026. Requests are now handled by <code>grok-imagine-image-2.0</code> with <code>quality: "low"</code>, and request and response formats are unchanged. The model name still works on AnyAIGC; for new projects use <a href="/en/models/grok-imagine-image-2.0">Grok Imagine Image 2.0</a>.'),
                ('How much does the Grok Imagine Image Quality API cost?', f'On AnyAIGC it’s {PQ} at 1K, ${TQ("1.5K")} at 1.5K and {PQ_HI} at 2K per image, plus {IN} per input image for edits. That’s {GAP} more than Image 2.0 at Low quality at each resolution. xAI no longer publishes a separate list price for Quality. Billed per successful generation; live prices are in the model catalog.'),
                ('What code do I need to change to move to 2.0?', 'Only set <code>model</code> to <code>grok-imagine-image-2.0</code>. The endpoint, request fields and response format stay the same. 2.0 also supports <code>quality</code> (low / medium / auto) and the 21:9 and 5:2 ratios.'),
                ('What happens if I don’t change anything?', 'Requests won’t fail. They’re served by 2.0 at low quality, and the <code>model</code> field in the response shows the model that actually handled them. You also keep paying the Quality price, which is higher than 2.0 Low. If you want medium quality, switch to 2.0 and pass <code>quality</code>.'),
                FAQ_DIFF, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT, FAQ_COMMERCIAL,
            ],
            final_h2='Switch from Quality to Image 2.0', final_p=f'From {P20} / image, cheaper than Quality at every resolution, with stronger typography and editing and unlimited concurrency.',
        )
    return c
