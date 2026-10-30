# 把 GLM 系列专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/glm_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Jev 系列之前新增「GLM 系列」类别（总览页由类别标题链接，不单独放卡片）。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glm_data import SITE, DATE, SLUGS, PRICE  # noqa: E402
from glm_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
LOGO = logo(cls='', size=26)

# slug -> (中文名, 中文简介, 中文标签, 英文名, 英文简介, 英文标签)
CARDS = {
    'glm': ('GLM API（全系总览）', '', [], 'GLM API (overview)', '', []),
    'glm-5.3': ('GLM-5.3 API', '智谱最新旗舰，与 GLM-5.2 同基座，复杂编程和 Agent 能力全面进阶，1M 上下文。', ['最新', '1M 上下文', '约官方 7 折'],
                'GLM-5.3 API', "Zhipu's latest flagship for complex coding and agents, with 1M context.", ['Latest', '1M context', 'About 30% off']),
    'glm-5.3-flash': ('GLM-5.3-Flash API', 'GLM-5 系列首个原生多模态模型，320B 总参 18B 激活，官方称整体超过 GLM-5.2。', ['多模态', '低价', '约官方 4 折'],
                      'GLM-5.3-Flash API', 'The first natively multimodal GLM-5 model, 320B total and 18B active parameters.', ['Multimodal', 'Low cost', 'About 60% off']),
    'glm-5.2': ('GLM-5.2 API', '面向长程任务的旗舰，真正可用的 1M 上下文，思考可开可关，MIT 开源。', ['长程任务', '思考可关', '1M'],
                'GLM-5.2 API', 'A long-horizon flagship with usable 1M context, optional thinking and an MIT license.', ['Long-horizon', 'Optional thinking', '1M']),
}
ORDER = ['glm-5.3', 'glm-5.3-flash', 'glm-5.2']
CAT = {'zh': ('GLM 系列', '全系总览与价格对比', '查看专题 →', '/ 1M 输入'),
       'en': ('GLM models', 'overview and price comparison', 'View guide →', '/ 1M input')}


def card(lang, slug):
    c = CARDS[slug]
    name, desc, tags = (c[0], c[1], c[2]) if lang == 'zh' else (c[3], c[4], c[5])
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    vendor = '智谱 Z.ai' if lang == 'zh' else 'Zhipu Z.ai'
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#f0f5ff;border:1px solid #c3d7fa" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{name}</a></h3>
              <span class="af-model-cat">{vendor} · {slug}</span>
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
    if '<!-- GLM -->' in s:
        s = re.sub(r'(<!-- GLM -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /GLM -->)',
                   lambda m: m.group(1) + cards + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-glm" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/glm">'
                 f'<span class="af-cat-name">{name}</span><span class="af-cat-more">{more} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>{NL}'
                 f'      <!-- GLM -->{NL}      <ul class="af-models">{NL}{cards}      </ul>{NL}      <!-- /GLM -->{NL}{NL}')
        assert '      <!-- Jev -->\n' in s
        s = s.replace('      <!-- Jev -->\n', block + '      <!-- Jev -->\n', 1)
        s = re.sub(r'(<li><a href="#cat-kimi">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-glm">{name}</a></li>', s, count=1)
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
