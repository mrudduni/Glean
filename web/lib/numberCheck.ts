import type { AssistantNumber } from "@/lib/types";

export interface Fact {
  id: string;
  text: string;
  source_ids: string[];
}

const numericToken = /(?:[$€£]\s?\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s?(?:%|mm|in|ac|ha|days?|years?)?\b)/g;

export function checkNumbers(answer: string, facts: Fact[]): AssistantNumber[] {
  const factText = facts.map((fact) => fact.text).join(" ").toLowerCase();
  const result: AssistantNumber[] = [];
  for (const match of answer.matchAll(numericToken)) {
    const value = match[0].trim();
    const normalized = value.replace(/[$€£,\s]/g, "").toLowerCase();
    const verified = normalized.length > 0 && factText.replace(/[$€£,\s]/g, "").includes(normalized);
    const fact = verified ? facts.find((item) =>
      item.text.toLowerCase().replace(/[$€£,\s]/g, "").includes(normalized)) : undefined;
    result.push({
      value,
      verified: Boolean(fact),
      ...(fact ? { fact_id: fact.id, source_ids: fact.source_ids } : {}),
    });
  }
  return result;
}
