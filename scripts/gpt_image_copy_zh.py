# GPT Image 系列专题页中文文案。build(slug) 返回页面用的字典。
from gpt_image_data import (TOKEN, OFFICIAL, CALL, MODELS, TOKENS_25, OFFICIAL_IMG_2, PRICING, SUPPORT,
                            DOCS_GEN_2, DOCS_EDIT_2, DOCS_GEN_25, DOCS_EDIT_25, OFFICIAL_GUIDE, CALL_CNY, C_OF, cny, money, cost_25, cost_2, save)
import gpt_image_layout as G

T2, T25 = TOKEN['2'], TOKEN['2.5']
S2 = save(T2['out'], OFFICIAL['out'])     # 92
S25 = save(T25['out'], OFFICIAL['out'])   # 41

SIZE_RULES = '最长边不超过 3840px，宽高都是 16 的倍数，长短边比例不超过 3:1，总像素在 655,360 到 8,294,400 之间'
CONC = '并发不限'

FAMILY = [
    ('gpt-image', '总览', 'GPT Image 全系', '3 个型号的价格对比与选型'),
    ('gpt-image-2.5-sunburst', '最新', 'GPT Image 2.5 Sunburst', f'编辑精度最高的旗舰 · 输出 ${T25["out"]} / 1M'),
    ('gpt-image-2.5-flare', '最新', 'GPT Image 2.5 Flare', f'速度最快，日常批量出图 · 输出 ${T25["out"]} / 1M'),
    ('gpt-image-2', '', 'GPT Image 2', f'2026 年 4 月发布 · 输出 ${T2["out"]} / 1M'),
]

COMMON_FAQ = [
    ('AnyAIGC 能开发票吗？支持增值税专票吗？',
     '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
    ('企业可以对公转账和签合同吗？',
     f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
]
LICENSE_FAQ = ('生成的图片可以商用吗？',
               '图片的使用权和内容政策以 OpenAI 官方条款为准。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用；涉及人物肖像、品牌商标等内容时，请自行确认授权。')


def conc_faq(name):
    return ('并发有限制吗？国内能直接调用吗？',
            f'AnyAIGC 对 {name} 不设并发限制，所有用户默认享有。接口地址是 <code>https://anyaigc.ai/v1</code>，面向国内网络优化，通常无需额外代理；按美元计费，支持微信支付和支付宝，同一个 Key 还能调用平台上 300+ 其他模型。')


def code_gen(model, size='1536x1024', quality='medium', n=True, prompt='产品静物：哑光黑机械键盘，影棚灯光，画面中没有文字'):
    nline = '\n        "n": 1,' if n else ''
    py = f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{prompt}",
        "size": "{size}",
        "quality": "{quality}",
        "format": "webp",
        "response_format": "url",{nline}
    }},
    timeout=300,
)
resp.raise_for_status()
image_url = resp.json()["data"][0]["url"]

# 下载图片到本地
with open("output.webp", "wb") as f:
    f.write(requests.get(image_url, timeout=120).content)
print("已保存 output.webp")'''
    ncurl = ',\n    "n": 1' if n else ''
    curl = f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "{prompt}",
    "size": "{size}",
    "quality": "{quality}",
    "format": "webp",
    "response_format": "url"{ncurl}
  }}\''''
    return curl, py


def code_edit(model, mask=True):
    mask_part = '''
# 局部重绘：mask 的透明区域是要重画的部分（PNG，小于 4MB，与原图同尺寸）
# files.append(("mask", open("mask.png", "rb")))''' if mask else ''
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

# 可以上传多张参考图（少于 16 张，总计 50MB 以内），重复 image 字段即可
files = [
    ("image", open("product.png", "rb")),
    ("image", open("background.png", "rb")),
]{mask_part}

