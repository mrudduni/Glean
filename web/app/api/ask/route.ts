// POST /api/ask (README §9, handover §7.2).
import { NextRequest, NextResponse } from "next/server";
import promptJson from "@/public/data/assistant/prompt.json";
import copyJson from "@/public/data/content/copy.json";
import cardTextJson from "@/public/data/content/card_text.json";
import sourcesJson from "@/public/data/sources.json";
import f1Context from "@/public/data/field/f1/assistant_context.json";
import f2Context from "@/public/data/field/f2/assistant_context.json";
import f3Context from "@/public/data/field/f3/assistant_context.json";
import f1Cache from "@/public/data/field/f1/assistant_cache.json";
import f2Cache from "@/public/data/field/f2/assistant_cache.json";
import f3Cache from "@/public/data/field/f3/assistant_cache.json";
import { checkNumbers } from "@/lib/numberCheck";
import {
  askRequestSchema, assistantCacheSchema, assistantContextSchema, cardTextSchema, copySchema, promptSchema, sourcesSchema,
} from "@/lib/schemas";
import type {
  AskError, AskRequest, AskResponse, AssistantCache, AssistantContext, CardText, CopyFile, FieldId, PromptFile,
  ScenarioKey, SourcesFile,
} from "@/lib/types";
import type { ZodType, ZodTypeDef } from "zod";

export const runtime = "nodejs";

const DEFAULT_SCENARIO = "cap300|actual";
const TIMEOUT_MS = 20_000;
const RATE_LIMIT = 20;            // requests per minute per IP
const RATE_WINDOW_MS = 60_000;
const REASONING_MAX_TOKENS = 1500;

/** Validate a bundled JSON file; log mismatches but keep serving so one stray field does not take the route down. */
function parse<T>(path: string, value: unknown, schema: ZodType<T, ZodTypeDef, unknown>): T {
  const result = schema.safeParse(value);
  if (!result.success) console.error(`[ask] ${path} does not match the contract`, result.error.issues.slice(0, 10));
  return result.success ? result.data : (value as T);
}

const prompt = parse<PromptFile>("assistant/prompt.json", promptJson, promptSchema);
const copy = parse<CopyFile>("content/copy.json", copyJson, copySchema);
const cardText = parse<CardText>("content/card_text.json", cardTextJson, cardTextSchema);
const sources = parse<SourcesFile>("sources.json", sourcesJson, sourcesSchema);
const contexts: Record<FieldId, AssistantContext> = {
  f1: parse("field/f1/assistant_context.json", f1Context, assistantContextSchema),
  f2: parse("field/f2/assistant_context.json", f2Context, assistantContextSchema),
  f3: parse("field/f3/assistant_context.json", f3Context, assistantContextSchema),
};
const caches: Record<FieldId, AssistantCache> = {
  f1: parse("field/f1/assistant_cache.json", f1Cache, assistantCacheSchema),
  f2: parse("field/f2/assistant_cache.json", f2Cache, assistantCacheSchema),
  f3: parse("field/f3/assistant_cache.json", f3Cache, assistantCacheSchema),
};

const hits = new Map<string, number[]>();
function rateLimited(ip: string): boolean {
  const now = Date.now();
  const recent = (hits.get(ip) ?? []).filter((time) => now - time < RATE_WINDOW_MS);
  recent.push(now);
  hits.set(ip, recent);
  if (hits.size > 5000) hits.clear();
  return recent.length > RATE_LIMIT;
}

function fail(status: 400 | 429 | 503, error: AskError["error"] | "rate_limited", message: string) {
  return NextResponse.json({ error, message }, { status });
}

const en = (key: string) => copy.strings?.[key]?.en ?? key;

function scenarioLabel(scenario: ScenarioKey): string {
  const [cap, climate] = scenario.split("|");
  return `${en(`constraints.cap.${cap}`)}, ${en(`climate.${climate}`)}`;
}

function topRotations(ids: AskRequest["top_rotations"]): string {
  if (!ids?.length) return "not given";
  return ids.map((id) => `${id} (${cardText.rotations?.[id]?.name.en ?? id})`).join(", ");
}

function fillTemplate(template: string, values: Record<string, string>): string {
  return template.replace(/\{([a-z_]+)\}/g, (match, key: string) => (key in values ? values[key] : match));
}

/** Shown when the provider is rate-limited: points to the suggested questions, whose answers are cached. */
function busyText(lang: AskRequest["lang"]): string {
  const key = "assistant.busy";
  const fallback = {
    en: "The assistant is busy right now. Try one of the suggested questions below. Their answers are ready.",
    es: "El asistente está ocupado ahora. Pruebe una de las preguntas sugeridas abajo. Sus respuestas ya están listas.",
  };
  return copy.strings?.[key]?.[lang] ?? fallback[lang];
}

function citations(answer: string): AskResponse["citations"] {
  const tags = new Set([...answer.matchAll(/\[([A-Za-z0-9]+)\]/g)].map((match) => match[1]));
  return sources.sources.filter((source) => tags.has(source.tag)).map(({ tag, name, url }) => ({ tag, name, url }));
}

function readAnswer(payload: unknown): string | null {
  const choice = (payload as { choices?: { message?: { content?: unknown } }[] })?.choices?.[0];
  const content = choice?.message?.content;
  return typeof content === "string" && content.trim() ? content.trim() : null;
}

