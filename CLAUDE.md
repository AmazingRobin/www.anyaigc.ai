# CLAUDE.md

@AGENTS.md

上面引入的 AGENTS.md 是本仓库的完整规则，做专题页前必须读完并按流程执行。以下是 Claude Code 专用的补充。

## 开工

- 用户说"做 <模型> 专题页"时，先按 AGENTS.md「1. 开工前向用户确认信息」逐项核对，缺的一次性问完，不要边做边问。
- 调研（官网风格、参考内容、接口文档、SEO 关键词）互相独立，并行用子代理做。
- 写完中文页再派子代理写英文页，同时自己做专题首页注册、sitemap、分享图。

## 工具

- 本地预览：`python scripts/preview.py`（后台运行），不要用 `python -m http.server`。
- 自检：`PYTHONIOENCODING=utf-8 python scripts/check_topics.py`，0 错误才能交付。
- Playwright MCP 截图路径必须在仓库内，用 `.playwright-mcp/`，交付前删除截图。
- `docs.anyaigc.ai` 是 JS 渲染的，用 Playwright `browser_navigate` + `browser_evaluate` 读 `main.innerText`。

## 交付

- 不要自动 commit 或 push，等用户要求。
- 回复里说明：新增/修改了哪些文件、自检结果、需要用户确认的事实、预览地址。
