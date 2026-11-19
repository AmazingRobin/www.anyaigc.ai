# 多语言专题页：从英文页生成其他语言页。
# 用法：
#   python scripts/i18n/build.py extract <slug>            抽取英文页，写出 drafts/i18n/<slug>/en.json
#   python scripts/i18n/build.py build <slug> <lang>       用 drafts/i18n/<slug>/<lang>.json 回填，写出 <lang>/models/<slug>.html
#   python scripts/i18n/build.py relink <lang> <slug>...   已生成的页面重新处理站内链接（新系列上线后用）
# 翻译文件是 JSON：{"units": {"<id>": "<译文>"}, "ld": {"<id>": "<译文>"}}，id 与 en.json 对应。
# 缺条目、多条目、标签结构对不上都会直接报错，不会写出半成品。
# 顺序：先把译文写回英文源页（编号稳定），再改路径、hreflang、语言切换。
#
# 语言切换（convert_switches）按位置分三类：
#   nav  导航栏里的切换链接   -> 下拉菜单，向下展开，按钮显示语言代码（ZH / EN / JA...）
#   foot 页脚里的切换链接     -> 下拉菜单，向上展开，按钮显示当前语言的自称
#   body 相关链接列表等正文处 -> zh/en 页保持原来的单个链接；新语言页直接删掉（页脚菜单已覆盖）
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H
import langs as L
import overseas as O

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = '\n'
DRAFT = os.path.join(ROOT, 'drafts', 'i18n')
MENU_CSS = '/assets/models/lang-menu.css?v=20261117c'
MENU_JS = '/assets/models/lang-menu.js?v=20261117c'
SHORT = {'zh': 'ZH', 'en': 'EN', 'ja': 'JA', 'ko': 'KO', 'es': 'ES', 'de': 'DE'}
# 导航栏文字太长会把右侧按钮挤出屏幕（西语七项共 92 个字符，中文只有 39）：只在导航栏里改用短写法，页面正文和页脚不变
NAV_SHORT = {
    'es': {'Guías de modelos': 'Modelos', 'Catálogo de modelos': 'Catálogo', 'Documentación de la API': 'Docs de API',
           'Iniciar sesión': 'Acceder'},
    'de': {'Modellguides': 'Modelle', 'Modellkatalog': 'Katalog', 'API-Dokumentation': 'API-Doku'},
}
NAV_CLASS = re.compile(r'(?:^|[\s_-])nav(?:[\s_-]|$)')


def cls(node):
    m = re.search(r'class="([^"]*)"', node.attrs or '')
    return m.group(1) if m else ''


def is_menu(node):
    return node.tag == 'details' and 'lang-menu' in (node.attrs or '')


def switch_anchors(root, src, hl='zh-CN'):
    """页面里所有指向另一种语言的原始切换链接。已经生成的下拉菜单里的链接不算。"""
    out = []

    def rec(n, anc):
        for k in n.kids:
            if k.tag == '#text' or is_menu(k):
                continue
            if k.tag == 'a' and f'hreflang="{hl}"' in k.attrs:
                out.append((k, anc))
            else:
                rec(k, anc + [k])
    rec(root, [])
    return out


def placement(node, anc):
    """nav / foot / body。页脚优先：有些页面的页脚链接带 locale 类，不能当导航。"""
    chain = anc[-3:] + [node]
    if any(a.tag == 'footer' for a in anc) or any(re.search(r'foot', cls(a)) for a in chain):
        return 'foot'
    if any(a.tag in ('header', 'nav') for a in anc) or any(NAV_CLASS.search(cls(a)) for a in anc[-4:] + [node]):
        return 'nav'
    return 'body'


def menu(slug, lang, langs=None, kind='nav'):
    langs = langs or L.ALL
    items = ''.join(
        f'<li><a href="/{c}/models/{slug}" hreflang="{L.LANGS[c]["hreflang"]}" lang="{L.LANGS[c]["hreflang"]}">'
        f'{L.LANGS[c]["native"]}</a></li>' for c in langs if c != lang)
    label = L.LANGS[lang]['native'] if kind == 'foot' else SHORT[lang]
    extra = ' lang-menu--foot' if kind == 'foot' else ''
    return (f'<details class="lang-menu{extra}"><summary aria-label="Language: {L.LANGS[lang]["native"]}">{label}</summary>'
            f'<ul class="lang-menu-list">{items}</ul></details>')


