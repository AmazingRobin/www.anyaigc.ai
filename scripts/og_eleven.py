# 生成 Eleven（ElevenLabs）系列专题页分享图（1200×630）：先写 HTML 到 .playwright-mcp/og/，再用无头 Chrome 截图成 assets/og/<slug>-<lang>.png，出完删掉临时 HTML
# 用法：python scripts/og_eleven.py [--langs=en,ja,ko,es,de] [--only=slug1,slug2] [--html-only] [--keep-html]
#   需要 python scripts/preview.py 在 http://localhost:8765 运行；--html-only 只生成 HTML（不截图、不删除）。
#   不带 --langs 时生成 zh、en。zh 图已定稿，只补其他语言时务必写 --langs，不要连带重出 zh。
# 风格跟 assets/models/eleven.css 一致：近白底、黑色大字、官网 v4 橙红 → 绿渐变艺术图（非 v4 型号用灰色流线图）、黑色胶囊价格标签
# logo 读 assets/icons/elevenlabs.svg（lobe-icons，见 scripts/icons.py）
import glob
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eleven_data import PRICE, SLUGS, is_stt  # noqa: E402
from eleven_layout import logo, HERO_IMG  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写，不要转大写

# 英文图是海外口径：发票在控制台自助开具，不写合同 / 对公 / 增值税。zh 图沿用国内口径，不动
ENT = {'zh': '对公 · 专票', 'en': 'Self-service invoices'}
UNIT = {'zh': '/ 万字符', 'en': '/ 10K chars'}
UNIT_STT = {'zh': '/ 秒', 'en': '/ second'}  # Scribe 语音转文字按秒计费
DEAL = {'zh': '约官方 8.1 折', 'en': '19% off list price'}
TAGS = {'zh': '并发不限', 'en': 'Unlimited RPM'}
# 每个页面：标题关键词（接在 Eleven 后面）、一句卖点
PAGES = {
    'eleven-v4': ('v4', {'zh': '旗舰语音合成，有声书与专业配音', 'en': 'Flagship text-to-speech for audiobooks and voiceover'}),
    'eleven-v4-turbo': ('v4 Turbo', {'zh': '低延迟语音合成，适合语音助手', 'en': 'Low-latency text-to-speech for voice agents'}),
    'eleven-v3': ('v3', {'zh': '戏剧化配音，故事与短剧', 'en': 'Dramatic voiceover for stories and short dramas'}),
    'eleven-v3-conversational': ('v3 Conversational', {'zh': '对话语音，口语自然', 'en': 'Conversational speech with a natural tone'}),
    'eleven-multilingual-v2': ('Multilingual v2', {'zh': '长文本稳定，双语混读', 'en': 'Stable long-form and mixed-language reading'}),
    'eleven-flash-v2-5': ('Flash v2.5', {'zh': '超长文本，批量字幕配音', 'en': 'Very long text and bulk subtitle voiceover'}),
    'eleven-flash-v2': ('Flash v2', {'zh': '轻量高速，英语短句播报', 'en': 'Light and fast English announcer'}),
    'eleven-scribe-v3': ('Scribe v3', {'zh': '录音转文字，90+ 种语言', 'en': 'Speech to text for recordings, 90+ languages'}),
    'eleven-scribe-v2': ('Scribe v2', {'zh': '上一代录音转写，90+ 种语言', 'en': 'Previous-gen transcription, 90+ languages'}),
}
assert list(PAGES) == SLUGS

# 新语言（ja / ko / es / de）分享图：Eleven 全部 9 个页面（7 个语音合成 + 2 个 Scribe）。
# 新语言页的发票口径同样是「在控制台自助开具」，标签用 Self-service invoices 的译法（与 og_gpt.py 一致）。
# 术语对照 scripts/i18n/briefs/batch6-misc.md；缺词直接 KeyError，不回退英文。
# 图上出现的词：标题关键词（型号名，如 v3 Conversational，不翻译）、副标题、价格单位、折扣、并发、发票；语言数 / 延迟数字不上图。
NEW_LANGS = ('ja', 'ko', 'es', 'de')
NEW_SLUGS = ('eleven-v4', 'eleven-v4-turbo', 'eleven-v3', 'eleven-v3-conversational', 'eleven-multilingual-v2',
             'eleven-flash-v2-5', 'eleven-flash-v2', 'eleven-scribe-v3', 'eleven-scribe-v2')
