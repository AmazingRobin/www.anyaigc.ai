# DeepSeek 系列专题页的 HTML 版块拼装（与语言无关，文案由 deepseek_copy_zh.py / deepseek_copy_en.py 提供），结构沿用 glm_layout.py。
# 视觉参考 deepseek.com：暖白底 #F9F8F8、首屏 #9CC1E7 冷蓝雾面渐变 + 淡网格、半透明白色玻璃卡片、全胶囊按钮、
# 暖黑主按钮 #1A1615、交互蓝 #4176E6 / 品牌蓝 #4D6BFE、偏蓝标题色 #152443、浅色代码块与浅色页脚。
import html
import io
import json
import os
import re

from deepseek_data import DATE, VER, SITE, REG, PRICING, SUPPORT, DOCS, PRICE, OFFICIAL, MODELS, MODEL_SLUGS

NL = '\n'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = 'deepseek'

L = {
    'zh': dict(lang='zh-CN', og='zh_CN', og_alt='en_US', other='en', other_name='English', other_short='EN', me_short='中文',
               home='首页', hub='模型专题', market='模型广场', price='价格', ent='企业接入', docs='API 文档', login='登录', series='DeepSeek',
               signup='免费注册', get_key='获取 API Key', see_price='查看价格', view_market='在模型广场查看',
               skip='跳到主要内容', nav='主导航', crumbs='面包屑', facts='核心信息', copy='复制', copied='已复制',
               code='代码示例', sales='联系企业客服', trial='先注册试用', signup_any='免费注册 AnyAIGC', read_docs='阅读 API 文档',
               all_hub='全部模型专题', more='更多', series_all='DeepSeek 全系总览', home_label='AnyAIGC 首页',
               cc_nav='Claude Code', category='大语言模型 API', lang_label='语言', deal='官方高峰价', deal_line='约为 DeepSeek 官方高峰价 · 输入 ${p} / 1M，全天同价',
               demo_send='发送示例问题', demo_wait='思考中…', demo_note='演示效果，以上为示例回答，并非实时生成。', demo_cta='注册后用你的 API Key 实际调用 →',
               foot_desc='国内外大模型 API 中转平台。一个 Base URL、一个 API Key，统一调用 300+ 模型。',
               foot=('产品', '资源', '条款'), foot_links=('模型专题', '模型广场', '控制台', 'API 文档 ↗', '联系我们', '隐私政策', '服务条款'),
               legal='&copy; 2026 AnyAIGC。DeepSeek 是杭州深度求索人工智能基础技术研究有限公司的商标。AnyAIGC 是独立的 API 服务商，与深度求索无隶属或合作关系。基准成绩与官方价格引自 DeepSeek 公开资料，模型许可与商用条款以 DeepSeek 官方为准。',
               ent_cards=[('增值税发票', '普票、专票都能开', '按实际充值金额开具增值税普通发票或增值税专用发票，方便企业报销和抵扣。'),
                          ('对公转账', '公司账户直接付款', '支持企业对公转账充值，无需个人垫付，账目清晰。'),
                          ('签订合同', '满足采购与法务流程', '可与 AnyAIGC 签订服务合同，适配企业内部的采购审批要求。'),
                          ('专属对接', '客服与技术支持', '提供专属客服和技术对接，协助完成接入、迁移和日常问题排查。')],
               ent_lead='研发团队和公司可以直接走企业流程采购，财务、法务和技术对接都有对应支持。',
               ent_h2='企业接入 {name} API', ent_kicker='企业'),
    'en': dict(lang='en', og='en_US', og_alt='zh_CN', other='zh', other_name='中文', other_short='中文', me_short='EN',
               home='Home', hub='Model guides', market='Model catalog', price='Pricing', ent='Enterprise', docs='API docs', login='Log in', series='DeepSeek',
               signup='Sign up free', get_key='Get an API key', see_price='See pricing', view_market='View in the model catalog',
               skip='Skip to main content', nav='Main', crumbs='Breadcrumb', facts='Key facts', copy='Copy', copied='Copied',
               code='Code examples', sales='Talk to sales', trial='Start with a free account', signup_any='Sign up for AnyAIGC',
               read_docs='Read the API docs', all_hub='All model guides', more='More', series_all='DeepSeek overview',
               home_label='AnyAIGC home', cc_nav='Claude Code', category='Large language model API', lang_label='Language', deal='Price', deal_line='vs. DeepSeek official peak price · input ${p} / 1M, one rate all day',
               demo_send='Send sample prompt', demo_wait='Thinking…', demo_note='Demo only. This is a sample answer, not generated live.', demo_cta='Sign up and try it with your own API key →',
               foot_desc='An API gateway for global AI models. One base URL and one API key for 300+ models.',
               foot=('Product', 'Resources', 'Legal'), foot_links=('Model guides', 'Model catalog', 'Console', 'API docs ↗', 'Contact us', 'Privacy Policy', 'Terms of Service'),
               legal='&copy; 2026 AnyAIGC. DeepSeek is a trademark of Hangzhou DeepSeek Artificial Intelligence Basic Technology Research Co., Ltd. AnyAIGC is an independent API provider and is not affiliated with DeepSeek. Benchmarks and official prices are quoted from DeepSeek\'s public materials; model licenses and commercial terms are governed by DeepSeek.',
               ent_cards=[('Invoices', 'Including China VAT invoices', 'Get invoices for every top-up, including Chinese VAT general and special invoices for companies in mainland China.'),
                          ('Bank transfer', 'Pay from a company account', 'Top up by corporate bank transfer, so nobody has to pay on a personal card and expense it.'),
                          ('Contracts', 'Fits procurement and legal review', 'Sign a service agreement with AnyAIGC to meet your internal purchasing requirements.'),
                          ('Dedicated support', 'Account and technical contacts', 'Work with a dedicated support contact and technical engineer for onboarding, migration and troubleshooting.')],
               ent_lead='Engineering teams and companies can buy through a standard business process, with support for finance, legal and engineering.',
               ent_h2='{name} API for teams and enterprises', ent_kicker='Enterprise'),
}

