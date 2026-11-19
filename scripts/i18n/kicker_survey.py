# 调查：每个页面里「这个型号的规格与选型」(spec-unique) 版块的小标题（kicker）与其它版块的是否一致。
# 用法：python scripts/i18n/kicker_survey.py
import collections
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KICK = re.compile(r'<(p|span|div|small)\b[^>]*class="([^"]*kicker[^"]*)"[^>]*>', re.I)


def main():
    rows = collections.OrderedDict()
    for lang in ('en',):
        for f in sorted(glob.glob(os.path.join(ROOT, lang, 'models', '*.html'))):
            name = os.path.basename(f)[:-5]
            if name == 'index':
                continue
            t = io.open(f, encoding='utf-8').read()
            m = re.search(r'<section class="[^"]*" id="spec-unique".*?</section>', t, re.S)
            if not m:
                continue
            spec = KICK.search(m.group(0))
            rest = t.replace(m.group(0), '')
            others = collections.Counter((a, b.split()[0]) for a, b in KICK.findall(rest))
            series = re.split(r'[-.]', name)[0]
            key = (series, (spec.group(1), spec.group(2)) if spec else None, others.most_common(1)[0][0] if others else None)
            rows.setdefault(key, []).append(name)
    print('series | spec-unique kicker (tag, class) | most common kicker elsewhere (tag, first class) | pages')
    for (s, a, b), v in rows.items():
        flag = ''
        if a is None:
            flag = ''
        elif b is None:
            flag = '   <-- spec has a kicker, nothing else does'
        elif a[1].split()[0] != b[1]:
            flag = '   <-- class differs'
        print(f'{s:12s} spec={a} others={b} n={len(v)}{flag}')


if __name__ == '__main__':
    main()
