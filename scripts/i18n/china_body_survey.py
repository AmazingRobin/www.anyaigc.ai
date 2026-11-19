# 调查：英文页里 FAQ 以外的"中国大陆可访问"说法，按位置（meta / JSON-LD / 正文单元）和句子归类。
# 用法：python scripts/i18n/china_body_survey.py [--all]    默认不列"Chinese VAT invoices"这类开票说法（它们由各系列的 overseas.py 处理）
import collections
import glob
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAT = re.compile(r'mainland China|from China|in China|China-?(?:friendly|ready)|within China|inside China|domestic|without (?:a )?(?:VPN|proxy)|no (?:VPN|proxy)|direct(?:ly)? (?:access|connect|call|reach)[^.]{0,30}China|reachable', re.I)
INVOICE = re.compile(r'Chinese VAT|China VAT|VAT|invoice', re.I)


def main():
    show_all = '--all' in sys.argv
    groups = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)[:-5]
        if name == 'index':
            continue
        src = io.open(f, encoding='utf-8').read()
        for s in H.collect(src):
            if s.kind == 'ldjson':
                texts = [('ld', v) for p, v in H.ld_strings(s.text)[1]]
            else:
                texts = [(s.meta.get('attr', 'text') if s.kind == 'attr' else 'text', s.text)]
            for where, t in texts:
                plain = re.sub(r'<[^>]+>', '', t)
                if not PAT.search(plain):
                    continue
                if not show_all and INVOICE.search(plain) and 'Chinese VAT' in plain and not re.search(r'direct|reach|proxy|optimi[sz]ed|tuned', plain, re.I):
                    continue
                groups[(where, re.sub(r'\s+', ' ', plain)[:230])].append(name)
    rows = sorted(groups.items(), key=lambda x: -len(x[1]))
    print('distinct (location, text):', len(rows), '| occurrences:', sum(len(v) for _, v in rows))
    byloc = collections.Counter()
    for (w, _), v in rows:
        byloc[w] += len(v)
    print('by location:', dict(byloc))
    for (w, t), v in rows:
        print(f'[{len(v):3d}] {w:12s} {t}')
        print(f'        e.g. {v[:3]}')


if __name__ == '__main__':
    main()
