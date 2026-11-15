"use client";

import { useEffect, useMemo, useState } from "react";
import { CartesianGrid, Line, LineChart, ReferenceArea, ReferenceDot, ResponsiveContainer, Tooltip, XAxis, YAxis, type TooltipProps } from "recharts";
import type { ReplayFile, ReplayYear, RotationId, ScenarioKey } from "@/lib/types";
import { formatVar, loc } from "@/lib/i18n";
import { useGlean } from "@/lib/state";
import { theme } from "@/lib/theme";
import type { UI } from "@/lib/ui";

type Metric = "irrigation" | "revenue" | "stress" | "bare";
const METRICS: Metric[] = ["irrigation", "revenue", "stress", "bare"];
const FIELD: Record<Metric, keyof ReplayYear> = {
  irrigation: "irrigation_mm", revenue: "revenue_usd_ac", stress: "stress_days", bare: "bare_days",
};
/** For revenue the worst years are the lowest; for the others they are the highest. */
const HIGHER_IS_WORSE: Record<Metric, boolean> = { irrigation: true, revenue: false, stress: true, bare: true };
const UNIT_FALLBACK: Record<Metric, string> = {
  irrigation: "Irrigation water, mm per year",
  revenue: "Income before costs, $ per acre",
  stress: "Days of crop water stress per year",
  bare: "Days of bare ground per year",
};

const HEIGHT = 340;
const MARGIN = { top: 28, right: 216, bottom: 8, left: 4 };  // right: room for the end labels
const X_AXIS_H = 30;

/** Rotation colours come from the CSS tokens so the chart follows the same light/dark swap as the cards. */
function useTokenColours(ids: RotationId[], mode: string) {
  const [colours, setColours] = useState<Record<string, string>>({});
  const key = ids.join(",");
  useEffect(() => {
    const css = getComputedStyle(document.documentElement);
    const read = (name: string, fallback: string) => css.getPropertyValue(name).trim() || fallback;
    const next: Record<string, string> = {
      grid: read("--rule", "#e2ded3"), axis: read("--text-3", "#6c736a"), band: read("--color-fg", "#1E2A22"), surface: read("--color-surface", "#fff"),
    };
    for (const id of key.split(",").filter(Boolean)) next[id] = read(`--rot-${id}`, theme.rot[id] ?? "#888");
    setColours(next);
  }, [key, mode]);
  return colours;
}

