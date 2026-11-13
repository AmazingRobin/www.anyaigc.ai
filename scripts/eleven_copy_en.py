# ElevenLabs (Eleven) series topic pages, English copy. Used by scripts/eleven_pages.py. Mirrors eleven_copy_zh.py (same names, same build() shape).
# Prices come from eleven_data.PRICE (model catalog detail drawer, read 2026-11-13); list prices from elevenlabs.io/pricing/api;
# specs from elevenlabs.io/docs/overview/models. Anything the AnyAIGC API docs do not state (response format, custom cloned voices, tag behavior,
# streaming) is not asserted: the copy says to test or ask support.
# Do not claim "works from mainland China" on English pages.
from decimal import Decimal

from eleven_data import PRICE, OFFICIAL, OFFICIAL_1K, MODELS, SLUGS, REG, MARKET, SUPPORT, DOCS_SPEECH, OFFICIAL_MODELS, OFFICIAL_PRICING
from eleven_layout import cost, money, unit_price
import eleven_code as code

DEAL = '19% off list price'


def p(slug):
    return f'${PRICE[slug]}'


def off(slug):
    return f'${OFFICIAL[slug]}'


def link(slug):
    return f'<a href="/en/models/{slug}">{MODELS[slug]["name"]}</a>'


# ---------------- per-model content ----------------
M = {
    'eleven-v4': dict(
        sell='Flagship TTS', lead='ElevenLabs flagship text-to-speech model with fine-grained emotion, built for audiobooks, voiceover and polished final audio',
        tag='ElevenLabs flagship text-to-speech model: fine-grained emotion, inline direction tags, 90+ languages.',
        sample_line='ElevenLabs official v4 demo (an Australian radio host, with laughs and pauses), 24 seconds, not generated live on this page.',
        about=['Eleven v4 is the flagship text-to-speech model from ElevenLabs. ElevenLabs describes it as a new architecture that reads a script the way a voice actor does: it knows who is speaking, what just happened, and how each line should land. The model catalog describes it as the top-tier model with the finest emotional range, the first choice for professional audiobook narration.',
               'The official docs list 90+ languages (including Mandarin and Cantonese) and a 10,000-character limit per generation. ElevenLabs says you can put inline directions such as [laughs], [whispers] and [door slams] straight into the script to steer tone and sound effects.',
               'On AnyAIGC, <code>eleven_v4</code> runs on <code>POST /v1/audio/speech</code> with a single Bearer key, so you do not need a separate ElevenLabs account. It is billed by the number of input characters, with no concurrency limit.'],
        feats=[('Emotion and context', 'ElevenLabs says v4 reads lines in context and handles different speakers and moods in one script, which suits content that needs a performance.'),
               ('Inline directions', 'ElevenLabs says you can add directions such as [laughs], [whispers] and [door slams] right in the script, and that v4 follows tag sequences more reliably than v3.'),
               ('90+ languages', 'The official docs list 90+ languages, including Mandarin (zh) and Cantonese (yue), so multilingual content can use one model.'),
               ('Stable across retakes', 'ElevenLabs says the speaker stays the same when you regenerate a line, which makes auditioning and redoing takes easier.')],
        uses=[('voice-narration.webp', '01 · Audiobooks', 'Audiobooks and long narration', 'Chapter narration, fiction reading and course lectures. The official docs list audiobooks and long-form emotional narration as a typical v4 use.'),
              ('voice-character.webp', '02 · Characters', 'Game and animation voices', 'The official docs say the emotional range of v4 suits games and animation. Write different directions for different characters.'),
              ('voice-entertainment.webp', '03 · Film and video', 'Short drama, trailers and story narration', 'Dramatic lines with ups and downs. Use tags to mark pauses, sighs and shifts in tone.'),
              ('voice-multilingual.webp', '04 · Multilingual', 'Localized content', 'Translate one script into several languages and generate each one with a similar voice quality, for video, courses and product intros.')],
        text='[warm] Welcome back. [long pause] Here is the tech briefing for today.'),
    'eleven-v4-turbo': dict(
        sell='Low-latency TTS', lead='The low-latency version of Eleven v4, keeping v4 expressiveness for voice assistants, support agents and interactive characters',
        tag='The low-latency version of Eleven v4: ElevenLabs states a median inference latency of about 100ms, aimed at voice assistants and interactive characters.',
        sample_line=None,
        about=['Eleven v4 Turbo is the low-latency version of Eleven v4. ElevenLabs says it keeps the expressiveness of v4 with a median inference latency of about 100ms, aimed at voice agents, support agents and interactive characters. The model catalog describes it as the real-time streaming version of V4: low latency with emotion and fast response.',
               'Two things to keep in mind. First, the official 100ms is median inference latency and excludes network and application latency, so time to first audio over an HTTP gateway will be longer. Second, the official WebSocket streaming interface is not part of what AnyAIGC currently offers: the model catalog lists a single endpoint for this model, <code>POST /v1/audio/speech</code>.',
               'On AnyAIGC, <code>eleven_v4_turbo</code> is billed by the number of input characters at half the price of Eleven v4, with no concurrency limit.'],
        feats=[('Low latency', 'ElevenLabs states a median inference latency of about 100ms (excluding network and application latency), a fit for latency-sensitive voice interaction.'),
               ('v4 expressiveness', 'ElevenLabs says Turbo carries the full expressiveness of v4 and supports the same inline directions.'),
               ('90+ languages', 'Same as Eleven v4: the official docs list 90+ languages, including Mandarin and Cantonese.'),
               ('Half the price of v4', f'{p("eleven-v4-turbo")} per 10K characters, against {p("eleven-v4")} for Eleven v4. The gap adds up on high-volume conversational content.')],
        uses=[('voice-conversational.webp', '01 · Assistants', 'Voice assistants and support agents', 'Turn replies from a language model into speech. The official docs list support agents and AI assistants as typical v4 Turbo uses.'),
              ('voice-character.webp', '02 · Interactive', 'Interactive characters and game NPCs', 'Character lines that must play right away are sensitive to latency. Send requests sentence by sentence.'),
              ('voice-social.webp', '03 · Short video', 'Short video and live voiceover', 'Batch generation of many short lines at half the cost of v4.'),
              ('voice-ads.webp', '04 · Announcements', 'Notifications and ad reads', 'Short announcements for stores, campaigns and outbound calls, with a natural tone and fast generation.')],
        text='[warm] Hello, this is customer support. How can I help you today?'),
    'eleven-v3': dict(
        sell='Dramatic voiceover', lead='The previous-generation ElevenLabs flagship, strong dramatic delivery for stories, short drama and character voices',
        tag='Strong dramatic delivery for stories and short drama, 70+ languages.',
        sample_line=None,
        about=['Eleven v3 is the previous-generation flagship text-to-speech model from ElevenLabs. ElevenLabs describes it as producing natural, life-like speech with a high emotional range and contextual understanding. The model catalog describes it as strongly dramatic, a fit for stories and short-drama dubbing, with a lot of atmosphere.',
               'The official docs list 70+ languages and a 5,000-character limit per generation. The docs now call v3 the previous generation, with Eleven v4 as the latest flagship. The two are priced the same on AnyAIGC, so for a new project it is worth auditioning the same text on both.',
               'On AnyAIGC, <code>eleven_v3</code> runs on <code>POST /v1/audio/speech</code>, billed by the number of input characters, with no concurrency limit.'],
        feats=[('Dramatic delivery', 'ElevenLabs describes v3 by its dramatic performance and wide emotional range, suited to content that needs acting.'),
               ('70+ languages', 'The official docs list 70+ languages, including Mandarin and Cantonese.'),
               ('Stories and short drama', 'The model catalog positions it for story and short-drama dubbing, with strong atmosphere for plots that rise and fall.'),
               ('Same price as v4', f'{p("eleven-v3")} per 10K characters, the same as Eleven v4, so you can audition one text on both before deciding.')],
        uses=[('voice-entertainment.webp', '01 · Short drama', 'Short drama and story dubbing', 'Dramatic lines, narration and plot twists. Pick v3 when the text needs emotional ups and downs.'),
              ('voice-character.webp', '02 · Characters', 'Story characters and game narration', 'Give each character a different voice, generate in segments and combine them in your editor.'),
              ('voice-narration.webp', '03 · Audiobooks', 'Story narration', 'Children stories, suspense fiction and other narration that needs atmosphere.'),
              ('voice-social.webp', '04 · Short video', 'Drama-style short video', 'Voiceover with emotion for short video scripts, within the official 5,000-character limit per request.')],
        text='When he pushed open the door, the room was empty. Only the rain outside kept falling.',
        notice=True),
    'eleven-v3-conversational': dict(
        sell='Conversational TTS', lead='The low-latency conversational version of v3, with a relaxed spoken tone for chat and voice characters',
        tag='The conversational version of v3: a relaxed, natural spoken tone, with a stated latency of about 165ms.',
        sample_line=None,
        about=['Eleven v3 Conversational is the version of v3 tuned for real-time conversation. ElevenLabs says it keeps the dramatic delivery of v3 with lower latency and supports custom audio tags. The model catalog describes it as built for conversation, relaxed and natural, a fit for casual chat.',
               'The official docs state a latency of about 165ms for v3 Conversational (median inference latency, excluding network and application latency) and 70+ languages. The official real-time streaming interface is outside what AnyAIGC currently offers: the model catalog lists only <code>POST /v1/audio/speech</code> for it.',
               'On AnyAIGC, <code>eleven_v3_conversational</code> is billed by the number of input characters at half the price of Eleven v3, with no concurrency limit.'],
        feats=[('Spoken tone', 'A relaxed, natural delivery, a fit for chat, companion and role-play content.'),
               ('Lower latency', 'The official docs state about 165ms median inference latency, excluding network and application latency.'),
               ('Custom audio tags', 'ElevenLabs says custom audio tags are supported, so you can mark changes in tone inside the text.'),
               ('Half the price of v3', f'{p("eleven-v3-conversational")} per 10K characters, against {p("eleven-v3")} for Eleven v3.')],
        uses=[('voice-conversational.webp', '01 · Chat', 'Chatbots and companion apps', 'Turn replies from a chat model into speech with a spoken tone, for chat and companion products.'),
              ('voice-character.webp', '02 · Characters', 'Virtual characters and NPC dialogue', 'Character lines sound closer to a real person talking than to a broadcaster.'),
              ('voice-social.webp', '03 · Short video', 'Casual voiceover', 'Spoken voiceover for lifestyle, review and product recommendation videos.'),
              ('voice-education.webp', '04 · Teaching', 'Speaking practice and explainers', 'Language practice, Q&A and explanations that need a natural tone.')],
        text='Oh, you are here early today. Did you not sleep well again?'),
    'eleven-multilingual-v2': dict(
        sell='Long-form TTS', lead='Stable on long scripts, with bilingual text that keeps its voice, for narration and courses',
        tag='Stable on long scripts: ElevenLabs says it is the most stable model on long-form generations. 29 languages.',
        sample_line=None,
        about=['Eleven Multilingual v2 is the ElevenLabs text-to-speech model for long-form content. ElevenLabs describes it as natural-sounding with consistent quality, and the most stable on long generations. The model catalog describes it as stable on long scripts, with mixed-language reading that keeps the voice intact.',
               'The official docs list 29 languages (including Mandarin) and a 10,000-character limit per generation. The docs also note that Multilingual v2 normalizes numbers better than Flash v2.5, so it is the better pick for phone numbers, dates and amounts.',
               'On AnyAIGC, <code>eleven_multilingual_v2</code> runs on <code>POST /v1/audio/speech</code>, billed by the number of input characters, with no concurrency limit.'],
        feats=[('Steadier on long text', 'ElevenLabs says it is the most stable model on long-form generations, a fit for full narration, course lectures and article reading.'),
               ('Mixed-language text', 'In text that mixes Chinese and English, the voice is less likely to drift at the language switch, which helps tech and education content.'),
               ('Better with numbers', 'The official docs say Multilingual v2 normalizes numbers better, so it is the one to pick for phone numbers, dates and amounts.'),
               ('29 languages', 'The official docs list 29 languages, including Mandarin, covering the common export languages.')],
        uses=[('voice-narration.webp', '01 · Narration', 'Long narration and article reading', 'Full-length reading of articles, news copy and reports.'),
              ('voice-education.webp', '02 · Education', 'Course lectures and training', 'Lectures that mix Chinese and English, with stable pronunciation of terms.'),
              ('voice-multilingual.webp', '03 · Multilingual', 'Multilingual video dubbing', 'Translate one script into several languages and generate each one.'),
              ('voice-ads.webp', '04 · Announcements', 'Explainers and announcements', 'Product explainers and event announcements that contain numbers and dates.')],
        text='This course has three parts. Part one covers the basic concepts of the API.'),
    'eleven-flash-v2-5': dict(
        sell='Very long text, in batch', lead='A fast, light model with a high per-request text limit, built for very long text and large batches of subtitles',
        tag='Fast and light: a 40,000-character limit per request and 32 languages, suited to batch generation.',
        sample_line=None,
        about=['Eleven Flash v2.5 is the fast, affordable text-to-speech model from ElevenLabs. ElevenLabs lists low latency (about 100ms), 32 languages and a 40,000-character limit per generation. The model catalog describes it as made for very long text, at the lowest price, suited to generating subtitles in large batches.',
               'The official docs carry a warning: Flash v2.5 does not normalize text by default, so phone numbers, dates and amounts may be read unclearly. Write those out the way you want them read, or pick Multilingual v2 instead.',
               'On AnyAIGC, <code>eleven_flash_v2_5</code> runs on <code>POST /v1/audio/speech</code>, billed by the number of input characters at half the price of Eleven v4, with no concurrency limit.'],
        feats=[('Very long text', 'The official limit is 40,000 characters per request, the highest among the ElevenLabs text-to-speech models, so long scripts need fewer splits.'),
               ('Fast', 'ElevenLabs states about 100ms median inference latency (excluding network and application latency), a fit for batch jobs.'),
               ('32 languages', 'The official docs list 32 languages, including Mandarin.'),
               ('Numbers need your help', 'The official docs say text is not normalized by default, so rewrite numbers, dates and amounts the way you want them read.')],
        uses=[('voice-education.webp', '01 · Subtitles', 'Batch subtitles and course dubbing', 'Convert large numbers of subtitle lines and course scripts to speech.'),
              ('voice-narration.webp', '02 · Reading', 'Long articles and news reading', 'Full reading of news, notices and documents.'),
              ('voice-ads.webp', '03 · Announcements', 'Notices and announcements', 'Batch notifications, store broadcasts and phone voice prompts.'),
              ('voice-social.webp', '04 · Short video', 'High-volume voiceover assets', 'Batch voiceover for e-commerce and news short videos.')],
        text='Attention passengers, the next stop is Central Station.'),
    'eleven-flash-v2': dict(
        sell='Light, fast announcements', lead='A light, fast English text-to-speech model for short lines and prompts',
        tag='Light and fast: the official docs list English only, with a stated latency of about 135ms.',
        sample_line=None,
        about=['Eleven Flash v2 is the light, fast text-to-speech model from ElevenLabs. In the official model table it lists English (en) only, with a stated latency of about 135ms and a 30,000-character limit per generation. The model catalog describes it as a light, fast announcement model with good value, suited to reading short lines.',
               'Keep in mind that the official docs list English only, so for Chinese or other languages pick Eleven Flash v2.5, Multilingual v2 or v4.',
               'On AnyAIGC, <code>eleven_flash_v2</code> runs on <code>POST /v1/audio/speech</code>, billed by the number of input characters at half the price of Eleven v4, with no concurrency limit.'],
        feats=[('Light and fast', 'ElevenLabs states about 135ms median inference latency (excluding network and application latency).'),
               ('English reading', 'The official docs list English only, a fit for English prompts, short lines and English teaching material.'),
               ('30,000 characters per request', 'The official limit is 30,000 characters per request, so long English text can go in one call.'),
               ('Low cost', f'{p("eleven-flash-v2")} per 10K characters, about half of Eleven v4.')],
        uses=[('voice-education.webp', '01 · Teaching', 'English teaching material', 'Audio for words, example sentences and short passages.'),
              ('voice-ads.webp', '02 · Announcements', 'English prompts and announcements', 'In-product English voice prompts and store announcements.'),
              ('voice-social.webp', '03 · Short video', 'English voiceover', 'Batch generation of English short-video voiceover.'),
              ('voice-narration.webp', '04 · Reading', 'English article reading', 'Full reading of English news and blog posts.')],
        text='Welcome back. Your order has been shipped.'),
}

