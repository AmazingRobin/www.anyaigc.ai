# -*- coding: utf-8 -*-
"""Model-specific "specs and how to choose" sections for MiniMax Speech and
HappyHorse pages, the two families with the highest body similarity.

Facts come only from vendor pages (checked 2026-11-15):
  MiniMax  https://platform.minimax.io/docs/guides/models-intro
           https://platform.minimax.io/docs/api-reference/speech-t2a-http
           https://www.minimax.io/news/minimax-speech-02 / -26 / -28
  Alibaba  https://www.alibabacloud.com/help/en/model-studio/video-generation
Prices are read from each page's own price table. The section sits before the
FAQ between fixed ids, so rerunning replaces it instead of duplicating it.

Usage: PYTHONIOENCODING=utf-8 python scripts/seo_unique_media.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MM_DOC = "https://platform.minimax.io/docs/guides/models-intro"
ALI_DOC = "https://www.alibabacloud.com/help/en/model-studio/video-generation"

# MiniMax's own one-line positioning for each model, plus generation facts.
SPEECH = {
    "speech-2.8-hd": ("超写实音质，支持声音标签", "Ultra-realistic quality featuring sound tags"),
    "speech-2.8-turbo": ("速度与自然语流兼顾", "Seamless speed meets natural flow"),
    "speech-2.6-hd": ("极致相似度，超高音质", "Ultimate similarity, ultra-high quality"),
    "speech-2.6-turbo": ("极致性价比，低延迟", "Ultimate value, low latency"),
    "speech-02-hd": ("复刻相似度更高，高音质生成", "Stronger replication similarity, high-quality voice generation"),
    "speech-02-turbo": ("节奏与稳定性更好，低延迟", "Superior rhythm and stability, low latency"),
}
GEN = {
    "2.8": ("Speech 2.8 新增原生声音标签，可以生成“嗯”“呃”“啊”这类口语停顿；10 秒音频样本即可复刻音色；背景噪声和合成痕迹更少；跨语言表现提升，首先覆盖中日语对。",
            "Speech 2.8 adds native sound tags for fillers such as \"um\", \"uh\" and \"ah\", clones a voice from a 10-second sample, reduces background noise and synthetic artifacts, and improves cross-lingual output, starting with Mandarin-Japanese."),
    "2.6": ("Speech 2.6 端到端延迟低于 250 毫秒，支持 40 多种语言，能正确读出网址、邮箱、电话号码、日期和金额，并用 Fluent LoRA 做音色复刻。",
            "Speech 2.6 has end-to-end latency under 250 milliseconds, supports more than 40 languages, reads URLs, emails, phone numbers, dates and amounts correctly, and uses Fluent LoRA for voice cloning."),
    "02": ("Speech-02 支持 32 种语言，采用可学习说话人编码器的零样本语音合成；Speech-02-HD 曾在 Artificial Analysis Speech Arena 和 Hugging Face TTS Arena 两个榜单排名第一。",
           "Speech-02 supports 32 languages and uses zero-shot synthesis with a learnable speaker encoder. Speech-02-HD ranked first on both the Artificial Analysis Speech Arena and the Hugging Face TTS Arena."),
}
API_ZH = "单次请求文本需少于 10,000 字符，采样率可选 8000–44100 Hz，输出格式支持 mp3、pcm、flac、wav、opus 等。"
API_EN = "Each request takes under 10,000 characters of text, sample rates from 8000 to 44100 Hz, and output in mp3, pcm, flac, wav, opus and other formats."

HH_MODE = {
    "t2v": ("文生视频，只需文字提示词", "text-to-video from a text prompt"),
    "i2v": ("图生视频，以一张图片作为首帧", "image-to-video, using one image as the first frame"),
    "r2v": ("参考生视频，用参考图保持主体和风格", "reference-to-video, keeping subjects and style from reference images"),
    "video-edit": ("视频编辑，用文字指令修改已有视频", "video editing of an existing clip with text instructions"),
}


def table_prices(page):
    i = page.find('id="pricing"')
    sec = page[i:page.find("</section>", i)] if i >= 0 else ""
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", sec, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        price = next((c for c in cells if re.match(r"^[\$¥]\s?[0-9]", c)), None)
        if price:
            rows.append((cells[0], price))
    return rows


def link(href, text):
    return f'<a href="{href}">{html.escape(text)}</a>'


def speech_section(lang, slug, page):
    zh = lang == "zh"
    gen, tier = re.match(r"speech-(2\.8|2\.6|02)-(hd|turbo)", slug).groups()
    sibling = f"speech-{gen}-{'turbo' if tier == 'hd' else 'hd'}"
    newer = {"02": "2.6", "2.6": "2.8"}.get(gen)
    rows = table_prices(page)
    pos = SPEECH[slug][0 if zh else 1]
    if zh:
        paras = [f"MiniMax 官方对 {slug} 的定位是：{pos}。",
                 GEN[gen][0], API_ZH]
        if rows:
            paras.append("本页价格为" + "、".join(f"{a} {b}" for a, b in rows) + "，与上方价格表一致。")
        sib_pos = SPEECH[sibling][0]
        if tier == "hd":
            paras.append(f"同代的 {link('/zh/models/' + sibling, sibling)} 定位是“{sib_pos}”，实时交互、对延迟敏感时选它；音色相似度和音质优先时留在 HD。")
        else:
            paras.append(f"同代的 {link('/zh/models/' + sibling, sibling)} 定位是“{sib_pos}”，有声书、品牌配音这类音质优先的任务选它；对话和实时播报留在 Turbo。")
        if newer:
            paras.append(f"新项目可以先对比 {link(f'/zh/models/speech-{newer}-{tier}', f'speech-{newer}-{tier}')}，两代接口相同，切换只需改 model 参数。")
        tail = f"以上信息来自 {link(MM_DOC, 'MiniMax 官方模型介绍')} 和 MiniMax 官方发布公告；价格以本页表格为准，模型广场的实时价格优先。"
        h2, kicker = "这个型号的规格与选型", f"Speech {gen}"
    else:
        paras = [f"MiniMax positions {slug} as: {pos}.", GEN[gen][1], API_EN]
        if rows:
            paras.append("This page lists " + ", ".join(f"{a.lower()} at {b}" for a, b in rows) + ", the same figures as the pricing table above.")
        sib_pos = SPEECH[sibling][1]
        if tier == "hd":
            paras.append(f"{link('/en/models/' + sibling, sibling)} in the same generation is positioned as \"{sib_pos}\". Pick it for real-time, latency-sensitive use; stay on HD when voice similarity and audio quality come first.")
        else:
            paras.append(f"{link('/en/models/' + sibling, sibling)} in the same generation is positioned as \"{sib_pos}\". Pick it for audiobooks and branded voice-over where quality comes first; stay on Turbo for conversation and live narration.")
        if newer:
            paras.append(f"For a new project, compare {link(f'/en/models/speech-{newer}-{tier}', f'speech-{newer}-{tier}')} first. Both generations share the same API, so switching only changes the model parameter.")
        tail = f"Sources: {link(MM_DOC, 'MiniMax model overview')} and MiniMax release notes. The table on this page is the price, and the model catalog is authoritative for live rates."
        h2, kicker = "Specs and how to choose it", f"Speech {gen}"
    body = "".join(f"<p>{p}</p>" for p in paras) + f'<p class="mm-unique-note">{tail}</p>'
    return (f'<section class="mm-section" id="mm-unique" aria-labelledby="mm-unique-title"><div class="mm-wrap">'
            f'<p class="mm-kicker">{kicker}</p><h2 id="mm-unique-title">{h2}</h2>{body}</div></section>\n')


def happyhorse_section(lang, slug, page):
    zh = lang == "zh"
    version, mode = re.match(r"happyhorse-(1\.[01])-(t2v|i2v|r2v|video-edit)", slug).groups()
    res = "480P、720P、1080P" if version == "1.1" else "720P、1080P"
    res_en = "480P, 720P and 1080P" if version == "1.1" else "720P and 1080P"
    rows = table_prices(page)
    other = f"happyhorse-{'1.0' if version == '1.1' else '1.1'}-{mode}"
    has_other = (ROOT / lang / "models" / f"{other}.html").is_file()
    mode_zh, mode_en = HH_MODE[mode]
    if zh:
        paras = [f"{slug} 是 HappyHorse {version} 的{mode_zh}。",
                 f"阿里云官方文档列出的输出规格：{res}，时长 3–15 秒，24 fps，MP4 格式，同时生成音频。"]
        if rows:
            listed = "、".join(a for a, _ in rows)
            paras.append("本页价格为" + "、".join(f"{a} {b}" for a, b in rows) + f"，与上方价格表一致" + (f"；官方支持的 480P 本页暂未列价" if version == "1.1" and "480P" not in listed else "") + "。")
        if has_other:
            if version == "1.1":
                paras.append(f"和 {link('/zh/models/' + other, other)} 相比，1.1 多了 480P 档，适合先用低分辨率批量试稿，再用 720P/1080P 出成片。")
            else:
                paras.append(f"{link('/zh/models/' + other, other)} 在 1.0 的基础上增加了 480P 档；需要低分辨率批量试稿时选 1.1。")
        elif mode == "video-edit":
            paras.append("视频编辑目前只有 1.0 版本，要从零生成新视频请选同系列的文生、图生或参考生视频型号。")
        tail = f"规格来自 {link(ALI_DOC, '阿里云百炼视频生成文档')}；价格以本页表格为准，模型广场的实时价格优先。"
        h2 = "这个型号的规格与选型"
    else:
        paras = [f"{slug} is the HappyHorse {version} model for {mode_en}.",
                 f"Alibaba Cloud's documentation lists {res_en} output, 3 to 15 seconds per clip, 24 fps, MP4, with audio generated alongside the video."]
        if rows:
            listed = " ".join(a for a, _ in rows)
            paras.append("This page lists " + ", ".join(f"{a} at {b}" for a, b in rows) + ", the same figures as the pricing table above." + (" 480P is officially supported but not priced on this page yet." if version == "1.1" and "480P" not in listed else ""))
        if has_other:
            if version == "1.1":
                paras.append(f"Compared with {link('/en/models/' + other, other)}, version 1.1 adds a 480P tier, useful for low-cost drafts before rendering finals at 720P or 1080P.")
            else:
                paras.append(f"{link('/en/models/' + other, other)} adds a 480P tier on top of 1.0. Choose 1.1 when you want low-resolution drafts.")
        elif mode == "video-edit":
            paras.append("Video editing is only available in version 1.0. To generate new footage, use the text, image or reference models in the same family.")
        tail = f"Specs come from the {link(ALI_DOC, 'Alibaba Cloud Model Studio video generation docs')}. The table on this page is the price, and the model catalog is authoritative for live rates."
        h2 = "Specs and how to choose it"
    body = "".join(f"<p>{p}</p>" for p in paras + [tail])
    return (f'<section class="q-section" id="q-unique"><div class="q-wrap q-narrow">'
            f'<p class="q-kicker">HappyHorse {version}</p><h2>{h2}</h2>{body}</div></section>')


GEN_CARDS = {
    "2.8": [("原生声音标签", "Native sound tags", "可生成“嗯”“呃”“啊”等口语停顿，语音更自然。", "Generates fillers such as \"um\", \"uh\" and \"ah\" for natural speech."),
            ("10 秒复刻音色", "10-second voice cloning", "用 10 秒音频样本即可复刻音色。", "Clones a voice from a 10-second sample.")],
    "2.6": [("低于 250 毫秒", "Under 250 ms", "端到端延迟低于 250 毫秒。", "End-to-end latency under 250 milliseconds."),
            ("40 多种语言", "40+ languages", "能正确读出网址、邮箱、电话、日期和金额。", "Reads URLs, emails, phone numbers, dates and amounts correctly.")],
    "02": [("32 种语言", "32 languages", "覆盖多种口音与情绪表达。", "Covers a wide range of accents and emotional expression."),
           ("零样本合成", "Zero-shot synthesis", "采用可学习说话人编码器。", "Uses a learnable speaker encoder.")],
}
USE = {
    "hd": [("有声书与长文", "Audiobooks and long-form", "音色一致、音质优先，适合逐段合成整本内容。", "Consistent voice and top quality for chapter-by-chapter narration."),
           ("品牌与角色配音", "Brand and character voice-over", "复刻相似度高，适合固定的品牌声音或角色。", "High replication similarity for a fixed brand or character voice."),
           ("课程与讲解", "Courses and explainers", "为教学和产品介绍制作高音质配音。", "High-quality narration for lessons and product walkthroughs.")],
    "turbo": [("实时对话助手", "Real-time assistants", "低延迟，适合语音助手和客服回复。", "Low latency for voice assistants and support replies."),
              ("播报与通知", "Announcements and alerts", "节奏稳定，适合新闻、提醒和系统播报。", "Stable rhythm for news, reminders and system prompts."),
              ("大批量配音", "High-volume voice-over", "单价更低，适合批量生成短音频。", "Lower rate for generating many short clips.")],
}


def cards(items, zh):
    return "".join(f'<article class="mm-feature"><span class="mm-number">0{i}</span><h3>{html.escape(c[0 if zh else 1])}</h3>'
                   f'<p>{html.escape(c[2 if zh else 3])}</p></article>' for i, c in enumerate(items, 1))


def set_grid(page, sid, inner):
    pat = re.compile(r'(<section[^>]*id="%s".*?<div class="mm-feature-grid">).*?(</div>\s*</div></section>)' % sid, re.S)
    return pat.sub(lambda m: m.group(1) + inner + m.group(2), page, count=1)


def speech_cards(lang, slug, page):
    zh = lang == "zh"
    gen, tier = re.match(r"speech-(2\.8|2\.6|02)-(hd|turbo)", slug).groups()
    pos = SPEECH[slug]
    api = ("单次少于 10,000 字符", "Under 10,000 characters", "采样率 8000–44100 Hz，支持 mp3、wav、flac、opus 等格式。",
           "Sample rates 8000–44100 Hz; mp3, wav, flac, opus and more.")
    own = ("官方定位" if zh else "Official positioning", "", pos[0], pos[1])
    caps = [(own[0], own[0], own[2], own[3])] + GEN_CARDS[gen] + [api]
    page = set_grid(page, "capabilities", cards(caps, zh))
    return set_grid(page, "use-cases", cards(USE[tier], zh))


def happyhorse_cards(slug, page):
    # 1.1 officially supports 480P too; the card text was copied from 1.0.
    if not slug.startswith("happyhorse-1.1-"):
        return page
    page = page.replace("<h3>720P / 1080P</h3>", "<h3>480P / 720P / 1080P</h3>")
    page = page.replace("按分辨率与生成视频时长计费，先确定规格再估算费用。", "官方支持 480P、720P、1080P，时长 3–15 秒；按分辨率与时长计费。")
    page = page.replace("Choose a resolution and output duration before estimating cost.", "Officially supports 480P, 720P and 1080P, 3–15 seconds; billed by resolution and duration.")
    return page


def model_faq(lang, slug):
    """Two FAQ items that only this model's page can answer, from the same official facts."""
    zh = lang == "zh"
    m = re.match(r"speech-(2\.8|2\.6|02)-(hd|turbo)", slug)
    if m:
        gen, tier = m.groups()
        sib = f"speech-{gen}-{'turbo' if tier == 'hd' else 'hd'}"
        pos, sib_pos = SPEECH[slug][0 if zh else 1], SPEECH[sib][0 if zh else 1]
        if zh:
            return [(f"{slug} 和 {sib} 有什么区别？",
                     f"MiniMax 官方定位：{slug} 是“{pos}”，{sib} 是“{sib_pos}”。HD 优先音色相似度和音质，Turbo 优先低延迟，两者接口和参数相同。"),
                    (f"{slug} 支持哪些语言和音频格式？",
                     GEN[gen][0] + " " + API_ZH)]
        return [(f"What is the difference between {slug} and {sib}?",
                 f"MiniMax positions {slug} as \"{pos}\" and {sib} as \"{sib_pos}\". HD favors voice similarity and audio quality, Turbo favors low latency; both use the same API and parameters."),
                (f"Which languages and audio formats does {slug} support?",
                 GEN[gen][1] + " " + API_EN)]
    m = re.match(r"happyhorse-(1\.[01])-(t2v|i2v|r2v|video-edit)", slug)
    if not m:
        return []
    version, mode = m.groups()
    res = "480P、720P、1080P" if version == "1.1" else "720P、1080P"
    res_en = "480P, 720P and 1080P" if version == "1.1" else "720P and 1080P"
    if zh:
        diff = ("1.1 比 1.0 多了 480P 档，其余规格相同：时长 3–15 秒、24 fps、MP4、同时生成音频。" if mode != "video-edit"
                else "视频编辑目前只有 1.0 版本；1.1 的文生、图生、参考生视频型号新增了 480P 档。")
        return [(f"{slug} 支持哪些分辨率和时长？", f"阿里云官方文档：{res}，每段 3–15 秒，24 fps，MP4 格式，同时生成音频。"),
                (f"HappyHorse 1.1 和 1.0 有什么区别？", diff)]
    diff = ("Version 1.1 adds a 480P tier; everything else matches 1.0: 3–15 seconds, 24 fps, MP4, with audio." if mode != "video-edit"
            else "Video editing is only available in 1.0. The 1.1 text, image and reference models add a 480P tier.")
    return [(f"Which resolutions and durations does {slug} support?",
             f"Per Alibaba Cloud's documentation: {res_en}, 3–15 seconds per clip, 24 fps, MP4, with audio generated."),
            ("What is the difference between HappyHorse 1.1 and 1.0?", diff)]


