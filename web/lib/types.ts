// Shared contract types. Copied verbatim from the root README §7.2, §8.3, §8.4, §8.5 and §9.
// If the README changes, update this file and lib/schemas.ts together.

import type { Polygon } from "geojson";

// ---------- §7.2 IDs ----------
export type FieldId     = "f1" | "f2" | "f3";      // f1 irrigated pivot, f2 dryland, f3 sandy / wind-erodible
export type CropId      = "corn" | "sorghum" | "wheat" | "soybean" | "alfalfa" | "triticale" | "rye_cover" | "cotton" | "fallow";
export type RotationId  = "R0" | "R1" | "R2" | "R3" | "R4" | "R5" | "R6";   // R0 = the field's current rotation
export type CapId       = "dryland" | "cap150" | "cap300" | "cap450";        // seasonal irrigation limit in mm
export type ClimateId   = "actual" | "hotdry";                                // hotdry = +1.5 °C and −15 % rain
export type ScenarioKey = `${CapId}|${ClimateId}`;                            // 8 scenarios; default "cap300|actual"
export type CriterionId = "water_use" | "income_mean" | "income_worst" | "soil_health"
                        | "water_erosion" | "wind_erosion" | "pest_break" | "heat_frost_risk";
export type RotationClass = "continuous_corn" | "corn_wheat_sorghum" | "corn_soy" | "wsf"
                          | "wheat_fallow" | "alfalfa" | "mixed";             // wsf = wheat–sorghum–fallow
export type SourceTag   = "POWER" | "IMERG" | "SMAP" | "MODIS" | "HLS" | "ECOSTRESS" | "GRACE" | "SRTM"
                        | "SSURGO" | "CSB" | "NASS" | "OpenET" | "PRISM" | "USGS" | "CoCoRaHS"
                        | "GAEZ" | "AMS" | "FAO56" | "MODEL";
export type EquipmentId = "hay" | "cotton";
export type Level       = "good" | "fair" | "limited";
export type Lang        = "en" | "es";
export type Localized   = { en: string; es: string };   // es may be "" → show en

// ---------- §8.3 D → web ----------
export interface Meta { schema: string; mock: boolean; generated_at: string; generator: string }

// fields.json
export interface FieldsFile { _meta: Meta; fields: Field[] }          // exactly f1, f2, f3
export interface Field {
  id: FieldId;
  name: Localized;                                              // e.g. "North pivot (irrigated)"
  kind: "irrigated_pivot" | "dryland" | "sandy_wind";
  county_fips: "20055";
  centroid: [number, number];                                   // [lon, lat]
  geometry: Polygon;                                            // EPSG:4326, simplified to ≤ 200 vertices
  area_ha: number; area_ac: number;
  irrigated: boolean;
  csb_id: string | null;
  crop_history: { year: number; crop: CropId | "other"; cdl_code: number; cdl_name: string }[];  // oldest → newest
  detected: { rotation_class: RotationClass; sequence: CropId[]; confidence: Level; years: [number, number] };
  soil: Soil;
  terrain: { elev_m: number; slope_pct: number; low_spot: boolean };   // low_spot = cold-air pooling candidate
}
export interface Soil {
  mukey: string; map_unit_name: string; component: string; comppct: number;
  texture: string;                       // surface texture, e.g. "loamy fine sand"
  awc_mm_per_m: number;                  // available water capacity, weighted 0–100 cm
  aws_0_100_mm: number;                  // available water storage 0–100 cm
  om_pct: number;                        // surface organic matter
  k_factor: number | null;               // water erodibility (kwfact)
  hydgrp: "A" | "B" | "C" | "D" | "A/D" | "B/D" | "C/D";
  slope_pct: number;
  weg: string | null;                    // wind erodibility group, e.g. "1", "4L"
  wei_t_ac_yr: number | null;            // wind erodibility index
  drainage_class: string;
  restrictive_depth_cm: number | null;
}

// sources.json
export interface SourcesFile { _meta: Meta; sources: {
  tag: SourceTag; name: string; provider: string; url: string;
  what: string; resolution: string; period: string; used_for: string;
}[] }

