# English copy for the Grok Video topic pages. build(slug) returns the fields grok_video_layout / grok_image_layout need.
# Mirrors grok_video_copy_zh.py (same keys and list lengths); prices in USD straight from the model catalog.
from grok_video_data import (MODELS, TIERS, INPUT_IMG, INPUT_VID, DOCS_GEN, DOCS_EDIT, DOCS_QUERY, XAI_15_POST, XAI_PRICING, XAI_API, tier, cny)  # noqa: F401
from grok_image_data import REG, PRICING, SUPPORT
from grok_video_layout import money

S15, SL, S10 = 'grok-imagine-video-1.5-preview', 'grok-imagine-video-1.5-lite', 'grok-imagine-video'
D = lambda usd: f'${usd}'
P15, PL, P10 = D(MODELS[S15]['usd']), D(MODELS[SL]['usd']), D(MODELS[S10]['usd'])
P15_720, PL_720, P10_720 = D(tier(S15, '720p')), D(tier(SL, '720p')), D(tier(S10, '720p'))
PL_1080 = D(tier(SL, '1080p'))
IMG15, IMG10, VID10 = D(INPUT_IMG[S15][0]), D(INPUT_IMG[S10][0]), D(INPUT_VID[S10][0])
SRC = f' (<a href="{XAI_PRICING}" target="_blank" rel="noopener">xAI pricing</a>)'
TAIL = f'Billed per second of successfully generated video. Live prices are on the <a href="{PRICING}">model catalog</a>.'

FAMILY = [
    ('grok-video', 'Overview', 'Grok Video overview', 'Prices and model picks for all three'),
    (S15, 'Recommended', 'Grok Imagine Video 1.5', f'From {P15} / sec, better visuals, motion and dialogue'),
    (SL, 'Lowest price', 'Grok Imagine Video 1.5 Lite', f'From {PL} / sec, built for volume'),
    (S10, '', 'Grok Imagine Video', f'From {P10} / sec, supports video editing'),
]
FAMILY_H2 = 'Grok Video models'
FAMILY_LEAD = 'Same API key, same endpoint. Switch models by changing the model field.'

# ---------------- Code examples ----------------
PROMPT = 'A small seaside town at dawn, an orange cat strolls down stone steps, sound of waves and distant gulls, cinematic'
IMG_URL = 'https://example.com/first-frame.jpg'


def code_py(model, res='720p'):
    return f'''import os
import time
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
HEADERS = {{"Authorization": "Bearer " + API_KEY}}

# 1. Submit the job
task = requests.post(
    "https://anyaigc.ai/v1/videos/generations",
    headers=HEADERS,
    json={{
        "model": "{model}",
        "prompt": "{PROMPT}",
        "duration": 6,  # 1-15 seconds, billed per second
        "aspect_ratio": "16:9",  # 16:9 / 9:16 / 1:1
        "resolution": "{res}",  # higher resolution costs more per second
    }},
    timeout=60,
).json()
task_id = task.get("request_id") or task.get("id")

# 2. Poll for the result (usually tens of seconds to a few minutes)
while True:
    r = requests.get(f"https://anyaigc.ai/v1/videos/{{task_id}}", headers=HEADERS, timeout=30).json()
    if r.get("status") in ("done", "completed", "succeeded"):
        print(r.get("video_url") or r["video"]["url"])  # temporary link, download it soon
        break
    if r.get("status") in ("failed", "expired"):
        raise RuntimeError(r)
    time.sleep(10)'''


def code_curl(model, res='480p'):
    return f'''# Submit an image-to-video job: image is the first frame, aspect ratio follows the image
curl https://anyaigc.ai/v1/videos/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "Slow push-in, the person turns and smiles",
    "image": {{"url": "{IMG_URL}"}},
    "duration": 5,
    "aspect_ratio": "16:9",
    "resolution": "{res}"
  }}'

# Check the job; when status is done, read the video link
curl https://anyaigc.ai/v1/videos/<request_id> \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY"'''


def code_edit():
    return '''# Edit a video: source video URL + an instruction; output length matches the source
curl https://anyaigc.ai/v1/videos/edits \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "grok-imagine-video",
    "prompt": "Change the hoodie to red, keep everything else the same",
    "video": {"url": "https://example.com/source.mp4"},
    "aspect_ratio": "16:9",
    "resolution": "480p"
  }'
# You get a job ID back; poll GET /v1/videos/<request_id> the same way'''


STEPS = lambda model: [
    f'<a href="{REG}">Sign up for AnyAIGC</a>. New accounts get 2M free tokens, and you can top up from $1.',
    'Create an API key in the <a href="https://anyaigc.ai/console">console</a> and save it as the <code>ANYAIGC_API_KEY</code> environment variable.',
    f'Submit a job to <code>POST https://anyaigc.ai/v1/videos/generations</code> with <code>model</code> set to <code>{model}</code>, then poll <code>GET /v1/videos/{{request_id}}</code> for the result.',
]
QS_NOTE = (f'Video generation is asynchronous: you get a job ID back, poll until it completes, then fetch the video link. The link is temporary, so download it promptly. Field reference in the AnyAIGC docs: '
           f'<a href="{DOCS_GEN}" target="_blank" rel="noopener">Create video</a>, <a href="{DOCS_QUERY}" target="_blank" rel="noopener">Get video</a>, '
           f'<a href="{DOCS_EDIT}" target="_blank" rel="noopener">Edit video</a>.')