# ---------------- DeepSeek logo（lobe-icons deepseek-color：鲸鱼，单色 #4D6BFE，颜色写在 SVG 的 fill 上） ----------------
_raw = io.open(os.path.join(ROOT, 'assets/icons/deepseek-color.svg'), encoding='utf-8').read()
_paths = re.findall(r'<path\b[^>]*?d="([^"]+)"', _raw)


def logo(cls='d-mark', size=None, fill='#4D6BFE'):
    c = f'class="{cls}" ' if cls else ''
    s = f' width="{size}" height="{size}"' if size else ''
    return (f'<svg {c}viewBox="0 0 24 24"{s} fill="{fill}" aria-hidden="true" focusable="false">'
            + ''.join(f'<path d="{d}" fill="{fill}"></path>' for d in _paths) + '</svg>')


def url(lang, slug):
    return f'{SITE}/{lang}/models/{slug}'


def text(h):
    """HTML 转纯文本（JSON-LD 用）"""
    t = re.sub(r'<[^>]+>', '', h)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


# ---------------- 代码高亮（极简：字符串 / 注释 / 关键字） ----------------
KW = r'\b(import|from|with|as|for|in|if|not|and|or|break|True|False|None|print|def|return|getattr)\b'


def hl(code):
    out = []
    for line in code.split(NL):
        parts = re.split(r'("(?:[^"\\]|\\.)*")', line)
        buf = ''
        comment = False
        for i, p in enumerate(parts):
            if comment:
                buf += html.escape(p, quote=False)
                continue
            if i % 2 == 1:
                buf += f'<span class="s">{html.escape(p, quote=False)}</span>'
                continue
            m = re.search(r'(^|\s)#\s', p)
            if m:
                pre, post = p[:m.start() + len(m.group(1))], p[m.start() + len(m.group(1)):]
                buf += re.sub(KW, r'<span class="k">\1</span>', html.escape(pre, quote=False))
                buf += '<span class="c">' + html.escape(post, quote=False)
                comment = True
                continue
            buf += re.sub(KW, r'<span class="k">\1</span>', html.escape(p, quote=False))
        if comment:
            buf += '</span>'
        out.append(buf)
    return NL.join(out)


def money(v):
    """成本示例金额：≥ 1 保留 2 位，≥ 0.01 保留 3 位，否则 4 位"""
    if v >= 1:
        return f'${v:,.2f}'
    if v >= 0.01:
        return f'${v:.3f}'
    return f'${v:.4f}'


