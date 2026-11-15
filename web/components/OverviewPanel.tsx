"use client";

import { ArrowDownRight, ArrowUpRight, Droplets, Leaf, MapPinned, ThermometerSun } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, YAxis } from "recharts";
import type { CopyFile, Field, GlossaryFile, SummaryFile, WaterFile } from "@/lib/types";
import { fill, formatVar } from "@/lib/i18n";
import { cardLine, ROTATION_CLASS_LABEL, type UI } from "@/lib/ui";
import { SourceChips } from "@/components/SourceChips";
import { CropChips } from "@/components/CropChips";
import { theme } from "@/lib/theme";

/** SSURGO wind erodibility group → plain words key (1 and 2 blow most easily). */
function windClass(weg: string | null): "high" | "moderate" | "low" | null {
  if (!weg) return null;
  const n = parseInt(weg, 10);
  if (Number.isNaN(n)) return null;
  return n <= 2 ? "high" : n <= 4 ? "moderate" : "low";
}

export function OverviewPanel({
  field, summary, water, glossary, copy, ui,
}: {
  field: Field;
  summary: SummaryFile;
  water: WaterFile | null;
  glossary: GlossaryFile | null;
  copy: CopyFile["strings"];
  ui: UI;
}) {
  const { t, lang } = ui;
  const soil = field.soil;
  const { normal, recent } = summary.climate;
  const heatDelta = recent.days_tmax_ge_35 - normal.days_tmax_ge_35;
  const grace = water?.grace.series.map((point) => ({ month: point.month, value: point.tws_anom_cm })) ?? [];
  const wind = windClass(soil.weg);
  const windTerm = glossary?.terms.find((term) => term.id === "wind_erosion");
  const [from, to] = summary.current_rotation.years;
  const nearestWell = water?.wells.slice().sort((a, b) => a.distance_km - b.distance_km)[0];

  return (
    <section className="workspace-section" id="overview" aria-labelledby="overview-heading">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> {t("overview.eyebrow", "Field snapshot")}</div>
          <h2 id="overview-heading">{t("nav.overview")}</h2>
        </div>
        <span className="section-index">01 / 06</span>
      </div>

      <div className="overview-grid">
        <article className="overview-card current-rotation-card">
          <div className="card-kicker"><span className="icon-disc"><Leaf size={17} aria-hidden="true" /></span><span>{t("overview.current_rotation")}</span></div>
          <h3>{t(`rotation_class.${summary.current_rotation.rotation_class}`, ROTATION_CLASS_LABEL[summary.current_rotation.rotation_class])}</h3>
          <CropChips steps={summary.current_rotation.steps} ui={ui} />
          <p className="small-note">{fill(copy["overview.detected_from"], { years_from: from, years_to: to }, lang)}</p>
          <SourceChips tags={["CSB"]} sources={ui.sources} />
        </article>

        <article className="overview-card soil-card">
          <div className="card-kicker"><span className="icon-disc sand"><MapPinned size={17} aria-hidden="true" /></span><span>{t("overview.soil")}</span></div>
          <div className="soil-texture">{soil.texture}</div>
          <p className="micro-note">{soil.map_unit_name}</p>
          <div className="soil-metrics">
            <div><small>{t("overview.water_storage", "Water storage, top metre")}</small><strong>{formatVar("aws_mm", soil.aws_0_100_mm, lang)}</strong></div>
            <div><small>{t("overview.organic_matter", "Organic matter")}</small><strong>{formatVar("om_pct", soil.om_pct, lang)}</strong></div>
          </div>
          {wind && (
            <div className="wind-note">
              <span>{t("overview.wind_erodibility", "Wind erodibility")}</span>
              <strong>{t(`overview.wind.${wind}`, { high: "Blows easily", moderate: "Moderate", low: "Low" }[wind])}</strong>
            </div>
          )}
          {windTerm && <p className="micro-note">{windTerm.short[lang] || windTerm.short.en}</p>}
          <SourceChips tags={["SSURGO"]} sources={ui.sources} />
        </article>

        <article className="overview-card climate-card">
          <div className="card-kicker"><span className="icon-disc orange"><ThermometerSun size={17} aria-hidden="true" /></span><span>{t("overview.climate_shift")}</span></div>
          <div className="climate-legend">
            <span><i className="dot normal" />{summary.climate.normal_period}</span>
            <span><i className="dot recent" />{summary.climate.recent_period}</span>
          </div>
          <ClimatePair label={t("overview.frost_free", "Frost-free days")} normal={normal.frost_free_days} recent={recent.frost_free_days} format={(v) => `${formatVar("days", v, lang)} ${t("unit.days", "days")}`} />
          <ClimatePair label={t("overview.hot_days", "Days at or above 35 °C")} normal={normal.days_tmax_ge_35} recent={recent.days_tmax_ge_35} format={(v) => `${formatVar("days", v, lang)} ${t("unit.days", "days")}`} />
          <ClimatePair label={t("overview.precip", "Rain per year")} normal={normal.precip_mm_yr} recent={recent.precip_mm_yr} format={(v) => formatVar("precip_mm", v, lang)} />
          <span className={`climate-delta ${heatDelta >= 0 ? "up" : "down"}`}>
            {heatDelta >= 0 ? <ArrowUpRight size={14} aria-hidden="true" /> : <ArrowDownRight size={14} aria-hidden="true" />}
            {cardLine(ui, "headline", "heat_days_change", { days: heatDelta })}
          </span>
          <SourceChips tags={summary.climate.sources} sources={ui.sources} />
        </article>

        <article className="overview-card water-card">
          <div className="card-kicker"><span className="icon-disc blue"><Droplets size={17} aria-hidden="true" /></span><span>{t("overview.water_outlook")}</span></div>
          <div className={`water-status outlook-${summary.water.outlook}`}><span className="water-status-dot" />{t(`overview.outlook.${summary.water.outlook}`)}</div>
          {grace.length > 0 && (
            <div className="water-chart" aria-label={t("overview.grace_chart", "GRACE water storage anomaly, cm")} role="img">
              <ResponsiveContainer width="100%" height={85}>
                <AreaChart data={grace}>
                  <YAxis hide domain={["dataMin", "dataMax"]} />
                  <Tooltip
                    contentStyle={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, fontSize: 13, color: "var(--ink)" }}
                    formatter={(value) => [`${value} cm`, "GRACE"]}
                    labelFormatter={(_label, payload) => String(payload?.[0]?.payload?.month ?? "")}
                  />
                  <Area type="monotone" dataKey="value" stroke={theme.risk.frost} fill={theme.risk.frost} fillOpacity={0.18} strokeWidth={2} isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
          <dl className="water-facts">
            <div><dt>GRACE</dt><dd>{formatVar("cm_per_yr", summary.water.grace_trend_cm_per_yr, lang)}</dd></div>
            {summary.water.wells_trend_m_per_yr !== null && (
              <div>
                <dt>{t("overview.wells_trend", "Depth to water, nearby wells")}</dt>
                <dd>{formatVar("m_per_yr", summary.water.wells_trend_m_per_yr, lang)}</dd>
              </div>
            )}
            {nearestWell && <div><dt>{t("overview.nearest_well", "Nearest well")}</dt><dd>{nearestWell.name}, {nearestWell.distance_km} km</dd></div>}
          </dl>
          <SourceChips tags={["GRACE", "USGS"]} sources={ui.sources} />
        </article>
      </div>

      <div className="headline-row">
        <div className="headline-title"><span>{t("overview.notes_kicker", "Field notes")}</span><h3>{t("overview.headlines", "What stands out")}</h3></div>
        {summary.headline_facts.map((fact, index) => (
          <article className="headline-fact" key={`${fact.text_id}-${index}`}>
            <span className="headline-number">0{index + 1}</span>
            <p>{cardLine(ui, "headline", fact.text_id, fact.vars)}</p>
            <SourceChips tags={fact.sources} sources={ui.sources} />
          </article>
        ))}
      </div>
    </section>
  );
}

function ClimatePair({ label, normal, recent, format }: { label: string; normal: number; recent: number; format: (v: number) => string }) {
  const max = Math.max(normal, recent, 1);
  return (
    <div className="climate-pair">
      <div className="climate-pair-label"><span>{label}</span><b>{format(recent)}</b></div>
      <div className="climate-track" aria-hidden="true">
        <span className="climate-bar normal" style={{ width: `${(normal / max) * 100}%` }} />
        <span className="climate-bar recent" style={{ width: `${(recent / max) * 100}%` }} />
      </div>
      <div className="climate-values"><span>{format(normal)}</span><span>{format(recent)}</span></div>
    </div>
  );
}
