# 给 Nano Banana 和 GPT Image 两个系列的专题页（zh / en / ja / ko / es / de，共 60 页）加「赠送额度能出多少张图」表。
# 用法：python scripts/gift_tables.py（重复运行结果不变）。
# 口径（用户 2026-11-26 确认）：新用户赠送 500 万 Token，约合 $0.5。张数 = 向下取整（$0.5 / 单张价）。
#   - Nano Banana 中文页：按页面上的人民币单价，$0.5 折 ¥3.35（× 6.7）。其他语言页：1K 按页面上的最低美元价；模型广场没有分档美元价，2K / 4K 按人民币分档价的比例换算（2.1：1.5× / 3.5×；2 和 Pro：1K = 2K，4K 另算），页面注明是估算。
#   - GPT Image：按 Token 计费的型号只算图片输出 Token（和页面上「每张图大概多少钱」同一套 Token 数），不含输入；-c 版按张单价。
# 插入位置：成本示例列表之后、价格版块的按钮之前，用 <!-- GIFT --> 包起来。
# 重新生成 nano_banana_pages.py / gpt_image_pages.py 或重新翻译 ja/ko/es/de 之后，要重跑本脚本（和 trust.py 一样）。
import io
import os
import re
import sys
from decimal import Decimal, ROUND_FLOOR

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gpt_image_data as GD  # noqa: E402
import nano_banana_data as ND  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ('zh', 'en', 'ja', 'ko', 'es', 'de')
GIFT_USD = Decimal('0.5')
GIFT_CNY = Decimal('3.35')  # 0.5 × 6.7

NANO = ['nano-banana', 'nano-banana-2.1', 'nano-banana-2', 'nano-banana-pro']
GPT = list(GD.SLUGS)
NANO_NAMES = {'nano-banana-2.1': 'Nano Banana 2.1', 'nano-banana-2': 'Nano Banana 2', 'nano-banana-pro': 'Nano Banana Pro'}

