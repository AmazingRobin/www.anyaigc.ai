import re,json
from pathlib import Path
D={'qwen3.5-plus':32,'qwen3.8-max':59,'qwen3.5-397b-a17b':32,'qwen3.8-max-0902':32,'qwen3.5-122b-a10b':32,'qwen3.7-max':32,'qwen3-vl-plus':32,'qwen3.5-27b':32,'qwen-flash':32,'qwen3.8-omni-flash':32,'qwen-plus':32,'qwen3.5-plus-2026-02-15':32,'qwen3.5-35b-a3b':32,'qwen-plus-2025-12-01':32,'qwen-max':32,'qwq-32b':32,'qwen-plus-character':32}
for lang in ('zh','en'):
 for p in [x for x in (Path(lang)/'models').glob('*.html') if x.stem=='qwq-32b' or x.stem.startswith('qwen')]:
  s=p.read_text(encoding='utf8'); slug=p.stem; zh=lang=='zh'; pct=D.get(slug)
  if slug=='qwen':
   # Overview: communicate the maximum verified saving across its model table.
   pct=59
  if pct and 'q-save' not in s:
   label=(f'比千问官方便宜 {pct}%' if zh else f'{pct}% below official Qwen pricing')
   s=s.replace('<ul class="q-facts">','<ul class="q-facts"><li class="q-save">'+label+'</li>',1)
   note=(f'最低分组价格相对千问官方同一档按量价便宜 {pct}%。' if zh else f'The lowest available group is {pct}% below the matching official Qwen usage rate.')
   s=s.replace('<p class="q-note">', '<p class="q-note q-save-note">'+note+' ',1)
   # add per-table model group marker for model pages; overview already has many groups, add concise marker to every group heading
   if slug=='qwen':
    s=s.replace('<tr class="q-group"><th colspan="3">', '<tr class="q-group"><th colspan="3">')
   p.write_text(s,encoding='utf8',newline='\n')
# add reusable styling
css=Path('assets/models/qwen.css'); c=css.read_text(encoding='utf8'); c += '\n.q-save{color:#315ef5!important;font-weight:700}.q-save-note{color:#315ef5!important;font-weight:600}\n'; css.write_text(c,encoding='utf8',newline='\n')
