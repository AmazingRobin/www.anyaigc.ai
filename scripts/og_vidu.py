"""Render 1200x630 Vidu share cards: python scripts/og_vidu.py

Writes temporary HTML to .playwright-mcp/vidu-og/ and screenshots each card
to assets/og/<slug>-<lang>.png: run python scripts/preview.py, open
http://localhost:8765/.playwright-mcp/vidu-og/<slug>-<lang>.html at
1200x630 in Playwright, screenshot, then delete .playwright-mcp/vidu-og/. Background
frames are the local Vidu poster images; logo is the pinned lobe-icons SVG.
"""

import re
from pathlib import Path

from vidu_data import MODELS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".playwright-mcp" / "vidu-og"
ICON = (ROOT / "assets/icons/vidu-color.svg").read_text(encoding="utf-8")
ICON = re.sub(r"<title>.*?</title>", "", ICON).replace('height="1em"', 'height="64"').replace('width="1em"', 'width="64"')

CARDS = [dict(slug="vidu", name="Vidu API", media="football",
              sub_zh="Q4 · Q3 · Q2 视频与图像，一个 Key 全部接入", sub_en="Q4, Q3 and Q2 video plus image, one API key",
              tags_zh=["7 个模型", "视频 $0.0223 起", "并发不限", "对公 · 专票"],
              tags_en=["7 models", "Video from $0.0223", "Unlimited concurrency", "VAT invoices"])]
for m in MODELS:
    CARDS.append(dict(slug=m["slug"], name=m["name"] + " API", media=m["media"],
                      sub_zh=m["title_zh"] + " · " + m["id"], sub_en=m["title_en"] + " · " + m["id"],
                      tags_zh=m["caps_zh"][:2] + [f'${m["start"]} 起', "并发不限"],
                      tags_en=m["caps_en"][:2] + [f'From ${m["start"]}', "Unlimited concurrency"]))

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;box-sizing:border-box}html,body{width:1200px;height:630px;overflow:hidden;background:#020b13;color:#fff;
font-family:-apple-system,"PingFang SC","Microsoft YaHei","Segoe UI",Arial,sans-serif}
.bg{position:absolute;inset:0;background:url(../../assets/models/vidu/__MEDIA__.webp) center/cover}
.sh{position:absolute;inset:0;background:linear-gradient(90deg,#020b13 0%,rgba(2,11,19,.86) 42%,rgba(2,11,19,.2) 78%),linear-gradient(0deg,rgba(2,11,19,.8),transparent 45%)}
.c{position:absolute;left:72px;top:64px;right:72px;bottom:60px;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:16px;font-size:26px;font-weight:700;letter-spacing:-.3px}
.top span{font-weight:500;color:rgba(255,255,255,.6);padding-left:16px;border-left:1px solid rgba(255,255,255,.25)}
h1{margin-top:auto;font-size:__SIZE__px;line-height:1.02;font-weight:800;letter-spacing:-2px;max-width:820px}
p{margin-top:20px;font-size:30px;color:rgba(255,255,255,.85);max-width:820px}
ul{display:flex;flex-wrap:wrap;gap:12px;margin-top:34px;padding:0;list-style:none}
li{padding:9px 20px;border-radius:999px;font-size:22px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22)}
li:first-child{background:linear-gradient(100deg,#40edd8,#22d5ff 35%,#047ffe);color:#020b13;font-weight:700;border:0}
</style></head><body><div class="bg"></div><div class="sh"></div><div class="c">
<div class="top">__ICON__AnyAIGC<span>Vidu</span></div><h1>__NAME__</h1><p>__SUB__</p><ul>__TAGS__</ul></div></body></html>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for c in CARDS:
        for lang in ("zh", "en"):
            size = 96 if len(c["name"]) <= 18 else 80
            html = (TPL.replace("__MEDIA__", c["media"]).replace("__ICON__", ICON).replace("__NAME__", c["name"])
                    .replace("__SIZE__", str(size)).replace("__SUB__", c["sub_" + lang])
                    .replace("__TAGS__", "".join(f"<li>{t}</li>" for t in c["tags_" + lang])))
            path = OUT / f'{c["slug"]}-{lang}.html'
            path.write_text(html, encoding="utf-8")
            jobs.append((path, ROOT / "assets/og" / f'{c["slug"]}-{lang}.png'))
    print(len(jobs), "cards written to", OUT)


if __name__ == "__main__":
    main()
