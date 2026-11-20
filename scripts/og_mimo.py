"""Write 1200x630 Xiaomi MiMo sharing-card HTML for Playwright screenshots.

Usage:
    python scripts/og_mimo.py   -> .playwright-mcp/mimo-og/<slug>-<lang>.html (zh、en)
    python scripts/og_mimo.py --langs=ja,ko,es,de
        -> 用 Chrome headless 直接截图到 assets/og/<slug>-<lang>.png（Pillow 裁成 1200x630，临时 html 用完删除）
    python scripts/og_mimo.py --langs=en   -> 只重出英文图
Then (with python scripts/preview.py running) open
http://localhost:8765/.playwright-mcp/mimo-og/<slug>-<lang>.html at 1200x630 and
capture assets/og/<slug>-<lang>.png. Uses the official V2.6 halftone poster
already in assets/models/mimo/ and the pinned lobe-icons logo.
"""
import glob
import os
import subprocess
import sys
from html import escape
from pathlib import Path

from mimo_data import MODELS, MODEL_BY_SLUG, SLUGS, deal
from mimo_pages import mark

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".playwright-mcp" / "mimo-og"

CSS = """
*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{background:#fcfaf8;color:#1a1a1a;font-family:Inter,-apple-system,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;position:relative}
.art{position:absolute;right:-40px;top:0;width:620px;height:630px;background:url(/assets/models/mimo/hero.webp) 58% 50%/cover;
 -webkit-mask-image:linear-gradient(90deg,transparent,#000 38%);mask-image:linear-gradient(90deg,transparent,#000 38%)}
.dots{position:absolute;right:-40px;top:0;width:620px;height:630px;background-color:#f3f1ea;
 background-image:radial-gradient(circle,rgba(82,110,62,.55) 1.8px,transparent 2.2px),radial-gradient(circle,rgba(82,110,62,.3) 1.8px,transparent 2.2px);
 background-size:14px 14px;background-position:0 0,7px 7px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 38%);mask-image:linear-gradient(90deg,transparent,#000 38%)}
.dots b{position:absolute;right:90px;top:200px;font:700 190px/1 Georgia,serif;color:#526e3e}
.main{position:absolute;left:72px;top:64px;width:700px}
.brand{display:flex;align-items:center;gap:14px;font-weight:700;font-size:26px}
.brand i{font-style:normal;color:rgba(0,0,0,.4);font-weight:400}
h1{margin:70px 0 0;font:400 76px/1.08 "LXGW WenKai","Kaiti SC","STKaiti","KaiTi",Georgia,serif;letter-spacing:.01em}
h1 small{display:block;margin-top:18px;font-size:34px;color:#333}
.deal{display:inline-flex;align-items:center;gap:14px;margin-top:34px;padding:6px 22px 6px 6px;border-radius:999px;background:#fff;border:1.5px solid #ffd2b0}
.deal b{background:#ff6700;color:#fff;border-radius:999px;padding:8px 18px;font-size:24px}
.deal span{font-size:22px;color:#5a2a06}
.old{background:#ece7df;border-color:#e0d8cc}.old b{background:#5d4c46}
.tags{position:absolute;left:72px;bottom:58px;display:flex;gap:12px;margin:0;padding:0;list-style:none}
.tags li{padding:8px 18px;border-radius:999px;background:#f0ebe5;font-size:20px;color:#333}
.n{font-family:Inter,-apple-system,"Yu Gothic UI","Malgun Gothic","Segoe UI",sans-serif}
.n h1 small{font-size:28px;line-height:1.3;margin-top:14px}
.n.ko h1 small,.n.ko .deal span{word-break:keep-all}
.n .deal span{font-size:20px}.n .deal b{font-size:21px;white-space:nowrap}
.n .tags{gap:8px}.n .tags li{font-size:17px;padding:8px 14px;white-space:nowrap}
"""

