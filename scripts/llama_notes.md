# Llama source notes — 2026-11-11

- Scope confirmed by the user: `/models/llama` overview plus all 12 IDs in the Ollama marketplace category, in Chinese and English.
- User confirmed: all users have unlimited concurrency and no fixed RPM cap by default.
- Public marketplace: https://anyaigc.ai/pricing?provider=Ollama . Read rendered cards, detail drawers, and the page's public `/api/pricing_new?lang=zh` response. `llama_data.py` preserves the exact four-decimal displayed prices.
- Eleven models have the marketplace's 32% savings offer. `llama-3.3-70b-instruct` has input/output $0.7290 per million tokens and no savings badge. Do not apply 68折 to that model or reverse-calculate rates from a rounded campaign label.
- The overview's starting input price is $0.3375 for `llama-3.2-1b-instruct`. Its displayed output price is $0.0844; cost examples intentionally use that displayed rate without rounding the result.
- Llama is developed by Meta, not Ollama. Ollama is the user's style reference and marketplace provider category. Some marketplace descriptions misstate Llama 3 parameter counts and refer to 3.3 as 3; those descriptions are not copied.
- Every listed model advertises the OpenAI endpoint. Request/response fields were checked against rendered `main.innerText` at https://docs.anyaigc.ai/reference/v1/chat/completions (redirects to `/en/reference/v1/chat/completions`). Examples use `model`, `messages`, `n=1`, `stream=false`, Bearer auth and the documented `choices`/`usage` response structure. Python uses the standard library. Examples are syntax-checked; no paid API request was made.
- Model descriptions read in full at https://ollama.com/library/llama2 , `/llama3`, `/llama3.1`, `/llama3.2`, `/llama3.2-vision`, `/llama3.3`. No platform context-window limit, benchmark, retirement claim or inference speed is invented.
- Vision models: 11B/90B Llama 3.2 Vision. Examples demonstrate text requests. Official model cards list English for image-text input and eight supported text languages for 3.1–3.3; Chinese is not in that list.
- Style: Ollama homepage, white `#ffffff`, neutral ink `#171717`, gray `#737373`, system sans-serif, generous whitespace, centered headline, pill CTA, metrics row and restrained separators. No borrowed photography or illustrations.
- Mark: lobe-icons `ollama.svg`, pinned to icons-static-svg 1.97.0, same mark in pages, hub and share cards. Brand attribution is explicit in the content.
- SEO research: searched Chinese `Llama API 价格 API key` and English `"Llama" "API" "pricing"` with Bing; Google timed out. Results included Ollama library, Meta developer guide and model explainers. Page content covers price units, API key, versions, exact IDs, cloud vs local deployment and enterprise procurement.

Regenerate content with `python scripts/llama_pages.py`, registration with `python scripts/llama_register.py`, and temporary sharing-card HTML with `python scripts/og_llama.py`. Rasterize the latter through Playwright at 1200×630 into `assets/og/<slug>-<lang>.png`, then remove the temporary HTML. All HTML and CSS/JS are directly deployable; these scripts are maintenance helpers, not a build requirement.

## Verification

- `python scripts/check_topics.py`: 0 errors; five pre-existing Kling title/description warnings, none for Llama.
- All 26 pages: HTTP 200, one H1, 11 FAQs, no browser JavaScript/console errors, full-page screenshots at 1440×900 and 390×844. Document scroll width equals viewport width throughout.
- Long Vision model page additionally checked at 1100, 900 and 640 px. Mobile prices and exact IDs remain visible.
- Chinese/English navigation clicked in both directions. Mobile menu, FAQ expansion, cURL/Python click and keyboard tabs, and clipboard copying verified (Windows clipboard CRLF normalized when comparing). Reduced-motion scroll behavior is `auto`.
- Exact visible FAQ/JSON-LD text and price-table/Offer parity verified on all 26 pages. All Python examples executed against a mocked standard-library HTTP transport, checking endpoint, model ID, auth header, `n` and `stream`. No paid API calls.
- All 26 PNGs are 1200×630. Long titles and image/text placement visually inspected. `node --check assets/models/llama.js` and `git diff --check` passed.
