# 多语言专题页：HTML 文本切分与回填。
# 把英文页切成「翻译单元」（保留内联标签），回填译文时只替换这些位置，其余字节原样保留。
# 不依赖第三方库：自带分词器记录每个标签、文本的字节偏移，所以回填是精确的区间替换。
import html as _html
import json
import re

VOID = {'meta', 'link', 'img', 'br', 'hr', 'input', 'source', 'area', 'base', 'col', 'embed', 'track', 'wbr'}
RAW = {'script', 'style'}
# 整块不翻译：代码、预格式化文本、脚本
SKIP = {'script', 'style', 'pre', 'kbd', 'samp', 'code', 'noscript_x'}
# 单元内用占位符保护的整块（译者看不到内部结构）
PLACEHOLDER = {'svg', 'img', 'video', 'audio', 'canvas', 'picture'}
BLOCK = {'div', 'p', 'li', 'ul', 'ol', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th', 'section', 'article',
         'header', 'footer', 'nav', 'main', 'aside', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'details', 'summary',
         'figure', 'figcaption', 'dl', 'dt', 'dd', 'form', 'select', 'option', 'caption', 'blockquote', 'button',
         'label', 'fieldset', 'legend', 'body', 'html', 'head'}
TRANS_ATTRS = {'alt', 'title', 'aria-label', 'placeholder', 'data-done', 'data-play-label', 'data-pause-label',
               'data-wait', 'data-text', 'data-label'}
META_TRANS = {('name', 'description'), ('name', 'keywords'), ('property', 'og:title'),
              ('property', 'og:description'), ('property', 'og:image:alt'), ('name', 'twitter:title'),
              ('name', 'twitter:description')}
LD_KEYS = {'name', 'description', 'text', 'headline', 'alternativeHeadline', 'category', 'caption', 'abstract'}

TOKEN = re.compile(r'<!--.*?-->|<![a-zA-Z][^>]*>|<(/?)([a-zA-Z][a-zA-Z0-9:_-]*)((?:"[^"]*"|\'[^\']*\'|[^>"\'])*)>', re.S)
ATTR = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'>]+)))?')
LETTER = re.compile(r'[^\W\d_]', re.U)
WORD2 = re.compile(r'[^\W\d_]{2,}', re.U)


class Node:
    __slots__ = ('tag', 'attrs', 's', 'so', 'ec', 'e', 'kids', 'parent', 'raw')

    def __init__(self, tag, s, so=None, parent=None):
        self.tag = tag          # 小写标签名；文本节点为 '#text'
        self.attrs = ''         # 起始标签里的属性原文
        self.s = s              # 起始标签（或文本）起点
        self.so = so            # 起始标签终点 = 内容起点（文本节点：文本终点）
        self.ec = None          # 结束标签起点 = 内容终点
        self.e = None           # 结束标签终点
        self.kids = []
        self.parent = parent
        self.raw = False


def parse(src):
    root = Node('#root', 0, 0)
    root.ec = root.e = len(src)
    stack = [root]
    pos = 0
    n = len(src)

    def text(a, b):
        if b > a:
            t = Node('#text', a, b, stack[-1])
            stack[-1].kids.append(t)

    while pos < n:
        m = TOKEN.search(src, pos)
        if not m:
            text(pos, n)
            break
        text(pos, m.start())
        pos = m.end()
        if m.group(2) is None:                       # 注释 / doctype
            continue
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if closing:
            for i in range(len(stack) - 1, 0, -1):
                if stack[i].tag == tag:
                    for dead in stack[i + 1:]:       # 隐式闭合
                        dead.ec = dead.e = m.start()
                    stack[i].ec, stack[i].e = m.start(), m.end()
                    del stack[i:]
                    break
            continue
        node = Node(tag, m.start(), m.end(), stack[-1])
        node.attrs = attrs
        stack[-1].kids.append(node)
        if tag in VOID or attrs.rstrip().endswith('/'):
            node.ec, node.e = m.end(), m.end()
            continue
        if tag in RAW:
            end = re.compile(r'</' + tag + r'\s*>', re.I).search(src, pos)
            if not end:
                raise ValueError(f'未闭合的 <{tag}> @ {m.start()}')
            node.raw = True
            node.ec, node.e = end.start(), end.end()
            if end.start() > pos:
                t = Node('#text', pos, end.start(), node)
                node.kids.append(t)
            pos = end.end()
            continue
        stack.append(node)
    for dead in stack[1:]:
        dead.ec = dead.e = n
    return root


def attrs_of(node):
    out = {}
    for m in ATTR.finditer(node.attrs):
        out[m.group(1).lower()] = _html.unescape(next((g for g in m.groups()[1:] if g is not None), ''))
    return out


def attr_spans(node):
    """属性值在原文中的区间：{name: (start, end, quote)}，只含带引号的。"""
    out = {}
    base = node.s + 1 + len(node.tag)
    for m in re.finditer(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*("([^"]*)"|\'([^\']*)\')', node.attrs):
        q = m.group(2)[0]
        vs = base + m.start(2) + 1
        out[m.group(1).lower()] = (vs, vs + len(m.group(2)) - 2, q)
    return out


def walk(node):
    yield node
    for k in node.kids:
        yield from walk(k)


def has_block(node):
    return any(d.tag in BLOCK for k in node.kids for d in walk(k))


