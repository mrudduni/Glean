import { describe, expect, it } from "vitest";
import { checkNumbers } from "../lib/numberCheck";

describe("assistant number checks", () => {
  const facts = [
    { id: "soil-storage", text: "Illustrative available water storage is 178 mm.", source_ids: ["SOIL"] },
    { id: "weather-sample", text: "The mock precipitation sample is 486 mm.", source_ids: ["GPM"] },
  ];

  it("marks numbers found in supplied facts as verified", () => {
    expect(checkNumbers("The demo value is 178 mm.", facts)).toEqual([
      { value: "178 mm", verified: true, fact_id: "soil-storage", source_ids: ["SOIL"] },
    ]);
  });

  it("marks unsourced values as unverified", () => {
    expect(checkNumbers("The estimate is 310 mm.", facts)).toEqual([
      { value: "310 mm", verified: false },
    ]);
  });

  it("does not report text without numeric claims", () => {
    expect(checkNumbers("Check this with a local agronomist.", facts)).toEqual([]);
  });
});