def convert_switches(src, slug, lang, langs, other_hl, drop_body):
    """原始的单语言切换链接 -> 菜单；已有菜单 -> 按当前语言原地重生成（重复运行结果不变）。"""
    root = H.parse(src)
    repl = []
    for n in H.walk(root):
        if is_menu(n):
            repl.append((n.s, n.e, menu(slug, lang, langs, 'foot' if 'lang-menu--foot' in n.attrs else 'nav')))
    for node, anc in switch_anchors(root, src, other_hl):
        place = placement(node, anc)
        parent = anc[-1] if anc else None
        if place == 'body':
            if not drop_body:
                continue
            if parent is not None and parent.tag == 'li' and \
                    O.strip_tags(src[parent.so:parent.ec]) == O.strip_tags(src[node.s:node.e]):
                repl.append(O.line_span(src, parent) + ('',))
            else:
                repl.append((node.s, node.e, ''))
            continue
        start = node.s
        if parent is not None:
            sib = parent.kids
            i = sib.index(node)
            if i and sib[i - 1].tag == 'span' and 'aria-current' in sib[i - 1].attrs:
                start = sib[i - 1].s                      # 去掉旧的"当前语言"标记
            # 外层容器自带胶囊底色（如 li.d-lang）会和菜单按钮叠成两层，去掉它的 class
            only_switch = all(k.tag in ('#text', 'span', 'a') for k in sib)
            if place == 'nav' and only_switch and re.search(r'lang|locale', cls(parent)) and parent.so is not None:
                repl.append((parent.s, parent.so, re.sub(r'\sclass="[^"]*"', '', src[parent.s:parent.so], count=1)))
        repl.append((start, node.e, menu(slug, lang, langs, place)))
    s = H.apply_spans(src, repl)
    return add_menu_assets(s)


def add_menu_assets(s):
    if 'class="lang-menu' not in s:
        return s
    if 'lang-menu.css' not in s:
        s = re.sub(r'(<link rel="stylesheet" href="/assets/models/scrollbar\.css[^>]*>)',
                   lambda m: m.group(1) + NL + f'<link rel="stylesheet" href="{MENU_CSS}">', s, count=1)
    else:
        s = re.sub(r'/assets/models/lang-menu\.css\?v=[0-9a-z]+', MENU_CSS, s)
    if 'lang-menu.js' not in s:
        s = s.replace('</body>', f'<script defer src="{MENU_JS}"></script>{NL}</body>', 1)
    else:
        s = re.sub(r'/assets/models/lang-menu\.js\?v=[0-9a-z]+', MENU_JS, s)
    return s


def shorten_nav(s, lang):
    table = NAV_SHORT.get(lang)
    if not table:
        return s
    root = H.parse(s)
    repl = []

    def rec(n, anc):
        for k in n.kids:
            if k.tag == '#text':
                continue
            if k.tag == 'a' and k.so is not None and placement(k, anc) == 'nav' and                     all(c.tag != 'a' for c in k.kids) and not is_menu(k):
                t = s[k.so:k.ec]
                if t in table:
                    repl.append((k.so, k.ec, table[t]))
            elif not is_menu(k):
                rec(k, anc + [k])
    rec(root, [])
    return H.apply_spans(s, repl)


def has_page(lang, slug):
    return os.path.isfile(os.path.join(ROOT, lang, 'models', slug + '.html'))


HREF_MODELS = re.compile(r'href="/(?:en|ja|ko|es|de)/models/([^"#?]*)"')


def relink(s, lang):
    """站内链接：目标语言页存在就指向它，不存在就退回英文页。
    带 hreflang 的链接是语言切换，不动。"""
    def fix(m):
        tag = m.group(0)
        if 'hreflang=' in tag:
            return tag
        mm = HREF_MODELS.search(tag)
        if not mm:
            return tag
        slug = mm.group(1) or 'index'
        want = lang if has_page(lang, slug) else 'en'
        return tag.replace(mm.group(0), f'href="/{want}/models/{mm.group(1)}"')
    return re.sub(r'<a\b[^>]*>', fix, s)


def localize(src, slug, lang):
    """路径、hreflang、og、语言切换。输入是已经翻译好的英文结构页。"""
    s = re.sub(r'(<html\b[^>]*\blang=")[^"]*"', lambda m: m.group(1) + L.LANGS[lang]['hreflang'] + '"', src, count=1)
    s = s.replace('/en/models/', f'/{lang}/models/')
    s = s.replace(f'/assets/og/{slug}-en.png', f'/assets/og/{slug}-{lang}.png')
    # 语言菜单在路径替换之后生成，它的链接要保持 /en/ /zh/ 等原样
    s = convert_switches(s, slug, lang, L.ALL, 'zh-CN', drop_body=True)
    s = shorten_nav(relink(s, lang), lang)
    s = re.sub(r'(property="og:locale" content=")[^"]*"', lambda m: m.group(1) + L.LANGS[lang]['og'] + '"', s, count=1)
    s = re.sub(r'<meta property="og:locale:alternate" content="[^"]*">\n?', '', s)
    alts = NL.join(f'<meta property="og:locale:alternate" content="{L.LANGS[c]["og"]}">' for c in L.ALL if c != lang)
    s = s.replace(f'<meta property="og:locale" content="{L.LANGS[lang]["og"]}">',
                  f'<meta property="og:locale" content="{L.LANGS[lang]["og"]}">{NL}{alts}', 1)
    s = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', '', s)
    links = NL.join(f'<link rel="alternate" hreflang="{L.LANGS[c]["hreflang"]}" href="{L.url(c, slug)}">' for c in L.ALL)
    links += f'{NL}<link rel="alternate" hreflang="x-default" href="{L.url("en", slug)}">'
    s = s.replace(f'<link rel="canonical" href="{L.url(lang, slug)}">',
                  f'<link rel="canonical" href="{L.url(lang, slug)}">{NL}{links}', 1)
    s = re.sub(r'("inLanguage":\s*")en(")', lambda m: m.group(1) + L.LANGS[lang]['hreflang'] + m.group(2), s)
    return s


