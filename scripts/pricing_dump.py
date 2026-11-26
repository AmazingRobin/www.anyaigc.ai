# 把模型广场（https://anyaigc.ai/pricing）所有模型的价格拉下来，存成 drafts/pricing.json，之后查价格直接读这个文件。
# 用法：
#   python scripts/pricing_dump.py                 重新拉取并写 drafts/pricing.json
#   python scripts/pricing_dump.py gpt-image       按模型名子串查价格（读本地文件，不联网）
#   python scripts/pricing_dump.py --group Codex   查看某个分组的倍率
# 价格口径（与模型广场详情弹窗一致，2026-11-25 用 gpt-image-2.5-sunburst 核对过）：
#   按量计费（quota_type=0）：输入 = model_ratio × 2 × 分组倍率（美元 / 100 万 Token）
#       输出 = 输入 × completion_ratio；缓存命中 = 输入 × cache_ratio；图片输入 = 输入 × image_ratio；图片缓存 = 输入 × image_cache_ratio
#   按次计费（quota_type=1）：单价 = model_price × 分组倍率（美元 / 次）
#   “最低价” = 该模型可用分组（enable_groups）里倍率最低的那一档，与模型广场卡片显示的价格一致。
# 取整：按量价、按次价都取 4 位小数。用 gpt-image-2.5-sunburst 的弹窗逐项核对：除 Codex-Gpt-2 分组的输出价外都一致，
#   该项弹窗显示 $2.4710，这里算出 $2.4709（差 0.0001，弹窗用的倍率精度比 /api/pricing 返回的更细）。页面上写的价格以弹窗显示为准。
#   视频、音频等带 step_ratios / video_resolution_ratios 的模型，分档倍率保留在 raw 里，lowest 只是基础价。
import io
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'drafts', 'pricing.json')
URL = 'https://anyaigc.ai/api/pricing'
RMB_RATE = 6.7   # 用户 2026-11-25 指定：页面上按张价格 × 6.7 换算成人民币


def r4(x):
    """按次价：4 位小数（$0.0165）"""
    return round(x + 1e-12, 4)


def sig4(x):
    """按量价：也取 4 位小数（弹窗显示 $24.7060 / $0.4118）"""
    return round(x + 1e-12, 4)


def fetch(tries=4):
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (pricing_dump)'})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:   # SSL 握手偶尔失败，等几秒重试
            if i == tries - 1:
                raise
            print(f'拉取失败（{type(e).__name__}），{3 * (i + 1)} 秒后重试 {i + 2}/{tries}')
            time.sleep(3 * (i + 1))


def prices(m, ratio):
    """某个模型在某个分组倍率下的美元价格"""
    if m.get('quota_type') == 1:
        return {'per_call': r4(m['model_price'] * ratio)}
    base = m['model_ratio'] * 2 * ratio
    p = {'input': sig4(base), 'output': sig4(base * m.get('completion_ratio', 1))}
    for key, field in (('cache_hit', 'cache_ratio'), ('image_input', 'image_ratio'), ('image_cache', 'image_cache_ratio'),
                       ('audio_input', 'audio_ratio')):
        if m.get(field):
            p[key] = sig4(base * m[field])
    return p


def build(j):
    gr = j['group_ratio']
    vendors = {v['id']: v.get('name') for v in j['vendors']} if isinstance(j['vendors'], list) else {}
    models = {}
    for m in sorted(j['data'], key=lambda x: x['model_name']):
        groups = [(g, gr[g]) for g in m.get('enable_groups', []) if g in gr]
        groups.sort(key=lambda x: x[1])
        by_group = {g: prices(m, r) for g, r in groups}
        low = groups[0] if groups else None
        entry = {
            'vendor': vendors.get(m.get('vendor_id')),
            'type': m.get('model_type'),
            'billing': 'per_call' if m.get('quota_type') == 1 else 'per_token',
            'lowest_group': low[0] if low else None,
            'lowest': by_group[low[0]] if low else None,
            'by_group': by_group,
            'endpoints': m.get('supported_endpoint_types'),
            'raw': {k: m[k] for k in ('model_ratio', 'model_price', 'completion_ratio', 'cache_ratio', 'image_ratio',
                                      'image_cache_ratio', 'audio_ratio', 'audio_completion_ratio', 'cache_creation_ratio',
                                      'step_ratios', 'video_resolution_ratios', 'official_price') if k in m},
            'description': m.get('description'),
        }
        if entry['billing'] == 'per_call' and entry['lowest']:
            entry['lowest_cny'] = r4(entry['lowest']['per_call'] * RMB_RATE)
        models[m['model_name']] = entry
    return {
        'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'source': 'https://anyaigc.ai/pricing',
        'api': URL,
        'unit': 'USD；按量计费为每 100 万 Token，按次计费为每次',
        'rmb_rate': RMB_RATE,
        'models': models,
        'group_ratio': gr,
    }


def load():
    return json.load(io.open(OUT, encoding='utf-8'))


def show(name, e):
    low = e['lowest'] or {}
    if e['billing'] == 'per_call':
        s = f"按次 ${low.get('per_call')} / 次（约 ¥{e.get('lowest_cny')}）"
    else:
        s = ' '.join(f'{k}=${v}' for k, v in low.items())
    print(f"{name:34s} {e['vendor'] or '-':12s} {e['lowest_group'] or '-':16s} {s}")


def main():
    a = sys.argv[1:]
    if a and a[0] == '--group':
        gr = load()['group_ratio']
        for g, r in sorted(gr.items(), key=lambda x: x[1]):
            if len(a) < 2 or a[1].lower() in g.lower():
                print(f'{g:26s} x{r:.4f}')
        return
    if a:
        d = load()
        print(f"数据时间 {d['fetched_at']}（价格单位 USD）")
        hit = [(n, e) for n, e in d['models'].items() if any(q.lower() in n.lower() for q in a)]
        for n, e in hit:
            show(n, e)
        print(f'共 {len(hit)} 个')
        return
    d = build(fetch())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, ensure_ascii=False, indent=1))
    per_call = sum(1 for e in d['models'].values() if e['billing'] == 'per_call')
    print(f"已写入 {OUT}：{len(d['models'])} 个模型（按次 {per_call}，按量 {len(d['models']) - per_call}），{len(d['group_ratio'])} 个分组")


if __name__ == '__main__':
    main()
