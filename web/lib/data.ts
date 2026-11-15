import type {
  CalendarFile, CardTextFile, CopyFile, FieldBundle, FieldId, FieldsFile,
  NeighborsFile, ObservedFile, ReplayFile, SourcesFile, StrategiesFile,
  SummaryFile, ValidationFile, WaterFile,
} from "@/lib/types";
import {
  calendarSchema, cardTextSchema, copySchema, fieldsSchema, neighborsSchema,
  observedSchema, replaySchema, sourcesSchema, strategiesSchema, summarySchema,
  validationSchema, waterSchema,
} from "@/lib/schemas";
import type { ZodType } from "zod";

type JsonSchema<T> = ZodType<T>;
const cache = new Map<string, Promise<unknown>>();
let hasMockData = false;

export function mockDataLoaded(): boolean {
  return hasMockData;
}

async function load<T>(path: string, schema: JsonSchema<T>, optional = false): Promise<T | null> {
  let pending = cache.get(path);
  if (!pending) {
    pending = fetch(path).then(async (response) => {
      if (optional && response.status === 404) return null;
      if (!response.ok) throw new Error(`Could not load ${path} (${response.status})`);
      return response.json() as Promise<unknown>;
    });
    cache.set(path, pending);
  }
  const raw = await pending;
  if (raw === null) return null;
  const result = schema.safeParse(raw);
  if (!result.success) {
    if (process.env.NODE_ENV === "development") console.error(`Invalid data at ${path}`, result.error.issues);
    throw new Error(`Data validation failed for ${path}`);
  }
  if (typeof raw === "object" && raw !== null && "_meta" in raw &&
      typeof raw._meta === "object" && raw._meta !== null && "mock" in raw._meta && raw._meta.mock === true) {
    hasMockData = true;
    if (typeof window !== "undefined") window.dispatchEvent(new Event("field-shift:mock-data"));
  }
  return result.data;
}

export const getFields = () => load("/data/fields.json", fieldsSchema) as Promise<FieldsFile>;
export const getSources = () => load("/data/sources.json", sourcesSchema) as Promise<SourcesFile>;
export const getCrops = async () => {
  const raw = await fetchJson("/data/crops.json");
  const parsed = (await import("@/lib/schemas")).cropSchema.array().safeParse(raw);
  if (!parsed.success) {
    if (process.env.NODE_ENV === "development") console.error("Invalid data at /data/crops.json", parsed.error.issues);
    throw new Error("Data validation failed for /data/crops.json");
  }
  return parsed.data;
};
export const getRotations = async () => {
  const raw = await fetchJson("/data/rotations.json");
  const parsed = (await import("@/lib/schemas")).rotationSchema.array().safeParse(raw);
  if (!parsed.success) {
    if (process.env.NODE_ENV === "development") console.error("Invalid data at /data/rotations.json", parsed.error.issues);
    throw new Error("Data validation failed for /data/rotations.json");
  }
  return parsed.data;
};

async function fetchJson(path: string): Promise<unknown> {
  let pending = cache.get(path);
  if (!pending) {
    pending = fetch(path).then(async (response) => {
      if (!response.ok) throw new Error(`Could not load ${path} (${response.status})`);
      return response.json() as Promise<unknown>;
    });
    cache.set(path, pending);
  }
  return pending;
}

export const getContent = async () => {
  const [cardText, copy, glossary, questions] = await Promise.all([
    load("/data/content/card_text.json", cardTextSchema),
    load("/data/content/copy.json", copySchema),
    load("/data/content/glossary.json", (await import("@/lib/schemas")).glossarySchema),
    load("/data/content/assistant_questions.json", (await import("@/lib/schemas")).assistantQuestionsSchema),
  ]);
  if (!cardText || !copy) throw new Error("Content files are missing");
  if (!glossary || !questions) throw new Error("Assistant content files are missing");
  return { cardText: cardText as CardTextFile, copy: copy as CopyFile, glossary, questions };
};
export function getFieldBundle(fid: FieldId): Promise<FieldBundle> {
  return Promise.all([
    load(`/data/field/${fid}/summary.json`, summarySchema),
    load("/data/field/common/calendar.json", calendarSchema),
    load("/data/field/common/replay.json", replaySchema),
    load("/data/field/common/strategies.json", strategiesSchema),
    load("/data/field/common/validation.json", validationSchema),
    load("/data/field/common/water.json", waterSchema),
    load("/data/field/common/observed.json", observedSchema),
    load("/data/field/common/neighbors.json", neighborsSchema, true),
  ]).then(([summary, calendar, replay, strategies, validation, water, observed, neighbors]) => {
    if (!summary || !calendar || !replay || !strategies || !validation || !water || !observed) {
      throw new Error(`Required field data is missing for ${fid}`);
    }
    return {
      summary: summary as SummaryFile,
      calendar: calendar as CalendarFile,
      replay: replay as ReplayFile,
      strategies: strategies as StrategiesFile,
      validation: validation as ValidationFile,
      water: water as WaterFile,
      observed: observed as ObservedFile,
      neighbors: neighbors as NeighborsFile | null,
    };
  });
}
