// zod mirrors of lib/types.ts (README §7–§9). Each schema is annotated with its type,
// so a drift between the two fails `tsc`.
import { z } from "zod";
import type * as T from "@/lib/types";

type Schema<Out> = z.ZodType<Out, z.ZodTypeDef, unknown>;

// ---------- §7.2 IDs ----------
export const FIELD_IDS = ["f1", "f2", "f3"] as const satisfies readonly T.FieldId[];
export const CROP_IDS = ["corn", "sorghum", "wheat", "soybean", "alfalfa", "triticale", "rye_cover", "cotton", "fallow"] as const satisfies readonly T.CropId[];
export const ROTATION_IDS = ["R0", "R1", "R2", "R3", "R4", "R5", "R6"] as const satisfies readonly T.RotationId[];
export const CAP_IDS = ["dryland", "cap150", "cap300", "cap450"] as const satisfies readonly T.CapId[];
export const CLIMATE_IDS = ["actual", "hotdry"] as const satisfies readonly T.ClimateId[];
export const SCENARIO_KEYS = CAP_IDS.flatMap((cap) => CLIMATE_IDS.map((climate) => `${cap}|${climate}` as const)) as T.ScenarioKey[];
export const CRITERION_IDS = ["water_use", "income_mean", "income_worst", "soil_health", "water_erosion", "wind_erosion", "pest_break", "heat_frost_risk"] as const satisfies readonly T.CriterionId[];
export const ROTATION_CLASSES = ["continuous_corn", "corn_wheat_sorghum", "corn_soy", "wsf", "wheat_fallow", "alfalfa", "mixed"] as const satisfies readonly T.RotationClass[];
export const SOURCE_TAGS = ["POWER", "IMERG", "SMAP", "MODIS", "HLS", "ECOSTRESS", "GRACE", "SRTM", "SSURGO", "CSB", "NASS", "OpenET", "PRISM", "USGS", "CoCoRaHS", "GAEZ", "AMS", "FAO56", "MODEL"] as const satisfies readonly T.SourceTag[];
export const EQUIPMENT_IDS = ["hay", "cotton"] as const satisfies readonly T.EquipmentId[];
export const LEVELS = ["good", "fair", "limited"] as const satisfies readonly T.Level[];
export const LANGS = ["en", "es"] as const satisfies readonly T.Lang[];

export const fieldId = z.enum(FIELD_IDS);
export const cropId = z.enum(CROP_IDS);
export const rotationId = z.enum(ROTATION_IDS);
export const capId = z.enum(CAP_IDS);
export const climateId = z.enum(CLIMATE_IDS);
export const scenarioKey = z.enum(SCENARIO_KEYS as [T.ScenarioKey, ...T.ScenarioKey[]]);
export const criterionId = z.enum(CRITERION_IDS);
export const rotationClass = z.enum(ROTATION_CLASSES);
export const sourceTag = z.enum(SOURCE_TAGS);
export const equipmentId = z.enum(EQUIPMENT_IDS);
export const level = z.enum(LEVELS);
export const lang = z.enum(LANGS);
export const localized: Schema<T.Localized> = z.object({ en: z.string(), es: z.string() });

/** An object with exactly these keys, each required (zod's record() would make them optional). */
function fullRecord<K extends string, V>(keys: readonly K[], value: Schema<V>): Schema<Record<K, V>> {
  const shape = Object.fromEntries(keys.map((key) => [key, value])) as Record<K, Schema<V>>;
  return z.object(shape) as unknown as Schema<Record<K, V>>;
}

const vars: Schema<Record<string, number | string>> = z.record(z.string(), z.union([z.number(), z.string()]));
const lonLat: Schema<[number, number]> = z.tuple([z.number(), z.number()]);
const polygon: Schema<T.Field["geometry"]> = z.object({
  type: z.literal("Polygon"),
  coordinates: z.array(z.array(z.array(z.number()))),
});
const step = z.object({ crop: cropId, cover_after: cropId.nullable() });

// ---------- §8.3 ----------
export const metaSchema: Schema<T.Meta> = z.object({
  schema: z.string(), mock: z.boolean(), generated_at: z.string(), generator: z.string(),
});

export const soilSchema: Schema<T.Soil> = z.object({
  mukey: z.string(), map_unit_name: z.string(), component: z.string(), comppct: z.number(),
  texture: z.string(), awc_mm_per_m: z.number(), aws_0_100_mm: z.number(), om_pct: z.number(),
  k_factor: z.number().nullable(), hydgrp: z.enum(["A", "B", "C", "D", "A/D", "B/D", "C/D"]),
  slope_pct: z.number(), weg: z.string().nullable(), wei_t_ac_yr: z.number().nullable(),
  drainage_class: z.string(), restrictive_depth_cm: z.number().nullable(),
});

