"use client";

import { SlidersHorizontal, Droplets, Wheat, Tractor, Coins, SunMedium } from "lucide-react";
import { useFieldShift } from "@/lib/state";
import { t } from "@/lib/i18n";
import type { CriterionId, CopyFile } from "@/lib/types";

const priorities: { id: CriterionId; icon: typeof Droplets; copyKey: string }[] = [
  { id: "water", icon: Droplets, copyKey: "priority.water" },
  { id: "soil", icon: Wheat, copyKey: "priority.soil" },
  { id: "climate", icon: SunMedium, copyKey: "priority.climate" },
  { id: "market", icon: Coins, copyKey: "priority.market" },
  { id: "operations", icon: Tractor, copyKey: "priority.operations" },
];

const caps = [
  { value: "dryland", key: "priority.cap.dryland" },
  { value: "cap150", key: "priority.cap.150" },
  { value: "cap300", key: "priority.cap.300" },
  { value: "cap450", key: "priority.cap.450" },
] as const;

export function PrioritiesPanel({ copy }: { copy: CopyFile["strings"] }) {
  const { lang, weights, setWeight, cap, setCap, climate, setClimate, hay, cotton, forage, setHay, setCotton, setForage } = useFieldShift();
  return (
    <section className="workspace-section priorities-section" id="priorities">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> MAKE IT YOURS</div>
          <h2>{t("priority.title", copy, lang)}</h2>
          <p>{t("priority.subtitle", copy, lang)}</p>
        </div>
        <span className="section-index">03 / 06</span>
      </div>
      <div className="priority-panel">
        <div className="priority-sliders">
          {priorities.map(({ id, icon: Icon, copyKey }) => (
            <label className="priority-slider" key={id}>
              <span className="priority-icon"><Icon size={18} /></span>
              <span className="priority-name">{t(copyKey, copy, lang)}</span>
              <input
                type="range"
                min="0"
                max="5"
                step="1"
                value={weights[id]}
                aria-label={t(copyKey, copy, lang)}
                onChange={(event) => setWeight(id, Number(event.currentTarget.value))}
              />
              <span className="slider-value">{weights[id]}<small>/5</small></span>
            </label>
          ))}
        </div>
        <div className="priority-controls">
          <div className="control-group">
            <span className="control-label">{t("priority.cap", copy, lang)}</span>
            <div className="segmented-control" role="group" aria-label={t("priority.cap", copy, lang)}>
              {caps.map((item) => (
                <button type="button" key={item.value} aria-pressed={cap === item.value} onClick={() => setCap(item.value)}>
                  {t(item.key, copy, lang)}
                </button>
              ))}
            </div>
          </div>
          <div className="control-group climate-control">
            <span className="control-label">{t("priority.climate_toggle", copy, lang)}</span>
            <div className="segmented-control" role="group" aria-label={t("priority.climate_toggle", copy, lang)}>
              <button type="button" aria-pressed={climate === "actual"} onClick={() => setClimate("actual")}>{t("priority.actual", copy, lang)}</button>
              <button type="button" aria-pressed={climate === "hotdry"} onClick={() => setClimate("hotdry")}>{t("priority.hotdry", copy, lang)}</button>
            </div>
          </div>
          <div className="equipment-options">
            <Toggle label={t("priority.hay", copy, lang)} value={hay} onChange={setHay} />
            <Toggle label={t("priority.cotton", copy, lang)} value={cotton} onChange={setCotton} />
            <Toggle label={t("priority.forage", copy, lang)} value={forage} onChange={setForage} />
          </div>
          <div className="priority-footnote"><SlidersHorizontal size={16} /> {t("priority.share_note", copy, lang)}</div>
        </div>
      </div>
    </section>
  );
}

function Toggle({ label, value, onChange }: { label: string; value: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="toggle-row">
      <span>{label}</span>
      <input type="checkbox" checked={value} onChange={(event) => onChange(event.currentTarget.checked)} />
      <span className="switch-track" aria-hidden="true"><i /></span>
    </label>
  );
}
