"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowUpRight, CheckCircle2, Database, Eye, Info } from "lucide-react";
import { SourceChips } from "@/components/SourceChips";
import { ValidationCards } from "@/components/TrustBadge";
import { useFieldShift } from "@/lib/state";
import { getContent, getFieldBundle, getFields, getSources } from "@/lib/data";
import { t } from "@/lib/i18n";
import type { CardTextFile, CopyFile, FieldBundle, FieldId, FieldsFile, SourcesFile } from "@/lib/types";

export default function HowWeKnowPage() {
  const { field, lang } = useFieldShift();
  const [sources, setSources] = useState<SourcesFile | null>(null);
  const [fields, setFields] = useState<FieldsFile | null>(null);
  const [bundle, setBundle] = useState<FieldBundle | null>(null);
  const [copy, setCopy] = useState<CopyFile["strings"]>({});
  const [cardText, setCardText] = useState<CardTextFile | null>(null);
  const [glossary, setGlossary] = useState<Record<string, { term: { en: string; es?: string }; short: { en: string; es?: string }; long: { en: string; es?: string }; source_ids?: string[] }>>({});
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([getSources(), getFields(), getContent(), getFieldBundle(field as FieldId)])
      .then(([sourceData, fieldData, content, fieldBundle]) => {
        if (!active) return;
        setSources(sourceData);
        setFields(fieldData);
        setBundle(fieldBundle);
        setCopy(content.copy.strings);
        setCardText(content.cardText);
        setGlossary((content.glossary as { entries: typeof glossary }).entries);
      })
      .catch((reason: unknown) => {
        console.error("Could not load trust and source details", reason);
        if (active) setError(true);
      });
    return () => { active = false; };
  }, [field]);

  return (
    <div className="trust-page page-wrap">
      <section className="trust-hero">
        <div className="eyebrow"><span className="eyebrow-rule" /> TRANSPARENCY BEFORE CERTAINTY</div>
        <h1>{t("trust.title", copy, lang)}</h1>
        <p>{t("trust.subtitle", copy, lang)}</p>
        <div className="trust-intro-note"><Info size={18} /><span>{t("disclaimer.main", copy, lang)}</span></div>
      </section>
      {error && <div className="error-panel" role="alert">{t("error.title", copy, lang)} <button className="text-button" type="button" onClick={() => window.location.reload()}>{t("error.retry", copy, lang)}</button></div>}
      {bundle && cardText && sources && (
        <section className="trust-section">
          <div className="trust-section-heading"><span className="trust-section-icon"><CheckCircle2 size={20} /></span><div><h2>{t("trust.validation", copy, lang)}</h2><p>{t("trust.validation_status", copy, lang)}</p></div></div>
          <ValidationCards validation={bundle.validation} cardText={cardText} copy={copy} sources={sources} lang={lang} />
          <div className="validation-definition"><span>INPUT CHECK</span><p>{t("trust.input_check", copy, lang)}</p><span>PROCESS CHECK</span><p>{t("trust.process_check", copy, lang)}</p><span>OUTCOME CHECK</span><p>{t("trust.outcome_check", copy, lang)}</p></div>
        </section>
      )}
      <section className="trust-section source-section">
        <div className="trust-section-heading"><span className="trust-section-icon"><Database size={20} /></span><div><h2>{t("trust.sources", copy, lang)}</h2><p>{t("trust.sources_status", copy, lang)}</p></div></div>
        {!sources ? <div className="trust-loading">{t("trust.loading_sources", copy, lang)}</div> : (
          <div className="source-table-wrap">
            <table className="source-table">
              <thead><tr><th>TAG</th><th>{lang === "es" ? "FUENTE" : "SOURCE"}</th><th>{lang === "es" ? "FUNCIÓN Y LÍMITE" : "ROLE AND LIMIT"}</th><th>{lang === "es" ? "LICENCIA / TÉRMINOS" : "LICENSE / TERMS"}</th></tr></thead>
              <tbody>{Object.entries(sources.sources).map(([id, source]) => (
                <tr key={id}><td><code>{id}</code></td><td><a href={source.url} target="_blank" rel="noreferrer">{source.name[lang] || source.name.en}<ArrowUpRight size={14} /></a></td><td>{source.role[lang] || source.role.en}</td><td>{source.license || t("trust.license_terms", copy, lang)}</td></tr>
              ))}</tbody>
            </table>
          </div>
        )}
        {fields && <p className="source-note"><Eye size={16} />{t("trust.selected_field", copy, lang).replace("{name}", fields.fields.find((item) => item.id === field)?.name[lang] || field)}</p>}
      </section>
      <section className="trust-section glossary-section">
        <div className="trust-section-heading"><span className="trust-section-icon"><Eye size={20} /></span><div><h2>{t("trust.glossary", copy, lang)}</h2><p>{t("trust.glossary_intro", copy, lang)}</p></div></div>
        <div className="glossary-grid">
          {Object.entries(glossary).map(([id, item]) => (
            <details className="glossary-card" key={id}>
              <summary><span>{item.term[lang] || item.term.en}</span><small>{item.short[lang] || item.short.en}</small></summary>
              <p>{item.long[lang] || item.long.en}</p>
              {sources && <SourceChips ids={item.source_ids || []} sources={sources} lang={lang} />}
            </details>
          ))}
        </div>
        <div className="explainer-grid">
          <article><span>01</span><h3>{t("trust.satellite_title", copy, lang)}</h3><p>{t("trust.satellite_vs_ground", copy, lang)}</p></article>
          <article><span>02</span><h3>{t("trust.model_title", copy, lang)}</h3><p>{t("trust.model_estimate", copy, lang)}</p></article>
        </div>
      </section>
      <section className="trust-closing">
        <p>{lang === "es" ? "Explore los datos y modelos aplicados a sus campos para evaluar rotaciones sostenibles." : "Ready to explore satellite evidence and compare rotations for your fields?"}</p>
        <Link className="button-primary" href={`/field/${field}`}>{lang === "es" ? "Volver al campo" : "Return to field workspace"} <ArrowUpRight size={17} /></Link>
      </section>
    </div>
  );
}
