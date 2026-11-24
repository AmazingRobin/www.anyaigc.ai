"""Create temporary HTML for 1200x630 share-image captures.

默认（不带参数）：只写 zh、en 的临时 HTML 和 manifest，交给 Playwright 截图。
新语言：python scripts/og_qwen_media.py --langs=ja,ko,es,de [--only=slug1,slug2]
  直接用 Chrome headless 截图并裁成 1200x630，写入 assets/og/<slug>-<lang>.png，随后删除临时 HTML。
  默认处理 NEW_SLUGS 里的 18 个页面（7 个 Qwen 图像/实时 + 11 个 HappyHorse/Wan）。
英文图：python scripts/og_qwen_media.py --langs=en [--only=...]
  页脚为 Self-service invoices（海外口径）；同样走 Chrome 截图 + 裁剪，覆盖 assets/og/<slug>-en.png。
  zh 图不在此流程内，不要用本脚本重新生成。
  需要先运行 python scripts/preview.py（http://localhost:8765）。
  词表缺词直接 KeyError，不回退英文。
"""
import glob
import json
import os
import subprocess
import sys
from pathlib import Path
from qwen_media_data import MODELS, BY_SLUG, price_label, entry_rate, money
from qwen_pages import logo
from html import escape

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'.playwright-mcp/qwen-media-og'

