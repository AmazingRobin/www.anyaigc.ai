# -*- coding: utf-8 -*-
"""Add a cross-vendor "related models" section to every topic page.

Each page is put in one category (text / image / video / audio) and links to
up to six other families in that category, never its own family. The section
is written between markers, so rerunning replaces it instead of duplicating it.
Run it again after regenerating any family:

    PYTHONIOENCODING=utf-8 python scripts/related_models.py
"""
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS_VERSION = "20261125"
START, END = "<!-- related-models -->", "<!-- /related-models -->"

# category -> [(family, target slug, display name)]
TARGETS = {
    "text": [
        ("claude", "claude", "Claude"), ("gpt", "gpt", "GPT"),
        ("gemini", "gemini-4-hydrogen", "Gemini 4"), ("deepseek", "deepseek", "DeepSeek"),
        ("qwen", "qwen", "Qwen"), ("kimi", "kimi", "Kimi"), ("glm", "glm", "GLM"),
        ("grok", "grok-4.x", "Grok 4"), ("doubao", "doubao-seed-2-1-pro", "Doubao Seed"),
        ("llama", "llama", "Llama"), ("mimo", "mimo", "Xiaomi MiMo"),
        ("minimax", "minimax", "MiniMax"), ("hy4", "hy4", "Hy4"),
    ],
    "image": [
        ("gpt-image", "gpt-image", "GPT Image"), ("nano-banana", "nano-banana", "Nano Banana"),
        ("seedream", "seedream", "Seedream"), ("qwen-image", "qwen-image-3.0", "Qwen Image"),
        ("midjourney", "midjourney", "Midjourney"), ("grok-image", "grok-image", "Grok Image"),
        ("kling", "kling-image-3.0", "Kling Image"), ("muse", "muse-image", "Muse Image"),
        ("vidu", "vidu-image-q2", "Vidu Image"),
    ],
    "video": [
        ("seedance", "seedance", "Seedance"), ("kling", "kling", "Kling"),
        ("vidu", "vidu", "Vidu"), ("grok-video", "grok-video", "Grok Video"),
        ("wan", "wan3.0-video", "Wan 3.0"), ("happyhorse", "happyhorse-1.1-t2v", "HappyHorse"),
        ("hailuo", "hailuo-h3", "Hailuo H3"), ("muse", "muse-video", "Muse Video"),
    ],
    "audio": [
        ("eleven", "eleven-v4", "ElevenLabs"), ("minimax", "speech-2.8-hd", "MiniMax Speech"),
        ("suno", "suno", "Suno"), ("gemini", "gemini-3.8-flash-tts", "Gemini TTS"),
        ("kling", "kling-audio", "Kling Audio"),
    ],
}

AUDIO = ("eleven", "speech-", "suno", "minimax-voice-design", "gemini-3.8-flash-tts",
         "kling-audio", "kling-custom-voices", "qwen3.8-omni-flash-realtime")
IMAGE = ("gpt-image", "nano-banana", "seedream", "qwen-image", "wan2.7-image", "z-image",
         "kling-image", "grok-image", "grok-imagine-image", "midjourney", "muse-image",
         "vidu-image")
VIDEO = ("doubao-seedance", "seedance", "kling", "vidu", "grok-video", "grok-imagine-video",
         "happyhorse", "wan2.5", "wan2.6", "wan3.0", "hailuo", "minimax-h3", "muse-video")


def category(slug):
    for kind, prefixes in (("audio", AUDIO), ("image", IMAGE), ("video", VIDEO)):
        if slug.startswith(prefixes):
            return kind
    return "text"


def family(slug):
    for prefix, fam in (
        ("gpt-image", "gpt-image"), ("gpt", "gpt"), ("claude", "claude"),
        ("gemini", "gemini"), ("deepseek", "deepseek"), ("qwen-image", "qwen-image"),
        ("wan", "wan"), ("z-image", "qwen-image"), ("happyhorse", "happyhorse"),
        ("qwen", "qwen"), ("qwq", "qwen"), ("kimi", "kimi"), ("glm", "glm"),
        ("grok-image", "grok-image"), ("grok-imagine-image", "grok-image"),
        ("grok-video", "grok-video"), ("grok-imagine-video", "grok-video"), ("grok", "grok"),
        ("doubao-seedance", "seedance"), ("seedance", "seedance"), ("doubao", "doubao"),
        ("seedream", "seedream"), ("nano-banana", "nano-banana"), ("llama", "llama"),
        ("mimo", "mimo"), ("hailuo", "hailuo"), ("minimax", "minimax"), ("speech-", "minimax"),
        ("kling", "kling"), ("vidu", "vidu"), ("muse", "muse"), ("eleven", "eleven"),
        ("suno", "suno"), ("midjourney", "midjourney"), ("hy4", "hy4"), ("jev", "jev"),
        ("sparkdesk", "sparkdesk"),
    ):
        if slug.startswith(prefix):
            return fam
    return slug


