"""Create temporary HTML for 1200x630 Playwright share-image captures."""
import json
from pathlib import Path
from qwen_media_data import MODELS, price_label
from qwen_pages import logo
from html import escape

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'.playwright-mcp/qwen-media-og'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    captures=[]
    for lang in ('zh','en'):
        for m in MODELS:
            name=m['name'];dark=m['kind']!='image';title=escape(name)
            label=('图像 API' if m['kind']=='image' else '实时音视频 API' if m['kind']=='realtime' else '视频 API') if lang=='zh' else ('IMAGE API' if m['kind']=='image' else 'REAL-TIME API' if m['kind']=='realtime' else 'VIDEO API')
            sub=escape(m['lead'][lang=='en']);price=escape(price_label(m,lang));filename=f'{m["slug"]}-{lang}'
            size=64 if len(name)<30 else 56
            template=f'''<!doctype html><html lang="{lang}"><meta charset="utf-8"><style>
*{{box-sizing:border-box}}html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:{'#10131d' if dark else '#fff'};color:{'#fff' if dark else '#1d1d1f'};font-family:system-ui,"Segoe UI","Microsoft YaHei",sans-serif}}
body:before{{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 100% 0,{'#343077' if dark else '#e9edff'},transparent 60%);z-index:0}}main{{position:absolute;inset:18px;padding:54px 64px;display:flex;flex-direction:column;border:1px solid {'#ffffff30' if dark else '#e2e6f2'};z-index:1}}
header{{display:flex;align-items:center;justify-content:space-between}}.brand{{font-size:27px;font-weight:700}}.kind{{font:14px ui-monospace,monospace;color:{'#48dbe4' if dark else '#082dff'};letter-spacing:.13em}}.logo{{margin-top:34px}}svg{{width:40px;height:40px;{'filter:brightness(0) invert(1)' if dark else ''}}}h1{{font-size:{size}px;line-height:1.12;letter-spacing:-.04em;margin:18px 0;max-width:1030px;overflow-wrap:anywhere}}p{{font-size:25px;line-height:1.4;margin:0;max-width:1020px;color:{'#bac2d8' if dark else '#657084'}}}footer{{margin-top:auto;display:flex;flex-wrap:wrap;gap:12px}}footer span{{border:1px solid {'#ffffff40' if dark else '#dbe1f3'};border-radius:999px;padding:10px 18px;font-size:18px}}footer span:first-child{{background:{'#3655f7' if dark else '#082dff'};color:#fff;border-color:transparent}}</style>
<main><header><span class="brand">AnyAIGC</span><span class="kind">{label}</span></header><div class="logo">{logo(40)}</div><h1>{title}</h1><p>{sub}</p><footer><span>{price}</span><span>{'并发不限' if lang=='zh' else 'No concurrency cap'}</span><span>{'对公 · 专票' if lang=='zh' else 'Contracts · invoices'}</span></footer></main></html>'''
            p=OUT/f'{filename}.html';p.write_text(template,encoding='utf-8')
            captures.append({'slug':m['slug'],'lang':lang,'url':f'http://localhost:8765/.playwright-mcp/qwen-media-og/{filename}.html','path':f'assets/og/{filename}.png'})
    (OUT/'manifest.json').write_text(json.dumps(captures,indent=2),encoding='utf-8')
    print(f'Created {len(captures)} share-image HTML sources and manifest.')


if __name__=='__main__':main()
