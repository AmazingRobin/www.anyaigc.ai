"""Register the Tencent Hy4 guide in both hubs and the sitemap, idempotently.

Run: python scripts/hy4_register.py
"""

import json
import re
from html import escape
from pathlib import Path

from hy4_data import CHECKED_DATE, SLUG, NAME, PRICES
from hy4_pages import mark, DEAL_ZH, DEAL_EN

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.anyaigc.ai"
COPY = {
    "zh": dict(category="腾讯混元", vendor="腾讯混元 Tencent Hunyuan", unit="1M 输入", go="查看专题 →",
               desc="腾讯混元 Hy4 正式版，强化 Agent 与长程任务，首次支持图像理解，OpenAI 与 Anthropic 两种接口格式。",
               tags=[DEAL_ZH, "图像理解", "并发不限"]),
    "en": dict(category="Tencent Hunyuan", vendor="Tencent Hunyuan", unit="1M input", go="View guide →",
               desc="Tencent Hunyuan's official Hy4 release: stronger agents and long-horizon work, image understanding, OpenAI and Anthropic formats.",
               tags=[DEAL_EN, "Image understanding", "Unlimited concurrency"]),
}


def block(lang):
    c = COPY[lang]
    price = PRICES[0]["amount"]
    tags = "\n".join(f"            <li>{escape(t)}</li>" for t in c["tags"])
    return (
        '      <!-- Hy4 -->\n'
        f'      <h3 class="af-section-head" id="cat-hy4" style="font-size:16px;margin:24px 0 12px">{escape(c["category"])}</h3>\n'
        '      <ul class="af-models">\n'
        '        <li class="af-model">\n'
        '          <div class="af-model-head">\n'
        f'            <span class="af-model-logo" style="background:#ffffff;border:1px solid #e6e6e6" aria-hidden="true">{mark("hy-hub-mark", 26)}</span>\n'
        f'            <div><h3><a href="/{lang}/models/{SLUG}">{NAME} API</a></h3>'
        f'<span class="af-model-cat">{escape(c["vendor"])} · hy4</span></div>\n'
        '          </div>\n'
        f'          <p>{escape(c["desc"])}</p>\n'
        f'          <ul class="af-tags">\n{tags}\n          </ul>\n'
        f'          <div class="af-model-foot"><span><strong>${price}</strong> / {c["unit"]}</span>'
        f'<span class="af-model-go" aria-hidden="true">{c["go"]}</span></div>\n'
        '        </li>\n'
        '      </ul>\n'
        '      <!-- /Hy4 -->\n'
    )


def hub(lang):
    path = ROOT / lang / "models/index.html"
    original = path.read_text(encoding="utf-8")
    content = original
    new = block(lang)
    # Drop any earlier block, then insert before DeepSeek's heading. That heading sits
    # ABOVE the "<!-- DeepSeek -->" comment, so anchoring on the comment splits it from its cards.
    content = re.sub(r'      <!-- Hy4 -->\n.*?      <!-- /Hy4 -->\n\n?', '', content, count=1, flags=re.S)
    anchor = re.search(r'^      <h3 class="af-section-head" id="cat-deepseek"', content, re.M)
    assert anchor, "DeepSeek heading anchor missing"
    content = content[:anchor.start()] + new + "\n" + content[anchor.start():]
    link = f'<li><a href="#cat-hy4">{COPY[lang]["category"]}</a></li>'
    if 'href="#cat-hy4"' in content:
        content = re.sub(r'<li><a href="#cat-hy4">[^<]*</a></li>', link, content, count=1)
    else:
        content, n = re.subn(r'(<li><a href="#cat-deepseek">[^<]*</a></li>)', lambda m: link + "\n        " + m.group(1), content, count=1)
        assert n == 1
    content = re.sub(r'("dateModified": ")[^"]+', lambda m: m.group(1) + CHECKED_DATE, content, count=1)
    m = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', content, re.S)
    graph = json.loads(m.group(1))
    target = f"{SITE}/{lang}/models/{SLUG}"
    for node in graph.get("@graph", [graph]):
        if node.get("@type") != "ItemList":
            continue
        items = [i for i in node["itemListElement"] if i["url"] != target]
        items.append({"@type": "ListItem", "name": f"{NAME} API", "url": target})
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
