"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowUpRight, CheckCircle2, Database, Eye, Info } from "lucide-react";
import { ValidationCards } from "@/components/TrustBadge";
import { useFieldShift } from "@/lib/state";
import { getContent, getCrops, getFields, getSources, getValidation } from "@/lib/data";
import { loc, makeT } from "@/lib/i18n";
import { cropNames, type UI } from "@/lib/ui";
import type { Content, CopyFile, Field, FieldId, SourcesFile, ValidationFile } from "@/lib/types";

const NO_STRINGS: CopyFile["strings"] = {};

export default function HowWeKnowPage() {
  const { field: fieldId, lang } = useFieldShift();
  const [sources, setSources] = useState<SourcesFile | null>(null);
  const [fields, setFields] = useState<Field[]>([]);
  const [content, setContent] = useState<Content | null>(null);
  const [crops, setCrops] = useState<UI["crops"]>({});
  const [validation, setValidation] = useState<Partial<Record<FieldId, ValidationFile | null>>>({});
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([getSources(), getFields(), getContent(), getCrops().catch(() => null)])
      .then(async ([sourceData, fieldData, contentData, cropData]) => {
        if (!active) return;
        setSources(sourceData);
        setFields(fieldData.fields);
        setContent(contentData);
        setCrops(cropNames(cropData));
        const bundles = await Promise.all(fieldData.fields.map((item) => getValidation(item.id).then((v) => [item.id, v] as const)));
        if (active) setValidation(Object.fromEntries(bundles));
      })
      .catch((reason: unknown) => {
        console.error("[how-we-know] could not load", reason);
        if (active) setError(true);
      });
    return () => { active = false; };
  }, []);

  const t = useMemo(() => makeT(content?.copy.strings ?? NO_STRINGS, lang), [content, lang]);
  const ui: UI | null = content && sources ? { lang, t, cardText: content.cardText, crops, sources } : null;
  const glossary = content?.glossary?.terms ?? [];
  const term = (id: string) => glossary.find((item) => item.id === id);

  return (
    <div className="trust-page page-wrap">
      <section className="trust-hero">
        <div className="eyebrow"><span className="eyebrow-rule" /> {t("trust.eyebrow", "Transparency before certainty")}</div>
        <h1>{t("trust.title")}</h1>
        <p>{t("trust.subtitle")}</p>
        <div className="trust-intro-note"><Info size={18} aria-hidden="true" /><span>{t("disclaimer.main")}</span></div>
      </section>
      {error && <div className="error-panel" role="alert">{t("error.title", "The data could not be loaded")} <button className="text-button" type="button" onClick={() => window.location.reload()}>{t("error.retry", "Try again")}</button></div>}

      {ui && (
        <section className="trust-section" aria-labelledby="validation-heading">
          <div className="trust-section-heading"><span className="trust-section-icon"><CheckCircle2 size={20} aria-hidden="true" /></span><div><h2 id="validation-heading">{t("trust.validation", "Checks against independent data")}</h2></div></div>
          {fields.map((field) => (
            <div key={field.id} className={field.id === fieldId ? "trust-field current" : "trust-field"}>
              <h3>{loc(field.name, lang)}</h3>
              {validation[field.id]
                ? <ValidationCards validation={validation[field.id] as ValidationFile} ui={ui} />
                : <p className="section-empty">{t("section.not_available", "Not available for this field yet.")}</p>}
            </div>
          ))}
        </section>
      )}

      <section className="trust-section source-section" aria-labelledby="sources-heading">
        <div className="trust-section-heading"><span className="trust-section-icon"><Database size={20} aria-hidden="true" /></span><div><h2 id="sources-heading">{t("trust.sources")}</h2></div></div>
        {sources && (
          <div className="source-table-wrap">
            <table className="source-table">
              <thead><tr><th scope="col">{t("trust.tag", "Tag")}</th><th scope="col">{t("trust.source", "Source")}</th><th scope="col">{t("trust.used_for", "Used for")}</th><th scope="col">{t("trust.coverage", "Resolution and period")}</th></tr></thead>
              <tbody>
                {sources.sources.map((source) => (
                  <tr key={source.tag}>
                    <td><code>{source.tag}</code></td>
                    <td><a href={source.url} target="_blank" rel="noreferrer">{source.name}<ArrowUpRight size={14} aria-hidden="true" /></a><small>{source.provider}</small></td>
                    <td>{source.used_for}<small>{source.what}</small></td>
                    <td>{source.resolution}<small>{source.period}</small></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="trust-section glossary-section" aria-labelledby="glossary-heading">
        <div className="trust-section-heading"><span className="trust-section-icon"><Eye size={20} aria-hidden="true" /></span><div><h2 id="glossary-heading">{t("trust.glossary")}</h2></div></div>
        <div className="explainer-grid">
          {["satellite_vs_ground", "model_estimate"].map((id, index) => {
            const item = term(id);
            return item ? <article key={id}><span>0{index + 1}</span><h3>{loc(item.term, lang)}</h3><p>{loc(item.long, lang)}</p></article> : null;
          })}
        </div>
        <div className="glossary-grid">
          {glossary.map((item) => (
            <details className="glossary-card" key={item.id}>
              <summary><span>{loc(item.term, lang)}</span><small>{loc(item.short, lang)}</small></summary>
              <p>{loc(item.long, lang)}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="trust-closing">
        <p>{t("disclaimer.main")}</p>
        <Link className="button-primary" href={`/field/${fieldId}`}>{t("nav.back_to_field", "Back to the field")} <ArrowUpRight size={17} aria-hidden="true" /></Link>
      </section>
    </div>
  );
}
