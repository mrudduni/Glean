"use client";

import { AlertCircle, CloudLightning, Snowflake, Sun, Wind } from "lucide-react";
import type { CalendarFile, CopyFile, Crop, Field, Lang, Rotation, StrategyEntry } from "@/lib/types";
import { fill, t } from "@/lib/i18n";

const months = {
  en: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  es: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
};

const riskIcon = {
  heat: Sun,
  frost: Snowflake,
  dry: AlertCircle,
  storm: CloudLightning,
  wind: Wind,
};

export function FieldCalendar({
  calendar,
  shown,
  rotations,
  crops,
  field,
  copy,
  lang,
}: {
  calendar: CalendarFile;
  shown: StrategyEntry[];
  rotations: Rotation[];
  crops: Crop[];
  field: Field;
  copy: CopyFile["strings"];
  lang: Lang;
}) {
  const cropMap = new Map(crops.map((crop) => [crop.id, crop]));
  const rotationMap = new Map(rotations.map((rotation) => [rotation.id, rotation]));
  return (
    <section className="workspace-section calendar-section" id="calendar">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> PLAN ACROSS SEASONS</div>
          <h2>{t("calendar.title", copy, lang)}</h2>
          <p>{t("calendar.subtitle", copy, lang)}</p>
        </div>
        <span className="section-index">02 / 06</span>
      </div>

      <div className="climate-risk-strip">
        <div className="climate-strip-title">
          <span>{lang === "es" ? "RIESGO CLIMÁTICO MENSUAL" : "MONTHLY CLIMATE RISK"}</span>
          <small>{lang === "es" ? "Probabilidad histórica" : "Historical risk probability"}</small>
        </div>
        <div className="climate-months">
          {calendar.climate_risk.map((risk, index) => (
            <div className="climate-month" key={risk.month}>
              <span>{months[lang][index]}</span>
              <i className="risk-meter heat-meter" style={{ "--meter-value": `${risk.p_heat * 100}%` } as React.CSSProperties} title={`${t("calendar.heat", copy, lang)}: ${Math.round(risk.p_heat * 10)} of 10`} />
              <i className="risk-meter dry-meter" style={{ "--meter-value": `${risk.p_dry_spell * 100}%` } as React.CSSProperties} title={`${t("calendar.dry", copy, lang)}: ${Math.round(risk.p_dry_spell * 10)} of 10`} />
              <span className="risk-counts">{risk.storm_days}·{risk.windy_days}</span>
            </div>
          ))}
        </div>
        <div className="risk-strip-legend">
          <span><i className="legend-risk heat" />{t("calendar.heat", copy, lang)}</span>
          <span><i className="legend-risk dry" />{t("calendar.dry", copy, lang)}</span>
          <span>{t("calendar.storm", copy, lang)} · {t("calendar.wind", copy, lang)}</span>
        </div>
      </div>

      <div className="calendar-scroll">
        <div className="calendar-blocks">
          {shown.map((entry) => {
            const rotation = rotationMap.get(entry.id);
            if (!rotation) return null;
            const steps = entry.id === "R0"
              ? (field.current_crops || rotation.steps.map((step) => step.crop_id)).map((cropId, index) => ({
                  crop_id: cropId,
                  months: cropId === "wheat" ? [3, 4, 5, 6, 7] : [4, 5, 6, 7, 8, 9],
                  stage: { en: cropId === "cover" ? "Overwinter cover" : "Growing season", es: cropId === "cover" ? "Cobertura de invierno" : "Temporada de crecimiento" },
                  year_index: index,
                }))
              : rotation.steps.map((step, index) => ({ ...step, year_index: index }));
            return (
              <article className="calendar-block" key={entry.id}>
                <header className="calendar-block-heading">
                  <span className="rotation-id">{entry.id}</span>
                  <span>{rotation.name[lang] || rotation.name.en}</span>
                  {entry.id === "R0" && <small>{lang === "es" ? "ACTUAL" : "CURRENT"}</small>}
                </header>
                <div className="calendar-month-head">
                  <span>{lang === "es" ? "AÑO" : "YEAR"}</span>
                  {months[lang].map((month) => <span key={month}>{month}</span>)}
                </div>
                {steps.map((step) => {
                  const crop = cropMap.get(step.crop_id);
                  return (
                    <div className="calendar-row" key={`${entry.id}-${step.year_index}`}>
                      <span className="calendar-year">{String(step.year_index + 1).padStart(2, "0")}</span>
                      {months[lang].map((month, monthIndex) => {
                        const monthNumber = monthIndex + 1;
                        const active = step.months.includes(monthNumber);
                        const risk = calendar.climate_risk[monthIndex];
                        const flags = [
                          risk.p_heat >= 0.4 ? "heat" : null,
                          risk.p_frost >= 0.2 ? "frost" : null,
                          risk.p_dry_spell >= 0.24 ? "dry" : null,
                          risk.storm_days >= 4 ? "storm" : null,
                          risk.windy_days >= 8 ? "wind" : null,
                        ].filter((flag): flag is keyof typeof riskIcon => Boolean(flag));
                        const riskText = fill(copy["calendar.risk_tooltip"], {
                          risk: t("calendar.heat", copy, lang),
                          count: Math.round(risk.p_heat * 10),
                          month,
                        }, lang);
                        const title = `${crop?.name[lang] || crop?.name.en || t("calendar.crop", copy, lang)} · ${step.stage[lang] || step.stage.en} · ${riskText}`;
                        return (
                          <span
                            className={`calendar-cell ${active ? "occupied" : "bare"}`}
                            key={month}
                            title={title}
                            style={active && crop ? { "--cell-color": crop.color } as React.CSSProperties : undefined}
                            aria-label={title}
                          >
                            {active && <span className="cell-crop">{crop?.name[lang]?.slice(0, 2) || crop?.id.slice(0, 2)}</span>}
                            <span className="cell-flags" aria-hidden="true">
                              {flags.slice(0, 2).map((flag) => {
                                const Icon = riskIcon[flag];
                                return <Icon key={flag} size={11} />;
                              })}
                            </span>
                          </span>
                        );
                      })}
                    </div>
                  );
                })}
              </article>
            );
          })}
        </div>
      </div>
      <div className="calendar-legend">
        <span><i className="legend-crop" style={{ "--cell-color": "#e9a23b" } as React.CSSProperties} />{t("calendar.crop_period", copy, lang)}</span>
        <span><i className="legend-crop bare-legend" />{t("calendar.fallow_period", copy, lang)}</span>
        <span><Sun size={15} /> Heat</span><span><Snowflake size={15} /> Frost</span><span><AlertCircle size={15} /> Dry</span>
      </div>
    </section>
  );
}
