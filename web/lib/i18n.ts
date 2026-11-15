// Text lookup and placeholder formatting (README §7.4, handover §6).
import type { CopyFile, CropId, Lang, Localized } from "@/lib/types";

export type CropNames = Partial<Record<CropId | string, Localized>>;
type Strings = CopyFile["strings"];

/** A localized string in the current language, falling back to English when Spanish is empty. */
export function loc(value: Localized | undefined, lang: Lang): string {
  if (!value) return "";
  return value[lang] || value.en;
}

/** copy.strings[key][lang] → en → fallback → key */
export function translate(strings: Strings, key: string, lang: Lang, fallback?: string): string {
  const entry = strings[key];
  return entry?.[lang] || entry?.en || fallback || key;
}

export type TFunction = (key: string, fallback?: string) => string;

/** Binds copy and language so components can call t("key", "Fallback"). */
export function makeT(strings: Strings, lang: Lang): TFunction {
  return (key, fallback) => translate(strings, key, lang, fallback);
}

const MINUS = "−";

function num(value: number, lang: Lang, maxDecimals: number, minDecimals = 0): string {
  const text = new Intl.NumberFormat(lang === "es" ? "es-ES" : "en-US", {
    maximumFractionDigits: maxDecimals,
    minimumFractionDigits: minDecimals,
    useGrouping: lang === "en",
  }).format(Math.abs(value));
  return value < 0 && text !== "0" && !/^0([.,]0+)?$/.test(text) ? `${MINUS}${text}` : text;
}

/** True when `name` is `suffix` itself or ends with `_suffix`. */
function hasSuffix(name: string, suffix: string): boolean {
  return name === suffix || name.endsWith(`_${suffix}`);
}

/** README §7.4: format a template variable by its name's suffix. */
export function formatVar(name: string, value: number | string, lang: Lang, crops?: CropNames): string {
  if (hasSuffix(name, "crop")) {
    const crop = crops?.[String(value)];
    return crop ? loc(crop, lang) : String(value);
  }
  if (typeof value === "string") return value;
  if (!Number.isFinite(value)) return "—";

  if (hasSuffix(name, "usd_ac")) {
    const amount = num(Math.round(Math.abs(value)), lang, 0);
    return `${value < 0 && Math.round(value) !== 0 ? MINUS : ""}$${amount}/ac`;
  }
  if (hasSuffix(name, "cm_per_yr")) return `${num(value, lang, 1, 1)} ${lang === "es" ? "cm/año" : "cm/yr"}`;
  if (hasSuffix(name, "m_per_yr")) {
    const feet = value / 0.3048;
    return lang === "es"
      ? `${num(value, lang, 1, 1)} m/año (${num(feet, lang, 1, 1)} pies/año)`
      : `${num(value, lang, 1, 1)} m/yr (${num(feet, lang, 1, 1)} ft/yr)`;
  }
  if (hasSuffix(name, "mm")) {
    const inches = num(value / 25.4, lang, 1, 1);
    return `${num(Math.round(value), lang, 0)} mm (${inches} ${lang === "es" ? "pulg." : "in"})`;
  }
  if (hasSuffix(name, "pct")) return `${num(value, lang, 1)}%`;
  if (name.endsWith("days")) return num(Math.round(value), lang, 0);
  if (name === "year" || name === "years_from" || name === "years_to") return String(Math.round(value));
  if (name === "n" || name.endsWith("_years")) return num(Math.round(value), lang, 0);
  if (name === "r") return num(value, lang, 2, 2);
  return num(value, lang, 1);
}

/** Replace {name} placeholders in a localized template via formatVar. Missing values render as an em-dash placeholder. */
export function fill(
  template: Localized | undefined,
  vars: Record<string, number | string>,
  lang: Lang,
  crops?: CropNames,
): string {
  const text = loc(template, lang);
  return text.replace(/\{([a-zA-Z0-9_]+)\}/g, (_match, name: string) => {
    if (!(name in vars)) {
      console.warn(`Missing template value: {${name}}`);
      return "—";
    }
    return formatVar(name, vars[name], lang, crops);
  });
}

/** Fill plain `{name}` placeholders with already-formatted strings (UI chrome only). */
export function interpolate(text: string, values: Record<string, string | number>): string {
  return text.replace(/\{([a-zA-Z0-9_]+)\}/g, (match, name: string) => (name in values ? String(values[name]) : match));
}
