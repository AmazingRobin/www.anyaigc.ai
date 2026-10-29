# Seedream 系列专题页中文文案。build(slug) 返回页面用的字典。价格用人民币（模型广场最低价按 6.718 换算）。
from seedream_data import MODELS, MODEL_SLUGS, CNY, USD, SUPPORT, PRICING, DOCS, VOLC_DOC, cny
import seedream_layout as G

NL = '\n'

FAMILY = [
    ('seedream', '总览', 'Seedream 全系', '5 个型号的价格与参数对比'),
    ('seedream-5.0-pro', '最新', 'Seedream 5.0 Pro', f'信息图、精准编辑、多语种 · {cny("seedream-5.0-pro")} / 张起'),
    ('seedream-5.0-lite', '高性价比', 'Seedream 5.0 lite', f'联网检索、组图、4K · {cny("seedream-5.0-lite")} / 张起'),
    ('seedream-4.5', '', 'Seedream 4.5', f'海报排版、多图融合 · {cny("seedream-4.5")} / 张起'),
    ('seedream-4.0', '', 'Seedream 4.0', f'生成编辑一体、组图 · {cny("seedream-4.0")} / 张起'),
    ('seedream-3.0', '旧版', 'Seedream 3.0', f'纯文生图 · {cny("seedream-3.0")} / 次'),
]

COMMON_FAQ = [
    ('AnyAIGC 能开发票吗？支持增值税专票吗？',
     '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
    ('企业可以对公转账和签合同吗？',
     f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
]
LICENSE_FAQ = ('生成的图片可以商用吗？能去掉水印吗？',
               '图片的使用权和内容政策以字节跳动 / 火山引擎官方条款为准。请求里把 <code>watermark</code> 设为 <code>false</code> 就不会在画面右下角加「AI 生成」水印。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用；涉及人物肖像、品牌商标等内容时，请自行确认授权。')


def conc_faq(name):
    return ('并发有限制吗？国内能直接调用吗？',
            f'AnyAIGC 对 {name} 不设并发限制，所有用户默认享有。接口地址是 <code>https://anyaigc.ai</code>，国内网络可以直接调用，不需要火山引擎账号和实名认证；同一个 Key 还能调用平台上 300+ 其他模型。')


def price_note(slug=None):
    return ('单价为模型广场显示的最低价，按 1 美元 ≈ ¥6.718 换算成人民币；不同输出分辨率单价不同，2K、4K 等更高档位的实时价格以'
            f'<a href="{PRICING}">模型广场</a>为准。按成功生成计费，提示词和参考图不另外收费。')


# ---------------------------------------------------------------- 代码示例
PROMPT = '一张竖版 4:5 咖啡品牌海报，标题“秋日限定”，暖色调，留白干净，右下角放产品图'


def code_py(model, size='2K', extra=''):
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{PROMPT}",
        "size": "{size}",  # 显式传 size，不传会按更高档位计费
        "response_format": "url",  # 或 b64_json
        "watermark": False,{extra}
    }},
    timeout=300,
)
resp.raise_for_status()
for item in resp.json()["data"]:
    print(item["url"])  # 临时链接，请及时下载保存'''


def code_curl(model, size='2K'):
    return f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "{PROMPT}",
    "size": "{size}",
    "response_format": "url",
    "watermark": false
  }}\''''


def code_edit(model, size='2K'):
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

# image 传图片 URL 数组：可以是一张图（改图），也可以是多张（多图融合）
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "把图1的商品放进图2的场景里，保持商品外观和包装文字不变",
        "image": [
            "https://example.com/product.png",
            "https://example.com/scene.jpg",
        ],
        "size": "{size}",
        "response_format": "url",
        "watermark": False,
    }},
    timeout=300,
)
resp.raise_for_status()
print(resp.json()["data"][0]["url"])'''


def code_seq(model, size='2K'):
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

# 组图：一次请求生成多张内容关联的图片
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "生成 4 张同一只橘猫的四季插画：春天樱花、夏天海边、秋天落叶、冬天雪地，画风统一",
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {{"max_images": 4}},
        "size": "{size}",
        "response_format": "url",
        "watermark": False,
    }},
    timeout=600,
)
resp.raise_for_status()
for i, item in enumerate(resp.json()["data"], 1):
    print(i, item["url"])'''


def code_sdk(model, size='2K'):
    return f'''import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["ANYAIGC_API_KEY"], base_url="https://anyaigc.ai/v1")

