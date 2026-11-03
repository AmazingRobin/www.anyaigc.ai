# 把 Muse Image 专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/muse_image_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Seedream 系列之后新增「Meta Muse」类别。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from muse_image_pages import SITE, DATE, SLUG, MODEL, CNY, USD, icon  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
LOGO = ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" focusable="false">'
        + re.sub(r'lobe-icons-meta-(\d+)-_R_0_', r'hubmeta-\1', icon('meta-color')) + '</svg>')
CAT = {'zh': ('Meta Muse', '查看专题 →'), 'en': ('Meta Muse', 'View guide →')}
CARD = {
    'zh': ('Meta 超级智能实验室的生图模型，会联网检索、写代码作图，擅长精准改图与多图合成。', ['新上线', '精准改图', '多图合成'],
           f'<strong>¥{CNY}</strong> / 张', 'Meta'),
    'en': ('Meta Superintelligence Labs\' image model. It searches the web and writes code before it renders, with precise edits and multi-image composition.',
           ['New', 'Precise edits', 'Multi-image'], f'<strong>${USD}</strong> / image', 'Meta'),
}


def card(lang):
    desc, tags, price, vendor = CARD[lang]
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#ffffff;border:1px solid #e1e6ec" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{SLUG}">Muse Image API</a></h3>
              <span class="af-model-cat">{vendor} · {MODEL}</span>
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
    if '<!-- Muse -->' in s:
        s = re.sub(r'(<!-- Muse -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /Muse -->)',
                   lambda m: m.group(1) + card(lang) + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-muse" style="font-size:16px;margin:24px 0 12px">{name}</h3>{NL}'
                 f'      <!-- Muse -->{NL}      <ul class="af-models">{NL}{card(lang)}      </ul>{NL}      <!-- /Muse -->{NL}{NL}')
        anchor = '      <!-- /Seedream -->\n\n'
        assert anchor in s
        s = s.replace(anchor, anchor + block, 1)
        s = re.sub(r'(<li><a href="#cat-seedream">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-muse">{name}</a></li>', s, count=1)
    # JSON-LD ItemList：追加条目并更新数量
    m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
    g = json.loads(m.group(1))
    for n in (g['@graph'] if '@graph' in g else [g]):
        if n.get('@type') == 'ItemList':
            items = n['itemListElement']
            u = f'{SITE}/{lang}/models/{SLUG}'
            if u not in {x['url'] for x in items}:
                items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': 'Muse Image API', 'url': u})
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
