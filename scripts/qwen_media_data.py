"""Qwen media catalog captured from model-detail drawers on 2026-11-07.

Amounts below preserve the catalog's displayed precision. Image 3.0 prices
are billing-unit base rates, not the cost of an output image. No group names
are rendered on the public pages. See qwen_media_notes.md for provenance.
"""
from decimal import Decimal, ROUND_HALF_UP

DATE = '2026-11-07'
VERSION = '20261107'
CNY_PER_USD = Decimal('6.7')
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
MARKET = 'https://anyaigc.ai/pricing?provider=Qwen'
SUPPORT = 'https://anyaigc.ai/customersupport'
VIDEO_ENDPOINT = '/alibailian/api/v1/services/aigc/video-generation/video-synthesis'


def rate(zh, en, amount, unit, multiplier=1, saving=None):
    return dict(zh=zh, en=en, amount=amount, unit=unit, multiplier=multiplier, saving=saving)


MODELS = [
    dict(slug='qwen-image-3.0', name='Qwen Image 3.0', kind='image',
         lead=('把长指令，变成信息丰富的画面。', 'Turn detailed instructions into rich visual content.'),
         summary=('面向海报、信息图与界面创作，支持最长 4.5K tokens 指令，兼顾文字渲染和复杂排版。', 'Create posters, infographics, and interfaces with up to 4.5K instruction tokens and detailed text layouts.'),
         features=[('4.5K tokens 指令', '4.5K instruction tokens', '为复杂构图、文字内容和元素关系提供更完整的描述空间。', 'Describe composition, wording, and relationships between visual elements in detail.'), ('细小文字与多语言', 'Small text, multiple languages', '官方展示 10px 小字与 12 种语言的渲染能力，适合信息密集的画面。', 'Official examples demonstrate 10px text and 12 languages for information-dense visuals.'), ('生成与参考图编辑', 'Generate and edit with references', '输出图像和参考图片分别计费，适合持续迭代同一创意。', 'Output images and reference images are billed separately for iterative creative work.')],
         rates=[rate('计费基价', 'Billing-unit base rate', '0.00159', 'base')],
         factors=[('输出图片', 'Output image', 18), ('参考图片', 'Reference image', 2)],
         uses=[('信息图与教育内容', 'Infographics and education', '把概念、说明文字与示意内容组合到同一版面。', 'Combine explanations, labels, and visual concepts in a single layout.'), ('产品界面与创意海报', 'Interfaces and posters', '先说明层级、文案、布局与风格，再迭代细节。', 'Specify hierarchy, copy, layout, and style, then iterate on details.')]),
    dict(slug='qwen-image-3.0-pro', name='Qwen Image 3.0 Pro', kind='image',
         lead=('复杂版面，细节也要到位。', 'Complex layouts, with attention to the details.'),
         summary=('适合报纸、菜单、分镜和界面等密集内容，支持 4.5K tokens 指令，按 1K / 2K 输出档位计费。', 'Build newspapers, menus, storyboards, and interfaces with 4.5K instruction tokens and separate 1K / 2K output rates.'),
         features=[('密集信息排版', 'Dense visual layouts', '把多块文字、画中画和分镜组织到同一张图中。', 'Organize text blocks, nested visuals, and storyboard panels in one image.'), ('1K / 2K 输出档位', '1K / 2K output tiers', '面积不超过 225 万像素按 1K 档计算；2K 档输出倍率更高。', 'Up to 2.25 million pixels falls in the 1K tier; the 2K output tier uses a higher billing multiplier.'), ('参考图独立计费', 'Separate reference billing', '每张参考图按基价的 2 倍计算，与输出费用相加。', 'Each reference image costs two billing units, added to the output charge.')],
         rates=[rate('计费基价', 'Billing-unit base rate', '0.00159', 'base')],
         factors=[('1K 输出图片', '1K output image', 25), ('2K 输出图片', '2K output image', 50), ('参考图片', 'Reference image', 2)],
         uses=[('菜单、试卷与分镜', 'Menus, worksheets, storyboards', '为文字密集与多格版面提供细致描述，减少反复拼接。', 'Describe dense text and multi-panel layouts as a complete composition.'), ('人像与细节表现', 'Portraits and fine detail', '通过光影、材质与局部描述控制画面质感。', 'Guide the look through lighting, materials, and localized detail.')]),
    dict(slug='wan2.7-image-pro', name='Wan 2.7 Image Pro', kind='image',
         lead=('从一张参考图，延展完整创意。', 'Build a visual idea from your references.'),
         summary=('万相图像生成与编辑模型，支持文生图、图像编辑、组图创作、多参考和交互式编辑。', 'Wan image generation and editing supports text prompts, image sets, multiple references, and interactive revisions.'),
         features=[('生成与编辑', 'Generation and editing', '同一模型覆盖新图创作与已有图片修改。', 'Create new images or revise existing ones with the same model.'), ('多参考创作', 'Multiple references', '组合主体与场景参考，适合连续的视觉创作。', 'Combine subject and scene references across a creative workflow.'), ('文字与主体一致性', 'Text and subject consistency', '围绕复杂指令、画面文字和主体保持安排任务。', 'Use detailed instructions for text rendering and consistent subjects.')],
         rates=[rate('图片输出', 'Image output', '0.0645', 'image')]),
    dict(slug='qwen-image-2.0-2026-03-03', name='Qwen Image 2.0 · 2026-03-03', short='Qwen Image 2.0', kind='image',
         lead=('生成和编辑，在同一创作流程里。', 'Generation and editing in one creative workflow.'),
         summary=('Qwen Image 2.0 的加速快照版本，统一图像生成与编辑，支持最长 1K tokens 指令。', 'An accelerated Qwen Image 2.0 snapshot combining generation and editing with up to 1K instruction tokens.'),
         features=[('加速版本', 'Accelerated variant', '在图像质量与推理效率之间取得平衡，适合持续迭代。', 'Balance image quality and inference efficiency across iterative tasks.'), ('生成编辑一体', 'Unified creation and editing', '在同一模型上完成文生图与图像修改。', 'Use one model for text-to-image creation and image revisions.'), ('固定快照名', 'Dated snapshot ID', '调用时使用完整日期后缀，明确选择 2026-03-03 版本。', 'Use the full dated ID to select the 2026-03-03 snapshot explicitly.')],
         rates=[rate('图片输出', 'Image output', '0.0258', 'image')]),
    dict(slug='z-image-turbo', name='Z-Image Turbo', kind='image',
         lead=('轻量推理，让创意快速成形。', 'Lightweight inference for visual exploration.'),
         summary=('6B 参数、8 步推理的图像模型，适合写实画面、中英文文字与多种主题的文生图任务。', 'A 6B-parameter image model with eight-step inference for photorealism, Chinese and English text, and varied subjects.'),
         features=[('6B 参数', '6B parameters', '轻量模型结构用于高效率图像生成。', 'A compact model architecture designed for efficient generation.'), ('8 步推理', 'Eight-step inference', '适合需要频繁试稿、比较构图与风格的工作流。', 'Useful for frequent drafts and comparisons of composition and style.'), ('中英文文字', 'Chinese and English text', '把需要出现在画面中的文字与视觉描述一起提交。', 'Specify on-image text alongside the visual description.')],
         rates=[rate('图像生成调用', 'Image generation request', '0.0101', 'request')]),
    dict(slug='qwen-image-max', name='Qwen Image Max', kind='image',
         lead=('真实质感，细节自然呈现。', 'Natural detail and a realistic look.'),
         summary=('Qwen Image Max 聚焦写实质感、人物细节、自然纹理与文字渲染，适合多类图像生成任务。', 'Qwen Image Max focuses on realism, human detail, natural textures, and text rendering across image-generation tasks.'),
         features=[('写实质感', 'Realistic texture', '围绕光线、材质和人物细节生成画面。', 'Guide results with lighting, materials, and human detail.'), ('自然细节', 'Natural detail', '适合商品展示、人物与自然场景等题材。', 'Suitable for product visuals, people, and natural scenes.'), ('按次计费', 'Per-request billing', '按模型详情中的调用价格计算，不把单次调用等同于固定图片数量。', 'Use the catalog request rate; a request does not imply a fixed image count.')],
         rates=[rate('图像生成调用', 'Image generation request', '0.0658', 'request')]),
    dict(slug='qwen-image-max-2025-12-30', name='Qwen Image Max · 2025-12-30', short='Qwen Image Max 12-30', kind='image',
         lead=('固定快照，延续已有创作。', 'A dated snapshot for an existing workflow.'),
         summary=('Qwen Image Max 的 2025-12-30 快照，用完整模型名选择版本，关注真实感、细节和文字生成。', 'The 2025-12-30 Qwen Image Max snapshot preserves an explicit version choice for realism, detail, and text generation.'),
         features=[('日期快照', 'Dated snapshot', '完整模型名包含 2025-12-30，适合明确版本的现有接入。', 'The full model ID includes 2025-12-30 for explicit version selection.'), ('写实生成', 'Realistic generation', '面向人物纹理、自然细节与文字排版。', 'Create human textures, natural details, and on-image text.'), ('独立调用名', 'Explicit model ID', '与无日期版本分别列出，方便按项目需要选择。', 'Listed separately from the undated model for project-level selection.')],
         rates=[rate('图像生成调用', 'Image generation request', '0.0658', 'request')]),
    dict(slug='wan3.0-video', name='Wan 3.0 Video', kind='video',
         lead=('让一段镜头，容纳完整故事。', 'Let one shot hold an entire story.'),
         summary=('万相 3.0 支持最长 30 秒视频、全模态参考和音画同出，覆盖参考生成、编辑、复刻与驱动。', 'Wan 3.0 supports up to 30 seconds, omni references, and native audio-visual generation across creation and editing.'),
         features=[('最长 30 秒', 'Up to 30 seconds', '为完整叙事、连续运镜和多阶段动作留出时间。', 'Make room for a narrative arc, continuous camera work, and evolving action.'), ('全模态参考', 'Omni reference', '官方支持文字、图片、视频、音频、文档和网页输入。', 'The official model accepts text, images, video, audio, documents, and web pages.'), ('480P / 720P / 1080P', '480P / 720P / 1080P', '按目标分辨率和视频秒数计费，三档价格分别展示。', 'Billing depends on resolution and video seconds, with each tier listed separately.')],
         rates=[rate('480P 视频', '480P video', '0.0439', 'second', saving='12.2'), rate('720P 视频', '720P video', '0.0878', 'second', saving='12.2'), rate('1080P 视频', '1080P video', '0.1755', 'second', saving='12.25')],
         official=['0.05', '0.10', '0.20']),
]

