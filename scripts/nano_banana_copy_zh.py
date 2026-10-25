# Nano Banana 系列专题页中文文案。build(slug) 返回页面用的字典。价格用人民币（用户提供）。
from nano_banana_data import (CNY, OFFICIAL, MODELS, MODEL_SLUGS, RATIOS_14, SIZES, SUPPORT, PRICING,
                              DOCS_21, DOCS_GEMINI, DOCS_CHAT, GOOGLE_DOC, cny_min)
import nano_banana_layout as G

NL = '\n'
CONC = '并发不限'

FAMILY = [
    ('nano-banana', '总览', 'Nano Banana 全系', '3 个型号的价格与参数对比'),
    ('nano-banana-2.1', '最新', 'Nano Banana 2.1', f'Nano Banana 2 的升级版 · 1K {cny_min("nano-banana-2.1")} / 张'),
    ('nano-banana-pro', '专业', 'Nano Banana Pro', f'4K 精修与复杂排版 · 1K/2K {cny_min("nano-banana-pro")} / 张'),
    ('nano-banana-2', '', 'Nano Banana 2', f'Gemini 3.1 Flash Image · 1K/2K {cny_min("nano-banana-2")} / 张'),
]

COMMON_FAQ = [
    ('AnyAIGC 能开发票吗？支持增值税专票吗？',
     '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
    ('企业可以对公转账和签合同吗？',
     f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
]
LICENSE_FAQ = ('生成的图片可以商用吗？有水印吗？',
               '图片的使用权和内容政策以 Google 官方条款为准。Google 会在 Nano Banana 生成的所有图片里加入不可见的 SynthID 数字水印，画面上看不到。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用；涉及人物肖像、品牌商标等内容时，请自行确认授权。')


def conc_faq(name):
    return ('并发有限制吗？国内能直接调用吗？',
            f'AnyAIGC 对 {name} 不设并发限制，所有用户默认享有。接口地址是 <code>https://anyaigc.ai</code>，面向国内网络优化，通常无需额外代理，也不需要 Google 账号和海外信用卡；同一个 Key 还能调用平台上 300+ 其他模型。')


def price_str(slug):
    return '、'.join(f'{r} 每张 ¥{p}' for r, p in CNY[slug])


# ---------------------------------------------------------------- 代码示例
def code_native(model, ratio='16:9', size='2K', prompt='一盘放在高级餐厅里的迷你香蕉料理，Gemini 主题装饰，柔和的顶光'):
    py = f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
MODEL = "{model}"

resp = requests.post(
    f"https://anyaigc.ai/v1beta/models/{{MODEL}}:generateContent",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "contents": [{{"role": "user", "parts": [{{"text": "{prompt}"}}]}}],
        "generationConfig": {{
            "responseModalities": ["TEXT", "IMAGE"],
            # aspectRatio / imageSize 必须写在 imageConfig 里，imageSize 用大写 K
            "imageConfig": {{"aspectRatio": "{ratio}", "imageSize": "{size}"}},
        }},
    }},
    timeout=300,
)
resp.raise_for_status()

# 图片在 parts 里的 inlineData（base64，不含 data: 前缀），文字说明在 text 里
for part in resp.json()["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        ext = part["inlineData"]["mimeType"].split("/")[-1]
        with open("output." + ext, "wb") as f:
            f.write(base64.b64decode(part["inlineData"]["data"]))
        print("已保存 output." + ext)
    elif "text" in part:
        print(part["text"])'''
    curl = f'''curl "https://anyaigc.ai/v1beta/models/{model}:generateContent" \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "contents": [{{"role": "user", "parts": [{{"text": "{prompt}"}}]}}],
    "generationConfig": {{
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {{"aspectRatio": "{ratio}", "imageSize": "{size}"}}
    }},
    "response_format": "url"
  }}\''''
    return curl, py


def code_edit(model, size='2K'):
    return f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]
MODEL = "{model}"


def image_part(path, mime="image/jpeg"):
    with open(path, "rb") as f:
        return {{"inlineData": {{"mimeType": mime, "data": base64.b64encode(f.read()).decode()}}}}


# 一段文字 + 多张参考图放在同一个 parts 里，用文字标明每张图的编号
parts = [
    {{"text": "把图1里的商品放进图2的场景，保持商品外观和包装文字不变"}},
    {{"text": "图1："}},
    image_part("product.jpg"),
    {{"text": "图2："}},
    image_part("scene.jpg"),
]

resp = requests.post(
    f"https://anyaigc.ai/v1beta/models/{{MODEL}}:generateContent",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "contents": [{{"role": "user", "parts": parts}}],
        "generationConfig": {{
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {{"aspectRatio": "1:1", "imageSize": "{size}"}},
        }},
        "response_format": "url",  # 返回临时下载链接（仅非流式），默认 base64
    }},
    timeout=300,
)
resp.raise_for_status()
for part in resp.json()["candidates"][0]["content"]["parts"]:
    if "fileData" in part:
        print(part["fileData"]["fileUri"])'''


def code_chat(model):
    return f'''curl https://anyaigc.ai/v1/chat/completions \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "messages": [
      {{"role": "user", "content": "画一张极简风格的香水瓶产品图，白色大理石台面，侧光"}}
    ]
  }}\''''


