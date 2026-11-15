import { describe, expect, it, vi } from "vitest";
import { fill, formatVar, interpolate, makeT, textureLabel, yearsLabel } from "@/lib/i18n";
import type { Lang } from "@/lib/types";

const crops = { sorghum: { en: "Sorghum", es: "Sorgo" }, triticale: { en: "Triticale", es: "" } };
const M = "−";

describe("formatVar (README 7.4)", () => {
  const cases: [string, number, Lang, string][] = [
    ["saved_mm", 310, "en", "310 mm (12.2 in)"],
    ["saved_mm", 310, "es", "310 mm (12,2 pulg.)"],
    ["saved_mm", -50, "en", `${M}50 mm (${M}2.0 in)`],
    ["revenue_usd_ac", 412, "en", "$412/ac"],
    ["diff_usd_ac", -35, "en", `${M}$35/ac`],
    ["revenue_usd_ac", 1250, "en", "$1,250/ac"],
    ["bias_pct", 12, "en", "12%"],
    ["bias_pct", -8.25, "en", `${M}8.3%`],
    ["bare_windy_days", 12.6, "en", "13"],
    ["days", 7, "en", "7"],
    ["cm_per_yr", -1.2, "en", `${M}1.2 cm/yr`],
    ["cm_per_yr", -0.86, "es", `${M}0,9 cm/año`],
    ["m_per_yr", -0.4, "en", `${M}0.4 m/yr (${M}1.3 ft/yr)`],
    ["year", 2012, "en", "2012"],
    ["years_from", 2018, "es", "2018"],
    ["n", 12, "en", "12"],
    ["legume_years", 2, "en", "2"],
    ["r", 0.6, "en", "0.60"],
    ["score", 63.47, "en", "63.5"],
  ];
  it.each(cases)("%s=%s (%s) gives %s", (name, value, lang, expected) => {
    expect(formatVar(name, value, lang)).toBe(expected);
  });
  it("renders _crop vars as crop names, falling back to English", () => {
    expect(formatVar("forage_crop", "sorghum", "es", crops)).toBe("Sorgo");
    expect(formatVar("forage_crop", "triticale", "es", crops)).toBe("Triticale");
  });
  it("passes other strings through", () => {
    expect(formatVar("label", "R2", "en")).toBe("R2");
  });
});

describe("fill", () => {
  it("replaces placeholders and falls back to English when Spanish is empty", () => {
    expect(fill({ en: "Saves {saved_mm} a year.", es: "" }, { saved_mm: 100 }, "es")).toBe("Saves 100 mm (3,9 pulg.) a year.");
  });
  it("renders a missing value as a dash and warns", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    expect(fill({ en: "In {year}: {irrigation_mm}", es: "" }, { year: 2012 }, "en")).toBe("In 2012: —");
    expect(warn).toHaveBeenCalled();
    warn.mockRestore();
  });
});

describe("plural selector {name|one|other}", () => {
  it("picks the singular or plural word for the value, per language", () => {
    const template = { en: "Longest run: {years} {years|year|years}.", es: "Racha más larga: {years} {years|año|años}." };
    expect(fill(template, { years: 1 }, "en")).toBe("Longest run: 1 year.");
    expect(fill(template, { years: 3 }, "en")).toBe("Longest run: 3 years.");
    expect(fill(template, { years: 1 }, "es")).toBe("Racha más larga: 1 año.");
    expect(fill(template, { years: 0 }, "es")).toBe("Racha más larga: 0 años.");
  });
  it("works in interpolate too", () => {
    expect(interpolate("{n} {n|field|fields}", { n: 1 })).toBe("1 field");
    expect(interpolate("{n} {n|field|fields}", { n: 12 })).toBe("12 fields");
  });
});

describe("t", () => {
  const strings = { "a.b": { en: "Hello", es: "Hola" }, "c.d": { en: "Only English", es: "" } };
  it("looks up lang, then en, then fallback, then key", () => {
    expect(makeT(strings, "es")("a.b")).toBe("Hola");
    expect(makeT(strings, "es")("c.d")).toBe("Only English");
    expect(makeT(strings, "en")("x.y", "Fallback")).toBe("Fallback");
    expect(makeT(strings, "en")("x.y")).toBe("x.y");
  });
});

describe("copy before it loads, textures and years", () => {
  it("shows nothing, not the raw key, before copy has loaded", () => {
    expect(makeT({}, "en")("pick.title")).toBe("");
    expect(makeT({}, "en")("pick.title", "Pick a field")).toBe("Pick a field");
    expect(makeT({ a: { en: "A", es: "A" } }, "en")("pick.title")).toBe("pick.title");
  });
  it("translates soil textures: copy key first, then the built-in Spanish name", () => {
    expect(textureLabel(makeT({}, "es"), "fine sand", "es")).toBe("arena fina");
    expect(textureLabel(makeT({}, "en"), "fine sand", "en")).toBe("fine sand");
    const t = makeT({ "soil.texture.silt_loam": { en: "Silt loam", es: "Limo franco" } }, "es");
    expect(textureLabel(t, "silt loam", "es")).toBe("Limo franco");
  });
  it("formats a year span through years.range", () => {
    expect(yearsLabel(makeT({}, "es"), 2018, 2025)).toBe("2018-2025");
  });
});

describe("plain-language layer for content templates", () => {
  const ui = (headline: string) => ({
    lang: "en" as const, t: (_k: string, f?: string) => f ?? "", crops: {}, sources: { _meta: {}, sources: [] },
    cardText: { headline: { heat_days_change: { en: headline, es: "" } } },
  });
  it("rewrites the form-like template while content still has it", async () => {
    const { cardLine } = await import("@/lib/ui");
    const old = "Hot days (35 °C or higher) a year, recent years versus 1991 to 2020, change in days: {days}.";
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    expect(cardLine(ui(old) as any, "headline", "heat_days_change", { days: -3 })).toBe("Recent years have had 3 fewer days at 35 °C or hotter each year than 1991 to 2020.");
  });
  it("leaves content alone once its owner changes the text", async () => {
    const { cardLine } = await import("@/lib/ui");
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    expect(cardLine(ui("Hot days changed by {days}.") as any, "headline", "heat_days_change", { days: -3 })).toBe(`Hot days changed by ${"−"}3.`);
  });
});
