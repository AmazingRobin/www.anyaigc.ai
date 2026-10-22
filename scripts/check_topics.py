# 专题页自检：python scripts/check_topics.py
# 检查每个 zh/models 与 en/models 页面的 SEO 必备项、站内链接、中英对应和注册情况（专题首页、sitemap）。
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.anyaigc.ai'
LANGS = {'zh': 'zh-CN', 'en': 'en'}
REGISTER = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
errors, warns = [], []


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()


def width(text):
    # 搜索结果按像素截断：汉字/全角约等于两个英文字符宽
    return sum(2 if ord(c) > 0x2e7f else 1 for c in text)


def local_exists(url):
    u = url.split('#')[0].split('?')[0]
    if u in ('', '/'):
        return True
    p = os.path.join(ROOT, u.lstrip('/').replace('/', os.sep))
    return os.path.isfile(p) or os.path.isfile(p + '.html') or os.path.isfile(os.path.join(p, 'index.html'))


SB_VARS = ('--sb-track', '--sb-thumb', '--sb-thumb-bg', '--sb-thumb-hover')


def check_scrollbar(tag, html):
    # 专题页必须在自己的 CSS 里把滚动条换成该模型的品牌色
    links = re.findall(r'<link rel="stylesheet" href="(/assets/models/[^"?]+\.css)(?:\?[^"]*)?"', html)
    own = [l for l in links if not l.endswith(('/scrollbar.css', '/hub.css'))]
    if not own:
        errors.append(f'{tag} 没有引入专题自己的 CSS（/assets/models/<slug>.css）')
        return
    css = ''.join(read(l.lstrip('/')) for l in own if local_exists(l))
    css += ''.join(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S))
    dark = 'data-scrollbar="dark"' in html.split('>', 2)[1] if '<html' in html else False
    sel = r':root\[data-scrollbar="dark"\]' if dark else r':root'
    blocks = ''.join(re.findall(sel + r'\s*\{([^}]*)\}', css))
    missing = [v for v in SB_VARS if re.search(re.escape(v) + r'\s*:', blocks) is None]
    if missing:
        where = ':root[data-scrollbar="dark"]' if dark else ':root'
        errors.append(f'{tag} 专题 CSS 的 {where} 里未设置滚动条品牌色：{", ".join(missing)}')
    if re.search(r'scrollbar-color\s*:', css):
        errors.append(f'{tag} 专题 CSS 里不要设置 scrollbar-color（Chrome 121+ 会忽略自定义滚动条）')


ENT = {
    'zh': ('增值税', '专票', '对公转账', '合同', '专属'),
    'en': ('VAT', 'bank transfer', 'contract', 'dedicated'),
}


def check_enterprise(tag, lang, html):
    # 每个专题页都必须有企业接入版块，并在 description 和 FAQ 里写明开票/对公转账
    if 'id="enterprise"' not in html:
        errors.append(f'{tag} 缺少企业接入版块（section id="enterprise"）')
    if 'href="#enterprise"' not in html:
        errors.append(f'{tag} 导航缺少指向 #enterprise 的入口')
    m = re.search(r'id="enterprise".*?</section>', html, re.S)
    body = m.group(0) if m else ''
    low = body.lower()
    miss = [k for k in ENT[lang] if k.lower() not in low]
    if m and miss:
        errors.append(f'{tag} 企业接入版块缺少要点：{", ".join(miss)}')
    if m and 'https://anyaigc.ai/customersupport' not in body:
        errors.append(f'{tag} 企业接入版块缺少联系客服按钮')
    d = re.search(r'<meta name="description" content="(.*?)"', html)
    key = ('对公', '专票', '发票') if lang == 'zh' else ('invoic', 'bank transfer', 'contract')
    if d and not any(k in d.group(1).lower() for k in key):
        errors.append(f'{tag} meta description 未提及企业开票/对公转账')
    faq_key = ('专票', '对公转账') if lang == 'zh' else ('VAT special invoice', 'bank transfer')
    for k in faq_key:
        if not re.search(r'"@type": "Question", "name": "[^"]*' + re.escape(k), html, re.I):
            errors.append(f'{tag} FAQ 缺少关于「{k}」的问题')
    if re.search(r'联系客服确认发票方案|contact support about invoicing', html, re.I):
        errors.append(f'{tag} 仍有含糊的开票说法，应改为明确支持对公转账和增值税发票')


