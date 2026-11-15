import type { Lang, Localized } from "@/lib/types";

export function t(
  key: string,
  copy: Record<string, Localized>,
  lang: Lang,
  fallback?: string,
): string {
  const entry = copy[key];
  return entry?.[lang] || entry?.en || fallback || key;
}

export function formatVar(name: string, value: number | string, lang: Lang): string {
  if (typeof value !== "number") return value;
  const locale = lang === "es" ? "es-US" : "en-US";
  if (name.endsWith("_mm")) {
    const inches = (value / 25.4).toFixed(1);
    return `${new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(value)} mm (${inches} ${lang === "es" ? "pulg." : "in"})`;
  }
  if (name.endsWith("_usd_ac")) return `$${Math.round(value).toLocaleString(locale)}/ac`;
  if (name.endsWith("_pct")) return `${Math.round(value)}%`;
  if (name.endsWith("_days")) return `${Math.round(value)} ${lang === "es" ? "días" : "days"}`;
  if (name.endsWith("_ac")) return `${Math.round(value).toLocaleString(locale)} ac`;
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(value);
}

export function fill(template: Localized | undefined, vars: Record<string, number | string>, lang: Lang): string {
  const text = template?.[lang] || template?.en || "";
  return text.replace(/\{([a-zA-Z0-9_]+)\}/g, (_match, name: string) => {
    if (!(name in vars)) {
      console.warn(`Missing template value: ${name}`);
      return "—";
    }
    return formatVar(name, vars[name], lang);
  });
}
