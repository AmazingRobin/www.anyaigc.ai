# 多语言专题页：语言配置。新增语言只改这里和 briefs/<code>.md。
# 源语言是英文页（/en/models/），其余语言都从英文页翻译，不从中文页翻译。
SITE = 'https://www.anyaigc.ai'

# code：目录名；hreflang：<link rel=alternate> 与 <html lang>；og：og:locale；
# native：语言切换里显示的自称；ui：版块里"选择语言"这类固定文案的语言名
LANGS = {
    'zh': dict(hreflang='zh-CN', og='zh_CN', native='中文', source=False),
    'en': dict(hreflang='en', og='en_US', native='English', source=True),
    'ja': dict(hreflang='ja', og='ja_JP', native='日本語', source=False),
    'ko': dict(hreflang='ko', og='ko_KR', native='한국어', source=False),
    'es': dict(hreflang='es', og='es_ES', native='Español', source=False),
    'de': dict(hreflang='de', og='de_DE', native='Deutsch', source=False),
}
NEW = ['ja', 'ko', 'es', 'de']          # 本次新增
ALL = ['zh', 'en'] + NEW
# 页面 <title>、description 的长度上限，按语言单独定（日韩按显示宽度，汉字假名谚文计 2）
TITLE_MAX = {'ja': 64, 'ko': 64, 'es': 65, 'de': 65}
DESC_RANGE = {'ja': (60, 120), 'ko': (60, 120), 'es': (120, 160), 'de': (120, 160)}

# 海外用户的发票口径（用户 2026-11-17 确认）：平台自助开具发票，不写中国增值税流程、对公转账流程。
# 新语言页的企业接入、支付方式、FAQ 都按这个口径单独写，不能照搬 zh/en 的企业文案。
INVOICE_RULE = 'self-service invoices on the platform'


def url(lang, slug):
    return f'{SITE}/{lang}/models/' + ('' if slug == 'index' else slug)


def og_image(lang, slug):
    # 分享图每种语言各一张：assets/og/<slug>-<lang>.png
    return f'{SITE}/assets/og/{slug}-{lang}.png'
