"""专题首页（模型指南列表页）分享图：assets/og/models-{ja,ko,es,de}.png（1200x630）。

assets/og/models-zh.png、models-en.png 早先直接放进仓库，没有生成脚本；本脚本按英文图复刻配色与版式
（暖黑底 #2a211f、白色粗体标题、浅橙药丸标签、左下角 AnyAIGC、底部珊瑚红色条 #e45f45），只出新语言，不碰 zh/en。

版式：顶部 2 个药丸标签（并发不限、自助开票），标题（可两行），副标题，左下品牌。不新增事实（不写模型数等）。
副标题 = "One API key · 300+ models" 的译文，标题 = 页面 H1 的译文。

用法（需先 python scripts/preview.py）：
    python scripts/og_models.py --langs=ja,ko,es,de
    python scripts/og_models.py --langs=ja --html-only      只写临时 HTML，不截图
截图前量 DOM 自检，越界/重叠自动缩小字号，仍违例不出图并报错。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import og_newlang as nl  # noqa: E402
from og_newlang import L  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og-models')
BRAND_A, BRAND_B = 'Any', 'AIGC'  # 品牌名区分大小写，不要转大写

# 标题 = 页面 H1 的译文；副标题 = "One API key · 300+ models" 的译文
H1 = L('AIモデル API ガイド', 'AI 모델 API 가이드', 'Guías de API de modelos de IA', 'API-Leitfäden für <span class="nw">KI-Modelle</span>')
SUB = L('1つのAPIキーで300以上のモデル', 'API 키 하나로 300개 이상 모델', 'Una clave de API · más de 300 modelos', 'Ein API-Schlüssel · über 300 Modelle')
TAGS = ('Unlimited concurrency', nl.ENT_EN)  # 词表里的固定译法（og_newlang.WORDS）

TPL = '''<!doctype html><html lang="@LANG"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{position:relative;background:#2a211f;color:#fff;font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif}
.main{position:absolute;left:80px;top:84px;width:1040px}
.tags{display:flex;flex-wrap:nowrap;gap:12px}
.tags span{padding:11px 22px;border-radius:999px;background:#3a2d29;border:1px solid #4d3a33;color:#f5d8cb;font-size:22px;font-weight:700;white-space:nowrap}
h1{margin:34px 0 0;font-size:104px;line-height:1.1;font-weight:800;letter-spacing:-.01em;color:#fff}
p{margin:22px 0 0;font-size:36px;line-height:1.3;color:#cfc3bd}
.brand{position:absolute;left:80px;bottom:62px;font-size:34px;font-weight:800;color:#fff;white-space:nowrap}
.brand b{color:#e45f45}
.bar{position:absolute;left:0;bottom:0;width:1200px;height:10px;background:#e45f45}
.n h1{font-size:92px}
html[lang=ko] h1{word-break:keep-all}
.nw{white-space:nowrap}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style></head><body>
<div class="main"><div class="tags">@CHIPS</div><h1>@H1</h1><p>@SUB</p></div>
<div class="brand">@A<b>@B</b></div><div class="bar"></div>
</body></html>'''

PAGES = {'models': None}


def card(lang):
    """返回一张图的 HTML。逐项查词表，缺词直接 KeyError，不回退英文。"""
    chips = ''.join(f'<span>{nl.word(t, lang)}</span>' for t in TAGS)
    return (TPL.replace('@LANG', nl.LANGATTR[lang]).replace('@CHIPS', chips).replace('@H1', H1[lang])
            .replace('@SUB', SUB[lang]).replace('@A', BRAND_A).replace('@B', BRAND_B))


# 标题、副标题、标签、品牌都要在画面内且互不重叠；标题/副标题/标签各自缩小
CFG = {'scale': ['h1', 'p'], 'chips': ['.tags span'], 'check': ['h1', 'p', '.brand'], 'obst': [], 'max': [1200, 630]}


def main():
    langs, _, html_only = nl.parse_args(sys.argv, PAGES)
    if not langs or any(x not in nl.NEW for x in langs):
        raise SystemExit('用法: python scripts/og_models.py --langs=ja,ko,es,de [--html-only]（只出新语言，zh/en 保持原样）')
    jobs = [('models', lang, card(lang)) for lang in langs]
    nl.shoot(jobs, ROOT, OUT, '.playwright-mcp/og-models', CFG, html_only)


if __name__ == '__main__':
    main()
