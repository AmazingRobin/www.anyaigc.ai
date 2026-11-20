# 复核补丁校验：补丁文件 out/<lang>-rev-<seg>.json 只含被改动的条目 [{id,text}]。
# 把补丁叠在 out/<lang>-all.json 上，放进临时系列目录，复用 batch.validate，只报告本段 id 的错误。
# 用法：python scripts/i18n/check_patch.py <series> <lang> <seg> <start> <end>
#   start/end 是 union.json 的下标范围 [start, end)；补丁里的 id 必须落在这个范围内。
import io, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch as BT

series, lang, seg, a, b = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
d = os.path.join(BT.DRAFT, series)
union = json.load(io.open(os.path.join(d, 'union.json'), encoding='utf-8'))
ids = {u['id'] for u in union[a:b]}
base = {o['id']: o['text'] for o in json.load(io.open(os.path.join(d, 'out', f'{lang}-all.json'), encoding='utf-8'))}
pp = os.path.join(d, 'out', f'{lang}-rev-{seg}.json')
patch = json.load(io.open(pp, encoding='utf-8')) if os.path.exists(pp) else []
bad = [p['id'] for p in patch if p['id'] not in ids]
errs = []
if bad:
    errs.append(f'补丁里有不属于本段的 id: {bad[:8]}')
for p in patch:
    if p['id'] in ids:
        base[p['id']] = p['text']
tmp = f'_rv_{series}_{lang}_{seg}'
td = os.path.join(BT.DRAFT, tmp)
os.makedirs(os.path.join(td, 'out'), exist_ok=True)
json.dump(union, io.open(os.path.join(td, 'union.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump([{'id': u['id'], 'text': base[u['id']]} for u in union], io.open(os.path.join(td, 'out', f'{lang}-all.json'), 'w', encoding='utf-8'), ensure_ascii=False)
e, w = BT.validate(tmp, lang)
shutil.rmtree(td, ignore_errors=True)
mine = lambda s: any(f' {i}:' in s or s.endswith(f' {i}') for i in ids)
errs += [x for x in e if mine(x)]
warns = [x for x in w if mine(x)]
print(f'{lang} 段 {seg}: 补丁 {len(patch)} 条，错误 {len(errs)}，提醒 {len(warns)}')
for x in errs[:30]:
    print('ERROR', x)
for x in warns[:10]:
    print('WARN ', x)
sys.exit(1 if errs else 0)
