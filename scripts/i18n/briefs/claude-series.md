# Claude 系列翻译简报（ja / ko / es / de）

## 这个系列是什么
Anthropic 的 Claude 模型 API（Fable、Opus、Sonnet、Haiku 四个家族，共 11 个模型加一个系列总览页）。
页面讲的是通过 AnyAIGC 用一个 API Key 调用，走 Anthropic 原生 `/v1/messages` 接口，
价格是 Anthropic 官方定价（list price）的一个折扣比例。读者是开发者，要看价格、缓存计费、上下文长度、怎么接入 Claude Code。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、Anthropic、Claude、Claude Code、Fable、Opus、Sonnet、Haiku、Mythos、GPT、Gemini
- 模型 ID：claude-fable-5、claude-opus-5-5、claude-haiku-5-5 等一律保持原文
- 所有代码、命令、JSON 字段、URL、请求头、环境变量（ANYAIGC_API_KEY 等）、参数名（max_tokens、tool_choice、thinking 等）
- 价格、百分比、倍数、token 数量里的数字一个都不能改；货币保持 USD / $
- 版本号、基准测试名（SWE-bench 等）保持英文

## 已确认的译法（2026-11-18，四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay，不要音译。
- **西语**：Business 译 Negocios；Enterprise 译 Empresas。两者不能用同一个词。
- **日语**：英文原文没有 about / ~ / approximately 的地方，不要加「約」。原文写 "76% off" 就是「76%オフ」。
- 折扣百分比：保留英文页里的数字，不要换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问。原文里没有的承诺不要添加。

## 术语（与 DeepSeek 系列一致，四种语言统一用这些）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| tokens | トークン | 토큰 | tokens | Tokens |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| context window / 1M context | コンテキスト長 | 컨텍스트 길이 | ventana de contexto | Kontextfenster |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price（Anthropic 官方定价） | 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| cache hit / cache write | キャッシュヒット / キャッシュ書き込み | 캐시 히트 / 캐시 쓰기 | acierto de caché / escritura en caché | Cache-Treffer / Cache-Schreibvorgang |
| prompt caching | プロンプトキャッシュ | 프롬프트 캐싱 | caché de prompts | Prompt-Caching |
| concurrency / unlimited concurrency | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| long-running agents | 長時間実行のエージェント | 장시간 실행 에이전트 | agentes de larga duración | langlaufende Agenten |
| sub-agent | サブエージェント | 서브 에이전트 | subagente | Sub-Agent |
| tool use | ツール利用 | 도구 사용 | uso de herramientas | Tool-Nutzung |
| computer use | コンピュータ操作（computer use） | 컴퓨터 사용(computer use) | uso del ordenador (computer use) | Computer Use |
| adaptive thinking / extended thinking | アダプティブシンキング / 拡張思考 | 적응형 사고 / 확장 사고 | razonamiento adaptativo / razonamiento extendido | adaptives Denken / erweitertes Denken |
| effort | 推論の強度（effort） | 추론 강도(effort) | nivel de esfuerzo (effort) | Aufwandsstufe (effort) |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| legacy（旧世代、仍可用） | 旧世代 | 이전 세대 | generación anterior | ältere Generation |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词。
- 标题和描述里要有当地开发者会搜的词：日语「Claude API 料金」、韩语「Claude API 가격」、西语「API de Claude precio」、德语「Claude API Preise」。保留模型名 + API + 价格这个核心。
- 数字格式：德语、西语小数点用逗号（0,1215），千分位用窄空格或点；日语、韩语保持 0.1215。
- 标题 <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，且要点到发票（自助开票）。

## 日本（ja）
- 敬体（です・ます）。「トークン」「コンテキスト」已是通用说法，不必再解释。

## 韩国（ko）
- 합니다体，技术文档语气，不口语化。价格、计费用「요금」「과금」。

## 西班牙（es）
- 通用西班牙语，不用西班牙或拉美特有说法。用无人称或统一的 tú，全文一致。

## 德国（de）
- 标准德语，用 "Sie"。复合词连写。价格用「Preis」，计费用「Abrechnung」。
