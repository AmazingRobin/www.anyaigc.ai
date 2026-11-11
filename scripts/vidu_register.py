"""Register the Vidu overview and 7 model guides in both hubs and sitemap.

Run: python scripts/vidu_register.py
The overview is linked from the category heading; model cards retain the site's
shared af-* presentation. Repeated runs replace this category without duplicates.
"""

import json
import re
from html import escape
from pathlib import Path

from vidu_data import CHECKED_DATE, MODELS, SLUGS


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.anyaigc.ai"
MODELS_BY_SLUG = {model["slug"]: model for model in MODELS}
COPY = {
    "zh": {
        "category": "Vidu 视频与图像系列",
        "more": "全系总览与价格对比",
        "guide": "查看专题 →",
        "overview": "Vidu API（全系总览）",
    },
    "en": {
        "category": "Vidu video & image",
        "more": "Overview and price comparison",
        "guide": "View guide →",
        "overview": "Vidu API (overview)",
    },
}


def logo(lang, slug):
    svg = (ROOT / "assets/icons/vidu-color.svg").read_text(encoding="utf-8").strip()
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    svg = re.sub(r'\b(?:height|width)="1em"', lambda match: match.group(0).replace("1em", "26"), svg)
    # Each inline gradient needs a unique id within the hub document.
    for identifier in re.findall(r'\bid="([^"]+)"', svg):
        unique = f"vidu-hub-{lang}-{slug}-{identifier}"
        svg = svg.replace(f'id="{identifier}"', f'id="{unique}"')
        svg = svg.replace(f"url(#{identifier})", f"url(#{unique})")
    return svg.replace("<svg ", '<svg aria-hidden="true" ', 1)


def card(lang, model):
    slug = model["slug"]
    category = model[f"tag_{lang}"]
    tags = model[f"caps_{lang}"][:3]
    tags_html = "\n".join(f"            <li>{escape(tag)}</li>" for tag in tags)
    return f'''        <li class="af-model">
          <div class="af-model-head">
            <span class="af-model-logo" style="background:#020b13;border:1px solid #020b13" aria-hidden="true">{logo(lang, slug)}</span>
            <div>
              <h3><a href="/{lang}/models/{slug}">{escape(model['name'])} API</a></h3>
              <span class="af-model-cat">Vidu · {escape(category)} · {escape(model['id'])}</span>
            </div>
          </div>
          <p>{escape(model[f'desc_{lang}'])}</p>
          <ul class="af-tags">
{tags_html}
          </ul>
          <div class="af-model-foot">
            <span><strong>${model['start']}</strong> / {escape(model[f'start_{lang}'])}</span>
            <span class="af-model-go" aria-hidden="true">{COPY[lang]['guide']}</span>
          </div>
        </li>
'''


def category_block(lang):
    copy = COPY[lang]
    cards = "".join(card(lang, model) for model in MODELS)
    return (
        '      <!-- Vidu -->\n'
        f'      <h3 class="af-section-head" id="cat-vidu" style="font-size:16px;margin:24px 0 12px">'
        f'<a class="af-cat-link" href="/{lang}/models/vidu">'
        f'<span class="af-cat-name">{copy["category"]}</span>'
        f'<span class="af-cat-more">{copy["more"]} <span class="af-cat-arrow" aria-hidden="true">→</span></span></a></h3>\n'
        f'      <ul class="af-models">\n{cards}      </ul>\n'
        '      <!-- /Vidu -->\n'
    )


def hub(lang):
    path = ROOT / lang / "models/index.html"
    original = path.read_text(encoding="utf-8")
    content = original
    block = category_block(lang)
    if "<!-- Vidu -->" in content:
        content, count = re.subn(
            r'      <!-- Vidu -->\n.*?      <!-- /Vidu -->\n',
            lambda _: block, content, count=1, flags=re.S,
        )
        assert count == 1, "Vidu category markers are malformed"
    else:
        anchor = '      <h3 class="af-section-head" id="cat-muse"'
        assert anchor in content, "Muse category insertion anchor is missing"
        content = content.replace(anchor, block + "\n" + anchor, 1)

    filter_link = f'<li><a href="#cat-vidu">{COPY[lang]["category"]}</a></li>'
    if 'href="#cat-vidu"' in content:
        content = re.sub(r'<li><a href="#cat-vidu">[^<]*</a></li>', filter_link, content, count=1)
    else:
        content, count = re.subn(
            r'(<li><a href="#cat-muse">[^<]*</a></li>)',
            lambda match: filter_link + "\n        " + match.group(1), content, count=1,
        )
        assert count == 1, "Muse filter insertion anchor is missing"

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
            name = COPY[lang]["overview"] if slug == "vidu" else f"{MODELS_BY_SLUG[slug]['name']} API"
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