for version, mode in [('1.1','r2v'), ('1.0','t2v'), ('1.1','t2v'), ('1.1','i2v'), ('1.0','video-edit'), ('1.0','r2v'), ('1.0','i2v')]:
    modes = {
        't2v': ('文生视频', 'Text-to-video', '从场景、人物、动作和镜头描述出发，将文字转化为动态画面。', 'Turn descriptions of scenes, characters, action, and camera movement into video.'),
        'i2v': ('图生视频', 'Image-to-video', '以输入图像为视觉起点，延续画面构图、主体和细节，生成动态片段。', 'Start from an image and carry its composition, subjects, and details into motion.'),
        'r2v': ('参考生视频', 'Reference-to-video', '最多使用 9 张参考图，保持主体、场景和风格，延续创作意图。', 'Use up to nine reference images to preserve subjects, scenes, and style.'),
        'video-edit': ('视频编辑', 'Video editing', '通过自然语言修改已有视频，最多使用 5 张参考图，支持局部和整体编辑。', 'Edit existing video with natural language and up to five reference images for local or global changes.'),
    }
    z, e, zd, ed = modes[mode]
    MODELS.append(dict(slug=f'happyhorse-{version}-{mode}', name=f'HappyHorse {version} {mode.upper() if mode != "video-edit" else "Video Edit"}', kind='video',
        lead=(z+'，让创作意图延续到每一帧。', e+' that carries your creative intent into motion.'),
        summary=(f'HappyHorse {version} {z}模型。{zd}', f'HappyHorse {version} for {e.lower()}. {ed}'),
        features=[(z,e,zd,ed), ('720P / 1080P','720P / 1080P','按分辨率与生成视频时长计费，先确定规格再估算费用。','Choose a resolution and output duration before estimating cost.'),
                  ('主体与动态表现','Subjects and motion', '明确主体特征、镜头调度和场景变化，帮助模型延续画面意图。', 'Describe subject details, camera direction, and scene changes to guide the result.')],
        rates=[rate('720P 视频', '720P video', '0.1161', 'second'), rate('1080P 视频','1080P video','0.1549' if version=='1.1' else '0.2065','second')]))

