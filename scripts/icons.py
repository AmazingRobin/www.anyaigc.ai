# 模型 logo 统一使用 lobe-icons（MIT，https://github.com/lobehub/lobe-icons），不要自己画。
# 源文件下载到 assets/icons/<id>.svg（固定版本，见 VERSION）。本脚本把图标 path 内联到页面里，颜色写在 SVG 属性上。
# 用法：python scripts/icons.py            → 更新所有专题页与专题首页里的模型 logo
#       python scripts/icons.py --fetch    → 先按 VERSION 重新下载 ICONS 里的图标
import io
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(ROOT, 'assets', 'icons')
VERSION = '1.97.0'
CDN = 'https://registry.npmmirror.com/@lobehub/icons-static-svg/{v}/files/icons/{id}.svg'
ICONS = ['claude-color', 'claude', 'anthropic', 'suno', 'claudecode-color', 'openai', 'codex', 'codex-color', 'typesafeai', 'gemini-color', 'gemini']
# 个别图标只在更新的版本里有，单独指定版本（其余图标仍用 VERSION）
ICON_VERSION = {'typesafeai': '1.98.0'}
NL = chr(10)


def fetch():
    os.makedirs(ICON_DIR, exist_ok=True)
    for i in ICONS:
        with urllib.request.urlopen(CDN.format(v=ICON_VERSION.get(i, VERSION), id=i), timeout=30) as r:
            io.open(os.path.join(ICON_DIR, i + '.svg'), 'wb').write(r.read())
        print('fetched', i)


def paths(icon_id):
    s = io.open(os.path.join(ICON_DIR, icon_id + '.svg'), encoding='utf-8').read()
    return re.findall(r'<path\b[^>]*?d="([^"]+)"', s)


def svg(icon_id, cls='', size=None, fill=None, label=None, evenodd=True):
    """内联 SVG。fill 为 None 时用图标自带颜色（-color 版本）或 currentColor。"""
    raw = io.open(os.path.join(ICON_DIR, icon_id + '.svg'), encoding='utf-8').read()
    body = re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S).group(1)
    body = re.sub(r'<title>.*?</title>', '', body, flags=re.S)
    attrs = ['viewBox="0 0 24 24"']
    if cls:
        attrs.insert(0, f'class="{cls}"')
    if size:
        attrs += [f'width="{size}"', f'height="{size}"']
    if fill:
        attrs.append(f'fill="{fill}"')
        body = re.sub(r'\sfill="[^"]*"', '', body)
    elif 'fill=' not in body:
        attrs.append('fill="currentColor"')
    attrs.append('fill-rule="evenodd"' if evenodd and 'fill-rule' not in body else '')
    attrs += ['aria-hidden="true"', 'focusable="false"'] if not label else ['role="img"', f'aria-label="{label}"']
    return '<svg ' + ' '.join(a for a in attrs if a) + '>' + body + '</svg>'


CLAUDE = svg('claude-color', cls='o-mark')
CLAUDE_HERO_ART = svg('claude-color')
CLAUDE_CARD = svg('claude-color', size=26)
SUNO_CARD = svg('suno', size=24, fill='#ffffff')
SUNO_HERO = svg('suno', cls='s-logo', fill='#ffffff')
# TypeSafe（Jev 系列）：图标本身不用 evenodd，保持 nonzero 填充
TS_INK = svg('typesafeai', fill='#1E1E1E', evenodd=False)
TS_MARK = svg('typesafeai', cls='j-mark', fill='#1E1E1E', evenodd=False)
TS_FOOT = svg('typesafeai', fill='#FEFEFE', evenodd=False)
TS_CARD = svg('typesafeai', size=24, fill='#1E1E1E', evenodd=False)
ANY_SVG = r'<svg\b(?:(?!</svg>).)*?</svg>'
# Gemini 星芒：彩色版带渐变 <defs>，同一页内联多次时给渐变 id 加序号，避免 id 重复
GEMINI_FOOT = svg('gemini', cls='gm-mark gm-mono', fill='#ffffff')
GEMINI_CARD_BG = 'background:#ffffff;border:1px solid #e1e6ec'