def add_faq(page, items):
    """Insert items after the first FAQ entry, in both the HTML and the FAQPage JSON-LD."""
    if not items:
        return page
    sec = re.search(r'<section[^>]*id="faq".*?</section>', page, re.S)
    first = re.search(r"<details[^>]*>.*?</details>", sec.group(0), re.S)
    ans_cls = re.search(r'<div class="([^"]+)"><p>', first.group(0)).group(1)
    new_html = [(q, a) for q, a in items if f"<h3>{html.escape(q, quote=False)}</h3>" not in sec.group(0)]
    if new_html:
        block = "".join(f'<details><summary><h3>{html.escape(q, quote=False)}</h3></summary>'
                        f'<div class="{ans_cls}"><p>{html.escape(a, quote=False)}</p></div></details>' for q, a in new_html)
        at = sec.start() + first.end()
        page = page[:at] + block + page[at:]
    ld = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', page, re.S)
    data = json.loads(ld.group(2))
    for node in data.get("@graph", [data]):
        if node.get("@type") == "FAQPage":
            names = [q["name"] for q in node["mainEntity"]]
            add = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                   for q, a in items if q not in names]
            node["mainEntity"][1:1] = add
    pretty = "\n" in ld.group(2).strip()
    body = json.dumps(data, ensure_ascii=False, indent=2 if pretty else None)
    if pretty:
        body = "\n" + body + "\n"
    return page[:ld.start(2)] + body + page[ld.end(2):]


