# 把 GPT Image 系列专题注册到专题首页（zh/en models/index.html）和 sitemap.xml：python scripts/gpt_image_register.py
# 重复运行结果不变：已注册就跳过。在专题首页的 GPT 系列之后新增「GPT Image 系列」类别（总览页由类别标题链接，不单独放卡片）。
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gpt_image_data import SITE, DATE, SLUGS, TOKEN, CALL, cny  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
LOGO_D = re.search(r' d="([^"]+)"', io.open(os.path.join(ROOT, 'assets/icons/openai.svg'), encoding='utf-8').read()).group(1)
LOGO = f'<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><path fill="#ffffff" fill-rule="evenodd" d="{LOGO_D}"></path></svg>'
T2, T25 = TOKEN['2']['out'], TOKEN['2.5']['out']

# slug -> (中文名, 中文简介, 中文标签, 中文价格, 英文名, 英文简介, 英文标签, 英文价格)
CARDS = {
    'gpt-image': ('GPT Image API（全系总览）', 'OpenAI GPT Image 全系价格对比与选型，含按张计费版，一个 Key 调用。', ['总览', '图像生成', '按张计费'], f'<strong>{cny("2")}</strong> / 张起',
                  'GPT Image API (overview)', 'Compare prices across the OpenAI GPT Image lineup, including per-image versions.', ['Overview', 'Image generation', 'Per image'], f'From <strong>${CALL["2"]}</strong> / image'),
    'gpt-image-2.5-sunburst': ('GPT Image 2.5 Sunburst API', 'OpenAI 编辑精度最高的图像模型，适合精修、商业海报和改图。', ['旗舰', '图像编辑', 'max 质量'], f'<strong>${T25}</strong> / 1M 图片输出',
                               'GPT Image 2.5 Sunburst API', "OpenAI's most precise image generation and editing model.", ['Flagship', 'Editing', 'max quality'], f'<strong>${T25}</strong> / 1M image output'),
    'gpt-image-2.5-flare': ('GPT Image 2.5 Flare API', 'OpenAI 速度最快的高质量图像模型，适合日常出图和批量生成。', ['速度最快', '批量出图', '图像生成'], f'<strong>${T25}</strong> / 1M 图片输出',
                            'GPT Image 2.5 Flare API', "OpenAI's fastest high-quality model for everyday image generation.", ['Fastest', 'High volume', 'Generation'], f'<strong>${T25}</strong> / 1M image output'),
    'gpt-image-2': ('GPT Image 2 API', 'ChatGPT 图像 2.0 背后的模型，按 token 计费单价全系最低。', ['文字渲染', '写实', '约 0.8 折'], f'<strong>${T2}</strong> / 1M 图片输出',
                    'GPT Image 2 API', 'The model behind ChatGPT Images 2.0, the lowest token rates in the family.', ['Text rendering', 'Photoreal', '92% off'], f'<strong>${T2}</strong> / 1M image output'),
}
CAT = {'zh': ('GPT Image 系列', '全系总览与价格对比', '查看专题 →'), 'en': ('GPT Image models', 'overview and price comparison', 'View guide →')}


def card(lang, slug):
    c = CARDS[slug]
    name, desc, tags, price = (c[0], c[1], c[2], c[3]) if lang == 'zh' else (c[4], c[5], c[6], c[7])
    tg = ''.join(f'{NL}            <li>{t}</li>' for t in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#000;border:1px solid #000" aria-hidden="true">{LOGO}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{name}</a></h3>
              <span class="af-model-cat">OpenAI · {slug}</span>
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
    if '<!-- GPT Image -->' in s:
        # 已注册：只重建卡片列表（价格可能变了）
        new = re.sub(r'(<!-- GPT Image -->\n      <ul class="af-models">\n).*?(      </ul>\n      <!-- /GPT Image -->)',
                     lambda m: m.group(1) + ''.join(card(lang, x) for x in SLUGS[1:]) + m.group(2), s, flags=re.S)
        # JSON-LD ItemList：去掉已下线的 -c 页面，重排序号
        m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', new, re.S)
        g = json.loads(m.group(1))
        for n in (g['@graph'] if '@graph' in g else [g]):
            if n.get('@type') == 'ItemList':
                items = [x for x in n['itemListElement'] if not re.search(r'/models/gpt-image-[\d.]+-?\w*-c$', x['url'])]
                for i, x in enumerate(items):
                    x['position'] = i + 1
                n['itemListElement'], n['numberOfItems'] = items, len(items)
        new = new[:m.start(1)] + json.dumps(g, ensure_ascii=False, indent=2) + new[m.end(1):]
        if new != s:
            io.open(p, 'w', encoding='utf-8', newline=NL).write(new)
        return new != s
    name, more, _ = CAT[lang]
    block = (f'{NL}      <h3 class="af-section-head" id="cat-gpt-image" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/gpt-image">'
             f'<span class="af-cat-name">{name}</span><span class="af-cat-more">{more} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>{NL}'
             f'      <!-- GPT Image -->{NL}      <ul class="af-models">{NL}' + ''.join(card(lang, x) for x in SLUGS[1:]) + f'      </ul>{NL}      <!-- /GPT Image -->{NL}')
    s = s.replace('      <!-- /GPT -->\n', '      <!-- /GPT -->\n' + block, 1)
    s = s.replace('<li><a href="#cat-gpt">', f'<li><a href="#cat-gpt">', 1)
    s = re.sub(r'(<li><a href="#cat-gpt">[^<]*</a></li>)', lambda m: m.group(1) + f'{NL}        <li><a href="#cat-gpt-image">{name}</a></li>', s, count=1)
    # JSON-LD ItemList：追加到末尾并更新数量
    m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
    g = json.loads(m.group(1))
    nodes = g['@graph'] if '@graph' in g else [g]
    for n in nodes:
        if n.get('@type') == 'ItemList':
            items = n['itemListElement']
            for x in SLUGS:
                items.append({'@type': 'ListItem', 'position': len(items) + 1,
                              'name': CARDS[x][0] if lang == 'zh' else CARDS[x][4], 'url': f'{SITE}/{lang}/models/{x}'})
            n['numberOfItems'] = len(items)
    s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False, indent=2) + s[m.end(1):]
    io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
    return True


def sitemap():
    p = os.path.join(ROOT, 'sitemap.xml')
    s = io.open(p, encoding='utf-8').read()
    o = s
    # 去掉已下线的 -c 页面
    for old in ('gpt-image-2-c', 'gpt-image-2.5-sunburst-c', 'gpt-image-2.5-flare-c'):
        s = re.sub(r'  <url>\n    <loc>[^<]*/models/' + re.escape(old) + r'</loc>\n(?:    .*\n)*?  </url>\n', '', s)
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
    if add or s != o:
        s = s.replace('</urlset>', add + '</urlset>')
        # 专题首页 lastmod 同步
        s = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+', lambda m: m.group(1) + DATE, s)
        io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
    return s != o


if __name__ == '__main__':
    print('hub zh:', hub('zh'), 'hub en:', hub('en'), 'sitemap:', sitemap())
