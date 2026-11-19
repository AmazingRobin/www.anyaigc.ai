# 新语言页上线后的注册：sitemap、以及已有中英文页的 hreflang 与语言菜单。
# 用法：python scripts/i18n/register.py <slug>...      （重复运行结果不变）
# 对每个 slug：以磁盘上实际存在的 <lang>/models/<slug>.html 为准，
#   1. sitemap.xml：每种存在的语言一条 <url>，且每条都带全部存在语言的 xhtml:link 与 x-default
#   2. zh/en 页：<head> 补上新语言 hreflang 和 og:locale:alternate；
#      导航和页脚里原来的单个语言链接换成下拉菜单；相关链接列表等正文处的单个链接保持不变
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
import langs as L

ROOT = B.ROOT
NL = '\n'
TODAY = '2026-11-17'


def read(p):
    return io.open(os.path.join(ROOT, p), encoding='utf-8').read()


def write(p, s):
    io.open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline=NL).write(s)


def present(slug):
    return [c for c in L.ALL if os.path.isfile(os.path.join(ROOT, c, 'models', slug + '.html'))]


def sitemap_block(slug, lang, langs, lastmod):
    alts = ''.join(f'    <xhtml:link rel="alternate" hreflang="{L.LANGS[c]["hreflang"]}" href="{L.url(c, slug)}"/>{NL}' for c in langs)
    alts += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{L.url("en", slug)}"/>{NL}'
    return f'  <url>{NL}    <loc>{L.url(lang, slug)}</loc>{NL}    <lastmod>{lastmod}</lastmod>{NL}{alts}  </url>'


def url_re(slug, lang):
    return re.compile(r'[ \t]*<url>\s*<loc>' + re.escape(L.url(lang, slug)) + r'</loc>.*?</url>', re.S)


def update_sitemap(slugs):
    s = read('sitemap.xml')
    for slug in slugs:
        langs = present(slug)
        # 已有的条目原地更新（保留各自的 lastmod），缺少的补到该 slug 最后一个条目之后
        for lang in L.ALL:
            m = url_re(slug, lang).search(s)
            if m:
                lm = re.search(r'<lastmod>([^<]+)</lastmod>', m.group(0))
                s = s[:m.start()] + sitemap_block(slug, lang, langs, lm.group(1) if lm else TODAY) + s[m.end():]
        ends = [m.end() for m in (url_re(slug, c).search(s) for c in L.ALL) if m]
        pos = max(ends)
        add = ''.join(NL + sitemap_block(slug, c, langs, TODAY) for c in langs
                      if f'<loc>{L.url(c, slug)}</loc>' not in s)
        s = s[:pos] + add + s[pos:]
    write('sitemap.xml', s)


def upgrade_page(lang, slug):
    """zh/en 页：补 hreflang、og:locale:alternate，导航和页脚的语言切换换成下拉菜单。"""
    rel = f'{lang}/models/{slug}.html'
    orig = read(rel)
    langs = present(slug)
    other = 'en' if lang == 'zh' else 'zh'
    s = B.convert_switches(orig, slug, lang, langs, L.LANGS[other]['hreflang'], drop_body=True)   # 正文里的单个语言链接（如 "X API in English"）有了语言菜单就不再需要
    links = NL.join(f'<link rel="alternate" hreflang="{L.LANGS[c]["hreflang"]}" href="{L.url(c, slug)}">' for c in langs)
    links += f'{NL}<link rel="alternate" hreflang="x-default" href="{L.url("en", slug)}">'
    s = re.sub(r'(?:<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?)+', lambda m: links + NL, s, count=1)
    s = re.sub(r'<meta property="og:locale:alternate" content="[^"]*">\n?', '', s)
    alts = NL.join(f'<meta property="og:locale:alternate" content="{L.LANGS[c]["og"]}">' for c in langs if c != lang)
    s = re.sub(r'(<meta property="og:locale" content="[^"]*">)\n?', lambda m: m.group(1) + NL + alts + NL, s, count=1)
    if s != orig:
        write(rel, s)
        return True
    return False


def main():
    slugs = sys.argv[1:]
    if not slugs:
        raise SystemExit('用法：register.py <slug>...')
    update_sitemap(slugs)
    n = 0
    for slug in slugs:
        for lang in ('zh', 'en'):
            if os.path.isfile(os.path.join(ROOT, lang, 'models', slug + '.html')):
                n += upgrade_page(lang, slug)
    print(f'sitemap 已更新 {len(slugs)} 个 slug；zh/en 页改动 {n} 个')


if __name__ == '__main__':
    main()