def cost(slug, inp=0, out=0, cache=0, n=1, official=None):
    """official=None 用 AnyAIGC 价；'off' / 'peak' 用 DeepSeek 官方闲时 / 高峰价"""
    p = OFFICIAL[slug][official] if official else PRICE[slug]
    return n * (inp * float(p[0]) + out * float(p[1]) + cache * float(p[2])) / 1e6


def discount(lang, slug, i):
    """AnyAIGC 相对 DeepSeek 官方高峰价（标准价）的折扣：中文写「4 折」，英文写「60% off」"""
    from decimal import Decimal, ROUND_HALF_UP
    r = Decimal(PRICE[slug][i]) / Decimal(OFFICIAL[slug]['peak'][i])
    if lang == 'zh':
        return f"{int((r * 10).quantize(Decimal('1'), rounding=ROUND_HALF_UP))} 折"
    return f"{int(((1 - r) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))}% off"


# ---------------- head ----------------
def head(lang, slug, c):
    me, zh, en = url(lang, slug), url('zh', slug), url('en', slug)
    og_img = f'{SITE}/assets/og/{slug}-{lang}.png'
    t = L[lang]
    crumbs = [(t['home'], f'{SITE}/'), (t['hub'], f'{SITE}/{lang}/models/')]
    if slug != HUB:
        crumbs.append(('DeepSeek', url(lang, HUB)))
    crumbs.append((c['crumb'], me))
    offers = c['offers']
    graph = [
        {'@type': 'Organization', '@id': f'{SITE}/#org', 'name': 'AnyAIGC', 'url': 'https://anyaigc.ai', 'logo': f'{SITE}/logo.webp'},
        {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'AnyAIGC', 'publisher': {'@id': f'{SITE}/#org'}},
        {'@type': 'WebPage', '@id': f'{me}#webpage', 'url': me, 'name': c['title'], 'description': c['desc'], 'inLanguage': t['lang'],
         'isPartOf': {'@id': f'{SITE}/#website'}, 'breadcrumb': {'@id': f'{me}#breadcrumb'}, 'mainEntity': {'@id': f'{me}#product'},
         'dateModified': DATE},
        {'@type': 'BreadcrumbList', '@id': f'{me}#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]},
        {'@type': 'Product', '@id': f'{me}#product', 'name': c['product'], 'description': c['product_desc'],
         'category': t['category'], 'sku': c['sku'], 'image': og_img,
         'brand': {'@type': 'Brand', 'name': 'AnyAIGC'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'USD', 'lowPrice': min(offers, key=lambda o: float(o[1]))[1],
                    'highPrice': max(offers, key=lambda o: float(o[1]))[1], 'offerCount': len(offers),
                    'availability': 'https://schema.org/InStock', 'url': f'{me}#pricing',
                    'offers': [{'@type': 'Offer', 'name': n, 'price': p, 'priceCurrency': 'USD'} for n, p in offers]}},
        {'@type': 'FAQPage', '@id': f'{me}#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': text(a)}} for q, a in c['faqs']]},
    ]
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    e = lambda s: html.escape(s, quote=True)
    return f'''<!DOCTYPE html>
<html lang="{t['lang']}" class="no-js">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(c['title'])}</title>
<meta name="description" content="{e(c['desc'])}">
<meta name="keywords" content="{e(c['keywords'])}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#f9f8f8">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{zh}">
<link rel="alternate" hreflang="en" href="{en}">
<link rel="alternate" hreflang="x-default" href="{en}">
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{t['og']}">
<meta property="og:locale:alternate" content="{t['og_alt']}">
<meta property="og:url" content="{me}">
<meta property="og:title" content="{e(c['title'])}">
<meta property="og:description" content="{e(c['og_desc'])}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(c['og_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(c['title'])}">
<meta name="twitter:description" content="{e(c['og_desc'])}">
<meta name="twitter:image" content="{og_img}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261024b">
<link rel="stylesheet" href="/assets/models/deepseek.css?v={VER}">
<script type="application/ld+json">
{ld}
</script>
</head>
'''


