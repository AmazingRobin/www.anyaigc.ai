# 把 Grok Image 系列注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/grok_image_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Meta Muse 之后新增「Grok Image 系列」类别（总览页由类别标题链接，不单独放卡片）。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grok_image_data import SITE, DATE, SLUGS, HUB, MODELS, cny  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
D = re.search(r'<path d="([^"]+)"', io.open(os.path.join(ROOT, 'assets/icons/grok.svg'), encoding='utf-8').read()).group(1)
LOGO = f'<svg viewBox="0 0 24 24" width="24" height="24" fill="#ffffff" fill-rule="evenodd" aria-hidden="true" focusable="false"><path d="{D}"></path></svg>'
CAT = {'zh': ('Grok Image 系列', '全系总览与价格对比', '查看专题 →'), 'en': ('Grok Image models', 'overview and price comparison', 'View guide →')}
# 分档的模型显示最低档，加「起 / from」
p = lambda lang, s: (f'<strong>¥{cny(MODELS[s]["usd"])}</strong> / 张' + (' 起' if MODELS[s]['tiered'] else '') if lang == 'zh'
                     else ('from ' if MODELS[s]['tiered'] else '') + f'<strong>${MODELS[s]["usd"]}</strong> / image')

# slug -> (中文名, 中文简介, 中文标签, 英文名, 英文简介, 英文标签)
CARDS = {
    'grok-image': ('Grok Imagine API（全系总览）', '', [], 'Grok Imagine API (overview)', '', []),
    'grok-imagine-image-2.0': ('Grok Imagine Image 2.0 API', 'xAI 新一代生图与改图模型，文字排版清晰，15 种宽高比。', ['推荐', '精准改图', '文字排版'],
                               'Grok Imagine Image 2.0 API', "xAI's latest image model for generation and editing, with sharp typography and 15 aspect ratios.", ['Recommended', 'Editing', 'Typography']),
    'grok-imagine-image': ('Grok Imagine Image API', 'xAI 第一代 Imagine 文生图模型，1k / 2k 输出，接口简单。', ['文生图', '1k / 2k', '第一代'],
                           'Grok Imagine Image API', "xAI's first Imagine text-to-image model, with 1k and 2k output.", ['Text to image', '1k / 2k', 'First gen']),
    'grok-imagine-image-quality': ('Grok Imagine Image Quality API', 'xAI 已并入 Image 2.0，旧代码仍可调用；换成 2.0 Low 更便宜。', ['已停用', '并入 2.0', '迁移'],
                                   'Grok Imagine Image Quality API', 'Retired by xAI and merged into Image 2.0. Old code still works, and 2.0 Low costs less.', ['Retired', 'Merged into 2.0', 'Migration']),
}


def card(lang, slug):
    c = CARDS[slug]
    name, desc, tags = (c[0], c[1], c[2]) if lang == 'zh' else (c[3], c[4], c[5])
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#0a0a0a;border:1px solid #0a0a0a" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{name}</a></h3>
              <span class="af-model-cat">xAI · {slug}</span>
            </div>
          </div>
          <p>{desc}</p>
          <ul class="af-tags">{tg}
          </ul>
          <div class="af-model-foot">
            <span>{p(lang, slug)}</span>
            <span class="af-model-go" aria-hidden="true">{CAT[lang][2]}</span>
          </div>
        </li>
'''


def hub(lang):
    path = os.path.join(ROOT, lang, 'models', 'index.html')
    s = io.open(path, encoding='utf-8').read()
    o = s
    name, more, _ = CAT[lang]
    cards = ''.join(card(lang, x) for x in SLUGS if x != HUB)
    if '<!-- Grok Image -->' in s:
        s = re.sub(r'(<!-- Grok Image -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /Grok Image -->)',
                   lambda m: m.group(1) + cards + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-grok-image" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/{HUB}">'
                 f'<span class="af-cat-name">{name}</span><span class="af-cat-more">{more} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>{NL}'
                 f'      <!-- Grok Image -->{NL}      <ul class="af-models">{NL}{cards}      </ul>{NL}      <!-- /Grok Image -->{NL}{NL}')
        anchor = '      <!-- /Muse -->\n\n'
        assert anchor in s
        s = s.replace(anchor, anchor + block, 1)
        s = re.sub(r'(<li><a href="#cat-muse">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-grok-image">{name}</a></li>', s, count=1)
    # JSON-LD ItemList：追加条目并更新数量
    m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
    g = json.loads(m.group(1))
    for n in (g['@graph'] if '@graph' in g else [g]):
        if n.get('@type') == 'ItemList':
            items = n['itemListElement']
            have = {x['url'] for x in items}
            for x in SLUGS:
                u = f'{SITE}/{lang}/models/{x}'
                if u not in have:
                    items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': CARDS[x][0] if lang == 'zh' else CARDS[x][3], 'url': u})
            n['numberOfItems'] = len(items)
    s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False, indent=2) + s[m.end(1):]
    if s != o:
        io.open(path, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


def sitemap():
    path = os.path.join(ROOT, 'sitemap.xml')
    s = io.open(path, encoding='utf-8').read()
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
        io.open(path, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


if __name__ == '__main__':
    print('hub zh:', hub('zh'), 'hub en:', hub('en'), 'sitemap:', sitemap())
