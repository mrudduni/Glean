"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, ResponsiveContainer, YAxis } from "recharts";
import type { CopyFile, Field, GlossaryFile, SummaryFile, WaterFile } from "@/lib/types";
import { formatVar, interpolate, textureLabel } from "@/lib/i18n";
import { type UI } from "@/lib/ui";
import { SourceChips } from "@/components/SourceChips";
import { useGlean } from "@/lib/state";

/** SSURGO wind erodibility group → plain words key (1 and 2 blow most easily). */
function windClass(weg: string | null): "high" | "moderate" | "low" | null {
  if (!weg) return null;
  const n = parseInt(weg, 10);
  if (Number.isNaN(n)) return null;
  return n <= 2 ? "high" : n <= 4 ? "moderate" : "low";
}

/** Read one CSS colour token so the small charts follow the light/dark swap. */
function useToken(name: string, fallback: string) {
  const { theme } = useGlean();
  const [value, setValue] = useState(fallback);
  useEffect(() => {
    setValue(getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback);
  }, [name, fallback, theme]);
  return value;
}

export function OverviewPanel({
  field, summary, water, glossary, ui,
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
  const wind = windClass(soil.weg);
  const windTerm = glossary?.terms.find((term) => term.id === "wind_erosion");
  const nearestWell = water?.wells.slice().sort((a, b) => a.distance_km - b.distance_km)[0];
  const lineColour = useToken("--color-accent", "#1B5E8C");
  const locale = lang === "es" ? "es-ES" : "en-US";
  const one = (v: number) => `${v < 0 ? "−" : ""}${Math.abs(v).toLocaleString(locale, { maximumFractionDigits: 1, minimumFractionDigits: 1 })}`;
  const signed = (v: number) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toLocaleString(locale, { maximumFractionDigits: 0 })}`;

  const grace = water?.grace.series.map((point) => ({ x: point.month, v: point.tws_anom_cm })) ?? [];
  const well = nearestWell?.series.map((point) => ({ x: point.date, v: point.depth_to_water_m })) ?? [];
  const wellsTrend = summary.water.wells_trend_m_per_yr;

  const climateRows = [
    { label: t("overview.frost_free", "Frost-free days"), a: normal.frost_free_days, b: recent.frost_free_days, fmt: (v: number) => formatVar("days", v, lang) },
    { label: t("overview.hot_days", "Days at or above 35 °C"), a: normal.days_tmax_ge_35, b: recent.days_tmax_ge_35, fmt: (v: number) => formatVar("days", v, lang) },
    { label: t("overview.precip", "Rain per year"), a: normal.precip_mm_yr, b: recent.precip_mm_yr, fmt: (v: number) => `${Math.round(v).toLocaleString(locale)} mm`, unit: "mm" },
  ];

  return (
    <section className="workspace-section" id="overview" aria-labelledby="overview-heading">
      <div className="section-title-row">
        <h2 id="overview-heading">{t("nav.overview")}</h2>
      </div>

      <div className="overview-grid">
        <article className="overview-item">
          <h3>{t("overview.soil")}</h3>
          <p className="overview-lead">{textureLabel(t, soil.texture, lang)}</p>
          <p className="micro-note">{soil.map_unit_name}</p>
          <dl className="overview-facts">
            <div><dt>{t("overview.water_storage", "Water storage, top metre")}</dt><dd>{formatVar("aws_mm", soil.aws_0_100_mm, lang)}</dd></div>
            <div><dt>{t("overview.organic_matter", "Organic matter")}</dt><dd>{formatVar("om_pct", soil.om_pct, lang)}</dd></div>
            {wind && <div><dt>{t("overview.wind_erodibility", "Wind erodibility")}</dt><dd>{t(`overview.wind.${wind}`, { high: "Blows easily", moderate: "Moderate", low: "Low" }[wind])}</dd></div>}
          </dl>
          {windTerm && <p className="micro-note">{windTerm.short[lang] || windTerm.short.en}</p>}
          <SourceChips tags={["SSURGO"]} sources={ui.sources} />
        </article>

        <article className="overview-item">
          <h3>{t("overview.climate_shift")}</h3>
          <table className="climate-table">
            <thead>
              <tr><th scope="col"><span className="sr-only">{t("overview.measure", "Measure")}</span></th><th scope="col">{summary.climate.normal_period}</th><th scope="col">{summary.climate.recent_period}</th><th scope="col">{t("overview.change", "Change")}</th></tr>
            </thead>
            <tbody>
              {climateRows.map((row) => (
                <tr key={row.label}>
                  <th scope="row">{row.label}</th>
                  <td>{row.fmt(row.a)}</td>
                  <td>{row.fmt(row.b)}</td>
                  <td className="climate-change">{signed(row.b - row.a)}{row.unit ? ` ${row.unit}` : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <SourceChips tags={summary.climate.sources} sources={ui.sources} />
        </article>

        <article className="overview-item">
          <h3>{t("overview.water_outlook")}</h3>
          <p className={`overview-lead water-status outlook-${summary.water.outlook}`}>{t(`overview.outlook.${summary.water.outlook}`)}</p>

          {grace.length > 1 && (
            <figure className="spark">
              <figcaption>{t("overview.grace_chart", "GRACE water storage anomaly, cm")}</figcaption>
              <div className="spark-plot" role="img" aria-label={`${t("overview.grace_chart", "GRACE water storage anomaly, cm")}: ${grace[0].x} ${one(grace[0].v)}, ${grace[grace.length - 1].x} ${one(grace[grace.length - 1].v)}`}>
                <ResponsiveContainer width="100%" height={56}>
                  <AreaChart data={grace} margin={{ top: 4, right: 0, bottom: 4, left: 0 }}>
                    <YAxis hide domain={["dataMin", "dataMax"]} />
                    <Area type="linear" dataKey="v" stroke={lineColour} fill={lineColour} fillOpacity={0.12} strokeWidth={1.5} isAnimationActive={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="spark-ends"><span>{grace[0].x.slice(0, 4)}: {one(grace[0].v)} cm</span><span>{grace[grace.length - 1].x.slice(0, 4)}: {one(grace[grace.length - 1].v)} cm</span></div>
            </figure>
          )}

          {well.length > 1 && nearestWell && (
            <figure className="spark">
              <figcaption>{interpolate(t("overview.well_chart", "Depth to water at the nearest well ({km} km), metres below ground"), { km: one(nearestWell.distance_km) })}</figcaption>
              <div className="spark-plot" role="img" aria-label={`${well[0].x.slice(0, 4)}: ${one(well[0].v)} m, ${well[well.length - 1].x.slice(0, 4)}: ${one(well[well.length - 1].v)} m`} title={nearestWell.name}>
                <ResponsiveContainer width="100%" height={56}>
                  <AreaChart data={well} margin={{ top: 4, right: 0, bottom: 4, left: 0 }}>
                    {/* Deeper water plots lower, the way a well reads. */}
                    <YAxis hide reversed domain={[0, "dataMax"]} />
                    <Area type="linear" dataKey="v" stroke={lineColour} fill={lineColour} fillOpacity={0.12} strokeWidth={1.5} baseValue={0} isAnimationActive={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="spark-ends"><span>{well[0].x.slice(0, 4)}: {one(well[0].v)} m</span><span>{well[well.length - 1].x.slice(0, 4)}: {one(well[well.length - 1].v)} m</span></div>
            </figure>
          )}

          <dl className="overview-facts">
            <div><dt>{t("overview.grace_trend", "GRACE trend")}</dt><dd>{formatVar("cm_per_yr", summary.water.grace_trend_cm_per_yr, lang)}</dd></div>
            {wellsTrend !== null && (
              <div>
                <dt>{t("overview.wells_trend", "Depth to water, nearby wells")}</dt>
                <dd>
                  <span className="nowrap">{formatVar("m_per_yr", Math.abs(wellsTrend), lang)}</span>{" "}
                  <span className="dd-note">{wellsTrend > 0 ? t("overview.wells_deeper", "deeper each year") : t("overview.wells_shallower", "shallower each year")}</span>
                </dd>
              </div>
            )}
          </dl>
          <SourceChips tags={["GRACE", "USGS"]} sources={ui.sources} />
        </article>
      </div>
    </section>
  );
}
