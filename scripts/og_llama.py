"""Generate temporary 1200x630 HTML cards for Playwright rasterization.

Run python scripts/og_llama.py, screenshot at 1200x630 through preview.py,
then remove .playwright-mcp/llama-og. No image-generation service is used.
"""
from html import escape
from pathlib import Path
from llama_data import BY_ID, SLUGS
from llama_pages import deal, mark

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'.playwright-mcp/llama-og'
CSS = '''
*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;background:#fff;color:#171717}
.brand{position:absolute;left:64px;top:43px;display:flex;gap:18px;align-items:center;font-size:24px;font-weight:600;letter-spacing:-.5px}.brand span{color:#888;font-size:16px;font-weight:400}
.mark{position:absolute;right:76px;top:187px;width:170px;height:170px}
.main{position:absolute;left:64px;top:157px;width:850px}.eyebrow{font:12px Consolas,monospace;letter-spacing:2px;color:#777;margin:0 0 24px}
h1{font-size:61px;font-weight:550;line-height:1.12;letter-spacing:-2.2px;max-width:830px;margin:0 0 22px;text-wrap:balance}h1.long{font-size:52px;max-width:790px}
.sub{font-size:24px;color:#666;margin:0;max-width:820px;line-height:1.4}.deal{display:inline-block;margin-top:26px;background:#171717;color:white;font-size:20px;padding:10px 23px;border-radius:999px}
.bottom{position:absolute;bottom:0;left:0;right:0;border-top:1px solid #e6e6e6;padding:28px 64px;display:flex;align-items:center;gap:26px;font-size:17px;color:#737373}.bottom b{color:#171717;font-weight:550}.bottom span:last-child{margin-left:auto}
'''


def page(lang,slug):
    model = BY_ID.get(slug)
    zh = lang == 'zh'
    name = (model['name'] if model else 'Llama') + ' API'
    sub = model['tag_'+lang] if model else ('12 个型号，一个 API Key。' if zh else '12 models. One API key.')
    price = model['input'] if model else '0.3375'
    return f'''<!DOCTYPE html><html lang="{'zh-CN' if zh else 'en'}"><head><meta charset="UTF-8"><title>{name}</title><style>{CSS}</style></head><body>
<div class="brand">AnyAIGC <span>× Llama</span></div><div class="mark">{mark(170)}</div>
<div class="main"><p class="eyebrow">META LLAMA · OLLAMA COLLECTION</p><h1 class="{'long' if len(name)>23 else ''}">{escape(name)}</h1><p class="sub">{escape(sub)}</p><div class="deal">{deal(lang,model)}</div></div>
<div class="bottom"><b>{'输入' if zh else 'Input'} ${price} / 1M tokens</b><span>{'并发不限' if zh else 'Unlimited concurrency'}</span><span>{'对公 · 专票' if zh else 'VAT invoices'}</span><span>www.anyaigc.ai</span></div></body></html>'''


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    for lang in ('zh','en'):
        for slug in SLUGS:
            (OUT/f'{slug}-{lang}.html').write_text(page(lang,slug),encoding='utf-8')
    print('Prepared 26 sharing cards in', OUT)