T = {
    'zh': dict(
        h3='赠送的 500 万 Token 能出多少张图',
        lead_nano='新用户赠送 500 万 Token，约合 $0.5（¥3.35）。按上表单价，可以生成的图片数量如下（向下取整）。',
        lead_gpt='新用户赠送 500 万 Token，约合 $0.5（¥3.35）。下表按上面的单价，列出不同质量和尺寸下可以生成的图片数量（向下取整）。',
        cap='赠送额度可生成的图片数量（张）', model='型号', quality='质量',
        nano_cols=('1K', '2K', '4K'),
        nano_note='按成功提交计费。实际张数以模型广场实时价格为准。',
        tok='只算图片输出 Token。提示词和参考图还会产生输入 Token，实际张数会略少。',
        c_split='按张计费的 {c} 版：1K 每张 {p1}，约 {n1} 张；2K / 4K 每张 {p2}，约 {n2} 张。',
        c_same='按张计费的 {c} 版：1K / 2K / 4K 每张 {p1}，约 {n1} 张。',
        live='实时价格以模型广场为准。',
        ov_cols=('按 Token 计费（medium，1024×1024）', '按张计费 -c 版（1K）')),
    'en': dict(
        h3='How many images the 5M free tokens cover',
        lead_nano='New accounts get 5M free tokens, worth about $0.5. At the prices above, that covers this many images (rounded down).',
        lead_gpt='New accounts get 5M free tokens, worth about $0.5. At the prices above, this is how many images each quality and size covers (rounded down).',
        cap='Images you can generate with the free credit', model='Model', quality='Quality',
        nano_cols=('Price from (1K)', 'Images'),
        nano_note="The 1K count uses the from price above. 2K and 4K counts are estimates based on AnyAIGC's price ratio between resolutions. Live prices are in the model catalog.",
        tok='Counts cover image output tokens only. Prompt text and reference images add input tokens, so you will get slightly fewer.',
        c_split='The flat per-image {c} version costs {p1} at 1K (about {n1} images) and {p2} at 2K / 4K (about {n2} images).',
        c_same='The flat per-image {c} version costs {p1} at 1K / 2K / 4K (about {n1} images).',
        live='Live prices are in the model catalog.',
        ov_cols=('Token billing (medium, 1024×1024)', 'Per-image -c version (1K)')),
    'ja': dict(
        h3='無料の500万トークンで生成できる枚数',
        lead_nano='新規アカウントには500万トークンが付与されます（約$0.5相当）。上記の料金で生成できる枚数は次のとおりです（小数点以下切り捨て）。',
        lead_gpt='新規アカウントには500万トークンが付与されます（約$0.5相当）。上記の料金で、品質とサイズごとに生成できる枚数は次のとおりです（小数点以下切り捨て）。',
        cap='無料枠で生成できる画像の枚数', model='モデル', quality='品質',
        nano_cols=('料金（1K、最低価格）', '枚数'),
        nano_note='1Kの枚数は上記の最低価格で計算しています。2Kと4Kは解像度ごとの料金比で換算した目安です。最新の料金はモデル一覧で確認してください。',
        tok='枚数は画像出力トークンのみで計算しています。プロンプトや参照画像の入力トークンが加わるため、実際はやや少なくなります。',
        c_split='1枚あたり固定料金の {c} 版は、1K で {p1}（約{n1}枚）、2K / 4K で {p2}（約{n2}枚）です。',
        c_same='1枚あたり固定料金の {c} 版は、1K / 2K / 4K いずれも {p1}（約{n1}枚）です。',
        live='最新の料金はモデル一覧で確認してください。',
        ov_cols=('トークン課金（medium、1024×1024）', '1枚課金の -c 版（1K）')),
    'ko': dict(
        h3='무료 토큰 500만 개로 만들 수 있는 이미지 수',
        lead_nano='신규 계정에는 토큰 500만 개가 제공되며 약 $0.5에 해당합니다. 위 가격 기준으로 생성할 수 있는 이미지 수는 다음과 같습니다(소수점 이하 버림).',
        lead_gpt='신규 계정에는 토큰 500만 개가 제공되며 약 $0.5에 해당합니다. 위 가격 기준으로 품질과 크기별 생성 가능한 이미지 수는 다음과 같습니다(소수점 이하 버림).',
        cap='무료 크레딧으로 생성할 수 있는 이미지 수', model='모델', quality='품질',
        nano_cols=('가격 (1K, 최저)', '이미지 수'),
        nano_note='1K 이미지 수는 위의 최저 가격 기준입니다. 2K와 4K는 해상도별 가격 비율로 환산한 추정치입니다. 실시간 가격은 모델 카탈로그에서 확인하세요.',
        tok='이미지 출력 토큰만 계산한 수치입니다. 프롬프트와 참조 이미지의 입력 토큰이 추가되므로 실제 장수는 조금 더 적습니다.',
        c_split='장당 고정 요금인 {c} 버전은 1K가 {p1}(약 {n1}장), 2K / 4K가 {p2}(약 {n2}장)입니다.',
        c_same='장당 고정 요금인 {c} 버전은 1K / 2K / 4K 모두 {p1}(약 {n1}장)입니다.',
        live='실시간 가격은 모델 카탈로그에서 확인하세요.',
        ov_cols=('토큰 과금 (medium, 1024×1024)', '장당 과금 -c 버전 (1K)')),
    'es': dict(
        h3='Cuántas imágenes cubren los 5M de tokens gratis',
        lead_nano='Las cuentas nuevas reciben 5M de tokens gratis, equivalentes a unos $0.5. Con los precios de arriba, alcanzan para esta cantidad de imágenes (redondeado hacia abajo).',
        lead_gpt='Las cuentas nuevas reciben 5M de tokens gratis, equivalentes a unos $0.5. Con los precios de arriba, esta es la cantidad de imágenes que cubre cada calidad y tamaño (redondeado hacia abajo).',
        cap='Imágenes que se pueden generar con el crédito gratis', model='Modelo', quality='Calidad',
        nano_cols=('Precio desde (1K)', 'Imágenes'),
        nano_note='La cifra de 1K usa el precio inicial de arriba. Las de 2K y 4K son estimaciones según la proporción de precios entre resoluciones. Los precios en vivo están en el catálogo de modelos.',
        tok='Las cifras solo cuentan los tokens de salida de la imagen. El texto del prompt y las imágenes de referencia añaden tokens de entrada, así que saldrán algunas menos.',
        c_split='La versión {c}, con precio fijo por imagen, cuesta {p1} en 1K (unas {n1} imágenes) y {p2} en 2K / 4K (unas {n2} imágenes).',
        c_same='La versión {c}, con precio fijo por imagen, cuesta {p1} en 1K / 2K / 4K (unas {n1} imágenes).',
        live='Los precios en vivo están en el catálogo de modelos.',
        ov_cols=('Facturación por token (medium, 1024×1024)', 'Versión -c por imagen (1K)')),
    'de': dict(
        h3='Wie viele Bilder die 5 Mio. Gratis-Tokens abdecken',
        lead_nano='Neue Konten erhalten 5 Mio. Gratis-Tokens, das entspricht etwa $0.5. Mit den obigen Preisen reicht das für folgende Bildanzahl (abgerundet).',
        lead_gpt='Neue Konten erhalten 5 Mio. Gratis-Tokens, das entspricht etwa $0.5. Mit den obigen Preisen reicht das für folgende Bildanzahl pro Qualität und Größe (abgerundet).',
        cap='Mit dem Gratis-Guthaben erzeugbare Bilder', model='Modell', quality='Qualität',
        nano_cols=('Preis ab (1K)', 'Bilder'),
        nano_note='Die 1K-Zahl nutzt den Einstiegspreis oben. Die Zahlen für 2K und 4K sind Schätzwerte nach dem Preisverhältnis zwischen den Auflösungen. Aktuelle Preise stehen im Modellkatalog.',
        tok='Die Zahlen berücksichtigen nur die Bildausgabe-Tokens. Prompt-Text und Referenzbilder verbrauchen zusätzlich Eingabe-Tokens, daher sind es in der Praxis etwas weniger Bilder.',
        c_split='Die {c}-Version mit festem Preis pro Bild kostet bei 1K {p1} (etwa {n1} Bilder) und bei 2K / 4K {p2} (etwa {n2} Bilder).',
        c_same='Die {c}-Version mit festem Preis pro Bild kostet bei 1K / 2K / 4K {p1} (etwa {n1} Bilder).',
        live='Aktuelle Preise stehen im Modellkatalog.',
        ov_cols=('Token-Abrechnung (medium, 1024×1024)', '-c-Version pro Bild (1K)')),
}


