# 调查：各系列英文页（git HEAD 版本）里语言切换链接的位置、外层容器和 class。
# 用法：python scripts/i18n/survey_switch.py
import collections
import glob
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
import htmlseg as H

ROOT = B.ROOT


def head(rel):
    return subprocess.run(['git', 'show', 'HEAD:' + rel], capture_output=True, cwd=ROOT).stdout.decode('utf-8')


def cls(node):
    m = re.search(r'class="([^"]*)"', node.attrs)
    return m.group(1) if m else ''


def main():
    ctx, ex = collections.Counter(), {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)
        if name == 'index.html':
            continue
        src = head('en/models/' + name)
        root = H.parse(src)
        for node, anc in B.switch_anchors(root, src, 'zh-CN'):
            place = 'nav' if B.in_nav(node, anc) else 'body'
            p = anc[-1] if anc else None
            gp = anc[-2] if len(anc) > 1 else None
            key = (place, (gp.tag + '.' + cls(gp)) if gp is not None else '-',
                   (p.tag + '.' + cls(p)) if p is not None else '-', cls(node))
            ctx[key] += 1
            ex.setdefault(key, name)
    for k, n in ctx.most_common(40):
        print(n, k, '|', ex[k][:30])
    print('distinct contexts:', len(ctx))


if __name__ == '__main__':
    main()
