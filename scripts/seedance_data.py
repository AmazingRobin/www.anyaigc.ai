"""Seedance catalog data read on 2026-11-05 (2.5 flash added 2026-11-20).

Pricing source: https://anyaigc.ai/pricing?keyword=seedance (detail drawers).
Rates are USD / 1M tokens. User confirmed using the lowest Fast/mini rates.
User confirmed on 2026-11-05: 2.0 supports 4K; mini uses the same content[]
request structure, generates one video per task, and has unlimited concurrency
by default for every user.
Official capabilities: seed.bytedance.com/zh/seedance2_0 and /zh/seedance2_5.
2026-11-20: 2.5 flash added from the catalog detail drawer (group Seedance-2,
USD / 1M tokens: 480p/720p without video input $8.505, with video input $5.225;
max 720p output). The official Seed pages do not mention flash, so its page only
states what the catalog and the docs confirm. User confirmed unlimited
concurrency and "reuse the closest documented endpoint, change only the model".
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.anyaigc.ai'
REG = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
PRICING = 'https://anyaigc.ai/pricing'
SUPPORT = 'https://anyaigc.ai/customersupport'
DOC_CREATE_20 = 'https://docs.anyaigc.ai/en/reference/seedance/post/api/v3/contents/generations/tasks?leaf=438503106'
DOC_CREATE_25 = 'https://docs.anyaigc.ai/en/reference/seedance/post/api/v3/contents/generations/tasks?leaf=c%3A1792738852814'
DOC_QUERY_20 = 'https://docs.anyaigc.ai/en/reference/volc/api/v3/contents/generations/tasks/%7Bid%7D?leaf=438503236'
DOC_QUERY = 'https://docs.anyaigc.ai/en/reference/seedance/api/v3/contents/generations/tasks/%7Bid%7D?leaf=c%3A1792739265091'
DATE = '2026-11-20'
VER = '20261120'

SLUGS = ['seedance', 'doubao-seedance-2-5', 'doubao-seedance-2-5-flash', 'doubao-seedance-2-0', 'doubao-seedance-2-0-fast', 'doubao-seedance-2-0-mini']

MODELS = {
    'doubao-seedance-2-5': {
        'name': 'Seedance 2.5', 'id': 'doubao-seedance-2-5-260628', 'min': '7.776',
        'desc_zh': '新一代多模态视频创作模型，面向长叙事、强参考、精准编辑与多语言内容。',
        'desc_en': 'A multimodal video model for long narratives, strong references, precise edits and multilingual content.',
        'rows': [('480p / 720p', '不含参考视频', '13.001'), ('480p / 720p', '含参考视频', '7.776'), ('1080p', '不含参考视频', '14.216'), ('1080p', '含参考视频', '8.505')],
        'rows_en': [('480p / 720p', 'Without reference video', '13.001'), ('480p / 720p', 'With reference video', '7.776'), ('1080p', 'Without reference video', '14.216'), ('1080p', 'With reference video', '8.505')],
        'official': 'https://seed.bytedance.com/zh/seedance2_5', 'tag': '最新', 'feature': '长叙事 · 强参考 · 精准编辑',
    },
    'doubao-seedance-2-5-flash': {
        'name': 'Seedance 2.5 flash', 'id': 'doubao-seedance-2-5-flash-261115', 'min': '5.225',
        'desc_zh': '字节跳动豆包推出的高效多模态视频生成模型，支持全模态音视频组合参考、有声视频生成及视频编辑延长，兼顾生成速度与多模态控制，最高支持 720p 输出。',
        'desc_en': 'An efficient multimodal video model from ByteDance Doubao. It supports combined audio and video references, video with sound, and video editing and extension, balancing speed with multimodal control, with output up to 720p.',
        'rows': [('480p / 720p', '不含参考视频', '8.505'), ('480p / 720p', '含参考视频', '5.225')],
        'rows_en': [('480p / 720p', 'Without reference video', '8.505'), ('480p / 720p', 'With reference video', '5.225')],
        'official': 'https://seed.bytedance.com/zh/seedance2_5', 'tag': '高效', 'feature': '高效生成 · 全模态参考 · 最高 720p',
    },
    'doubao-seedance-2-0': {
        'name': 'Seedance 2.0', 'id': 'doubao-seedance-2-0-260128', 'min': '2.916',
        'desc_zh': '专业级多模态创作视频模型，支持文字、图片、音频、视频参考，以及视频编辑和延长。',
        'desc_en': 'A professional multimodal video model with text, image, audio and video references, editing and extension.',
        'rows': [('480p / 720p', '不含参考视频', '8.505'), ('480p / 720p', '含参考视频', '5.225'), ('1080p', '不含参考视频', '9.356'), ('1080p', '含参考视频', '5.711'), ('4K', '不含参考视频', '4.860'), ('4K', '含参考视频', '2.916')],
        'rows_en': [('480p / 720p', 'Without reference video', '8.505'), ('480p / 720p', 'With reference video', '5.225'), ('1080p', 'Without reference video', '9.356'), ('1080p', 'With reference video', '5.711'), ('4K', 'Without reference video', '4.860'), ('4K', 'With reference video', '2.916')],
        'official': 'https://seed.bytedance.com/zh/seedance2_0', 'tag': '旗舰', 'feature': '全模态参考 · 原生音画 · 可编辑',
    },
    'doubao-seedance-2-0-fast': {
        'name': 'Seedance 2.0 Fast', 'id': 'doubao-seedance-2-0-fast-260128', 'min': '2.896',
        'desc_zh': '继承 Seedance 2.0 核心能力的快速版本，适合高频草稿与批量视频生成。',
        'desc_en': 'A faster Seedance 2.0 variant for high-frequency drafts and batch video generation.',
        'rows': [('480p / 720p', '不含参考视频', '4.914'), ('480p / 720p', '含参考视频', '2.896')],
        'rows_en': [('480p / 720p', 'Without reference video', '4.914'), ('480p / 720p', 'With reference video', '2.896')],
        'official': 'https://seed.bytedance.com/zh/seedance2_0', 'tag': '快速', 'feature': '更快生成 · 多模态 · 批量草稿',
    },
    'doubao-seedance-2-0-mini': {
        'name': 'Seedance 2.0 mini', 'id': 'doubao-seedance-2-0-mini-260615', 'min': '1.843',
        'desc_zh': '面向更广泛视频需求的高性价比型号，适合更低门槛、更高频、更规模化的应用。',
        'desc_en': 'A cost-effective model for broader video needs, lower entry barriers, higher frequency and scale.',
        'rows': [('480p / 720p', '不含参考视频', '3.071'), ('480p / 720p', '含参考视频', '1.843')],
        'rows_en': [('480p / 720p', 'Without reference video', '3.071'), ('480p / 720p', 'With reference video', '1.843')],
        'official': 'https://seed.bytedance.com/zh/seedance2_0', 'tag': '高性价比', 'feature': '低门槛 · 高频生成 · 易规模化',
    },
}
