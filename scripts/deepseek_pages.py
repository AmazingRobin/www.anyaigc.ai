# 生成 DeepSeek 系列专题页（总览 + V4.1 Flash / V4 Pro / V4 Flash）：python scripts/deepseek_pages.py [zh] [en]
# 不传参数时生成中英文；deepseek_copy_en.py 只在生成英文时才导入。
# 数据在 deepseek_data.py，版块在 deepseek_layout.py，文案在 deepseek_copy_zh.py / deepseek_copy_en.py。
# 每次整页重写，之后需重跑 scripts/payments.py 和 scripts/trust.py 补上支付方式与信任版块（两个脚本重复运行结果不变）。
import importlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deepseek_layout as G  # noqa: E402
from deepseek_data import SLUGS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'


def copy(lang):
    # 懒加载：只生成中文时不需要 deepseek_copy_en.py 存在
    return importlib.import_module('deepseek_copy_zh' if lang == 'zh' else 'deepseek_copy_en')


def page(lang, slug):
    C = copy(lang)
    c = C.build(slug)
    out = G.head(lang, slug, c) + G.nav(lang, slug) + G.hero(lang, slug, c)
    if slug == G.HUB:
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
    out += G.family(lang, slug, C.FAMILY, c['family_h2'], c['family_lead'], 'DeepSeek')
    out += G.faq(c)
    out += G.final(lang, slug, c)
    out += G.footer(lang, slug)
    return out


def main():
    langs = [a for a in sys.argv[1:] if a in ('zh', 'en')] or ['zh', 'en']
    done = []
    for lang in langs:
        for slug in SLUGS:
            p = os.path.join(ROOT, lang, 'models', slug + '.html')
            io.open(p, 'w', encoding='utf-8', newline=NL).write(page(lang, slug))
            done.append(f'{lang}/{slug}')
    print('written:', ', '.join(done))


if __name__ == '__main__':
    main()