def floor_div(total, price):
    return int((Decimal(total) / Decimal(str(price))).to_integral_value(rounding=ROUND_FLOOR))


def table(caption, head, rows):
    th = ''.join(f'<th scope="col"{"" if i == 0 else " class=\"o-num\""}>{h}</th>' for i, h in enumerate(head))
    body = ''.join(f'            <tr>{r}</tr>\n' for r in rows)
    return ('      <div class="o-table-wrap o-reveal">\n        <table class="o-table">\n'
            f'          <caption class="o-sr">{caption}</caption>\n          <thead><tr>{th}</tr></thead>\n'
            f'          <tbody>\n{body}          </tbody>\n        </table>\n      </div>\n')


def row(label, cells):
    return f'<th scope="row">{label}</th>' + ''.join(f'<td class="o-num">{c}</td>' for c in cells)


# ---------------------------------------------------------------- Nano Banana
def nano_block(lang, slug):
    t = T[lang]
    slugs = ['nano-banana-2.1', 'nano-banana-pro', 'nano-banana-2'] if slug == 'nano-banana' else [slug]
    rows = []
    if lang == 'zh':
        head = [t['model']] + list(t['nano_cols'])
        for s in slugs:
            tiers = {}
            for res, p in ND.CNY[s]:
                for r in res.split('/'):
                    tiers[r.strip()] = floor_div(GIFT_CNY, p)
            rows.append(row(NANO_NAMES[s], [tiers['1K'], tiers['2K'], tiers['4K']]))
        cap = f'Nano Banana {t["cap"]}'
    else:
        head = [t['model'], '1K', '2K', '4K']
        for s in slugs:
            # 1K = 页面上的最低美元价；2K / 4K 按人民币分档价相对 1K 的比例换算
            cny = {r.strip(): Decimal(p) for res, p in ND.CNY[s] for r in res.split('/')}
            tiers = [Decimal(ND.USD[s]) * cny[k] / cny['1K'] for k in ('1K', '2K', '4K')]
            rows.append(row(NANO_NAMES[s], [floor_div(GIFT_USD, x) for x in tiers]))
        cap = f'Nano Banana: {t["cap"]}'
    inner = table(cap, head, rows)
    return t, inner, t['lead_nano'], t['nano_note'], 'nb-h3'