export const fieldSchema: Schema<T.Field> = z.object({
  id: fieldId, name: localized, kind: z.enum(["irrigated_pivot", "dryland", "sandy_wind"]),
  county_fips: z.literal("20055"), centroid: lonLat, geometry: polygon,
  area_ha: z.number(), area_ac: z.number(), irrigated: z.boolean(), csb_id: z.string().nullable(),
  crop_history: z.array(z.object({
    year: z.number(), crop: z.union([cropId, z.literal("other")]), cdl_code: z.number(), cdl_name: z.string(),
  })),
  detected: z.object({
    rotation_class: rotationClass, sequence: z.array(cropId), confidence: level,
    years: z.tuple([z.number(), z.number()]),
  }),
  soil: soilSchema,
  terrain: z.object({ elev_m: z.number(), slope_pct: z.number(), low_spot: z.boolean() }),
});
export const fieldsSchema: Schema<T.FieldsFile> = z.object({ _meta: metaSchema, fields: z.array(fieldSchema) });

export const sourcesSchema: Schema<T.SourcesFile> = z.object({
  _meta: metaSchema,
  sources: z.array(z.object({
    tag: sourceTag, name: z.string(), provider: z.string(), url: z.string(),
    what: z.string(), resolution: z.string(), period: z.string(), used_for: z.string(),
  })),
});

export const waterSchema: Schema<T.WaterFile> = z.object({
  _meta: metaSchema, field_id: fieldId,
  grace: z.object({
    cell_center: lonLat,
    series: z.array(z.object({ month: z.string(), tws_anom_cm: z.number() })),
    trend_cm_per_yr: z.number(), period: z.tuple([z.string(), z.string()]),
  }),
  wells: z.array(z.object({
    site_id: z.string(), name: z.string(), distance_km: z.number(),
    series: z.array(z.object({ date: z.string(), depth_to_water_m: z.number() })),
    trend_m_per_yr: z.number().nullable(),
  })),
  smap_rootzone_anom: z.array(z.object({ month: z.string(), anom_pct: z.number() })),
});

export const observedSchema: Schema<T.ObservedFile> = z.object({
  _meta: metaSchema, field_id: fieldId,
  ndvi_modis: z.array(z.object({ date: z.string(), ndvi: z.number() })),
  ndvi_climatology: z.array(z.object({ doy: z.number(), mean: z.number(), p10: z.number(), p90: z.number() })),
  drought_years: z.array(z.object({ year: z.number(), ndvi_summer_anom_pct: z.number() })),
  openet_monthly: z.array(z.object({ month: z.string(), et_mm: z.number() })),
  ecostress: z.array(z.object({ datetime: z.string(), et_mm_day: z.number().nullable(), esi: z.number().nullable() })),
  precip_check: z.array(z.object({
    month: z.string(), power_mm: z.number(), imerg_mm: z.number().nullable(), cocorahs_mm: z.number().nullable(),
  })),
});

export const neighborsSchema: Schema<T.NeighborsFile> = z.object({
  _meta: metaSchema, field_id: fieldId, pool_size: z.number(), matched: z.number(),
  method: z.object({ features: z.array(z.string()), k: z.number(), note: z.string() }),
  groups: z.array(z.object({
    rotation_class: rotationClass, matches_rotation: rotationId.nullable(), is_current: z.boolean(), n: z.number(),
    et_mm_yr_median: z.number().nullable(), ndvi_drop_2012_pct: z.number().nullable(),
    ndvi_drop_2022_pct: z.number().nullable(), esi_summer_mean: z.number().nullable(),
  })),
  fields: z.array(z.object({
    id: z.string(), centroid: lonLat, geometry: polygon, rotation_class: rotationClass,
    irrigated: z.boolean(), similarity: z.number(),
  })),
});

