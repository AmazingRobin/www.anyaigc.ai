# 调查：英文页里含 "China" 的 FAQ 问题有哪些写法、每页几条；JSON-LD 按原格式重新序列化是否和原文一致（决定能不能只删一条而不改其余字节）。
# 用法：python scripts/i18n/china_faq_survey.py
import collections
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H
import overseas as O

ROOT = O.__file__ and os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = '\n'


def faq_details(src):
    root = H.parse(src)
    sec = O.find_section(root, src, 'faq')
    if sec is None:
        return root, []
    return root, [n for n in H.walk(sec) if n.tag == 'details']


def main():
    questions = collections.Counter()
    per_page = collections.Counter()
    no_faq, roundtrip_bad, multi_ld = [], [], 0
    pages = 0
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)
        if name == 'index.html':
            continue
        pages += 1
        src = io.open(f, encoding='utf-8').read()
        root, dets = faq_details(src)
        if not dets:
            no_faq.append(name)
        n = 0
        for d in dets:
            summ = next((k for k in d.kids if k.tag == 'summary'), None)
            q = O.inner_text(src, summ) if summ is not None else ''
            if re.search(r'China|Chinese|mainland', q, re.I):
                questions[re.sub(r'(?:Claude |GPT-?|Gemini |Grok |Qwen|Kimi |GLM-?|DeepSeek |Doubao |Kling |Vidu|MiniMax |Suno |Llama )[\w .\-/+]*?(?= API| from| in)', 'X', q)] += 1
                n += 1
        per_page[n] += 1
        # JSON-LD 往返
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
            raw = m.group(1)
            data = json.loads(raw)
            multi = NL in raw.strip()
            text = json.dumps(data, ensure_ascii=False, indent=2 if multi else None, separators=None if multi else (', ', ': '))
            same = (NL + text + NL == raw) if multi else (text == raw)
            if not same:
                roundtrip_bad.append(name)
    print('pages', pages, '| FAQ China-question count per page:', dict(per_page))
    print('pages without a parsable FAQ section:', no_faq)
    print('JSON-LD not byte-identical after re-serialising:', len(roundtrip_bad), roundtrip_bad[:8])
    print('distinct China questions:')
    for q, n in questions.most_common(12):
        print(f'  {n:4d}  {q[:110]}')


if __name__ == '__main__':
    main()