# ---------------------------------------------------------------- GPT Image
def gpt_cost(base, q, size):
    if base == '2':
        return GD.cost_2(q, size)[0]
    if base == '2.5':
        return GD.cost_25(q, size)[0]
    return GD.cost_26(q, size)


def gpt_block(lang, slug):
    t = T[lang]
    if slug == 'gpt-image':
        head = [t['model']] + list(t['ov_cols'])
        rows = []
        for label, base in (('GPT Image 2.6 Sunburst / Flare', '2.6'), ('GPT Image 2.5 Sunburst / Flare', '2.5'), ('GPT Image 2', '2')):
            tok = floor_div(GIFT_USD, repr(round(gpt_cost(base, 'medium', '1024x1024'), 10)))
            call = floor_div(GIFT_USD, GD.CALL[base])
            rows.append(row(label, [tok, call]))
        inner = table(f'GPT Image: {t["cap"]}', head, rows)
        return t, inner, t['lead_gpt'], f'{t["tok"]} {t["live"]}', 'gi-h3'
    base = GD.MODELS[slug]['base']
    if base == '2':
        sizes, quals = ['1024x1024', '1024x1536', '1536x1024'], ['low', 'medium', 'high']
    else:
        sizes, quals = ['1024x1024', '1536x1024', '2048x2048', '3840x2160'], ['low', 'medium', 'high', 'xhigh', 'max']
    head = [t['quality']] + [s.replace('x', '×') for s in sizes]
    rows = [row(f'<code>{q}</code>', [floor_div(GIFT_USD, repr(round(gpt_cost(base, q, s), 10))) for s in sizes]) for q in quals]
    inner = table(f'{GD.MODELS[slug]["name"]}: {t["cap"]}', head, rows)
    cname = f'<code>{GD.C_OF[slug][0]}</code>'
    p1, p2 = GD.CALL[base], GD.CALL_4K[base]

    def shown(p, tier):
        # 中文页的按张价写人民币（× 6.7，和首屏一致），括号里附美元价
        return f'{GD.cny(base, tier)}（${p}）' if lang == 'zh' else '$' + p
    if p1 == p2:
        c_note = t['c_same'].format(c=cname, p1=shown(p1, '1k'), n1=floor_div(GIFT_USD, p1))
    else:
        c_note = t['c_split'].format(c=cname, p1=shown(p1, '1k'), n1=floor_div(GIFT_USD, p1), p2=shown(p2, '4k'), n2=floor_div(GIFT_USD, p2))
    return t, inner, t['lead_gpt'], f'{t["tok"]} {c_note} {t["live"]}', 'gi-h3'


def block(lang, slug):
    t, tbl, lead, note, h3cls = nano_block(lang, slug) if slug in NANO else gpt_block(lang, slug)
    return ('      <!-- GIFT -->\n'
            f'      <h3 class="{h3cls} o-reveal">{t["h3"]}</h3>\n'
            f'      <p class="o-note">{lead}</p>\n'
            f'{tbl}'
            f'      <p class="o-note">{note}</p>\n'
            '      <!-- /GIFT -->\n')


def apply(path, lang, slug):
    s = io.open(path, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    s = s.replace('\r\n', '\n')
    o = s
    s = re.sub(r'      <!-- GIFT -->.*?<!-- /GIFT -->\n', '', s, flags=re.S)
    start = s.index('<ul class="o-costs">')
    end = s.index('</ul>\n', start) + len('</ul>\n')
    s = s[:end] + block(lang, slug) + s[end:]
    if s != o:
        io.open(path, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
        return True
    return False


def main():
    done = []
    for lang in LANGS:
        for slug in NANO + GPT:
            p = os.path.join(ROOT, lang, 'models', slug + '.html')
            if apply(p, lang, slug):
                done.append(f'{lang}/{slug}')
    print(f'updated {len(done)} pages')


if __name__ == '__main__':
    main()
