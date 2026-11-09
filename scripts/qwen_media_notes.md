# Qwen media guides — 2026-11-07

Scope: seven image models and eleven audio/video models (ten video models
and one real-time omni model). The earlier retrieval-model request remains
separate from this media batch.

## Evidence and rates

`qwen_media_drawers.json` records the text read after opening **each** of the
18 model drawers in the supplied AnyAIGC pricing pages. Do not calculate
page prices from the provider-wide multiplier or from the list-card price.

`qwen_media_data.py` preserves the cheapest drawer's complete rate schedule
and its displayed decimal precision. Group names appear only in the internal
evidence file, never in rendered pages.

The user requested Chinese image/video prices in RMB on 2026-11-07.
Calculate USD × 6.7 using exact Decimal arithmetic, then display CNY rounded
to two decimal places with ROUND_HALF_UP, per the user's follow-up request.
Cost estimates multiply the original USD rates before conversion and rounding;
never multiply a rounded displayed base rate. Savings use original USD rates.
Chinese tables, estimates, FAQ, metadata, JSON-LD, related cards, hub cards,
and share images use CNY consistently. Stored source rates remain USD.
Chinese Omni Realtime token prices and English prices retain USD. The page
explains that CNY is a reference conversion and settlement remains in USD.

- Qwen Image 3.0: $0.00159 is a **base billing unit**. Output ×18; each reference
  image ×2. Do not advertise $0.00159 as the final output-image price.
- Qwen Image 3.0 Pro: output 1K ×25, 2K ×50; reference images ×2 each.
  Area ≤2.25 million pixels is the 1K tier. Computed examples are explicitly
  estimates based on the displayed base rate.
- Wan 3.0: 480P $0.0439/s; 720P $0.0878/s; 1080P $0.1755/s.
- HappyHorse 1.1: 720P $0.1161/s; 1080P $0.1549/s.
- HappyHorse 1.0: 720P $0.1161/s; 1080P $0.2065/s.
- Wan 2.5 and 2.6: preserve the exact resolution/duration prices in the drawer;
  do not replace them with the list-card per-second rate.
- Omni Realtime: four token rates; speech output charges both audio and
  corresponding output text.
- The user permits omitting missing model documentation. Pages show verified
  endpoint paths but do not invent request bodies or polling response schemas.

Wan 3.0 official list rates are $0.05/$0.10/$0.20 per second at
https://modelstudio.console.alibabacloud.com/model-releases/wan3.0-video .
Its displayed 30%-off promotion ended September 24, 2026, so it is not the
comparison baseline. Savings use the actual displayed rates and list rates:
12.2%, 12.2%, 12.25%. A page displays the Savings column only if at least one
rate has a verified positive saving. Missing, zero, or negative savings do
not create the column. An em dash is used only for non-discounted rows on a
page that has other discounted rows; the explanatory note follows that rule.

## Visual references and assets

- https://qwen.ai/blog?id=qwen-image-3.0
- https://qwen.ai/blog?id=qwen-image-2.1 (style reference only, not an added model)
- https://modelstudio.console.alibabacloud.com/model-releases/wan3.0-video

Image pages use the official blog's white canvas, #1d1d1f text, #082dff accent,
large title and inline examples. Video pages use the Wan release's cinematic
dark hero, pale #f7f8fc body, cyan/violet accents, and pill buttons.

Locally hosted official assets (user authorized downloading official media):

- `assets/models/qwen-media/qwen-image-3-layout.webp` derived from
  https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image3/update2.png
- `assets/models/qwen-media/qwen-image-3-whale.webp` derived from
  https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image3/whale.jpg
- `assets/models/qwen-media/wan3-poster.webp` derived from
  https://g.alicdn.com/bailian-fe/hot-activity/0.0.38/animal-sparring-poster.jpg
- `assets/models/qwen-media/wan3-sparring.mp4` from
  https://cloud.video.taobao.com/vod/UGklRMIJjB0OlrhM7lboEFtt9X802PMOTp23mEFiE88.mp4

Image examples are shown on their corresponding model pages. Video guides
reuse the official Wan 3.0 clip as decorative background footage, with a
visible source link explicitly identifying Wan 3.0 on other models' pages;
it is not represented as their output or as an AnyAIGC test. The Qwen mark is the existing
pinned lobe-icons asset. No remote fonts, scripts, or runtime media are required.

All ten video-generation models use the locally hosted demo as an edge-to-edge
hero background with muted autoplay, inline playback, and looping. The user
extended the Wan 3.0 treatment to the remaining video pages on 2026-11-09.
All Qwen topic-page visible breadcrumbs are omitted at the user's request
(including conversation, image, video, and real-time guides, in both languages).
Structured BreadcrumbList metadata is retained. A pause/play button is available;
reduced-motion users see the poster until they explicitly start playback.
Image and real-time Omni heroes retain their existing layout.

## Rebuild

1. `python scripts/qwen_media_pages.py`
2. `python scripts/qwen_media_register.py`
3. `python scripts/og_qwen_media.py`, then capture the generated temporary HTML
   at 1200×630 with Playwright (see the generated capture manifest).
4. `python scripts/check_topics.py`

The generator is safe to import; importing it must not write pages. Text, image,
and video guides share `assets/models/qwen.js` and the `q-*` motion rules in
`qwen.css`: staggered character blur/translation for headings, blur for copy,
and entrance transitions for small cards. Each heading is observed directly;
long sections and pricing tables are never hidden. Reduced motion, missing
IntersectionObserver, and initialization failure leave content readable.
