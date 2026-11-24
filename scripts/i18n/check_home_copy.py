# -*- coding: utf-8 -*-
"""检查首页文案 scripts/home_copy/<lang>.json 是否和英文源 en.json 对得上。
用法：python scripts/i18n/check_home_copy.py <lang>...        例：python scripts/i18n/check_home_copy.py ja ko
ERROR 必须为 0；WARN 由复核人判断。检查内容：结构（键、数组长度）、固定键、占位符、HTML 标签、
禁用说法（增值税、对公转账、合同、SLA、分组、大陆等）、小数逗号、品牌名大小写、title / description 长度、导航项长度、未翻译的整句。
"""
import io
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXED = {
    'ja': {'lang': 'ja', 'html_lang': 'ja', 'og_locale': 'ja_JP', 'native': '日本語'},
    'ko': {'lang': 'ko', 'html_lang': 'ko', 'og_locale': 'ko_KR', 'native': '한국어'},
    'es': {'lang': 'es', 'html_lang': 'es', 'og_locale': 'es_ES', 'native': 'Español'},
    'de': {'lang': 'de', 'html_lang': 'de', 'og_locale': 'de_DE', 'native': 'Deutsch'},
}
# 允许和英文相同的键路径（品牌名、型号名、标签、数字）
SAME_OK = re.compile(r'^(lang|html_lang|og_locale|native|vendors\[\d+\]|models\.items\[\d+\]\[0\]|tools\.items\[\d+\]\[0\]|'
                     r'why\.cards\[\d+\]\.(tag|big)|ent\.cards\[\d+\]\.tag|stats\[\d+\]\[0\]|ent\.pay\[\d+\]|start\.copy|keywords)$')
BAD = re.compile(r'增值税|增值稅|対公|对公|公対公|VAT|\bIVA\b|MwSt|Mehrwertsteuer|bank transfer|wire transfer|Überweisung|transferencia bancaria|銀行振込|계좌 ?이체|'
                 r'\bSLA\b|可用率|分组|グループ分け|mainland|中国大陆|中国大陸|\bcontrato\b|Vertrag|契約|계약|サービス契約|service agreement', re.I)
BAD_CASE = re.compile(r'ANYAIGC|Anyaigc|anyAIGC|AnyAigc')
HAN = re.compile(r'[一-鿿]')
INVOICE = {'ja': '請求書', 'ko': '인보이스', 'es': 'factura', 'de': 'rechnung'}


def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)


def walk(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, f'{p}.{k}' if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f'{p}[{i}]')
    else:
        yield p, o


def tags(s):
    return re.findall(r'</?[a-zA-Z][^>]*>', s)


def check(lang):
    errs, warns = [], []
    en = json.load(io.open(os.path.join(ROOT, 'scripts', 'home_copy', 'en.json'), encoding='utf-8'))
    pth = os.path.join(ROOT, 'scripts', 'home_copy', lang + '.json')
    if not os.path.exists(pth):
        return [f'{lang}: 文件不存在 {pth}'], []
    try:
        tr = json.load(io.open(pth, encoding='utf-8'))
    except ValueError as ex:
        return [f'{lang}: JSON 读取失败 {ex}'], []
    ea, ta = dict(walk(en)), dict(walk(tr))
    miss, extra = sorted(set(ea) - set(ta)), sorted(set(ta) - set(ea))
    if miss:
        errs.append(f'缺少键 {miss[:8]}（共 {len(miss)}）')
    if extra:
        errs.append(f'多出键 {extra[:8]}（共 {len(extra)}）')
    for k, v in FIXED[lang].items():
        if tr.get(k) != v:
            errs.append(f'固定键 {k} 应为 {v!r}，现在是 {tr.get(k)!r}')
    for p, ev in ea.items():
        tv = ta.get(p)
        if tv is None:
            continue
        if not isinstance(tv, str) or (not tv.strip() and ev.strip()):
            errs.append(f'{p}: 空值或不是字符串')
            continue
        if not ev.strip():
            if tv.strip():
                errs.append(f'{p}: 英文原文是空的，这里也必须留空')
            continue
        if sorted(re.findall(r'\{[a-z]+\}', ev)) != sorted(re.findall(r'\{[a-z]+\}', tv)):
            errs.append(f'{p}: 占位符不一致 {re.findall(r"{[a-z]+}", ev)} / {re.findall(r"{[a-z]+}", tv)}')
        if [re.sub(r'\s+', ' ', t) for t in tags(ev)] != [re.sub(r'\s+', ' ', t) for t in tags(tv)]:
            errs.append(f'{p}: HTML 标签被改动 {tags(ev)[:3]} / {tags(tv)[:3]}')
        if tv == ev and not SAME_OK.match(p) and len(ev) > 12:
            errs.append(f'{p}: 和英文原文完全相同（漏译？）{ev[:50]!r}')
        if re.search(r'\d,\d', tv):
            errs.append(f'{p}: 出现小数逗号，一律用小数点：{tv[:60]!r}')
        if BAD.search(tv) and not BAD_CASE.search(tv):
            errs.append(f'{p}: 含禁用说法 {BAD.search(tv).group(0)!r}')
        if BAD_CASE.search(tv):
            errs.append(f'{p}: 品牌名大小写应为 AnyAIGC')
        if lang != 'ja' and HAN.search(tv):
            errs.append(f'{p}: 含汉字（只有日语页允许）：{HAN.search(tv).group(0)!r}')
        if '\\' in tv or '"' in tv and p == 'term.user_msg':
            errs.append(f'{p}: 示例提问里不能有引号或反斜杠')
    t = ta.get('title', '')
    mx = 64 if lang in ('ja', 'ko') else 65
    if (width(t) if lang in ('ja', 'ko') else len(t)) > mx:
        errs.append(f'title 太长：{width(t) if lang in ("ja", "ko") else len(t)} > {mx}')
    d = ta.get('desc', '')
    lo, hi = (60, 240) if lang in ('ja', 'ko') else (120, 160)
    dl = width(d) if lang in ('ja', 'ko') else len(d)
    if not lo <= dl <= hi:
        errs.append(f'desc 长度 {dl} 不在 {lo}–{hi}')
    if INVOICE[lang] not in d.lower():
        errs.append(f'desc 没有提到自助开票（应含「{INVOICE[lang]}」）')
    for i, n in enumerate(tr.get('nav', [])):
        lim = 8 * 2 if lang in ('ja', 'ko') else 16
        if (width(n) if lang in ('ja', 'ko') else len(n)) > lim:
            warns.append(f'nav[{i}] {n!r} 偏长（手机顶栏会换行）')
    for k in ('login', 'cta_key'):
        if len(tr.get(k, '')) > 20:
            warns.append(f'{k} {tr[k]!r} 偏长')
    h = tr.get('hero', {})
    for k in ('h1a', 'h1b'):
        v = h.get(k, '')
        lim = 24 if lang in ('ja', 'ko') else 26
        if width(v) > lim and lang in ('ja', 'ko') or (lang in ('es', 'de') and len(v) > 26):
            warns.append(f'hero.{k} {v!r} 偏长')
    return errs, warns


if __name__ == '__main__':
    langs = sys.argv[1:] or ['ja', 'ko', 'es', 'de']
    bad = 0
    for lang in langs:
        e, w = check(lang)
        for x in e:
            print(f'ERROR [{lang}] {x}')
        for x in w:
            print(f'WARN  [{lang}] {x}')
        print(f'{lang}: {len(e)} 个错误，{len(w)} 个提醒')
        bad += len(e)
    sys.exit(1 if bad else 0)
