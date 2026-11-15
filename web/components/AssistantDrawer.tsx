"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { ArrowUpRight, Bot, LoaderCircle, MessageCircle, Send, X } from "lucide-react";
import { t } from "@/lib/i18n";
import type {
  AssistantNumber, AssistantQuestion, AssistantResponse, CopyFile, FieldId, Lang, ScenarioId, SourcesFile,
} from "@/lib/types";

interface Message {
  role: "user" | "assistant";
  content: string;
  numbers?: AssistantNumber[];
  notice?: string;
  id: number;
}

export function AssistantDrawer({
  fieldId,
  scenario,
  shownIds,
  questions,
  sources,
  copy,
  lang,
}: {
  fieldId: FieldId;
  scenario: ScenarioId;
  shownIds: string[];
  questions: AssistantQuestion[];
  sources: SourcesFile;
  copy: CopyFile["strings"];
  lang: Lang;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [waiting, setWaiting] = useState(false);
  const [error, setError] = useState(false);
  const [needsAttention, setNeedsAttention] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const panelRef = useRef<HTMLElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!open) return;
    previousFocus.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    inputRef.current?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
      }
      if (event.key !== "Tab" || !panelRef.current) return;
      const focusable = panelRef.current.querySelectorAll<HTMLElement>("button:not([disabled]), textarea:not([disabled]), a[href]");
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      previousFocus.current?.focus();
    };
  }, [open]);

  const send = async (question: string, questionId?: string) => {
    const trimmed = question.trim();
    if (!trimmed || waiting || trimmed.length > 500) return;
    setMessages((current) => [...current, { role: "user", content: trimmed, id: Date.now() }]);
    setDraft("");
    setWaiting(true);
    setError(false);
    setNotice(null);
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          field_id: fieldId,
          lang,
          scenario,
          question: trimmed,
          question_id: questionId,
          history: messages.slice(-6).map(({ role, content }) => ({ role, content })),
          top_rotations: shownIds,
        }),
      });
      if (!response.ok) {
        setError(true);
        setNeedsAttention(response.status === 503);
        throw new Error(`Assistant request failed (${response.status})`);
      }
      const result = await response.json() as AssistantResponse;
      if (result.notice) setNotice(result.notice);
      setMessages((current) => [...current, {
        role: "assistant", content: result.answer, numbers: result.numbers, notice: result.notice, id: Date.now() + 1,
      }]);
    } catch (reason) {
      console.error("Field assistant request failed", reason);
      if (!error) setError(true);
    } finally {
      setWaiting(false);
    }
  };

  return (
    <>
      <button className="assistant-fab" type="button" aria-label={t("assistant.open", copy, lang)} onClick={() => setOpen(true)}>
        <MessageCircle size={18} /><span>{lang === "es" ? "Preguntar" : "Ask Field Shift"}</span>
      </button>
      {open && (
        <div className="assistant-overlay" onMouseDown={(event) => {
          if (event.target === event.currentTarget) setOpen(false);
        }}>
          <aside className="assistant-drawer" role="dialog" aria-modal="true" aria-labelledby="assistant-heading" ref={panelRef}>
            <header className="assistant-header">
              <span className="assistant-avatar"><Bot size={19} /></span>
              <div><h2 id="assistant-heading">{t("assistant.title", copy, lang)}</h2><p>{t("assistant.subtitle", copy, lang)}</p></div>
              <button type="button" className="icon-button" aria-label={lang === "es" ? "Cerrar" : "Close"} onClick={() => setOpen(false)}><X size={18} /></button>
            </header>
            <div className="assistant-main">
              <p className="assistant-disclaimer">{t("assistant.notice", copy, lang)}</p>
              {notice && <div className="assistant-notice" role="status">{t("assistant.using_cache", copy, lang)}</div>}
              <div className="assistant-chat" aria-live="polite">
                {!messages.length && <div className="assistant-welcome"><Bot size={20} /><p>{t("assistant.welcome", copy, lang)}</p></div>}
                {messages.map((message) => (
                  <article className={`chat-message ${message.role}`} key={message.id}>
                    {message.role === "assistant" && <span className="chat-avatar"><Bot size={13} /></span>}
                    <div className="chat-bubble">
                      {message.notice && <div className="assistant-notice">{t("assistant.using_cache", copy, lang)}</div>}
                      <RichAnswer message={message} sources={sources} lang={lang} copy={copy} />
                    </div>
                  </article>
                ))}
                {waiting && <div className="assistant-waiting"><LoaderCircle size={15} className="spin" />{t("assistant.waiting", copy, lang)}</div>}
                {error && <div className="assistant-error" role="alert">{t("assistant.error", copy, lang)}</div>}
              </div>
              {!messages.length && (
                <div className="suggested-questions">
                  <span>{lang === "es" ? "PREGUNTAS SUGERIDAS" : "SUGGESTED QUESTIONS"}</span>
                  {questions.map((question) => (
                    <button className={needsAttention ? "question-chip attention" : "question-chip"} key={question.id} type="button" disabled={waiting} onClick={() => void send(question[lang], question.id)}>
                      {question[lang]}<ArrowUpRight size={15} />
                    </button>
                  ))}
                </div>
              )}
            </div>
            <form className="assistant-form" onSubmit={(event) => { event.preventDefault(); void send(draft); }}>
              <label className="sr-only" htmlFor="assistant-question">{t("assistant.placeholder", copy, lang)}</label>
              <textarea
                id="assistant-question"
                ref={inputRef}
                value={draft}
                maxLength={500}
                rows={2}
                placeholder={t("assistant.placeholder", copy, lang)}
                disabled={waiting}
                onChange={(event) => setDraft(event.currentTarget.value)}
              />
              <div className="assistant-form-bottom">
                <span>{draft.length}/500</span>
                <button type="submit" disabled={!draft.trim() || waiting} aria-label={t("assistant.send", copy, lang)}><Send size={15} /><span>{t("assistant.send", copy, lang)}</span></button>
              </div>
            </form>
          </aside>
        </div>
      )}
    </>
  );
}

