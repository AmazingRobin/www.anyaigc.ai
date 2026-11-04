# 生成 Grok Video 系列专题页（中英文各 4 页）：python scripts/grok_video_pages.py
# 数据在 grok_video_data.py，视频版块在 grok_video_layout.py（通用版块复用 grok_image_layout.py），
# 文案在 grok_video_copy_zh.py / grok_video_copy_en.py。
# 每次整页重写，之后需重跑 scripts/payments.py 和 scripts/trust.py 补上支付方式与信任版块（两个脚本重复运行结果不变）。
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grok_video_layout as V  # noqa: E402  先导入：覆盖 grok_image_layout 的系列名、链接和脚本名
import grok_image_layout as G  # noqa: E402
from grok_video_data import SLUGS, HUB  # noqa: E402
import grok_video_copy_zh  # noqa: E402
import grok_video_copy_en  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = '\n'
COPY = {'zh': grok_video_copy_zh, 'en': grok_video_copy_en}


def page(lang, slug):
    c = COPY[lang].build(slug)
    out = V.head(lang, slug, c) + G.nav(lang, slug) + V.hero(lang, slug, c)
    out += V.lineup(lang, c) if slug == HUB else G.about(c)
    out += V.features(lang, c)
    if c.get('edits_h2'):
        out += V.edits(lang, c)
    out += V.pricing(lang, slug, c)
    if c.get('gallery'):
        out += V.gallery(lang, c)
    out += V.uses(lang, c)
    out += G.why(c)
    out += G.quickstart(lang, c)
    out += G.enterprise(lang, c)
    out += G.family(lang, slug, c['family'], c['family_h2'], c['family_lead'])
    out += G.faq(c)
    out += G.final(lang, slug, c)
    out += G.footer(lang, slug, c['docs'])
    return out


def main():
    G.load_icon()
    done = []
    for lang in ('zh', 'en'):
        for slug in SLUGS:
            p = os.path.join(ROOT, lang, 'models', slug + '.html')
            io.open(p, 'w', encoding='utf-8', newline=NL).write(page(lang, slug))
            done.append(f'{lang}/{slug}')
    print('written:', ', '.join(done))


if __name__ == '__main__':
    main()
