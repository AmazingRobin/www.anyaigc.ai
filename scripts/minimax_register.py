"""Register the MiniMax overview and 12 model guides in both hubs and sitemap.

Run: python scripts/minimax_register.py
The overview is linked from the category heading; model cards retain the site's
shared af-* presentation. Repeated runs replace this category without duplicates.
"""

import json
import re
from html import escape
from pathlib import Path

from minimax_data import CHECKED_DATE, MODELS, SLUGS, savings_label


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.anyaigc.ai"
MODELS_BY_SLUG = {model["slug"]: model for model in MODELS}
COPY = {
    "zh": {
        "category": "MiniMax 系列",
        "more": "低至约官方 4 折 · 全系总览",
        "guide": "查看专题 →",
        "overview": "MiniMax API（全系总览）",
    },
    "en": {
        "category": "MiniMax models",
        "more": "Save up to 59% vs. official · overview",
        "guide": "View guide →",
        "overview": "MiniMax API (overview)",
    },
}


def logo(lang, slug):
    svg = (ROOT / "assets/icons/minimax-color.svg").read_text(encoding="utf-8").strip()
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    svg = re.sub(r'\b(?:height|width)="1em"', lambda match: match.group(0).replace("1em", "26"), svg)
    # Each inline gradient needs a unique id within the hub document.
    for identifier in re.findall(r'\bid="([^"]+)"', svg):
        unique = f"minimax-hub-{lang}-{slug}-{identifier}"
        svg = svg.replace(f'id="{identifier}"', f'id="{unique}"')
        svg = svg.replace(f"url(#{identifier})", f"url(#{unique})")
    return svg.replace("<svg ", '<svg aria-hidden="true" ', 1)


def card(lang, model):
    slug = model["slug"]
    category = model[f"category_{lang}"]
    tags = [category, *model[f"capabilities_{lang}"][:2]]
    if savings_label(lang, model):
        tags = [savings_label(lang, model), category, model[f"capabilities_{lang}"][0]]
    tags_html = "\n".join(f"            <li>{escape(tag)}</li>" for tag in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#fff4f3;border:1px solid #f5d7dd" aria-hidden="true">{logo(lang, slug)}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{escape(model['name'])} API</a></h3>
              <span class="af-model-cat">MiniMax · {escape(category)} · {escape(model['id'])}</span>
            </div>
          </div>
          <p>{escape(model[f'desc_{lang}'])}</p>
          <ul class="af-tags">
{tags_html}
          </ul>
          <div class="af-model-foot">
            <span><strong>${model['price_start']}</strong> / {escape(model[f'price_unit_{lang}'])}</span>
            <span class="af-model-go" aria-hidden="true">{COPY[lang]['guide']}</span>
          </div>
        </li>
'''


def category_block(lang):
    copy = COPY[lang]
    cards = "".join(card(lang, model) for model in MODELS)
    return (
        '      <!-- MiniMax -->\n'
        f'      <h3 class="af-section-head" id="cat-minimax" style="font-size:16px;margin:24px 0 12px">'
        f'<a class="af-cat-link" href="/{lang}/models/minimax">'
        f'<span class="af-cat-name">{copy["category"]}</span>'
        f'<span class="af-cat-more">{copy["more"]} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>\n'
        f'      <ul class="af-models">\n{cards}      </ul>\n'
        '      <!-- /MiniMax -->\n'
    )


def hub(lang):
    path = ROOT / lang / "models/index.html"
    original = path.read_text(encoding="utf-8")
    content = original
    block = category_block(lang)
    if "<!-- MiniMax -->" in content:
        content, count = re.subn(
            r'      <!-- MiniMax -->\n.*?      <!-- /MiniMax -->\n',
            lambda _: block, content, count=1, flags=re.S,
        )
        assert count == 1, "MiniMax category markers are malformed"
    else:
        anchor = '      <h3 class="af-section-head" id="cat-kimi"'
        assert anchor in content, "Kimi category insertion anchor is missing"
        content = content.replace(anchor, block + "\n" + anchor, 1)

    filter_link = f'<li><a href="#cat-minimax">{COPY[lang]["category"]}</a></li>'
    if 'href="#cat-minimax"' in content:
        content = re.sub(r'<li><a href="#cat-minimax">[^<]*</a></li>', filter_link, content, count=1)
    else:
        content, count = re.subn(
            r'(<li><a href="#cat-kimi">[^<]*</a></li>)',
            lambda match: filter_link + "\n        " + match.group(1), content, count=1,
        )
        assert count == 1, "Kimi filter insertion anchor is missing"

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
            name = COPY[lang]["overview"] if slug == "minimax" else f"{MODELS_BY_SLUG[slug]['name']} API"
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
