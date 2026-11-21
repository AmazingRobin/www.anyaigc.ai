# ElevenLabs (Eleven) series speech-to-text (STT) topic pages, English copy: eleven-scribe-v3, eleven-scribe-v2. Dispatched from eleven_copy_en.build(); same return shape as the TTS pages.
# Prices come from eleven_data.PRICE (model catalog detail drawer, billed per second, same for both models); list price $0.20 per hour from the
# Speech to Text API row of elevenlabs.io/pricing/api (read 2026-11-20). Capabilities from elevenlabs.io/docs/overview/models and
# docs/overview/capabilities/speech-to-text; the v3 release date from docs/changelog.
# The AnyAIGC reference (Speech to text, gpt-4o-transcribe) lists only file, model, language, prompt, response_format and temperature. Word timestamps,
# diarization, keyterm prompting and multichannel are ElevenLabs official features: the copy labels them as such and says to test, never claims they work through AnyAIGC.
# Do not claim "works from mainland China" on English pages.
from decimal import Decimal

from eleven_data import (PRICE, MODELS, REG, MARKET, SUPPORT, DOCS_TRANSCRIBE, OFFICIAL_MODELS, OFFICIAL_PRICING,
                         OFFICIAL_CHANGELOG, STT_OFFICIAL_HOUR, STT_HOUR, STT_MINUTE)
from eleven_layout import money, stt_cost
import eleven_code as code

DEAL = '19% off list price'


def p(slug):
    return f'${PRICE[slug]}'


def link(slug):
    return f'<a href="/en/models/{slug}">{MODELS[slug]["name"]}</a>'


def off_text(seconds):
    d = Decimal(STT_OFFICIAL_HOUR) * Decimal(seconds) / Decimal(3600)
    q = d.quantize(Decimal('0.0001'))
    return money(d) if d == q else 'about ' + money(q)


