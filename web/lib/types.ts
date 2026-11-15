export type Lang = "en" | "es";
export type FieldId = "f1" | "f2" | "f3";
export type Climate = "actual" | "hotdry";
export type WaterCap = "dryland" | "cap150" | "cap300" | "cap450";
export type CriterionId = "water" | "soil" | "climate" | "market" | "operations";
export type ScenarioId = `${WaterCap}|${Climate}`;
export type Localized = { en: string; es?: string };

export interface Meta {
  mock?: boolean;
  version?: string;
  updated_at?: string;
  note?: string;
}

export interface Crop {
  id: string;
  name: Localized;
  color: string;
  category: "cash" | "cover" | "bare";
}

export interface RotationStep {
  crop_id: string;
  months: number[];
  stage: Localized;
}

export interface Rotation {
  id: string;
  name: Localized;
  steps: RotationStep[];
  tags: string[];
}

export interface Field {
  id: FieldId;
  name: Localized;
  kind: "irrigated" | "dryland";
  area_ha: number;
  area_ac: number;
  soil_texture: Localized;
  center: [number, number];
  polygon: [number, number][];
  current_rotation_id: string;
  current_crops?: string[];
  years: [number, number];
}

export interface FieldsFile {
  _meta: Meta;
  fields: Field[];
  neighbors?: Array<{ id: string; polygon: [number, number][] }>;
}

export interface SourcesFile {
  _meta: Meta;
  sources: Record<string, { name: Localized; url: string; role: Localized; license?: string }>;
}

export interface SummaryFile {
  _meta: Meta;
  field_id: FieldId;
  current_rotation: { id: string; years: [number, number]; steps: string[] };
  soil: {
    texture: Localized;
    water_storage_mm: number;
    organic_matter_pct: number;
    wind_erosion: Localized;
    source_ids: string[];
  };
  climate: {
    normal: { frost_free_days: number; hot_days: number; precipitation_mm: number };
    recent: { frost_free_days: number; hot_days: number; precipitation_mm: number };
    source_ids: string[];
  };
  headline_facts: Array<{ text_id: string; vars: Record<string, number | string>; source_ids: string[] }>;
}

export interface CriterionValue {
  norm: number;
  vars: Record<string, number | string>;
}

export interface StrategyEntry {
  id: string;
  scenario: ScenarioId;
  criteria: Record<CriterionId, CriterionValue>;
  flags: string[];
  needs_irrigation_mm: number;
  needs_equipment: boolean;
  equipment_required?: "hay" | "cotton";
  needs_forage_market: boolean;
  crops_without_local_market: string[];
  confidence: "high" | "medium" | "low";
  evidence: Array<{ text_id: string; vars: Record<string, number | string>; source_ids: string[] }>;
  benefits: Array<{ text_id: string; vars: Record<string, number | string>; source_ids: string[] }>;
  gaps: string[];
  risks: string[];
}

export interface StrategiesFile {
  _meta: Meta;
  entries: StrategyEntry[];
  scenario_adjustments?: Record<ScenarioId, { irrigation_factor: number; climate_delta: number }>;
}

export interface ClimateRisk {
  month: number;
  p_heat: number;
  p_frost: number;
  p_dry_spell: number;
  storm_days: number;
  windy_days: number;
}

export interface CalendarFile {
  _meta: Meta;
  climate_risk: ClimateRisk[];
  years: number;
}

export type ReplayMetric = "irrigation" | "revenue" | "stress" | "bare";
export interface ReplayPoint {
  year: number;
  value: number;
}
export interface ReplayFile {
  _meta: Meta;
  series: Record<Climate, Record<string, Record<ReplayMetric, ReplayPoint[]>>>;
  drought_years: number[];
}

export interface ValidationFile {
  _meta: Meta;
  checks: Array<{ id: string; level: "high" | "medium" | "low"; vars: Record<string, number | string>; source_ids: string[] }>;
}

export interface WaterFile {
  _meta: Meta;
  grace: Array<{ month: string; anomaly_mm: number }>;
  well: { name: Localized; trend_m_per_year: number; source_ids: string[] } | null;
  outlook: "watch" | "steady" | "limited";
}

export interface ObservedFile {
  _meta: Meta;
  points: Array<{ year: number; ndvi: number; soil_moisture_pct: number }>;
}

export interface NeighborsFile {
  _meta: Meta;
  disclaimer: string;
  groups: Array<{
    rotation_id: string;
    n_fields: number;
    median_et_mm: number;
    drought_greenness: { y2012: number; y2022: number };
    is_current: boolean;
    center: [number, number];
  }>;
}

export interface FieldBundle {
  summary: SummaryFile;
  calendar: CalendarFile;
  replay: ReplayFile;
  strategies: StrategiesFile;
  validation: ValidationFile;
  water: WaterFile;
  observed: ObservedFile;
  neighbors: NeighborsFile | null;
}

export interface CopyFile {
  _meta: Meta;
  strings: Record<string, Localized>;
}

export interface CardTextFile {
  _meta: Meta;
  rotations: Record<string, Localized>;
  why: Record<CriterionId, Localized>;
  evidence: Record<string, Localized>;
  benefits: Record<string, Localized>;
  gaps: Record<string, Localized>;
  risks: Record<string, Localized>;
  infeasible: Record<string, Localized>;
  validation: Record<string, Localized>;
  headline: Record<string, Localized>;
}

export interface GlossaryEntry {
  term: Localized;
  short: Localized;
  long: Localized;
  source_ids?: string[];
}

export interface AssistantQuestion {
  id: string;
  en: string;
  es: string;
}

export interface AssistantRequest {
  field_id: FieldId;
  lang: Lang;
  scenario: ScenarioId;
  question: string;
  question_id?: string;
  history: Array<{ role: "user" | "assistant"; content: string }>;
  top_rotations: string[];
}

export interface AssistantNumber {
  value: string;
  verified: boolean;
  fact_id?: string;
  source_ids?: string[];
}

export interface AssistantResponse {
  answer: string;
  numbers: AssistantNumber[];
  notice?: "using_cache" | "scenario_mismatch";
}
