# Grok 系列翻译简报（ja / ko / es / de）

## 这个系列是什么
AnyAIGC（API 聚合平台）的 xAI Grok 专题页，共 17 页，分三组：
- **文本与代码模型**：Grok 4（4.20 Reasoning / Non-Reasoning、4.3、4.5、4.6、4.7）、Grok Build 0.1，外加总览页 `grok-4.x` 和 `grok-4`。
- **图像模型**：Grok Imagine Image（含 2.0、Quality），外加总览页 `grok-image`。
- **视频模型**：Grok Imagine Video（含 1.5 Lite、1.5 Preview），外加总览页 `grok-video`。
读者是开发者，要看价格、上下文长度、推理与非推理型号的区别、工具调用、图像宽高比与分辨率档位、视频时长与按秒计费。价格是 xAI 官方价（list price）的一个折扣比例，或者直接给出按 token / 按张 / 按秒的价格。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、xAI、Grok、Grok Imagine、Grok Build、Claude、GPT、Gemini
- 型号名与代号：Grok 4.20 Reasoning、Grok 4.3、Grok Imagine Image 2.0、Quality、Lite、Preview 等（Lite、Preview、Quality 在型号名里保持英文）
- 模型 ID 与接口路径：grok-4.3、grok-imagine-image-2.0、grok-imagine-video-1.5-lite 等；`/v1/chat/completions`、`/v1/images/generations`、`/v1/videos/...`；参数名（model、n、aspect_ratio、resolution、duration、max_tokens 等）
- 分辨率与宽高比：1k / 1.5k / 2k、720p、16:9 等原样保留
- 所有代码、命令、JSON 字段、URL、环境变量；价格、百分比、倍数、数字一个都不能改；货币保持 USD / $
- 页面里的 `{{0}}` 之类占位符（logo 图标）原样保留

## 已确认的译法（四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay。敬体统一「~하세요」，疑问句统一「~입니까/합니까」。list price 译「공식 정가」。「300+」译「300개 이상」。「~12%」这类带波浪线的用「약」。
- **西语**：Business 译 Negocios，Enterprise 译 Empresas。请求统一 petición（不用 solicitud）。「~12%」译「aproximadamente el 12 %」，不要丢掉“约”。
- **日语**：APIキー（不带空格）。英文原文没有 about / ~ / approximately 的地方，不要加「約」，写「定価の12%」。原文有 ~ 的才用「約」。「1Mコンテキスト」统一写「コンテキスト長1M」。
- **德语**：统一用 Sie；复合词连写；「~12%」译「rund 12 %」。Anfrage（请求）全文统一。
- 折扣百分比保留英文页数字，不换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问、海外信用卡；不写增值税/对公转账/签合同。发票只写“在控制台自助开具”。原文没有的承诺不要添加。

## 术语（与 DeepSeek / Claude / 第 1 批 / GPT 已复核译文一致，全文只用一个词）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| tokens | トークン | 토큰 | tokens | Tokens |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| context window / 1M context | コンテキスト長 | 컨텍스트 길이 | ventana de contexto | Kontextfenster |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price（xAI 官方定价） | 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| reasoning / non-reasoning | 推論あり / 推論なし | 추론형 / 비추론형 | con razonamiento / sin razonamiento | mit Reasoning / ohne Reasoning |
| tool calling / function calling | ツール呼び出し / 関数呼び出し | 도구 호출 / 함수 호출 | llamada a herramientas / a funciones | Tool-Aufrufe / Funktionsaufrufe |
| structured output | 構造化出力 | 구조화된 출력 | salida estructurada | strukturierte Ausgabe |
| cached input / cache hit | キャッシュ入力 / キャッシュヒット | 캐시 입력 / 캐시 히트 | entrada en caché / acierto de caché | zwischengespeicherte Eingabe / Cache-Treffer |
| concurrency / unlimited concurrency | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| image generation / edit | 画像生成 / 画像編集 | 이미지 생성 / 이미지 편집 | generación / edición de imágenes | Bildgenerierung / Bildbearbeitung |
| aspect ratio | アスペクト比 | 종횡비 | relación de aspecto | Seitenverhältnis |
| resolution | 解像度 | 해상도 | resolución | Auflösung |
| text-to-video / image-to-video | テキストから動画 / 画像から動画 | 텍스트→비디오 / 이미지→비디오 | de texto a vídeo / de imagen a vídeo | Text-zu-Video / Bild-zu-Video |
| per second / per image | 1秒あたり / 1枚あたり | 초당 / 이미지당 | por segundo / por imagen | pro Sekunde / pro Bild |
| keyframe / reference image | キーフレーム / 参照画像 | 키프레임 / 참조 이미지 | fotograma clave / imagen de referencia | Keyframe / Referenzbild |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| legacy（旧世代，仍可用） | 旧世代 | 이전 세대 | generación anterior | ältere Generation |
| deprecated / retired | 非推奨 / 提供終了 | 지원 중단 / 종료 | obsoleto / retirado | veraltet / eingestellt |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词。
- 标题和描述里要有当地开发者会搜的词：日语「Grok API 料金」；韩语「Grok API 가격」；西语「API de Grok precio」；德语「Grok API Preise」。保留模型名 + API + 价格这个核心。
- 数字格式：德语、西语小数点用逗号（0,0993），日语、韩语保持 0.0993。
- <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，并提到发票（自助开票）。
- 视频、图像模型的局限描述（"不支持参考图或关键帧""复杂人物、多人、长连续动作效果有限"）照原意翻，不要弱化也不要加原文没有的承诺。

## 日本（ja）
敬体（です・ます）。「トークン」「コンテキスト」已是通用说法，不必再解释。

## 韩国（ko）
합니다体，技术文档语气。价格、计费用「요금」「과금」。

## 西班牙（es）
通用西班牙语，不用西班牙或拉美特有说法。用无人称或统一的 tú，全文一致。

## 德国（de）
标准德语，用 "Sie"。价格用「Preis」，计费用「Abrechnung」。