// ---------- §8.4 ----------
const dateWindow = z.object({ start: z.string(), end: z.string() }).nullable();
export const cropTraitsSchema: Schema<T.CropTraits> = z.object({
  name: localized, family: z.string(), host_group: z.string(),
  season: z.enum(["summer", "winter", "perennial", "cover", "none"]),
  plant_window: dateWindow, harvest_window: dateWindow,
  stage_days: z.object({ ini: z.number(), dev: z.number(), mid: z.number(), late: z.number() }).nullable(),
  kc: z.object({ ini: z.number(), mid: z.number(), end: z.number() }).nullable(),
  root_max_m: z.number().nullable(), p: z.number().nullable(), ky: z.number().nullable(),
  heat: z.object({ stage: z.enum(["ini", "dev", "mid", "late"]), tmax_c: z.number() }).nullable(),
  frost_kill_c: z.number().nullable(), requires_irrigation: z.boolean(), n_fixing: z.boolean(),
  residue: z.enum(["low", "medium", "high"]), root_type: z.enum(["fibrous", "tap", "deep_tap"]),
  forage: z.boolean(),
  yield: z.object({
    nass_commodity: z.string().nullable(), unit: z.string().nullable(),
    irrigated_default: z.number().nullable(), dryland_default: z.number().nullable(),
  }).nullable(),
  price: z.object({ unit: z.string().nullable(), default: z.number().nullable() }).nullable(),
  equipment: z.array(equipmentId), sources: z.array(z.string()),
});
export const cropsSchema: Schema<T.CropsFile> = z.object({ _meta: metaSchema, crops: fullRecord(CROP_IDS, cropTraitsSchema) });

export const rotationSchema: Schema<T.Rotation> = z.object({
  id: rotationId, steps: z.array(step), irrigated: z.boolean(), min_cap: capId,
  requires_equipment: z.array(equipmentId), needs_forage_market: z.boolean(), tier: z.enum(["must", "could"]),
});
export const rotationsSchema: Schema<T.RotationsFile> = z.object({ _meta: metaSchema, rotations: z.array(rotationSchema) });

const climateStats: Schema<T.ClimateStats> = z.object({
  frost_free_days: z.number(), last_spring_frost: z.string(), first_fall_frost: z.string(),
  gdd_base10_c: z.number(), precip_mm_yr: z.number(), days_tmax_ge_35: z.number(), et0_mm_yr: z.number(),
});
export const summarySchema: Schema<T.SummaryFile> = z.object({
  _meta: metaSchema, field_id: fieldId,
  current_rotation: z.object({ steps: z.array(step), rotation_class: rotationClass, years: z.tuple([z.number(), z.number()]) }),
  climate: z.object({
    normal: climateStats, recent: climateStats,
    normal_period: z.literal("1991-2020"), recent_period: z.literal("2016-2025"), sources: z.array(sourceTag),
  }),
  water: z.object({
    grace_trend_cm_per_yr: z.number(), wells_trend_m_per_yr: z.number().nullable(),
    outlook: z.enum(["declining", "stable", "rising"]),
  }),
  headline_facts: z.array(z.object({ text_id: z.string(), vars, sources: z.array(sourceTag) })),
});

const calendarCell: Schema<T.CalendarCell> = z.object({
  state: z.union([cropId, z.literal("bare")]),
  stage: z.enum(["ini", "dev", "mid", "late"]).nullable(),
  flags: z.array(z.enum(["heat", "frost", "dry", "bare_storm", "bare_wind"])),
});
export const calendarSchema: Schema<T.CalendarFile> = z.object({
  _meta: metaSchema, field_id: fieldId,
  climate_risk: z.array(z.object({
    month: z.number(), p_heat: z.number(), p_frost: z.number(), p_dry_spell: z.number(),
    storm_days: z.number(), windy_days: z.number(),
  })),
  rotations: z.array(z.object({
    rotation_id: rotationId,
    years: z.array(z.object({ year_index: z.number(), months: z.array(calendarCell) })),
  })),
});

const replaySummary: Schema<T.ReplaySummary> = z.object({
  irrigation_mm_mean: z.number(), eta_mm_mean: z.number(), stress_days_mean: z.number(), rel_yield_mean: z.number(),
  revenue_usd_ac_mean: z.number(), revenue_usd_ac_worst5: z.number(),
  bare_days_mean: z.number(), bare_storm_days_mean: z.number(), bare_windy_days_mean: z.number(),
  water_erosion_idx: z.number(), wind_erosion_idx: z.number(),
  heat_days_mean: z.number(), frost_events_total: z.number(),
});
const replayYear: Schema<T.ReplayYear> = z.object({
  year: z.number(), crop_mix: z.record(cropId, z.number()),
  irrigation_mm: z.number(), eta_mm: z.number(), etc_mm: z.number(), stress_days: z.number(), rel_yield: z.number(),
  revenue_usd_ac: z.number(), bare_days: z.number(), water_erosion_idx: z.number(), wind_erosion_idx: z.number(),
  heat_days: z.number(), frost_events: z.number(),
});
const replayRun: Schema<T.ReplayRun> = z.object({ feasible: z.boolean(), summary: replaySummary, by_year: z.array(replayYear) });
export const replaySchema: Schema<T.ReplayFile> = z.object({
  _meta: metaSchema, field_id: fieldId,
  years: z.tuple([z.literal(2000), z.literal(2025)]),
  drought_years: z.array(z.number()),
  scenarios: fullRecord(SCENARIO_KEYS, z.record(rotationId, replayRun)),
});

