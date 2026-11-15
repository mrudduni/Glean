"use client";

import { Children, Fragment, useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import ReactMarkdown from "react-markdown";
import { ArrowUpRight, Bot, CircleCheck, KeyRound, LoaderCircle, MessageCircle, Send, X } from "lucide-react";
import type { AskRequest, AskResponse, AssistantQuestionsFile, FieldId, Lang, RotationId, ScenarioKey, SourcesFile } from "@/lib/types";
import { askResponseSchema } from "@/lib/schemas";
import { findNumbers } from "@/lib/numberCheck";
import { loc, type TFunction } from "@/lib/i18n";

/** Bring your own key. Kept in this tab only (sessionStorage), sent per request in headers, never in the URL or body. */
type OwnProvider = "groq" | "gemini" | "custom";
interface OwnKey { on: boolean; provider: OwnProvider; baseUrl: string; model: string; key: string }
const OWN_KEY_STORE = "glean_own_llm";
const PRESET_URL: Record<Exclude<OwnProvider, "custom">, string> = {
  groq: "https://api.groq.com/openai/v1",
  gemini: "https://generativelanguage.googleapis.com/v1beta/openai",
};
const MODEL_HINT: Record<OwnProvider, string> = { groq: "openai/gpt-oss-120b", gemini: "gemini-2.5-flash", custom: "model id" };
const NO_KEY: OwnKey = { on: false, provider: "groq", baseUrl: "", model: "", key: "" };

function readOwnKey(): OwnKey {
  try {
    const raw = sessionStorage.getItem(OWN_KEY_STORE);
    return raw ? { ...NO_KEY, ...(JSON.parse(raw) as Partial<OwnKey>) } : NO_KEY;
  } catch {
    return NO_KEY;
  }
}

function ownKeyHeaders(own: OwnKey): Record<string, string> | null {
  if (!own.on || !own.key.trim() || !own.model.trim()) return null;
  const baseUrl = own.provider === "custom" ? own.baseUrl.trim() : PRESET_URL[own.provider];
  if (!baseUrl) return null;
  return { "x-user-llm-key": own.key.trim(), "x-user-llm-base-url": baseUrl, "x-user-llm-model": own.model.trim() };
}

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  response?: AskResponse;
}

