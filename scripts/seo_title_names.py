# -*- coding: utf-8 -*-
"""Fix display names in page titles: drop "Preview", complete truncated dates.

Searchers look for "Gemini 3.1 Pro API", not "Gemini 3.1 Pro Preview API", so the
title leads with the plain product name. Only the <title> and its copies
(og:title, twitter:title, WebPage name in JSON-LD) change. The H1, body text and
every code sample keep the full model ID, because the API call needs
"gemini-3.1-pro-preview" exactly.

Raw model IDs used as the title name (doubao-seed-2-0-code-preview) are NOT
shortened: "doubao-seed-2-0-code" is not a real ID and would mislead anyone
copying it.

Run last among the title scripts. Rerunning is a no-op.
Usage: PYTHONIOENCODING=utf-8 python scripts/seo_title_names.py [--dry-run]
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv

# slug -> (display name as it appears in titles, name without "Preview")
NAMES = {
    "gemini-3.1-pro-preview": ("Gemini 3.1 Pro Preview", "Gemini 3.1 Pro"),
    "wan2.5-i2v-preview": ("Wan 2.5 I2V Preview", "Wan 2.5 I2V"),
    "viduq4-preview": ("Vidu Q4 Preview", "Vidu Q4"),
    # "12-30" has no year, so a reader cannot tell which snapshot this is.
    "qwen-image-max-2025-12-30": ("Qwen Image Max", "Qwen Image Max"),
}
# Titles that need different wording, not just a different name, to fit.
TRIMMED = {
    ("en", "qwen-image-max-2025-12-30"): "Qwen Image Max API Pricing | $0.0658/request - AnyAIGC",
}
LIMIT_EN, LIMIT_ZH = 65, 64  # escaped length / display width, as check_topics.py counts


def zh_width(text):
    return len(text) + sum(ord(c) > 0x2E7F for c in text)


def replace_title(page, old, new):
    for a, b in ((html.escape(old, quote=True), html.escape(new, quote=True)), (old, new)):
        page = page.replace(a, b)
    return page


def main():
    changed = 0
    for slug, (long_name, short_name) in NAMES.items():
        for lang in ("zh", "en"):
            path = ROOT / lang / "models" / f"{slug}.html"
            if not path.is_file():
                continue
            page = path.read_text(encoding="utf-8")
            old = html.unescape(re.search(r"<title>(.*?)</title>", page, re.S).group(1))
            if not old.startswith(long_name):
                continue
            new = short_name + old[len(long_name):]
            if (lang, slug) in TRIMMED:
                # The full date does not fit with the original wording, so the title is
                # rewritten shorter instead of leaving the year off.
                new = TRIMMED[(lang, slug)]
            too_long = (zh_width(new) > LIMIT_ZH) if lang == "zh" else (len(html.escape(new, quote=True)) > LIMIT_EN)
            if too_long:
                print(f"skip {lang} {slug}: {new!r} exceeds the title limit")
                continue
            if DRY:
                print(f"{lang} {slug:26} {old}  ->  {new}")
            else:
                path.write_text(replace_title(page, old, new), encoding="utf-8", newline="\n")
            changed += 1
    print("titles changed:", changed)


if __name__ == "__main__":
    main()
