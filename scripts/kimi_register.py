# 把 Kimi 系列专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/kimi_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Jev 系列之前新增「Kimi 系列」类别（总览页由类别标题链接，不单独放卡片）。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kimi_data import SITE, DATE, SLUGS, PRICE  # noqa: E402
from kimi_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
LOGO = logo(cls='', size=26)

# slug -> (中文名, 中文简介, 中文标签, 英文名, 英文简介, 英文标签)
CARDS = {
    'kimi': ('Kimi API（全系总览）', '', [], 'Kimi API (overview)', '', []),
    'kimi-k3.1-pro': ('Kimi K3.1 Pro API', 'Kimi K3.1 系列首款，1M 上下文，代码、3D 创作和金融研究比 K3 更强，单价更低。', ['最新', '1M 上下文', '约官方 4 折'],
                      'Kimi K3.1 Pro API', 'The first K3.1 model, with 1M context and gains over K3 in coding, 3D and finance, at a lower price.', ['Latest', '1M context', 'About 60% off']),
    'kimi-k3': ('Kimi K3 API', 'Moonshot 开源的 2.8T 参数模型，1M 上下文，面向长程编程、知识工作和深度推理。', ['1M 上下文', '长程编程', '约官方 4 折'],
                'Kimi K3 API', "Moonshot's 2.8T-parameter open-weight model with 1M context for long-horizon coding and reasoning.", ['1M context', 'Long-horizon coding', 'About 60% off']),
    'kimi-k2.7-code': ('Kimi K2.7 Code API', '基于 K2.6 的编程向 Agent 模型，编程成功率更高，可直接接入 Claude Code。', ['编程 Agent', 'Claude Code', '256K'],
                       'Kimi K2.7 Code API', 'A coding-focused agent model built on K2.6, with higher task success and Claude Code support.', ['Coding agent', 'Claude Code', '256K']),
    'kimi-k2.6': ('Kimi K2.6 API', '开源原生多模态 Agent 模型，思考与非思考可切换，兼顾编码与通用对话。', ['多模态', '思考可关', '256K'],
                  'Kimi K2.6 API', 'An open multimodal agent model with switchable thinking, for coding and general tasks.', ['Multimodal', 'Optional thinking', '256K']),
}
ORDER = ['kimi-k3.1-pro', 'kimi-k3', 'kimi-k2.7-code', 'kimi-k2.6']
CAT = {'zh': ('Kimi 系列', '全系总览与价格对比', '查看专题 →', '/ 1M 输入'),
       'en': ('Kimi models', 'overview and price comparison', 'View guide →', '/ 1M input')}


def card(lang, slug):
    c = CARDS[slug]
    name, desc, tags = (c[0], c[1], c[2]) if lang == 'zh' else (c[3], c[4], c[5])
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#000000;border:1px solid #000000" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{name}</a></h3>
              <span class="af-model-cat">Moonshot AI · {slug}</span>
            </div>
          </div>
          <p>{desc}</p>
          <ul class="af-tags">{tg}
          </ul>
          <div class="af-model-foot">
            <span><strong>${PRICE[slug][0]}</strong> {CAT[lang][3]}</span>
            <span class="af-model-go" aria-hidden="true">{CAT[lang][2]}</span>
          </div>
        </li>
'''


def hub(lang):
    p = os.path.join(ROOT, lang, 'models', 'index.html')
    s = io.open(p, encoding='utf-8').read()
    o = s
    name, more = CAT[lang][0], CAT[lang][1]
    cards = ''.join(card(lang, x) for x in ORDER)
    if '<!-- Kimi -->' in s:
        s = re.sub(r'(<!-- Kimi -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /Kimi -->)',
                   lambda m: m.group(1) + cards + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-kimi" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/kimi">'
                 f'<span class="af-cat-name">{name}</span><span class="af-cat-more">{more} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>{NL}'
                 f'      <!-- Kimi -->{NL}      <ul class="af-models">{NL}{cards}      </ul>{NL}      <!-- /Kimi -->{NL}{NL}')
        assert '      <!-- Jev -->\n' in s
        s = s.replace('      <!-- Jev -->\n', block + '      <!-- Jev -->\n', 1)
        s = re.sub(r'(<li><a href="#cat-nano-banana">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-kimi">{name}</a></li>', s, count=1)
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
        io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


if __name__ == '__main__':
    print('hub zh:', hub('zh'), 'hub en:', hub('en'), 'sitemap:', sitemap())
