import { z } from "zod";

const meta = z.object({
  mock: z.boolean().optional(),
  version: z.string().optional(),
  updated_at: z.string().optional(),
  note: z.string().optional(),
});
const localized = z.object({ en: z.string(), es: z.string().optional() });
const sourceIds = z.array(z.string());
const fieldId = z.enum(["f1", "f2", "f3"]);
const climate = z.enum(["actual", "hotdry"]);
const scenario = z.enum([
  "dryland|actual", "dryland|hotdry", "cap150|actual", "cap150|hotdry",
  "cap300|actual", "cap300|hotdry", "cap450|actual", "cap450|hotdry",
]);
const criterion = z.enum(["water", "soil", "climate", "market", "operations"]);
const point = z.object({ year: z.number(), value: z.number() });
const metricSeries = z.record(z.enum(["irrigation", "revenue", "stress", "bare"]), z.array(point));

export const cropSchema = z.object({
  id: z.string(), name: localized, color: z.string(), category: z.enum(["cash", "cover", "bare"]),
});
export const glossarySchema = z.object({
  _meta: meta,
  entries: z.record(z.object({ term: localized, short: localized, long: localized, source_ids: sourceIds.optional() })),
});
export const assistantQuestionsSchema = z.object({
  _meta: meta,
  questions: z.array(z.object({ id: z.string(), en: z.string(), es: z.string() })),
});
export const assistantContextSchema = z.object({
  _meta: meta,
  facts: z.array(z.object({ id: z.string(), text: z.string(), source_ids: sourceIds })),
});
export const assistantCacheSchema = z.object({
  _meta: meta,
  answers: z.record(z.object({ en: z.string(), es: z.string() })),
});
export const promptSchema = z.object({ _meta: meta, template: z.string() });
export const tokensSchema = z.object({
  ink: z.string(), muted: z.string(), surface: z.string(), canvas: z.string(), line: z.string(),
  primary: z.string(), "primary-light": z.string(), accent: z.string(),
  "risk-heat": z.string(), "risk-frost": z.string(), "risk-dry": z.string(),
  "risk-storm": z.string(), "risk-wind": z.string(),
  crop: z.record(z.string()), rotation: z.record(z.string()),
});
export const rotationSchema = z.object({
  id: z.string(), name: localized,
  steps: z.array(z.object({ crop_id: z.string(), months: z.array(z.number()), stage: localized })),
  tags: z.array(z.string()),
});
export const fieldsSchema = z.object({
  _meta: meta,
  fields: z.array(z.object({
    id: fieldId, name: localized, kind: z.enum(["irrigated", "dryland"]),
    area_ha: z.number(), area_ac: z.number(), soil_texture: localized,
    center: z.tuple([z.number(), z.number()]), polygon: z.array(z.tuple([z.number(), z.number()])),
    current_rotation_id: z.string(), current_crops: z.array(z.string()).optional(), years: z.tuple([z.number(), z.number()]),
  })),
  neighbors: z.array(z.object({ id: z.string(), polygon: z.array(z.tuple([z.number(), z.number()])) })).optional(),
});
export const sourcesSchema = z.object({
  _meta: meta,
  sources: z.record(z.object({ name: localized, url: z.string().url(), role: localized, license: z.string().optional() })),
});
export const copySchema = z.object({ _meta: meta, strings: z.record(localized) });
export const cardTextSchema = z.object({
  _meta: meta,
  rotations: z.record(localized),
  why: z.record(criterion, localized),
  evidence: z.record(localized),
  benefits: z.record(localized),
  gaps: z.record(localized),
  risks: z.record(localized),
  infeasible: z.record(localized),
  validation: z.record(localized),
  headline: z.record(localized),
});
export const summarySchema = z.object({
  _meta: meta,
  field_id: fieldId,
  current_rotation: z.object({ id: z.string(), years: z.tuple([z.number(), z.number()]), steps: z.array(z.string()) }),
  soil: z.object({
    texture: localized, water_storage_mm: z.number(), organic_matter_pct: z.number(),
    wind_erosion: localized, source_ids: sourceIds,
  }),
  climate: z.object({
    normal: z.object({ frost_free_days: z.number(), hot_days: z.number(), precipitation_mm: z.number() }),
    recent: z.object({ frost_free_days: z.number(), hot_days: z.number(), precipitation_mm: z.number() }),
    source_ids: sourceIds,
  }),
  headline_facts: z.array(z.object({ text_id: z.string(), vars: z.record(z.union([z.number(), z.string()])), source_ids: sourceIds })),
});
export const strategiesSchema = z.object({
  _meta: meta,
  scenario_adjustments: z.record(scenario, z.object({ irrigation_factor: z.number(), climate_delta: z.number() })).optional(),
  entries: z.array(z.object({
    id: z.string(), scenario, criteria: z.record(criterion, z.object({ norm: z.number(), vars: z.record(z.union([z.number(), z.string()])) })),
    flags: z.array(z.string()), needs_irrigation_mm: z.number(), needs_equipment: z.boolean(),
    equipment_required: z.enum(["hay", "cotton"]).optional(),
    needs_forage_market: z.boolean(), crops_without_local_market: z.array(z.string()),
    confidence: z.enum(["high", "medium", "low"]),
    evidence: z.array(z.object({ text_id: z.string(), vars: z.record(z.union([z.number(), z.string()])), source_ids: sourceIds })),
    benefits: z.array(z.object({ text_id: z.string(), vars: z.record(z.union([z.number(), z.string()])), source_ids: sourceIds })),
    gaps: z.array(z.string()), risks: z.array(z.string()),
  })),
});
export const calendarSchema = z.object({
  _meta: meta, years: z.number(),
  climate_risk: z.array(z.object({
    month: z.number(), p_heat: z.number(), p_frost: z.number(), p_dry_spell: z.number(),
    storm_days: z.number(), windy_days: z.number(),
  })),
});
export const replaySchema = z.object({
  _meta: meta,
  series: z.record(climate, z.record(z.string(), metricSeries)),
  drought_years: z.array(z.number()),
});
export const validationSchema = z.object({
  _meta: meta,
  checks: z.array(z.object({
    id: z.string(), level: z.enum(["high", "medium", "low"]),
    vars: z.record(z.union([z.number(), z.string()])), source_ids: sourceIds,
  })),
});
export const waterSchema = z.object({
  _meta: meta,
  grace: z.array(z.object({ month: z.string(), anomaly_mm: z.number() })),
  well: z.object({ name: localized, trend_m_per_year: z.number(), source_ids: sourceIds }).nullable(),
  outlook: z.enum(["watch", "steady", "limited"]),
});
export const observedSchema = z.object({
  _meta: meta, points: z.array(z.object({ year: z.number(), ndvi: z.number(), soil_moisture_pct: z.number() })),
});
export const neighborsSchema = z.object({
  _meta: meta, disclaimer: z.string(),
  groups: z.array(z.object({
    rotation_id: z.string(), n_fields: z.number(), median_et_mm: z.number(),
    drought_greenness: z.object({ y2012: z.number(), y2022: z.number() }),
    is_current: z.boolean(), center: z.tuple([z.number(), z.number()]),
  })),
});
export const assistantRequestSchema = z.object({
  field_id: fieldId, lang: z.enum(["en", "es"]), scenario,
  question: z.string().min(1).max(500),
  question_id: z.string().optional(),
  history: z.array(z.object({ role: z.enum(["user", "assistant"]), content: z.string().max(1500) })).max(6),
  top_rotations: z.array(z.string()).max(4),
});
