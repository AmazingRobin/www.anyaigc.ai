# GPT Image 2.6（Sunburst / Flare）专题页中英文文案。build(lang, slug) 返回页面用的字典，被 gpt_image_copy_zh/en.py 调用。
# 事实来源：OpenAI《Introducing Images 2.6》发布页、developers.openai.com 模型页与 image-generation 指南（2026-11-05 读取）。
# 用户 2026-11-05 确认：AnyAIGC 接口支持 complexity、GIF、SVG、markup；不与官方价对比；-c 版中文页 1K/2K/4K 统一 ¥0.13。
from gpt_image_data import (TOKEN, CALL, TOKENS_26, PRICING, SUPPORT, DOCS_GEN_25, DOCS_EDIT_25, POST_26, cny, money, cost_26)
import gpt_image_layout as G

T = TOKEN['2.6']

SIZE_RULES = {'zh': '最长边不超过 3840px，宽高都是 16 的倍数，长短边比例不超过 3:1，总像素在 655,360 到 8,294,400 之间',
              'en': ('the longest edge is at most 3840px, both sides are multiples of 16, the aspect ratio is no wider than 3:1, '
                     'and the total pixel count is between 655,360 and 8,294,400')}

CREDIT = {'zh': '示例图和动画来自 OpenAI《Introducing Images 2.6》发布页，由 GPT Image 2.6 生成（部分为 OpenArt、fal、Higgsfield、Picsart、Sable、Town 等早期客户的作品），版权归原作者所有。动画为便于网页播放转成了视频格式。',
          'en': 'Sample images and animations come from OpenAI\'s "Introducing Images 2.6" post and were made with GPT Image 2.6, some by early customers such as OpenArt, fal, Higgsfield, Picsart, Sable and Town. © their owners. Animations are converted to video for web playback.'}


def gif(lang, slug):
    """GIF 动图版块的文案：两个型号都支持"""
    if lang == 'zh':
        return dict(
            h2='GPT Image 2.6 能直接出 GIF 动图',
            lead='这是 2.6 最大的新能力：一句提示词描述主体、动作和循环方式，返回一张完整的 GIF。可以做品牌吉祥物动画、社媒表情、产品循环展示，也能把手绘草图变成会动的角色。',
            tiles=[('i26-chibi-down', '股价下跌时哭出来的 Q 版上班族（OpenArt）'), ('i26-owl-sketch', '一张画在横线纸上的手绘草图'), ('i26-owl', '由这张草图生成的猫头鹰 GIF')],
            params=[('format', 'gif'), ('frame_count', '2–64 帧，默认 9'), ('frame_duration_ms', '每帧 20–2000 毫秒，默认 200'), ('size', '每一帧的尺寸，默认 auto')],
            params_label='GIF 请求参数')
    return dict(
        h2='GPT Image 2.6 makes animated GIFs',
        lead='This is the headline feature of 2.6. Describe the subject, the motion and how it loops in one prompt, and you get a finished GIF back. Animate a brand mascot, make reactions for social media, loop a product shot, or turn a hand-drawn sketch into a moving character.',
        tiles=[('i26-chibi-down', 'A chibi office worker crying at a falling chart (OpenArt)'), ('i26-owl-sketch', 'A pen sketch on lined paper'), ('i26-owl', 'The owl GIF made from that sketch')],
        params=[('format', 'gif'), ('frame_count', '2–64 frames, default 9'), ('frame_duration_ms', '20–2000 ms per frame, default 200'), ('size', 'Size of each frame, default auto')],
        params_label='GIF request fields')


# ---------------------------------------------------------------- 代码示例
def code_gen(lang, model, quality, complexity):
    z = lang == 'zh'
    prompt = '电商主图：白色背景上的玻璃香水瓶，瓶身标签写着 AURORA，柔和影棚光' if z else 'E-commerce hero shot: a glass perfume bottle on white, the label reads AURORA, soft studio light'
    note = '# complexity 控制出图前的规划程度：low 适合快速改动，high（默认）适合元素多、排版复杂的画面' if z else '# complexity sets how much the model plans: low for quick edits, high (default) for dense layouts'
    save = ('# 下载图片到本地', '已保存 output.webp') if z else ('# Download the image', 'Saved output.webp')
    py = f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{prompt}",
        "size": "1536x1024",
        "quality": "{quality}",
        {note}
        "complexity": "{complexity}",
        "format": "webp",
        "response_format": "url",
        "n": 1,
    }},
    timeout=300,
)
resp.raise_for_status()
image_url = resp.json()["data"][0]["url"]

{save[0]}
with open("output.webp", "wb") as f:
    f.write(requests.get(image_url, timeout=120).content)
print("{save[1]}")'''
    curl = f'''curl https://anyaigc.ai/v1/images/generations \\
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model}",
    "prompt": "{prompt}",
    "size": "1536x1024",
    "quality": "{quality}",
    "complexity": "{complexity}",
    "format": "webp",
    "response_format": "url",
    "n": 1
  }}\''''
    return py, curl


def code_gif(lang, model):
    z = lang == 'zh'
    prompt = ('无缝循环动画：一只圆滚滚的橘猫吉祥物挥手打招呼，然后眨眼微笑，最后一帧自然衔接第一帧，纯色背景，不要文字'
              if z else 'Seamless loop: a round orange cat mascot waves hello, blinks and smiles, the last frame flows back into the first, plain background, no text')
    c = (('# GIF 只能用 generations 接口生成', '# 帧数 2–64，默认 9', '# 每帧时长 20–2000 毫秒，默认 200', '# 每一帧的尺寸，auto 由模型决定', '已保存 loop.gif')
         if z else ('# GIFs are generation-only', '# 2–64 frames, default 9', '# 20–2000 ms per frame, default 200', '# Size of each frame; auto lets the model choose', 'Saved loop.gif'))
    return f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

{c[0]}
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{prompt}",
        "format": "gif",
        "frame_count": 9,  {c[1]}
        "frame_duration_ms": 200,  {c[2]}
        "size": "auto",  {c[3]}
        "quality": "low",
        "response_format": "b64_json",
    }},
    timeout=300,
)
resp.raise_for_status()
with open("loop.gif", "wb") as f:
    f.write(base64.b64decode(resp.json()["data"][0]["b64_json"]))
print("{c[4]}")'''


