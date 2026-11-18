# 一个系列的翻译批次：把多个页面的翻译单元合并去重，分块交给翻译，再拆回每个页面。
# 用法：
#   python scripts/i18n/batch.py prepare <series> <slug>...     合并去重，写 drafts/i18n/<series>/union.json 和 chunks/
#   python scripts/i18n/batch.py merge <series> <lang> <slug>... 把 drafts/i18n/<series>/out/<lang>-*.json 拆回各页面的 <lang>.json
# 同一句话在多个页面里只翻译一次，全系列用词自然一致。
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import htmlseg as H
import build as B

ROOT = B.ROOT
DRAFT = B.DRAFT
CHUNK_CHARS = 9000      # 每块的原文字符数上限（约 60–90 个单元），保证单个翻译任务读得完、写得完


def role_of(s):
    if s.kind == 'attr':
        return s.meta.get('attr', 'attr')
    return 'text'


def page_units(slug):
    src = io.open(os.path.join(ROOT, 'en', 'models', slug + '.html'), encoding='utf-8').read()
    spans = H.collect(src)
    out = []
    for i, s in enumerate(spans):
        if s.kind == 'ldjson':
            data, paths = H.ld_strings(s.text)
            for j, (p, v) in enumerate(paths):
                out.append((f'ld{j}', v, 'ld:' + str(p[-1])))
        else:
            r = role_of(s)
            if r == 'text' and re.search(r'<title\b', src[max(0, s.s - 10):s.s]):
                r = 'title'
            out.append((f'u{i}', s.text, r))
    return out


def prepare(series, slugs):
    union, order = {}, []
    for slug in slugs:
        for uid, text, role in page_units(slug):
            k = (text, role)
            if k not in union:
                union[k] = {'text': text, 'role': role, 'pages': []}
                order.append(k)
            union[k]['pages'].append(slug)
    items = []
    for n, k in enumerate(order):
        v = union[k]
        items.append({'id': f'k{n}', 'text': v['text'], 'role': v['role'], 'pages': len(v['pages'])})
    d = os.path.join(DRAFT, series)
    os.makedirs(os.path.join(d, 'chunks'), exist_ok=True)
    os.makedirs(os.path.join(d, 'out'), exist_ok=True)
    io.open(os.path.join(d, 'union.json'), 'w', encoding='utf-8', newline='\n').write(
        json.dumps(items, ensure_ascii=False, indent=1))
    for old in glob.glob(os.path.join(d, 'chunks', '*.json')):
        os.remove(old)
    chunks, cur, size = [], [], 0
    for it in items:
        # 标题/描述/关键词放在同一块里，译者能一起把握长度和关键词
        if cur and size + len(it['text']) > CHUNK_CHARS:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(it)
        size += len(it['text'])
    if cur:
        chunks.append(cur)
    for i, c in enumerate(chunks):
        io.open(os.path.join(d, 'chunks', f'{i:02d}.json'), 'w', encoding='utf-8', newline='\n').write(
            json.dumps(c, ensure_ascii=False, indent=1))
    total = sum(len(i['text']) for i in items)
    raw = sum(len(t) for s in slugs for _, t, _ in page_units(s))
    print(f'{series}: {len(slugs)} 页，合并后 {len(items)} 个单元（去重前 {sum(len(page_units(s)) for s in slugs)}），'
          f'{total} 字符（去重前 {raw}），分 {len(chunks)} 块')


def merge(series, lang, slugs):
    d = os.path.join(DRAFT, series)
    items = json.load(io.open(os.path.join(d, 'union.json'), encoding='utf-8'))
    tr = {}
    for f in sorted(glob.glob(os.path.join(d, 'out', f'{lang}-*.json'))):
        for it in json.load(io.open(f, encoding='utf-8')):
            tr[it['id']] = it['text']
    miss = [i['id'] for i in items if i['id'] not in tr]
    if miss:
        raise SystemExit(f'{series}/{lang} 缺 {len(miss)} 条译文：{miss[:10]}')
    by = {(i['text'], i['role']): tr[i['id']] for i in items}
    for slug in slugs:
        units, ld = {}, {}
        for uid, text, role in page_units(slug):
            (ld if uid.startswith('ld') else units)[uid] = by[(text, role)]
        os.makedirs(os.path.join(DRAFT, slug), exist_ok=True)
        io.open(os.path.join(DRAFT, slug, f'{lang}.json'), 'w', encoding='utf-8', newline='\n').write(
            json.dumps({'units': units, 'ld': ld}, ensure_ascii=False, indent=1))
    print(f'{series}/{lang}: 已拆回 {len(slugs)} 个页面')


def _norm_num(t):
    t = re.sub(r'(?<=\d)[  ](?=\d{3}\b)', '', t)           # 千分位（窄不换行空格）
    return re.sub(r'(?<=\d),(?=\d)', '.', t)                              # 小数逗号 → 小数点


def _decimals(t):
    return set(re.findall(r'\d+\.\d+', _norm_num(re.sub(r'<[^>]+>', ' ', t))))


def _tags(t):
    return re.findall(r'</?[a-zA-Z][^>]*>', t)


CJK = re.compile(r'[一-鿿぀-ヿ가-힯]')
HAN = re.compile(r'[一-鿿]')
KANA = re.compile(r'[぀-ヿ]')
HANGUL = re.compile(r'[가-힯]')


