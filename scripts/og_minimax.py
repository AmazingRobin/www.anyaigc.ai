"""Write 1200 x 630 MiniMax sharing-card HTML for Playwright screenshots.

Usage:
    python scripts/preview.py                          # 先在后台启动预览
    python scripts/og_minimax.py --html-only           # 只写 zh/en 的 HTML 和 manifest
    python scripts/og_minimax.py --langs=ja,ko,es,de   # 只生成指定语言，用无头 Chrome 直接截图到 assets/og/
    python scripts/og_minimax.py --png                 # 重新生成 zh/en 并截图

Open http://localhost:8765/.playwright-mcp/minimax-og/<slug>-<lang>.html
at a 1200 x 630 viewport, then capture assets/og/<slug>-<lang>.png.
The default command only writes HTML and a capture manifest; it does not
launch a browser. Local official MiniMax images and the pinned lobe-icons
logo are shared with the topic pages.
"""

from __future__ import annotations

import argparse
import glob
from html import escape
import json
import os
from pathlib import Path
import subprocess

from minimax_data import MODELS, SLUGS, savings_label


NEW = ("ja", "ko", "es", "de")
LANGATTR = {"zh": "zh-CN", "en": "en", "ja": "ja", "ko": "ko", "es": "es", "de": "de"}

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
    "hailuo": {
        "zh": "海螺 H3 与 H3-Max 极速版，文生与首尾帧图生。",
        "en": "Hailuo H3 and fast H3-Max for text and frame-to-video.",
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

# 新语言副标题，键与 SUBTITLES 一致
SUBTITLES_I18N = {
    "hub": {"ja": "チャットから動画・音声制作まで。", "ko": "대화부터 영상·음성 제작까지.",
            "es": "De las conversaciones inteligentes al vídeo y la voz.", "de": "Vom intelligenten Dialog bis zu Video und Sprache."},
    "chat": {"ja": "コード、ツール呼び出し、エージェントを構築。", "ko": "코드, 도구 호출, 에이전트 워크플로를 구축하세요.",
             "es": "Crea con código, herramientas y flujos de agentes.", "de": "Bauen mit Code, Tools und Agenten-Workflows."},
    "video": {"ja": "マルチモーダル参照、ネイティブ音声付き動画生成。", "ko": "멀티모달 참조, 네이티브 오디오 영상 생성.",
              "es": "Vídeo multimodal con audio nativo.", "de": "Multimodale Videogenerierung mit nativem Audio."},
    "hailuo": {"ja": "Hailuo H3 と高速版 H3-Max、テキスト・先頭末尾フレーム対応。", "ko": "Hailuo H3와 빠른 H3-Max, 텍스트·첫/끝 프레임 영상 생성.",
               "es": "Hailuo H3 y el rápido H3-Max, de texto y fotogramas a vídeo.", "de": "Hailuo H3 und schnelles H3-Max, Text- und Frame-zu-Video."},
    "speech": {"ja": "テキストを自然で表情豊かな音声に。", "ko": "텍스트를 자연스럽고 생생한 음성으로.",
               "es": "Convierte tus palabras en voz natural y expresiva.", "de": "Aus Text wird natürliche, ausdrucksstarke Sprache."},
    "voice-design": {"ja": "テキストで声を描写し、個性を形に。", "ko": "텍스트로 목소리를 설명하고 개성을 입히세요.",
                     "es": "Describe una voz y dale vida.", "de": "Beschreibe eine Stimme und erwecke sie zum Leben."},
}

# 新语言词表，键是英文原文（price_unit_en / category_en / 固定标签）；缺词直接 KeyError，不回退英文
TXT = {
    "1M input tokens": {"ja": "1M 入力トークン", "ko": "1M 입력 토큰", "es": "1M de tokens de entrada", "de": "1M Eingabe-Tokens"},
    "second of 768P output": {"ja": "秒（768P出力）", "ko": "초 (768P 출력)", "es": "segundo de salida 768P", "de": "Sekunde 768P-Ausgabe"},
    "second of H3-Max 480P": {"ja": "秒（H3-Max 480P）", "ko": "초 (H3-Max 480P)", "es": "segundo de H3-Max 480P", "de": "Sekunde H3-Max 480P"},
    "10,000 characters": {"ja": "1万文字", "ko": "1만 자", "es": "10.000 caracteres", "de": "10.000 Zeichen"},
    "Chat": {"ja": "チャット", "ko": "채팅", "es": "Chat", "de": "Chat"},
    "Video": {"ja": "動画", "ko": "비디오", "es": "Vídeo", "de": "Video"},
    "Speech": {"ja": "音声", "ko": "음성", "es": "Voz", "de": "Sprache"},
    "Unlimited concurrency": {"ja": "同時実行数の上限なし", "ko": "동시 실행 제한 없음", "es": "Sin límite de RPM", "de": "Kein RPM-Limit"},
    "One API key": {"ja": "APIキー1つ", "ko": "API 키 하나", "es": "Una sola clave de API", "de": "Ein API-Key"},
    "Save up to 59% vs. official": {"ja": "公式価格より最大59%オフ", "ko": "공식가 대비 최대 59% 할인",
                                    "es": "Hasta 59 % menos que el precio oficial", "de": "Bis zu 59 % günstiger als offiziell"},
    "Save {p}% vs. official": {"ja": "公式価格より{p}%オフ", "ko": "공식가 대비 {p}% 할인",
                               "es": "{p} % menos que el precio oficial", "de": "{p} % günstiger als offiziell"},
    "{n} models": {"ja": "{n}モデル", "ko": "모델 {n}개", "es": "{n} modelos", "de": "{n} Modelle"},
    "MINIMAX / MODEL APIs": {"ja": "MINIMAX / モデル API", "ko": "MINIMAX / 모델 API", "es": "MINIMAX / API DE MODELOS", "de": "MINIMAX / MODELL-APIS"},
    "Pricing & integration": {"ja": "料金と接続ガイド", "ko": "요금 및 연동 가이드", "es": "Precios e integración", "de": "Preise & Integration"},
}


TEMPLATE = """<!doctype html>
<html lang="@LANG@" class="@HC@">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=1200, initial-scale=1">
  <title>@TITLE@ · AnyAIGC</title>
  <style>
    *{box-sizing:border-box}
    html,body{margin:0;width:1200px;height:630px;overflow:hidden}
    body{position:relative;isolation:isolate;background:#11141d;color:#fff;font-family:Arial,"Helvetica Neue","PingFang SC","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",sans-serif;-webkit-font-smoothing:antialiased}
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
    .n .subtitle{font-size:24px;letter-spacing:0}
    .n .chip{font-size:15px;padding:10px 15px}
    .k .subtitle{word-break:keep-all}
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
    if lang in NEW:
        def t(key: str) -> str:
            return TXT[key][lang]
        if model is None:
            return [t("Save up to 59% vs. official"), t("{n} models").format(n=len(MODELS)),
                    t("Unlimited concurrency"), t("One API key")]
        tags = [
            f"${model['price_start']} / {t(model['price_unit_en'])}",
            t(model["category_en"]),
            t("Unlimited concurrency"),
        ]
        label = savings_label("en", model)  # 形如 "Save 59% vs. official"，只取百分比
        if label:
            tags[1] = t("Save {p}% vs. official").format(p=label.split("%")[0].split()[-1])
        return tags
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
    media = "hero-video.webp" if kind in ("video", "hailuo") else "hero-text.webp"
    tags = card_tags(model, lang)
    chips = "".join(
        f'<span class="chip{" price" if index == 0 else ""}">{escape(tag)}</span>'
        for index, tag in enumerate(tags)
    )
    values = {
        "LANG": LANGATTR[lang],
        "HC": ("n" + (" k" if lang == "ko" else "")) if lang in NEW else "",
        "TITLE": escape(title),
        "MEDIA": f"/assets/models/minimax/{media}",
        "LOGO": logo,
        "EYEBROW": TXT["MINIMAX / MODEL APIs"][lang] if lang in NEW else ("MINIMAX / API 模型家族" if lang == "zh" else "MINIMAX / MODEL APIs"),
        "TITLE_CLASS": title_class,
        "HEADING": heading_html,
        "SUBTITLE": escape(SUBTITLES_I18N[kind][lang] if lang in NEW else SUBTITLES[kind][lang]),
        "CHIPS": chips,
        "FOOTER": TXT["Pricing & integration"][lang] if lang in NEW else ("价格与接入指南" if lang == "zh" else "Pricing & integration"),
    }
    html = TEMPLATE
    for token, value in values.items():
        html = html.replace(f"@{token}@", value)
    return html


def chrome() -> str | None:
    hits = sorted(glob.glob(os.path.expanduser("~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe")))
    return hits[-1] if hits else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html-only", action="store_true", help="Only write HTML (the default; screenshots are captured separately).")
    parser.add_argument("--langs", help="逗号分隔的语言，如 ja,ko,es,de；指定后用无头 Chrome 直接截图到 assets/og/ 并删除临时 HTML")
    parser.add_argument("--png", action="store_true", help="不指定 --langs 时也用 Chrome 截图")
    args = parser.parse_args()
    langs = tuple(args.langs.split(",")) if args.langs else ("zh", "en")
    for lang in langs:
        if lang not in LANGATTR:
            raise ValueError(f"Unknown language: {lang}")
    logo = (ROOT / "assets" / "icons" / "minimax-color.svg").read_text(encoding="utf-8").strip()
    OUT.mkdir(parents=True, exist_ok=True)
    captures = []
    for slug in SLUGS:
        if slug != "minimax" and slug not in MODEL_BY_SLUG:
            raise ValueError(f"Unknown MiniMax slug: {slug}")
        for lang in langs:
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
    if args.html_only or not (args.langs or args.png):
        return
    exe = chrome()
    if not exe:
        raise SystemExit("找不到 Playwright 的 Chromium，无法截图")
    from PIL import Image
    for item in captures:
        png = ROOT / item["output"]
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,800",
                        "--virtual-time-budget=6000", f"--screenshot={png}", item["url"]],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        # 无头 Chrome 的窗口尺寸含浏览器边框，截得偏矮；放大窗口再裁成 1200×630
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        print("png", item["output"], png.stat().st_size)
        (OUT / f"{item['name']}.html").unlink()
    (OUT / "manifest.json").unlink()
    if not any(OUT.iterdir()):
        OUT.rmdir()


if __name__ == "__main__":
    main()
