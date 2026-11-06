"""Register Grok text models in both hubs and sitemap; safe to run repeatedly."""
import json
import re
from grok_text_pages import ROOT, logo, tr
from grok_text_data import SITE, DATE, HUB, SLUGS, MODELS


def hub(lang):
    path = ROOT / lang / 'models/index.html'
    s = path.read_text(encoding='utf-8')
    cat = tr(lang, 'Grok 文本 / 编程系列', 'Grok text & coding models')
    cards = []
    for slug, m in MODELS.items():
        cards.append(f'''        <li class="af-model">
          <div class="af-model-head"><span class="af-model-logo gt-lobe" style="background:#0a0a0a;border:1px solid #0a0a0a" aria-hidden="true">{logo('gt-card-mark','#ffffff')}</span><div><h3><a href="/{lang}/models/{slug}">{m['name']} API</a></h3><span class="af-model-cat">xAI · {slug}</span></div></div>
          <p>{m[lang][2]}{tr(lang,'，按 tokens 计费，所有用户默认并发不限。','. Token billing and unlimited concurrency for every user.')}</p>
          <ul class="af-tags"><li>{tr(lang,'文本 / 编程','Text / code')}</li><li>{tr(lang,'双接口','Two endpoints') if m['messages'] else 'Chat Completions'}</li><li>{tr(lang,'对公 · 专票','Contracts · invoices')}</li></ul>
          <div class="af-model-foot"><span><strong>${m['prices'][0]}</strong> / 1M {tr(lang,'输入','input')}</span><span class="af-model-go" aria-hidden="true">{tr(lang,'查看专题','View guide')} →</span></div>
        </li>''')
    block = f'''      <!-- Grok Text -->
      <h3 class="af-section-head" id="cat-grok-text" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/{HUB}"><span class="af-cat-name">{cat}</span><span class="af-cat-more">{tr(lang,'全系总览与价格对比','Overview and price comparison')} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>
      <ul class="af-models">
{chr(10).join(cards)}
      </ul>
      <!-- /Grok Text -->

'''
    if '<!-- Grok Text -->' in s:
        s = re.sub(r'      <!-- Grok Text -->.*?      <!-- /Grok Text -->\n\n',lambda _:block,s,flags=re.S)
    else:
        anchor = '      <!-- Jev -->'
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
        s = re.sub(r'(<li><a href="#cat-jev">)', f'<li><a href="#cat-grok-text">{cat}</a></li>\n        '+r'\1', s, count=1)
    match = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>',s,re.S)
    graph = json.loads(match[1])
    for n in graph['@graph']:
        if n['@type'] == 'ItemList':
            items = [i for i in n['itemListElement'] if i['url'] not in {f'{SITE}/{lang}/models/{x}' for x in SLUGS}]
            for slug in SLUGS:
                name = 'Grok 4.x API' if slug == HUB else MODELS[slug]['name']+' API'
                items.append({'@type':'ListItem','position':len(items)+1,'name':name,'url':f'{SITE}/{lang}/models/{slug}'})
            for i,item in enumerate(items):
                item['position'] = i+1
            n['itemListElement'], n['numberOfItems'] = items,len(items)
        if n['@type'] == 'CollectionPage':
            n['dateModified'] = DATE
    s = s[:match.start(1)] + json.dumps(graph,ensure_ascii=False,indent=2) + s[match.end(1):]
    path.write_text(s,encoding='utf-8',newline='\n')


def sitemap():
    path = ROOT/'sitemap.xml'
    s = path.read_text(encoding='utf-8')
    for slug in SLUGS:
        for lang in ('zh','en'):
            loc = f'{SITE}/{lang}/models/{slug}'
            if f'<loc>{loc}</loc>' in s:
                s = re.sub(r'(<loc>'+re.escape(loc)+r'</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+DATE,s)
                continue
            block = f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{DATE}</lastmod>\n'
            for hl, ln in [('zh-CN','zh'),('en','en'),('x-default','en')]:
                block += f'    <xhtml:link rel="alternate" hreflang="{hl}" href="{SITE}/{ln}/models/{slug}"/>\n'
            s = s.replace('</urlset>',block+'  </url>\n</urlset>')
    s = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+DATE,s)
    path.write_text(s,encoding='utf-8',newline='\n')


if __name__=='__main__':
    hub('zh')
    hub('en')
    sitemap()
    print('Registered nine bilingual Grok text guides.')