resp = requests.post(
    "https://anyaigc.ai/v1/images/edits",
    headers={{"Authorization": "Bearer " + API_KEY}},
    data={{
        "model": "{model}",
        "prompt": "把第一张图里的产品放到第二张图的场景中，保持产品外观和标签文字不变",
        "size": "1024x1024",
        "quality": "high",
    }},
    files=files,
    timeout=300,
)
resp.raise_for_status()
print(resp.json()["data"][0]["url"])'''


def steps(model):
    return [f'<a href="{G.REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
            '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'向 <code>https://anyaigc.ai/v1/images/generations</code> 发请求，<code>model</code> 填 <code>{model}</code>；改图用 <code>/v1/images/edits</code>。']


def token_price_tables(base):
    return G.table(f'GPT Image {base} 按 token 计费单价（美元 / 每 100 万 tokens）',
                   [('计费项', False), ('AnyAIGC', True), ('OpenAI 官方', True), ('节省', True)],
                   [(None, G.token_rows('zh', base))])


def token_billing():
    return [('按 token 计费', '提示词、参考图和生成的图片分别计价'), ('一次 1–10 张', '用 n 参数指定张数'),
            (CONC, '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')]




def token_costs_25():
    out = []
    for h, q, s, n in [('电商主图批量生成', 'medium', '1536x1024', 1000), ('4K 海报', 'high', '3840x2160', 100), ('一张 max 质量方图', 'max', '1024x1024', 1)]:
        a, o = cost_25(q, s)
        t = TOKENS_25[q][s]
        out.append((h, f'{n:,} 张 {s.replace("x", "×")}，<code>quality={q}</code>，每张约 {t:,} 输出 tokens × ${T25["out"]} / 1M',
                    money(a * n, 2 if n > 1 else 4), f'官方 <s>{money(o * n, 2 if n > 1 else 4)}</s>'))
    return out


def token_costs_2():
    out = []
    for h, q, s, n in [('电商主图批量生成', 'medium', '1024x1024', 1000), ('高质量横幅', 'high', '1536x1024', 100), ('草图快速出图', 'low', '1024x1024', 1000)]:
        a, o = cost_2(q, s)
        out.append((h, f'{n:,} 张 {s.replace("x", "×")}，<code>quality={q}</code>，官方单张 ${OFFICIAL_IMG_2[q][s]} 按输出单价 ${T2["out"]} / 1M 折算',
                    money(a * n, 2), f'官方 <s>{money(o * n, 2)}</s>'))
    return out


def call_costs(base, model):
    k1, k4 = float(CALL_CNY[base]['1k']), float(CALL_CNY[base]['4k'])
    return [('1,000 张 1K 商品图', f'1,000 × {cny(base)}，质量档位不影响单价', f'¥{k1 * 1000:,.0f}', '1K 出图'),
            ('10,000 张 1K 批量素材', f'10,000 × {cny(base)}', f'¥{k1 * 10000:,.0f}', '1K 出图'),
            ('100 张 4K 海报', f'100 × {cny(base, "4k")}，2K、4K 同价', f'¥{k4 * 100:,.0f}', '2K / 4K 出图')]




def build(slug):
    if slug == 'gpt-image':
        return hub()
    m = MODELS[slug]
    return token_page(slug, m)


# ---------------------------------------------------------------- 总览页
def hub():
    tok = []
    for s in ['gpt-image-2.5-sunburst', 'gpt-image-2.5-flare', 'gpt-image-2']:
        b = MODELS[s]['base']
        t = TOKEN[b]
        tok.append(f'<th scope="row"><a href="/zh/models/{s}">{MODELS[s]["name"]}</a><small><code>{s}</code></small></th>'
                   f'<td class="o-num">${t["text_in"]}</td><td class="o-num">${t["img_in"]}</td><td class="o-num o-hl">${t["out"]}</td><td class="o-num o-save">{save(t["out"], OFFICIAL["out"])}%</td>')
    call = []
    for s in ['gpt-image-2.5-sunburst-c', 'gpt-image-2.5-flare-c', 'gpt-image-2-c']:
        b = MODELS[s]['base']
        call.append(f'<th scope="row"><a href="/zh/models/{MODELS[s]["of"]}#per-image">{MODELS[s]["name"]}</a><small><code>{s}</code></small></th>'
                    f'<td class="o-num" colspan="2">1K {cny(b)} / 张 · 2K/4K {cny(b, "4k")} / 张</td><td class="o-num o-hl">{cny(b)} / 张起</td><td class="o-num">-</td>')
    tables = G.table('GPT Image 全系价格', [('模型', False), ('文本输入 / 1M', True), ('图片输入 / 1M', True), ('图片输出', True), ('比官方省', True)],
                     [('按 token 计费 · 官方价：文本输入 $5.00、图片输入 $8.00、图片输出 $30.00 / 1M', tok), ('按张计费（-c 版，人民币）', call)])
    models_html = ''
    cards = [
        ('gpt-image-2.5-sunburst', 'is-red', '编辑精度最高', 'OpenAI 目前能力最强的图像生成与编辑模型，适合精修、商业海报和对细节要求高的改图。', f'${T25["out"]}', '图片输出 / 1M tokens'),
        ('gpt-image-2.5-flare', 'is-blue', '速度最快', 'OpenAI 最快的高质量图像模型，适合日常出图、批量生成和需要快速返回的产品功能。', f'${T25["out"]}', '图片输出 / 1M tokens'),
        ('gpt-image-2', '', '上一代主力', '2026 年 4 月发布，ChatGPT 图像 2.0 背后的模型。按 token 计费单价全系最低，约官方价 0.8 折。', f'${T2["out"]}', '图片输出 / 1M tokens'),
    ]
    for s, cls, tag, p, price, unit in cards:
        models_html += (f'        <li class="o-reveal"><a class="gi-model" href="/zh/models/{s}"><span class="gi-model-tag {cls}">{tag}</span>'
                        f'<h3>{MODELS[s]["name"]}</h3><code>{s}</code><p>{p}</p>'
                        f'<span class="gi-model-price"><strong>{price}</strong>{unit}</span><span class="gi-model-go">查看专题 →</span></a></li>\n')
    choose = G.table('GPT Image 型号怎么选', [('需求', False), ('推荐型号', False), ('原因', False)], [(None, [
        '<th scope="row">精修、改图、商业海报</th><td><a href="/zh/models/gpt-image-2.5-sunburst">2.5 Sunburst</a></td><td>官方定位为编辑精度最高的型号，支持 xhigh / max 质量</td>',
        '<th scope="row">产品内实时出图、批量生成</th><td><a href="/zh/models/gpt-image-2.5-flare">2.5 Flare</a></td><td>官方标注速度 Very fast，单价与 Sunburst 相同</td>',
        '<th scope="row">已有 gpt-image-2 集成、成本优先</th><td><a href="/zh/models/gpt-image-2">GPT Image 2</a></td><td>按 token 单价约官方 0.8 折，全系最低</td>',
        '<th scope="row">高质量、大尺寸，预算按张算</th><td><a href="/zh/models/gpt-image-2.5-sunburst#per-image">2.5 Sunburst-c</a> / <a href="/zh/models/gpt-image-2.5-flare#per-image">Flare-c</a></td><td>每张固定价，质量开到 high 以上时比按 token 便宜</td>',
        '<th scope="row">海量素材、单张成本最低</th><td><a href="/zh/models/gpt-image-2#per-image">GPT Image 2-c</a></td><td>' + f'1K 每张 {cny("2")}，质量档位不影响单价</td>',
    ])])
    a25 = cost_25('high', '1024x1024')
    faqs = [
        ('GPT Image API 多少钱？',
         f'按 token 计费的型号：GPT Image 2.5 Sunburst 与 Flare 文本输入 ${T25["text_in"]}、图片输入 ${T25["img_in"]}、图片输出 ${T25["out"]}（每百万 tokens），约官方价 6 折；GPT Image 2 文本输入 ${T2["text_in"]}、图片输入 ${T2["img_in"]}、图片输出 ${T2["out"]}，约官方价 0.8 折。按张计费的 -c 版：gpt-image-2.5-sunburst-c 与 gpt-image-2.5-flare-c 1K 出图每张 {cny("2.5")}、2K/4K 每张 {cny("2.5", "4k")}；gpt-image-2-c 1K 每张 {cny("2")}、2K/4K 每张 {cny("2", "4k")}。实时价格以模型广场为准。'),
        ('Sunburst、Flare 和 GPT Image 2 有什么区别？',
         'Sunburst 和 Flare 是 OpenAI 2026 年 9 月发布的 GPT Image 2.5 系列。OpenAI 把 Sunburst 定位为编辑精度最高的型号，Flare 是速度最快的高质量日常出图型号，两者官方 token 单价相同，都新增了 xhigh 和 max 两档质量。GPT Image 2 是 2026 年 4 月发布的上一代，质量档位为 low、medium、high、auto。'),
        ('按 token 计费和按张计费（-c 版）怎么选？',
         f'按 token 计费的费用随尺寸和质量变化：低质量小图很便宜，质量越高、尺寸越大越贵。-c 版每张固定价（1K、2K/4K 两档），不受质量档位影响，但一次只出 1 张，不支持 n 和 mask 参数，也不支持透明背景。以 1024×1024、high 质量为例，2.5 按 token 计费每张约 {money(a25[0])}，-c 版每张 {cny("2.5")}。'),
        ('支持哪些接口？可以改图吗？',
         f'GPT Image 全系（包括 -c 按张计费版）都支持 <code>POST /v1/images/generations</code>（文生图）和 <code>POST /v1/images/edits</code>（图生图、多图合成）。编辑时可以上传少于 16 张参考图（总计 50MB 以内）；按 token 计费的型号还支持用 mask 局部重绘。字段说明见 <a href="{DOCS_GEN_25}">AnyAIGC API 文档</a>。'),
        conc_faq('GPT Image 全系'),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    curl, py = code_gen('gpt-image-2.5-flare')
    return dict(
        title='GPT Image API 价格与接入｜gpt-image-2 与 2.5 全系 - AnyAIGC',
        desc=f'GPT Image API 全系：gpt-image-2.5 Sunburst、Flare 与 gpt-image-2，按 token 计费最低约官方价 0.8 折，按张计费 {cny("2")} 起，并发不限，支持对公转账与增值税专票。',
        og_desc=f'一个 Key 调用 GPT Image 全系：2.5 Sunburst、2.5 Flare、gpt-image-2，另有按张计费版，{cny("2")} / 张起，并发不限。',
        og_alt='AnyAIGC GPT Image API：gpt-image-2 与 2.5 全系',
        keywords='GPT Image API,gpt-image-2 API,gpt-image-2.5 API,GPT Image 2 价格,gpt-image-2.5-sunburst,gpt-image-2.5-flare,OpenAI 图像生成 API,GPT Image API 中转,GPT Image API 企业,GPT Image API 发票,AnyAIGC',
        crumb='GPT Image', product='GPT Image API（AnyAIGC）', sku='gpt-image',
        product_desc='通过 AnyAIGC 调用 OpenAI GPT Image 全系图像模型：gpt-image-2.5-sunburst、gpt-image-2.5-flare、gpt-image-2 及按张计费版，兼容 /v1/images/generations 与 /v1/images/edits。',
        offers=[('GPT Image 2.5 图片输出（每 100 万 tokens）', T25['out']), ('GPT Image 2 图片输出（每 100 万 tokens）', T2['out'])],
        eyebrow='OpenAI · GPT Image 系列', h1='GPT Image API<small>gpt-image-2 与 GPT Image 2.5 全系</small>',
        lead=f'一个 API Key 调用 OpenAI 全部 GPT Image 型号，<strong>按张 {cny("2")} 起</strong>。',
        lead_sub='文字渲染、写实人像、多语言排版和多图编辑都能直接走 API。按 token 计费最低约官方价 0.8 折，也可以选每张固定价的 -c 版。',
        facts=[('型号', '3 个 + 按张版'), ('接口', '/v1/images/generations · edits'), ('最大尺寸', '3840×2160'), ('并发', '不限'), ('企业', '对公 · 专票')],
        hero_imgs=('polyglot-collage', 'matcha-poster', 'candid-coast'),
        about_h2='选一个 GPT Image 型号',
        about_ps=[],
        models_html=models_html, choose=choose,
        gallery=['chinese-comic', 'matcha-poster', 'typography-poster', 'aliens-cafe', 'cantor-infographic', 'korean-hanok-ad', 'candid-flash', 'merch-grid', 'miami-comic'],
        gallery_h2='GPT Image 能画出什么', gallery_lead='下面的图都由 ChatGPT 图像 2.0 生成，背后就是 gpt-image-2。中文排版、杂志信息图、写实摄影和连续漫画都能一次成图。',
        price_h2='GPT Image API 价格', price_lead='3 个型号按 token 计费，费用随尺寸和质量浮动；每个型号另有按张计费的 -c 版，每张固定价。',
        billing_label='计费要点', billing=[('两种计费', '按 token 或按张固定价'), ('一个 Key', '全系共用'), (CONC, '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')],
        price_tables=tables + '      <h3 class="gi-h3 o-reveal">按需求选型号</h3>\n' + choose,
        price_note=f'按 token 计费单位为 USD，为模型广场最低价，自定义尺寸、透明背景等能力的单价可能更高；-c 版为人民币按张价格：2.5 系列 1K 每张 {cny("2.5")}、2K/4K 每张 {cny("2.5", "4k")}，gpt-image-2-c 1K 每张 {cny("2")}、2K/4K 每张 {cny("2", "4k")}。实时价格以<a href="{PRICING}">模型广场</a>为准。',
        costs_h3='成本示例', costs_lead='按上表单价和 OpenAI 官方计算器的输出 tokens 计算，不含提示词文本 tokens。',
        costs=[(h, c, t, o) for h, c, t, o in [token_costs_25()[0], token_costs_2()[0], call_costs('2', 'gpt-image-2-c')[0]]],
        uses_h2='用在哪里',
        uses=[('01 · 电商', '商品主图与场景图', '上传产品图，用 edits 接口换背景、换场景，标签和包装文字能保持清晰。', 'matcha-poster'),
              ('02 · 营销', '海报、横幅与广告素材', '直接生成带标题、正文和品牌元素的成品海报，最大 3840×2160。', 'korean-hanok-ad'),
              ('03 · 内容', '信息图与教学插图', '科普图解、学术海报、数据卡片，排版和文字一次到位。', 'cantor-infographic'),
              ('04 · 本地化', '多语言版本', '中文、日文、韩文、阿拉伯文等文字都能渲染，同一张图快速出多个语言版本。', 'typography-poster')],
        steps=steps('gpt-image-2.5-flare'),
        codes=[('py', 'Python', 'POST /v1/images/generations', py), ('curl', 'cURL', 'POST /v1/images/generations', curl),
               ('edit', '图片编辑', 'POST /v1/images/edits', code_edit('gpt-image-2.5-sunburst'))],
        qs_h2='三步接入 GPT Image API',
        callout='换型号只改 <code>model</code> 字段：<code>gpt-image-2.5-sunburst</code>、<code>gpt-image-2.5-flare</code>、<code>gpt-image-2</code>，或按张计费的 <code>-c</code> 版。-c 版不要传 <code>n</code> 和 <code>mask</code>。',
        qs_note=f'图片格式字段是 <code>format</code>（png / jpeg / webp），返回 <code>data[0].url</code>；传 <code>response_format=b64_json</code> 可以拿 base64。完整参数见 <a href="{DOCS_GEN_25}" target="_blank" rel="noopener">生成接口文档</a> 与 <a href="{DOCS_EDIT_25}" target="_blank" rel="noopener">编辑接口文档</a>。',
        family_h2='GPT Image 全部型号', family_lead='同一个 API Key，换型号只改 model 字段。',
        faq_h2='GPT Image API 常见问题', faqs=faqs,
        final_h2='用一个 Key 调用 GPT Image 全系', final_p='注册即送 200 万 tokens 试用额度，先出几张图看看效果。',
        name='GPT Image', docs=DOCS_GEN_25,
    )


# ---------------------------------------------------------------- 按 token 计费的型号页
def token_page(slug, m):
    b = m['base']
    t = TOKEN[b]
    name = m['name']
    is25 = b == '2.5'
    short = {'gpt-image-2.5-sunburst': '2.5 Sunburst', 'gpt-image-2.5-flare': '2.5 Flare', 'gpt-image-2': 'GPT Image 2'}[slug]
    zhe = '6 折' if is25 else '0.8 折'
    per = G.per_image_25('zh') if is25 else G.per_image_2('zh')
    tables = token_price_tables(b) + '      <h3 class="gi-h3 o-reveal">每张图大概多少钱</h3>\n' + \
        ('      <p class="o-note">按 OpenAI 官方计算器给出的每张图片输出 tokens × AnyAIGC 输出单价估算，不含提示词和参考图的输入 tokens。</p>\n' if is25 else
         '      <p class="o-note">按 OpenAI 官方给出的 GPT Image 2 单张输出价格，乘以 AnyAIGC 与官方输出单价之比估算，不含输入 tokens。</p>\n') + per
    costs = token_costs_25() if is25 else token_costs_2()
    tables += G.call_block('zh', C_OF[slug])
    q_levels = 'low、medium、high、xhigh、max、auto' if is25 else 'low、medium、high、auto'
    c_slug = C_OF[slug][0]
    c_link = f'<a href="#per-image"><code>{c_slug}</code></a>'
    if slug == 'gpt-image-2.5-sunburst':
        eyebrow, h1sub = 'OpenAI · gpt-image-2.5-sunburst', '编辑精度最高的 GPT Image 旗舰'
        lead = f'OpenAI 目前能力最强的图像生成与编辑模型，<strong>约官方价 {zhe}</strong>。'
        lead_sub = f'官方定位为“编辑精度最重要的工作流”首选。在 AnyAIGC 调用 <code>{slug}</code>，图片输出 ${t["out"]} / 百万 tokens，官方价 ${OFFICIAL["out"]}。'
        about_h2 = 'GPT Image 2.5 Sunburst：改图最准的那一个'
        about = ['OpenAI 于 2026 年 9 月发布 GPT Image 2.5，分为 Sunburst 和 Flare 两个型号。OpenAI 把 Sunburst 称为“图像生成和编辑能力最强的模型”，性能标注为 Highest，建议用于编辑精度最重要的工作流；Flare 则主打速度。',
                 'Sunburst 支持文本和图片输入、图片输出，质量档位比 GPT Image 2 多了 xhigh 和 max。尺寸可以自定义，' + SIZE_RULES + '，OpenAI 说明超过 2560×1440 的分辨率属于实验性能力。快照版本为 <code>gpt-image-2.5-sunburst-2026-09-08</code>。',
                 f'在 AnyAIGC 上，Sunburst 和 Flare 单价相同，都约为官方价的 59%。如果你更在意每张图的固定成本，可以用按张计费的 {c_link}，1K 出图每张 {cny("2.5")}。']
        spec = [('性能（官方）', 'Highest'), ('速度（官方）', 'Medium'), ('质量档位', 'low – max'), ('最大尺寸', '3840×2160'), ('快照', '2026-09-08'), ('接口', 'generations · edits')]
        hero_imgs = ('korean-hanok-ad', 'high-fashion', 'academic-poster')
        gallery = ['high-fashion', 'academic-poster', 'wolf-magazine', 'surreal-portrait', 'art-deco-bookmark', 'color-analysis']
        uses = [('01 · 精修', '商业海报与品牌主视觉', '用 high、xhigh 或 max 质量生成成品海报，细节和文字还原更稳。', 'korean-hanok-ad'),
                ('02 · 改图', '产品换景与局部重绘', '上传产品图和 mask，只改背景或局部，产品外观和标签保持不变。', 'matcha-poster'),
                ('03 · 出版', '杂志版面与印刷物料', '信息图、跨页、书签这类排版复杂的物料，一次生成接近定稿。', 'wolf-magazine'),
                ('04 · 时尚', '人像与时尚大片', '写实人像、服装造型和布光，适合广告提案和创意测试。', 'high-fashion')]
        diff = ('Sunburst 和 Flare 有什么区别？',
                f'两者都是 GPT Image 2.5，官方 token 单价相同，质量档位都是 low 到 max。OpenAI 把 Sunburst 定位为编辑精度最高的型号（性能 Highest、速度 Medium），Flare 是速度最快的高质量日常出图型号（性能 Higher、速度 Very fast）。精修和改图选 Sunburst，量大、要快选 <a href="/zh/models/gpt-image-2.5-flare">Flare</a>。在 AnyAIGC 上两者单价一样。')
        default_q = 'high'
    elif slug == 'gpt-image-2.5-flare':
        eyebrow, h1sub = 'OpenAI · gpt-image-2.5-flare', '速度最快的高质量 GPT Image'
        lead = f'OpenAI 最快的高质量图像模型，适合日常和批量出图，<strong>约官方价 {zhe}</strong>。'
        lead_sub = f'官方速度标注为 Very fast。在 AnyAIGC 调用 <code>{slug}</code>，图片输出 ${t["out"]} / 百万 tokens，官方价 ${OFFICIAL["out"]}，并发不限。'
        about_h2 = 'GPT Image 2.5 Flare：快，而且画质不打折'
        about = ['GPT Image 2.5 Flare 是 OpenAI 2026 年 9 月随 GPT Image 2.5 一起发布的型号。OpenAI 称它是“速度最快的高质量日常图像生成模型”，性能标注为 Higher，速度为 Very fast。',
                 'Flare 和 Sunburst 用同一套参数：文本和图片输入、图片输出，质量从 low 到 max，尺寸可以自定义，' + SIZE_RULES + '。快照版本为 <code>gpt-image-2.5-flare-2026-09-08</code>。',
                 f'在 AnyAIGC 上 Flare 和 Sunburst 单价相同。低质量档每张只要零点几美分，适合草图、批量素材和产品内的实时出图。想按张固定成本，可以用 {c_link}，1K 出图每张 {cny("2.5")}。']
        spec = [('性能（官方）', 'Higher'), ('速度（官方）', 'Very fast'), ('质量档位', 'low – max'), ('最大尺寸', '3840×2160'), ('快照', '2026-09-08'), ('接口', 'generations · edits')]
        hero_imgs = ('merch-grid', 'candid-flash', 'matcha-poster')
        gallery = ['merch-grid', 'candid-flash', 'character-sheet', 'dunk-keyframes', 'moodboard', 'thai-street-panorama']
        uses = [('01 · 产品功能', '应用内实时出图', 'AI 头像、贺卡、壁纸这类面向用户的功能，响应快，体验更顺。', 'candid-flash'),
                ('02 · 电商', '批量商品图', '同一套提示词模板批量生成上千张图，用 medium 质量控制成本。', 'merch-grid'),
                ('03 · 游戏动漫', '角色设定与分镜', '角色多角度设定、动作分解和分镜草图，快速迭代方案。', 'character-sheet'),
                ('04 · 社媒', '日常内容配图', '公众号、小红书、短视频封面，按需生成横版、竖版和方图。', 'moodboard')]
        diff = ('Flare 和 Sunburst 有什么区别？',
                f'两者都是 GPT Image 2.5，官方 token 单价相同，质量档位都是 low 到 max。Flare 主打速度（官方速度 Very fast，性能 Higher），适合日常和批量出图；<a href="/zh/models/gpt-image-2.5-sunburst">Sunburst</a> 主打编辑精度（性能 Highest，速度 Medium）。在 AnyAIGC 上两者单价一样。')
        default_q = 'medium'
    else:
        eyebrow, h1sub = 'OpenAI · gpt-image-2', 'ChatGPT 图像 2.0 背后的模型'
        lead = f'2026 年 4 月发布的 GPT Image 2，按 token 计费单价全系最低，<strong>约官方价 {zhe}</strong>。'
        lead_sub = f'在 AnyAIGC 调用 <code>{slug}</code>，文本输入 ${t["text_in"]}、图片输出 ${t["out"]} / 百万 tokens，官方价 ${OFFICIAL["text_in"]} 和 ${OFFICIAL["out"]}。'
        about_h2 = 'GPT Image 2：文字渲染和写实感的一次跃升'
        about = ['OpenAI 于 2026 年 4 月 21 日发布 ChatGPT 图像 2.0，同期在 API 推出 <code>gpt-image-2</code>（快照 <code>gpt-image-2-2026-04-21</code>）。官方介绍它支持快速、高质量的图像生成和编辑，可以灵活设置尺寸，图片输入始终按高保真处理，不需要也不能设置 <code>input_fidelity</code>。',
                 '质量档位为 low、medium、high、auto。尺寸可以自定义，' + SIZE_RULES + '。常用尺寸有 1024×1024、1536×1024、1024×1536、2048×2048、2048×1152 和 3840×2160。',
                 f'OpenAI 之后推出了 GPT Image 2.5（Sunburst 和 Flare），官方指南建议新集成优先使用 2.5。gpt-image-2 在 API 里仍可正常调用，在 AnyAIGC 上单价约为 2.5 的七分之一，适合对成本敏感的批量任务。按张计费版是 {c_link}，1K 出图每张 {cny("2")}。']
        spec = [('发布', '2026-04-21'), ('性能（官方）', 'Higher'), ('质量档位', 'low – high'), ('最大尺寸', '3840×2160'), ('图片输入', '始终高保真'), ('接口', 'generations · edits')]
        hero_imgs = ('chinese-comic', 'rice-macro', 'computer-lab')
        gallery = ['chinese-comic', 'rice-macro', 'computer-lab', 'cantor-infographic', 'polyglot-collage', 'aliens-cafe']
        uses = [('01 · 中文内容', '带中文的海报与漫画', '中文标题、对白和招牌都能清楚渲染，适合国内营销物料。', 'chinese-comic'),
                ('02 · 写实', '摄影风格素材', '微距、街拍、年代感照片，质感接近实拍。', 'rice-macro'),
                ('03 · 教育', '图解与课件插图', '数学证明、科普图解和课件配图，结构清楚。', 'cantor-infographic'),
                ('04 · 成本敏感', '大批量素材生产', '按 token 计费单价全系最低，low 质量每张不到 0.1 美分。', 'computer-lab')]
        diff = ('gpt-image-2 还能用吗？要不要换 GPT Image 2.5？',
                f'能用。OpenAI 官方指南建议新集成优先使用 GPT Image 2.5，但 gpt-image-2 目前没有停用公告，在 AnyAIGC 上照常调用。2.5 多了 xhigh 和 max 质量档；gpt-image-2 的优势是便宜，在 AnyAIGC 上图片输出 ${T2["out"]} / 百万 tokens，2.5 为 ${T25["out"]}。换型号只改 <code>model</code> 字段，可以先拿同一批提示词对比 <a href="/zh/models/gpt-image-2.5-flare">2.5 Flare</a>。')
        default_q = 'medium'
    notice = None if is25 else '<span><strong>已有更新版本：</strong>OpenAI 已推出 GPT Image 2.5，官方建议新集成优先使用。gpt-image-2 目前仍可正常调用，没有停用公告。新项目可以看看 <a href="/zh/models/gpt-image-2.5-flare">GPT Image 2.5 Flare</a>。</span>'
    a1, o1 = (cost_25('medium', '1024x1024') if is25 else cost_2('medium', '1024x1024'))
    faqs = [
        (f'{name} API 多少钱？',
         f'AnyAIGC 上 <code>{slug}</code> 按 token 计费：文本输入 ${t["text_in"]}、图片输入 ${t["img_in"]}、图片输出 ${t["out"]}（每百万 tokens），缓存输入文本 ${t["text_cache"]}、图片 ${t["img_cache"]}。OpenAI 官方价为文本输入 ${OFFICIAL["text_in"]}、图片输入 ${OFFICIAL["img_in"]}、图片输出 ${OFFICIAL["out"]}。以 1024×1024、medium 质量为例，每张图片输出约 {money(a1)}（官方约 {money(o1)}）。实时价格以模型广场为准。'),
        diff,
        ('支持哪些尺寸、质量和格式？',
         f'常用尺寸有 1024×1024、1536×1024、1024×1536、2048×2048、2048×1152、3840×2160、2160×3840 和 auto；自定义尺寸需满足{SIZE_RULES}。质量档位为 {q_levels}。输出格式用 <code>format</code> 字段选 png、jpeg 或 webp，返回图片 URL 或 base64。最低价支持{"自定义尺寸" if is25 else "上述预设尺寸"}，{"透明背景" if is25 else "自定义尺寸和透明背景"}的单价更高，以模型广场为准。'),
        ('怎么做图生图和局部重绘？',
         f'调用 <code>POST /v1/images/edits</code>（multipart/form-data），<code>image</code> 字段可以传少于 16 张参考图，总计 50MB 以内；需要局部重绘时再传 <code>mask</code>，它的透明区域就是要重画的部分，必须是 PNG、小于 4MB、与第一张图同尺寸。参数见 <a href="{DOCS_EDIT_25 if is25 else DOCS_EDIT_2}">编辑接口文档</a>。'),
        (f'有按张计费的版本吗？{c_slug} 怎么收费？',
         f'有。AnyAIGC 平台上的 <code>{c_slug}</code> 是 {name} 的按张计费版，接口相同，只改 <code>model</code> 字段。每张固定价，质量档位不影响单价：1K 出图每张 {cny(b)}，2K、4K 出图每张 {cny(b, "4k")}。每次请求出 1 张，不支持 <code>n</code>、<code>mask</code> 参数，也不支持透明背景。质量开到 {"high 及以上" if is25 else "high"} 或出大图时，按张计费通常更省。'),
        conc_faq(slug),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    curl, py = code_gen(slug, quality=default_q)
    title = f'{name} API 价格与接入｜约官方价 {zhe} - AnyAIGC'
    return dict(
        title=title,
        desc=(f'{name} API（{slug}）：{"编辑精度最高的 OpenAI 图像模型" if slug.endswith("sunburst") else ("速度最快的高质量图像模型" if slug.endswith("flare") else "ChatGPT 图像 2.0 背后的模型")}，'
              f'图片输出 ${t["out"]}/1M，约官方价 {zhe}，并发不限，支持对公转账与增值税专票。'),
        og_desc=f'{slug} 文本输入 ${t["text_in"]}、图片输出 ${t["out"]} / 1M tokens，约官方价 {zhe}。兼容 /v1/images/generations 与 /v1/images/edits，并发不限。',
        og_alt=f'AnyAIGC {name} API：约官方价 {zhe}',
        keywords=f'{name} API,{slug},{slug} API,{name} 价格,{name} API 价格,GPT Image API,OpenAI 图像生成 API,{name} API 企业,{name} API 发票,GPT Image API 对公转账,AnyAIGC',
        crumb=f'{short} API' if is25 else 'GPT Image 2 API', product=f'{name} API（AnyAIGC）', sku=slug,
        product_desc=f'通过 AnyAIGC 调用 OpenAI {name}（{slug}）：兼容 /v1/images/generations 与 /v1/images/edits，按 token 计费，约官方价 {zhe}，并发不限。',
        offers=[('文本输入（每 100 万 tokens）', t['text_in']), ('图片输入（每 100 万 tokens）', t['img_in']), ('图片输出（每 100 万 tokens）', t['out']),
                ('文本缓存输入（每 100 万 tokens）', t['text_cache']), ('图片缓存输入（每 100 万 tokens）', t['img_cache'])],
        eyebrow=eyebrow, h1=f'{name}<span class="o-sr"> API</span><small>{h1sub}</small>', lead=lead, lead_sub=lead_sub, notice=notice,
        facts=[('模型 ID', slug), ('图片输出', f'${t["out"]} / 1M'), ('价格', f'约官方 {zhe}'), ('并发', '不限'), ('企业', '对公 · 专票')],
        hero_imgs=hero_imgs, about_h2=about_h2, about_ps=about, spec=spec,
        gallery=gallery, gallery_h2=f'{short} 能画出什么' if is25 else 'GPT Image 2 能画出什么',
        gallery_lead='示例图由 ChatGPT 图像 2.0 生成，展示 GPT Image 系列的文字渲染、排版和写实能力。' + (' GPT Image 2.5 在此基础上提升了细节和编辑精度。' if is25 else ''),
        price_h2=f'{name} API 价格', price_lead=f'按 token 计费，固定单价，没有订阅和月费。文本输入、图片输入和图片输出都约为 OpenAI 官方价的 {100 - save(t["out"], OFFICIAL["out"])}%。',
        billing_label='计费要点', billing=token_billing(), price_tables=tables,
        price_note=f'按 token 价格单位为 USD，按张计费（-c 版）单位为人民币，均按成功请求计费。表中为模型广场最低价，{"透明背景" if is25 else "自定义尺寸、透明背景"}等能力的单价更高。缓存价格仅在上游明确返回缓存用量时生效。实时价格以<a href="{PRICING}">模型广场</a>为准。',
        costs_h3='成本示例', costs_lead='按上表单价计算，只算图片输出 tokens，不含提示词文本。',
        costs=costs,
        uses_h2=f'{short} 适合做什么', uses=uses,
        steps=steps(slug),
        codes=[('py', 'Python', 'POST /v1/images/generations', py), ('curl', 'cURL', 'POST /v1/images/generations', curl), ('edit', '图片编辑', 'POST /v1/images/edits', code_edit(slug))],
        qs_h2=f'三步接入 {name} API',
        callout=f'想按张固定价？把 <code>model</code> 换成 <code>{c_slug}</code>（1K 每张 {cny(b)}，2K/4K 每张 {cny(b, "4k")}），去掉 <code>n</code> 和 <code>mask</code> 即可。',
        qs_note=f'返回 <code>data[0].url</code>；传 <code>response_format=b64_json</code> 可以拿 base64。提示词最长 1000 字符。完整参数见 <a href="{DOCS_GEN_25 if is25 else DOCS_GEN_2}" target="_blank" rel="noopener">生成接口文档</a>。',
        family_h2='GPT Image 全部型号', family_lead='同一个 API Key，换型号只改 model 字段。',
        faq_h2=f'{name} API 常见问题', faqs=faqs,
        final_h2=f'现在开始调用 {name}', final_p='注册即送 200 万 tokens 试用额度，先出几张图看看效果。',
        name=name, docs=DOCS_GEN_25 if is25 else DOCS_GEN_2,
    )
