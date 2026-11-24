# 第 5 批翻译简报：视频与图像生成模型（Kling / HappyHorse / Wan / Vidu / Hailuo）（ja / ko / es / de）

## 这批是什么
AnyAIGC（API 聚合平台）的视频、图像生成模型专题页，共 37 页。读者是开发者，要看价格、接口、怎么接入：
- **Kling**：快手可灵的视频与图像模型（Kling 3.0、2.x、Turbo、Image 3.0 等）。
- **HappyHorse**：HappyHorse 1.0 / 1.1 的 t2v、i2v、r2v、video-edit 等视频模型。
- **Wan**：通义万相 Wan 系列（Wan 2.5 / 2.6 / 2.7 / 3.0，视频与图像）。
- **Vidu**：生数科技 Vidu Q2 / Q3 / Q4 视频模型和 Vidu Image。
- **Hailuo**：MiniMax 的 Hailuo H3 视频模型。
厂商名以对应英文页写法为准，不要自己补充英文页没有的厂商信息。页面讲通过 AnyAIGC 一个 API Key 调用，走异步任务接口，按秒、按片段（clip）或按张计费，并发不限。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、Kling、HappyHorse、Wan、Vidu、Hailuo、MiniMax、Alibaba、Kuaishou、Shengshu、Claude、GPT、Gemini、OpenAI
- 型号名与代号：Kling 3.0 Turbo、Kling Image 3.0、Vidu Q2 Pro、Q3 Turbo、Q4 Preview、HappyHorse 1.1 I2V、Wan 2.7 Image Pro、H3 等；t2v / i2v / r2v / I2V / R2V 这类缩写
- 模型 ID 与接口路径：viduq2-pro、vidu-image-q2、wan2.6-i2v、happyhorse-1.0-t2v 等；所有接口路径与参数名（model、prompt、duration、resolution、aspect_ratio、seed、callback_url 等）
- 分辨率与规格：540p / 720p / 1080p、768P、4K、16:9 这类写法原样保留
- 所有代码、命令、JSON 字段、URL、环境变量；价格、百分比、倍数、数字一个都不能改；货币保持 USD / $

## 已确认的译法（四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay。敬体统一「~하세요」，疑问句统一「~입니까/합니까」。list price 译「공식 정가」。「300+」译「300개 이상」。「~12%」这类带波浪线的用「약」。
- **西语**：Business 译 Negocios，Enterprise 译 Empresas。请求统一 petición（不用 solicitud）。「~12%」译「aproximadamente el 12 %」。「300+ models」写「más de 300 modelos」。vídeo 带重音。
- **日语**：APIキー（不带空格）。英文没有 about / ~ 的地方不要加「約」；原文有 about / ~ 才用「約」。自助开票写「請求書をセルフサービスで発行」。
- **德语**：统一用 Sie；复合词连写；「~12%」译「rund 12 %」。Anfrage（请求）全文统一。
- 折扣百分比保留英文页数字，不换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问、海外信用卡；不写增值税、对公转账、签合同。发票只写“在控制台自助开具”。原文没有的承诺不要添加。
- 原文里残留的中文（例如 meta keywords 里的「企业」「发票」）：译成当地开发者会搜的词（法人向け / 기업용 / para empresas / für Unternehmen、請求書 / 인보이스 / factura / Rechnung），不要保留中文。

## 术语（与前几批已复核译文一致，全文只用一个词）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| text-to-video | テキストから動画 | 텍스트→비디오 | de texto a vídeo | Text-zu-Video |
| image-to-video | 画像から動画 | 이미지→비디오 | de imagen a vídeo | Bild-zu-Video |
| reference-to-video | 参照から動画 | 참조→비디오 | de referencia a vídeo | Referenz-zu-Video |
| text-to-image / image editing | テキストから画像 / 画像編集 | 텍스트→이미지 / 이미지 편집 | de texto a imagen / edición de imágenes | Text-zu-Bild / Bildbearbeitung |
| video editing | 動画編集 | 비디오 편집 | edición de vídeo | Videobearbeitung |
| reference image / video / audio | 参照画像 / 動画 / 音声 | 참조 이미지 / 비디오 / 오디오 | imagen / vídeo / audio de referencia | Referenzbild / -video / -audio |
| first / last frame | 最初・最後のフレーム | 첫 / 마지막 프레임 | primer / último fotograma | erstes / letztes Frame |
| native audio | ネイティブ音声 | 네이티브 오디오 | audio nativo | natives Audio |
| motion control | モーションコントロール | 모션 컨트롤 | control de movimiento | Motion Control |
| lip sync | リップシンク | 립싱크 | sincronización labial | Lippensynchronisation |
| multi-shot / shot transitions | マルチショット / ショット切り替え | 멀티샷 / 샷 전환 | varios planos / transiciones de plano | Multi-Shot / Szenenwechsel |
| elements / custom subjects（Kling Elements） | エレメント / カスタム被写体 | 엘리먼트 / 커스텀 피사체 | elementos / sujetos personalizados | Elemente / eigene Motive |
| async task | 非同期タスク | 비동기 작업 | tarea asíncrona | asynchrone Aufgabe |
| polling / callback | ポーリング / コールバック | 폴링 / 콜백 | sondeo / callback | Polling / Callback |
| duration / resolution / aspect ratio | 長さ / 解像度 / アスペクト比 | 길이 / 해상도 / 화면 비율 | duración / resolución / relación de aspecto | Dauer / Auflösung / Seitenverhältnis |
| per second / per clip / per image | 1秒 / 1クリップ / 1枚あたり | 초당 / 클립당 / 이미지당 | por segundo / por clip / por imagen | pro Sekunde / pro Clip / pro Bild |
| watermark | 透かし | 워터마크 | marca de agua | Wasserzeichen |
| prompt / negative prompt | プロンプト / ネガティブプロンプト | 프롬프트 / 네거티브 프롬프트 | prompt / prompt negativo | Prompt / Negativ-Prompt |
| tokens / context window | トークン / コンテキスト長 | 토큰 / 컨텍스트 길이 | tokens / ventana de contexto | Tokens / Kontextfenster |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price | 定価 / 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| concurrency / unlimited | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| preview（预览版型号） | プレビュー | 프리뷰 | versión preliminar | Preview |
| legacy / deprecated / retired | 旧世代 / 非推奨 / 提供終了 | 이전 세대 / 지원 중단 / 종료 | generación anterior / obsoleto / retirado | ältere Generation / veraltet / eingestellt |
| FAQ 标题 | よくある質問 | 자주 묻는 질문 | Preguntas frecuentes | Häufige Fragen |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词，不要夸大画质、速度。
- 标题和描述里要有当地开发者会搜的词：日语「Kling API 料金」；韩语「Kling API 가격」；西语「API de Kling precio」；德语「Kling API Preise」。
- 数字格式：价格和小数一律用小数点（如 0.1985），德语、西语也不用逗号（2026-11-23 用户确认，与英文页、表格、代码、JSON-LD 保持一致）；千分位按各语言习惯写，但不要产生 0,0596 这类逗号小数。
- <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，并提到发票（自助开票）。
- 页面里关于模型局限、官方文档来源的说明，照原意翻，不要弱化也不要加原文没有的承诺。
- 按钮和短标签要短：德语按钮不要超过 28 个字符（手机宽度 390px 下太长会把页面撑宽）。
- hero 打字动画里的 demo prompt（带 caret span）：译成目标语言，语气用礼貌体（日语「〜してください」），与前几批同类页面一致。
