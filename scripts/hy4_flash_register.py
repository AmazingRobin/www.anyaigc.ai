"""Register the Tencent Hy4 flash guide in both hubs and the sitemap, idempotently.

Run: python scripts/hy4_flash_register.py

Hy4 flash joins the existing "腾讯混元 / Tencent Hunyuan" category, so its card goes into the
Hy4 group instead of opening a new category. Run hy4_register.py first if the Hy4 block
itself is rebuilt: that script rewrites the whole group, and this one adds the Flash card back.
"""

import json
import re
from html import escape
from pathlib import Path

from hy4_flash_data import CHECKED_DATE, SLUG, NAME, PRICES
from hy4_flash_pages import mark, DEAL_ZH, DEAL_EN

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.anyaigc.ai"
START, END = "        <!-- Hy4 Flash -->\n", "        <!-- /Hy4 Flash -->\n"
COPY = {
    "zh": dict(vendor="腾讯混元 Tencent Hunyuan", unit="1M 输入", go="查看专题 →",
               desc="腾讯混元 Hy4 flash，面向日常工作的高性价比模型，总参数 224B、激活 12B，支持图像理解与 1M 上下文，OpenAI 与 Anthropic 两种接口格式。",
               tags=[DEAL_ZH, "图像理解", "1M 上下文"]),
    "en": dict(vendor="Tencent Hunyuan", unit="1M input", go="View guide →",
               desc="Tencent Hunyuan's Hy4 flash, a low-cost model for everyday work: 224B total and 12B active parameters, image input, a 1M-token context, OpenAI and Anthropic formats.",
               tags=[DEAL_EN, "Image understanding", "1M context"]),
}


def card(lang):
    c = COPY[lang]
    price = PRICES[0]["amount"]
    tags = "\n".join(f"            <li>{escape(t)}</li>" for t in c["tags"])
    return (
        START +
        '        <li class="af-model">\n'
        '          <div class="af-model-head">\n'
        f'            <span class="af-model-logo" style="background:#ffffff;border:1px solid #e6e6e6" aria-hidden="true">{mark("hy-hub-mark", 26)}</span>\n'
        f'            <div><h3><a href="/{lang}/models/{SLUG}">{NAME} API</a></h3>'
        f'<span class="af-model-cat">{escape(c["vendor"])} · {SLUG}</span></div>\n'
        '          </div>\n'
        f'          <p>{escape(c["desc"])}</p>\n'
        f'          <ul class="af-tags">\n{tags}\n          </ul>\n'
        f'          <div class="af-model-foot"><span><strong>${price}</strong> / {c["unit"]}</span>'
        f'<span class="af-model-go" aria-hidden="true">{c["go"]}</span></div>\n'
        '        </li>\n' +
        END
    )


def hub(lang):
    path = ROOT / lang / "models/index.html"
    original = path.read_text(encoding="utf-8")
    content = original
    # Drop an earlier Flash card, then add it again at the end of the Hy4 group.
    content = re.sub(re.escape(START) + r".*?" + re.escape(END), "", content, count=1, flags=re.S)
    anchor = "      </ul>\n      <!-- /Hy4 -->"
    assert content.count(anchor) == 1, "Hy4 group end marker missing: run hy4_register.py first"
    content = content.replace(anchor, card(lang) + anchor, 1)
    content = re.sub(r'("dateModified": ")[^"]+', lambda m: m.group(1) + CHECKED_DATE, content, count=1)
    m = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', content, re.S)
    graph = json.loads(m.group(1))
    target = f"{SITE}/{lang}/models/{SLUG}"
    hy4 = f"{SITE}/{lang}/models/hy4"
    for node in graph.get("@graph", [graph]):
        if node.get("@type") != "ItemList":
            continue
        items = [i for i in node["itemListElement"] if i["url"] != target]
        at = next((k for k, i in enumerate(items) if i["url"] == hy4), len(items) - 1)
        items.insert(at + 1, {"@type": "ListItem", "name": f"{NAME} API", "url": target})
        for pos, item in enumerate(items, 1):
            item["position"] = pos
        node["itemListElement"] = items
        node["numberOfItems"] = len(items)
    content = content[:m.start(1)] + json.dumps(graph, ensure_ascii=False, indent=2) + content[m.end(1):]
    if content != original:
        path.write_text(content, encoding="utf-8", newline="\n")
    return content != original


def entry(lang):
    return (
        f'  <url>\n    <loc>{SITE}/{lang}/models/{SLUG}</loc>\n    <lastmod>{CHECKED_DATE}</lastmod>\n'
        f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{SLUG}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{SLUG}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{SLUG}"/>\n'
        '  </url>\n')


def sitemap():
    path = ROOT / "sitemap.xml"
    original = path.read_text(encoding="utf-8")
    content, missing = original, []
    for lang in ("zh", "en"):
        loc = f"{SITE}/{lang}/models/{SLUG}"
        if f"<loc>{loc}</loc>" in content:
            content = re.sub(r'  <url>\s*<loc>' + re.escape(loc) + r'</loc>.*?</url>\n?', lambda _: entry(lang), content, count=1, flags=re.S)
        else:
            missing.append(entry(lang))
    content = content.replace("</urlset>", "".join(missing) + "</urlset>")
    content = re.sub(r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+', lambda m: m.group(1) + CHECKED_DATE, content)
    if content != original:
        path.write_text(content, encoding="utf-8", newline="\n")
    return content != original


if __name__ == "__main__":
    print("hub zh:", hub("zh"), "hub en:", hub("en"), "sitemap:", sitemap())
