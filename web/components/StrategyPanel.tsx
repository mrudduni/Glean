"use client";

import { useRef, useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp, Droplets, Info } from "lucide-react";
import type { CapId, CopyFile, CriterionId, EquipmentId, Rotation, RotationId, StrategyEntry, SummaryFile } from "@/lib/types";
import { fill, formatVar, interpolate, loc } from "@/lib/i18n";
import { useGlean } from "@/lib/state";
import { CRITERION_IDS } from "@/lib/schemas";
import { benefitsShown, scoreEntry, whyBullets, type Constraints, type ExclusionReason, type Picked, type Weights } from "@/lib/score";
import { cardLine, cropLabel, type UI } from "@/lib/ui";
import { SourceChips } from "@/components/SourceChips";
import { TrustBadge } from "@/components/TrustBadge";
import { CropChips } from "@/components/CropChips";
import { AnimatedNumber } from "@/components/AnimatedNumber";
import { rotColor } from "@/lib/theme";

/** Criterion label from card_text; "Heat and frost risk" reads backwards on a better-is-longer bar, so it uses the wireframe's wording. */
export function criterionLabel(ui: UI, k: CriterionId): string {
  if (k === "heat_frost_risk") return ui.t("criteria.heat_frost_display", "Avoids heat and frost damage");
  return loc(ui.cardText.criteria_labels[k], ui.lang) || k;
}

export function rotationSteps(id: RotationId, rotations: Rotation[], summary: SummaryFile) {
  return id === "R0" ? summary.current_rotation.steps : rotations.find((rotation) => rotation.id === id)?.steps ?? [];
}

