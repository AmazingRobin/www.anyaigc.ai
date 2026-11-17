# -*- coding: utf-8 -*-
"""Write a per-model "specs and how to choose" section from researched
official facts (scripts/seo_specs_data.json).

Each record in the JSON names its official source URL; only facts read from
the vendor's own pages belong there. The section reuses each family's own
markup (mm-/o-/gt-/vd-/mi- classes), sits right before the FAQ, and is
replaced in place on rerun. Prices are read from the page's own table.

Usage: PYTHONIOENCODING=utf-8 python scripts/seo_unique_specs.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "seo_specs_data.json"
SID = "spec-unique"


def esc(text):
    return html.escape(text, quote=False)


def table_prices(page):
    i = page.find('id="pricing"')
    sec = page[i:page.find("</section>", i)] if i >= 0 else ""
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", sec, re.S):
        raw = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        # A label cell may carry a <small>/<span> note; keep only the label itself.
        label = html.unescape(re.sub(r"<[^>]+>", "", re.split(r"<(?:small|span|br|em|p)\b", raw[0])[0])).strip() if raw else ""
        cells = [html.unescape(re.sub(r"<[^>]+>", " ", c)).strip() for c in raw]
        cells = [re.sub(r"\s+", " ", c) for c in cells]
        price = next((c for c in cells if re.match(r"^[\$¥]\s?[0-9]", c)), None)
        if price and label and label != price:
            rows.append((label, price))
    return rows[:4]


def shell(page):
    """Section/wrap/kicker/h2 classes copied from the page's own FAQ section."""
    m = re.search(r'<section class="([^"]+)" id="faq"[^>]*>\s*(<div class="[^"]+">)?', page)
    sec_cls = m.group(1) if m else "o-section"
    wrap = m.group(2) or ""
    prefix = re.match(r"([a-z]+)-", sec_cls).group(1)
    kicker = re.search(r'<p class="([a-z]+-kicker)[^"]*"', page)
    kicker_cls = kicker.group(1) if kicker else f"{prefix}-kicker"
    h2 = re.search(r'id="faq".*?<h2( class="[^"]*")?', page, re.S)
    h2_cls = (h2.group(1) or "") if h2 else ""
    if "gt-section gt-wrap" in sec_cls:
        wrap = ""
    return sec_cls, wrap, kicker_cls, h2_cls.replace(" o-reveal", "")


def section(lang, rec, page):
    zh = lang == "zh"
    facts = rec["facts_zh" if zh else "facts_en"]
    paras = [esc(f) for f in facts]
    rows = table_prices(page)
    if rows:
        if zh:
            paras.append("本页价格为：" + "、".join(f"{esc(a)} {esc(b)}" for a, b in rows) + "，与上方价格表一致。")
        else:
            paras.append("This page lists " + ", ".join(f"{esc(a)} at {esc(b)}" for a, b in rows) + ", matching the pricing table above.")
    other = rec.get("compare_slug") or ""
    text = rec.get("compare_zh" if zh else "compare_en") or ""
    if other and text and (ROOT / lang / "models" / f"{other}.html").is_file():
        label = f'<a href="/{lang}/models/{other}">{esc(other)}</a>'
        body_text = esc(text)
        # Link the first mention, unless the sentence opens with it (reads as a stray link).
        at = body_text.find(esc(other))
        if at > 0:
            paras.append(body_text.replace(esc(other), label, 1))
        else:
            paras.append((f"对比 {label}：{body_text}" if zh else f"Compared with {label}: {body_text}"))
    src = rec["source"]
    host = re.sub(r"^https?://(www\.)?", "", src).split("/")[0]
    note = (f'规格来自厂商官方资料（<a href="{html.escape(src)}">{esc(host)}</a>）；价格以本页表格为准，模型广场的实时价格优先。' if zh
            else f'Specs come from the vendor\'s official documentation (<a href="{html.escape(src)}">{esc(host)}</a>). The table on this page is the price, and the model catalog is authoritative for live rates.')
    sec_cls, wrap, kicker_cls, h2_cls = shell(page)
    title = "这个型号的规格与选型" if zh else "Specs and how to choose it"
    kicker = "规格" if zh else "SPECS"
    body = "".join(f"<p>{p}</p>" for p in paras) + f'<p class="spec-note">{note}</p>'
    inner = f'<p class="{kicker_cls}">{kicker}</p><h2{h2_cls} id="{SID}-title">{title}</h2>{body}'
    if wrap:
        inner = f"{wrap}{inner}</div>"
    return f'<section class="{sec_cls}" id="{SID}" aria-labelledby="{SID}-title">{inner}</section>\n'


def apply(path, lang, rec):
    page = path.read_text(encoding="utf-8")
    if not rec["facts_zh" if lang == "zh" else "facts_en"]:
        return "no-facts"
    block = section(lang, rec, page)
    old = re.search(rf'<section class="[^"]*" id="{SID}"[^>]*>.*?</section>\n?', page, re.S)
    if old:
        new = page[:old.start()] + block + page[old.end():]
    else:
        anchor = re.search(r'<section class="[^"]+" id="faq"', page)
        if not anchor:
            return "no-anchor"
        new = page[:anchor.start()] + block + page[anchor.start():]
    if new == page:
        return "unchanged"
    path.write_text(new, encoding="utf-8", newline="\n")
    return "written"


def main():
    records = json.loads(DATA.read_text(encoding="utf-8"))
    counts = {}
    for rec in records:
        for lang in ("zh", "en"):
            path = ROOT / lang / "models" / f"{rec['slug']}.html"
            result = apply(path, lang, rec) if path.is_file() else "missing"
            counts[result] = counts.get(result, 0) + 1
    print(counts)


if __name__ == "__main__":
    main()