def validate(series, lang, only=None):
    """逐块检查译文：返回 (errors, warnings)。errors 必须修；warnings 由人/复核代理判断。"""
    d = os.path.join(DRAFT, series)
    errs, warns = [], []
    files = sorted(glob.glob(os.path.join(d, 'chunks', '*.json')))
    got = {}
    outs = sorted(glob.glob(os.path.join(d, 'out', f'{lang}-*.json')))
    if not outs:
        errs.append(f'{lang}: out/ 下没有译文文件')
    for of in outs:
        try:
            for o in json.load(io.open(of, encoding='utf-8')):
                got[o['id']] = o['text']
        except (ValueError, KeyError, TypeError) as e:
            errs.append(f'{os.path.basename(of)}: 读取失败 {e}')
    for cf in files:
        n = os.path.basename(cf)
        if only and n != only:
            continue
        src = json.load(io.open(cf, encoding='utf-8'))
        lack = [i['id'] for i in src if i['id'] not in got]
        if lack:
            errs.append(f'{lang}-{n}: 缺 {len(lack)} 条译文 {lack[:6]}')
            continue
        for it in src:
            t, o, rid = it['text'], got[it['id']], it['id']
            if not isinstance(o, str) or not o.strip():
                errs.append(f'{lang}-{n} {rid}: 译文为空')
                continue
            if _tags(t) != _tags(o):
                errs.append(f'{lang}-{n} {rid}: 标签结构被改动 原 {_tags(t)[:4]} 译 {_tags(o)[:4]}')
            if t.count('{{') != o.count('{{'):
                errs.append(f'{lang}-{n} {rid}: 占位符数量不对')
            miss = _decimals(t) - _decimals(o)
            if miss:
                errs.append(f'{lang}-{n} {rid}: 价格/小数丢失或改动 {sorted(miss)}（德语、西语可用小数逗号，其余必须同数字）')
            for ent in ('&amp;', '&lt;', '&gt;'):
                if t.count(ent) != o.count(ent):
                    errs.append(f'{lang}-{n} {rid}: 实体 {ent} 数量不一致')
            for code in re.findall(r'<code[^>]*>(.*?)</code>', t, re.S):
                if code not in o:
                    errs.append(f'{lang}-{n} {rid}: <code> 内容被改动 {code[:40]!r}')
            if lang == 'ja' and (HANGUL.search(o)):
                errs.append(f'{lang}-{n} {rid}: 日语里出现韩文')
            if lang == 'ko' and (KANA.search(o) or HAN.search(o)):
                errs.append(f'{lang}-{n} {rid}: 韩语里出现假名或汉字')
            if lang in ('es', 'de') and CJK.search(o):
                errs.append(f'{lang}-{n} {rid}: 出现中日韩字符')
            body = re.sub(r'<[^>]+>|&[#a-zA-Z0-9]+;|\{\{\d+\}\}', ' ', t)
            if len(re.findall(r'[A-Za-z]{3,}', body)) >= 5 and o.strip() == t.strip() and it['role'] not in ('ld:name',):
                warns.append(f'{lang}-{n} {rid}: 与原文完全相同（漏译？） {t[:50]!r}')
            if it['role'] == 'title':
                w = sum(2 if CJK.search(c) else 1 for c in o)
                lim = 64 if lang in ('ja', 'ko') else 65
                if w > lim:
                    warns.append(f'{lang}-{n} {rid}: 标题宽度 {w} > {lim}：{o}')
            if it['role'] == 'meta:description':
                w = sum(2 if CJK.search(c) else 1 for c in o)
                lo, hi = (60, 240) if lang in ('ja', 'ko') else (120, 160)
                if not lo <= w <= hi:
                    warns.append(f'{lang}-{n} {rid}: description 宽度 {w}，建议 {lo}–{hi}')
    return errs, warns


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prepare':
        prepare(sys.argv[2], sys.argv[3:])
    elif cmd == 'merge':
        merge(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif cmd == 'tm-fill':
        # 用翻译记忆库（drafts/i18n/<series>/tm-<lang>.json，键 = role + 0x1f + 原文）按原文文本回填，
        # 写出 out/<lang>-tm.json（新编号），没覆盖的条目写入 delta-<lang>.json 等待补译。
        series, lang = sys.argv[2], sys.argv[3]
        d = os.path.join(DRAFT, series)
        items = json.load(io.open(os.path.join(d, 'union.json'), encoding='utf-8'))
        tm = json.load(io.open(os.path.join(d, f'tm-{lang}.json'), encoding='utf-8'))
        for old in glob.glob(os.path.join(d, 'out', f'{lang}-*.json')):
            os.remove(old)
        hit, miss = [], []
        for it in items:
            k = it['role'] + chr(31) + it['text']
            (hit if k in tm else miss).append({'id': it['id'], 'text': tm[k]} if k in tm else it)
        io.open(os.path.join(d, 'out', f'{lang}-tm.json'), 'w', encoding='utf-8', newline='\n').write(
            json.dumps(hit, ensure_ascii=False, indent=1))
        io.open(os.path.join(d, f'delta-{lang}.json'), 'w', encoding='utf-8', newline='\n').write(
            json.dumps(miss, ensure_ascii=False, indent=1))
        print(f'{series}/{lang}: 记忆库命中 {len(hit)} 条，待补译 {len(miss)} 条')
    elif cmd == 'render':
        # 合并译文并回填：每次都先 merge 再 build，保证编号和当前英文源页对得上
        series, lang, slugs = sys.argv[2], sys.argv[3], sys.argv[4:]
        merge(series, lang, slugs)
        for sl in slugs:
            B.build(sl, lang)
    elif cmd == 'validate':
        e, w = validate(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
        for x in e:
            print('ERROR', x)
        for x in w:
            print('WARN ', x)
        print(f'校验完成：{len(e)} 个错误，{len(w)} 个提醒')
        sys.exit(1 if e else 0)
    else:
        raise SystemExit('用法：batch.py prepare <series> <slug>... | batch.py merge <series> <lang> <slug>...')