QS_NOTE = f'Full parameters are in the <a href="{DOCS_SPEECH}" target="_blank" rel="noopener">Create speech API reference</a>. Swap the model name in the example for the Eleven model ID you want.'
PRICE_HEAD = [('Billing unit', ''), ('Model', ''), ('ElevenLabs list price (USD)', 'o-num'), ('AnyAIGC price (USD)', 'o-num o-hl')]
COMPARE_HEAD = [('Model', ''), ('Focus', 'el-txt'), ('Languages (official)', 'el-txt'), ('Per-request limit (official)', 'el-txt'), ('Latency (official)', 'el-txt'), ('AnyAIGC per 10K chars', 'o-num o-hl')]
POS = {'eleven-v4': 'Flagship, audiobooks and pro voiceover', 'eleven-v4-turbo': 'Low latency, voice assistants', 'eleven-v3': 'Dramatic, stories and short drama',
       'eleven-v3-conversational': 'Conversational, natural tone', 'eleven-multilingual-v2': 'Stable on long text, mixed languages',
       'eleven-flash-v2-5': 'Very long text, batch subtitles', 'eleven-flash-v2': 'Light and fast, short English lines'}


def langs_text(slug):
    l = MODELS[slug]['langs']
    return 'English only' if l == 'en' else f'{l} languages'