def page_url(lang, slug):
    return f'{SITE}/{lang}/models/' + ('' if slug == 'index' else slug)


def check(lang, slug):
    rel = f'{lang}/models/{slug}.html'
    s = read(rel)
    tag = f'[{rel}]'
    me, other = page_url(lang, slug), page_url('en' if lang == 'zh' else 'zh', slug)

    if not re.search(rf'<html lang="{LANGS[lang]}"', s):
        errors.append(f'{tag} <html lang> 应为 {LANGS[lang]}')
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    d = re.search(r'<meta name="description" content="(.*?)"', s)
    if not t:
        errors.append(f'{tag} 缺少 <title>')
    elif lang == 'en' and len(t.group(1)) > 65:
        warns.append(f'{tag} 英文 title {len(t.group(1))} 字符，建议 ≤ 65')
    elif lang == 'zh' and width(t.group(1)) > 64:
        warns.append(f'{tag} 中文 title 显示宽度 {width(t.group(1))}（汉字计 2），建议 ≤ 64')
    if not d:
        errors.append(f'{tag} 缺少 meta description')
    elif lang == 'en' and not 120 <= len(d.group(1)) <= 160:
        warns.append(f'{tag} 英文 description {len(d.group(1))} 字符，建议 120–160')
    elif lang == 'zh' and not 60 <= len(d.group(1)) <= 120:
        warns.append(f'{tag} 中文 description {len(d.group(1))} 字，建议 60–120')

    if len(re.findall(r'<h1[\s>]', s)) != 1:
        errors.append(f'{tag} 必须且只能有一个 <h1>')
    canon = re.findall(r'rel="canonical" href="([^"]+)"', s)
    if canon != [me]:
        errors.append(f'{tag} canonical 应为 {me}，实际 {canon}')
    hl = dict(re.findall(r'rel="alternate" hreflang="([^"]+)" href="([^"]+)"', s))
    want = {'zh-CN': page_url('zh', slug), 'en': page_url('en', slug), 'x-default': page_url('en', slug)}
    if hl != want:
        errors.append(f'{tag} hreflang 不完整或不对：{hl}')
    for prop in ('og:title', 'og:description', 'og:image', 'og:url'):
        if f'property="{prop}"' not in s:
            errors.append(f'{tag} 缺少 {prop}')
    og = re.search(r'property="og:image" content="([^"]+)"', s)
    if og and og.group(1).startswith(SITE) and not local_exists(og.group(1)[len(SITE):]):
        errors.append(f'{tag} og:image 文件不存在：{og.group(1)}')
    if 'name="twitter:card"' not in s:
        errors.append(f'{tag} 缺少 twitter:card')
    if '/assets/models/scrollbar.css' not in s:
        errors.append(f'{tag} 未引入 /assets/models/scrollbar.css')
    if slug != 'index':
        check_scrollbar(tag, s)
        check_enterprise(tag, lang, s)

    types = []
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            data = json.loads(m)
        except ValueError as e:
            errors.append(f'{tag} JSON-LD 解析失败：{e}')
            continue
        for g in data.get('@graph', [data]):
            types.append(g.get('@type'))
    need = ['BreadcrumbList'] + (['ItemList'] if slug == 'index' else ['Product', 'FAQPage'])
    for n in need:
        if n not in types:
            errors.append(f'{tag} JSON-LD 缺少 {n}')

    if slug != 'index':
        faq_visible = len(re.findall(r'<details', s))
        faq_ld = s.count('"@type": "Question"')
        if faq_visible != faq_ld:
            errors.append(f'{tag} 可见 FAQ {faq_visible} 条，JSON-LD FAQ {faq_ld} 条，必须一致')

    for h in sorted(set(re.findall(r'(?:href|src)="(/[^"]*)"', s))):
        if not local_exists(h):
            errors.append(f'{tag} 站内链接失效：{h}')
    for h in re.findall(r'href="(/[^"]*\.html)"', s):
        warns.append(f'{tag} 站内链接带 .html（Cloudflare 会 308 跳转）：{h}')
    if re.search(r'(?:href|src)="(?!/|https?:|#|mailto:|data:)[^"]+"', s):
        errors.append(f'{tag} 存在相对路径资源/链接，专题页必须用以 / 开头的绝对路径')
    if not re.search(rf'href="/{"en" if lang == "zh" else "zh"}/models/{"" if slug == "index" else slug}"', s):
        errors.append(f'{tag} 缺少切换到另一语言版本的链接')
    for r in re.findall(r'https://anyaigc\.ai/register[^"\s<]*', s):
        if r.replace('&amp;', '&') != REGISTER:
            errors.append(f'{tag} 注册链接应为 {REGISTER}，实际 {r}')
    # 只看可见文字和 JSON-LD 文本，忽略标签属性（如 class="s-group"、scope="rowgroup"）
    body = re.sub(r'<script\b.*?</script>|<style\b.*?</style>', ' ', s, flags=re.S)
    visible = re.sub(r'<[^>]+>', ' ', body) + ' '.join(re.findall(r'"(?:name|text)": "([^"]*)"', s))
    if re.search(r'分组|\bgroups?\b', visible, re.I):
        errors.append(f'{tag} 页面不能出现令牌分组信息（分组/group）')
    if '500+' in s:
        errors.append(f'{tag} 平台模型数应写 300+，发现 500+')


