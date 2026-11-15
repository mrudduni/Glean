// Mock assistant_cache.json per field (README §8.4 / §9), built from the mock assistant_context.json.
// Uses lib/numberCheck.ts so cached answers carry the same number check the route runs.
// Run from web/ after make_mocks.py:  node scripts/mocks/make_cache.mts
import { readFileSync, writeFileSync } from "node:fs";
import { checkNumbers } from "../../lib/numberCheck.ts";
import type { AskResponse, AssistantContext, Fact, Lang, SourcesFile } from "../../lib/types.ts";

const DATA = new URL("../../public/data/", import.meta.url);
const read = <T,>(rel: string): T => JSON.parse(readFileSync(new URL(rel, DATA), "utf8")) as T;
const sources = read<SourcesFile>("sources.json");
const SCENARIO = "cap300|actual";

function fact(facts: Fact[], id: string): Fact | undefined {
  return facts.find((item) => item.id === id);
}

function answers(ctx: AssistantContext): Record<string, Record<Lang, string>> {
  const f = ctx.facts;
  const irr = (rid: string) => fact(f, `replay.${rid}.${SCENARIO}.irrigation_mm_mean`)?.value;
  const rev = (rid: string) => fact(f, `replay.${rid}.${SCENARIO}.revenue_usd_ac_mean`)?.value;
  const worst = (rid: string) => fact(f, `replay.${rid}.${SCENARIO}.revenue_usd_ac_worst5`)?.value;
  const rids = ["R1", "R2", "R3", "R5", "R6"].filter((rid) => irr(rid) !== undefined);
  const lowest = rids.reduce((best, rid) => ((irr(rid) ?? 1e9) < (irr(best) ?? 1e9) ? rid : best), rids[0]);
  const grace = fact(f, "water.grace_trend_cm_per_yr")?.value;
  const wells = fact(f, "water.wells_trend_m_per_yr")?.value;
  const hotNow = fact(f, "climate.recent.days_tmax_ge_35")?.value;
  const hotThen = fact(f, "climate.normal.days_tmax_ge_35")?.value;
  const aws = fact(f, "field.soil.aws_0_100_mm")?.value;
  return {
    q1: {
      en: `On ${ctx.field_name}, **${lowest}** needs the least irrigation: about ${irr(lowest)} mm a year [MODEL], against ${irr("R0")} mm for your current rotation [MODEL]. It averages $${rev(lowest)}/ac [MODEL]. Check your water right before you change plans.`,
      es: `En ${ctx.field_name}, **${lowest}** necesita menos riego: unos ${irr(lowest)} mm al año [MODEL], frente a ${irr("R0")} mm de su rotación actual [MODEL]. Promedia $${rev(lowest)}/ac [MODEL].`,
    },
    q2: {
      en: `Across 2000 to 2025, your current rotation averaged $${rev("R0")}/ac [MODEL] and $${worst("R0")}/ac in its 5 worst years [MODEL], which include the 2012 drought. Ask your extension agent how your yields compared that year.`,
      es: `De 2000 a 2025, su rotación actual promedió $${rev("R0")}/ac [MODEL] y $${worst("R0")}/ac en sus 5 peores años [MODEL], que incluyen la sequía de 2012.`,
    },
    q3: {
      en: `Alfalfa (R4) needs about ${irr("R4") ?? "more"} mm of irrigation a year here [MODEL], more than your 300 mm limit, plus hay equipment and a forage buyer. This soil holds about ${aws} mm of water [SSURGO], so alfalfa stands would depend on steady pumping.`,
      es: `La alfalfa (R4) necesita unos ${irr("R4") ?? "más"} mm de riego al año aquí [MODEL], más que su límite de 300 mm. Este suelo retiene unos ${aws} mm de agua [SSURGO].`,
    },
    q4: {
      en: `Yes. GRACE shows the regional water store changing by ${grace} cm a year [GRACE]${wells !== undefined ? `, and nearby wells show depth to water growing by ${wells} m a year [USGS]` : ""}. Saving irrigation now stretches the aquifer.`,
      es: `Sí. GRACE muestra que el almacenamiento regional de agua cambia ${grace} cm al año [GRACE]${wells !== undefined ? ` y los pozos cercanos muestran que la profundidad al agua aumenta ${wells} m al año [USGS]` : ""}.`,
    },
    q5: {
      en: `Recent summers (2016 to 2025) bring about ${hotNow} days at or above 35 °C [POWER], against ${hotThen} days in the 1991 to 2020 normal [POWER]. Heat during July pollination hurts corn most.`,
      es: `Los veranos recientes (2016 a 2025) traen unos ${hotNow} días a 35 °C o más [POWER], frente a ${hotThen} días en la normal de 1991 a 2020 [POWER].`,
    },
    q6: {
      en: "Ask about herbicide carryover between crops, local buyers for sorghum or forage, crop insurance rules for a new rotation, and your water right. Our model holds prices constant and does not include input costs.",
      es: "Pregunte por el efecto residual de herbicidas, compradores locales de sorgo o forraje, reglas del seguro agrícola y su derecho de agua.",
    },
  };
}

function response(answer: string, facts: Fact[]): AskResponse {
  const tags = [...new Set([...answer.matchAll(/\[([A-Za-z0-9]+)\]/g)].map((m) => m[1]))];
  return {
    answer_md: answer,
    citations: tags.flatMap((tag) => {
      const source = sources.sources.find((item) => item.tag === tag);
      return source ? [{ tag: source.tag, name: source.name, url: source.url }] : [];
    }),
    numbers: checkNumbers(answer, facts),
    cached: true,
    provider: "cache",
    model: null,
  };
}

for (const fid of ["f1", "f2", "f3"] as const) {
  const ctx = read<AssistantContext>(`field/${fid}/assistant_context.json`);
  const facts = ctx.facts.filter((item) => !item.scenario || item.scenario === SCENARIO);
  const out: Record<string, Record<Lang, AskResponse>> = {};
  for (const [qid, text] of Object.entries(answers(ctx))) {
    out[qid] = { en: response(text.en, facts), es: response(text.es, facts) };
  }
  const payload = {
    _meta: { schema: "assistant_cache@1", mock: true, generated_at: new Date().toISOString().replace(/\.\d+Z$/, "Z"), generator: "web/scripts/mocks/make_cache.mts" },
    field_id: fid, scenario: SCENARIO, answers: out,
  };
  writeFileSync(new URL(`field/${fid}/assistant_cache.json`, DATA), JSON.stringify(payload, null, 1) + "\n");
  console.log("wrote", fid);
}
