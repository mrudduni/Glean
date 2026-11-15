"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowDown, ArrowLeft, Check, CircleHelp, Link2, MapPin, MessageCircle, Printer, RotateCcw } from "lucide-react";
import { OverviewPanel } from "@/components/OverviewPanel";
import { PrioritiesPanel } from "@/components/PrioritiesPanel";
import { FieldCalendar } from "@/components/FieldCalendar";
import { rotationSteps, StrategyPanel } from "@/components/StrategyPanel";
import { SourceChips } from "@/components/SourceChips";
import dynamic from "next/dynamic";
import { NeighborsView } from "@/components/NeighborsView";
import { AssistantDrawer } from "@/components/AssistantDrawer";
import { CropChips } from "@/components/CropChips";
import { useGlean } from "@/lib/state";
import { getContent, getCrops, getFieldBundle, getFields, getRotations, getSources } from "@/lib/data";
import { pickShown, sameRotation, scoreEntry, weightsFromSliders } from "@/lib/score";
import { formatVar, interpolate, loc, makeT, textureLabel, yearsLabel } from "@/lib/i18n";
import { cardLine, cropNames, KIND_LABEL, type UI } from "@/lib/ui";
import { FIELD_IDS } from "@/lib/schemas";
import type { CapId, Content, CropsFile, Field, FieldBundle, FieldId, RotationId, RotationsFile, ScenarioKey, SourcesFile } from "@/lib/types";

// The chart library is only needed for Rotation Replay, further down the page: load it on its own.
const ReplayChart = dynamic(() => import("@/components/ReplayChart").then((module) => module.ReplayChart), {
  ssr: false,
  loading: () => <div className="workspace-section"><div className="skeleton-block" style={{ height: 480 }} /></div>,
});

interface Loaded {
  field: Field;
  fields: Field[];
  bundle: FieldBundle;
  crops: CropsFile | null;
  rotations: RotationsFile;
  sources: SourcesFile;
  content: Content;
}

const NO_STRINGS: Content["copy"]["strings"] = {};

const sections = [
  ["overview", "nav.overview"],
  ["calendar", "nav.calendar"],
  ["strategies", "strategies.eyebrow"],
  ["replay", "nav.replay"],
  ["neighbors", "nav.neighbors"],
] as const;

