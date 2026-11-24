# -*- coding: utf-8 -*-
"""Give series overview pages their own title format, and fix the Kling
length warnings from check_topics.py.

Overview pages own "<series> API" plus a model comparison; subpages keep the
model name. Prices and model counts are the ones already on each page. The
old string is replaced everywhere it appears (<title>, og/twitter meta,
JSON-LD), so all copies stay identical. Rerunning is a no-op.

Usage: PYTHONIOENCODING=utf-8 python scripts/seo_overview_titles.py
"""
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TITLES = {
    # zh grok-4.x is owned by seo_title_selling.py (overseas models carry 中转).
    ("en", "grok-4.x"): "Grok 4.x API: Compare 8 Models, From $0.0993/1M - AnyAIGC",
    ("zh", "qwen"): "Qwen API 价格对比｜全系 24 个型号，输入 $0.0338 起 - AnyAIGC",
    ("en", "qwen"): "Qwen API: Compare 24 Models, From $0.0338/1M - AnyAIGC",
    ("zh", "kling-advanced-custom-elements"): "Kling Advanced Custom Elements API｜$0.00169/次起 - AnyAIGC",
    ("en", "kling-advanced-custom-elements"): "Kling Advanced Custom Elements API | $0.00169/call - AnyAIGC",
    # Qwen Image 3.0 only lists a "billing unit base" price, which is not a per-image
    # price, so the selling point comes from the capability text on the page.
    ("zh", "qwen-image-3.0"): "Qwen Image 3.0 API 价格与接入｜长指令与文字渲染 - AnyAIGC",
    ("zh", "qwen-image-3.0-pro"): "Qwen Image 3.0 Pro API 价格｜密集排版与多语言文字 - AnyAIGC",
    ("en", "qwen-image-3.0"): "Qwen Image 3.0 API Pricing | Reliable Text Rendering - AnyAIGC",
    ("en", "qwen-image-3.0-pro"): "Qwen Image 3.0 Pro API Pricing | Multilingual Text - AnyAIGC",
}

DESCRIPTIONS = {
    ("en", "kling"): "Kling API overview: 16 image, video and audio models, from text-to-video to motion control and avatars. Unlimited concurrency, self-service invoices.",
    ("en", "kling-advanced-lip-sync"): "Kling Advanced Lip Sync API: $0.00844 face detection, $0.0844 per 5s lip-sync. Async jobs, unlimited concurrency, self-service invoices.",
}


def zh_width(text):
    return len(text) + sum(ord(c) > 0x2E7F for c in text)


def swap(page, old, new):
    for a, b in ((html.escape(old, quote=True), html.escape(new, quote=True)), (old, new)):
        page = page.replace(a, b)
    return page


def main():
    changed = 0
    for (lang, slug), new in TITLES.items():
        if lang == "zh":
            assert zh_width(new) <= 64, (slug, zh_width(new))
        else:
            assert len(html.escape(new, quote=True)) <= 65, (slug, len(new))
    for (lang, slug), new in DESCRIPTIONS.items():
        assert 120 <= len(new) <= 160, (slug, len(new))

    for lang, slug in set(TITLES) | set(DESCRIPTIONS):
        path = ROOT / lang / "models" / f"{slug}.html"
        page = path.read_text(encoding="utf-8")
        new = page
        if (lang, slug) in TITLES:
            start = new.index("<title>") + len("<title>")
            old = html.unescape(new[start:new.index("</title>", start)])
            new = swap(new, old, TITLES[(lang, slug)])
        if (lang, slug) in DESCRIPTIONS:
            marker = 'name="description" content="'
            start = new.index(marker) + len(marker)
            old = html.unescape(new[start:new.index('"', start)])
            new = swap(new, old, DESCRIPTIONS[(lang, slug)])
        if new != page:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
            print("updated", lang, slug)
    print("files changed:", changed)


if __name__ == "__main__":
    main()
