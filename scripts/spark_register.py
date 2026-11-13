# 把 SparkDesk 系列专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/spark_register.py
# 重复运行结果不变：已注册就只重建卡片。在 Jev 系列之前新增「SparkDesk 系列」类别；三款模型各自独立成页，没有总览页，所以类别标题不放链接。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spark_data import SITE, DATE, SLUGS, PRICE, MODELS  # noqa: E402
from spark_layout import logo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
LOGO = logo(cls='', size=26)

# slug -> (中文名, 中文简介, 中文标签, 英文名, 英文简介, 英文标签)
CARDS = {
    'sparkdesk-v3.5': ('SparkDesk-v3.5 API', '讯飞星火 Max 档（接口版本 v3.5），多轮对话、知识问答、逻辑推理和代码理解，输入输出同价。', ['星火 Max', '对话问答', '并发不限'],
                       'SparkDesk-v3.5 API', 'iFLYTEK Spark Max tier (API v3.5) for chat, Q&A, reasoning and code, same price for input and output.', ['Spark Max', 'Chat and Q&A', 'Unlimited RPM']),
    'sparkdesk-v3.1': ('SparkDesk-v3.1 API', '讯飞星火 Pro 档（接口版本 v3.1），对话、知识问答、数学解题和文案改写，输入输出同价。', ['星火 Pro', '对话问答', '并发不限'],
                       'SparkDesk-v3.1 API', 'iFLYTEK Spark Pro tier (API v3.1) for chat, Q&A, math and copy rewriting, same price for input and output.', ['Spark Pro', 'Chat and Q&A', 'Unlimited RPM']),
    'sparkdesk-v2.1': ('SparkDesk-v2.1 API', '讯飞星火早期的 2.x 版本（接口版本 v2.1），三款里单价最低，适合存量业务沿用。', ['旧版', '最低单价', '并发不限'],
                       'SparkDesk-v2.1 API', 'iFLYTEK Spark early 2.x release (API v2.1), the lowest price of the three, a fit for existing workloads.', ['Legacy', 'Lowest price', 'Unlimited RPM']),
}
ORDER = ['sparkdesk-v3.5', 'sparkdesk-v3.1', 'sparkdesk-v2.1']
CAT = {'zh': ('SparkDesk 系列', '查看专题 →', '/ 1M 输入', '科大讯飞'),
       'en': ('SparkDesk models', 'View guide →', '/ 1M input', 'iFLYTEK')}


def card(lang, slug):
    c = CARDS[slug]
    name, desc, tags = (c[0], c[1], c[2]) if lang == 'zh' else (c[3], c[4], c[5])
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#f2f7ff;border:1px solid #bcd5ff" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{name}</a></h3>
              <span class="af-model-cat">{CAT[lang][3]} · {MODELS[slug]['id']}</span>
            </div>
          </div>
          <p>{desc}</p>
          <ul class="af-tags">{tg}
          </ul>
          <div class="af-model-foot">
            <span><strong>${PRICE[slug][0]}</strong> {CAT[lang][2]}</span>
            <span class="af-model-go" aria-hidden="true">{CAT[lang][1]}</span>
          </div>
        </li>
'''


def hub(lang):
    p = os.path.join(ROOT, lang, 'models', 'index.html')
    s = io.open(p, encoding='utf-8').read()
    o = s
    name = CAT[lang][0]
    cards = ''.join(card(lang, x) for x in ORDER)
    if '<!-- SparkDesk -->' in s:
        s = re.sub(r'(<!-- SparkDesk -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /SparkDesk -->)',
                   lambda m: m.group(1) + cards + m.group(2), s, flags=re.S)
    else:
        block = (f'      <h3 class="af-section-head" id="cat-sparkdesk" style="font-size:16px;margin:24px 0 12px">{name}</h3>{NL}'
                 f'      <!-- SparkDesk -->{NL}      <ul class="af-models">{NL}{cards}      </ul>{NL}      <!-- /SparkDesk -->{NL}{NL}')
        assert '      <!-- Jev -->\n' in s
        s = s.replace('      <!-- Jev -->\n', block + '      <!-- Jev -->\n', 1)
        s = re.sub(r'(<li><a href="#cat-glm">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-sparkdesk">{name}</a></li>', s, count=1)
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
