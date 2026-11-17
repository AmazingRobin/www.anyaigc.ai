# -*- coding: utf-8 -*-
"""Give the Qwen overview page a price FAQ that states real numbers.

The generic "价格是多少？ / What does it cost?" answer only pointed at the table.
The new answer quotes the lowest and highest input and output rate found in the
page's own price table, so it can never disagree with it. The question becomes
"Qwen API 多少钱？" / "How much does the Qwen API cost?".

The visible FAQ and the FAQPage JSON-LD are changed together. Rerunning is a
no-op, and it also refreshes the numbers if the table changes.

Usage: PYTHONIOENCODING=utf-8 python scripts/seo_overview_faq.py
"""
import html
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from seo_titles import set_faq  # noqa: E402

TARGETS = {
    "qwen": {
        "zh": ("价格是多少？", "Qwen API 多少钱？"),
        "en": ("What does it cost?", "How much does the Qwen API cost?"),
    },
}


def text(cell):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", cell))).strip()


def rates(page):
    """{'in': [(Decimal, model)], 'out': [...]} from the page's price table."""
    i = page.find('id="pricing"')
    sec = page[i:page.find("</section>", i)]
    found = {"in": [], "out": []}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", sec, re.S):
        cells = [text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        if len(cells) < 3:
            continue
        m = re.match(r"^\$([0-9.]+)", cells[2])
        if not m:
            continue
        label = cells[0].lower()
        if label.startswith(("输入", "input")):
            found["in"].append((Decimal(m.group(1)), cells[1]))
        elif label.startswith(("输出", "output")):
            found["out"].append((Decimal(m.group(1)), cells[1]))
    return found


def answer(lang, found):
    lo_i, hi_i = min(found["in"]), max(found["in"])
    lo_o, hi_o = min(found["out"]), max(found["out"])
    if lang == "zh":
        return (f"Qwen 对话模型按输入和输出 tokens 分别计费，单位是美元 / 每百万 tokens。"
                f"输入单价从 ${lo_i[0]}（{lo_i[1]}）到 ${hi_i[0]}（{hi_i[1]}），"
                f"输出单价从 ${lo_o[0]}（{lo_o[1]}）到 ${hi_o[0]}（{hi_o[1]}）。"
                f"每个型号的具体价格见上方价格表，实时价格以模型广场为准。")
    return (f"Qwen conversation models are billed separately for input and output tokens, in USD per million tokens. "
            f"Input runs from ${lo_i[0]} ({lo_i[1]}) to ${hi_i[0]} ({hi_i[1]}), "
            f"and output from ${lo_o[0]} ({lo_o[1]}) to ${hi_o[0]} ({hi_o[1]}). "
            f"Each model's own rate is in the pricing table above, and the model catalog is authoritative for live prices.")


# Pages whose answer already states the starting price: only the question is renamed.
RENAME_ONLY = {
    "kling": {
        "zh": ("价格是多少？", "Kling API 多少钱？"),
        "en": ("What does it cost?", "How much does the Kling API cost?"),
    },
}


def rename_only(page, old_q, new_q):
    """Rename one FAQ question in the visible HTML and in the FAQPage JSON-LD."""
    if f"<summary><h3>{new_q}</h3></summary>" in page:
        return page
    page = page.replace(f"<summary><h3>{old_q}</h3></summary>", f"<summary><h3>{new_q}</h3></summary>", 1)
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', page, re.S)
    data = json.loads(m.group(2))
    for node in data.get("@graph", [data]):
        if node.get("@type") == "FAQPage":
            for q in node["mainEntity"]:
                if q["name"] == old_q:
                    q["name"] = new_q
    pretty = "\n" in m.group(2).strip()
    body = json.dumps(data, ensure_ascii=False, indent=2 if pretty else None)
    if pretty:
        body = "\n" + body + "\n"
    return page[:m.start(2)] + body + page[m.end(2):]


def main():
    changed = 0
    for slug, langs in RENAME_ONLY.items():
        for lang, (old_q, new_q) in langs.items():
            path = ROOT / lang / "models" / f"{slug}.html"
            page = path.read_text(encoding="utf-8")
            new = rename_only(page, old_q, new_q)
            if new != page:
                path.write_text(new, encoding="utf-8", newline="\n")
                changed += 1
                print("renamed", lang, slug)
    for slug, langs in TARGETS.items():
        for lang, (old_q, new_q) in langs.items():
            path = ROOT / lang / "models" / f"{slug}.html"
            page = path.read_text(encoding="utf-8")
            found = rates(page)
            if not found["in"] or not found["out"]:
                print("no rates found:", path.name, lang)
                continue
            body = html.escape(answer(lang, found), quote=False)
            new = set_faq(page, old_q, new_q, body)
            if new == page:
                new = set_faq(page, new_q, new_q, body)  # already renamed: refresh the numbers
            if new != page:
                path.write_text(new, encoding="utf-8", newline="\n")
                changed += 1
                print("updated", lang, slug)
    print("files changed:", changed)


if __name__ == "__main__":
    main()
