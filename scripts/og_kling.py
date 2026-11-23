"""Kling 系列分享图（1200x630）：en / ja / ko / es / de，输出 assets/og/<slug>-<lang>.png。

zh 图不在这里生成，也不要改。
用法：
  python scripts/og_kling.py                       # 默认 ja,ko,es,de 全部 17 页
  python scripts/og_kling.py --langs=en            # 英文图（海外口径）
  python scripts/og_kling.py --langs=ja,ko --only=kling-audio,kling-video
  python scripts/og_kling.py --html-only           # 只写临时 html，不截图
  python scripts/og_kling.py --resume              # 跳过 3 小时内已出的图，中断后续跑

流程：每张图写一个临时 html（.playwright-mcp/og-kling/），页面内 JS 用 getBoundingClientRect 量
标题、副标题、标签：越界、溢出、标签间距 < 8px、标签重叠都算违例，违例就按 4% 步长缩小字号重试。
缩到下限仍违例则不出图并报错。出图后删除临时 html。
需要预览服务：python scripts/preview.py（http://localhost:8765）。
"""
import concurrent.futures as cf
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / '.playwright-mcp' / 'og-kling'
BASE = 'http://localhost:8765'
NEW = ('ja', 'ko', 'es', 'de')
LANGS_ALL = ('en',) + NEW
LANGATTR = {'en': 'en', 'ja': 'ja', 'ko': 'ko', 'es': 'es', 'de': 'de'}
# 起始字号倍率：新语言文案更长，从更小的字号开始；en 用满
K0 = {'en': 1.0, 'ja': 0.9, 'ko': 0.88, 'es': 0.9, 'de': 0.88}

# 固定标签文案（缺语言直接 KeyError）
TAG_CONC = {'en': 'Unlimited concurrency', 'ja': '同時実行数の上限なし', 'ko': '동시 실행 제한 없음',
            'es': 'Sin límite de RPM', 'de': 'Kein RPM-Limit'}
TAG_INV = {'en': 'Self-service invoices', 'ja': '請求書を自分で発行', 'ko': '인보이스 직접 발급',
           'es': 'Facturas en consola', 'de': 'Rechnungen im Konto'}
FOOT = {'en': 'Pricing & integration', 'ja': '料金と導入ガイド', 'ko': '가격 및 연동 가이드',
        'es': 'Precios e integración', 'de': 'Preise & Integration'}

# 价格句式：{p} 是已格式化的美元金额
UNIT = {
    'second': {'en': 'from {p} / second', 'ja': '1秒 {p} から', 'ko': '초당 {p}부터',
               'es': 'desde {p} / segundo', 'de': 'ab {p} / Sekunde'},
    'call': {'en': 'from {p} / call', 'ja': '1回 {p} から', 'ko': '호출당 {p}부터',
             'es': 'desde {p} / llamada', 'de': 'ab {p} / Aufruf'},
    'p5s': {'en': 'from {p} / 5 s', 'ja': '5秒 {p} から', 'ko': '5초당 {p}부터',
            'es': 'desde {p} / 5 s', 'de': 'ab {p} / 5 s'},
    'image': {'en': 'from {p} / image', 'ja': '1枚 {p} から', 'ko': '이미지당 {p}부터',
              'es': 'desde {p} / imagen', 'de': 'ab {p} / Bild'},
    # Advanced Lip Sync：只写口型同步 5 秒单价（人脸检测另计），不重复写术语
    'lipsync': {'en': '{p} / 5 s clip', 'ja': '5秒 {p}', 'ko': '5초당 {p}',
                'es': '{p} / 5 s', 'de': '{p} / 5 s'},
}


def money(v):
    """美元金额，小数一律用点。"""
    return '$' + v


def L(en, ja, ko, es, de):
    return {'en': en, 'ja': ja, 'ko': ko, 'es': es, 'de': de}


