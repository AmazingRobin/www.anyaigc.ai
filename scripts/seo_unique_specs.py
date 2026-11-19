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
    """(rows, tier, more_tiers). Tiered tables list their first tier only.

    Rows with a single cell are tier headings ("输入 <= 200,000 tokens"). Mixing
    two tiers would repeat labels like 输入/输出 with different prices, so only the
    first tier is read and the caller is told that other tiers exist.

    When the header names an "AnyAIGC" column, that column is the price. Some tables
    put the vendor's list price first, and reading the first price cell would then
    quote the official price as this page's price.
    """
    i = page.find('id="pricing"')
    sec = page[i:page.find("</section>", i)] if i >= 0 else ""

    def text(cell):
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", cell))).strip()

    head_html = sec[:sec.find("</thead>")] if "</thead>" in sec else ""
    heads = [text(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", head_html, re.S)]
    ours = next((k for k, h in enumerate(heads) if "AnyAIGC" in h), None)
    body = sec[sec.find("</thead>"):] if "</thead>" in sec else sec

    groups, current = [], None
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        raw = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        cells = [text(c) for c in raw]
        if len(cells) == 1 and cells[0]:
            current = [cells[0], []]
            groups.append(current)
            continue
        label = html.unescape(re.sub(r"<[^>]+>", "", re.split(r"<(?:small|span|br|em|p)\b", raw[0])[0])).strip() if raw else ""
        isprice = lambda c: re.match(r"^[\$¥]\s?[0-9]", c)
        price = cells[ours] if ours is not None and len(cells) > ours and isprice(cells[ours]) else next((c for c in cells if isprice(c)), None)
        if price:
            # A cell can carry a trailing note ("$0.0035 官方 $0.0059"): keep the amount and unit only.
            m = re.match(r"^([\$¥]\s?[0-9][0-9.,]*(?:\s*/\s*[^\s$¥]+(?:\s+tokens)?)?)", price)
            price = m.group(1).strip() if m else price
        if price and label and label != price:
            if current is None:
                current = ["", []]
                groups.append(current)
            current[1].append((label, price))
    groups = [g for g in groups if g[1]]
    if not groups:
        return [], "", False
    tier, rows = groups[0]
    return rows[:4], (tier if len(groups) > 1 else ""), len(groups) > 1


def shell(page):
    """Section/wrap/kicker/h2 classes copied from the page's own FAQ section."""
    m = re.search(r'<section class="([^"]+)" id="faq"[^>]*>\s*(<div class="[^"]+">)?', page)
    sec_cls = m.group(1) if m else "o-section"
    wrap = m.group(2) or ""
    # 小标题只复制本页其它版块真正在用的写法（标签和 class 原样）：
    #   其它版块没有小标题的页面（Claude、GPT、Doubao 等）这里也不加；
    #   其它版块用 <span class="d-kicker"> 的页面（DeepSeek 等）这里也用它，颜色才和其它版块一致。
    # 要先去掉本版块自己，否则重跑时会读到上一次生成的 o-kicker（它没有样式，显示成黑字）。
    rest = re.sub(r'<section class="[^"]*" id="' + SID + r'".*?</section>\n?', "", page, flags=re.S)
    kicker = re.search(r'<(p|span)\s+class="([a-z]+-kicker)[^"]*"', rest)
    kicker_tag, kicker_cls = (kicker.group(1), kicker.group(2)) if kicker else ("", "")
    h2 = re.search(r'id="faq".*?<h2( class="[^"]*")?', page, re.S)
    h2_cls = (h2.group(1) or "") if h2 else ""
    if "gt-section gt-wrap" in sec_cls:
        wrap = ""
    return sec_cls, wrap, (kicker_tag, kicker_cls), h2_cls.replace(" o-reveal", "")


def section(lang, rec, page):
    zh = lang == "zh"
    facts = rec["facts_zh" if zh else "facts_en"]
    paras = [esc(f) for f in facts]
    rows, tier, more = table_prices(page)
    if rows:
        if zh:
            head = f"本页价格（{esc(tier)}）为：" if tier else "本页价格为："
            tail = "，其余档位见上方价格表。" if more else "，与上方价格表一致。"
            paras.append(head + "、".join(f"{esc(a)} {esc(b)}" for a, b in rows) + tail)
        else:
            head = f"This page lists ({esc(tier)}) " if tier else "This page lists "
            tail = "; other tiers are in the pricing table above." if more else ", matching the pricing table above."
            paras.append(head + ", ".join(f"{esc(a)} at {esc(b)}" for a, b in rows) + tail)
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
    k_tag, k_cls = kicker_cls
    kicker_html = f'<{k_tag} class="{k_cls}">{kicker}</{k_tag}>' if k_cls else ""
    inner = f'{kicker_html}<h2{h2_cls} id="{SID}-title">{title}</h2>{body}'
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
