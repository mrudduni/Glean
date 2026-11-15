import { describe, expect, it } from "vitest";
import { DEFAULT_SLIDERS, excluded, pickShown, scoreEntry, weightsFromSliders, whyBullets, type Constraints, sameRotation, benefitsShown } from "@/lib/score";
import { CRITERION_IDS } from "@/lib/schemas";
import type { CriterionId, RotationId, StrategyEntry } from "@/lib/types";

function entry(id: RotationId, norm: Partial<Record<CriterionId, number>> = {}, patch: Partial<StrategyEntry> = {}): StrategyEntry {
  const criteria = Object.fromEntries(CRITERION_IDS.map((k) => [k, { raw: k === "water_use" ? 100 : 0, unit: "mm", norm: norm[k] ?? 50, vars: {} }])) as StrategyEntry["criteria"];
  return {
    rotation_id: id, feasible: true, infeasible_reason_id: null, criteria,
    requires_equipment: [], needs_forage_market: false, crops_without_local_market: [],
    benefits: [], evidence: [], gap_ids: [], risk_ids: [], confidence: "good", ...patch,
  };
}
const none: Constraints = { cap: "cap300", hay: false, cotton: false, forage: false };

describe("weightsFromSliders", () => {
  it("splits each slider across its criteria per README 8.7", () => {
    const w = weightsFromSliders({ save_water: 1, income: 2, steady_income: 10, soil_health: 10, erosion: 10 });
    expect(w.water_use).toBe(1);
    expect(w.income_mean).toBe(2);
    expect(w.income_worst).toBeCloseTo(7);
    expect(w.heat_frost_risk).toBeCloseTo(3);
    expect(w.soil_health).toBeCloseTo(7);
    expect(w.pest_break).toBeCloseTo(3);
    expect(w.wind_erosion).toBeCloseTo(6);
    expect(w.water_erosion).toBeCloseTo(4);
  });
  it("covers all 8 criteria with the 5 default sliders", () => {
    const w = weightsFromSliders(DEFAULT_SLIDERS);
    expect(Object.keys(w).sort()).toEqual([...CRITERION_IDS].sort());
    expect(Object.values(w).reduce((a, b) => a + b, 0)).toBeCloseTo(15);
  });
});

describe("scoreEntry", () => {
  it("is the weighted mean of norms", () => {
    const w = weightsFromSliders({ save_water: 5, income: 0, steady_income: 0, soil_health: 0, erosion: 0 });
    expect(scoreEntry(entry("R1", { water_use: 80, income_mean: 10 }), w)).toBe(80);
  });
  it("uses equal weights when every slider is 0", () => {
    const w = weightsFromSliders({ save_water: 0, income: 0, steady_income: 0, soil_health: 0, erosion: 0 });
    const e = entry("R1", { water_use: 100, income_mean: 100, income_worst: 100, soil_health: 100, water_erosion: 0, wind_erosion: 0, pest_break: 0, heat_frost_risk: 0 });
    expect(scoreEntry(e, w)).toBe(50);
  });
});

describe("excluded", () => {
  it("flags infeasible, missing equipment and forage market", () => {
    expect(excluded(entry("R4", {}, { feasible: false, infeasible_reason_id: "needs_more_water" }), none)).toBe("needs_more_water");
    expect(excluded(entry("R4", {}, { requires_equipment: ["hay"] }), none)).toBe("needs_equipment");
    expect(excluded(entry("R4", {}, { requires_equipment: ["hay"] }), { ...none, hay: true })).toBeNull();
    expect(excluded(entry("R3", {}, { needs_forage_market: true }), none)).toBe("no_local_market");
    expect(excluded(entry("R3", {}, { needs_forage_market: true }), { ...none, forage: true })).toBeNull();
  });
  it("only flags crops without a local market, never excludes for it", () => {
    expect(excluded(entry("R6", {}, { crops_without_local_market: ["cotton"] }), none)).toBeNull();
  });
});