// field/{fid}/water.json
export interface WaterFile {
  _meta: Meta; field_id: FieldId;
  grace: { cell_center: [number, number]; series: { month: string; tws_anom_cm: number }[];
           trend_cm_per_yr: number; period: [string, string] };
  wells: { site_id: string; name: string; distance_km: number;
           series: { date: string; depth_to_water_m: number }[]; trend_m_per_yr: number | null }[];
  smap_rootzone_anom: { month: string; anom_pct: number }[];     // vs 2015–2025 monthly mean
}

// field/{fid}/observed.json
export interface ObservedFile {
  _meta: Meta; field_id: FieldId;
  ndvi_modis: { date: string; ndvi: number }[];                  // QA-filtered 16-day series
  ndvi_climatology: { doy: number; mean: number; p10: number; p90: number }[];   // 23 composites
  drought_years: { year: number; ndvi_summer_anom_pct: number }[];               // Jun–Aug vs 2016–2019 mean
  openet_monthly: { month: string; et_mm: number }[];
  ecostress: { datetime: string; et_mm_day: number | null; esi: number | null }[];
  precip_check: { month: string; power_mm: number; imerg_mm: number | null; cocorahs_mm: number | null }[];
}

// field/{fid}/neighbors.json
export interface NeighborsFile {
  _meta: Meta; field_id: FieldId;
  pool_size: number; matched: number;
  method: { features: string[]; k: number; note: string };
  groups: {
    rotation_class: RotationClass;
    matches_rotation: RotationId | null;     // see §7.2 mapping
    is_current: boolean;                     // same class as the demo field
    n: number;
    et_mm_yr_median: number | null;          // OpenET, annual
    ndvi_drop_2012_pct: number | null;
    ndvi_drop_2022_pct: number | null;
    esi_summer_mean: number | null;
  }[];
  fields: { id: string; centroid: [number, number]; geometry: Polygon;
            rotation_class: RotationClass; irrigated: boolean; similarity: number }[];   // similarity 0–1
}

// ---------- §8.4 M → web ----------
// crops.json — converted from content/crops.yaml (same fields, see §8.5)
export interface CropsFile { _meta: Meta; crops: Record<CropId, CropTraits> }

// rotations.json — structure only; names live in card_text.json
export interface RotationsFile { _meta: Meta; rotations: Rotation[] }   // R1–R6 (R0 is per field, in summary.json)
export interface Rotation {
  id: RotationId;
  steps: { crop: CropId; cover_after: CropId | null }[];          // one step per crop season, cycled
  irrigated: boolean;
  min_cap: CapId;                                                 // lowest water cap where it's feasible
  requires_equipment: EquipmentId[];
  needs_forage_market: boolean;
  tier: "must" | "could";
}

// field/{fid}/summary.json
export interface SummaryFile {
  _meta: Meta; field_id: FieldId;
  current_rotation: { steps: { crop: CropId; cover_after: CropId | null }[];
                      rotation_class: RotationClass; years: [number, number] };
  climate: {
    normal: ClimateStats; recent: ClimateStats;
    normal_period: "1991-2020"; recent_period: "2016-2025"; sources: SourceTag[];
  };
  water: { grace_trend_cm_per_yr: number; wells_trend_m_per_yr: number | null;
           outlook: "declining" | "stable" | "rising" };
  headline_facts: { text_id: string; vars: Record<string, number | string>; sources: SourceTag[] }[];  // 3 items
}
export interface ClimateStats {
  frost_free_days: number; last_spring_frost: string; first_fall_frost: string;   // MM-DD
  gdd_base10_c: number; precip_mm_yr: number; days_tmax_ge_35: number; et0_mm_yr: number;
}

// field/{fid}/calendar.json
export interface CalendarFile {
  _meta: Meta; field_id: FieldId;
  climate_risk: { month: number;                 // 1–12
                  p_heat: number; p_frost: number; p_dry_spell: number;   // 0–1, share of years
                  storm_days: number; windy_days: number }[];             // mean per month
  rotations: { rotation_id: RotationId;
               years: { year_index: number;      // 1…cycle length
                        months: CalendarCell[] }[] }[];                   // 12 cells, Jan → Dec
}
export interface CalendarCell {
  state: CropId | "bare";
  stage: "ini" | "dev" | "mid" | "late" | null;
  flags: ("heat" | "frost" | "dry" | "bare_storm" | "bare_wind")[];
}