for v in ['2.6','2.5']:
    tiers = [('720P',5,'0.2904'),('720P',10,'0.5808'),('720P',15,'0.8712'),('1080P',5,'0.4840'),('1080P',10,'0.9680'),('1080P',15,'1.452')] if v=='2.6' else [('480P',5,'0.1452'),('480P',10,'0.2904'),('720P',5,'0.2904'),('720P',10,'0.5808'),('1080P',5,'0.4840'),('1080P',10,'0.9680')]
    preview=' Preview' if v=='2.5' else ''
    MODELS.append(dict(slug=f'wan{v}-i2v'+('-preview' if v=='2.5' else ''), name=f'Wan {v} I2V{preview}',kind='video',
        lead=('让静态图像，进入下一段故事。','Give a still image its next scene.'),
        summary=(f'Wan {v} 图生视频'+('预览模型，按 480P、720P、1080P 与 5/10 秒档位列价。' if v=='2.5' else '模型，支持多镜头叙事、配音与自定义音频，按 5/10/15 秒档位列价。'),
                 f'Wan {v} image-to-video '+('preview with 480P, 720P, and 1080P pricing for 5- and 10-second outputs.' if v=='2.5' else 'with multi-shot narratives, dubbing, and custom audio; priced for 5-, 10-, and 15-second outputs.')),
        features=[('首帧图生视频','First-frame image-to-video','以首帧图片确定视觉起点，再描述后续动作和运镜。','Use a first-frame image to establish the look, then describe action and camera movement.'),('时长档位','Duration tiers','按详情页列出的分辨率与时长组合选择，表内为一段视频的价格。','Choose from the resolution and duration combinations listed; prices are per video.'),('异步任务','Asynchronous tasks','提交生成任务后再查询结果，适合接入内容制作流水线。','Submit generation and retrieve the result later as part of a production workflow.')],
        rates=[rate(f'{res} · {seconds} 秒',f'{res} · {seconds}s',amount,'clip') for res,seconds,amount in tiers]))

