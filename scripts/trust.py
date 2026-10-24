# 给所有模型专题页加「信任与保障」：一个 6 项的信任清单版块 + 3 条 FAQ（可见内容与 JSON-LD 同步）。
# 文案只写用户确认属实的信息（2026-10-24 确认）：
#   新用户送 200 万 tokens 试用额度、$1 起充、余额可退且无手续费、官方渠道不掺假不降智、
#   内容数据不做持久化存储用于训练（与隐私政策 1.2 一致）、控制台可查每次调用明细、可设 Key 额度、7×24 客服
# 用法：python scripts/trust.py  （重复运行结果不变；修改文案后重跑会整体替换版块）
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NL = chr(10)
SUPPORT = 'https://anyaigc.ai/customersupport'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'

ITEMS = {
    'zh': [
        ('注册送 200 万 tokens', '新用户注册即送试用额度，先测效果再充值。'),
        ('$1 起充，余额可退', '最低 1 美元起充，未使用余额可申请退款，不收手续费。'),
        ('官方渠道，不掺假不降智', '请求走官方模型渠道，不用低配或逆向模型冒充。'),
        ('内容不留存、不训练', f'除法律法规要求外，不对你的输入输出做持久化存储，也不用于训练。详见<a href="/privacy">隐私政策</a>。'),
        ('账单透明，可设额度', '控制台可查每次调用的 tokens 与扣费明细，可给每个 API Key 设置额度上限。'),
        ('7×24 客服', f'随时<a href="{SUPPORT}">联系客服</a>，接入、计费和故障问题都有人响应。'),
    ],
    'en': [
        ('2M free tokens to start', 'New accounts get trial credit, so you can test before you top up.'),
        ('Top up from $1, refundable', 'Top up from $1. Unused balance can be refunded with no fee.'),
        ('Official channels, real models', 'Requests go to official model channels, never cheaper or reverse-engineered substitutes.'),
        ('No retention, no training', 'Unless the law requires it, your prompts and outputs are not persistently stored or used for training. See the <a href="/privacy">privacy policy</a>.'),
        ('Transparent billing, spend caps', 'See tokens and cost for every request in the console, and set a quota on each API key.'),
        ('24/7 support', f'<a href="{SUPPORT}">Contact support</a> any time about integration, billing or incidents.'),
    ],
}
HEAD = {'zh': ('为什么可以放心用 AnyAIGC', '试用、充值、退款、数据和账单，这些开发者最关心的问题，我们都写清楚了。'),
        'en': ('Why teams trust AnyAIGC', 'Trial credit, top-ups, refunds, data handling and billing, spelled out up front.')}
FAQ = {
    'zh': [
        ('新用户有免费试用额度吗？', '有。新用户注册后赠送 200 万 tokens 的试用额度，可以先测试效果再决定是否充值。最低 1 美元起充。'),
        ('余额可以退款吗？', '可以。未使用的余额可以申请退款，不收取手续费。具体流程请联系客服。'),
        ('会不会用低配模型冒充？我的数据安全吗？', '请求走官方模型渠道，不用低配或逆向模型冒充。除法律法规要求外，我们不会对你的输入输出内容做持久化存储，也不会用于训练模型；控制台可以查看每次调用的 tokens 与扣费明细。'),
    ],
    'en': [
        ('Is there free trial credit for new users?', 'Yes. New accounts get 2 million tokens of trial credit, so you can test before deciding to top up. Top-ups start at $1.'),
        ('Can I get a refund on my balance?', 'Yes. Unused balance can be refunded with no fee. Contact support to start a refund.'),
        ('Are these the real models? Is my data safe?', 'Requests go to official model channels, never cheaper or reverse-engineered substitutes. Unless the law requires it, we do not persistently store your prompts or outputs or use them for training, and the console shows tokens and cost for every request.'),
    ],
}