def has_letters_text(node, src):
    return any(k.tag == '#text' and LETTER.search(src[k.s:k.so]) for k in node.kids)


def translatable(inner):
    """单元里除标签、实体、占位符外是否还有 2 个以上连续字母。"""
    t = re.sub(r'<[^>]+>|&[#a-zA-Z0-9]+;|\{\{\d+\}\}', ' ', inner)
    return bool(WORD2.search(t))


class Span:
    """一个可替换的区间。kind: unit / attr / title / ld。"""
    __slots__ = ('kind', 's', 'e', 'text', 'ph', 'meta')

    def __init__(self, kind, s, e, text, ph=None, meta=None):
        self.kind, self.s, self.e, self.text, self.ph, self.meta = kind, s, e, text, ph or [], meta or {}


def protect(inner):
    """把 svg/img/video 等整块换成 {{N}} 占位符，返回 (文本, 原块列表)。"""
    ph = []

    def sub(m):
        ph.append(m.group(0))
        return '{{%d}}' % (len(ph) - 1)
    pat = r'<(svg|video|audio|canvas|picture)\b[^>]*>.*?</\1\s*>|<img\b[^>]*>'
    return re.sub(pat, sub, inner, flags=re.S | re.I), ph


def restore(text, ph):
    return re.sub(r'\{\{(\d+)\}\}', lambda m: ph[int(m.group(1))], text)


def collect(src, root=None):
    """返回按位置排序的 Span 列表。"""
    root = root or parse(src)
    spans = []

    def add_unit(a, b):
        inner = src[a:b]
        lead = len(inner) - len(inner.lstrip())
        trail = len(inner) - len(inner.rstrip())
        core = inner[lead:len(inner) - trail]
        if not core:
            return
        text, ph = protect(core)
        if translatable(text):
            spans.append(Span('unit', a + lead, b - trail, text, ph))

    def visit(node):
        tag = node.tag
        if tag == '#text':
            return
        if tag == 'details' and 'lang-menu' in node.attrs:
            return                                    # 语言下拉菜单由 build.py 生成，不参与翻译
        if node.raw:
            if tag == 'script' and 'ld+json' in node.attrs:
                spans.append(Span('ldjson', node.so, node.ec, src[node.so:node.ec]))
            return
        # 属性
        if tag == 'meta':
            at = attrs_of(node)
            key = next(((k, at[k]) for k in ('name', 'property') if k in at), None)
            if key in META_TRANS and 'content' in at:
                sp = attr_spans(node).get('content')
                if sp:
                    spans.append(Span('attr', sp[0], sp[1], _html.unescape(src[sp[0]:sp[1]]), meta={'attr': 'meta:' + key[1]}))
            return
        if tag in ('link', 'base'):
            return
        if node.attrs and tag not in ('html',):
            sp = attr_spans(node)
            at = attrs_of(node)
            for a in TRANS_ATTRS:
                if a in sp and WORD2.search(at.get(a, '')) and not (tag == 'a' and a == 'title' and False):
                    spans.append(Span('attr', sp[a][0], sp[a][1], _html.unescape(src[sp[a][0]:sp[a][1]]), meta={'attr': a}))
        if tag in SKIP:
            return
        if tag == 'svg':
            for d in walk(node):
                if d.tag in ('text', 'title', 'desc', 'tspan') and d.ec is not None and d is not node:
                    if not any(k.tag != '#text' for k in d.kids):
                        add_unit(d.so, d.ec)
            return
        if tag == 'title':
            add_unit(node.so, node.ec)
            return
        if tag in PLACEHOLDER:
            return
        if node.so is not None and has_letters_text(node, src) and not has_block(node):
            # 带有 hreflang 的语言切换链接单独处理，不进翻译
            if tag == 'a' and 'hreflang' in node.attrs:
                return
            # 内联子元素上的属性（如 <a title=...>）留在单元文本里，由译者一并翻译，校验时核对标签结构
            add_unit(node.so, node.ec)
            return
        for k in node.kids:
            if k.tag == '#text':
                if node.tag not in ('#root', 'head') and LETTER.search(src[k.s:k.so]):
                    add_unit(k.s, k.so)
            else:
                visit(k)

    for k in root.kids:
        visit(k)
    spans.sort(key=lambda s: s.s)
    return spans


def ld_strings(raw):
    """JSON-LD 里需要翻译的字符串路径（FAQPage 单独由可见 FAQ 同步，不在此列）。"""
    data = json.loads(raw)
    out = []

    def rec(o, path, skip):
        if isinstance(o, dict):
            t = o.get('@type')
            if t == 'FAQPage' or t == 'Question' or t == 'Answer':
                return
            if t in ('Organization', 'Brand', 'WebSite'):
                skip = True
            for k, v in o.items():
                if isinstance(v, str) and k in LD_KEYS and not skip and WORD2.search(v):
                    out.append((path + [k], v))
                else:
                    rec(v, path + [k], skip)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                rec(v, path + [i], skip)
    rec(data, [], False)
    return data, out


def set_path(data, path, value):
    o = data
    for p in path[:-1]:
        o = o[p]
    o[path[-1]] = value


def apply_spans(src, repl):
    """repl: [(start, end, new_text)]，按区间替换。"""
    out, last = [], 0
    for s, e, t in sorted(repl):
        out.append(src[last:s])
        out.append(t)
        last = e
    out.append(src[last:])
    return ''.join(out)
