# 把各段复核补丁 out/<lang>-rev-*.json 合并进 out/<lang>-all.json（补丁覆盖同 id）；补丁文件移到 out_parts/ 保留。
# 用法：python scripts/i18n/merge_patches.py <series> <lang>
import glob, io, json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
series, lang = sys.argv[1], sys.argv[2]
d = os.path.join(ROOT, 'drafts', 'i18n', series, 'out')
ap = os.path.join(d, f'{lang}-all.json')
allv = json.load(io.open(ap, encoding='utf-8'))
idx = {o['id']: i for i, o in enumerate(allv)}
n = 0
files = sorted(glob.glob(os.path.join(d, f'{lang}-rev-*.json')))
for f in files:
    for p in json.load(io.open(f, encoding='utf-8')):
        if p['id'] in idx:
            allv[idx[p['id']]]['text'] = p['text']; n += 1
os.makedirs(os.path.join(d, '..', 'out_parts'), exist_ok=True)
json.dump(allv, io.open(ap, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
for f in files:
    shutil.move(f, os.path.join(d, '..', 'out_parts', os.path.basename(f)))
print(f'{series}/{lang}: 合并 {len(files)} 个补丁文件，覆盖 {n} 条')
