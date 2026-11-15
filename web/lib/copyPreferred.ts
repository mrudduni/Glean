// Plain-language versions of a few content templates that read like form fields ("change in days: -3",
// "in years: 1"). Each entry applies ONLY while content still has the exact old English text (`was`),
// so the moment the content owner edits a string, their version wins. The same proposals are written
// up for them in HANDOFF_OTHER_OWNERS.md.
import type { Lang } from "@/lib/types";

type Vars = Record<string, number | string>;
type Line = string | ((vars: Vars) => string);
interface Preferred { was: string; en: Line; es: Line }

const n = (v: number | string | undefined) => Math.abs(Math.round(Number(v ?? 0)));
const days = (k: number, lang: Lang) => (lang === "es" ? (k === 1 ? "día" : "días") : (k === 1 ? "day" : "days"));

export const PREFERRED: Record<string, Preferred> = {
  "card_text.headline.heat_days_change": {
    was: "Hot days (35 °C or higher) a year, recent years versus 1991 to 2020, change in days: {days}.",
    en: (v) => { const d = Number(v.days); const k = n(d); return d === 0 ? "Recent years have had about as many days at 35 °C or hotter as 1991 to 2020." : `Recent years have had ${k} ${d < 0 ? "fewer" : "more"} ${days(k, "en")} at 35 °C or hotter each year than 1991 to 2020.`; },
    es: (v) => { const d = Number(v.days); const k = n(d); return d === 0 ? "En los años recientes hubo tantos días a 35 °C o más como en 1991 a 2020." : `En los años recientes hubo ${k} ${days(k, "es")} ${d < 0 ? "menos" : "más"} a 35 °C o más cada año que en 1991 a 2020.`; },
  },
  "card_text.headline.frost_free_change": {
    was: "Frost-free season, recent years versus 1991 to 2020, change in days: {days}.",
    en: (v) => { const d = Number(v.days); const k = n(d); return d === 0 ? "The frost-free season is about as long as in 1991 to 2020." : `The frost-free season is now ${k} ${days(k, "en")} ${d > 0 ? "longer" : "shorter"} than in 1991 to 2020.`; },
    es: (v) => { const d = Number(v.days); const k = n(d); return d === 0 ? "La temporada sin heladas dura lo mismo que en 1991 a 2020." : `La temporada sin heladas es ahora ${k} ${days(k, "es")} más ${d > 0 ? "larga" : "corta"} que en 1991 a 2020.`; },
  },
  "card_text.headline.grace_trend": {
    was: "NASA GRACE satellites show groundwater storage in this region changing by {cm_per_yr} a year since 2002.",
    en: "NASA GRACE satellites show groundwater storage in this region changing by {cm_per_yr} since 2002.",
    es: "Los satélites GRACE de la NASA muestran que el agua subterránea de esta región cambia {cm_per_yr} desde 2002.",
  },
  "card_text.why.soil_health": {
    was: "Soil health score: {score} out of 100. Days a year with living roots in the ground: about {living_root_days}. Years with a legume in the cycle: {legume_years}.",
    en: "Soil health score {score} out of 100. Living roots are in the ground about {living_root_days} days a year, and a legume grows in {legume_years} {legume_years|year|years} of the cycle.",
    es: "Puntaje de salud del suelo: {score} de 100. Hay raíces vivas unos {living_root_days} días al año, y una leguminosa crece en {legume_years} {legume_years|año|años} del ciclo.",
  },
  "card_text.why.pest_break": {
    was: "Years in a row with the same crop family: {max_run_years}, compared with {r0_max_run_years} now. Shorter runs may help break pest and disease cycles.",
    en: "The same crop family runs at most {max_run_years} {max_run_years|year|years} in a row, against {r0_max_run_years} now. Shorter runs may help break pest and disease cycles.",
    es: "La misma familia de cultivos se repite como máximo {max_run_years} {max_run_years|año|años} seguidos, frente a {r0_max_run_years} ahora. Rachas más cortas pueden ayudar a romper ciclos de plagas y enfermedades.",
  },
  "card_text.why.water_erosion": {
    was: "Stormy days a year with bare ground: {bare_storm_days}, compared with {r0_bare_storm_days} now.",
    en: "Bare ground on {bare_storm_days} stormy days a year, against {r0_bare_storm_days} now.",
    es: "Suelo descubierto en {bare_storm_days} días de tormenta al año, frente a {r0_bare_storm_days} ahora.",
  },
  "card_text.why.wind_erosion": {
    was: "Windy days a year with bare ground: {bare_windy_days}, compared with {r0_bare_windy_days} now.",
    en: "Bare ground on {bare_windy_days} windy days a year, against {r0_bare_windy_days} now.",
    es: "Suelo descubierto en {bare_windy_days} días de viento al año, frente a {r0_bare_windy_days} ahora.",
  },
  "card_text.why.heat_frost_risk": {
    was: "Hot days a year when crops are in a heat-sensitive stage: {heat_days}, compared with {r0_heat_days} now.",
    en: "Crops are in a heat-sensitive stage on {heat_days} hot days a year, against {r0_heat_days} now.",
    es: "Los cultivos están en una etapa sensible al calor {heat_days} días calurosos al año, frente a {r0_heat_days} ahora.",
  },
  "card_text.benefits.pest_cycle_broken": {
    was: "Changing crops often may help break pest cycles. Longest run of one crop family, in years: {max_run_years}.",
    en: "Changing crops often may help break pest cycles. The longest run of one crop family is {max_run_years} {max_run_years|year|years}.",
    es: "Cambiar de cultivo seguido puede ayudar a romper ciclos de plagas. La racha más larga de una misma familia es de {max_run_years} {max_run_years|año|años}.",
  },
  "card_text.benefits.bare_days_reduced": {
    was: "Days a year with the ground covered may rise by about {days}.",
    en: "The ground may be covered about {days} more days a year.",
    es: "El suelo podría estar cubierto unos {days} días más al año.",
  },
  "card_text.benefits.legume_added": {
    was: "Legume years in the cycle: {legume_years} of {cycle_years}. Legumes can lower the nitrogen fertilizer the next crop needs.",
    en: "A legume grows in {legume_years} of {cycle_years} years. Legumes can lower the nitrogen fertilizer the next crop needs.",
    es: "Una leguminosa crece en {legume_years} de {cycle_years} años. Las leguminosas pueden reducir el fertilizante nitrogenado que necesita el siguiente cultivo.",
  },
  "copy.card.hidden_count": {
    was: "Options hidden by your limits: {n}",
    en: "{n} more {n|option is|options are} hidden by your limits",
    es: "{n} {n|opción más está oculta|opciones más están ocultas} por sus límites",
  },
  "copy.card.shown_at": {
    was: "Numbers shown with: {cap}.",
    en: "Numbers shown at {cap}.",
    es: "Cifras mostradas con {cap}.",
  },
};

/** The preferred line for `key` if the content still has the old English text, else null (content wins). */
export function preferred(key: string, currentEn: string | undefined, lang: Lang, vars: Vars): { template: string } | { text: string } | null {
  const entry = PREFERRED[key];
  if (!entry || currentEn !== entry.was) return null;
  const line = entry[lang] ?? entry.en;
  return typeof line === "function" ? { text: line(vars) } : { template: line };
}