export async function POST(request: NextRequest) {
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  if (rateLimited(ip)) return fail(429, "rate_limited", "Too many questions. Wait a minute and try again.");

  let raw: unknown;
  try {
    raw = await request.json();
  } catch {
    return fail(400, "bad_request", "Body must be JSON.");
  }
  const parsed = askRequestSchema.safeParse(raw);
  if (!parsed.success) {
    return fail(400, "bad_request", parsed.error.issues.map((issue) => `${issue.path.join(".") || "body"}: ${issue.message}`).join("; "));
  }
  const input = parsed.data;

  // 1. Suggested question → cached answer, never the LLM.
  if (input.question_id) {
    const cached = caches[input.field_id].answers?.[input.question_id]?.[input.lang];
    if (!cached) return fail(400, "bad_request", `Unknown question_id ${input.question_id}.`);
    const response: AskResponse = {
      ...cached,
      cached: true,
      provider: "cache",
      ...(input.scenario !== DEFAULT_SCENARIO ? { notice: "scenario_mismatch" as const } : {}),
    };
    return NextResponse.json(response);
  }
  const question = input.question as string;

  // 2-3. Facts for this scenario, prompt template filled.
  const context = contexts[input.field_id];
  // Keep the prompt small (free tiers allow ~8k tokens a minute): this scenario only, and only
  // rotation facts for R0 and the rotations on screen.
  const onScreen = new Set<string>(["R0", ...(input.top_rotations ?? [])]);
  const facts = context.facts.filter((fact) => (!fact.scenario || fact.scenario === input.scenario)
    && (!fact.rotation_id || !input.top_rotations?.length || onScreen.has(fact.rotation_id)));
  const factsBlock = facts.map((fact) => `- (${fact.id}) ${fact.text} [${fact.source}]`).join("\n");
  const system = fillTemplate(prompt.system, {
    field_name: context.field_name,
    lang_name: input.lang === "es" ? "Spanish" : "English",
    scenario_label: scenarioLabel(input.scenario),
    top_rotations: topRotations(input.top_rotations),
    facts_block: factsBlock,
  });

  const { LLM_PROVIDER, LLM_BASE_URL, LLM_MODEL, LLM_API_KEY } = process.env;
  if (!LLM_BASE_URL || !LLM_MODEL || !LLM_API_KEY) {
    return fail(503, "llm_unavailable", "The assistant is not configured. Use a suggested question.");
  }

  // 4. OpenAI-compatible chat completion with a 20 s timeout.
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    // Reasoning models (gpt-oss) spend max_tokens on hidden reasoning first; give them room and keep reasoning short.
    const reasoning = LLM_MODEL.startsWith("openai/gpt-oss");
    const call = () => fetch(`${LLM_BASE_URL.replace(/\/+$/, "")}/chat/completions`, {
      method: "POST",
      headers: { "content-type": "application/json", authorization: `Bearer ${LLM_API_KEY}` },
      body: JSON.stringify({
        model: LLM_MODEL,
        messages: [{ role: "system", content: system }, ...(input.history ?? []).slice(-6), { role: "user", content: question }],
        temperature: prompt.temperature,
        max_tokens: reasoning ? Math.max(prompt.max_tokens, REASONING_MAX_TOKENS) : prompt.max_tokens,
        ...(reasoning ? { reasoning_effort: "low" } : {}),
      }),
      signal: controller.signal,
    });

    let answer: string | null = null;
    let limited = false;
    for (let attempt = 0; attempt < 2 && !answer; attempt += 1) {
      const upstream = await call();
      if (upstream.status === 429) {
        limited = true;
        // One retry when the provider asks for a short wait; otherwise give up now.
        const wait = Number(upstream.headers.get("retry-after"));
        if (attempt === 0 && wait > 0 && wait <= 8) { await new Promise((resolve) => setTimeout(resolve, wait * 1000)); continue; }
        break;
      }
      limited = false;
      if (!upstream.ok) {
        console.warn(`[ask] provider returned ${upstream.status}`);
        return fail(503, "llm_unavailable", "The assistant provider returned an error.");
      }
      answer = readAnswer(await upstream.json());   // empty content (reasoning ran out of tokens) → retry once
      if (!answer) console.warn("[ask] provider returned an empty answer");
    }
    if (!answer && limited) {
      console.warn("[ask] provider rate limit; sending the busy answer");
      const busy: AskResponse = { answer_md: busyText(input.lang), citations: [], numbers: [], cached: true, provider: "cache", model: "none" };
      return NextResponse.json(busy);
    }
    if (!answer) return fail(503, "llm_unavailable", "The assistant provider returned an empty answer.");

    // 5. Number check and citations.
    const response: AskResponse = {
      answer_md: answer,
      citations: citations(answer),
      numbers: checkNumbers(answer, facts),
      cached: false,
      provider: LLM_PROVIDER === "gemini" ? "gemini" : "groq",
      model: LLM_MODEL,
    };
    return NextResponse.json(response);
  } catch (error) {
    // 6. Timeout or network failure → 503; the UI falls back to the suggested-question chips.
    console.warn(`[ask] ${error instanceof Error && error.name === "AbortError" ? "timed out" : "request failed"}`);
    return fail(503, "llm_unavailable", "The assistant did not answer in time.");
  } finally {
    clearTimeout(timer);
  }
}