def nav(lang, slug):
    t = L[lang]
    o = t['other']
    return f'''<body>
<a class="o-skip" href="#main">{t['skip']}</a>

<header class="o-nav">
  <div class="o-wrap o-nav-inner">
    <a class="o-brand" href="/" aria-label="{t['home_label']}">AnyAIGC</a>
    <nav aria-label="{t['nav']}">
      <ul class="o-nav-left">
        <li><a class="o-pill" href="/{lang}/models/">{t['hub']}</a></li>
        <li class="d-hide-md"><a class="o-pill" href="/{lang}/models/{HUB}">DeepSeek</a></li>
        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="#pricing">{t['price']}</a></li>
        <li class="d-hide-md"><a class="o-pill" href="#claude-code">{t['cc_nav']}</a></li>
        <li><a class="o-pill" href="#enterprise">{t['ent']}</a></li>
        <li class="d-hide-md"><a class="o-pill" href="{DOCS}" target="_blank" rel="noopener">{t['docs']}</a></li>
      </ul>
    </nav>
    <ul class="o-nav-right">
      <li class="d-lang" aria-label="{t['lang_label']}"><span class="d-lang-on" aria-current="true">{t['me_short']}</span><a href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_short']}</a></li>
      <li><a class="o-pill d-nav-login" href="https://anyaigc.ai/console">{t['login']}</a></li>
      <li><a class="o-pill d-nav-cta" href="{REG}">{t['signup']}</a></li>
    </ul>
  </div>
</header>

<main id="main">
'''


ARROW = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'


def hero(lang, slug, c):
    t = L[lang]
    h = c['hero']
    crumb = f'            <li><a href="/{lang}/models/{HUB}">DeepSeek</a></li>{NL}' if slug != HUB else ''
    # 首屏第一个要点：相对 DeepSeek 官方高峰价的折扣（按输入价计算，总览页用 V4.1 Flash）
    deal_slug = slug if slug in PRICE else MODEL_SLUGS[0]
    deal = f'          <li class="is-deal">{t["deal"]} <strong>{discount(lang, deal_slug, 0)}{"" if lang == "zh" else " official peak"}</strong></li>{NL}'
    facts = deal + ''.join(f'          <li>{k} <strong>{v}</strong></li>{NL}' for k, v in h['facts'])
    chips = ''.join(f'<button type="button" class="d-chip{" is-on" if i == 0 else ""}" aria-pressed="{"true" if i == 0 else "false"}">{x}</button>'
                    for i, x in enumerate(h['chips']))
    notice = f'      <p class="o-notice" role="note">{h["notice"]}</p>{NL}' if h.get('notice') else ''
    # 首屏输入卡是演示：点发送后逐字显示写在 HTML 里的示例回答（deepseek.js），不发起真实请求
    lines = ''.join(f'          <p{" class=\"d-json\"" if x.startswith("{") else ""}>{x}</p>{NL}' for x in h['out'])
    return f'''  <!-- 首屏 -->
  <section class="d-hero" aria-labelledby="hero-title">
    <div class="d-hero-grid" aria-hidden="true"></div>
    <div class="o-wrap d-hero-inner">
      <nav aria-label="{t['crumbs']}">
        <ol class="o-crumbs">
          <li><a href="/">{t['home']}</a></li>
          <li><a href="/{lang}/models/">{t['hub']}</a></li>
{crumb}          <li aria-current="page">{c['crumb']}</li>
        </ol>
      </nav>
      <p class="d-announce"><span class="d-spark" aria-hidden="true">✦</span><span>{h['announce']}</span></p>
      <p class="d-eyebrow">{logo()}<span>{h['eyebrow']}</span></p>
      <h1 class="d-h1 d-rise" id="hero-title">{h['h1']}</h1>
      <p class="d-lead d-rise">{h['lead']}</p>
      <p class="d-deal d-rise"><strong>{discount(lang, deal_slug, 0)}</strong><span>{t['deal_line'].format(p=PRICE[deal_slug][0])}</span></p>
{notice}      <div class="d-ask d-rise" data-demo>
        <p class="d-ask-q">{h['ask']}<span class="d-caret" aria-hidden="true"></span></p>
        <div class="d-ask-bar">{chips}<button type="button" class="d-send" aria-label="{t['demo_send']}">{ARROW}</button></div>
        <div class="d-ask-out" hidden aria-live="polite">
          <p class="d-think" data-wait="{t['demo_wait']}">{h['think']}</p>
{lines}          <p class="d-ask-note">{t['demo_note']} <a href="{REG}">{t['demo_cta']}</a></p>
        </div>
      </div>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{t['get_key']}</a>
        <a class="o-btn o-btn-light" href="#pricing">{t['see_price']}</a>
        <a class="o-btn o-btn-light" href="#quickstart">{h['qs_btn']}</a>
      </div>
      <p class="d-lead-sub">{h['sub']}</p>
      <ul class="o-facts" aria-label="{t['facts']}">
{facts}      </ul>
    </div>
  </section>

'''


