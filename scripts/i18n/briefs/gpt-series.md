# GPT 系列翻译简报（ja / ko / es / de）

## 这个系列是什么
AnyAIGC（API 聚合平台）的 OpenAI GPT 专题页，共 17 页：
- **文本模型**：GPT-5.5、GPT-5.5 Pro、GPT-5.6（Luna / Sol / Terra）、GPT-6（Luna / Sol / Astra）、GPT-6.1（Sol / Terra），外加一个总览页 `gpt`。
- **图像模型**：GPT Image 2、GPT Image 2.5 / 2.6（Flare / Sunburst），外加总览页 `gpt-image`。
读者是开发者，要看价格、两种接口（`/v1/chat/completions`、`/v1/responses`）、推理强度（reasoning effort）、缓存计费、图像生成和编辑。价格是 OpenAI 官方价（list price）的一个折扣比例。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、OpenAI、GPT、ChatGPT、Codex、Claude、Gemini、Anthropic、Google
- 型号名与代号：GPT-5.5 Pro、GPT-6.1 Sol / Terra、GPT-6 Astra / Luna、GPT Image 2.5 Flare / Sunburst 等，包括 Sol、Terra、Luna、Astra、Flare、Sunburst
- 模型 ID 与接口路径：gpt-5.5-pro、gpt-image-2 等；`/v1/chat/completions`、`/v1/responses`、`/v1/images/generations`、`/v1/images/edits`；参数名（reasoning_effort、max_output_tokens、stream、quality、size、n、mask、model、base_url 等）
- 推理强度的取值：low / medium / high / xhigh 保持英文，放在 `<code>` 或原样出现
- 所有代码、命令、JSON 字段、URL、环境变量；价格、百分比、倍数、数字一个都不能改；货币保持 USD / $
- 基准测试名（SWE-bench、GPQA 等）保持英文

## 已确认的译法（四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay。敬体统一「~하세요」，疑问句统一「~입니까/합니까」。list price 译「공식 정가」。「300+」译「300개 이상」。「~12%」这类带波浪线的用「약」。
- **西语**：Business 译 Negocios，Enterprise 译 Empresas。请求统一 petición（不用 solicitud）。「~12%」译「aproximadamente el 12 %」，不要丢掉“约”。
- **日语**：APIキー（不带空格）。英文原文没有 about / ~ / approximately 的地方，不要加「約」，写「定価の12%」。原文有 ~ 的才用「約」。「1Mコンテキスト」统一写「コンテキスト長1M」。
- **德语**：统一用 Sie；复合词连写；「~12%」译「rund 12 %」。Anfrage（请求）全文统一。
- 折扣百分比保留英文页数字，不换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问、海外信用卡；不写增值税/对公转账/签合同。发票只写“在控制台自助开具”。原文没有的承诺不要添加。

## 术语（与 DeepSeek / Claude / 第 1 批已复核译文一致，全文只用一个词）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| tokens | トークン | 토큰 | tokens | Tokens |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| context window / 1M context | コンテキスト長 | 컨텍스트 길이 | ventana de contexto | Kontextfenster |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price（OpenAI 官方定价） | 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| cached input / cache hit | キャッシュ入力 / キャッシュヒット | 캐시 입력 / 캐시 히트 | entrada en caché / acierto de caché | zwischengespeicherte Eingabe / Cache-Treffer |
| reasoning effort | 推論の強度（reasoning effort） | 추론 강도(reasoning effort) | nivel de razonamiento (reasoning effort) | Reasoning-Aufwand (reasoning effort) |
| streaming | ストリーミング | 스트리밍 | streaming | Streaming |
| function calling / tool calling | 関数呼び出し / ツール呼び出し | 함수 호출 / 도구 호출 | llamada a funciones / a herramientas | Funktionsaufrufe / Tool-Aufrufe |
| structured output | 構造化出力 | 구조화된 출력 | salida estructurada | strukturierte Ausgabe |
| computer use | コンピュータ操作（computer use） | 컴퓨터 사용(computer use) | uso del ordenador (computer use) | Computer Use |
| concurrency / unlimited concurrency | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| image generation / image edit / inpainting | 画像生成 / 画像編集 / インペイント | 이미지 생성 / 이미지 편집 / 인페인팅 | generación de imágenes / edición / inpainting | Bildgenerierung / Bildbearbeitung / Inpainting |
| per image | 1枚あたり | 이미지당 | por imagen | pro Bild |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| legacy（旧世代，仍可用） | 旧世代 | 이전 세대 | generación anterior | ältere Generation |
| deprecated / retired | 非推奨 / 提供終了 | 지원 중단 / 종료 | obsoleto / retirado | veraltet / eingestellt |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词。
- 标题和描述里要有当地开发者会搜的词：日语「GPT-5.5 API 料金」；韩语「GPT-5.5 API 가격」；西语「API de GPT-5.5 precio」；德语「GPT-5.5 API Preise」。保留模型名 + API + 价格这个核心。
- 数字格式：德语、西语小数点用逗号（0,0119），日语、韩语保持 0.0119。
- <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，并提到发票（自助开票）。
- 页面里的"Newer models are available…"这类提示讲的是 OpenAI 已发布更新的型号，照原意翻，不要加原文没有的结论。

## 日本（ja）
敬体（です・ます）。「トークン」「コンテキスト」已是通用说法，不必再解释。

## 韩国（ko）
합니다体，技术文档语气。价格、计费用「요금」「과금」。

## 西班牙（es）
通用西班牙语，不用西班牙或拉美特有说法。用无人称或统一的 tú，全文一致。

## 德国（de）
标准德语，用 "Sie"。价格用「Preis」，计费用「Abrechnung」。
