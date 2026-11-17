# -*- coding: utf-8 -*-
"""Drop free add-on items from Product AggregateOffer in JSON-LD.

Items priced 0 (free output tokens, the first 5 reference images, free
Midjourney actions) are not something a customer buys on their own. Keeping
them makes lowPrice 0, which search results show as "from $0". The free items
stay on the visible price table; only the structured data changes.
Rerunning is a no-op.

Usage: PYTHONIOENCODING=utf-8 python scripts/seo_offers.py
"""
import json
import re
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LD = re.compile(r'(<script type="application/ld\+json">)(\s*)(.*?)(\s*)(</script>)', re.S)


def fix(node):
    changed = False
    if isinstance(node, list):
        return any([fix(x) for x in node])
    if not isinstance(node, dict):
        return False
    offers = node.get("offers")
    if isinstance(offers, dict) and offers.get("@type") == "AggregateOffer" and offers.get("offers"):
        paid = [o for o in offers["offers"] if Decimal(str(o.get("price", "0"))) > 0]
        if paid and len(paid) != len(offers["offers"]):
            prices = [Decimal(str(o["price"])) for o in paid]
            offers["offers"] = paid
            offers["offerCount"] = len(paid)
            offers["lowPrice"] = str(min(prices))
            offers["highPrice"] = str(max(prices))
            changed = True
    for value in node.values():
        changed = fix(value) or changed
    return changed


def main():
    count = 0
    for lang in ("zh", "en"):
        for path in sorted((ROOT / lang / "models").glob("*.html")):
            text = path.read_text(encoding="utf-8")
            out, pos, dirty = [], 0, False
            for m in LD.finditer(text):
                data = json.loads(m.group(3))
                if fix(data):
                    dirty = True
                    pretty = "\n" in m.group(3)
                    body = json.dumps(data, ensure_ascii=False, indent=2 if pretty else None)
                    out.append(text[pos:m.start(3)] + body)
                    pos = m.end(3)
            if dirty:
                out.append(text[pos:])
                path.write_text("".join(out), encoding="utf-8", newline="\n")
                count += 1
                print("fixed", path.relative_to(ROOT).as_posix())
    print("files changed:", count)


if __name__ == "__main__":
    main()