export function StrategyPanel({
  picked, weights, rotations, summary, irrigation, shownAt = {}, copy, ui, irrigated = true,
}: {
  irrigated?: boolean;
  picked: Picked;
  weights: Weights;
  rotations: Rotation[];
  summary: SummaryFile;
  irrigation: Partial<Record<RotationId, number>>;
  shownAt?: Partial<Record<RotationId, CapId | "none">>;
  copy: CopyFile["strings"];
  ui: UI;
}) {
  const { t, lang } = ui;
  const [showHidden, setShowHidden] = useState(false);
  const [active, setActive] = useState(0);
  const gridRef = useRef<HTMLDivElement>(null);
  const onSwipe = () => {
    const grid = gridRef.current;
    const card = grid?.querySelector<HTMLElement>(".strategy-card");
    if (grid && card) setActive(Math.round(grid.scrollLeft / (card.offsetWidth + 12)));
  };
  const name = (id: RotationId) => loc(ui.cardText.rotations[id]?.name, lang) || id;
  const hiddenCount = picked.hidden.length + picked.others.length;
  // Caveats every shown card carries are said once, below the cards, instead of four times.
  const common = (lists: string[][]) => (lists.length > 1 ? lists.reduce((a, b) => a.filter((item) => b.includes(item))) : []);
  const sharedGaps = common(picked.shown.map((entry) => entry.gap_ids));
  const sharedRisks = common(picked.shown.map((entry) => entry.risk_ids));
  // Options outside the farmer's limits go after the ones that fit, so the eye lands on what is possible.
  const ordered = [...picked.shown].sort((a, b) => Number(Boolean(picked.filled[a.rotation_id])) - Number(Boolean(picked.filled[b.rotation_id])));
  const currentEntry = picked.shown.find((entry) => entry.rotation_id === "R0");
  // A criterion that scores the same for every option tells nothing apart: say it once instead of drawing it four times.
  const uniform = CRITERION_IDS.filter((k) => new Set(picked.shown.map((entry) => Math.round(entry.criteria[k].norm))).size === 1 && picked.shown.length > 1);
  const label = (k: CriterionId) => criterionLabel(ui, k);

  return (
    <div className="strategy-results">
      {picked.shown.length - 1 === Object.keys(picked.filled).length && <div className="empty-state"><Info size={17} aria-hidden="true" />{irrigated
        ? t("strategies.none_fit", "No other rotation fits these limits. Try a higher water cap or tick the equipment you have.")
        : t("strategies.none_fit_dryland", "No other dryland rotation fits these limits. Tick the equipment or buyers you have to see more.")}</div>}
      <p className="criteria-hint">
        {t("card.bars_hint_tick", "Longer bars are better for you; 100 is the best of the options shown. The tick marks your current rotation.")}
        {uniform.length > 0 && <> {interpolate(t("card.uniform", "Same for every option, so not drawn: {list}."), { list: uniform.map((k) => `${label(k)} (${Math.round(picked.shown[0].criteria[k].norm)})`).join(", ") })}</>}
      </p>
      <div className="strategy-grid" data-count={ordered.length} ref={gridRef} onScroll={onSwipe}>
        {ordered.map((entry) => (
          <StrategyCard key={entry.rotation_id} entry={entry} currentEntry={currentEntry} hiddenCriteria={uniform} reason={picked.filled[entry.rotation_id]} rotations={rotations} weights={weights} steps={rotationSteps(entry.rotation_id, rotations, summary)} irrigation={irrigation[entry.rotation_id]} shownAt={shownAt[entry.rotation_id]} sharedGaps={sharedGaps} sharedRisks={sharedRisks} ui={ui} />
        ))}
      </div>
      {ordered.length > 1 && (
        <p className="swipe-dots" aria-hidden="true">{ordered.map((entry, index) => <i key={entry.rotation_id} className={index === active ? "active" : ""} />)}</p>
      )}
      {(sharedGaps.length > 0 || sharedRisks.length > 0) && (
        <section className="shared-caveats" id="shared-caveats" aria-labelledby="shared-caveats-heading">
          <h3 id="shared-caveats-heading">{t("card.shared_title", "Applies to every option above")}</h3>
          <div className="shared-caveats-grid">
            {sharedGaps.length > 0 && (
              <div>
                <h4>{t("card.gaps")}</h4>
                <ul>{sharedGaps.map((gap) => <li key={gap}>{cardLine(ui, "gaps", gap)}</li>)}</ul>
              </div>
            )}
            {sharedRisks.length > 0 && (
              <div>
                <h4>{t("card.risks")}</h4>
                <ul>{sharedRisks.map((risk) => <li key={risk}>{cardLine(ui, "risks", risk)}</li>)}</ul>
              </div>
            )}
          </div>
        </section>
      )}
      {hiddenCount > 0 && (
        <div className="hidden-strategies">
          <button type="button" className="hidden-toggle" aria-expanded={showHidden} aria-controls="hidden-strategy-list" onClick={() => setShowHidden((value) => !value)}>
            <span>{showHidden ? <ChevronUp size={16} aria-hidden="true" /> : <ChevronDown size={16} aria-hidden="true" />}{fill(copy["card.hidden_count"], { n: hiddenCount }, lang)}</span>
            <span className="hidden-count">{hiddenCount}</span>
          </button>
          {showHidden && (
            <div className="hidden-list" id="hidden-strategy-list">
              {picked.hidden.map(({ entry, reason }) => (
                <div className="hidden-item" key={entry.rotation_id}>
                  <span className="hidden-rotation">{name(entry.rotation_id)}</span>
                  <span>{cardLine(ui, "infeasible", reason)}</span>
                  <span className="hidden-score">{scoreEntry(entry, weights)}/100</span>
                </div>
              ))}
              {picked.others.map((entry) => (
                <div className="hidden-item" key={entry.rotation_id}>
                  <span className="hidden-rotation">{name(entry.rotation_id)}</span>
                  <span>{t("card.lower_score", "Fits your limits, but scores lower than the three shown.")}</span>
                  <span className="hidden-score">{scoreEntry(entry, weights)}/100</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      <p className="strategy-footnote">{t("strategies.score_note", "Scores are relative to the rotations compared here, 0 to 100. They are model estimates, not forecasts.")}</p>
    </div>
  );
}

const CAP_ORDER: CapId[] = ["dryland", "cap150", "cap300", "cap450"];

/** What the farmer could change to include a rotation that is outside their limits. */
function unlockHint(entry: StrategyEntry, reason: ExclusionReason, rotations: Rotation[], t: UI["t"], constraints: Constraints): string | null {
  const tick = (label: string) => interpolate(t("card.unlock_tick", "Tick “{option}” to include it."), { option: label });
  if (reason === "needs_equipment") {
    const owned: Record<EquipmentId, boolean> = { hay: constraints.hay, cotton: constraints.cotton };
    const missing = entry.requires_equipment.filter((item) => !owned[item]);
    return missing.length ? missing.map((item) => tick(t(`constraints.${item}_equipment`))).join(" ") : null;
  }
  if (reason === "no_local_market") return constraints.forage ? null : tick(t("constraints.forage_buyer"));
  const minCap = rotations.find((rotation) => rotation.id === entry.rotation_id)?.min_cap;
  if (!minCap || CAP_ORDER.indexOf(minCap) <= CAP_ORDER.indexOf(constraints.cap)) return null;
  return interpolate(t("card.unlock_cap", "Set the water limit to “{option}” or higher to include it."), { option: t(`constraints.cap.${minCap}`) });
}

function StrategyCard({
  entry, currentEntry, hiddenCriteria, reason, weights, steps, rotations, irrigation, shownAt, sharedGaps, sharedRisks, ui,
}: {
  currentEntry?: StrategyEntry;
  hiddenCriteria: CriterionId[];
  entry: StrategyEntry;
  shownAt?: CapId | "none";
  reason?: ExclusionReason;
  weights: Weights;
  rotations: Rotation[];
  steps: Rotation["steps"];
  irrigation: number | undefined;
  sharedGaps: string[];
  sharedRisks: string[];
  ui: UI;
}) {
  const { t, lang } = ui;
  const id = entry.rotation_id;
  const gaps = entry.gap_ids.filter((gap) => !sharedGaps.includes(gap));
  const risks = entry.risk_ids.filter((risk) => !sharedRisks.includes(risk));
  const sharedNote = (n: number) => (n > 0
    ? <li className="shared-note"><a href="#shared-caveats">{interpolate(t("card.shared_more", "Plus {n} that apply to every option, listed below the cards."), { n })}</a></li>
    : null);
  const score = scoreEntry(entry, weights);
  const current = id === "R0";
  // R0 is the baseline: its why and benefit lines would compare it with itself.
  // A rotation that cannot get the water it needs here has no fair why or benefit lines either.
  const unavailable = Boolean(reason);
  const unfair = current || shownAt === "none" || unavailable;
  const es = lang === "es";   // Spanish fallbacks until these keys reach copy.json
  // A reason to switch must be something this option does better than the current rotation.
  const why = unfair ? [] : whyBullets(entry, weights).filter((k) => !currentEntry || entry.criteria[k].norm > currentEntry.criteria[k].norm);
  const benefits = unfair ? [] : benefitsShown(entry);
  const { cap, hay, cotton, forage } = useGlean();
  const unlock = reason ? unlockHint(entry, reason, rotations, t, { cap, hay, cotton, forage }) : null;
  const text = ui.cardText.rotations[id];
  const label = (k: CriterionId) => criterionLabel(ui, k);
  // "Needs more water" and "this field has no irrigation" say one thing; show it once.
  const noWaterHere = reason === "needs_more_water" && shownAt === "none";
  return (
    <article className={`strategy-card ${current ? "current-strategy" : ""} ${unavailable ? "unavailable" : ""}`} style={{ "--rotation-color": rotColor(id) } as React.CSSProperties} aria-labelledby={`card-${id}`}>
      <div className="strategy-card-head">
        <div className="strategy-heading">
          <h3 id={`card-${id}`}><span className="rotation-key" aria-hidden="true" />{loc(text?.name, lang) || id}</h3>
          {unavailable && <p className="unavailable-flag">{t("card.unavailable", "Not available with your current limits")}</p>}
          {reason && !noWaterHere && (
            <p className="infeasible-badge">
              <AlertTriangle size={13} aria-hidden="true" />
              <span>{cardLine(ui, "infeasible", reason)}{unlock && <b> {unlock}</b>}</span>
            </p>
          )}
          {noWaterHere && (
            <p className="infeasible-badge">
              <AlertTriangle size={13} aria-hidden="true" />
              <span>{t("card.needs_water_none", "Needs irrigation, and this field has none. Its numbers assume no water.")}</span>
            </p>
          )}
          {shownAt && !noWaterHere && <p className="shown-at">{shownAt === "none"
            ? t("card.no_water_here", es ? "Este campo no tiene riego. Estas cifras suponen cero agua, así que subestiman esta rotación." : "This field is not irrigated. These numbers assume no water, so they understate this rotation.")
            : interpolate(t("card.shown_at", es ? "Cifras mostradas con: {cap}." : "Numbers shown with: {cap}."), { cap: t(`constraints.cap.${shownAt}`) })}</p>}
          <p className="strategy-tagline">{loc(text?.tagline, lang)}</p>
        </div>
      </div>
      <div className="strategy-crops"><CropChips steps={steps} ui={ui} /></div>
      <div className="strategy-score">
      <div className="score-row">
        <div><small title={t("card.fit_help", "How well this option matches the priorities you set, compared with the other options here. It changes when you move a slider.")}>{t("card.fit_label", "Fit with your priorities")}</small><strong><AnimatedNumber value={score} /><span>/100</span></strong></div>
        <div className="score-meter" role="meter" aria-valuenow={score} aria-valuemin={0} aria-valuemax={100} aria-label={t("card.fit_label", "Fit with your priorities")}>
          <i style={{ width: `${score}%` }} />
        </div>
      </div>
      <div className="strategy-meta-row">
        <span className="confidence-label">{t("card.confidence")}</span>
        <TrustBadge level={entry.confidence} label={t(`trust.level.${entry.confidence}`)} />
        {irrigation !== undefined && <span className="water-need" title={t("replay.metric.irrigation")}><Droplets size={15} aria-hidden="true" />{formatVar("irrigation_mm", irrigation, lang)}</span>}
      </div>
      </div>
      <div className="criteria-bars">
        {CRITERION_IDS.filter((k) => !hiddenCriteria.includes(k)).map((k) => {
          const mine = entry.criteria[k].norm;
          const base = currentEntry?.criteria[k].norm;
          const delta = current || base === undefined ? 0 : Math.round(mine) - Math.round(base);
          return (
            <div className={`criterion-bar ${delta > 0 ? "better" : delta < 0 ? "worse" : ""}`} key={k}>
              <span>{label(k)}</span>
              <i aria-hidden="true">
                <b style={{ width: `${mine}%` }} />
                {!current && base !== undefined && <em style={{ left: `${base}%` }} />}
              </i>
              <strong>
                {Math.round(mine)}
                {delta !== 0 && <small className="sr-only">{delta > 0 ? t("card.better_than_current", "better than your current rotation") : t("card.worse_than_current", "worse than your current rotation")}</small>}
              </strong>
            </div>
          );
        })}
      </div>

      <CardSection title={t("card.why")}>
        {why.length
          ? <ul>{why.map((k) => <li key={k}><b>{label(k)}.</b> {cardLine(ui, "why", k, entry.criteria[k].vars)}</li>)}</ul>
          : <p className="section-empty">{current ? t("card.current_why", "This is your baseline. The other cards are compared against it.") : unavailable && !noWaterHere ? `${t("card.unavailable", "Not available with your current limits")}.${unlock ? ` ${unlock}` : ""}` : shownAt === "none" ? t("card.no_water_why", es ? "No se sugiere aquí: necesita riego que este campo no tiene." : "Not suggested here: it needs irrigation this field does not have.") : t("card.no_why", "No criterion stands out at these priorities.")}</p>}
      </CardSection>
      <section className="strategy-subsection">
        {entry.evidence.length ? (
          <details className="evidence-details">
            <summary><h4>{t("card.evidence")}</h4><span className="evidence-count">{entry.evidence.length}</span><ChevronDown size={15} aria-hidden="true" /></summary>
            {entry.evidence.map((item, index) => (
              <div className="text-evidence" key={`${item.text_id}-${index}`}>
                <p>{cardLine(ui, "evidence", item.text_id, item.vars)}</p>
                <SourceChips tags={item.sources} sources={ui.sources} />
              </div>
            ))}
          </details>
        ) : <><h4>{t("card.evidence")}</h4><p className="section-empty">{t("card.none", "Nothing listed.")}</p></>}
      </section>
      <CardSection title={t("card.benefits")}>
        {benefits.length
          ? <ul>{benefits.map((item, index) => <li key={`${item.text_id}-${index}`}>{cardLine(ui, "benefits", item.text_id, item.vars)}</li>)}</ul>
          : <p className="section-empty">{current ? t("card.current_benefits", "Benefits of the other rotations are measured against this one.") : t("card.none", "Nothing listed.")}</p>}
      </CardSection>
      <CardSection title={t("card.gaps")} tone="gap">
        {gaps.length || sharedGaps.length
          ? <ul>{gaps.map((gap) => <li key={gap}>{cardLine(ui, "gaps", gap)}</li>)}{sharedNote(sharedGaps.length)}</ul>
          : <p className="section-empty">{t("card.none", "Nothing listed.")}</p>}
      </CardSection>
      <CardSection title={t("card.risks")} tone="risk">
        <ul>
          {risks.map((risk) => <li key={risk}>{cardLine(ui, "risks", risk)}</li>)}
          {sharedNote(sharedRisks.length)}
          {entry.crops_without_local_market.length > 0 && (
            <li>{cardLine(ui, "infeasible", "no_local_market")} ({entry.crops_without_local_market.map((crop) => cropLabel(ui, crop)).join(", ")})</li>
          )}
        </ul>
      </CardSection>
    </article>
  );
}

function CardSection({ title, children, tone = "" }: { title: string; children: React.ReactNode; tone?: string }) {
  return <section className={`strategy-subsection ${tone}`}><h4>{title}</h4>{children}</section>;
}