def limit_text(slug):
    l = MODELS[slug]['limit']
    return f'{l} chars' if l else 'Not listed'


def latency_text(slug):
    return MODELS[slug]['latency'] or 'Not stated'


def compare_rows():
    return [(f'<a href="/en/models/{s}">{MODELS[s]["name"]}</a>', '', [POS[s], langs_text(s), limit_text(s), latency_text(s), p(s)], s) for s in SLUGS]


COMPARE_NOTE = ('Language counts, character limits and latency come from the <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs model docs</a>. Latency is the median inference latency ElevenLabs states, excluding network and application latency. '
                'Prices are current AnyAIGC prices; live prices are in the model catalog. "Not listed" and "Not stated" mean the official docs do not give that item.')

FAMILY = [(s, '', f'{POS[s]} · {p(s)} / 10K chars') for s in SLUGS]
FAMILY[0] = (FAMILY[0][0], 'Flagship', FAMILY[0][2])
FAMILY[1] = (FAMILY[1][0], 'Low latency', FAMILY[1][2])


def costs(slug):
    c = lambda n: money(cost(slug, n))
    o = lambda n: f'ElevenLabs list price for the same usage {money(cost(slug, n, True))}'
    return [('One short-video voiceover', 'About 300 characters', c(300), o(300)),
            ('One audiobook chapter', 'About 8,000 characters', c(8000), o(8000)),
            ('Batch of 1M characters', 'About 1 million characters, unit price x 100', c(1000000), o(1000000))]


