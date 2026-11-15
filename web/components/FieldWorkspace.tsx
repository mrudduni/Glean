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
import { SourceChips } from "@/components/SourceChips";
import { useFieldShift } from "@/lib/state";
import { getContent, getCrops, getFieldBundle, getFields, getRotations, getSources } from "@/lib/data";
import { pickShown, weightsFromSliders, type Constraints } from "@/lib/score";
import { t } from "@/lib/i18n";
import type {
  CardTextFile, CopyFile, Crop, Field, FieldBundle, FieldId, Rotation, SourcesFile, StrategyEntry,
} from "@/lib/types";

const sectionLinks = [
  ["overview", "nav.overview"],
  ["calendar", "nav.calendar"],
  ["priorities", "nav.priorities"],
  ["strategies", "nav.strategies"],
  ["replay", "nav.replay"],
  ["neighbors", "nav.neighbors"],
] as const;

export function FieldWorkspace({ fieldId }: { fieldId: FieldId }) {
  const router = useRouter();
  const state = useFieldShift();
  const { lang } = state;
  const [field, setFieldData] = useState<Field | null>(null);
  const [allFields, setAllFields] = useState<Field[]>([]);
  const [allNeighbors, setAllNeighbors] = useState<Array<{ id: string; polygon: [number, number][] }>>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [rotations, setRotations] = useState<Rotation[]>([]);
  const [bundle, setBundle] = useState<FieldBundle | null>(null);
  const [sources, setSources] = useState<SourcesFile | null>(null);
  const [copy, setCopy] = useState<CopyFile["strings"]>({});
  const [cardText, setCardText] = useState<CardTextFile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    Promise.all([
      getFields(), getCrops(), getRotations(), getSources(), getContent(), getFieldBundle(fieldId),
    ]).then(([fieldsFile, cropData, rotationData, sourceData, content, fieldBundle]) => {
      if (!active) return;
      const current = fieldsFile.fields.find((item) => item.id === fieldId);
      if (!current) throw new Error(`Unknown field ${fieldId}.`);
      setFieldData(current);
      setAllFields(fieldsFile.fields);
      setAllNeighbors(fieldsFile.neighbors || []);
      setCrops(cropData as Crop[]);
      setRotations(rotationData as Rotation[]);
      setSources(sourceData);
      setBundle(fieldBundle);
      setCopy(content.copy.strings);
      setCardText(content.cardText);
    }).catch((reason: unknown) => {
      console.error(`Could not load workspace for ${fieldId}`, reason);
      if (active) setError(reason instanceof Error ? reason.message : "The field data could not be loaded.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [fieldId]);

  const shown = useMemo(() => {
    if (!bundle) return [];
    const adjustment = bundle.strategies.scenario_adjustments?.[state.scenario] || { irrigation_factor: 1, climate_delta: 0 };
    const adjusted = bundle.strategies.entries.map((entry) => ({
      ...entry,
      needs_irrigation_mm: Math.round(entry.needs_irrigation_mm * adjustment.irrigation_factor),
      criteria: {
        ...entry.criteria,
        climate: { ...entry.criteria.climate, norm: Math.max(0, Math.min(10, entry.criteria.climate.norm + adjustment.climate_delta)) },
      },
    }));
    const constraints: Constraints = { cap: state.cap, hay: state.hay, cotton: state.cotton, forage: state.forage };
    return pickShown(adjusted, weightsFromSliders(state.weights), constraints).shown;
  }, [bundle, state.cap, state.cotton, state.forage, state.hay, state.scenario, state.weights]);

  if (loading) {
    return <div className="workspace-loading page-wrap"><span className="map-spinner" /><p>{t("loading", copy, lang)}</p><div className="skeleton-grid"><i /><i /><i /></div></div>;
  }
  if (error || !field || !bundle || !sources || !cardText) {
    return (
      <div className="page-wrap workspace-error">
        <div className="eyebrow"><span className="eyebrow-rule" /> FIELD WORKSPACE</div>
        <h1>{t("error.title", copy, lang)}</h1>
        <p>{error || t("not_available", copy, lang)}</p>
        <button type="button" className="button-primary" onClick={() => window.location.reload()}><RotateCcw size={15} />{t("error.retry", copy, lang)}</button>
      </div>
    );
  }

  const nav = sectionLinks.map(([id, key]) => ({ id, label: t(key, copy, lang) }));
  const currentRotation = rotations.find((rotation) => rotation.id === field.current_rotation_id);
  return (
    <div className="workspace-page">
      <div className="workspace-toolbar page-wrap">
        <Link href="/" className="back-link"><ArrowLeft size={16} />{lang === "es" ? "Todos los campos" : "All fields"}</Link>
        <div className="field-switcher">
          <label htmlFor="field-switch"><MapPin size={15} /><span>{lang === "es" ? "CAMPO" : "FIELD"}</span></label>
          <select
            id="field-switch"
            value={field.id}
            onChange={(event) => {
              const next = event.currentTarget.value as FieldId;
              if (!["f1", "f2", "f3"].includes(next)) return;
              router.push(`/field/${next}`);
            }}
          >
            {allFields.map((item) => <option value={item.id} key={item.id}>{item.name[lang] || item.name.en}</option>)}
          </select>
        </div>
      </div>
      <section className="field-masthead page-wrap">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> FINNEY COUNTY, KANSAS · FIELD {field.id.slice(1).padStart(2, "0")}</div>
          <h1>{field.name[lang] || field.name.en}<span className={`field-kind ${field.kind}`}>{field.kind === "dryland" ? t("field.dryland", copy, lang) : t("field.irrigated", copy, lang)}</span></h1>
          <p>{field.area_ha.toFixed(1)} ha <span>/</span> {field.area_ac.toFixed(1)} ac <span>/</span> {field.soil_texture[lang] || field.soil_texture.en}</p>
        </div>
        <div className="masthead-cards">
          <div className="masthead-badge-card">
            <small>{lang === "es" ? "CONTEXTO AGROECOLÓGICO" : "AGRO-ECOLOGICAL PROFILE"}</small>
            <strong>{field.kind === "dryland" ? (lang === "es" ? "Transición Secano" : "Semi-Arid Dryland") : (lang === "es" ? "Acuífero Ogallala" : "Ogallala Aquifer Basin")}</strong>
            <span>{field.soil_texture[lang] || field.soil_texture.en} · 880 m ASL</span>
          </div>
          <div className="detected-rotation">
            <small>{t("overview.current", copy, lang)}</small>
            <strong>{currentRotation?.name[lang] || currentRotation?.name.en}</strong>
            <span>{t("field.sample_history", copy, lang, "{start} to {end} · {count} recorded crop seasons").replace("{start}", String(field.years[0])).replace("{end}", String(field.years[1])).replace("{count}", String(field.current_crops?.length || 0))}</span>
          </div>
        </div>
      </section>
      <nav className="section-nav" aria-label="Field sections">
        <div className="section-nav-inner page-wrap">
          {nav.map((item, index) => <a href={`#${item.id}`} key={item.id}><span>0{index + 1}</span>{item.label}</a>)}
          <Link href="/how-we-know" className="trust-nav"><CircleHelp size={16} />{t("nav.trust", copy, lang)}</Link>
        </div>
      </nav>

      <div className="workspace-content page-wrap">
        <OverviewPanel field={field} bundle={bundle} crops={crops} rotations={rotations} sources={sources} copy={copy} cardText={cardText} lang={lang} />
        <FieldCalendar calendar={bundle.calendar} shown={shown} rotations={rotations} crops={crops} field={field} copy={copy} lang={lang} />
        <PrioritiesPanel copy={copy} />
        <StrategyPanel
          entries={bundle.strategies.entries}
          rotations={rotations}
          crops={crops}
          field={field}
          cardText={cardText}
          copy={copy}
          sources={sources}
          lang={lang}
          scenarioAdjustments={bundle.strategies.scenario_adjustments || {}}
        />
        <ReplayChart replay={bundle.replay} shown={shown} copy={copy} />
        <NeighborsView neighbors={bundle.neighbors} fields={{ _meta: { version: "1.0.0" }, fields: allFields, neighbors: allNeighbors }} field={field} rotations={rotations} sources={sources} copy={copy} lang={lang} />
        <div className="workspace-notice">
          <span className="notice-icon"><Info size={18} /></span>
          <p>{t("disclaimer.main", copy, lang)}</p>
          <Link href="/how-we-know">{lang === "es" ? "Ver fuentes y validación" : "See sources and validation"} <ArrowUpRight size={15} /></Link>
        </div>
      </div>
    </div>
  );
}
