# 把 Eleven（ElevenLabs）系列专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/eleven_register.py
# 重复运行结果不变：已注册就只重建卡片。7 张卡片并入现有的「音频与音乐」类别（紧跟 Suno 卡片，用 <!-- Eleven --> 标记包住）；
# 每款模型各自独立成页，没有系列总览页，所以不新增类别标题。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eleven_data import SITE, DATE, SLUGS, PRICE, MODELS  # noqa: E402
from eleven_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
LOGO = logo(cls='', size=24, fill='#ffffff')

# slug -> (中文名, 中文简介, 中文标签, 英文名, 英文简介, 英文标签)
CARDS = {
    'eleven-v4': ('Eleven v4 API', 'ElevenLabs 旗舰语音合成模型，情感层次细腻，支持内联指令，90+ 种语言，适合有声书和专业配音。', ['旗舰', '90+ 种语言', '并发不限'],
                  'Eleven v4 API', 'ElevenLabs flagship text-to-speech model with fine-grained emotion, inline directions and 90+ languages, for audiobooks and pro voiceover.', ['Flagship', '90+ languages', 'Unlimited RPM']),
    'eleven-v4-turbo': ('Eleven v4 Turbo API', 'Eleven v4 的低延迟版本，官方标注中位推理延迟约 100ms，价格是 v4 的一半，适合语音助手。', ['低延迟', '语音助手', '并发不限'],
                        'Eleven v4 Turbo API', 'Low-latency Eleven v4 with a stated median inference latency of about 100ms, half the price of v4, built for voice assistants.', ['Low latency', 'Voice agents', 'Unlimited RPM']),
    'eleven-v3': ('Eleven v3 API', '戏剧表现力强，适合故事、短剧和角色配音，70+ 种语言，单次上限 5,000 字符。', ['戏剧化', '70+ 种语言', '并发不限'],
                  'Eleven v3 API', 'Dramatic, expressive delivery for stories, short dramas and characters, 70+ languages, 5,000 characters per request.', ['Dramatic', '70+ languages', 'Unlimited RPM']),
    'eleven-v3-conversational': ('Eleven v3 Conversational API', 'v3 的对话版本，口语松弛自然，官方标注延迟约 165ms，价格是 v3 的一半。', ['对话', '口语自然', '并发不限'],
                                 'Eleven v3 Conversational API', 'Conversational version of v3 with relaxed, natural speech, a stated latency of about 165ms, half the price of v3.', ['Conversational', 'Natural tone', 'Unlimited RPM']),
    'eleven-multilingual-v2': ('Eleven Multilingual v2 API', '长篇文稿表现稳定，双语混读音色不容易崩坏，29 种语言，单次上限 10,000 字符。', ['长文本', '双语混读', '并发不限'],
                               'Eleven Multilingual v2 API', 'Stable on long-form scripts and mixed-language reading, 29 languages, 10,000 characters per request.', ['Long-form', 'Mixed languages', 'Unlimited RPM']),
    'eleven-flash-v2-5': ('Eleven Flash v2.5 API', '轻量高速，单次上限 40,000 字符，32 种语言，适合超长文本和大批量字幕生成。', ['超长文本', '批量字幕', '并发不限'],
                          'Eleven Flash v2.5 API', 'Fast and light, 40,000 characters per request and 32 languages, for very long text and bulk subtitle voiceover.', ['Very long text', 'Bulk subtitles', 'Unlimited RPM']),
    'eleven-flash-v2': ('Eleven Flash v2 API', '轻量高速播报模型，官方文档只列了英语，适合英文短句朗读和提示音。', ['轻量高速', '英语', '并发不限'],
                        'Eleven Flash v2 API', 'Light and fast announcer model, English only per the official docs, for short English lines and prompts.', ['Light and fast', 'English', 'Unlimited RPM']),
}
CAT = {'zh': ('查看专题 →', '/ 万字符', 'ElevenLabs'),
       'en': ('View guide →', '/ 10K characters', 'ElevenLabs')}


def card(lang, slug):
    c = CARDS[slug]
    name, desc, tags = (c[0], c[1], c[2]) if lang == 'zh' else (c[3], c[4], c[5])
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#0c0a09" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{name}</a></h3>
              <span class="af-model-cat">{CAT[lang][2]} · {MODELS[slug]['id']}</span>
            </div>
          </div>
          <p>{desc}</p>
          <ul class="af-tags">{tg}
          </ul>
          <div class="af-model-foot">
            <span><strong>${PRICE[slug]}</strong> {CAT[lang][1]}</span>
            <span class="af-model-go" aria-hidden="true">{CAT[lang][0]}</span>
          </div>
        </li>
'''


def hub(lang):
    p = os.path.join(ROOT, lang, 'models', 'index.html')
    s = io.open(p, encoding='utf-8').read()
    o = s
    cards = ''.join(card(lang, x) for x in SLUGS)
    block = f'        <!-- Eleven -->{NL}{cards}        <!-- /Eleven -->{NL}'
    # 先清掉旧的 Eleven 块（包括曾经插错位置的），再插到「音频与音乐」列表末尾
    s = re.sub(r'        <!-- Eleven -->\n.*?        <!-- /Eleven -->\n', '', s, flags=re.S)
    i = s.index('id="cat-audio"')
    j = s.index('<ul class="af-models">', i)
    # 必须带换行匹配行首：卡片内部标签列表的 "          </ul>" 也以 6 个空格加 </ul> 结尾，会被误认成列表结尾
    k = s.index('\n      </ul>\n', j) + 1
    s = s[:k] + block + s[k:]
    # JSON-LD ItemList：追加缺少的条目并更新数量
    m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
    g = json.loads(m.group(1))
    for n in (g['@graph'] if '@graph' in g else [g]):
        if n.get('@type') == 'ItemList':
            items = n['itemListElement']
            have = {x['url'] for x in items}
            for x in SLUGS:
                u = f'{SITE}/{lang}/models/{x}'
                if u not in have:
                    items.append({'@type': 'ListItem', 'position': len(items) + 1,
                                  'name': CARDS[x][0] if lang == 'zh' else CARDS[x][3], 'url': u})
            n['numberOfItems'] = len(items)
    s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False, indent=2) + s[m.end(1):]
    if s != o:
        io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


def sitemap():
    p = os.path.join(ROOT, 'sitemap.xml')
    s = io.open(p, encoding='utf-8').read()
    o = s
    add = ''
    for slug in SLUGS:
        for lang in ('zh', 'en'):
            u = f'{SITE}/{lang}/models/{slug}'
            if f'<loc>{u}</loc>' in s:
                continue
            add += (f'  <url>{NL}    <loc>{u}</loc>{NL}    <lastmod>{DATE}</lastmod>{NL}'
                    f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{slug}"/>{NL}'
                    f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{slug}"/>{NL}'
                    f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{slug}"/>{NL}  </url>{NL}')
    if add:
        s = s.replace('</urlset>', add + '</urlset>')
        s = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+', lambda m: m.group(1) + DATE, s)
    if s != o:
        io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


if __name__ == '__main__':
    print('hub zh:', hub('zh'), 'hub en:', hub('en'), 'sitemap:', sitemap())
