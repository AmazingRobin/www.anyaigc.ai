# 根首页翻译简报（ja / ko / es / de）

## 这是什么
AnyAIGC（API 聚合平台）站点根首页 `/`。一个 API Key 调用 300+ 模型，OpenAI 协议兼容，按量计费。读者是各国的开发者、工作室和企业团队。

文案文件：`scripts/home_copy/en.json` 是源文，译成 `scripts/home_copy/<lang>.json`。**结构必须和 en.json 完全一致**：同样的键、同样的数组长度、同样的顺序。只翻译字符串的值，键名一个字不改。

## 不翻译、原样复制的键
`lang`（改成目标语言代码）、`html_lang`、`og_locale`、`native` 这四个键按下表填，其余键全部翻译：

| lang | html_lang | og_locale | native |
| :--- | :--- | :--- | :--- |
| ja | ja | ja_JP | 日本語 |
| ko | ko | ko_KR | 한국어 |
| es | es | es_ES | Español |
| de | de | de_DE | Deutsch |

`why.cards[*].tag`、`ent.cards[*].tag`（MODELS、INVOICE 这类大写英文标签）、`why.cards[*].big`（"300+"）原样保留，不翻译。`stats[*][0]` 里的 "300+"、"OpenAI"、"$1" 原样保留，只翻译第二项。

## 必须原样保留
- 品牌与产品名：AnyAIGC、Claude、OpenAI、Gemini、Grok、DeepSeek、Qwen、Kimi、Doubao、Zhipu GLM、Kling、Seedance、Seedream、MiniMax、Claude Code、Codex、Cursor、Dify、OpenClaw、Hermes Agent、Chatbox、Cherry Studio、OpenWebUI、n8n、WeChat Pay、Alipay、USDT、Anthropic、Google、xAI、Moonshot、Zhipu
- 技术词：OpenAI SDK、Base URL、API Key（在日语里写 APIキー，在韩语里写 API 키，西语 clave de API，德语 API-Schlüssel；但 "API Key" 作为按钮或固定名词时，参考下面的固定译法）、baseURL、apiKey、model、/v1/messages、tokens、cURL、Python、Authorization: Bearer
- HTML 标签（`<b>`、`<a href="{privacy}">`）、占位符 `{privacy}` `{support}` `{docs}` `{base}`、`&lt;API Key&gt;` 这类实体：原样保留，只翻译标签之间的文字
- 数字：300+、500 万 tokens（"5M free tokens" 在非英文页写成各语言习惯的写法：日语「500万トークン」、韩语「500만 토큰」、西语「5 millones de tokens」、德语「5 Mio. Tokens」）、$1、7×24
- 价格和小数一律用小数点；本文件里没有小数，如有按小数点

## 固定译法（与已完成的专题页一致）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| :--- | :--- | :--- | :--- | :--- |
| Get an API Key | APIキーを取得 | API 키 받기 | Obtener clave de API | API-Schlüssel holen |
| Model Guides（导航与链接） | モデルガイド | 모델 가이드 | Guías de modelos | Modellguides |
| Models & Pricing | モデルと料金 | 모델과 가격 | Modelos y precios | Modelle & Preise |
| Quick Start | クイックスタート | 빠른 시작 | Inicio rápido | Schnellstart |
| Enterprise | 法人向け | 기업용 | Empresas | Unternehmen |
| API Docs | APIドキュメント | API 문서 | Documentación de la API | API-Doku |
| Log in | ログイン | 로그인 | Iniciar sesión | Anmelden |
| Talk to sales | 営業に問い合わせる | 영업팀 문의 | Hablar con ventas | Vertrieb kontaktieren |
| Start with a free account | 無料アカウントで始める | 무료 계정으로 시작 | Empieza con una cuenta gratuita | Mit kostenlosem Konto starten |
| Self-service invoices | 請求書を自分で発行 | 인보이스 직접 발급 | Facturas en consola | Rechnungen im Konto |
| Payment methods | お支払い方法 | 결제 수단 | Métodos de pago | Zahlungsmethoden |
| pay as you go | 従量課金 | 종량제 | pago por uso | nutzungsbasiert abgerechnet |
| tokens | トークン | 토큰 | tokens | Tokens |
| model ID | モデルID | 모델 ID | ID de modelo | Modell-ID |
| console | コンソール | 콘솔 | consola | Konsole |
| unlimited concurrency | 同時実行数の上限なし | 동시 실행 제한 없음 | sin límite de RPM | kein RPM-Limit |
| list price | 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| Privacy Policy | プライバシーポリシー | 개인정보 처리방침 | Política de privacidad | Datenschutzerklärung |
| Terms of Service | 利用規約 | 이용약관 | Términos del servicio | Nutzungsbedingungen |

## 口径（用户已确认，不要改）
- 非中文页只写「在控制台自助开具发票，按实际充值金额开具」。**不写**增值税、增值税专用发票、对公转账、签订合同、国内网络直连、中国大陆访问、海外信用卡相关说法。en.json 里没有这些，翻译时也不要加。
- 不写 SLA、可用率、令牌分组、企业专属线路；不添加 en.json 里没有的数字、承诺、功能、客户名。
- 保留支付方式：WeChat Pay、Alipay、USDT、Credit card（信用卡按各语言习惯写：クレジットカード / 신용카드 / tarjeta de crédito / Kreditkarte）。

## 风格
- 开发者文档的语气：直接、具体、短句；不要营销腔，不要原文没有的夸张词。
- 日语敬体（です・ます），韩语合니다体，西语通用（不带地区特征，统一用 tú 或无人称），德语统一用 Sie。
- 标题（title）显示宽度 ≤ 64（日韩：汉字假名谚文各算 2）或 ≤ 65 字符（西德）；描述（desc）日韩 60–240 宽度、西德 120–160 字符。desc 里要提到自助开票。
- title 要有当地开发者会搜的词：日语「API」「料金」不必硬加，但保留 300+ 模型、OpenAI 互換 这类核心词；不要写成「中转」。
- 导航按钮在手机上空间很小：nav 的五项（模型专题/模型广场/快速开始/企业接入/API 文档）每项尽量短，德语和西语不超过 14 个字符，日韩不超过 8 个字；login、cta_key 不超过 14 个字符（德语 API-Schlüssel holen 已经是上限）。
- `hero.h1a` 和 `hero.h1b` 是标题的两行（中间会换行），各自不要太长：日韩每行不超过 12 个字，西德每行不超过 24 个字符；`h1b` 会渲染成渐变色高亮词。
- 页脚 `foot.note` 前面会自动加 "© 2026 AnyAIGC"，不要重复。
- 终端示例里的 `term.user_msg` 是示例提问：写成目标语言里自然的一句话（如日语「こんにちは、自己紹介してください」），不要含引号和反斜杠。
