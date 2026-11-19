# 2026-11-18 用户确认的三项译法，批量应用到 DeepSeek 试点的译文（out/ 里的 JSON），之后要 tm-save 再 render。
#   1. 韩语：微信支付、支付宝用英文原名 WeChat Pay / Alipay（不音译）
#   2. 西语：Business 译 Negocios，和 Enterprise 的 Empresas 区分开
#   3. 日语：原文没有 about / ~ 的地方不加「約」（"Save 60%" 就是 60%）
# 以后每个系列的简报里都写进这三条，新系列翻译时直接遵守，不用再跑这个脚本。
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEDGE = re.compile(r'about|approx|roughly|~|around|nearly', re.I)


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def save(p, data):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(data, ensure_ascii=False, indent=1))


def main():
    series = sys.argv[1]
    d = os.path.join(ROOT, 'drafts', 'i18n', series)
    items = {i['id']: i for i in load(os.path.join(d, 'union.json'))}
    stat = {'ko': 0, 'es': 0, 'ja': 0}
    for f in sorted(glob.glob(os.path.join(d, 'out', '*-*.json'))):
        lang = os.path.basename(f).split('-')[0]
        if lang not in stat:
            continue
        data = load(f)
        for it in data:
            src = items.get(it['id'], {}).get('text', '')
            t = it['text']
            new = t
            if lang == 'ko':
                new = re.sub(r'위챗\s?페이', 'WeChat Pay', new)
                new = re.sub(r'알리\s?페이', 'Alipay', new)
            elif lang == 'es':
                if src.startswith('Business ') or src == 'Business':
                    new = re.sub(r'^Empresas', 'Negocios', new)
            elif lang == 'ja':
                if not HEDGE.search(src):
                    new = re.sub(r'約\s?(\d+(?:\.\d+)?\s?[%％])', lambda m: m.group(1), new)
            if new != t:
                it['text'] = new
                stat[lang] += 1
        save(f, data)
    print('已改动的译文条数:', stat)


if __name__ == '__main__':
    main()
