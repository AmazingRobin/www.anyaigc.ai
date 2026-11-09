"""Write 1200 x 630 MiniMax sharing-card HTML for Playwright screenshots.

Usage:
    python scripts/og_minimax.py --html-only
    python scripts/preview.py

Open http://localhost:8765/.playwright-mcp/minimax-og/<slug>-<lang>.html
at a 1200 x 630 viewport, then capture assets/og/<slug>-<lang>.png.
The default command only writes HTML and a capture manifest; it does not
launch a browser. Local official MiniMax images and the pinned lobe-icons
logo are shared with the topic pages.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path

from minimax_data import MODELS, SLUGS, savings_label


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".playwright-mcp" / "minimax-og"
MODEL_BY_SLUG = {model["slug"]: model for model in MODELS}

SUBTITLES = {
    "hub": {
        "zh": "从智能对话，到视频与语音创作。",
        "en": "From intelligent conversations to video and speech.",
    },
    "chat": {
        "zh": "编程、工具调用与 Agent 工作流。",
        "en": "Build with code, tools, and agent workflows.",
    },
    "video": {
        "zh": "多模态参考，原生音画视频生成。",
        "en": "Multimodal video generation with native audio.",
    },
    "speech": {
        "zh": "把文字转化为自然、生动的声音。",
        "en": "Turn your words into natural, expressive speech.",
    },
    "voice-design": {
        "zh": "用文字描述，设计你的专属音色。",
        "en": "Describe a voice. Bring its character to life.",
    },
}


TEMPLATE = """<!doctype html>
<html lang="@LANG@">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=1200, initial-scale=1">
  <title>@TITLE@ · AnyAIGC</title>
  <style>
    *{box-sizing:border-box}
    html,body{margin:0;width:1200px;height:630px;overflow:hidden}
    body{position:relative;isolation:isolate;background:#11141d;color:#fff;font-family:Arial,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;-webkit-font-smoothing:antialiased}
    .media{position:absolute;inset:0;width:1200px;height:630px;object-fit:cover;object-position:center;z-index:-3}
    .shade{position:absolute;inset:0;z-index:-2;background:linear-gradient(90deg,rgba(7,10,19,.91) 0%,rgba(9,13,23,.75) 43%,rgba(10,14,24,.28) 80%),linear-gradient(0deg,rgba(8,11,20,.78),transparent 42%,rgba(8,11,20,.18))}
    .glow{position:absolute;inset:0;z-index:-1;background:radial-gradient(ellipse at 8% 110%,rgba(197,66,108,.18),transparent 65%)}
    .top{position:absolute;left:64px;right:64px;top:47px;display:flex;align-items:center;justify-content:space-between}
    .brand{font-size:25px;font-weight:700;letter-spacing:-1px}
    .provider{display:flex;align-items:center;gap:11px;font-size:19px;font-weight:500;letter-spacing:-.5px}
    .provider svg{width:33px;height:33px;overflow:visible}
    .provider span{color:rgba(255,255,255,.85)}
    .content{position:absolute;left:64px;right:64px;top:170px}
    .eyebrow{font-size:13px;font-weight:400;line-height:1.5;letter-spacing:.13em;color:rgba(255,255,255,.58);margin:0 0 22px}
    h1{margin:0;max-width:1072px;font-size:78px;font-weight:500;line-height:1.08;letter-spacing:-3.6px}
    h1 span{display:block;white-space:nowrap}
    h1.two-lines{font-size:67px;line-height:1.08;letter-spacing:-2.7px}
    h1.compact{font-size:70px;letter-spacing:-3px}
    .subtitle{margin:24px 0 0;max-width:1040px;font-size:25px;font-weight:400;line-height:1.5;letter-spacing:-.25px;color:rgba(255,255,255,.72);white-space:nowrap}
    .two-lines+.subtitle{margin-top:20px}
    .bottom{position:absolute;left:64px;right:64px;bottom:39px}
    .chips{display:flex;align-items:center;gap:11px;margin-bottom:30px}
    .chip{display:flex;align-items:center;min-height:42px;padding:10px 17px;border:1px solid rgba(255,255,255,.25);border-radius:100px;font-size:16px;font-weight:400;line-height:1.3;color:rgba(255,255,255,.85);white-space:nowrap;background:rgba(255,255,255,.035)}
    .chip.price{background:#fff;border-color:#fff;color:#18181b;font-weight:500}
    .foot{display:flex;align-items:center;justify-content:space-between;padding-top:17px;border-top:1px solid rgba(255,255,255,.2);font-size:12px;line-height:1.5;letter-spacing:.02em;color:rgba(255,255,255,.5)}
    .foot .arrow{font-size:18px;line-height:1;color:rgba(255,255,255,.72)}
  </style>
</head>
<body>
  <img class="media" src="@MEDIA@" alt="">
  <div class="shade"></div><div class="glow"></div>
  <div class="top"><span class="brand">AnyAIGC</span><div class="provider">@LOGO@<span>MiniMax</span></div></div>
  <main class="content">
    <p class="eyebrow">@EYEBROW@</p>
    <h1 class="@TITLE_CLASS@">@HEADING@</h1>
    <p class="subtitle">@SUBTITLE@</p>
  </main>
  <div class="bottom">
    <div class="chips">@CHIPS@</div>
    <div class="foot"><span>www.anyaigc.ai</span><span>@FOOTER@ <span class="arrow">↗</span></span></div>
  </div>
</body>
</html>
"""


def heading(model: dict | None) -> tuple[str, str, str]:
    """Use intentional lines instead of shrinking long Speech names to fit."""
    if model is None:
        return "MiniMax API", "", "<span>MiniMax API</span>"
    name = model["name"]
    title = f"{name} API"
    if model["kind"] == "speech":
        line = f"{model['version']} {model['voice_tier'].upper()} API"
        return title, "two-lines", f"<span>MiniMax Speech</span><span>{escape(line)}</span>"
    if model["kind"] == "voice-design":
        return title, "two-lines", "<span>MiniMax</span><span>Voice Design API</span>"
    return title, "compact" if len(title) > 21 else "", f"<span>{escape(title)}</span>"


def card_tags(model: dict | None, lang: str) -> list[str]:
    if model is None:
        return (["低至约官方 4 折 · 省 59%", f"{len(MODELS)} 个模型", "不限并发", "一个 API Key"]
                if lang == "zh" else
                ["Save up to 59% vs. official", f"{len(MODELS)} models", "Unlimited concurrency", "One API key"])
    tags = [
        f"${model['price_start']} / {model[f'price_unit_{lang}']}",
        model[f"category_{lang}"],
        "不限并发" if lang == "zh" else "Unlimited concurrency",
    ]
    if savings_label(lang, model):
        tags[1] = savings_label(lang, model)
    return tags


def render(slug: str, lang: str, logo: str) -> str:
    model = MODEL_BY_SLUG.get(slug)
    kind = model["kind"] if model else "hub"
    title, title_class, heading_html = heading(model)
    media = "hero-video.webp" if kind == "video" else "hero-text.webp"
    tags = card_tags(model, lang)
    chips = "".join(
        f'<span class="chip{" price" if index == 0 else ""}">{escape(tag)}</span>'
        for index, tag in enumerate(tags)
    )
    values = {
        "LANG": "zh-CN" if lang == "zh" else "en",
        "TITLE": escape(title),
        "MEDIA": f"/assets/models/minimax/{media}",
        "LOGO": logo,
        "EYEBROW": "MINIMAX / API 模型家族" if lang == "zh" else "MINIMAX / MODEL APIs",
        "TITLE_CLASS": title_class,
        "HEADING": heading_html,
        "SUBTITLE": escape(SUBTITLES[kind][lang]),
        "CHIPS": chips,
        "FOOTER": "价格与接入指南" if lang == "zh" else "Pricing & integration",
    }
    html = TEMPLATE
    for token, value in values.items():
        html = html.replace(f"@{token}@", value)
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-only", action="store_true", help="Only write HTML (the default; screenshots are captured separately).")
    parser.parse_args()
    logo = (ROOT / "assets" / "icons" / "minimax-color.svg").read_text(encoding="utf-8").strip()
    OUT.mkdir(parents=True, exist_ok=True)
    captures = []
    for slug in SLUGS:
        if slug != "minimax" and slug not in MODEL_BY_SLUG:
            raise ValueError(f"Unknown MiniMax slug: {slug}")
        for lang in ("zh", "en"):
            name = f"{slug}-{lang}"
            source = OUT / f"{name}.html"
            source.write_text(render(slug, lang, logo), encoding="utf-8")
            captures.append({
                "name": name,
                "url": f"http://localhost:8765/.playwright-mcp/minimax-og/{name}.html",
                "output": f"assets/og/{name}.png",
                "width": 1200,
                "height": 630,
            })
    (OUT / "manifest.json").write_text(json.dumps(captures, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(captures)} MiniMax sharing-card HTML files in {OUT.relative_to(ROOT)}")
    print("Screenshot targets: assets/og/<slug>-<lang>.png (1200 x 630)")
    print(f"Capture manifest: {(OUT / 'manifest.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
