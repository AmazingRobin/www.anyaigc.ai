"""Write 1200x630 Hy4 sharing-card HTML for Playwright screenshots.

Usage: python scripts/og_hy4.py  -> .playwright-mcp/hy4-og/hy4-<lang>.html
Screenshot each at 1200x630 into assets/og/hy4-<lang>.png, then delete the temp HTML.

新语言 / 重出英文图（需先 python scripts/preview.py）：
    python scripts/og_hy4.py --langs=ja,ko,es,de [--only=hy4]
    python scripts/og_hy4.py --langs=en
直接截图到 assets/og/<slug>-<lang>.png，截图前量 DOM 自检，越界/重叠自动缩小字号，仍违例不出图；zh 图不在这里重出。
"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import og_newlang as nl  # noqa: E402
from og_newlang import L  # noqa: E402

from hy4_data import PRICES
from hy4_pages import mark, DEAL_ZH, DEAL_EN

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".playwright-mcp" / "hy4-og"

CSS = """
*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{background:#f9f9f9;color:#1a1a1a;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",-apple-system,"Helvetica Neue",Arial,sans-serif;position:relative}
.main{position:absolute;left:72px;top:64px;width:640px}
.brand{display:flex;align-items:center;gap:14px;font-weight:700;font-size:26px}
.brand i{font-style:normal;color:rgba(0,0,0,.4);font-weight:400}
h1{margin:64px 0 0;font:500 84px/1.05 "PingFang SC","Microsoft YaHei",sans-serif;letter-spacing:-.01em}
h1 small{display:block;margin-top:18px;font-size:32px;line-height:1.35;font-weight:400;color:#333}
.deal{display:inline-flex;align-items:center;gap:14px;margin-top:34px;padding:6px 22px 6px 6px;border-radius:999px;background:#fff;border:1.5px solid #e6e6e6}
.deal b{background:#0052d9;color:#fff;border-radius:999px;padding:8px 18px;font-size:24px}
.deal span{font-size:22px;color:#1a1a1a}
.art{position:absolute;right:56px;top:96px;width:430px;height:430px;background:#fff;border:1px solid #e6e6e6;border-radius:8px}
.art svg{display:block;width:100%;height:100%}
.tags{position:absolute;left:72px;bottom:58px;display:flex;gap:12px;margin:0;padding:0;list-style:none}
.tags li{padding:8px 18px;border-radius:999px;background:#fff;border:1px solid #e6e6e6;font-size:20px;color:#333;white-space:nowrap}
.deal{white-space:nowrap}
.n h1 small{font-size:28px}.n .deal b{font-size:21px}.n .deal span{font-size:19px}.n .tags li{font-size:18px;padding:8px 15px}
"""

# 新语言文案（事实只取英文页现有内容）；缺词直接 KeyError，不回退英文
TXT = {
    "OpenAI + Anthropic": L("OpenAI + Anthropic", "OpenAI + Anthropic", "OpenAI + Anthropic", "OpenAI + Anthropic"),
}
DEAL_I18N = {  # 英文图「About N% off list」；列表价用各语言的「定价」说法（简报术语表）
    "ja": "定価より約{n}%オフ", "ko": "공식 정가 대비 약 {n}% 저렴",
    "es": "Aprox. {n} % menos que la lista", "de": "Rund {n} % unter Listenpreis",
}
DETAIL_I18N = {
    "ja": "入力 {a} · 定価 {o}", "ko": "입력 {a} · 정가 {o}", "es": "Entrada {a} · lista {o}", "de": "Eingabe {a} · Liste {o}",
}
SUB_I18N = {
    "ja": "Tencent Hunyuan の最新モデル：画像理解とエージェント作業", "ko": "Tencent Hunyuan의 최신 모델: 이미지 이해와 에이전트 작업",
    "es": "Lo último de Tencent Hunyuan: visión y trabajo con agentes", "de": "Das Neueste von Tencent Hunyuan: Vision und Agentenarbeit",
}
SAVE = 32  # 「About 32% off list」


def art():
    ink = "#1a1a1a"
    hatch = "".join(f"M{x} 320V{320 - (x - 120) * 200 / 240:.1f}" for x in range(132, 360, 12))
    return (f'<svg viewBox="40 30 500 340"><rect x="96" y="84" width="304" height="256" fill="none" stroke="{ink}" stroke-width="1.2" stroke-dasharray="4 4"/>'
            f'<path d="M60 340H520M512 335l8 5-8 5M60 340V50M55 58l5-8 5 8" fill="none" stroke="{ink}" stroke-width="1.2"/>'
            f'<path d="M120 320H360V120Z" fill="none" stroke="{ink}" stroke-width="1.2"/>'
            f'<path d="{hatch}" fill="none" stroke="{ink}" stroke-width=".7"/>'
            '<circle cx="120" cy="320" r="7" fill="#f6d46b"/><circle cx="360" cy="120" r="7" fill="#7fd6ee"/><circle cx="360" cy="320" r="7" fill="#f6d46b"/>'
            f'<text x="376" y="246" font-size="72" font-family="Georgia, Times New Roman, serif" font-weight="700" fill="{ink}">Hy4</text></svg>')


def fields(lang):
    """返回 (品牌名, 副标题, 折扣标签, 价格说明, 标签列表)。新语言逐项查词表，不回退英文。"""
    p = PRICES[0]
    if lang in nl.NEW:
        a, o = nl.money(p["amount"], lang), nl.money(p["official"], lang)
        deal = DEAL_I18N[lang].format(n=SAVE)
        detail = DETAIL_I18N[lang].format(a=a, o=o)
        tags = [nl.word(t, lang, TXT) for t in ["Image input", "OpenAI + Anthropic", "Unlimited concurrency", nl.ENT_EN]]
        return "Tencent Hunyuan", SUB_I18N[lang], deal, detail, tags
    if lang == "zh":
        return "腾讯混元", "腾讯混元新一代模型，图像理解与 Agent 任务", DEAL_ZH, f'输入 ${p["amount"]} · 官方 ${p["official"]}', ["图像理解", "OpenAI + Anthropic 格式", "并发不限", "对公 · 专票"]
    return "Tencent Hunyuan", "Tencent Hunyuan's latest: vision and agent work", DEAL_EN, f'Input ${p["amount"]} · list ${p["official"]}', [nl.ENT_EN if t == "VAT invoices" else t for t in ["Image input", "OpenAI + Anthropic", "Unlimited concurrency", nl.ENT_EN]]


def page(lang):
    brand, sub, deal, detail, tags = fields(lang)
    lis = "".join(f"<li>{escape(t)}</li>" for t in tags)
    return (f'<!doctype html><html lang="{nl.LANGATTR[lang]}"><head><meta charset="utf-8"><title>Hy4 API</title><style>{CSS}</style></head><body>'
            f'<div class="art">{art()}</div><div class="main"><div class="brand">AnyAIGC <i>×</i> {mark("m", 40)} {brand}</div>'
            f'<h1>Hy4 API<small>{escape(sub)}</small></h1>'
            f'<div class="deal"><b>{escape(deal)}</b><span>{escape(detail)}</span></div></div><ul class="tags">{lis}</ul></body></html>')


# 版面自检配置：右侧图框不能被文字压到，标签不能越出画面
SLUGS = ["hy4"]
CFG = {"scale": ["h1", "h1 small", [".deal b", ".deal span"]], "chips": [".tags li"],
       "check": ["h1", "h1 small", ".deal", ".brand"], "obst": [".art"], "max": [1200, 630]}


def main():
    langs, only, html_only = nl.parse_args(sys.argv, SLUGS)
    if langs:
        jobs = [("hy4", lang, page(lang)) for lang in langs if only is None or "hy4" in only]
        nl.shoot(jobs, str(ROOT), str(OUT), ".playwright-mcp/hy4-og", CFG, html_only)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("zh", "en"):
        (OUT / f"hy4-{lang}.html").write_text(page(lang), encoding="utf-8")
        print(f"hy4-{lang}.html")


if __name__ == "__main__":
    main()
