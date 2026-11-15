"use client";

import { useMemo, useState } from "react";
import { CartesianGrid, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ReplayFile, ReplayYear, RotationId, ScenarioKey } from "@/lib/types";
import { formatVar, loc } from "@/lib/i18n";
import { useFieldShift } from "@/lib/state";
import { theme } from "@/lib/theme";
import type { UI } from "@/lib/ui";

type Metric = "irrigation" | "revenue" | "stress" | "bare";
const METRICS: Metric[] = ["irrigation", "revenue", "stress", "bare"];
const FIELD: Record<Metric, keyof ReplayYear> = {
  irrigation: "irrigation_mm", revenue: "revenue_usd_ac", stress: "stress_days", bare: "bare_days",
};
/** For revenue the worst years are the lowest; for the others they are the highest. */
const HIGHER_IS_WORSE: Record<Metric, boolean> = { irrigation: true, revenue: false, stress: true, bare: true };

export function ReplayChart({ replay, scenario, order, ui }: { replay: ReplayFile; scenario: ScenarioKey; order: RotationId[]; ui: UI }) {
  const { t, lang } = ui;
  const { theme: mode } = useFieldShift();
  const dark = mode === "dark";
  const [metric, setMetric] = useState<Metric>("irrigation");
  const runs = useMemo(() => replay.scenarios[scenario] ?? {}, [replay, scenario]);
  const ids = useMemo(() => order.filter((id) => runs[id]), [order, runs]);
  const key = FIELD[metric];
  const format = (value: number) => (
    metric === "irrigation" ? formatVar("irrigation_mm", value, lang)
      : metric === "revenue" ? formatVar("revenue_usd_ac", value, lang)
        : `${formatVar("days", value, lang)} ${t("unit.days", "days")}`
  );

  const data = useMemo(() => {
    const years: number[] = [];
    for (let y = replay.years[0]; y <= replay.years[1]; y += 1) years.push(y);
    return years.map((year) => {
      const row: Record<string, number | null> = { year };
      for (const id of ids) {
        const point = runs[id]?.by_year.find((item) => item.year === year);
        row[id] = point ? (point[key] as number) : null;
      }
      return row;
    });
  }, [ids, key, replay.years, runs]);

  const summaries = ids.map((id) => {
    const values = (runs[id]?.by_year ?? []).map((item) => item[key] as number).sort((a, b) => a - b);
    const worst = HIGHER_IS_WORSE[metric] ? values.slice(-5) : values.slice(0, 5);
    const avg = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    return { id, avg, worst: worst.length ? worst.reduce((a, b) => a + b, 0) / worst.length : 0, feasible: runs[id]?.feasible ?? false };
  });

  const axis = dark ? "#8da192" : "#6a7063";
  return (
    <section className="workspace-section replay-section" id="replay" aria-labelledby="replay-heading">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> {t("replay.eyebrow", "Look back before looking ahead")}</div>
          <h2 id="replay-heading">{t("replay.title")}</h2>
          <p>{t("replay.subtitle")}</p>
        </div>
        <span className="section-index">05 / 06</span>
      </div>
      <div className="replay-panel">
        <div className="replay-toolbar">
          <div className="replay-metric-switch" role="group" aria-label={t("replay.metric_label", "Choose what to plot")}>
            {METRICS.map((item) => (
              <button type="button" key={item} aria-pressed={metric === item} onClick={() => setMetric(item)}>{t(`replay.metric.${item}`)}</button>
            ))}
          </div>
          <span className={`scenario-chip ${scenario.split("|")[1]}`}>{t(`constraints.cap.${scenario.split("|")[0]}`)} · {t(`climate.${scenario.split("|")[1]}`)}</span>
        </div>
        <div className="chart-scroll">
          <div className="replay-chart-inner" role="img" aria-label={`${t("replay.title")}: ${t(`replay.metric.${metric}`)}, ${ids.join(", ")}`}>
            <ResponsiveContainer width="100%" height={302}>
              <LineChart data={data} margin={{ top: 16, right: 12, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={dark ? "rgba(255,255,255,0.08)" : "#e8e8df"} strokeDasharray="3 5" vertical={false} />
                {replay.drought_years.map((year) => (
                  <ReferenceArea key={year} x1={year - 0.5} x2={year + 0.5} fill={theme.risk.heat} fillOpacity={dark ? 0.22 : 0.14} strokeOpacity={0} ifOverflow="hidden" />
                ))}
                <XAxis dataKey="year" type="number" domain={[replay.years[0], replay.years[1]]} ticks={[2000, 2005, 2010, 2015, 2020, 2025]} tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: axis }} />
                <YAxis width={56} tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: axis }} />
                <Tooltip
                  contentStyle={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 8, fontSize: 14, color: "var(--ink)" }}
                  formatter={(value, name) => [typeof value === "number" ? format(value) : String(value), String(name)]}
                  labelFormatter={(year) => (replay.drought_years.includes(Number(year)) ? `${year} · ${t("replay.drought_marker")}` : String(year))}
                />
                {ids.map((id) => (
                  <Line
                    key={id} type="monotone" dataKey={id} name={id}
                    stroke={theme.rot[id]} strokeWidth={id === "R0" ? 2 : 2.4}
                    strokeDasharray={id === "R0" ? "5 4" : undefined}
                    dot={false} activeDot={{ r: 5, strokeWidth: 0 }} isAnimationActive={false} connectNulls
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="replay-legend">
          {ids.map((id) => <span key={id}><i style={{ background: theme.rot[id] }} />{id} · {loc(ui.cardText.rotations[id]?.name, lang)}</span>)}
          <span className="drought-key"><i />{t("replay.drought_marker")}: {replay.drought_years.join(", ")}</span>
        </div>
        <table className="replay-summary-table">
          <caption className="sr-only">{t("replay.summary_caption", "Average and worst 5 years per rotation")}</caption>
          <thead className="sr-only"><tr><th>{t("replay.rotation", "Rotation")}</th><th>{t("replay.average", "Average")}</th><th>{t("replay.worst5", "Worst 5 years")}</th></tr></thead>
          <tbody>
            {summaries.map((item) => (
              <tr className="replay-summary-row" key={item.id}>
                <th scope="row" className="summary-rotation"><i style={{ background: theme.rot[item.id] }} />{item.id}{!item.feasible && <small> · {t("replay.not_feasible", "over your water limit")}</small>}</th>
                <td><small>{t("replay.average", "Average")}</small><b>{format(Math.round(item.avg))}</b></td>
                <td><small>{t("replay.worst5", "Worst 5 years")}</small><b>{format(Math.round(item.worst))}</b></td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="chart-note">{t("replay.note", "Average across every phase of the rotation, on this field's real weather.")}</p>
      </div>
    </section>
  );
}
