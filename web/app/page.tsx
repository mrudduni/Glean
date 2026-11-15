"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowDownRight, ArrowUpRight, Compass, Droplets, Layers3, MoveRight, Radio, Satellite, Sun } from "lucide-react";
import { FieldMap } from "@/components/FieldMap";
import { useFieldShift } from "@/lib/state";
import { getContent, getCrops, getFields, getRotations } from "@/lib/data";
import { t } from "@/lib/i18n";
import type { CopyFile, Crop, Field, Rotation } from "@/lib/types";

export default function HomePage() {
  const router = useRouter();
  const { lang, setField } = useFieldShift();
  const [fields, setFields] = useState<Field[]>([]);
  const [neighbors, setNeighbors] = useState<Array<{ id: string; polygon: [number, number][] }>>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [rotations, setRotations] = useState<Rotation[]>([]);
  const [copy, setCopy] = useState<CopyFile["strings"]>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([getFields(), getCrops(), getRotations(), getContent()])
      .then(([fieldsFile, cropData, rotationData, content]) => {
        if (!active) return;
        setFields(fieldsFile.fields);
        setNeighbors(fieldsFile.neighbors || []);
        setCrops(cropData as Crop[]);
        setRotations(rotationData as Rotation[]);
        setCopy(content.copy.strings);
      })
      .catch((reason: unknown) => {
        console.error("Could not load field selection data", reason);
        if (active) setError(reason instanceof Error ? reason.message : "Data could not be loaded.");
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const cropsById = useMemo(() => new Map(crops.map((crop) => [crop.id, crop])), [crops]);
  const openField = (id: string) => {
    if (!["f1", "f2", "f3"].includes(id)) return;
    setField(id as Field["id"]);
    router.push(`/field/${id}`);
  };

  return (
    <div className="home-page">
      <section className="home-hero page-wrap">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-rule" /> FIELD DECISIONS, WITH MORE CONTEXT</div>
          <h1>{t("app.tagline", copy, lang, "A clearer way to explore what comes next.")}</h1>
          <p>{t("pick.subtitle", copy, lang, "Choose a field to explore current conditions and compare possible crop rotations.")}</p>
          <div className="hero-cta-group">
            <button type="button" className="button-primary" onClick={() => openField("f1")}>
              <span>{lang === "es" ? "Explorar campo principal" : "Explore field workspace"}</span>
              <ArrowUpRight size={17} />
            </button>
            <a className="hero-scroll" href="#field-picker">
              <span>{t("home.start", copy, lang, lang === "es" ? "Ver los 3 campos" : "Compare all 3 fields")}</span>
              <ArrowDownRight size={19} />
            </a>
          </div>
        </div>

        <div className="hero-telemetry-hub">
          <div className="telemetry-topline">
            <span className="telemetry-live-badge">
              <span className="telemetry-live-dot" />
              <span>{lang === "es" ? "DATOS DE OBSERVACIÓN EN VIVO" : "ACTIVE SATELLITE FEEDS"}</span>
            </span>
            <span className="telemetry-coordinates">37.99° N, 100.87° W</span>
          </div>

          <div className="telemetry-grid">
            <div className="telemetry-item">
              <div className="telemetry-item-head">
                <Satellite size={15} />
                <span>CDL · SENTINEL</span>
              </div>
              <strong>{lang === "es" ? "8 Temporadas" : "8-Yr History"}</strong>
              <small>{lang === "es" ? "4 cultivos detectados" : "Corn, soy, wheat, sorghum"}</small>
            </div>
            <div className="telemetry-item">
              <div className="telemetry-item-head">
                <Sun size={15} />
                <span>NASA POWER</span>
              </div>
              <strong>174d {lang === "es" ? "sin helada" : "Frost-Free"}</strong>
              <small>{lang === "es" ? "31 días cálidos registrados" : "+7 hot-day delta observed"}</small>
            </div>
            <div className="telemetry-item">
              <div className="telemetry-item-head">
                <Droplets size={15} />
                <span>NASA SMAP</span>
              </div>
              <strong>178 mm (7.0 in)</strong>
              <small>{lang === "es" ? "Almacenamiento de suelo" : "Surface & root moisture"}</small>
            </div>
            <div className="telemetry-item">
              <div className="telemetry-item-head">
                <Radio size={15} />
                <span>GRACE FO</span>
              </div>
              <strong>{lang === "es" ? "Acuífero Ogallala" : "Ogallala Outlook"}</strong>
              <small>{lang === "es" ? "-0.3 m/año tendencia de pozo" : "-0.3 m/yr local well trend"}</small>
            </div>
          </div>

          <div className="telemetry-launcher">
            <div className="telemetry-launcher-head">
              <span>{lang === "es" ? "ACCESO RÁPIDO A CAMPOS" : "QUICK FIELD LAUNCHER"}</span>
              <span className="launcher-counter">3 / 3</span>
            </div>
            <div className="telemetry-field-chips">
              {fields.map((f, i) => (
                <button
                  type="button"
                  key={f.id}
                  className="telemetry-field-chip"
                  onClick={() => openField(f.id)}
                >
                  <span className="telemetry-field-index">0{i + 1}</span>
                  <div className="telemetry-field-info">
                    <strong>{f.name[lang] || f.name.en}</strong>
                    <small>{f.area_ac.toFixed(1)} ac · {f.soil_texture[lang] || f.soil_texture.en}</small>
                  </div>
                  <span className={`chip-kind-pill ${f.kind}`}>{f.kind === "dryland" ? (lang === "es" ? "Secano" : "Dryland") : (lang === "es" ? "Riego" : "Irrigated")}</span>
                  <MoveRight size={14} className="telemetry-arrow" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="picker-section page-wrap" id="field-picker">
        <div className="section-heading picker-heading">
          <div>
            <div className="eyebrow"><span className="eyebrow-rule" /> {t("app.location", copy, lang, "FINNEY COUNTY, KANSAS")}</div>
            <h2>{t("pick.choose", copy, lang, "Choose a field")}</h2>
            <p>{t("pick.subtitle", copy, lang, "Choose a field to explore current conditions and compare possible crop rotations.")}</p>
          </div>
          <span className="field-count">{fields.length || 3} / 3 <small>{t("pick.fields_count", copy, lang, "monitored fields")}</small></span>
        </div>
        {loading && (
          <div className="loading-panel">
            <span className="map-spinner" />
            <span>{lang === "es" ? "Preparando el mapa del campo…" : "Preparing the field map…"}</span>
            <div className="skeleton-line" />
          </div>
        )}
        {error && (
          <div className="error-panel" role="alert">
            <strong>{t("error.title", copy, lang)}</strong><span>{error}</span>
            <button type="button" className="text-button" onClick={() => window.location.reload()}>{t("error.retry", copy, lang)}</button>
          </div>
        )}
        {!loading && !error && (
          <div className="field-picker-grid">
            <div className="map-column">
              <FieldMap fields={fields} neighbors={neighbors} onSelect={openField} />
              <div className="map-caption"><Compass size={16} /> <span>{t("home.map_caption", copy, lang, "Field locations and boundaries in Finney County.")}</span></div>
            </div>
            <div className="field-list">
              {fields.map((field, index) => {
                const currentCrops = field.current_crops || rotations.find((rotation) => rotation.id === field.current_rotation_id)?.steps.map((step) => step.crop_id) || [];
                return (
                  <Link className={`field-option field-option-${index + 1}`} href={`/field/${field.id}`} key={field.id} onClick={() => setField(field.id)}>
                    <div className="field-option-top">
                      <span className="field-number">0{index + 1}</span>
                      <span className={`field-kind ${field.kind}`}>{field.kind === "dryland" ? "DRYLAND" : "IRRIGATED"}</span>
                      <ArrowUpRight className="field-arrow" size={20} />
                    </div>
                    <h3>{field.name[lang] || field.name.en}</h3>
                    <div className="field-meta">
                      <span><small>{t("field.area", copy, lang, "FIELD SIZE")}</small>{field.area_ha.toFixed(1)} ha <i>/</i> {field.area_ac.toFixed(1)} ac</span>
                      <span><small>{t("field.soil", copy, lang, "SOIL TEXTURE")}</small>{field.soil_texture[lang] || field.soil_texture.en}</span>
                    </div>
                    <div className="crop-chip-line">
                      <small>{lang === "es" ? "ROTACIÓN DETECTADA" : "DETECTED ROTATION"}</small>
                      <div>{currentCrops.map((id, cropIndex) => {
                        const crop = cropsById.get(id);
                        return crop ? <span className="crop-chip" key={`${id}-${cropIndex}`} style={{ "--chip-color": crop.color } as React.CSSProperties}>{crop.name[lang] || crop.name.en}</span> : null;
                      })}</div>
                    </div>
                    <span className="field-option-bottom"><span>{t("field.open", copy, lang, "Explore field")}</span><MoveRight size={17} /></span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </section>

      <section className="home-lower page-wrap">
        <div className="home-feature-card">
          <div className="home-feature-icon"><Layers3 size={20} /></div>
          <div className="home-feature-content">
            <span className="feature-kicker">{lang === "es" ? "DATOS SATELITALES" : "EARTH OBSERVATION"}</span>
            <h3>{t("home.feature_data.title", copy, lang, "NASA and soil context")}</h3>
            <p>{t("home.feature_data.body", copy, lang, "Satellite signals, soil maps and crop history in one place.")}</p>
          </div>
        </div>
        <div className="home-feature-card">
          <div className="home-feature-icon"><Compass size={20} /></div>
          <div className="home-feature-content">
            <span className="feature-kicker">{lang === "es" ? "PERSONALIZACIÓN" : "USER WEIGHTS"}</span>
            <h3>{t("home.feature_priorities.title", copy, lang, "Your priorities")}</h3>
            <p>{t("home.feature_priorities.body", copy, lang, "Explore trade-offs by changing what matters to you.")}</p>
          </div>
        </div>
        <div className="home-feature-card">
          <div className="home-feature-icon"><ArrowUpRight size={20} /></div>
          <div className="home-feature-content">
            <span className="feature-kicker">{lang === "es" ? "CONFIANZA LOCAL" : "DECISION SUPPORT"}</span>
            <h3>{t("home.feature_judgment.title", copy, lang, "Farmer judgment")}</h3>
            <p>{t("home.feature_judgment.body", copy, lang, "Evidence supports decisions. Local knowledge leads them.")}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