def offers(slug):
    return [('Per 10K characters', PRICE[slug])]


def billing(slug):
    return [('Per character', 'Billed on input text length'), ('About 19% off', f'List {off(slug)} per 10K chars'), ('Unlimited concurrency', 'Default for every account'), ('USD', 'One balance for 300+ models')]


def pricing_labels():
    # (label, small, multiplier relative to "per 10K characters", highlighted row)
    return [('Per 10K characters', 'Model catalog billing unit', 1, True), ('Per 1K characters', 'Matches the ElevenLabs pricing page', Decimal('0.1'), False), ('Per 1M characters', 'Bulk reference', 100, False)]


def pricing_note(slug):
    extra = ' The list price is taken from the Flash / Turbo row of the pricing page.' if slug in ('eleven-flash-v2-5', 'eleven-flash-v2') else ''
    return (f'Prices are in USD, billed on the number of input characters. The table shows the lowest catalog price; live prices are in the <a href="{MARKET}">AnyAIGC model catalog</a>. '
            f'The list price comes from the Text to Speech API table on the <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">ElevenLabs pricing page</a> at ${OFFICIAL_1K[slug]} per 1K characters. '
            f'AnyAIGC charges 81% of that list price, about 19% off.{extra}')


def qs_steps(model):
    return ['<strong>Sign up and top up</strong>: create an account at <a href="' + REG + '">anyaigc.ai</a>. Top-ups start at $1, and the balance works across every model on the platform.',
            '<strong>Create an API key</strong>: create a token in the console, copy the key that starts with <code>sk-</code>, and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Send a request</strong>: call <code>POST https://anyaigc.ai/v1/audio/speech</code> with <code>model</code> set to <code>{model}</code> and <code>voice</code> set to an ElevenLabs voice_id, authenticate with <code>Authorization: Bearer</code>, and save the returned audio as mp3.']


