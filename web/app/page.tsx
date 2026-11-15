"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowDownRight, ArrowUpRight, Compass, Droplets, Layers3, MoveRight, Satellite, Sprout } from "lucide-react";
import { FieldMap } from "@/components/FieldMap";
import { CropChips } from "@/components/CropChips";
import { SpotlightCard } from "@/components/SpotlightCard";
import { useGlean } from "@/lib/state";
import { getContent, getCrops, getFields, getSources } from "@/lib/data";
import { formatVar, loc, makeT, textureLabel, yearsLabel } from "@/lib/i18n";
import { cropNames, KIND_LABEL } from "@/lib/ui";
import type { CopyFile, CropsFile, Field, FieldId, SourcesFile } from "@/lib/types";

const NO_STRINGS: CopyFile["strings"] = {};

export default function HomePage() {
  const router = useRouter();
  const { lang, setField } = useGlean();
  const [fields, setFields] = useState<Field[]>([]);
  const [crops, setCrops] = useState<CropsFile | null>(null);
  const [sources, setSources] = useState<SourcesFile | null>(null);
  const [copy, setCopy] = useState<CopyFile["strings"]>(NO_STRINGS);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([getFields(), getCrops().catch(() => null), getContent(), getSources().catch(() => null)])
      .then(([fieldsFile, cropsFile, content, sourcesFile]) => {
        if (!active) return;
        setFields(fieldsFile.fields);
        setCrops(cropsFile);
        setCopy(content.copy.strings);
        setSources(sourcesFile);
      })
      .catch((reason: unknown) => {
        console.error("[home] could not load fields", reason);
        if (active) setError(reason instanceof Error ? reason.message : String(reason));
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const t = useMemo(() => makeT(copy, lang), [copy, lang]);
  const ui = useMemo(() => ({ lang, t, crops: cropNames(crops) }), [crops, lang, t]);
  const openField = (id: string) => {
    const fid = id as FieldId;
    if (!fields.some((field) => field.id === fid)) return;
    setField(fid);
    router.push(`/field/${fid}`);
  };
  const years = fields.flatMap((field) => field.crop_history.map((item) => item.year));
  const historySpan = years.length ? yearsLabel(t, Math.min(...years), Math.max(...years)) : "";
  const awc = fields.map((field) => field.soil.aws_0_100_mm);
  return (
    <div className="home-page">
      <section className="home-hero page-wrap">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-rule" /> <span className="text-shimmer">{t("app.name")}</span></div>
          <h1>{t("app.tagline")}</h1>
          <p>{t("pick.subtitle")}</p>
          <div className="hero-cta-group">
            <a className="button-primary" href="#field-picker"><span>{t("pick.title")}</span><ArrowDownRight size={17} aria-hidden="true" /></a>
            <Link className="hero-scroll" href="/how-we-know"><span>{t("nav.trust")}</span><ArrowUpRight size={19} aria-hidden="true" /></Link>
          </div>
        </div>

        <div>
          <SpotlightCard className="hero-telemetry-hub">
            <div className="telemetry-topline">
              <span className="telemetry-live-badge"><span className="telemetry-live-dot" /><span className="text-shimmer">{t("home.data_in_use", "Data behind these fields")}</span></span>
              <span className="telemetry-coordinates">Finney County, KS · FIPS 20055</span>
            </div>
            <div className="telemetry-grid">
              <div className="telemetry-item">
                <div className="telemetry-item-head"><Satellite size={15} aria-hidden="true" /><span>CSB</span></div>
                <strong>{historySpan || "—"}</strong>
                <small>{t("home.crop_history", "USDA crop history per field")}</small>
              </div>
              <div className="telemetry-item">
                <div className="telemetry-item-head"><Droplets size={15} aria-hidden="true" /><span>SSURGO</span></div>
                <strong>{awc.length ? `${formatVar("min_mm", Math.min(...awc), lang)}` : "—"}</strong>
                <small>{t("home.soil_storage", "Lowest soil water storage of the 3 fields")}</small>
              </div>
              <div className="telemetry-item">
                <div className="telemetry-item-head"><Layers3 size={15} aria-hidden="true" /><span>{t("trust.sources")}</span></div>
                <strong>{sources?.sources.length ?? "—"}</strong>
                <small>{sources ? sources.sources.map((item) => item.tag).join(", ") : ""}</small>
              </div>
              <div className="telemetry-item">
                <div className="telemetry-item-head"><Sprout size={15} aria-hidden="true" /><span>{t("home.rotations", "Rotations")}</span></div>
                <strong>R0 + 6</strong>
                <small>{t("home.rotations_note", "Current rotation against six alternatives")}</small>
              </div>
            </div>
            <div className="telemetry-launcher">
              <div className="telemetry-launcher-head"><span>{t("pick.title")}</span><span className="launcher-counter">{fields.length} / 3</span></div>
              <div className="telemetry-field-chips">
                {fields.map((field, index) => (
                  <button type="button" key={field.id} className="telemetry-field-chip" onClick={() => openField(field.id)}>
                    <span className="telemetry-field-index">0{index + 1}</span>
                    <div className="telemetry-field-info">
                      <strong>{loc(field.name, lang)}</strong>
                      <small>{field.area_ac.toFixed(0)} ac · {textureLabel(t, field.soil.texture, lang)}</small>
                    </div>
                    <span className={`chip-kind-pill ${field.kind}`}>{t(`field.kind.${field.kind}`, KIND_LABEL[field.kind])}</span>
                    <MoveRight size={14} className="telemetry-arrow" aria-hidden="true" />
                  </button>
                ))}
              </div>
            </div>
          </SpotlightCard>
        </div>
      </section>

      <section className="picker-section page-wrap" id="field-picker" aria-labelledby="picker-heading">
        <div className="section-heading picker-heading">
          <div>
            <div className="eyebrow"><span className="eyebrow-rule" /> {t("app.location", "Finney County, Kansas")}</div>
            <h2 id="picker-heading">{t("pick.title")}</h2>
            <p>{t("pick.subtitle")}</p>
          </div>
        </div>
        {loading && <div className="loading-panel" aria-busy="true"><span className="map-spinner" /><div className="skeleton-line" /></div>}
        {error && (
          <div className="error-panel" role="alert">
            <strong>{t("error.title", "The data could not be loaded")}</strong><span>{error}</span>
            <button type="button" className="text-button" onClick={() => window.location.reload()}>{t("error.retry", "Try again")}</button>
          </div>
        )}
        {!loading && !error && (
          <div className="field-picker-grid">
            <div className="map-column">
              <FieldMap fields={fields} onSelect={openField} t={t} lang={lang} />
              <div className="map-caption"><Compass size={16} aria-hidden="true" /> <span>{t("home.map_caption", "Click a field outline to open it.")}</span></div>
            </div>
            <div className="field-list">
              {fields.map((field, index) => (
                <SpotlightCard
                  key={field.id}
                  as="div"
                  className={`field-option field-option-${index + 1}`}
                  enableTilt={true}
                  tiltMax={3.5}
                >
                  <Link
                    href={`/field/${field.id}`}
                    onClick={() => setField(field.id)}
                    style={{ display: "contents", color: "inherit", textDecoration: "none" }}
                  >
                    <div className="field-option-top">
                      <span className="field-number">0{index + 1}</span>
                      <span className={`field-kind ${field.kind}`}>{t(`field.kind.${field.kind}`, KIND_LABEL[field.kind])}</span>
                      <ArrowUpRight className="field-arrow" size={20} aria-hidden="true" />
                    </div>
                    <h3>{loc(field.name, lang)}</h3>
                    <div className="field-meta">
                      <span><small>{t("field.area", "Area")}</small>{field.area_ha.toFixed(1)} ha <i>/</i> {field.area_ac.toFixed(1)} ac</span>
                      <span><small>{t("overview.soil")}</small>{textureLabel(t, field.soil.texture, lang)}</span>
                    </div>
                    <div className="crop-chip-line">
                      <small>{t("overview.current_rotation")}</small>
                      <CropChips steps={field.detected.sequence} ui={ui} />
                    </div>
                    <span className="field-option-bottom"><span>{t("pick.open_field")}</span><MoveRight size={17} aria-hidden="true" /></span>
                  </Link>
                </SpotlightCard>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