# 每种页面风格的版块模板：(版块 class, 内层 wrap, 标题 html, 列表 class, 项 html)
STYLES = {
    'o': dict(sec='o-section', wrap='o-wrap o-col', h=lambda h, l: f'      <h2 class="o-h2 o-reveal" id="trust-title">{h}</h2>{NL}      <p class="o-lead o-reveal">{l}</p>{NL}',
              ans='o-ans'),
    'p': dict(sec='p-band p-band-white', wrap='o-wrap', h=lambda h, l: f'      <div class="p-head o-reveal">{NL}        <h2 class="p-h2" id="trust-title">{h}</h2>{NL}        <p>{l}</p>{NL}      </div>{NL}',
              ans='o-ans'),
    's': dict(sec='s-section', wrap='s-wrap', h=lambda h, l: f'      <div class="s-head s-center s-reveal">{NL}        <h2 class="s-h2" id="trust-title">{h}</h2>{NL}        <p class="s-lead">{l}</p>{NL}      </div>{NL}',
              ans='s-ans'),
}


def section(lang, style):
    st = STYLES[style]
    h, lead = HEAD[lang]
    rev = 's-reveal' if style == 's' else 'o-reveal'
    lis = ''.join(f'        <li class="{rev}"><h3>{t}</h3><p>{d}</p></li>{NL}' for t, d in ITEMS[lang])
    cta = ('先注册领取 200 万 tokens' if lang == 'zh' else 'Sign up for 2M free tokens')
    btn = ('s-pill s-pill-aura s-pill-lg' if style == 's' else 'o-btn o-btn-dark')
    cta_cls = 's-price-cta' if style == 's' else ('o-cta' if style == 'p' else 'o-price-cta')
    return (f'  <!-- TRUST -->{NL}'
            f'  <section class="{st["sec"]}" id="trust" aria-labelledby="trust-title">{NL}'
            f'    <div class="{st["wrap"]}">{NL}'
            + st['h'](h, lead) +
            f'      <ul class="trust-list">{NL}{lis}      </ul>{NL}'
            f'      <div class="{cta_cls} {rev}"><a class="{btn}" href="{REG}">{cta}</a></div>{NL}'
            f'    </div>{NL}  </section>{NL}  <!-- /TRUST -->{NL}{NL}')


def add_faq(s, lang, ans_cls):
    for q, a in FAQ[lang]:
        if f'<h3>{q}</h3>' in s:
            continue
        # 每次重新定位：上一轮重写 JSON-LD 后偏移会变
        faq_start = s.index('id="faq"')
        end = s.index('</section>', faq_start)
        last = s.rfind('<details', faq_start, end)
        line_start = s.rfind(NL, 0, last) + 1
        indent = s[line_start:last]
        item = f'{indent}<details><summary><h3>{q}</h3></summary><div class="{ans_cls}"><p>{a}</p></div></details>{NL}'
        s = s[:line_start] + item + s[line_start:]
        m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
        g = json.loads(m.group(1))
        for node in g['@graph']:
            if node.get('@type') == 'FAQPage':
                node['mainEntity'].insert(len(node['mainEntity']) - 1, {
                    '@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
        s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False, indent=2) + s[m.end(1):]
    return s


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
            style = 's' if 'class="s-section" id="enterprise"' in s else ('p' if 'class="p-band' in s else 'o')
            s = re.sub(r'  <!-- TRUST -->.*?<!-- /TRUST -->\n\n', '', s, flags=re.S)
            # 放在企业接入版块之后
            sec = s.index('id="enterprise"')
            end = s.index('</section>', sec) + len('</section>') + 1
            while s[end:end + 1] == NL:
                end += 1
            s = s[:end] + section(lang, style) + s[end:]
            s = add_faq(s, lang, STYLES[style]['ans'])
            if s != o:
                io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
                done.append(f'{lang}/{f}')
    print('updated:', ', '.join(done) or 'none')


if __name__ == '__main__':
    main()