export function FieldWorkspace({ fieldId }: { fieldId: FieldId }) {
  const router = useRouter();
  const state = useGlean();
  const { lang, scenario } = state;
  const [data, setData] = useState<Loaded | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setData(null);
    setError(null);
    Promise.all([getFields(), getCrops().catch(() => null), getRotations(), getSources(), getContent(), getFieldBundle(fieldId)])
      .then(([fieldsFile, crops, rotations, sources, content, bundle]) => {
        if (!active) return;
        const field = fieldsFile.fields.find((item) => item.id === fieldId);
        if (!field) throw new Error(`Field ${fieldId} is not in fields.json`);
        setData({ field, fields: fieldsFile.fields, bundle, crops, rotations, sources, content });
      })
      .catch((reason: unknown) => {
        console.error(`[workspace] could not load ${fieldId}`, reason);
        if (active) setError(reason instanceof Error ? reason.message : String(reason));
      });
    return () => { active = false; };
  }, [fieldId]);

  // A field without irrigation can only run dryland options: start there, and give the 300 mm default back
  // when the farmer moves on to an irrigated field.
  const forcedDryland = useRef(false);
  const irrigated = data?.field.irrigated;
  useEffect(() => {
    if (irrigated === undefined) return;
    if (!irrigated && state.cap !== "dryland") { forcedDryland.current = true; state.setCap("dryland"); }
    if (irrigated && forcedDryland.current) { forcedDryland.current = false; if (state.cap === "dryland") state.setCap("cap300"); }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [irrigated, fieldId]);

  // Section nav shows where the reader is.
  const [activeSection, setActiveSection] = useState<string>("overview");
  const loaded = Boolean(data);
  useEffect(() => {
    if (!loaded) return;
    const nodes = sections.map(([id]) => document.getElementById(id)).filter((node): node is HTMLElement => Boolean(node));
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (visible) setActiveSection(visible.target.id);
    }, { rootMargin: "-30% 0px -60% 0px" });
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, [loaded]);

  // Share the exact view (field, priorities, limits and language are in the URL).
  const [copied, setCopied] = useState(false);
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2500);
    } catch {
      window.prompt?.(t("share.copy_manual", "Copy this link"), window.location.href);
    }
  };

  const copy = data?.content.copy.strings ?? NO_STRINGS;
  const t = useMemo(() => makeT(copy, lang), [copy, lang]);
  const ui: UI | null = useMemo(() => (data ? {
    lang, t, cardText: data.content.cardText, crops: cropNames(data.crops), sources: data.sources,
  } : null), [data, lang, t]);

  const weights = useMemo(() => weightsFromSliders(state.sliders), [state.sliders]);
  const irrigation = useMemo(() => {
    const runs = data?.bundle.replay.scenarios[scenario] ?? {};
    return Object.fromEntries(Object.entries(runs).map(([id, run]) => [id, run?.summary.irrigation_mm_mean])) as Partial<Record<RotationId, number>>;
  }, [data, scenario]);
  const duplicates = useMemo(() => {
    const current = data?.bundle.summary.current_rotation.steps ?? [];
    return new Set((data?.rotations.rotations ?? []).filter((rotation) => sameRotation(rotation.steps, current)).map((rotation) => rotation.id));
  }, [data]);
  const { picked, irrigationShown, shownAt } = useMemo(() => {
    const entries = data?.bundle.strategies.scenarios[scenario] ?? [];
    const result = pickShown(entries, weights, { cap: state.cap, hay: state.hay, cotton: state.cotton, forage: state.forage }, irrigation, duplicates);
    // A filler that needs more water is shown with its numbers at its own minimum cap, not at a cap it cannot run under.
    const climate = scenario.split("|")[1];
    const at: Partial<Record<RotationId, CapId | "none">> = {};
    const water = { ...irrigation };
    const shown = result.shown.map((entry) => {
      if (result.filled[entry.rotation_id] !== "needs_more_water") return entry;
      const minCap = data?.rotations.rotations.find((rotation) => rotation.id === entry.rotation_id)?.min_cap;
      const key = `${minCap}|${climate}` as ScenarioKey;
      const better = minCap ? data?.bundle.strategies.scenarios[key]?.find((other) => other.rotation_id === entry.rotation_id) : undefined;
      // No cap makes it feasible here (a field without irrigation): keep the numbers, flag that they assume no water.
      if (!minCap || !better?.feasible) { at[entry.rotation_id] = "none"; return entry; }
      at[entry.rotation_id] = minCap;
      water[entry.rotation_id] = data?.bundle.replay.scenarios[key]?.[entry.rotation_id]?.summary.irrigation_mm_mean;
      return better;
    });
    return { picked: { ...result, shown }, irrigationShown: water, shownAt: at };
  }, [data, scenario, weights, state.cap, state.hay, state.cotton, state.forage, irrigation, duplicates]);
  const order = useMemo(() => picked.shown.map((entry) => entry.rotation_id), [picked]);
  const currentEntry = picked.shown.find((entry) => entry.rotation_id === "R0");
  const best = picked.shown.find((entry) => entry.rotation_id !== "R0" && !picked.filled[entry.rotation_id]);
  const unavailableCount = Object.keys(picked.filled).length;

  if (error) {
    return (
      <div className="page-wrap state-page" role="alert">
        <h1>{t("error.field_title", "This field could not be loaded")}</h1>
        <p>{t("error.check_connection", "Check your connection and try again.")}</p>
        <div className="state-actions">
          <button type="button" className="button-primary" onClick={() => window.location.reload()}><RotateCcw size={15} aria-hidden="true" />{t("error.retry", "Try again")}</button>
          <Link href="/" className="text-button">{t("nav.all_fields", "All fields")}</Link>
        </div>
        <details className="state-detail"><summary>{t("error.detail", "Technical detail")}</summary><code>{error}</code></details>
      </div>
    );
  }
  if (!data || !ui) {
    // Placeholder shaped like the page that is coming, so nothing jumps when it arrives.
    return (
      <div className="page-wrap workspace-skeleton" aria-busy="true" aria-live="polite">
        <span className="sr-only">{t("state.loading_field", "Loading this field")}</span>
        <div className="skeleton-block sk-title" />
        <div className="skeleton-block sk-meta" />
        <div className="sk-brief"><div className="skeleton-block" /><div className="skeleton-block" /><div className="skeleton-block" /></div>
        <div className="skeleton-block sk-nav" />
        <div className="skeleton-block sk-section" />
      </div>
    );
  }

  const { field, bundle } = data;
  return (
    <div className="workspace-page">
      <div className="workspace-toolbar page-wrap">
        <Link href="/" className="back-link"><ArrowLeft size={16} aria-hidden="true" />{t("nav.all_fields", "All fields")}</Link>
        <div className="toolbar-actions">
          <button type="button" className="text-button" onClick={() => void copyLink()}>
            {copied ? <Check size={16} aria-hidden="true" /> : <Link2 size={16} aria-hidden="true" />}
            {copied ? t("share.copied", "Link copied") : t("share.copy", "Copy link to this view")}
          </button>
          <span className="sr-only" aria-live="polite">{copied ? t("share.copied", "Link copied") : ""}</span>
          <button type="button" className="text-button" onClick={() => window.print()}>
            <Printer size={16} aria-hidden="true" />{t("share.print", "Print summary")}
          </button>
        </div>
        <div className="field-switcher">
          <label htmlFor="field-switch"><MapPin size={15} aria-hidden="true" /><span>{t("nav.field", "Field")}</span></label>
          <select
            id="field-switch"
            value={field.id}
            onChange={(event) => {
              const next = event.currentTarget.value as FieldId;
              if (FIELD_IDS.includes(next)) router.push(`/field/${next}${window.location.search}`);
            }}
          >
            {data.fields.map((item) => <option value={item.id} key={item.id}>{loc(item.name, lang)}</option>)}
          </select>
        </div>
      </div>

      <section className="field-masthead page-wrap" aria-labelledby="field-heading">
        <div className="masthead-title">
          <h1 id="field-heading">{loc(field.name, lang)}</h1>
          <p className="masthead-meta">
            <span className={`field-kind ${field.kind}`}>{t(`field.kind.${field.kind}`, KIND_LABEL[field.kind])}</span>
            <span>{formatVar("area", field.area_ha, lang)} ha · {formatVar("area", field.area_ac, lang)} ac</span>
            <span>{textureLabel(t, field.soil.texture, lang)}</span>
            <span>{Math.round(field.terrain.elev_m)} m</span>
          </p>
        </div>

        <div className="masthead-brief">
          <a className="brief-best" href="#strategies">
            <span className="brief-label">{t("summary.best_fit", "Best fit for your priorities")}</span>
            {best ? (
              <>
                <strong>{loc(data.content.cardText.rotations[best.rotation_id]?.name, lang) || best.rotation_id}</strong>
                <CropChips steps={rotationSteps(best.rotation_id, data.rotations.rotations, bundle.summary)} ui={ui} />
                <span className="brief-score">
                  {interpolate(t("summary.vs_current", "Fit with your priorities: {score}, against {current} for your current rotation."), { score: scoreEntry(best, weights), current: currentEntry ? scoreEntry(currentEntry, weights) : "—" })}
                </span>
              </>
            ) : (
              <>
                <strong>{t("summary.none_fit_title", "Nothing fits your limits yet")}</strong>
                <span className="brief-score">
                  {interpolate(t("summary.unavailable", "{n} {n|option is|options are} shown below, each needing a change to your limits."), { n: unavailableCount }, lang)}
                </span>
              </>
            )}
            <span className="brief-go">{t("summary.see_options", "Compare all options")}<ArrowDown size={15} aria-hidden="true" /></span>
          </a>

          <div className="brief-facts">
            <h2>{t("overview.headlines", "What stands out")}</h2>
            <ul>
              {bundle.summary.headline_facts.map((fact, index) => (
                <li key={`${fact.text_id}-${index}`}>
                  <p>{cardLine(ui, "headline", fact.text_id, fact.vars)}</p>
                  <SourceChips tags={fact.sources} sources={ui.sources} />
                </li>
              ))}
            </ul>
          </div>

          <div className="brief-current">
            <span className="brief-label">{t("overview.current_rotation")}</span>
            <CropChips steps={field.detected.sequence} ui={ui} />
            <span className="brief-note">{yearsLabel(t, field.detected.years[0], field.detected.years[1])} · {t("card.confidence")}: {t(`trust.level.${field.detected.confidence}`)}</span>
          </div>
        </div>
      </section>

      <nav className="section-nav" aria-label={t("nav.sections", "Field sections")}>
        <div className="section-nav-inner page-wrap">
          {sections.map(([id, key]) => <a href={`#${id}`} key={id} aria-current={activeSection === id ? "location" : undefined}>{t(key)}</a>)}
          <Link href="/how-we-know" className="trust-nav"><CircleHelp size={16} aria-hidden="true" />{t("nav.trust")}</Link>
          <button type="button" className="nav-ask" onClick={() => window.dispatchEvent(new Event("glean:open-assistant"))}>
            <MessageCircle size={16} aria-hidden="true" />{t("assistant.title")}
          </button>
        </div>
      </nav>

      <div className="workspace-content page-wrap">
        <OverviewPanel field={field} summary={bundle.summary} water={bundle.water} glossary={data.content.glossary} copy={copy} ui={ui} />
        <FieldCalendar calendar={bundle.calendar} order={order} ui={ui} bestId={best?.rotation_id} />
        <section className="workspace-section compare-section" id="strategies" aria-labelledby="strategies-heading">
          <div className="section-title-row">
            <h2 id="strategies-heading">{t("strategies.eyebrow", "Compare your options")}</h2>
            <p>{t("strategies.subtitle", "Your current rotation and the three that fit your priorities most closely.")}</p>
          </div>
          <div className="compare-layout">
            <PrioritiesPanel t={t} irrigated={field.irrigated} />
            <StrategyPanel picked={picked} weights={weights} rotations={data.rotations.rotations} summary={bundle.summary} irrigation={irrigationShown} shownAt={shownAt} copy={copy} ui={ui} irrigated={field.irrigated} />
          </div>
        </section>
        <ReplayChart replay={bundle.replay} scenario={scenario} order={order} ui={ui} />
        <NeighborsView neighbors={bundle.neighbors} field={field} ui={ui} />
      </div>
      <AssistantDrawer fieldId={field.id} scenario={scenario} shownIds={order} questions={data.content.questions} sources={data.sources} t={t} lang={lang} />
    </div>
  );
}
