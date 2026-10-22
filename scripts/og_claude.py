# 生成 Claude 系列专题页分享图（1200×630）的 HTML 源文件，再用 Playwright 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_claude.py  → 输出到 .playwright-mcp/og/，然后在 http://localhost:8765/.playwright-mcp/og/<name>.html 截图
# 文案全部从页面本身读取：标题取 H1，副标题取 og:title「｜/:」后的卖点，标签取专题首页卡片的 tags，价格取页面价格表
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 品牌名区分大小写，不要转成全大写

# 分享图副标题（每个模型一句卖点）。新增型号时在这里加一行；没写的从 og:title 自动截取
SUBS = {
    'claude':           {'zh': '全系 10 个型号，一个 API Key 调用', 'en': 'Every Claude model, one API key'},
    'claude-opus-5-5':  {'zh': '原生 /v1/messages 接口 · 官方价约 1.2 折', 'en': 'Native /v1/messages API · 88% off list price'},
    'claude-sonnet-5-5': {'zh': '接近 Opus 5.5，官方价约 1.2 折', 'en': 'Near-Opus results at 88% off list price'},
    'claude-haiku-5-5': {'zh': '高并发、低成本任务和子 Agent 之选', 'en': 'High-volume, low-cost work and sub-agents'},
    'claude-fable-5-1': {'zh': 'Mythos 级长任务模型，约 2.4 折', 'en': 'Mythos-level long-running agents, 76% off'},
    'claude-fable-5':   {'zh': 'Mythos 级模型，旧版仍可用', 'en': 'Mythos-class model, legacy but still live'},
    'claude-opus-5':    {'zh': '接近 Fable 5 的智能，约 1.2 折', 'en': 'Near-Fable 5 intelligence at 88% off'},
    'claude-sonnet-5':  {'zh': '接近 Opus 4.8 的 Agent 能力', 'en': 'Near-Opus 4.8 agents at 88% off'},
    'claude-opus-4-8':  {'zh': '4.x 系列最终版，约 1.2 折', 'en': 'The final 4.x Opus, 88% off list'},
    'claude-opus-4-7':  {'zh': 'SWE-bench Verified 87.6%，约 1.2 折', 'en': '87.6% SWE-bench Verified, 88% off'},
    'claude-opus-4-6':  {'zh': '旧版仍可用，约官方价 1.2 折', 'en': 'Legacy but still available, 88% off list'},
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#faf9f5;color:#141413;font-family:Inter,"Segoe UI","Microsoft YaHei",sans-serif;position:relative;overflow:hidden}
.c{position:absolute;left:90px;top:96px;right:90px}
.b{font-size:28px;font-weight:700;letter-spacing:.01em}
.t{display:flex;align-items:center;gap:26px;margin-top:38px}
h1{margin:0;font-family:Georgia,"Songti SC","SimSun",serif;font-size:@FSpx;line-height:1;font-weight:500;letter-spacing:-2px;white-space:nowrap}
p{margin:30px 0 0;font-family:Georgia,"Songti SC","SimSun",serif;font-size:34px;color:#30302e}
.r{position:absolute;left:90px;bottom:80px;display:flex;gap:14px}
.r span{padding:10px 20px;border-radius:999px;background:#f5f4ed;border:1px solid #e8e6dc;font-size:24px;color:#3d3d3a;white-space:nowrap}
.r span.d{background:#141413;border-color:#141413;color:#faf9f5}
</style></head><body><div class="c"><div class="b">@BRAND</div><div class="t"><svg viewBox="0 0 24 24" width="92" height="92" fill="#d97757"><path d="@STAR"/></svg><h1>@NAME</h1></div><p>@SUB</p></div><div class="r">@CHIPS</div></body></html>'''


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def main():
    os.makedirs(OUT, exist_ok=True)
    names = []
    for lang in ('zh', 'en'):
        hub = read(f'{lang}/models/index.html')
        star = re.search(r'<path\b[^>]*?d="([^"]+)"', read('assets/icons/claude-color.svg')).group(1)  # lobe-icons claude-color
        for f in sorted(os.listdir(os.path.join(ROOT, lang, 'models'))):
            if not (f.startswith('claude') and f.endswith('.html')):
                continue
            slug = f[:-5]
            s = read(f'{lang}/models/{f}')
            if slug == 'claude':
                # 系列总览页：标题固定为 Claude API，标签取全系卖点
                n = f'claude-{lang}'
                tags = ['10 个型号', '约官方 1.2 折起', '对公 · 专票'] if lang == 'zh' else ['10 models', 'Up to 88% off', 'Contracts · invoices']
                chips = '<span class="d">' + ('$0.0119 / 1M 起' if lang == 'zh' else 'From $0.0119 / 1M') + '</span>' + ''.join(f'<span>{t}</span>' for t in tags)
                html = (TPL.replace('@BRAND', BRAND).replace('@STAR', star).replace('@NAME', 'Claude API')
                        .replace('@SUB', SUBS['claude'][lang]).replace('@CHIPS', chips).replace('@FS', '104'))
                io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
                names.append(n)
                continue
            name = re.sub(r'\s*API$', '', re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)).strip())
            sub = SUBS.get(slug, {}).get(lang)
            if not sub:
                og_title = re.search(r'property="og:title" content="([^"]*)"', s).group(1)
                sub = re.split(r'[｜:]', og_title, maxsplit=1)[-1]
                sub = re.sub(r'\s*[-|]\s*AnyAIGC.*$', '', sub).strip()
            price = re.search(r'<td class="o-num o-hl">(\$[0-9.]+)</td>', s).group(1)
            card = re.search(r'href="/' + lang + '/models/' + re.escape(slug) + r'">.*?<ul class="af-tags">(.*?)</ul>', hub, re.S)
            tags = re.findall(r'<li>([^<]*)</li>', card.group(1))[:3] if card else []
            unit = ' / 1M 输入' if lang == 'zh' else ' / 1M input'
            chips = [f'<span class="d">{price}{unit}</span>'] + [f'<span>{t}</span>' for t in tags]
            fs = '96' if len(name) <= 15 else '88'
            html = (TPL.replace('@BRAND', BRAND).replace('@STAR', star).replace('@NAME', name)
                    .replace('@SUB', sub).replace('@CHIPS', ''.join(chips)).replace('@FS', fs))
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))


if __name__ == '__main__':
    main()
