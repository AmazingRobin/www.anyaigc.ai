# 西语、德语页面的数字统一用小数点（2026-11-23 用户确认：价格、百分比等小数都写 0.0596，不写 0,0596）。
# 只改「译文里新出现的小数逗号」：
#   - 英文源页里本来就有的写法（1,048,576 / 10,000 这种千分位）原样保留；
#   - 只处理文本节点和 content / alt / title / aria-label 属性，style、svg path、script、pre、code 不动；
#   - JSON-LD 只改字符串值里的数字。
# 三种目标：
#   python scripts/i18n/decimal_point.py html [--dry-run]    已渲染的 es/de 专题页
#   python scripts/i18n/decimal_point.py series [--dry-run]  drafts/i18n/<系列>/out/<lang>-all.json（下次重渲染不会变回去）
#   python scripts/i18n/decimal_point.py tm [--dry-run]      drafts/i18n/<系列>/tm-<lang>.json（翻译记忆库）
# 重复运行安全：改过的不会再匹配。
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LANGS = ('es', 'de')
# 小数逗号：前面不能是字母、数字、点、逗号；后面不能再跟数字或「,数字」（排除 1,048,576 这类千分位链）
DEC = re.compile(r'(?<![\w.,])(\d+),(\d+)(?!\d|,\d)')
PROTECTED = re.compile(r'(<details class="lang-menu.*?</details>|<style\b.*?</style>|<pre\b.*?</pre>|<code\b.*?</code>|'
                       r'<script(?![^>]*ld\+json)\b.*?</script>)', re.S)
LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
ATTR = re.compile(r'(\b(?:content|alt|title|aria-label)=")([^"]*)(")')
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')


def en_tokens(text):
    return {m.group(0) for m in DEC.finditer(text)}


def conv(text, keep):
    n = [0]

    def sub(m):
        if m.group(0) in keep:
            return m.group(0)
        n[0] += 1
        return m.group(1) + '.' + m.group(2)
    return DEC.sub(sub, text), n[0]


def conv_html(html, keep):
    total = 0
    out = []
    for part in PROTECTED.split(html):
        if PROTECTED.fullmatch(part or ''):
            out.append(part)
            continue
        # JSON-LD：只改字符串值
        def ld_sub(m):
            nonlocal total

            def s_sub(sm):
                nonlocal total
                v, c = conv(sm.group(1), keep)
                total += c
                return '"' + v + '"'
            body = STR.sub(s_sub, m.group(2))
            return m.group(1) + body + m.group(3)
        chunks = LD.split(part)
        # LD.split 带 3 个捕获组：[前, 开标签, 内容, 闭标签, 中, ...]
        res = []
        i = 0
        while i < len(chunks):
            if i % 4 == 0:
                seg = chunks[i]
                pieces = re.split(r'(<[^>]*>)', seg)
                for k, p in enumerate(pieces):
                    if k % 2 == 1:  # 标签：只改允许的属性
                        def a_sub(am):
                            nonlocal total
                            v, c = conv(am.group(2), keep)
                            total += c
                            return am.group(1) + v + am.group(3)
                        pieces[k] = ATTR.sub(a_sub, p)
                    else:
                        v, c = conv(p, keep)
                        total += c
                        pieces[k] = v
                res.append(''.join(pieces))
                i += 1
            else:
                block = chunks[i] + chunks[i + 1] + chunks[i + 2]
                res.append(ld_sub(re.fullmatch(r'(<script type="application/ld\+json">)(.*?)(</script>)', block, re.S)))
                i += 3
        out.append(''.join(res))
    return ''.join(out), total


def run_html(dry):
    grand = 0
    changed = 0
    for lang in LANGS:
        for f in sorted(glob.glob(os.path.join(ROOT, lang, 'models', '*.html'))):
            slug = os.path.basename(f)[:-5]
            if slug == 'index':
                continue
            ep = os.path.join(ROOT, 'en', 'models', slug + '.html')
            keep = en_tokens(io.open(ep, encoding='utf-8').read()) if os.path.exists(ep) else set()
            src = io.open(f, encoding='utf-8').read()
            new, c = conv_html(src, keep)
            for blk in LD.findall(new):
                json.loads(blk[1])  # 结构化数据必须仍是合法 JSON
            if c:
                grand += c
                changed += 1
                if not dry:
                    io.open(f, 'w', encoding='utf-8', newline='\n').write(new)
    print(f'html: {"将改" if dry else "已改"} {grand} 处，{changed} 页')


def series_dirs():
    return [d for d in sorted(glob.glob(os.path.join(ROOT, 'drafts', 'i18n', '*'))) if os.path.exists(os.path.join(d, 'union.json'))]


def run_series(dry):
    grand = 0
    for d in series_dirs():
        union = {x['id']: x['text'] for x in json.load(io.open(os.path.join(d, 'union.json'), encoding='utf-8'))}
        for lang in LANGS:
            p = os.path.join(d, 'out', f'{lang}-all.json')
            if not os.path.exists(p):
                continue
            data = json.load(io.open(p, encoding='utf-8'))
            c = 0
            for x in data:
                src = union.get(x['id'], '')
                new, k = conv(x['text'], en_tokens(src))
                if k:
                    x['text'] = new
                    c += k
            if c and not dry:
                io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(data, ensure_ascii=False, indent=1))
            grand += c
    print(f'series all.json: {"将改" if dry else "已改"} {grand} 处')


def run_tm(dry):
    grand = 0
    for d in series_dirs():
        for lang in LANGS:
            p = os.path.join(d, f'tm-{lang}.json')
            if not os.path.exists(p):
                continue
            data = json.load(io.open(p, encoding='utf-8'))
            c = 0
            for k, v in list(data.items()):
                en = k.split('\x1f', 1)[-1]
                new, n = conv(v, en_tokens(en))
                if n:
                    data[k] = new
                    c += n
            if c and not dry:
                io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(data, ensure_ascii=False, indent=1))
            grand += c
    print(f'tm: {"将改" if dry else "已改"} {grand} 处')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    dry = '--dry-run' in sys.argv
    {'html': run_html, 'series': run_series, 'tm': run_tm}[mode](dry)