/** A tick step of 1, 2 or 5 × 10^n that gives about four intervals. */
function niceStep(range: number) {
  const raw = Math.max(range, 1) / 4;
  const mag = 10 ** Math.floor(Math.log10(raw));
  return [1, 2, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? raw;
}

/** Contiguous dry years become one band: 2011 and 2012 read as "2011–12". */
function droughtRanges(years: number[]) {
  const sorted = [...years].sort((a, b) => a - b);
  const out: { from: number; to: number }[] = [];
  for (const year of sorted) {
    const last = out[out.length - 1];
    if (last && year === last.to + 1) last.to = year; else out.push({ from: year, to: year });
  }
  return out;
}

export function ReplayChart({ replay, scenario, order, ui }: { replay: ReplayFile; scenario: ScenarioKey; order: RotationId[]; ui: UI }) {
  const { t, lang } = ui;
  const { theme: mode } = useGlean();
  const [metric, setMetric] = useState<Metric>("irrigation");
  const runs = useMemo(() => replay.scenarios[scenario] ?? {}, [replay, scenario]);
  const ids = useMemo(() => order.filter((id) => runs[id]), [order, runs]);
  const colours = useTokenColours(ids, mode);
  // On a field without irrigation every option uses 0 mm: open on income instead of an empty chart.
  const noIrrigation = useMemo(() => ids.length > 0 && ids.every((id) => (runs[id]?.by_year ?? []).every((item) => !item.irrigation_mm)), [ids, runs]);
  useEffect(() => { if (noIrrigation) setMetric((current) => (current === "irrigation" ? "revenue" : current)); }, [noIrrigation]);
  const key = FIELD[metric];
  const name = (id: RotationId) => loc(ui.cardText.rotations[id]?.name, lang) || id;
  const format = (value: number) => (
    metric === "irrigation" ? formatVar("irrigation_mm", value, lang)
      : metric === "revenue" ? formatVar("revenue_usd_ac", value, lang)
        : `${formatVar("days", value, lang)} ${t("unit.days", "days")}`
  );
  const tick = (value: number) => (metric === "revenue" ? `$${value.toLocaleString(lang === "es" ? "es-ES" : "en-US")}` : value.toLocaleString(lang === "es" ? "es-ES" : "en-US"));

  const data = useMemo(() => {
    const rows: Record<string, number | null>[] = [];
    for (let year = replay.years[0]; year <= replay.years[1]; year += 1) {
      const row: Record<string, number | null> = { year };
      for (const id of ids) {
        const point = runs[id]?.by_year.find((item) => item.year === year);
        row[id] = point ? (point[key] as number) : null;
      }
      rows.push(row);
    }
    return rows;
  }, [ids, key, replay.years, runs]);

  // A series that never leaves zero (a dryland rotation on the irrigation view) is named for what it is.
  const flat = new Set(ids.filter((id) => data.every((row) => !row[id])));
  const lineName = (id: RotationId) => (flat.has(id) && metric === "irrigation" ? `${name(id)} · ${t("replay.no_irrigation", "no irrigation")}` : name(id));
  // Each rotation's worst year on this metric, marked on its line.
  const worstYears = ids.filter((id) => !flat.has(id)).map((id) => {
    const points = data.filter((row) => typeof row[id] === "number") as Record<string, number>[];
    const pick = points.reduce((a, b) => ((HIGHER_IS_WORSE[metric] ? b[id] > a[id] : b[id] < a[id]) ? b : a), points[0]);
    return pick ? { id, year: pick.year, value: pick[id] } : null;
  }).filter((item): item is { id: RotationId; year: number; value: number } => Boolean(item));

  // Honest axis: magnitudes start at zero; the top is a round number just above the data.
  const values = data.flatMap((row) => ids.map((id) => row[id])).filter((v): v is number => typeof v === "number");
  const lo = Math.min(0, ...values);
  const step = niceStep(Math.max(...values, 1) - lo);
  const hi = Math.ceil(Math.max(...values, step) / step) * step;
  const yTicks = Array.from({ length: Math.round((hi - lo) / step) + 1 }, (_, i) => lo + i * step);

  // Direct labels at the end of each line, nudged apart so they never overlap.
  const plotTop = MARGIN.top;
  const plotH = HEIGHT - MARGIN.top - MARGIN.bottom - X_AXIS_H;
  const endLabels = useMemo(() => {
    const last = data[data.length - 1] ?? {};
    const items = ids
      .map((id) => ({ id, value: last[id] }))
      .filter((item): item is { id: RotationId; value: number } => typeof item.value === "number")
      .map((item) => ({ ...item, y: plotTop + (1 - (item.value - lo) / (hi - lo || 1)) * plotH }))
      .sort((a, b) => a.y - b.y);
    for (let i = 1; i < items.length; i += 1) items[i].y = Math.max(items[i].y, items[i - 1].y + 20);
    const overflow = items.length ? items[items.length - 1].y - (plotTop + plotH) : 0;
    if (overflow > 0) for (const item of items) item.y -= overflow;
    return items;
  }, [data, ids, lo, hi, plotH, plotTop]);

  const summaries = ids.map((id) => {
    const series = (runs[id]?.by_year ?? []).map((item) => item[key] as number).sort((a, b) => a - b);
    const worst = HIGHER_IS_WORSE[metric] ? series.slice(-5) : series.slice(0, 5);
    const avg = series.length ? series.reduce((a, b) => a + b, 0) / series.length : 0;
    return { id, avg, worst: worst.length ? worst.reduce((a, b) => a + b, 0) / worst.length : 0, feasible: runs[id]?.feasible ?? false };
  });

  const bands = droughtRanges(replay.drought_years);
  const bandLabel = (band: { from: number; to: number }) => (band.from === band.to ? String(band.from) : `${band.from}–${String(band.to).slice(2)}`);
  const [cap, climate] = scenario.split("|");

  return (
    <section className="workspace-section replay-section" id="replay" aria-labelledby="replay-heading">
      <div className="section-title-row">
        <h2 id="replay-heading">{t("replay.title")}</h2>
        <p>{t("replay.subtitle")}</p>
      </div>

      <div className="replay-panel">
        <div className="replay-toolbar">
          <div className="segmented-control replay-metric-switch" role="group" aria-label={t("replay.metric_label", "Choose what to plot")}>
            {METRICS.map((item) => (
              <button type="button" key={item} aria-pressed={metric === item} onClick={() => setMetric(item)}>{t(`replay.metric.${item}`)}</button>
            ))}
          </div>
          <span className="scenario-chip">{t(`constraints.cap.${cap}`)} · {t(`climate.${climate}`)}</span>
        </div>

        <p className="replay-unit" id="replay-unit">{t(`replay.unit.${metric}`, UNIT_FALLBACK[metric])}</p>
        {metric === "irrigation" && noIrrigation ? (
          <p className="empty-state replay-empty">{t("replay.no_irrigation_note", "This field has no irrigation, so every option uses 0 mm. Income, stress days and bare ground still differ.")}</p>
        ) : (
        <div className="chart-scroll" tabIndex={0} role="region" aria-label={t("replay.title")}>
          <div className="replay-chart-inner" role="img" aria-labelledby="replay-unit" aria-describedby="replay-table-caption">
            <ResponsiveContainer width="100%" height={HEIGHT}>
              <LineChart data={data} margin={MARGIN}>
                <CartesianGrid stroke={colours.grid} vertical={false} />
                {bands.map((band) => (
                  <ReferenceArea
                    key={band.from}
                    x1={band.from - 0.5} x2={band.to + 0.5}
                    fill={colours.band} fillOpacity={0.07} strokeOpacity={0} ifOverflow="hidden"
                    label={{ value: bandLabel(band), position: "insideTop", fill: colours.axis, fontSize: 12, dy: -22 }}
                  />
                ))}
                <XAxis dataKey="year" type="number" domain={[replay.years[0] - 0.5, replay.years[1] + 0.5]} ticks={[2000, 2005, 2010, 2015, 2020, 2025]} tickLine={false} axisLine={{ stroke: colours.grid }} height={X_AXIS_H} tick={{ fontSize: 13, fill: colours.axis }} />
                <YAxis width={52} domain={[lo, hi]} ticks={yTicks} tickFormatter={tick} tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: colours.axis }} />
                <Tooltip
                  cursor={{ stroke: colours.axis, strokeWidth: 1 }}
                  content={(props: TooltipProps<number, string>) => (
                    <ReplayTooltip {...props} order={ids} colours={colours} name={name} format={format} dry={replay.drought_years} dryLabel={t("replay.drought_marker")} />
                  )}
                />
                {worstYears.map((item) => (
                  <ReferenceDot key={`worst-${item.id}`} x={item.year} y={item.value} r={5} fill={colours.surface} stroke={colours[item.id]} strokeWidth={2} ifOverflow="visible" />
                ))}
                {ids.map((id) => (
                  <Line
                    key={id} type="linear" dataKey={id} name={id}
                    stroke={colours[id]} strokeWidth={2}
                    strokeDasharray={id === "R0" ? "6 4" : undefined}
                    dot={false}
                    activeDot={{ r: 4, stroke: colours.surface, strokeWidth: 2, fill: colours[id] }}
                    isAnimationActive={false} connectNulls
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
            <ul className="replay-end-labels" aria-hidden="true">
              {endLabels.map((item) => (
                <li key={item.id} style={{ top: item.y }}><i className={item.id === "R0" ? "dashed" : ""} style={{ "--key": colours[item.id] } as React.CSSProperties} />{lineName(item.id)}</li>
              ))}
            </ul>
          </div>
        </div>
        )}
        <div className="replay-legend">
          {ids.map((id) => <span key={id}><i className={id === "R0" ? "dashed" : ""} style={{ "--key": colours[id] } as React.CSSProperties} />{name(id)}</span>)}
          <span className="drought-key"><i />{t("replay.drought_marker")}</span>
          {worstYears.length > 0 && <span className="worst-key"><b aria-hidden="true" />{t("replay.worst_year_key", "Worst year for each option")}</span>}
        </div>

        <table className="replay-summary-table">
          <caption id="replay-table-caption">{t("replay.summary_caption", "Average and worst 5 years per rotation")}</caption>
          <thead><tr><th scope="col">{t("replay.rotation", "Rotation")}</th><th scope="col">{t("replay.average", "Average")}</th><th scope="col">{t("replay.worst5", "Worst 5 years")}</th></tr></thead>
          <tbody>
            {summaries.map((item) => (
              <tr key={item.id}>
                <th scope="row"><i className={item.id === "R0" ? "dashed" : ""} style={{ "--key": colours[item.id] } as React.CSSProperties} />{lineName(item.id)}{!item.feasible && <small>{t("replay.not_feasible", "over your water limit")}</small>}</th>
                <td>{format(Math.round(item.avg))}</td>
                <td>{format(Math.round(item.worst))}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="chart-note">{t("replay.note", "Average across every phase of the rotation, on this field's real weather.")}</p>
      </div>
    </section>
  );
}

function ReplayTooltip({
  active, payload, label, order, colours, name, format, dry, dryLabel,
}: TooltipProps<number, string> & {
  order: RotationId[];
  colours: Record<string, string>;
  name: (id: RotationId) => string;
  format: (value: number) => string;
  dry: number[];
  dryLabel: string;
}) {
  if (!active || !payload?.length) return null;
  const rows = order
    .map((id) => ({ id, value: payload.find((item) => item.dataKey === id)?.value }))
    .filter((row): row is { id: RotationId; value: number } => typeof row.value === "number")
    .sort((a, b) => b.value - a.value);
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-title">{label}{dry.includes(Number(label)) ? ` · ${dryLabel}` : ""}</p>
      <ul>
        {rows.map((row) => (
          <li key={row.id}><i className={row.id === "R0" ? "dashed" : ""} style={{ "--key": colours[row.id] } as React.CSSProperties} /><span>{name(row.id)}</span><b>{format(row.value)}</b></li>
        ))}
      </ul>
    </div>
  );
}
