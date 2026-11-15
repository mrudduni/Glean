// Browser-side scoring (README §8.7, handover §5.4). Pure functions.
import type { CapId, CriterionId, EquipmentId, RotationId, StrategyEntry } from "@/lib/types";
import { CRITERION_IDS } from "@/lib/schemas";

export const SLIDER_IDS = ["save_water", "income", "steady_income", "soil_health", "erosion"] as const;
export type SliderId = (typeof SLIDER_IDS)[number];
export type Sliders = Record<SliderId, number>;          // 0–5 each
export type Weights = Record<CriterionId, number>;

/** Slider → criteria shares (README §8.7 table). */
export const SLIDER_SHARES: Record<SliderId, Partial<Record<CriterionId, number>>> = {
  save_water: { water_use: 1.0 },
  income: { income_mean: 1.0 },
  steady_income: { income_worst: 0.7, heat_frost_risk: 0.3 },
  soil_health: { soil_health: 0.7, pest_break: 0.3 },
  erosion: { wind_erosion: 0.6, water_erosion: 0.4 },
};

export const DEFAULT_SLIDERS: Sliders = { save_water: 3, income: 3, steady_income: 3, soil_health: 3, erosion: 3 };

export interface Constraints {
  cap: CapId;
  hay: boolean;
  cotton: boolean;
  forage: boolean;
}

export type ExclusionReason = "needs_more_water" | "needs_equipment" | "no_local_market";

function zeroWeights(): Weights {
  return Object.fromEntries(CRITERION_IDS.map((id) => [id, 0])) as Weights;
}

/** w_k = Σ over sliders (slider_value × share_k) */
export function weightsFromSliders(sliders: Sliders): Weights {
  const weights = zeroWeights();
  for (const slider of Object.keys(SLIDER_SHARES) as SliderId[]) {
    const value = sliders[slider] ?? 0;
    for (const [criterion, share] of Object.entries(SLIDER_SHARES[slider]) as [CriterionId, number][]) {
      weights[criterion] += value * share;
    }
  }
  return weights;
}

/** Equal weights when every slider is at 0. */
function effective(weights: Weights): Weights {
  const total = CRITERION_IDS.reduce((sum, id) => sum + weights[id], 0);
  if (total > 0) return weights;
  return Object.fromEntries(CRITERION_IDS.map((id) => [id, 1])) as Weights;
}

function rawScore(entry: StrategyEntry, weights: Weights): number {
  const w = effective(weights);
  const total = CRITERION_IDS.reduce((sum, id) => sum + w[id], 0);
  const weighted = CRITERION_IDS.reduce((sum, id) => sum + w[id] * entry.criteria[id].norm, 0);
  return weighted / total;
}

/** score(r) = Σ_k w_k × norm_k(r) / Σ_k w_k, rounded to an integer 0–100. */
export function scoreEntry(entry: StrategyEntry, weights: Weights): number {
  return Math.round(Math.max(0, Math.min(100, rawScore(entry, weights))));
}

/** excluded = !feasible OR requires_equipment ⊄ owned OR (needs_forage_market AND !forage_buyer) */
export function excluded(entry: StrategyEntry, constraints: Constraints): ExclusionReason | null {
  if (!entry.feasible) {
    const reason = entry.infeasible_reason_id;
    return reason === "needs_equipment" || reason === "no_local_market" ? reason : "needs_more_water";
  }
  const owned: Record<EquipmentId, boolean> = { hay: constraints.hay, cotton: constraints.cotton };
  if (entry.requires_equipment.some((item) => !owned[item])) return "needs_equipment";
  if (entry.needs_forage_market && !constraints.forage) return "no_local_market";
  return null;
}

export interface Ranked {
  entry: StrategyEntry;
  score: number;
}
export interface Picked {
  shown: StrategyEntry[];                                         // R0 first, then up to 3 by score
  hidden: { entry: StrategyEntry; reason: ExclusionReason }[];    // excluded rotations
  others: StrategyEntry[];                                        // feasible but outside the top 3
  /** Excluded rotations moved into `shown` so the row always has R0 + 3; each card shows its reason. */
  filled: Partial<Record<RotationId, ExclusionReason>>;
}

