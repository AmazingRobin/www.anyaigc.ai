# 把按旧编号写的译文，按「角色 + 原文」重新映射到当前 union.json 的编号上。
# 用途：翻译源变了（去掉残缺日期、改了改写规则），union 的编号错开，但译文本身还能用的时候。
# 用法：python scripts/i18n/remap.py <series> <旧译文目录> [--old-no-typo]
#   旧译文目录里是 <lang>-<NN>.json（旧编号）；--old-no-typo 表示旧编号是在没有 TYPO_RULES 的翻译源上生成的。
# 输出：out/<lang>-remap.json（新编号，只含原文没变的条目）；原文变了的条目不迁移，留给重新翻译。
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch as BT
import overseas as O

ROOT = BT.ROOT
LANGS = ('ja', 'ko', 'es', 'de')


def old_union(slugs, no_typo):
    saved = O.TYPO_RULES
    if no_typo:
        O.TYPO_RULES = []
    try:
        order, seen = [], {}
        for slug in slugs:
            for uid, text, role in BT.page_units(slug):
                k = (role, text)
                if k not in seen:
                    seen[k] = f'k{len(order)}'
                    order.append((seen[k], role, text))
        return order
    finally:
        O.TYPO_RULES = saved


def main():
    series, old_dir = sys.argv[1], sys.argv[2]
    d = os.path.join(BT.DRAFT, series)
    slugs = [s for s in open(os.path.join(d, 'slugs.txt'), encoding='utf-8').read().split()]
    old = old_union(slugs, '--old-no-typo' in sys.argv)
    new = {(i['role'], i['text']): i['id'] for i in json.load(io.open(os.path.join(d, 'union.json'), encoding='utf-8'))}
    print(f'旧 union {len(old)} 条，新 union {len(new)} 条')
    for lang in LANGS:
        tr = {}
        for f in sorted(glob.glob(os.path.join(old_dir, f'{lang}-0?.json'))):
            for it in json.load(io.open(f, encoding='utf-8')):
                tr[it['id']] = it['text']
        out, same, changed, none = [], 0, 0, 0
        for oid, role, text in old:
            if oid not in tr:
                none += 1
                continue
            nk = (role, text)
            if nk in new:
                out.append({'id': new[nk], 'text': tr[oid]})
                same += 1
            else:
                changed += 1
        seen_ids, uniq = set(), []
        for it in out:
            if it['id'] not in seen_ids:
                seen_ids.add(it['id'])
                uniq.append(it)
        io.open(os.path.join(d, 'out', f'{lang}-remap.json'), 'w', encoding='utf-8', newline='\n').write(
            json.dumps(uniq, ensure_ascii=False, indent=1))
        print(f'{lang}: 迁移 {len(uniq)} 条；原文已变（重译）{changed}；旧译文缺失 {none}')


if __name__ == '__main__':
    main()
