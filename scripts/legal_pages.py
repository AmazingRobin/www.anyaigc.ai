# -*- coding: utf-8 -*-
"""隐私政策、服务条款的多语言页面。
中文原文是根目录的 privacy.html、terms.html（法律文本，唯一的源）；其他语言生成到 /<lang>/privacy.html、/<lang>/terms.html（en ja ko es de）。
译文在 scripts/legal_copy/<lang>.json：{"privacy": {"u0": "…"}, "terms": {…}}，键是 htmlseg 单元编号，和 scripts/legal_copy/src.json 一一对应。

用法：
  PYTHONIOENCODING=utf-8 python scripts/legal_pages.py extract        # 从中文页抽出待翻译单元，写 scripts/legal_copy/src.json
  PYTHONIOENCODING=utf-8 python scripts/legal_pages.py build [lang…]  # 生成各语言页面；同时给中文页补上 canonical / hreflang / 语言菜单，并更新 sitemap.xml
  PYTHONIOENCODING=utf-8 python scripts/legal_pages.py check          # 中文原文有没有改过（改过就要重新翻译）；各语言译文自检另见 scripts/i18n/check_legal_copy.py
中文页里 <!-- i18n:head --> 和 <!-- i18n:menu --> 两段是本脚本生成的，重复运行结果不变；抽取和渲染都先把它们去掉。
改了中文原文后：先 extract，把变化的单元重新翻译进各 <lang>.json，再 build。
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts', 'i18n'))
import htmlseg as H  # noqa: E402

PAGES = ['privacy', 'terms']
LANGS = ['zh', 'en', 'ja', 'ko', 'es', 'de']
NEW = ['en', 'ja', 'ko', 'es', 'de']
HL = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
NATIVE = {'zh': '中文', 'en': 'English', 'ja': '日本語', 'ko': '한국어', 'es': 'Español', 'de': 'Deutsch'}
SHORT = {'zh': 'ZH', 'en': 'EN', 'ja': 'JA', 'ko': 'KO', 'es': 'ES', 'de': 'DE'}
SITE = 'https://www.anyaigc.ai'
TODAY = '2026-11-24'
CSS_VER = '20261124'
MENU_CSS = '/assets/models/lang-menu.css?v=20261123c'
MENU_JS = '/assets/models/lang-menu.js?v=20261117c'
COPY = os.path.join(ROOT, 'scripts', 'legal_copy')


def path(lang, page):
    return f'/{page}' if lang == 'zh' else f'/{lang}/{page}'


def url(lang, page):
    return SITE + path(lang, page)


def read(p):
    return io.open(os.path.join(ROOT, p), encoding='utf-8').read()


def write(p, s):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, 'w', encoding='utf-8', newline='\n').write(s)


GEN = [re.compile(r'[ \t]*<!-- i18n:head -->.*?<!-- /i18n:head -->\n?', re.S),
       re.compile(r'[ \t]*<!-- i18n:menu -->.*?<!-- /i18n:menu -->\n?', re.S)]


def base_of(zh_html):
    """中文原文去掉本脚本生成的两段（head 补充、语言菜单），抽取和渲染都以它为准。"""
    s = zh_html
    for g in GEN:
        s = g.sub('', s)
    return s


def units(base):
    out = []
    for i, sp in enumerate(H.collect(base)):
        if sp.kind == 'ldjson':
            continue
        out.append({'id': f'u{i}', 'kind': sp.kind if sp.kind != 'attr' else 'attr:' + str(sp.meta.get('attr', '')), 'text': sp.text})
    return out


def menu_html(lang, page):
    items = ''.join(f'<li><a href="{path(c, page)}" hreflang="{HL[c]}" lang="{HL[c]}">{NATIVE[c]}</a></li>' for c in LANGS if c != lang)
    return (f'<details class="lang-menu"><summary aria-label="Language: {NATIVE[lang]}">{SHORT[lang]}</summary>'
            f'<ul class="lang-menu-list">{items}</ul></details>')


def head_block(lang, page):
    alts = '\n'.join(f'    <link rel="alternate" hreflang="{HL[c]}" href="{url(c, page)}" />' for c in LANGS)
    alts += f'\n    <link rel="alternate" hreflang="x-default" href="{url("en", page)}" />'
    return (f'    <!-- i18n:head -->\n    <link rel="canonical" href="{url(lang, page)}" />\n{alts}\n'
            f'    <link rel="stylesheet" href="{MENU_CSS}" />\n    <script defer src="{MENU_JS}"></script>\n    <!-- /i18n:head -->\n')


def render(page, lang, tr=None):
    """生成一个页面。lang == 'zh'：原文不动，只补 head 和语言菜单。tr：{"u0": "…"}，为空时从 legal_copy/<lang>.json 读。"""
    base = base_of(read(f'{page}.html'))
    if lang == 'zh':
        s = base
    else:
        if tr is None:
            tr = json.load(io.open(os.path.join(COPY, lang + '.json'), encoding='utf-8'))[page]
        spans = H.collect(base)
        repl = []
        for i, sp in enumerate(spans):
            if sp.kind == 'ldjson':
                continue
            text = H.restore(tr[f'u{i}'], sp.ph)
            if sp.kind == 'attr':
                text = text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
            repl.append((sp.s, sp.e, text))
        s = H.apply_spans(base, repl)
        s = re.sub(r'(<html\b[^>]*\blang=")[^"]*"', lambda m: m.group(1) + HL[lang] + '"', s, count=1)
        cut = s.find('<header class="af-hero">')
        top, rest = s[:cut], s[cut:]
        top = top.replace('href="https://anyaigc.ai"', f'href="/{lang}/"')   # 顶栏品牌和「首页」指向该语言的站点首页（原来指向控制台站点）
        s = top + rest
        for p in PAGES:
            s = s.replace(f'href="{p}.html"', f'href="{path(lang, p)}"')
        s = s.replace('href="favicon.ico"', 'href="/favicon.ico"')
    pre = '' if lang == 'zh' else '/'
    s = re.sub(r'href="/?legal\.css\?v=[0-9a-z]+"', f'href="{pre}legal.css?v={CSS_VER}"', s)
    s = s.replace('</head>', head_block(lang, page) + '  </head>', 1)
    i = s.find('</nav>')
    if i < 0:
        raise SystemExit(f'{page}: 找不到顶栏 </nav>')
    s = s[:i + 6] + f'\n        <!-- i18n:menu -->{menu_html(lang, page)}<!-- /i18n:menu -->' + s[i + 6:]
    return s


def sitemap_block(page, lang):
    alts = ''.join(f'    <xhtml:link rel="alternate" hreflang="{HL[c]}" href="{url(c, page)}"/>\n' for c in LANGS)
    alts += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url("en", page)}"/>\n'
    return f'  <url>\n    <loc>{url(lang, page)}</loc>\n    <lastmod>{TODAY}</lastmod>\n{alts}  </url>'


def update_sitemap():
    s = read('sitemap.xml')
    for page in PAGES:
        pat = {c: re.compile(r'[ \t]*<url>\s*<loc>' + re.escape(url(c, page)) + r'</loc>.*?</url>\n?', re.S) for c in LANGS}
        if not pat['zh'].search(s):
            raise SystemExit(f'sitemap.xml 里找不到 {url("zh", page)}')
        for c in NEW:
            s = pat[c].sub('', s)
        m = pat['zh'].search(s)
        s = s[:m.start()] + '\n'.join(sitemap_block(page, c) for c in LANGS) + '\n' + s[m.end():]
    write('sitemap.xml', s)


def cmd_extract():
    src = {p: units(base_of(read(f'{p}.html'))) for p in PAGES}
    write('scripts/legal_copy/src.json', json.dumps(src, ensure_ascii=False, indent=1) + '\n')
    print({p: len(v) for p, v in src.items()}, '个单元 -> scripts/legal_copy/src.json')


def cmd_check():
    src = json.load(io.open(os.path.join(COPY, 'src.json'), encoding='utf-8'))
    bad = 0
    for p in PAGES:
        now = units(base_of(read(f'{p}.html')))
        old = src[p]
        if [(u['id'], u['text']) for u in now] != [(u['id'], u['text']) for u in old]:
            bad += 1
            diff = [(a['id'], a['text'][:30]) for a, b in zip(now, old) if a['text'] != b['text']][:5]
            print(f'{p}.html 中文原文和 src.json 不一致（单元数 {len(now)} / {len(old)}），先 extract 再重新翻译：{diff}')
    print('中文原文与 src.json 一致' if not bad else '有差异')
    sys.exit(1 if bad else 0)


def cmd_build(langs):
    langs = langs or LANGS
    for lang in langs:
        for p in PAGES:
            out = render(p, lang)
            dest = f'{p}.html' if lang == 'zh' else f'{lang}/{p}.html'
            write(dest, out)
            print('written', dest, len(out.encode('utf-8')) // 1024, 'KB')
    if len(langs) == len(LANGS):
        update_sitemap()
        print('sitemap.xml 已更新')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'extract':
        cmd_extract()
    elif cmd == 'build':
        cmd_build([x for x in sys.argv[2:] if x in LANGS])
    elif cmd == 'check':
        cmd_check()
    else:
        raise SystemExit(__doc__)
