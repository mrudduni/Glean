// Challenge rule (README 1): every field compares at least three rotations, the current one included.
// Runs pickShown on the real public/data files with the app's default settings.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { DEFAULT_SLIDERS, pickShown, sameRotation, weightsFromSliders } from "@/lib/score";
import type { FieldId, ReplayFile, RotationId, RotationsFile, StrategiesFile, SummaryFile } from "@/lib/types";

const read = <T,>(path: string): T => JSON.parse(readFileSync(resolve(__dirname, "../public/data", path), "utf8")) as T;
const rotations = read<RotationsFile>("rotations.json").rotations;
const defaults = { cap: "cap300", hay: false, cotton: false, forage: false } as const;
const scenario = "cap300|actual" as const;

function pickFor(fid: FieldId) {
  const summary = read<SummaryFile>(`field/${fid}/summary.json`);
  const strategies = read<StrategiesFile>(`field/${fid}/strategies.json`);
  const replay = read<ReplayFile>(`field/${fid}/replay.json`);
  const duplicates = new Set(rotations.filter((r) => sameRotation(r.steps, summary.current_rotation.steps)).map((r) => r.id));
  const irrigation = Object.fromEntries(Object.entries(replay.scenarios[scenario] ?? {}).map(([id, run]) => [id, run?.summary.irrigation_mm_mean])) as Partial<Record<RotationId, number>>;
  return { duplicates, picked: pickShown(strategies.scenarios[scenario] ?? [], weightsFromSliders(DEFAULT_SLIDERS), defaults, irrigation, duplicates) };
}

describe.each(["f1", "f2", "f3"] as FieldId[])("%s with default settings", (fid) => {
  it("shows R0 plus three alternatives, none a duplicate of R0", () => {
    const { duplicates, picked } = pickFor(fid);
    const ids = picked.shown.map((e) => e.rotation_id);
    expect(ids[0]).toBe("R0");
    expect(ids).toHaveLength(4);
    expect(new Set(ids).size).toBe(4);
    for (const id of ids.slice(1)) expect(duplicates.has(id)).toBe(false);
  });
  it("gives every filled card a reason and does not count it as hidden", () => {
    const { picked } = pickFor(fid);
    const hiddenIds = picked.hidden.map((h) => h.entry.rotation_id);
    for (const id of Object.keys(picked.filled) as RotationId[]) {
      expect(picked.shown.some((e) => e.rotation_id === id)).toBe(true);
      expect(hiddenIds).not.toContain(id);
    }
  });
});

it("f2 drops R2 (same rotation as R0) and fills the row with excluded rotations", () => {
  const { duplicates, picked } = pickFor("f2");
  expect(duplicates.has("R2")).toBe(true);
  expect(picked.shown.map((e) => e.rotation_id)).not.toContain("R2");
  expect(Object.keys(picked.filled).length).toBeGreaterThan(0);
});
