# -*- coding: utf-8 -*-
"""Title, search-term and keyword fixes for topic pages (SEO review items 6-8).

Every number written here is read from the page itself (its meta description
or price table), so no new facts are introduced. Rerunning is safe: each rule
checks whether it has already been applied.

  1. Titles without a selling point, or with a phrase shared by many pages
     (编程与智能体, 视频生成与编辑), get the page's own starting price.
  2. English titles that are only "<Model> API Pricing & Access" get the price.
  3. zh quickstart H2 becomes "<模型> API 接入教程".
  4. Qwen subpages stop competing with the overview: keywords, the first FAQ
     and the closing CTA use the model name, and "价格是多少？" becomes
     "<模型> API 多少钱？" with the real numbers.
  5. Overseas models (Claude, GPT, Gemini, Grok) get "API 中转 / 国内调用"
     keywords on their Chinese pages.

Usage: PYTHONIOENCODING=utf-8 python scripts/seo_titles.py [--dry-run]
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv
SHARED = ("编程与智能体", "视频生成与编辑")
OVERSEAS = ("claude", "gpt", "gemini", "grok")


def zh_width(text):
    return len(text) + sum(ord(c) > 0x2E7F for c in text)


def model_name(page):
    """Product name from the H1. Some pages put a subtitle in a second <span> inside the
    H1 ("Hy4 API" + "腾讯混元新一代模型…"); only the first span is the name, otherwise
    the subtitle gets glued onto it."""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    if not h1:
        return ""
    inner = h1.group(1)
    # Subtitles come in three shapes: <small>…</small>, a second <span>, or a trailing
    # text node. Cut at the first of them; keep the product name before it.
    cut = re.search(r"<small\b|<span\b[^>]*class=\"[^\"]*(?:sub|j-nw)[^\"]*\"", inner)
    if cut:
        inner = inner[:cut.start()]
    # A visually hidden " API" (class o-sr) is part of the name's reading, not its text.
    inner = re.sub(r"<span\b[^>]*class=\"o-sr\"[^>]*>.*?</span>", "", inner, flags=re.S)
    name = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
    return re.sub(r"\s*API\s*$", "", name)


def desc_of(page):
    m = re.search(r'name="description" content="([^"]*)"', page)
    return html.unescape(m.group(1)) if m else ""


RANGE = r"(?:\s*[–-]\s*[\$¥]?[0-9.]+)?"  # "$0.1688–$1.519 / call": keep the low end
ZH_UNITS = {"second": "秒", "call": "次", "5s": "5秒", "image": "张", "request": "次", "clip": "条"}


def zh_price(desc):
    # A "billing unit base price" is not a per-item price; a bare number would mislead.
    if "计费单位" in desc or "billing unit" in desc:
        return []
    m = re.search(r"\$([0-9.]+)\s*/\s*百万 tokens", desc) or re.search(r"每百万 tokens \$([0-9.]+)", desc)
    if m:
        return [f"输入 ${m.group(1)}/百万 tokens 起", f"${m.group(1)}/百万 tokens 起", f"${m.group(1)}/M tokens 起", f"${m.group(1)}/M 起"]
    # No \b here: between two CJK characters ("秒起") it never matches.
    m = re.search(r"([\$¥])\s?([0-9.]+)" + RANGE + r"\s*/\s*([0-9]*\s*(?:秒|张|次|段|条)|(?:second|call|5s|image|request|clip)(?![A-Za-z]))", desc)
    if m:
        unit = m.group(3).replace(" ", "")
        unit = ZH_UNITS.get(unit, unit)
        return [f"{m.group(1)}{m.group(2)}/{unit}起"]
    return []


def en_price(desc):
    if "billing unit" in desc:
        return []
    m = re.search(r"\$([0-9.]+)" + RANGE + r"\s*(?:/|per)\s*(1M (?:input )?tokens|second|image|request|clip|call|5s)", desc)
    if not m:
        return []
    unit = {"1M input tokens": "1M tokens"}.get(m.group(2), m.group(2))
    short = {"1M tokens": "1M", "second": "s"}.get(unit, unit)
    return [f"From ${m.group(1)}/{unit}", f"From ${m.group(1)}/{short}", f"${m.group(1)}/{short}"]


def replace_title(page, old, new):
    """Swap the title everywhere it appears: <title>, og/twitter, JSON-LD."""
    for a, b in ((html.escape(old, quote=True), html.escape(new, quote=True)), (old, new)):
        page = page.replace(a, b)
    return page


def fix_title(page, lang):
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    old = html.unescape(m.group(1))
    suffix = re.search(r"\s*[-|｜]\s*AnyAIGC\s*$", old)
    if not suffix:
        return page, None
    core, tail = old[:suffix.start()], old[suffix.start():]
    desc = desc_of(page)
    if lang == "zh":
        head, _, point = core.partition("｜")
        if point and point not in SHARED:
            return page, None
        # Long model names: drop "与接入" before giving up on the price.
        heads = [head] + ([head.replace("价格与接入", "价格")] if "价格与接入" in head else [])
        for h in heads:
            for candidate in zh_price(desc):
                new = f"{h}｜{candidate}{tail}"
                if zh_width(new) <= 64:
                    return replace_title(page, old, new), new
        return page, None
    if not re.fullmatch(r".* API Pricing(?: & Access| & Integration)?", core):
        return page, None
    bases = [core, re.sub(r" & (?:Access|Integration)$", "", core)]
    for base in dict.fromkeys(bases):
        for candidate in en_price(desc):
            new = f"{base} | {candidate}{tail}"
            if len(html.escape(new, quote=True)) <= 65:
                return replace_title(page, old, new), new
    return page, None


def fix_quickstart(page, name):
    m = re.search(r'(<section[^>]*id="quickstart"[^>]*>.*?<h2[^>]*>)(.*?)(</h2>)', page, re.S)
    if not m or not name:
        return page
    want = f"{html.escape(name)} API 接入教程"
    if m.group(2) == want:
        return page
    # Replace both a missing heading and one an earlier run glued a subtitle onto.
    if "接入教程" in m.group(2) and len(re.sub(r"<[^>]+>", "", m.group(2))) <= len(want) + 2:
        return page
    return page[:m.start(2)] + want + page[m.end(2):]


def price_rows(page):
    i = page.find('id="pricing"')
    sec = page[i:page.find("</section>", i)] if i >= 0 else ""
    rows = re.findall(r"<tr><th>([^<]*)</th><td><code>[^<]*</code></td><td>(\$[0-9.]+ / 1M)</td>", sec)
    return [(label.replace(" tokens", ""), price.replace(" / 1M", "")) for label, price in rows]


def set_faq(page, old_q, new_q, new_a=None):
    """Rewrite one FAQ in both the visible HTML and the FAQPage JSON-LD."""
    pat = re.compile(r"(<summary><h3>)" + re.escape(old_q) + r"(</h3></summary><div class=\"q-ans\"><p>)(.*?)(</p>)", re.S)
    m = pat.search(page)
    if not m:
        return page
    answer = new_a if new_a is not None else m.group(3)
    page = page[:m.start()] + m.group(1) + new_q + m.group(2) + answer + m.group(4) + page[m.end():]
    block = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', page, re.S)
    data = json.loads(block.group(2))
    for node in data.get("@graph", []):
        if node.get("@type") == "FAQPage":
            for q in node["mainEntity"]:
                if q["name"] == html.unescape(old_q):
                    q["name"] = html.unescape(new_q)
                    q["acceptedAnswer"]["text"] = html.unescape(re.sub(r"<[^>]+>", "", answer))
    compact = "\n" not in block.group(2).strip()
    text = json.dumps(data, ensure_ascii=False) if compact else json.dumps(data, ensure_ascii=False, indent=2)
    return page[:block.start(2)] + text + page[block.end(2):]


def fix_qwen(page, lang, slug, name):
    zh = lang == "zh"
    page = re.sub(r'(name="keywords" content=")Qwen API,Qwen API pricing,Qwen API for business,Qwen API 发票,AnyAIGC"',
                  lambda m: m.group(1) + (f"{name} API,{name} API 价格,{slug},{name} API 企业,{name} API 发票,AnyAIGC\"" if zh
                                          else f"{name} API,{name} API pricing,{slug},{name} API for business,AnyAIGC\""), page)
    page = set_faq(page, "Qwen API 走什么接口？" if zh else "Which endpoint does Qwen use?",
                   f"{name} API 走什么接口？" if zh else f"Which endpoint does the {name} API use?")
    rows = price_rows(page)
    if rows:
        if zh:
            parts = "、".join(f"{label} {price}" for label, price in rows)
            answer = f"{name} 按 tokens 计费，{parts}（每百万 tokens 美元单价）。实时价格以模型广场为准。"
            page = set_faq(page, "价格是多少？", f"{name} API 多少钱？", answer)
        else:
            parts = ", ".join(f"{label.lower()} {price}" for label, price in rows)
            answer = f"{name} is billed per token: {parts} per million tokens. Live prices are in the model catalog."
            page = set_faq(page, "What does it cost?", f"How much does the {name} API cost?", answer)
    page = page.replace("<h2>准备好接入 Qwen API？</h2>", f"<h2>准备好接入 {html.escape(name)} API？</h2>")
    page = page.replace("<h2>Ready to call the Qwen API?</h2>", f"<h2>Ready to call the {html.escape(name)} API?</h2>")
    return page


def fix_overseas_keywords(page, name):
    m = re.search(r'name="keywords" content="([^"]*)"', page)
    extra = [f"{name} API 中转", f"{name} API 国内调用"]
    if m:
        have = [k.strip() for k in html.unescape(m.group(1)).split(",")]
        if extra[0] in have:
            return page
        value = html.escape(",".join(have[:1] + extra + have[1:]), quote=True)
        return page[:m.start(1)] + value + page[m.end(1):]
    tag = f'<meta name="keywords" content="{html.escape(",".join([name + " API"] + extra), quote=True)}">'
    return page.replace('<meta name="robots"', tag + '<meta name="robots"', 1)


def title_name(page):
    """Product name as the page's own <title> writes it ("Gemini 3.1 Pro", "GPT-5.5").

    Used for the quickstart heading, because H1 markup varies too much (subtitle in a
    <small>, a second <span>, or glued text) to read a clean name from it."""
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    if not m:
        return ""
    return re.split(r" API", html.unescape(m.group(1)), maxsplit=1)[0].strip()


def main():
    stats = {"title": 0, "quickstart": 0, "qwen": 0, "overseas": 0, "files": 0}
    for lang in ("zh", "en"):
        for path in sorted((ROOT / lang / "models").glob("*.html")):
            slug = path.stem
            if slug == "index":
                continue
            page = path.read_text(encoding="utf-8")
            new = page
            name = model_name(new)
            new, title = fix_title(new, lang)
            if title:
                stats["title"] += 1
                if DRY:
                    print(lang, slug, "->", title)
            if lang == "zh":
                before = new
                new = fix_quickstart(new, title_name(new))
                stats["quickstart"] += new != before
                if slug.startswith(OVERSEAS) and not slug.startswith(("gpt-image", "grok-image", "grok-imagine", "grok-video")):
                    before = new
                    new = fix_overseas_keywords(new, name)
                    stats["overseas"] += new != before
            if (slug.startswith("qwen") or slug.startswith("qwq")) and slug != "qwen" and "Qwen API,Qwen API pricing" in new:
                new = fix_qwen(new, lang, slug, name)
                stats["qwen"] += 1
            if new != page:
                stats["files"] += 1
                if not DRY:
                    path.write_text(new, encoding="utf-8", newline="\n")
    print(stats)


if __name__ == "__main__":
    main()
