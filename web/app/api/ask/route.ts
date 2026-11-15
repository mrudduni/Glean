import { NextRequest, NextResponse } from "next/server";
import prompt from "@/public/data/content/prompt.json";
import copy from "@/public/data/content/copy.json";
import glossary from "@/public/data/content/glossary.json";
import sources from "@/public/data/sources.json";
import f1Context from "@/public/data/field/f1/assistant_context.json";
import f2Context from "@/public/data/field/f2/assistant_context.json";
import f3Context from "@/public/data/field/f3/assistant_context.json";
import f1Cache from "@/public/data/field/f1/assistant_cache.json";
import f2Cache from "@/public/data/field/f2/assistant_cache.json";
import f3Cache from "@/public/data/field/f3/assistant_cache.json";
import { checkNumbers, type Fact } from "@/lib/numberCheck";
import {
  assistantCacheSchema, assistantContextSchema, assistantRequestSchema,
  copySchema, glossarySchema, promptSchema, sourcesSchema,
} from "@/lib/schemas";
import type { AssistantResponse, FieldId, Lang, ScenarioId } from "@/lib/types";
import type { ZodType } from "zod";

export const runtime = "nodejs";

function parseStatic<T>(path: string, value: unknown, schema: ZodType<T>): T {
  const parsed = schema.safeParse(value);
  if (!parsed.success) {
    if (process.env.NODE_ENV === "development") console.error(`Invalid data at ${path}`, parsed.error.issues);
    throw new Error(`Data validation failed for ${path}`);
  }
  return parsed.data;
}

const promptData = parseStatic("/data/content/prompt.json", prompt, promptSchema);
const copyData = parseStatic("/data/content/copy.json", copy, copySchema);
const glossaryData = parseStatic("/data/content/glossary.json", glossary, glossarySchema);
const sourcesData = parseStatic("/data/sources.json", sources, sourcesSchema);
const fieldContexts: Record<FieldId, { facts: Fact[] }> = {
  f1: parseStatic("/data/field/f1/assistant_context.json", f1Context, assistantContextSchema),
  f2: parseStatic("/data/field/f2/assistant_context.json", f2Context, assistantContextSchema),
  f3: parseStatic("/data/field/f3/assistant_context.json", f3Context, assistantContextSchema),
};
const fieldCaches: Record<FieldId, { answers: Record<string, Record<Lang, string>> }> = {
  f1: parseStatic("/data/field/f1/assistant_cache.json", f1Cache, assistantCacheSchema),
  f2: parseStatic("/data/field/f2/assistant_cache.json", f2Cache, assistantCacheSchema),
  f3: parseStatic("/data/field/f3/assistant_cache.json", f3Cache, assistantCacheSchema),
};
const requestsByIp = new Map<string, number[]>();

function limited(ip: string): boolean {
  const now = Date.now();
  const timestamps = (requestsByIp.get(ip) || []).filter((timestamp) => now - timestamp < 60_000);
  if (timestamps.length >= 20) {
    requestsByIp.set(ip, timestamps);
    return true;
  }
  timestamps.push(now);
  requestsByIp.set(ip, timestamps);
  return false;
}

function scenarioLabel(scenario: ScenarioId): string {
  const [cap, climate] = scenario.split("|");
  const capKey = cap === "dryland" ? "priority.cap.dryland" : `priority.cap.${cap.slice(3)}`;
  const capText = copyData.strings[capKey]?.en || cap;
  const climateText = copyData.strings[climate === "actual" ? "priority.actual" : "priority.hotdry"]?.en || climate;
  return `${capText}; ${climateText}`;
}

function factsWithSources(facts: Fact[]): string {
  return facts.map((fact) => {
    const sourceNames = fact.source_ids.map((id) => sourcesData.sources[id]?.name.en).filter(Boolean);
    return `${fact.id}: ${fact.text}${sourceNames.length ? ` Sources: ${sourceNames.join(", ")}.` : ""}`;
  }).join("\n");
}

