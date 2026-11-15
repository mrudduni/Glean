"use client";

import { AlertTriangle, CircleCheck, Info } from "lucide-react";
import type { Level, ValidationFile } from "@/lib/types";
import { SourceChips } from "@/components/SourceChips";
import { cardLine, type UI } from "@/lib/ui";

const icons = { good: CircleCheck, fair: Info, limited: AlertTriangle };
const legacyClass = { good: "high", fair: "medium", limited: "low" } as const;

export function TrustBadge({ level, label }: { level: Level; label: string }) {
  const Icon = icons[level];
  return <span className={`trust-badge trust-${legacyClass[level]}`}><Icon size={15} aria-hidden="true" />{label}</span>;
}

export function ValidationCards({ validation, ui }: { validation: ValidationFile; ui: UI }) {
  if (!validation.items.length) return <p className="section-empty">{ui.t("trust.no_validation", "No validation checks for this field yet.")}</p>;
  return (
    <div className="validation-grid">
      {validation.items.map((item) => (
        <article className="validation-card" key={item.id}>
          <TrustBadge level={item.level} label={ui.t(`trust.level.${item.level}`)} />
          <p>{cardLine(ui, "validation", item.id, item.vars)}</p>
          <small className="micro-note">n = {item.n}</small>
          <SourceChips tags={item.sources} sources={ui.sources} />
        </article>
      ))}
    </div>
  );
}