img = client.images.generate(
    model="{model}",
    prompt="{PROMPT}",
    size="{size}",
    response_format="url",
    extra_body={{"watermark": False}},  # Seedream 专有字段放在 extra_body 里
)
print(img.data[0].url)'''


def codes(slug):
    m = MODELS[slug]
    mid = m['id']
    if slug == 'seedream-3.0':
        return [('py', 'Python', f'Python · {mid} 文生图', code_py(mid, '1024x1024')),
                ('curl', 'cURL', f'cURL · {mid} 文生图', code_curl(mid, '1024x1024')),
                ('sdk', 'OpenAI SDK', 'Python · OpenAI SDK', code_sdk(mid, '1024x1024'))]
    out = [('py', 'Python', f'Python · {mid} 文生图', code_py(mid)),
           ('curl', 'cURL', f'cURL · {mid} 文生图', code_curl(mid)),
           ('edit', '参考图编辑', f'Python · {mid} 多图融合', code_edit(mid))]
    if m['seq']:
        out.append(('seq', '组图', f'Python · {mid} 组图', code_seq(mid)))
    out.append(('sdk', 'OpenAI SDK', 'Python · OpenAI SDK', code_sdk(mid)))
    return out


def steps(mid):
    return [f'<a href="{G.REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
            '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
            f'向 <code>POST https://anyaigc.ai/v1/images/generations</code> 发请求（OpenAI 兼容格式），<code>model</code> 填 <code>{mid}</code>。']


QS_NOTE = (f'请求头用 <code>Authorization: Bearer &lt;API Key&gt;</code>。返回体是 <code>{{"created": ..., "data": [{{"url": ...}}]}}</code>，'
           f'<code>response_format</code> 填 <code>b64_json</code> 时返回 base64。<code>watermark</code> 默认为 true，需要无水印图请显式传 false。'
           f'字段说明见 <a href="{DOCS}" target="_blank" rel="noopener">AnyAIGC Seedream 接口文档</a>。')


# ---------------------------------------------------------------- 价格与对比
PRICE_HEAD = [('型号', False), ('模型名', False), ('计费方式', False), ('AnyAIGC 起步价', True), ('美元价', True)]


def price_row(slug):
    m = MODELS[slug]
    unit = '按次' if m['unit'] == '次' else '按张'
    return (f'<th scope="row"><a href="/zh/models/{slug}">{m["name"]}</a><small>{m["sizes"]}</small></th><td><code>{m["id"]}</code></td>'
            f'<td>{unit}</td><td class="o-num o-hl">{cny(slug)} / {m["unit"]}</td><td class="o-num sd-off">${USD[slug]}</td>')


def price_table(slugs):
    return G.table('Seedream API 价格（人民币）', PRICE_HEAD, [(None, [price_row(s) for s in slugs])])


def billing(slug=None):
    one = '一次返回 1 张；组图按实际生成张数计' if slug in (None, 'seedream-5.0-lite', 'seedream-4.5', 'seedream-4.0') else '一次请求返回 1 张图片'
    return [('按张计费', '固定单价，不按 token 算'), ('产出', one), ('并发不限', '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')]


def compare_table(cur=None):
    cols = MODEL_SLUGS
    def cls(s):
        return ' class="sd-cur"' if s == cur else ''
    head = [('', False)] + [(f'<a href="/zh/models/{s}">{MODELS[s]["name"]}</a>', False) for s in cols]
    def row(label, vals):
        return f'<th scope="row">{label}</th>' + ''.join(f'<td{cls(s)}>{v}</td>' for s, v in zip(cols, vals))
    rows = [
        row('AnyAIGC 模型名', [f'<code>{MODELS[s]["id"]}</code>' for s in cols]),
        row('定位', ['旗舰：智能思考、高密度信息图、交互式精准编辑', '轻量版：深度思考 + 联网检索，最高 4K', '海报排版、小字清晰、多图融合', '生成与编辑一体，组图', '旧版，纯文生图']),
        row('输出分辨率', [MODELS[s]['sizes'] for s in cols]),
        row('参考图', ['最多 10 张', '最多 14 张', '最多 14 张', '最多 14 张', '不支持']),
        row('组图（一次多张）', ['不支持', '最多 15 张', '最多 15 张', '最多 15 张', '不支持']),
        row('专有能力', ['图层拆分、框选编辑、透明背景、十余种语言', '联网搜索（web_search）', '保持原图人脸与光影', '风格迁移、知识类插画', '中英双语']),
        row('AnyAIGC 起步价', [f'<strong>{cny(s)}</strong> / {MODELS[s]["unit"]}' for s in cols]),
    ]
    return G.table('Seedream 5.0 Pro、5.0 lite、4.5、4.0、3.0 参数对比', head, [(None, rows)], cls='sd-compare')


COMPARE_NOTE = (f'参数引自<a href="{VOLC_DOC}" target="_blank" rel="noopener">火山方舟图片生成 API 文档</a>与字节跳动 Seed 模型页（2026-10-28 读取），'
                '3.0 参数引自 Seedream 3.0 技术报告。调用字段以 AnyAIGC 接口文档为准。')

USES = [
    ('电商', '商品主图与场景图', '上传商品图换背景、换场景，保持包装和文字不变；同一个 SKU 按 1:1、3:4、16:9 分别出图。'),
    ('营销', '海报与中文排版', '标题、卖点和小字直接写进画面，中文渲染清晰，适合活动海报、长图和社媒封面。'),
    ('教育', '信息图与讲解图', '把知识点、流程和数据做成结构清晰的信息图，5.0 Pro 擅长高密度信息排版。'),
    ('内容', '系列插画与分镜', '用组图一次生成风格统一的多张画面，适合绘本、漫画分镜和品牌 IP 形象。'),
    ('设计', '草图转效果图', '手绘线稿、批注截图或 UI 草稿加一句描述，直接变成可用的效果图。'),
    ('出海', '多语种物料', '同一张海报换成英文、日文、阿拉伯文等版本，版式保持不变。'),
]


# ---------------------------------------------------------------- 总览页
def hub():
    sp, sl, s45, s40, s30 = MODEL_SLUGS
    models = [
        (f'/zh/models/{sp}', '最新旗舰', 'Seedream 5.0 Pro', MODELS[sp]['id'],
         '具备智能思考能力的多模态生图模型，擅长高密度信息图、交互式精准编辑和真实人像质感，原生支持十余种语言。', cny(sp), ' / 张起'),
        (f'/zh/models/{sl}', '高性价比', 'Seedream 5.0 lite', MODELS[sl]['id'],
         '5.0 的轻量版，深度思考加联网检索，最高 4K 输出，支持组图和最多 14 张参考图。', cny(sl), ' / 张起'),
        (f'/zh/models/{s45}', '海报排版', 'Seedream 4.5', MODELS[s45]['id'],
         '保持原图人脸和光影细节，海报与 logo 排版更稳，小字清晰可读，多图融合时角色一致。', cny(s45), ' / 张起'),
        (f'/zh/models/{s40}', '生成编辑一体', 'Seedream 4.0', MODELS[s40]['id'],
         '在一个模型里完成文生图、图片编辑和多图合成，一次最多输出 15 张关联图片，支持 4K。', cny(s40), ' / 张起'),
        (f'/zh/models/{s30}', '旧版', 'Seedream 3.0', MODELS[s30]['id'],
         '中英双语文生图模型，原生 2K，只支持文生图。新项目建议用 4.0 及以上型号。', cny(s30), ' / 次'),
    ]
    choose = G.table('Seedream 型号怎么选', [('需求', False), ('推荐型号', False), ('原因', False)], [(None, [
        f'<th scope="row">信息图、海报、UI 等文字密集画面</th><td><a href="/zh/models/{sp}">Seedream 5.0 Pro</a></td><td>官方主打高密度信息呈现，排版和小字最稳</td>',
        f'<th scope="row">按批注、框选精准改图</th><td><a href="/zh/models/{sp}">Seedream 5.0 Pro</a></td><td>响应框选和涂鸦批注，支持图层拆分和透明背景</td>',
        f'<th scope="row">日常批量出图、控制成本</th><td><a href="/zh/models/{sl}">Seedream 5.0 lite</a></td><td>5.0 代际单价最低（{cny(sl)} / 张），最高 4K</td>',
        f'<th scope="row">一次生成多张关联图（组图）</th><td><a href="/zh/models/{sl}">5.0 lite</a> / <a href="/zh/models/{s45}">4.5</a> / <a href="/zh/models/{s40}">4.0</a></td><td>三个型号都支持一次最多 15 张，5.0 Pro 不支持组图</td>',
        f'<th scope="row">需要实时信息（节日、热点）</th><td><a href="/zh/models/{sl}">Seedream 5.0 lite</a></td><td>唯一支持联网搜索的型号</td>',
    ])])
    faqs = [
        ('Seedream API 多少钱？',
         f'AnyAIGC 上 Seedream 全系固定单价：5.0 Pro {cny(sp)} / 张起，5.0 lite {cny(sl)} / 张起，4.5 {cny(s45)} / 张起，4.0 {cny(s40)} / 张起，3.0 {cny(s30)} / 次。不同分辨率单价不同，实时价格以模型广场为准。'),
        ('Seedream 是什么？和豆包、即梦是什么关系？',
         'Seedream 是字节跳动 Seed 团队的图像生成模型系列，在火山引擎上以「豆包 Seedream」（doubao-seedream）的名字提供 API，即梦等字节产品里的生图能力也基于它。AnyAIGC 提供的是 Seedream 官方模型的 API 调用。'),
        ('5.0 Pro、5.0 lite、4.5、4.0 有什么区别？',
         '5.0 Pro 是旗舰，擅长信息图、精准编辑和多语种，最高 2K，不支持组图。5.0 lite 是轻量版，带联网检索，最高 4K。4.5 强在海报排版和保持原图细节。4.0 是第一个把生成和编辑合在一起的版本。5.0 lite、4.5、4.0 都支持组图和最多 14 张参考图。'),
        ('支持哪些接口？可以改图吗？',
         f'全系走 OpenAI 兼容的 <code>POST /v1/images/generations</code>，换型号只改 <code>model</code>。改图、多图融合时在 <code>image</code> 里传图片 URL 数组；组图用 <code>sequential_image_generation: "auto"</code>。字段说明见 <a href="{DOCS}">AnyAIGC 接口文档</a>。'),
        conc_faq('Seedream 全系'),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(
        name='Seedream', crumb='Seedream', product='Seedream API（AnyAIGC）', sku='seedream', currency='CNY',
        title=f'Seedream API 价格与接入｜5.0 Pro、4.5 全系 {cny(sl)} 起 - AnyAIGC',
        desc=f'Seedream API 全系：豆包 Seedream 5.0 Pro、5.0 lite、4.5、4.0，按张计费 {cny(sl)} 起，支持多图融合、组图与 4K，并发不限，支持对公转账与增值税专票。',
        og_desc=f'一个 Key 调用字节跳动 Seedream 全系：5.0 Pro、5.0 lite、4.5、4.0，按张 {cny(sl)} 起，并发不限。',
        og_alt='AnyAIGC Seedream API：5.0 Pro、5.0 lite、4.5、4.0 全系',
        keywords='Seedream API,Seedream API 价格,Seedream 5.0 API,Seedream 5.0 Pro API,Seedream 4.5 API,豆包 Seedream API,豆包生图 API,doubao-seedream,Seedream API Key,Seedream 组图,即梦 API,Seedream API 企业,Seedream API 发票,AnyAIGC',
        product_desc='通过 AnyAIGC 调用字节跳动 Seedream 全系图像模型：doubao-seedream-5-0-pro、5-0（lite）、4-5、4-0、3-0，OpenAI 兼容 /v1/images/generations。',
        offers=[(f'{MODELS[s]["name"]}（每{MODELS[s]["unit"]}起）', CNY[s]) for s in MODEL_SLUGS],
        eyebrow='字节跳动 · Seedream 系列', h1='Seedream API<small>豆包 Seedream 5.0 Pro、5.0 lite、4.5、4.0 全系</small>',
        lead=f'一个 API Key 调用字节跳动全部 Seedream 型号，<strong>按张 {cny(sl)} 起</strong>。',
        lead_sub='信息图、海报排版、多图融合、组图和 4K 出图都能直接走 API。固定单价，不按 token 算，国内直接调用。',
        facts=[('起步价', f'{cny(sl)} / 张'), ('最高', '4K'), ('参考图', '最多 14 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
        tiles=[('info', 'Seedream 5.0 Pro'), ('seq', 'Seedream 5.0 lite'), ('multi', 'Seedream 4.5'), ('edit', 'Seedream 4.0')],
        models_h2='Seedream 全系型号', models_lead='所有型号接口相同，只需切换 <code>model</code>。点卡片查看每个型号的价格、参数和代码示例。',
        models=models,
        compare_h2='Seedream 5.0 Pro vs 5.0 lite vs 4.5 vs 4.0 参数对比', compare_lead='分辨率、参考图、组图和专有能力放在一张表里。',
        compare_table=compare_table(), compare_note=COMPARE_NOTE,
        price_h2='Seedream API 价格', price_lead='全系固定单价。同一个 API Key、同一份余额调用全部型号。',
        billing=billing(), billing_label='计费要点', price_tables=price_table(MODEL_SLUGS), price_note=price_note(),
        price_extra=f'      <h3 class="sd-h3 o-reveal">型号怎么选</h3>{NL}' + choose,
        costs_h3='成本示例', costs_lead='按上表起步价直接相加，不含其他费用。',
        costs=[('1,000 张商品图', f'Seedream 5.0 lite，1,000 × {cny(sl)}', f'¥{1000 * float(CNY[sl]):.0f}', '日常批量出图'),
               ('100 张信息图海报', f'Seedream 5.0 Pro，100 × {cny(sp)}', f'¥{100 * float(CNY[sp]):.0f}', '文字密集的版式'),
               ('一组 15 张系列插画', f'Seedream 4.0 组图，15 × {cny(s40)}', f'¥{15 * float(CNY[s40]):.2f}', '一次请求返回 15 张')],
        uses_h2='Seedream API 使用场景', uses=USES,
        qs_h2='快速接入 Seedream API', steps=steps(MODELS[sp]['id']), codes=codes(sp),
        callout='换型号只改 <code>model</code>：<code>doubao-seedream-5-0-pro-260628</code>、<code>doubao-seedream-5-0-260128</code>、<code>doubao-seedream-4-5-251128</code> 或 <code>doubao-seedream-4-0-250828</code>，请求和返回格式相同。',
        qs_note=QS_NOTE,
        family_h2='Seedream 系列专题', family_lead='每个型号单独一页，含完整价格、参数和代码示例。',
        faq_h2='Seedream API 常见问题', faqs=faqs,
        final_h2='现在开始调用 Seedream', final_p='注册即送 200 万 tokens 试用额度，一个 Key 调用 Seedream 全系和 300+ 其他模型。',
    )


# ---------------------------------------------------------------- 型号页
def model_page(slug):
    m = MODELS[slug]
    name, mid, unit = m['name'], m['id'], m['unit']
    p = cny(slug)
    base = dict(name=name, crumb=name, sku=mid, currency='CNY', product=f'{name} API（AnyAIGC）',
                offers=[(f'{name}（每{unit}起）', CNY[slug])],
                billing=billing(slug), billing_label='计费要点', price_tables=price_table([slug]), price_note=price_note(slug),
                costs_h3='成本示例', costs_lead='按上表起步价直接相加，不含其他费用。',
                compare_h2=f'{name} 与同系列对比', compare_table=compare_table(slug), compare_note=COMPARE_NOTE,
                uses_h2=f'{name} API 使用场景', uses=USES,
                qs_h2=f'快速接入 {name} API', steps=steps(mid), codes=codes(slug), qs_note=QS_NOTE,
                family_h2='Seedream 系列其他型号', family_lead='接口相同，换 <code>model</code> 即可切换。',
                faq_h2=f'{name} API 常见问题',
                price_h2=f'{name} API 价格', price_lead=f'固定单价，{name} 起步价 {p} / {unit}。',
                final_h2=f'现在开始调用 {name}', final_p=f'注册即送 200 万 tokens 试用额度，{p} / {unit}起，并发不限。',
                h1=f'{name} API<small>{mid}</small>', eyebrow=f'字节跳动 · {name}')

    def price_faq(extra=''):
        return (f'{name} API 多少钱？',
                f'AnyAIGC 上 {name}（<code>{mid}</code>）{p} / {unit}起（${USD[slug]}）。{extra}按成功生成计费，实时价格以模型广场为准。')

    def costs3(n1, n2, n3, l1, l2, l3):
        f = float(CNY[slug])
        return [(l1[0], f'{n1:,} × {p}', f'¥{n1 * f:.0f}' if n1 * f >= 10 else f'¥{n1 * f:.2f}', l1[1]),
                (l2[0], f'{n2:,} × {p}', f'¥{n2 * f:.0f}' if n2 * f >= 10 else f'¥{n2 * f:.2f}', l2[1]),
                (l3[0], f'{n3:,} × {p}', f'¥{n3 * f:.0f}' if n3 * f >= 10 else f'¥{n3 * f:.2f}', l3[1])]

    if slug == 'seedream-5.0-pro':
        faqs = [
            price_faq('不同分辨率单价不同，不传 <code>size</code> 会按更高档位计费，建议显式传 <code>1K</code> 或 <code>2K</code>。'),
            ('Seedream 5.0 Pro 是什么？',
             'Seedream 5.0 Pro 是字节跳动 Seed 团队的旗舰图像生成模型，官方定位是「具备智能思考能力、支持高效创作和生产的多模态图像生成模型」。它主打高密度信息呈现、交互式精准编辑、真实影像与人像质感，以及十余种语言的原生支持。AnyAIGC 于 2026 年 8 月上线该模型。'),
            ('支持哪些分辨率？能出 4K 吗？',
             '不能。按火山方舟文档，5.0 Pro 的 <code>size</code> 支持 <code>1K</code>、<code>1.5K</code>、<code>2K</code>（默认 2K），也可以直接写像素尺寸，例如 <code>2048x2048</code>、<code>2816x1584</code>，宽高比范围 1:16 到 16:1。需要 4K 请用 <a href="/zh/models/seedream-5.0-lite">Seedream 5.0 lite</a> 或 4.5。'),
            ('能上传几张参考图？支持组图吗？',
             '<code>image</code> 最多传 10 张参考图，用于改图和多图融合。5.0 Pro 不支持组图（一次生成多张关联图），需要组图请用 5.0 lite、4.5 或 4.0。'),
            ('5.0 Pro 和 5.0 lite 怎么选？',
             f'信息图、海报、UI 这类文字密集的画面，以及按批注框选精准改图，选 5.0 Pro。日常批量出图、需要 4K、组图或联网检索，选 <a href="/zh/models/seedream-5.0-lite">5.0 lite</a>，单价更低（{cny("seedream-5.0-lite")} / 张起）。'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 5.0 Pro API 价格与接入｜{p}/张起 - AnyAIGC',
            desc=f'Seedream 5.0 Pro API（doubao-seedream-5-0-pro-260628）按张计费 {p} 起，擅长信息图、精准编辑与多语种文字，参考图最多 10 张，并发不限，支持对公转账与增值税专票。',
            og_desc=f'字节跳动 Seedream 5.0 Pro API：{p} / 张起，高密度信息图、框选精准编辑、十余种语言，并发不限。',
            og_alt='AnyAIGC Seedream 5.0 Pro API 价格与接入',
            keywords='Seedream 5.0 Pro API,Seedream 5.0 Pro API 价格,doubao-seedream-5-0-pro-260628,豆包 Seedream 5.0 Pro,Seedream 5.0 Pro 接入,Seedream 5.0 Pro vs lite,Seedream API Key,Seedream API 企业,Seedream API 发票,AnyAIGC',
            product_desc='通过 AnyAIGC 调用字节跳动 Seedream 5.0 Pro（doubao-seedream-5-0-pro-260628）图像生成与编辑模型，按张计费，OpenAI 兼容 /v1/images/generations。',
            lead=f'字节跳动 Seed 旗舰生图模型，<strong>每张 {p} 起</strong>。',
            lead_sub='具备智能思考能力：高密度信息图、按批注框选精准编辑、真实人像质感，原生支持十余种语言的文字生成。',
            facts=[('起步价', f'{p} / 张'), ('最高', '2K'), ('参考图', '最多 10 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
            tiles=[('info', '高密度信息图'), ('edit', '电商首屏 UI'), ('photo', '真实人像质感'), ('lang', '多语种海报')],
            about_h2='Seedream 5.0 Pro 是什么',
            about_ps=['Seedream 5.0 Pro 是字节跳动 Seed 团队发布的旗舰图像生成模型，官方定位为「具备智能思考能力、支持高效创作和生产的多模态图像生成模型」。它能理解复杂指令和视觉内容，在信息图、分镜、UI 这类信息密集的画面上可以直接出可用的效果。',
                      f'在 AnyAIGC 上，模型名是 <code>{mid}</code>，走 OpenAI 兼容的 <code>/v1/images/generations</code>，每张 {p} 起。不需要火山引擎账号和实名认证，国内网络可以直接调用。'],
            spec=[('模型名', f'<code>{mid}</code>'), ('输出分辨率', '1K / 1.5K / 2K（默认 2K）'), ('参考图', '最多 10 张'),
                  ('组图', '不支持'), ('专有能力', '图层拆分 · 透明背景'), ('接口', '/v1/images/generations')],
            features_h2='Seedream 5.0 Pro 能做什么',
            features_lead='下面四项是字节跳动 Seed 官方页面列出的核心能力。',
            features=[('info', '高密度信息呈现', '驾驭复杂信息组织：信息图、技术图纸、游戏界面、分镜和教育海报，排版和小字可以直接出效果。'),
                      ('edit', '交互式精准编辑', '精准响应框选、涂鸦线稿和手写批注，只改标出来的地方，其余保持不变；支持图层拆分。'),
                      ('photo', '真实影像与人像质感', '还原真实的物理光影和人物肌理，生活摄影、人像精修和妆容修改更自然。'),
                      ('lang', '多语种原生支持', '直接用十余种常用语言写提示词并生成画面文字，可以把海报翻译成其他语言并保持版式，阿拉伯语支持从右到左排版。')],
            costs=costs3(100, 500, 1000, ('100 张信息图海报', '文字密集的版式'), ('500 张商品精修图', '按批注改图'), ('1,000 张多语种物料', '出海广告素材')),
            callout='5.0 Pro 不支持组图（<code>sequential_image_generation</code>）；需要一次出多张关联图片，把 <code>model</code> 换成 <code>doubao-seedream-5-0-260128</code>（5.0 lite）即可。',
            faqs=faqs,
        )

    if slug == 'seedream-5.0-lite':
        faqs = [
            price_faq('不同分辨率单价不同，2K、3K、4K 的实时价格以模型广场为准。组图一次返回多张，按实际生成张数计费。'),
            ('Seedream 5.0 lite 是什么？',
             'Seedream 5.0 lite 是 Seedream 5.0 的轻量版，在 AnyAIGC 上的模型名是 doubao-seedream-5-0-260128。官方主打「深度思考 + 实时检索增强」：能更准确理解意图，控制风格和版式，并可以联网获取实时信息。AnyAIGC 于 2026 年 2 月上线该模型。'),
            ('支持哪些分辨率？能出 4K 吗？',
             '能。按火山方舟文档，5.0 lite 的 <code>size</code> 支持 <code>2K</code>、<code>3K</code>、<code>4K</code>，也可以写像素尺寸，宽高比范围 1:16 到 16:1。'),
            ('组图怎么用？最多几张？',
             '传 <code>sequential_image_generation: "auto"</code>，再用 <code>sequential_image_generation_options.max_images</code> 指定上限（1–15）。纯文字最多生成 15 张；带参考图时，参考图张数加生成张数不超过 15。'),
            ('能上传几张参考图？可以联网吗？',
             '<code>image</code> 最多 14 张参考图。5.0 lite 是 Seedream 系列里唯一支持联网搜索的型号，适合画节日、热点等需要实时信息的内容。'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 5.0 lite API 价格与接入｜4K 生图 {p} 起 - AnyAIGC',
            desc=f'Seedream 5.0 lite API（doubao-seedream-5-0-260128）按张计费 {p} 起，最高 4K，支持组图、14 张参考图和联网检索，并发不限，支持对公转账与增值税专票。',
            og_desc=f'字节跳动 Seedream 5.0 lite API：{p} / 张起，最高 4K、组图、联网检索，并发不限。',
            og_alt='AnyAIGC Seedream 5.0 lite API 价格与接入',
            keywords='Seedream 5.0 lite API,Seedream 5.0 API,Seedream 5.0 lite 价格,doubao-seedream-5-0-260128,豆包 Seedream 5.0,Seedream 4K,Seedream 组图,Seedream API Key,Seedream API 企业,Seedream API 发票,AnyAIGC',
            product_desc='通过 AnyAIGC 调用字节跳动 Seedream 5.0 lite（doubao-seedream-5-0-260128）图像生成模型，按张计费，OpenAI 兼容 /v1/images/generations。',
            lead=f'Seedream 5.0 轻量版，<strong>每张 {p} 起</strong>，最高 4K。',
            lead_sub='深度思考加实时检索增强：意图理解更准，风格和版式可控，还能联网画出节日、热点等实时内容。',
            facts=[('起步价', f'{p} / 张'), ('最高', '4K'), ('组图', '最多 15 张'), ('参考图', '最多 14 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
            tiles=[('seq', '16 宫格组图'), ('multi', '复古手账贴纸'), ('photo', '识别并标注热量'), ('type', '结合热点作画')],
            about_h2='Seedream 5.0 lite 是什么',
            about_ps=['Seedream 5.0 lite 是字节跳动 Seed 团队 Seedream 5.0 系列的轻量版。官方主打「深度思考 + 实时检索增强」，在理解复杂意图、控制风格与版式方面更强，也能通过联网搜索拿到实时信息。',
                      f'在 AnyAIGC 上，模型名是 <code>{mid}</code>，每张 {p} 起，是 5.0 代际里单价最低的型号。'],
            spec=[('模型名', f'<code>{mid}</code>'), ('输出分辨率', '2K / 3K / 4K'), ('参考图', '最多 14 张'),
                  ('组图', '最多 15 张'), ('联网搜索', '支持'), ('接口', '/v1/images/generations')],
            features_h2='Seedream 5.0 lite 能做什么',
            features=[('search', '联网检索实时信息', '开启联网搜索后，模型能结合实时信息作画，适合节日海报、热点配图和需要最新事实的画面。'),
                      ('seq', '组图一次生成多张', '一次请求最多 15 张内容关联、风格统一的图片，适合系列插画、分镜和多角度商品图。'),
                      ('multi', '多图融合', '最多 14 张参考图，把商品、人物和场景合进同一张画面。'),
                      ('type', '风格与版式控制', '按提示词精确控制画风、构图和文字排版，最高输出 4K。')],
            costs=costs3(1000, 200, 15, ('1,000 张商品图', '日常批量出图'), ('200 张社媒配图', '多比例出图'), ('一组 15 张系列插画', '一次组图请求')),
            callout='5.0 lite 支持 <code>stream</code> 流式返回组图；联网搜索用 <code>tools: [{"type": "web_search"}]</code> 开启（以 AnyAIGC 接口文档为准）。',
            faqs=faqs,
        )

    if slug == 'seedream-4.5':
        faqs = [
            price_faq('不同分辨率单价不同，2K、4K 的实时价格以模型广场为准。组图按实际生成张数计费。'),
            ('Seedream 4.5 是什么？',
             'Seedream 4.5 是字节跳动 Seed 团队的图像创作模型，AnyAIGC 上的模型名是 doubao-seedream-4-5-251128。它原生支持文字、单图和多图输入，能做主体一致的多图融合、图片编辑和组图。官方强调它能保留原图的人脸、光影和细节，海报和 logo 排版更稳，小字清晰可读。'),
            ('支持哪些分辨率？',
             '按火山方舟文档，4.5 的 <code>size</code> 支持 <code>2K</code> 和 <code>4K</code>，也可以写像素尺寸，宽高比范围 1:16 到 16:1。'),
            ('能上传几张参考图？组图最多几张？',
             '<code>image</code> 最多 14 张参考图。组图用 <code>sequential_image_generation: "auto"</code>，一次最多 15 张；带参考图时，参考图加生成张数不超过 15。'),
            ('4.5 和 5.0 lite 怎么选？',
             f'两者都支持 4K、组图和 14 张参考图。需要联网检索或更强的意图理解选 <a href="/zh/models/seedream-5.0-lite">5.0 lite</a>（{cny("seedream-5.0-lite")} / 张起）；已有 4.5 集成、追求海报排版和原图细节保持可以继续用 4.5。'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 4.5 API 价格与接入｜海报排版 {p} 起 - AnyAIGC',
            desc=f'Seedream 4.5 API（doubao-seedream-4-5-251128）按张计费 {p} 起，擅长海报排版与多图融合，支持 4K、组图和 14 张参考图，并发不限，支持对公转账与增值税专票。',
            og_desc=f'字节跳动 Seedream 4.5 API：{p} / 张起，海报排版、多图融合、4K 与组图，并发不限。',
            og_alt='AnyAIGC Seedream 4.5 API 价格与接入',
            keywords='Seedream 4.5 API,Seedream 4.5 API 价格,doubao-seedream-4-5-251128,豆包 Seedream 4.5,Seedream 4.5 接入,Seedream 多图融合,Seedream 组图,Seedream API Key,Seedream API 企业,Seedream API 发票,AnyAIGC',
            product_desc='通过 AnyAIGC 调用字节跳动 Seedream 4.5（doubao-seedream-4-5-251128）图像生成与编辑模型，按张计费，OpenAI 兼容 /v1/images/generations。',
            lead=f'海报排版与多图融合，<strong>每张 {p} 起</strong>。',
            lead_sub='保持原图人脸、光影和细节，海报与 logo 排版更稳、小字清晰；多图输入时角色保持一致，支持 4K 和组图。',
            facts=[('起步价', f'{p} / 张'), ('最高', '4K'), ('组图', '最多 15 张'), ('参考图', '最多 14 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
            tiles=[('type', '图中文字翻译'), ('photo', '邀请函排版'), ('multi', '绘本封面'), ('seq', '参考创意出图')],
            about_h2='Seedream 4.5 是什么',
            about_ps=['Seedream 4.5 是字节跳动 Seed 团队的图像创作模型，原生支持文字、单图和多图输入，在一个模型里完成主体一致的多图融合、图片编辑和组图生成。',
                      f'官方强调三点：改图时保留原图的人脸、光影和细节；海报、logo 排版更稳，小字清晰可读；多图融合时能锁定主体，保持角色连续。在 AnyAIGC 上，模型名是 <code>{mid}</code>，每张 {p} 起。'],
            spec=[('模型名', f'<code>{mid}</code>'), ('输出分辨率', '2K / 4K'), ('参考图', '最多 14 张'),
                  ('组图', '最多 15 张'), ('输入', '文字 · 单图 · 多图'), ('接口', '/v1/images/generations')],
            features_h2='Seedream 4.5 能做什么',
            features=[('type', '海报排版与小字', '标题、卖点和说明小字都能清楚排进画面，适合活动海报、包装和 logo 设计。'),
                      ('photo', '改图保留原图细节', '换背景、换风格时，人脸、光影和细节保持不变，不会把整张图重画一遍。'),
                      ('multi', '多图融合角色一致', '最多 14 张参考图，模型会在多张输入里识别并锁定主体，角色在不同画面里保持一致。'),
                      ('seq', '组图', '一次请求最多 15 张关联图片，适合系列海报、绘本和多角度商品图。')],
            costs=costs3(500, 1000, 15, ('500 张活动海报', '标题与小字直出'), ('1,000 张商品场景图', '多图融合'), ('一组 15 张系列图', '一次组图请求')),
            callout='新项目可以直接试 <code>doubao-seedream-5-0-260128</code>（5.0 lite），单价更低，参数基本相同，迁移只改 <code>model</code>。',
            faqs=faqs,
        )

    if slug == 'seedream-4.0':
        faqs = [
            price_faq('不同分辨率单价不同，2K、4K 的实时价格以模型广场为准。组图按实际生成张数计费。'),
            ('Seedream 4.0 是什么？',
             'Seedream 4.0 是字节跳动 Seed 团队的多模态图像生成模型，AnyAIGC 上的模型名是 doubao-seedream-4-0-250828。它在统一框架里整合了文生图、图片编辑和多图合成，能根据提示词自动选择合适的宽高比和生成张数，一次最多输出 15 张主题关联的图片，支持 4K。'),
            ('支持哪些分辨率？',
             '按火山方舟文档，4.0 的 <code>size</code> 支持 <code>1K</code>、<code>2K</code>、<code>4K</code>，也可以写像素尺寸，宽高比范围 1:16 到 16:1。'),
            ('能上传几张参考图？组图最多几张？',
             '<code>image</code> 最多 14 张参考图（按火山方舟当前文档）。组图一次最多 15 张；带参考图时，参考图加生成张数不超过 15。'),
            ('还推荐用 4.0 吗？',
             f'4.0 可以继续调用，单价比 4.5 低（{p} / 张起），支持 1K 档位。新项目建议优先试 <a href="/zh/models/seedream-5.0-lite">5.0 lite</a> 或 <a href="/zh/models/seedream-4.5">4.5</a>，接口相同，迁移只改模型名。'),
            conc_faq(name),
            *COMMON_FAQ,
            LICENSE_FAQ,
        ]
        return dict(base,
            title=f'Seedream 4.0 API 价格与接入｜生成编辑一体 {p} 起 - AnyAIGC',
            desc=f'Seedream 4.0 API（doubao-seedream-4-0-250828）按张计费 {p} 起，文生图、编辑与多图合成一体，组图最多 15 张，支持 4K，并发不限，支持对公转账与增值税专票。',
            og_desc=f'字节跳动 Seedream 4.0 API：{p} / 张起，生成编辑一体、组图最多 15 张、4K，并发不限。',
            og_alt='AnyAIGC Seedream 4.0 API 价格与接入',
            keywords='Seedream 4.0 API,Seedream 4.0 API 价格,doubao-seedream-4-0-250828,豆包 Seedream 4.0,Seedream 4.0 接入,Seedream 图片编辑 API,Seedream 组图,Seedream API Key,Seedream API 企业,Seedream API 发票,AnyAIGC',
            product_desc='通过 AnyAIGC 调用字节跳动 Seedream 4.0（doubao-seedream-4-0-250828）图像生成与编辑模型，按张计费，OpenAI 兼容 /v1/images/generations。',
            lead=f'文生图、编辑、多图合成一体，<strong>每张 {p} 起</strong>。',
            lead_sub='根据提示词自动选择宽高比和张数，一次最多输出 15 张关联图片；中文文字生成更准，支持 4K。',
            facts=[('起步价', f'{p} / 张'), ('最高', '4K'), ('组图', '最多 15 张'), ('参考图', '最多 14 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
            tiles=[('multi', '多图组合'), ('edit', '改海报文字'), ('seq', '一图多风格'), ('info', '解题步骤')],
            about_h2='Seedream 4.0 是什么',
            about_ps=['Seedream 4.0 是字节跳动 Seed 团队的多模态图像生成模型，在一个统一框架里整合了文生图、图片编辑和多图合成。它会对提示词做推理，自动选择合适的宽高比和生成张数，一次最多输出 15 张主题关联的图片。',
                      f'官方还提到它的中文文字生成准确率和内容多样性都有明显提升，支持 4K 超清输出。在 AnyAIGC 上，模型名是 <code>{mid}</code>，每张 {p} 起。'],
            spec=[('模型名', f'<code>{mid}</code>'), ('输出分辨率', '1K / 2K / 4K'), ('参考图', '最多 14 张'),
                  ('组图', '最多 15 张'), ('能力', '生成 · 编辑 · 合成'), ('接口', '/v1/images/generations')],
            features_h2='Seedream 4.0 能做什么',
            features=[('seq', '组图', '一次请求最多 15 张主题关联的图片，模型会自动决定张数和比例。'),
                      ('edit', '指令编辑', '用一句话改图：加减元素、换风格、换背景，不需要画蒙版。'),
                      ('multi', '多图合成', '把多张参考图里的人物、商品和场景合成到同一张画面。'),
                      ('info', '知识类插画', '能画公式、科普图解等需要知识的画面，中文文字生成更准确。')],
            costs=costs3(1000, 300, 15, ('1,000 张商品图', '1K 起步，批量出图'), ('300 张改图', '指令编辑'), ('一组 15 张关联图', '一次组图请求')),
            callout='4.0 是三个支持组图的型号里唯一有 <code>1K</code> 档位的，适合对分辨率要求不高的批量任务。',
            faqs=faqs,
        )

    # Seedream 3.0（旧版）
    faqs = [
        price_faq('3.0 在模型广场按次计费，一次请求返回 1 张图。'),
        ('Seedream 3.0 停用了吗？',
         '没有，AnyAIGC 上 <code>doubao-seedream-3-0-t2i-250415</code> 目前可以正常调用。不过火山方舟当前的图片生成文档已经不再列出 3.0，后续可能下线。新项目建议直接用 <a href="/zh/models/seedream-4.0">Seedream 4.0</a> 或 <a href="/zh/models/seedream-5.0-lite">5.0 lite</a>，接口相同，迁移只改模型名。'),
        ('Seedream 3.0 是什么？',
         'Seedream 3.0 是字节跳动 Seed 团队 2025 年 4 月发布的中英双语文生图基础模型，原生支持 2K 高分辨率，小字生成和文字排版更准确，指令遵循和画面美感都比上一代有提升。'),
        ('3.0 能改图或上传参考图吗？',
         '不能。3.0（t2i）只支持文生图，不支持参考图、改图和组图。需要改图请用 4.0 及以上型号。'),
        ('size 怎么填？',
         '3.0 的 <code>size</code> 写像素尺寸，例如 <code>1024x1024</code>、<code>1280x720</code>、<code>720x1280</code>。'),
        conc_faq(name),
        *COMMON_FAQ,
        LICENSE_FAQ,
    ]
    return dict(base,
        title=f'Seedream 3.0 API 价格与接入｜文生图 {p}/次 - AnyAIGC',
        desc=f'Seedream 3.0 API（doubao-seedream-3-0-t2i-250415）按次计费 {p}，中英双语文生图、原生 2K，并发不限，支持对公转账与增值税专票。新项目建议使用 4.0 及以上。',
        og_desc=f'字节跳动 Seedream 3.0 文生图 API：{p} / 次，中英双语、原生 2K，并发不限。',
        og_alt='AnyAIGC Seedream 3.0 API 价格与接入',
        keywords='Seedream 3.0 API,Seedream 3.0 API 价格,doubao-seedream-3-0-t2i-250415,豆包 Seedream 3.0,Seedream 文生图 API,Seedream API Key,Seedream API 企业,Seedream API 发票,AnyAIGC',
        product_desc='通过 AnyAIGC 调用字节跳动 Seedream 3.0（doubao-seedream-3-0-t2i-250415）文生图模型，按次计费，OpenAI 兼容 /v1/images/generations。',
        lead=f'中英双语文生图，<strong>每次 {p}</strong>。',
        lead_sub='原生 2K 高分辨率，小字生成和文字排版更准确。只支持文生图，适合已有 3.0 集成的项目继续使用。',
        notice='火山方舟当前文档已不再列出 Seedream 3.0。新项目建议改用 <a href="/zh/models/seedream-4.0">Seedream 4.0</a> 或 <a href="/zh/models/seedream-5.0-lite">5.0 lite</a>，迁移只需改模型名。',
        facts=[('单价', f'{p} / 次'), ('分辨率', '原生 2K'), ('能力', '文生图'), ('并发', '不限'), ('企业', '对公 · 专票')],
        tiles=[('type', '中英双语文字'), ('photo', '原生 2K'), ('info', '小字排版'), ('lang', '指令遵循')],
        price_lead=f'按次计费，每次 {p}，一次返回 1 张图。',
        billing=[('按次计费', '固定单价，不按 token 算'), ('每次 1 张', '一次请求返回 1 张图片'), ('并发不限', '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')],
        about_h2='Seedream 3.0 是什么',
        about_ps=['Seedream 3.0 是字节跳动 Seed 团队 2025 年 4 月发布的中英双语图像生成基础模型，原生支持 2K 高分辨率输出，在小字生成、文字排版、指令遵循和画面美感上都比上一代有明显提升。',
                  f'在 AnyAIGC 上，模型名是 <code>{mid}</code>，按次计费，每次 {p}。它只支持文生图，不支持参考图、改图和组图。'],
        spec=[('模型名', f'<code>{mid}</code>'), ('分辨率', '原生 2K'), ('size', '像素尺寸，如 1024x1024'),
              ('参考图', '不支持'), ('语言', '中文 · 英文'), ('接口', '/v1/images/generations')],
        features_h2='Seedream 3.0 能做什么',
        features=[('type', '中英双语文字', '中文、英文提示词都能直接用，画面里的文字生成更准确。'),
                  ('photo', '原生 2K', '直接输出 2K 高分辨率图片，细节更清楚。'),
                  ('info', '小字与排版', '相比上一代，小字和文字排版更准确。'),
                  ('lang', '指令遵循', '对提示词的理解和执行更稳，画面结构和美感更好。')],
        costs=costs3(1000, 500, 100, ('1,000 张配图', '纯文生图'), ('500 张封面', '中英文标题'), ('100 张测试图', '对比效果')),
        callout='迁移到新型号只需把 <code>model</code> 换成 <code>doubao-seedream-4-0-250828</code> 等，<code>size</code> 可以改用 <code>2K</code> 这类档位写法。',
        faqs=faqs,
    )


def build(slug):
    return hub() if slug == 'seedream' else model_page(slug)
