# 生成 Kimi 系列专题页（中英文各 4 页：总览 + K3 / K2.7 Code / K2.6）：python scripts/kimi_pages.py
# 数据在 kimi_data.py，版块在 kimi_layout.py，文案在 kimi_copy_zh.py / kimi_copy_en.py。
# 每次整页重写，之后需重跑 scripts/payments.py 和 scripts/trust.py 补上支付方式与信任版块（两个脚本重复运行结果不变）。
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kimi_layout as G  # noqa: E402
from kimi_data import SLUGS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'


def copy(lang):
    if lang == 'zh':
        import kimi_copy_zh as C
    else:
        import kimi_copy_en as C
    return C


def page(lang, slug):
    C = copy(lang)
    c = C.build(slug)
    out = G.head(lang, slug, c) + G.nav(lang, slug) + G.hero(lang, slug, c)
    if slug == 'kimi':
        out += G.models(lang, c)
        out += G.pricing(lang, slug, c)
        out += G.compare(c)
    else:
        out += G.about(c)
        out += G.features(c)
        out += G.pricing(lang, slug, c)
        out += G.bench(c)
        out += G.compare(c)
    out += G.uses(c)
    out += G.quickstart(lang, c)
    out += G.claude_code(lang, c)
    out += G.enterprise(lang, c['ent_name'])
    out += G.family(lang, slug, C.FAMILY, c['family_h2'], c['family_lead'], 'Kimi')
    out += G.faq(c)
    out += G.final(lang, slug, c)
    out += G.footer(lang, slug)
    return out


def main():
    langs = sys.argv[1:] or ['zh', 'en']
    done = []
    for lang in langs:
        for slug in SLUGS:
            p = os.path.join(ROOT, lang, 'models', slug + '.html')
            io.open(p, 'w', encoding='utf-8', newline=NL).write(page(lang, slug))
            done.append(f'{lang}/{slug}')
    print('written:', ', '.join(done))


if __name__ == '__main__':
    main()