def gemini_color(cls='gm-mark', size=None):
    n = [0]

    def one(_=None):
        n[0] += 1
        out = svg('gemini-color', cls=cls, size=size, evenodd=False)
        return re.sub(r'lobe-icons-gemini-(\d)-_R_0_', lambda m: f'gm{n[0]}-{m.group(1)}', out)
    return one


def update_pages():
    changed = []
    for lang in ('zh', 'en'):
        d = os.path.join(ROOT, lang, 'models')
        for f in sorted(os.listdir(d)):
            if not f.endswith('.html'):
                continue
            p = os.path.join(d, f)
            s = io.open(p, encoding='utf-8').read()
            o = s
            # Claude 星芒：专题页首屏/结尾（o-mark）
            s = re.sub(r'<svg class="o-mark"[^>]*>.*?</svg>', CLAUDE, s, flags=re.S)
            # 总览页首屏大图
            s = re.sub(r'(<div class="p-hero-art"[^>]*>\s*)<svg\b.*?</svg>', lambda m: m.group(1) + CLAUDE_HERO_ART, s, flags=re.S)
            # Suno 专题页首屏标题
            s = re.sub(r'<svg class="s-logo".*?</svg>', SUNO_HERO, s, flags=re.S)
            # 专题首页卡片
            s = re.sub(r'(<span class="af-model-logo" style="background:#faf9f5;border:1px solid #e8e6dc" aria-hidden="true">)<svg\b.*?</svg>(</span>)',
                       lambda m: m.group(1) + CLAUDE_CARD + m.group(2), s, flags=re.S)
            s = re.sub(r'(<span class="af-model-logo" style="background:linear-gradient\(135deg,#ffb003,#e8502a 55%,#fe3c7d\)" aria-hidden="true">)(?:♫|<svg\b.*?</svg>)(</span>)',
                       lambda m: m.group(1) + SUNO_CARD + m.group(2), s, flags=re.S)
            # Jev（TypeSafe）专题页：首屏眉标、关于窗口、结尾 j-mark、页脚
            if f.startswith('jev'):
                s = re.sub(r'(<p class="j-eyebrow">)' + ANY_SVG, lambda m: m.group(1) + TS_INK, s, flags=re.S)
                s = re.sub(r'(<div class="j-win j-about-win">\s*<div class="j-win-bar">.*?</div>\s*<div class="j-win-body">\s*)' + ANY_SVG,
                           lambda m: m.group(1) + TS_INK, s, flags=re.S)
                s = re.sub(r'<svg class="j-mark"(?:(?!</svg>).)*?</svg>', TS_MARK, s, flags=re.S)
                s = re.sub(r'(<div class="o-foot-bottom">\s*<p>)' + ANY_SVG, lambda m: m.group(1) + TS_FOOT, s, flags=re.S)
            # Gemini 专题页：首屏、结尾 gm-mark 用彩色星芒，页脚 gm-mono 用白色单色
            if f.startswith('gemini'):
                s = re.sub(r'<svg class="gm-mark gm-mono"(?:(?!</svg>).)*?</svg>', GEMINI_FOOT, s, flags=re.S)
                s = re.sub(r'<svg class="gm-mark"(?:(?!</svg>).)*?</svg>', gemini_color(), s, flags=re.S)
            # 专题首页 Gemini 卡片
            s = re.sub(r'(<span class="af-model-logo" style="' + GEMINI_CARD_BG + r'" aria-hidden="true">)' + ANY_SVG + '(</span>)',
                       (lambda f: lambda m: m.group(1) + f() + m.group(2))(gemini_color(cls='', size=26)), s, flags=re.S)
            # 专题首页 Jev 卡片
            s = re.sub(r'(<span class="af-model-logo" style="background:#F386A1;border:1px solid #1E1E1E;border-radius:0" aria-hidden="true">)' + ANY_SVG + '(</span>)',
                       lambda m: m.group(1) + TS_CARD + m.group(2), s, flags=re.S)
            if s != o:
                io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
                changed.append(f'{lang}/models/{f}')
    print('updated:', ', '.join(changed) or 'none')


if __name__ == '__main__':
    if '--fetch' in sys.argv:
        fetch()
    update_pages()
