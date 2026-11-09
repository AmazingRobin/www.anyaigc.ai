"""Register the Xiaomi MiMo overview and 4 model guides in both hubs and sitemap.

Run: python scripts/mimo_register.py
The overview is linked from the category heading; model cards retain the site's
shared af-* presentation. Repeated runs replace this category without duplicates.
"""

import json
import re
from html import escape
from pathlib import Path

from mimo_data import CHECKED_DATE, MODELS, SLUGS, deal
from mimo_pages import mark


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.anyaigc.ai"
MODELS_BY_SLUG = {model["slug"]: model for model in MODELS}
COPY = {
    "zh": {
        "category": "Xiaomi MiMo 系列",
        "more": "V2.6 约官方 4 折 · 全系总览",
        "guide": "查看专题 →",
        "overview": "Xiaomi MiMo API（全系总览）",
    },
    "en": {
        "category": "Xiaomi MiMo models",
 "more": "V2.6 at ~40% of official · overview",
        "guide": "View guide →",
        "overview": "Xiaomi MiMo API (overview)",
    },
}


def logo(lang, slug):
    return mark("#1a1a1a", "mi-hub-mark", 26)


def card(lang, model):
    slug = model["slug"]
    category = "对话" if lang == "zh" else "Chat"
    status = deal(lang, model) or ("官方已停用" if lang == "zh" else "Retired by Xiaomi")
    tags = [status, category, model[f"caps_{lang}"][0]]
    tags_html = "\n".join(f"     <li>{escape(tag)}</li>" for tag in tags)
    unit = "百万输入 tokens" if lang == "zh" else "1M input tokens"
    return f'''        <li class="af-model">
          <div class="af-model-head">
     <span class="af-model-logo" style="background:#faf7f3;border:1px solid #ebe4dc" aria-hidden="true">{logo(lang, slug)}</span>
     <div>
       <h3><a href="/{lang}/models/{slug}">{escape(model['name'])} API</a></h3>
       <span class="af-model-cat">Xiaomi MiMo · {escape(category)} · {escape(model['id'])}</span>
     </div>
          </div>
   <p>{escape(model[f'desc_{lang}'])}</p>
          <ul class="af-tags">
{tags_html}
   </ul>
          <div class="af-model-foot">
            <span><strong>${model['prices'][0]['amount']}</strong> / {unit}</span>
            <span class="af-model-go" aria-hidden="true">{COPY[lang]['guide']}</span>
          </div>
        </li>
'''


def category_block(lang):
    copy = COPY[lang]
    cards = "".join(card(lang, model) for model in MODELS)
    return (
        '      <!-- MiMo -->\n'
        f'      <h3 class="af-section-head" id="cat-mimo" style="font-size:16px;margin:24px 0 12px">'
        f'<a class="af-cat-link" href="/{lang}/models/mimo">'
        f'<span class="af-cat-name">{copy["category"]}</span>'
        f'<span class="af-cat-more">{copy["more"]} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>\n'
        f'      <ul class="af-models">\n{cards}      </ul>\n'
        '      <!-- /MiMo -->\n'
    )


def hub(lang):
    path = ROOT / lang / "models/index.html"
    original = path.read_text(encoding="utf-8")
    content = original
    block = category_block(lang)
    if "<!-- MiMo -->" in content:
        content, count = re.subn(
            r'      <!-- MiMo -->\n.*?      <!-- /MiMo -->\n',
            lambda _: block, content, count=1, flags=re.S,
        )
        assert count == 1, "MiMo category markers are malformed"
    else:
        anchor = '      <!-- MiniMax -->'
        assert anchor in content, "MiniMax category insertion anchor is missing"
        content = content.replace(anchor, block + "\n" + anchor, 1)

    filter_link = f'<li><a href="#cat-mimo">{COPY[lang]["category"]}</a></li>'
    if 'href="#cat-mimo"' in content:
        content = re.sub(r'<li><a href="#cat-mimo">[^<]*</a></li>', filter_link, content, count=1)
    else:
        content, count = re.subn(
            r'(<li><a href="#cat-minimax">[^<]*</a></li>)',
            lambda match: filter_link + "\n        " + match.group(1), content, count=1,
        )
        assert count == 1, "MiniMax filter insertion anchor is missing"

    match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', content, re.S)
    assert match, "Hub JSON-LD is missing"
    graph = json.loads(match.group(1))
    nodes = graph.get("@graph", [graph])
    urls = {f"{SITE}/{lang}/models/{slug}" for slug in SLUGS}
    for node in nodes:
        if node.get("@type") != "ItemList":
            continue
        items = [item for item in node["itemListElement"] if item["url"] not in urls]
        for slug in SLUGS:
            name = COPY[lang]["overview"] if slug == "mimo" else f"{MODELS_BY_SLUG[slug]['name']} API"
            items.append({"@type": "ListItem", "name": name, "url": f"{SITE}/{lang}/models/{slug}"})
        for position, item in enumerate(items, 1):
            item["position"] = position
        node["itemListElement"] = items
        node["numberOfItems"] = len(items)
    content = content[:match.start(1)] + json.dumps(graph, ensure_ascii=False, indent=2) + content[match.end(1):]
    if content != original:
        path.write_text(content, encoding="utf-8", newline="\n")
    return content != original


def sitemap_entry(lang, slug):
    return (
        f'  <url>\n    <loc>{SITE}/{lang}/models/{slug}</loc>\n    <lastmod>{CHECKED_DATE}</lastmod>\n'
        f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}/zh/models/{slug}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/models/{slug}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/en/models/{slug}"/>\n'
        '  </url>\n'
    )


def sitemap():
    path = ROOT / "sitemap.xml"
    original = path.read_text(encoding="utf-8")
    content = original
    missing = []
    for slug in SLUGS:
        for lang in ("zh", "en"):
            url = f"{SITE}/{lang}/models/{slug}"
            pattern = r'  <url>\s*<loc>' + re.escape(url) + r'</loc>.*?</url>\n?'
            entry = sitemap_entry(lang, slug)
            if f"<loc>{url}</loc>" in content:
                content, count = re.subn(pattern, lambda _: entry, content, count=1, flags=re.S)
                assert count == 1, f"Could not update sitemap entry: {url}"
            else:
                missing.append(entry)
    content = content.replace("</urlset>", "".join(missing) + "</urlset>")
    content = re.sub(
        r'(<loc>https://www\.anyaigc\.ai/(?:zh|en)/models/</loc>\s*<lastmod>)[^<]+',
        lambda match: match.group(1) + CHECKED_DATE, content,
    )
    if content != original:
        path.write_text(content, encoding="utf-8", newline="\n")
    return content != original


if __name__ == "__main__":
    print("hub zh:", hub("zh"), "hub en:", hub("en"), "sitemap:", sitemap())
