// Typed client-side loaders for /data/** (handover §4.2). In-memory cache keyed by path.
import type { ZodType, ZodTypeDef } from "zod";
import type {
  AssistantQuestionsFile, CalendarFile, CardText, Content, CopyFile, CropsFile, FieldBundle, FieldId,
  FieldsFile, GlossaryFile, NeighborsFile, ObservedFile, ReplayFile, RotationsFile, SourcesFile,
  StrategiesFile, SummaryFile, ValidationFile, WaterFile,
} from "@/lib/types";
import {
  assistantQuestionsSchema, calendarSchema, cardTextSchema, copySchema, cropsSchema, fieldsSchema,
  glossarySchema, neighborsSchema, observedSchema, replaySchema, rotationsSchema, sourcesSchema,
  strategiesSchema, summarySchema, validationSchema, waterSchema,
} from "@/lib/schemas";

type Schema<T> = ZodType<T, ZodTypeDef, unknown>;

const cache = new Map<string, Promise<unknown>>();
const mockPaths = new Set<string>();
const listeners = new Set<() => void>();

export const MOCK_EVENT = "field-shift:mock-data";

/** Paths of every loaded file with `_meta.mock === true`. */
export function mockFiles(): string[] {
  return [...mockPaths].sort();
}

export function onMockChange(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function markMock(path: string, raw: unknown) {
  const meta = typeof raw === "object" && raw !== null ? (raw as { _meta?: { mock?: unknown } })._meta : undefined;
  if (meta?.mock === true && !mockPaths.has(path)) {
    mockPaths.add(path);
    listeners.forEach((listener) => listener());
  }
}

class MissingFile extends Error {}

function fetchJson(path: string): Promise<unknown> {
  let pending = cache.get(path);
  if (!pending) {
    pending = fetch(path).then(async (response) => {
      if (response.status === 404) throw new MissingFile(path);
      if (!response.ok) throw new Error(`Could not load ${path} (${response.status})`);
      return response.json() as Promise<unknown>;
    });
    pending.catch(() => cache.delete(path));
    cache.set(path, pending);
  }
  return pending;
}

/**
 * Load and validate one file. Validation issues are logged loudly but never crash the page:
 * the raw data is still returned so one stray field does not blank a section.
 */
async function load<T>(path: string, schema: Schema<T>): Promise<T> {
  const raw = await fetchJson(path);
  markMock(path, raw);
  const result = schema.safeParse(raw);
  if (result.success) return result.data;
  console.error(`[data] ${path} does not match the contract`, result.error.issues.slice(0, 20));
  return raw as T;
}

/** Same as load, but a missing file (404) or a network failure resolves to null. */
async function loadOptional<T>(path: string, schema: Schema<T>): Promise<T | null> {
  try {
    return await load(path, schema);
  } catch (error) {
    if (!(error instanceof MissingFile)) console.error(`[data] optional file ${path} failed`, error);
    return null;
  }
}

export const getFields = (): Promise<FieldsFile> => load("/data/fields.json", fieldsSchema);
export const getSources = (): Promise<SourcesFile> => load("/data/sources.json", sourcesSchema);
export const getCrops = (): Promise<CropsFile> => load("/data/crops.json", cropsSchema);
export const getRotations = (): Promise<RotationsFile> => load("/data/rotations.json", rotationsSchema);

export async function getContent(): Promise<Content> {
  const [cardText, copy, glossary, questions] = await Promise.all([
    load<CardText>("/data/content/card_text.json", cardTextSchema),
    load<CopyFile>("/data/content/copy.json", copySchema),
    loadOptional<GlossaryFile>("/data/content/glossary.json", glossarySchema),
    loadOptional<AssistantQuestionsFile>("/data/content/assistant_questions.json", assistantQuestionsSchema),
  ]);
  return { cardText, copy, glossary, questions };
}

export async function getFieldBundle(fid: FieldId): Promise<FieldBundle> {
  const base = `/data/field/${fid}`;
  const [summary, calendar, replay, strategies, validation, water, observed, neighbors] = await Promise.all([
    load<SummaryFile>(`${base}/summary.json`, summarySchema),
    load<CalendarFile>(`${base}/calendar.json`, calendarSchema),
    load<ReplayFile>(`${base}/replay.json`, replaySchema),
    load<StrategiesFile>(`${base}/strategies.json`, strategiesSchema),
    loadOptional<ValidationFile>(`${base}/validation.json`, validationSchema),
    loadOptional<WaterFile>(`${base}/water.json`, waterSchema),
    loadOptional<ObservedFile>(`${base}/observed.json`, observedSchema),
    loadOptional<NeighborsFile>(`${base}/neighbors.json`, neighborsSchema),
  ]);
  return { summary, calendar, replay, strategies, validation, water, observed, neighbors };
}

export const getValidation = (fid: FieldId): Promise<ValidationFile | null> =>
  loadOptional<ValidationFile>(`/data/field/${fid}/validation.json`, validationSchema);
