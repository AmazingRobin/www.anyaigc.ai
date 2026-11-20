# 检查分享图底部标签行的右边距：最右侧的标签边缘必须离画布右边至少 80px（和左边距一致）。
# 用法：python scripts/i18n/og_margin.py <前缀>     例：deepseek
import glob
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WIDTH, MARGIN = 1200, 80
# --overlap：额外检查副标题折行后是否压到标签行。只适用标签行顶部在 y≥514 的版式（Gemini、GPT）；
# Claude、DeepSeek、Suno、Midjourney 的标签行更靠上，价格胶囊本身会落进检查区间，用它会误报。
OVERLAP = '--overlap' in sys.argv
# 右侧有大块亮色图片/光晕的版式，"最右亮像素"检查不适用，只能目检（已逐张看过）：
SKIP = ('suno-', 'midjourney-', 'gpt-image', 'grok-image', 'grok-imagine-', 'grok-video')


_DARK = {}


def is_dark(path):
    if path not in _DARK:
        im = Image.open(path).convert('L')
        _DARK[path] = im.getpixel((8, 8)) < 90 and im.getpixel((600, 560)) < 120
    return _DARK[path]


def rightmost(path, pad):
    """最右侧标签的右边缘 ≈ 最右的深色文字像素 + 标签右内边距。
    背景有蓝色光斑，不能用"比背景深"判断边缘；标签文字是 #1e232c，亮度远低于背景，用它定位。"""
    im = Image.open(path).convert('L')
    dark = is_dark(path)
    w, h = im.size
    best = 0
    for y in range(505, 580, 2):
        for x in range(w - 1, 0, -1):
            v = im.getpixel((x, y))
            if (v > 150) if dark else (v < 110):
                best = max(best, x)
                break
    return best + pad


def subtitle_collides(path):
    """副标题折行后会压到标签行：标签行上沿以上 30px 内（y 484-514）、图标左侧（x<900）不应有深色文字。"""
    im = Image.open(path).convert('L')
    dark = is_dark(path)
    for y in range(484, 514, 2):
        for x in range(80, 900, 3):
            v = im.getpixel((x, y))
            if (v > 150) if dark else (v < 110):
                return True
    return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    prefix = args[0] if args else ''
    bad = 0
    for f in sorted(glob.glob(os.path.join(ROOT, 'assets', 'og', prefix + '*-??.png'))):
        # 默认只检查新语言；zh/en 是原有的图，加 --all 才一起看
        if not re.search(r'-(ja|ko|es|de)\.png$' if '--all' not in sys.argv else r'-(zh|en|ja|ko|es|de)\.png$', f):
            continue
        if os.path.basename(f).startswith(SKIP):
            continue
        pad = 22 if re.search(r'-(zh|en)\.png$', f) else 17      # 新语言图的标签内边距更小（og_deepseek.py 的 .r.s）
        r = rightmost(f, pad)
        collides = OVERLAP and subtitle_collides(f)
        ok = r <= WIDTH - MARGIN and not collides
        bad += not ok
        print(f'{os.path.basename(f):38s} {r:5d}  {"ok" if ok else ("SUBTITLE OVERLAPS CHIPS" if collides else "TOO CLOSE TO RIGHT EDGE")}')
    print(f'超出右边距的图：{bad}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
