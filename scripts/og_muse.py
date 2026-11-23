"""Muse Image / Muse Video 分享图（1200×630）。

assets/og/muse-{image,video}-{zh,en}.png 最初是随专题页一起提交的（提交 4d136ae9、5b4eb3c9），没有生成脚本；
本脚本按那两张英文图复刻配色与版式（白底、Meta 蓝 #0064e0、深色徽章、右侧素材拼图），并修正版面：
标签固定单行（和原图一致），撞到右侧图块或越界时由自检缩小标签字号，不再换行挤到副标题。素材是页面自己的示例图/视频封面，logo 读 assets/icons/meta-color.svg。

用法（需先 python scripts/preview.py）：
    python scripts/og_muse.py                              只写 zh/en 的临时 HTML，不截图
    python scripts/og_muse.py --langs=ja,ko,es,de [--only=muse-image]
    python scripts/og_muse.py --langs=en                   只重出英文图
zh 图不在这里重出。截图前量 DOM 自检，越界/重叠自动缩小字号，仍违例不出图。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import og_newlang as nl  # noqa: E402
from og_newlang import L  # noqa: E402
from icons import svg as icon_svg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og-muse')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

# 图块：(素材路径, 左, 上, 宽, 高)。image 两列四张竖图，video 两列四张 16:9 封面（带播放键）
TILES = {
    'muse-image': [('muse-image/poster-state-tech', 682, 62, 228, 262), ('muse-image/fashion-mondrian', 682, 338, 228, 262),
                   ('muse-image/matcha-ad', 924, 40, 228, 262), ('muse-image/polaroid-big-sur', 924, 316, 228, 262)],
    'muse-video': [('muse-video/blush-fizz', 672, 134, 233, 131), ('muse-video/otter', 672, 279, 233, 131),
                   ('muse-video/panda', 919, 110, 233, 131), ('muse-video/juggler', 919, 255, 233, 131)],
}

# 每页：标题、英文副标题（价格取自页面 og:description）、英文标签（与现有英文图一致，没有企业标签，不新加）
PAGES = {
    'muse-image': dict(name='Muse Image API', price='0.00596', unit='image', tags=['Precise edits', 'Multi-image', 'Unlimited concurrency'],
                       sub={'zh': 'Meta 的生图模型，¥0.04 / 张', 'en': "Meta's image model, $0.00596 / image"},
                       tags_zh=['精准改图', '多图合成', '并发不限']),
    'muse-video': dict(name='Muse Video API', price='0.0397', unit='second', tags=['Native audio', '720p · 4–30 s', 'Unlimited concurrency'],
                       sub={'zh': 'Meta 的视频模型，¥0.27 / 秒', 'en': "Meta's video model, $0.0397 / second"},
                       tags_zh=['原生音频', '720p · 4–30 秒', '并发不限']),
}

# 新语言副标题模板：{p} 为已带 $ 的价格；缺词直接 KeyError，不回退英文
SUB_I18N = {
    'image': L('Meta の画像モデル、1枚 {p}', 'Meta의 이미지 모델, 이미지당 {p}', 'El modelo de imágenes de Meta, {p} por imagen', 'Metas Bildmodell, {p} pro Bild'),
    'second': L('Meta の動画モデル、1秒 {p}', 'Meta의 비디오 모델, 초당 {p}', 'El modelo de vídeo de Meta, {p} por segundo', 'Metas Videomodell, {p} pro Sekunde'),
}
TXT = {
    'Precise edits': L('精密な編集', '정밀 편집', 'Edición precisa', 'Präzise Bearbeitung'),
    'Multi-image': L('複数画像', '멀티 이미지', 'Varias imágenes', 'Mehrere Bilder'),
    '720p · 4–30 s': L('720p · 4〜30秒', '720p · 4–30초', '720p · 4–30 s', '720p · 4–30 s'),
}

TPL = '''<!doctype html><html lang="@LANG"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{position:relative;background:#fff;color:#1c2b33;font-family:Arial,"Helvetica Neue","Microsoft YaHei",sans-serif}
.brand{position:absolute;left:72px;top:76px;display:flex;align-items:center;gap:14px;font-size:26px;font-weight:700;letter-spacing:-.01em}
.brand svg{width:54px;height:54px;flex:none}
.badge{position:absolute;left:72px;top:162px;padding:8px 18px;border-radius:999px;background:#1c2b33;color:#fff;font-size:16px;font-weight:700;letter-spacing:.2em;white-space:nowrap}
h1{position:absolute;left:72px;top:212px;width:560px;margin:0;font-size:84px;line-height:1.08;font-weight:400;letter-spacing:-.01em}
p{position:absolute;left:72px;top:412px;width:560px;margin:0;font-size:32px;line-height:1.3;color:#465a69}
.tags{position:absolute;left:72px;bottom:64px;display:flex;flex-wrap:nowrap;gap:12px}
.tags span{padding:11px 20px;border-radius:999px;background:#f1f4f7;font-size:22px;white-space:nowrap;color:#1c2b33}
.tags span:first-child{background:#0064e0;color:#fff;font-weight:700}
.tile{position:absolute;border-radius:16px;overflow:hidden;background:#dee3e9 center/cover no-repeat;box-shadow:0 2px 10px rgba(28,43,51,.14)}
.play{position:absolute;left:12px;bottom:12px;width:30px;height:30px;border-radius:50%;background:rgba(28,43,51,.72)}
.play:after{content:"";position:absolute;left:11px;top:8px;border-left:10px solid #fff;border-top:7px solid transparent;border-bottom:7px solid transparent}
.n p{font-size:28px}.n h1{font-size:80px}.n .tags span{font-size:20px;padding:10px 16px}
</style></head><body>
<div class="brand">@ICON@BRAND</div><div class="badge">META · MUSE</div>
<h1>@NAME</h1><p>@SUB</p><div class="tags">@CHIPS</div>
@TILES</body></html>'''


def card(slug, lang):
    """返回一张图的 HTML。新语言逐项查词表，不回退英文。"""
    pg = PAGES[slug]
    if lang in nl.NEW:
        sub = SUB_I18N[pg['unit']][lang].format(p=nl.money(pg['price'], lang))
        tags = [nl.word(t, lang, TXT) for t in pg['tags']]
    elif lang == 'zh':
        sub, tags = pg['sub']['zh'], pg['tags_zh']
    else:
        sub, tags = pg['sub']['en'], pg['tags']
    tiles = ''.join(
        f'<div class="tile" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background-image:url(/assets/models/{src}.webp)">'
        + ('<i class="play"></i>' if slug == 'muse-video' else '') + '</div>\n'
        for src, x, y, w, h in TILES[slug])
    chips = ''.join(f'<span>{t}</span>' for t in tags)
    return (TPL.replace('@LANG', nl.LANGATTR[lang]).replace('@ICON', icon_svg('meta-color', size=54, evenodd=False))
            .replace('@BRAND', BRAND).replace('@NAME', pg['name']).replace('@SUB', sub).replace('@CHIPS', chips).replace('@TILES', tiles))


# 版面自检：文字和标签不能压到右侧图块，不能越出画面
CFG = {'scale': ['h1', 'p'], 'chips': ['.tags span'], 'check': ['h1', 'p', '.brand', '.badge'], 'obst': ['.tile'], 'max': [1200, 630]}


def main():
    langs, only, html_only = nl.parse_args(sys.argv, PAGES)
    if langs:
        jobs = [(slug, lang, card(slug, lang)) for lang in langs for slug in PAGES if only is None or slug in only]
        nl.shoot(jobs, ROOT, OUT, '.playwright-mcp/og-muse', CFG, html_only)
        return
    os.makedirs(OUT, exist_ok=True)
    for lang in ('zh', 'en'):
        for slug in PAGES:
            with open(os.path.join(OUT, f'{slug}-{lang}.html'), 'w', encoding='utf-8') as f:
                f.write(card(slug, lang))
            print(f'{slug}-{lang}.html')


if __name__ == '__main__':
    main()
