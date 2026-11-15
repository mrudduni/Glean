"use client";

import { ChevronDown } from "lucide-react";
import { useGlean } from "@/lib/state";
import { CAP_IDS } from "@/lib/schemas";
import type { SliderId } from "@/lib/score";
import type { TFunction } from "@/lib/i18n";

const SLIDERS: SliderId[] = ["save_water", "income", "steady_income", "soil_health", "erosion"];

/**
 * Priorities and limits, shown as a sticky rail beside the strategy cards (wireframe s4)
 * so every change visibly re-ranks the cards next to it. On phones it collapses above the cards.
 */
export function PrioritiesPanel({ t, irrigated = true }: { t: TFunction; irrigated?: boolean }) {
  const state = useGlean();
  return (
    <details className="priority-rail" open aria-labelledby="priorities-heading">
      <summary>
        <h3 id="priorities-heading">{t("priorities.title")}</h3>
        <ChevronDown className="priority-rail-chevron" size={18} aria-hidden="true" />
      </summary>
      <div className="priority-rail-body">
        <p className="priority-hint">{t("priorities.rail_hint", "Move a slider and the cards re-rank instantly.")}</p>

        <div className="priority-sliders">
          {SLIDERS.map((id) => {
            const label = t(`priorities.${id}`);
            const value = state.sliders[id];
            return (
              <label className="priority-slider" key={id}>
                <span className="priority-name">{label}</span>
                <output className="slider-value" aria-hidden="true">{value}</output>
                <input
                  type="range" min={0} max={5} step={1}
                  value={value}
                  aria-valuetext={`${value} / 5`}
                  onChange={(event) => state.setSlider(id, Number(event.currentTarget.value))}
                />
              </label>
            );
          })}
        </div>

        <fieldset className="control-group">
          <legend className="control-label">{t("constraints.water_cap")}</legend>
          <div className="segmented-control stacked">
            {CAP_IDS.map((cap) => (
              <button type="button" key={cap} aria-pressed={state.cap === cap} disabled={!irrigated && cap !== "dryland"} onClick={() => state.setCap(cap)}>
                {t(`constraints.cap.${cap}`)}
              </button>
            ))}
          </div>
          {!irrigated && <p className="control-note">{t("constraints.no_irrigation_note", "This field has no irrigation, so only dryland options apply.")}</p>}
        </fieldset>

        <fieldset className="control-group">
          <legend className="control-label">{t("climate.title")}</legend>
          <div className="segmented-control stacked">
            <button type="button" aria-pressed={state.climate === "actual"} onClick={() => state.setClimate("actual")}>{t("climate.actual")}</button>
            <button type="button" aria-pressed={state.climate === "hotdry"} onClick={() => state.setClimate("hotdry")}>{t("climate.hotdry")}</button>
          </div>
        </fieldset>

        <fieldset className="control-group equipment-options">
          <legend className="control-label">{t("constraints.title")}</legend>
          <Toggle label={t("constraints.hay_equipment")} value={state.hay} onChange={state.setHay} />
          <Toggle label={t("constraints.cotton_equipment")} value={state.cotton} onChange={state.setCotton} />
          <Toggle label={t("constraints.forage_buyer")} value={state.forage} onChange={state.setForage} />
        </fieldset>
      </div>
    </details>
  );
}

function Toggle({ label, value, onChange }: { label: string; value: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="toggle-row">
      <span>{label}</span>
      <input type="checkbox" role="switch" checked={value} onChange={(event) => onChange(event.currentTarget.checked)} />
      <span className="switch-track" aria-hidden="true"><i /></span>
    </label>
  );
}
