# 调查：英文页里所有与中国相关的说法（meta、关键词、JSON-LD、正文），排除中文语言支持（Chinese 作为语言）和开票说法。
import collections
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAT = re.compile(r'\bChina\b|\bChinese\b|\bdomestic\b|\bVPN\b|\bproxy\b|\bGFW\b|\bfirewall\b|\bmainland\b|\bCN\b', re.I)
SKIP = re.compile(r'Chinese VAT|China VAT|Chinese (?:text|characters?|speech|language|and English|, English|prompts?|names?|voices?|dialects?|poetry|lyrics?)|(?:Mandarin|support|supports|in|and) Chinese|Chinese-(?:language|speaking)|Cantonese', re.I)


def main():
    groups = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)[:-5]
        if name == 'index':
            continue
        src = io.open(f, encoding='utf-8').read()
        for s in H.collect(src):
            if s.kind == 'ldjson':
                items = [('ld:' + str(p[-1]), v) for p, v in H.ld_strings(s.text)[1]]
            elif s.kind == 'attr':
                items = [(s.meta.get('attr', 'attr'), s.text)]
            else:
                items = [('text', s.text)]
            for where, t in items:
                plain = re.sub(r'<[^>]+>', '', t)
                for m in PAT.finditer(plain):
                    ctx = plain[max(0, m.start() - 70):m.end() + 70]
                    if SKIP.search(ctx):
                        continue
                    groups[(where.split(':')[0], re.sub(r'\s+', ' ', ctx))].append(name)
                    break
    print('distinct:', len(groups), '| occurrences:', sum(len(v) for v in groups.values()))
    byloc = collections.Counter()
    for (w, _), v in groups.items():
        byloc[w] += len(v)
    print('by location:', dict(byloc))
    for (w, c), v in sorted(groups.items(), key=lambda x: -len(x[1])):
        print(f'[{len(v):3d}] {w:12s} …{c}…   e.g. {v[0]}')


if __name__ == '__main__':
    main()