# kind 决定眉标：VIDEO / IMAGE / AUDIO / MODELS；cap 为 dict（分语言）或 str（各语言相同）
PAGES = {
    'kling': dict(
        h1='Kling API', kind='MODELS', price=('call', '0.00169'),
        sub=L('One key for every Kling video and audio workflow.',
              'Kling の動画・音声ワークフローを1つのキーで。',
              '하나의 키로 모든 Kling 비디오·오디오 워크플로.',
              'Una clave para todos los flujos de vídeo y audio de Kling.',
              'Ein Schlüssel für alle Kling-Video- und Audio-Workflows.'),
        cap=L('Video & audio models', '動画・音声モデル', '비디오·오디오 모델',
              'Modelos de vídeo y audio', 'Video- und Audiomodelle')),
    'kling-3.0-turbo': dict(
        h1='Kling 3.0 Turbo API', kind='VIDEO', price=('second', '0.1350'),
        sub=L('Fast, lightweight video for batch short clips.',
              'バッチ制作向けの軽量・高速な動画モデル。',
              '배치 숏폼 제작을 위한 가볍고 빠른 비디오 모델.',
              'Vídeo rápido y ligero para producir clips cortos en lote.',
              'Schnelles, leichtes Video für Kurzclips im Batch.'),
        cap=L('Fast short video', '高速ショート動画', '빠른 숏폼 비디오', 'Vídeo corto rápido', 'Schnelle Kurzvideos')),
    'kling-advanced-custom-elements': dict(
        h1='Kling Advanced Custom Elements API', kind='VIDEO', price=('call', '0.00169'),
        sub=L('Upgraded subject creation from 3–8 s clips.',
              'アップグレード版の被写体作成。3〜8秒のクリップに対応。',
              '업그레이드된 피사체 생성, 3~8초 클립 지원.',
              'Creación de sujetos mejorada, con clips de 3 a 8 s.',
              'Verbesserte Motiverstellung aus 3–8-s-Clips.'),
        cap=L('Custom subjects', 'カスタム被写体', '커스텀 피사체', 'Sujetos personalizados', 'Eigene Motive')),
    'kling-advanced-lip-sync': dict(
        h1='Kling Advanced Lip Sync API', kind='VIDEO', price=('lipsync', '0.0844'),
        sub=L('High-precision lip sync for natural speech.',
              '自然な発話のための高精度リップシンク。',
              '자연스러운 발화를 위한 고정밀 립싱크.',
              'Sincronización labial de alta precisión para un habla natural.',
              'Hochpräzise Lippensynchronisation für natürliche Sprache.'),
        cap=L('Face detection + lip sync', '顔検出＋リップシンク', '얼굴 감지 + 립싱크',
              'Detección facial + sincronización labial', 'Gesichtserkennung + Lippensynchronisation')),
    'kling-audio': dict(
        h1='Kling Audio API', kind='AUDIO', price=('call', '0.00844'),
        sub=L('Sound effects, video sound and speech for post-production.',
              'ポストプロダクション向けの効果音・動画サウンド・音声合成。',
              '후반 작업을 위한 효과음, 영상 사운드, 음성 합성.',
              'Efectos de sonido, sonido de vídeo y voz para posproducción.',
              'Soundeffekte, Video-Sound und Sprache für die Postproduktion.'),
        cap=L('Sound effects & speech', '効果音と音声合成', '효과음·음성 합성', 'Efectos y síntesis de voz', 'Soundeffekte & Sprache')),
    'kling-avatar-image2video': dict(
        h1='Kling Avatar Image2Video API', kind='VIDEO', price=('second', '0.0675'),
        sub=L('Turn a portrait into a talking avatar video.',
              'ポートレート画像からトーキングアバター動画を生成。',
              '인물 이미지를 말하는 아바타 비디오로.',
              'Convierte un retrato en un vídeo de avatar parlante.',
              'Aus einem Porträt wird ein sprechendes Avatar-Video.'),
        cap=L('Talking avatars', 'トーキングアバター', '말하는 아바타', 'Avatares parlantes', 'Sprechende Avatare')),
    'kling-custom-elements': dict(
        h1='Kling Custom Elements API', kind='VIDEO', price=('call', '0.00169'),
        sub=L('Reusable subject assets from 3–8 s clips.',
              '3〜8秒のクリップから再利用できる被写体素材。',
              '3~8초 클립으로 만드는 재사용 피사체 에셋.',
              'Recursos de sujeto reutilizables a partir de clips de 3 a 8 s.',
              'Wiederverwendbare Motiv-Assets aus 3–8-s-Clips.'),
        cap=L('Custom subjects', 'カスタム被写体', '커스텀 피사체', 'Sujetos personalizados', 'Eigene Motive')),
    'kling-custom-voices': dict(
        h1='Kling Custom Voices API', kind='AUDIO', price=('call', '0.00844'),
        sub=L('Reusable voice profiles for TTS and dubbing.',
              'TTS と吹き替え向けの再利用できるボイス。',
              'TTS와 더빙을 위한 재사용 보이스 프로필.',
              'Perfiles de voz reutilizables para TTS y doblaje.',
              'Wiederverwendbare Stimmprofile für TTS und Synchronisation.'),
        cap=L('Custom voices', 'カスタムボイス', '커스텀 보이스', 'Voces personalizadas', 'Eigene Stimmen')),
    'kling-effects': dict(
        h1='Kling Effects API', kind='VIDEO', price=('call', '0.1688'),
        sub=L('136+ creative video effects and style transfers.',
              '136種以上のクリエイティブ動画エフェクトとスタイル変換。',
              '136개 이상의 크리에이티브 비디오 효과와 스타일 변환.',
              'Más de 136 efectos creativos de vídeo y transferencias de estilo.',
              'Über 136 kreative Videoeffekte und Stilübertragungen.'),
        cap=L('Video effects', '動画エフェクト', '비디오 효과', 'Efectos de vídeo', 'Videoeffekte')),
    'kling-image-3.0': dict(
        h1='Kling Image 3.0 API', kind='IMAGE', price=('image', '0.00169'),
        sub=L('Kuaishou Kling image model, native 2K / 4K.',
              'Kuaishou の Kling 画像モデル。2K / 4K をネイティブ出力。',
              'Kuaishou의 Kling 이미지 모델, 네이티브 2K / 4K.',
              'Modelo de imagen Kling de Kuaishou, 2K / 4K nativo.',
              'Kling-Bildmodell von Kuaishou, natives 2K / 4K.'),
        cap=L('Text & image-to-image', 'テキスト・画像から画像', '텍스트·이미지→이미지',
              'De texto y de imagen a imagen', 'Text- und Bild-zu-Bild')),
    'kling-motion-control': dict(
        h1='Kling Motion Control API', kind='VIDEO', price=('second', '0.0844'),
        sub=L('Transfer motion from a reference video to a character image.',
              '参照動画の動きをキャラクター画像に転写。',
              '참조 비디오의 동작을 캐릭터 이미지에 적용.',
              'Transfiere el movimiento de un vídeo de referencia a una imagen de personaje.',
              'Überträgt Bewegung aus einem Referenzvideo auf ein Charakterbild.'),
        cap=L('Motion control', 'モーションコントロール', '모션 컨트롤', 'Control de movimiento', 'Motion Control')),
    'kling-multi-elements': dict(
        h1='Kling Multi Elements API', kind='VIDEO', price=('call', '0.5064'),
        sub=L('Blend multiple elements in one video.',
              '1本の動画で複数のエレメントを合成。',
              '한 비디오 안에서 여러 엘리먼트를 합성.',
              'Combina varios elementos en un mismo vídeo.',
              'Mehrere Elemente in einem Video kombinieren.'),
        cap=L('Multi-element video', 'マルチエレメント動画', '멀티 엘리먼트 비디오',
              'Vídeo con varios elementos', 'Video mit mehreren Elementen')),
    'kling-omni-video': dict(
        h1='Kling Omni Video API', kind='VIDEO', price=('call', '0.1688'),
        sub=L('Multimodal model with video, image and subject references.',
              '動画・画像・被写体の参照を使えるマルチモーダルモデル。',
              '비디오·이미지·피사체 참조를 쓰는 멀티모달 모델.',
              'Modelo multimodal con referencias de vídeo, imagen y sujeto.',
              'Multimodales Modell mit Video-, Bild- und Motivreferenzen.'),
        cap=L('Multimodal references', 'マルチモーダル参照', '멀티모달 참조', 'Referencias multimodales', 'Multimodale Referenzen')),
    'kling-video-extend': dict(
        h1='Kling Video Extend API', kind='VIDEO', price=('call', '0.1688'),
        sub=L('Extend existing videos with consistent style.',
              'スタイルを保ったまま既存の動画を延長。',
              '스타일을 유지하며 기존 비디오를 연장.',
              'Amplía vídeos existentes manteniendo el estilo.',
              'Bestehende Videos verlängern, Stil bleibt konsistent.'),
        cap=L('Video extension', '動画の延長', '비디오 연장', 'Extensión de vídeo', 'Video-Verlängerung')),
    'kling-video-v4-flash': dict(
        h1='Kling Video V4 Flash API', kind='VIDEO', price=('second', '0.1206'),
        sub=L('Fast 720p video from text or references.',
              'テキストや参照から高速に720p動画を生成。',
              '텍스트나 참조로 빠르게 720p 비디오 생성.',
              'Vídeo 720p rápido a partir de texto o referencias.',
              'Schnelles 720p-Video aus Text oder Referenzen.'),
        cap='720p · 3–30 s'),
    'kling-video-v4': dict(
        h1='Kling Video V4 API', kind='VIDEO', price=('second', '0.1795'),
        sub=L('Realistic, controllable shots with native audio.',
              'リアルで制御しやすいショットとネイティブ音声。',
              '사실적이고 제어하기 쉬운 샷과 네이티브 오디오.',
              'Planos realistas y controlables con audio nativo.',
              'Realistische, steuerbare Einstellungen mit nativem Audio.'),
        cap=L('Native audio & lip sync', 'ネイティブ音声とリップシンク', '네이티브 오디오·립싱크',
              'Audio nativo y sincronización labial', 'Natives Audio & Lippensynchronisation')),
    'kling-video': dict(
        h1='Kling Video API', kind='VIDEO', price=('p5s', '0.2532'),
        sub=L('Text-to-video, image-to-video and video continuation.',
              'テキスト・画像から動画、動画の続きの生成に対応。',
              '텍스트·이미지→비디오와 영상 이어가기 지원.',
              'De texto y de imagen a vídeo, y continuación de vídeo.',
              'Text- und Bild-zu-Video sowie Fortsetzung.'),
        cap='Video-O1 · V1.0–V2.6'),
}
SLUGS = tuple(PAGES)