NEW = ('ja', 'ko', 'es', 'de')
LANGATTR = {'zh': 'zh-CN', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
# 这一批要出新语言图的页面（其余以后批次再做）
NEW_SLUGS = ['qwen-image-3.0', 'qwen-image-3.0-pro', 'qwen-image-2.0-2026-03-03', 'qwen-image-max',
             'qwen-image-max-2025-12-30', 'z-image-turbo', 'qwen3.8-omni-flash-realtime',
             'happyhorse-1.0-i2v', 'happyhorse-1.0-r2v', 'happyhorse-1.0-t2v', 'happyhorse-1.0-video-edit',
             'happyhorse-1.1-i2v', 'happyhorse-1.1-r2v', 'happyhorse-1.1-t2v',
             'wan2.5-i2v-preview', 'wan2.6-i2v', 'wan2.7-image-pro', 'wan3.0-video']
# 英文图页脚（海外口径）；zh 的「对公 · 专票」保持原样
EN_INV = 'Self-service invoices'


def _t(ja, ko, es, de):
    return {'ja': ja, 'ko': ko, 'es': es, 'de': de}


# 类别标签（与英文 label 一一对应）
LABEL_I18N = {
    'IMAGE API': _t('画像 API', '이미지 API', 'API de imágenes', 'Bild-API'),
    'REAL-TIME API': _t('リアルタイム API', '실시간 API', 'API en tiempo real', 'Echtzeit-API'),
    'VIDEO API': _t('動画 API', '비디오 API', 'API de vídeo', 'Video-API'),
}
# 页脚标签：并发不限 / 自助开票（英文图和新语言图都写自助开票）
FOOT_I18N = {
    'No concurrency cap': _t('同時実行数の上限なし', '동시 실행 제한 없음', 'Sin límite de RPM', 'Kein RPM-Limit'),
    'Self-service invoices': _t('請求書を自分で発行', '인보이스 직접 발급', 'Facturas en consola', 'Rechnungen im Konto'),
}
# 单价单位（美元数字与英文图一致，只翻译单位；术语见 briefs/batch4-qwen.md）
UNIT_I18N = {
    'image': _t('1枚', '이미지', 'imagen', 'Bild'),
    'request': _t('リクエスト', '요청', 'petición', 'Anfrage'),
    'tokens': _t('100万トークン', '100만 토큰', 'millón de tokens', '1 Mio. Tokens'),
    'base': _t('課金単位（基本料金）', '과금 단위 기본가', 'unidad de facturación (base)', 'Abrechnungseinheit (Basis)'),
}
# 每个型号的一句话 lead，按 m['lead'][1] 的英文原意翻译
LEAD_I18N = {
    'Turn detailed instructions into rich visual content.': _t(
        '詳細な指示を、情報量の多いビジュアルに。', '상세한 지시를 풍부한 비주얼로 바꿔 줍니다.',
        'Convierte instrucciones detalladas en contenido visual rico.', 'Verwandelt detaillierte Anweisungen in reichhaltige visuelle Inhalte.'),
    'Complex layouts, with attention to the details.': _t(
        '複雑なレイアウトも、細部まで丁寧に。', '복잡한 레이아웃도 디테일까지 놓치지 않습니다.',
        'Diseños complejos, atentos a cada detalle.', 'Komplexe Layouts, mit Liebe zum Detail.'),
    'Generation and editing in one creative workflow.': _t(
        '生成と編集を、ひとつの制作フローで。', '생성과 편집을 하나의 제작 흐름에서.',
        'Generación y edición en un mismo flujo creativo.', 'Erzeugen und Bearbeiten in einem kreativen Workflow.'),
    'Lightweight inference for visual exploration.': _t(
        '軽量な推論で、ビジュアルを探索。', '가벼운 추론으로 비주얼을 탐색합니다.',
        'Inferencia ligera para explorar ideas visuales.', 'Leichtgewichtige Inferenz zum Erkunden visueller Ideen.'),
    'Natural detail and a realistic look.': _t(
        '自然なディテールと、リアルな質感。', '자연스러운 디테일과 사실적인 질감.',
        'Detalle natural y aspecto realista.', 'Natürliche Details und realistische Optik.'),
    'A dated snapshot for an existing workflow.': _t(
        '既存のワークフロー向けの日付付きスナップショット。', '기존 워크플로를 위한 날짜 지정 스냅샷.',
        'Una instantánea con fecha para un flujo de trabajo existente.', 'Ein datierter Snapshot für einen bestehenden Workflow.'),
    'Listen, see, and respond in real time.': _t(
        'リアルタイムで聞き、見て、応答します。', '실시간으로 듣고, 보고, 응답합니다.',
        'Escucha, ve y responde en tiempo real.', 'Hört, sieht und antwortet in Echtzeit.'),
    # HappyHorse：m['lead'][1] = 模式名 + ' that carries your creative intent into motion.'（术语见 briefs/batch5-video.md）
    'Text-to-video that carries your creative intent into motion.': _t(
        'テキストから動画へ。創作の意図を、動きにのせて。', '텍스트→비디오로 창작 의도를 움직임으로 옮깁니다.',
        'De texto a vídeo, para llevar la intención creativa al movimiento.', 'Text-zu-Video, das die kreative Absicht in Bewegung bringt.'),
    'Image-to-video that carries your creative intent into motion.': _t(
        '画像から動画へ。創作の意図を、動きにのせて。', '이미지→비디오로 창작 의도를 움직임으로 옮깁니다.',
        'De imagen a vídeo, para llevar la intención creativa al movimiento.', 'Bild-zu-Video, das die kreative Absicht in Bewegung bringt.'),
    'Reference-to-video that carries your creative intent into motion.': _t(
        '参照から動画へ。創作の意図を、動きにのせて。', '참조→비디오로 창작 의도를 움직임으로 옮깁니다.',
        'De referencia a vídeo, para llevar la intención creativa al movimiento.', 'Referenz-zu-Video, das die kreative Absicht in Bewegung bringt.'),
    'Video editing that carries your creative intent into motion.': _t(
        '動画編集で、創作の意図を動きにのせて。', '비디오 편집으로 창작 의도를 움직임으로 옮깁니다.',
        'Edición de vídeo que lleva la intención creativa al movimiento.', 'Videobearbeitung, die die kreative Absicht in Bewegung bringt.'),
    'Give a still image its next scene.': _t(
        '静止画に、次のシーンを。', '정지 이미지에 다음 장면을 이어 줍니다.',
        'Da a una imagen fija su siguiente escena.', 'Einem Standbild die nächste Szene geben.'),
    'Build a visual idea from your references.': _t(
        '参照画像から、ビジュアルのアイデアを形に。', '참조 이미지에서 비주얼 아이디어를 완성합니다.',
        'Construye una idea visual a partir de referencias.', 'Aus Referenzen eine visuelle Idee entwickeln.'),
    'Let one shot hold an entire story.': _t(
        'ワンショットに、ひとつの物語をまるごと。', '한 번의 샷에 이야기 전체를 담습니다.',
        'Que un solo plano contenga una historia entera.', 'Ein Shot, eine ganze Geschichte.'),
}
# 按秒 / 按片段 / 按张计费的写法（ja 用斜线，ko 前置，es/de 后置；术语见 briefs/batch5-video.md）
PER_I18N = {
    'second': _t('1秒', '초당', 'por segundo', 'pro Sekunde'),
    'clip': _t('1クリップ', '클립당', 'por clip', 'pro Clip'),
    'image': _t('1枚', '이미지당', 'por imagen', 'pro Bild'),
}


def price_i18n(m, lang):
    """美元数字与英文图一致，只翻译单位。"""
    r = entry_rate(m)
    amount = money(r['amount'], m, 'en')
    if r['unit'] in PER_I18N:
        per = PER_I18N[r['unit']][lang]
        return {'ja': f'{amount} / {per}', 'ko': f'{per} {amount}'}.get(lang, f'{amount} {per}')
    return f'{amount} / {UNIT_I18N[r["unit"]][lang]}'


# 页面内自检：量 DOM，越界或重叠就缩小字号，直到都在画布内。结果写到 <html data-fit>
FIT_JS = '''<script>(function(){
var W=1200,H=630,main=document.querySelector('main'),h1=document.querySelector('h1'),p=document.querySelector('main>p'),foot=document.querySelector('footer');
var spans=[].slice.call(foot.children);
function fs(el){return parseFloat(getComputedStyle(el).fontSize)}
function bad(){
  var mr=main.getBoundingClientRect(),right=mr.right-64+.5,bottom=mr.bottom-54+.5,all=[].slice.call(document.querySelectorAll('main, main *'));
  for(var i=0;i<all.length;i++){var r=all[i].getBoundingClientRect();if(!r.width&&!r.height)continue;
    if(r.left<-.5||r.top<-.5||r.right>W+.5||r.bottom>H+.5)return all[i].tagName==='H1'?'h1':all[i].tagName==='P'?'p':'foot'}
  var kids=[].slice.call(main.children);
  for(i=0;i<kids.length;i++){var k=kids[i].getBoundingClientRect();if(k.right>right||k.bottom>bottom)return kids[i]===h1?'h1':kids[i]===p?'p':'foot'}
  if(h1.getBoundingClientRect().bottom>p.getBoundingClientRect().top+.5)return 'h1';
  if(p.getBoundingClientRect().bottom>foot.getBoundingClientRect().top+.5)return 'p';
  if(p.scrollWidth>p.clientWidth+1)return 'p';
  if(foot.scrollWidth>foot.clientWidth+1)return 'foot';
  var t=spans[0].getBoundingClientRect().top;for(i=1;i<spans.length;i++)if(Math.abs(spans[i].getBoundingClientRect().top-t)>2)return 'foot';
  return ''}
var n=0,e;
while((e=bad())&&n<60){n++;
  if(e==='h1')h1.style.fontSize=Math.max(32,fs(h1)-2)+'px';
  else if(e==='p')p.style.fontSize=Math.max(14,fs(p)-1)+'px';
  else spans.forEach(function(s){s.style.fontSize=Math.max(11,fs(s)-.5)+'px'})}
document.documentElement.setAttribute('data-fit',(e?'BAD:'+e:'ok')+' steps='+n+' h1='+fs(h1)+' p='+fs(p)+' foot='+fs(spans[0]));
})()</script>'''


def render(m, lang, shot=False):
    """生成一个页面的 HTML。zh 的输出与改动前完全一致；en 的页脚为 Self-service invoices。
    shot=True（en 用 Chrome 截图）：只给 body 加 position:relative，其余样式与 Playwright 版相同。"""
    name=m['name'];dark=m['kind']!='image';title=escape(name)
    new = lang in NEW
    en_label = 'IMAGE API' if m['kind']=='image' else 'REAL-TIME API' if m['kind']=='realtime' else 'VIDEO API'
    if new:
        label = LABEL_I18N[en_label][lang]
        sub = escape(LEAD_I18N[m['lead'][1]][lang])
        price = escape(price_i18n(m, lang))
        conc = FOOT_I18N['No concurrency cap'][lang]
        inv = FOOT_I18N['Self-service invoices'][lang]
    else:
        label=('图像 API' if m['kind']=='image' else '实时音视频 API' if m['kind']=='realtime' else '视频 API') if lang=='zh' else en_label
        sub=escape(m['lead'][lang=='en']);price=escape(price_label(m,lang))
        conc='并发不限' if lang=='zh' else 'No concurrency cap'
        inv='对公 · 专票' if lang=='zh' else EN_INV
    size=64 if len(name)<30 else 56
    fonts = 'system-ui,"Segoe UI","Microsoft YaHei","Yu Gothic UI","Malgun Gothic",sans-serif' if new else 'system-ui,"Segoe UI","Microsoft YaHei",sans-serif'
    # 新语言文本比英文长：缩小字号；韩语按词断行
    # body 设为定位元素，main 才按 1200x630 的画布布局（Chrome 窗口是 1280x800，不设会撑出画布）
    ncss = '.n{position:relative}.n .kind{letter-spacing:.06em}.n p{font-size:23px}.n footer{flex-wrap:nowrap}.n footer span{font-size:16px;white-space:nowrap;padding:10px 16px}.k p{word-break:keep-all}' if new else ''
    body_open = f'<body class="n{" k" if lang=="ko" else ""}">' if new else '<body class="e">' if shot else ''
    body_close = ('</body>' if new or shot else '')
    if shot and not new:
        # Chrome headless 把 ui-monospace 解析成别的字体，与 Playwright 旧图不同；英文图的类别标签固定用 Consolas
        ncss = '.e{position:relative}.e .kind{font-family:Consolas,ui-monospace,monospace}'
    fit = FIT_JS if (new or shot) else ''
    template=f'''<!doctype html><html lang="{LANGATTR[lang] if new else lang}"><meta charset="utf-8"><style>
*{{box-sizing:border-box}}html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:{'#10131d' if dark else '#fff'};color:{'#fff' if dark else '#1d1d1f'};font-family:{fonts}}}
body:before{{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 100% 0,{'#343077' if dark else '#e9edff'},transparent 60%);z-index:0}}main{{position:absolute;inset:18px;padding:54px 64px;display:flex;flex-direction:column;border:1px solid {'#ffffff30' if dark else '#e2e6f2'};z-index:1}}
header{{display:flex;align-items:center;justify-content:space-between}}.brand{{font-size:27px;font-weight:700}}.kind{{font:14px ui-monospace,monospace;color:{'#48dbe4' if dark else '#082dff'};letter-spacing:.13em}}.logo{{margin-top:34px}}svg{{width:40px;height:40px;{'filter:brightness(0) invert(1)' if dark else ''}}}h1{{font-size:{size}px;line-height:1.12;letter-spacing:-.04em;margin:18px 0;max-width:1030px;overflow-wrap:anywhere}}p{{font-size:25px;line-height:1.4;margin:0;max-width:1020px;color:{'#bac2d8' if dark else '#657084'}}}footer{{margin-top:auto;display:flex;flex-wrap:wrap;gap:12px}}footer span{{border:1px solid {'#ffffff40' if dark else '#dbe1f3'};border-radius:999px;padding:10px 18px;font-size:18px}}footer span:first-child{{background:{'#3655f7' if dark else '#082dff'};color:#fff;border-color:transparent}}{ncss}</style>
{body_open}<main><header><span class="brand">AnyAIGC</span><span class="kind">{label}</span></header><div class="logo">{logo(40)}</div><h1>{title}</h1><p>{sub}</p><footer><span>{price}</span><span>{conc}</span><span>{inv}</span></footer></main>{fit}{body_close}</html>'''
    return template


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    return hits[-1] if hits else None


def capture_new(langs, slugs):
    """新语言：写临时 HTML → Chrome 自检字号 → Chrome 截图 → Pillow 裁 1200x630 → 删 HTML。"""
    from PIL import Image
    exe = chrome()
    if not exe:
        sys.exit('找不到 Playwright 的 chromium')
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for lang in langs:
        for slug in slugs:
            m = BY_SLUG[slug]
            hp = OUT / f'{slug}-{lang}.html'
            hp.write_text(render(m, lang, shot=True), encoding='utf-8')
            url = f'http://localhost:8765/.playwright-mcp/qwen-media-og/{slug}-{lang}.html'
            png = ROOT / 'assets' / 'og' / f'{slug}-{lang}.png'
            base = [exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1280,800', '--virtual-time-budget=6000']
            dom = subprocess.run(base + ['--dump-dom', url], capture_output=True, timeout=90).stdout.decode('utf-8', 'replace')
            fit = dom.split('data-fit="', 1)[1].split('"', 1)[0] if 'data-fit="' in dom else 'NO-FIT-RESULT'
            subprocess.run(base + [f'--screenshot={png}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
            hp.unlink()
            n += 1
            print(f'{slug}-{lang}: {fit} size={png.stat().st_size}')
    print(f'Wrote {n} PNG files.')


def main():
    args = sys.argv[1:]
    langs = [a.split('=', 1)[1].split(',') for a in args if a.startswith('--langs=')]
    only = [a.split('=', 1)[1].split(',') for a in args if a.startswith('--only=')]
    if langs:
        bad = [l for l in langs[0] if l not in NEW and l != 'en']
        if bad:
            sys.exit(f'--langs 只支持 en,{",".join(NEW)}，zh 图保持原样不重新生成: {bad}')
        slugs = only[0] if only else NEW_SLUGS
        for s in slugs:
            if s not in BY_SLUG:
                sys.exit(f'未知 slug: {s}')
        capture_new(langs[0], slugs)
        return
    OUT.mkdir(parents=True,exist_ok=True)
    captures=[]
    for lang in ('zh','en'):
        for m in MODELS:
            filename=f'{m["slug"]}-{lang}'
            p=OUT/f'{filename}.html';p.write_text(render(m,lang),encoding='utf-8')
            captures.append({'slug':m['slug'],'lang':lang,'url':f'http://localhost:8765/.playwright-mcp/qwen-media-og/{filename}.html','path':f'assets/og/{filename}.png'})
    (OUT/'manifest.json').write_text(json.dumps(captures,indent=2),encoding='utf-8')
    print(f'Created {len(captures)} share-image HTML sources and manifest.')


if __name__=='__main__':main()
