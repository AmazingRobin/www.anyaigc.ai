# -*- coding: utf-8 -*-
"""Keep sitemap lastmod honest.

Google only trusts lastmod when it has always matched real content changes, so
each URL is dated by the last commit that touched the page's *content*. The
<head> and every <script>/<style> block are stripped first, which drops JSON-LD
dateModified, asset version queries (?v=20261114) and inline CSS. A commit that
only bumps a cache version therefore does not move the date.

An entry is updated only when its current lastmod is older than that content
date. A newer lastmod is left alone and reported, never pulled backwards, and
privacy.html / terms.html gain the <lastmod> they were missing.

Usage: PYTHONIOENCODING=utf-8 python scripts/sitemap_lastmod.py
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.anyaigc.ai"
SITEMAP = ROOT / "sitemap.xml"


def content_of(text):
    text = re.sub(r"<head\b.*?</head>", " ", text, flags=re.S)
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", text, flags=re.S)
    return re.sub(r"\s+", " ", text).strip()


def committed(commit, path):
    """Content of one file at one commit, or None if the commit lacks it."""
    spec = commit + ":" + path.replace("\\", "/")
    run = subprocess.run(["git", "cat-file", "-e", spec], cwd=ROOT, capture_output=True)
    if run.returncode != 0:
        return None
    show = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True)
    return content_of(show.stdout.decode("utf-8", "replace"))


def content_dates(paths):
    """path -> YYYY-MM-DD of the newest commit that changed its content.

    Walks each file's own history newest first and stops at the first commit
    whose content differs from the working tree, so a commit that only changed
    the head, JSON-LD or a stylesheet version does not count.
    """
    log = subprocess.run(
        ["git", "log", "--format=COMMIT %H %cs", "--name-only", "--", "*.html"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    wanted = set(paths)
    history = {path: [] for path in wanted}
    commit = date = None
    for line in log.splitlines():
        if line.startswith("COMMIT "):
            _, commit, date = line.split()
            continue
        if line in history:
            history[line].append((commit, date))

    dates = {}
    for path in sorted(wanted):
        current = content_of((ROOT / path).read_text(encoding="utf-8"))
        dates[path] = history[path][0][1] if history[path] else None
        for commit, date in history[path]:
            previous = committed(commit, path)
            if previous is None or previous != current:
                break
            dates[path] = date
            current = previous
    return dates


def repo_path(loc):
    rel = loc[len(SITE):]
    if rel in ("", "/"):
        return "index.html"
    if rel in ("/privacy", "/terms"):
        return rel[1:] + ".html"
    return rel[1:] + ".html"


def main():
    text = SITEMAP.read_text(encoding="utf-8")
    entries = re.findall(r"<loc>([^<]+)</loc>", text)
    paths = [repo_path(loc) for loc in entries if (ROOT / repo_path(loc)).is_file()]
    dates = content_dates(paths)

    updated = kept = missing = 0

    def apply(match):
        nonlocal updated, kept, missing
        loc, gap = match.group(1), match.group(2)
        current = re.match(r"\s*<lastmod>([^<]*)</lastmod>", gap)
        lastmod = current.group(1) if current else None
        date = dates.get(repo_path(loc))
        if not date:
            missing += 1
            return match.group(0)
        if lastmod == date:
            return match.group(0)
        if lastmod and lastmod > date:
            kept += 1
            print(f"kept {loc}: sitemap {lastmod} is newer than content {date}")
            return match.group(0)
        updated += 1
        return f"<loc>{loc}</loc>\n    <lastmod>{date}</lastmod>\n    "

    new = re.sub(
        r"<loc>([^<]+)</loc>(\s*)(?:<lastmod>[^<]*</lastmod>\s*)?",
        apply, text)
    if new != text:
        SITEMAP.write_text(new, encoding="utf-8", newline="\n")
    print(f"updated {updated}, left newer entries {kept}, no history {missing}")


if __name__ == "__main__":
    main()