QS_NOTE_NO_EDIT = QS_NOTE.replace(f', <a href="{DOCS_EDIT}" target="_blank" rel="noopener">Edit video</a>', '')

ENT_LEAD = 'Short-video studios, e-commerce teams and content platforms can buy through a proper business process, with support for finance, legal and engineering.'
FAQ_INVOICE = ('Can AnyAIGC issue invoices, including VAT special invoices?',
               'Yes. AnyAIGC issues invoices for every top-up, including Chinese VAT general and special invoices based on the amount you actually top up. Send your billing details to support to get one.')
FAQ_CONTRACT = ('Can my company pay by bank transfer and sign a contract?',
                f'Yes. You can top up by corporate bank transfer, sign a service agreement, and get dedicated support and a technical contact. For business purchases, <a href="{SUPPORT}">talk to AnyAIGC sales</a>.')
FAQ_CN = ('Do I need an xAI account? Does it work from mainland China?',
          'No xAI account needed. Sign up on AnyAIGC to get an API key, no overseas credit card required. The endpoint is <code>https://anyaigc.ai</code>, reachable directly from mainland China, and the same key works with 300+ other models on the platform.')
FAQ_CONC = ('Is there a concurrency limit?', 'AnyAIGC sets no concurrency limit on the Grok Video models. Every account gets this by default, so batch jobs don’t need a quota request.')
FAQ_ASYNC = ('Why don’t I get the video back right away?', 'Video generation is asynchronous. Submitting returns a job ID; poll <code>GET /v1/videos/{request_id}</code> about every 10 seconds and read the video link once the job completes. Most jobs take tens of seconds to a few minutes. The link is temporary, so download and store the file promptly.')
FAQ_AUDIO = ('Do the videos have sound?', 'Yes. Grok Imagine generates picture and sound together, including sound effects, ambience and dialogue, so you don’t need a separate voiceover. Video 1.5 and 1.5 Lite support lip-synced speech.')
FAQ_DIFF = ('Video 1.5, 1.5 Lite or Video: which one should I use?',
            f'<strong>Grok Imagine Video 1.5</strong> (<code>{S15}</code>) leads the series on visuals, motion and dialogue, from {P15} / sec, a good fit for ads and finished pieces. '
            f'<strong>1.5 Lite</strong> (<code>{SL}</code>) is the cheapest in the series, from {PL} / sec, goes up to 1080p, and suits high-volume jobs and drafts. '
            f'<strong>Grok Imagine Video</strong> (<code>{S10}</code>) is the first-generation model, from {P10} / sec, and the only one in the series that edits an uploaded video.')

WHY = [('One key, 300+ models', 'Grok Imagine, Sora, Veo, Kling and other video models share one API key and one balance with chat and image models.'),
       ('Direct access from China', 'The endpoint <code>https://anyaigc.ai</code> works on mainland networks, no xAI account needed.'),
       ('Below xAI list price', 'Billed per second, with every tier about 40% below xAI’s list price and every charge visible in the console.'),
       ('Unlimited concurrency', 'Every account runs without a concurrency cap, so batch jobs don’t wait for approval.')]

FEATURES = [
    ('speech-1', 'Native sound and dialogue', 'Picture, sound effects, ambience and dialogue come out in one pass, with lip sync, so there’s no voiceover step.'),
    ('property', 'Text to video and image to video', 'Generate a clip from one sentence, or upload a first frame and bring it to life.'),
    ('try-on', 'Products and try-on', 'Put a product shot and a person in the same clip, handy for e-commerce and virtual try-on.'),
    ('mockup-moon', 'Mockups to real footage', 'Turn sketches, 3D models or prototypes into realistic shots, then swap the setting.'),
    ('perfume', 'Ad-ready mood pieces', 'Detailed light, materials and camera moves for perfume, drink and fashion ads.'),
    ('speech-2', '1–15 seconds, several ratios', 'Set the length from 1 to 15 seconds and pick 16:9 landscape, 9:16 vertical or 1:1 square.'),
]
GALLERY = [('property', 'Real estate'), ('dining', 'Food & drink'), ('perfume', 'Perfume'), ('clothing', 'Fashion'), ('speech-1', 'Dialogue'), ('speech-2', 'Cinematic'),
           ('mockup-3d', 'Prototype'), ('mockup-earth', 'New setting')]
