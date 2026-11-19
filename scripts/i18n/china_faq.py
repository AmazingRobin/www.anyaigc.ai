# 英文页删除「能否从中国大陆调用」类 FAQ（用户 2026-11-18 确认；规则见记忆 en-no-china-access-claim）。
#   纯问题（Can I call X from mainland China?）                     → 整条删除
#   复合问题（并发限制 / xAI 账号 / 怎么拿 key + 能否从大陆调用）    → 只去掉中国相关的问句和句子，保留其余信息
#   已经有新语言译本的页面（翻译源早已整条丢掉了这类 FAQ）            → 复合问题也整条删除，保证英文页和译本内容一致
# 可见 FAQ 和 JSON-LD 的 FAQPage 一起改；JSON-LD 只改对应的 Question 对象，其余字节原样保留（41 个页面的 JSON-LD 排版各不相同）。
# 用法：python scripts/i18n/china_faq.py [--dry-run] [slug 前缀...]    重复运行结果不变；系列重新生成英文页后要再跑一次。
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H
import overseas as O

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = '\n'
CHINA_Q = re.compile(r'mainland China|from China|in China')
PURE_Q = re.compile(r'Can I call (?:it|the .+?|.+?) from (?:mainland )?China\?')
NEW_LANGS = ('ja', 'ko', 'es', 'de')


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def article(name):
    return 'an' if name[:1].lower() in 'aeiou' else 'a'


def rewrite(q, a):
    """复合问题：返回 (新问题, 新答案 html)；认不出的返回 None。"""
    m = re.fullmatch(r'(Are there concurrency limits\?|Is there a concurrency limit\?) Does it work from (?:mainland )?China\?', q)
    if m:
        a2 = re.sub(r', which is tuned for networks in mainland China, so you usually do not need a proxy\.', '.', a)
        a2 = a2.replace(', which is tuned for networks in mainland China, so you usually do not need a proxy, a Google account, or an overseas credit card.',
                        ', and you do not need a Google account or an overseas credit card.')
        a2 = a2.replace(', reachable from mainland China,', ',')
        return m.group(1), a2
    if q == 'Do I need an xAI account? Does it work from mainland China?':
        return 'Do I need an xAI account?', a.replace(', reachable directly from mainland China,', ',')
    m = re.fullmatch(r'Can I call (?:the (.+?) API|it) from mainland China, and how do I get (?:a|an)(?: API)? key\?', q)
    if m:
        new_q = f'How do I get {article(m.group(1))} {m.group(1)} API key?' if m.group(1) else 'How do I get an API key?'
        a2 = re.sub(r'^Yes\. AnyAIGC is (?:tuned|optimized) for networks in mainland China, so you can usually call '
                    r'<code>[^<]*</code> without (?:an extra |a )?proxy\.(?: Billing is in USD\.)? ', '', a)
        return new_q, a2
    return None


def object_spans(raw):
    """JSON 文本里所有对象 {...} 的 (起, 止) 区间，字符串感知。"""
    spans, stack, in_str, esc = [], [], False, False
    for i, ch in enumerate(raw):
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == '{':
            stack.append(i)
        elif ch == '}' and stack:
            spans.append((stack.pop(), i + 1))
    return spans


def question_objects(raw):
    out = []
    for s, e in object_spans(raw):
        try:
            o = json.loads(raw[s:e])
        except ValueError:
            continue
        if isinstance(o, dict) and o.get('@type') == 'Question':
            out.append((s, e, o))
    return out


def ld_delete(raw, s, e):
    """删掉 [s, e) 这个对象：优先连同后面的逗号和空白一起删，最后一个元素则连同前面的逗号。"""
    m = re.compile(r',\s*').match(raw, e)
    if m:
        return raw[:s] + raw[m.end():]
    k = s
    while k > 0 and raw[k - 1] in ' \t\r\n':
        k -= 1
    if k > 0 and raw[k - 1] == ',':
        return raw[:k - 1] + raw[e:]
    raise ValueError('FAQ 只剩一个元素，无法安全删除')


def ld_replace(raw, s, e, obj):
    """用新对象替换 [s, e)，沿用原来的排版（单行 / 缩进 2）。"""
    old = raw[s:e]
    ascii_ = '\\u' in old
    if NL in old:
        ls = raw.rfind(NL, 0, s) + 1
        base = raw[ls:s] if not raw[ls:s].strip() else ''
        text = json.dumps(obj, ensure_ascii=ascii_, indent=2).replace(NL, NL + base)
    else:
        text = json.dumps(obj, ensure_ascii=ascii_, separators=(', ', ': '))
    return raw[:s] + text + raw[e:]