UNIT_I18N = {'ja': '/ 1万文字', 'ko': '/ 1만 자', 'es': '/ 10 000 caracteres', 'de': '/ 10.000 Zeichen'}  # 语音合成按 1 万字符计费
UNIT_STT_I18N = {'ja': '/ 秒', 'ko': '/ 초', 'es': '/ segundo', 'de': '/ Sekunde'}
DEAL_I18N = {'ja': '定価から19%オフ', 'ko': '정가 대비 19% 할인', 'es': '19 % menos', 'de': '19 % günstiger'}
TAGS_I18N = {'ja': '同時実行数の上限なし', 'ko': '동시 실행 제한 없음', 'es': 'Sin límite de RPM', 'de': 'Kein RPM-Limit'}
ENT_I18N = {'ja': '請求書を自分で発行', 'ko': '인보이스 직접 발급', 'es': 'Facturas en consola', 'de': 'Rechnungen im Konto'}
SUB_I18N = {
    'eleven-v4': {'ja': 'オーディオブックとナレーション向けの音声合成（TTS）フラッグシップ',
                  'ko': '오디오북과 내레이션용 플래그십 음성 합성(TTS)',
                  'es': 'Síntesis de voz (TTS) insignia para audiolibros y locución',
                  'de': 'Flaggschiff der Sprachsynthese (TTS) für Hörbücher und Voiceover'},
    'eleven-v4-turbo': {'ja': '低レイテンシの音声合成（TTS）、音声アシスタント向け',
                        'ko': '음성 비서용 지연 시간이 짧은 음성 합성(TTS)',
                        'es': 'Síntesis de voz (TTS) de baja latencia para asistentes de voz',
                        'de': 'Sprachsynthese (TTS) mit niedriger Latenz für Sprachassistenten'},
    'eleven-v3': {'ja': '物語やショートドラマ向けのドラマチックなナレーション',
                  'ko': '이야기와 숏드라마를 위한 극적인 내레이션',
                  'es': 'Locución dramática para historias y series cortas',
                  'de': 'Dramatische Sprachausgabe für Geschichten und Kurzdramen'},
    'eleven-v3-conversational': {'ja': '低レイテンシの会話向け音声合成（TTS）、自然な口調',
                                 'ko': '지연 시간이 짧은 대화형 음성 합성(TTS), 자연스러운 말투',
                                 'es': 'Síntesis de voz (TTS) conversacional de baja latencia, tono natural',
                                 'de': 'Dialogorientierte Sprachsynthese (TTS) mit niedriger Latenz'},
    'eleven-multilingual-v2': {'ja': '長文でも安定、二言語が混在するテキストの読み上げ',
                               'ko': '긴 텍스트에도 안정적, 두 언어가 섞인 텍스트 낭독',
                               'es': 'Estable en textos largos y en textos bilingües mezclados',
                               'de': 'Stabil bei langen Texten und zweisprachigen Mischtexten'},
    'eleven-flash-v2-5': {'ja': '非常に長いテキストと字幕音声の一括生成',
                          'ko': '매우 긴 텍스트와 자막 음성 일괄 생성',
                          'es': 'Textos muy largos y locución de subtítulos en lote',
                          'de': 'Sehr lange Texte und Untertitel-Vertonung im Batch'},
    'eleven-flash-v2': {'ja': '軽量で高速、英語の短いセリフ向け音声合成（TTS）',
                        'ko': '가볍고 빠른 영어 짧은 문장용 음성 합성(TTS)',
                        'es': 'Síntesis de voz (TTS) ligera y rápida para frases cortas en inglés',
                        'de': 'Leichte, schnelle Sprachsynthese (TTS) für kurze englische Sätze'},
    'eleven-scribe-v3': {'ja': '録音の音声文字起こし、90以上の言語', 'ko': '녹음 음성 텍스트 변환, 90개 이상 언어',
                         'es': 'Voz a texto para grabaciones, más de 90 idiomas', 'de': 'Sprache-zu-Text für Aufnahmen, 90+ Sprachen'},
    'eleven-scribe-v2': {'ja': '前世代の文字起こし、90以上の言語', 'ko': '이전 세대 음성 텍스트 변환, 90개 이상 언어',
                         'es': 'Transcripción de la generación anterior, más de 90 idiomas', 'de': 'Transkription der Vorgängerversion, 90+ Sprachen'},
}