def pick(v, lang):
    return v if isinstance(v, str) else v[lang]


def logo():
    svg = (ROOT / 'assets' / 'icons' / 'kling.svg').read_text(encoding='utf-8')
    svg = re.sub(r'<title>.*?</title>', '', svg)
    return svg.replace('fill="currentColor"', 'fill="#0b0b12"', 1).replace('height="1em"', 'height="26"').replace('width="1em"', 'width="26"')


CSS = '''
*{box-sizing:border-box}
html,body{margin:0}
body{position:relative;width:1200px;height:630px;overflow:hidden;color:#141b2d;
 background:linear-gradient(135deg,#f8f8ff 0%,#eef0ff 55%,#dfe6ff 100%);
 font-family:"Segoe UI","Yu Gothic UI","Meiryo","Malgun Gothic","Microsoft YaHei",Arial,sans-serif}
body.ko,body.ko *{word-break:keep-all}
.top{position:absolute;left:64px;right:64px;top:44px;height:34px;display:flex;align-items:center;justify-content:space-between}
.brand{font-size:24px;font-weight:700;letter-spacing:-.4px}
.vendor{display:flex;align-items:center;gap:12px;font-size:22px;font-weight:700;color:#2f2a7c}
.vendor i{display:flex;width:34px;height:34px;border-radius:9px;background:#fff;align-items:center;justify-content:center}
.col{position:absolute;left:64px;top:110px;width:690px;height:345px;display:flex;flex-direction:column;justify-content:center}
.eyebrow{font-size:calc(17px*var(--k));font-weight:800;letter-spacing:3px;color:#5b5ef0;margin:0 0 calc(14px*var(--k))}
h1{margin:0;font-size:calc(var(--h)*var(--k));line-height:1.08;font-weight:800;letter-spacing:-1.5px;color:#141b2d}
.sub{margin:calc(18px*var(--k)) 0 0;font-size:calc(var(--s)*var(--k));line-height:1.4;color:#4a5568}
.sub b{display:inline-block;color:#2f2a7c;font-weight:700}
.art{position:absolute;right:64px;top:118px;width:314px;height:332px}
.art div{position:absolute;width:150px;height:150px;border-radius:22px;box-shadow:0 18px 40px rgba(60,60,160,.18)}
.a1{left:0;top:0;background:linear-gradient(135deg,#c4b5fd,#6366f1 60%,#312e81)}
.a2{left:164px;top:18px;background:linear-gradient(160deg,#bae6fd,#38bdf8 50%,#1d4ed8)}
.a3{left:0;top:164px;background:linear-gradient(160deg,#e9a8ff,#7c3aed 45%,#1e1b4b)}
.a4{left:164px;top:182px;background:linear-gradient(160deg,#4f46e5,#a5b4fc 55%,#e0e7ff)}
.tags{position:absolute;left:64px;bottom:110px;display:flex;gap:12px;align-items:center}
.tags span{white-space:nowrap;font-size:calc(19px*var(--k));line-height:1.2;padding:calc(14px*var(--k)) calc(24px*var(--k));border:1px solid #d3d8f6;border-radius:999px;background:#fff;color:#2f2a7c}
.tags span.cap{background:#2f2a7c;border-color:#2f2a7c;color:#fff;font-weight:700}
.rule{position:absolute;left:64px;right:64px;bottom:68px;height:1px;background:#d7dbf3}
.foot{position:absolute;left:64px;right:64px;bottom:28px;display:flex;justify-content:space-between;font-size:17px;color:#6b7280}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
'''

