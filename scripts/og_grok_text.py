"""Write temporary OG HTML, capture with Playwright at 1200x630, then remove HTML."""
from grok_text_data import MODELS, HUB, SLUGS
from grok_text_pages import ROOT, logo, tr, e


def main():
    out=ROOT/'.playwright-mcp/og-grok-text'
    out.mkdir(parents=True,exist_ok=True)
    for lang in ('zh','en'):
        for slug in SLUGS:
            m=MODELS['grok-4.7' if slug==HUB else slug]
            name='Grok 4.x' if slug==HUB else m['name']
            sub=tr(lang,'为编程、智能体与知识工作而构建。','Built for coding, agents, and knowledge work.') if slug==HUB else m[lang][2]
            price='0.0993' if slug==HUB else m['prices'][0]
            fs=64 if len(name)>20 else 82
            s=f'''<!doctype html><html lang="{'zh-CN' if lang=='zh' else 'en'}"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}}body{{width:1200px;height:630px;margin:0;background:#fff;color:#0a0a0a;font-family:Arial,"Microsoft YaHei",sans-serif;position:relative;overflow:hidden}}.top{{position:absolute;left:64px;right:64px;top:45px;display:flex;align-items:center;justify-content:space-between;font-size:24px;letter-spacing:-.6px}}.brand{{font-weight:700}}.top small{{font:13px Consolas,monospace;color:#777;letter-spacing:1.5px}}.mark{{position:absolute;right:72px;top:145px;border:1px solid #deddd9;border-radius:32px;padding:35px;background:#f7f7f5}}.mark svg{{width:120px;height:120px}}h1{{position:absolute;left:64px;top:157px;margin:0;max-width:920px;font-size:{fs}px;line-height:1.15;font-weight:400;letter-spacing:-3px}}h1 span{{display:block;font-size:45px;margin-top:7px;letter-spacing:-1px;color:#777}}p{{position:absolute;left:64px;top:331px;font-size:29px;margin:0;max-width:1000px;line-height:1.5;font-weight:400}}.tags{{position:absolute;left:64px;bottom:65px;display:flex;gap:12px;align-items:center}}.tags span{{font-size:18px;border:1px solid #d7d6d1;border-radius:999px;padding:13px 21px;white-space:nowrap}}.tags .price{{background:#0a0a0a;color:#fff;border-color:#0a0a0a}}.rule{{position:absolute;left:64px;right:64px;bottom:30px;height:1px;background:#deddd9}}
</style></head><body><div class="top"><span class="brand">AnyAIGC <span style="font-weight:400;color:#777">/ Grok</span></span><small>TEXT & CODE / API</small></div>{'<div class="mark">'+logo()+'</div>' if len(name)<22 else ''}<h1>{e(name)}<span>API</span></h1><p>{e(sub)}</p><div class="tags"><span class="price">${price} / 1M {tr(lang,'输入起','input')}</span><span>{tr(lang,'并发不限','Unlimited concurrency')}</span><span>{tr(lang,'对公 · 专票','Contracts · invoices')}</span></div><div class="rule"></div></body></html>'''
            s=s.replace('<span class="brand">AnyAIGC', '<span class="brand" style="display:flex;align-items:center;gap:10px">'+logo()+'AnyAIGC')
            s=s.replace('.brand{font-weight:700}', '.brand{font-weight:700}.brand svg{width:25px;height:25px}')
            (out/f'{slug}-{lang}.html').write_text(s,encoding='utf-8')
    print('Wrote 18 temporary OG HTML files.')


if __name__=='__main__':
    main()