// field/{fid}/replay.json
export interface ReplayFile {
  _meta: Meta; field_id: FieldId;
  years: [2000, 2025];
  drought_years: number[];                         // detected from data, e.g. [2002, 2011, 2012, 2022]
  scenarios: Record<ScenarioKey, Partial<Record<RotationId, ReplayRun>>>;   // all 8 scenarios, R0–R5 (+R6)
}
export interface ReplayRun { feasible: boolean; summary: ReplaySummary; by_year: ReplayYear[] }
export interface ReplaySummary {
  irrigation_mm_mean: number; eta_mm_mean: number; stress_days_mean: number; rel_yield_mean: number;
  revenue_usd_ac_mean: number; revenue_usd_ac_worst5: number;          // mean of the 5 worst years
  bare_days_mean: number; bare_storm_days_mean: number; bare_windy_days_mean: number;
  water_erosion_idx: number; wind_erosion_idx: number;
  heat_days_mean: number; frost_events_total: number;
}
export interface ReplayYear {
  year: number;
  crop_mix: Partial<Record<CropId, number>>;      // share of the rotation's acres in each crop that year (phase-averaged)
  irrigation_mm: number; eta_mm: number; etc_mm: number; stress_days: number; rel_yield: number;
  revenue_usd_ac: number; bare_days: number; water_erosion_idx: number; wind_erosion_idx: number;
  heat_days: number; frost_events: number;
}

// field/{fid}/strategies.json
export interface StrategiesFile { _meta: Meta; field_id: FieldId; scenarios: Record<ScenarioKey, StrategyEntry[]> }
export interface StrategyEntry {
  rotation_id: RotationId;
  feasible: boolean;
  infeasible_reason_id: string | null;            // key in card_text.infeasible
  criteria: Record<CriterionId, {
    raw: number; unit: string;
    norm: number;                                  // 0–100, higher = better for the farmer (already inverted where needed)
    vars: Record<string, number | string>;         // fills card_text.why[criterion]
  }>;
  requires_equipment: EquipmentId[];
  needs_forage_market: boolean;
  crops_without_local_market: CropId[];            // NASS shows no county acres
  benefits: TextRef[];                             // keys in card_text.benefits
  evidence: (TextRef & { sources: SourceTag[] })[];// keys in card_text.evidence
  gap_ids: string[];                               // keys in card_text.gaps
  risk_ids: string[];                              // keys in card_text.risks
  confidence: Level;
}
export interface TextRef { text_id: string; vars: Record<string, number | string> }

// field/{fid}/validation.json
export interface ValidationFile { _meta: Meta; field_id: FieldId; items: {
  id: "et_vs_openet" | "sm_vs_smap" | "precip_power_vs_imerg" | "precip_vs_cocorahs";
  metric: "bias_pct" | "r" | "r2"; value: number; n: number; level: Level;
  vars: Record<string, number | string>;           // fills card_text.validation[id]
  sources: SourceTag[];
}[] }

// field/{fid}/assistant_context.json
export interface AssistantContext {
  _meta: Meta; field_id: FieldId;
  field_name: string;
  facts: Fact[];                                   // ~80–150 facts, ≤ ~6k tokens in total
}
export interface Fact {
  id: string;                                      // e.g. "replay.R2.cap300|actual.irrigation_mm_mean"
  text: string;                                    // English sentence containing the number
  value: number | null; unit: string | null;       // null for text-only facts (M sends these); "mm", "usd_ac", ...
  source: SourceTag;
  scenario?: ScenarioKey;                          // omit = applies to all scenarios
  rotation_id?: RotationId;
}

// field/{fid}/assistant_cache.json
export interface AssistantCache {
  _meta: Meta; field_id: FieldId; scenario: "cap300|actual";
  top_rotations?: RotationId[];   // cards on screen when the cache was generated (R0 + top 3)
  answers: Record<string, Record<Lang, AskResponse>>;   // question id (q1–q6) → lang → response (§9)
}

