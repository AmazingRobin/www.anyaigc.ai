"""Register Seedance pages in both model hubs and the sitemap; safe to rerun."""
import json
import re
from pathlib import Path
from seedance_data import ROOT, SITE, DATE, SLUGS, MODELS
from seedance_pages import logo


def hub(lang):
    p = Path(ROOT) / lang / 'models' / 'index.html'
    s = p.read_text(encoding='utf-8')
    zh = lang == 'zh'
    cards = []
    for slug, m in MODELS.items():
        tags = ['视频生成', '异步任务', '并发不限'] if zh else ['Video generation', 'Async tasks', 'Unlimited concurrency']
        cards.append(f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo sd-lobe" style="background:#ffffff;border:1px solid #e1e6ec" aria-hidden="true">{logo(26)}</span>
            <div><h3><a href="/{lang}/models/{slug}">{m['name']} API</a></h3><span class="af-model-cat">ByteDance · {m['id']}</span></div>
          </div>
          <p>{m['desc_zh' if zh else 'desc_en']}</p>
          <ul class="af-tags">{''.join('<li>' + x + '</li>' for x in tags)}</ul>
          <div class="af-model-foot"><span>{'最低' if zh else 'From'} <strong>${m['min']}</strong> / 1M tokens</span><span class="af-model-go" aria-hidden="true">{'查看专题' if zh else 'View guide'} →</span></div>
        </li>
''')
    category = 'Seedance 视频系列' if zh else 'Seedance video models'
    block = f'''      <h3 class="af-section-head" id="cat-seedance" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/seedance"><span class="af-cat-name">{category}</span><span class="af-cat-more">{'全系总览与价格对比' if zh else 'Overview and pricing'} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>
      <!-- Seedance -->
      <ul class="af-models">
{''.join(cards)}      </ul>
      <!-- /Seedance -->

'''
    if 'id="cat-seedance"' in s:
        s = re.sub(r'      <h3 class="af-section-head" id="cat-seedance".*?<!-- /Seedance -->\n\n', lambda _: block, s, flags=re.S)
    else:
        anchor = '      <h3 class="af-section-head" id="cat-muse"'
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
        anchor = '        <li><a href="#cat-muse">'
        s = s.replace(anchor, f'        <li><a href="#cat-seedance">{category}</a></li>\n' + anchor, 1)
    match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', s, re.S)
    graph = json.loads(match.group(1))
    for node in graph['@graph']:
        if node.get('@type') == 'ItemList':
            items = node['itemListElement']
            items = [x for x in items if x['url'].rsplit('/', 1)[-1] not in SLUGS]
            for slug in SLUGS:
                items.append({'@type': 'ListItem', 'position': len(items) + 1,
                              'name': ('Seedance API（全系总览）' if zh else 'Seedance API (overview)') if slug == 'seedance' else MODELS[slug]['name'] + ' API',
                              'url': f'{SITE}/{lang}/models/{slug}'})
            node['itemListElement'] = items
            node['numberOfItems'] = len(items)
        if node.get('@type') == 'CollectionPage':
            node['dateModified'] = DATE
    s = s[:match.start(1)] + json.dumps(graph, ensure_ascii=False, indent=2) + s[match.end(1):]
    p.write_text(s, encoding='utf-8', newline='\n')


def sitemap():
    p = Path(ROOT) / 'sitemap.xml'
    s = p.read_text(encoding='utf-8')
    entries = []
    for slug in SLUGS:
        for lang in ('zh', 'en'):
            url = f'{SITE}/{lang}/models/{slug}'
            if f'<loc>{url}</loc>' in s:
                continue
            links = '\n'.join(f'    <xhtml:link rel="alternate" hreflang="{hl}" href="{SITE}/{l}/models/{slug}"/>' for hl, l in [('zh-CN', 'zh'), ('en', 'en'), ('x-default', 'en')])
            entries.append(f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{DATE}</lastmod>\n{links}\n  </url>\n')
    s = s.replace('</urlset>', ''.join(entries) + '</urlset>')
    s = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+', lambda m: m.group(1) + DATE, s)
    p.write_text(s, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    hub('zh')
    hub('en')
    sitemap()
    print('registered Seedance pages')
