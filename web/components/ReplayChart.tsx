"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid, Line, LineChart, ReferenceArea, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";
import type { CopyFile, ReplayFile, StrategyEntry } from "@/lib/types";
import { fill, t } from "@/lib/i18n";
import { useFieldShift } from "@/lib/state";
import { theme } from "@/lib/theme";

type Metric = "irrigation" | "revenue" | "stress" | "bare";
const colors = theme.rotation;
const metrics: Metric[] = ["irrigation", "revenue", "stress", "bare"];

export function ReplayChart({ replay, shown, copy }: { replay: ReplayFile; shown: StrategyEntry[]; copy: CopyFile["strings"] }) {
  const { climate, lang, theme } = useFieldShift();
  const isDark = theme === "dark";
  const [metric, setMetric] = useState<Metric>("irrigation");
  const series = replay.series[climate];
  const chartData = useMemo(() => {
    const years = [...new Set(shown.flatMap((entry) => series[entry.id]?.[metric]?.map((point) => point.year) || []))].sort((a, b) => a - b);
    return years.map((year) => {
      const row: Record<string, string | number> = { year };
      shown.forEach((entry) => {
        row[entry.id] = series[entry.id]?.[metric]?.find((point) => point.year === year)?.value ?? 0;
      });
      return row;
    });
  }, [metric, series, shown]);
  const unit = metric === "irrigation" ? " mm" : metric === "revenue" ? " $/ac" : " days";
  const metricLabels = {
    irrigation: t("replay.metric.irrigation", copy, lang),
    revenue: t("replay.metric.revenue", copy, lang),
    stress: t("replay.metric.stress", copy, lang),
    bare: t("replay.metric.bare", copy, lang),
  };
  const summaries = shown.map((entry) => {
    const points = series[entry.id]?.[metric] || [];
    const values = points.map((point) => point.value).sort((a, b) => a - b);
    const worst = metric === "revenue" ? values.slice(0, 5) : values.slice(-5);
    const average = values.length ? values.reduce((total, value) => total + value, 0) / values.length : 0;
    const worstAverage = worst.length ? worst.reduce((total, value) => total + value, 0) / worst.length : 0;
    return { id: entry.id, average, worstAverage };
  });
  return (
    <section className="workspace-section replay-section" id="replay">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> LOOK BACK BEFORE LOOKING AHEAD</div>
          <h2>{t("replay.title", copy, lang)}</h2>
          <p>{t("replay.subtitle", copy, lang)}</p>
        </div>
        <span className="section-index">05 / 06</span>
      </div>
      <div className="replay-panel">
        <div className="replay-toolbar">
          <div className="replay-metric-switch" role="group" aria-label="Choose replay metric">
            {metrics.map((item) => <button type="button" key={item} aria-pressed={metric === item} onClick={() => setMetric(item)}>{metricLabels[item]}</button>)}
          </div>
          <span className={`scenario-chip ${climate}`}>{climate === "actual" ? t("priority.actual", copy, lang) : t("priority.hotdry", copy, lang)}</span>
        </div>
        <div className="chart-scroll">
          <div className="replay-chart-inner">
            <ResponsiveContainer width="100%" height={302}>
              <LineChart data={chartData} margin={{ top: 16, right: 12, bottom: 8, left: 0 }}>
                <CartesianGrid stroke={isDark ? "rgba(255, 255, 255, 0.08)" : "#e8e8df"} strokeDasharray="3 5" vertical={false} />
                <XAxis dataKey="year" type="number" domain={[2000, 2025]} ticks={[2000, 2005, 2010, 2015, 2020, 2025]} tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: isDark ? "#8da192" : "#6a7063" }} />
                <YAxis width={52} tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: isDark ? "#8da192" : "#6a7063" }} />
                <Tooltip
                  contentStyle={{
                    background: isDark ? "rgba(18, 28, 22, 0.96)" : "#fff",
                    border: isDark ? "1px solid rgba(255, 255, 255, 0.12)" : "1px solid #e4e6dc",
                    borderRadius: 8,
                    fontSize: 14,
                    color: isDark ? "#edf5ef" : "#24352b",
                    boxShadow: isDark ? "0 8px 24px rgba(0, 0, 0, 0.5)" : "0 4px 14px rgba(0, 0, 0, 0.08)",
                  }}
                  itemStyle={{ color: isDark ? "#edf5ef" : "#24352b" }}
                  formatter={(value, name) => [`${value}${unit}`, `${name}`]}
                  labelFormatter={(value) => fill(copy["replay.year"], { year: String(value) }, lang)}
                />
                {replay.drought_years.map((year) => <ReferenceArea key={year} x1={year - 0.6} x2={year + 0.6} fill="#d98762" fillOpacity={isDark ? 0.2 : 0.12} strokeOpacity={0} />)}
                {shown.map((entry) => (
                  <Line
                    key={entry.id}
                    type="monotone"
                    dataKey={entry.id}
                    name={entry.id}
                    stroke={colors[entry.id]}
                    strokeWidth={entry.id === "R0" ? 2 : 2.4}
                    strokeDasharray={entry.id === "R0" ? "5 4" : undefined}
                    dot={{ r: 3, strokeWidth: 1.5, fill: isDark ? "#121d16" : "#fff" }}
                    activeDot={{ r: 5, strokeWidth: 0 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="replay-legend">
          {shown.map((entry) => <span key={entry.id}><i style={{ background: colors[entry.id] }} />{entry.id}</span>)}
          <span className="drought-key"><i />{t("replay.drought_sample", copy, lang, "Historic drought benchmark years")}</span>
        </div>
        <div className="replay-summary-table">
          {summaries.map((item) => (
            <div className="replay-summary-row" key={item.id}>
              <span className="summary-rotation"><i style={{ background: colors[item.id] }} />{item.id}</span>
              <span><small>{t("replay.average", copy, lang)}</small><b>{formatMetric(item.average, metric)}{unit}</b></span>
              <span><small>{t("replay.worst", copy, lang)}</small><b>{formatMetric(item.worstAverage, metric)}{unit}</b></span>
            </div>
          ))}
        </div>
        <p className="chart-note">{t("replay.note", copy, lang)}</p>
      </div>
    </section>
  );
}

function formatMetric(value: number, metric: Metric): string {
  return metric === "revenue" ? `$${Math.round(value).toLocaleString()}` : Math.round(value).toLocaleString();
}
