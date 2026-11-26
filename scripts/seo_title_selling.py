# -*- coding: utf-8 -*-
"""Chinese title selling points: the discount written as "约官方 X 折"
whenever the page itself states a discount
against the official price. Chinese readers parse 折 faster than a percentage.

The discount is never computed from prices. It comes from a claim already on
the page that names the official price (约官方 1.2 折, 比千问官方便宜 32%, ...).
A bare campaign badge such as "68 折" is not treated as an official discount.
"X 折" means paying X/10 of official, so a stated saving of S% is (100-S)/10 折.
When a page states no official discount, the title keeps its starting price
instead, which seo_titles.py already wrote.

Run after seo_titles.py / seo_overview_titles.py. Rerunning is a no-op.
Usage: PYTHONIOENCODING=utf-8 python scripts/seo_title_selling.py [--dry-run]
"""
import html
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv
# Claude, GPT, Gemini and Grok, including the same vendors' image and video models.
OVERSEAS = ("claude", "gpt", "gemini", "grok", "nano-banana")
# Titles owned by seo_overview_titles.py; changing them here would fight that script.
SKIP = {"qwen", "kling-advanced-custom-elements", "qwen-image-3.0", "qwen-image-3.0-pro"}

# "4–7 折" is a range; group 1 is the low end, i.e. the largest saving.
ZHE = r"(?<![\d.])(\d(?:\.\d{1,2})?)(?:\s*[–-]\s*\d(?:\.\d{1,2})?)?\s*折"
OFFICIAL_CLAIMS = [
    # 约官方 1.2 折 / 官方价约 1.2 折 / 约官方价 6 折 / 官方 8.1 折 / 官方4折
    re.compile(r"官方(?:美元)?价?的?\s*约?\s*" + ZHE),
    # 约 4 折 相比 Moonshot 官方 / 4 折 ... 对比 DeepSeek 官方
    re.compile(ZHE + r"[^。；|｜]{0,24}?(?:相比|对比)[^。；|｜]{0,24}?官方"),
    # 比千问官方便宜 32% / 比官方省 32% / 最高比官方便宜 88%（上一版标题写法）
    re.compile(r"比[^。；，|｜]{0,8}?官方[^。；，|｜]{0,4}?(?:便宜|省)\s*(\d{1,2}(?:\.\d+)?)\s*%"),
]


def zh_width(text):
    return len(text) + sum(ord(c) > 0x2E7F for c in text)


def fmt(value):
    text = f"{value.normalize():f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def as_zhe(match_index, raw):
    """A claim's value as 折 (tenths of the official price), or None.

    Only one decimal place: "8.78 折" reads as noise, and a discount that
    shallow is a weaker hook than the page's own starting price.
    """
    value = Decimal(raw) if match_index < 2 else (100 - Decimal(raw)) / 10
    if not 0 < value < 10 or value != value.quantize(Decimal("0.1")):
        return None
    return value


def all_discounts(text):
    """Every official-discount claim in the text, in 折."""
    out = []
    for i, pat in enumerate(OFFICIAL_CLAIMS):
        for m in pat.finditer(text):
            value = as_zhe(i, m.group(1))
            if value is not None:
                out.append(value)
    return out


def discount(text):
    """The first claim in reading order (the page's own headline), in 折."""
    for i, pat in enumerate(OFFICIAL_CLAIMS):
        m = pat.search(text)
        if m:
            value = as_zhe(i, m.group(1))
            if value is not None:
                return value
    return None


def overview_slugs():
    """Series overview pages, as linked from the category headings of the hub."""
    hub = (ROOT / "zh" / "models" / "index.html").read_text(encoding="utf-8")
    found = re.findall(r'<h3 class="af-section-head"[^>]*>\s*<a class="af-cat-link" href="/zh/models/([a-z0-9.-]+)"', hub)
    return set(found)


def visible(page):
    body = page.split("</head>", 1)[-1]
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))


