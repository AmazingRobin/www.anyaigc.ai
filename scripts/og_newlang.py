"""分享图新语言（ja / ko / es / de）与英文重出的共用部分：词表、Chrome headless 截图、版面自检。

用法（在 og_jev.py / og_spark.py / og_hy4.py / og_hy4_flash.py / og_muse.py 里 import）：
    python scripts/og_xxx.py --langs=ja,ko,es,de [--only=slug1,slug2]
    python scripts/og_xxx.py --langs=en
截图前先用 JS 量 DOM（Range / getBoundingClientRect）：标题、副标题、标签必须都在画面内、不压到装饰图、
标签之间间距 >= 8px 且不重叠；违例就整体缩小字号（每次 x0.93，最多 14 次）再量，仍违例则不出图并报错。
需要先启动 python scripts/preview.py（http://localhost:8765）。
"""
import glob
import json
import os
import re
import subprocess

NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
ENT_EN = 'Self-service invoices'  # 英文图海外口径；中文图的「对公 · 专票」由各脚本自己保留


def L(ja, ko, es, de):
    return dict(ja=ja, ko=ko, es=es, de=de)


# 通用标签词表，键是英文图上的原文；缺词直接 KeyError，不回退英文
WORDS = {
    'Unlimited concurrency': L('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    'Unlimited RPM': L('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    ENT_EN: L('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
    'Free output': L('出力は無料', '출력 무료', 'Salida gratuita', 'Ausgabe kostenlos'),
    'Image input': L('画像入力', '이미지 입력', 'Entrada de imágenes', 'Bildeingabe'),
    '1M context': L('コンテキスト長1M', '1M 컨텍스트', '1M de contexto', '1M Kontext'),
    '256k context': L('コンテキスト長256k', '256k 컨텍스트', '256k de contexto', '256k Kontext'),
    'Native audio': L('ネイティブ音声', '네이티브 오디오', 'Audio nativo', 'Natives Audio'),
}
# 「$X / 1M input」句式（英文图没有 from 就不加 から/부터/desde/ab），{p} 为已带 $ 的价格
PRICE_IN = L('入力 100万トークン {p}', '입력 100만 토큰 {p}', '{p} / 1M de entrada', '{p} / 1 Mio. Eingabe')

FONT_CSS = '''<style>
html[lang=ja] body,html[lang=ja] body :not(svg):not(svg *):not(.bar):not(.bar *){font-family:"Yu Gothic UI","Meiryo","Segoe UI",Arial,sans-serif !important}
html[lang=ko] body,html[lang=ko] body :not(svg):not(svg *):not(.bar):not(.bar *){font-family:"Malgun Gothic","Segoe UI",Arial,sans-serif !important}
html[lang=ko] body{word-break:keep-all}
</style>'''

FIT_JS = '''<script>(function(){
var C=__CFG__;
function all(s){return Array.prototype.slice.call(document.querySelectorAll(s))}
function fs(e){return parseFloat(getComputedStyle(e).fontSize)}
// 水平取文字范围（块级元素的盒子比文字宽），垂直取元素盒（Range 的高度是字体内容区，比 line-height 高，会误报重叠）
function trect(e){var r=document.createRange();r.selectNodeContents(e);var a=r.getBoundingClientRect(),b=e.getBoundingClientRect();return {left:a.left,right:a.right,top:b.top,bottom:b.bottom}}
function hit(a,b,p){return a.left<b.right+p&&b.left<a.right+p&&a.top<b.bottom+p&&b.top<a.bottom+p}
// 缩放分组：scale 里每个选择器各一组，标签（chips）合成一组；只缩小出问题的那一组
var groups={},order=[];
// scale 的每一项是一个选择器或选择器数组，各自成一组；chips 合成一组
C.scale.forEach(function(s){var ss=[].concat(s),els=[];ss.forEach(function(x){els=els.concat(all(x))});groups[ss.join(',')]={els:els,k:1};order.push(ss.join(','))});
groups.chips={els:[],k:1};C.chips.forEach(function(s){groups.chips.els=groups.chips.els.concat(all(s))});order.push('chips');
order.forEach(function(g){groups[g].base=groups[g].els.map(fs)});
// 先精确匹配，再看包含关系（元素在组内或组内元素在它里面）
function gOf(e){for(var i=0;i<order.length;i++){if(groups[order[i]].els.indexOf(e)>=0)return order[i]}
 for(var i=0;i<order.length;i++){if(groups[order[i]].els.some(function(x){return x.contains(e)||e.contains(x)}))return order[i]}return null}
function bad(){
 var o=[],obs=[],items=[];
 C.obst.forEach(function(s){all(s).forEach(function(e){obs.push(e.getBoundingClientRect())})});
 C.check.forEach(function(s){all(s).forEach(function(e){items.push({e:e,r:trect(e),chip:0})})});
 groups.chips.els.forEach(function(e){items.push({e:e,r:e.getBoundingClientRect(),chip:1})});
 items.forEach(function(it){var r=it.r,n=it.e.textContent.trim().slice(0,14),g=it.chip?'chips':gOf(it.e);
  if(r.left<0||r.top<0||r.right>C.max[0]||r.bottom>C.max[1])o.push({m:'out:'+n,g:g});
  if(it.e.scrollWidth>it.e.clientWidth+1)o.push({m:'clip:'+n,g:g});
  obs.forEach(function(b){if(hit(r,b,0))o.push({m:'obst:'+n,g:g})})});
 for(var i=0;i<items.length;i++)for(var j=i+1;j<items.length;j++){var a=items[i],b=items[j];
  if(a.e.contains(b.e)||b.e.contains(a.e))continue;
  var cc=a.chip&&b.chip;
  if(hit(a.r,b.r,cc?7.9:2))o.push({m:(cc?'gap:':'overlap:')+a.e.textContent.trim().slice(0,10)+'|'+b.e.textContent.trim().slice(0,10),g:cc?'chips':(a.chip?gOf(b.e):gOf(a.e))})}
 return o}
var n=0;
while(bad().length&&n<14){n++;var seen={};bad().forEach(function(v){if(v.g&&!seen[v.g]){seen[v.g]=1;var g=groups[v.g];g.k*=.93;g.els.forEach(function(e,i){e.style.fontSize=(g.base[i]*g.k).toFixed(2)+'px'})}});
 if(!Object.keys(seen).length)break}
var sc={};order.forEach(function(g){sc[g]=+groups[g].k.toFixed(3)});
document.body.setAttribute('data-fit',JSON.stringify({scale:sc,steps:n,bad:bad().map(function(v){return v.m})}));
})()</script>'''


def money(amount, lang):
    """各语言小数一律用点；一律美元。amount 不带 $。"""
    return '$' + amount


def word(key, lang, extra=None):
    """查词表；extra 是脚本自己的词表。缺词直接 KeyError。"""
    table = extra if extra is not None and key in extra else WORDS
    return table[key][lang]


def parse_args(argv, slugs):
    """返回 (langs 或 None, only 或 None, html_only)。"""
    langs = only = None
    for a in argv[1:]:
        if a.startswith('--langs='):
            langs = tuple(a.split('=', 1)[1].split(','))
        elif a.startswith('--only='):
            only = a.split('=', 1)[1].split(',')
    for lang in langs or ():
        if lang not in LANGATTR:
            raise SystemExit('未知语言: ' + lang)
        if lang == 'zh':
            raise SystemExit('zh 图不在这里重出（保持原样）')
    if only:
        miss = [s for s in only if s not in slugs]
        if miss:
            raise SystemExit('--only 里有未知 slug: ' + ','.join(miss))
    return langs, only, '--html-only' in argv


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def prepare(html, lang, cfg):
    """注入字体、新语言 .n 类和自检脚本。"""
    html = html.replace('</head>', FONT_CSS + '</head>', 1)
    if lang in NEW:
        html = html.replace('<body', '<body class="n"', 1)
    return html.replace('</body>', FIT_JS.replace('__CFG__', json.dumps(cfg)) + '</body>', 1)


def shoot(jobs, root, out_dir, url_dir, cfg, html_only=False):
    """jobs: [(slug, lang, html)]。写临时 HTML、自检、截图到 assets/og/<slug>-<lang>.png，最后删临时 HTML。"""
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for slug, lang, html in jobs:
        p = os.path.join(out_dir, f'{slug}-{lang}.html')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(prepare(html, lang, cfg))
        paths.append(p)
    exe = chrome()
    if html_only:
        print('只写了临时 HTML：', out_dir)
        return
    if not exe:
        raise SystemExit('找不到 Playwright 的 Chromium，无法截图')
    fails, shrunk = [], []
    flags = [exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800', '--virtual-time-budget=6000']
    try:
        for (slug, lang, _), p in zip(jobs, paths):
            png = os.path.join(root, 'assets', 'og', f'{slug}-{lang}.png')
            url = f'http://localhost:8765/{url_dir}/{slug}-{lang}.html'
            dom = subprocess.run(flags + ['--dump-dom', url], capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
            m = re.search(r"data-fit='([^']*)'|data-fit=\"([^\"]*)\"", dom)
            fit = (m.group(1) or m.group(2)).replace('&quot;', '"') if m else 'NO-REPORT'
            ok = '"bad":[]' in fit
            if not ok:
                fails.append(f'{slug}-{lang}')
                print('SKIP', f'{slug}-{lang}', 'fit', fit, '<-- 违例，不出图')
                continue
            subprocess.run(flags + [f'--screenshot={png}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
            if json.loads(fit)['steps']:
                shrunk.append(f'{slug}-{lang}')
            print('png', os.path.relpath(png, root).replace('\\', '/'), os.path.getsize(png), 'fit', fit)
    finally:
        for p in paths:
            if os.path.exists(p):
                os.unlink(p)
        try:
            os.rmdir(out_dir)
        except OSError:
            pass
    print(f'缩小字号 {len(shrunk)} 张:', ' '.join(shrunk) or '无')
    if fails:
        raise SystemExit('版面自检未通过: ' + ', '.join(fails))
