"""Render 1200x630 Vidu share cards: python scripts/og_vidu.py

默认只写 zh/en 的临时 HTML。新语言和英文重出走 Chrome headless 直接截图（需先启动 python scripts/preview.py）：
    python scripts/og_vidu.py --langs=ja,ko,es,de [--only=viduq2,viduq3-pro]
    python scripts/og_vidu.py --langs=en
截图前用 JS 量 DOM，标题/副标题/标签越界或重叠时自动缩小字号再出图；出图后删除临时 HTML。

Writes temporary HTML to .playwright-mcp/vidu-og/ and screenshots each card
to assets/og/<slug>-<lang>.png: run python scripts/preview.py, open
http://localhost:8765/.playwright-mcp/vidu-og/<slug>-<lang>.html at
1200x630 in Playwright, screenshot, then delete .playwright-mcp/vidu-og/. Background
frames are the local Vidu poster images; logo is the pinned lobe-icons SVG.
"""

import glob
import os
import re
import subprocess
import sys
from pathlib import Path

from vidu_data import MODELS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".playwright-mcp" / "vidu-og"
ICON = (ROOT / "assets/icons/vidu-color.svg").read_text(encoding="utf-8")
ICON = re.sub(r"<title>.*?</title>", "", ICON).replace('height="1em"', 'height="64"').replace('width="1em"', 'width="64"')

CARDS = [dict(slug="vidu", name="Vidu API", media="football",
              sub_zh="Q4 · Q3 · Q2 视频与图像，一个 Key 全部接入", sub_en="Q4, Q3 and Q2 video plus image, one API key",
              tags_zh=["7 个模型", "视频 $0.0223 起", "并发不限", "对公 · 专票"],
              tags_en=["7 models", "Video from $0.0223", "Unlimited concurrency", "Self-service invoices"], start_en="")]
for m in MODELS:
    CARDS.append(dict(slug=m["slug"], name=m["name"] + " API", media=m["media"], start_en=m["start_en"],
                      sub_zh=m["title_zh"] + " · " + m["id"], sub_en=m["title_en"] + " · " + m["id"],
                      tags_zh=m["caps_zh"][:2] + [f'${m["start"]} 起', "并发不限"],
                      tags_en=m["caps_en"][:2] + [f'From ${m["start"]}', "Unlimited concurrency"]))

NEW = ("ja", "ko", "es", "de")
LANGATTR = {"zh": "zh-CN", "en": "en", "ja": "ja", "ko": "ko", "es": "es", "de": "de"}


def L(ja, ko, es, de):
    return dict(ja=ja, ko=ko, es=es, de=de)


# 副标题（原为 title_en + " · " + id，id 保持原样）
SUB_I18N = {
    "vidu": L("Q4・Q3・Q2 の動画と画像を 1 つの API キーで", "Q4·Q3·Q2 비디오와 이미지를 API 키 하나로",
              "Vídeo e imagen de Q4, Q3 y Q2 con una sola clave API", "Q4-, Q3- und Q2-Video plus Bild mit einem API-Key"),
    "viduq4-preview": L("4K 対応の画像・参照から動画", "4K 이미지·참조 비디오", "Vídeo de imagen y referencia en 4K", "4K-Video aus Bild und Referenz"),
    "viduq3-pro": L("ネイティブ音声付きの動画生成", "네이티브 오디오 비디오 생성", "Vídeo con audio nativo", "Video mit nativem Audio"),
    "viduq3-turbo": L("音声付きの高速動画", "오디오 포함 빠른 비디오", "Vídeo rápido con audio", "Schnelles Video mit Audio"),
    "viduq2-pro": L("画像・最初と最後のフレームから動画", "이미지·첫/마지막 프레임 비디오",
                    "Vídeo desde imagen y primer/último fotograma", "Video aus Bild und erstem/letztem Frame"),
    "viduq2": L("テキスト・参照から動画", "텍스트·참조 비디오", "Vídeo de texto y de referencia", "Text- und Referenz-Video"),
    "viduq2-turbo": L("高速な画像から動画", "빠른 이미지→비디오", "Imagen a vídeo rápido", "Schnelles Bild-zu-Video"),
    "vidu-image-q2": L("テキスト・参照から画像", "텍스트·참조 이미지 생성", "Imágenes desde texto y referencia", "Bilder aus Text und Referenz"),
}
# 标签词表，键为英文图上的原文；缺词直接 KeyError，不回退英文
TXT = {
    "7 models": L("7 モデル", "모델 7개", "7 modelos", "7 Modelle"),
    "Unlimited concurrency": L("同時実行数の上限なし", "동시 실행 제한 없음", "Sin límite de RPM", "Kein RPM-Limit"),
    "Self-service invoices": L("請求書を自分で発行", "인보이스 직접 발급", "Facturas en consola", "Rechnungen im Konto"),
    "Image to video": L("画像から動画", "이미지→비디오", "Imagen a vídeo", "Bild-zu-Video"),
    "Reference to video": L("参照から動画", "참조→비디오", "Referencia a vídeo", "Referenz-zu-Video"),
    "Native audio": L("ネイティブ音声", "네이티브 오디오", "Audio nativo", "Natives Audio"),
    "Smart shot transitions": L("スマートなショット切り替え", "스마트 샷 전환", "Transiciones de plano inteligentes", "Smarte Szenenwechsel"),
    "Faster than Q3 Pro": L("Q3 Pro より高速", "Q3 Pro보다 빠름", "Más rápido que Q3 Pro", "Schneller als Q3 Pro"),
    "First & last frame": L("最初と最後のフレーム", "첫·마지막 프레임", "Primer y último fotograma", "Erstes & letztes Frame"),
    "Text to video": L("テキストから動画", "텍스트→비디오", "Texto a vídeo", "Text-zu-Video"),
    "Reference video (images / subjects)": L("参照動画（画像・被写体）", "참조 비디오(이미지·피사체)",
                                             "Vídeo de referencia (imágenes / sujetos)", "Referenzvideo (Bilder / Motive)"),
    "Fast generation": L("高速生成", "빠른 생성", "Generación rápida", "Schnelle Generierung"),
    "Text to image": L("テキストから画像", "텍스트→이미지", "Texto a imagen", "Text-zu-Bild"),
    "Reference images (1–7)": L("参照画像（1〜7 枚）", "참조 이미지(1–7장)", "Imágenes de referencia (1–7)", "Referenzbilder (1–7)"),
    "Video from": L("動画 {p} から", "비디오 {p}부터", "Vídeo desde {p}", "Video ab {p}"),
}
PRICE = {  # 起步价句式，{p} 为 "$x"
    "second": L("1秒 {p} から", "초당 {p}부터", "desde {p} / segundo", "ab {p} / Sekunde"),
    "first": L("最初の1秒 {p} から", "첫 1초 {p}부터", "desde {p} por el primer segundo", "ab {p} für die erste Sekunde"),
    "image": L("1枚 {p} から", "이미지당 {p}부터", "desde {p} / imagen", "ab {p} / Bild"),
}