def section_text(page, sid):
    i = page.find(f'id="{sid}"')
    if i < 0:
        return ""
    return visible(page[i:page.find("</section>", i)])


def replace_title(page, old, new):
    for a, b in ((html.escape(old, quote=True), html.escape(new, quote=True)), (old, new)):
        page = page.replace(a, b)
    return page


def candidates(name, pct, point, overseas, overview):
    """Title bodies, best first: "<name> API 价格与接入｜<discount in 折>".

    Overseas and domestic models share this wording. "中转" stays in the page
    keywords (seo_titles.py) but not in the title: it was tried there and
    replaced by "价格" after checking real Google results.
    """
    best = f"最低约官方 {pct} 折" if overview else f"约官方 {pct} 折"
    if overseas:
        # A discount leads when the page states one; otherwise keep whatever selling
        # point the title already had (usually the starting price), because a bare
        # "API 价格与接入" tells the reader nothing.
        tails = ([best] if pct else []) + ([point] if point and "中转" not in point else [])
        # A compact spelling of the same price, tried when the full tail is too long:
        # "输入 $0.1985/百万 Token 起" -> "$0.1985/M 起". No information is dropped.
        # Only spacing and units are tightened; qualifiers like "输入" and "全系" stay.
        # "¥0.08 / 秒起" -> "¥0.08/秒起", "8 个型号" -> "8 型号", "/百万 Token" -> "/M".
        compact = [re.sub(r" / ", "/", re.sub(r"(\d+) 个型号", r"\1 型号", re.sub(r"/(?:百万|M) Token", "/M", t))) for t in tails]
        tails = tails + [c for c in compact if c not in tails]
        # "价格与接入" says the page has both the price and the integration steps. When the
        # tail is too long for it, the shorter "价格" form is tried before dropping the tail.
        return ([f"{name} API 价格与接入｜{t}" for t in tails]
                + [f"{name} API 价格｜{t}" for t in tails]
                + [f"{name} API 价格与接入", f"{name} API 价格"])
    if not pct:
        return []
    return [f"{name} API 价格与接入｜{best}", f"{name} API 价格｜{best}", f"{name} API｜{best}"]


def main():
    changed = 0
    overviews = overview_slugs()
    for path in sorted((ROOT / "zh" / "models").glob("*.html")):
        slug = path.stem
        if slug == "index" or slug in SKIP:
            continue
        page = path.read_text(encoding="utf-8")
        m = re.search(r"<title>(.*?)</title>", page, re.S)
        old = html.unescape(m.group(1))
        tail = re.search(r"\s*[-|｜]\s*AnyAIGC\s*$", old)
        if not tail:
            continue
        core = old[:tail.start()]
        name = re.split(r" API", core, maxsplit=1)[0].strip()
        point = core.split("｜", 1)[1] if "｜" in core else ""
        overseas = slug.startswith(OVERSEAS)
        overview = slug in overviews
        if overview:
            # An overview covers several models: advertise the deepest discount.
            own = re.sub(r"<!-- related-models -->.*?<!-- /related-models -->", "", page, flags=re.S)
            values = all_discounts(core) + all_discounts(visible(own))
            pct = fmt(min(values)) if values else None
        else:
            pct = discount(core) or discount(section_text(page, "pricing"))
            if pct is not None:
                pct = fmt(pct)
        for body in candidates(name, pct, point, overseas, overview):
            new = body + " - AnyAIGC"
            if zh_width(new) > 64:
                continue
            # The first candidate that fits is the best one. If the title already
            # says it, stop here rather than falling through to a weaker variant.
            if new != old:
                if DRY:
                    print(slug, "|", old, "->", new)
                else:
                    path.write_text(replace_title(page, old, new), encoding="utf-8", newline="\n")
                changed += 1
            break
    print("titles changed:", changed)


if __name__ == "__main__":
    main()