def head2(kicker, h2, sid, lead=None):
    out = f'      <span class="d-kicker o-reveal">{kicker}</span>{NL}      <h2 class="o-h2 o-reveal" id="{sid}">{h2}</h2>{NL}'
    if lead:
        out += f'      <p class="o-lead o-reveal">{lead}</p>{NL}'
    return out


def about(c):
    a = c['about']
    paras = ''.join(f'        <p class="o-reveal">{p}</p>{NL}' for p in a['paras'])
    spec = ''.join(f'        <div><dt>{dt}</dt><dd>{dd}' + (f'<small>{sm}</small>' if sm else '') + f'</dd></div>{NL}' for dt, dd, sm in a['spec'])
    return f'''  <!-- 模型介绍 -->
  <section class="o-section" id="about" aria-labelledby="about-title">
    <div class="o-wrap d-wide">
{head2(a['kicker'], a['h2'], 'about-title')}      <div class="d-prose">
{paras}      </div>
      <dl class="d-spec o-reveal">
{spec}      </dl>
    </div>
  </section>

'''


def features(c):
    f = c['features']
    items = ''.join(f'        <li class="o-reveal"><span class="d-num">{i + 1:02d}</span><h3>{h}</h3><p>{p}</p></li>{NL}' for i, (h, p) in enumerate(f['items']))
    return f'''  <!-- 能力 -->
  <section class="o-section" id="features" aria-labelledby="features-title">
    <div class="o-wrap d-wide">
{head2(f['kicker'], f['h2'], 'features-title', f.get('lead'))}      <ul class="d-caps">
{items}      </ul>
    </div>
  </section>

'''


def models(lang, c):
    """总览页：型号卡片"""
    m = c['models']
    cards = ''
    for slug, tag, desc, bullets in m['items']:
        p = PRICE[slug]
        bl = ''.join(f'<li>{b}</li>' for b in bullets)
        tg = f'<span class="d-tag{" d-tag-muted" if tag == m.get("legacy_tag") else ""}">{tag}</span>' if tag else ''
        cards += (f'        <li class="d-model o-reveal"><a href="/{lang}/models/{slug}">{tg}'
                  f'<span class="d-model-id">{slug}</span><h3>{MODELS[slug]["name"]}</h3><p>{desc}</p><ul>{bl}</ul>'
                  f'<span class="d-model-price"><b>${p[0]}</b> / {m["unit_in"]} · <b>${p[1]}</b> / {m["unit_out"]}</span>'
                  f'<span class="d-model-go">{m["go"]} <span aria-hidden="true">→</span></span></a></li>{NL}')
    return f'''  <!-- 型号 -->
  <section class="o-section" id="models" aria-labelledby="models-title">
    <div class="o-wrap d-wide">
{head2(m['kicker'], m['h2'], 'models-title', m['lead'])}      <ul class="d-models">
{cards}      </ul>
    </div>
  </section>

'''


def price_rows(lang, slug, labels, with_model=True):
    rows = ''
    for i, (lab, small) in enumerate(labels):
        mid = f'<td><code>{slug}</code></td>' if with_model else ''
        rows += (f'            <tr><th scope="row">{lab}<small>{small}</small></th>{mid}'
                 f'<td class="o-num o-hl">${PRICE[slug][i]}</td><td class="o-num o-strike">${OFFICIAL[slug]["off"][i]}</td>'
                 f'<td class="o-num o-strike">${OFFICIAL[slug]["peak"][i]}</td>'
                 f'<td class="o-num o-save">{discount(lang, slug, i)}</td></tr>{NL}')
    return rows


