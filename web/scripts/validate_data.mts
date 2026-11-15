// Validate every file in public/data against lib/schemas.ts. Run: node scripts/validate_data.mts
import { readFileSync, existsSync } from "node:fs";
import * as s from "../lib/schemas.ts";

const files: [string, { safeParse: (v: unknown) => { success: boolean; error?: { issues: { path: (string | number)[]; message: string }[] } } }][] = [
  ["fields.json", s.fieldsSchema], ["sources.json", s.sourcesSchema], ["crops.json", s.cropsSchema], ["rotations.json", s.rotationsSchema],
  ["assistant/prompt.json", s.promptSchema], ["content/copy.json", s.copySchema], ["content/card_text.json", s.cardTextSchema],
  ["content/glossary.json", s.glossarySchema], ["content/assistant_questions.json", s.assistantQuestionsSchema],
];
const perField: [string, typeof files[number][1]][] = [
  ["summary", s.summarySchema], ["calendar", s.calendarSchema], ["replay", s.replaySchema], ["strategies", s.strategiesSchema],
  ["validation", s.validationSchema], ["water", s.waterSchema], ["observed", s.observedSchema], ["neighbors", s.neighborsSchema],
  ["assistant_context", s.assistantContextSchema], ["assistant_cache", s.assistantCacheSchema],
];
for (const id of ["f1", "f2", "f3"]) for (const [name, schema] of perField) files.push([`field/${id}/${name}.json`, schema]);

let bad = 0;
for (const [path, schema] of files) {
  const full = `public/data/${path}`;
  if (!existsSync(full)) { console.log(`missing ${path}`); continue; }
  const result = schema.safeParse(JSON.parse(readFileSync(full, "utf8")));
  if (result.success) continue;
  bad += 1;
  console.log(`FAIL ${path}`);
  for (const issue of result.error!.issues.slice(0, 6)) console.log(`   ${issue.path.join(".")}: ${issue.message}`);
}
console.log(bad ? `${bad} file(s) fail the contract` : "all files match the contract");
process.exitCode = bad ? 1 : 0;
