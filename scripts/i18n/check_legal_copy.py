# -*- coding: utf-8 -*-
"""检查隐私政策、服务协议的译文 scripts/legal_copy/<lang>.json 是否和 src.json 对得上。
用法：python scripts/i18n/check_legal_copy.py <lang>...        例：python scripts/i18n/check_legal_copy.py en ja
ERROR 必须为 0；WARN 由复核人判断。检查：每个单元都有译文、没有多余键、HTML 标签和实体不变、没有残留汉字（日语除外）、
品牌名大小写、数字是否保留、日期和版本号、title / description 长度、目录标题和正文标题一致、没有和原文逐字相同的整句。
"""
import io
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HAN = re.compile(r'[一-鿿]')
CJK_PUNCT = re.compile(r'[「」『』（）、，。：；！？]')
BAD_CASE = re.compile(r'ANYAIGC|Anyaigc|anyAIGC|AnyAigc')
TITLE_MAX = {'en': 65, 'ja': 64, 'ko': 64, 'es': 65, 'de': 65}
DESC_RANGE = {'en': (120, 160), 'ja': (60, 240), 'ko': (60, 240), 'es': (120, 160), 'de': (120, 160)}


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)


def tags(s):
    return [re.sub(r'\s+', ' ', t) for t in re.findall(r'</?[a-zA-Z][^>]*>|&[a-z]+;', s)]


def digits(s):
    return sorted(re.findall(r'\d+(?:\.\d+)?', s))


def check(lang):
    errs, warns = [], []
    src = json.load(io.open(os.path.join(ROOT, 'scripts', 'legal_copy', 'src.json'), encoding='utf-8'))
    p = os.path.join(ROOT, 'scripts', 'legal_copy', lang + '.json')
    if not os.path.exists(p):
        return [f'{lang}: 文件不存在 {p}'], []
    try:
        tr = json.load(io.open(p, encoding='utf-8'))
    except ValueError as ex:
        return [f'{lang}: JSON 读取失败 {ex}'], []
    for page in ('privacy', 'terms'):
        su = {u['id']: u for u in src[page]}
        tu = tr.get(page, {})
        miss, extra = sorted(set(su) - set(tu)), sorted(set(tu) - set(su))
        if miss:
            errs.append(f'{page}: 缺少 {len(miss)} 个单元 {miss[:6]}')
        if extra:
            errs.append(f'{page}: 多出 {len(extra)} 个键 {extra[:6]}')
        for i, u in su.items():
            v = tu.get(i)
            if v is None:
                continue
            if not isinstance(v, str) or not v.strip():
                errs.append(f'{page}.{i}: 空值')
                continue
            if tags(u['text']) != tags(v):
                errs.append(f'{page}.{i}: HTML 标签或实体被改动 {tags(u["text"])[:3]} / {tags(v)[:3]}')
            if lang != 'ja' and HAN.search(v):
                errs.append(f'{page}.{i}: 残留汉字 {HAN.search(v).group(0)!r}：{v[:40]!r}')
            if CJK_PUNCT.search(v) and lang not in ('ja', 'ko'):
                errs.append(f'{page}.{i}: 含中文标点 {v[:40]!r}')
            if BAD_CASE.search(v):
                errs.append(f'{page}.{i}: 品牌名大小写应为 AnyAIGC')
            if u['text'] == v and len(u['text']) > 12 and not re.fullmatch(r'[A-Za-z0-9 &;./:_-]+', u['text']):
                errs.append(f'{page}.{i}: 和中文原文逐字相同（漏译）{v[:30]!r}')
            if 'AnyAIGC' in u['text'] and 'AnyAIGC' not in v and len(u['text']) < 40:
                warns.append(f'{page}.{i}: 原文有 AnyAIGC，译文没有：{v[:40]!r}')
            ds, dt = digits(u['text']), digits(v)
            if ds != dt and not re.search(r'\d{4}\s*年', u['text']):
                warns.append(f'{page}.{i}: 数字不一致 {ds} / {dt}：{v[:50]!r}')
        # 标题、描述
        t0 = tu.get('u0', '')
        if t0:
            w = width(t0) if lang in ('ja', 'ko') else len(t0)
            if w > TITLE_MAX[lang]:
                errs.append(f'{page}: title 太长 {w} > {TITLE_MAX[lang]}')
            if 'AnyAIGC' not in t0:
                errs.append(f'{page}: title 里要有 AnyAIGC')
        if page == 'privacy':
            d = tu.get('u1', '')
            lo, hi = DESC_RANGE[lang]
            dl = width(d) if lang in ('ja', 'ko') else len(d)
            if d and not lo <= dl <= hi:
                errs.append(f'privacy: description 长度 {dl} 不在 {lo}–{hi}')
        # 目录标题与正文标题一致：目录里的每一条都应该在正文标题里出现
        heads = [(i, tu[i]) for i in tu if su.get(i, {}).get('text', '').startswith(('一、', '二、', '三、', '四、', '五、', '六、', '七、', '八、', '九、', '十'))
                 or re.match(r'^\d+\. ', su.get(i, {}).get('text', ''))]
        seen = {}
        for i, v in heads:
            seen.setdefault(re.sub(r'^\s*\d+[.、]\s*', '', v).strip(), []).append(i)
        for k, ids in seen.items():
            if len(ids) < 2:
                warns.append(f'{page}: 目录/正文标题只出现一次，检查是否对得上：{k[:40]!r} {ids}')
        txt = json.dumps(tu, ensure_ascii=False)
        if page == 'privacy' and not re.search(r'1\.1', txt):
            errs.append('privacy: 缺少版本号 1.1')
        if not re.search(r'2026', txt):
            errs.append(f'{page}: 缺少生效日期 2026')
    return errs, warns


if __name__ == '__main__':
    langs = sys.argv[1:] or ['en', 'ja', 'ko', 'es', 'de']
    bad = 0
    for lang in langs:
        e, w = check(lang)
        for x in e:
            print(f'ERROR [{lang}] {x}')
        for x in w[:25]:
            print(f'WARN  [{lang}] {x}')
        print(f'{lang}: {len(e)} 个错误，{len(w)} 个提醒')
        bad += len(e)
    sys.exit(1 if bad else 0)