# 页面内自检：量 DOM，违例就缩小字号重试，结果写进 #fit
JS = r'''
(function(){
 var root=document.documentElement, MIN=0.62, STEP=0.04;
 function R(el){var r=el.getBoundingClientRect();return {l:r.left,t:r.top,r:r.right,b:r.bottom}}
 function T(el){var g=document.createRange();g.selectNodeContents(el);var r=g.getBoundingClientRect();return {l:r.left,t:r.top,r:r.right,b:r.bottom}}
 function viol(){
  var v=[], q=function(s){return document.querySelector(s)};
  var h1=q('h1'), sub=q('.sub'), eb=q('.eyebrow'), col=q('.col'), art=q('.art'), tags=[].slice.call(document.querySelectorAll('.tags span'));
  var cr=R(col), ar=R(art);
  [['h1',h1],['sub',sub],['eyebrow',eb]].forEach(function(p){
   var t=T(p[1]);
   if(t.l<0||t.t<0||t.r>1200||t.b>630) v.push(p[0]+' 超出画布');
   if(t.r>cr.r+0.5) v.push(p[0]+' 超出文字列右边界');
   if(t.t<R(q('.top')).b+8) v.push(p[0]+' 压到顶栏');
   if(p[1].scrollWidth>p[1].clientWidth+1) v.push(p[0]+' 横向溢出');
  });
  if(T(sub).r>ar.l-16) v.push('副标题压到右侧图形');
  var tg=R(q('.tags'));
  tags.forEach(function(s,i){
   var r=R(s);
   if(r.l<0||r.t<0||r.r>1200||r.b>630) v.push('标签'+i+' 超出画布');
   if(r.r>1136.5) v.push('标签'+i+' 超出右边距');
   if(s.scrollWidth>s.clientWidth+1) v.push('标签'+i+' 文字溢出');
   if(i>0){var p=R(tags[i-1]); if(r.l-p.r<8) v.push('标签'+i+' 与前一标签间距<8');}
   if(!(r.r<ar.l||r.l>ar.r||r.b<ar.t||r.t>ar.b)) v.push('标签'+i+' 压到右侧图形');
  });
  var colText=Math.max(T(h1).b,T(sub).b);
  if(colText>tg.t-8) v.push('标题/副标题压到标签行');
  if(R(h1).b>R(sub).t+1) v.push('标题与副标题重叠');
  return v;
 }
 var k=parseFloat(root.dataset.k0), k0=k, v;
 for(;;){
  root.style.setProperty('--k',k);
  v=viol();
  if(!v.length||k<=MIN) break;
  k=Math.round((k-STEP)*100)/100;
 }
 var pre=document.createElement('pre'); pre.id='fit'; pre.style.display='none';
 pre.textContent=JSON.stringify({k0:k0,k:k,viol:v});
 document.body.appendChild(pre);
})();
'''


