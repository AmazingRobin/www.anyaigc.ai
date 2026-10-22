# 🚀 AnyAIGC · LLM API Gateway for Domestic & Overseas Models

[简体中文](./README.md) ｜ English

> One Base URL, one API Key — call 300+ domestic and overseas large models through a single endpoint. OpenAI-compatible, with direct access from within mainland China.

This repository hosts the official site for [anyaigc.ai](https://anyaigc.ai). This README also serves as a complete platform overview and integration guide.

---

## 📖 Table of Contents

- [What is this](#-what-is-this)
- [Key Features](#-key-features)
- [Supported Models](#-supported-models)
- [Get Started in Three Steps](#️-get-started-in-three-steps)
- [Code Examples](#-code-examples)
- [Developer Tool Integrations](#-developer-tool-integrations)
- [Typical Use Cases](#-typical-use-cases)
- [FAQ](#-faq)
- [Links](#-links)

---

## 🎯 What is this

AnyAIGC is a **large-model API gateway (aggregator)**. It takes the scattered APIs from Claude, OpenAI, Gemini, Grok, DeepSeek, Qwen, Kimi, Doubao, Zhipu GLM and more, and unifies them behind a single **OpenAI-compatible protocol**.

For developers, this solves three concrete problems:

| Pain point | How AnyAIGC handles it |
| :--- | :--- |
| 🧩 Every new model means rewriting SDKs and auth | One Base URL + one API Key; switch models by changing only the `model` field |
| 🌐 Accessing overseas models from China needs extra proxying | Usually reachable directly from mainland networks, no self-hosted relay needed |
| 💳 Multiple accounts, top-ups and bills | Single account, pay-as-you-go, with usage and spend in one console |

It suits **developers, indie studios and enterprise teams** building AI apps, coding tools, automation workflows and internal systems.

---

## ✨ Key Features

### 🗂️ 300+ models in one catalog
Covers language, image, video, embedding and retrieval models. Pick from the live catalog in the console — no need to memorize each vendor's API quirks.

### 🔌 OpenAI SDK compatible
Most existing projects migrate by **swapping just three things**: `baseURL`, `apiKey` and `model`. Your business logic stays largely untouched.

### 🇨🇳 Direct access from China & flexible routing
No extra proxy needed on most mainland networks. Choose routing groups by **price, route or availability policy**, so cost-sensitive and stability-sensitive workloads run separately.

### 💰 Pay-as-you-go & enterprise invoicing
Individuals, studios and enterprise teams can use it on demand; enterprise users can contact support about invoicing options.

### 🔄 One Key across the whole toolchain
Claude Code, Codex, Cursor, Dify, Chatbox, n8n and other clients share the same Key — no separate application per tool.

---

## 🤖 Supported Models

Main coverage grouped by vendor (**exact model IDs, pricing and maintenance status follow the live catalog in the console**):

| Type | Coverage |
| :--- | :--- |
| 🌍 Overseas language models | Claude, OpenAI (GPT family), Gemini, Grok |
| 🀄 Domestic language models | DeepSeek, Qwen, Kimi, Doubao, Zhipu GLM |
| 🎨 Image models | Text-to-image / image-to-image models |
| 🎬 Video models | Text-to-video / image-to-video models |
| 🔍 Embedding & retrieval | Embedding, Rerank and RAG-related models |

> ⚠️ The model catalog is dynamic: vendors add or retire versions and adjust prices, and the console reflects that. **Do not hardcode model IDs as if they were permanent** — keep them in configuration.

---

## 🛠️ Get Started in Three Steps

### 1️⃣ Register an account
Register an AnyAIGC account and open the console 👉 [Sign up now](https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9)

### 2️⃣ Create an API Key
Create an API Key in the console, and note down:

```text
Base URL: https://anyaigc.ai/v1
API Key : sk-xxxxxxxxxxxxxxxxxxxxxxxx
Model   : copy a real model ID from the console model list
```

> 💡 The Base URL and currently available model IDs are authoritative as shown in the console.

### 3️⃣ Wire it into your project or tool
Point your OpenAI SDK, Cursor, Dify, Chatbox, etc. at the Base URL above. Run a **small validation request** first to confirm billing and responses look right, then scale up.

---

## 💻 Code Examples

### 🐍 Python (openai SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://anyaigc.ai/v1",
    api_key="sk-your-api-key",          # read from an env var; don't commit it
)

resp = client.chat.completions.create(
    model="model-ID-copied-from-console",
    messages=[{"role": "user", "content": "Explain API gateways in one sentence"}],
)

print(resp.choices[0].message.content)
```

### 🟩 Node.js (openai SDK)

```js
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'https://anyaigc.ai/v1',
  apiKey: process.env.ANYAIGC_API_KEY,
});

const resp = await client.chat.completions.create({
  model: 'model-ID-copied-from-console',
  messages: [{ role: 'user', content: 'Explain API gateways in one sentence' }],
});

console.log(resp.choices[0].message.content);
```

### 🌊 Streaming output (stream)

```python
stream = client.chat.completions.create(
    model="model-ID-copied-from-console",
    messages=[{"role": "user", "content": "Write a short poem about autumn"}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

### 🧪 Quick check with curl

```bash
curl https://anyaigc.ai/v1/chat/completions \
  -H "Authorization: Bearer $ANYAIGC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "model-ID-copied-from-console",
    "messages": [{"role": "user", "content": "ping"}]
  }'
```

> 🔐 **Never commit your API Key.** Use environment variables or a secrets manager, and add `.env` to `.gitignore`.

---

## 🧰 Developer Tool Integrations

| Tool | Use case |
| :--- | :--- |
| 🖥️ **Claude Code** | Claude coding workflows in the terminal: project understanding, code Q&A, refactoring suggestions, scripting |
| 🤖 **Codex** | Local coding agent: read/write projects, run commands, fix issues, run tests |
| 🐾 **OpenClaw** | Local AI workbench: browser control, file handling, tool calls, multi-model config |
| 📨 **Hermes** | Agent gateway and message routing: task dispatch, tool-call forwarding, long-flow orchestration |
| ✏️ **Cursor** | Code generation, refactoring, project Q&A, everyday development |
| 🧠 **Dify** | AI workflows, knowledge bases, support assistants, internal enterprise apps |
| 💬 **Chatbox / Cherry Studio** | Everyday chat, summarization, translation, quick model switching |
| 🔗 **OpenWebUI / n8n** | Self-hosted platforms, automation orchestration, team toolchains |

Detailed setup for each tool is in the 📚 [official docs](https://docs.anyaigc.ai). Before integrating, confirm the protocol your client supports (OpenAI-compatible / Anthropic-native, etc.) and the real model IDs.

---

## 🎬 Typical Use Cases

- 🧑‍💻 **AI coding tools** — power Cursor / Claude Code / Codex with one Key across the whole set
- 💬 **Chat assistants & support** — compare models side by side, route by cost and quality
- ⚙️ **Automation workflows** — batch summarization, translation and content generation in n8n or Dify
- 🏢 **Internal enterprise systems** — internal Q&A, document processing, report generation, with one egress for easy auditing and cost attribution
- 📚 **Knowledge base / RAG** — combine embedding + rerank + generation models behind one endpoint
- 🖼️ **Image & video generation** — batch asset production and creative validation

---

## ❓ FAQ

<details>
<summary><b>How is this different from using official APIs directly?</b></summary>

It removes multiple SDKs, multiple auth setups and multiple bills, plus the networking hop for reaching overseas models from China. The trade-off is one extra relay layer — for latency-critical scenarios, benchmark it yourself first.
</details>

<details>
<summary><b>Is migrating an existing project expensive?</b></summary>

If your project already uses the OpenAI SDK, you change `baseURL`, `apiKey` and `model` — three spots. Any parts that rely on vendor-specific parameters (special fields, private endpoints) need to be verified separately.
</details>

<details>
<summary><b>Where do I get model IDs?</b></summary>

From the model list page in the console. The IDs in this README and on the landing page are placeholder examples — **don't copy them verbatim**, since the catalog changes as vendors add and retire models.
</details>

<details>
<summary><b>Do you support streaming, function calling and multimodal?</b></summary>

These depend on each model's capabilities, not a platform-wide switch. Test against the specific model you plan to use before going live.
</details>

<details>
<summary><b>How do I control cost?</b></summary>

Pay-as-you-go, with usage visible in the console. Recommended: validate the pipeline with small requests first, then pick routing groups at different price points by task type, using cheaper models for high-volume low-value work.
</details>

<details>
<summary><b>Can enterprises get invoices?</b></summary>

Yes — contact support to confirm the specifics.
</details>

---

## 🔗 Links

| Entry | URL |
| :--- | :--- |
| 🏠 Website | <https://anyaigc.ai> |
| 🔑 Register & create an API Key | <https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9> |
| 💵 Models & pricing | <https://anyaigc.ai/pricing> |
| 📚 Integration docs | <https://docs.anyaigc.ai> |

---

<div align="center">

**One Base URL, access every model you need** 🚀

[Create an API Key](https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9) · [View models & pricing](https://anyaigc.ai/pricing) · [Read the docs](https://docs.anyaigc.ai)

</div>