def pricing(lang, slug, c):
    t = L[lang]
    p = c['pricing']
    billing = ''.join(f'        <li><strong>{s}</strong>{x}</li>{NL}' for s, x in p['billing'])
    th = ''.join(f'<th scope="col"{" class=" + chr(34) + cls + chr(34) if cls else ""}>{h}</th>' for h, cls in p['head'])
    if slug == HUB:
        body = ''
        for s in MODEL_SLUGS:
            body += (f'          <tbody>{NL}            <tr class="d-group"><th scope="rowgroup" colspan="5"><code>{s}</code> · {MODELS[s]["name"]}</th></tr>{NL}'
                     + price_rows(lang, s, p['labels'], with_model=False) + f'          </tbody>{NL}')
    else:
        body = f'          <tbody>{NL}' + price_rows(lang, slug, p['labels']) + f'          </tbody>{NL}'
    costs = ''.join(f'''        <li class="o-cost o-reveal">
          <h4>{h}</h4>
          <p class="o-cost-calc">{calc}</p>
          <p class="o-cost-total">{tot}</p>
          <p class="o-cost-off">{off}</p>
        </li>{NL}''' for h, calc, tot, off in p['costs'])
    q = '?keyword=deepseek' if slug == HUB else f'?keyword={slug}'
    return f'''  <!-- 价格 -->
  <section class="o-section d-band" id="pricing" aria-labelledby="pricing-title">
    <div class="o-wrap d-wide">
{head2(p['kicker'], p['h2'], 'pricing-title', p['lead'])}      <ul class="o-billing o-reveal" aria-label="{p['billing_label']}">
{billing}      </ul>

      <div class="o-table-wrap o-reveal">
        <table class="o-table">
          <caption class="o-sr">{p['caption']}</caption>
          <thead>
            <tr>{th}</tr>
          </thead>
{body}        </table>
      </div>
      <p class="o-note">{p['note']}</p>

      <h3 class="d-h3 o-reveal">{p['costs_h3']}</h3>
      <p class="d-sub o-reveal">{p['costs_lead']}</p>
      <ul class="o-costs">
{costs}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-dark" href="{REG}">{t['get_key']}</a>
        <a class="o-btn o-btn-light" href="{PRICING}{q}">{t['view_market']}</a>
      </div>
    </div>
  </section>

'''


def table(head_cells, rows, caption):
    th = ''.join(f'<th scope="col"{" class=" + chr(34) + cls + chr(34) if cls else ""}>{h}</th>' for h, cls in head_cells)
    body = ''
    for r in rows:
        lab, small, vals = r[0], r[1], r[2:]
        cells = ''.join(f'<td class="o-num{" o-hl" if j == 0 else ""}">{v}</td>' for j, v in enumerate(vals))
        sm = f'<small>{small}</small>' if small else ''
        body += f'            <tr><th scope="row">{lab}{sm}</th>{cells}</tr>{NL}'
    return f'''      <div class="o-table-wrap o-reveal">
        <table class="o-table">
          <caption class="o-sr">{caption}</caption>
          <thead>
            <tr>{th}</tr>
          </thead>
          <tbody>
{body}          </tbody>
        </table>
      </div>
'''


def bench(c):
    b = c.get('bench')
    if not b:
        return ''
    chart = ''
    if b.get('chart'):
        title, bars = b['chart']
        lis = ''.join(f'          <li class="d-bar{" is-me" if me else ""}"><span class="d-bar-label">{lab}</span>'
                      f'<span class="d-bar-track" aria-hidden="true"><span class="d-bar-fill" style="--v:{v}"></span></span>'
                      f'<span class="d-bar-val">{v}</span></li>{NL}' for lab, v, me in bars)
        chart = f'''      <div class="d-chart o-reveal" role="group" aria-labelledby="chart-title">
        <p class="d-chart-title" id="chart-title">{title}</p>
        <ul class="d-bars">
{lis}        </ul>
      </div>
'''
    return f'''  <!-- 基准 -->
  <section class="o-section" id="benchmarks" aria-labelledby="bench-title">
    <div class="o-wrap d-wide">
{head2(b['kicker'], b['h2'], 'bench-title', b['lead'])}{chart}{table(b['head'], b['rows'], b['caption'])}      <p class="o-note">{b['note']}</p>
    </div>
  </section>

'''


