"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, Check, ChevronDown, ChevronUp, Droplets, Info, Leaf, ShieldCheck } from "lucide-react";
import type {
  CardTextFile, CopyFile, Crop, Field, Lang, Rotation, SourcesFile, StrategyEntry,
} from "@/lib/types";
import { fill, formatVar, t } from "@/lib/i18n";
import { criterionIds, pickShown, scoreEntry, weightsFromSliders, whyBullets, type Constraints } from "@/lib/score";
import { SourceChips } from "@/components/SourceChips";
import { TrustBadge } from "@/components/TrustBadge";
import { useFieldShift } from "@/lib/state";
import { theme } from "@/lib/theme";

const criterionCopy: Record<string, string> = {
  water: "priority.water",
  soil: "priority.soil",
  climate: "priority.climate",
  market: "priority.market",
  operations: "priority.operations",
};

const rotationColors = theme.rotation;

export function StrategyPanel({
  entries,
  rotations,
  crops,
  field,
  cardText,
  copy,
  sources,
  lang,
  scenarioAdjustments,
}: {
  entries: StrategyEntry[];
  rotations: Rotation[];
  crops: Crop[];
  field: Field;
  cardText: CardTextFile;
  copy: CopyFile["strings"];
  sources: SourcesFile;
  lang: Lang;
  scenarioAdjustments: Record<string, { irrigation_factor: number; climate_delta: number }>;
}) {
  const { weights: sliders, cap, climate, hay, cotton, forage } = useFieldShift();
  const [showHidden, setShowHidden] = useState(false);
  const weights = useMemo(() => weightsFromSliders(sliders), [sliders]);
  const scenarioKey = `${cap}|${climate}`;
  const adjustment = useMemo(
    () => scenarioAdjustments[scenarioKey] || { irrigation_factor: 1, climate_delta: 0 },
    [scenarioAdjustments, scenarioKey]
  );
  const activeEntries = useMemo(() => entries.map((entry) => ({
    ...entry,
    needs_irrigation_mm: Math.round(entry.needs_irrigation_mm * adjustment.irrigation_factor),
    criteria: {
      ...entry.criteria,
      climate: { ...entry.criteria.climate, norm: Math.max(0, Math.min(10, entry.criteria.climate.norm + adjustment.climate_delta)) },
    },
  })), [entries, adjustment]);
  const constraints: Constraints = { cap, hay, cotton, forage };
  const { shown, hidden } = pickShown(activeEntries, weights, constraints);
  const rotationMap = new Map(rotations.map((rotation) => [rotation.id, rotation]));
  const cropMap = new Map(crops.map((crop) => [crop.id, crop]));
  const reasons = {
    needs_more_water: t("strategy.hidden_water", copy, lang, "Needs more water than selected"),
    needs_equipment: t("strategy.hidden_equipment", copy, lang, "Needs unavailable equipment"),
    needs_forage_market: t("strategy.hidden_forage", copy, lang, "Needs a forage market"),
    lower_rank: t("strategy.lower_rank", copy, lang),
  };
  return (
    <section className="workspace-section strategies-section" id="strategies">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> COMPARE YOUR OPTIONS</div>
          <h2>{t("strategy.title", copy, lang)}</h2>
          <p>{t("strategy.subtitle", copy, lang)}</p>
        </div>
        <span className="section-index">04 / 06</span>
      </div>
      {shown.length <= 1 && <div className="empty-state"><Info size={17} />{t("strategy.empty", copy, lang)}</div>}
      <div className="strategy-grid">
        {shown.map((entry) => {
          const rotation = rotationMap.get(entry.id);
          if (!rotation) return null;
          const cropIds = entry.id === "R0" ? (field.current_crops || rotation.steps.map((step) => step.crop_id)) : rotation.steps.map((step) => step.crop_id);
          const score = scoreEntry(entry, weights);
          const why = entry.id === "R0" ? [] : whyBullets(entry, weights);
          const allRisks = entry.crops_without_local_market.length
            ? [...entry.risks, "no_local_market"]
            : entry.risks;
          return (
            <article className={`strategy-card ${entry.id === "R0" ? "current-strategy" : ""}`} key={entry.id} style={{ "--rotation-color": rotationColors[entry.id] || "#557a56" } as React.CSSProperties}>
              <div className="strategy-card-head">
                <div className="strategy-id">{entry.id}</div>
                <div className="strategy-heading">
                  <div className="strategy-title-line">
                    <h3>{rotation.name[lang] || rotation.name.en}</h3>
                    {entry.id === "R0" && <span className="current-pill"><Check size={11} />{t("strategy.current", copy, lang)}</span>}
                  </div>
                  <p>{fill(cardText.rotations[entry.id], {}, lang)}</p>
                </div>
              </div>
              <div className="strategy-crops">{cropIds.map((id, index) => {
                const crop = cropMap.get(id);
                return crop ? <span className="crop-chip" key={`${id}-${index}`} style={{ "--chip-color": crop.color } as React.CSSProperties}>{crop.name[lang] || crop.name.en}</span> : null;
              })}</div>
              <div className="score-row">
                <div><small>{t("strategy.score", copy, lang)}</small><strong>{score}<span>/100</span></strong></div>
                <div className="score-meter" role="meter" aria-valuenow={score} aria-valuemin={0} aria-valuemax={100} aria-label={`${t("strategy.score", copy, lang)} ${score} out of 100`}>
                  <i style={{ width: `${score}%` }} />
                </div>
              </div>
              <div className="strategy-meta-row">
                <TrustBadge level={entry.confidence} label={t(`confidence.${entry.confidence}`, copy, lang)} />
                <span className="water-need"><Droplets size={15} />{formatVar("amount_mm", entry.needs_irrigation_mm, lang)}</span>
              </div>
              <div className="criteria-bars">
                {criterionIds.map((id) => (
                  <div className="criterion-bar" key={id}>
                    <span>{t(criterionCopy[id], copy, lang)}</span>
                    <i><b style={{ width: `${entry.criteria[id].norm * 10}%` }} /></i>
                    <strong>{entry.criteria[id].norm.toFixed(1)}</strong>
                  </div>
                ))}
              </div>

              <CardSection title={t("strategy.why", copy, lang)} icon={<Leaf size={15} />}>
                {entry.id === "R0"
                  ? <p className="section-empty">{t("strategy.current_baseline", copy, lang)}</p>
                  : <ul>{why.map((id) => <li key={id}>{fill(cardText.why[id], entry.criteria[id].vars, lang)}</li>)}</ul>}
              </CardSection>
              <CardSection title={t("strategy.evidence", copy, lang)} icon={<Info size={15} />}>
                {entry.evidence.length ? entry.evidence.map((item, index) => (
                  <div className="text-evidence" key={`${item.text_id}-${index}`}>
                    <p>{fill(cardText.evidence[item.text_id], { ...entry.criteria.water.vars, ...item.vars }, lang)}</p>
                    <SourceChips ids={item.source_ids} sources={sources} lang={lang} />
                  </div>
                )) : <p className="section-empty">{lang === "es" ? "La línea base no tiene una explicación de evidencia adicional." : "The baseline has no additional evidence explanation."}</p>}
              </CardSection>
              <CardSection title={t("strategy.benefits", copy, lang)} icon={<ShieldCheck size={15} />}>
                {entry.benefits.length ? entry.benefits.map((item, index) => (
                  <div className="text-evidence" key={`${item.text_id}-${index}`}>
                    <p>{fill(cardText.benefits[item.text_id], item.vars, lang)}</p>
                    <SourceChips ids={item.source_ids} sources={sources} lang={lang} />
                  </div>
                )) : <p className="section-empty">{lang === "es" ? "La línea base se muestra sin beneficios añadidos." : "The baseline is shown without added benefit claims."}</p>}
              </CardSection>
              <CardSection title={t("strategy.gaps", copy, lang)} icon={<Info size={15} />} tone="gap">
                <ul>{entry.gaps.map((id) => <li key={id}>{fill(cardText.gaps[id], {}, lang)}</li>)}</ul>
              </CardSection>
              <CardSection title={t("strategy.risks", copy, lang)} icon={<AlertTriangle size={15} />} tone="risk">
                <ul>{allRisks.map((id, index) => <li key={`${id}-${index}`}>{fill(cardText.risks[id], {}, lang)}</li>)}</ul>
              </CardSection>
            </article>
          );
        })}
      </div>
      {hidden.length > 0 && (
        <div className="hidden-strategies">
          <button type="button" className="hidden-toggle" aria-expanded={showHidden} onClick={() => setShowHidden((value) => !value)}>
            <span>{showHidden ? <ChevronUp size={16} /> : <ChevronDown size={16} />}{showHidden ? t("strategy.hide_hidden", copy, lang) : t("strategy.show_hidden", copy, lang).replace("{count}", String(hidden.length))}</span>
            <span className="hidden-count">{hidden.length}</span>
          </button>
          {showHidden && (
            <div className="hidden-list">
              {hidden.map(({ entry, reason }) => (
                <div className="hidden-item" key={entry.id}>
                  <span className="hidden-rotation">{entry.id} · {rotationMap.get(entry.id)?.name[lang] || rotationMap.get(entry.id)?.name.en}</span>
                  <span>{reasons[reason]}</span>
                  <span className="hidden-score">{scoreEntry(entry, weights)}/100</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      <p className="strategy-footnote">{t("strategy.score_note", copy, lang)}</p>
    </section>
  );
}

function CardSection({ title, icon, children, tone = "" }: { title: string; icon: React.ReactNode; children: React.ReactNode; tone?: string }) {
  return <section className={`strategy-subsection ${tone}`}><h4>{icon}{title}</h4>{children}</section>;
}
