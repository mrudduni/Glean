"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import type { Climate, CriterionId, FieldId, Lang, ScenarioId, WaterCap } from "@/lib/types";
import type { Weights } from "@/lib/score";

export type Theme = "light" | "dark";

export interface FieldShiftState {
  field: FieldId;
  cap: WaterCap;
  climate: Climate;
  weights: Weights;
  hay: boolean;
  cotton: boolean;
  forage: boolean;
  lang: Lang;
  theme: Theme;
  scenario: ScenarioId;
  setField: (value: FieldId) => void;
  setCap: (value: WaterCap) => void;
  setClimate: (value: Climate) => void;
  setWeight: (key: CriterionId, value: number) => void;
  setHay: (value: boolean) => void;
  setCotton: (value: boolean) => void;
  setForage: (value: boolean) => void;
  setLang: (value: Lang) => void;
  setTheme: (value: Theme) => void;
  toggleTheme: () => void;
}

const initialWeights: Weights = { water: 3, soil: 3, climate: 3, market: 3, operations: 3 };
const initialState = {
  field: "f1" as FieldId,
  cap: "cap300" as WaterCap,
  climate: "actual" as Climate,
  weights: initialWeights,
  hay: false,
  cotton: false,
  forage: false,
  lang: "en" as Lang,
  theme: "light" as Theme,
};

const StateContext = createContext<FieldShiftState | null>(null);

function readState(search: string, pathname: string) {
  const params = new URLSearchParams(search);
  const pathField = pathname.match(/\/field\/(f1|f2|f3)/)?.[1];
  const queryField = params.get("field");
  const cap = params.get("cap");
  const climate = params.get("climate");
  const lang = params.get("lang");
  let theme: Theme = "light";
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem("fieldshift_theme");
    if (saved === "dark" || saved === "light") {
      theme = saved;
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      theme = "dark";
    }
  }
  const queryTheme = params.get("theme");
  if (queryTheme === "dark" || queryTheme === "light") {
    theme = queryTheme;
  }
  const weights = { ...initialWeights };
  (["water", "soil", "climate", "market", "operations"] as CriterionId[]).forEach((key) => {
    const parsed = Number(params.get(`w_${key}`));
    if (Number.isFinite(parsed)) weights[key] = Math.max(0, Math.min(5, parsed));
  });
  return {
    field: (pathField || queryField || "f1") as FieldId,
    cap: (["dryland", "cap150", "cap300", "cap450"].includes(cap || "") ? cap : "cap300") as WaterCap,
    climate: (climate === "hotdry" ? "hotdry" : "actual") as Climate,
    weights,
    hay: params.get("hay") === "1",
    cotton: params.get("cotton") === "1",
    forage: params.get("forage") === "1",
    lang: (lang === "es" ? "es" : "en") as Lang,
    theme,
  };
}

function writeState(values: typeof initialState) {
  if (typeof window === "undefined") return;
  const params = new URLSearchParams(window.location.search);
  params.set("field", values.field);
  params.set("cap", values.cap);
  params.set("climate", values.climate);
  params.set("lang", values.lang);
  params.set("theme", values.theme);
  (Object.keys(values.weights) as CriterionId[]).forEach((key) => params.set(`w_${key}`, String(values.weights[key])));
  params.set("hay", values.hay ? "1" : "0");
  params.set("cotton", values.cotton ? "1" : "0");
  params.set("forage", values.forage ? "1" : "0");
  window.history.replaceState(window.history.state, "", `${window.location.pathname}?${params.toString()}`);
}

export function AppProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [values, setValues] = useState(initialState);

  useEffect(() => {
    const initial = readState(window.location.search, window.location.pathname);
    setValues(initial);
    document.documentElement.setAttribute("data-theme", initial.theme);
    document.documentElement.classList.toggle("dark", initial.theme === "dark");
    const onPopState = () => {
      const state = readState(window.location.search, window.location.pathname);
      setValues(state);
      document.documentElement.setAttribute("data-theme", state.theme);
      document.documentElement.classList.toggle("dark", state.theme === "dark");
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", values.theme);
      document.documentElement.classList.toggle("dark", values.theme === "dark");
      localStorage.setItem("fieldshift_theme", values.theme);
    }
  }, [values.theme]);

  useEffect(() => {
    setValues((current) => {
      const pathField = pathname.match(/\/field\/(f1|f2|f3)/)?.[1];
      if (!pathField || pathField === current.field) return current;
      const next = { ...current, field: pathField as FieldId };
      writeState(next);
      return next;
    });
  }, [pathname]);

  const update = useCallback((patch: Partial<typeof initialState>) => {
    setValues((current) => {
      const next = { ...current, ...patch };
      writeState(next);
      return next;
    });
  }, []);

  const setTheme = useCallback((theme: Theme) => {
    update({ theme });
  }, [update]);

  const toggleTheme = useCallback(() => {
    setValues((current) => {
      const nextTheme: Theme = current.theme === "dark" ? "light" : "dark";
      const next = { ...current, theme: nextTheme };
      writeState(next);
      return next;
    });
  }, []);

  const state = useMemo<FieldShiftState>(() => ({
    ...values,
    scenario: `${values.cap}|${values.climate}` as ScenarioId,
    setField: (value) => update({ field: value }),
    setCap: (value) => update({ cap: value }),
    setClimate: (value) => update({ climate: value }),
    setWeight: (key, value) => update({ weights: { ...values.weights, [key]: Math.max(0, Math.min(5, value)) } }),
    setHay: (value) => update({ hay: value }),
    setCotton: (value) => update({ cotton: value }),
    setForage: (value) => update({ forage: value }),
    setLang: (value) => update({ lang: value }),
    setTheme,
    toggleTheme,
  }), [setTheme, toggleTheme, update, values]);

  return <StateContext.Provider value={state}>{children}</StateContext.Provider>;
}

export function useFieldShift(): FieldShiftState {
  const state = useContext(StateContext);
  if (!state) throw new Error("useFieldShift must be used inside AppProvider.");
  return state;
}