# ---------------- FAQ ----------------
def faq_common(name, slug):
    return [
        ('Can AnyAIGC issue invoices, including VAT special invoices?',
         'Yes. AnyAIGC can issue invoices for every top-up, including Chinese VAT general invoices and VAT special invoices. Send your invoicing details to support.'),
        ('Can my company pay by bank transfer and sign a contract?',
         f'Yes. You can top up by corporate bank transfer and sign a service agreement, with a dedicated support contact and technical contact. For company purchases, <a href="{SUPPORT}">contact AnyAIGC support</a>.'),
        ('Are my text and the generated audio used for training?',
         'No. Unless the law requires it, AnyAIGC does not persistently store your inputs or outputs and does not use them for training. Requests are encrypted with HTTPS. See the AnyAIGC <a href="/privacy">Privacy Policy</a>. The data policy of the model itself is set by ElevenLabs.'),
    ]


def faq_rpm(slug):
    return ('Is there a rate limit?',
            f'AnyAIGC sets no concurrency limit on <code>{MODELS[slug]["id"]}</code>, and every account gets this by default, so batch generation and parallel tasks are fine. Billing is per character, with no monthly fee and no quota that resets on a time window.')


def special_faq(slug):
    if slug == 'eleven-v4':
        return ('Can I put tags like [laughs] and [whispers] in the text?',
                'ElevenLabs says Eleven v4 supports inline directions such as [laughs], [whispers] and [door slams] in the script, and that v4 follows tag sequences more reliably than v3. The AnyAIGC API reference does not document a separate tag parameter, so audition a short piece of text first to confirm how a tag behaves.')
    if slug == 'eleven-v4-turbo':
        return ('How low is the latency of Eleven v4 Turbo?',
                'ElevenLabs states a median inference latency of about 100ms, and that number excludes network and application latency. AnyAIGC currently offers the HTTP <code>/v1/audio/speech</code> endpoint, not the official WebSocket streaming interface, so real wait time depends on text length and the network. For real-time conversation, measure it yourself and send requests sentence by sentence.')
    if slug == 'eleven-v3':
        return ('Has Eleven v3 been retired?',
                'No. The official docs call v3 the previous generation and Eleven v4 the latest flagship, and v3 is not in the official list of deprecated models (that list names eleven_turbo_v2_5, eleven_turbo_v2 and others). For a new project, audition the same text on ' + link('eleven-v4') + ' too; the two cost the same on AnyAIGC. Whether a model stays available is shown in the model catalog.')
    if slug == 'eleven-v3-conversational':
        return ('What is the difference between Eleven v3 Conversational and Eleven v3?',
                'The conversational version is built for dialogue, sounds more spoken, has a stated latency of about 165ms and costs half as much as Eleven v3. Eleven v3 is more dramatic, a fit for stories and short drama. Audition the same text on both. See ' + link('eleven-v3') + '.')
    if slug == 'eleven-multilingual-v2':
        return ('Which model should I use for phone numbers, dates and amounts?',
                'The official docs say Multilingual v2 normalizes numbers better than Flash v2.5, so pick Multilingual v2 for phone numbers, dates and similar content. You can also rewrite the numbers the way you want them read before generating.')
    if slug == 'eleven-flash-v2-5':
        return ('Flash v2.5 reads numbers and dates unclearly. What can I do?',
                'The official docs say Flash v2.5 does not normalize text by default, so phone numbers, dates and amounts may be read unclearly (Enterprise customers can turn normalization on). Rewrite numbers the way you want them read, or use ' + link('eleven-multilingual-v2') + ' instead.')
    return ('Does Eleven Flash v2 support Chinese?',
            'In the official model table Flash v2 lists English (en) only, so do not pick it for Chinese or other languages. Use ' + link('eleven-flash-v2-5') + ', ' + link('eleven-multilingual-v2') + ' or ' + link('eleven-v4') + ' instead.')


