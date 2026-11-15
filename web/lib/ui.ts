// Bundle of text helpers passed to workspace components.
import type { CardText, CropId, CropsFile, Lang, SourcesFile } from "@/lib/types";
import { fill, loc, type CropNames, type TFunction } from "@/lib/i18n";

export interface UI {
  lang: Lang;
  t: TFunction;
  cardText: CardText;
  crops: CropNames;
  sources: SourcesFile;
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
  return fill(template, vars, ui.lang, ui.crops);
}