def compare(c):
    b = c['compare']
    return f'''  <!-- 选型 -->
  <section class="o-section d-band" id="compare" aria-labelledby="compare-title">
    <div class="o-wrap d-wide">
{head2(b['kicker'], b['h2'], 'compare-title', b['lead'])}{table(b['head'], b['rows'], b['caption'])}      <p class="o-note">{b['note']}</p>
    </div>
  </section>

'''


def uses(c):
    u = c['uses']
    items = ''.join(f'        <li class="o-reveal"><span class="d-k">{k}</span><h3>{h}</h3><p>{p}</p></li>{NL}' for k, h, p in u['items'])
    return f'''  <!-- 使用场景 -->
  <section class="o-section" id="use-cases" aria-labelledby="uses-title">
    <div class="o-wrap d-wide">
{head2(u['kicker'], u['h2'], 'uses-title')}      <ul class="d-uses">
{items}      </ul>
    </div>
  </section>

'''


def quickstart(lang, c):
    t = L[lang]
    q = c['qs']
    steps = ''.join(f'        <li>{s}</li>{NL}' for s in q['steps'])
    tabs, panels = '', ''
    for i, (tid, label, cap, code) in enumerate(q['tabs']):
        sel = 'true' if i == 0 else 'false'
        tabs += f'        <li role="presentation"><button type="button" role="tab" id="tab-{tid}" aria-controls="panel-{tid}" aria-selected="{sel}">{label}</button></li>{NL}'
        panels += f'''      <figure class="o-code" id="panel-{tid}" role="tabpanel" aria-labelledby="tab-{tid}">
        <figcaption><b>{cap}</b><button class="o-copy" type="button" aria-controls="code-{tid}" data-done="{t['copied']}">{t['copy']}</button></figcaption>
<pre id="code-{tid}"><code>{hl(code)}</code></pre>
      </figure>

'''
    return f'''  <!-- 快速开始 -->
  <section class="o-section" id="quickstart" aria-labelledby="qs-title">
    <div class="o-wrap o-col">
{head2(q['kicker'], q['h2'], 'qs-title')}      <ol class="o-steps o-reveal">
{steps}      </ol>

      <ul class="o-tabs" role="tablist" aria-label="{t['code']}">
{tabs}      </ul>

{panels}      <p class="d-callout o-reveal">{q['callout']}</p>
      <p class="o-note">{q['note']}</p>
    </div>
  </section>

'''


def claude_code(lang, c):
    t = L[lang]
    cc = c['cc']
    steps = ''.join(f'        <li>{s}</li>{NL}' for s in cc['steps'])
    return f'''  <!-- Claude Code -->
  <section class="o-section d-band" id="claude-code" aria-labelledby="cc-title">
    <div class="o-wrap o-col">
{head2(cc['kicker'], cc['h2'], 'cc-title', cc['lead'])}      <ol class="o-steps o-reveal">
{steps}      </ol>
      <figure class="o-code o-reveal">
        <figcaption><b>~/.claude/settings.json</b><button class="o-copy" type="button" aria-controls="code-cc" data-done="{t['copied']}">{t['copy']}</button></figcaption>
<pre id="code-cc"><code>{hl(cc['code'])}</code></pre>
      </figure>
      <p class="d-callout o-reveal">{cc['callout']}</p>
      <p class="o-note">{cc['note']}</p>
    </div>
  </section>

'''


def enterprise(lang, name):
    t = L[lang]
    cards = ''.join(f'        <li class="o-card o-reveal"><strong>{a}</strong><h3>{b}</h3><p>{d}</p></li>{NL}' for a, b, d in t['ent_cards'])
    return f'''  <!-- 企业接入 -->
  <section class="o-section" id="enterprise" aria-labelledby="ent-title">
    <div class="o-wrap o-col">
      <span class="d-kicker o-reveal">{t['ent_kicker']}</span>
      <h2 class="o-h2 o-reveal" id="ent-title">{t['ent_h2'].format(name=name)}</h2>
      <p class="o-lead o-reveal">{t['ent_lead']}</p>
      <ul class="o-cards">
{cards}      </ul>
      <div class="o-price-cta o-reveal">
        <a class="o-btn o-btn-dark d-btn-blue" href="{SUPPORT}">{t['sales']}</a>
        <a class="o-btn o-btn-light" href="{REG}">{t['trial']}</a>
      </div>
    </div>
  </section>

'''