def apply(path, lang):
    slug = path.stem
    page = path.read_text(encoding="utf-8")
    page = add_faq(page, model_faq(lang, slug))
    if slug in SPEECH:
        page = speech_cards(lang, slug, page)
    elif slug.startswith("happyhorse-1.1-"):
        page = happyhorse_cards(slug, page)
    original = path.read_text(encoding="utf-8")
    if slug in SPEECH:
        block, sid = speech_section(lang, slug, page), "mm-unique"
        anchor = re.search(r'<section class="mm-section[^"]*" id="faq"', page)
    elif re.match(r"happyhorse-1\.[01]-", slug):
        block, sid = happyhorse_section(lang, slug, page), "q-unique"
        anchor = re.search(r'<section class="q-section[^"]*" id="faq"', page)
    else:
        return "skip"
    old = re.search(rf'<section class="[^"]*" id="{sid}"[^>]*>.*?</section>\n?', page, re.S)
    if old:
        new = page[:old.start()] + block + page[old.end():]
    elif anchor:
        new = page[:anchor.start()] + block + page[anchor.start():]
    else:
        return "no-anchor"
    if new == original:
        return "unchanged"
    path.write_text(new, encoding="utf-8", newline="\n")
    return "written"


def main():
    counts = {}
    for lang in ("zh", "en"):
        for path in sorted((ROOT / lang / "models").glob("*.html")):
            r = apply(path, lang)
            if r != "skip":
                counts[r] = counts.get(r, 0) + 1
    print(counts)


if __name__ == "__main__":
    main()
