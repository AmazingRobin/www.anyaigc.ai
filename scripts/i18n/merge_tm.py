# 把已完成系列的翻译记忆库合并成一份（后面的系列覆盖前面的同键条目），写到 drafts/i18n/<目标系列>/tm-<lang>.json。
# 用法：python scripts/i18n/merge_tm.py <目标系列> <来源系列>...
import io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dst, srcs = sys.argv[1], sys.argv[2:]
for lang in ('ja', 'ko', 'es', 'de'):
    merged = {}
    for s in srcs:
        p = os.path.join(ROOT, 'drafts', 'i18n', s, f'tm-{lang}.json')
        if os.path.exists(p):
            merged.update(json.load(io.open(p, encoding='utf-8')))
    os.makedirs(os.path.join(ROOT, 'drafts', 'i18n', dst), exist_ok=True)
    io.open(os.path.join(ROOT, 'drafts', 'i18n', dst, f'tm-{lang}.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(merged, ensure_ascii=False, indent=1))
    print(dst, lang, 'memory entries', len(merged))