function RichAnswer({
  message,
  sources,
  lang,
  copy,
}: {
  message: Message;
  sources: SourcesFile;
  lang: Lang;
  copy: CopyFile["strings"];
}) {
  const parts = message.content.split(/(\[[A-Z0-9_]+\])/g);
  return (
    <div className="markdown-answer">
      {parts.map((part, index) => {
        const sourceId = part.match(/^\[([A-Z0-9_]+)\]$/)?.[1];
        if (sourceId) {
          const source = sources.sources[sourceId];
          return source
            ? <a className="assistant-source-chip" href={source.url} key={`${sourceId}-${index}`} title={source.role[lang] || source.role.en} target="_blank" rel="noreferrer">{source.name[lang] || source.name.en}</a>
            : null;
        }
        return <ReactMarkdown key={index} components={{
          p: ({ children }) => <p>{markNumbers(children, message.numbers || [], copy, lang)}</p>,
          li: ({ children }) => <li>{markNumbers(children, message.numbers || [], copy, lang)}</li>,
          strong: ({ children }) => <strong>{markNumbers(children, message.numbers || [], copy, lang)}</strong>,
        }}>{part}</ReactMarkdown>;
      })}
    </div>
  );
}

function markNumbers(
  children: React.ReactNode,
  numbers: AssistantNumber[],
  copy: CopyFile["strings"],
  lang: Lang,
): React.ReactNode {
  if (typeof children === "string") {
    const tokens = children.split(/(\$?\b\d[\d,.]*(?:\s?(?:%|mm|in|ac|ha|days?|years?))?\b)/g);
    return tokens.map((token, index) => {
      const itemIndex = numbers.findIndex((number) => number.value === token.trim());
      const item = itemIndex >= 0 ? numbers[itemIndex] : undefined;
      return item
        ? item.verified
          ? <span className="verified-number" key={index} title={item.fact_id || "Verified against field context"}>{token}</span>
          : <span className="unverified-number" key={index}>{token}<small>{t("assistant.unverified", copy, lang)}</small></span>
        : token;
    });
  }
  if (Array.isArray(children)) return children.map((child, index) => <span key={index}>{markNumbers(child, numbers, copy, lang)}</span>);
  return children;
}