def family(lang, slug, items, h2, lead, kicker):
    lis = ''
    for s, tag, desc in items:
        cur = ' aria-current="page"' if s == slug else ''
        tg = f'<span class="o-tag">{tag}</span>' if tag else ''
        name = MODELS[s]['name'] if s in MODELS else desc[0]
        sub = desc if s in MODELS else desc[1]
        lis += f'        <li><a href="/{lang}/models/{s}"{cur}>{tg}<b>{name}</b><span>{sub}</span></a></li>{NL}'
    return f'''  <!-- FAMILY -->
  <section class="o-section" id="family" aria-labelledby="family-title">
    <div class="o-wrap o-col">
{head2(kicker, h2, 'family-title', lead)}      <ul class="o-family o-reveal">
{lis}      </ul>
    </div>
  </section>

'''


def faq(c):
    items = ''.join(f'        <details{" open" if i == 0 else ""}><summary><h3>{q}</h3></summary><div class="o-ans"><p>{a}</p></div></details>{NL}'
                    for i, (q, a) in enumerate(c['faqs']))
    return f'''  <!-- FAQ -->
  <section class="o-section" id="faq" aria-labelledby="faq-title">
    <div class="o-wrap o-col">
      <span class="d-kicker o-reveal">FAQ</span>
      <h2 class="o-h2 o-reveal" id="faq-title">{c['faq_h2']}</h2>
      <div class="o-faq">
{items}      </div>
    </div>
  </section>

'''


def final(lang, slug, c):
    t = L[lang]
    o = t['other']
    f = c['final']
    series = '' if slug == HUB else f'        <li><a class="o-pill" href="/{lang}/models/{HUB}">{t["series_all"]}</a></li>{NL}'
    return f'''  <!-- 结尾 CTA -->
  <section class="o-final" aria-labelledby="final-title">
    <div class="o-wrap">
      {logo('d-mark d-final-mark')}
      <h2 id="final-title">{f['h2']}</h2>
      <p>{f['p']}</p>
      <div class="o-cta">
        <a class="o-btn o-btn-dark" href="{REG}">{t['signup_any']}</a>
        <a class="o-btn o-btn-light" href="{DOCS}" target="_blank" rel="noopener">{t['read_docs']} <span aria-hidden="true">↗</span></a>
      </div>
      <ul class="o-related" aria-label="{t['more']}">
        <li><a class="o-pill" href="/{lang}/models/">{t['all_hub']}</a></li>
{series}        <li><a class="o-pill" href="{PRICING}">{t['market']}</a></li>
        <li><a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{f['other']}</a></li>
      </ul>
    </div>
  </section>
</main>

'''


def footer(lang, slug):
    t = L[lang]
    o = t['other']
    fl = t['foot_links']
    return f'''<footer class="o-foot">
  <div class="o-wrap">
    <div class="o-foot-top">
      <div class="o-foot-brand">
        <a class="o-brand" href="/">AnyAIGC</a>
        <p>{t['foot_desc']}</p>
      </div>
      <div class="o-foot-cols">
        <div class="o-foot-col">
          <h2>{t['foot'][0]}</h2>
          <ul>
            <li><a href="/{lang}/models/">{fl[0]}</a></li>
            <li><a href="{PRICING}">{fl[1]}</a></li>
            <li><a href="https://anyaigc.ai/console">{fl[2]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{t['foot'][1]}</h2>
          <ul>
            <li><a href="{DOCS}" target="_blank" rel="noopener">{fl[3]}</a></li>
            <li><a href="{SUPPORT}">{fl[4]}</a></li>
          </ul>
        </div>
        <div class="o-foot-col">
          <h2>{t['foot'][2]}</h2>
          <ul>
            <li><a href="/privacy">{fl[5]}</a></li>
            <li><a href="/terms">{fl[6]}</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="o-foot-bottom">
      <p>{logo('d-mark d-foot-mark')}<span>{t['legal']}</span></p>
      <a class="o-pill" href="/{o}/models/{slug}" hreflang="{L[o]['lang']}" lang="{L[o]['lang']}">{t['other_name']}</a>
    </div>
  </div>
</footer>

<script src="/assets/models/deepseek.js?v={VER}" defer></script>
</body>
</html>
'''
