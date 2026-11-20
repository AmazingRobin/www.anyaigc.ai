# 英文页正文里的「中国大陆可访问」卖点：卡片标题/正文、句子里的一段（用户 2026-11-18 确认删除；规则见记忆 en-no-china-access-claim）。
#   卡片：去掉中国相关的标题和说法，保留卡片里原有的其它事实（如「不需要 xAI 账号」），卡片数量不变，网格不会缺格。
#   句子：用 overseas.CHINA_RULES 删掉中国大陆相关的那一小段（与新语言页翻译源用同一组规则，两边不会错开）。
# 可见文字和 JSON-LD 里的同一句话一起改；JSON-LD 只替换对应片段，其余字节原样保留。
# 不处理：meta keywords 里的 "OpenAI API China" 这类关键词、「Chinese VAT」开票说法（各系列的 overseas.py 负责）。
# 用法：python scripts/i18n/china_body.py [--dry-run] [slug 前缀...]    重复运行结果不变；系列重新生成英文页后要再跑一次。
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
CODE = '<code>https://anyaigc.ai</code>'
SYSTEMONE = '<code>https://anyaigc.ai/v1/systemone</code>'

# 连续的几段文字（标题、正文）整体换成新写法。键是旧文字，必须连续出现。
CARDS = [
    (['Direct access from mainland China', 'Use the AnyAIGC endpoint without a separate Volcano Engine account.'],
     ['No Volcano Engine account needed', 'Use the AnyAIGC endpoint without a separate Volcano Engine account.']),
    (['Direct access in China', 'Connect through https://anyaigc.ai with one provider account.'],
     ['One provider account', 'Connect through https://anyaigc.ai with one provider account.']),
    (['Direct access from China', f'The endpoint {CODE} works on mainland networks, no xAI account needed.'],
     ['No xAI account needed', f'The endpoint {CODE} needs no xAI account.']),
    (['Reachable from China', f'Send requests to {SYSTEMONE}, usually with no extra proxy.'],
     ['Send requests directly', f'Send requests to {SYSTEMONE}.']),
    (['Stable', 'Dev to production', 'Stable calls from dev to production.'],
     ['1 endpoint', 'Dev to production', 'Use the same endpoint from development to production.']),
    (['Reachable from mainland China', f'Send requests to {SYSTEMONE}, usually without an extra proxy.'],
     ['Send requests directly', f'Send requests to {SYSTEMONE}.']),
    (['Works from mainland China', f'Requests go to {SYSTEMONE}, usually with no extra proxy.'],
     ['Send requests directly', f'Requests go to {SYSTEMONE}.']),
    (['Works from mainland China', f'The base URL {CODE} is reachable from China, with no Meta developer account needed.'],
     ['No Meta account needed', f'The base URL {CODE} needs no Meta developer account.']),
    (['Works from mainland China', f'The base URL {CODE} is reachable from China, with no Meta account needed.'],
     ['No Meta account needed', f'The base URL {CODE} needs no Meta account.']),
    (['Direct access from China', 'Call AnyAIGC directly from mainland China and configure timeouts and retries for your workload.'],
     ['Direct access', 'Call AnyAIGC directly and configure timeouts and retries for your workload.']),
    (['China-ready', 'No extra proxy', 'Optimized for networks in mainland China, with stable calls from dev to production.'],
     ['1 endpoint', 'Dev to production', 'Use the same endpoint from development to production.']),
]


def card_fixes(spans):
    """返回 {span 下标: 新文字}。"""
    out = {}
    for old, new in CARDS:
        n = len(old)
        for i in range(len(spans) - n + 1):
            if all(spans[i + k].kind == 'unit' and spans[i + k].text == old[k] for k in range(n)):
                for k in range(n):
                    out[i + k] = new[k]
    return out


def apply_rules(t, rules):
    for pat, rep in rules:
        t = re.sub(pat, rep, t)
    return t


KEYWORD_DROP = re.compile(r'^(?:(?:OpenAI|Gemini) API China|GPT API 中转|OpenAI API 国内)$')
META_KW = re.compile(r'(<meta name="keywords" content=")([^"]*)(")')


def strip_keywords(src):
    """meta keywords 里删掉 "OpenAI API China" / "Gemini API China"（用户 2026-11-18 确认）；其余词条和顺序不变。"""
    def fix(m):
        items = m.group(2).split(',')
        kept = [x for x in items if not KEYWORD_DROP.match(x.strip())]
        return m.group(1) + ','.join(kept) + m.group(3) if len(kept) != len(items) else m.group(0)
    return META_KW.sub(fix, src, count=1)


def process(src):
    rules = O.CHINA_RULES
    kw_src = strip_keywords(src)
    kw_changed = kw_src != src
    src = kw_src
    spans = H.collect(src)
    fixes = card_fixes(spans)
    repl, stat = [], {'card': 0, 'rule': 0, 'ld': 0, 'kw': 1 if kw_changed else 0}
    for i, s in enumerate(spans):
        if s.kind == 'ldjson':
            raw = s.text
            new = apply_rules(raw, rules)
            if new != raw:
                json.loads(new)
                repl.append((s.s, s.e, new))
                stat['ld'] += 1
            continue
        if i in fixes:
            new = fixes[i]
            stat['card'] += 1
        else:
            new = apply_rules(s.text, rules)
            if new != s.text:
                stat['rule'] += 1
        if new != s.text:
            repl.append((s.s, s.e, new))
    if not repl:
        return src, stat
    out = H.apply_spans(src, repl)
    # 校验：可见 FAQ 与 JSON-LD 的 FAQPage 仍然逐条一致
    norm = lambda x: re.sub(r'\s+', ' ', x).strip()
    vis = [(norm(a), norm(b)) for a, b in O.faq_pairs(out)]
    ld = None
    for n in H.walk(H.parse(out)):
        if n.tag == 'script' and 'ld+json' in n.attrs:
            for node in json.loads(out[n.so:n.ec]).get('@graph', []):
                if node.get('@type') == 'FAQPage':
                    ld = [(norm(x['name']), norm(x['acceptedAnswer']['text'])) for x in node['mainEntity']]
    if ld is not None and ld != vis:
        raise SystemExit('改完后可见 FAQ 与 JSON-LD 不一致')
    return out, stat


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    total = {'card': 0, 'rule': 0, 'ld': 0, 'kw': 0}
    changed = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'en', 'models', '*.html'))):
        name = os.path.basename(f)[:-5]
        if name == 'index' or (args and not any(name.startswith(a) for a in args)):
            continue
        src = io.open(f, encoding='utf-8').read()
        out, stat = process(src)
        if out == src:
            continue
        changed.append(name)
        for k in total:
            total[k] += stat[k]
        if not dry:
            io.open(f, 'w', encoding='utf-8', newline=NL).write(out)
    print(('将修改' if dry else '已修改'), len(changed), '页；卡片文字', total['card'], '段，句子', total['rule'], '处，JSON-LD', total['ld'], '处，关键词', total['kw'], '页')


if __name__ == '__main__':
    main()