USES = [
    ('clothing', 'E-commerce', 'Product videos and try-on', 'Turn product shots into showcase clips or dress a model in a chosen outfit, at catalog scale.'),
    ('perfume', 'Advertising', 'Brand ad creative', 'Spin up several 6–10 second versions of one concept for ad testing.'),
    ('speech-1', 'Short video', 'Talking clips and skits', 'Characters speak with lip sync, good for talking-head clips, skits and social content.'),
    ('property', 'Real estate', 'Home walkthroughs', 'Generate a walkthrough from one interior photo to show off the layout and finish.'),
    ('mockup-3d', 'Design', 'Prototype and concept videos', 'Turn 3D models or design files into realistic footage for pitches and launches.'),
    ('restyle-a', 'Creative', 'Restyling and video edits', 'Use the first-generation model to restyle existing footage or recolor clothing while keeping the motion.'),
]
OFFERS = lambda s, name: [(f'{name}, {r} (per second)', u) for r, u, _ in TIERS[s]]


def base(slug):
    return dict(family=FAMILY, family_h2=FAMILY_H2, family_lead=FAMILY_LEAD, why_h2='Why call it through AnyAIGC', why=WHY,
                docs=DOCS_GEN, ent_lead=ENT_LEAD, in_other=f'{EN_NAME[slug]} API 中文版', category='Video generation API',
                in_img='Image to video adds {p} per input image', in_vid='Video edits add {p} per second of source video')


EN_NAME = {'grok-video': 'Grok Video', S15: 'Grok Imagine Video 1.5', SL: 'Grok Imagine Video 1.5 Lite', S10: 'Grok Imagine Video'}


