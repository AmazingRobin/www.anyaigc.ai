# -*- coding: utf-8 -*-
"""Put the official discount into English titles as "Save X%".

English has no equivalent of 折, so the Chinese "约官方 2.4 折" becomes
"Save 76%" rather than a literal translation. The percentage is derived from
the discount already confirmed on the Chinese page of the same model
(折 -> 100 - 10 * 折), so the two languages can never disagree.

Three cases:
  - title states no discount  -> add "Save X%" if it fits in 65 characters
  - title states a different % -> correct it to match the Chinese page
  - title already correct      -> left alone

Run after seo_title_selling.py. Rerunning is a no-op.
Usage: PYTHONIOENCODING=utf-8 python scripts/seo_titles_en_save.py [--dry-run]
"""
import html
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv
LIMIT = 65  # check_topics.py counts the escaped title
ZH_DISCOUNT = re.compile(r"(最低)?约官方 (\d(?:\.\d)?) 折")
# "76% Off", "76% off list", "Up to 88% Off", "Save 32%", "36% of Google List Price"
STATED = re.compile(r"(?:Up to\s*)?(\d+(?:\.\d+)?)\s*%\s*(?:off|of\b)"
                    r"|Save\s*(?:up\s*to\s*)?(\d+(?:\.\d+)?)\s*%", re.I)


def title_of(page):
    return html.unescape(re.search(r"<title>(.*?)</title>", page, re.S).group(1))


def width(text):
    return len(html.escape(text, quote=True))


def replace_title(page, old, new):
    for a, b in ((html.escape(old, quote=True), html.escape(new, quote=True)), (old, new)):
        page = page.replace(a, b)
    return page


def zh_saving(slug):
    """(percent, is_series_minimum) from the Chinese title, or None."""
    path = ROOT / "zh" / "models" / f"{slug}.html"
    if not path.is_file():
        return None
    m = ZH_DISCOUNT.search(title_of(path.read_text(encoding="utf-8")))
    if not m:
        return None
    value = 100 - Decimal(m.group(2)) * 10
    if not 0 < value < 100:
        return None
    return f"{value.normalize():f}", bool(m.group(1))


def main():
    added = fixed = kept = skipped = 0
    for path in sorted((ROOT / "en" / "models").glob("*.html")):
        slug = path.stem
        if slug == "index":
            continue
        got = zh_saving(slug)
        if not got:
            continue
        pct, series = got
        page = path.read_text(encoding="utf-8")
        old = title_of(page)
        tail = re.search(r"\s*[-|｜]\s*AnyAIGC\s*$", old)
        if not tail:
            continue
        core, suffix = old[:tail.start()], old[tail.start():]

        stated = STATED.search(core)
        if stated:
            shown = stated.group(1) or stated.group(2)
            # "36% of list price" states the share paid, not the saving.
            share = bool(stated.group(1)) and re.search(r"%\s*of", stated.group(0), re.I)
            want = str(100 - Decimal(pct)) if share else pct
            if Decimal(shown) == Decimal(want):
                kept += 1
                continue
            # Patch the number in place: the surrounding wording ("at 86% Off",
            # "41% off list") is already idiomatic, so only the figure is wrong.
            at = core.index(shown, stated.start())
            new = core[:at] + want + core[at + len(shown):] + suffix
            if width(new) <= LIMIT:
                if DRY:
                    print(f"fix  {slug:26} {old}  ->  {new}")
                else:
                    path.write_text(replace_title(page, old, new), encoding="utf-8", newline="\n")
                fixed += 1
            else:
                skipped += 1
            continue

        label = f"Save up to {pct}%" if series else f"Save {pct}%"
        # A concrete starting price beats a modest saving, so keep the price and
        # only append the discount if both fit. Mirrors the Chinese rule.
        has_price = re.search(r"\$[0-9]", core)
        if has_price and Decimal(pct) < 50:
            candidates = (f"{core}, {label}",)
        else:
            candidates = None
        # Append to the existing selling point when it fits; otherwise the discount
        # replaces it, since a concrete saving outranks a capability phrase.
        head = re.sub(r"\s*[|｜:].*$", "", core).rstrip(" :|")
        # Avoid two "|" separators when the suffix itself is "| AnyAIGC". A colon
        # binds to the preceding word; a pipe takes spaces on both sides.
        join = (lambda a, b: f"{a}: {b}") if suffix.lstrip().startswith("|") else (lambda a, b: f"{a} | {b}")
        if candidates is None:
            candidates = (join(core, label), f"{core}, {label}",
                          join(head, label), join(head, f"Save {pct}%"))
        for candidate in candidates:
            new = re.sub(r" {2,}", " ", candidate).strip() + suffix
            if width(new) <= LIMIT and new != old:
                if DRY:
                    print(f"add  {slug:26} {old}  ->  {new}")
                else:
                    path.write_text(replace_title(page, old, new), encoding="utf-8", newline="\n")
                added += 1
                break
        else:
            skipped += 1
            if DRY:
                print(f"skip {slug:26} {old}  (no room for Save {pct}%)")
    print(f"added {added}, corrected {fixed}, already correct {kept}, no room {skipped}")


if __name__ == "__main__":
    main()