export function AssistantDrawer({
  fieldId, scenario, shownIds, questions, sources, t, lang,
}: {
  fieldId: FieldId;
  scenario: ScenarioKey;
  shownIds: RotationId[];
  questions: AssistantQuestionsFile | null;
  sources: SourcesFile;
  t: TFunction;
  lang: Lang;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [waiting, setWaiting] = useState(false);
  const [error, setError] = useState<string | boolean>(false);
  const [own, setOwn] = useState<OwnKey>(NO_KEY);
  useEffect(() => { setOwn(readOwnKey()); }, []);
  const updateOwn = (patch: Partial<OwnKey>) => setOwn((current) => {
    const next = { ...current, ...patch };
    try { sessionStorage.setItem(OWN_KEY_STORE, JSON.stringify(next)); } catch { /* private mode: keep it in memory only */ }
    return next;
  });
  const panelRef = useRef<HTMLElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fabRef = useRef<HTMLButtonElement>(null);
  const chatEnd = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([]);
    setError(false);
  }, [fieldId]);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ block: "end" });
  }, [messages, waiting]);

  useEffect(() => {
    if (!open) return;
    const fab = fabRef.current;
    inputRef.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
        return;
      }
      if (event.key !== "Tab" || !panelRef.current) return;
      const focusable = [...panelRef.current.querySelectorAll<HTMLElement>("button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), summary, a[href]")];
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      fab?.focus();
    };
  }, [open]);

  const send = async (text: string, questionId?: string) => {
    const question = text.trim();
    if (!question || waiting || question.length > 500) return;
    const history = messages.slice(-6).map(({ role, content }) => ({ role, content: content.slice(0, 1500) }));
    setMessages((current) => [...current, { id: Date.now(), role: "user", content: question }]);
    setDraft("");
    setWaiting(true);
    setError(false);
    const body: AskRequest = {
      field_id: fieldId, lang, scenario, top_rotations: shownIds, history,
      ...(questionId ? { question_id: questionId } : { question }),
    };
    // Suggested questions are answered from the cache, so the user's key is only sent with free text.
    const userHeaders = questionId ? null : ownKeyHeaders(own);
    try {
      const response = await fetch("/api/ask", { method: "POST", headers: { "content-type": "application/json", ...(userHeaders ?? {}) }, body: JSON.stringify(body) });
      if (!response.ok) {
        // With the user's own key, show the server's reason (it never contains the key).
        const reason = userHeaders ? ((await response.json().catch(() => null)) as { message?: string } | null)?.message : undefined;
        setError(reason || true);
        throw new Error(`Assistant request failed (${response.status})`);
      }
      const parsed = askResponseSchema.safeParse(await response.json());
      if (!parsed.success) {
        console.error("[assistant] response does not match the contract", parsed.error.issues);
        throw new Error("Invalid assistant response");
      }
      setMessages((current) => [...current, { id: Date.now() + 1, role: "assistant", content: parsed.data.answer_md, response: parsed.data }]);
    } catch (reason) {
      console.warn("[assistant]", reason instanceof Error ? reason.message : reason);
      setError((current) => current || true);
    } finally {
      setWaiting(false);
    }
  };

  const chips = questions?.questions ?? [];
  return (
    <>
      <button ref={fabRef} className="assistant-fab" type="button" aria-haspopup="dialog" aria-expanded={open} onClick={() => setOpen(true)}>
        <MessageCircle size={18} aria-hidden="true" /><span>{t("assistant.title")}</span>
      </button>
      {/* Portal to <body> so the drawer stacks above the site header, not inside <main>'s stacking context. */}
      {open && createPortal(
        <div className="assistant-overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
          <aside className="assistant-drawer" role="dialog" aria-modal="true" aria-labelledby="assistant-heading" ref={panelRef}>
            <header className="assistant-header">
              <span className="assistant-avatar"><Bot size={19} aria-hidden="true" /></span>
              <div><h2 id="assistant-heading">{t("assistant.title")}</h2><p>{t("assistant.subtitle", "Answers use only this field's data. Every number is checked.")}</p></div>
              <button type="button" className="icon-button" aria-label={t("assistant.close", "Close")} onClick={() => setOpen(false)}><X size={18} aria-hidden="true" /></button>
            </header>
            <div className="assistant-main">
              <div className="assistant-chat" aria-live="polite">
                {messages.map((message) => (
                  <article className={`chat-message ${message.role}`} key={message.id}>
                    {message.role === "assistant" && <span className="chat-avatar"><Bot size={13} aria-hidden="true" /></span>}
                    <div className="chat-bubble">
                      {message.response?.notice && <div className="assistant-notice" role="status">{t("assistant.using_cache")}</div>}
                      {message.response ? <Answer response={message.response} sources={sources} t={t} /> : <p>{message.content}</p>}
                    </div>
                  </article>
                ))}
                {waiting && <div className="assistant-waiting"><LoaderCircle size={15} className="spin" aria-hidden="true" />{t("assistant.waiting", "Checking the field data")}</div>}
                {error && <div className="assistant-error" role="alert">{typeof error === "string" ? error : t("assistant.error")}</div>}
                <div ref={chatEnd} />
              </div>
              {chips.length > 0 && (
                <div className="suggested-questions">
                  <span>{t("assistant.suggested")}</span>
                  {chips.map((question) => (
                    <button className={error ? "question-chip attention" : "question-chip"} key={question.id} type="button" disabled={waiting} onClick={() => void send(loc(question.text, lang), question.id)}>
                      {loc(question.text, lang)}<ArrowUpRight size={15} aria-hidden="true" />
                    </button>
                  ))}
                </div>
              )}
            </div>
            <details className="own-key">
              <summary><KeyRound size={14} aria-hidden="true" />{t("assistant.own_key", "Use my own key")}{own.on && ownKeyHeaders(own) ? <b> · {t("assistant.own_key_on", "on")}</b> : null}</summary>
              <div className="own-key-body">
                <label className="own-key-toggle">
                  <input type="checkbox" checked={own.on} onChange={(event) => updateOwn({ on: event.currentTarget.checked })} />
                  {t("assistant.own_key_toggle", "Answer free-text questions with my key")}
                </label>
                <label>{t("assistant.own_key_provider", "Provider")}
                  <select value={own.provider} onChange={(event) => updateOwn({ provider: event.currentTarget.value as OwnProvider })}>
                    <option value="groq">Groq</option>
                    <option value="gemini">Gemini</option>
                    <option value="custom">{t("assistant.own_key_custom", "Other (base URL)")}</option>
                  </select>
                </label>
                {own.provider === "custom" && (
                  <label>{t("assistant.own_key_url", "Base URL (https)")}
                    <input type="url" inputMode="url" value={own.baseUrl} placeholder="https://..." autoComplete="off" spellCheck={false} onChange={(event) => updateOwn({ baseUrl: event.currentTarget.value })} />
                  </label>
                )}
                <label>{t("assistant.own_key_model", "Model id")}
                  <input type="text" value={own.model} placeholder={MODEL_HINT[own.provider]} autoComplete="off" spellCheck={false} onChange={(event) => updateOwn({ model: event.currentTarget.value })} />
                </label>
                <label>{t("assistant.own_key_key", "API key")}
                  <input type="password" value={own.key} autoComplete="off" spellCheck={false} onChange={(event) => updateOwn({ key: event.currentTarget.value })} />
                </label>
                <p>{t("assistant.own_key_note", "Your key stays in this browser tab and is sent only with your questions. Suggested questions never use it.")}</p>
              </div>
            </details>
            <form className="assistant-form" onSubmit={(event) => { event.preventDefault(); void send(draft); }}>
              <label className="sr-only" htmlFor="assistant-question">{t("assistant.placeholder")}</label>
              <textarea
                id="assistant-question" ref={inputRef} value={draft} maxLength={500} rows={2}
                placeholder={t("assistant.placeholder")} disabled={waiting}
                onChange={(event) => setDraft(event.currentTarget.value)}
                onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void send(draft); } }}
              />
              <div className="assistant-form-bottom">
                <span>{draft.length}/500</span>
                <button type="submit" disabled={!draft.trim() || waiting}><Send size={15} aria-hidden="true" /><span>{t("assistant.send")}</span></button>
              </div>
            </form>
          </aside>
        </div>,
        document.body,
      )}
    </>
  );
}

