"use client";

import { Coins, Droplets, Scale, Sprout, Wind } from "lucide-react";
import { useGlean } from "@/lib/state";
import { CAP_IDS } from "@/lib/schemas";
import type { SliderId } from "@/lib/score";
import type { TFunction } from "@/lib/i18n";

const sliders: { id: SliderId; icon: typeof Droplets }[] = [
  { id: "save_water", icon: Droplets },
  { id: "income", icon: Coins },
  { id: "steady_income", icon: Scale },
  { id: "soil_health", icon: Sprout },
  { id: "erosion", icon: Wind },
];

export function PrioritiesPanel({ t }: { t: TFunction }) {
  const state = useGlean();
  return (
    <section className="workspace-section priorities-section" id="priorities" aria-labelledby="priorities-heading">
      <div className="section-title-row">
        <div>
          <h2 id="priorities-heading">{t("priorities.title")}</h2>
          <p>{t("priorities.subtitle", "Move the sliders to say what matters most. The cards below re-rank instantly.")}</p>
        </div>
      </div>
      <div className="priority-panel">
        <div className="priority-sliders">
          {sliders.map(({ id, icon: Icon }) => {
            const label = t(`priorities.${id}`);
            return (
              <label className="priority-slider" key={id}>
                <span className="priority-icon"><Icon size={18} aria-hidden="true" /></span>
                <span className="priority-name">{label}</span>
                <input
                  type="range" min={0} max={5} step={1}
                  value={state.sliders[id]}
                  aria-valuetext={`${state.sliders[id]} / 5`}
                  onChange={(event) => state.setSlider(id, Number(event.currentTarget.value))}
                />
                <span className="slider-value" aria-hidden="true">{state.sliders[id]}<small>/5</small></span>
              </label>
            );
          })}
        </div>
        <div className="priority-controls">
          <fieldset className="control-group">
            <legend className="control-label">{t("constraints.water_cap")}</legend>
            <div className="segmented-control" role="group">
              {CAP_IDS.map((cap) => (
                <button type="button" key={cap} aria-pressed={state.cap === cap} onClick={() => state.setCap(cap)}>
                  {t(`constraints.cap.${cap}`)}
                </button>
              ))}
            </div>
          </fieldset>
          <fieldset className="control-group climate-control">
            <legend className="control-label">{t("climate.title")}</legend>
            <div className="segmented-control" role="group">
              <button type="button" aria-pressed={state.climate === "actual"} onClick={() => state.setClimate("actual")}>{t("climate.actual")}</button>
              <button type="button" aria-pressed={state.climate === "hotdry"} onClick={() => state.setClimate("hotdry")}>{t("climate.hotdry")}</button>
            </div>
          </fieldset>
          <fieldset className="equipment-options">
            <legend className="control-label">{t("constraints.title")}</legend>
            <Toggle label={t("constraints.hay_equipment")} value={state.hay} onChange={state.setHay} />
            <Toggle label={t("constraints.cotton_equipment")} value={state.cotton} onChange={state.setCotton} />
            <Toggle label={t("constraints.forage_buyer")} value={state.forage} onChange={state.setForage} />
          </fieldset>
        </div>
      </div>
    </section>
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
