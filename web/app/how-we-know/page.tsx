"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { TrustBadge } from "@/components/TrustBadge";
import { SourceChips } from "@/components/SourceChips";
import { useGlean } from "@/lib/state";
import { getContent, getCrops, getFields, getSources, getValidation } from "@/lib/data";
import { formatVar, loc, makeT } from "@/lib/i18n";
import { sourceText } from "@/lib/sourcesEs";
import { cardLine, cropNames, type UI } from "@/lib/ui";
import type { Content, CopyFile, Field, FieldId, SourcesFile, ValidationFile } from "@/lib/types";

const NO_STRINGS: CopyFile["strings"] = {};

export default function HowWeKnowPage() {
  const { field: fieldId, lang } = useGlean();
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
        <h1>{t("trust.title")}</h1>
        <p>{t("trust.subtitle")}</p>
      </section>
      {error && <div className="error-panel" role="alert">{t("error.title", "The data could not be loaded")} <button className="text-button" type="button" onClick={() => window.location.reload()}>{t("error.retry", "Try again")}</button></div>}

      {ui && (
        <section className="trust-section" aria-labelledby="validation-heading">
          <h2 id="validation-heading">{t("trust.validation", "Checks against independent data")}</h2>
          <div className="trust-table-wrap">
            <table className="trust-table validation-table">
              <thead>
                <tr>
                  <th scope="col">{t("nav.field", "Field")}</th>
                  <th scope="col">{t("trust.check", "What we checked")}</th>
                  <th scope="col">{t("trust.match", "Match")}</th>
                  <th scope="col">{t("trust.n", "Data points")}</th>
                  <th scope="col">{t("trust.sources")}</th>
                </tr>
              </thead>
              <tbody>
                {fields.flatMap((field) => {
                  const file = validation[field.id];
                  if (!file || !file.items.length) {
                    return [<tr key={field.id} className={field.id === fieldId ? "current" : ""}><th scope="row">{loc(field.name, lang)}</th><td colSpan={4}>{t("section.not_available", "Not available for this field yet.")}</td></tr>];
                  }
                  return file.items.map((item, index) => (
                    <tr key={`${field.id}-${item.id}`} className={field.id === fieldId ? "current" : ""}>
                      <th scope="row">{index === 0 ? loc(field.name, lang) : <span className="sr-only">{loc(field.name, lang)}</span>}</th>
                      <td>{cardLine(ui, "validation", item.id, item.vars)}</td>
                      <td><TrustBadge level={item.level} label={t(`trust.level.${item.level}`)} /></td>
                      <td>{formatVar("n", item.n, lang)}</td>
                      <td><SourceChips tags={item.sources} sources={ui.sources} /></td>
                    </tr>
                  ));
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="trust-section source-section" aria-labelledby="sources-heading">
        <h2 id="sources-heading">{t("trust.sources")}</h2>
        {sources && (
          <div className="trust-table-wrap">
            <table className="trust-table source-table">
              <thead><tr><th scope="col">{t("trust.tag", "Tag")}</th><th scope="col">{t("trust.source", "Source")}</th><th scope="col">{t("trust.used_for", "Used for")}</th><th scope="col">{t("trust.coverage", "Resolution and period")}</th></tr></thead>
              <tbody>
                {sources.sources.map((source) => (
                  <tr key={source.tag}>
                    <td><code>{source.tag}</code></td>
                    <td><a href={source.url} target="_blank" rel="noreferrer">{source.name}<ArrowUpRight size={14} aria-hidden="true" /></a><small>{source.provider}</small></td>
                    <td>{sourceText(source.used_for, lang)}<small>{sourceText(source.what, lang)}</small></td>
                    <td>{sourceText(source.resolution, lang)}<small>{sourceText(source.period, lang)}</small></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="trust-section glossary-section" aria-labelledby="glossary-heading">
        <h2 id="glossary-heading">{t("trust.glossary")}</h2>
        <div className="explainer-grid">
          {["satellite_vs_ground", "model_estimate"].map((id) => {
            const item = term(id);
            return item ? <article key={id}><h3>{loc(item.term, lang)}</h3><p>{loc(item.long, lang)}</p></article> : null;
          })}
        </div>
        <div className="glossary-grid">
          {glossary.filter((item) => !["satellite_vs_ground", "model_estimate"].includes(item.id)).map((item) => (
            <details className="glossary-card" key={item.id}>
              <summary><span>{loc(item.term, lang)}</span><small>{loc(item.short, lang)}</small></summary>
              <p>{loc(item.long, lang)}</p>
            </details>
          ))}
        </div>
      </section>

      <p className="trust-back"><Link className="button-primary" href={`/field/${fieldId}`}>{t("nav.back_to_field", "Back to the field")}</Link></p>
    </div>
  );
}
