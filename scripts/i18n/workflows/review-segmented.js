export const meta = {
  name: 'i18n-review-segmented',
  description: '按 id 段并行复核：每种语言 N 段，每段一个独立复核代理，只写补丁文件 <lang>-rev-<seg>.json，不碰 all.json',
  phases: [{ title: 'Review', detail: '4 种语言 × 分段并行复核' }],
}

// args: { series, total, segs, brief, desc, refs: [series...], extra: 本批特有的检查点（字符串） }
const SERIES = args.series
const TOTAL = args.total
const SEGS = args.segs
const BRIEF = args.brief
const DESC = args.desc
const REFS = args.refs
const EXTRA = args.extra || ''
const DIR = `drafts/i18n/${SERIES}`
const size = Math.ceil(TOTAL / SEGS)
const SEGLIST = Array.from({ length: SEGS }, (_, i) => ({ seg: `s${i}`, a: i * size, b: Math.min(TOTAL, (i + 1) * size) }))
const LANGS = [
  { code: 'ja', name: '日语', rules: 'APIキー（不带空格）；「コンテキスト長1M」；原文没有 about / ~ 的百分比不要加「約」；同一概念全文只用一个词（「提供終了」「非推奨」不要混用）；价格表述与已复核系列一致；不要夹杂其他语言（曾出现德语残留）。' },
  { code: 'ko', name: '韩语', rules: '敬体统一「~하세요」，疑问句统一「~입니까/합니까」；list price 统一「공식 정가」；「300+」统一「300개 이상」；WeChat Pay / Alipay 用英文名；带波浪线的「~12%」用「약」。' },
  { code: 'es', name: '西班牙语', rules: 'Enterprise=Empresas、Business=Negocios；petición 全文统一（不要 solicitud）；「~12%」译「aproximadamente el 12 %」；小数逗号；vídeo 带重音；billion 统一写「mil millones」。' },
  { code: 'de', name: '德语', rules: '统一 Sie；复合词连写；「~12%」译「rund 12 %」；小数逗号；Anfrage 全文统一；按钮和短标签 ≤ 28 个字符；billion 统一写「Milliarden」。' },
]
const REVIEW = {
  type: 'object',
  properties: {
    lang: { type: 'string' }, seg: { type: 'string' }, fixed: { type: 'number' }, validateErrors: { type: 'number' },
    issues: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, kind: { type: 'string' }, note: { type: 'string' } }, required: ['id', 'kind', 'note'] } },
    unresolved: { type: 'array', items: { type: 'string' } },
  },
  required: ['lang', 'seg', 'fixed', 'validateErrors'],
}

const refList = (L) => REFS.map(r => `drafts/i18n/${r}/out/${L.code}-all.json`).join('、')

const prompt = (L, S) => `你是${L.name}的独立复核人，没有参与翻译。你只负责 ${DIR}/union.json 里下标 [${S.a}, ${S.b}) 的条目（共 ${S.b - S.a} 条，段名 ${S.seg}）。其他段由别的复核人同时在做，不要碰。

读取：${DIR}/union.json（每项 {id,text,role,pages}，取下标 ${S.a} 到 ${S.b - 1}）和对应译文 ${DIR}/out/${L.code}-all.json（只读，按 id 对应）。先读 ${BRIEF}。同一语言里已复核的译文在 ${refList(L)}（只读），用词和语气必须与它们一致。这批是${DESC}。

**输出方式：只把需要修改的条目写进补丁文件 ${DIR}/out/${L.code}-rev-${S.seg}.json**，格式是 JSON 数组 [{"id": "...", "text": "改后的译文"}]，只含你改过的 id，且 id 必须在你的下标范围内。不要修改 ${L.code}-all.json，不要运行 consolidate、tm-fill、tm-save、render、register、prepare、tm-chunks、resync、merge_patches，不要删除或移动任何文件，不要写辅助脚本批量改写。每检查约 120 条就保存一次补丁文件，不要最后一次性写。

重点检查：
- 一致性：${L.rules}
- 简报术语表全文只用一个译法；型号名、模型 ID、分辨率保持英文。
- 标题 ≤ ${L.code === 'ja' || L.code === 'ko' ? '64 显示宽度（汉字假名谚文各算 2）' : '65 字符'}；description ${L.code === 'ja' || L.code === 'ko' ? '60–240 宽度' : '120–160 字符'}，超长的精简并保留“自助开票”；同一个页面的 title / og:title / twitter:title / ld:name 写法一致。
- 英文原文里价格列表和 “See the catalog for live prices.” 之间常缺句号，译文应自然断句（日语「。」）。
${EXTRA}

再从五个角度逐项检查并改正：
- fact：价格、数字、模型 ID、折扣百分比、参数、接口路径与英文逐项一致；没有新增或漏掉的事实、承诺（没有 SLA、中国大陆访问、海外信用卡、增值税、对公转账、合同）。
- context：像${L.name}母语者写的开发者文档，不是翻译腔；语气、敬体、称呼全文一致；标题和描述里有当地开发者会搜的词。
- term：与简报术语表一致；同一概念全文只用一个词。
- residue：没有漏译整句、中文、其他语言残留、机翻痕迹；检查是否还有与英文原文逐字相同的长句（品牌名、模型 ID、代码、URL 除外）。
- structure：标签、占位符、<code> 与原文一致。

写完补丁后运行：python scripts/i18n/check_patch.py ${SERIES} ${L.code} ${S.seg} ${S.a} ${S.b}
ERROR 必须为 0（“与原文完全相同”的提醒可忽略）；有 ERROR 就改补丁文件再跑。没有任何要改的条目时写空数组 []。
**最后一步必须调用 StructuredOutput** 返回：lang、seg、fixed（补丁里的条数）、validateErrors、issues（每处 {id, kind∈fact|context|term|residue|structure, note}，最多 25 条代表性的）、unresolved（真正需要人判断的，最多 5 条）。`

phase('Review')
const jobs = []
const ONLY = args.only ? new Set(args.only) : null  // 例如 ["ja-s0","de-s1"]：只跑这几段
for (const L of LANGS) for (const S of SEGLIST) if (!ONLY || ONLY.has(`${L.code}-${S.seg}`)) jobs.push(() => agent(prompt(L, S), { label: `review:${SERIES}:${L.code}-${S.seg}`, phase: 'Review', schema: REVIEW }))
const out = await parallel(jobs)
return out.filter(Boolean)