def build(slug):
    c = base(slug)
    if slug == 'grok-video':
        c.update(
            title=f'Grok Video API Pricing | Grok Imagine from {PL}/sec - AnyAIGC',
            desc=f'Grok Video API (Grok Imagine Video 1.5, 1.5 Lite, Video): from {PL}/sec, native sound and dialogue, unlimited concurrency, bank transfer and VAT invoices.',
            keywords='Grok Imagine Video API,Grok Imagine Video API pricing,Grok video generation API,xAI video API,grok-imagine-video,Grok image to video API,Grok text to video API,Grok Video API for business,AnyAIGC',
            og_desc=f'Every Grok Imagine video model in one API: from {PL} / sec, native sound and dialogue, 1–15 seconds, unlimited concurrency.',
            og_alt_txt='AnyAIGC Grok Video API pricing and access', crumb='Grok Video',
            product='Grok Imagine Video API (AnyAIGC)', product_desc='Access xAI’s Grok Imagine video generation models through AnyAIGC, billed per second, via /v1/videos/generations.',
            sku=S15, offers=OFFERS(S15, 'Grok Imagine Video 1.5') + OFFERS(SL, 'Grok Imagine Video 1.5 Lite') + OFFERS(S10, 'Grok Imagine Video'),
            kicker='xAI · Grok Imagine video series', h1='Grok Video API',
            lead=f'xAI’s video models generate picture and sound together. One key covers the whole series, from <strong>{PL} / sec</strong>, every tier about 40% below xAI’s list price, with unlimited concurrency.',
            hero_vid='speech-2', hero_cap='xAI sample, with sound',
            facts=[('Models', '3'), ('Price', f'from {PL} / sec'), ('Length', '1–15 sec'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='Which Grok Video models are there?', about_lead='All three are live on AnyAIGC, billed per second. Change the <code>model</code> field to switch.',
            lineup=[
                (S15, 'Recommended', 'Grok Imagine Video 1.5', 'xAI’s new-generation video model, released in June 2026, with better visuals, motion and dialogue.', ['Text to video, image to video', 'Lip-synced dialogue', '480p / 720p']),
                (SL, 'Lowest price', 'Grok Imagine Video 1.5 Lite', 'A lighter, cheaper Video 1.5 for high-volume jobs and quick drafts.', ['Text to video, image to video', '480p / 720p / 1080p', 'Lowest per-second price in the series']),
                (S10, '', 'Grok Imagine Video', 'The first-generation video model, launched with the Imagine API in January 2026.', ['Text to video, image to video', 'Edits uploaded videos', '480p / 720p']),
            ],
            features_h2='What the Grok video models can do', features_lead='These clips were generated by Grok Imagine and come from xAI’s official pages. Click to play (with sound).', features=FEATURES,
            edits_h2='Video editing: new colors, new styles', edits_lead='The first-generation <code>grok-imagine-video</code> takes an uploaded video and changes clothing, colors or the whole look from one instruction, keeping the motion intact (xAI samples).',
            edit_rows=[('Swap the outfit', [('edit-input', 'Source'), ('edit-a', 'Result 1'), ('edit-b', 'Result 2')]),
                       ('Change the style', [('restyle-original', 'Source'), ('restyle-a', 'Result 1'), ('restyle-b', 'Result 2')])],
            edits_note='Edits go through <code>POST /v1/videos/edits</code>. Only <code>grok-imagine-video</code> supports them today; output is up to 720p and matches the source length.',
            gallery_h2='Official Grok Imagine sample videos', gallery_lead='These clips were generated by Grok Imagine and come from xAI’s Imagine API page and the Video 1.5 launch post.', gallery=GALLERY,
            pricing_h2='Grok video API pricing', pricing_lead=f'Billed per second of output video, tiered by resolution, from {PL} / sec.',
            billing=[('Per second', 'Billed on video length, not tokens'), ('Tiers', '480p / 720p / 1080p'), ('Image to video', f'{IMG10}–{IMG15} per input image'), ('Unlimited concurrency', 'On every account by default')],
            price_rows=[(S15, 'Grok Imagine Video 1.5 (recommended)'), (SL, 'Grok Imagine Video 1.5 Lite (lowest price)'), (S10, 'Grok Imagine Video (video editing)')],
            price_note=f'Prices from the AnyAIGC model catalog. xAI list prices: Video 1.5 $0.08 (480p) and $0.14 (720p) / sec; 1.5 Lite $0.02 (480p), $0.03 (720p) and $0.14 (1080p) / sec; Video $0.05 (480p) and $0.07 (720p) / sec{SRC}. {TAIL}',
            costs=[('100 six-second drafts', f'100 × 6 sec × {PL}', money('en', MODELS[SL]['usd'], 600), '1.5 Lite, 480p'),
                   ('100 ten-second ads', f'100 × 10 sec × {P15_720}', money('en', tier(S15, '720p'), 1000), 'Video 1.5, 720p'),
                   ('100 eight-second image-to-video clips', f'100 × (8 sec × {P10} + {IMG10})', money('en', MODELS[S10]['usd'], 800, 100 * float(INPUT_IMG[S10][0])), 'Video, 480p')],
            uses_h2='Grok video API use cases', uses=USES,
            qs_h2='Get started with the Grok video API', steps=STEPS(S15),
            tabs=[('py', 'Python', 'Python · text to video + polling', code_py(S15)),
                  ('curl', 'cURL', 'cURL · image to video', code_curl(SL)),
                  ('edit', 'Edit', 'cURL · edit an uploaded video', code_edit())],
            qs_note=QS_NOTE, ent_h2='Grok Video API for teams and enterprises',
            faq_h2='Grok Video API FAQ',
            faqs=[
                ('How much does the Grok video API cost?', f'On AnyAIGC you pay per second of output video: Video 1.5 is {P15} (480p) and {P15_720} (720p) / sec; 1.5 Lite is {PL} (480p), {PL_720} (720p) and {PL_1080} (1080p) / sec; Video is {P10} (480p) and {P10_720} (720p) / sec. Image to video adds a per-image input charge. A 6-second 1.5 Lite clip at 480p costs about {money("en", MODELS[SL]["usd"], 6)}. Live prices are on the model catalog.'),
                FAQ_DIFF,
                ('How long can a video be? Which resolutions and aspect ratios are supported?', '<code>duration</code> takes 1–15 seconds and you pay for the actual length. <code>resolution</code>: Video 1.5 and Video support 480p and 720p; 1.5 Lite supports 480p, 720p and 1080p. <code>aspect_ratio</code> supports 16:9, 9:16 and 1:1; for image to video the frame follows the input image.'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
                ('Can I use the videos commercially?', 'Usage rights and content policy follow xAI’s official terms. AnyAIGC only provides API access and adds no extra restrictions on what you do with the output.'),
            ],
            final_h2='Start calling the Grok video API', final_p=f'Sign up for 2M free tokens. From {PL} / sec, unlimited concurrency.',
        )
    elif slug == S15:
        c.update(
            title=f'Grok Imagine Video 1.5 API Pricing | from {P15}/sec - AnyAIGC',
            desc=f'Grok Imagine Video 1.5 API from {P15}/sec, below xAI list price: native sound, lip-synced dialogue, image to video, unlimited concurrency, VAT invoices.',
            keywords=f'Grok Imagine Video 1.5 API,{S15},grok-imagine-video-1.5,Grok Imagine Video API pricing,Grok video generation API,Grok image to video API,Grok Imagine Video 1.5 API for business,AnyAIGC',
            og_desc=f'Grok Imagine Video 1.5 API: from {P15} / sec, native sound and dialogue, text and image to video, unlimited concurrency.',
            og_alt_txt='AnyAIGC Grok Imagine Video 1.5 API pricing and access', crumb='Grok Imagine Video 1.5',
            product='Grok Imagine Video 1.5 API (AnyAIGC)', product_desc=f'Access xAI’s Grok Imagine Video 1.5 ({S15}) video generation model through AnyAIGC, billed per second.',
            sku=S15, offers=OFFERS(S15, 'Grok Imagine Video 1.5'),
            kicker='xAI · released June 2026', h1='Grok Imagine Video 1.5 API',
            lead=f'xAI’s new-generation video model improves visuals, motion and dialogue over the first generation, with sound and lip sync generated together. On AnyAIGC it starts at <strong>{P15} / sec</strong>, every tier about 40% below xAI’s list price, with unlimited concurrency.',
            hero_vid='speech-1', hero_cap='From xAI’s Video 1.5 launch post, with sound',
            facts=[('Model', f'<code>{S15}</code>'), ('Price', f'from {P15} / sec'), ('Resolution', '480p / 720p'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='What is Grok Imagine Video 1.5?',
            about_ps=[
                f'Grok Imagine Video 1.5 is the video model xAI launched as a preview on June 3, 2026 and released generally on June 16. In xAI’s docs <code>{S15}</code> is an alias of <code>grok-imagine-video-1.5</code>; they are the same model.',
                f'According to <a href="{XAI_15_POST}" target="_blank" rel="noopener">xAI’s launch post</a>, 1.5 improves sound, dialogue, motion and physics, and speaking characters stay lip-synced. It handles text to video and image to video, 1–15 seconds per clip.',
                f'On AnyAIGC it costs {P15} / sec at 480p and {P15_720} / sec at 720p, plus {IMG15} per input image for image to video. xAI lists it at $0.08 (480p) and $0.14 (720p) / sec.',
            ],
            spec=[('Model', f'<code>{S15}</code>'), ('Create', '/v1/videos/generations'), ('Get', '/v1/videos/{id}'),
                  ('Length', '1–15 sec'), ('Resolution', '480p / 720p'), ('Aspect ratio', '16:9 / 9:16 / 1:1')],
            features_h2='What Grok Imagine Video 1.5 can do', features_lead='These clips were generated by Grok Imagine and come from xAI’s official pages. Click to play (with sound).', features=FEATURES,
            gallery_h2='Official Grok Imagine sample videos', gallery_lead='These clips were generated by Grok Imagine and come from xAI’s Imagine API page and the Video 1.5 launch post.', gallery=GALLERY,
            pricing_h2='Grok Imagine Video 1.5 API pricing', pricing_lead=f'Billed per second of output video: {P15} / sec at 480p, {P15_720} / sec at 720p.',
            billing=[('Per second', 'Billed on video length, not tokens'), ('Tiers', '480p / 720p'), ('Image to video', f'{IMG15} per input image'), ('Unlimited concurrency', 'On every account by default')],
            price_rows=[(S15, 'Grok Imagine Video 1.5')],
            price_note=f'Prices from the AnyAIGC model catalog. xAI list prices: $0.08 / sec at 480p, $0.14 / sec at 720p, $0.01 per input image{SRC}. {TAIL}',
            costs=[('One 6-second clip', f'6 sec × {P15}', money('en', MODELS[S15]['usd'], 6), '480p'),
                   ('100 ten-second ads', f'100 × 10 sec × {P15_720}', money('en', tier(S15, '720p'), 1000), '720p'),
                   ('100 eight-second image-to-video clips', f'100 × (8 sec × {P15} + {IMG15})', money('en', MODELS[S15]['usd'], 800, 100 * float(INPUT_IMG[S15][0])), '480p, one first frame each')],
            uses_h2='Grok Imagine Video 1.5 use cases', uses=USES[:5] + [('dining', 'Food & drink', 'Dish and drink clips', 'Turn one food photo into a short clip with ambient sound for delivery apps and store promos.')],
            qs_h2='Get started with the Grok Imagine Video 1.5 API', steps=STEPS(S15),
            tabs=[('py', 'Python', f'Python · {S15} text to video', code_py(S15)),
                  ('curl', 'cURL', 'cURL · image to video', code_curl(S15))],
            qs_note=QS_NOTE_NO_EDIT,
            ent_h2='Grok Imagine Video 1.5 API for teams and enterprises',
            faq_h2='Grok Imagine Video 1.5 API FAQ',
            faqs=[
                ('How much does the Grok Imagine Video 1.5 API cost?', f'On AnyAIGC, Grok Imagine Video 1.5 (<code>{S15}</code>) is billed per second of output video: {P15} / sec at 480p and {P15_720} / sec at 720p, plus {IMG15} per input image for image to video. A 6-second 480p clip costs about {money("en", MODELS[S15]["usd"], 6)}. xAI lists it at $0.08 (480p) and $0.14 (720p) / sec. Live prices are on the model catalog.'),
                (f'Are {S15} and grok-imagine-video-1.5 the same model?', f'Yes. Per xAI’s docs, <code>{S15}</code> is an alias of <code>grok-imagine-video-1.5</code>. Version 1.5 launched as a preview on June 3, 2026 and went generally available on June 16. On AnyAIGC you call it as <code>{S15}</code>.'),
                ('Video 1.5 or 1.5 Lite: how do I choose?', f'Pick Video 1.5 (from {P15} / sec) when picture quality, complex motion and dialogue matter. Pick 1.5 Lite (from {PL} / sec) for volume, draft checks or simple scenes; it also goes up to 1080p.'),
                ('How long can a video be? Which resolutions and aspect ratios are supported?', '<code>duration</code> takes 1–15 seconds and you pay for the actual length; <code>resolution</code> supports 480p and 720p; <code>aspect_ratio</code> supports 16:9, 9:16 and 1:1, and for image to video the frame follows the input image.'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
            ],
            final_h2='Start calling Grok Imagine Video 1.5', final_p=f'Sign up for 2M free tokens. From {P15} / sec, unlimited concurrency.',
        )
    elif slug == SL:
        c.update(
            title=f'Grok Imagine Video 1.5 Lite API Price | {PL}/sec - AnyAIGC',
            desc=f'Grok Imagine Video 1.5 Lite API, the lowest-cost Grok video model: from {PL}/sec, 1080p, native sound, unlimited concurrency, VAT invoices.',
            keywords=f'Grok Imagine Video 1.5 Lite API,{SL},Grok Imagine Video API pricing,Grok video generation API,cheap video generation API,Grok text to video API,Grok Imagine Video 1.5 Lite API for business,AnyAIGC',
            og_desc=f'Grok Imagine Video 1.5 Lite API: from {PL} / sec, the lowest price in the series, 1080p and native sound, unlimited concurrency.',
            og_alt_txt='AnyAIGC Grok Imagine Video 1.5 Lite API pricing and access', crumb='Grok Imagine Video 1.5 Lite',
            product='Grok Imagine Video 1.5 Lite API (AnyAIGC)', product_desc=f'Access xAI’s Grok Imagine Video 1.5 Lite ({SL}) video generation model through AnyAIGC, billed per second.',
            sku=SL, offers=OFFERS(SL, 'Grok Imagine Video 1.5 Lite'),
            kicker='xAI · the lighter, cheaper Video 1.5', h1='Grok Imagine Video 1.5 Lite API',
            lead=f'The lightweight Video 1.5 generates picture and sound together and suits high-volume output and quick idea checks. On AnyAIGC it starts at <strong>{PL} / sec</strong>, the lowest price in the Grok video series, with unlimited concurrency.',
            hero_vid='property', hero_cap='xAI sample, with sound',
            facts=[('Model', f'<code>{SL}</code>'), ('Price', f'from {PL} / sec'), ('Resolution', '480p–1080p'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='What is Grok Imagine Video 1.5 Lite?',
            about_ps=[
                f'Grok Imagine Video 1.5 Lite (<code>{SL}</code>) is the lightweight, lower-cost version of xAI’s Video 1.5. xAI’s docs describe it as its lowest-cost text-to-video and image-to-video model and recommend it for simple videos.',
                'It also generates sound natively, delivering picture, sound effects and ambience in one pass. Clips run 1–15 seconds, resolution can be 480p, 720p or 1080p (1080p is upscaled from 720p), in landscape, vertical or square.',
                'It doesn’t support reference images or keyframes, and complex characters, multiple people, long continuous motion and character consistency are weaker than the full Video 1.5. For polished final cuts, use <a href="/en/models/grok-imagine-video-1.5-preview">Grok Imagine Video 1.5</a>.',
            ],
            spec=[('Model', f'<code>{SL}</code>'), ('Create', '/v1/videos/generations'), ('Get', '/v1/videos/{id}'),
                  ('Length', '1–15 sec'), ('Resolution', '480p / 720p / 1080p'), ('Modes', 'Text / image to video')],
            features_h2='What Grok Imagine Video 1.5 Lite is good for',
            features=[
                (None, 'Lowest price in the series', f'{PL} / sec at 480p and {PL_720} / sec at 720p; a 6-second 480p clip costs about {money("en", MODELS[SL]["usd"], 6)}.'),
                (None, 'Native sound', 'Picture, sound effects and ambience are generated together, no voiceover step.'),
                (None, 'Up to 1080p', 'Choose 480p, 720p or 1080p. 1080p is upscaled from 720p, useful when you need to deliver high resolution.'),
                (None, 'Text and image to video', 'Get a clip from one sentence, or upload a first frame and animate it.'),
                (None, '1–15 seconds, per second', 'You only pay for the seconds you generate, so short shots stay cheap.'),
                (None, 'Upgrade to 1.5 in one line', f'When you need complex motion, several characters or better dialogue, change <code>model</code> to <code>{S15}</code>.'),
            ],
            pricing_h2='Grok Imagine Video 1.5 Lite API pricing', pricing_lead=f'Billed per second of output video: {PL} (480p), {PL_720} (720p) and {PL_1080} (1080p) / sec.',
            billing=[('Per second', 'Billed on video length, not tokens'), ('Tiers', '480p / 720p / 1080p'), ('Image to video', f'{IMG15} per input image'), ('Unlimited concurrency', 'On every account by default')],
            price_rows=[(SL, 'Grok Imagine Video 1.5 Lite'), (S15, 'Compare: Grok Imagine Video 1.5')],
            price_note=f'Prices from the AnyAIGC model catalog. xAI list prices for 1.5 Lite: $0.02 (480p), $0.03 (720p) and $0.14 (1080p) / sec, $0.01 per input image{SRC}. {TAIL}',
            costs=[('1,000 six-second drafts', f'1,000 × 6 sec × {PL}', money('en', MODELS[SL]['usd'], 6000), '480p'),
                   ('100 ten-second clips', f'100 × 10 sec × {PL_720}', money('en', tier(SL, '720p'), 1000), '720p'),
                   ('10 ten-second 1080p finals', f'10 × 10 sec × {PL_1080}', money('en', tier(SL, '1080p'), 100), '1080p')],
            uses_h2='Grok Imagine Video 1.5 Lite use cases',
            uses=[(None, 'Volume', 'Short-video assets at scale', 'The lowest per-second price makes it practical to generate hundreds or thousands of clips and pick the keepers.'),
                  (None, 'Drafts', 'Storyboards and concept checks', 'Prove out shots and ideas on Lite, then switch to Video 1.5 for the final cut.'),
                  (None, 'E-commerce', 'Product motion and short clips', 'Add simple motion to product shots for listing pages and feeds.'),
                  (None, 'Social', 'Clips for posts', 'Give articles and posts a few seconds of motion and ambient sound.'),
                  (None, 'Apps', 'In-app video generation', 'Add text to video to your app with per-second costs that are easy to forecast.'),
                  (None, 'High res', '1080p delivery', 'When you need 1080p output, Lite is the only model in the series that offers it.')],
            qs_h2='Get started with the Grok Imagine Video 1.5 Lite API', steps=STEPS(SL),
            tabs=[('py', 'Python', f'Python · {SL} text to video', code_py(SL, '480p')),
                  ('curl', 'cURL', 'cURL · image to video', code_curl(SL))],
            qs_note=QS_NOTE_NO_EDIT,
            ent_h2='Grok Imagine Video 1.5 Lite API for teams and enterprises',
            faq_h2='Grok Imagine Video 1.5 Lite API FAQ',
            faqs=[
                ('How much does the Grok Imagine Video 1.5 Lite API cost?', f'On AnyAIGC, Grok Imagine Video 1.5 Lite (<code>{SL}</code>) is billed per second of output video: {PL} (480p), {PL_720} (720p) and {PL_1080} (1080p) / sec, plus {IMG15} per input image for image to video. A 6-second 480p clip costs about {money("en", MODELS[SL]["usd"], 6)}. xAI lists it at $0.02 (480p), $0.03 (720p) and $0.14 (1080p) / sec. Live prices are on the model catalog.'),
                ('How is 1.5 Lite different from Video 1.5?', f'Lite is the lighter, cheaper version and adds 1080p, but it has no reference images or keyframes, and complex characters, multiple people, long continuous motion and character consistency are weaker than the full model. Use Lite for bulk assets and drafts, and Video 1.5 (from {P15} / sec) for ads and final cuts.'),
                ('Is the 1080p output native?', 'Per xAI’s docs, 1.5 Lite’s 1080p is upscaled from 720p, not native 1080p. The 1080p per-second price is also well above 720p, so choose it only when you need it.'),
                ('How long can a video be? Which aspect ratios are supported?', '<code>duration</code> takes 1–15 seconds and you pay for the actual length; <code>aspect_ratio</code> supports 16:9, 9:16 and 1:1, and for image to video the frame follows the input image.'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
            ],
            final_h2='Start calling Grok Imagine Video 1.5 Lite', final_p=f'Sign up for 2M free tokens. From {PL} / sec, unlimited concurrency.',
        )
    elif slug == S10:
        c.update(
            title=f'Grok Imagine Video API Pricing | from {P10}/sec - AnyAIGC',
            desc=f'Grok Imagine Video API ({S10}) from {P10}/sec: text and image to video, video editing, native sound, unlimited concurrency, VAT invoices.',
            keywords=f'Grok Imagine Video API,{S10},Grok Imagine Video API pricing,Grok video generation API,Grok video editing API,Grok image to video API,Grok Imagine Video API for business,AnyAIGC',
            og_desc=f'Grok Imagine Video API: from {P10} / sec, text and image to video, video editing, native sound, unlimited concurrency.',
            og_alt_txt='AnyAIGC Grok Imagine Video API pricing and access', crumb='Grok Imagine Video',
            product='Grok Imagine Video API (AnyAIGC)', product_desc=f'Access xAI’s Grok Imagine Video ({S10}) video generation and editing model through AnyAIGC, billed per second.',
            sku=S10, offers=OFFERS(S10, 'Grok Imagine Video'),
            kicker='xAI · released January 2026 · video editing', h1='Grok Imagine Video API',
            lead=f'xAI’s first-generation video model generates picture and sound together, and can edit an uploaded video to change clothing or style. On AnyAIGC it starts at <strong>{P10} / sec</strong>, every tier about 40% below xAI’s list price, with unlimited concurrency.',
            hero_vid='restyle-a', hero_cap='xAI video editing sample',
            facts=[('Model', f'<code>{S10}</code>'), ('Price', f'from {P10} / sec'), ('Resolution', '480p / 720p'), ('Concurrency', 'Unlimited'), ('Business', 'Contracts · invoices')],
            about_h2='What is Grok Imagine Video?',
            about_ps=[
                f'Grok Imagine Video (<code>{S10}</code>) is the video model xAI launched with the Grok Imagine API on January 28, 2026. It supports text to video, image to video and video editing, and its videos come with sound.',
                f'xAI’s <a href="{XAI_API}" target="_blank" rel="noopener">launch post</a> says it ranked #1 on the Artificial Analysis text-to-video leaderboard (data as of 2026-01-28). xAI has since released Video 1.5 and 1.5 Lite; the first-generation model has not been retired, and xAI’s docs now position it for editing and extending videos.',
                f'On AnyAIGC it costs {P10} / sec at 480p and {P10_720} / sec at 720p; image to video adds {IMG10} per input image, and video edits add {VID10} per second of source video. xAI lists it at $0.05 (480p) and $0.07 (720p) / sec.',
            ],
            spec=[('Model', f'<code>{S10}</code>'), ('Create', '/v1/videos/generations'), ('Edit', '/v1/videos/edits'),
                  ('Length', '1–15 sec'), ('Resolution', '480p / 720p'), ('Aspect ratio', '16:9 / 9:16 / 1:1')],
            features_h2='What Grok Imagine Video can do', features_lead='These clips were generated by Grok Imagine and come from xAI’s official pages. Click to play (with sound).',
            features=[('edit-a', 'Edit an uploaded video', 'Change clothing or colors with one sentence while the motion and camera stay the same.'),
                      ('restyle-b', 'Restyle the whole clip', 'Turn live footage into animation, blocks and other looks, keeping the original movement.'),
                      ('property', 'Text to video and image to video', 'Generate a clip from one sentence, or upload a first frame and bring it to life.'),
                      FEATURES[0], FEATURES[2], FEATURES[5]],
            edits_h2='Video editing: new colors, new styles', edits_lead='Upload a video and change clothing, colors or the whole look with one instruction, keeping the motion intact (xAI samples).',
            edit_rows=[('Swap the outfit', [('edit-input', 'Source'), ('edit-a', 'Result 1'), ('edit-b', 'Result 2')]),
                       ('Change the style', [('restyle-original', 'Source'), ('restyle-a', 'Result 1'), ('restyle-b', 'Result 2')])],
            edits_note=f'Edits go through <code>POST /v1/videos/edits</code>. Per xAI’s docs the source video can be up to 8.7 seconds, and output is up to 720p with the same length as the source. You pay the output per-second price plus {VID10} per second of source video.',
            pricing_h2='Grok Imagine Video API pricing', pricing_lead=f'Billed per second of output video: {P10} / sec at 480p, {P10_720} / sec at 720p.',
            billing=[('Per second', 'Billed on video length, not tokens'), ('Tiers', '480p / 720p'), ('Image to video', f'{IMG10} per input image'), ('Video edits', f'{VID10} per second of source video')],
            price_rows=[(S10, 'Grok Imagine Video'), (S15, 'Compare: Grok Imagine Video 1.5')],
            price_note=f'Prices from the AnyAIGC model catalog. xAI list prices: $0.05 / sec at 480p, $0.07 / sec at 720p, $0.002 per input image, $0.01 per second of input video{SRC}. {TAIL}',
            costs=[('One 6-second clip', f'6 sec × {P10}', money('en', MODELS[S10]['usd'], 6), '480p'),
                   ('100 ten-second clips', f'100 × 10 sec × {P10_720}', money('en', tier(S10, '720p'), 1000), '720p'),
                   ('Edit one 6-second video', f'6 sec × ({P10} + {VID10})', money('en', MODELS[S10]['usd'], 6, 6 * float(INPUT_VID[S10][0])), '480p output')],
            uses_h2='Grok Imagine Video use cases', uses=[USES[5]] + USES[:5],
            qs_h2='Get started with the Grok Imagine Video API', steps=STEPS(S10),
            tabs=[('py', 'Python', f'Python · {S10} text to video', code_py(S10)),
                  ('curl', 'cURL', 'cURL · image to video', code_curl(S10)),
                  ('edit', 'Edit', 'cURL · edit an uploaded video', code_edit())],
            qs_note=QS_NOTE, ent_h2='Grok Imagine Video API for teams and enterprises',
            faq_h2='Grok Imagine Video API FAQ',
            faqs=[
                ('How much does the Grok Imagine Video API cost?', f'On AnyAIGC, Grok Imagine Video (<code>{S10}</code>) is billed per second of output video: {P10} / sec at 480p and {P10_720} / sec at 720p. Image to video adds {IMG10} per input image, and video edits add {VID10} per second of source video. A 6-second 480p clip costs about {money("en", MODELS[S10]["usd"], 6)}. xAI lists it at $0.05 (480p) and $0.07 (720p) / sec. Live prices are on the model catalog.'),
                FAQ_DIFF,
                ('How do I edit a video?', f'Send <code>model</code>, <code>prompt</code> and the source <code>video</code> (a URL) to <code>POST /v1/videos/edits</code>, describing what to change. Per xAI’s docs the source can be up to 8.7 seconds and output is up to 720p. Right now only <code>{S10}</code> in the series supports editing.'),
                ('Is grok-imagine-video being retired?', 'Not at the moment. What xAI retired on November 2, 2026 was the image model <code>grok-imagine-image-quality</code>; the video models are not affected. xAI’s docs position the first-generation video model for editing and extending videos.'),
                FAQ_ASYNC, FAQ_AUDIO, FAQ_CN, FAQ_CONC, FAQ_INVOICE, FAQ_CONTRACT,
            ],
            final_h2='Start calling Grok Imagine Video', final_p=f'Sign up for 2M free tokens. From {P10} / sec, unlimited concurrency.',
        )
    return c