/** Markdown answer with [TAG] chips and number-check marks (README §9 step 5). */
function Answer({ response, sources, t }: { response: AskResponse; sources: SourcesFile; t: TFunction }) {
  // Stateless lookup: markdown renderers can run more than once (StrictMode), so never consume a queue.
  const take = (text: string) => response.numbers.find((item) => item.text === text);

  const markText = (text: string, key: string): ReactNode[] => {
    const out: ReactNode[] = [];
    text.split(/(\[[A-Za-z0-9]+\])/g).forEach((part, i) => {
      const tag = part.match(/^\[([A-Za-z0-9]+)\]$/)?.[1];
      if (tag) {
        const source = sources.sources.find((item) => item.tag === tag) ?? response.citations.find((item) => item.tag === tag);
        out.push(source
          ? <a key={`${key}-${i}`} className="assistant-source-chip" href={source.url} target="_blank" rel="noreferrer" title={source.name}>{tag}</a>
          : <span key={`${key}-${i}`} className="assistant-source-chip">{tag}</span>);
        return;
      }
      let cursor = 0;
      for (const found of findNumbers(part)) {
        const item = take(found.text);
        if (!item) continue;
        out.push(part.slice(cursor, found.index));
        out.push(item.verified
          ? <span key={`${key}-${i}-${found.index}`} className="verified-number" title={`${t("assistant.verified")}: ${item.fact_id}`}>{part.slice(found.index, found.index + found.text.length)}<CircleCheck size={11} aria-label={t("assistant.verified")} /></span>
          : <span key={`${key}-${i}-${found.index}`} className="unverified-number">{part.slice(found.index, found.index + found.text.length)}<small>{t("assistant.unverified")}</small></span>);
        cursor = found.index + found.text.length;
      }
      out.push(part.slice(cursor));
    });
    return out;
  };

  const walk = (children: ReactNode, key: string): ReactNode =>
    Children.map(children, (child, i) => (
      typeof child === "string" ? <Fragment key={`${key}-${i}`}>{markText(child, `${key}-${i}`)}</Fragment> : child
    ));

  return (
    <div className="markdown-answer">
      <ReactMarkdown components={{
        p: ({ children }) => <p>{walk(children, "p")}</p>,
        li: ({ children }) => <li>{walk(children, "li")}</li>,
        strong: ({ children }) => <strong>{walk(children, "s")}</strong>,
        em: ({ children }) => <em>{walk(children, "e")}</em>,
      }}>{response.answer_md}</ReactMarkdown>
    </div>
  );
}