def build(slug):
    m = M[slug]
    d = MODELS[slug]
    mid, name = d['id'], d['name']
    s = slug
    price, offp = p(s), off(s)
    text = m['text']
    has_sample = m['sample_line'] is not None

    faqs = [
        (f'How much does the {name} API cost?',
         f'On AnyAIGC, <code>{mid}</code> is billed per character at {price} per 10K characters, about 19% off the ElevenLabs list price of {offp} per 10K characters. The price is fixed, with no subscription or monthly fee. Live prices are in the model catalog.'),
        (f'What is the {name} model ID, and how does it relate to ElevenLabs?',
         f'The model ID is <code>{mid}</code> (case-sensitive), the same as the ElevenLabs model_id. AnyAIGC is an independent API provider that offers an OpenAI-style <code>/v1/audio/speech</code> call, and is not affiliated with ElevenLabs.'),
        (f'How do I choose between {name} and the other Eleven models?',
         f'The platform has 7 Eleven voice models: {link("eleven-v4")} (flagship), {link("eleven-v4-turbo")} (low latency), {link("eleven-v3")}, {link("eleven-v3-conversational")}, {link("eleven-multilingual-v2")}, {link("eleven-flash-v2-5")} and {link("eleven-flash-v2")}. '
         'Pick v4 for polished final audio, v4 Turbo for voice assistants, Multilingual v2 for long text and mixed languages, and Flash v2.5 for large subtitle batches. Audition the same text before you commit.'),
        (f'How do I call the {name} API, and what goes in voice?',
         f'Call <code>POST https://anyaigc.ai/v1/audio/speech</code> with the required <code>model</code>, <code>input</code> and <code>voice</code> fields. <code>voice</code> takes an ElevenLabs voice_id, and an unknown or unavailable voice_id returns 400. <code>response_format</code> supports mp3, opus, aac and flac. See the <a href="{DOCS_SPEECH}" target="_blank" rel="noopener">API reference</a>.'),
        (f'How long can the text be for one {name} request?',
         ('The ElevenLabs docs state a limit of ' + d['limit'] + ' characters per generation for this model. ' if d['limit'] else 'The ElevenLabs docs do not state a per-request character limit for this model. ')
         + 'The AnyAIGC Create speech reference lists the maximum length of <code>input</code> as 4,096 characters, so split longer text by that length and join the audio afterwards.'),
        (f'Does {name} support Chinese, and how many languages?',
         ('In the official model table it lists English only, so use another model for Chinese. ' if d['langs'] == 'en'
          else f'Yes. The official docs list {d["langs"]} languages for this model, and Mandarin (zh) is among them. ')
         + 'For the exact languages see the <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs model docs</a>.'),
        special_faq(s),
        faq_rpm(s),
        ('Can I use my own cloned voice?',
         'The API reference only says that <code>voice</code> takes an ElevenLabs voice_id. It does not say whether a cloned voice from your own ElevenLabs account can be used with an AnyAIGC key. Please <a href="' + SUPPORT + '">ask AnyAIGC support</a> to confirm.'),
    ]
    faqs += faq_common(name, s)
    key_q = (f'How do I get a {name} API key?',
             f'Sign up and top up at <a href="{REG}">anyaigc.ai</a>, then create a token in the console. One key works for 300+ models on the platform, and you do not need a separate ElevenLabs account. Set <code>model</code> to <code>{mid}</code> in the request body.')
    faqs.insert(3, key_q)

    sell = m['sell']
    hero_notice = None
    if m.get('notice'):
        hero_notice = f'ElevenLabs docs call Eleven v3 the previous generation, with <a href="/en/models/eleven-v4">Eleven v4</a> as the latest flagship (same price on AnyAIGC). v3 is still callable in the model catalog today; whether it stays available is shown in the <a href="{MARKET}">model catalog</a>.'

    sample = None
    if has_sample:
        sample = dict(play='Play the sample audio', pause='Pause the sample audio', title='ElevenLabs official v4 demo', line=m['sample_line'])

    langs_fact = 'English only' if d['langs'] == 'en' else f'{d["langs"]} languages'
    facts = [('Model ID', mid), ('Price', f'{price} / 10K chars'), ('Languages', langs_fact), ('Concurrency', 'Unlimited'), ('Teams', 'Invoices · contracts')]

    return dict(
        title=f'{name} API Price and Access, 19% Off - AnyAIGC',
        desc=f'{mid} text-to-speech API: {price} per 10K chars, about 19% off list. Unlimited concurrency, bank transfer and VAT special invoices.',
        og_desc=f'{mid} at {price} per 10K characters, about 19% off ElevenLabs list price. {m["lead"]}. Unlimited concurrency, bank transfer and VAT special invoices.',
        og_alt=f'AnyAIGC {mid} API: {price} per 10K characters, about 19% off list price',
        keywords=f'{mid} API,{mid},{name} API price,{name} API access,{name} API key,ElevenLabs API,ElevenLabs API pricing,ElevenLabs gateway,text to speech API,AI voiceover API,{name} API for teams,{name} API VAT special invoice,ElevenLabs API bank transfer,AnyAIGC',
        crumb=f'{name} API', product=f'{name} API (AnyAIGC)', sku=s,
        product_desc=f'Call ElevenLabs {name} through AnyAIGC: POST /v1/audio/speech, billed per character at {price} per 10K characters (about 19% off list price), unlimited concurrency.',
        offers=offers(s),
        hero=dict(eyebrow=f'ElevenLabs · {mid}', deal=DEAL,
                  h1=f'Eleven <b>{d["short"]}</b><span class="o-sr"> API</span>',
                  lead=f'{m["tag"]} One API key, billed per character, about 19% off the ElevenLabs list price.',
                  sample=sample,
                  sub=f'<code>{mid}</code> {price} per 10K characters (ElevenLabs list price {offp}), unlimited concurrency, bank transfer and VAT special invoices for teams.',
                  notice=hero_notice, facts=facts),
        about=dict(kicker='About the model', h2=f'{name}: {sell}', paras=m['about'],
                   spec=[('Model ID', mid, 'The model field in the request body, case-sensitive'), ('Endpoint', 'Text to speech', 'POST /v1/audio/speech'),
                         ('Price', price, 'Per 10K characters, about 19% off list'), ('Languages', langs_fact, 'ElevenLabs docs'),
                         ('Per-request limit', limit_text(s), 'ElevenLabs docs; the AnyAIGC reference lists input at 4,096 characters max'),
                         ('Latency', latency_text(s), 'Median inference latency stated by ElevenLabs, excluding network')]),
        features=dict(kicker='Capabilities', h2=f'What {name} can do',
                      items=m['feats'] + [('OpenAI-style endpoint', 'One Bearer key and <code>/v1/audio/speech</code>. Pass model, input and voice, get an audio file back. The audio.speech call in the OpenAI SDK works too.'),
                                          ('Unlimited concurrency, about 19% off', f'Every account gets unlimited concurrency by default. {price} per 10K characters, against an ElevenLabs list price of {offp}.')]),
        pricing=dict(kicker='Pricing', h2=f'{name} API pricing', lead='Billed on the number of input characters at a fixed price, with no subscription or monthly fee, about 19% off the ElevenLabs list price.',
                     billing_label='Billing at a glance', billing=billing(s), head=PRICE_HEAD, labels=pricing_labels(),
                     caption=f'{mid} price comparison (USD): ElevenLabs list price and AnyAIGC price', note=pricing_note(s),
                     costs_h3='Cost examples', costs_lead='Estimates for common uses, worked out by multiplying the unit prices above, next to the list price.', costs=costs(s)),
        compare=dict(kicker='Compare', h2='Choosing among the 7 Eleven voice models', lead='Pick v4 for polished final audio, v4 Turbo for voice assistants, Multilingual v2 for long text and mixed languages, and Flash v2.5 for large subtitle batches.',
                     head=COMPARE_HEAD, rows=compare_rows(), caption='Comparison of the 7 Eleven voice models; prices are AnyAIGC USD per 10K characters', note=COMPARE_NOTE),
        uses=dict(kicker='Use cases', h2=f'What {name} is good for', items=m['uses']),
        qs=dict(kicker='Quick start', h2=f'Call the {name} API in three steps', steps=qs_steps(mid),
                tabs=[('curl', 'cURL', 'POST /v1/audio/speech', code.curl(mid, text)),
                      ('py', 'Python · requests', 'Python · requests', code.requests_py(mid, text)),
                      ('sdk', 'Python · OpenAI SDK', 'Python · openai SDK', code.sdk_py(mid, text))],
                callout=f'<strong>Parameter notes:</strong> the model ID is case-sensitive, so write <code>{mid}</code>. <code>voice</code> takes an ElevenLabs voice_id, and an unknown or unavailable one returns 400. The reference lists <code>input</code> at 4,096 characters max, so split longer text. The examples save the response body as an mp3 file.',
                note=QS_NOTE),
        family_h2='All Eleven models', family_lead='One API key calls every Eleven voice model below. Choose by use case and budget.',
        faq_h2=f'{name} API FAQ', faqs=faqs,
        final=dict(h2=f'Call {name} with one key', p=f'Sign up, create an API key, and you can use {mid} in your code within minutes. Your balance works across 300+ models.', other=f'{name} API 中文页'),
        ent_name=name,
    )
