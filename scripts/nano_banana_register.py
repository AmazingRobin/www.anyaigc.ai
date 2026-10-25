# 把 Nano Banana 系列专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/nano_banana_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Gemini 系列之后新增「Nano Banana 系列」类别（总览页由类别标题链接，不单独放卡片）。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nano_banana_data import SITE, DATE, SLUGS, MODEL_SLUGS, USD, cny_min, CNY  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
_raw = io.open(os.path.join(ROOT, 'assets/icons/nanobanana-color.svg'), encoding='utf-8').read()
_body = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S)
LOGO = f'<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" focusable="false">{_body}</svg>'

# slug -> (中文名, 中文简介, 中文标签, 中文价格, 英文名, 英文简介, 英文标签, 英文价格, 厂商标注)
CARDS = {
    'nano-banana': ('Nano Banana API（全系总览）', '', [], '', 'Nano Banana API (overview)', '', [], '', ''),
    'nano-banana-2.1': ('Nano Banana 2.1 API', 'Google 最新的 Nano Banana 升级版，画质和文字渲染更好，支持 4K 与超宽比例。', ['最新', '4K', '14 种比例'],
                        f'<strong>{cny_min("nano-banana-2.1")}</strong> / 张起',
                        'Nano Banana 2.1 API', "Google's latest Nano Banana update with better image quality, text rendering and 4K output.", ['Latest', '4K', '14 aspect ratios'],
                        f'From <strong>${USD["nano-banana-2.1"]}</strong> / image', 'gemini-nano-banana-2.1'),
    'nano-banana-pro': ('Nano Banana Pro API', 'Gemini 3 Pro Image，推理驱动的专业级生图，适合复杂排版和密集文字。', ['专业级', '文字排版', '4K'],
                        f'<strong>{cny_min("nano-banana-pro")}</strong> / 张起',
                        'Nano Banana Pro API', 'Gemini 3 Pro Image, a reasoning-driven model for complex layouts and dense text.', ['Pro', 'Typography', '4K'],
                        f'From <strong>${USD["nano-banana-pro"]}</strong> / image', 'gemini-3-pro-image'),
    'nano-banana-2': ('Nano Banana 2 API', 'Gemini 3.1 Flash Image，Flash 级速度的高效生图模型，1K 与 2K 同价。', ['Flash 速度', '多图编辑', '1K/2K 同价'],
                      f'<strong>{cny_min("nano-banana-2")}</strong> / 张起',
                      'Nano Banana 2 API', 'Gemini 3.1 Flash Image, fast and efficient image generation and editing.', ['Flash speed', 'Multi-image edits', 'Grounding'],
                      f'From <strong>${USD["nano-banana-2"]}</strong> / image', 'gemini-3.1-flash-image'),
}
ORDER = ['nano-banana-2.1', 'nano-banana-pro', 'nano-banana-2']
CAT = {'zh': ('Nano Banana 系列', '全系总览与价格对比', '查看专题 →'), 'en': ('Nano Banana models', 'overview and price comparison', 'View guide →')}


def card(lang, slug):
    c = CARDS[slug]
    name, desc, tags, price = (c[0], c[1], c[2], c[3]) if lang == 'zh' else (c[4], c[5], c[6], c[7])
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#121317;border:1px solid #121317" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{name}</a></h3>
              <span class="af-model-cat">Google · {c[8]}</span>
            </div>
          </div>
          <p>{desc}</p>
          <ul class="af-tags">{tg}
          </ul>
          <div class="af-model-foot">
            <span>{price}</span>
            <span class="af-model-go" aria-hidden="true">{CAT[lang][2]}</span>
          </div>
        </li>
'''


def hub(lang):
    p = os.path.join(ROOT, lang, 'models', 'index.html')
    s = io.open(p, encoding='utf-8').read()
    o = s
    name, more, _ = CAT[lang]
    cards = ''.join(card(lang, x) for x in ORDER)
    if '<!-- Nano Banana -->' in s:
        s = re.sub(r'(<!-- Nano Banana -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /Nano Banana -->)',
                   lambda m: m.group(1) + cards + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-nano-banana" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/nano-banana">'
                 f'<span class="af-cat-name">{name}</span><span class="af-cat-more">{more} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>{NL}'
                 f'      <!-- Nano Banana -->{NL}      <ul class="af-models">{NL}{cards}      </ul>{NL}      <!-- /Nano Banana -->{NL}{NL}')
        assert '      <!-- Jev -->\n' in s
        s = s.replace('      <!-- Jev -->\n', block + '      <!-- Jev -->\n', 1)
        s = re.sub(r'(<li><a href="#cat-gemini">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-nano-banana">{name}</a></li>', s, count=1)
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
                                  'name': CARDS[x][0] if lang == 'zh' else CARDS[x][4], 'url': u})
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
        io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


if __name__ == '__main__':
    print('hub zh:', hub('zh'), 'hub en:', hub('en'), 'sitemap:', sitemap())
