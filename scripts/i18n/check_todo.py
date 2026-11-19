# 译者自检：校验一个补译块 todo/<lang>-<n>.json 对应的译文 out/<lang>-todo-<n>.json。
# 原理：在 drafts/i18n/_chk_<lang>_<n>/ 里临时搭一个只有这一块的"系列"，直接复用 batch.validate，不改动真正的 out/。
# 用法：python scripts/i18n/check_todo.py claude <lang> <n>
import io
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch as BT


def main():
    series, lang, n = sys.argv[1], sys.argv[2], sys.argv[3]
    d = os.path.join(BT.DRAFT, series)
    todo = os.path.join(d, 'todo', f'{lang}-{n}.json')
    out = os.path.join(d, 'out', f'{lang}-todo-{n}.json')
    if not os.path.exists(out):
        raise SystemExit(f'还没有译文文件：{out}')
    tmp = os.path.join(BT.DRAFT, f'_chk_{lang}_{n}')
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(tmp, 'out'))
    shutil.copy(todo, os.path.join(tmp, 'union.json'))
    shutil.copy(out, os.path.join(tmp, 'out', f'{lang}-all.json'))
    errs, warns = BT.validate(os.path.basename(tmp), lang)
    shutil.rmtree(tmp, ignore_errors=True)
    for e in errs:
        print('ERROR', e)
    for w in warns:
        if '与原文完全相同' not in w:
            print('WARN ', w)
    print(f'校验完成：{len(errs)} 个错误')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
