import json,re
from pathlib import Path
from qwen_media_data import IMG,VID,MODELS,SITE,DATE,MARKET,price_label
ROOT=Path(__file__).resolve().parent.parent

def card(lang,m):
    zh=lang=='zh'
    summary=m['summary'][not zh]
    cat=('图像' if zh else 'Image') if m['kind']=='image' else ('实时音视频' if zh else 'Real-time audio/video') if m['kind']=='realtime' else ('视频' if zh else 'Video')
    return f'''<li class="af-model">
  <div class="af-model-head"><span class="af-model-logo" style="background:#eef2ff;border:1px solid #c7d2fe" aria-hidden="true"><img src="/assets/icons/qwen.svg" width="26" height="26" alt=""></span><div><h3><a href="/{lang}/models/{m['slug']}">{m['name']} API</a></h3><span class="af-model-cat">Qwen · {cat}</span></div></div>
  <p>{summary}</p><ul class="af-tags"><li>{cat}</li><li>{'并发不限' if zh else 'No concurrency cap'}</li><li>{'对公 · 专票' if zh else 'Contracts · invoices'}</li></ul>
  <div class="af-model-foot"><span><strong>{price_label(m,lang)}</strong></span><span class="af-model-go">{'查看专题 →' if zh else 'View guide →'}</span></div>
</li>'''

def hub(lang):
    p=ROOT/lang/'models/index.html';s=p.read_text(encoding='utf-8')
    for cat,models,name in [('cat-qwen-image',IMG,'千问 Qwen 图像模型' if lang=='zh' else 'Qwen image models'),('cat-qwen-video',VID,'Qwen 视频与实时音视频' if lang=='zh' else 'Qwen video and real-time models')]:
        block=f'<h3 class="af-section-head" id="{cat}" style="font-size:16px;margin:24px 0 12px">{name}</h3><!-- {cat} --><ul class="af-models">'+ '\n'.join(card(lang,m) for m in models)+f'</ul><!-- /{cat} -->'
        pattern=r'<h3 class="af-section-head" id="'+cat+r'".*?<!-- /'+cat+r' -->'
        if re.search(pattern,s,re.S):s=re.sub(pattern,lambda _:block,s,count=1,flags=re.S)
        else:s=s.replace('<h3 class="af-section-head" id="cat-seedream"',block+'<h3 class="af-section-head" id="cat-seedream"',1)
        if f'href="#{cat}"' not in s:
            marker='<li><a href="#cat-qwen">'
            assert marker in s
            s=s.replace(marker,f'<li><a href="#{cat}">{name}</a></li>'+marker,1)
    match=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S);g=json.loads(match[1])
    items=next(x for x in g['@graph'] if x.get('@type')=='ItemList');by_url={x['url']:x for x in items['itemListElement']}
    for m in MODELS:
        u=f'{SITE}/{lang}/models/{m["slug"]}'
        if u in by_url:by_url[u]['name']=m['name']+' API'
        else:items['itemListElement'].append({'@type':'ListItem','name':m['name']+' API','url':u})
    for i,item in enumerate(items['itemListElement'],1):item['position']=i
    items['numberOfItems']=len(items['itemListElement'])
    for node in g['@graph']:
        if node.get('@type')=='CollectionPage':node['dateModified']=DATE
    s=s[:match.start(1)]+'\n'+json.dumps(g,ensure_ascii=False,indent=2)+'\n'+s[match.end(1):]
    p.write_text(s,encoding='utf-8',newline='\n')

def sitemap():
    p=ROOT/'sitemap.xml';s=p.read_text(encoding='utf-8')
    for slug in [m['slug'] for m in MODELS]+['']:
        modified='2026-11-09' if any(m['slug']==slug and m['kind']=='video' for m in MODELS) else DATE
        for lang in ['zh','en']:
            loc=f'{SITE}/{lang}/models/{slug}'
            pat=r'<url>\s*<loc>'+re.escape(loc)+r'</loc>.*?</url>'
            block=f'''<url>
    <loc>{loc}</loc><lastmod>{modified}</lastmod>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{slug}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{slug}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{slug}"/>
  </url>'''
            if re.search(pat,s,re.S):s=re.sub(pat,lambda _:block,s,count=1,flags=re.S)
            else:s=s.replace('</urlset>',block+'\n</urlset>')
    p.write_text(s,encoding='utf-8',newline='\n')

if __name__=='__main__':
    for lang in ('zh','en'): hub(lang)
    sitemap()
