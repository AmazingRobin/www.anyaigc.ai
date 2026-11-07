import re
from pathlib import Path
DISCOUNT={'qwen3.5-plus':32,'qwen3.8-max':59,'qwen3.5-397b-a17b':32,'qwen3.8-max-0902':32,'qwen3.5-122b-a10b':32,'qwen3.7-max':32,'qwen3-vl-plus':32,'qwen3.5-27b':32,'qwen-flash':32,'qwen3.8-omni-flash':32,'qwen-plus':32,'qwen3.5-plus-2026-02-15':32,'qwen3.5-35b-a3b':32,'qwen-plus-2025-12-01':32,'qwen-max':32,'qwq-32b':32,'qwen-plus-character':32}
for lang in ('zh','en'):
    zh=lang=='zh'
    for p in [x for x in (Path(lang)/'models').glob('*.html') if x.stem=='qwq-32b' or x.stem.startswith('qwen')]:
        s=p.read_text(encoding='utf8')
        # Fourth column in the header.
        s=s.replace('<th>单价（USD）</th></tr>', '<th>单价（USD）</th><th>优惠</th></tr>')
        s=s.replace('<th>Price (USD)</th></tr>', '<th>Price (USD)</th><th>Savings</th></tr>')
        # Process each model block separately: remove full-width savings row and add one vertically merged cell.
        def tbody(match):
            b=match.group(0)
            b=re.sub(r'<tr class="q-save-row">.*?</tr>', '', b, flags=re.S)
            b=b.replace('<th colspan="3">', '<th colspan="4">')
            model=re.search(r'<code>([^<]+)</code>', b)
            if not model:
                return b
            key=model.group(1)
            # Count billed operation rows (input, output, and optional cache hit).
            count=len(re.findall(r'<tr><th>(?:输入 tokens|Input tokens|输出 tokens|Output tokens|缓存命中|Cache hit)</th>', b))
            label=(f'比千问官方便宜 {DISCOUNT[key]}%' if zh else f'{DISCOUNT[key]}% below official') if key in DISCOUNT else ('—' if zh else '—')
            target=r'(<tr><th>(?:输入 tokens|Input tokens)</th><td><code>'+re.escape(key)+r'</code></td><td>.*?</td>)(</tr>)'
            b=re.sub(target, lambda m:m.group(1)+f'<td class="q-discount" rowspan="{count}">{label}</td>'+m.group(2), b, count=1, flags=re.S)
            return b
        s=re.sub(r'<tbody>.*?</tbody>', tbody, s, flags=re.S)
        # Remove the price-block discount paragraph; the data now lives in the table column.
        s=re.sub(r'<p class="q-note q-save-note">.*?</p>', '', s, count=1, flags=re.S)
        p.write_text(s,encoding='utf8',newline='\n')
