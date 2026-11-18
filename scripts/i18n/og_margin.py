# 检查分享图底部标签行的右边距：最右侧的标签边缘必须离画布右边至少 80px（和左边距一致）。
# 用法：python scripts/i18n/og_margin.py <前缀>     例：deepseek
import glob
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WIDTH, MARGIN = 1200, 80


def rightmost(path, pad):
    """最右侧标签的右边缘 ≈ 最右的深色文字像素 + 标签右内边距。
    背景有蓝色光斑，不能用"比背景深"判断边缘；标签文字是 #1e232c，亮度远低于背景，用它定位。"""
    im = Image.open(path).convert('L')
    w, h = im.size
    best = 0
    for y in range(505, 580, 2):
        for x in range(w - 1, 0, -1):
            if im.getpixel((x, y)) < 110:
                best = max(best, x)
                break
    return best + pad


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    prefix = args[0] if args else ''
    bad = 0
    for f in sorted(glob.glob(os.path.join(ROOT, 'assets', 'og', prefix + '*-??.png'))):
        # 默认只检查新语言；zh/en 是原有的图，加 --all 才一起看
        if not re.search(r'-(ja|ko|es|de)\.png$' if '--all' not in sys.argv else r'-(zh|en|ja|ko|es|de)\.png$', f):
            continue
        pad = 22 if re.search(r'-(zh|en)\.png$', f) else 17      # 新语言图的标签内边距更小（og_deepseek.py 的 .r.s）
        r = rightmost(f, pad)
        ok = r <= WIDTH - MARGIN
        bad += not ok
        print(f'{os.path.basename(f):38s} {r:5d}  {"ok" if ok else "TOO CLOSE TO RIGHT EDGE"}')
    print(f'超出右边距的图：{bad}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