def codes(model, ratio='16:9', size='2K'):
    curl, py = code_native(model, ratio, size)
    return [('py', 'Python', f'Python · {model} 文生图', py),
            ('curl', 'cURL', f'cURL · {model} 文生图', curl),
            ('edit', '多图编辑', f'Python · {model} 参考图编辑', code_edit(model, size)),
            ('chat', 'OpenAI 兼容', 'cURL · /v1/chat/completions', code_chat(model))]


def steps(model):
    return [f'<a href="{G.REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
            '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'向 <code>POST https://anyaigc.ai/v1beta/models/{model}:generateContent</code> 发请求（Gemini 原生格式）；已有 OpenAI SDK 的项目也可以用 <code>/v1/chat/completions</code>，<code>model</code> 填 <code>{model}</code>。']


QS_NOTE = (f'请求头用 <code>Authorization: Bearer &lt;API Key&gt;</code>。<code>imageConfig.imageSize</code> 支持 <code>1K</code>、<code>2K</code>、<code>4K</code>，默认 1K；'
           f'<code>response_format</code> 是平台扩展字段，填 <code>url</code> 时返回 <code>fileData.fileUri</code> 临时链接（仅非流式），不填默认返回 base64。'
           f'安全策略拦截时 <code>finishReason</code> 为 <code>SAFETY</code> 或 <code>PROHIBITED_CONTENT</code>，不返回图片。')


# ---------------------------------------------------------------- 价格与对比
def price_rows(slug):
    m = MODELS[slug]
    ids = '<br>'.join(f'<code>{i}</code>' for i in m['ids'])
    rows = []
    for res, p in CNY[slug]:
        off = ' / '.join(f'${OFFICIAL[slug][r.strip()]}' for r in res.split('/'))
        rows.append(f'<th scope="row">{res} 出图<small>{"、".join(r.strip() for r in res.split("/"))} 分辨率</small></th><td>{ids}</td>'
                    f'<td class="o-num o-hl">¥{p} / 张</td><td class="o-num nb-off">{off}</td>')
    return rows


PRICE_HEAD = [('分辨率', False), ('模型名', False), ('AnyAIGC 单价', True), ('Google 官方（美元 / 张）', True)]


def price_table(slugs):
    groups = [(MODELS[s]['name'] if len(slugs) > 1 else None, price_rows(s)) for s in slugs]
    return G.table('Nano Banana 按张计费价格（人民币 / 张）', PRICE_HEAD, groups)


BILLING = [('按张计费', '按出图分辨率分档，固定单价'), ('每次 1 张', '一次请求通常返回 1 张图片'),
           (CONC, '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')]
PRICE_NOTE = ('AnyAIGC 单价为人民币，按成功提交计费，提示词和参考图不另外收费；Google 官方价为 Standard 档美元价，引自 '
              '<a href="https://ai.google.dev/gemini-api/docs/pricing" target="_blank" rel="noopener">Gemini API 定价页</a>，仅供参考。实时价格以'
              f'<a href="{PRICING}">模型广场</a>为准。')


def compare_table(cur=None):
    cols = MODEL_SLUGS
    def cls(s):
        return ' class="nb-cur"' if s == cur else ''
    head = [('', False)] + [(f'<a href="/zh/models/{s}">{MODELS[s]["name"]}</a>', False) for s in cols]
    def row(label, vals):
        return f'<th scope="row">{label}</th>' + ''.join(f'<td{cls(s)}>{v}</td>' for s, v in zip(cols, vals))
    rows = [
        row('AnyAIGC 模型名', ['<br>'.join(f'<code>{i}</code>' for i in MODELS[s]['ids']) for s in cols]),
        row('Google 官方名', [MODELS[s]['google'] for s in cols]),
        row('定位', ['Nano Banana 2 的升级版，画质、文字和多轮一致性更好', 'Flash 级速度的主力生图模型', '推理驱动的专业级生图，适合复杂排版和精修']),
        row('输出分辨率', ['1K / 2K / 4K', '1K / 2K / 4K（官方另有 512px）', '1K / 2K / 4K']),
        row('宽高比', ['14 种，含 1:4、4:1、1:8、8:1', '14 种，含 1:4、4:1、1:8、8:1', '10 种（1:1 到 21:9）']),
        row('参考图（最多 14 张）', ['物体 10 张 + 角色 4 张', '物体 10 张 + 角色 4 张', '物体 6 张 + 角色 5 张 + 风格 3 张']),
        row('Google 搜索 grounding', ['网页 + 图片搜索', '网页 + 图片搜索', '网页搜索']),
        row('思考（Thinking）', ['可配置', '可配置', '默认开启，不可关闭']),
        row('AnyAIGC 价格', ['<br>'.join(f'{r} <strong>¥{p}</strong>' for r, p in CNY[s]) for s in cols]),
        row('Google 官方价', [f'1K ${OFFICIAL[s]["1K"]} · 2K ${OFFICIAL[s]["2K"]} · 4K ${OFFICIAL[s]["4K"]}' for s in cols]),
        row('发布时间', ['2026-10-06 正式版', '2026-02-26 预览，2026-05-28 正式版', '2025-11-20 预览，2026-05-28 正式版']),
    ]
    return G.table('Nano Banana 2.1、Nano Banana 2 与 Nano Banana Pro 参数对比', head, [(None, rows)], cls='nb-compare')


COMPARE_NOTE = (f'参数引自 Google <a href="{GOOGLE_DOC["zh"]}" target="_blank" rel="noopener">Gemini API 图片生成文档</a>与模型列表（2026-10-25 读取）。'
                f'调用字段以 <a href="{DOCS_21}" target="_blank" rel="noopener">AnyAIGC API 文档</a>为准。')

USES = [
    ('电商', '商品主图与场景图', '上传商品图，换背景、换场景、换模特，保持包装和文字不变；一个 SKU 一次出多种比例。'),
    ('营销', '海报与多语言改字', '直接在画面里写标题和卖点，或把现有海报上的文字翻译成其他语言，版式保持不动。'),
    ('社媒', '多平台配图', '同一个创意按 1:1、4:5、9:16、16:9 分别出图，适配朋友圈、小红书、抖音和网站横幅。'),
    ('教育', '信息图与图解', '把知识点、流程或数据讲成带标注的信息图，借助 Google 搜索让画面里的事实更准确。'),
    ('IP', '角色与形象一致', '用几张角色参考图生成多场景、多姿势的连续画面，适合绘本、漫画分镜和品牌形象。'),
    ('设计', '草图转效果图', '手绘线稿、户型图或产品草图加一句描述，直接变成写实效果图，再用对话继续修改细节。'),
]


# ---------------------------------------------------------------- 总览页
def hub():
    s21, s2, sp = 'nano-banana-2.1', 'nano-banana-2', 'nano-banana-pro'
    models = [
        (f'/zh/models/{s21}', '最新 · 推荐', 'Nano Banana 2.1', 'gemini-nano-banana-2.1',
         'Google 2026 年 10 月发布的 Nano Banana 2 升级版。画质、文字渲染和多轮角色一致性都有提升，支持 1:8、8:1 超宽比例。', cny_min(s21), '/ 张起（1K）', False),
        (f'/zh/models/{sp}', '专业级', 'Nano Banana Pro', 'gemini-3-pro-image',
         '基于 Gemini 3 Pro 的推理型生图模型，适合复杂排版、密集文字、商业精修和需要真实世界知识的画面。', cny_min(sp), '/ 张起（1K/2K）', False),
        (f'/zh/models/{s2}', 'Flash 速度', 'Nano Banana 2', 'gemini-3.1-flash-image',
         'Gemini 3.1 Flash Image，速度快、成本低。Google 建议新项目改用 2.1，已有集成可以继续调用。', cny_min(s2), '/ 张起（1K/2K）', False),
    ]
    choose = G.table('Nano Banana 型号怎么选', [('需求', False), ('推荐型号', False), ('原因', False)], [(None, [
        f'<th scope="row">新项目、日常出图、批量生成</th><td><a href="/zh/models/{s21}">Nano Banana 2.1</a></td><td>全系单价最低（1K {cny_min(s21)} / 张），官方定位为主力生图模型</td>',
        f'<th scope="row">海报、信息图、密集文字排版</th><td><a href="/zh/models/{sp}">Nano Banana Pro</a></td><td>推理能力更强，复杂版式和文字更稳，2K 与 1K 同价</td>',
        f'<th scope="row">4K 高清大图、印刷物料</th><td><a href="/zh/models/{sp}">Nano Banana Pro</a> / <a href="/zh/models/{s21}">2.1</a></td><td>两者都支持 4K；Pro 细节更强，2.1 每张更便宜（¥{CNY[s21][2][1]}）</td>',
        f'<th scope="row">超宽横幅、长图（1:8、8:1）</th><td><a href="/zh/models/{s21}">Nano Banana 2.1</a></td><td>2.1 修复了极端比例在 2K / 4K 下的拼接问题</td>',
        f'<th scope="row">已有 gemini-3.1-flash-image 集成</th><td><a href="/zh/models/{s2}">Nano Banana 2</a></td><td>接口不变可以继续用，迁移到 2.1 只需改模型名</td>',
    ])])
    faqs = [
        ('Nano Banana API 多少钱？',
         f'AnyAIGC 上 Nano Banana 全系按张计费：Nano Banana 2.1 {price_str(s21)}；Nano Banana 2 {price_str(s2)}；Nano Banana Pro {price_str(sp)}。按成功提交计费，实时价格以模型广场为准。'),
        ('Nano Banana 2.1、Nano Banana 2 和 Nano Banana Pro 有什么区别？',
         'Nano Banana 2.1（gemini-nano-banana-2.1）是 Google 2026 年 10 月 6 日发布的 Nano Banana 2 升级版，画质、文字渲染和多轮一致性更好。Nano Banana 2（gemini-3.1-flash-image）是 Flash 级的高效生图模型。Nano Banana Pro（gemini-3-pro-image）基于 Gemini 3 Pro，带推理能力，适合复杂排版和专业级精修。三者都支持 1K、2K、4K 输出。'),
        ('Nano Banana 是哪个模型？和 Gemini 是什么关系？',
         'Nano Banana 是 Google Gemini 图像生成模型的昵称。最早的 Nano Banana 是 Gemini 2.5 Flash Image，之后有 Nano Banana Pro（Gemini 3 Pro Image）、Nano Banana 2（Gemini 3.1 Flash Image）和 Nano Banana 2.1。它们都通过 Gemini API 的 generateContent 接口调用。'),
        ('支持哪些接口？可以改图吗？',
         f'支持 Gemini 原生格式 <code>POST /v1beta/models/&lt;模型名&gt;:generateContent</code>，也支持 OpenAI 兼容的 <code>/v1/chat/completions</code>。文生图只放一段文字；改图、多图合成时把一段文字和多张参考图（inlineData）放在同一个 parts 里，最多 14 张参考图。字段说明见 <a href="{DOCS_21}">AnyAIGC API 文档</a>。'),
        conc_faq('Nano Banana 全系'),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(
        name='Nano Banana', docs=DOCS_21,
        title='Nano Banana API 价格与接入｜2.1、2 与 Pro 全系 - AnyAIGC',
        desc=f'Nano Banana API 全系：Nano Banana 2.1、Nano Banana 2、Nano Banana Pro，按张计费 {cny_min(s21)} 起，支持 4K 与多图编辑，并发不限，支持对公转账与增值税专票。',
        og_desc=f'一个 Key 调用 Google Nano Banana 全系：2.1、2、Pro，按张 {cny_min(s21)} 起，4K 出图，并发不限。',
        og_alt='AnyAIGC Nano Banana API：2.1、2 与 Pro 全系',
        keywords='Nano Banana API,Nano Banana API 价格,Nano Banana 2.1 API,Nano Banana Pro API,Nano Banana 2 API,gemini-nano-banana-2.1,gemini-3-pro-image,gemini-3.1-flash-image,Gemini 图像生成 API,Nano Banana API key 国内,Nano Banana API 企业,Nano Banana API 发票,AnyAIGC',
        crumb='Nano Banana', product='Nano Banana API（AnyAIGC）', sku='nano-banana', currency='CNY',
        product_desc='通过 AnyAIGC 调用 Google Nano Banana 全系图像模型：gemini-nano-banana-2.1、gemini-3.1-flash-image、gemini-3-pro-image，兼容 Gemini generateContent 与 /v1/chat/completions。',
        offers=[(f'{MODELS[s]["name"]} {r}（每张）', p) for s in (s21, s2, sp) for r, p in CNY[s]],
        eyebrow='Google · Nano Banana 系列', h1='Nano Banana API<small>Nano Banana 2.1、2 与 Pro 全系</small>',
        lead=f'一个 API Key 调用 Google 全部 Nano Banana 型号，<strong>按张 {cny_min(s21)} 起</strong>。',
        lead_sub='文字渲染、多图合成、对话式改图和 4K 出图都能直接走 API。按分辨率固定单价，不按 token 算，成本一眼算清。',
        facts=[('起步价', f'{cny_min(s21)} / 张'), ('最高', '4K'), ('参考图', '最多 14 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
        hero_imgs=('golden-hour-portrait', 'neon-portrait', 'can-localization'),
        quote='想到什么，就画出来。<span>写实、俏皮、精细或天马行空，一句话描述就够了。</span>',
        models_h2='Nano Banana 全系型号', models_lead='三个型号接口相同，只需切换 <code>model</code>。点卡片查看每个型号的价格、参数和代码示例。',
        models=models,
        compare_h2='Nano Banana 2.1 vs 2 vs Pro 参数对比', compare_lead='分辨率、宽高比、参考图数量和官方价格放在一张表里。', compare_table=compare_table(),
        compare_note=COMPARE_NOTE,
        choose=choose,
        price_h2='Nano Banana API 价格', price_lead='全系按张计费，单价按出图分辨率分档。同一个 API Key、同一份余额调用全部型号。',
        billing=BILLING, billing_label='计费要点', price_tables=price_table([s21, sp, s2]), price_note=PRICE_NOTE,
        price_extra=f'      <h3 class="nb-h3 o-reveal">型号怎么选</h3>{NL}' + choose,
        costs_h3='成本示例', costs_lead='按上表单价直接相加，不含其他费用。',
        costs=[('1,000 张商品图', f'Nano Banana 2.1，1K，1,000 × ¥{CNY[s21][0][1]}', '¥80', '日常批量出图'),
               ('100 张 2K 海报', f'Nano Banana Pro，2K，100 × ¥{CNY[sp][0][1]}', '¥22', '1K 与 2K 同价'),
               ('50 张 4K 大图', f'Nano Banana 2.1，4K，50 × ¥{CNY[s21][2][1]}', '¥14', '换成 Pro 为 ¥19.5')],
        gallery_h2='Nano Banana 能画什么', gallery_lead='海报排版、多语言改字、多图合成、信息图和写实摄影，下面是 Google 官方发布的示例。',
        gallery=['can-localization', 'multi-character-composite', 'woodchuck-text', 'stag-day-night-edit', 'earth-layers-infographic', 'golden-hour-portrait',
                 'sketch-to-car', 'impossible-typography', 'spinning-red-dress'],
        uses_h2='Nano Banana API 使用场景', uses=USES,
        qs_h2='快速接入 Nano Banana API', steps=steps('gemini-nano-banana-2.1'), codes=codes('gemini-nano-banana-2.1'),
        callout='换型号只改 <code>MODEL</code>：<code>gemini-nano-banana-2.1</code>、<code>gemini-3.1-flash-image</code> 或 <code>gemini-3-pro-image</code>，请求和返回格式完全相同。',
        qs_note=QS_NOTE,
        family_h2='Nano Banana 系列专题', family_lead='每个型号单独一页，含完整价格表和代码示例。',
        faq_h2='Nano Banana API 常见问题', faqs=faqs,
        final_h2='现在开始调用 Nano Banana', final_p='注册即送 200 万 tokens 试用额度，一个 Key 调用 Nano Banana 全系和 300+ 其他模型。',
    )


# ---------------------------------------------------------------- 型号页
def model_page(slug):
    m = MODELS[slug]
    name, mid = m['name'], m['ids'][0]
    p = CNY[slug]
    base = dict(name=name, crumb=name, sku=mid, currency='CNY', docs=DOCS_21 if slug == 'nano-banana-2.1' else DOCS_GEMINI,
                product=f'{name} API（AnyAIGC）',
                offers=[(f'{name} {r}（每张）', v) for r, v in p],
                billing=BILLING, billing_label='计费要点', price_tables=price_table([slug]), price_note=PRICE_NOTE,
                costs_h3='成本示例', costs_lead='按上表单价直接相加，不含其他费用。',
                compare_h2=f'{name} 与同系列对比', compare_table=compare_table(slug), compare_note=COMPARE_NOTE,
                uses_h2=f'{name} API 使用场景', uses=USES,
                qs_h2=f'快速接入 {name} API', steps=steps(mid),
                qs_note=QS_NOTE,
                family_h2='Nano Banana 系列其他型号', family_lead='接口相同，换 <code>model</code> 即可切换。',
                faq_h2=f'{name} API 常见问题',
                quote='想到什么，就画出来。<span>写实、俏皮、精细或天马行空，一句话描述就够了。</span>')

    if slug == 'nano-banana-2.1':
        faqs = [
            ('Nano Banana 2.1 API 多少钱？',
             f'AnyAIGC 上 Nano Banana 2.1 按张计费：{price_str(slug)}。Google 官方价为 1K $0.0336、2K $0.0504、4K $0.113 每张。按成功提交计费，实时价格以模型广场为准。'),
            ('Nano Banana 2.1 是什么？什么时候发布的？',
             'Nano Banana 2.1（Gemini Nano Banana 2.1，模型名 gemini-nano-banana-2.1）是 Google 在 2026 年 10 月 6 日发布的图像生成与编辑模型，是 Nano Banana 2（Gemini 3.1 Flash Image）的升级版。Google 把它定位为 Nano Banana 系列的主力高效模型。'),
            ('Nano Banana 2.1 和 Nano Banana 2 有什么区别？',
             '2.1 在画质、文字渲染和多轮对话中的角色一致性上都有提升，修复了 1:4、4:1、1:8、8:1 等极端比例在 2K / 4K 下的拼接问题，单价也更低。2.1 不支持 512px（0.5K）档位，只支持 1K、2K、4K。接口完全相同，迁移只需把 <code>model</code> 换成 <code>gemini-nano-banana-2.1</code>。'),
            ('Nano Banana 2.1 和 Nano Banana Pro 怎么选？',
             f'日常出图、批量生成和超宽比例选 2.1，单价更低（1K {cny_min(slug)} / 张）。版式复杂、文字密集、需要更强推理和细节的商业物料选 Pro（1K/2K {cny_min("nano-banana-pro")} / 张）。'),
            ('支持哪些分辨率和宽高比？',
             f'<code>imageConfig.imageSize</code> 支持 <code>1K</code>、<code>2K</code>、<code>4K</code>，默认 1K，不支持 512。<code>imageConfig.aspectRatio</code> 支持 {"、".join(RATIOS_14)} 共 14 种。例如 16:9 的 2K 输出是 2752×1536，4K 是 5504×3072。'),
            ('能上传几张参考图？可以开关思考吗？',
             '一次请求最多 14 张参考图：最多 10 张物体图和 4 张角色图。思考用 <code>thinkingConfig.thinkingLevel</code> 控制，支持 <code>minimal</code> 和 <code>high</code>，不支持 thinkingBudget；也可以在模型名后加 <code>-thinking</code> 或 <code>-nothinking</code>。'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Nano Banana 2.1 API 价格与接入｜4K 生图 {cny_min(slug)} 起 - AnyAIGC',
            desc=f'Nano Banana 2.1 API（gemini-nano-banana-2.1）按张计费，1K {cny_min(slug)}、2K ¥0.12、4K ¥0.28，支持 14 种比例和多图编辑，并发不限，支持对公转账与增值税专票。',
            og_desc=f'Google Nano Banana 2.1 API：1K {cny_min(slug)} / 张起，4K 出图、14 种比例、多图编辑，并发不限。',
            og_alt='AnyAIGC Nano Banana 2.1 API 价格与接入',
            keywords='Nano Banana 2.1 API,Nano Banana 2.1 API 价格,gemini-nano-banana-2.1,Nano Banana 2.1 接入,Nano Banana 2.1 4K,Nano Banana 2.1 vs Pro,Nano Banana API key 国内,Nano Banana API 企业,Nano Banana API 发票,AnyAIGC',
            product_desc='通过 AnyAIGC 调用 Google Nano Banana 2.1（gemini-nano-banana-2.1）图像生成与编辑模型，按张计费，兼容 Gemini generateContent。',
            eyebrow='Google · Nano Banana 2.1', h1='Nano Banana 2.1 API<small>gemini-nano-banana-2.1</small>',
            lead=f'Google 最新的 Nano Banana 升级版，<strong>1K 每张 {cny_min(slug)}</strong>。',
            lead_sub='画质、文字渲染和多轮角色一致性都比 Nano Banana 2 更好，支持 1K、2K、4K 输出和 1:8、8:1 超宽比例。',
            facts=[('1K', f'{cny_min(slug)} / 张'), ('2K', '¥0.12'), ('4K', '¥0.28'), ('比例', '14 种'), ('并发', '不限'), ('企业', '对公 · 专票')],
            hero_imgs=('foggy-orange-sedan', 'indie-film-posters', 'spinning-red-dress'),
            about_h2='Nano Banana 2.1 是什么',
            about_ps=['Nano Banana 2.1 是 Google 在 2026 年 10 月 6 日发布的图像生成与编辑模型，Google 官方名为 Gemini Nano Banana 2.1，是 Nano Banana 2（Gemini 3.1 Flash Image）的升级版。它保持 Flash 级的速度和成本，同时提升了画质、文字渲染和多轮对话里的角色一致性。',
                      '在 AnyAIGC 上，模型名是 <code>gemini-nano-banana-2.1</code>，按出图分辨率按张计费：1K ¥0.08、2K ¥0.12、4K ¥0.28。不需要 Google 账号和海外信用卡，国内网络可直接调用。'],
            spec=[('模型名', '<code>gemini-nano-banana-2.1</code>'), ('输出分辨率', '1K / 2K / 4K（默认 1K）'), ('宽高比', '14 种，含 1:4、4:1、1:8、8:1'),
                  ('参考图', '最多 14 张（物体 10 + 角色 4）'), ('思考', 'minimal / high'), ('接口', 'generateContent · chat/completions')],
            features_h2='Nano Banana 2.1 能做什么',
            features=[('文字渲染更准', '海报标题、包装文字、菜单和信息图里的文字更清晰，可以指定字体风格和排版。', 'desert-poster-design'),
                      ('一句话改图', '上传图片，用自然语言说要改什么：换光线、换背景、去掉物体，其余部分保持不变，还能多轮继续改。', 'stag-day-night-edit'),
                      ('多图合成与角色一致', '最多 14 张参考图，其中 4 张角色图用来保持人物在多张画面里长得一样。', 'multi-character-composite'),
                      ('超宽与长图比例', '支持 4:1、8:1、1:4、1:8，2.1 修复了这些比例在 2K / 4K 下的拼接问题，适合横幅和长图。', 'indie-film-posters')],
            price_h2='Nano Banana 2.1 API 价格', price_lead='按张计费，单价按出图分辨率分为 1K、2K、4K 三档。',
            costs=[('1,000 张商品图', '1K，1,000 × ¥0.08', '¥80', '日常批量出图'),
                   ('200 张社媒配图', '2K，200 × ¥0.12', '¥24', '适合 4:5、9:16 竖图'),
                   ('50 张 4K 大图', '4K，50 × ¥0.28', '¥14', '印刷与大屏物料')],
            gallery_h2='Nano Banana 2.1 示例', gallery_lead='下面是 Google 在 Nano Banana 系列模型页发布的示例图。',
            gallery=['desert-poster-design', 'indie-film-posters', 'earth-layers-infographic', 'foggy-orange-sedan', 'spinning-red-dress', 'neon-portrait'],
            codes=codes(mid),
            callout='想关掉思考换取更快返回，可以把模型名写成 <code>gemini-nano-banana-2.1-nothinking</code>；需要更强的构图推理用 <code>-thinking</code>。',
            faqs=faqs,
            final_h2='现在开始调用 Nano Banana 2.1', final_p=f'注册即送 200 万 tokens 试用额度，1K 每张 {cny_min(slug)}，并发不限。',
        )

    if slug == 'nano-banana-2':
        faqs = [
            ('Nano Banana 2 API 多少钱？',
             f'AnyAIGC 上 Nano Banana 2 按张计费：{price_str(slug)}，<code>gemini-3.1-flash-image</code> 和 <code>gemini-3.1-flash-image-preview</code> 同价。Google 官方价为 1K $0.067、2K $0.101、4K $0.151 每张。实时价格以模型广场为准。'),
            ('Nano Banana 2 停用了吗？要迁移到 2.1 吗？',
             'Google 已把 Nano Banana 2.1 列为 gemini-3.1-flash-image 的推荐替代型号，但目前没有公布停用日期，AnyAIGC 上可以继续调用。新项目建议直接用 <a href="/zh/models/nano-banana-2.1">Nano Banana 2.1</a>，迁移只需改模型名，请求格式不变。'),
            ('Nano Banana 2 是哪个模型？',
             'Nano Banana 2 是 Google Gemini 3.1 Flash Image 的昵称，2026 年 2 月 26 日发布预览版，5 月 28 日推出正式版 gemini-3.1-flash-image。它把 Pro 级的大部分能力带到了 Flash 级的速度和价格。'),
            ('Nano Banana 2 和 Nano Banana Pro 哪个好？',
             '名字里的“2”不代表比 Pro 新一代。Nano Banana 2 是 Flash 级模型，速度更快、更便宜，适合批量出图；Pro 基于 Gemini 3 Pro，推理更强，复杂排版和细节更稳。'),
            ('支持哪些分辨率和宽高比？',
             f'AnyAIGC 按 1K/2K 和 4K 两档计价。<code>imageConfig.aspectRatio</code> 支持 {"、".join(RATIOS_14)} 共 14 种；一次请求最多 14 张参考图（物体 10 张 + 角色 4 张）。'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Nano Banana 2 API 价格与接入｜gemini-3.1-flash-image - AnyAIGC',
            desc=f'Nano Banana 2 API（gemini-3.1-flash-image）按张计费，1K/2K {cny_min(slug)}、4K ¥0.19，支持 14 种比例和多图编辑，并发不限，支持对公转账与增值税专票。',
            og_desc=f'Google Nano Banana 2（Gemini 3.1 Flash Image）API：1K/2K {cny_min(slug)} / 张，4K ¥0.19，并发不限。',
            og_alt='AnyAIGC Nano Banana 2 API 价格与接入',
            keywords='Nano Banana 2 API,Nano Banana 2 API 价格,gemini-3.1-flash-image API,Gemini 3.1 Flash Image API,gemini-3.1-flash-image-preview,Nano Banana 2 迁移 2.1,Nano Banana API 企业,Nano Banana API 发票,AnyAIGC',
            product_desc='通过 AnyAIGC 调用 Google Nano Banana 2（gemini-3.1-flash-image）图像生成与编辑模型，按张计费，兼容 Gemini generateContent。',
            eyebrow='Google · Nano Banana 2', h1='Nano Banana 2 API<small>gemini-3.1-flash-image</small>',
            lead=f'Gemini 3.1 Flash Image，<strong>1K / 2K 每张 {cny_min(slug)}</strong>。',
            lead_sub='Flash 级的速度，Pro 级的大部分能力：文字渲染、多图合成、Google 搜索 grounding 和 4K 输出。',
            notice='Google 已推荐新项目改用 <a href="/zh/models/nano-banana-2.1">Nano Banana 2.1</a>（更便宜、画质更好），Nano Banana 2 暂无停用日期，可以继续调用。',
            facts=[('1K / 2K', f'{cny_min(slug)} / 张'), ('4K', '¥0.19'), ('比例', '14 种'), ('并发', '不限'), ('企业', '对公 · 专票')],
            hero_imgs=('earth-layers-infographic', 'spinning-red-dress', 'foggy-orange-sedan'),
            about_h2='Nano Banana 2 是什么',
            about_ps=['Nano Banana 2 是 Google Gemini 3.1 Flash Image 的昵称，2026 年 2 月 26 日发布预览版，5 月 28 日推出正式版。它面向高吞吐的开发场景，在保持 Flash 级速度和成本的同时，提供接近 Pro 的画质、文字渲染和编辑能力。',
                      '在 AnyAIGC 上，正式版 <code>gemini-3.1-flash-image</code> 和预览版 <code>gemini-3.1-flash-image-preview</code> 都可以调用，价格相同：1K / 2K 每张 ¥0.10，4K 每张 ¥0.19。'],
            spec=[('模型名', '<code>gemini-3.1-flash-image</code>'), ('预览版', '<code>gemini-3.1-flash-image-preview</code>'), ('宽高比', '14 种，含 1:4、4:1、1:8、8:1'),
                  ('参考图', '最多 14 张（物体 10 + 角色 4）'), ('Google 搜索', '网页 + 图片搜索'), ('接口', 'generateContent · chat/completions')],
            features_h2='Nano Banana 2 能做什么',
            features=[('借助搜索画准事实', '结合 Google 网页和图片搜索，地标、冷门物品和信息图里的事实细节更准确。', 'earth-layers-infographic'),
                      ('对话式改图', '上传图片后用一句话修改，支持多轮连续编辑，适合迭代海报和商品图。', 'stag-day-night-edit'),
                      ('清晰的文字', '画面里的标题、标签和说明文字清楚可读，适合海报、菜单和社媒图。', 'woodchuck-text'),
                      ('电影感写实', '光线、景深和动态模糊都能用提示词控制，出图速度快。', 'spinning-red-dress')],
            price_h2='Nano Banana 2 API 价格', price_lead='按张计费，1K 与 2K 同价，4K 单独计价。',
            costs=[('1,000 张商品图', '1K，1,000 × ¥0.10', '¥100', '1K 与 2K 同价'),
                   ('500 张 2K 社媒图', '2K，500 × ¥0.10', '¥50', '直接出 2K 不加价'),
                   ('100 张 4K 大图', '4K，100 × ¥0.19', '¥19', f'换成 2.1 4K 为 ¥{100 * float(CNY["nano-banana-2.1"][2][1]):.0f}')],
            gallery_h2='Nano Banana 2 示例', gallery_lead='下面是 Google 在 Nano Banana 系列模型页发布的示例图。',
            gallery=['earth-layers-infographic', 'woodchuck-text', 'spinning-red-dress', 'foggy-orange-sedan', 'spider-macro', 'golden-hour-portrait'],
            codes=codes(mid),
            callout='迁移到 Nano Banana 2.1 只需把 <code>MODEL</code> 改成 <code>gemini-nano-banana-2.1</code>，请求和返回格式不变。',
            faqs=faqs,
            final_h2='现在开始调用 Nano Banana 2', final_p=f'注册即送 200 万 tokens 试用额度，1K / 2K 每张 {cny_min(slug)}，并发不限。',
        )

    # Nano Banana Pro
    faqs = [
        ('Nano Banana Pro API 多少钱？',
         f'AnyAIGC 上 Nano Banana Pro 按张计费：{price_str(slug)}，<code>gemini-3-pro-image</code> 和 <code>gemini-3-pro-image-preview</code> 同价。Google 官方价为 1K / 2K $0.134、4K $0.24 每张。实时价格以模型广场为准。'),
        ('Nano Banana Pro 是哪个模型？',
         'Nano Banana Pro 是 Google Gemini 3 Pro Image 的昵称，2025 年 11 月 20 日发布预览版，2026 年 5 月 28 日推出正式版 gemini-3-pro-image。它带推理能力，适合复杂版式、密集文字、商业精修和需要真实世界知识的画面。'),
        ('Nano Banana Pro 和 Nano Banana 2.1 怎么选？',
         f'需要复杂排版、密集文字、多人物一致或专业级细节时选 Pro。日常出图、批量生成或需要 1:8、8:1 超宽比例时选 <a href="/zh/models/nano-banana-2.1">Nano Banana 2.1</a>，单价更低（1K {cny_min("nano-banana-2.1")} / 张）。'),
        ('Nano Banana Pro 支持 4K 吗？有哪些比例？',
         '支持。<code>imageConfig.imageSize</code> 可选 <code>1K</code>、<code>2K</code>、<code>4K</code>，1K 和 2K 同价。<code>imageConfig.aspectRatio</code> 支持 1:1、2:3、3:2、3:4、4:3、4:5、5:4、9:16、16:9、21:9 共 10 种。'),
        ('能上传几张参考图？能保持人物一致吗？',
         '一次请求最多 14 张参考图：最多 6 张物体图、5 张角色图和 3 张风格参考图。角色图用来让同一个人物在多张画面里保持一致。'),
        conc_faq(name),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(base,
        title=f'Nano Banana Pro API 价格与接入｜4K 生图 {cny_min(slug)} 起 - AnyAIGC',
        desc=f'Nano Banana Pro API（gemini-3-pro-image）按张计费，1K/2K {cny_min(slug)}、4K ¥0.39，擅长文字渲染与复杂排版，并发不限，支持对公转账与增值税专票。',
        og_desc=f'Google Nano Banana Pro（Gemini 3 Pro Image）API：1K/2K {cny_min(slug)} / 张，4K ¥0.39，并发不限。',
        og_alt='AnyAIGC Nano Banana Pro API 价格与接入',
        keywords='Nano Banana Pro API,Nano Banana Pro API 价格,gemini-3-pro-image API,Gemini 3 Pro Image API,gemini-3-pro-image-preview,Nano Banana Pro 4K,Nano Banana Pro 国内调用,Nano Banana API 企业,Nano Banana API 发票,AnyAIGC',
        product_desc='通过 AnyAIGC 调用 Google Nano Banana Pro（gemini-3-pro-image）专业级图像生成与编辑模型，按张计费，兼容 Gemini generateContent。',
        eyebrow='Google · Nano Banana Pro', h1='Nano Banana Pro API<small>gemini-3-pro-image</small>',
        lead=f'Gemini 3 Pro Image，<strong>1K / 2K 每张 {cny_min(slug)}</strong>。',
        lead_sub='推理驱动的专业级生图：复杂版式、密集文字、多人物一致和 4K 细节，适合商业物料和精修。',
        facts=[('1K / 2K', f'{cny_min(slug)} / 张'), ('4K', '¥0.39'), ('参考图', '最多 14 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
        hero_imgs=('can-localization', 'futuristic-city', 'solar-infographic'),
        about_h2='Nano Banana Pro 是什么',
        about_ps=['Nano Banana Pro 是 Google Gemini 3 Pro Image 的昵称，基于 Gemini 3 Pro 构建，2025 年 11 月 20 日发布预览版，2026 年 5 月 28 日推出正式版。它在出图前会先推理构图和内容，适合复杂的平面设计、高保真商品图和需要真实世界知识的信息图。',
                  '在 AnyAIGC 上，正式版 <code>gemini-3-pro-image</code> 和预览版 <code>gemini-3-pro-image-preview</code> 都可以调用，价格相同：1K / 2K 每张 ¥0.22，4K 每张 ¥0.39。'],
        spec=[('模型名', '<code>gemini-3-pro-image</code>'), ('预览版', '<code>gemini-3-pro-image-preview</code>'), ('输出分辨率', '1K / 2K / 4K'),
              ('宽高比', '10 种（1:1 到 21:9）'), ('参考图', '物体 6 + 角色 5 + 风格 3'), ('接口', 'generateContent · chat/completions')],
        features_h2='Nano Banana Pro 能做什么',
        features=[('精准改字与本地化', '把包装、海报上的文字翻译成其他语言，字体和版式保持不变。', 'can-localization'),
                  ('密集文字与信息图', '长句、多段说明和标注都能清楚排在画面里，适合教学图和产品说明图。', 'solar-infographic'),
                  ('多图合成', '最多 14 张参考图合成一张画面，角色图保持人物一致，风格图统一画风。', 'multi-character-composite'),
                  ('草图转效果图', '线稿加材质参考，直接生成立体写实的效果图。', 'sketch-to-car')],
        price_h2='Nano Banana Pro API 价格', price_lead='按张计费，1K 与 2K 同价，4K 单独计价。',
        costs=[('100 张 2K 海报', '2K，100 × ¥0.22', '¥22', '1K 与 2K 同价'),
               ('100 张 4K 物料', '4K，100 × ¥0.39', '¥39', '印刷与大屏'),
               ('1,000 张商品精修图', '2K，1,000 × ¥0.22', '¥220', '直接出 2K 不加价')],
        gallery_h2='Nano Banana Pro 示例', gallery_lead='下面是 Google 在 Nano Banana Pro 模型页发布的示例图。',
        gallery=['can-localization', 'woodchuck-text', 'impossible-typography', 'futuristic-city', 'sketch-to-car', 'stag-day-night-edit'],
        codes=codes(mid, '4:3', '4K'),
        callout='Nano Banana Pro 的思考默认开启、不能关闭；宽高比只支持 10 种，不支持 1:4、4:1、1:8、8:1。',
        faqs=faqs,
        final_h2='现在开始调用 Nano Banana Pro', final_p=f'注册即送 200 万 tokens 试用额度，1K / 2K 每张 {cny_min(slug)}，并发不限。',
    )


def build(slug):
    return hub() if slug == 'nano-banana' else model_page(slug)
