// Number check (README §9). A port of model/assistant/number_check.py; both pass
// model/assistant/number_check_cases.json (copied to tests/fixtures/).
// Refinements over the README text, agreed with M:
// - the comma-thousands branch must not end inside a digit run (2012 is one number);
// - U+2212 minus reads as "-"; a "-" right after a letter, digit or % is a hyphen, not a sign;
// - a 4-digit integer 1980-2035 is skipped only with no $ and no unit;
// - without an explicit minus, magnitudes are compared (a fall of 0.86 cm matches -0.86);
// - a unit may carry "/ac" (bu/ac, tons/ac); a bare "/ac" reads as usd.
import type { AskResponse, Fact } from "@/lib/types";

export type CheckedNumber = AskResponse["numbers"][number];

export interface FoundNumber {
  index: number;          // start offset in the answer
  text: string;           // matched text, number plus unit
  value: number;          // as written, with sign
  unit: string | null;    // canonical unit as written: mm, in, ft, cm, m, pct, usd, days, years, c, f, ac, bu, tons
  step: number;           // rounding step of the written number
  signed: boolean;        // written with an explicit minus
}

const NUMBER = String.raw`\$?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?(?!\d)|\$?-?\d+(?:\.\d+)?`;
const UNITS = String.raw`mm|inches|in|%|°C|°F|days?|years?|cm|ft|m|acres|ac|bu|tons?|\/ac`;
// The unit must not run into a following letter ("5 increase" is not "5 in").
// The lookbehind keeps digits inside identifiers (R2, cap300) out; the Python port gets the same
// effect because those never carry a unit and never match a fact by accident in the shared cases.
const PATTERN = new RegExp(String.raw`(?<![A-Za-z0-9_.$])(${NUMBER})(?:\s?((?:${UNITS})(?:\/ac)?)(?![A-Za-z]))?`, "g");
const TAG_SPAN = /\[[A-Za-z0-9_]+\]/g;
const FACT_ID_SPAN = /\([A-Za-z0-9_|:-]+(?:\.[A-Za-z0-9_|:-]+)+\)/g;

const MM_PER_IN = 25.4;
const M_PER_FT = 0.3048;

const CANON: Record<string, string> = {
  mm: "mm", mm_per_yr: "mm", mm_per_day: "mm",
  in: "in", inch: "in", inches: "in",
  ft: "ft", feet: "ft",
  cm: "cm", cm_per_yr: "cm",
  m: "m", m_per_yr: "m",
  "%": "pct", pct: "pct", percent: "pct",
  usd: "usd", usd_ac: "usd", $: "usd", "/ac": "usd", "usd/ac": "usd",
  day: "days", days: "days",
  year: "years", years: "years", yr: "years",
  "°c": "c", c: "c", degc: "c",
  "°f": "f", f: "f", degf: "f",
  ac: "ac", acre: "ac", acres: "ac", area_ac: "ac",
  bu: "bu", "bu/ac": "bu", bu_ac: "bu",
  ton: "tons", tons: "tons", "tons/ac": "tons", tons_ac: "tons",
};

function canonUnit(unit: string | null | undefined): string | null {
  if (unit == null) return null;
  const u = unit.trim().toLowerCase();
  return CANON[u] ?? u;
}

/** Value, unit and rounding-step scale in base units (in → mm, ft → m, °F → °C). */
function toBase(value: number, unit: string | null): [number, string | null, number] {
  if (unit === "in") return [value * MM_PER_IN, "mm", MM_PER_IN];
  if (unit === "ft") return [value * M_PER_FT, "m", M_PER_FT];
  if (unit === "f") return [((value - 32) * 5) / 9, "c", 5 / 9];
  return [value, unit, 1];
}

function decimals(raw: string): number {
  const match = /\.(\d+)$/.exec(raw);
  return match ? match[1].length : 0;
}

function skipSpans(text: string): [number, number][] {
  return [...text.matchAll(TAG_SPAN), ...text.matchAll(FACT_ID_SPAN)].map((m) => [m.index, m.index + m[0].length]);
}

/** Find every checkable number in an answer, in order. */
export function findNumbers(answer: string): FoundNumber[] {
  // Both replacements keep the string length, so offsets still point into the original answer.
  const text = answer.replace(/−/g, "-").replace(/(?<=[A-Za-z0-9%])-(?=\d)/g, " ");
  const spans = skipSpans(text);
  const found: FoundNumber[] = [];
  for (const match of text.matchAll(PATTERN)) {
    const start = match.index;
    const end = start + match[0].length;
    if (spans.some(([a, b]) => a <= start && start < b)) continue;
    const raw = match[1];
    const rawUnit = match[2] ?? null;
    const dollar = raw.startsWith("$");
    const digits = raw.replace(/^\$/, "");
    const signed = digits.startsWith("-");
    const abs = digits.replace(/^-/, "");

    // List marker: a number alone at the start of a line followed by "." or ")".
    const lineStart = text.lastIndexOf("\n", start - 1) + 1;
    if (!rawUnit && !dollar && text.slice(lineStart, start).trim() === "" && end < text.length && ".)".includes(text[end])) continue;

    const plain = abs.replace(/,/g, "");
    if (!dollar && !rawUnit && !abs.includes(",") && !abs.includes(".") && plain.length === 4) {
      const year = Number(plain);
      if (year >= 1980 && year <= 2035) continue;
    }

    found.push({
      index: start,
      text: text.slice(start, end).trim(),
      value: Number(plain) * (signed ? -1 : 1),
      unit: dollar ? "usd" : canonUnit(rawUnit),
      step: 10 ** -decimals(plain),
      signed,
    });
  }
  return found;
}

function compatible(a: string | null, b: string | null): boolean {
  return a === null || b === null || a === b;
}

/** README §9: verified when a fact with a compatible unit is within max(5 %, rounding step). First match wins. */
export function checkNumbers(answer: string, facts: Pick<Fact, "id" | "value" | "unit">[]): CheckedNumber[] {
  const prepared = facts.flatMap((fact) => {
    if (typeof fact.value !== "number") return [];   // text-only facts have nothing to match
    const [value, unit] = toBase(fact.value, canonUnit(fact.unit));
    return [{ id: fact.id, value, unit }];
  });
  return findNumbers(answer).map((found) => {
    const [value, unit, scale] = toBase(found.value, found.unit);
    const step = found.step * scale;
    const hit = prepared.find((fact) => {
      if (!compatible(unit, fact.unit)) return false;
      const [x, y] = found.signed ? [value, fact.value] : [Math.abs(value), Math.abs(fact.value)];
      return Math.abs(x - y) <= Math.max(0.05 * Math.abs(fact.value), step) + 1e-9;
    });
    return { text: found.text, value: found.value, unit: found.unit, verified: hit !== undefined, fact_id: hit?.id ?? null };
  });
}