const SHOWN_ALTERNATIVES = 3;

/** saved_mm < 0 means the rotation uses more water than R0, so "saved" text would read wrong. */
function usesMoreWater(vars: Record<string, number | string> | undefined): boolean {
  const saved = vars?.saved_mm;
  return typeof saved === "number" && saved < 0;
}

/** Benefits to render: drops water_saved when the rotation does not save water. */
export function benefitsShown(entry: StrategyEntry): StrategyEntry["benefits"] {
  return entry.benefits.filter((item) => !(item.text_id === "water_saved" && usesMoreWater(item.vars)));
}

/**
 * shown = R0 always + top 3 non-excluded rotations by score (ties → lower irrigation_mm_mean).
 * `irrigation` comes from replay summaries; without it, criteria.water_use.raw is the tie-breaker.
 */
type Step = { crop: string; cover_after: string | null };

/** Same rotation, allowing a different starting year (wheat→sorghum→fallow equals sorghum→fallow→wheat). */
export function sameRotation(a: readonly Step[], b: readonly Step[]): boolean {
  if (a.length !== b.length || !a.length) return false;
  const key = (steps: readonly Step[]) => steps.map((step) => `${step.crop}+${step.cover_after ?? ""}`);
  const left = key(a);
  const right = key(b);
  return left.some((_, shift) => left.every((_, i) => left[(i + shift) % left.length] === right[i]));
}

/** duplicates: alternatives whose steps equal the current rotation; they are dropped, not listed as hidden. */
export function pickShown(
  entries: StrategyEntry[],
  weights: Weights,
  constraints: Constraints,
  irrigation?: Partial<Record<RotationId, number>>,
  duplicates?: ReadonlySet<RotationId>,
): Picked {
  const water = (entry: StrategyEntry) => irrigation?.[entry.rotation_id] ?? entry.criteria.water_use.raw;
  const current = entries.find((entry) => entry.rotation_id === "R0");
  const hidden: Picked["hidden"] = [];
  const candidates: { entry: StrategyEntry; score: number }[] = [];
  for (const entry of entries) {
    if (entry.rotation_id === "R0" || duplicates?.has(entry.rotation_id)) continue;
    const reason = excluded(entry, constraints);
    if (reason) hidden.push({ entry, reason });
    else candidates.push({ entry, score: rawScore(entry, weights) });
  }
  candidates.sort((a, b) => {
    const diff = Math.round(b.score) - Math.round(a.score);
    return diff !== 0 ? diff : water(a.entry) - water(b.entry);
  });
  const top = candidates.slice(0, SHOWN_ALTERNATIVES).map((item) => item.entry);
  // Fewer than 3 fit: fill the row with the best-scoring excluded rotations, flagged with their reason.
  const filled: Picked["filled"] = {};
  const fillers = hidden
    .map((item) => ({ ...item, score: rawScore(item.entry, weights) }))
    .sort((a, b) => Math.round(b.score) - Math.round(a.score) || water(a.entry) - water(b.entry))
    .slice(0, Math.max(0, SHOWN_ALTERNATIVES - top.length));
  for (const item of fillers) filled[item.entry.rotation_id] = item.reason;
  return {
    shown: [...(current ? [current] : []), ...top, ...fillers.map((item) => item.entry)],
    hidden: hidden.filter((item) => !(item.entry.rotation_id in filled)),
    others: candidates.slice(SHOWN_ALTERNATIVES).map((item) => item.entry),
    filled,
  };
}

/** The 3 criteria with the highest w_k × norm_k where norm_k ≥ 50. */
export function whyBullets(entry: StrategyEntry, weights: Weights): CriterionId[] {
  const w = effective(weights);
  return CRITERION_IDS
    .filter((id) => entry.criteria[id].norm >= 50 && w[id] > 0)
    .filter((id) => !(id === "water_use" && usesMoreWater(entry.criteria[id].vars)))
    .sort((a, b) => w[b] * entry.criteria[b].norm - w[a] * entry.criteria[a].norm)
    .slice(0, 3);
}