M = {
    'eleven-scribe-v3': dict(
        sell='Accurate recording transcription', lead='The ElevenLabs speech-to-text model for recorded audio, 90+ languages, which ElevenLabs calls its most accurate model for recordings, for meeting notes, subtitles and interview write-ups',
        tag='The ElevenLabs speech-to-text model for recorded audio: ElevenLabs calls it its most accurate recording model, with 90+ languages.',
        about=['Eleven Scribe v3 is the ElevenLabs speech-to-text (STT) model for recorded audio. The official model docs call it the most accurate speech recognition model for recorded audio, covering 90+ languages. The ElevenLabs changelog dates the Scribe v3 release to 9 November 2026 and says it makes 27% fewer word errors than Scribe v2 on the FLEURS benchmark across 102 languages. The AnyAIGC model catalog describes it as the same price and same interface as v2, with clearly better accuracy and speaker separation.',
               'The official docs list word-level timestamps, speaker diarization for up to 32 speakers, keyterm prompting with up to 1,000 terms, audio event tagging such as laughter and applause, and entity detection. The official capabilities page gives a 5 GB file limit, up to 15 hours per file, and up to 5 channels for multichannel audio. Those are the capabilities listed in the official ElevenLabs docs.',
               'On AnyAIGC, <code>scribe_v3</code> runs on <code>POST /v1/audio/transcriptions</code>. You upload audio as multipart/form-data and are billed per second of audio, with no concurrency limit and a single Bearer key, so you do not need a separate ElevenLabs account.'],
        feats=[('90+ languages', 'The official docs list 90+ languages, and both Mandarin and Cantonese are on the official language list.'),
               ('Word-level timestamps', 'ElevenLabs says v3 returns word-level timestamps, useful for subtitle alignment.'),
               ('Speaker diarization', 'ElevenLabs says v3 separates up to 32 speakers, a fit for multi-person meetings and interviews.'),
               ('Keyterms and audio events', 'ElevenLabs says v3 accepts up to 1,000 keyterms to correct names and product terms, and tags non-speech events such as laughter and applause.')],
        uses=[('voice-conversational.webp', '01 · Meetings', 'Meeting notes and recording write-ups', 'Turn a meeting recording into a transcript, then pass it to a language model for key points and action items. ElevenLabs says v3 can tell multiple speakers apart.'),
              ('voice-entertainment.webp', '02 · Subtitles', 'Video subtitles and podcast transcripts', 'Convert spoken video and podcast content into a first-draft transcript or subtitle file, then proofread it.'),
              ('voice-ads.webp', '03 · QA', 'Call-center recording QA', 'Transcribe call recordings, then search by keyword and sample service quality. Billing is per second of audio, so batch cost is easy to estimate.'),
              ('voice-narration.webp', '04 · Interviews', 'Interview and research write-ups', 'Turn interviews and research recordings into text that you can search, quote and archive.')]),
    'eleven-scribe-v2': dict(
        sell='Recording transcription', lead='The previous-generation ElevenLabs workhorse for recording transcription, 90+ languages, word timestamps, diarization and keyterm prompting, for meeting notes and subtitles',
        tag='The previous-generation ElevenLabs speech-to-text model: 90+ languages, still listed as available in the official docs and succeeded by Scribe v3.',
        about=['Eleven Scribe v2 is an ElevenLabs speech-to-text (STT) model. The official model docs call it the previous state-of-the-art speech recognition model, succeeded by <code>scribe_v3</code>, designed for accurate transcription across 90+ languages. It remains available and is not in the official list of deprecated models. The AnyAIGC model catalog describes it as the previous workhorse with 90+ languages, word timestamps, speaker diarization, keyterm prompting and multichannel splitting.',
               'The official docs list word-level timestamps, speaker diarization, dynamic audio tagging, keyterm prompting and entity detection for v2. The official capabilities page gives a 5 GB file limit, up to 15 hours per file, and up to 5 channels for multichannel audio. Those are the capabilities listed in the official ElevenLabs docs.',
               'On AnyAIGC, <code>scribe_v2</code> runs on <code>POST /v1/audio/transcriptions</code>, billed per second of audio at the same price as <a href="/en/models/eleven-scribe-v3">Eleven Scribe v3</a>, with no concurrency limit. For a new project, transcribe the same recording with both and compare.'],
        feats=[('90+ languages', 'The official docs list 90+ languages, and both Mandarin and Cantonese are on the official language list.'),
               ('Word-level timestamps', 'ElevenLabs says v2 returns word-level timestamps.'),
               ('Speaker diarization', 'The official docs list speaker diarization for v2, a fit for multi-person meetings and interviews. The model catalog also mentions multichannel splitting, which separates speakers by channel.'),
               ('Keyterm prompting', 'The official docs list keyterm prompting for v2, so you can hint at names and industry terms to cut misrecognition.')],
        uses=[('voice-conversational.webp', '01 · Meetings', 'Meeting notes and recording write-ups', 'Turn a meeting recording into a transcript, then use a language model to pull out key points and action items.'),
              ('voice-entertainment.webp', '02 · Subtitles', 'Video subtitles and podcast transcripts', 'Convert spoken content into a first-draft transcript or subtitle file, then proofread it.'),
              ('voice-ads.webp', '03 · QA', 'Call-center recording QA', 'Batch-transcribe call recordings, then search by keyword and sample service quality.'),
              ('voice-narration.webp', '04 · Interviews', 'Interview and research write-ups', 'Turn interviews and research recordings into text that you can search, quote and archive.')]),
}

POS = {'eleven-scribe-v3': 'Latest recording transcription, higher accuracy', 'eleven-scribe-v2': 'Previous generation, still available'}
STATUS = {'eleven-scribe-v3': 'Latest, released 2026-11-09 (official changelog)', 'eleven-scribe-v2': 'Previous generation, succeeded by Scribe v3, still available'}

QS_NOTE = f'See the <a href="{DOCS_TRANSCRIBE}" target="_blank" rel="noopener">Speech to text API reference</a>. To call Scribe, set model to scribe_v3 or scribe_v2.'
PRICE_HEAD = [('Billing unit', ''), ('Model', ''), ('ElevenLabs list price (USD)', 'o-num'), ('AnyAIGC price (USD)', 'o-num o-hl')]
COMPARE_HEAD = [('Model', ''), ('Focus', 'el-txt'), ('Languages (official)', 'el-txt'), ('Official status', 'el-txt'), ('AnyAIGC per hour', 'o-num o-hl')]


def compare_rows():
    return [(f'<a href="/en/models/{s}">{MODELS[s]["name"]}</a>', '', [POS[s], '90+ languages', STATUS[s], f'${STT_HOUR}'], s) for s in ('eleven-scribe-v3', 'eleven-scribe-v2')]


COMPARE_NOTE = ('Language counts and model status come from the <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs model docs</a>, and the v3 release date from the <a href="' + OFFICIAL_CHANGELOG
                + '" target="_blank" rel="noopener">official changelog</a>. Both models cost the same on AnyAIGC, and the hourly price is the per-second price x 3600. Live prices are in the model catalog.')