def main():
    slugs = {}
    for lang in LANGS:
        d = os.path.join(ROOT, lang, 'models')
        slugs[lang] = sorted(f[:-5] for f in os.listdir(d) if f.endswith('.html')) if os.path.isdir(d) else []
    for s in set(slugs['zh']) ^ set(slugs['en']):
        errors.append(f'中英文不对称：{s}.html 只存在于一种语言')
    sitemap = read('sitemap.xml')
    for lang in LANGS:
        hub = read(f'{lang}/models/index.html')
        for slug in slugs[lang]:
            check(lang, slug)
            if slug == 'index':
                continue
            if f'href="/{lang}/models/{slug}"' not in hub:
                errors.append(f'[{lang}/models/index.html] 专题首页未加入 {slug} 的卡片')
            if f'"{page_url(lang, slug)}"' not in hub:
                errors.append(f'[{lang}/models/index.html] JSON-LD ItemList 未加入 {slug}')
            if f'<loc>{page_url(lang, slug)}</loc>' not in sitemap:
                errors.append(f'[sitemap.xml] 未加入 {page_url(lang, slug)}')
        # 卡片 + 分类标题里链接的系列总览页（如 Claude 系列标题链接到 /models/claude）
        cards = len(re.findall(r'<li class="af-model[ "]', hub)) + len(re.findall(r'<h3 class="af-section-head"[^>]*><a href="/' + lang + r'/models/', hub))
        m = re.search(r'"numberOfItems": (\d+)', hub)
        if m and int(m.group(1)) != len(slugs[lang]) - 1:
            errors.append(f'[{lang}/models/index.html] numberOfItems={m.group(1)}，实际专题数 {len(slugs[lang]) - 1}')
        if cards != len(slugs[lang]) - 1:
            warns.append(f'[{lang}/models/index.html] 卡片 {cards} 张，专题页 {len(slugs[lang]) - 1} 个')

    for w in warns:
        print('WARN ', w)
    for e in errors:
        print('ERROR', e)
    print(f'\n检查完成：{len(errors)} 个错误，{len(warns)} 个警告')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