def code_svg(lang, model):
    z = lang == 'zh'
    prompt = ('面包店 logo：麦穗环绕的圆形徽章，中间写 Field & Flour，扁平矢量风格，两种颜色'
              if z else 'Bakery logo: a round badge circled by wheat stalks, Field & Flour in the center, flat vector style, two colors')
    c = (('# SVG 只能用 generations 接口生成，n 必须为 1', '# quality 控制生成 SVG 前的参考图', '# 返回的是 UTF-8 编码的 SVG 文本，按 .svg 保存', '已保存 logo.svg')
         if z else ('# SVG is generation-only, and n must be 1', '# quality applies to the reference image behind the SVG', '# The result is UTF-8 SVG markup; save it as .svg', 'Saved logo.svg'))
    return f'''import base64
import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

{c[0]}
resp = requests.post(
    "https://anyaigc.ai/v1/images/generations",
    headers={{"Authorization": "Bearer " + API_KEY}},
    json={{
        "model": "{model}",
        "prompt": "{prompt}",
        "format": "svg",
        "n": 1,
        "quality": "medium",  {c[1]}
        "response_format": "b64_json",
    }},
    timeout=300,
)
resp.raise_for_status()
{c[2]}
with open("logo.svg", "wb") as f:
    f.write(base64.b64decode(resp.json()["data"][0]["b64_json"]))
print("{c[3]}")'''


def code_markup(lang, model):
    z = lang == 'zh'
    prompt = ('把红圈里的条纹花瓶改成纯钴蓝色陶瓷，保持形状、干花和厨房其他部分不变，成图里去掉红圈'
              if z else 'Recolor the striped vase inside the red circle to solid cobalt blue ceramic. Keep its shape, the dried stems and the rest of the kitchen unchanged. Remove the red circle.')
    c = (('# markup 是一张透明 PNG 标注层：在要改的地方画圈、画线或写字',
          '# 必须和第一张图同宽同高，不能和 mask 一起用', '# 第一张图是要改的原图', '# 局部小改动用 low complexity 更快')
         if z else ('# markup is a transparent PNG annotation layer: circle, sketch or write on the areas to change',
                    '# It must match the first image in width and height, and cannot be combined with mask', '# The first image is the one being edited', '# low complexity is faster for focused edits'))
    return f'''import os
import requests

API_KEY = os.environ["ANYAIGC_API_KEY"]

{c[0]}
{c[1]}
files = [
    ("image", open("kitchen.png", "rb")),  {c[2]}
    ("markup", open("vase-overlay.png", "rb")),
]

resp = requests.post(
    "https://anyaigc.ai/v1/images/edits",
    headers={{"Authorization": "Bearer " + API_KEY}},
    data={{
        "model": "{model}",
        "prompt": "{prompt}",
        "quality": "medium",
        "complexity": "low",  {c[3]}
    }},
    files=files,
    timeout=300,
)
resp.raise_for_status()
print(resp.json()["data"][0]["url"])'''


# ---------------------------------------------------------------- 价格版块
def price_tables(lang, slug):
    z = lang == 'zh'
    tab = G.table('GPT Image 2.6 按 token 计费单价（美元 / 每 100 万 tokens）' if z else 'GPT Image 2.6 token pricing (USD per 1M tokens)',
                  [('计费项' if z else 'Item', False), ('AnyAIGC 单价' if z else 'AnyAIGC rate', True)],
                  [(None, G.token_rows_plain(lang, '2.6'))])
    per = (f'      <h3 class="gi-h3 o-reveal">{"每张图大概多少钱" if z else "What one image costs"}</h3>\n'
           f'      <p class="o-note">{"按 OpenAI 官方计算器给出的每张图片输出 tokens × AnyAIGC 输出单价估算，不含提示词和参考图的输入 tokens。GPT Image 2.6 的 Sunburst 和 Flare 使用同一套 tokens 数据。" if z else "Estimated from output tokens per image in OpenAI&#39;s official calculator × the AnyAIGC output rate, excluding prompt and reference image input tokens. Sunburst and Flare share the same token figures."}</p>\n'
           + G.per_image_26(lang))
    return tab + per + G.call_block(lang, [slug + '-c'])


def costs(lang):
    z = lang == 'zh'
    out = []
    rows = [('电商主图批量生成' if z else 'E-commerce shots in bulk', 'medium', '1536x1024', 1000),
            ('4K 海报' if z else '4K posters', 'high', '3840x2160', 100),
            ('一张 max 质量方图' if z else 'One max-quality square image', 'max', '1024x1024', 1)]
    for h, q, s, n in rows:
        a = cost_26(q, s)
        tk = TOKENS_26[q][s]
        if z:
            calc = f'{n:,} 张 {s.replace("x", "×")}，<code>quality={q}</code>，每张约 {tk:,} 输出 tokens × ${T["out"]} / 1M'
        else:
            calc = f'{n:,} {"image" if n == 1 else "images"} at {s.replace("x", "×")}, <code>quality={q}</code>, about {tk:,} output tokens each × ${T["out"]} / 1M'
        out.append((h, calc, money(a * n, 2 if n > 1 else 4), ('只算图片输出' if z else 'Image output only')))
    return out


