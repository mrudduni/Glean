// Bring-your-own-key and the server fallback provider in POST /api/ask.
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import { POST } from "@/app/api/ask/route";

const base = { field_id: "f1", lang: "en", scenario: "cap300|actual" } as const;
const env = { LLM_PROVIDER: "groq", LLM_BASE_URL: "https://api.groq.com/openai/v1", LLM_MODEL: "server-model", LLM_API_KEY: "server-key" };
const userHeaders = {
  "x-user-llm-key": "user-secret-key",
  "x-user-llm-base-url": "https://generativelanguage.googleapis.com/v1beta/openai",
  "x-user-llm-model": "gemini-flash",
};
const ok = (content = "Fine [POWER].") => Response.json({ choices: [{ message: { content } }] });

const ask = (body: unknown, headers: Record<string, string> = {}) =>
  POST(new NextRequest("http://localhost/api/ask", {
    method: "POST",
    headers: { "content-type": "application/json", "x-forwarded-for": `p-${Math.random()}`, ...headers },
    body: JSON.stringify(body),
  }));

describe("bring your own key", () => {
  beforeEach(() => { for (const [k, v] of Object.entries(env)) vi.stubEnv(k, v); });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("sends the user's key, base URL and model instead of the server's", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(ok());
    vi.stubGlobal("fetch", fetchSpy);
    const json = await (await ask({ ...base, question: "Water?" }, userHeaders)).json();
    const [url, init] = fetchSpy.mock.calls[0];
    expect(url).toBe("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions");
    expect(init.headers.authorization).toBe("Bearer user-secret-key");
    expect(JSON.parse(init.body).model).toBe("gemini-flash");
    expect(json.provider).toBe("gemini");
    expect(json.model).toBe("gemini-flash");
  });

  it("does not fall back to the server key when the user's key is rejected, and never echoes it", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(new Response("bad key", { status: 401 }));
    vi.stubGlobal("fetch", fetchSpy);
    const response = await ask({ ...base, question: "Water?" }, userHeaders);
    const text = await response.text();
    expect(response.status).toBe(503);
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(text).toContain("401");
    expect(text).not.toContain("user-secret-key");
  });

  it("returns 503, not the busy answer, when the user's provider is rate-limited", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("slow", { status: 429 })));
    const response = await ask({ ...base, question: "Water?" }, userHeaders);
    expect(response.status).toBe(503);
    expect((await response.json()).message).toMatch(/429/);
  });

  it("rejects non-https and non-allowlisted base URLs (SSRF guard)", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    for (const url of ["http://api.groq.com/openai/v1", "https://169.254.169.254/latest", "https://evil.example.com/v1", "not a url"]) {
      const response = await ask({ ...base, question: "Water?" }, { ...userHeaders, "x-user-llm-base-url": url });
      expect(response.status).toBe(400);
    }
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("allows a custom https URL only when the server enables it", async () => {
    vi.stubEnv("ALLOW_CUSTOM_LLM_URL", "1");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(ok()));
    const json = await (await ask({ ...base, question: "Water?" }, { ...userHeaders, "x-user-llm-base-url": "https://llm.example.com/v1" })).json();
    expect(json.provider).toBe("custom");
  });

  it("ignores the user's key for suggested questions", async () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    const json = await (await ask({ ...base, question_id: "q1" }, userHeaders)).json();
    expect(json.provider).toBe("cache");
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});

describe("server fallback provider", () => {
  beforeEach(() => {
    for (const [k, v] of Object.entries(env)) vi.stubEnv(k, v);
    vi.stubEnv("LLM_FALLBACK_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai");
    vi.stubEnv("LLM_FALLBACK_MODEL", "gemini-flash");
    vi.stubEnv("LLM_FALLBACK_API_KEY", "fallback-key");
  });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("answers from the fallback when the primary is rate-limited", async () => {
    const fetchSpy = vi.fn()
      .mockResolvedValueOnce(new Response("cap", { status: 429 }))
      .mockResolvedValueOnce(ok());
    vi.stubGlobal("fetch", fetchSpy);
    const json = await (await ask({ ...base, question: "Water?" })).json();
    expect(json.provider).toBe("gemini");
    expect(json.model).toBe("gemini-flash");
    expect(fetchSpy.mock.calls[1][1].headers.authorization).toBe("Bearer fallback-key");
  });

  it("answers from the fallback when the primary has a server error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response("down", { status: 500 })).mockResolvedValueOnce(ok()));
    expect((await (await ask({ ...base, question: "Water?" })).json()).provider).toBe("gemini");
  });

  it("does not try the fallback after a 400 from the primary", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(new Response("bad", { status: 400 }));
    vi.stubGlobal("fetch", fetchSpy);
    expect((await (await ask({ ...base, question: "Water?" })).json()).provider).toBe("cache");
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it("sends the busy answer when both are rate-limited", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("cap", { status: 429 })));
    const json = await (await ask({ ...base, question: "Water?" })).json();
    expect(json.provider).toBe("cache");
  });
});