MODELS.append(dict(slug='qwen3.8-omni-flash-realtime',name='Qwen3.8 Omni Flash Realtime',short='Qwen3.8 Omni Realtime',kind='realtime',
    lead=('实时听见、看见，并作出回应。','Listen, see, and respond in real time.'),
    summary=('面向智能硬件、机器人和交互 Agent 的实时全模态模型。音频与文本输出独立计费，支持 Function Call 与 MCP 接入。','A real-time omni model for devices, robots, and interactive agents, with separate audio/text billing and tool integration.'),
    features=[('音视频双工交互','Duplex audio-video interaction','支持多通道音频输入与实时交互，适合持续会话。','Supports multi-channel audio input and ongoing real-time conversations.'),('多语言输入输出','Multilingual input and output','模型广场列明 60+ 语言音频输入、30+ 语言语音输出。','The catalog lists audio input in 60+ languages and speech output in 30+ languages.'),('工具与 MCP','Tools and MCP','在实时会话中接入业务工具与服务，编排交互逻辑。','Connect business tools and services to a live conversation workflow.')],
    rates=[rate('输入：音频','Input: audio','1.3810','tokens'),rate('输入：文本 / 图片 / 视频','Input: text / image / video','0.3416','tokens'),rate('输出：文本','Output: text','1.0400','tokens'),rate('输出：音频','Output: audio','2.7770','tokens')]))

BY_SLUG = {m['slug']: m for m in MODELS}
IMG = [m for m in MODELS if m['kind']=='image']
VID = [m for m in MODELS if m['kind']!='image']
UNITS = {'image':('张','image'), 'request':('次','request'), 'second':('秒','second'), 'clip':('段','clip'), 'tokens':('百万 tokens','1M tokens'), 'base':('计费单位','billing unit')}


def entry_rate(m):
    if m.get('factors'):
        return m['rates'][0]
    return min(m['rates'],key=lambda r:Decimal(r['amount']))


def display_currency(m, lang):
    return 'CNY' if lang == 'zh' and m['kind'] in ('image', 'video') else 'USD'


def display_amount(usd, m, lang):
    """Round CNY only for display; calculations use the original USD rates."""
    if display_currency(m, lang) == 'USD':
        return str(usd)
    value = (Decimal(str(usd)) * CNY_PER_USD).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return format(value, '.2f')


def money(usd, m, lang):
    symbol = '¥' if display_currency(m, lang) == 'CNY' else '$'
    return symbol + display_amount(usd, m, lang)


def price_label(m, lang):
    r=entry_rate(m); unit=UNITS[r['unit']][lang=='en']
    extra=(' 基价' if lang=='zh' else ' base') if m.get('factors') else ''
    return f'{money(r["amount"], m, lang)} / {unit}{extra}'
