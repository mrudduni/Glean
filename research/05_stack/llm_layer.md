# LLM layer for explanations

Field Shift must explain, for each strategy, why the tool suggested it, what evidence supports it, what it may gain, where data is missing, and what a farmer or agronomist must check locally (`research/00_challenge/details.md`). This file covers how an LLM can write those explanations without inventing facts, which models and APIs to use, and what the Space Apps rules allow.

Model facts below come from the Anthropic `claude-api` reference bundled with Claude Code (model table cached 3 November 2026), which points to these live pages: https://platform.claude.com/docs/en/about-claude/models/overview.md and https://platform.claude.com/docs/en/about-claude/pricing.md. Prices change, so recheck the pricing page before launch.

## Design principle: the LLM explains, the engine decides

The ranking, scores, and every number come from deterministic Python code (crop rules, water balance, TOPSIS, see `research/03_domain/`). The LLM only turns a structured evidence bundle into plain sentences in the farmer's language. It never computes a number, never adds a source, and never ranks.

This keeps Validity high and matches the challenge rule that the tool supports farmer judgment and does not replace it.

## Grounding pattern

1. The engine builds an evidence bundle per strategy as JSON. Each item has an `id`, a value with units, the dataset, the collection or granule ID, the date range, a confidence or quality flag, and a source URL. Missing data appears as explicit items with `status: "missing"`.
2. The prompt gives the model only that bundle plus fixed instructions: use only listed items, cite each claim by `id`, state missing data, and end with local checks.
3. The model returns structured output: a JSON object whose schema we define in Pydantic, for example `{"strategy_id", "why": [{"text", "evidence_ids"}], "gains": [...], "data_gaps": [...], "local_checks": [...]}`.
4. The server validates the result. Every `evidence_ids` entry must exist in the bundle. Every number in the text must match a number in a cited item (a regex check on digits). If a check fails, retry once, then fall back to a template sentence built from the bundle.
5. The UI renders each sentence with clickable evidence chips that open the dataset, date range, and URL.
6. A template-only mode (no LLM) must always work, so the app runs with no API key and for offline use.

## Claude API features that matter here

| Feature | What it does | Fit for Field Shift |
| --- | --- | --- |
| Structured outputs (`output_config.format`, `client.messages.parse()`) | Constrains the response to a JSON schema | Core. Gives a typed explanation object we can validate |
| Strict tool use (`strict: true` on a tool) | Guarantees tool inputs match the schema | Alternative to structured outputs |
| Citations (`citations: {enabled: true}` on document blocks) | Returns `cited_text` and character or block locations for each claim | Useful if we pass evidence as documents. It returns a 400 if combined with `output_config.format`, so choose one per request |
| Prompt caching (`cache_control`) | Reuses a fixed prefix (system prompt, crop rules, glossary) | Saves cost when many strategies share one long instruction block |
| Message Batches | Asynchronous jobs at about 50 percent of the cost | Pre-generate explanations for demo farms |
| Server-side refusal fallbacks (`fallbacks: "default"`, beta `server-side-fallback-2026-07-01`) | Retries on another model if a safety classifier declines | Recommended by the reference for current Opus models |

Caching economics from the reference: cache reads cost about 0.1 times the base input price on most models, and 0.05 times on Claude Opus 5.5 and Claude Sonnet 5.5. Cache writes cost 1.25 times for the 5-minute TTL and 2 times for the 1-hour TTL. The minimum cacheable prefix depends on the model and is 512 tokens on the newest models. Live page: https://platform.claude.com/docs/en/build-with-claude/prompt-caching.md.

Structured outputs page: https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md. Citations page: https://platform.claude.com/docs/en/build-with-claude/citations.md.

Choosing between citations and structured outputs. Structured outputs give us the exact shape the UI needs and let us check evidence IDs ourselves. Native citations give character-level spans, but only as text blocks, and not together with a schema. Recommendation: structured outputs with our own `evidence_ids` and server-side validation.

## Current Claude models

| Model | Model ID | Context | Input per million tokens | Output per million tokens |
| --- | --- | --- | --- | --- |
| Claude Opus 5.5 | `claude-opus-5-5` | 1M | $4.00 | $20.00 |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 1M | $2.00 | $10.00 |
| Claude Haiku 5.5 | `claude-haiku-5-5` | 1M | $0.10 | $0.50 (prompts up to 100K tokens) |
| Claude Fable 5.2 | `claude-fable-5-2` | 1M | $8.00 | $40.00 |

