# 把 Midjourney 专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/midjourney_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Meta Muse 之后新增「Midjourney」类别。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from midjourney_data import SITE, DATE, SLUG, usd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
_raw = io.open(os.path.join(ROOT, 'assets/icons/midjourney.svg'), encoding='utf-8').read()
LOGO = ('<svg viewBox="0 0 24 24" width="26" height="26" fill="#ffffff" fill-rule="evenodd" aria-hidden="true" focusable="false">'
        + re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S) + '</svg>')
CAT = {'zh': ('Midjourney', '查看专题 →'), 'en': ('Midjourney', 'View guide →')}
CARD = {
    'zh': ('Imagine 出图、放大、变体、扩图、局部重绘、混图与图生文，14 种操作一个页面讲清楚，按次计费。', ['14 种操作', 'Niji', '并发不限'],
           f'<strong>${usd("mj_imagine")}</strong> / 次'),
    'en': ('Imagine, upscale, variations, zoom, inpainting, blend and describe: all 14 operations on one page, billed per call.',
           ['14 operations', 'Niji', 'Unlimited concurrency'], f'<strong>${usd("mj_imagine")}</strong> / call'),
}


def card(lang):
    desc, tags, price = CARD[lang]
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#06051d" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{SLUG}">Midjourney API</a></h3>
              <span class="af-model-cat">Midjourney · mj_imagine</span>
            </div>
          </div>
          <p>{desc}</p>
          <ul class="af-tags">{tg}
          </ul>
          <div class="af-model-foot">
            <span>{price}</span>
            <span class="af-model-go" aria-hidden="true">{CAT[lang][1]}</span>
          </div>
        </li>
'''


def hub(lang):
    p = os.path.join(ROOT, lang, 'models', 'index.html')
    s = io.open(p, encoding='utf-8').read()
    o = s
    name = CAT[lang][0]
    if '<!-- Midjourney -->' in s:
        s = re.sub(r'(<!-- Midjourney -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /Midjourney -->)',
                   lambda m: m.group(1) + card(lang) + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-midjourney" style="font-size:16px;margin:24px 0 12px">{name}</h3>{NL}'
                 f'      <!-- Midjourney -->{NL}      <ul class="af-models">{NL}{card(lang)}      </ul>{NL}      <!-- /Midjourney -->{NL}{NL}')
        anchor = '      <!-- /Muse -->\n\n'
        assert anchor in s
        s = s.replace(anchor, anchor + block, 1)
        s = re.sub(r'(<li><a href="#cat-muse">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-midjourney">{name}</a></li>', s, count=1)
    m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
    g = json.loads(m.group(1))
    for n in (g['@graph'] if '@graph' in g else [g]):
        if n.get('@type') == 'ItemList':
            items = n['itemListElement']
            u = f'{SITE}/{lang}/models/{SLUG}'
            if u not in {x['url'] for x in items}:
                items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': 'Midjourney API', 'url': u})
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
    for lang in ('zh', 'en'):
        u = f'{SITE}/{lang}/models/{SLUG}'
        if f'<loc>{u}</loc>' in s:
            continue
        add += (f'  <url>{NL}    <loc>{u}</loc>{NL}    <lastmod>{DATE}</lastmod>{NL}'
                f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{SLUG}"/>{NL}'
                f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{SLUG}"/>{NL}'
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{SLUG}"/>{NL}  </url>{NL}')
    if add:
        s = s.replace('</urlset>', add + '</urlset>')
        s = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+', lambda m: m.group(1) + DATE, s)
        io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


if __name__ == '__main__':
    print('hub zh:', hub('zh'), 'hub en:', hub('en'), 'sitemap:', sitemap())