describe("production layout: Gemini primary, Groq gpt-oss fallback", () => {
  const prod = {
    LLM_PROVIDER: "gemini", LLM_BASE_URL: "https://generativelanguage.googleapis.com/v1beta/openai", LLM_MODEL: "gemini-3.5-flash", LLM_API_KEY: "gemini-key",
    LLM_FALLBACK_PROVIDER: "groq", LLM_FALLBACK_BASE_URL: "https://api.groq.com/openai/v1", LLM_FALLBACK_MODEL: "openai/gpt-oss-120b", LLM_FALLBACK_API_KEY: "groq-key",
  };
  beforeEach(() => { for (const [k, v] of Object.entries(prod)) vi.stubEnv(k, v); });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });
  const body = { ...base, question: "Water?" };

  it("primary ok: Gemini answers with low reasoning effort and room for thinking", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(ok());
    vi.stubGlobal("fetch", fetchSpy);
    const json = await (await ask(body)).json();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(json).toMatchObject({ provider: "gemini", model: "gemini-3.5-flash", cached: false });
    const sent = JSON.parse(fetchSpy.mock.calls[0][1].body);
    expect(sent.reasoning_effort).toBe("low");
    expect(sent.max_tokens).toBeGreaterThanOrEqual(1500);
  });

  it("primary 429: Groq answers and is reported as the provider", async () => {
    const fetchSpy = vi.fn().mockResolvedValueOnce(new Response("quota", { status: 429 })).mockResolvedValueOnce(ok());
    vi.stubGlobal("fetch", fetchSpy);
    const json = await (await ask(body)).json();
    expect(json).toMatchObject({ provider: "groq", model: "openai/gpt-oss-120b" });
    expect(fetchSpy.mock.calls[1][0]).toBe("https://api.groq.com/openai/v1/chat/completions");
    expect(JSON.parse(fetchSpy.mock.calls[1][1].body).reasoning_effort).toBe("low");
  });

  it("primary empty twice: Groq answers", async () => {
    const empty = () => Response.json({ choices: [{ message: { content: "" }, finish_reason: "length" }] });
    const fetchSpy = vi.fn().mockResolvedValueOnce(empty()).mockResolvedValueOnce(empty()).mockResolvedValueOnce(ok());
    vi.stubGlobal("fetch", fetchSpy);
    expect((await (await ask(body)).json()).provider).toBe("groq");
    expect(fetchSpy).toHaveBeenCalledTimes(3);
  });

  it("truncated answer (finish_reason length): retried at 3000 tokens, never shown cut off", async () => {
    const cut = () => Response.json({ choices: [{ message: { content: "Corn uses an average of 299 mm (11.8" }, finish_reason: "length" }] });
    const fetchSpy = vi.fn().mockResolvedValueOnce(cut()).mockResolvedValueOnce(ok("Corn uses 299 mm [WATER]."));
    vi.stubGlobal("fetch", fetchSpy);
    const json = await (await ask(body)).json();
    expect(json).toMatchObject({ provider: "gemini", answer_md: "Corn uses 299 mm [WATER]." });
    expect(JSON.parse(fetchSpy.mock.calls[0][1].body).max_tokens).toBe(1500);
    expect(JSON.parse(fetchSpy.mock.calls[1][1].body).max_tokens).toBe(3000);
  });

  it("truncated twice: Groq answers", async () => {
    const cut = () => Response.json({ choices: [{ message: { content: "La rotación se estima" }, finish_reason: "length" }] });
    const fetchSpy = vi.fn().mockResolvedValueOnce(cut()).mockResolvedValueOnce(cut()).mockResolvedValueOnce(ok());
    vi.stubGlobal("fetch", fetchSpy);
    expect((await (await ask(body)).json()).provider).toBe("groq");
    expect(fetchSpy).toHaveBeenCalledTimes(3);
  });

  it("primary timeout: Groq answers", async () => {
    const fetchSpy = vi.fn()
      .mockRejectedValueOnce(Object.assign(new Error("aborted"), { name: "AbortError" }))
      .mockResolvedValueOnce(ok());
    vi.stubGlobal("fetch", fetchSpy);
    expect((await (await ask(body)).json()).provider).toBe("groq");
  });

  it("both fail with 429: busy note from the cache", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("quota", { status: 429 })));
    const response = await ask(body);
    expect(response.status).toBe(200);
    expect(await response.json()).toMatchObject({ provider: "cache", cached: true, numbers: [] });
  });

  it("both fail with server errors: busy note, both tried", async () => {
    const fetchSpy = vi.fn().mockResolvedValue(new Response("down", { status: 503 }));
    vi.stubGlobal("fetch", fetchSpy);
    const response = await ask(body);
    expect(response.status).toBe(200);
    expect((await response.json()).provider).toBe("cache");
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });
});