def money(amount, lang):
    """西班牙语、德语小数用逗号，日韩用点；仍为美元。"""
    return "$" + (amount.replace(".", ",") if lang in ("es", "de") else amount)


def new_tags(c, lang):
    """新语言标签：与英文图一一对应，逐项查词表。"""
    out = []
    for t in c["tags_en"]:
        if t.startswith("From $"):
            unit = "image" if c["slug"] == "vidu-image-q2" else ("first" if c["start_en"].startswith("first") else "second")
            out.append(PRICE[unit][lang].format(p=money(t[6:], lang)))
        elif t.startswith("Video from $"):
            out.append(TXT["Video from"][lang].format(p=money(t[12:], lang)))
        else:
            out.append(TXT[t][lang])
    return out


TPL = """<!doctype html><html lang="__LANG__"><head><meta charset="utf-8"><style>
*{margin:0;box-sizing:border-box}html,body{width:1200px;height:630px;overflow:hidden;position:relative;background:#020b13;color:#fff;
font-family:-apple-system,"PingFang SC","Microsoft YaHei","Segoe UI",Arial,sans-serif}
html[lang=ja] body{font-family:-apple-system,"Yu Gothic UI","Meiryo","Segoe UI",Arial,sans-serif}
html[lang=ko] body{font-family:-apple-system,"Malgun Gothic","Segoe UI",Arial,sans-serif}
.bg{position:absolute;inset:0;background:url(../../assets/models/vidu/__MEDIA__.webp) center/cover}
.sh{position:absolute;inset:0;background:linear-gradient(90deg,#020b13 0%,rgba(2,11,19,.86) 42%,rgba(2,11,19,.2) 78%),linear-gradient(0deg,rgba(2,11,19,.8),transparent 45%)}
.c{position:absolute;left:72px;top:64px;right:72px;bottom:60px;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:16px;font-size:26px;font-weight:700;letter-spacing:-.3px}
.top span{font-weight:500;color:rgba(255,255,255,.6);padding-left:16px;border-left:1px solid rgba(255,255,255,.25)}
h1{margin-top:auto;font-size:__SIZE__px;line-height:1.02;font-weight:800;letter-spacing:-2px;max-width:820px}
p{margin-top:20px;font-size:30px;color:rgba(255,255,255,.85);max-width:820px}
ul{display:flex;flex-wrap:wrap;gap:12px;margin-top:34px;padding:0;list-style:none}
li{padding:9px 20px;border-radius:999px;font-size:22px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22)}
li:first-child{background:linear-gradient(100deg,#40edd8,#22d5ff 35%,#047ffe);color:#020b13;font-weight:700;border:0}
.n p{font-size:26px}.n li{font-size:19px;padding:8px 16px}.n.k p,.n.k li{word-break:keep-all}
</style></head><body class="__BODY__"><div class="bg"></div><div class="sh"></div><div class="c">
<div class="top">__ICON__AnyAIGC<span>Vidu</span></div><h1>__NAME__</h1><p>__SUB__</p><ul>__TAGS__</ul></div></body></html>"""


