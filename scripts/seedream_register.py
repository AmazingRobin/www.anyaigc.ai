# 把 Seedream 系列专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/seedream_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Nano Banana 系列之后新增「Seedream 系列」类别（总览页由类别标题链接，不单独放卡片）。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seedream_data import SITE, DATE, SLUGS, MODELS, cny, usd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
_raw = io.open(os.path.join(ROOT, 'assets/icons/bytedance-color.svg'), encoding='utf-8').read()
_body = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', _raw, re.S).group(1), flags=re.S)
LOGO = f'<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" focusable="false">{_body}</svg>'

# slug -> (中文简介, 中文标签, 英文简介, 英文标签)
CARDS = {
    'seedream-5.0-pro': ('字节跳动 Seed 旗舰生图模型，擅长高密度信息图、框选精准编辑和多语种文字。', ['最新', '信息图', '精准编辑'],
                         "ByteDance Seed's flagship image model for dense infographics, precise markup edits and multilingual text.", ['Latest', 'Infographics', 'Precise edits']),
    'seedream-5.0-lite': ('Seedream 5.0 轻量版，深度思考加联网检索，最高 4K，支持组图。', ['4K', '联网检索', '组图'],
                          'The lighter Seedream 5.0 with reasoning and web search, up to 4K and image sets.', ['4K', 'Web search', 'Image sets']),
    'seedream-4.5': ('海报排版与小字更稳，改图保持原图细节，多图融合角色一致。', ['海报排版', '多图融合', '4K'],
                     'Stronger poster layout and small text, keeps source details, consistent multi-image blends.', ['Typography', 'Multi-image', '4K']),
    'seedream-4.0': ('文生图、编辑和多图合成一体，一次最多输出 15 张关联图片。', ['生成编辑一体', '组图', '1K–4K'],
                     'Generation, editing and compositing in one model, up to 15 related images per request.', ['Edit + generate', 'Image sets', '1K–4K']),
    'seedream-3.0': ('中英双语文生图模型，原生 2K。旧版，新项目建议用 4.0 及以上。', ['旧版', '文生图', '原生 2K'],
                     'Bilingual Chinese-English text-to-image model with native 2K. Legacy; use 4.0 or newer for new work.', ['Legacy', 'Text-to-image', 'Native 2K']),
}
ORDER = ['seedream-5.0-pro', 'seedream-5.0-lite', 'seedream-4.5', 'seedream-4.0', 'seedream-3.0']
CAT = {'zh': ('Seedream 系列', '全系总览与价格对比', '查看专题 →'), 'en': ('Seedream models', 'overview and price comparison', 'View guide →')}
VENDOR = {'zh': '字节跳动', 'en': 'ByteDance'}


def card(lang, slug):
    m = MODELS[slug]
    zd, zt, ed, et = CARDS[slug]
    desc, tags = (zd, zt) if lang == 'zh' else (ed, et)
    if lang == 'zh':
        price = f'<strong>{cny(slug)}</strong> / {m["unit"]}{"起" if m["unit"] == "张" else ""}'
    else:
        price = f'From <strong>{usd(slug)}</strong> / image' if m['unit'] == '张' else f'<strong>{usd(slug)}</strong> / request'
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#ffffff;border:1px solid #e1e6ec" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{m['name']} API</a></h3>
              <span class="af-model-cat">{VENDOR[lang]} · {m['id']}</span>
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


def item_name(lang, slug):
    if slug == 'seedream':
        return 'Seedream API（全系总览）' if lang == 'zh' else 'Seedream API (overview)'
    return f'{MODELS[slug]["name"]} API'


def hub(lang):
    p = os.path.join(ROOT, lang, 'models', 'index.html')
    s = io.open(p, encoding='utf-8').read()
    o = s
    name, more, _ = CAT[lang]
    cards = ''.join(card(lang, x) for x in ORDER)
    if '<!-- Seedream -->' in s:
        s = re.sub(r'(<!-- Seedream -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /Seedream -->)',
                   lambda m: m.group(1) + cards + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-seedream" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/seedream">'
                 f'<span class="af-cat-name">{name}</span><span class="af-cat-more">{more} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>{NL}'
                 f'      <!-- Seedream -->{NL}      <ul class="af-models">{NL}{cards}      </ul>{NL}      <!-- /Seedream -->{NL}{NL}')
        anchor = '      <h3 class="af-section-head" id="cat-kimi"'
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
        s = re.sub(r'(<li><a href="#cat-nano-banana">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-seedream">{name}</a></li>', s, count=1)
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
                    items.append({'@type': 'ListItem', 'position': len(items) + 1, 'name': item_name(lang, x), 'url': u})
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