function checkPromptTemplate(values: Record<string, string>): string {
  return promptData.template.replace(/\{([a-z_]+)\}/g, (_match, key: string) => values[key] || "—");
}

export async function POST(request: NextRequest) {
  const forwardedFor = request.headers.get("x-forwarded-for");
  const ip = forwardedFor?.split(",")[0]?.trim() || "unknown";
  if (limited(ip)) return NextResponse.json({ error: "Rate limit reached." }, { status: 429 });

  let raw: unknown;
  try {
    raw = await request.json();
  } catch {
    return NextResponse.json({ error: "Request body must be valid JSON." }, { status: 400 });
  }
  const parsed = assistantRequestSchema.safeParse(raw);
  if (!parsed.success) return NextResponse.json({ error: "Invalid assistant request." }, { status: 400 });

  const input = parsed.data;
  const facts = fieldContexts[input.field_id].facts;
  const questionId = input.question_id;
  if (questionId) {
    const answer = fieldCaches[input.field_id].answers[questionId]?.[input.lang];
    if (!answer) return NextResponse.json({ error: "Unknown suggested question." }, { status: 400 });
    const result: AssistantResponse = { answer, numbers: checkNumbers(answer, facts), notice: "using_cache" };
    return NextResponse.json(result);
  }

  if (process.env.LLM_PROVIDER !== "openai-compatible" ||
      !process.env.LLM_BASE_URL || !process.env.LLM_MODEL || !process.env.LLM_API_KEY) {
    return NextResponse.json({ error: "Assistant provider is not configured." }, { status: 503 });
  }

  const localizedGlossary = Object.entries(glossaryData.entries)
    .map(([key, entry]) => `${key}: ${entry.short[input.lang] || entry.short.en}`)
    .join("\n");
  const factBlock = `${factsWithSources(facts)}\nField guide:\n${localizedGlossary}\nShown rotations: ${input.top_rotations.join(", ")}`;
  const systemPrompt = checkPromptTemplate({
    lang_name: input.lang === "en" ? "English" : "Spanish",
    field_id: input.field_id,
    scenario_label: scenarioLabel(input.scenario),
    facts_block: factBlock,
    question: input.question,
  });
  const history = input.history.slice(-6).map((turn) => ({ role: turn.role, content: turn.content }));
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20_000);

  try {
    const endpoint = `${process.env.LLM_BASE_URL.replace(/\/+$/, "")}/chat/completions`;
    const upstream = await fetch(endpoint, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${process.env.LLM_API_KEY}`,
      },
      body: JSON.stringify({
        model: process.env.LLM_MODEL,
        messages: [{ role: "system", content: systemPrompt }, ...history, { role: "user", content: input.question }],
        temperature: 0.2,
      }),
      signal: controller.signal,
    });
    if (!upstream.ok) return NextResponse.json({ error: "Assistant provider returned an error." }, { status: 503 });
    const payload: unknown = await upstream.json();
    const answer = typeof payload === "object" && payload !== null &&
      "choices" in payload && Array.isArray(payload.choices) &&
      typeof payload.choices[0] === "object" && payload.choices[0] !== null &&
      "message" in payload.choices[0] && typeof payload.choices[0].message === "object" &&
      payload.choices[0].message !== null && "content" in payload.choices[0].message &&
      typeof payload.choices[0].message.content === "string"
      ? payload.choices[0].message.content
      : null;
    if (!answer) return NextResponse.json({ error: "Assistant provider returned an invalid answer." }, { status: 503 });
    const result: AssistantResponse = { answer, numbers: checkNumbers(answer, facts) };
    return NextResponse.json(result);
  } catch {
    return NextResponse.json({ error: "Assistant request timed out or could not reach its provider." }, { status: 503 });
  } finally {
    clearTimeout(timeout);
  }
}