Source: the `claude-api` reference model table (cached 2026-11-03), which links https://platform.claude.com/docs/en/about-claude/pricing.md.

Behaviour notes for Claude Opus 5.5 from the same reference:

- Thinking cannot be turned off. Use `thinking: {type: "adaptive"}` and set `output_config.effort`. Its default is `medium`, so set it explicitly. `low` suits short explanation writing.
- Forced `tool_choice` (`any` or a named tool) returns a 400. Use structured outputs instead.
- Assistant prefill is not supported.
- Sampling parameters (`temperature`, `top_p`, `top_k`) are rejected.
- Check `stop_reason` for `refusal` before reading the content.

Cost estimate (assumption, not measured): one farm with 4 strategies, about 3,000 input tokens of evidence and instructions and 600 output tokens per strategy, is about 12,000 input and 2,400 output tokens. On Claude Opus 5.5 that is about $0.05 per farm before caching. The team can choose a cheaper model such as Claude Haiku 5.5 if cost matters more than quality. Measure on real bundles before deciding.

Python SDK: `anthropic` 2.8.0 (2026-11-10, Apache-2.0, https://pypi.org/pypi/anthropic/json). Keep the API key in a server-side `.env` and never in the browser.

## Open-weight local options

| Tool | Version (date) | Licence | Source |
| --- | --- | --- | --- |
| Ollama Python client | 0.6.3 (2026-09-29) | MIT | https://pypi.org/pypi/ollama/json |
| llama-cpp-python | 0.3.36 (2026-10-01) | MIT | https://pypi.org/pypi/llama-cpp-python/json |
| vLLM | 0.33.0 (2026-11-02) | Apache-2.0 | https://pypi.org/pypi/vllm/json |
| LiteLLM (provider switch layer) | 1.109.1 (2026-11-12) | MIT | https://pypi.org/pypi/litellm/json |
| Instructor (schema-constrained output) | 1.17.0 (2026-09-09) | MIT | https://pypi.org/pypi/instructor/json |
| Pydantic AI | 2.68.0 (2026-11-12) | MIT | https://pypi.org/pypi/pydantic-ai/json |

- Local models let the tool run offline or on an extension office laptop, and keep farm data on the device.
- Model weights have their own licences, separate from the runtime. Some families use Apache 2.0, while others use custom community licences that are not OSI-approved (not confirmed for specific current releases; check each model card before use).
- Small local models follow schemas less reliably, and their Hindi and Spanish quality varies. Our validation step and the template fallback catch failures.

Recommendation: hackathon uses the Claude API with structured outputs, plus the template fallback. Long term, put a small interface in front of the LLM call (one function: evidence bundle in, validated explanation out) so a local model can replace it for offline deployments. Avoid a heavy agent framework; one structured call per strategy is enough.

## Evaluation

Build a small eval set before the demo: 10 to 20 evidence bundles with known gaps. Check automatically that every claim cites a valid ID, that no number appears that is not in the bundle, that every data gap in the bundle is mentioned, and that each output has at least one local check. Have one person with farm or agronomy knowledge read a sample.

## Space Apps rules for SI (AI) in the product

From `research/02_hackathon/rules_judging.md`:

- SI tools are allowed to speed up development. They must not be used to come up with the team's idea.
- SI-generated images and videos need a visible watermark. SI code and data must be acknowledged in descriptive text and metadata.
- Judges see SI markers inside the project.

The rules file does not say whether an LLM may run inside the product at runtime (not confirmed). Nothing we found forbids it. To stay safe:

- Label every generated explanation in the UI, for example "Written by Claude from the evidence shown. Check locally before acting."
- Describe the LLM use in the project's SI section and References, including the model name.
- Keep the template mode so the core idea and results stand without the LLM.
- Do not let the LLM produce images or video for the demo, or watermark them if it does.

## Sources

- Claude models overview: https://platform.claude.com/docs/en/about-claude/models/overview.md
- Claude pricing: https://platform.claude.com/docs/en/about-claude/pricing.md
- Structured outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md
- Citations: https://platform.claude.com/docs/en/build-with-claude/citations.md
- Prompt caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching.md
- Batch processing: https://platform.claude.com/docs/en/build-with-claude/batch-processing.md
- PyPI JSON API, queried 14 November 2026: https://pypi.org/pypi/{package}/json
- Space Apps rules summary: `research/02_hackathon/rules_judging.md`
