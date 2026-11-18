# 海外口径改写：把英文源页改成"非中文页面"的企业/发票/支付写法，再交给翻译。
# 用户 2026-11-17 确认的口径：
#   - 发票：在控制台自助开具，按实际充值金额开具（不写增值税、专票、中国发票流程）
#   - 支付方式：保留微信支付、支付宝、USDT、信用卡；去掉"对公转账"
#   - 删除「对公转账」「签订合同」两张企业卡片，以及对应的 FAQ
#   - 保留「专属客服和技术对接」
# 额外：「能否在中国大陆调用」的 FAQ 保留，只去掉答案里「企业可对公转账、开增值税发票」那一句。
# 这一层只改新增语言的源文，不改 /en/ 页面本身。
import html
import json
import re

import htmlseg as H

NL = '\n'

# 整张卡片/整个条目要删除：文本命中其一的 li/article 会被整体删除（限企业接入版块与支付方式行）
DROP_LABELS = {'Bank transfer', 'Contracts'}
# 整条 FAQ 要删除（问题文字匹配）
DROP_FAQ = [r'bank transfer and sign a contract']

# 开票/支付 FAQ：整条改写（问题 + 回答），不依赖各系列原文怎么写
INVOICE_Q = 'Can I get an invoice from AnyAIGC?'
INVOICE_A = 'Yes. You can issue invoices yourself in the console, for the amount you actually topped up.'
PAY_A = ('You can top up with WeChat Pay, Alipay, USDT or a credit card. Your balance is in USD and works across '
         'every model on the platform. Invoices can be issued in the console for the amount you topped up.')

# 整句精确替换（单元文本完全相等才替换）
EXACT = {
    'Business <strong>Contracts · invoices</strong>': 'Business <strong>Self-service invoices</strong>',
    'Engineering teams and companies can buy through a standard business process, with support for finance, legal and engineering.':
        'Teams can top up, issue invoices themselves, and work with a dedicated support and technical contact.',
    'Including China VAT invoices': 'Issue them yourself',
    'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.':
        'Issue an invoice in the console for the amount you actually topped up, whenever you need one.',
}

# 描述、关键词等里的短语（正则，对每个单元和结构化数据字符串都执行）
RULES = [
    (r'\s*Companies can pay by bank transfer and get [^.]*\.', ''),
    (r'Invoices and contracts for teams\.', 'Self-service invoices.'),
    (r'Invoices and contracts\.', 'Self-service invoices.'),
    (r'Bank transfer, VAT invoices\.', 'Self-service invoices.'),
    (r', VAT invoices\.', ', invoices.'),
    (r'\bVAT invoices\.', 'Invoices.'),
    (r'\bbank transfer, ', ''),
]

# 处理完仍不应出现在新语言页面里的说法；命中就报错，由人决定怎么写
LEFTOVER = re.compile(r'\bVAT\b|bank transfer|wire transfer|corporate (?:bank|account)|special invoice|service agreement|'
                      r'sign a contract|对公|专票', re.I)


