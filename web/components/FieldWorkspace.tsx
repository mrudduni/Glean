"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowUpRight, CircleHelp, Info, MapPin, RotateCcw } from "lucide-react";
import { OverviewPanel } from "@/components/OverviewPanel";
import { PrioritiesPanel } from "@/components/PrioritiesPanel";
import { FieldCalendar } from "@/components/FieldCalendar";
import { StrategyPanel } from "@/components/StrategyPanel";
import { ReplayChart } from "@/components/ReplayChart";
import { NeighborsView } from "@/components/NeighborsView";
import { AssistantDrawer } from "@/components/AssistantDrawer";
import { CropChips } from "@/components/CropChips";
import { useFieldShift } from "@/lib/state";
import { getContent, getCrops, getFieldBundle, getFields, getRotations, getSources } from "@/lib/data";
import { pickShown, sameRotation, weightsFromSliders } from "@/lib/score";
import { loc, makeT } from "@/lib/i18n";
import { cropNames, KIND_LABEL, type UI } from "@/lib/ui";
import { FIELD_IDS } from "@/lib/schemas";
import type { Content, CropsFile, Field, FieldBundle, FieldId, RotationId, RotationsFile, SourcesFile } from "@/lib/types";

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
  ["priorities", "nav.plan"],
  ["replay", "nav.replay"],
  ["neighbors", "nav.neighbors"],
] as const;

export function FieldWorkspace({ fieldId }: { fieldId: FieldId }) {
  const router = useRouter();
  const state = useFieldShift();
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
  const picked = useMemo(() => {
    const entries = data?.bundle.strategies.scenarios[scenario] ?? [];
    return pickShown(entries, weights, { cap: state.cap, hay: state.hay, cotton: state.cotton, forage: state.forage }, irrigation, duplicates);
  }, [data, scenario, weights, state.cap, state.hay, state.cotton, state.forage, irrigation, duplicates]);
  const order = useMemo(() => picked.shown.map((entry) => entry.rotation_id), [picked]);

  if (error) {
    return (
      <div className="page-wrap workspace-error" role="alert">
        <h1>{t("error.title", "This field could not be loaded")}</h1>
        <p>{error}</p>
        <button type="button" className="button-primary" onClick={() => window.location.reload()}><RotateCcw size={15} aria-hidden="true" />{t("error.retry", "Try again")}</button>
      </div>
    );
  }
  if (!data || !ui) {
    return <div className="workspace-loading page-wrap" aria-busy="true"><span className="map-spinner" /><div className="skeleton-grid"><i /><i /><i /></div></div>;
  }

  const { field, bundle } = data;
  return (
    <div className="workspace-page">
      <div className="workspace-toolbar page-wrap">
        <Link href="/" className="back-link"><ArrowLeft size={16} aria-hidden="true" />{t("nav.all_fields", "All fields")}</Link>
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

      <section className="field-masthead page-wrap">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> {t("app.location", "Finney County, Kansas")} · {field.id.toUpperCase()}</div>
          <h1>{loc(field.name, lang)}<span className={`field-kind ${field.kind}`}>{t(`field.kind.${field.kind}`, KIND_LABEL[field.kind])}</span></h1>
          <p>{field.area_ha.toFixed(1)} ha <span>/</span> {field.area_ac.toFixed(1)} ac <span>/</span> {field.soil.texture} <span>/</span> {Math.round(field.terrain.elev_m)} m</p>
        </div>
        <div className="masthead-cards">
          <div className="detected-rotation">
            <small>{t("overview.current_rotation")}</small>
            <CropChips steps={field.detected.sequence} ui={ui} />
            <span>{field.detected.years[0]} to {field.detected.years[1]} · {t("card.confidence")}: {t(`trust.level.${field.detected.confidence}`)}</span>
          </div>
        </div>
      </section>

      <nav className="section-nav" aria-label={t("nav.sections", "Field sections")}>
        <div className="section-nav-inner page-wrap">
          {sections.map(([id, key], index) => <a href={`#${id}`} key={id}><span>0{index + 1}</span>{t(key)}</a>)}
          <Link href="/how-we-know" className="trust-nav"><CircleHelp size={16} aria-hidden="true" />{t("nav.trust")}</Link>
        </div>
      </nav>

      <div className="workspace-content page-wrap">
        <OverviewPanel field={field} summary={bundle.summary} water={bundle.water} glossary={data.content.glossary} copy={copy} ui={ui} />
        <FieldCalendar calendar={bundle.calendar} order={order} ui={ui} />
        <PrioritiesPanel t={t} />
        <StrategyPanel picked={picked} weights={weights} rotations={data.rotations.rotations} summary={bundle.summary} irrigation={irrigation} copy={copy} ui={ui} />
        <ReplayChart replay={bundle.replay} scenario={scenario} order={order} ui={ui} />
        <NeighborsView neighbors={bundle.neighbors} field={field} ui={ui} />
        <div className="workspace-notice">
          <span className="notice-icon"><Info size={18} aria-hidden="true" /></span>
          <p>{t("disclaimer.main")}</p>
          <Link href="/how-we-know">{t("nav.trust")} <ArrowUpRight size={15} aria-hidden="true" /></Link>
        </div>
      </div>
      <AssistantDrawer fieldId={field.id} scenario={scenario} shownIds={order} questions={data.content.questions} sources={data.sources} t={t} lang={lang} />
    </div>
  );
}
