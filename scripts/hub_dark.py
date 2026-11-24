# 专题首页换深色新风格的一次性改动（可重复运行，结果不变）：
#   <html> 加 data-scrollbar="dark"；顶栏品牌改 logo 图片；hub.css 版本号。
# 只动这三处，不碰任何可见文字、卡片、链接、JSON-LD。
import io
import re
import sys

LANGS = ('zh', 'en', 'ja', 'ko', 'es', 'de')
HUB_V = sys.argv[1] if len(sys.argv) > 1 else '20261123d'
BRAND = ('<a class="af-brand" href="{h}" aria-label="AnyAIGC">'
         '<img src="/assets/home/logo.webp?v=20261123d" width="102" height="42" alt="AnyAIGC"></a>')

for lang in LANGS:
    p = f'{lang}/models/index.html'
    with io.open(p, encoding='utf-8', newline='') as f:
        s = f.read()
    o = s
    s = re.sub(r'<html lang="([^"]+)"(?! data-scrollbar)', r'<html lang="\1" data-scrollbar="dark"', s, count=1)
    s = re.sub(r'<a class="af-brand" href="([^"]*)">AnyAIGC</a>', lambda m: BRAND.format(h=m.group(1)), s, count=1)
    s = re.sub(r'(/assets/models/hub\.css\?v=)[0-9a-z]+', r'\g<1>' + HUB_V, s)
    if s != o:
        with io.open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(s)
    print(lang, 'changed' if s != o else 'same')