def costs(slug):
    c = lambda sec: money(stt_cost(slug, sec))
    o = lambda sec: f'ElevenLabs list price for the same usage {off_text(sec)}'
    return [('10-minute podcast', '600 seconds x unit price', c(600), o(600)),
            ('1-hour meeting recording', '3,600 seconds x unit price', c(3600), o(3600)),
            ('100 hours of support calls', '360,000 seconds x unit price', c(360000), o(360000))]


def billing(slug):
    return [('Per second of audio', 'Billed on audio length'), ('About 19% off', f'List ${STT_OFFICIAL_HOUR} per hour'), ('Unlimited concurrency', 'Default for every account'), ('USD', 'One balance for 300+ models')]


def price_rows(slug):
    mid = MODELS[slug]['id']
    return [('Per second', 'Model catalog billing unit', '—', '$' + PRICE[slug], mid, True),
            ('Per minute', 'Per-second price x 60', '—', '$' + STT_MINUTE, mid, False),
            ('Per hour', 'Per-second price x 3600, matches the ElevenLabs pricing page', '$' + STT_OFFICIAL_HOUR, '$' + STT_HOUR, mid, False)]


def pricing_note():
    return (f'Prices are in USD, billed on audio length in seconds. The table shows the lowest catalog price; live prices are in the <a href="{MARKET}">AnyAIGC model catalog</a>. '
            f'The list price comes from the Speech to Text API row on the <a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener">ElevenLabs pricing page</a>: Scribe v3 and Scribe v2 are both ${STT_OFFICIAL_HOUR} per hour. '
            f'AnyAIGC charges ${STT_HOUR} per hour (${PRICE["eleven-scribe-v3"]} per second x 3600), which is 81% of list, about 19% off. ElevenLabs quotes its price per hour, so the per-second and per-minute list cells are left empty.')


def qs_steps(model):
    return ['<strong>Sign up and top up</strong>: create an account at <a href="' + REG + '">anyaigc.ai</a>. Top-ups start at $1, and the balance works across every model on the platform.',
            '<strong>Create an API key</strong>: create a token in the console, copy the key that starts with <code>sk-</code>, and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
            f'<strong>Upload a recording</strong>: call <code>POST https://anyaigc.ai/v1/audio/transcriptions</code> as multipart/form-data with <code>file</code> (the audio file) and <code>model</code> set to <code>{model}</code>, authenticate with <code>Authorization: Bearer</code>, and read the transcript from <code>text</code> in the response.']


def faq_common(name):
    return [
        ('Can AnyAIGC issue invoices, including VAT special invoices?',
         'Yes. AnyAIGC can issue invoices for every top-up, including Chinese VAT general invoices and VAT special invoices. Send your invoicing details to support.'),
        ('Can my company pay by bank transfer and sign a contract?',
         f'Yes. You can top up by corporate bank transfer and sign a service agreement, with a dedicated support contact and technical contact. For company purchases, <a href="{SUPPORT}">contact AnyAIGC support</a>.'),
        ('Are my uploaded recordings and the transcripts used for training?',
         'No. Unless the law requires it, AnyAIGC does not persistently store your inputs or outputs and does not use them for training. Requests are encrypted with HTTPS. See the AnyAIGC <a href="/privacy">Privacy Policy</a>. The data policy of the model itself is set by ElevenLabs. If a recording contains personal information, make sure you have the right to process it.'),
    ]


def special_faq(slug):
    if slug == 'eleven-scribe-v3':
        return ('What is the difference between Scribe v3 and Scribe v2?',
                'The ElevenLabs changelog says Scribe v3 makes 27% fewer word errors than Scribe v2 on the FLEURS benchmark across 102 languages, and that it labels speakers more accurately. On AnyAIGC the two have the same price and the same interface; only the model field differs. For a new project try v3 first, or transcribe the same recording with both and compare. See ' + link('eleven-scribe-v2') + ' for v2.')
    return ('Can I still use Scribe v2, and how do I choose between it and Scribe v3?',
            'Yes. The official model docs call Scribe v2 the previous generation, succeeded by Scribe v3, but still available, and it is not in the official list of deprecated models. Both cost the same on AnyAIGC. A project already on v2 can keep using it; for a new project, transcribe the same recording with both before you choose. See ' + link('eleven-scribe-v3') + '. Whether a model stays available is shown in the model catalog.')


