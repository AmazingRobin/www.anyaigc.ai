# 调查：每种"中国大陆可访问"写法在样例页里的外层结构（卡片 / 标签 / 句子），决定怎么删。
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLES = {
    'doubao-seed-1-6-flash': r'Direct access from mainland China$',
    'grok-image': r'Direct access from China$',
    'doubao-seedance-2-0-fast': r'Direct access in China$',
    'jev': r'Reachable from China$',
    'muse-image': r'Works from mainland China|reachable from China',
    'suno': r'China-ready|Optimized for networks in mainland China',
    'mimo-v2.5-pro': r'Call AnyAIGC directly from mainland China',
    'minimax': r'Call AnyAIGC directly from mainland China',
    'hailuo-h3': r'Connect directly through the AnyAIGC domain from mainland China',
    'nano-banana-2.1': r'works directly from mainland Chi',
}


def main():
    for slug, pat in SAMPLES.items():
        src = io.open(os.path.join(ROOT, 'en', 'models', slug + '.html'), encoding='utf-8').read()
        root = H.parse(src)
        hit = None
        for n in H.walk(root):
            if n.tag == '#text' and re.search(pat, src[n.s:n.so]):
                hit = n
                break
        if hit is None:
            print(f'== {slug}: NOT FOUND for {pat}')
            continue
        chain, p = [], hit.parent
        while p is not None and p.tag != '#root':
            chain.append(p)
            p = p.parent
        cont = next((c for c in chain if c.tag in ('li', 'article', 'section', 'dd')), chain[0])
        print(f'== {slug}  chain: ' + ' < '.join(f'{c.tag}.{re.sub(chr(34), "", re.search(r"class=.([^\"]*)", c.attrs).group(1)) if "class=" in c.attrs else ""}' for c in chain[:5]))
        print('   container:', re.sub(r'\s+', ' ', src[cont.s:cont.e])[:520])
        sib = [k for k in cont.parent.kids if k.tag != '#text']
        print(f'   container has {len(sib)} sibling elements of kind <{cont.tag}> in <{cont.parent.tag}>')


if __name__ == '__main__':
    main()
