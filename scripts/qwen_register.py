import json,re
from pathlib import Path
from qwen_pages import R,SITE,DATE,M,SL,logo
CARDS={x[0]:x for x in M}
def card(lang,s):
 a,n,i,o,c=CARDS[s]; zh=lang=='zh'; return f'<li class="af-model"><div class="af-model-head"><span class="af-model-logo" style="background:#eef2ff;border:1px solid #c7d2fe" aria-hidden="true">{logo(26)}</span><div><h3><a href="/{lang}/models/{a}">{n} API</a></h3><span class="af-model-cat">Qwen · {a}</span></div></div><p>{"千问对话模型，OpenAI 兼容 Chat Completions，并发不限。" if zh else "Qwen conversation model on OpenAI-compatible Chat Completions, with no concurrency cap."}</p><ul class="af-tags"><li>{"对话" if zh else "Conversation"}</li><li>Chat Completions</li><li>{"对公 · 专票" if zh else "Contracts · invoices"}</li></ul><div class="af-model-foot"><span><strong>${i}</strong> / 1M {"输入" if zh else "input"}</span><span class="af-model-go">{"查看专题 →" if zh else "View guide →"}</span></div></li>'
def hub(lang):
 p=R/lang/'models/index.html'; s=p.read_text(encoding='utf8'); zh=lang=='zh'; cards=''.join(card(lang,x[0]) for x in M); h=f'<h3 class="af-section-head" id="cat-qwen" style="font-size:16px;margin:24px 0 12px"><a class="af-cat-link" href="/{lang}/models/qwen"><span class="af-cat-name">{"千问 Qwen 系列" if zh else "Qwen models"}</span><span class="af-cat-more">{"全系总览与价格对比" if zh else "overview and price comparison"} <span class="af-cat-arrow">→</span></span></a></h3><!-- Qwen --><ul class="af-models">{cards}</ul><!-- /Qwen -->'
 s=re.sub(r'<h3 class="af-section-head" id="cat-qwen".*?<!-- /Qwen -->',h,s,flags=re.S) if '<!-- Qwen -->' in s else s.replace('<h3 class="af-section-head" id="cat-grok-text"',h+'<h3 class="af-section-head" id="cat-grok-text"',1)
 if '#cat-qwen' not in s: s=s.replace('<li><a href="#cat-grok-text">','<li><a href="#cat-qwen">'+('千问 Qwen 系列' if zh else 'Qwen models')+'</a></li><li><a href="#cat-grok-text">',1)
 m=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S); g=json.loads(m.group(1)); il=next(x for x in g['@graph'] if x.get('@type')=='ItemList'); have={x['url'] for x in il['itemListElement']}
 for s0 in SL:
  u=f'{SITE}/{lang}/models/{s0}'
  if u not in have: il['itemListElement'].append({'@type':'ListItem','position':len(il['itemListElement'])+1,'name':('Qwen API overview' if s0=='qwen' else CARDS[s0][1]+' API'),'url':u})
 il['numberOfItems']=len(il['itemListElement']); s=s[:m.start(1)]+json.dumps(g,ensure_ascii=False,indent=2)+s[m.end(1):]; p.write_text(s,encoding='utf8',newline='\n')
def sitemap():
 p=R/'sitemap.xml'; s=p.read_text(encoding='utf8'); add=''
 for a in SL:
  for lang in ('zh','en'):
   u=f'{SITE}/{lang}/models/{a}'
   if f'<loc>{u}</loc>' not in s:add+=f'<url><loc>{u}</loc><lastmod>{DATE}</lastmod><xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{a}"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{a}"/><xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{a}"/></url>'
 s=s.replace('</urlset>',add+'</urlset>'); s=re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+',r'\g<1>'+DATE,s); p.write_text(s,encoding='utf8',newline='\n')
for l in ('zh','en'):hub(l)
sitemap()
