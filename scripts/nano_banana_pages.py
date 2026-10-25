# 生成 Nano Banana 系列专题页（中英文各 4 页：总览 + 2.1 / 2 / Pro）：python scripts/nano_banana_pages.py
# 数据在 nano_banana_data.py，版块在 nano_banana_layout.py，文案在 nano_banana_copy_zh.py / nano_banana_copy_en.py。
# 每次整页重写，之后需重跑 scripts/payments.py 和 scripts/trust.py 补上支付方式与信任版块（两个脚本重复运行结果不变）。
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nano_banana_layout as G  # noqa: E402
from nano_banana_data import SLUGS  # noqa: E402
import nano_banana_copy_zh  # noqa: E402
import nano_banana_copy_en  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
COPY = {'zh': nano_banana_copy_zh, 'en': nano_banana_copy_en}


def page(lang, slug):
    C = COPY[lang]
    c = C.build(slug)
    out = G.head(lang, slug, c) + G.nav(lang, slug) + G.hero(lang, slug, c) + G.quote(c)
    if slug == 'nano-banana':
        out += G.models(c)
        out += G.pricing(lang, c)
        out += G.compare(c)
        out += G.gallery(lang, c)
    else:
        out += G.about(c)
        out += G.features(lang, c)
        out += G.pricing(lang, c)
        out += G.compare(c)
        out += G.gallery(lang, c)
    out += G.uses(c)
    out += G.quickstart(lang, c)
    out += G.enterprise(lang, c['name'])
    out += G.family(lang, slug, C.FAMILY, c['family_h2'], c['family_lead'])
    out += G.faq(c)
    out += G.final(lang, slug, c)
    out += G.footer(lang, slug, c['docs'])
    return out


def main():
    raw = io.open(os.path.join(ROOT, 'assets/icons/nanobanana-color.svg'), encoding='utf-8').read()
    G.ICON = re.sub(r'<title>.*?</title>', '', re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S).group(1), flags=re.S)
    done = []
    for lang in ('zh', 'en'):
        for slug in SLUGS:
            p = os.path.join(ROOT, lang, 'models', slug + '.html')
            io.open(p, 'w', encoding='utf-8', newline=NL).write(page(lang, slug))
            done.append(f'{lang}/{slug}')
    print('written:', ', '.join(done))


if __name__ == '__main__':
    main()
