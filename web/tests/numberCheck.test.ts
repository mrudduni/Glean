import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { checkNumbers, findNumbers } from "@/lib/numberCheck";
import type { Fact } from "@/lib/types";

const facts: Fact[] = [
  { id: "replay.R2.cap300|actual.irrigation_mm_mean", text: "R2 needs 126 mm.", value: 126, unit: "mm", source: "MODEL" },
  { id: "replay.R2.cap300|actual.revenue_usd_ac_mean", text: "R2 earns $253/ac.", value: 253, unit: "usd_ac", source: "MODEL" },
  { id: "water.grace_trend_cm_per_yr", text: "GRACE trend -0.86 cm/yr.", value: -0.86, unit: "cm_per_yr", source: "GRACE" },
  { id: "climate.recent.days_tmax_ge_35", text: "42 hot days.", value: 42, unit: "days", source: "POWER" },
  { id: "validation.bias_pct", text: "Bias 8%.", value: 8, unit: "pct", source: "OpenET" },
  { id: "field.area_ac", text: "128 acres.", value: 128.4, unit: "ac", source: "CSB" },
  { id: "field.unitless", text: "r is 0.62.", value: 0.62, unit: null, source: "MODEL" },
];
const texts = (answer: string) => findNumbers(answer).map((n) => n.text);
const verdicts = (answer: string) => checkNumbers(answer, facts).map((n) => [n.text, n.verified, n.fact_id]);

describe("findNumbers (README 9 steps 1-2)", () => {
  it("matches numbers with optional units and a leading $", () => {
    expect(texts("About 126 mm and $253/ac, 8% and 1,200 acres.")).toEqual(["126 mm", "$253/ac", "8%", "1,200 acres"]);
  });
  it("skips years 1980-2035 but not other 4-digit numbers", () => {
    expect(texts("In 2012 and from 2016 to 2025 it used 1500 mm, unlike 1975.")).toEqual(["1500 mm", "1975"]);
  });
  it("skips list markers at the start of a line", () => {
    expect(texts("1. Uses 126 mm\n  2) Then 42 days")).toEqual(["126 mm", "42 days"]);
  });
  it("skips numbers inside [TAG] and (fact_id)", () => {
    expect(texts("126 mm [MODEL] (replay.R2.cap300|actual.irrigation_mm_mean) and 42 days [POWER]")).toEqual(["126 mm", "42 days"]);
  });
  it("does not split identifiers like R2 or cap300", () => {
    expect(texts("R2 under cap300 saves 12 mm")).toEqual(["12 mm"]);
  });
  it("keeps conversions in parentheses", () => {
    expect(texts("126 mm (5.0 in)")).toEqual(["126 mm", "5.0 in"]);
  });
  it("reads a unicode minus as negative", () => {
    expect(findNumbers("−0.86 cm")[0].value).toBeCloseTo(-0.86);
  });
});

describe("checkNumbers (README 9 steps 3-4)", () => {
  it("verifies within 5% with a compatible unit and records the fact id", () => {
    expect(verdicts("R2 needs 130 mm and earns $253/ac.")).toEqual([
      ["130 mm", true, "replay.R2.cap300|actual.irrigation_mm_mean"],
      ["$253/ac", true, "replay.R2.cap300|actual.revenue_usd_ac_mean"],
    ]);
  });
  it("rejects numbers more than 5% away", () => {
    expect(verdicts("R2 needs 140 mm.")).toEqual([["140 mm", false, null]]);
  });
  it("rejects an incompatible unit", () => {
    expect(verdicts("It takes 126 days.")).toEqual([["126 days", false, null]]);
  });
  it("converts inches to mm before comparing", () => {
    expect(verdicts("About 5 in of water.")).toEqual([["5 in", true, "replay.R2.cap300|actual.irrigation_mm_mean"]]);
  });
  it("uses the rounding step of the written number", () => {
    expect(verdicts("Storage falls -0.9 cm a year.")).toEqual([["-0.9 cm", true, "water.grace_trend_cm_per_yr"]]);
    expect(verdicts("About 128 ac.")).toEqual([["128 ac", true, "field.area_ac"]]);
  });
  it("treats a missing unit as compatible", () => {
    expect(verdicts("r = 0.62")).toEqual([["0.62", true, "field.unitless"]]);
    expect(verdicts("about 42 of them")).toEqual([["42", true, "climate.recent.days_tmax_ge_35"]]);
  });
  it("converts degrees F to C", () => {
    const f: Fact[] = [{ id: "t", text: "35 °C", value: 35, unit: "c", source: "POWER" }];
    expect(checkNumbers("95 °F", f)[0].verified).toBe(true);
  });
});

// Shared cases with model/assistant/number_check.py (README 9: both implementations must agree).
interface SharedCase {
  name?: string; id?: string; answer?: string; text?: string; facts: Fact[];
  expected: { text: string; value: number; unit: string | null; verified: boolean; fact_id: string | null }[];
}
const sharedPaths = [
  resolve(__dirname, "../../model/assistant/number_check_cases.json"),
  resolve(__dirname, "fixtures/number_check_cases.json"),
];
const sharedPath = sharedPaths.find((path) => existsSync(path));
const raw = sharedPath ? (JSON.parse(readFileSync(sharedPath, "utf8")) as { cases?: SharedCase[] } | SharedCase[]) : null;
const shared: SharedCase[] = raw ? (Array.isArray(raw) ? raw : raw.cases ?? []) : [];

describe.skipIf(!shared.length)(`shared number check cases (${sharedPath ?? "none found"})`, () => {
  it.each(shared.map((c, i) => [c.name ?? c.id ?? `case ${i + 1}`, c] as const))("%s", (_name, c) => {
    const got = checkNumbers(c.answer ?? c.text ?? "", c.facts);
    expect(got.map(({ text, value, unit, verified, fact_id }) => ({ text, value, unit, verified, fact_id }))).toEqual(c.expected);
  });
});

describe("text-only facts", () => {
  it("never verifies a number against a fact with a null value", () => {
    const got = checkNumbers("It is 0 mm.", [{ id: "field.irrigation", value: null, unit: null }]);
    expect(got[0].verified).toBe(false);
  });
});