TEXT = {
    "mimo": {"zh": ("Xiaomi MiMo API", "官方 4 折，接入 V2.6 全模态旗舰"), "en": ("Xiaomi MiMo API", "V2.6 omni-modal models at 60% off")},
}

NEW = ("ja", "ko", "es", "de")
LANGATTR = {"zh": "zh-CN", "en": "en", "ja": "ja", "ko": "ko", "es": "es", "de": "de"}


def _t(ja, ko, es, de):
    return {"ja": ja, "ko": ko, "es": es, "de": de}


# 新语言词表：英文原文 -> 译文。缺词直接 KeyError，不回退英文。
TXT = {
    "About 60% off": _t("約60%オフ", "약 60% 저렴", "Un 60 % menos", "Rund 60 % günstiger"),
    "Retired": _t("提供終了", "지원 종료", "Retirado", "Eingestellt"),
    "Replacement at about 60% off": _t("後継モデルは約60%オフ", "대체 모델은 약 60% 저렴", "El reemplazo cuesta un 60 % menos", "Nachfolger rund 60 % günstiger"),
    "1M context": _t("1Mコンテキスト長", "1M 컨텍스트", "Contexto de 1M", "1M Kontext"),
    "OpenAI compatible": _t("OpenAI 互換", "OpenAI 호환", "Compatible con OpenAI", "OpenAI-kompatibel"),
    "Unlimited concurrency": _t("同時実行数の上限なし", "동시 실행 제한 없음", "Sin límite de RPM", "Kein RPM-Limit"),
    "Self-service invoices": _t("請求書を自分で発行", "인보이스 직접 발급", "Facturas en consola", "Rechnungen im Konto"),
    "Drop-in migration": _t("model を変えるだけで移行", "model만 바꾸면 이전 완료", "Migra cambiando solo model", "Umstieg nur über model"),
    "input": _t("入力", "입력", "entrada", "Eingabe"),
    "official": _t("公式", "공식", "oficial", "offiziell"),
}
SUB_I18N = {
    "mimo": _t("V2.6 オムニモーダルモデルが約60%オフ", "V2.6 옴니모달 모델 약 60% 저렴",
               "Modelos omnimodales V2.6 con un 60 % menos", "Omnimodale V2.6-Modelle, rund 60 % günstiger"),
    "mimo-v2.6-pro": _t("Xiaomi MiMo の現行オムニモーダル・フラッグシップ", "Xiaomi MiMo의 현재 옴니모달 플래그십",
                        "El modelo insignia omnimodal actual de Xiaomi MiMo", "Das aktuelle omnimodale Flaggschiff von Xiaomi MiMo"),
    "mimo-v2.6-flash": _t("オムニモーダルで高性能、低コストで効率的", "옴니모달, 높은 성능, 낮은 비용의 효율",
                          "Omnimodal, capaz y eficiente a bajo coste", "Omnimodal, leistungsstark und günstig im Betrieb"),
}
RETIRED_SUB = {"ja": "提供終了 · {n} へ移行", "ko": "지원 종료 · {n}로 이전", "es": "Retirado · pasa a {n}", "de": "Eingestellt · Wechsel zu {n}"}


def tx(lang, en):
    return TXT[en][lang]


def price_line(lang, amount, official, prefix=""):
    """新语言的价格行：'<prefix>入力 $x · 公式 $y'（价格取自 mimo_data，与英文图一致）。"""
    word = tx(lang, "input")
    if not prefix:
        word = word[0].upper() + word[1:]
    return f"{prefix}{word} ${amount} · {tx(lang, 'official')} ${official}"


