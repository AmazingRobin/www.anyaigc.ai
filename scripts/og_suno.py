"""Generate Suno sharing-image HTML; render at 1200x630 with Playwright."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.playwright-mcp/og'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    logo = (ROOT / 'assets/icons/suno.svg').read_text(encoding='utf-8').replace('fill="currentColor"', 'fill="#ffffff"')
    for lang in ('zh', 'en'):
        subtitle = 'AI 音乐生成接口 · 发起创作 ¥0.80/次' if lang == 'zh' else 'AI music generation API · from $0.1191 per song'
        tags = ['v3 – v6', '200 RPM', '分轨 + MIDI', '对公 · 专票'] if lang == 'zh' else ['v3 – v6', '200 RPM', 'Stems + MIDI', 'Contracts · invoices']
        chips = ''.join(f'<span>{tag}</span>' for tag in tags)
        html = f'''<!doctype html><html lang="{'zh-CN' if lang == 'zh' else 'en'}"><head><meta charset="utf-8"><title>Suno API | AnyAIGC</title><style>
*{{box-sizing:border-box}}body{{margin:0;width:1200px;height:630px;overflow:hidden;position:relative;background:#101012;color:#fff;font-family:Arial,"Microsoft YaHei",sans-serif}}
.aura{{position:absolute;border-radius:50%;filter:blur(90px)}}
.a1{{width:600px;height:600px;left:-300px;top:-330px;background:#ffb003;opacity:.6}}
.a2{{width:600px;height:600px;right:-50px;top:-400px;background:#fe3c7d;opacity:.45}}
.a3{{width:500px;height:500px;left:280px;top:340px;background:#e8502a;opacity:.3}}
.content{{position:absolute;left:80px;right:80px;top:98px}}.brand{{font-size:24px;font-weight:700}}.title{{display:flex;align-items:center;gap:30px;margin-top:42px}}.logo{{width:100px;height:132px;display:flex;align-items:center}}.logo svg{{width:100px;height:132px;fill:#fff}}h1{{font-size:104px;font-weight:700;letter-spacing:-2px;line-height:1;margin:0}}p{{font-size:36px;margin:42px 0 0;color:#f0edef}}
.tags{{position:absolute;left:80px;bottom:74px;display:flex;gap:16px}}.tags span{{font-size:23px;white-space:nowrap;padding:15px 22px;border:1px solid #ffffff30;border-radius:999px;background:#10101255}}
</style></head><body><div class="aura a1"></div><div class="aura a2"></div><div class="aura a3"></div><div class="content"><div class="brand">AnyAIGC</div><div class="title"><div class="logo">{logo}</div><h1>Suno API</h1></div><p>{subtitle}</p></div><div class="tags">{chips}</div></body></html>'''
        path = OUT / f'suno-{lang}.html'
        path.write_text(html, encoding='utf-8')
        print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
