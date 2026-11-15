// Bundle of text helpers passed to workspace components.
import type { CardText, CropId, CropsFile, Lang, SourcesFile } from "@/lib/types";
import { fill, loc, type CropNames, type TFunction } from "@/lib/i18n";
import { preferred } from "@/lib/copyPreferred";

export interface UI {
  lang: Lang;
  t: TFunction;
  cardText: CardText;
  crops: CropNames;
  sources: SourcesFile;
  /** copy.json strings, for templates rendered inside components (copyLine). */
  copy?: Record<string, { en: string; es: string }>;
}

export function cropNames(crops: CropsFile | null): CropNames {
  if (!crops) return {};
  return Object.fromEntries(Object.entries(crops.crops).map(([id, traits]) => [id, traits.name]));
}

export function cropLabel(ui: Pick<UI, "crops" | "lang" | "t">, id: CropId | "bare" | "other"): string {
  if (id === "bare") return ui.t("calendar.bare", "Bare soil");
  if (id === "other") return ui.t("crop.other", "Other");
  return loc(ui.crops[id], ui.lang) || id;
}

/** Render a card_text section entry (why, benefits, evidence, ...) with its vars. */
export function cardLine(ui: UI, section: Exclude<keyof CardText, "_meta" | "rotations" | "criteria_labels">, id: string, vars: Record<string, number | string> = {}): string {
  const template = (ui.cardText[section] as Record<string, { en: string; es: string }>)[id];
  if (!template) {
    console.warn(`Missing card_text.${section}.${id}`);
    return id;
  }
  const better = preferred(`card_text.${section}.${id}`, template.en, ui.lang, vars);
  if (better && "text" in better) return better.text;
  if (better) return fill({ en: better.template, es: better.template }, vars, ui.lang, ui.crops);
  return fill(template, vars, ui.lang, ui.crops);
}

/** A copy.json template (with {vars}) through the same plain-language layer as cardLine. */
export function copyLine(copy: Record<string, { en: string; es: string }>, key: string, vars: Record<string, number | string>, lang: Lang, fallback: string): string {
  const template = copy[key] ?? { en: fallback, es: fallback };
  const better = preferred(`copy.${key}`, template.en, lang, vars);
  if (better && "text" in better) return better.text;
  if (better) return fill({ en: better.template, es: better.template }, vars, lang);
  return fill(template, vars, lang);
}

export const KIND_LABEL: Record<string, string> = {
  irrigated_pivot: "Irrigated pivot", dryland: "Dryland", sandy_wind: "Sandy, wind-erodible",
};
export const ROTATION_CLASS_LABEL: Record<string, string> = {
  continuous_corn: "Continuous corn", corn_wheat_sorghum: "Corn, wheat, sorghum", corn_soy: "Corn and soybean",
  wsf: "Wheat, sorghum, fallow", wheat_fallow: "Wheat and fallow", alfalfa: "Alfalfa", mixed: "Mixed",
};