describe("pickShown", () => {
  const w = weightsFromSliders(DEFAULT_SLIDERS);
  it("always shows R0 first, then the top 3 non-excluded", () => {
    const entries = [
      entry("R0", { water_use: 0 }, { feasible: false }),
      entry("R1", { water_use: 90 }), entry("R2", { water_use: 80 }), entry("R3", { water_use: 70 }),
      entry("R4", { water_use: 100 }, { feasible: false }), entry("R5", { water_use: 10 }),
    ];
    const picked = pickShown(entries, w, none);
    expect(picked.shown.map((e) => e.rotation_id)).toEqual(["R0", "R1", "R2", "R3"]);
    expect(picked.hidden.map((h) => [h.entry.rotation_id, h.reason])).toEqual([["R4", "needs_more_water"]]);
    expect(picked.others.map((e) => e.rotation_id)).toEqual(["R5"]);
  });
  it("breaks ties by lower irrigation_mm_mean", () => {
    const entries = [entry("R0"), entry("R1"), entry("R2"), entry("R3"), entry("R5")];
    const picked = pickShown(entries, w, none, { R1: 300, R2: 100, R3: 200, R5: 400 });
    expect(picked.shown.map((e) => e.rotation_id)).toEqual(["R0", "R2", "R3", "R1"]);
  });
});

describe("whyBullets", () => {
  it("returns up to 3 criteria by w*norm among norm >= 50", () => {
    const w = weightsFromSliders({ save_water: 5, income: 1, steady_income: 0, soil_health: 3, erosion: 0 });
    const e = entry("R2", { water_use: 90, income_mean: 95, soil_health: 60, pest_break: 100, income_worst: 100, water_erosion: 40, wind_erosion: 49, heat_frost_risk: 10 });
    expect(whyBullets(e, w)).toEqual(["water_use", "soil_health", "income_mean"]);
  });
  it("skips criteria below 50", () => {
    const w = weightsFromSliders(DEFAULT_SLIDERS);
    expect(whyBullets(entry("R2", Object.fromEntries(CRITERION_IDS.map((k) => [k, 49]))), w)).toEqual([]);
  });
});

describe("sameRotation", () => {
  const s = (...crops: string[]) => crops.map((crop) => ({ crop, cover_after: null }));
  it("matches equal and shifted cycles only", () => {
    expect(sameRotation(s("wheat", "sorghum", "fallow"), s("wheat", "sorghum", "fallow"))).toBe(true);
    expect(sameRotation(s("wheat", "sorghum", "fallow"), s("sorghum", "fallow", "wheat"))).toBe(true);
    expect(sameRotation(s("wheat", "sorghum", "fallow"), s("wheat", "fallow", "sorghum"))).toBe(false);
    expect(sameRotation(s("corn"), s("corn", "corn"))).toBe(false);
  });
});

describe("pickShown fills the row to R0 + 3", () => {
  const w = weightsFromSliders(DEFAULT_SLIDERS);
  it("adds the best-scoring excluded rotations with their reason when fewer than 3 fit", () => {
    const entries = [
      entry("R0"), entry("R1", { water_use: 90 }),
      entry("R2", { water_use: 20 }, { feasible: false }), entry("R3", { water_use: 80 }, { feasible: false }),
      entry("R4", { water_use: 10 }, { feasible: false }),
    ];
    const picked = pickShown(entries, w, none);
    expect(picked.shown.map((e) => e.rotation_id)).toEqual(["R0", "R1", "R3", "R2"]);
    expect(picked.filled).toEqual({ R3: "needs_more_water", R2: "needs_more_water" });
    expect(picked.hidden.map((h) => h.entry.rotation_id)).toEqual(["R4"]);
  });
  it("does not count or fill with duplicates of R0", () => {
    const entries = [entry("R0"), entry("R1"), entry("R2", {}, { feasible: false })];
    const picked = pickShown(entries, w, none, undefined, new Set(["R1"] as RotationId[]));
    expect(picked.shown.map((e) => e.rotation_id)).toEqual(["R0", "R2"]);
    expect(picked.filled).toEqual({ R2: "needs_more_water" });
  });
});

describe("water guards", () => {
  const w = weightsFromSliders({ save_water: 5, income: 0, steady_income: 0, soil_health: 0, erosion: 0 });
  it("skips the water_use why bullet when saved_mm is negative", () => {
    const more = entry("R1", { water_use: 90, income_mean: 80 });
    more.criteria.water_use.vars = { irrigation_mm: 400, saved_mm: -50 };
    expect(whyBullets(more, w)).not.toContain("water_use");
    more.criteria.water_use.vars = { irrigation_mm: 200, saved_mm: 50 };
    expect(whyBullets(more, w)).toContain("water_use");
  });
  it("drops benefits.water_saved when saved_mm is negative", () => {
    const e = entry("R1", {}, { benefits: [{ text_id: "water_saved", vars: { saved_mm: -20 } }, { text_id: "legume_added", vars: { legume_years: 1, cycle_years: 3 } }] });
    expect(benefitsShown(e).map((b) => b.text_id)).toEqual(["legume_added"]);
  });
});