def tag_skeleton(text):
    return re.findall(r'</?[a-zA-Z][^>]*>', text)


def dump(spans):
    units, ld = {}, {}
    for i, s in enumerate(spans):
        if s.kind == 'ldjson':
            data, paths = H.ld_strings(s.text)
            for j, (p, v) in enumerate(paths):
                ld[f'ld{j}'] = v
        else:
            units[f'u{i}'] = s.text
    return {'units': units, 'ld': ld}


def source(slug):
    """翻译源 = 英文页去掉"中国大陆可访问"卖点（非中文页不写，见记忆 en-no-china-access-claim）。
    extract / batch.prepare / build 三处都必须用它，单元编号才对得上。"""
    src = io.open(os.path.join(ROOT, 'en', 'models', slug + '.html'), encoding='utf-8').read()
    return O.strip_china_access(src)


def extract(slug):
    src = source(slug)
    out = dump(H.collect(src))
    d = os.path.join(DRAFT, slug)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'en.json'), 'w', encoding='utf-8', newline=NL).write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print(f'{slug}: {len(out["units"])} 个文本单元，{len(out["ld"])} 条结构化数据')


def build(slug, lang):
    src = source(slug)
    spans = H.collect(src)
    base = dump(spans)
    tr = json.load(io.open(os.path.join(DRAFT, slug, lang + '.json'), encoding='utf-8'))
    miss = (set(base['units']) - set(tr['units'])) | (set(base['ld']) - set(tr['ld']))
    extra = (set(tr['units']) - set(base['units'])) | (set(tr['ld']) - set(base['ld']))
    if miss or extra:
        raise SystemExit(f'{slug}/{lang} 翻译条目对不上：缺 {sorted(miss)[:8]}，多 {sorted(extra)[:8]}')
    for k, v in base['units'].items():
        if tag_skeleton(v) != tag_skeleton(tr['units'][k]):
            raise SystemExit(f'{slug}/{lang} {k} 的标签结构被改动了，译文必须保留原文里的标签')
        if v.count('{{') != tr['units'][k].count('{{'):
            raise SystemExit(f'{slug}/{lang} {k} 的占位符数量不对')

    repl = []
    for i, s in enumerate(spans):
        if s.kind == 'ldjson':
            data, paths = H.ld_strings(s.text)
            for j, (p, v) in enumerate(paths):
                H.set_path(data, p, tr['ld'][f'ld{j}'])
            repl.append((s.s, s.e, NL + json.dumps(data, ensure_ascii=False, indent=2) + NL))
        else:
            text = H.restore(tr['units'][f'u{i}'], s.ph)
            if s.kind == 'attr':
                text = text.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
            repl.append((s.s, s.e, text))
    # FAQPage 按可见 FAQ 重建，保证两处一致
    page = O.sync_faq(localize(H.apply_spans(src, repl), slug, lang))
    dest = os.path.join(ROOT, lang, 'models', slug + '.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    io.open(dest, 'w', encoding='utf-8', newline=NL).write(page)
    print(f'written {lang}/models/{slug}.html')


def relink_pages(lang, slugs):
    n = 0
    for slug in slugs:
        p = os.path.join(ROOT, lang, 'models', slug + '.html')
        if not os.path.isfile(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        t = relink(s, lang)
        if t != s:
            io.open(p, 'w', encoding='utf-8', newline=NL).write(t)
            n += 1
    print(f'relink {lang}: 改动 {n} 页')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'extract':
        extract(sys.argv[2])
    elif cmd == 'build':
        build(sys.argv[2], sys.argv[3])
    elif cmd == 'relink':
        relink_pages(sys.argv[2], sys.argv[3:])
    else:
        raise SystemExit('用法：build.py extract <slug> | build <slug> <lang> | relink <lang> <slug>...')