# 断行：韩语 keep-all 按词换行，日语 auto-phrase 按文节换行（Chrome 119+），避免副标题在词中间折行。
# 版面自检：出图前在页面里用 getBoundingClientRect 量 DOM，有违例就逐步缩小对应字号，到下限仍违例就报错、不出图。
# 规则：标题 / 副标题 / 标签文字都在 0..1200 × 0..630 内；副标题和标签左右另留 80px 边距；标签之间间距 ≥ 8px 且不重叠；
# 副标题与标签行垂直间距 ≥ 16px；标题和副标题不压右侧 logo 方块（留 8px）。
FIT_JS = '''<script>
(function(){
var W=1200,H=630,MX=80,GAP=8,LIM={cf:16,sf:22,hf:56};
function box(r){return {l:r.left,t:r.top,r:r.right,b:r.bottom}}
function R(e){return box(e.getBoundingClientRect())}
function lines(e){var g=document.createRange();g.selectNodeContents(e);return Array.prototype.map.call(g.getClientRects(),box).filter(function(x){return x.r-x.l>0})}
function inb(x,m){return x.l>=0&&x.t>=0&&x.r<=W-(m||0)&&x.b<=H}
function hit(a,b,m){return a.l<b.r+m&&a.r>b.l-m&&a.t<b.b+m&&a.b>b.t-m}
function fs(e){return parseFloat(getComputedStyle(e).fontSize)}
function run(){
var h1=document.querySelector('h1'),p=document.querySelector('.c p'),chips=[].slice.call(document.querySelectorAll('.r span'));
var mark=R(document.querySelector('.mark')),brand=R(document.querySelector('.b'));
var init={hf:fs(h1),sf:fs(p),cf:fs(chips[0])},cur={hf:init.hf,sf:init.sf,cf:init.cf},res={ok:false,msgs:[]};
for(var step=0;step<60;step++){
 var v={},hl=lines(h1),pl=lines(p),cr=chips.map(R);
 hl.forEach(function(x){if(!inb(x)||hit(x,mark,GAP))v.hf=1});
 pl.forEach(function(x){if(!inb(x,MX)||hit(x,mark,GAP))v.sf=1});
 if(Math.max.apply(null,pl.map(function(x){return x.b}))>Math.min.apply(null,cr.map(function(x){return x.t}))-16)v.sf=1;
 cr.forEach(function(x,i){if(!inb(x,MX))v.cf=1});
 for(var i=0;i<cr.length;i++)for(var j=i+1;j<cr.length;j++){var a=cr[i],b=cr[j];
  if(a.t<b.b&&a.b>b.t&&!(a.r+GAP<=b.l||b.r+GAP<=a.l))v.cf=1}
 if(!inb(brand))res.msgs.push('brand out of canvas');
 if(!v.hf&&!v.sf&&!v.cf){res.ok=!res.msgs.length;break}
 var moved=false;
 if(v.hf&&cur.hf>LIM.hf){cur.hf=Math.max(LIM.hf,cur.hf-4);h1.style.fontSize=cur.hf+'px';moved=true}
 if(v.sf&&cur.sf>LIM.sf){cur.sf=Math.max(LIM.sf,cur.sf-1);p.style.fontSize=cur.sf+'px';moved=true}
 if(v.cf&&cur.cf>LIM.cf){cur.cf=Math.max(LIM.cf,cur.cf-1);chips.forEach(function(c){c.style.fontSize=cur.cf+'px'});moved=true}
 if(!moved){res.msgs.push('still violates at limit: '+Object.keys(v).join(','));break}
}
res.init=init;res.cur=cur;res.shrunk=(init.hf!==cur.hf||init.sf!==cur.sf||init.cf!==cur.cf);
res.h1Lines=lines(h1).length;res.subLines=lines(p).length;
res.chipEnd=Math.round(Math.max.apply(null,chips.map(function(c){return R(c).r})));
document.getElementById('ogres').textContent=JSON.stringify(res);
}
(document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(run);
})();
</script>'''