COPY = {
    "zh": {"h2": "同类模型 API", "kind": {"text": "对话", "image": "图像", "video": "视频", "audio": "语音与音频"},
           "lead": "同一个 AnyAIGC API Key 也能调用这些{kind}模型，按需对比价格和能力。", "go": "查看专题"},
    "en": {"h2": "Related model APIs", "kind": {"text": "language", "image": "image", "video": "video", "audio": "speech and audio"},
           "lead": "The same AnyAIGC API key works with these {kind} models. Compare pricing and capabilities.", "go": "View guide"},
}


SEC_TOKEN = re.compile(r"^[a-z]+-(?:section|wrap)$")


def faq_shell(text):
    """本页 FAQ 版块的容器：section 上的 *-section / *-wrap class，以及紧挨着的内层容器 class。
    「同类模型 API」沿用同一套容器，宽度和左右边距就和上一个版块（FAQ）自动一致；
    各系列 FAQ 的内容列宽度从 668px 到 1248px 不等，没法写成一个固定宽度。
    背景类（j-dark、p-band-white 这类）不沿用，免得把这个版块也染成深色。"""
    m = re.search(r'<section class="([^"]+)"[^>]*\bid="faq"[^>]*>\s*(?:<div class="([^"]+)"[^>]*>)?', text)
    if not m:
        return "", ""
    sec = [c for c in m.group(1).split() if SEC_TOKEN.match(c)]
    # section 自己已经带 *-wrap（Grok 文本页）时，后面紧跟的 div 只是标题块，不是内容容器
    wrap = "" if any(c.endswith("-wrap") for c in sec) else (m.group(2) or "")
    return " ".join(sec), wrap


def block(lang, slug, sec_cls="", wrap_cls=""):
    kind = category(slug)
    own = family(slug)
    pool = [t for t in TARGETS[kind] if t[0] != own and t[1] != slug]
    shift = zlib.crc32(slug.encode()) % len(pool)
    picks = (pool[shift:] + pool[:shift])[:6]
    c = COPY[lang]
    items = "".join(
        f'<li><a href="/{lang}/models/{target}"><b>{name} API</b><span>{c["go"]} →</span></a></li>'
        for _, target, name in picks)
    # rel-inner 包住标题、说明和列表：这样说明文字不会是容器的直接子元素，深色页的 ".o-wrap>p" 之类规则碰不到它
    inner = (f'<div class="rel-inner"><h2 id="related-title">{c["h2"]}</h2>'
             f'<p>{c["lead"].format(kind=c["kind"][kind])}</p><ul class="rel-list">{items}</ul></div>')
    if wrap_cls:
        body = f'<div class="{wrap_cls}">{inner}</div>'
    elif sec_cls:
        body = inner                      # section 自己就是内容列（Kling 等）
    else:
        body = f'<div class="rel-wrap">{inner}</div>'
    return (f'{START}<section class="{("rel-models " + sec_cls).strip()}" id="related" aria-labelledby="related-title">'
            f'{body}</section>{END}')


def apply(path, lang):
    slug = path.stem
    text = path.read_text(encoding="utf-8")
    new = re.sub(re.escape(START) + r"\n?.*?" + re.escape(END) + r"\n?", "", text, flags=re.S)
    # 放在收尾 CTA（<section class="*-final">）前面；CTA 前面如果紧跟一条注释（<!-- Final CTA -->），插在注释前，注释仍然贴着 CTA
    sec_cls, wrap_cls = faq_shell(new)
    cta = re.search(r'<section class="[^"]*-final[^"]*"', new)
    if cta:
        pos = cta.start()
        before = new[:pos].rstrip()
        if before.endswith("-->"):
            pos = before.rfind("<!--")
        ls = new.rfind("\n", 0, pos) + 1
        if new[ls:pos].strip() == "":
            pos = ls
        new = new[:pos] + block(lang, slug, sec_cls, wrap_cls) + "\n" + new[pos:]
    else:                                   # 没有收尾 CTA 的页面：保持原来的位置
        anchor = "</main>" if "</main>" in new else "<footer"
        if anchor not in new:
            return "no-anchor"
        new = new.replace(anchor, block(lang, slug, sec_cls, wrap_cls) + anchor, 1)
    new = re.sub(r"scrollbar\.css\?v=[0-9a-z]+", f"scrollbar.css?v={CSS_VERSION}", new)
    if new == text:
        return "unchanged"
    path.write_text(new, encoding="utf-8", newline="\n")
    return "written"


def main():
    counts = {}
    for lang in ("zh", "en"):
        for path in sorted((ROOT / lang / "models").glob("*.html")):
            if path.name == "index.html":
                continue
            result = apply(path, lang)
            counts[result] = counts.get(result, 0) + 1
    print(counts)


if __name__ == "__main__":
    main()
