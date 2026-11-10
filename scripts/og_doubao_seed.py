"""Write temporary 1200x630 HTML share cards and a Playwright CLI capture job.

Run python scripts/og_doubao_seed.py, then use playwright-cli run-code
--filename=.playwright-mcp/doubao-og/capture.js in an open browser session.
Only CSS and the pinned lobe-icons ByteDance SVG are used.
"""
import json
from doubao_seed_pages import (
    ROOT, VER, e, name, logo, tr, art,
    MODELS, COPY, SLUGS, SNAPSHOT_IDS, LATEST,
)

OUT = ROOT / '.playwright-mcp/doubao-og'

def card(lang, slug):
    c = COPY[slug][lang]
    tags = ['Chat Completions', '300+ ' + tr(lang, '模型', 'models'), tr(lang, '对公 · 专票', 'Bank transfer · VAT')]
    title = name(slug).replace('doubao-seed-', 'doubao-seed-<br>', 1)
    return f'''<!DOCTYPE html><html lang="{tr(lang, 'zh-CN', 'en')}" class="no-js"><head><meta charset="utf-8">
<link rel="stylesheet" href="/assets/models/doubao-seed.css?v={VER}">
<style>
html,body{{width:1200px;height:630px;margin:0;overflow:hidden;background:#101116;color:#fff}}
body{{position:relative;background:radial-gradient(ellipse at 88% 30%,#26387388,transparent 60%),radial-gradient(ellipse at 90% 95%,#00c8d233,transparent 48%),#101116}}
.content{{position:absolute;left:64px;top:48px;width:735px}}
.brand{{display:flex;align-items:center;gap:14px;color:#fff;font-size:27px;font-weight:600}}
.content h1{{margin:66px 0 20px;color:#fff;font-size:60px;line-height:1.1;letter-spacing:-1.5px;font-weight:600;overflow-wrap:anywhere}}
.content p{{max-width:720px;font-size:26px;line-height:1.45;color:#b8c8e7}}
.tags{{position:absolute;left:64px;bottom:55px;display:flex;gap:10px}}
.tags span{{font-size:19px;padding:8px 17px;background:#ffffff14;border-radius:999px;color:#ebf4ff}}
.art{{position:absolute;right:54px;top:158px;width:300px;display:grid;gap:14px}}
.art .db-art{{height:145px;border-radius:20px;aspect-ratio:auto}}
.art .db-art:nth-child(2){{transform:translateX(-25px)}}
</style></head><body><div class="content"><div class="brand">{logo(34)}AnyAIGC</div><h1>{title} API</h1><p>{e(c['tagline'])}</p></div>
<div class="tags">{''.join(f'<span>{e(t)}</span>' for t in tags)}</div><div class="art">{art('code')}{art('flow')}</div></body></html>'''

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for slug in SLUGS:
        for lang in ('zh', 'en'):
            filename = f'{slug}-{lang}'
            (OUT / (filename + '.html')).write_text(card(lang, slug), encoding='utf-8')
            jobs.append(filename)
    capture = '''async (page) => {
  await page.setViewportSize({width:1200,height:630});
  for (const name of JOBS) {
    await page.goto('http://localhost:8765/.playwright-mcp/doubao-og/'+name+'.html');
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({path:'assets/og/'+name+'.png',scale:'css'});
  }
  console.log('Captured '+JOBS.length+' share images');
}'''.replace('JOBS', json.dumps(jobs))
    (OUT / 'capture.js').write_text(capture, encoding='utf-8')
    print(f'Prepared {len(jobs)} share cards in {OUT}')

if __name__ == '__main__':
    main()