TPL = '''<!doctype html><html lang="@LANG"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html{overflow:hidden;background:#fdfcfc}
body{margin:0;width:1200px;height:630px;background:#fdfcfc;color:#0c0a09;font-family:-apple-system,"Segoe UI",Roboto,Arial,"PingFang SC","Microsoft YaHei","Yu Gothic","Malgun Gothic",sans-serif;position:relative;overflow:hidden}
.art{position:absolute;inset:0 0 0 38%;background:url(/assets/models/eleven/@IMG) center/cover no-repeat;-webkit-mask-image:linear-gradient(to right,transparent 0,#000 46%);mask-image:linear-gradient(to right,transparent 0,#000 46%)}
.mark{position:absolute;right:84px;top:92px;width:210px;height:210px;padding:56px;border-radius:52px;background:#0c0a09;box-shadow:0 10px 44px rgba(28,25,23,.28)}
.mark svg{width:100%;height:100%}
.c{position:absolute;left:80px;top:64px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:28px;font-weight:700;letter-spacing:-.02em;color:#1c1917}
.b em{font-style:normal;font-weight:500;color:#77716a}
.b svg{width:28px;height:28px}
h1{margin:64px 0 0;max-width:900px;font-size:@FSpx;line-height:1.02;font-weight:300;letter-spacing:-.035em;color:#0c0a09}
h1 span{background:linear-gradient(100deg,#e8502a 4%,#f08a5d 46%,#6f9a4a 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-weight:400}
p:lang(ko){word-break:keep-all;text-wrap:balance}
p:lang(ja){word-break:auto-phrase;line-break:strict}
p{margin:26px 0 0;font-size:34px;line-height:1.3;font-weight:500;color:#44403c;max-width:720px}
.r{position:absolute;left:80px;bottom:56px;display:flex;gap:12px;width:max-content}
.r span{white-space:nowrap;flex:none;padding:12px 20px;border-radius:999px;background:rgba(255,255,255,.9);border:1.5px solid #e7e3df;font-size:24px;color:#44403c}
.r .d{background:#0c0a09;color:#fff;border-color:#0c0a09}
.r .o{background:linear-gradient(100deg,#e8502a,#f08a5d 55%,#6f9a4a);color:#fff;border-color:transparent}
</style></head><body><div class="art"></div>
<div class="mark">@LOGO</div>
<div class="c"><div class="b">@SMALL@BRAND<em>· ElevenLabs</em></div><h1>Eleven <span>@KEY</span></h1><p>@SUB</p></div>
<div class="r">@CHIPS</div><pre id="ogres" style="display:none"></pre>@FIT</body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def arg(name):
    for a in sys.argv[1:]:
        if a.startswith(name + '='):
            return a.split('=', 1)[1].split(',')
    return None


def build(slug, lang):
    key, sub = PAGES[slug]
    if lang in NEW_LANGS:
        price = PRICE[slug]
        unit = (UNIT_STT_I18N if is_stt(slug) else UNIT_I18N)[lang]
        deal, tags, ent, sub_l = DEAL_I18N[lang], TAGS_I18N[lang], ENT_I18N[lang], SUB_I18N[slug][lang]
    else:
        price = PRICE[slug]
        unit = UNIT_STT[lang] if is_stt(slug) else UNIT[lang]
        deal, tags, ent, sub_l = DEAL[lang], TAGS[lang], ENT[lang], sub[lang]
    chips = (f'<span class="d">${price} {unit}</span><span class="o">{deal}</span>'
             f'<span>{tags}</span><span>{ent}</span>')
    fs = 112 if len(key) <= 8 else 84
    return (TPL.replace('@IMG', HERO_IMG[slug]).replace('@LOGO', logo(cls='', fill='#ffffff'))
            .replace('@SMALL', logo(cls='', fill='#0c0a09')).replace('@BRAND', BRAND)
            .replace('@KEY', key).replace('@SUB', sub_l).replace('@CHIPS', chips).replace('@FS', str(fs))
            .replace('@FIT', FIT_JS).replace('@LANG', lang))


def measure(exe, n):
    """用 --dump-dom 取页面里自检脚本写回的结果（JSON）。"""
    r = subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                        '--virtual-time-budget=3000', '--dump-dom', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                       capture_output=True, timeout=90)
    m = re.search(r'<pre id="ogres"[^>]*>(.*?)</pre>', r.stdout.decode('utf-8', 'replace'), re.S)
    if not m or not m.group(1).strip():
        return None
    return json.loads(m.group(1).replace('&amp;', '&'))


def main():
    os.makedirs(OUT, exist_ok=True)
    langs = arg('--langs') or ['zh', 'en']
    only = arg('--only')
    if only:
        bad = [s for s in only if s not in PAGES]
        if bad:
            sys.exit(f'--only 里有未知 slug：{bad}')
    names = []
    for lang in langs:
        if lang not in ('zh', 'en') + NEW_LANGS:
            sys.exit(f'未知语言：{lang}')
        new = lang in NEW_LANGS
        for slug in PAGES:
            if only and slug not in only:
                continue
            if new and slug not in NEW_SLUGS:
                continue
            # 新语言以英文页是否存在为准（译文页可能还没渲染）；zh / en 以本语言页为准
            if not os.path.exists(os.path.join(ROOT, 'en' if new else lang, 'models', slug + '.html')):
                continue
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(build(slug, lang))
            names.append(n)
    print(' '.join(names))
    exe = chrome()
    if '--html-only' in sys.argv or not exe:
        return
    from PIL import Image
    fails, shrunk = [], []
    for n in names:
        html = os.path.join(OUT, n + '.html')
        png = os.path.join(ROOT, 'assets', 'og', n + '.png')
        try:
            res = measure(exe, n)
            if not res or not res.get('ok'):
                fails.append(n)
                print('FAIL 版面违例，不出图', n, json.dumps(res, ensure_ascii=False))
                continue
            if res['shrunk']:
                shrunk.append(n)
            print('fit ', n, 'h1=%s sub=%s chip=%s' % (res['cur']['hf'], res['cur']['sf'], res['cur']['cf']),
                  'shrunk' if res['shrunk'] else 'ok', 'h1Lines=%s subLines=%s chipEnd=%s' % (res['h1Lines'], res['subLines'], res['chipEnd']))
            subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800',
                            '--virtual-time-budget=3000', f'--screenshot={png}', f'http://localhost:8765/.playwright-mcp/og/{n}.html'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            # 无头 Chrome 的窗口尺寸含浏览器边框，截图会偏大，这里放大窗口再裁成 1200×630
            Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
            print('png', os.path.relpath(png, ROOT), os.path.getsize(png) if os.path.exists(png) else 'MISSING')
        finally:
            if '--keep-html' not in sys.argv and os.path.exists(html):
                os.remove(html)
    print(f'共 {len(names)} 张，缩小字号 {len(shrunk)} 张：{" ".join(shrunk)}，版面违例 {len(fails)} 张：{" ".join(fails)}')
    if fails:
        sys.exit(1)


if __name__ == '__main__':
    main()
