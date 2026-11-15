# AI use disclosure

Space Apps asks teams to say where AI helped. This page covers the AI inside the app and the AI tools the team used to build it.

## 1. The in-app assistant

**What it does.** The Field Assistant explains the tool's results to a farmer: why a strategy ranks first, how much water it may save, how sure the numbers are. It supports the farmer's judgement and does not replace it.

**Which model.** The assistant calls a hosted large language model through an OpenAI-compatible chat API. The provider, base URL, model id and key are server-side environment variables (`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`). The key never reaches the browser and is never committed. The current build uses Groq with `openai/gpt-oss-120b`. Gemini Flash works through the same interface, so the provider can change without code changes.

**What the model never sees.** It gets no farmer data, no account data and no location beyond the three demo fields. Every request carries only the system prompt, the field's fact list, the last few chat turns and the question.

## 2. How answers are grounded

The assistant is not trusted to know anything. Four layers keep it honest.

1. **Facts only.** `model/assistant/context.py` builds about 340 facts per field. Each is one English sentence with its number, unit, source tag and, where it applies, a scenario and rotation. Only the facts for the selected scenario (about 3,600 tokens) go into the prompt. Every number comes from NASA or USDA data, or from our water-budget model run on that data.
2. **A strict prompt.** `model/assistant/prompt.md` tells the model to use only the listed facts, to tag each sentence with its source in square brackets, to say "may" and "estimated" instead of "will", to refuse pesticide, fertilizer-rate, water-rights and financial advice, and to say "I don't have that" and point to a K-State Research and Extension agent when the facts run out. Temperature is 0.2.
3. **A number check.** After the model answers, `model/assistant/number_check.py` (and the same logic in the web app) finds every number in the answer. It converts inches to mm and °F to °C, then compares each number with the facts, allowing 5% or the rounding step. Numbers that match show a check and their source. Numbers that do not match get an "unverified" badge, so the farmer sees what is not backed by data. 34 shared test cases keep the Python and TypeScript versions identical.
4. **A cache for the demo path.** The six suggested questions, in English and Spanish, for each of the three fields, are answered ahead of time (`assistant_cache.json`). They are generated once, retried once if a number fails the check, then reviewed. Judges who click a suggested question get a reviewed answer even if the live model is down. Free-text questions go to the live model and fall back to the suggested questions when it fails.

## 3. How we tested the assistant

- **Unit tests** for the number check (`model/assistant/tests`, run with `pytest`).
- **LLM-as-judge** (`model/assistant/judge.py`). A second model call scores each cached answer from 1 to 5 on accuracy to the facts, no invented numbers, no overclaiming, no forbidden advice, readability, language and source tags. Rule checks run alongside it: under 150 words, every number verified, no "will/guaranteed/proven", no pesticide or legal terms, correct language, tags present. Failing answers are regenerated with the reviewer's notes, at most twice. The report is `model/out/assistant_review.md`.
- **Manual read** of the final cached answers by the team before the demo.

## 4. Known limits

- The model can still misread a fact or choose a poor emphasis. The number check catches wrong numbers, not wrong reasoning.
- Spanish answers are machine-written. Wording may read oddly to a native speaker. Numbers use a decimal point in both languages so the check works.
- The model's own claims about the world outside the facts are not checked. The prompt tells it to stay inside the facts.
- Answers describe replayed past weather and a simplified model. They are not forecasts or advice.

## 5. AI tools the team used to build the project

| Tool | Used for |
|---|---|
| Claude Code (Anthropic Claude models) | Planning, writing and reviewing the Python data and model code, the assistant pipeline, the web app contract, tests and documentation |
| Groq-hosted `openai/gpt-oss-120b` | The in-app assistant, answer generation and the LLM-as-judge review |

People chose the datasets, the farm questions, the scoring design and the contract between roles, and checked results against the source data. AI-written code and text were run, tested and edited by the team before use. No AI tool was used to invent data: every number the app shows comes from the datasets listed in the README or from the model run on them.
