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
ICONS = ['claude-color', 'claude', 'anthropic', 'suno', 'claudecode-color', 'openai', 'codex', 'codex-color']
NL = chr(10)


def fetch():
    os.makedirs(ICON_DIR, exist_ok=True)
    for i in ICONS:
        with urllib.request.urlopen(CDN.format(v=VERSION, id=i), timeout=30) as r:
            io.open(os.path.join(ICON_DIR, i + '.svg'), 'wb').write(r.read())
        print('fetched', i)


def paths(icon_id):
    s = io.open(os.path.join(ICON_DIR, icon_id + '.svg'), encoding='utf-8').read()
    return re.findall(r'<path\b[^>]*?d="([^"]+)"', s)


def svg(icon_id, cls='', size=None, fill=None, label=None):
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
    attrs.append('fill-rule="evenodd"' if 'fill-rule' not in body else '')
    attrs += ['aria-hidden="true"', 'focusable="false"'] if not label else ['role="img"', f'aria-label="{label}"']
    return '<svg ' + ' '.join(a for a in attrs if a) + '>' + body + '</svg>'


CLAUDE = svg('claude-color', cls='o-mark')
CLAUDE_HERO_ART = svg('claude-color')
CLAUDE_CARD = svg('claude-color', size=26)
SUNO_CARD = svg('suno', size=24, fill='#ffffff')
SUNO_HERO = svg('suno', cls='s-logo', fill='#ffffff')


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
            if s != o:
                io.open(p, 'w', encoding='utf-8', newline=NL).write(s)
                changed.append(f'{lang}/models/{f}')
    print('updated:', ', '.join(changed) or 'none')


if __name__ == '__main__':
    if '--fetch' in sys.argv:
        fetch()
    update_pages()
