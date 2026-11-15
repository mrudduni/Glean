import { describe, expect, it } from "vitest";
import { excluded, pickShown, scoreEntry, weightsFromSliders, whyBullets } from "../lib/score";
import type { CriterionId, StrategyEntry } from "../lib/types";

const criteria = {
  water: { norm: 8, vars: {} },
  soil: { norm: 7, vars: {} },
  climate: { norm: 6, vars: {} },
  market: { norm: 5, vars: {} },
  operations: { norm: 4, vars: {} },
};

function entry(id: string, irrigation: number, overrides: Partial<StrategyEntry> = {}): StrategyEntry {
  return {
    id,
    scenario: "cap300|actual",
    criteria,
    flags: [],
    needs_irrigation_mm: irrigation,
    needs_equipment: false,
    needs_forage_market: false,
    crops_without_local_market: [],
    confidence: "medium",
    evidence: [],
    benefits: [],
    gaps: [],
    risks: [],
    ...overrides,
  };
}

describe("rotation scoring", () => {
  it("normalizes slider weights and uses the selected criteria", () => {
    const weights = weightsFromSliders({ water: 5, soil: 3, climate: 1, market: 1, operations: 0 });
    expect(Object.values(weights).reduce((sum, value) => sum + value, 0)).toBeCloseTo(100);
    expect(scoreEntry(entry("R1", 100), weights)).toBeGreaterThan(0);
    expect(scoreEntry(entry("R1", 100), weights)).toBeLessThanOrEqual(100);
  });

  it("keeps R0 visible and shows the three highest-ranked feasible alternatives", () => {
    const entries = [
      entry("R0", 400),
      entry("R1", 150),
      entry("R2", 150),
      entry("R3", 150),
      entry("R4", 150),
      entry("R5", 450),
    ];
    const result = pickShown(entries, weightsFromSliders({ water: 5, soil: 4, climate: 3, market: 2, operations: 1 }), {
      cap: "cap300", hay: false, cotton: false, forage: false,
    });
    expect(result.shown).toHaveLength(4);
    expect(result.shown[0].id).toBe("R0");
    expect(result.hidden.find(({ entry: item }) => item.id === "R5")?.reason).toBe("needs_more_water");
    expect(result.hidden.every(({ entry: item }) => item.id !== "R0")).toBe(true);
  });

  it("excludes forage only when the forage market constraint is unmet", () => {
    const forage = entry("R4", 100, { needs_forage_market: true });
    expect(excluded(forage, { cap: "cap300", hay: true, cotton: false, forage: false })).toBe("needs_forage_market");
    expect(excluded(forage, { cap: "cap300", hay: true, cotton: false, forage: true })).toBeNull();
  });

  it("does not exclude crops with missing market evidence", () => {
    const uncertainMarket = entry("R2", 100, { crops_without_local_market: ["sorghum"] });
    expect(excluded(uncertainMarket, { cap: "cap300", hay: false, cotton: false, forage: false })).toBeNull();
  });

  it("returns at most three weighted explanation criteria above the halfway norm", () => {
    const weights = weightsFromSliders({ water: 5, soil: 4, climate: 3, market: 2, operations: 1 });
    const ids = whyBullets(entry("R1", 100), weights);
    expect(ids).toHaveLength(3);
    expect(ids.every((id: CriterionId) => criteria[id].norm >= 5)).toBe(true);
  });
});
