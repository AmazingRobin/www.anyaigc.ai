"""Register the Doubao Seed guides in both model hubs and the sitemap."""
import json
import re
from doubao_seed_pages import (
    ROOT, SITE, DATE, name, e, logo, tr,
    MODELS, COPY, SLUGS, SNAPSHOT_IDS, LATEST,
)

def card(lang, slug):
    c = COPY[slug][lang]
    tags = [c['tagline'], 'Chat Completions', tr(lang, '对公 · 专票', 'Bank transfer · VAT')]
    return f'''        <li class="af-model">
          <div class="af-model-head"><span class="af-model-logo db-lobe" style="background:#fff;border:1px solid #e1e6ec" aria-hidden="true">{logo(26)}</span><div><h3><a href="/{lang}/models/{slug}">{e(name(slug))} API</a></h3><span class="af-model-cat">{tr(lang, '字节跳动', 'ByteDance')} · Doubao Seed</span></div></div>
          <p>{e(c['summary'])}</p>
          <ul class="af-tags">{''.join(f'<li>{e(t)}</li>' for t in tags)}</ul>
          <div class="af-model-foot"><span><strong>${MODELS[slug]['rates'][0]['input']}</strong> / 1M {tr(lang, '输入起', 'input from')}</span><span class="af-model-go">{tr(lang, '查看专题 →', 'View guide →')}</span></div>
        </li>
'''

def hub(lang):
    path = ROOT / lang / 'models/index.html'
    source = path.read_text(encoding='utf-8')
    title = tr(lang, '豆包 Doubao Seed 对话模型', 'Doubao Seed chat models')
    block = f'''      <!-- Doubao Seed -->
      <h3 class="af-section-head" id="cat-doubao-seed" style="font-size:16px;margin:24px 0 12px">{title}</h3>
      <ul class="af-models">
{''.join(card(lang, s) for s in SLUGS)}      </ul>
      <!-- /Doubao Seed -->
'''
    if '<!-- Doubao Seed -->' in source:
        source = re.sub(r'      <!-- Doubao Seed -->.*?      <!-- /Doubao Seed -->\n', lambda _: block, source, flags=re.S)
    else:
        anchor = '<h3 class="af-section-head" id="cat-seedream"'
        assert anchor in source
        source = source.replace(anchor, '\n' + block + '\n      ' + anchor, 1)
        anchor = '<li><a href="#cat-seedream">'
        assert anchor in source
        source = source.replace(anchor, f'<li><a href="#cat-doubao-seed">{title}</a></li>\n        ' + anchor, 1)
    match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', source, re.S)
    graph = json.loads(match[1])
    for node in graph.get('@graph', [graph]):
        if node.get('@type') == 'ItemList':
            # Replace the whole family so dated snapshot URLs cannot survive
            # a later rerun after consolidation into canonical model pages.
            prefix = f'{SITE}/{lang}/models/doubao-seed-'
            items = [item for item in node['itemListElement']
                     if not item.get('url', '').startswith(prefix)]
            for slug in SLUGS:
                url = f'{SITE}/{lang}/models/{slug}'
                items.append({'@type': 'ListItem', 'name': name(slug) + ' API', 'url': url})
            for position, item in enumerate(items, 1):
                item['position'] = position
            node['itemListElement'] = items
            node['numberOfItems'] = len(items)
        elif node.get('@type') == 'CollectionPage':
            node['dateModified'] = DATE
    source = source[:match.start(1)] + json.dumps(graph, ensure_ascii=False, indent=2) + source[match.end(1):]
    path.write_text(source, encoding='utf-8', newline='\n')

def sitemap():
    path = ROOT / 'sitemap.xml'
    source = path.read_text(encoding='utf-8')
    # Remove both the old snapshot URLs and any prior canonical registrations.
    # Keep every unrelated XML block byte-for-byte as it was.
    family_loc = re.compile(r'<loc>' + re.escape(SITE) + r'/(?:zh|en)/models/doubao-seed-[^<]*</loc>')
    source = re.sub(r'  <url>.*?</url>\r?\n?',
                    lambda match: '' if family_loc.search(match[0]) else match[0],
                    source, flags=re.S)
    additions = ''
    for slug in SLUGS:
        for lang in ('zh', 'en'):
            url = f'{SITE}/{lang}/models/{slug}'
            additions += f'''  <url>
    <loc>{url}</loc>
    <lastmod>{DATE}</lastmod>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{slug}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{slug}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{slug}"/>
  </url>
'''
    source = source.replace('</urlset>', additions + '</urlset>')
    source = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+', lambda m: m[1] + DATE, source)
    path.write_text(source, encoding='utf-8', newline='\n')

if __name__ == '__main__':
    for lang in ('zh', 'en'):
        hub(lang)
    sitemap()
    print(f'Registered {len(SLUGS)} Doubao Seed models in both hubs and sitemap.')
