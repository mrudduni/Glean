"use client";

// App state, mirrored in URL search params so a view can be shared (handover §5).
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import type { CapId, ClimateId, FieldId, Lang, ScenarioKey } from "@/lib/types";
import { CAP_IDS } from "@/lib/schemas";
import { DEFAULT_SLIDERS, SLIDER_IDS, type SliderId, type Sliders } from "@/lib/score";

export type Theme = "light" | "dark";

interface Values {
  field: FieldId;
  cap: CapId;
  climate: ClimateId;
  sliders: Sliders;
  hay: boolean;
  cotton: boolean;
  forage: boolean;
  lang: Lang;
  theme: Theme;
}

export interface FieldShiftState extends Values {
  scenario: ScenarioKey;
  setField: (value: FieldId) => void;
  setCap: (value: CapId) => void;
  setClimate: (value: ClimateId) => void;
  setSlider: (key: SliderId, value: number) => void;
  setHay: (value: boolean) => void;
  setCotton: (value: boolean) => void;
  setForage: (value: boolean) => void;
  setLang: (value: Lang) => void;
  setTheme: (value: Theme) => void;
}

const initial: Values = {
  field: "f1", cap: "cap300", climate: "actual", sliders: DEFAULT_SLIDERS,
  hay: false, cotton: false, forage: false, lang: "en", theme: "light",
};

const StateContext = createContext<FieldShiftState | null>(null);

function preferredTheme(params: URLSearchParams): Theme {
  const query = params.get("theme");
  if (query === "dark" || query === "light") return query;
  try {
    const saved = localStorage.getItem("fieldshift_theme");
    if (saved === "dark" || saved === "light") return saved;
  } catch {
    // storage blocked: fall through to the system preference
  }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function readState(): Values {
  const params = new URLSearchParams(window.location.search);
  const pathField = window.location.pathname.match(/\/field\/(f1|f2|f3)/)?.[1];
  const queryField = params.get("field");
  const cap = params.get("cap") as CapId | null;
  const sliders = { ...DEFAULT_SLIDERS };
  for (const key of SLIDER_IDS) {
    const raw = params.get(`w_${key}`);
    const parsed = raw === null ? NaN : Number(raw);
    if (Number.isFinite(parsed)) sliders[key] = Math.max(0, Math.min(5, Math.round(parsed)));
  }
  return {
    field: (pathField || (["f1", "f2", "f3"].includes(queryField ?? "") ? queryField : "f1")) as FieldId,
    cap: cap && CAP_IDS.includes(cap) ? cap : "cap300",
    climate: params.get("climate") === "hotdry" ? "hotdry" : "actual",
    sliders,
    hay: params.get("hay") === "1",
    cotton: params.get("cotton") === "1",
    forage: params.get("forage") === "1",
    lang: params.get("lang") === "es" ? "es" : "en",
    theme: preferredTheme(params),
  };
}

function writeState(values: Values) {
  const params = new URLSearchParams(window.location.search);
  params.set("field", values.field);
  params.set("cap", values.cap);
  params.set("climate", values.climate);
  params.set("lang", values.lang);
  for (const key of SLIDER_IDS) params.set(`w_${key}`, String(values.sliders[key]));
  params.set("hay", values.hay ? "1" : "0");
  params.set("cotton", values.cotton ? "1" : "0");
  params.set("forage", values.forage ? "1" : "0");
  params.delete("theme");
  window.history.replaceState(window.history.state, "", `${window.location.pathname}?${params.toString()}`);
}

function applyTheme(theme: Theme) {
  document.documentElement.setAttribute("data-theme", theme);
  document.documentElement.classList.toggle("dark", theme === "dark");
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [values, setValues] = useState<Values>(initial);

  useEffect(() => {
    setValues(readState());
    const onPopState = () => setValues(readState());
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    applyTheme(values.theme);
    try {
      localStorage.setItem("fieldshift_theme", values.theme);
    } catch {
      // ignore blocked storage
    }
  }, [values.theme]);

  useEffect(() => {
    document.documentElement.lang = values.lang;
  }, [values.lang]);

  useEffect(() => {
    const pathField = pathname.match(/\/field\/(f1|f2|f3)/)?.[1] as FieldId | undefined;
    setValues((current) => {
      if (!pathField || pathField === current.field) return current;
      const next = { ...current, field: pathField };
      writeState(next);
      return next;
    });
  }, [pathname]);

  const update = useCallback((patch: Partial<Values>) => {
    setValues((current) => {
      const next = { ...current, ...patch };
      writeState(next);
      return next;
    });
  }, []);

  const state = useMemo<FieldShiftState>(() => ({
    ...values,
    scenario: `${values.cap}|${values.climate}`,
    setField: (field) => update({ field }),
    setCap: (cap) => update({ cap }),
    setClimate: (climate) => update({ climate }),
    setSlider: (key, value) => update({ sliders: { ...values.sliders, [key]: Math.max(0, Math.min(5, value)) } }),
    setHay: (hay) => update({ hay }),
    setCotton: (cotton) => update({ cotton }),
    setForage: (forage) => update({ forage }),
    setLang: (lang) => update({ lang }),
    setTheme: (theme) => update({ theme }),
  }), [update, values]);

  return <StateContext.Provider value={state}>{children}</StateContext.Provider>;
}

export function useFieldShift(): FieldShiftState {
  const state = useContext(StateContext);
  if (!state) throw new Error("useFieldShift must be used inside AppProvider.");
  return state;
}
