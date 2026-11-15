"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { MoveRight } from "lucide-react";
import { FieldMap } from "@/components/FieldMap";
import { CropChips } from "@/components/CropChips";
import { SourceChips } from "@/components/SourceChips";
import { useGlean } from "@/lib/state";
import { getContent, getCrops, getFields, getSources } from "@/lib/data";
import { loc, makeT, textureLabel, yearsLabel } from "@/lib/i18n";
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
  const area = (field: Field) => `${field.area_ha.toLocaleString(lang === "es" ? "es-ES" : "en-US", { maximumFractionDigits: 0 })} ha · ${field.area_ac.toLocaleString(lang === "es" ? "es-ES" : "en-US", { maximumFractionDigits: 0 })} ac`;

  return (
    <div className="home-page page-wrap">
      <header className="home-intro">
        <h1>{t("app.tagline")}</h1>
        <p>{t("pick.subtitle")}</p>
      </header>

      {loading && (
        <div className="home-grid" aria-busy="true" aria-label={t("pick.title")}>
          <div className="skeleton-block home-map-skeleton" />
          <div className="home-fields">{[0, 1, 2].map((i) => <div className="skeleton-block home-field-skeleton" key={i} />)}</div>
        </div>
      )}
      {error && (
        <div className="error-panel" role="alert">
          <strong>{t("error.title", "The data could not be loaded")}</strong>
          <span>{t("error.check_connection", "Check your connection and try again.")}</span>
          <button type="button" className="text-button" onClick={() => window.location.reload()}>{t("error.retry", "Try again")}</button>
        </div>
      )}

      {!loading && !error && (
        <section className="home-grid" aria-labelledby="picker-heading">
          <div className="home-map">
            <FieldMap fields={fields} onSelect={openField} t={t} lang={lang} labels />
            <p className="map-caption">{t("home.map_caption", "Click a field outline to open it.")}</p>
          </div>

          <div className="home-fields">
            <h2 id="picker-heading">{t("pick.title")}</h2>
            <ul className="field-list">
              {fields.map((field) => (
                <li key={field.id}>
                  <Link className="field-option" href={`/field/${field.id}`} onClick={() => setField(field.id)}>
                    <span className="field-option-head">
                      <span className="field-option-name">{loc(field.name, lang)}</span>
                      <span className={`field-kind ${field.kind}`}>{t(`field.kind.${field.kind}`, KIND_LABEL[field.kind])}</span>
                    </span>
                    <span className="field-option-meta">{area(field)} · {textureLabel(t, field.soil.texture, lang)}</span>
                    <span className="field-option-rotation">
                      <span className="field-option-label">{t("overview.current_rotation")}</span>
                      <CropChips steps={field.detected.sequence} ui={ui} />
                    </span>
                    <span className="field-option-go">{t("pick.open_field")}<MoveRight size={16} aria-hidden="true" /></span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {sources && (
        <p className="home-sources">
          <span>{t("home.data_in_use", "Data behind these fields")}{historySpan ? ` (${historySpan})` : ""}:</span>
          <SourceChips tags={sources.sources.map((item) => item.tag)} sources={sources} />
          <Link href="/how-we-know">{t("nav.trust")}</Link>
        </p>
      )}
    </div>
  );
}