def build_html(slug, lang):
    p = PAGES[slug]
    unit, val = p['price']
    price = UNIT[unit][lang].format(p=money(val))
    sub = p['sub'][lang]
    h1 = p['h1']
    hsize = 84 if len(h1) <= 20 else (72 if len(h1) <= 26 else 64)
    cap = pick(p['cap'], lang)
    e = html.escape
    return f'''<!doctype html><html lang="{LANGATTR[lang]}" data-k0="{K0[lang]}" style="--k:{K0[lang]};--h:{hsize}px;--s:30px"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body class="{lang}"><div class="top"><span class="brand">AnyAIGC</span><span class="vendor"><i>{logo()}</i>Kling</span></div>
<div class="col"><p class="eyebrow">KLING · {p['kind']} API</p><h1>{e(h1)}</h1><p class="sub">{e(sub)} <b>{e(price)}</b></p></div>
<div class="art"><div class="a1"></div><div class="a2"></div><div class="a3"></div><div class="a4"></div></div>
<div class="tags"><span class="cap">{e(cap)}</span><span>{e(TAG_CONC[lang])}</span><span>{e(TAG_INV[lang])}</span></div>
<div class="rule"></div><div class="foot"><span>www.anyaigc.ai</span><span>{e(FOOT[lang])} ↗</span></div>
<script>{JS}</script></body></html>'''