def page(lang, slug):
    model = MODEL_BY_SLUG.get(slug)
    zh = lang == "zh"
    nw = lang in NEW
    if model is None:
        title = "Xiaomi MiMo API"
        sub = SUB_I18N["mimo"][lang] if nw else TEXT["mimo"][lang][1]
        if nw:
            detail = price_line(lang, "0.0563", "0.14", prefix="V2.6-Flash ")
        else:
            detail = "V2.6-Flash 输入 $0.0563 · 官方 $0.14" if zh else "V2.6-Flash input $0.0563 · official $0.14"
        chip, cls = (tx(lang, "About 60% off") if nw else deal(lang)), ""
    elif model["legacy"]:
        succ = MODEL_BY_SLUG[model["successor"]]
        title = model["name"] + " API"
        if nw:
            sub = RETIRED_SUB[lang].format(n=succ["name"])
            detail = tx(lang, "Replacement at about 60% off")
            chip = tx(lang, "Retired")
        else:
            sub = ("官方已停用 · 迁移到 " + succ["name"]) if zh else ("Retired · move to " + succ["name"])
            detail = "替代型号约官方 4 折" if zh else "Replacement at about 60% off"
            chip = "已停用" if zh else "Retired"
        cls = " old"
    else:
        p = model["prices"][0]
        title = model["name"] + " API"
        if nw:
            sub = SUB_I18N[slug][lang]
            detail = price_line(lang, p["amount"], p["official"])
            chip = tx(lang, "About 60% off")
        else:
            sub = model["tagline_" + lang]
            detail = (f'输入 ${p["amount"]} · 官方 ${p["official"]}' if zh else f'Input ${p["amount"]} · official ${p["official"]}')
            chip = deal(lang)
        cls = ""
    if zh:
        tags = ["1M 上下文", "OpenAI 兼容", "并发不限", "对公 · 专票"]
        if model and model["legacy"]:
            tags[0] = "迁移只改 model"
    else:
        # 英文图用海外口径：自助开票，不写对公 / 合同
        tags = ["1M context", "OpenAI compatible", "Unlimited concurrency", "Self-service invoices"]
        if model and model["legacy"]:
            tags[0] = "Drop-in migration"
        if nw:
            tags = [tx(lang, t) for t in tags]
    art = '<div class="dots"><b>' + escape(model["short"].split(" ")[0]) + "</b></div>" if model and model["legacy"] else '<div class="art"></div>'
    lis = "".join(f"<li>{escape(t)}</li>" for t in tags)
    htmlcls = f' class="n {lang}"' if nw else ""
    return (f'<!doctype html><html lang="{LANGATTR[lang]}"{htmlcls}><head><meta charset="utf-8"><title>{escape(title)}</title><style>{CSS}</style></head><body{htmlcls}>'
     f'{art}<div class="main"><div class="brand">AnyAIGC <i>×</i> {mark("#1a1a1a", "m", 40)} Xiaomi MiMo</div>'
     f'<h1>{escape(title)}<small>{escape(sub)}</small></h1>'
     f'<div class="deal{cls}"><b>{escape(chip)}</b><span>{escape(detail)}</span></div></div><ul class="tags">{lis}</ul></body></html>')


def chrome():
    hits = sorted(glob.glob(os.path.expanduser("~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe")))
    return hits[-1] if hits else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = [a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--langs=")]
    if not only:
        for lang in ("zh", "en"):
            for slug in SLUGS:
                (OUT / f"{slug}-{lang}.html").write_text(page(lang, slug), encoding="utf-8")
                print(f"{slug}-{lang}.html")
        return
    from PIL import Image
    for lang in only[0]:
        for slug in SLUGS:
            hp = OUT / f"{slug}-{lang}.html"
            hp.write_text(page(lang, slug), encoding="utf-8")
            png = ROOT / "assets" / "og" / f"{slug}-{lang}.png"
            subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,800",
                            "--virtual-time-budget=6000", f"--screenshot={png}",
                            f"http://localhost:8765/.playwright-mcp/mimo-og/{slug}-{lang}.html"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            Image.open(png).crop((0, 0, 1200, 630)).save(png, optimize=True)
            hp.unlink()
            print("png", png.relative_to(ROOT), png.stat().st_size)


if __name__ == "__main__":
    main()