def process(src, translated):
    root = H.parse(src)
    sec = O.find_section(root, src, 'faq')
    if sec is None:
        return src, [], []
    dets = [n for n in H.walk(sec) if n.tag == 'details']
    repl, notes, ld_ops = [], [], []
    for i, d in enumerate(dets):
        summ = next((k for k in d.kids if k.tag == 'summary'), None)
        if summ is None:
            continue
        q = O.inner_text(src, summ)
        if not CHINA_Q.search(q):
            continue
        qn = next((n for n in H.walk(summ) if n.tag == 'h3'), summ)
        p = next((n for n in H.walk(d) if n.tag == 'p'), None)
        a_html = src[p.so:p.ec] if p is not None else ''
        pure = PURE_Q.fullmatch(q) is not None
        new = None if (pure or translated) else rewrite(q, a_html)
        if not pure and not translated and new is None:
            raise SystemExit(f'认不出的复合问题：{q!r}')
        if new is None:                                     # 整条删除
            s, e = O.line_span(src, d)
            repl.append((s, e, ''))
            if 'open' in d.attrs and i + 1 < len(dets) and 'open' not in dets[i + 1].attrs:
                repl.append((dets[i + 1].s + len('<details'), dets[i + 1].s + len('<details'), ' open'))
            ld_ops.append(('delete', norm(q), None, None))
            notes.append(('delete', q))
        else:
            nq, na = new
            if CHINA_Q.search(nq) or CHINA_Q.search(na) or 'China' in na:
                raise SystemExit(f'改写后仍含中国相关内容：{nq!r} / {na!r}')
            repl.append((qn.so, qn.ec, nq))
            repl.append((p.so, p.ec, na))
            ld_ops.append(('rewrite', norm(q), nq, O.strip_tags(na)))
            notes.append(('rewrite', q, nq, O.strip_tags(na)))
    if not repl:
        return src, [], []
    # JSON-LD
    for n in H.walk(root):
        if n.tag == 'script' and 'ld+json' in n.attrs:
            raw = src[n.so:n.ec]
            new_raw = raw
            for op, q, nq, na in ld_ops:
                found = [(s, e, o) for s, e, o in question_objects(new_raw) if norm(o.get('name', '')) == q]
                if len(found) != 1:
                    raise SystemExit(f'JSON-LD 里找不到唯一的 Question：{q!r}（{len(found)}）')
                s, e, o = found[0]
                if op == 'delete':
                    new_raw = ld_delete(new_raw, s, e)
                else:
                    o['name'] = nq
                    o['acceptedAnswer']['text'] = na
                    new_raw = ld_replace(new_raw, s, e, o)
            repl.append((n.so, n.ec, new_raw))
            break
    out = H.apply_spans(src, repl)
    # 校验：可见 FAQ 与 JSON-LD 逐条一致，且不再有中国相关问题
    pairs = O.faq_pairs(out)
    r2 = H.parse(out)
    ld = None
    for n in H.walk(r2):
        if n.tag == 'script' and 'ld+json' in n.attrs:
            for node in json.loads(out[n.so:n.ec]).get('@graph', []):
                if node.get('@type') == 'FAQPage':
                    ld = [(norm(x['name']), norm(x['acceptedAnswer']['text'])) for x in node['mainEntity']]
    vis = [(norm(a), norm(b)) for a, b in pairs]
    if ld != vis:
        raise SystemExit(f'改完后可见 FAQ 与 JSON-LD 不一致：可见 {len(vis)} 条，JSON-LD {len(ld or [])} 条')
    if any(CHINA_Q.search(a) for a, _ in vis):
        raise SystemExit('改完后仍有中国相关 FAQ 问题')
    return out, notes, ld_ops


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    stat = {'delete': 0, 'rewrite': 0}
    changed = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)[:-5]
        if name == 'index' or (args and not any(name.startswith(a) for a in args)):
            continue
        src = io.open(f, encoding='utf-8').read()
        translated = any(os.path.isfile(os.path.join(ROOT, lang, 'models', name + '.html')) for lang in NEW_LANGS)
        out, notes, _ = process(src, translated)
        if out == src:
            continue
        changed.append(name)
        for note in notes:
            stat[note[0]] += 1
            if note[0] == 'rewrite' and '--verbose' in sys.argv:
                print(f'[{name}]\n  Q: {note[1]}\n  → {note[2]}\n  A: {note[3]}')
        if not dry:
            io.open(f, 'w', encoding='utf-8', newline=NL).write(out)
    print(('将修改' if dry else '已修改'), len(changed), '页；整条删除', stat['delete'], '条，改写', stat['rewrite'], '条')


if __name__ == '__main__':
    main()