def chrome():
    hits = sorted(glob.glob(os.path.expanduser('~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe')))
    if not hits:
        raise SystemExit('找不到 Playwright Chromium（~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe）')
    return hits[-1]


def run_chrome(args, url, tries=3):
    """超时就只结束这一个 Chrome 进程树（不动其他 Chrome），最多重试 tries 次。
    不要加 --user-data-dir：在这台机器上会让 headless Chrome 挂住。"""
    cmd = [chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars',
           '--window-size=1280,800', '--virtual-time-budget=6000', *args, url]
    for _ in range(tries):
        pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            out, _e = pr.communicate(timeout=45)
            return out
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pr.pid)], capture_output=True)
            pr.communicate()
    return None


def render(slug, lang):
    """返回 (slug, lang, 状态, 详情)。状态：ok / shrunk / fail。"""
    from PIL import Image
    hp = OUT_HTML / f'{slug}-{lang}.html'
    png = ROOT / 'assets' / 'og' / f'{slug}-{lang}.png'
    url = f'{BASE}/.playwright-mcp/og-kling/{slug}-{lang}.html'
    try:
        r = run_chrome(['--dump-dom'], url)
        if r is None:
            return slug, lang, 'fail', 'Chrome 多次超时（量 DOM）'
        dom = r.decode('utf-8', 'replace')
        m = re.search(r'<pre id="fit"[^>]*>(.*?)</pre>', dom, re.S)
        if not m:
            return slug, lang, 'fail', '页面没有返回自检结果（预览服务没跑？）'
        fit = json.loads(html.unescape(m.group(1)))
        if fit['viol']:
            return slug, lang, 'fail', f"缩到 {fit['k']} 仍违例：{'; '.join(fit['viol'])}"
        tmp = png.with_suffix('.tmp.png')
        tmp.unlink(missing_ok=True)
        run_chrome([f'--screenshot={tmp}'], url)
        if not tmp.exists():
            return slug, lang, 'fail', '截图失败'
        Image.open(tmp).crop((0, 0, 1200, 630)).convert('RGB').save(png, optimize=True)
        tmp.unlink()
        return slug, lang, ('shrunk' if fit['k'] < fit['k0'] else 'ok'), f"k0={fit['k0']} k={fit['k']} {png.stat().st_size}B"
    finally:
        hp.unlink(missing_ok=True)


def main():
    args = sys.argv[1:]
    langs = next((a.split('=', 1)[1].split(',') for a in args if a.startswith('--langs=')), list(NEW))
    only = next((a.split('=', 1)[1].split(',') for a in args if a.startswith('--only=')), list(SLUGS))
    for lang in langs:
        if lang not in LANGS_ALL:
            raise SystemExit(f'不支持的语言：{lang}（zh 图不在此脚本生成）')
    for slug in only:
        if slug not in PAGES:
            raise SystemExit(f'未知 slug：{slug}')
    OUT_HTML.mkdir(parents=True, exist_ok=True)
    jobs = [(s, l) for l in langs for s in only]
    if '--resume' in args:  # 跳过 3 小时内已出过的图，用于中断后续跑
        import time
        fresh = lambda s, l: (ROOT / 'assets' / 'og' / f'{s}-{l}.png').exists() and             time.time() - (ROOT / 'assets' / 'og' / f'{s}-{l}.png').stat().st_mtime < 3 * 3600
        jobs = [j for j in jobs if not fresh(*j)]
        print(f'resume：还需出 {len(jobs)} 张')
    for s, l in jobs:
        (OUT_HTML / f'{s}-{l}.html').write_text(build_html(s, l), encoding='utf-8')
    if '--html-only' in args:
        print(f'写了 {len(jobs)} 个临时 html：{OUT_HTML}')
        return
    res = []
    with cf.ThreadPoolExecutor(max_workers=1) as ex:
        for r in ex.map(lambda j: render(*j), jobs):
            res.append(r)
            print(f'{r[2]:6} {r[0]}-{r[1]}  {r[3]}', flush=True)
    bad = [r for r in res if r[2] == 'fail']
    shrunk = [r for r in res if r[2] == 'shrunk']
    print(f'共 {len(res)} 张，成功 {len(res) - len(bad)}，其中自动缩小字号 {len(shrunk)} 张，失败 {len(bad)} 张')
    if bad:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
