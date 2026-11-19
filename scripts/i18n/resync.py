# 英文页改动后（移动版块、改写文字），按「角色 + 原文」把已复核的译文重新映射到新的 union.json 编号上。
# 译文来源：<系列>/tm-<lang>.json（tm-save 存的、已复核的译文）。重映射后写 out/<lang>-all.json，缺的条目写 todo-resync-<lang>.json。
# 旧的 out/ 文件整体挪到 out_prev_<序号>/ 里保留，不删除。
# 用法：python scripts/i18n/resync.py <series>        （先 python scripts/i18n/batch.py prepare <series> <slug>... 生成新 union.json）
#       python scripts/i18n/resync.py <series> --dry-run
import glob
import io
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch as BT

LANGS = ('ja', 'ko', 'es', 'de')


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def main():
    series = sys.argv[1]
    dry = '--dry-run' in sys.argv
    d = os.path.join(BT.DRAFT, series)
    union = load(os.path.join(d, 'union.json'))
    out = os.path.join(d, 'out')
    if not dry:
        n = 1
        while os.path.exists(os.path.join(d, f'out_prev_{n}')):
            n += 1
        prev = os.path.join(d, f'out_prev_{n}')
        os.makedirs(prev)
        for f in glob.glob(os.path.join(out, '*.json')):
            shutil.move(f, os.path.join(prev, os.path.basename(f)))
    missing_all = {}
    for lang in LANGS:
        tm = load(os.path.join(d, f'tm-{lang}.json'))
        rows, miss = [], []
        for it in union:
            k = it['role'] + chr(31) + it['text']
            if k in tm:
                rows.append({'id': it['id'], 'text': tm[k]})
            else:
                miss.append(it)
        missing_all[lang] = miss
        print(f'{series}/{lang}: 命中 {len(rows)}/{len(union)}，缺 {len(miss)}')
        if not dry:
            io.open(os.path.join(out, f'{lang}-all.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(rows, ensure_ascii=False, indent=1))
            io.open(os.path.join(d, f'todo-resync-{lang}.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(miss, ensure_ascii=False, indent=1))
    ids = [sorted(i['id'] for i in m) for m in missing_all.values()]
    print('各语言缺失的条目一致:', all(x == ids[0] for x in ids))
    for it in missing_all['ja'][:8]:
        print('  缺:', it['id'], it['role'], '|', it['text'][:130])


if __name__ == '__main__':
    main()
