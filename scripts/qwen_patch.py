import json,re
from pathlib import Path
for lang in ('zh','en'):
 for p in [x for x in (Path(lang)/'models').glob('*.html') if x.stem == 'qwq-32b' or x.stem.startswith('qwen')]:
  s=p.read_text(encoding='utf8')
  qs=[('新用户有免费试用额度吗？','有。新用户注册即送 200 万 tokens 试用额度。'),('余额可以退款吗？','可以。未使用余额可退款，不收手续费。'),('会不会用低配模型冒充？我的数据安全吗？','请求走官方模型渠道，除法律法规要求外不做持久化存储，也不用于训练。'),('企业可以对公转账和签合同吗？','可以。支持企业对公转账充值、签订服务合同，并提供专属客服和技术对接。')] if lang=='zh' else [('Is there free trial credit for new users?','Yes. New accounts get 2 million tokens of trial credit.'),('Can I get a refund on my balance?','Yes. Unused balance can be refunded with no fee.'),('Are these official models and is my data safe?','Requests use official model channels. Prompts and outputs are not persistently stored or used for training unless required by law.'),('Can my company pay by bank transfer and sign a contract?','Yes. Companies can pay by bank transfer, sign a service agreement, and receive dedicated support and technical contact.')]
  m=re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S); g=json.loads(m.group(1)); faq=next(x for x in g['@graph'] if x.get('@type')=='FAQPage'); existing={x['name'] for x in faq['mainEntity']}; ins=''
  for q,a in qs:
   if q not in existing:
    faq['mainEntity'].append({'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}}); ins+=f'<details><summary><h3>{q}</h3></summary><div class="q-ans"><p>{a}</p></div></details>'
  if ins:
   s=s.replace('</div></div></section><section class="q-final"',ins+'</div></div></section><section class="q-final"',1); s=s[:m.start(1)]+json.dumps(g,ensure_ascii=False)+s[m.end(1):]; p.write_text(s,encoding='utf8',newline='\n')
