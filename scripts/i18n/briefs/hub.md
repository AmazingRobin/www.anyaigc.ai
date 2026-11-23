# 专题首页翻译简报（ja / ko / es / de）

## 这是什么
AnyAIGC（API 聚合平台）的「AI Model API Guides」专题首页：列出 216 个模型专题页的卡片，按厂商分 19 个类别。每张卡片有标题（模型名 + API）、厂商 · 模型 ID、一句话简介、几个标签、起步价。读者是开发者。

## 本批要翻译的内容
- 页面标题、描述、og/twitter 标题和描述、结构化数据（JSON-LD）里的名称和描述
- 首屏文案、分类标题和分类的小字说明（如 “overview and price comparison”“Save up to 59% vs. official”）
- 卡片里的一句话简介、标签、价格行（如 “$0.2382 / 1M input”）
- 页脚、“Don't see the model you need?” 区块
- 模型专题页本身已翻译过的文案已经由翻译记忆库带入，本批只译其余的。

## 固定译法（H1 必须用下面这个，分享图也用它）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| AI Model API Guides（H1） | AIモデル API ガイド | AI 모델 API 가이드 | Guías de API de modelos de IA | API-Leitfäden für KI-Modelle |
| One API key · 300+ models | 1つのAPIキーで300以上のモデル | API 키 하나로 300개 이상 모델 | Una clave de API · más de 300 modelos | Ein API-Schlüssel · über 300 Modelle |
| Get an API Key | APIキーを取得 | API 키 받기 | Obtener clave de API | API-Schlüssel holen |
| See All Models & Pricing | すべてのモデルと料金を見る | 전체 모델과 가격 보기 | Ver todos los modelos y precios | Alle Modelle und Preise ansehen |
| Model Guides（导航/面包屑） | モデルガイド | 모델 가이드 | Guías de modelos | Modell-Leitfäden |
| overview and price comparison | 概要と料金比較 | 개요 및 가격 비교 | resumen y comparación de precios | Überblick und Preisvergleich |
| Self-service invoices | 請求書を自分で発行 | 인보이스 직접 발급 | Facturas en consola | Rechnungen im Konto |
| per 1M input / from | 入力100万トークンあたり … から | 입력 100만 토큰당 … 부터 | por 1 M de entrada · desde | pro 1 Mio. Eingabe · ab |

## 必须原样保留
- 品牌与模型名、模型 ID、厂商名（OpenAI、Anthropic、Google、ByteDance、Moonshot、Zhipu、Alibaba、Meta、ElevenLabs、MiniMax、Tencent、iFLYTEK、Xiaomi 等）、AnyAIGC
- 价格数字：**所有语言一律用小数点**（`$0.2382`），西语、德语也不用逗号
- 结构化数据里的模型名（如 “GPT-6 Astra API”“Suno API”）基本保持原样，只翻译其中的普通词（如 “(all models)”“Model Guides”）
- HTML 标签、属性、`{{N}}` 占位符、`&amp;` 等实体原样保留

## 已确认的译法与规则（与前几批一致）
- 韩语：敬体统一「~하세요」；list price 译「공식 정가」；「300+」译「300개 이상」；WeChat Pay、Alipay 写英文名。
- 西语：通用西语，Business 译 Negocios，Enterprise 译 Empresas；请求用 petición；vídeo 带重音。
- 日语：APIキー（不带空格）；原文没有 about / ~ 不要加「約」。
- 德语：统一用 Sie；复合词连写；Anfrage 全文统一；按钮和短标签不超过 28 个字符。
- 发票只写“自助开票 / 在控制台自助开具”；不写增值税、对公转账、合同、SLA、可用率、中国大陆访问。
- 卡片一句话简介照英文原意翻，不添加原文没有的承诺、数字、功能，不夸大。
- 标题显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符。
- 术语与已复核系列一致，参考 `scripts/i18n/briefs/batch3-series.md`、`batch5-video.md`、`batch6-misc.md` 的术语表。
