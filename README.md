# 🚀 AnyAIGC · 国内外大模型 API 中转平台

> 一个 Base URL，一个 API Key，统一调用 500+ 国内外大模型。兼容 OpenAI 协议，国内网络可直连。

本仓库是 [anyaigc.ai](https://anyaigc.ai) 的官方站点，同时这份 README 也可作为平台的完整介绍与接入指南。

---

## 📖 目录

- [这是什么](#-这是什么)
- [核心特性](#-核心特性)
- [支持的模型](#-支持的模型)
- [三步完成接入](#️-三步完成接入)
- [代码示例](#-代码示例)
- [开发工具接入](#-开发工具接入)
- [典型使用场景](#-典型使用场景)
- [常见问题](#-常见问题)
- [相关链接](#-相关链接)

---

## 🎯 这是什么

AnyAIGC 是一个 **大模型 API 中转（聚合）平台**。它把 Claude、OpenAI、Gemini、Grok、DeepSeek、通义千问、Kimi、豆包、智谱 GLM 等分散在各家厂商的接口，统一收敛成一套 **OpenAI 兼容协议**。

对开发者来说，这解决三个具体问题：

| 痛点 | AnyAIGC 的做法 |
| :--- | :--- |
| 🧩 每接一家模型都要重写一套 SDK 和鉴权 | 统一 Base URL + 统一 API Key，换模型只换 `model` 字段 |
| 🌐 国内访问海外模型需要额外代理 | 国内网络通常可直连，无需自建中转 |
| 💳 多家账号、多份充值、多套账单 | 单账号按量计费，用量与花费集中在一个控制台 |

适合 **开发者、独立工作室、企业团队** 用于 AI 应用、代码工具、自动化工作流和内部系统。

---

## ✨ 核心特性

### 🗂️ 500+ 模型统一目录
覆盖语言、图像、视频、向量（Embedding）与检索模型，在控制台按实时目录选择，不用记各家的接口差异。

### 🔌 兼容 OpenAI SDK
多数现有项目 **只需替换三样东西** 即可迁移：`baseURL`、`apiKey`、`model`。业务代码基本不动。

### 🇨🇳 国内直连与灵活分组
国内网络通常无需额外代理。可按 **价格、线路、可用性策略** 选择不同的路由分组，把成本敏感的任务和稳定性敏感的任务分开跑。

### 💰 按量计费与企业发票
个人、工作室、企业团队都能按需使用；企业用户可联系客服确认发票方案。

### 🔄 一个 Key 打通全部工具链
Claude Code、Codex、Cursor、Dify、Chatbox、n8n 等客户端共用同一个 Key，不必为每个工具单独申请。

---

## 🤖 支持的模型

按厂商归类的主要覆盖范围（**具体模型 ID、价格与维护状态以控制台实时目录为准**）：

| 类型 | 覆盖范围 |
| :--- | :--- |
| 🌍 海外语言模型 | Claude、OpenAI（GPT 系列）、Gemini、Grok |
| 🀄 国内语言模型 | DeepSeek、通义千问 Qwen、Kimi、豆包 Doubao、智谱 GLM |
| 🎨 图像模型 | 文生图 / 图生图类模型 |
| 🎬 视频模型 | 文生视频 / 图生视频类模型 |
| 🔍 向量与检索 | Embedding、Rerank、检索增强相关模型 |

> ⚠️ 模型目录是动态的：厂商上下新版本、调价、下线都会反映到控制台。**不要把模型 ID 硬编码在代码里当成永久有效**，建议放到配置项中。

---

## 🛠️ 三步完成接入

### 1️⃣ 注册账号
注册 AnyAIGC 账号并进入控制台 👉 [立即注册](https://anyaigc.ai/register?aff=oOK7)

### 2️⃣ 创建 API Key
在控制台创建 API Key，同时记下：

```text
Base URL: https://anyaigc.ai/v1
API Key : sk-xxxxxxxxxxxxxxxxxxxxxxxx
Model   : 从控制台模型列表复制真实模型 ID
```

> 💡 Base URL 与当前可用模型 ID 请以控制台展示为准。

### 3️⃣ 接入项目或工具
把 OpenAI SDK、Cursor、Dify、Chatbox 等的接口地址替换为上面的 Base URL，先跑一次 **小规模验证请求**，确认计费与返回正常后再放量。

---

## 💻 代码示例

### 🐍 Python（openai SDK）

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://anyaigc.ai/v1",
    api_key="sk-你的APIKey",          # 建议从环境变量读取，不要写进代码库
)

resp = client.chat.completions.create(
    model="从控制台复制的模型ID",
    messages=[{"role": "user", "content": "用一句话解释什么是 API 中转"}],
)

print(resp.choices[0].message.content)
```

### 🟩 Node.js（openai SDK）

```js
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'https://anyaigc.ai/v1',
  apiKey: process.env.ANYAIGC_API_KEY,
});

const resp = await client.chat.completions.create({
  model: '从控制台复制的模型ID',
  messages: [{ role: 'user', content: '用一句话解释什么是 API 中转' }],
});

console.log(resp.choices[0].message.content);
```

### 🌊 流式输出（stream）

```python
stream = client.chat.completions.create(
    model="从控制台复制的模型ID",
    messages=[{"role": "user", "content": "写一首关于秋天的短诗"}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

### 🧪 curl 快速验证

```bash
curl https://anyaigc.ai/v1/chat/completions \
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "从控制台复制的模型ID",
    "messages": [{"role": "user", "content": "ping"}]
  }'
```

> 🔐 **别把 API Key 提交进仓库。** 用环境变量或密钥管理服务，`.env` 记得加进 `.gitignore`。

---

## 🧰 开发工具接入

| 工具 | 适用场景 |
| :--- | :--- |
| 🖥️ **Claude Code** | 终端里的 Claude 编程工作流：项目理解、代码问答、重构建议、脚本编写 |
| 🤖 **Codex** | 本地代码代理：读写项目、执行命令、修复问题、跑测试 |
| 🐾 **OpenClaw** | 本地 AI 工作台：浏览器操作、文件处理、工具调用、多模型配置 |
| 📨 **Hermes** | Agent 网关与消息流转：任务分发、工具调用转发、长流程编排 |
| ✏️ **Cursor** | 代码生成、重构、项目问答、日常开发 |
| 🧠 **Dify** | AI 工作流、知识库、客服助手、企业内部应用 |
| 💬 **Chatbox / Cherry Studio** | 日常对话、总结、翻译、多模型快速切换 |
| 🔗 **OpenWebUI / n8n** | 自建平台、自动化编排、团队工具链 |

各工具的详细配置步骤见 📚 [官方文档](https://docs.anyaigc.ai)。接入前先确认客户端支持的协议（OpenAI 兼容 / Anthropic 原生等）与真实模型 ID。

---

## 🎬 典型使用场景

- 🧑‍💻 **AI 编程工具** — 给 Cursor / Claude Code / Codex 供能，一个 Key 全套工具通用
- 💬 **聊天助手与客服** — 多模型对比测试，按成本和效果分流
- ⚙️ **自动化工作流** — n8n、Dify 里的批量总结、翻译、内容生成
- 🏢 **企业内部系统** — 内部问答、文档处理、报表生成，统一出口便于审计与成本归集
- 📚 **知识库 / RAG** — Embedding + Rerank + 生成模型在同一个接口下组合
- 🖼️ **图像与视频生成** — 素材批量生产、创意验证

---

## ❓ 常见问题

<details>
<summary><b>和直接用官方 API 有什么区别？</b></summary>

省掉了多套 SDK、多份鉴权、多个账单，以及国内访问海外模型的网络环节。代价是多了一层中转，对延迟极端敏感的场景建议先自己压测再决定。
</details>

<details>
<summary><b>现有项目迁移成本高吗？</b></summary>

如果项目本来就用 OpenAI SDK，改 `baseURL`、`apiKey`、`model` 三处即可。用了各厂商私有参数（特殊字段、私有 endpoint）的部分需要单独确认。
</details>

<details>
<summary><b>模型 ID 从哪里拿？</b></summary>

控制台的模型列表页。README 和落地页里的写法都是占位示例，**不要照抄** —— 目录会随厂商上下线变化。
</details>

<details>
<summary><b>支持流式输出、函数调用、多模态吗？</b></summary>

这些按模型能力决定，不是平台统一开关。上线前请针对你要用的具体模型实测。
</details>

<details>
<summary><b>怎么控制成本？</b></summary>

按量计费，用量在控制台可查。建议：先用小请求验证链路，再按任务类型选择不同价位的分组，把便宜模型用在批量低价值任务上。
</details>

<details>
<summary><b>企业能开发票吗？</b></summary>

可以，具体方案联系客服确认。
</details>

---

## 🔗 相关链接

| 入口 | 地址 |
| :--- | :--- |
| 🏠 官网 | <https://anyaigc.ai> |
| 🔑 注册并创建 API Key | <https://anyaigc.ai/register?aff=oOK7> |
| 💵 模型与价格 | <https://anyaigc.ai/pricing> |
| 📚 接入文档 | <https://docs.anyaigc.ai> |

---

<div align="center">

**一个 Base URL，接入你需要的全部模型** 🚀

[创建 API Key](https://anyaigc.ai/register?aff=oOK7) · [查看模型与价格](https://anyaigc.ai/pricing) · [阅读文档](https://docs.anyaigc.ai)

</div>