// assistant/prompt.json
export interface PromptFile {
  _meta: Meta; version: string;
  system: string;     // template with {field_name} {lang_name} {scenario_label} {top_rotations} {facts_block}
  temperature: number; max_tokens: number;
}

// ---------- §8.5 U files ----------
// CropTraits: the content/crops.yaml entry shape, as converted by M into crops.json.
// family and root_type are nullable here because fallow has neither (U's crops.yaml).
export interface CropTraits {
  name: Localized;
  family: string | null;
  host_group: string;
  season: "summer" | "winter" | "perennial" | "cover" | "none";
  plant_window: { start: string; end: string } | null;
  harvest_window: { start: string; end: string } | null;
  stage_days: { ini: number; dev: number; mid: number; late: number } | null;
  kc: { ini: number; mid: number; end: number } | null;
  root_max_m: number | null;
  p: number | null;
  ky: number | null;
  heat: { stage: "ini" | "dev" | "mid" | "late"; tmax_c: number } | null;
  frost_kill_c: number | null;
  requires_irrigation: boolean;
  n_fixing: boolean;
  residue: "low" | "medium" | "high";
  root_type: "fibrous" | "tap" | "deep_tap" | null;
  forage: boolean;
  yield: { nass_commodity: string | null; unit: string | null; irrigated_default: number | null; dryland_default: number | null } | null;
  price: { unit: string | null; default: number | null } | null;
  equipment: EquipmentId[];
  sources: string[];
}

export interface CardText {
  _meta: Meta;
  rotations: Record<RotationId, { name: Localized; tagline: Localized }>;
  criteria_labels: Record<CriterionId, Localized>;
  why: Record<CriterionId, Localized>;              // templates, vars per §8.6
  benefits: Record<string, Localized>;
  evidence: Record<string, Localized>;
  gaps: Record<string, Localized>;
  risks: Record<string, Localized>;
  infeasible: Record<string, Localized>;
  headline: Record<string, Localized>;
  validation: Record<string, Localized>;
}
export interface CopyFile { _meta: Meta; strings: Record<string, Localized> }
export interface GlossaryFile { _meta: Meta; terms: { id: string; term: Localized; short: Localized; long: Localized }[] }
export interface AssistantQuestionsFile { _meta: Meta; questions: { id: string; text: Localized }[] }  // id "q1"…"q6"

// ---------- §9 AI assistant API ----------
export interface AskRequest {
  field_id: FieldId;
  lang: Lang;
  scenario: ScenarioKey;
  question_id?: string;              // "q1"…"q6" → served from cache, no LLM call
  question?: string;                 // free text, ≤ 500 chars (required if no question_id)
  top_rotations?: RotationId[];      // what the UI currently shows, best first
  history?: { role: "user" | "assistant"; content: string }[];   // last ≤ 6 turns
}

export interface AskResponse {
  answer_md: string;                 // markdown with [TAG] source tags
  citations: { tag: SourceTag; name: string; url: string }[];    // tags found in the answer, resolved via sources.json
  numbers: { text: string; value: number; unit: string | null;
             verified: boolean; fact_id: string | null }[];
  cached: boolean;
  provider: "gemini" | "groq" | "custom" | "cache";   // custom: a user's own OpenAI-compatible endpoint
  model: string | null;
  notice?: "using_cache" | "scenario_mismatch";   // scenario_mismatch: cached answer is for cap300|actual
}

export type AskError =
  | { error: "bad_request"; message: string }
  | { error: "llm_unavailable"; message: string };

// ---------- web-only helpers (not part of the contract) ----------
export interface Content {
  cardText: CardText;
  copy: CopyFile;
  glossary: GlossaryFile | null;
  questions: AssistantQuestionsFile | null;
}
export interface FieldBundle {
  summary: SummaryFile;
  calendar: CalendarFile;
  replay: ReplayFile;
  strategies: StrategiesFile;
  validation: ValidationFile | null;
  water: WaterFile | null;
  observed: ObservedFile | null;
  neighbors: NeighborsFile | null;
}
