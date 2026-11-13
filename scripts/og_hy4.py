"""Write 1200x630 Hy4 sharing-card HTML for Playwright screenshots.

Usage: python scripts/og_hy4.py  -> .playwright-mcp/hy4-og/hy4-<lang>.html
Screenshot each at 1200x630 into assets/og/hy4-<lang>.png, then delete the temp HTML.
"""
from html import escape
from pathlib import Path

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
.tags li{padding:8px 18px;border-radius:999px;background:#fff;border:1px solid #e6e6e6;font-size:20px;color:#333}
"""


def art():
    ink = "#1a1a1a"
    hatch = "".join(f"M{x} 320V{320 - (x - 120) * 200 / 240:.1f}" for x in range(132, 360, 12))
    return (f'<svg viewBox="40 30 500 340"><rect x="96" y="84" width="304" height="256" fill="none" stroke="{ink}" stroke-width="1.2" stroke-dasharray="4 4"/>'
            f'<path d="M60 340H520M512 335l8 5-8 5M60 340V50M55 58l5-8 5 8" fill="none" stroke="{ink}" stroke-width="1.2"/>'
            f'<path d="M120 320H360V120Z" fill="none" stroke="{ink}" stroke-width="1.2"/>'
            f'<path d="{hatch}" fill="none" stroke="{ink}" stroke-width=".7"/>'
            '<circle cx="120" cy="320" r="7" fill="#f6d46b"/><circle cx="360" cy="120" r="7" fill="#7fd6ee"/><circle cx="360" cy="320" r="7" fill="#f6d46b"/>'
            f'<text x="376" y="246" font-size="72" font-family="Georgia, Times New Roman, serif" font-weight="700" fill="{ink}">Hy4</text></svg>')


def page(lang):
    zh = lang == "zh"
    p = PRICES[0]
    sub = "腾讯混元新一代模型，图像理解与 Agent 任务" if zh else "Tencent Hunyuan's latest: vision and agent work"
    detail = f'输入 ${p["amount"]} · 官方 ${p["official"]}' if zh else f'Input ${p["amount"]} · list ${p["official"]}'
    tags = ["图像理解", "OpenAI + Anthropic 格式", "并发不限", "对公 · 专票"] if zh else ["Image input", "OpenAI + Anthropic", "Unlimited concurrency", "VAT invoices"]
    lis = "".join(f"<li>{escape(t)}</li>" for t in tags)
    return (f'<!doctype html><html lang="{"zh-CN" if zh else "en"}"><head><meta charset="utf-8"><title>Hy4 API</title><style>{CSS}</style></head><body>'
            f'<div class="art">{art()}</div><div class="main"><div class="brand">AnyAIGC <i>×</i> {mark("m", 40)} {"腾讯混元" if zh else "Tencent Hunyuan"}</div>'
            f'<h1>Hy4 API<small>{escape(sub)}</small></h1>'
            f'<div class="deal"><b>{escape(DEAL_ZH if zh else DEAL_EN)}</b><span>{escape(detail)}</span></div></div><ul class="tags">{lis}</ul></body></html>')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("zh", "en"):
        (OUT / f"hy4-{lang}.html").write_text(page(lang), encoding="utf-8")
        print(f"hy4-{lang}.html")


if __name__ == "__main__":
    main()
