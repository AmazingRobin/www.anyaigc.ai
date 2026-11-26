# -*- coding: utf-8 -*-
"""Inject a model-specific section into templated topic pages.

The section states only facts from scripts/seo_model_facts.py (vendor docs)
plus the price already printed in that page's own table, and it is written
idempotently: running this twice changes nothing.

Usage: PYTHONIOENCODING=utf-8 python scripts/seo_unique.py
"""
import html
import re
from pathlib import Path

from seo_model_facts import COMPARE, FACTS

ROOT = Path(__file__).resolve().parent.parent
MARK = "q-unique"

KIND_ZH = {"flash": "低时延", "plus": "均衡", "max": "旗舰", "open": "开源权重", "sized": "固定参数规模",
           "omni": "全模态", "vl": "视觉语言", "coder": "推理", "roleplay": "角色扮演"}
KIND_EN = {"flash": "low-latency", "plus": "balanced", "max": "flagship", "open": "open-weight", "sized": "fixed-size",
           "omni": "omni-modal", "vl": "vision-language", "coder": "reasoning", "roleplay": "role-play"}


def fmt_tokens(n, zh):
    """Spell the count out so it is never rounded."""
    if zh and n % 10_000 == 0:
        return f"{n // 10_000} 万"
    return f"{n:,}"


def prices_of(page):
    """(input, output) USD per 1M tokens, read from the page's price table."""
    rows = re.findall(r"<tr><th>([^<]*)</th><td><code>[^<]*</code></td><td>\$([0-9.]+) / 1M</td>", page)
    got = {}
    for label, price in rows:
        key = "in" if label.startswith("输入") or label.startswith("Input") else \
              "out" if label.startswith("输出") or label.startswith("Output") else None
        if key and key not in got:
            got[key] = price
    return got.get("in"), got.get("out")


def section(lang, slug, pin, pout):
    f = FACTS[slug]
    zh = lang == "zh"
    ctx = fmt_tokens(f["context"], zh)
    out = fmt_tokens(f["out"], zh) if f["out"] else None
    kind = KIND_ZH[f["kind"]] if zh else KIND_EN[f["kind"]]
    if zh:
        bits = [f"上下文窗口 {ctx} tokens"]
        if out:
            bits.append(f"单次输出最长 {out} tokens")
        if f["kind"] != "sized":
            bits.append(f"定位是{f['gen']} 的{kind}型号")
        spec = "，".join(bits) + "。"
        price = f"本页标价为每百万 Token 输入 ${pin}、输出 ${pout}，与上方价格表是同一组数字。"
        tail = "以上规格数字来自千问官方模型文档，价格以本页表格为准，模型广场的实时价格优先。"
    else:
        bits = [f"a context window of {ctx} tokens"]
        if out:
            bits.append(f"up to {out} tokens of output per response")
        spec = "It offers " + " and ".join(bits) + (f", and it is the {kind} model in the {f['gen']} generation." if f["kind"] != "sized" else ".")
        price = f"This page lists ${pin} per million input tokens and ${pout} per million output tokens, the same figures as the pricing table above."
        tail = "These specifications come from the official Qwen model documentation. The table on this page is the price, and the model catalog is authoritative for live rates."
    paras = [f["note_zh" if zh else "note_en"], spec, price]
    cmp = next(((a, b, cz, ce) for a, b, cz, ce in COMPARE if a == slug), None)
    if cmp:
        _, other, cz, ce = cmp
        href = f"/{lang}/models/{other}"
        if zh:
            paras.append(f'拿它和 <a href="{href}">{html.escape(other)}</a> 比较，{cz}，选后者更合适。')
        else:
            paras.append(f'Set it next to <a href="{href}">{html.escape(other)}</a> and choose that model instead {ce}.')
    body = "".join(f"<p>{p}</p>" for p in paras + [tail])
    h2 = "这个型号的规格与选型" if zh else "Specs and how to choose it"
    return (f'<section class="q-section" id="{MARK}"><div class="q-wrap q-narrow">'
            f'<p class="q-kicker">{html.escape(f["gen"])}</p><h2>{h2}</h2>{body}</div></section>')


def apply(path):
    slug = path.stem
    if slug not in FACTS:
        text = path.read_text(encoding="utf-8")
        stale = re.compile(rf'<section class="q-section" id="{MARK}">.*?</section>', re.S)
        if stale.search(text):
            path.write_text(stale.sub("", text, count=1), encoding="utf-8", newline="\n")
            return "removed"
        return "skip"
    lang = path.parts[-3]
    text = path.read_text(encoding="utf-8")
    pin, pout = prices_of(text)
    if not pin or not pout:
        return "no-price"
    block = section(lang, slug, pin, pout)
    pattern = re.compile(rf'<section class="q-section" id="{MARK}">.*?</section>', re.S)
    if pattern.search(text):
        new = pattern.sub(block, text, count=1)
    else:
        anchor = '<section class="q-section" id="faq">'
        if anchor not in text:
            return "no-anchor"
        new = text.replace(anchor, block + anchor, 1)
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")
        return "written"
    return "unchanged"


def main():
    counts = {}
    for lang in ("zh", "en"):
        for path in sorted((ROOT / lang / "models").glob("qwen*.html")):
            result = apply(path)
            counts[result] = counts.get(result, 0) + 1
    print(counts)


if __name__ == "__main__":
    main()
