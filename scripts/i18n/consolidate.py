# 把一种语言分散在 out/ 里的译文合并成一个文件 out/<lang>-all.json，供复核和渲染使用。
# 合并来源（后面的覆盖前面的）：<lang>-tm.json（记忆库命中）→ <lang>-remap.json（找回/迁移的译文）→ <lang>-todo-*.json（补译）
# 合并后 id 按 union.json 的顺序排列；被合并的文件挪到 out_parts/ 保留，不删除。
# 用法：python scripts/i18n/consolidate.py <series> <lang>
# 重复运行安全：已存在 <lang>-all.json 时，它作为最高优先级来源（复核修改不会被覆盖），只补入 all 里没有的 id。
import glob
import io
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def main():
    series, lang = sys.argv[1], sys.argv[2]
    d = os.path.join(ROOT, 'drafts', 'i18n', series)
    out = os.path.join(d, 'out')
    union = load(os.path.join(d, 'union.json'))
    merged = {}
    parts = []
    order = [f'{lang}-tm.json', f'{lang}-remap.json'] + [os.path.basename(f) for f in sorted(glob.glob(os.path.join(out, f'{lang}-todo-*.json')))]
    for name in order:
        p = os.path.join(out, name)
        if os.path.exists(p):
            for it in load(p):
                merged[it['id']] = it['text']
            parts.append(p)
    allp = os.path.join(out, f'{lang}-all.json')
    if os.path.exists(allp):
        for it in load(allp):
            merged[it['id']] = it['text']          # 已合并过的文件优先，保住复核的修改
    missing = [i['id'] for i in union if i['id'] not in merged]
    rows = [{'id': i['id'], 'text': merged[i['id']]} for i in union if i['id'] in merged]
    io.open(allp, 'w', encoding='utf-8', newline='\n').write(json.dumps(rows, ensure_ascii=False, indent=1))
    keep = os.path.join(d, 'out_parts')
    os.makedirs(keep, exist_ok=True)
    for p in parts:
        shutil.move(p, os.path.join(keep, os.path.basename(p)))
    print(f'{series}/{lang}: 合并 {len(rows)}/{len(union)} 条，缺 {len(missing)} 条 {missing[:8]}')
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
