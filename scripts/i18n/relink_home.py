# -*- coding: utf-8 -*-
"""把 en / ja / ko / es / de 专题页和专题首页里指向站点首页的链接，从 / （中文首页）改成各自语言的首页 /<lang>/。
改两处：
  1. 可见链接：<a ... href="/"> （品牌、「首页」、面包屑）
  2. BreadcrumbList 里的 "item": "https://www.anyaigc.ai/"
  3. 指向 /privacy、/terms 的链接 -> /<lang>/privacy、/<lang>/terms
zh 页不动。Organization / WebSite 的 url、@id 是站点级标识，保持 https://www.anyaigc.ai/ 不变。
重复运行结果不变。重新生成英文页（各 *_pages.py 脚本）之后要再运行一次；新语言页由 build.py 的 localize() 在渲染时处理。
用法：python scripts/i18n/relink_home.py [--dry-run]
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LANGS = ['en', 'ja', 'ko', 'es', 'de']
SITE = 'https://www.anyaigc.ai'
ANCHOR = re.compile(r'(<a\b[^>]*?\bhref=")/(")')
ITEM = re.compile(r'("item":\s*")' + re.escape(SITE) + r'/(")')
LEGAL = re.compile(r'(<a\s[^>]*?href=")/(privacy|terms)(")')


def convert(t, lang):
    t, n1 = ANCHOR.subn(lambda m: f'{m.group(1)}/{lang}/{m.group(2)}', t)
    t, n2 = ITEM.subn(lambda m: f'{m.group(1)}{SITE}/{lang}/{m.group(2)}', t)
    # 隐私政策、服务条款：非中文页指向各自语言的法律页（scripts/legal_pages.py 生成，必须先生成再运行本脚本，否则 check_topics 报站内链接失效）
    t, n3 = LEGAL.subn(lambda m: f'{m.group(1)}/{lang}/{m.group(2)}{m.group(3)}', t)
    return t, n1 + n3, n2


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    tot1 = tot2 = files = 0
    for lang in LANGS:
        for f in sorted(glob.glob(os.path.join(ROOT, lang, 'models', '*.html'))):
            t = io.open(f, encoding='utf-8').read()
            t2, n1, n2 = convert(t, lang)
            if t2 != t:
                files += 1
                tot1 += n1
                tot2 += n2
                if not dry:
                    io.open(f, 'w', encoding='utf-8', newline='\n').write(t2)
    print(('将修改' if dry else '已修改'), files, '页；链接', tot1, '处；面包屑 item', tot2, '处')