const textRef: Schema<T.TextRef> = z.object({ text_id: z.string(), vars });
const criterionValue = z.object({ raw: z.number(), unit: z.string(), norm: z.number(), vars });
export const strategyEntrySchema: Schema<T.StrategyEntry> = z.object({
  rotation_id: rotationId, feasible: z.boolean(), infeasible_reason_id: z.string().nullable(),
  criteria: fullRecord(CRITERION_IDS, criterionValue),
  requires_equipment: z.array(equipmentId), needs_forage_market: z.boolean(),
  crops_without_local_market: z.array(cropId),
  benefits: z.array(textRef),
  evidence: z.array(z.object({ text_id: z.string(), vars, sources: z.array(sourceTag) })),
  gap_ids: z.array(z.string()), risk_ids: z.array(z.string()), confidence: level,
});
export const strategiesSchema: Schema<T.StrategiesFile> = z.object({
  _meta: metaSchema, field_id: fieldId, scenarios: fullRecord(SCENARIO_KEYS, z.array(strategyEntrySchema)),
});

export const validationSchema: Schema<T.ValidationFile> = z.object({
  _meta: metaSchema, field_id: fieldId,
  items: z.array(z.object({
    id: z.enum(["et_vs_openet", "sm_vs_smap", "precip_power_vs_imerg", "precip_vs_cocorahs"]),
    metric: z.enum(["bias_pct", "r", "r2"]), value: z.number(), n: z.number(), level, vars,
    sources: z.array(sourceTag),
  })),
});

export const factSchema: Schema<T.Fact> = z.object({
  id: z.string(), text: z.string(), value: z.number(), unit: z.string().nullable(), source: sourceTag,
  scenario: scenarioKey.optional(), rotation_id: rotationId.optional(),
});
export const assistantContextSchema: Schema<T.AssistantContext> = z.object({
  _meta: metaSchema, field_id: fieldId, field_name: z.string(), facts: z.array(factSchema),
});

export const askResponseSchema: Schema<T.AskResponse> = z.object({
  answer_md: z.string(),
  citations: z.array(z.object({ tag: sourceTag, name: z.string(), url: z.string() })),
  numbers: z.array(z.object({
    text: z.string(), value: z.number(), unit: z.string().nullable(), verified: z.boolean(), fact_id: z.string().nullable(),
  })),
  cached: z.boolean(),
  provider: z.enum(["gemini", "groq", "cache"]),
  model: z.string().nullable(),
  notice: z.enum(["using_cache", "scenario_mismatch"]).optional(),
});
export const assistantCacheSchema: Schema<T.AssistantCache> = z.object({
  _meta: metaSchema, field_id: fieldId, scenario: z.literal("cap300|actual"),
  answers: z.record(z.string(), fullRecord(LANGS, askResponseSchema)),
});

export const promptSchema: Schema<T.PromptFile> = z.object({
  _meta: metaSchema, version: z.string(), system: z.string(), temperature: z.number(), max_tokens: z.number(),
});

// ---------- §8.5 ----------
const locRecord = z.record(z.string(), localized);
export const cardTextSchema: Schema<T.CardText> = z.object({
  _meta: metaSchema,
  rotations: fullRecord(ROTATION_IDS, z.object({ name: localized, tagline: localized })),
  criteria_labels: fullRecord(CRITERION_IDS, localized),
  why: fullRecord(CRITERION_IDS, localized),
  benefits: locRecord, evidence: locRecord, gaps: locRecord, risks: locRecord,
  infeasible: locRecord, headline: locRecord, validation: locRecord,
});
export const copySchema: Schema<T.CopyFile> = z.object({ _meta: metaSchema, strings: locRecord });
export const glossarySchema: Schema<T.GlossaryFile> = z.object({
  _meta: metaSchema,
  terms: z.array(z.object({ id: z.string(), term: localized, short: localized, long: localized })),
});
export const assistantQuestionsSchema: Schema<T.AssistantQuestionsFile> = z.object({
  _meta: metaSchema, questions: z.array(z.object({ id: z.string(), text: localized })),
});

// ---------- §9 ----------
export const askRequestSchema: Schema<T.AskRequest> = z.object({
  field_id: fieldId, lang, scenario: scenarioKey,
  question_id: z.string().max(16).optional(),
  question: z.string().trim().min(1).max(500).optional(),
  top_rotations: z.array(rotationId).max(7).optional(),
  history: z.array(z.object({ role: z.enum(["user", "assistant"]), content: z.string().max(1500) })).max(6).optional(),
}).refine((request) => Boolean(request.question_id || request.question), {
  message: "question or question_id is required",
});
