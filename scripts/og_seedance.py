"""Create 1200x630 share cards through temporary HTML and Playwright CLI.

Start scripts/preview.py first. Temporary HTML stays in .playwright-mcp/og/seedance.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path
from seedance_data import ROOT, SLUGS, MODELS
from seedance_pages import logo


def main():
    out = Path(ROOT) / '.playwright-mcp' / 'og' / 'seedance'
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for slug in SLUGS:
        overview = slug == 'seedance'
        model = MODELS.get(slug)
        name = 'Seedance' if overview else model['name']
        price = '1.843' if overview else model['min']
        for lang in ('zh', 'en'):
            zh = lang == 'zh'
            subtitle = (f'多模态视频生成 · ${price} / 1M tokens 起' if zh else f'Multimodal video · from ${price} / 1M tokens')
            tags = ['四个型号', '音画同步', '并发不限', '对公 · 专票'] if zh else ['4 models', 'Native audio', 'Unlimited concurrency', 'VAT invoices']
            if not overview:
                tags[0] = {'doubao-seedance-2-5': '30 秒长叙事' if zh else '30-second stories',
                           'doubao-seedance-2-0': '全模态参考' if zh else 'Multimodal references',
                           'doubao-seedance-2-0-fast': '更快生成' if zh else 'Faster generation',
                           'doubao-seedance-2-0-mini': '高频与规模化' if zh else 'High-frequency workloads'}[slug]
                if slug == 'doubao-seedance-2-0-mini':
                    tags[1] = '按 tokens 计费' if zh else 'Token-based billing'
                    subtitle = f'高频视频生成 · ${price} / 1M tokens 起' if zh else f'High-frequency video · from ${price} / 1M tokens'
            h = f'''<!doctype html><html lang="{'zh-CN' if zh else 'en'}"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}}body{{width:1200px;height:630px;margin:0;overflow:hidden;background:{'#f8f8f8' if overview else '#0e1014'};color:{'#212121' if overview else '#fff'};font-family:Arial,"Microsoft YaHei",sans-serif}}
.glow{{position:absolute;inset:0;background:radial-gradient(ellipse at 90% 10%,{'#dae7fa' if overview else '#363543'},transparent 65%)}}
.logo{{position:absolute;left:66px;top:54px;display:flex;align-items:center;gap:12px;font-size:24px;font-weight:600}}.logo i{{height:22px;width:1px;background:#9599a2;margin:0 8px}}.logo span{{font-size:20px;font-weight:400;opacity:.6}}
.title{{position:absolute;left:66px;top:188px;width:850px}}h1{{font-size:{78 if len(name)<18 else 68}px;font-weight:600;letter-spacing:-3px;line-height:1.05;margin:0}}h1 span{{display:block;font-size:46px;font-weight:400;letter-spacing:-1px;margin-top:13px}}p{{font-size:27px;line-height:1.5;margin:26px 0 0;opacity:.68}}
.tags{{position:absolute;left:66px;bottom:66px;display:flex;gap:10px}}.tags span{{font-size:18px;padding:10px 17px;border:1px solid {'#d1d4db' if overview else '#646771'};border-radius:999px}}
.orb{{position:absolute;right:-120px;top:100px;width:420px;height:420px;border-radius:50%;border:1px solid {'#a4afc5' if overview else '#8c827d'};background:radial-gradient(circle at 25% 20%,{'#78e6dc' if overview else '#b8a18c'},transparent 55%);opacity:.45;transform:rotate(-25deg) scaleX(.75)}}
</style></head><body><div class="glow"></div><div class="orb"></div><div class="logo">{logo(32)} AnyAIGC<i></i><span>ByteDance Seed</span></div><div class="title"><h1>{name}<span>Video API</span></h1><p>{subtitle}</p></div><div class="tags">{''.join('<span>'+x+'</span>' for x in tags)}</div></body></html>'''
            filename = slug + '-' + lang
            (out / (filename + '.html')).write_text(h, encoding='utf-8')
            jobs.append({'url': f'http://127.0.0.1:8765/.playwright-mcp/og/seedance/{filename}.html',
                         'path': str(Path(ROOT) / 'assets' / 'og' / (filename + '.png'))})
    runner = out / 'render.js'
    runner.write_text('async (page) => { await page.setViewportSize({width:1200,height:630}); const jobs=' + json.dumps(jobs) + '; for(const job of jobs){await page.goto(job.url);await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:job.path});} return {rendered:jobs.length}; }', encoding='utf-8')
    cli = shutil.which('npx.cmd' if os.name == 'nt' else 'npx')
    assert cli, 'npx is required'
    subprocess.run([cli, '--yes', '--package', '@playwright/cli', 'playwright-cli', '-s=seedance-og', 'open', 'about:blank'], check=True, cwd=ROOT)
    try:
        subprocess.run([cli, '--yes', '--package', '@playwright/cli', 'playwright-cli', '-s=seedance-og', 'run-code', '--filename', str(runner)], check=True, cwd=ROOT)
    finally:
        subprocess.run([cli, '--yes', '--package', '@playwright/cli', 'playwright-cli', '-s=seedance-og', 'close'], cwd=ROOT)


if __name__ == '__main__':
    main()
