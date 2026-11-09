"""Write 1200x630 Xiaomi MiMo sharing-card HTML for Playwright screenshots.

Usage:
    python scripts/og_mimo.py   -> .playwright-mcp/mimo-og/<slug>-<lang>.html
Then (with python scripts/preview.py running) open
http://localhost:8765/.playwright-mcp/mimo-og/<slug>-<lang>.html at 1200x630 and
capture assets/og/<slug>-<lang>.png. Uses the official V2.6 halftone poster
already in assets/models/mimo/ and the pinned lobe-icons logo.
"""
from html import escape
from pathlib import Path

from mimo_data import MODELS, MODEL_BY_SLUG, SLUGS, deal
from mimo_pages import mark

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".playwright-mcp" / "mimo-og"

CSS = """
*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{background:#fcfaf8;color:#1a1a1a;font-family:Inter,-apple-system,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;position:relative}
.art{position:absolute;right:-40px;top:0;width:620px;height:630px;background:url(/assets/models/mimo/hero.webp) 58% 50%/cover;
 -webkit-mask-image:linear-gradient(90deg,transparent,#000 38%);mask-image:linear-gradient(90deg,transparent,#000 38%)}
.dots{position:absolute;right:-40px;top:0;width:620px;height:630px;background-color:#f3f1ea;
 background-image:radial-gradient(circle,rgba(82,110,62,.55) 1.8px,transparent 2.2px),radial-gradient(circle,rgba(82,110,62,.3) 1.8px,transparent 2.2px);
 background-size:14px 14px;background-position:0 0,7px 7px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 38%);mask-image:linear-gradient(90deg,transparent,#000 38%)}
.dots b{position:absolute;right:90px;top:200px;font:700 190px/1 Georgia,serif;color:#526e3e}
.main{position:absolute;left:72px;top:64px;width:700px}
.brand{display:flex;align-items:center;gap:14px;font-weight:700;font-size:26px}
.brand i{font-style:normal;color:rgba(0,0,0,.4);font-weight:400}
h1{margin:70px 0 0;font:400 76px/1.08 "LXGW WenKai","Kaiti SC","STKaiti","KaiTi",Georgia,serif;letter-spacing:.01em}
h1 small{display:block;margin-top:18px;font-size:34px;color:#333}
.deal{display:inline-flex;align-items:center;gap:14px;margin-top:34px;padding:6px 22px 6px 6px;border-radius:999px;background:#fff;border:1.5px solid #ffd2b0}
.deal b{background:#ff6700;color:#fff;border-radius:999px;padding:8px 18px;font-size:24px}
.deal span{font-size:22px;color:#5a2a06}
.old{background:#ece7df;border-color:#e0d8cc}.old b{background:#5d4c46}
.tags{position:absolute;left:72px;bottom:58px;display:flex;gap:12px;margin:0;padding:0;list-style:none}
.tags li{padding:8px 18px;border-radius:999px;background:#f0ebe5;font-size:20px;color:#333}
"""

TEXT = {
    "mimo": {"zh": ("Xiaomi MiMo API", "官方 4 折，接入 V2.6 全模态旗舰"), "en": ("Xiaomi MiMo API", "V2.6 omni-modal models at 60% off")},
}


def page(lang, slug):
    model = MODEL_BY_SLUG.get(slug)
    zh = lang == "zh"
    if model is None:
        title, sub = TEXT["mimo"][lang]
        detail = "V2.6-Flash 输入 $0.0563 · 官方 $0.14" if zh else "V2.6-Flash input $0.0563 · official $0.14"
        chip, cls = deal(lang), ""
    elif model["legacy"]:
        succ = MODEL_BY_SLUG[model["successor"]]
        title, sub = model["name"] + " API", ("官方已停用 · 迁移到 " + succ["name"]) if zh else ("Retired · move to " + succ["name"])
        detail = f'{"替代型号约官方 4 折" if zh else "Replacement at about 60% off"}'
        chip, cls = ("已停用" if zh else "Retired"), " old"
    else:
        p = model["prices"][0]
        title, sub = model["name"] + " API", model["tagline_" + lang]
        detail = (f'输入 ${p["amount"]} · 官方 ${p["official"]}' if zh else f'Input ${p["amount"]} · official ${p["official"]}')
        chip, cls = deal(lang), ""
    tags = ["1M 上下文", "OpenAI 兼容", "并发不限", "对公 · 专票"] if zh else ["1M context", "OpenAI compatible", "Unlimited concurrency", "VAT invoices"]
    if model and model["legacy"]:
        tags[0] = "迁移只改 model" if zh else "Drop-in migration"
    art = '<div class="dots"><b>' + escape(model["short"].split(" ")[0]) + "</b></div>" if model and model["legacy"] else '<div class="art"></div>'
    lis = "".join(f"<li>{escape(t)}</li>" for t in tags)
    return (f'<!doctype html><html lang="{"zh-CN" if zh else "en"}"><head><meta charset="utf-8"><title>{escape(title)}</title><style>{CSS}</style></head><body>'
     f'{art}<div class="main"><div class="brand">AnyAIGC <i>×</i> {mark("#1a1a1a", "m", 40)} Xiaomi MiMo</div>'
     f'<h1>{escape(title)}<small>{escape(sub)}</small></h1>'
     f'<div class="deal{cls}"><b>{escape(chip)}</b><span>{escape(detail)}</span></div></div><ul class="tags">{lis}</ul></body></html>')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("zh", "en"):
        for slug in SLUGS:
            (OUT / f"{slug}-{lang}.html").write_text(page(lang, slug), encoding="utf-8")
            print(f"{slug}-{lang}.html")


if __name__ == "__main__":
    main()
