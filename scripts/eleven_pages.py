# 生成 ElevenLabs（Eleven）系列专题页（中英文各 7 页：eleven-v4 / v4-turbo / v3 / v3-conversational / multilingual-v2 / flash-v2-5 / flash-v2）：python scripts/eleven_pages.py
# 数据在 eleven_data.py，版块在 eleven_layout.py，文案在 eleven_copy_zh.py / eleven_copy_en.py，代码示例在 eleven_code.py。
# 7 款模型各自独立成页，没有系列总览页。
# 每次整页重写，之后需重跑 scripts/icons.py、payments.py、trust.py（三个脚本重复运行结果不变）。
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eleven_layout as G  # noqa: E402
from eleven_data import SLUGS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'


def copy(lang):
    if lang == 'zh':
        import eleven_copy_zh as C
    else:
        import eleven_copy_en as C
    return C


def page(lang, slug):
    C = copy(lang)
    c = C.build(slug)
    out = G.head(lang, slug, c) + G.nav(lang, slug) + G.hero(lang, slug, c)
    out += G.about(c)
    out += G.features(c)
    out += G.pricing(lang, slug, c)
    out += G.compare(c, slug)
    out += G.uses(c)
    out += G.quickstart(lang, c)
    out += G.enterprise(lang, c['ent_name'])
    out += G.family(lang, slug, C.FAMILY, c['family_h2'], c['family_lead'], 'Eleven')
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
