import type { CriterionId, StrategyEntry } from "@/lib/types";

export type Weights = Record<CriterionId, number>;
export interface Constraints {
  cap: "dryland" | "cap150" | "cap300" | "cap450";
  hay: boolean;
  cotton: boolean;
  forage: boolean;
}

export const criterionIds: CriterionId[] = ["water", "soil", "climate", "market", "operations"];
const capMillimeters: Record<Constraints["cap"], number> = {
  dryland: 0,
  cap150: 150,
  cap300: 300,
  cap450: 450,
};

export function weightsFromSliders(sliders: Weights): Weights {
  const sum = criterionIds.reduce((total, key) => total + Math.max(0, sliders[key]), 0);
  if (sum === 0) return { water: 20, soil: 20, climate: 20, market: 20, operations: 20 };
  return Object.fromEntries(criterionIds.map((key) => [key, Math.max(0, sliders[key]) * 100 / sum])) as Weights;
}

export function scoreEntry(entry: StrategyEntry, weights: Weights): number {
  return Math.round(criterionIds.reduce((score, key) => {
    const normalized = Math.min(100, Math.max(0, entry.criteria[key].norm * 10));
    return score + normalized * weights[key] / 100;
  }, 0));
}

export function excluded(
  entry: StrategyEntry,
  constraints: Constraints,
): null | "needs_more_water" | "needs_equipment" | "needs_forage_market" {
  if (entry.needs_irrigation_mm > capMillimeters[constraints.cap]) return "needs_more_water";
  if (entry.needs_equipment) {
    const equipmentAvailable = entry.equipment_required === "hay"
      ? constraints.hay
      : entry.equipment_required === "cotton"
        ? Boolean(constraints.cotton)
        : constraints.hay || constraints.cotton;
    if (!equipmentAvailable) return "needs_equipment";
  }
  if (entry.needs_forage_market && !constraints.forage) return "needs_forage_market";
  return null;
}

export function pickShown(
  entries: StrategyEntry[],
  weights: Weights,
  constraints: Constraints,
): { shown: StrategyEntry[]; hidden: { entry: StrategyEntry; reason: NonNullable<ReturnType<typeof excluded>> | "lower_rank" }[] } {
  const current = entries.find((entry) => entry.id === "R0");
  const eligible = entries.filter((entry) => entry.id !== "R0")
    .map((entry) => ({ entry, reason: excluded(entry, constraints) }))
    .sort((a, b) => scoreEntry(b.entry, weights) - scoreEntry(a.entry, weights));
  const shown = [current, ...eligible.filter(({ reason }) => !reason).slice(0, 3).map(({ entry }) => entry)]
    .filter((entry): entry is StrategyEntry => Boolean(entry));
  const hiddenEntries = eligible.filter(({ entry }) => !shown.includes(entry));
  return {
    shown,
    hidden: hiddenEntries.map(({ entry, reason }) => ({
      entry,
      reason: reason || "lower_rank",
    })),
  };
}

export function whyBullets(entry: StrategyEntry, weights: Weights): CriterionId[] {
  return criterionIds
    .map((id) => ({ id, impact: weights[id] * entry.criteria[id].norm }))
    .filter(({ id }) => entry.criteria[id].norm >= 5)
    .sort((a, b) => b.impact - a.impact)
    .slice(0, 3)
    .map(({ id }) => id);
}
