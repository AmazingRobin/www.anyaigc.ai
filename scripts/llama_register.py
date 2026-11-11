"""Register the Llama overview and 12 model guides, idempotently."""
import json
import re
from html import escape
from pathlib import Path

from llama_data import BY_ID, DATE, MODELS, SLUGS
from llama_pages import deal, mark

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://www.anyaigc.ai'


def hub(lang):
    zh = lang == 'zh'
    name = 'Llama 系列' if zh else 'Llama models'
    cards = ''
    for model in MODELS:
        cards += f'''        <li class="af-model">
          <div class="af-model-head"><span class="af-model-logo ll-lobe" style="background:#ffffff;border:1px solid #e6e6e6" aria-hidden="true">{mark(26,cls='ll-card-mark')}</span>
            <div><h3><a href="/{lang}/models/{model['id']}">{model['name']} API</a></h3><span class="af-model-cat">Meta Llama · Ollama · {'文本 / 对话' if zh else 'Text / chat'}</span></div>
          </div>
          <p>{escape(model['desc_'+lang])}</p>
          <ul class="af-tags"><li>{deal(lang,model)}</li><li>{'并发不限' if zh else 'Unlimited concurrency'}</li><li>OpenAI {'兼容' if zh else 'compatible'}</li></ul>
          <div class="af-model-foot"><span><strong>${model['input']}</strong> / {'百万输入 tokens' if zh else '1M input tokens'}</span><span class="af-model-go" aria-hidden="true">{'查看专题' if zh else 'View guide'} →</span></div>
        </li>
'''
    block = f'''      <!-- Llama -->
      <h3 class="af-section-head" id="cat-llama" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/llama"><span class="af-cat-name">{name}</span><span class="af-cat-more">{'部分型号 68 折 · 全系总览' if zh else 'Save 32% on selected models · overview'} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>
      <ul class="af-models">
{cards}      </ul>
      <!-- /Llama -->
'''
    path = ROOT/lang/'models/index.html'
    source = path.read_text(encoding='utf-8')
    if '<!-- Llama -->' in source:
        source = re.sub(r'      <!-- Llama -->\n.*?      <!-- /Llama -->\n',lambda _:block,source,flags=re.S)
    else:
        anchor = '      <!-- MiniMax -->'
        assert anchor in source
        source = source.replace(anchor,block+'\n'+anchor,1)
    if 'href="#cat-llama"' not in source:
        source = source.replace('<li><a href="#cat-minimax">',f'<li><a href="#cat-llama">{name}</a></li>\n        <li><a href="#cat-minimax">',1)
    match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',source,re.S)
    graph = json.loads(match.group(1))
    urls = {f'{SITE}/{lang}/models/{slug}' for slug in SLUGS}
    for node in graph['@graph']:
        if node['@type'] == 'ItemList':
            items = [i for i in node['itemListElement'] if i['url'] not in urls]
            items += [{'@type':'ListItem','name':(BY_ID[slug]['name'] if slug in BY_ID else 'Llama')+' API','url':f'{SITE}/{lang}/models/{slug}'} for slug in SLUGS]
            for position,item in enumerate(items,1):
                item['position'] = position
            node['itemListElement'] = items
            node['numberOfItems'] = len(items)
        if node['@type'] == 'CollectionPage':
            node['dateModified'] = DATE
    source = source[:match.start(1)]+json.dumps(graph,ensure_ascii=False,indent=2)+source[match.end(1):]
    path.write_text(source,encoding='utf-8',newline='\n')


def sitemap():
    path = ROOT/'sitemap.xml'
    source = path.read_text(encoding='utf-8')
    for lang in ('zh','en'):
        for slug in SLUGS:
            url = f'{SITE}/{lang}/models/{slug}'
            entry = f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{DATE}</lastmod>\n'
            for code,folder in [('zh-CN','zh'),('en','en'),('x-default','en')]:
                entry += f'    <xhtml:link rel="alternate" hreflang="{code}" href="{SITE}/{folder}/models/{slug}"/>\n'
            entry += '  </url>\n'
            if '<loc>'+url+'</loc>' in source:
                source = re.sub(r'  <url>\s*<loc>'+re.escape(url)+r'</loc>.*?</url>\n?',lambda _:entry,source,flags=re.S)
            else:
                source = source.replace('</urlset>',entry+'</urlset>')
    source = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+DATE,source)
    path.write_text(source,encoding='utf-8',newline='\n')


if __name__ == '__main__':
    for lang in ('zh','en'):
        hub(lang)
    sitemap()
    print('Registered Llama: 13 guides per language.')
