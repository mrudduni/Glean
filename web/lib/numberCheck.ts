// Number check (README §9). Must stay identical in behaviour to model/assistant/number_check.py.
import type { AskResponse, Fact } from "@/lib/types";

export type CheckedNumber = AskResponse["numbers"][number];

export interface FoundNumber {
  index: number;          // start offset in the answer
  text: string;           // matched text, number plus unit
  value: number;          // converted to metric (in → mm, °F → °C, ft → m)
  step: number;           // rounding step of the written number, in the converted unit
  unit: string | null;    // canonical unit: mm, pct, c, days, years, cm, m, ac, bu, tons, usd, per_ac
}

const NUMBER = String.raw`\$?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\$?-?\d+(?:\.\d+)?`;
// Longest alternatives first so "mm" wins over "m" and "inches" over "in".
const UNIT = String.raw`inches|acres|years?|days?|tons?|mm|in|°C|°F|cm|ft|ac|bu|\/ac|%|m`;
// (?!\d) forces the alternation to take the whole digit run ("2016", not "201" + "6").
const PATTERN = new RegExp(String.raw`(?<![\w.$])(${NUMBER})(?!\d)(?:\s?(${UNIT})(?![A-Za-z]))?`, "g");

const UNIT_CANON: Record<string, string> = {
  mm: "mm", in: "mm", inches: "mm",
  "%": "pct",
  "°C": "c", "°F": "c",
  day: "days", days: "days",
  year: "years", years: "years",
  cm: "cm", m: "m", ft: "m",
  ac: "ac", acres: "ac",
  bu: "bu", ton: "tons", tons: "tons",
  "/ac": "per_ac",
};

/** Spans to ignore: [TAG] source tags and (fact_id) references. */
function ignoredSpans(text: string): [number, number][] {
  const spans: [number, number][] = [];
  for (const match of text.matchAll(/\[[^\]\n]*\]/g)) spans.push([match.index, match.index + match[0].length]);
  for (const match of text.matchAll(/\(([^()\s]+)\)/g)) {
    const inner = match[1];
    if (/[A-Za-z]/.test(inner) && /[._|]/.test(inner)) spans.push([match.index, match.index + match[0].length]);
  }
  return spans;
}

function decimals(raw: string): number {
  const dot = raw.indexOf(".");
  return dot === -1 ? 0 : raw.length - dot - 1;
}

/** Find every checkable number in an answer, in order. */
export function findNumbers(answer: string): FoundNumber[] {
  const text = answer.replace(/−/g, "-");
  const skip = ignoredSpans(text);
  const found: FoundNumber[] = [];
  for (const match of text.matchAll(PATTERN)) {
    const start = match.index;
    if (skip.some(([from, to]) => start >= from && start < to)) continue;
    const rawNumber = match[1];
    const rawUnit = match[2] ?? null;
    const dollar = rawNumber.startsWith("$");
    const digits = rawNumber.replace(/[$,]/g, "");
    let value = Number(digits);
    if (!Number.isFinite(value)) continue;

    // Years: plain 4-digit integers 1980–2035.
    if (!dollar && /^\d{4}$/.test(digits) && value >= 1980 && value <= 2035) continue;
    // List markers at the start of a line: "1." or "1)".
    const lineStart = text.lastIndexOf("\n", start - 1) + 1;
    const after = text.slice(start + rawNumber.length, start + rawNumber.length + 2);
    if (!rawUnit && /^\s*$/.test(text.slice(lineStart, start)) && /^[.)](\s|$)/.test(after)) continue;

    let step = 10 ** -decimals(digits);
    let unit: string | null = dollar ? "usd" : rawUnit ? UNIT_CANON[rawUnit] ?? null : null;
    if (dollar && rawUnit === "/ac") unit = "usd";
    if (rawUnit === "in" || rawUnit === "inches") { value *= 25.4; step *= 25.4; }
    if (rawUnit === "°F") { value = (value - 32) * 5 / 9; step *= 5 / 9; }
    if (rawUnit === "ft") { value *= 0.3048; step *= 0.3048; }

    found.push({ index: start, text: match[0], value, step, unit });
  }
  return found;
}

/** Canonical family of a fact unit ("usd_ac" → "usd", "cm_per_yr" → "cm", "%" → "pct"). */
function factFamily(unit: string): string {
  const u = unit.toLowerCase();
  if (u === "%" || u.startsWith("pct")) return "pct";
  if (u.startsWith("usd") || u === "$") return "usd";
  if (u.startsWith("day")) return "days";
  if (u.startsWith("year") || u === "yr") return "years";
  if (u === "c" || u === "°c" || u.startsWith("deg")) return "c";
  if (u.startsWith("ton")) return "tons";
  return u.split("_")[0];
}

function compatible(numberUnit: string | null, factUnit: string | null): boolean {
  if (numberUnit === null || factUnit === null) return true;
  if (numberUnit === "per_ac") return factUnit.toLowerCase().endsWith("_ac");
  return numberUnit === factFamily(factUnit);
}

/** README §9 number check: verified when some fact is within max(5 %, rounding step) with a compatible unit. */
export function checkNumbers(answer: string, facts: Fact[]): CheckedNumber[] {
  return findNumbers(answer).map((found) => {
    let best: { fact: Fact; diff: number } | null = null;
    for (const fact of facts) {
      if (!compatible(found.unit, fact.unit)) continue;
      const diff = Math.abs(found.value - fact.value);
      const tolerance = Math.max(0.05 * Math.abs(fact.value), found.step) + 1e-9;
      if (diff <= tolerance && (!best || diff < best.diff)) best = { fact, diff };
    }
    return {
      text: found.text,
      value: Number(found.value.toFixed(4)),
      unit: found.unit,
      verified: best !== null,
      fact_id: best?.fact.id ?? null,
    };
  });
}
