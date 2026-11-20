# 统计一个工作流里各阶段的耗时：每个代理的开始/结束时间来自它的对话记录（agent-*.jsonl 的 timestamp）。
# 用法：python scripts/i18n/wf_timing.py <工作流目录名>      例：wf_5d7e3db4-00b
import collections, datetime, glob, io, json, os, sys
BASE = r'C:\Users\yijia\.claude\projects\c--Users-yijia-Documents-GitHub-www-anyaigc-ai\44efc830-e873-441d-9d8f-047800f57aed\subagents\workflows'
d = os.path.join(BASE, sys.argv[1])
def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
rows = []
for mf in glob.glob(os.path.join(d, 'agent-*.meta.json')):
    m = json.load(io.open(mf, encoding='utf-8'))
    jf = mf[:-10] + '.jsonl'
    if not os.path.exists(jf):
        continue
    t = [ts(json.loads(l).get('timestamp')) for l in io.open(jf, encoding='utf-8', errors='replace') if l.strip() and json.loads(l).get('timestamp')]
    if t:
        rows.append((m.get('description', ''), min(t), max(t)))
t0 = min(r[1] for r in rows)
kinds = collections.defaultdict(list)
for lab, a, b in rows:
    kinds['review' if lab.startswith('review') else 'translate'].append((lab, a - t0, b - t0, b - a))
for k, v in kinds.items():
    durs = sorted(x[3] for x in v)
    print(f'{k:9} agents={len(v):3d} | each agent: median {durs[len(durs)//2]/60:5.1f} min, max {durs[-1]/60:5.1f} min | first start {min(x[1] for x in v)/60:5.1f} min, last end {max(x[2] for x in v)/60:5.1f} min (from workflow start)')
    if k == 'review':
        for lab, a, b, dur in sorted(v):
            print(f'    {lab:12} started {a/60:5.1f}  ended {b/60:5.1f}  ({dur/60:4.1f} min)')
# 同一时刻最多有几个代理在跑
ev = sorted([(a, 1) for _, a, b in rows] + [(b, -1) for _, a, b in rows])
cur = peak = 0
for _, x in ev:
    cur += x; peak = max(peak, cur)
print('peak concurrent agents:', peak, '| total wall time:', round((max(r[2] for r in rows) - t0) / 60, 1), 'min')