# 版面自检：量 DOM，越界/重叠/挤压时整体缩小字号再重量，结果写进 body[data-fit]
FIT_JS = """<script>(function(){
var q=function(x){return document.querySelector(x)},all=function(x){return Array.prototype.slice.call(document.querySelectorAll(x))};
var els=[q('h1'),q('p')].concat(all('li')),base=els.map(function(e){return parseFloat(getComputedStyle(e).fontSize)});
function bad(){var o=[],top=q('.top').getBoundingClientRect(),h=q('h1').getBoundingClientRect(),p=q('p').getBoundingClientRect(),
 ul=q('ul').getBoundingClientRect(),lis=all('li').map(function(e){return e.getBoundingClientRect()});
 els.forEach(function(e){var r=e.getBoundingClientRect();if(r.left<0||r.top<0||r.right>1200||r.bottom>630)o.push('out:'+e.textContent.slice(0,16));
  if(e.scrollWidth>e.clientWidth+1)o.push('clip:'+e.textContent.slice(0,16))});
 if(h.top<top.bottom)o.push('h1-top');if(p.top<h.bottom-1)o.push('p-h1');if(ul.top<p.bottom)o.push('ul-p');if(ul.bottom>571)o.push('ul-bottom');
 for(var i=0;i<lis.length;i++)for(var j=i+1;j<lis.length;j++){var a=lis[i],b=lis[j];
  if(a.left<b.right&&b.left<a.right&&a.top<b.bottom&&b.top<a.bottom)o.push('overlap:'+i+'-'+j)}
 return o}
var k=1,n=0;while(bad().length&&n<14){k*=.93;n++;els.forEach(function(e,i){e.style.fontSize=(base[i]*k).toFixed(2)+'px'})}
document.body.setAttribute('data-fit',JSON.stringify({scale:+k.toFixed(3),steps:n,bad:bad()}));
})()</script>"""


def chrome():
    hits = sorted(glob.glob(os.path.expanduser("~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe")))
    return hits[-1] if hits else None


def render(c, lang, fit=False):
    size = 96 if len(c["name"]) <= 18 else 80
    if lang in NEW:
        sub = SUB_I18N[c["slug"]][lang] + ("" if c["slug"] == "vidu" else " · " + c["slug"])
        tags = new_tags(c, lang)
    else:
        sub, tags = c["sub_" + lang], c["tags_" + lang]
    body = ("n" + (" k" if lang == "ko" else "")) if lang in NEW else ""
    html = (TPL.replace("__LANG__", LANGATTR[lang]).replace("__BODY__", body).replace("__MEDIA__", c["media"])
            .replace("__ICON__", ICON).replace("__NAME__", c["name"]).replace("__SIZE__", str(size))
            .replace("__SUB__", sub).replace("__TAGS__", "".join(f"<li>{t}</li>" for t in tags)))
    return html.replace("</body>", FIT_JS + "</body>") if fit else html


def main():
    langs = ("zh", "en")
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--langs="):
            langs = tuple(a.split("=", 1)[1].split(","))
        elif a.startswith("--only="):
            only = a.split("=", 1)[1].split(",")
    for lang in langs:
        if lang not in LANGATTR:
            raise ValueError(f"Unknown language: {lang}")
    shoot = any(a.startswith("--langs=") for a in sys.argv[1:])
    cards = [c for c in CARDS if only is None or c["slug"] in only]
    if only and len(cards) != len(only):
        raise ValueError("Unknown slug in --only: " + ",".join(set(only) - {c["slug"] for c in cards}))
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for c in cards:
        for lang in langs:
            path = OUT / f'{c["slug"]}-{lang}.html'
            path.write_text(render(c, lang, fit=shoot), encoding="utf-8")
            jobs.append((c["slug"], lang, path, ROOT / "assets/og" / f'{c["slug"]}-{lang}.png'))
    if not shoot:
        print(len(jobs), "cards written to", OUT)
        return
    exe = chrome()
    if not exe:
        raise SystemExit("找不到 Playwright 的 Chromium，无法截图")
    from PIL import Image
    fails = []
    for slug, lang, path, png in jobs:
        url = f"http://localhost:8765/.playwright-mcp/vidu-og/{slug}-{lang}.html"
        flags = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,800", "--virtual-time-budget=6000"]
        dom = subprocess.run(flags + ["--dump-dom", url], capture_output=True, timeout=90).stdout.decode("utf-8", "replace")
        m = re.search(r"data-fit='([^']*)'|data-fit=\"([^\"]*)\"", dom)
        fit = (m.group(1) or m.group(2)).replace("&quot;", '"') if m else "NO-REPORT"
        subprocess.run(flags + [f"--screenshot={png}", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
        path.unlink()
        ok = '"bad":[]' in fit
        if not ok:
            fails.append(f"{slug}-{lang}")
        print("png", png.relative_to(ROOT), png.stat().st_size, "fit", fit, "" if ok else "<-- 违例")
    if not any(OUT.iterdir()):
        OUT.rmdir()
    if fails:
        raise SystemExit("版面自检未通过: " + ", ".join(fails))


if __name__ == "__main__":
    main()