# ---------------------------------------------------------------- 页面
def build(lang, slug):
    z = lang == 'zh'
    sun = slug.endswith('sunburst')
    name = 'GPT Image 2.6 Sunburst' if sun else 'GPT Image 2.6 Flare'
    short = '2.6 Sunburst' if sun else '2.6 Flare'
    other = 'gpt-image-2.6-flare' if sun else 'gpt-image-2.6-sunburst'
    other_name = '2.6 Flare' if sun else '2.6 Sunburst'
    prev = 'gpt-image-2.5-sunburst' if sun else 'gpt-image-2.5-flare'
    c_slug = slug + '-c'
    pc = cny('2.6') if z else '$' + CALL['2.6']
    unit = '张' if z else 'image'
    default_q, default_cx = ('high', 'high') if sun else ('medium', 'medium')
    a_low, a_med = cost_26('low', '1024x1024'), cost_26('medium', '1024x1024')
    rules = SIZE_RULES[lang]
    py, curl = code_gen(lang, slug, default_q, default_cx)
    codes = [('py', 'Python', 'POST /v1/images/generations', py), ('curl', 'cURL', 'POST /v1/images/generations', curl),
             ('gif', 'GIF', 'POST /v1/images/generations · format=gif', code_gif(lang, slug)),
             ('svg', 'SVG', 'POST /v1/images/generations · format=svg', code_svg(lang, slug)),
             ('markup', '标注改图' if z else 'Markup edit', 'POST /v1/images/edits · markup', code_markup(lang, slug))]

    if z:
        if sun:
            eyebrow, h1sub = 'OpenAI · gpt-image-2.6-sunburst', '细节更强、多轮编辑更一致的 GPT Image'
            lead = f'OpenAI 2026 年 11 月发布的 GPT Image 2.6 精细版，<strong>按次计费每张 {pc}</strong>，1K、2K、4K 出图同价。'
            lead_sub = f'官方定位为“细节要求高的视觉作品”。质量设为 medium 或 high 时，多轮编辑中人物、产品和品牌细节更稳定。新增 GIF 动图、SVG 矢量输出、标注改图和 complexity 参数；也可以按 token 计费，图片输出 ${T["out"]} / 百万 tokens。'
            about_h2 = 'GPT Image 2.6 Sunburst：改了几轮，主体还是原来那个'
            about = ['OpenAI 于 2026 年 11 月 4 日发布 Images 2.6，API 里分为 Sunburst 和 Flare 两个型号。官方把 Sunburst 描述为“面向细节视觉作品的图像生成与编辑模型”：质量设为 medium 或 high 时，画面细节更好，跨多轮编辑的一致性也更强，适合角色、产品和品牌元素需要前后一致的工作。',
                     f'这一代新增了 4 个能力：<code>complexity</code> 参数（low、medium、high，控制出图前规划多少）、标注改图 <code>markup</code>、SVG 矢量输出和 GIF 动图输出。质量档位与 2.5 相同，为 low、medium、high、xhigh、max 和 auto；尺寸可以自定义，{rules}。',
                     f'在 AnyAIGC 上，Sunburst 和 <a href="/zh/models/{other}">{other_name}</a> 单价相同。注意 2.6 在 low、medium 质量下每张图的输出 tokens 比 2.5 多不少，高质量档相同；如果更在意每张图的固定成本，可以用按张计费的 <a href="#per-image"><code>{c_slug}</code></a>，每张 {pc}。']
            spec = [('发布', '2026-11-04'), ('官方定位', '细节视觉作品'), ('质量档位', 'low – max'), ('complexity', 'low · medium · high'), ('输出格式', 'png · jpeg · webp · gif · svg'), ('接口', 'generations · edits')]
            hero_imgs = ('i26-knight-1', 'i26-chibi-up', 'i26-glass-whale')
            gallery = ['i26-knight-1', 'i26-knight-2', 'i26-knight-3', 'i26-glass-whale', 'i26-product-world', 'i26-monty', 'i26-markup-before', 'i26-markup-after']
            gallery_lead = '同一位骑士连改三轮：换背景、换盔甲配色，人物和姿势保持不变。下面还有奇幻场景、带文字的产品视觉、产品内角色动画和标注改图前后对比。'
            uses = [('01 · 品牌', '角色与吉祥物的多轮修改', '同一个角色反复换场景、换服装，脸和细节不跑偏，适合系列海报和 IP 物料。', 'i26-knight-2'),
                    ('02 · 电商', '产品图精修与换景', '用标注圈出要改的地方，只动局部，产品外观和标签保持原样。', 'i26-markup-after'),
                    ('03 · 动画', '品牌角色动起来', '把吉祥物或产品角色做成循环 GIF，用在应用内提示、加载动画和营销物料里。', 'i26-monty'),
                    ('04 · 广告', '商业定稿与主视觉', '用 high、xhigh 或 max 质量生成细节丰富的成品图，适合提案和投放素材。', 'i26-glass-whale')]
            diff = ('Sunburst 和 Flare 怎么选？和 GPT Image 2.5 比有什么变化？',
                    f'两者都是 GPT Image 2.6，在 AnyAIGC 上单价相同，参数也一样。官方把 Sunburst 定位为细节视觉作品，质量设为 medium 或 high 时多轮编辑更一致；<a href="/zh/models/{other}">Flare</a> 面向快速迭代，low 质量下最快约 6 秒出图。和 <a href="/zh/models/{prev}">GPT Image 2.5 Sunburst</a> 相比，2.6 新增了 complexity、markup、SVG 和 GIF；low、medium 质量每张输出 tokens 比 2.5 多，high 及以上相同。')
            title = 'GPT Image 2.6 Sunburst API 价格与接入｜多轮编辑更一致 - AnyAIGC'
            pitch = '细节更强、多轮编辑更一致'
        else:
            eyebrow, h1sub = 'OpenAI · gpt-image-2.6-flare', '更快出图、适合快速迭代的 GPT Image'
            lead = f'OpenAI 2026 年 11 月发布的 GPT Image 2.6 快速版，<strong>按次计费每张 {pc}</strong>，1K、2K、4K 出图同价。'
            lead_sub = f'官方介绍 Images 2.6 出图比之前快 50%，Flare 在 low 质量下最快约 6 秒出一张，海报和产品图的版式也更好。支持 GIF 动图、SVG 矢量输出和标注改图；也可以按 token 计费，图片输出 ${T["out"]} / 百万 tokens。'
            about_h2 = 'GPT Image 2.6 Flare：快速出图，也能出动图'
            about = ['OpenAI 于 2026 年 11 月 4 日发布 Images 2.6，API 里分为 Sunburst 和 Flare 两个型号。官方把 Flare 描述为“面向快速迭代的图像生成与编辑模型”：Images 2.6 出图比之前快 50%，Flare 在 low 质量下最快约 6 秒出图，同时提升了海报、产品图等专业视觉的版式质量。',
                     f'Flare 和 Sunburst 用同一套参数：新增 <code>complexity</code>（low、medium、high）、标注改图 <code>markup</code>、SVG 矢量输出和 GIF 动图输出；质量档位为 low、medium、high、xhigh、max 和 auto；尺寸可以自定义，{rules}。',
                     f'在 AnyAIGC 上 Flare 和 <a href="/zh/models/{other}">{other_name}</a> 单价相同。按 token 计费时，low 质量 1024×1024 每张约 {money(a_low)}，medium 约 {money(a_med)}；需要每张固定成本可以用 <a href="#per-image"><code>{c_slug}</code></a>，每张 {pc}。']
            spec = [('发布', '2026-11-04'), ('官方定位', '快速迭代'), ('low 质量出图', '最快约 6 秒'), ('complexity', 'low · medium · high'), ('输出格式', 'png · jpeg · webp · gif · svg'), ('接口', 'generations · edits')]
            hero_imgs = ('i26-chibi-up', 'i26-markup-after', 'i26-glass-whale')
            gallery = ['i26-speed', 'i26-monty', 'i26-product-world', 'i26-knight-1', 'i26-markup-before', 'i26-knight-3']
            gallery_lead = '同一则旅行广告，2.6 Flare 比 2.5 Flare 更快完成（计时为 8 倍速回放）。还有产品内的角色动画、带标题文字的产品视觉、奇幻角色插画和标注改图的原图。'
            uses = [('01 · 社媒', 'GIF 表情与动态贴纸', '一句提示词生成循环动图，做反应表情、梗图和社媒互动素材。', 'i26-chibi-down'),
                    ('02 · 产品功能', '应用内实时出图', 'low 质量最快约 6 秒，适合头像、贺卡、壁纸这类面向用户的功能。', 'i26-speed'),
                    ('03 · 动画', '草图变动画角色', '上传手绘草图，生成会动的角色，做分镜预演和游戏素材。', 'i26-owl'),
                    ('04 · 修图', '标注改图快速修改', '在图上圈出要改的位置，配合 low complexity 快速完成局部修改。', 'i26-markup-before')]
            diff = ('Flare 和 Sunburst 怎么选？和 GPT Image 2.5 比有什么变化？',
                    f'两者都是 GPT Image 2.6，在 AnyAIGC 上单价相同，参数也一样。Flare 面向快速迭代，low 质量下最快约 6 秒出图，适合产品内实时出图、草稿和 GIF；<a href="/zh/models/{other}">Sunburst</a> 面向细节视觉作品，多轮编辑更一致。和 <a href="/zh/models/{prev}">GPT Image 2.5 Flare</a> 相比，2.6 新增了 complexity、markup、SVG 和 GIF；low、medium 质量每张输出 tokens 比 2.5 多，high 及以上相同。')
            title = 'GPT Image 2.6 Flare API 价格与接入｜出图提速 50% - AnyAIGC'
            pitch = '出图更快、支持 GIF 动图'
        caps = [('出图更快', '官方介绍 Images 2.6 出图比之前快 50%，Flare 在 low 质量下最快约 6 秒出一张。'),
                ('多轮编辑更一致', 'Sunburst 在 medium、high 质量下，跨多轮编辑保持人物、产品和品牌细节一致。'),
                ('GIF 动图', '<code>format</code> 设为 gif，用 <code>frame_count</code>（2–64）和 <code>frame_duration_ms</code> 控制帧数和节奏。'),
                ('SVG 矢量输出', '<code>format</code> 设为 svg，返回可编辑路径、形状和颜色的 SVG，适合 logo 和图标。'),
                ('标注改图', '上传一张透明 PNG 标注层 <code>markup</code>，圈出要改的位置，再用提示词说明怎么改。'),
                ('complexity 参数', 'low、medium、high 三档，控制出图前规划多少。快速改图用 low，复杂排版用 high，不额外收费。')]
        faqs = [
            (f'{name} API 多少钱？',
             f'AnyAIGC 上 <code>{slug}</code> 按 token 计费：文本输入 ${T["text_in"]}、图片输入 ${T["img_in"]}、图片输出 ${T["out"]}（每百万 tokens），缓存输入文本 ${T["text_cache"]}、图片 ${T["img_cache"]}。以 1024×1024 为例，low 质量每张图片输出约 {money(a_low)}，medium 约 {money(a_med)}。按张计费版 <code>{c_slug}</code> 每张 {pc}。实时价格以模型广场为准。'),
            diff,
            ('怎么生成 GIF 动图和 SVG？',
             '都走 <code>POST /v1/images/generations</code>。GIF：<code>format</code> 设为 gif，<code>frame_count</code> 取 2–64（默认 9），<code>frame_duration_ms</code> 取 20–2000 毫秒（默认 200），<code>size</code> 是每一帧的尺寸。SVG：<code>format</code> 设为 svg，<code>n</code> 必须为 1，<code>quality</code> 作用于生成 SVG 前的参考图，返回的是静态矢量内容。两者都不支持编辑接口、流式输出和压缩参数。'),
            ('complexity 和标注改图（markup）怎么用？',
             '<code>complexity</code> 取 low、medium 或 high，不传时默认 high，调整它不额外收费。官方建议多数编辑任务用 low 配合需要的质量档，元素多、约束多的画面用 medium 或 high。标注改图走 <code>POST /v1/images/edits</code>：第一张 <code>image</code> 是原图，再传一张透明 PNG 作为 <code>markup</code>，宽高与原图一致，圈出要改的位置并在提示词里写清楚改法；markup 不能和 <code>mask</code> 一起用。'),
            (f'有按张计费的版本吗？{c_slug} 怎么收费？',
             f'有。<code>{c_slug}</code> 是 {name} 的按张计费版，接口相同，只改 <code>model</code> 字段。每张固定 {pc}，1K、2K、4K 出图同价，质量档位不影响单价。每次请求出 1 张，不支持 <code>n</code>、<code>mask</code> 参数，也不支持透明背景。质量开到 medium 及以上或出大图时，按张计费通常更省。'),
            ('并发有限制吗？国内能直接调用吗？',
             f'AnyAIGC 对 {slug} 不设并发限制，所有用户默认享有。接口地址是 <code>https://anyaigc.ai/v1</code>，面向国内网络优化，通常无需额外代理；按美元计费，支持微信支付和支付宝，同一个 Key 还能调用平台上 300+ 其他模型。'),
            ('AnyAIGC 能开发票吗？支持增值税专票吗？',
             '能。AnyAIGC 可以按实际充值金额开具增值税普通发票和增值税专用发票，开票信息提交给客服即可。'),
            ('企业可以对公转账和签合同吗？',
             f'可以。支持企业对公转账充值，也可以签订服务合同，并提供专属客服和技术对接。企业采购请<a href="{SUPPORT}">联系 AnyAIGC 客服</a>。'),
            ('生成的图片可以商用吗？',
             '图片的使用权和内容政策以 OpenAI 官方条款为准。AnyAIGC 只提供 API 调用通道，不额外限制你对生成结果的使用；涉及人物肖像、品牌商标等内容时，请自行确认授权。'),
        ]
        return dict(
            title=title,
            desc=f'{name} API：{pitch}，支持 GIF、SVG 和标注改图，图片输出 ${T["out"]}/1M，按张 {pc} 起，并发不限，支持对公转账与增值税专票。',
            og_desc=f'{slug} 图片输出 ${T["out"]} / 1M tokens，按张版每张 {pc}。新增 complexity、标注改图、SVG 和 GIF，兼容 /v1/images/generations 与 /v1/images/edits。',
            og_alt=f'AnyAIGC {name} API：{pitch}',
            keywords=f'{name} API,{slug},{slug} API,GPT Image 2.6 API,{name} 价格,GPT Image 2.6 价格,GPT Image 2.6 GIF,GPT Image 2.6 SVG,OpenAI 图像生成 API,{name} API 企业,{name} API 发票,GPT Image API 对公转账,AnyAIGC',
            crumb=f'{short} API', product=f'{name} API（AnyAIGC）', sku=slug,
            product_desc=f'通过 AnyAIGC 调用 OpenAI {name}（{slug}）：兼容 /v1/images/generations 与 /v1/images/edits，支持 complexity、markup、SVG 与 GIF 输出，按 token 计费，并发不限。',
            offers=[('文本输入（每 100 万 tokens）', T['text_in']), ('图片输入（每 100 万 tokens）', T['img_in']), ('图片输出（每 100 万 tokens）', T['out']),
                    ('文本缓存输入（每 100 万 tokens）', T['text_cache']), ('图片缓存输入（每 100 万 tokens）', T['img_cache'])],
            eyebrow=eyebrow, h1=f'{name}<span class="o-sr"> API</span><small>{h1sub}</small>', lead=lead, lead_sub=lead_sub, notice=None,
            facts=[('模型 ID', slug), ('图片输出', f'${T["out"]} / 1M'), ('按张', f'{pc} / 张'), ('并发', '不限'), ('企业', '对公 · 专票')],
            hero_imgs=hero_imgs, credit=CREDIT['zh'], credit_url=POST_26, gif=gif('zh', slug),
            about_h2=about_h2, about_ps=about, spec=spec,
            caps_h2=f'{short} 新增了什么', caps=caps, caps_lead='这些能力 Sunburst 和 Flare 都支持，接口字段相同。',
            gallery=gallery, gallery_h2=f'{short} 能做出什么', gallery_lead=gallery_lead,
            price_h2=f'{name} API 价格', price_lead='按 token 计费，固定单价，没有订阅和月费。Sunburst 和 Flare 单价相同；也可以选每张固定价的 -c 版。',
            billing_label='计费要点',
            billing=[('按 token 计费', '提示词、参考图和生成的图片分别计价'), ('complexity 不加价', '三档同一单价'), ('并发不限', '所有用户默认享有'), ('余额通用', '同一余额可调用 300+ 模型')],
            price_tables=price_tables('zh', slug),
            price_note=f'按 token 价格单位为 USD，按张计费（-c 版）单位为人民币，均按成功请求计费。表中为模型广场最低价；SVG 输出除参考图的图片 tokens 外，还会计入生成 SVG 所用的 tokens。缓存价格仅在上游明确返回缓存用量时生效。实时价格以<a href="{PRICING}">模型广场</a>为准。',
            costs_h3='成本示例', costs_lead='按上表单价计算，只算图片输出 tokens，不含提示词文本。', costs=costs('zh'),
            uses_h2=f'{short} 适合做什么', uses=uses,
            steps=[f'<a href="{G.REG}">注册 AnyAIGC</a>，新用户送 200 万 tokens 试用额度，最低 $1 起充。',
                   '在<a href="https://anyaigc.ai/console">控制台</a>创建 API Key，保存到环境变量 <code>ANYAIGC_API_KEY</code>。',
                   f'向 <code>https://anyaigc.ai/v1/images/generations</code> 发请求，<code>model</code> 填 <code>{slug}</code>；改图和标注改图用 <code>/v1/images/edits</code>。'],
            codes=codes, qs_h2=f'三步接入 {name} API',
            callout=f'想按张固定价？把 <code>model</code> 换成 <code>{c_slug}</code>（每张 {pc}，1K/2K/4K 同价），去掉 <code>n</code> 和 <code>mask</code> 即可。',
            qs_note=f'普通图片返回 <code>data[0].url</code>，传 <code>response_format=b64_json</code> 可以拿 base64；GIF 和 SVG 示例用 base64 直接保存文件。提示词最长 1000 字符。其他字段与 GPT Image 2.5 相同，见 <a href="{DOCS_GEN_25}" target="_blank" rel="noopener">生成接口文档</a> 与 <a href="{DOCS_EDIT_25}" target="_blank" rel="noopener">编辑接口文档</a>。',
            family_h2='GPT Image 全部型号', family_lead='同一个 API Key，换型号只改 model 字段。',
            faq_h2=f'{name} API 常见问题', faqs=faqs,
            final_h2=f'现在开始调用 {name}', final_p='注册即送 200 万 tokens 试用额度，先出几张图、做一个 GIF 看看效果。',
            name=name, docs=DOCS_GEN_25,
        )

    # ---------------- English
    if sun:
        eyebrow, h1sub = 'OpenAI · gpt-image-2.6-sunburst', 'More detail and steadier multi-round edits'
        lead = f'The detail-focused GPT Image 2.6 model from OpenAI, released November 2026. <strong>{pc} per image</strong>, the same at 1K, 2K or 4K.'
        lead_sub = f'OpenAI built it for detailed visual work. At medium or high quality, characters, products and brand details hold steady across editing rounds. It adds GIF and SVG output, markup-guided edits and a complexity setting. Token billing is also available at ${T["out"]} per 1M image output tokens.'
        about_h2 = 'GPT Image 2.6 Sunburst: the subject stays the same, round after round'
        about = ['OpenAI released Images 2.6 on November 4, 2026, with two API models, Sunburst and Flare. OpenAI describes Sunburst as image generation and editing for detailed visual work. At medium or high quality it delivers finer detail and stronger consistency across edits, which suits characters, products and brand elements that must match from one version to the next.',
                 f'This generation adds four capabilities: a <code>complexity</code> setting (low, medium or high) that controls how much the model plans, markup-guided edits with <code>markup</code>, SVG output and animated GIF output. Quality levels match GPT Image 2.5: low, medium, high, xhigh, max and auto. Custom sizes work as long as {rules}.',
                 f'On AnyAIGC, Sunburst and <a href="/en/models/{other}">{other_name}</a> cost the same. At low and medium quality, 2.6 uses noticeably more output tokens per image than 2.5; from high up the counts match. For a fixed cost per image, use <a href="#per-image"><code>{c_slug}</code></a> at {pc} per image.']
        spec = [('Released', '2026-11-04'), ('Built for', 'Detailed visual work'), ('Quality', 'low – max'), ('complexity', 'low · medium · high'), ('Formats', 'png · jpeg · webp · gif · svg'), ('Endpoints', 'generations · edits')]
        hero_imgs = ('i26-knight-1', 'i26-chibi-up', 'i26-glass-whale')
        gallery = ['i26-knight-1', 'i26-knight-2', 'i26-knight-3', 'i26-glass-whale', 'i26-product-world', 'i26-monty', 'i26-markup-before', 'i26-markup-after']
        gallery_lead = 'The same knight across three edits: a new background, then new armor colors, with the face and pose unchanged. Below are a fantasy scene, a product visual with a headline, an in-product character animation and a markup edit before and after.'
        uses = [('01 · Brand', 'Characters and mascots across many edits', 'Change scenes and outfits again and again without the face or details drifting, for poster series and IP assets.', 'i26-knight-2'),
                ('02 · E-commerce', 'Product retouching and new scenes', 'Circle what to change with markup and edit only that area, keeping the product and its label intact.', 'i26-markup-after'),
                ('03 · Animation', 'Bring brand characters to life', 'Turn a mascot or product character into a looping GIF for in-app hints, loaders and campaigns.', 'i26-monty'),
                ('04 · Advertising', 'Final commercial visuals', 'Use high, xhigh or max quality for detailed finished images for pitches and campaigns.', 'i26-glass-whale')]
        diff = ('Sunburst or Flare? And what changed from GPT Image 2.5?',
                f'Both are GPT Image 2.6, with the same rates on AnyAIGC and the same parameters. OpenAI positions Sunburst for detailed visual work, with steadier edits at medium or high quality. <a href="/en/models/{other}">Flare</a> is built for fast iteration and can return a low-quality image in as little as six seconds. Compared with <a href="/en/models/{prev}">GPT Image 2.5 Sunburst</a>, 2.6 adds complexity, markup, SVG and GIF. At low and medium quality it uses more output tokens per image than 2.5; from high up the counts are the same.')
        title = 'GPT Image 2.6 Sunburst API pricing | Consistent edits - AnyAIGC'
        pitch = 'more detail and steadier multi-round edits'
        dpitch = 'steadier edits, GIF and SVG'
    else:
        eyebrow, h1sub = 'OpenAI · gpt-image-2.6-flare', 'Faster images, built for quick iteration'
        lead = f'The fast GPT Image 2.6 model from OpenAI, released November 2026. <strong>{pc} per image</strong>, the same at 1K, 2K or 4K.'
        lead_sub = f'OpenAI says Images 2.6 generates images 50% faster than before, and Flare can return a low-quality image in as little as six seconds, with better layouts for posters and product shots. It supports GIF and SVG output and markup-guided edits. Token billing is also available at ${T["out"]} per 1M image output tokens.'
        about_h2 = 'GPT Image 2.6 Flare: fast images, and animated ones too'
        about = ['OpenAI released Images 2.6 on November 4, 2026, with two API models, Sunburst and Flare. OpenAI describes Flare as image generation and editing for fast iteration. Images 2.6 generates images 50% faster than before, Flare can finish a low-quality image in as little as six seconds, and layout quality improves for posters, product imagery and other professional visuals.',
                 f'Flare uses the same parameters as Sunburst. It adds <code>complexity</code> (low, medium or high), markup-guided edits with <code>markup</code>, SVG output and animated GIF output. Quality levels are low, medium, high, xhigh, max and auto. Custom sizes work as long as {rules}.',
                 f'On AnyAIGC, Flare and <a href="/en/models/{other}">{other_name}</a> cost the same. With token billing, a 1024×1024 image costs about {money(a_low)} at low quality and {money(a_med)} at medium. For a fixed cost per image, use <a href="#per-image"><code>{c_slug}</code></a> at {pc} per image.']
        spec = [('Released', '2026-11-04'), ('Built for', 'Fast iteration'), ('Low quality', 'As fast as ~6 s'), ('complexity', 'low · medium · high'), ('Formats', 'png · jpeg · webp · gif · svg'), ('Endpoints', 'generations · edits')]
        hero_imgs = ('i26-chibi-up', 'i26-markup-after', 'i26-glass-whale')
        gallery = ['i26-speed', 'i26-monty', 'i26-product-world', 'i26-knight-1', 'i26-markup-before', 'i26-knight-3']
        gallery_lead = 'The same travel ad finishes sooner on 2.6 Flare than on 2.5 Flare (timers at 8x playback). Also shown: an in-product character animation, a product visual with a headline, fantasy character art and a markup input.'
        uses = [('01 · Social', 'GIF reactions and stickers', 'Turn one prompt into a looping GIF for reactions, memes and social posts.', 'i26-chibi-down'),
                ('02 · Product features', 'Real-time generation in your app', 'Low quality returns in as little as six seconds, which suits avatars, cards and wallpapers for end users.', 'i26-speed'),
                ('03 · Animation', 'Sketches to animated characters', 'Upload a hand-drawn sketch and get a moving character for storyboards and game assets.', 'i26-owl'),
                ('04 · Retouching', 'Quick markup edits', 'Circle the spot to change and pair it with low complexity for fast, focused edits.', 'i26-markup-before')]
        diff = ('Flare or Sunburst? And what changed from GPT Image 2.5?',
                f'Both are GPT Image 2.6, with the same rates on AnyAIGC and the same parameters. Flare is built for fast iteration and can return a low-quality image in as little as six seconds, which suits in-app generation, drafts and GIFs. <a href="/en/models/{other}">Sunburst</a> is built for detailed visual work, with steadier multi-round edits. Compared with <a href="/en/models/{prev}">GPT Image 2.5 Flare</a>, 2.6 adds complexity, markup, SVG and GIF. At low and medium quality it uses more output tokens per image than 2.5; from high up the counts are the same.')
        title = 'GPT Image 2.6 Flare API pricing | 50% faster images - AnyAIGC'
        pitch = 'faster images and animated GIFs'
        dpitch = '50% faster, with GIF and SVG output'
    caps = [('Faster generation', 'OpenAI says Images 2.6 is 50% faster than before, and Flare can return a low-quality image in as little as six seconds.'),
            ('Steadier edits', 'At medium and high quality, Sunburst keeps characters, products and brand details consistent across editing rounds.'),
            ('Animated GIFs', 'Set <code>format</code> to gif and control the animation with <code>frame_count</code> (2–64) and <code>frame_duration_ms</code>.'),
            ('SVG output', 'Set <code>format</code> to svg to get editable paths, shapes and colors, ideal for logos and icons.'),
            ('Markup-guided edits', 'Send a transparent PNG annotation layer as <code>markup</code> to mark what to change, then describe the change in the prompt.'),
            ('complexity setting', 'Low, medium or high controls how much the model plans. Use low for quick edits and high for dense layouts, at no extra cost.')]
    faqs = [
        (f'How much does the {name} API cost?',
         f'On AnyAIGC, <code>{slug}</code> is billed per token: ${T["text_in"]} for text input, ${T["img_in"]} for image input and ${T["out"]} for image output per 1M tokens, with cached text input at ${T["text_cache"]} and cached image input at ${T["img_cache"]}. A 1024×1024 image costs about {money(a_low)} in image output at low quality and {money(a_med)} at medium. The per-image version <code>{c_slug}</code> is {pc} per image. See the model catalog for live prices.'),
        diff,
        ('How do I generate GIFs and SVGs?',
         'Both use <code>POST /v1/images/generations</code>. For a GIF, set <code>format</code> to gif, <code>frame_count</code> to 2–64 (default 9) and <code>frame_duration_ms</code> to 20–2000 ms (default 200); <code>size</code> sets each frame. For an SVG, set <code>format</code> to svg and <code>n</code> to 1. <code>quality</code> applies to the reference image behind the SVG, and the result is static vector content. Neither works with the edits endpoint, streaming or compression settings.'),
        ('How do complexity and markup-guided edits work?',
         '<code>complexity</code> takes low, medium or high and defaults to high. Changing it costs nothing extra. OpenAI recommends low for most edits, paired with the quality you need, and medium or high for scenes with many elements or constraints. Markup edits use <code>POST /v1/images/edits</code>: send the original as the first <code>image</code>, plus a transparent PNG as <code>markup</code> with the same width and height. Mark the areas to change and describe the change in the prompt. Markup cannot be combined with <code>mask</code>.'),
        (f'Is there a per-image version? How is {c_slug} priced?',
         f'Yes. <code>{c_slug}</code> is the per-image version of {name}. It uses the same endpoints; only the <code>model</code> field changes. Each image costs a flat {pc} at 1K, 2K or 4K and at any quality level. Each request returns one image, and <code>n</code>, <code>mask</code> and transparent backgrounds are not supported. At medium quality and above, or for large images, per-image billing is usually cheaper.'),
        ('Are there concurrency limits? Does it work from mainland China?',
         f'AnyAIGC sets no concurrency limit on {slug}, and every account gets this by default. The base URL is <code>https://anyaigc.ai/v1</code>, which is tuned for networks in mainland China, so you usually do not need a proxy. Billing is in USD, you can pay with WeChat Pay, Alipay, USDT or a credit card, and the same key works for 300+ other models.'),
        ('Can AnyAIGC issue invoices, including VAT special invoices?',
         'Yes. AnyAIGC issues invoices for the amount you top up, including Chinese VAT general invoices and VAT special invoices. Send your billing details to support to request one.'),
        ('Can my company pay by bank transfer and sign a contract?',
         f'Yes. Companies can top up by corporate bank transfer and sign a service agreement, and get a dedicated support and technical contact. <a href="{SUPPORT}">Contact AnyAIGC support</a> to get started.'),
        ('Can I use the generated images commercially?',
         "Usage rights and content policies follow OpenAI's official terms. AnyAIGC only provides API access and adds no extra restrictions on how you use the output. If an image involves real people's likenesses or third-party trademarks, make sure you have the rights you need."),
    ]
    return dict(
        title=title,
        desc=f'{name} API: {dpitch}. ${T["out"]}/1M image output or {pc}/image, unlimited concurrency, bank transfer and VAT invoices.',
        og_desc=f'{slug}: ${T["out"]} per 1M image output tokens, or {pc} per image. Adds complexity, markup edits, SVG and GIF output on /v1/images/generations and /v1/images/edits.',
        og_alt=f'AnyAIGC {name} API: {pitch}',
        keywords=f'{name} API,{slug},{slug} API,GPT Image 2.6 API,{name} pricing,GPT Image 2.6 API pricing,GPT Image 2.6 GIF,GPT Image 2.6 SVG,OpenAI image API,{name} API for business,{name} API invoice,AnyAIGC',
        crumb=f'{short} API', product=f'{name} API (AnyAIGC)', sku=slug,
        product_desc=f'Access OpenAI {name} ({slug}) through AnyAIGC: compatible with /v1/images/generations and /v1/images/edits, with complexity, markup, SVG and GIF output, billed per token with unlimited concurrency.',
        offers=[('Text input (per 1M tokens)', T['text_in']), ('Image input (per 1M tokens)', T['img_in']), ('Image output (per 1M tokens)', T['out']),
                ('Cached text input (per 1M tokens)', T['text_cache']), ('Cached image input (per 1M tokens)', T['img_cache'])],
        eyebrow=eyebrow, h1=f'{name}<span class="o-sr"> API</span><small>{h1sub}</small>', lead=lead, lead_sub=lead_sub, notice=None,
        facts=[('Model ID', slug), ('Image output', f'${T["out"]} / 1M'), ('Per image', f'{pc}'), ('Concurrency', 'Unlimited'), ('Enterprise', 'Contracts · invoices')],
        hero_imgs=hero_imgs, credit=CREDIT['en'], credit_url=POST_26, gif=gif('en', slug),
        about_h2=about_h2, about_ps=about, spec=spec,
        caps_h2=f'What is new in {short}', caps=caps, caps_lead='Sunburst and Flare both support these, with the same request fields.',
        gallery=gallery, gallery_h2=f'What {short} can make', gallery_lead=gallery_lead,
        price_h2=f'{name} API pricing', price_lead='Billed per token at fixed rates, with no subscription or monthly fee. Sunburst and Flare cost the same, and a flat per-image -c version is also available.',
        billing_label='Billing at a glance',
        billing=[('Token billing', 'Prompt text, reference images and output priced separately'), ('No complexity surcharge', 'Same rate at every level'), ('Unlimited concurrency', 'On by default for every account'), ('One balance', 'Works across 300+ models')],
        price_tables=price_tables('en', slug),
        price_note=f'Prices in USD, charged per successful request. The table shows the lowest price in the model catalog. SVG output is billed for the reference image tokens plus the tokens used to write the SVG. Cached rates apply only when upstream reports cache usage. See the <a href="{PRICING}">model catalog</a> for live prices.',
        costs_h3='Cost examples', costs_lead='Calculated from the rates above, counting image output tokens only and excluding prompt text.', costs=costs('en'),
        uses_h2=f'What {short} is good for', uses=uses,
        steps=[f'<strong>Sign up</strong>: <a href="{G.REG}">create an AnyAIGC account</a>. New accounts get 2 million tokens of trial credit, and top-ups start at $1.',
               '<strong>Create an API key</strong>: generate a key in the <a href="https://anyaigc.ai/console">console</a> and store it in the <code>ANYAIGC_API_KEY</code> environment variable.',
               f'<strong>Send a request</strong>: call <code>https://anyaigc.ai/v1/images/generations</code> with <code>model</code> set to <code>{slug}</code>. Use <code>/v1/images/edits</code> for edits and markup edits.'],
        codes=codes, qs_h2=f'Get started with the {name} API in three steps',
        callout=f'Want a flat price per image? Switch <code>model</code> to <code>{c_slug}</code> ({pc} per image at 1K, 2K or 4K) and drop <code>n</code> and <code>mask</code>.',
        qs_note=f'Regular images return <code>data[0].url</code>; pass <code>response_format=b64_json</code> to get base64. The GIF and SVG examples save the base64 result straight to a file. Prompts can be up to 1000 characters. Other fields match GPT Image 2.5; see the <a href="{DOCS_GEN_25}" target="_blank" rel="noopener">generations docs</a> and <a href="{DOCS_EDIT_25}" target="_blank" rel="noopener">edits docs</a>.',
        family_h2='All GPT Image models', family_lead='Same API key; switch models by changing the model field.',
        faq_h2=f'{name} API FAQ', faqs=faqs,
        final_h2=f'Start building with {name}', final_p='New accounts get 2 million tokens of trial credit. Make a few images, or a GIF, and see the results.',
        name=name, docs=DOCS_GEN_25,
    )
