# 干跑：对 git HEAD 里每个英文页做语言菜单转换，统计导航/页脚/正文的切换链接各有几个，找出结构特殊的页面。
# 用法：python scripts/i18n/survey_menus.py
import collections
import glob
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
import htmlseg as H

ROOT = B.ROOT


def head(rel):
    return subprocess.run(['git', 'show', 'HEAD:' + rel], capture_output=True, cwd=ROOT).stdout.decode('utf-8')


def main():
    shapes, odd = collections.Counter(), collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)
        if name == 'index.html':
            continue
        src = head('en/models/' + name)
        root = H.parse(src)
        c = collections.Counter(B.placement(n, a) for n, a in B.switch_anchors(root, src, 'zh-CN'))
        out = B.convert_switches(src, name[:-5], 'en', ['zh', 'en', 'ja', 'ko', 'es', 'de'], 'zh-CN', drop_body=False)
        menus = out.count('<details class="lang-menu')
        key = (c['nav'], c['foot'], c['body'], menus)
        shapes[key] += 1
        if c['nav'] != 1 or c['foot'] != 1:
            odd[key].append(name[:-5])
    print('(nav, foot, body, menus) -> pages')
    for k, n in shapes.most_common():
        print(' ', k, n)
    print('\n结构特殊（导航或页脚的切换链接不是各 1 个）:')
    for k, v in odd.items():
        print(' ', k, len(v), v[:6])


if __name__ == '__main__':
    main()
