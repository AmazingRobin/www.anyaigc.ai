# 生成 GPT 系列专题页分享图（1200×630）的 HTML 源文件，输出到 .playwright-mcp/og/，再用 Playwright 截图成 assets/og/<slug>-<lang>.png
# 用法：python scripts/og_gpt.py → 在 http://localhost:8765/.playwright-mcp/og/<name>.html 截图
# 价格读 .playwright-mcp/gpt_data.json 不稳定（临时文件），所以直接读页面价格表第一行的 AnyAIGC 价格
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '.playwright-mcp', 'og')
BRAND = 'AnyAIGC'  # 区分大小写

# 每个页面一句卖点 + 3 个标签
SUBS = {
    'gpt':           ({'zh': 'OpenAI 全系 9 个型号，一个 API Key 调用', 'en': 'Every OpenAI GPT model, one API key'},
                      {'zh': ['9 个型号', '约官方 0.5 折起', '对公 · 专票'], 'en': ['9 models', 'Up to 95% off', 'Contracts · invoices']}),
    'gpt-6-astra':   ({'zh': 'OpenAI 旗舰模型，约官方价 0.5 折', 'en': "OpenAI's flagship model at 95% off"},
                      {'zh': ['最高智能', 'Codex', '并发不限'], 'en': ['Top tier', 'Codex', 'Unlimited concurrency']}),
    'gpt-6.1-sol':   ({'zh': '接近 Astra 的智能，约官方价 0.5 折', 'en': 'Near-Astra intelligence at 95% off'},
                      {'zh': ['Responses API', 'Codex', '并发不限'], 'en': ['Responses API', 'Codex', 'Unlimited concurrency']}),
    'gpt-6-luna':    ({'zh': '高频批量任务，速度快、成本低', 'en': 'Fast, low-cost, built for volume'},
                      {'zh': ['约 1.3 折', '高频批量', '并发不限'], 'en': ['86% off', 'High volume', 'Unlimited concurrency']}),
    'gpt-6-sol':     ({'zh': '官方价比 GPT-5.6 Sol 低 50%', 'en': '50% below GPT-5.6 Sol list price'},
                      {'zh': ['约 0.5 折', '已有 6.1 Sol', '仍可调用'], 'en': ['95% off', 'Newer: 6.1 Sol', 'Still available']}),
    'gpt-5.6-sol':   ({'zh': 'GPT-5.6 旗舰，推广价约 0.6 折', 'en': 'GPT-5.6 flagship at 94% off promo price'},
                      {'zh': ['ultra 多智能体', 'Codex', '并发不限'], 'en': ['Ultra multi-agent', 'Codex', 'Unlimited concurrency']}),
    'gpt-5.6-terra': ({'zh': '比肩 GPT-5.5 的日常模型，约 0.5 折', 'en': 'GPT-5.5-class everyday model at 95% off'},
                      {'zh': ['均衡', '约 0.5 折', '并发不限'], 'en': ['Balanced', '95% off', 'Unlimited concurrency']}),
    'gpt-5.6-luna':  ({'zh': '大批量低价任务，约官方价 1.3 折', 'en': 'High-volume, low-cost at 86% off'},
                      {'zh': ['工具调用', '多步工作流', '并发不限'], 'en': ['Tool use', 'Multistep', 'Unlimited concurrency']}),
    'gpt-5.5':       ({'zh': '上一代旗舰，仍可调用，约 0.5 折', 'en': 'Previous flagship, still available, 95% off'},
                      {'zh': ['Terminal-Bench 2.0', 'Codex', '并发不限'], 'en': ['Terminal-Bench 2.0', 'Codex', 'Unlimited concurrency']}),
    'gpt-5.5-pro':   ({'zh': '高算力深度推理，仅 Responses API', 'en': 'More compute, deeper reasoning, Responses API'},
                      {'zh': ['约 5.9 折', '高准确率', 'Responses'], 'en': ['41% off', 'High accuracy', 'Responses only']}),
}

TPL = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1200px;height:630px;background:#000;color:#fff;font-family:Inter,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;position:relative;overflow:hidden}
.glow{position:absolute;inset:0;background:radial-gradient(circle at 74% 44%,rgba(250,229,152,.22),rgba(184,128,43,.10) 22%,transparent 46%),radial-gradient(circle at 50% 50%,#0d1a22 0%,#071016 40%,#000 75%)}
.disc{position:absolute;left:640px;top:70px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle at 45% 40%,#1b2a30,#071016 70%);box-shadow:0 0 120px rgba(250,229,152,.10)}
.c{position:absolute;left:80px;top:80px;right:80px}
.b{display:flex;align-items:center;gap:12px;font-size:26px;font-weight:600;letter-spacing:-.01em}
.b svg{width:30px;height:30px}
h1{margin:120px 0 0;font-size:@FSpx;line-height:1;font-weight:500;letter-spacing:-.03em;color:#f5f6fb;white-space:nowrap}
p{margin:22px 0 0;font-size:34px;line-height:1.3;color:rgba(255,255,255,.82);letter-spacing:-.01em}
.r{position:absolute;left:80px;bottom:64px;display:flex;gap:12px}
.r span{padding:10px 20px;border-radius:999px;border:1px solid rgba(255,255,255,.28);font-size:23px;color:rgba(255,255,255,.9);white-space:nowrap}
.r span.d{background:#fff;border-color:#fff;color:#000;font-weight:600}
</style></head><body><div class="glow"></div><div class="disc"></div><div class="c"><div class="b"><svg viewBox="0 0 24 24" fill="#ffffff" fill-rule="evenodd"><path d="@LOGO"/></svg>@BRAND</div><h1>@NAME</h1><p>@SUB</p></div><div class="r">@CHIPS</div></body></html>'''


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = re.search(r' d="([^"]+)"', read('assets/icons/openai.svg')).group(1)
    names = []
    for lang in ('zh', 'en'):
        for slug, (sub, tags) in SUBS.items():
            p = f'{lang}/models/{slug}.html'
            if not os.path.exists(os.path.join(ROOT, p)):
                continue
            s = read(p)
            if slug == 'gpt':
                name = 'GPT API'
                price = '$0.0135 / 1M 起' if lang == 'zh' else 'From $0.0135 / 1M'
            else:
                h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)
                h1 = re.sub(r'<span class="o-sr">.*?</span>', '', h1, flags=re.S)
                name = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h1)).strip()
                name = re.sub(r'\s*API$', '', name)
                name = re.sub(r'^GPT (\d)', r'GPT-\1', name)  # 拆分标题 GPT / 5.5 还原为 GPT-5.5
                m = re.search(r'<td class="o-num o-hl">(\$[0-9.]+)</td>', s)
                price = m.group(1) + (' / 1M 输入' if lang == 'zh' else ' / 1M input')
            chips = f'<span class="d">{price}</span>' + ''.join(f'<span>{t}</span>' for t in tags[lang])
            fs = '120' if len(name) <= 11 else ('104' if len(name) <= 13 else '92')
            html = (TPL.replace('@LOGO', logo).replace('@BRAND', BRAND).replace('@NAME', name)
                    .replace('@SUB', sub[lang]).replace('@CHIPS', chips).replace('@FS', fs))
            n = f'{slug}-{lang}'
            io.open(os.path.join(OUT, n + '.html'), 'w', encoding='utf-8').write(html)
            names.append(n)
    print(' '.join(names))


if __name__ == '__main__':
    main()
