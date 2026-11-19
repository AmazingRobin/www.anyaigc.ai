# 调查：英文页里"中国大陆可访问"卡片——最近的卡片容器、同组卡片数量与标题、网格列数（读系列 CSS）。
# 用法：python scripts/i18n/china_cards.py
import collections
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TITLE = re.compile(r'^(?:Direct access(?: from (?:mainland )?China| in China|, [a-z ]+)?|Works from mainland China|Reachable from (?:mainland )?China|No extra proxy)$', re.I)
CARD_TAGS = ('li', 'article', 'div')


def css_for(src):
    out = ''
    for m in re.finditer(r'<link rel="stylesheet" href="(/assets/models/[^"?]+)', src):
        p = os.path.join(ROOT, m.group(1).lstrip('/'))
        if os.path.exists(p) and 'scrollbar' not in p and 'lang-menu' not in p:
            out += io.open(p, encoding='utf-8').read()
    return out


def grid_rule(css, cls):
    if not cls:
        return ''
    best = ''
    for m in re.finditer(r'(?:^|[},\s])\.' + re.escape(cls) + r'\s*\{([^}]*)\}', css):
        r = re.sub(r'\s+', ' ', m.group(1))
        if 'grid-template-columns' in r or 'flex' in r:
            best = r
    cols = re.search(r'grid-template-columns:\s*([^;]+)', best)
    return (cols.group(1) if cols else best)[:80]


def main():
    seen = collections.OrderedDict()
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)[:-5]
        if name == 'index':
            continue
        src = io.open(f, encoding='utf-8').read()
        root = H.parse(src)
        css = None
        for n in H.walk(root):
            if n.tag not in ('h3', 'strong', 'b') or n.so is None or n.ec is None:
                continue
            t = re.sub(r'<[^>]+>', '', src[n.so:n.ec]).strip()
            if not TITLE.match(t):
                continue
            card = n.parent
            while card is not None and card.tag not in CARD_TAGS:
                card = card.parent
            if card is None:
                continue
            par = card.parent
            sibs = [k for k in par.kids if k.tag == card.tag]
            titles = []
            for k in sibs:
                m = re.search(r'<h3[^>]*>(.*?)</h3>', src[k.so:k.ec], re.S)
                titles.append(re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else '?')
            pc = re.search(r'class="([^"]*)"', par.attrs or '')
            cls = pc.group(1).split()[0] if pc else ''
            if css is None:
                css = css_for(src)
            body = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', src[card.so:card.ec])).strip()
            key = (cls, len(sibs), grid_rule(css, cls))
            seen.setdefault(key, []).append((name, t, body[:140], titles))
    print('distinct (group class, cards in group, grid):', len(seen))
    for (cls, n, grid), v in seen.items():
        print(f'\n## .{cls or "(none)"}  cards={n}  grid="{grid}"  pages={len(v)}: {[x[0] for x in v][:6]}')
        print('   titles :', v[0][3])
        print('   china  :', v[0][1], '|', v[0][2])


if __name__ == '__main__':
    main()
