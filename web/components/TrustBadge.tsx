"use client";

import { AlertTriangle, CircleCheck, Info } from "lucide-react";
import type { Lang, SourcesFile, ValidationFile } from "@/lib/types";
import type { CardTextFile, CopyFile } from "@/lib/types";
import { fill, t } from "@/lib/i18n";
import { SourceChips } from "@/components/SourceChips";

const trustIcons = { high: CircleCheck, medium: Info, low: AlertTriangle };

export function TrustBadge({
  level,
  label,
}: {
  level: "high" | "medium" | "low";
  label: string;
}) {
  const Icon = trustIcons[level];
  return <span className={`trust-badge trust-${level}`}><Icon size={15} />{label}</span>;
}

export function ValidationCards({
  validation,
  cardText,
  copy,
  sources,
  lang,
}: {
  validation: ValidationFile;
  cardText: CardTextFile;
  copy: CopyFile["strings"];
  sources: SourcesFile;
  lang: Lang;
}) {
  return (
    <div className="validation-grid">
      {validation.checks.map((check) => (
        <article className="validation-card" key={check.id}>
          <TrustBadge level={check.level} label={t(`confidence.${check.level}`, copy, lang)} />
          <p>{fill(cardText.validation[check.id], check.vars, lang)}</p>
          <SourceChips ids={check.source_ids} sources={sources} lang={lang} />
        </article>
      ))}
    </div>
  );
}
