# 给所有模型专题页加「支付方式」：企业接入版块内的一行徽标 + 一条 FAQ（可见内容与 JSON-LD 同步）。
# 用法：python scripts/payments.py   （重复运行结果不变）
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = chr(10)
METHODS = {'zh': ['微信支付', '支付宝', 'USDT', '信用卡', '对公转账'],
           'en': ['WeChat Pay', 'Alipay', 'USDT', 'Credit card', 'Bank transfer']}
LABEL = {'zh': '支持的支付方式', 'en': 'Payment methods'}
Q = {'zh': '支持哪些支付方式？',
     'en': 'Which payment methods are supported?'}
A = {'zh': '支持微信支付、支付宝、USDT 和信用卡充值，企业还可以对公转账，并开具增值税普通发票或专用发票。余额按美元计价，对平台所有模型通用。',
     'en': 'You can top up with WeChat Pay, Alipay, USDT or a credit card. Companies can also pay by bank transfer and get VAT general or special invoices. Your balance is in USD and works across every model on the platform.'}


def pay_row(lang, prefix):
    items = ''.join(f'<li>{m}</li>' for m in METHODS[lang])
    return (f'      <div class="pay-row {prefix}-reveal" role="group" aria-label="{LABEL[lang]}">'
            f'<span class="pay-label">{LABEL[lang]}</span><ul class="pay-list">{items}</ul></div>{NL}')


def add_faq(s, lang, ans_cls):
    if Q[lang] in s:
        return s
    # 可见 FAQ：插在最后一个 <details> 之前（保持数据/隐私类问题在最后）
    faq_start = s.index('id="faq"')
    last = s.rfind('<details', faq_start, s.index('</section>', faq_start))
    line_start = s.rfind(NL, 0, last) + 1
    indent = s[line_start:last]
    item = f'{indent}<details><summary><h3>{Q[lang]}</h3></summary><div class="{ans_cls}"><p>{A[lang]}</p></div></details>{NL}'
    s = s[:line_start] + item + s[line_start:]
    # JSON-LD：在 FAQPage 的最后一个问题之前插入，保持与可见顺序一致
    m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
    g = json.loads(m.group(1))
    for node in g['@graph']:
        if node.get('@type') == 'FAQPage':
            node['mainEntity'].insert(len(node['mainEntity']) - 1, {
                '@type': 'Question', 'name': Q[lang],
                'acceptedAnswer': {'@type': 'Answer', 'text': A[lang]}})
    return s[:m.start(1)] + json.dumps(g, ensure_ascii=False, indent=2) + s[m.end(1):]


def main():
    done = []
    for lang in ('zh', 'en'):
        d = os.path.join(ROOT, lang, 'models')
        for f in sorted(os.listdir(d)):
            if not f.endswith('.html') or f == 'index.html':
                continue
            p = os.path.join(d, f)
            s = io.open(p, encoding='utf-8').read()
            o = s
            prefix = 's' if 'class="s-section" id="enterprise"' in s else 'o'
            ans_cls = 's-ans' if prefix == 's' else 'o-ans'
            if 'class="pay-row' not in s:
                sec = s.index('id="enterprise"')
                end = s.index('</section>', sec)
                cta = s.rfind('<div class="', sec, end)  # 版块最后一个 div（按钮区）
                line_start = s.rfind(NL, 0, cta) + 1
                s = s[:line_start] + pay_row(lang, prefix) + s[line_start:]
            s = add_faq(s, lang, ans_cls)
            if s != o:
                io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
                done.append(f'{lang}/{f}')
    print('updated:', ', '.join(done) or 'none')


if __name__ == '__main__':
    main()
