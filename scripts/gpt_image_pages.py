# 生成 GPT Image 系列专题页（中英文各 7 页）：python scripts/gpt_image_pages.py
# 数据在 gpt_image_data.py，版块在 gpt_image_layout.py，文案在 gpt_image_copy_zh.py / gpt_image_copy_en.py。
# 生成后需运行 scripts/payments.py 和 scripts/trust.py 补上支付方式与信任版块（两个脚本重复运行结果不变）。
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gpt_image_layout as G  # noqa: E402
from gpt_image_data import SLUGS  # noqa: E402
import gpt_image_copy_zh  # noqa: E402
import gpt_image_copy_en  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
COPY = {'zh': gpt_image_copy_zh, 'en': gpt_image_copy_en}


def page(lang, slug):
    C = COPY[lang]
    c = C.build(slug)
    out = G.head(lang, slug, c) + G.nav(lang, slug) + G.hero(lang, slug, c)
    if slug == 'gpt-image':
        out += G.section('models', c['about_h2'], f'      <ul class="gi-models">{NL}{c["models_html"]}      </ul>{NL}', c.get('models_lead', ''))
    else:
        out += G.about(c)
    out += G.pricing(lang, c)
    out += G.gallery(lang, c)
    out += G.uses(lang, c)
    out += G.quickstart(lang, c)
    out += G.enterprise(lang, c['name'])
    out += G.family(lang, slug, C.FAMILY, c['family_h2'], c['family_lead'])
    out += G.faq(c)
    out += G.final(lang, slug, c)
    out += G.footer(lang, slug, c['docs'])
    return out


def main():
    G.LOGO_D = re.search(r' d="([^"]+)"', io.open(os.path.join(ROOT, 'assets/icons/openai.svg'), encoding='utf-8').read()).group(1)
    done = []
    for lang in ('zh', 'en'):
        for slug in SLUGS:
            p = os.path.join(ROOT, lang, 'models', slug + '.html')
            new = page(lang, slug)
            # 保留 payments.py / trust.py 已插入的内容：每次都整页重写，之后重跑这两个脚本即可
            io.open(p, 'w', encoding='utf-8', newline=NL).write(new)
            done.append(f'{lang}/{slug}')
    print('written:', ', '.join(done))


if __name__ == '__main__':
    main()
