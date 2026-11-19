# 调查：含"中国大陆可访问"说法的卡片，同组其他卡片的标题，以及这组卡片的网格列数（读各系列 CSS）。
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLES = ['doubao-seed-1-6-flash', 'grok-image', 'doubao-seedance-2-0-fast', 'jev', 'muse-image', 'suno',
           'mimo-v2.5-pro', 'minimax', 'hailuo-h3']
PAT = re.compile(r'mainland China|from China|in China|reachable from|China-ready|mainland networks', re.I)


def css_for(src):
    out = ''
    for m in re.finditer(r'<link rel="stylesheet" href="(/assets/models/[^"?]+)', src):
        p = os.path.join(ROOT, m.group(1).lstrip('/'))
        if os.path.exists(p) and 'scrollbar' not in p and 'lang-menu' not in p:
            out += io.open(p, encoding='utf-8').read()
    return out


def main():
    for slug in SAMPLES:
        src = io.open(os.path.join(ROOT, 'en', 'models', slug + '.html'), encoding='utf-8').read()
        root = H.parse(src)
        css = css_for(src)
        for n in H.walk(root):
            if n.tag in ('li', 'article', 'div') and n.ec is not None and PAT.search(re.sub(r'<[^>]+>', ' ', src[n.so:n.ec])) \
                    and not any(c.tag in ('li', 'article', 'div') and PAT.search(re.sub(r'<[^>]+>', ' ', src[c.so:c.ec])) for c in n.kids if c.tag != '#text'):
                par = n.parent
                kids = [k for k in par.kids if k.tag == n.tag]
                titles = [re.sub(r'<[^>]+>', '', (re.search(r'<h3[^>]*>(.*?)</h3>', src[k.so:k.ec], re.S) or re.search(r'<strong>(.*?)</strong>', src[k.so:k.ec], re.S) or [None, ''])[1]) for k in kids]
                cls = re.search(r'class="([^"]*)"', par.attrs)
                cls = cls.group(1).split()[0] if cls else ''
                rule = ''
                if cls:
                    m = re.search(r'(?:^|[},\s])\.' + re.escape(cls) + r'\s*\{([^}]*)\}', css)
                    rule = re.sub(r'\s+', ' ', m.group(1))[:170] if m else '(no rule)'
                print(f'== {slug}: <{par.tag} class="{cls}"> has {len(kids)} <{n.tag}>: {titles}')
                print(f'   grid: {rule}')
                break


if __name__ == '__main__':
    main()