def strip_tags(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def inner_text(src, n):
    return strip_tags(src[n.so:n.ec])


def line_span(src, n):
    """节点所在的整行区间（含缩进和换行），用来整块删除。"""
    s = src.rfind(NL, 0, n.s) + 1
    if src[s:n.s].strip():
        s = n.s
    e = n.e
    while e < len(src) and src[e] in ' \t':
        e += 1
    if e < len(src) and src[e] == NL and s != n.s:
        e += 1
    return s, e


def find_section(root, src, sid):
    for n in H.walk(root):
        if n.tag == 'section' and f'id="{sid}"' in n.attrs:
            return n
    return None


def climb_card(node):
    n = node
    while n is not None and n.tag not in ('li', 'article'):
        n = n.parent
    return n


def drop_cards(src):
    root = H.parse(src)
    sec = find_section(root, src, 'enterprise')
    if sec is None:
        return src
    kill = {}
    for n in H.walk(sec):
        if n.tag in ('strong', 'li', 'span', 'b', 'h3') and n.ec is not None and n.kids:
            if inner_text(src, n) in DROP_LABELS:
                card = climb_card(n)
                if card is not None and card.parent is not None and len(card.parent.kids) > 1:
                    kill[card.s] = card
    repl = []
    for card in kill.values():
        s, e = line_span(src, card)
        repl.append((s, e, ''))
    return H.apply_spans(src, repl)


def rewrite_faq(src):
    """删除/改写 FAQ 条目，然后把 JSON-LD 的 FAQPage 按可见内容重建。"""
    root = H.parse(src)
    sec = find_section(root, src, 'faq')
    if sec is None:
        return src
    repl = []
    for d in [n for n in H.walk(sec) if n.tag == 'details']:
        summ = next((k for k in d.kids if k.tag == 'summary'), None)
        if summ is None:
            continue
        q = inner_text(src, summ)
        if any(re.search(p, q, re.I) for p in DROP_FAQ):
            s, e = line_span(src, d)
            repl.append((s, e, ''))
            continue
        kind = 'invoice' if re.search(r'invoice', q, re.I) else ('pay' if re.search(r'payment methods', q, re.I) else None)
        if not kind:
            continue
        ans = next((n for n in H.walk(d) if n.tag == 'p'), None)
        qn = next((n for n in H.walk(summ) if n.tag == 'h3'), summ)
        if ans is None:
            continue
        if kind == 'invoice':
            repl.append((qn.so, qn.ec, INVOICE_Q))
            repl.append((ans.so, ans.ec, INVOICE_A))
        else:
            repl.append((ans.so, ans.ec, PAY_A))
    return sync_faq(H.apply_spans(src, repl))


def faq_pairs(src):
    root = H.parse(src)
    sec = find_section(root, src, 'faq')
    out = []
    if sec is None:
        return out
    for d in [n for n in H.walk(sec) if n.tag == 'details']:
        summ = next((k for k in d.kids if k.tag == 'summary'), None)
        ans = [n for n in H.walk(d) if n.tag in ('p', 'div') and n is not d and n.parent is not summ
               and n.tag == 'p']
        if summ is None or not ans:
            continue
        out.append((inner_text(src, summ), strip_tags(src[d.so:d.ec].split('</summary>', 1)[1])))
    return out


def sync_faq(src):
    """JSON-LD 的 FAQPage 按可见 FAQ 重建，问题与回答逐条一致。"""
    pairs = faq_pairs(src)
    root = H.parse(src)
    for n in H.walk(root):
        if n.tag == 'script' and 'ld+json' in n.attrs:
            raw = src[n.so:n.ec]
            data = json.loads(raw)
            changed = False
            for node in data.get('@graph', [data]):
                if node.get('@type') == 'FAQPage':
                    node['mainEntity'] = [{'@type': 'Question', 'name': q,
                                           'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]
                    changed = True
            if changed:
                multi = NL in raw.strip()
                text = json.dumps(data, ensure_ascii=False, indent=2 if multi else None,
                                  separators=None if multi else (', ', ': '))
                return src[:n.so] + (NL + text + NL if multi else text) + src[n.ec:]
    return src


def rewrite_text(src):
    """整句替换 + 短语规则，作用于所有翻译单元和 JSON-LD 字符串。"""
    repl = []
    for s in H.collect(src):
        if s.kind == 'ldjson':
            continue
        t = s.text
        new = EXACT.get(t, t)
        for pat, rep in RULES:
            new = re.sub(pat, rep, new)
        if new != t:
            repl.append((s.s, s.e, new))
    src = H.apply_spans(src, repl)
    # JSON-LD（非 FAQ 部分）
    root = H.parse(src)
    out = []
    for n in H.walk(root):
        if n.tag == 'script' and 'ld+json' in n.attrs:
            raw = src[n.so:n.ec]
            data, paths = H.ld_strings(raw)
            ch = False
            for p, v in paths:
                new = v
                for pat, rep in RULES:
                    new = re.sub(pat, rep, new)
                if new != v:
                    H.set_path(data, p, new)
                    ch = True
            if ch:
                multi = NL in raw.strip()
                text = json.dumps(data, ensure_ascii=False, indent=2 if multi else None,
                                  separators=None if multi else (', ', ': '))
                out.append((n.so, n.ec, NL + text + NL if multi else text))
    return H.apply_spans(src, out)


def drop_pay_row_item(src):
    root = H.parse(src)
    repl = []
    for n in H.walk(root):
        if n.tag == 'li' and n.ec is not None and inner_text(src, n) == 'Bank transfer':
            anc = n.parent
            while anc is not None and 'pay-list' not in anc.attrs and 'pay-row' not in anc.attrs:
                anc = anc.parent
            if anc is not None:
                s, e = line_span(src, n)
                repl.append((s, e, ''))
    return H.apply_spans(src, repl)


def lint(src, tag=''):
    """返回处理后页面里仍然带有中国发票/对公转账说法的片段（只看可见文字和 JSON-LD，忽略标签与样式）。"""
    body = re.sub(r'<style\b.*?</style>', ' ', src, flags=re.S)
    body = re.sub(r'<(?!script)[^>]+>', ' ', body)
    hits = []
    for m in LEFTOVER.finditer(body):
        a = max(0, m.start() - 50)
        hits.append(re.sub(r'\s+', ' ', body[a:m.end() + 50]))
    return hits


def apply(src):
    s = drop_cards(src)
    s = drop_pay_row_item(s)
    s = rewrite_faq(s)
    s = rewrite_text(s)
    return sync_faq(s)


def main():
    """用法：python scripts/i18n/overseas.py [--dry-run] <slug 前缀>...   例：deepseek
    把 /en/models/ 下匹配前缀的页面改成海外口径，原地写回；重复运行结果不变。"""
    import os
    import sys
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    d = os.path.join(root, 'en', 'models')
    changed, left = [], []
    for f in sorted(os.listdir(d)):
        if not f.endswith('.html') or f == 'index.html' or not any(f.startswith(a) for a in args):
            continue
        p = os.path.join(d, f)
        src = io_read(p)
        out = apply(src)
        if out != src:
            changed.append(f)
            if not dry:
                io_write(p, out)
        for h in lint(out):
            left.append(f'{f}: {h[:120]}')
    print(('将修改' if dry else '已修改'), len(changed), '页:', ', '.join(changed) or '无')
    print('仍有中国发票/对公转账说法:', len(left))
    for x in left[:20]:
        print('  ', x)


def io_read(p):
    import io
    return io.open(p, encoding='utf-8').read()


def io_write(p, s):
    import io
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)


if __name__ == '__main__':
    main()
