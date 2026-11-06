# Grok text guides — 2026-11-05

- User confirmed all eight models have unlimited concurrency by default for every user.
- User confirmed endpoints should follow the model catalog: 4.7 / 4.6 / 4.5 / 4.3 support Chat Completions and Messages; 4 / both 4.20 variants / Build 0.1 list Chat Completions only.
- `grok-4.x` is the requested overview slug, not a callable model ID. The overview examples use `grok-4.7`.
- Public prices were read in the rendered catalog and model detail tables, under the conversation category. Preserve displayed decimal precision, including `1.4890` and `1.191`.
- Billing tiers: input up to 200,000 tokens, then over 200,000 and up to 500,000 tokens. Do not treat billing tier boundaries as every model's context window.
- Cache-hit base rates are displayed for 4.7, 4.6, 4.5, and 4.3. No cache price is invented for other models or the long-input tier.
- Reference `https://x.ai/news/grok-4-7` successfully loaded. White background, ink `#0a0a0a`, warm neutral panels, thin rules, lightweight sans-serif titles, pill buttons. Use system fonts; do not download xAI's font.
- `https://x.ai/api` returned Cloudflare 403. Google search returned 429 and Bing returned no useful results. SEO wording uses the requested API / pricing / key intent and verified source facts.
- `https://docs.x.ai/developers/models` lists Grok 4.7 with a 500K context window and states live events require search tools. No native search availability is promised for the gateway.
- AnyAIGC Chat Completions docs verified `model`, `messages`, `stream`, Bearer auth, and the `choices` response. Messages docs verified `/v1/messages` and request fields but mix generic response examples; no Grok-specific response payload is asserted or fabricated. Live model API calls were not made.

Regenerate pages with `python scripts/grok_text_pages.py`, register with `python scripts/grok_text_register.py`, then run `python scripts/payments.py`, `python scripts/trust.py` and `python scripts/check_topics.py`. Shared styles/scripts use version `20261105`.

`python scripts/og_grok_text.py` writes temporary 1200×630 HTML to `.playwright-mcp/og-grok-text/`. Capture with Playwright into `assets/og/<slug>-<lang>.png` and remove temporary HTML/screenshots after visual verification.
