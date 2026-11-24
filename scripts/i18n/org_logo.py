# 把专题页 JSON-LD 里 Organization.logo 从旧的 /logo.webp（256×256 复古手写版）换成新 logo 的 512×512 方形版。
# 用法：python scripts/i18n/org_logo.py [--dry-run]    重复运行结果不变。
# 专题首页（*/models/index.html）没有 Organization，不碰。
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OLD = 'https://www.anyaigc.ai/logo.webp'
NEW = 'https://www.anyaigc.ai/assets/home/logo-512.png'
dry = '--dry-run' in sys.argv
n = files = 0
bad = []
for f in sorted(glob.glob(os.path.join(ROOT, '*', 'models', '*.html'))):
    if os.path.basename(f) == 'index.html':
        continue
    t = io.open(f, encoding='utf-8').read()
    c = t.count(OLD)
    if not c:
        continue
    t2 = t.replace(OLD, NEW)
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t2, re.S):
        try:
            json.loads(blk)
        except Exception:
            bad.append(f)
    if not dry:
        io.open(f, 'w', encoding='utf-8', newline='\n').write(t2)
    n += c
    files += 1
print(('将替换' if dry else '已替换'), n, '处，', files, '页；JSON-LD 不合法：', bad[:3])
