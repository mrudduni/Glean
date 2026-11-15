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
    expect((await ask({ ...base, question: "Water?" })).status).toBe(503);
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it("sends the busy answer when both are rate-limited", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("cap", { status: 429 })));
    const json = await (await ask({ ...base, question: "Water?" })).json();
    expect(json.provider).toBe("cache");
  });
});
