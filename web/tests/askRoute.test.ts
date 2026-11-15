import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import { POST } from "@/app/api/ask/route";
import context from "@/public/data/field/f1/assistant_context.json";

const ask = (body: unknown, ip = `test-${Math.random()}`) =>
  POST(new NextRequest("http://localhost/api/ask", {
    method: "POST",
    headers: { "content-type": "application/json", "x-forwarded-for": ip },
    body: typeof body === "string" ? body : JSON.stringify(body),
  }));

const base = { field_id: "f1", lang: "en", scenario: "cap300|actual" } as const;
const env = { LLM_PROVIDER: "groq", LLM_BASE_URL: "https://llm.test/v1", LLM_MODEL: "test-model", LLM_API_KEY: "test-key" };

describe("POST /api/ask", () => {
  beforeEach(() => { for (const [k, v] of Object.entries(env)) vi.stubEnv(k, v); });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); vi.useRealTimers(); });

  it("rejects bad requests with 400 bad_request", async () => {
    for (const body of ["not json", { ...base, field_id: "f9", question: "hi" }, { ...base }, { ...base, question: "x".repeat(501) }, { ...base, scenario: "cap999|actual", question: "hi" }, { ...base, question: "hi", history: Array(7).fill({ role: "user", content: "a" }) }]) {
      const response = await ask(body);
      expect(response.status).toBe(400);
      expect((await response.json()).error).toBe("bad_request");
    }
  });

  it("serves suggested questions from the cache without calling the LLM", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    const response = await ask({ ...base, question_id: "q1" });
    const json = await response.json();
    expect(response.status).toBe(200);
    expect(json.cached).toBe(true);
    expect(json.provider).toBe("cache");
    expect(json.notice).toBeUndefined();
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("flags scenario_mismatch for cached answers outside cap300|actual", async () => {
    const json = await (await ask({ ...base, scenario: "dryland|hotdry", question_id: "q1" })).json();
    expect(json.notice).toBe("scenario_mismatch");
  });

  it("returns 503 when the LLM is not configured", async () => {
    vi.stubEnv("LLM_API_KEY", "");
    const response = await ask({ ...base, question: "Why not alfalfa?" });
    expect(response.status).toBe(503);
    expect((await response.json()).error).toBe("llm_unavailable");
  });

  it("returns 503 when the provider fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(Object.assign(new Error("aborted"), { name: "AbortError" })));
    expect((await ask({ ...base, question: "Why not alfalfa?" })).status).toBe(503);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("nope", { status: 500 })));
    expect((await ask({ ...base, question: "Why not alfalfa?" })).status).toBe(503);
  });

  it("sends only this scenario's facts and number-checks the answer", async () => {
    const fact = context.facts.find((item) => item.scenario === "cap300|actual" && item.unit === "mm");
    const other = context.facts.find((item) => item.scenario && item.scenario !== "cap300|actual");
    expect(fact).toBeDefined();
    const fetchSpy = vi.fn().mockResolvedValue(Response.json({ choices: [{ message: { content: `It needs ${fact?.value} mm [MODEL] and 9999 mm [POWER].` } }] }));
    vi.stubGlobal("fetch", fetchSpy);
    const response = await ask({ ...base, question: "Water?", top_rotations: ["R0", "R2"], history: [{ role: "user", content: "hi" }] });
    const json = await response.json();
    expect(response.status).toBe(200);
    expect(json.cached).toBe(false);
    expect(json.provider).toBe("groq");
    expect(json.model).toBe("test-model");
    expect(json.numbers.map((n: { text: string; verified: boolean }) => [n.text, n.verified])).toEqual([[`${fact?.value} mm`, true], ["9999 mm", false]]);
    expect(json.citations.map((c: { tag: string }) => c.tag).sort()).toEqual(["MODEL", "POWER"]);

    const [url, init] = fetchSpy.mock.calls[0];
    expect(url).toBe("https://llm.test/v1/chat/completions");
    expect(init.headers.authorization).toBe("Bearer test-key");
    const sent = JSON.parse(init.body);
    expect(sent.messages.map((m: { role: string }) => m.role)).toEqual(["system", "user", "user"]);
    const system: string = sent.messages[0].content;
    expect(system).toContain(`(${fact?.id})`);
    if (other) expect(system).not.toContain(`(${other.id})`);
    expect(system).toMatch(/R2 \(/);
    expect(system).not.toMatch(/\{(field_name|lang_name|scenario_label|top_rotations|facts_block)\}/);
  });

  it("gives gpt-oss models room to reason and retries an empty answer once", async () => {
    vi.stubEnv("LLM_MODEL", "openai/gpt-oss-120b");
    const fetchSpy = vi.fn()
      .mockResolvedValueOnce(Response.json({ choices: [{ message: { content: "" }, finish_reason: "length" }] }))
      .mockResolvedValueOnce(Response.json({ choices: [{ message: { content: "Fine [POWER]." } }] }));
    vi.stubGlobal("fetch", fetchSpy);
    const response = await ask({ ...base, question: "Water?" });
    expect(response.status).toBe(200);
    expect(fetchSpy).toHaveBeenCalledTimes(2);
    const sent = JSON.parse(fetchSpy.mock.calls[0][1].body);
    expect(sent.reasoning_effort).toBe("low");
    expect(sent.max_tokens).toBeGreaterThanOrEqual(1500);
  });

  it("does not send reasoning_effort to other models", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(Response.json({ choices: [{ message: { content: "Fine." } }] }));
    vi.stubGlobal("fetch", fetchSpy);
    await ask({ ...base, question: "Water?" });
    expect(JSON.parse(fetchSpy.mock.calls[0][1].body).reasoning_effort).toBeUndefined();
  });

  it("answers with a busy note pointing to suggested questions when rate limited", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("slow down", { status: 429 })));
    const response = await ask({ ...base, lang: "es", question: "Water?" });
    const json = await response.json();
    expect(response.status).toBe(200);
    expect(json.cached).toBe(true);
    expect(json.provider).toBe("cache");
    expect(json.answer_md).toMatch(/pregunta/i);
  });

  it("sends only facts for R0 and the rotations on screen", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(Response.json({ choices: [{ message: { content: "Fine." } }] }));
    vi.stubGlobal("fetch", fetchSpy);
    await ask({ ...base, question: "Water?", top_rotations: ["R0", "R2"] });
    const system: string = JSON.parse(fetchSpy.mock.calls[0][1].body).messages[0].content;
    const rotationFacts = context.facts.filter((f) => f.rotation_id && f.scenario === "cap300|actual");
    for (const fact of rotationFacts) {
      const included = system.includes(`(${fact.id})`);
      expect(included).toBe(fact.rotation_id === "R0" || fact.rotation_id === "R2");
    }
  });

  it("rate limits after 20 requests a minute from one IP", async () => {
    let last = 0;
    for (let i = 0; i < 21; i += 1) last = (await ask({ ...base, question_id: "q1" }, "same-ip")).status;
    expect(last).toBe(429);
  });
});