def build(slug):
    m = M[slug]
    d = MODELS[slug]
    mid, name = d['id'], d['name']
    s = slug
    price = p(s)

    faqs = [
        (f'How much does the {name} API cost?',
         f'On AnyAIGC, <code>{mid}</code> is billed per second of audio at {price} per second, which is ${STT_MINUTE} per minute or ${STT_HOUR} per hour, about 19% off the ElevenLabs list price of ${STT_OFFICIAL_HOUR} per hour. The price is fixed, with no subscription or monthly fee. Live prices are in the model catalog.'),
        (f'What is the {name} model ID, and how does it relate to ElevenLabs?',
         f'The model ID is <code>{mid}</code> (case-sensitive), the same as the ElevenLabs model_id. AnyAIGC is an independent API provider that offers an OpenAI-style <code>/v1/audio/transcriptions</code> call, and is not affiliated with ElevenLabs.'),
        (f'How do I choose between {name} and the other Eleven models?',
         f'The Eleven models on AnyAIGC fall into two kinds: 7 text-to-speech models, starting with {link("eleven-v4")}, and 2 speech-to-text models, {link("eleven-scribe-v3")} and {link("eleven-scribe-v2")}. Pick Scribe to turn recordings into text, and pick v4, Multilingual v2 or another text-to-speech model to turn text into speech.'),
        (f'How do I call the {name} API?',
         f'Call <code>POST https://anyaigc.ai/v1/audio/transcriptions</code> as multipart/form-data with <code>file</code> (the audio file) and <code>model</code> set to <code>{mid}</code>, and authenticate with <code>Authorization: Bearer</code>. A successful call returns <code>{{"text": "..."}}</code>. See the <a href="{DOCS_TRANSCRIBE}" target="_blank" rel="noopener">API reference</a>.'),
        (f'Which audio formats does {name} accept, and how large can a file be?',
         'The API reference lists these file formats: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav and webm. The ElevenLabs capabilities page gives a limit of 5 GB and 15 hours per file.'),
        (f'Does {name} support Chinese, and how many languages?',
         'Yes. The official docs say Scribe supports 90+ languages, and Mandarin and Cantonese are on the official language list. For the exact languages see the <a href="' + OFFICIAL_MODELS + '" target="_blank" rel="noopener">ElevenLabs model docs</a>.'),
        special_faq(s),
        ('Is there a real-time (streaming) transcription model?',
         'This page covers the recording-file models <code>scribe_v3</code> and <code>scribe_v2</code>, called over HTTP at <code>/v1/audio/transcriptions</code>: you upload a complete recording and get the text back. ElevenLabs also offers real-time models (such as scribe_v3_live), which are out of scope here. Whether they are offered is shown in the model catalog.'),
        ('Is there a rate limit?',
         f'AnyAIGC sets no concurrency limit on <code>{mid}</code>, and every account gets this by default, so batch transcription and parallel tasks are fine. Billing is per second of audio, with no monthly fee and no quota that resets on a time window.'),
    ]
    faqs += faq_common(name)
    key_q = (f'How do I get a {name} API key?',
             f'Sign up and top up at <a href="{REG}">anyaigc.ai</a>, then create a token in the console. One key works for 300+ models on the platform, and you do not need a separate ElevenLabs account. Set <code>model</code> to <code>{mid}</code> in the request.')
    faqs.insert(3, key_q)

    sell = m['sell']
    facts = [('Model ID', mid), ('Price', f'{price} / sec'), ('Languages', '90+ languages'), ('Concurrency', 'Unlimited'), ('Teams', 'Invoices · contracts')]
    hero_notice = None
    if s == 'eleven-scribe-v2':
        hero_notice = f'ElevenLabs docs call Scribe v2 the previous generation, succeeded by <a href="/en/models/eleven-scribe-v3">Scribe v3</a> (same price on AnyAIGC). v2 is still available from ElevenLabs and callable in the model catalog today; whether it stays available is shown in the <a href="{MARKET}">model catalog</a>.'

    return dict(
        title=f'{name} API Price and Access, 19% Off - AnyAIGC',
        desc=f'{mid} speech-to-text API: {price} per second (${STT_HOUR}/hour), about 19% off list. Unlimited concurrency, bank transfer and VAT special invoices.',
        og_desc=f'{mid} at {price} per second (${STT_HOUR} per hour), about 19% off the ElevenLabs list price. {m["lead"]}. Unlimited concurrency, bank transfer and VAT special invoices.',
        og_alt=f'AnyAIGC {mid} API: {price} per second, about 19% off list price',
        keywords=f'{mid} API,{mid},{name} API price,{name} API access,{name} API key,ElevenLabs Scribe API,ElevenLabs API,ElevenLabs speech to text,speech to text API,transcription API,meeting transcription API,{name} API for teams,{name} API VAT special invoice,ElevenLabs API bank transfer,AnyAIGC',
        crumb=f'{name} API', product=f'{name} API (AnyAIGC)', sku=s, category='Speech-to-text API',
        product_desc=f'Call ElevenLabs {name} through AnyAIGC: POST /v1/audio/transcriptions, billed per second of audio at {price} per second (${STT_HOUR} per hour, about 19% off list price), unlimited concurrency.',
        offers=[('Per second', PRICE[s])],
        hero=dict(eyebrow=f'ElevenLabs · {mid}', deal=DEAL,
                  h1=f'Eleven <b>{d["short"]}</b><span class="o-sr"> API</span>',
                  lead=f'{m["tag"]} One API key, billed per second of audio, about 19% off the ElevenLabs list price.',
                  sample=None,
                  sub=f'<code>{mid}</code> {price} per second (${STT_HOUR} per hour; ElevenLabs list price ${STT_OFFICIAL_HOUR} per hour), unlimited concurrency, bank transfer and VAT special invoices for teams.',
                  notice=hero_notice, facts=facts),
        about=dict(kicker='About the model', h2=f'{name}: {sell}', paras=m['about'],
                   spec=[('Model ID', mid, 'The model field in the request body, case-sensitive'), ('Endpoint', 'Speech to text', 'POST /v1/audio/transcriptions'),
                         ('Price', price, 'Per second, about 19% off list'), ('Languages', '90+ languages', 'ElevenLabs docs'),
                         ('Per-file limit', '5 GB / 15 hours', 'ElevenLabs capabilities page'),
                         ('Audio formats', 'mp3, wav, m4a and more', 'AnyAIGC reference: flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm')]),
        features=dict(kicker='Capabilities', h2=f'What {name} can do',
                      items=m['feats'] + [('OpenAI-style endpoint', 'One Bearer key. Upload audio as multipart to <code>/v1/audio/transcriptions</code> with file and model, and get <code>{"text": "..."}</code> back. The audio.transcriptions call in the OpenAI SDK works too.'),
                                          ('Unlimited concurrency, about 19% off', f'Every account gets unlimited concurrency by default. {price} per second, or ${STT_HOUR} per hour, against an ElevenLabs list price of ${STT_OFFICIAL_HOUR} per hour.')]),
        pricing=dict(kicker='Pricing', h2=f'{name} API pricing', lead='Billed on audio length in seconds at a fixed price, with no subscription or monthly fee, about 19% off the ElevenLabs list price.',
                     billing_label='Billing at a glance', billing=billing(s), head=PRICE_HEAD, labels=None, rows=price_rows(s),
                     caption=f'{mid} price comparison (USD): ElevenLabs list price and AnyAIGC price', note=pricing_note(),
                     costs_h3='Cost examples', costs_lead='Estimates for common uses, worked out by multiplying the unit price above, next to the list price.', costs=costs(s)),
        compare=dict(kicker='Compare', h2='Choosing between Scribe v3 and Scribe v2', lead='Both cost the same and use the same interface. Try Scribe v3 first on a new project, keep v2 if you already use it, or transcribe one recording with both before you decide.',
                     head=COMPARE_HEAD, rows=compare_rows(), caption='Comparison of the Eleven Scribe speech-to-text models; prices are AnyAIGC USD per hour', note=COMPARE_NOTE),
        uses=dict(kicker='Use cases', h2=f'What {name} is good for', items=m['uses']),
        qs=dict(kicker='Quick start', h2=f'Call the {name} API in three steps', steps=qs_steps(mid),
                tabs=[('curl', 'cURL', 'POST /v1/audio/transcriptions', code.curl_stt(mid)),
                      ('py', 'Python · requests', 'Python · requests', code.requests_stt(mid)),
                      ('sdk', 'Python · OpenAI SDK', 'Python · openai SDK', code.sdk_stt(mid))],
                callout=f'<strong>Parameter notes:</strong> the model ID is case-sensitive, so write <code>{mid}</code>. The request is multipart/form-data, and <code>file</code> is the audio file itself, not a file name. A successful call returns <code>{{"text": "..."}}</code>.',
                note=QS_NOTE),
        family_h2='All Eleven models', family_lead='One API key calls every Eleven model below: 7 text-to-speech models and 2 speech-to-text models. Choose by use case and budget.',
        faq_h2=f'{name} API FAQ', faqs=faqs,
        final=dict(h2=f'Call {name} with one key', p=f'Sign up, create an API key, and you can use {mid} in your code within minutes. Your balance works across 300+ models.', other=f'{name} API 中文页'),
        ent_name=name,
    )
